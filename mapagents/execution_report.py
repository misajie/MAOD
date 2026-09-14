"""Automatic execution report required by the proposal §9.1.

Failed map measurements cannot support a feature merely because the request
appears in a trace. Coverage uses successful `map:` evidence IDs only.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .training import save_json


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path):
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _is_base(feature: dict) -> bool:
    return feature.get("mechanism") == "Supplied public geographic covariate"


def _query_index(rows: list[dict]) -> dict[str, dict]:
    by_id = {}
    for row in rows:
        key = row.get("id")
        if not key:
            continue
        previous = by_id.get(key)
        if previous is None or ("error" in previous and "error" not in row):
            by_id[key] = row
    return by_id


def _feature_coverage(feature: dict, successful: set[str], failed: set[str]) -> dict:
    evidence = [str(x) for x in feature.get("evidence") or []]
    map_ids = [e for e in evidence if e.startswith("map:")]
    supplied = [e for e in evidence if not e.startswith("map:")]
    ok = [e for e in map_ids if e in successful]
    bad = [e for e in map_ids if e in failed or e not in successful]
    agent_added = not _is_base(feature)
    supported = (not agent_added) or bool(ok)
    if agent_added and bad and not ok:
        supported = False
    return {
        "name": feature.get("name"),
        "scope": feature.get("scope"),
        "hypothesis_id": feature.get("hypothesis_id"),
        "n_evidence": len(evidence),
        "n_map_evidence": len(map_ids),
        "n_successful_map_evidence": len(ok),
        "n_failed_or_unknown_map_evidence": len(bad),
        "successful_map_ids": ok,
        "failed_or_unknown_map_ids": bad,
        "supplied_evidence_ids": supplied,
        "supported_by_successful_measurement": supported,
        "agent_added": agent_added,
    }


def _rejection_kind(reason) -> str:
    text = json.dumps(reason, ensure_ascii=False) if not isinstance(reason, str) else reason
    lowered = text.lower()
    if "duplicate" in lowered or "numerically duplicates" in lowered:
        return "duplicate"
    if "constant" in lowered or "cancels in row softmax" in lowered or "origin-only" in lowered:
        return "constant"
    return "other"


def collect_execution_report(run_dir) -> dict:
    run_dir = Path(run_dir)
    queries = _jsonl(run_dir / "agents" / "evidence_queries.jsonl")
    traces = _jsonl(run_dir / "agents" / "agent_trace.jsonl")
    by_id = _query_index(queries)
    successful = {k for k, v in by_id.items() if "error" not in v}
    failed = {k for k, v in by_id.items() if "error" in v}
    by_type = Counter((row.get("request") or {}).get("type", "unknown") for row in queries)
    failed_by_type = Counter((row.get("request") or {}).get("type", "unknown") for row in queries if "error" in row)

    cartographer = [t for t in traces if t.get("role") == "Cartographer"]
    repair_calls = [t for t in cartographer if isinstance(t.get("input"), dict) and t["input"].get("executor_errors")]
    roles = Counter(t.get("role") for t in traces)

    constant_duplicate = []
    candidate_status = []
    for selection_path in sorted(run_dir.glob("round_*/selection.json")):
        round_dir = selection_path.parent
        selection = _read_json(selection_path)
        for record in selection.get("candidates", []):
            candidate_status.append({"round": round_dir.name, **{k: record.get(k) for k in
                                    ("candidate", "status", "program", "reason", "validation_cpc")}})
            folder = round_dir / record["candidate"]
            inspection_path = folder / "feature_inspection.json"
            if inspection_path.exists():
                inspection = _read_json(inspection_path)
                for item in inspection.get("invalid") or []:
                    constant_duplicate.append({"round": round_dir.name, "candidate": record["candidate"],
                                               "kind": _rejection_kind(item.get("reason") or item), **item})
            rejection_path = folder / "rejection.json"
            if rejection_path.exists() and record.get("status") == "rejected":
                reason = record.get("reason") or _read_json(rejection_path).get("reason")
                constant_duplicate.append({"round": round_dir.name, "candidate": record["candidate"],
                                           "kind": _rejection_kind(reason), "reason": reason})

    for deliberation_path in sorted(run_dir.glob("round_*/deliberation.json")):
        deliberation = _read_json(deliberation_path)
        for mechanism in deliberation.get("compiled_mechanisms") or []:
            for item in mechanism.get("executor_rejected_templates") or []:
                constant_duplicate.append({"round": deliberation_path.parent.name, "stage": "surveyor_template",
                                           "kind": "other", **item})
        for item in deliberation.get("survey", {}).get("rejected_hypotheses") or []:
            constant_duplicate.append({"round": deliberation_path.parent.name, "stage": "surveyor_hypothesis",
                                       "kind": "other", **item})

    selected_path = run_dir / "selected_program.json"
    selected_program = _read_json(selected_path) if selected_path.exists() else None
    if selected_program is None:
        last = sorted(run_dir.glob("round_*/selection.json"))
        if last:
            checkpoint = _read_json(last[-1]).get("checkpoint", "")
            relative = Path(str(checkpoint).replace("\\", "/"))
            if "reference" in relative.parts:
                ref = run_dir / "reference" / "program.json"
                selected_program = _read_json(ref) if ref.exists() else None
            else:
                program_file = run_dir / relative.parent / "program.json"
                selected_program = _read_json(program_file) if program_file.exists() else None
        elif (run_dir / "reference" / "program.json").exists():
            selected_program = _read_json(run_dir / "reference" / "program.json")

    features = list((selected_program or {}).get("features") or [])
    coverage = [_feature_coverage(f, successful, failed) for f in features]
    added = [c for c in coverage if c["agent_added"]]
    unsupported = [c for c in added if not c["supported_by_successful_measurement"]]
    candidate_coverage = []
    for folder in sorted(run_dir.glob("round_*/program_*")):
        program_path = folder / "program.json"
        if not program_path.exists():
            continue
        candidate_program = _read_json(program_path)
        rows = [_feature_coverage(f, successful, failed) for f in candidate_program.get("features") or [] if not _is_base(f)]
        candidate_coverage.append({
            "round": folder.parent.name, "candidate": folder.name,
            "program": candidate_program.get("name"),
            "n_agent_added": len(rows),
            "n_unsupported": sum(1 for r in rows if not r["supported_by_successful_measurement"]),
            "features": rows,
        })
    accepted = [r for r in candidate_status if r.get("status") == "executed"
                and r.get("candidate", "").startswith("program_")
                and (r.get("validation_cpc") is not None)]
    kept_edits = []
    parent_cpc = None
    history = _read_json(run_dir / "search_history.json") if (run_dir / "search_history.json").exists() else []
    for record in history:
        if record.get("candidate") == "weight_only" and record.get("status") == "executed":
            parent_cpc = record.get("validation_cpc")
        if record.get("status") == "executed" and str(record.get("candidate", "")).startswith("program_"):
            delta = record.get("delta_from_parent")
            if delta is None:
                continue
            if delta > 0:
                kept_edits.append({"round": record.get("round"), "candidate": record.get("candidate"),
                                   "program": record.get("program"), "delta_from_parent": record.get("delta_from_parent")})

    kinds = Counter(item.get("kind") for item in constant_duplicate)
    report = {
        "run_dir": str(run_dir),
        "rule": "Failed measurements cannot support a feature simply because their request appears in a trace.",
        "execution_success": {
            "n_query_records": len(queries),
            "n_unique_query_ids": len(by_id),
            "n_successful_unique": len(successful),
            "n_failed_unique": len(failed),
            "success_rate_unique": (len(successful) / len(by_id)) if by_id else None,
            "records_by_type": dict(by_type),
            "failed_records_by_type": dict(failed_by_type),
            "failed_queries": [{"id": k, "type": (by_id[k].get("request") or {}).get("type"),
                                "error": by_id[k].get("error")} for k in sorted(failed)],
        },
        "repair_counts": {
            "cartographer_calls": len(cartographer),
            "cartographer_repair_calls": len(repair_calls),
            "llm_calls_by_role": dict(roles),
        },
        "successful_measurement_coverage": {
            "selected_program_name": (selected_program or {}).get("name"),
            "n_selected_features": len(features),
            "n_agent_added_features": len(added),
            "n_agent_added_with_successful_map_evidence": sum(1 for c in added if c["n_successful_map_evidence"] > 0),
            "n_agent_added_unsupported": len(unsupported),
            "coverage_rate_agent_added": (sum(1 for c in added if c["supported_by_successful_measurement"]) / len(added)) if added else None,
            "features": coverage,
            "unsupported_selected_features": unsupported,
            "executed_candidate_programs": candidate_coverage,
        },
        "constant_duplicate_rejection": {
            "n_total": len(constant_duplicate),
            "n_constant": int(kinds.get("constant", 0)),
            "n_duplicate": int(kinds.get("duplicate", 0)),
            "n_other": int(kinds.get("other", 0)),
            "items": constant_duplicate,
        },
        "selected_program_size": {
            "n_features": len(features),
            "n_base_features": sum(1 for f in features if _is_base(f)),
            "n_agent_added_features": len(added),
            "name": (selected_program or {}).get("name"),
        },
        "accepted_edits": {
            "n_program_candidates_executed": len(accepted),
            "n_edits_kept_over_parent": len(kept_edits),
            "kept": kept_edits,
            "candidate_status": candidate_status,
        },
        "pass": {
            "no_selected_feature_rests_on_failed_measurement_only": len(unsupported) == 0,
            "report_complete": bool(by_id or features or traces),
        },
    }
    return report


def write_execution_report(run_dir) -> dict:
    run_dir = Path(run_dir)
    report = collect_execution_report(run_dir)
    save_json(run_dir / "execution_report.json", report)
    return report
