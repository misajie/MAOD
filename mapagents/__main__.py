from __future__ import annotations
import argparse
import json
from pathlib import Path

from .settings import read_config
from .training import save_json


def main():
    parser = argparse.ArgumentParser(prog="mapagents", description="RAG spatial program discovery and Deep Gravity adaptation")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "run"):
        p = sub.add_parser(name); p.add_argument("--config", default="configs/new_york.yaml")
    p = sub.add_parser("prepare-generic")
    for key in ("zones", "flows", "features", "output"): p.add_argument("--"+key, required=True)
    p.add_argument("--splits"); p.add_argument("--seed", type=int, default=1234)
    p.add_argument("--target-only", action="store_true", help="Import a target-only dataset, including a single city, for predict/adapt")
    p = sub.add_parser("adapt")
    p.add_argument("--config", default="configs/new_york.yaml")
    p.add_argument("--source-run", required=True); p.add_argument("--output", required=True)
    p.add_argument("--budget", type=float, required=True)
    p = sub.add_parser("extract-osm")
    p.add_argument("--pbf", required=True); p.add_argument("--zones", required=True); p.add_argument("--output", required=True)
    p.add_argument("--buffer-m", type=float, default=3000)
    p = sub.add_parser("predict")
    p.add_argument("--data", required=True); p.add_argument("--checkpoint", required=True)
    p.add_argument("--program", required=True); p.add_argument("--output", required=True)
    p.add_argument("--split", choices=["train", "validation", "test"], default="test")
    p.add_argument("--device", default="cuda"); p.add_argument("--osm")
    p.add_argument("--row-splits", help="Adaptation row_splits.json, for scoring the exact same held-out rows")
    p = sub.add_parser("score")
    p.add_argument("--observed", required=True, help="NPZ containing observed and ordered IDs")
    p.add_argument("--predicted", required=True, help="NPZ containing predicted and ordered IDs")
    p.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command in {"run", "prepare", "adapt"}:
        from .pipeline import ensure_data, run, make_adaptation_splits
        cfg = read_config(args.config)
        if args.command == "prepare":
            data = ensure_data(cfg); print(json.dumps(data.metadata, indent=2, ensure_ascii=False)); return
        if args.command == "adapt":
            data = ensure_data(cfg)
            rows, budget = make_adaptation_splits(data, args.budget, cfg.get("seed", 1234))
            cfg["output_dir"] = str(Path(args.output).resolve()); cfg["adaptation"] = budget
            save_json(Path(cfg["output_dir"])/"row_splits.json", rows)
            return run(cfg, source_run=args.source_run, row_splits=rows)
        return run(cfg)
    if args.command == "prepare-generic":
        from .data import prepare_generic
        data = prepare_generic(Path(args.zones), Path(args.flows), Path(args.features), Path(args.output),
                               Path(args.splits) if args.splits else None, seed=args.seed, target_only=args.target_only)
        print(json.dumps(data.metadata, ensure_ascii=False, indent=2))
    elif args.command == "extract-osm":
        from .osm import extract_pbf
        print(json.dumps(extract_pbf(args.pbf, args.zones, args.output, args.buffer_m), ensure_ascii=False, indent=2))
    elif args.command == "predict":
        from .data import load_dataset
        from .programs import SpatialCompiler
        from .training import ODStore, load_checkpoint, evaluate
        data = load_dataset(Path(args.data))
        program = json.loads(Path(args.program).read_text(encoding="utf-8"))
        bundle = SpatialCompiler(data, args.osm).compile(program)
        model, transform, _ = load_checkpoint(args.checkpoint, args.device)
        if bundle.input_ids != model.input_ids: raise ValueError("Program and checkpoint semantic columns differ")
        row_splits = json.loads(Path(args.row_splits).read_text(encoding="utf-8")) if args.row_splits else None
        result, _ = evaluate(ODStore(data, row_splits=row_splits), bundle, model, transform, args.split, args.output)
        print(json.dumps(result, indent=2))
    elif args.command == "score":
        import numpy as np
        from .metrics import matrix_metrics
        with np.load(args.observed, allow_pickle=False) as a, np.load(args.predicted, allow_pickle=False) as b:
            for key in ("origin_ids", "destination_ids"):
                if key not in a or key not in b or not np.array_equal(a[key], b[key]):
                    raise ValueError(f"External prediction has mismatched or missing {key}; align explicitly before scoring")
            result = matrix_metrics(a["observed"], b["predicted"], origin_ids=a["origin_ids"], destination_ids=a["destination_ids"])
        save_json(args.output, result); print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
