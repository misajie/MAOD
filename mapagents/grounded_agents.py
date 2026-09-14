"""Validation-guided agents with executable map and supplied-covariate tools."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from .agents import AgentSystem
from .programs import OPERATORS, ProgramError, normalize_program, validate_program, semantic_id


def canonical_program(program):
    result = copy.deepcopy(program)
    for feature in result["features"]:
        expr = feature["expression"]
        if feature.get("scope") == "pair" and expr.get("op") in {"origin", "destination"}:
            feature["scope"], feature["expression"] = expr["op"], expr["arg"]
    return normalize_program(result)


def addition_errors(feature, source_columns):
    errors = []
    if not isinstance(feature, dict):
        return ["Feature must be an object"]
    if feature.get("scope") not in {"destination", "pair"}:
        errors.append("Only destination or pair additions are allowed; inline origin expressions inside pair interactions")
    try:
        validate_program({"version": 1, "features": [feature]})
    except (ValueError, KeyError, TypeError) as error:
        errors.append(str(error))
    def visit(node):
        if not isinstance(node, dict): return
        if node.get("op") == "source" and node.get("column") not in source_columns:
            errors.append("Unknown source.column " + str(node.get("column")) + "; inline the complete expression instead of referencing a feature name")
        for key in ("arg", "left", "right"):
            if key in node: visit(node[key])
    visit(feature.get("expression"))
    return errors


def endpoint_dependencies(expression):
    if not isinstance(expression, dict):
        return set()
    op = expression.get("op")
    if op in {"origin", "destination"}:
        return {op}
    if op == "same_zone":
        return {"origin", "destination", "same_zone"}
    result = {"distance"} if op == "distance" else set()
    for key in ("arg", "left", "right"):
        if key in expression:
            result.update(endpoint_dependencies(expression[key]))
    return result


class GroundedAgentSystem(AgentSystem):
    def __init__(self, config, rag_root, output_dir, map_evidence, program_checker=None):
        super().__init__(config, rag_root, output_dir)
        self.maps = map_evidence
        self.program_checker = program_checker
        prior_path = config.get("prior_catalog")
        self.prior_catalog = json.loads(Path(prior_path).read_text(encoding="utf-8")) if prior_path else None

    def discover(self, current, diagnostics, history, task, count=2):
        if diagnostics.get("split") != "validation":
            raise ValueError("Agent adaptation accepts validation diagnostics only")
        targets = {}
        for region in diagnostics["largest_error_regions"]:
            for pair in region.get("pair_errors", []):
                targets[pair["diagnostic_id"]] = pair
        request = self._call("Adapter",
            "Diagnose an OD predictor using validation evidence. Residual=observed-predicted: positive is underprediction, "
            "negative is overprediction. Direction labels and numbers are computed by the executor and authoritative. "
            "Identify missing spatial information, competing explanations and prior edits that failed. "
            "Row totals are supplied: origin mass alone cannot fix them. Separate diagonal allocation and off-diagonal destination choice. "
            "Interpret each OD pair as ordered: origin characteristics condition travel demand and distance sensitivity; destination "
            "characteristics describe candidate opportunities. A zone can have multiple functional roles and different roles as origin "
            "and destination. Distinguish complementary endpoint roles, competing destinations and same-zone retention. "
            "Do not infer individual demographics, actual trip purposes or residential population from aggregate OD totals. "
            "Return {focus:[{diagnostic_id,hypothesis,expected_change:increase|decrease}], "
            "map_questions:[str], previous_edit_lessons:[str]}. Choose up to six diagnostic IDs from pair_errors. "
            "Hypotheses should concern measurable map relations, not geographic ID exceptions. Do not repeat numeric residual signs in prose. "
            "Adding a decay feature is not changing a known fixed decay parameter of the neural network.",
            {"task": task, "validation_diagnostics": diagnostics, "current_program": current,
             "history": history[-12:], "aggregation_prior": self.prior_catalog})
        focus, corrections = [], []
        for item in request.get("focus", [])[:6]:
            key = item.get("diagnostic_id")
            if key not in targets:
                corrections.append({"rejected_target": key, "reason": "unknown diagnostic ID"})
                continue
            fact = targets[key]
            direction = "increase" if fact["residual"] > 0 else "decrease"
            if item.get("expected_change") != direction:
                corrections.append({"diagnostic_id": key, "reported": item.get("expected_change"), "computed": direction})
            focus.append({**fact, "hypothesis": item.get("hypothesis", ""), "expected_change": direction})
        grounded_request = {"focus": focus, "map_questions": request.get("map_questions", []),
                            "previous_edit_lessons": request.get("previous_edit_lessons", []),
                            "executor_direction_corrections": corrections}
        maps = self.maps.bootstrap({"focus": focus} if focus else diagnostics)
        docs = self.index.retrieve(task, k=4)
        query_plan = self._call("Surveyor",
            "You are a map investigator. Use the supplied map tool to distinguish competing explanations of OD allocation errors. "
            "The initial dossiers contain actual local objects, source feature gaps and nearest/feature-similar zones. "
            "The ordered pair dossiers retain origin and destination identities. Compare endpoint feature composition and examine "
            "whether swapping the endpoints should change the proposed relation. Functional roles are open and overlapping; "
            "ground them in measured facilities, land use, supplied mass and neighborhood context. "
            "Return {requests:[map_tool_request,...], knowledge_queries:[str]}. Request up to six map queries and two short knowledge queries. "
            "Request local tag_search and feature_probe to verify proposed raw OSM or cross-layer measurements. "
            "Queries execute against real data; unavailable measurements return errors, not invented values. "
            "Choose tags and scales from the actual map; there is no closed attractor vocabulary. "
            "aggregation_prior documents reusable DGM aggregation recipes and input semantics. It is prior knowledge, "
            "not a measured local map record; verify new quantities through executable tools. "
            "Raw counts refer to OSM elements, not deduplicated physical facilities. Travel times and independent census population "
            "are unavailable unless explicitly supplied. Respect the metadata definition of any supplied mass/population feature. "
            "Use feature_probe for ZONE expressions without origin/destination wrappers. Use pair_feature_probe for directed "
            "PAIR expressions with explicit endpoint wrappers; it returns forward/reversed values and within-origin destination variation. "
            "Exclude constant columns and distinguish general movement from commuting. "
            "Raw OSM snapshot provenance is supplied; do not assert an unknown temporal match.",
            {"task": task, "diagnosis": grounded_request, "map_evidence": maps,
             "tool_schema": self.maps.tool_schema(), "operators": OPERATORS,
             "knowledge": docs, "aggregation_prior": self.prior_catalog})
        for query in query_plan.get("requests", [])[:6]:
            maps.append(self.maps.query(query))
        for query in query_plan.get("knowledge_queries", [])[:2]:
            docs.extend(self.index.retrieve(str(query), k=4))
        docs = list({d["id"]: d for d in docs}.values())
        survey = self._call("Surveyor",
            "Synthesize executable spatial hypotheses from the returned map measurements. "
            "Return {mechanisms:[{hypothesis_id,name,hypothesis,map_evidence_ids,knowledge_ids,proposed_expressions,"
            "endpoint_roles:{origin:str,destination:str},swap_expectation:str,competing_explanation}], "
            "rejected_hypotheses:[{hypothesis,reason}]}. "
            "Use at most six mechanisms. Every mechanism must cite at least one supplied successful map: evidence ID. "
            "aggregation_prior supplies recipes and interpretation only; a prior: ID never substitutes for measured map: evidence. "
            "Describe separately what the origin contributes, what the destination contributes, and whether reversing their "
            "roles changes the expression. Include an origin-conditioned relation for the Cartographer to consider, grounded "
            "in observed feature composition, declared mass or distance context. Multiple functional roles per zone are allowed. "
            "Separate a recovered missing measurement, a finer tag hierarchy, and a new spatial relation. "
            "A request that failed is not evidence. Ground object names in records; never use names or zone IDs as numerical constants. "
            "Neighborhood scales must reflect observed zone sizes and distances. Density is not network centrality. "
            "No causal claims. Supplied source units may be unknown; do not mix unknown areas with counts. "
            "Current model = trainable DG score + learned weighted sum of standardized spatial-program features. "
            "Only the latter is exactly decomposable. Origin-only additive terms cancel under row softmax; propose destination or interacting pair terms.",
            {"task": task, "diagnosis": grounded_request, "current_program": current,
             "map_evidence": maps, "knowledge": docs, "operators": OPERATORS,
             "aggregation_prior": self.prior_catalog})
        valid_map = {d["id"] for d in maps if "error" not in d}
        source_columns = set(self.maps.columns)
        mechanisms = {}
        for original in survey.get("mechanisms", []):
            key = original.get("hypothesis_id")
            if not isinstance(key, str) or not key.strip(): continue
            if not set(original.get("map_evidence_ids", [])) & valid_map: continue
            mechanism = copy.deepcopy(original)
            valid, invalid = [], []
            for feature in mechanism.get("proposed_expressions", []):
                errors = addition_errors(feature, source_columns)
                if errors:
                    invalid.append({"name": feature.get("name") if isinstance(feature, dict) else None, "errors": errors})
                else: valid.append(feature)
            mechanism["proposed_expressions"] = valid
            mechanism["executor_rejected_templates"] = invalid
            mechanisms[key] = mechanism
        if not mechanisms:
            raise RuntimeError("Surveyor produced no hypothesis grounded in successful map measurements")
        payload = {"task": task, "current_program": current, "mechanisms": list(mechanisms.values()),
                   "map_evidence": maps, "knowledge": docs, "operators": OPERATORS,
                   "aggregation_prior": self.prior_catalog,
                   "candidate_count": count, "source_columns": sorted(source_columns),
                   "removable_features": [f["name"] for f in current["features"]
                                          if f.get("mechanism") != "Supplied public geographic covariate"]}
        instruction = (
            f"Compile exactly {count} distinct candidate edits into the documented JSON spatial DSL. "
            "Return {candidates:[{name,remove:[existing_feature_name],add:[{name,scope,expression,mechanism,hypothesis_id,evidence:[id],"
            "endpoint_roles:{origin:str,destination:str},swap_expectation:str}]}]}. "
            "Each candidate has one to six focused new features, an internally coherent hypothesis and up to four removals of old agent features. "
            "Keep the supplied DG base features. Scope for additions must be destination or pair. "
            "Use actual raw OSM queries when they recover missing information. Mechanism names and tag vocabulary are open. "
            "Use hypotheses and successful map: IDs from this payload; every addition must cite its hypothesis_id and at least one map: ID. "
            "aggregation_prior is a documented recipe catalog, not measured evidence or a closed feature list. "
            "Do not duplicate a destination column by wrapping it as a pair. A pair expression must depend on destination or distance, "
            "not just origin. Use the same program for all zones. No place IDs, memorized zone constants, OD labels or made-up statistics. "
            "At least one candidate must include a nontrivial origin-conditioned pair relation: origin evidence interacting with "
            "destination evidence or distance. Merely multiplying a destination feature by an origin constant does not qualify. "
            "For every addition state the endpoint_roles and swap_expectation. Roles are evidence-backed functional hypotheses, "
            "not fixed categories or inferred personal identities; 'any origin' is acceptable for a pure destination feature. "
            "Examples of relation forms, only when supported by measurements, include origin mass times destination opportunity "
            "share, origin facility composition times a distinct destination composition, and origin context modulating distance "
            "sensitivity. An available OD-row-total mass is a mobility-volume prior, not census population or an OD edge label. "
            "These are additive logit corrections with learned coefficients. Origin-only or constant terms cancel; a distance basis is a feature, "
            "not a guaranteed monotone prediction effect. Source values are signed-log1p transformed and train-standardized automatically. "
            "Do not reinterpret tiny unverified upstream area/length values as physical units. "
            "Use radial_basis for a distance band; exp_decay is monotone, not band-shaped. "
            "source.column must be in source_columns, never a newly added feature name. Inline the full expression tree every time. "
            "remove must be empty when removable_features is empty, including constant-zero base columns. "
            "A count denominator can be zero due to incomplete OSM: inspect probe extremes and use an explicit pseudocount or zone area when justified. "
            "Use only documented operator arguments. Do not emit Python code.")
        base_names = {f["name"] for f in current["features"] if f.get("mechanism") == "Supplied public geographic covariate"}
        for attempt in range(3):
            repair_instruction = ""
            if attempt:
                payload["repair_attempt"] = attempt
                repair_instruction = "\nThe previous response was rejected. Correct ALL executor_errors; do not reuse the rejected response. " + json.dumps(payload["executor_errors"])
            response = self._call("Cartographer", instruction + repair_instruction, payload)
            errors = []
            try:
                candidates = response.get("candidates", [])
                if not isinstance(candidates, list) or len(candidates) != count:
                    raise ProgramError(f"Expected {count} candidates")
                programs = []
                for edit in candidates:
                    candidate_errors = []
                    removed = set(edit.get("remove", []))
                    names = {f["name"] for f in current["features"]}
                    if removed & base_names or removed - names:
                        candidate_errors.append("Remove only names in removable_features; keep all supplied DG columns")
                    adds = edit.get("add", [])
                    if not isinstance(adds, list) or not 1 <= len(adds) <= 6:
                        raise ProgramError("Each edit needs 1..6 features")
                    for feature in adds:
                        feature_errors = addition_errors(feature, source_columns)
                        if feature.get("hypothesis_id") not in mechanisms:
                            feature_errors.append("Feature hypothesis_id is not grounded")
                        if not set(feature.get("evidence", [])) & valid_map:
                            feature_errors.append("Feature needs a successful map: evidence ID")
                        roles = feature.get("endpoint_roles")
                        if not isinstance(roles, dict) or any(not isinstance(roles.get(k), str) or not roles[k].strip()
                                                              for k in ("origin", "destination")):
                            feature_errors.append("Feature needs nonempty endpoint_roles.origin and endpoint_roles.destination")
                        if not isinstance(feature.get("swap_expectation"), str) or not feature["swap_expectation"].strip():
                            feature_errors.append("Feature needs a swap_expectation grounded in its ordered expression")
                        feature["endpoint_dependencies"] = sorted(endpoint_dependencies(feature.get("expression")))
                        if feature_errors:
                            candidate_errors.append({"feature": feature.get("name"), "errors": feature_errors})
                    if candidate_errors:
                        errors.append({"candidate": edit.get("name"), "errors": candidate_errors})
                        continue
                    p = canonical_program({"version": 1, "name": edit["name"], "features":
                                           [f for f in current["features"] if f["name"] not in removed] + adds})
                    try:
                        validate_program(p)
                        if self.program_checker is not None:
                            inspection = self.program_checker(p)
                            if inspection["invalid"]:
                                errors.append({"candidate": edit["name"], "numeric_feedback": inspection})
                                continue
                    except (ValueError, KeyError, TypeError) as error:
                        errors.append({"candidate": edit["name"], "error": str(error)})
                        continue
                    programs.append(p)
                if errors: raise ProgramError("Repair all structural and numeric errors")
                has_origin_interaction = any(
                    f.get("scope") == "pair" and "origin" in endpoint_dependencies(f["expression"])
                    and bool(endpoint_dependencies(f["expression"]) & {"destination", "distance"})
                    and f["expression"].get("op") != "same_zone"
                    for edit in candidates for f in edit.get("add", []))
                if not has_origin_interaction:
                    raise ProgramError("Include at least one origin-conditioned destination or distance interaction across the candidates")
                signatures = [semantic_id({"features": [(f["scope"], f["expression"]) for f in p["features"]]}) for p in programs]
                if len(set(signatures)) != count: raise ProgramError("Candidates must have distinct numerical expressions")
                return programs, {"diagnosis": grounded_request, "survey": survey,
                                  "compiled_mechanisms": list(mechanisms.values()),
                                  "evidence_ids": [d["id"] for d in maps], "query_plan": query_plan}
            except (ValueError, KeyError, TypeError) as error:
                payload["executor_errors"] = errors or [{"error": str(error)}]
                payload["rejected_response"] = response
        raise RuntimeError("Cartographer failed to compile grounded candidate edits")
