"""Resumable feature-program discovery and joint parameter adaptation."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import torch

from .agents import AgentSystem
from .data import load_dataset, prepare_deepgravity
from .programs import SpatialCompiler, default_program, ProgramError
from .metrics import selection_score
from .training import ODStore, fit_model, evaluate, save_json, load_checkpoint


def ensure_data(config):
    d = config["data"]
    prepared = Path(d["prepared"])
    if (prepared / "metadata.json").exists(): return load_dataset(prepared)
    if d.get("format", "deepgravity") != "deepgravity":
        raise ValueError("Prepare custom data with 'mapagents prepare-generic' before running")
    return prepare_deepgravity(Path(d["source"]), prepared,
                               seed=int(config.get("seed", 1234)),
                               validation_fraction=float(d.get("validation_fraction", .2)))


def _score(summary, metric="cpc"):
    return selection_score(summary, metric)


def run(config, *, source_run=None, row_splits=None):
    output = Path(config["output_dir"])
    output.mkdir(parents=True, exist_ok=True)
    config_path = output / "config.json"
    if config_path.exists():
        previous = json.loads(config_path.read_text(encoding="utf-8"))
        if previous != config: raise ValueError("Output directory contains another configuration. Choose a new output_dir.")
    else: save_json(config_path, config)
    completed = output / "result.json"
    if completed.exists():
        print(f"Completed run already exists: {completed}", flush=True)
        return json.loads(completed.read_text(encoding="utf-8"))
    data = ensure_data(config)
    store = ODStore(data, row_splits=row_splits)
    if not store.examples("train", positive_only=True) or not store.examples("validation", positive_only=True):
        raise ValueError("Training and validation require positive observed origins")
    compiler = SpatialCompiler(data, config["data"].get("osm_path"), config["data"].get("spatial_cache", output / "spatial_cache"))
    if store.row_splits is not None:
        save_json(output / "row_splits.json", {k: sorted(v) for k, v in store.row_splits.items()})
    seed = int(config.get("seed", 1234))
    training_config = config["training"]
    metric_name = str(training_config.get("selection_metric", "cpc"))
    catalog, profile = compiler.catalog(), compiler.profile()
    save_json(output / "map_profile.json", profile)
    save_json(output / "dataset_metadata.json", data.metadata)
    source_model = source_transform = None
    if source_run:
        source_run = Path(source_run)
        source_result = json.loads((source_run / "result.json").read_text(encoding="utf-8"))
        current_program = json.loads((source_run / "selected_program.json").read_text(encoding="utf-8"))
        source_model, source_transform, _ = load_checkpoint(source_run / source_result["checkpoint"].replace("\\", "/"), training_config["device"])
    else:
        current_program = default_program(data)
    reference = output / "reference"
    save_json(reference / "program.json", current_program)
    current_bundle = compiler.compile(current_program)
    current_model, current_transform, _ = fit_model(store, current_bundle, training_config, reference, seed,
                                                    source_model, source_transform)
    current_summary, current_diagnostics = evaluate(store, current_bundle, current_model, current_transform, "validation")
    save_json(reference / "validation.json", current_summary)
    save_json(reference / "diagnostics.json", current_diagnostics)
    current_checkpoint = reference / "model.pt"
    history = [{"stage": "reference", "selection_metric": metric_name,
                "selection_score": _score(current_summary, metric_name),
                "validation_cpc": current_summary["macro"].get("cpc"),
                "validation_offdiagonal_cpc": current_summary["macro"].get("offdiagonal_cpc"),
                "program": current_program["name"],
                "input_columns": len(current_bundle.input_ids)}]
    print(f"Reference {metric_name}={_score(current_summary, metric_name):.6f} matrix_cpc={current_summary['macro'].get('cpc')}", flush=True)
    search = config.get("search", {})
    agent = None
    if search.get("enabled", True):
        agent = AgentSystem(config["llm"], Path(config["rag_root"]), output / "agents")
        for round_index in range(int(search.get("rounds", 2)) + 1):
            stage = output / f"round_{round_index:02d}"
            stage.mkdir(parents=True, exist_ok=True)
            proposal_file = stage / "proposals.json"
            if proposal_file.exists():
                proposals = json.loads(proposal_file.read_text(encoding="utf-8"))
            elif round_index == 0:
                proposals = [agent.initial_program(catalog, profile, current_program, config["task"])]
                save_json(proposal_file, proposals)
            else:
                proposals = agent.propose(catalog, profile, current_program, current_diagnostics, history,
                                          config["task"], count=int(search.get("candidates_per_round", 2)))
                save_json(proposal_file, proposals)
            # A weight-only continuation has the same per-candidate training
            # opportunity and starts from the same parent checkpoint.
            candidates = [("weight_only", copy.deepcopy(current_program))] + [
                (f"program_{i+1}", p) for i, p in enumerate(proposals)]
            stage_records = []
            best = (current_program, current_bundle, current_model, current_transform, current_summary,
                    current_diagnostics, current_checkpoint)
            best_score = _score(current_summary, metric_name)
            candidate_config = {**training_config, "epochs": int(search.get("candidate_epochs", 5))}
            for label, program in candidates:
                folder = stage / label
                save_json(folder / "program.json", program)
                try:
                    bundle = compiler.compile(program)
                    if label != "weight_only" and set(bundle.input_ids) == set(current_bundle.input_ids):
                        record = {"round": round_index, "candidate": label, "status": "rejected",
                                  "reason": "Candidate has the same numeric feature expressions as the parent"}
                        save_json(folder / "rejection.json", record)
                        stage_records.append(record)
                        continue
                    model, transform, trained = fit_model(store, bundle, candidate_config, folder,
                                                         seed + round_index + 1, current_model, current_transform)
                    summary, diagnostics = evaluate(store, bundle, model, transform, "validation")
                    score = _score(summary, metric_name)
                    save_json(folder / "validation.json", summary)
                    save_json(folder / "diagnostics.json", diagnostics)
                    record = {"round": round_index, "candidate": label, "name": program.get("name"),
                              "selection_metric": metric_name, "selection_score": score,
                              "delta_from_parent": score - _score(current_summary, metric_name),
                              "validation_cpc": summary["macro"].get("cpc"),
                              "validation_offdiagonal_cpc": summary["macro"].get("offdiagonal_cpc"),
                              "input_columns": len(bundle.input_ids), "training_seconds": trained["elapsed_seconds"],
                              "transfer": trained.get("transfer"), "status": "executed"}
                    print(f"Round {round_index} {label}: {metric_name}={score:.6f} matrix_cpc={summary['macro'].get('cpc')}", flush=True)
                    if score > best_score + float(search.get("min_improvement", 0.)):
                        best_score = score
                        best = (program, bundle, model, transform, summary, diagnostics, folder / "model.pt")
                except ProgramError as e:
                    record = {"round": round_index, "candidate": label, "status": "rejected", "reason": str(e)}
                    save_json(folder / "rejection.json", record)
                stage_records.append(record)
            current_program, current_bundle, current_model, current_transform, current_summary, current_diagnostics, current_checkpoint = best
            history.extend(stage_records)
            save_json(stage / "selection.json", {"checkpoint": current_checkpoint.relative_to(output).as_posix(),
                                                   "selection_metric": metric_name, "selection_score": best_score,
                                                   "candidates": stage_records})
            save_json(output / "search_history.json", history)
    # Selection finishes before any test prediction or score is requested.
    save_json(output / "selected_program.json", current_program)
    save_json(output / "selected_feature_report.json", current_bundle.report)
    final_summary, _ = evaluate(store, current_bundle, current_model, current_transform, "test", output / "predictions")
    all_usage = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "seconds": 0.}
    trace = output / "agents" / "agent_trace.jsonl"
    if trace.exists():
        for line in trace.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line); usage = entry.get("usage", {})
            all_usage["calls"] += 1
            all_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
            all_usage["completion_tokens"] += usage.get("completion_tokens", 0)
            all_usage["seconds"] += entry.get("elapsed_seconds", 0.)
    result = {"task": config["task"], "dataset": data.metadata.get("dataset"),
              "input_mode": current_bundle.report["input_mode"],
              "checkpoint": current_checkpoint.relative_to(output).as_posix(),
              "validation": current_summary, "held_out": final_summary,
              "selected_program": current_program.get("name"), "input_columns": len(current_bundle.input_ids),
              "agent_usage_this_invocation": agent.usage if agent else None,
              "agent_usage_including_resumed_calls": all_usage,
              "source_run": str(source_run) if source_run else None,
              "row_budget": config.get("adaptation"),
              "interpretation": data.metadata.get("prediction_target", "Execution on the supplied public movement example; not an original-paper reproduction.")}
    save_json(completed, result)
    print(f"Held-out {metric_name}={_score(final_summary, metric_name):.6f} matrix_cpc={final_summary['macro'].get('cpc')}\nRun artifacts: {output}", flush=True)
    return result


def make_adaptation_splits(data, budget, seed=1234, validation_fraction=.25, regions=None):
    """Budget includes both target fit and target validation rows."""
    if not 0 < budget < 1: raise ValueError("Adaptation budget must be strictly between 0 and 1")
    regions = set(regions or data.splits["test"])
    target_ids = data.zones.loc[data.zones.region_id.isin(regions), "zone_id"].astype(str).tolist()
    positive = set(data.flows.groupby("origin").flow.sum().loc[lambda s: s > 0].index)
    candidates = np.asarray([z for z in target_ids if z in positive], dtype=object)
    n = int(np.floor(len(candidates) * budget))
    if n < 2: raise ValueError(f"Budget supplies {n} positive origins; at least two are needed for target train/validation")
    rng = np.random.default_rng(seed)
    rng.shuffle(candidates)
    support = candidates[:n].tolist()
    n_val = max(1, min(n-1, int(round(n*validation_fraction))))
    validation, train = support[:n_val], support[n_val:]
    support_set = set(support)
    splits = {"train": train, "validation": validation, "test": [z for z in target_ids if z not in support_set]}
    visible = data.flows.loc[data.flows.origin.isin(support_set)]
    zone_count = data.zones.groupby("region_id").size().to_dict()
    id_region = data.zones.set_index("zone_id").region_id.to_dict()
    budget_report = {"fraction_of_positive_target_origins": budget, "target_positive_origins": len(candidates),
                     "visible_origins": n, "fit_origins": len(train), "validation_origins": len(validation),
                     "visible_nonzero_edges": int((visible.flow > 0).sum()),
                     "visible_cells": sum(int(zone_count[id_region[z]]) for z in support),
                     "observed_row_totals_available_for_output_scaling": True,
                     "all_program_selection_labels_included": True, "seed": seed}
    return splits, budget_report
