"""New York development: grounded program search without held-out scoring."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import torch

from .data import load_dataset
from .evidence import MapEvidence
from .grounded_agents import GroundedAgentSystem
from .metrics import aggregate_metrics, matrix_metrics, selection_score
from .programs import SpatialCompiler, default_program, ProgramError, semantic_id
from .execution_report import write_execution_report
from .training import ODStore, evaluate, fit_model, raw_inputs, save_json


def _values(store, bundle, seed, limit=20000):
    rng = np.random.default_rng(seed)
    rows = store.examples("train", positive_only=True)
    rng.shuffle(rows)
    chunks = []; groups = []
    remaining = limit
    for region_id, i in rows:
        region = store.regions[region_id]
        selected = rng.choice(len(region.zone_ids), size=min(64, len(region.zone_ids), remaining), replace=False)
        chunks.append(raw_inputs(bundle, region, np.full(len(selected), i), selected))
        groups.extend([len(chunks)-1] * len(selected))
        remaining -= len(selected)
        if remaining <= 0: break
    return np.concatenate(chunks), np.asarray(groups)


def inspect_program(store, bundle, backbone_ids, seed):
    values, groups = _values(store, bundle, seed)
    values = np.sign(values) * np.log1p(np.abs(values))
    report = []
    invalid = []
    for j, key in enumerate(bundle.input_ids):
        if key in backbone_ids: continue
        column = values[:, j]
        reason = None
        if key.startswith("origin:"):
            reason = "origin-only additive correction cancels in row softmax"
        elif np.ptp(column) <= 1e-14:
            reason = "constant on sampled training map pairs"
        elif all(np.ptp(column[groups == group]) <= 1e-14 for group in np.unique(groups)):
            reason = "constant within every sampled origin row; cancels in row softmax"
        else:
            for k in range(j):
                if np.array_equal(column, values[:, k]):
                    reason = "numerically duplicates " + bundle.input_ids[k]
                    break
        report.append({"input_id": key, "std_signed_log1p": float(column.std()), "rejection_reason": reason})
        if reason: invalid.append({"input_id": key, "reason": reason})
    return {"n_sampled_training_pairs": len(values), "features": report, "invalid": invalid}


def _metric(summary, metric="cpc"):
    return selection_score(summary, metric)


def prepare_reference(config):
    """Fit the unchanged geographic DG reference while raw map ingestion proceeds."""
    data = load_dataset(Path(config["data"]["prepared"]))
    store = ODStore(data)
    compiler = SpatialCompiler(data)
    bundle = compiler.compile(default_program(data))
    folder = Path(config["output_dir"]) / "reference"
    model, transform, training = fit_model(store, bundle, config["training"], folder, int(config.get("seed", 1234)))
    validation, diagnostics = evaluate(store, bundle, model, transform, "validation")
    save_json(folder / "validation.json", validation)
    save_json(folder / "diagnostics.json", diagnostics)
    save_json(folder / "program.json", default_program(data))
    print(json.dumps({"validation": validation, "selected_epoch": training.get("selected_epoch"),
                      "heldout_evaluated": False}), flush=True)
    return validation


@torch.inference_mode()
def explain_validation(store, bundle, model, transform, output_dir, program=None):
    """Exact score decomposition and feature removal at fixed learned weights."""
    output_dir = Path(output_dir)
    model.eval()
    keys = model.program_input_ids
    feature_metadata = {}
    for feature in (program or {}).get("features", []):
        scope = feature.get("scope", "both")
        for side in (["origin", "destination"] if scope == "both" else [scope]):
            feature_metadata[side + ":" + semantic_id(feature["expression"])] = {
                k: feature[k] for k in ("name", "hypothesis_id", "mechanism", "evidence", "endpoint_roles", "swap_expectation", "expression") if k in feature}
    diagnostic_targets = {}
    for path in sorted(output_dir.glob("round_*/deliberation.json")):
        deliberation = json.loads(path.read_text(encoding="utf-8"))
        for target in deliberation.get("diagnosis", {}).get("focus", []):
            key = (target["origin_id"], target["destination_id"])
            diagnostic_targets.setdefault(key, []).append({"round": path.parent.name, **target})
    if not keys:
        result = {"split": "validation", "program_terms": [], "note": "Selected model has no spatial correction."}
        save_json(output_dir / "explanations.json", result)
        return result
    device = next(model.parameters()).device
    totals = np.zeros(len(keys)); pairs = 0
    removal_records = [[] for _ in keys]
    base_records = []; full_records = []; examples = []; target_explanations = []
    for region_id, rows in store.rows_by_region("validation").items():
        region = store.regions[region_id]
        truth = region.flows[rows]
        base_logits = []; contributions = []
        for start in range(0, len(rows), 16):
            chosen = np.asarray(rows[start:start+16])
            x = transform.transform(raw_inputs(bundle, region, chosen[:, None], np.arange(len(region.zone_ids))[None, :]))
            x = torch.as_tensor(x, device=device)
            base_logits.append(model.backbone_scores(x).cpu().numpy().astype(np.float64))
            contributions.append(model.program_terms(x).cpu().numpy().astype(np.float64))
        base_logits = np.concatenate(base_logits); terms = np.concatenate(contributions)
        logits = base_logits + terms.sum(-1)
        def normalize(score):
            p = np.exp(score - score.max(axis=-1, keepdims=True))
            return p / p.sum(axis=-1, keepdims=True) * truth.sum(axis=-1, keepdims=True)
        full = normalize(logits); base = normalize(base_logits)
        args = (region.distances[rows], region.zone_ids[rows], region.zone_ids)
        full_records.append(matrix_metrics(truth, full, *args))
        base_records.append(matrix_metrics(truth, base, *args))
        centered = terms - terms.mean(axis=1, keepdims=True)
        totals += np.abs(centered).sum(axis=(0, 1)); pairs += terms.shape[0]*terms.shape[1]
        matched = []
        row_lookup = {str(region.zone_ids[row]): i for i, row in enumerate(rows)}
        destination_lookup = {str(zone): j for j, zone in enumerate(region.zone_ids)}
        for (origin, destination), requests in diagnostic_targets.items():
            if origin not in row_lookup or destination not in destination_lookup: continue
            i, j = row_lookup[origin], destination_lookup[destination]
            entry = {"origin_id": origin, "destination_id": destination, "observed": float(truth[i,j]),
                     "predicted": float(full[i,j]), "prediction_with_head_disabled": float(base[i,j]),
                     "original_diagnoses": requests, "term_interventions": []}
            matched.append((i, j, entry)); target_explanations.append(entry)
        for k in range(len(keys)):
            removed_prediction = normalize(logits - terms[..., k])
            removal_records[k].append(matrix_metrics(truth, removed_prediction, *args))
            for i, j, entry in matched:
                change = float(full[i,j] - removed_prediction[i,j])
                entry["term_interventions"].append({"input_id": keys[k], "prediction_without_term": float(removed_prediction[i,j]),
                                                    "change_from_term": change,
                                                    "direction": "increase" if change > 0 else "decrease" if change < 0 else "unchanged"})
        for flat in np.argsort(-np.abs(full-base).ravel())[:2]:
            i, j = np.unravel_index(flat, full.shape)
            contrast = terms[i, j] - terms[i].mean(axis=0)
            examples.append({"region_id": region_id, "origin_id": str(region.zone_ids[rows[i]]),
                             "destination_id": str(region.zone_ids[j]), "observed": float(truth[i, j]),
                             "predicted": float(full[i, j]), "prediction_with_head_disabled": float(base[i, j]),
                             "change": float(full[i,j]-base[i,j]),
                             "centered_logit_contributions": dict(zip(keys, contrast.tolist()))})
    full_summary = aggregate_metrics(full_records)
    terms_report = []
    for k, key in enumerate(keys):
        removed = aggregate_metrics(removal_records[k])
        terms_report.append({"input_id": key, **feature_metadata.get(key, {}), "coefficient": float(model.program_weights[k].cpu()),
                             "mean_abs_centered_logit_contribution": float(totals[k]/max(pairs, 1)),
                             "cpc_drop_when_removed": selection_score(full_summary, "cpc") - selection_score(removed, "cpc"),
                             "offdiagonal_cpc_drop_when_removed": selection_score(full_summary, "offdiagonal_cpc") - selection_score(removed, "offdiagonal_cpc"),
                             "removed_validation": removed})
    examples.sort(key=lambda r: -abs(r["change"]))
    result = {"split": "validation", "full": full_summary, "head_disabled": aggregate_metrics(base_records),
              "program_terms": terms_report, "examples": examples[:16],
              "diagnosed_pairs": target_explanations,
              "interpretation": "Fixed-model feature intervention and exact additive score contributions, not causal effects or a retrained DG baseline. Contributions are centered over each complete destination row; softmax redistribution is nonlinear."}
    save_json(output_dir / "explanations.json", result)
    return result


def run_discovery(config):
    out = Path(config["output_dir"]); out.mkdir(parents=True, exist_ok=True)
    if (out / "config.json").exists():
        if json.loads((out / "config.json").read_text()) != config:
            raise ValueError("Use a new output directory for a changed discovery configuration")
    else: save_json(out / "config.json", config)
    if (out / "result.json").exists():
        return json.loads((out / "result.json").read_text())
    data = load_dataset(Path(config["data"]["prepared"]))
    store = ODStore(data)
    osm_path = config["data"].get("osm_path")
    if not osm_path or not Path(osm_path).is_file():
        raise FileNotFoundError("Historical OSM objects are required for grounded discovery; no current-snapshot or aggregate-only fallback is used.")
    source_info = json.loads(Path(str(osm_path) + ".json").read_text(encoding="utf-8"))
    dated = source_info.get("osm_snapshot_date") or (source_info.get("source_manifest") or {}).get("nominal_archive_date")
    cutoff = config["data"].get("latest_osm_year")
    if cutoff is not None and (not dated or int(dated[:4]) > int(cutoff)):
        raise ValueError("OSM provenance is undated or newer than the configured historical cutoff")
    compiler = SpatialCompiler(data, config["data"].get("osm_path"), out / "spatial_cache")
    seed = int(config.get("seed", 1234)); settings = config["training"]
    metric_name = str(settings.get("selection_metric", "cpc"))
    base_program = default_program(data); base_bundle = compiler.compile(base_program)
    backbone_ids = list(base_bundle.input_ids)
    maps = MapEvidence(compiler, out / "agents")
    # Build the full tag inventory before selective queries; the context summary
    # is bounded but the map tool can retrieve any observed tag.
    save_json(out / "map_profile.json", compiler.profile())
    reference, reference_transform, reference_training = fit_model(store, base_bundle, settings, out / "reference", seed)
    reference_summary, diagnostics = evaluate(store, base_bundle, reference, reference_transform, "validation")
    save_json(out / "reference" / "validation.json", reference_summary)
    save_json(out / "reference" / "diagnostics.json", diagnostics)
    program, bundle, model, transform = base_program, base_bundle, reference, reference_transform
    summary = reference_summary; checkpoint = out / "reference" / "model.pt"
    dg_model, dg_transform = reference, reference_transform
    history = []
    def check_program(candidate):
        compiled = compiler.compile(candidate)
        inspection = inspect_program(store, compiled, backbone_ids, seed)
        if set(compiled.input_ids) == set(bundle.input_ids):
            inspection["invalid"].append({"input_id": "program", "reason": "No change to the current numerical expressions"})
        return inspection
    agent_config = {**config["llm"], "prior_catalog": config.get("prior_catalog")}
    agent = GroundedAgentSystem(agent_config, Path(config["rag_root"]), out / "agents", maps, check_program)
    search = config["search"]
    if int(search.get("rounds", 3)) < 1: raise ValueError("Discovery requires at least one round")
    for round_index in range(int(search.get("rounds", 3))):
        stage = out / f"round_{round_index:02d}"
        status = {"stage": "search", "round": round_index, "selection_metric": metric_name,
                  "selection_score": _metric(summary, metric_name),
                  "validation_cpc": summary["macro"].get("cpc"),
                  "validation_offdiagonal_cpc": summary["macro"].get("offdiagonal_cpc"),
                  "heldout_evaluated": False}
        save_json(out / "status.json", status)
        proposals_path = stage / "proposals.json"
        if proposals_path.exists():
            proposals = json.loads(proposals_path.read_text())
        else:
            proposals, deliberation = agent.discover(program, diagnostics, history, config["task"], search.get("candidates_per_round", 2))
            save_json(stage / "deliberation.json", deliberation)
            save_json(proposals_path, proposals)
        continuation = {**settings, "epochs": int(search["candidate_epochs"])}
        dg_model, dg_transform, dg_training = fit_model(store, base_bundle, continuation, stage / "dg", seed+round_index+1, dg_model, dg_transform)
        dg_summary, _ = evaluate(store, base_bundle, dg_model, dg_transform, "validation")
        save_json(stage / "dg" / "validation.json", dg_summary)
        best = (program, bundle, model, transform, summary, diagnostics, checkpoint)
        best_score = _metric(summary, metric_name)
        records = []
        for label, proposed in [("weight_only", copy.deepcopy(program))] + [(f"program_{i+1}", p) for i,p in enumerate(proposals)]:
            folder = stage / label
            save_json(folder / "program.json", proposed)
            try:
                compiled = compiler.compile(proposed)
                inspection = inspect_program(store, compiled, backbone_ids, seed)
                save_json(folder / "feature_inspection.json", inspection)
                if inspection["invalid"]:
                    raise ProgramError("Noninformative or duplicate program inputs: " + json.dumps(inspection["invalid"]))
                if label != "weight_only" and set(compiled.input_ids) == set(bundle.input_ids):
                    raise ProgramError("No change to numeric input expressions")
                training_config = {**continuation, "backbone_input_ids": backbone_ids}
                trained_model, fitted, training = fit_model(store, compiled, training_config, folder, seed+round_index+1, model, transform)
                validation, feedback = evaluate(store, compiled, trained_model, fitted, "validation")
                save_json(folder / "validation.json", validation); save_json(folder / "diagnostics.json", feedback)
                record = {"round": round_index, "candidate": label, "status": "executed", "program": proposed["name"],
                          "selection_metric": metric_name,
                          "selection_score": _metric(validation, metric_name),
                          "delta_from_parent": _metric(validation, metric_name) - _metric(summary, metric_name),
                          "validation_cpc": validation["macro"].get("cpc"),
                          "validation_offdiagonal_cpc": validation["macro"].get("offdiagonal_cpc"),
                          "metrics": validation["macro"], "selected_epoch": training.get("selected_epoch"),
                          "training_seconds": training["elapsed_seconds"], "input_columns": len(compiled.input_ids)}
                if _metric(validation, metric_name) > best_score + float(search.get("min_improvement", 0.0001)):
                    best_score = _metric(validation, metric_name)
                    best = (proposed, compiled, trained_model, fitted, validation, feedback, folder / "model.pt")
            except ProgramError as error:
                record = {"round": round_index, "candidate": label, "status": "rejected", "reason": str(error)}
                save_json(folder / "rejection.json", record)
            records.append(record)
            print(json.dumps(record, ensure_ascii=True), flush=True)
        program, bundle, model, transform, summary, diagnostics, checkpoint = best
        weight = next((r for r in records if r["candidate"] == "weight_only" and r["status"] == "executed"), None)
        for record in records:
            if record["status"] == "executed" and weight:
                record["delta_from_weight_only"] = record["selection_score"] - weight["selection_score"]
        history.extend(records)
        save_json(stage / "selection.json", {"checkpoint": str(checkpoint.relative_to(out)), "validation": summary,
                                              "dg_validation": dg_summary, "candidates": records})
        save_json(out / "search_history.json", history)
        write_execution_report(out)
    save_json(out / "selected_program.json", program)
    save_json(out / "selected_feature_report.json", bundle.report)
    explanation = explain_validation(store, bundle, model, transform, out, program)
    usage = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0}
    for line in (out / "agents" / "agent_trace.jsonl").read_text(encoding="utf-8").splitlines():
        entry = json.loads(line); usage["calls"] += 1
        for key in ("prompt_tokens", "completion_tokens"): usage[key] += entry.get("usage", {}).get(key, 0)
    result = {"dataset": data.metadata.get("dataset"), "seed": seed, "checkpoint": str(checkpoint.relative_to(out)),
              "reference_validation": reference_summary, "dg_validation": dg_summary, "validation": summary,
              "heldout_evaluated": False, "agent_usage": usage, "program_terms": len(explanation["program_terms"]),
              "mass_prior": data.metadata.get("mass_prior"),
              "label_access_protocol": data.metadata.get("label_access_protocol", "Training/validation labels only; all map covariates available"),
              "input_transform": transform.to_dict()["transform"],
              "search_budget": search, "reference_training_seconds": reference_training["elapsed_seconds"],
              "interpretation": "Development on fixed training and validation tiles only. DG has the same continuation depth; agent search uses additional candidate fits and validation selections. No held-out or publication claim."}
    save_json(out / "result.json", result)
    save_json(out / "status.json", {"stage": "completed", "heldout_evaluated": False,
                                    "selection_metric": metric_name, "selection_score": _metric(summary, metric_name),
                                    "validation_cpc": summary["macro"].get("cpc"),
                                    "validation_offdiagonal_cpc": summary["macro"].get("offdiagonal_cpc")})
    report = write_execution_report(out)
    result["execution_report"] = {
        "execution_success": report["execution_success"]["success_rate_unique"],
        "n_failed_queries": report["execution_success"]["n_failed_unique"],
        "cartographer_repair_calls": report["repair_counts"]["cartographer_repair_calls"],
        "n_constant_duplicate_rejections": report["constant_duplicate_rejection"]["n_total"],
        "selected_program_size": report["selected_program_size"]["n_features"],
        "n_accepted_edits": report["accepted_edits"]["n_edits_kept_over_parent"],
        "no_selected_feature_rests_on_failed_measurement_only": report["pass"]["no_selected_feature_rests_on_failed_measurement_only"],
    }
    save_json(out / "result.json", result)
    print(json.dumps(result, ensure_ascii=True), flush=True)
    return result
