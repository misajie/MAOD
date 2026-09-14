"""Launch the original DeepGravity main.py without rewriting its trainer.

Missing optional imports (skmob, area) are stubbed only because the New York
tessellation already exists and `area` is unused. Training, sampling, loss,
checkpointing and the original evaluator remain the upstream files.
"""
from __future__ import annotations

import argparse
import json
import os
import runpy
import shutil
import sys
import time
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DGM = ROOT / "resources" / "deepgravity" / "deepgravity"
DEFAULT_OUT = ROOT / "runs" / "dgm_native_new_york"


def install_stubs():
    if "area" not in sys.modules:
        sys.modules["area"] = types.ModuleType("area")
    if "skmob" not in sys.modules:
        skmob = types.ModuleType("skmob")
        tess = types.ModuleType("skmob.tessellation")
        tilers = types.ModuleType("skmob.tessellation.tilers")

        class _Tiler:
            def get(self, *args, **kwargs):
                raise RuntimeError("original tessellation shapefile is present; tilers must not run")

        tilers.tiler = _Tiler()
        sys.modules["skmob"] = skmob
        sys.modules["skmob.tessellation"] = tess
        sys.modules["skmob.tessellation.tilers"] = tilers


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--epochs", type=int, default=20, help="Paper reports 20; argparse default is 15")
    p.add_argument("--batch-size", type=int, default=1, help="Paper reports 64; original collate only supports 1")
    p.add_argument("--seed", type=int, default=1234)
    p.add_argument("--device", default="gpu")
    p.add_argument("--skip-train", action="store_true")
    p.add_argument("--score-only", action="store_true")
    return p.parse_args()


def run_original(args, out: Path):
    install_stubs()
    (DGM / "results").mkdir(exist_ok=True)
    argv = [
        str(DGM / "main.py"),
        "--dataset", "new_york",
        "--oa-id-column", "GEOID",
        "--flow-origin-column", "geoid_o",
        "--flow-destination-column", "geoid_d",
        "--flow-flows-column", "pop_flows",
        "--epochs", str(args.epochs),
        "--batch_size", str(args.batch_size),
        "--seed", str(args.seed),
        "--device", args.device,
        "--mode", "train",
    ]
    write_json(out / "launch.json", {
        "cwd": str(DGM),
        "argv": argv,
        "note": "Original main.py. Paper text: 20 epochs, batch 64. This run uses the original DataLoader (batch_size=1 required for ragged tiles) and the paper epoch count unless overridden.",
        "stubs": ["area (unused import)", "skmob.tessellation.tilers (tessellation.shp already present)"],
        "code_unmodified": True,
    })
    sys.argv = argv
    started = time.perf_counter()
    os_cwd = Path.cwd()
    raised = None
    try:
        os.chdir(DGM)
        runpy.run_path(str(DGM / "main.py"), run_name="__main__")
    except Exception as exc:
        raised = repr(exc)
        (out / "original_evaluate_error.txt").write_text(raised, encoding="utf-8")
        print("ORIGINAL_MAIN_EXCEPTION", raised, flush=True)
    finally:
        os.chdir(os_cwd)
    elapsed = time.perf_counter() - started
    copied = []
    for name in ("model_DG_new_york.pt", "tile2cpc_DG_new_york.csv"):
        src = DGM / "results" / name
        if src.exists():
            shutil.copy2(src, out / name)
            copied.append(name)
    write_json(out / "timing.json", {
        "elapsed_seconds": elapsed, "epochs": args.epochs, "batch_size": args.batch_size,
        "original_exception": raised, "copied": copied,
    })
    if "model_DG_new_york.pt" not in copied:
        raise RuntimeError("original main.py did not write results/model_DG_new_york.pt")
    return elapsed


def score(out: Path):
    install_stubs()
    import os
    import numpy as np
    import pandas as pd
    import torch
    from importlib.machinery import SourceFileLoader

    os.chdir(DGM)
    utils = SourceFileLoader("dg_utils_native", str(DGM / "utils.py")).load_module()
    dgd = SourceFileLoader("dg_data_native", str(DGM / "data_loader.py")).load_module()

    db_dir = str(DGM / "data" / "new_york")
    tileid2oa2features2vals, oa_gdf, flow_df, oa2pop, oa2features, od2flow, oa2centroid = utils.load_data(
        db_dir, "tile_ID", "geometry", "GEOID", "geometry", "geoid_o", "geoid_d", "pop_flows"
    )
    oa2features = {oa: [np.log(oa2pop[oa])] + list(feats) for oa, feats in oa2features.items()}
    o2d2flow = {}
    for (o, d), f in od2flow.items():
        o2d2flow.setdefault(o, {})[d] = f

    test_tiles = pd.read_csv(DGM / "data/new_york/processed/test_tiles.csv", header=None, dtype=object)[0].astype(str).tolist()
    test_data = [oa for t in test_tiles for oa in tileid2oa2features2vals[str(t)].keys()]
    dataset = dgd.FlowDataset(test_data, tileid2oa2features2vals=tileid2oa2features2vals, o2d2flow=o2d2flow,
                              oa2features=oa2features, oa2pop=oa2pop, oa2centroid=oa2centroid,
                              dim_dests=int(1e9), frac_true_dest=0.0, model="DG")
    dim_input = len(dataset.get_features(test_data[0], test_data[0]))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = utils.instantiate_model(oa2centroid, oa2features, oa2pop, dim_input, device=device)
    ckpt = torch.load(out / "model_DG_new_york.pt", map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()

    loc2cpc_numerator = {}
    native_rows = []
    with torch.no_grad():
        for origin in test_data:
            tile = dataset.oa2tile[origin]
            dests = list(tileid2oa2features2vals[tile].keys())
            if not dests:
                continue
            x, y = dataset.get_X_T([origin], [dests])
            x, y = x.to(device), y.to(device)
            output = model.forward(x)
            cpc_num = model.get_cpc(x, y, numerator_only=True)
            loc2cpc_numerator[origin] = float(cpc_num)
            native_rows.append({
                "origin": origin, "tile": str(tile), "n_dest": len(dests),
                "cpc_numerator": float(cpc_num),
                "origin_full_outflow": float(sum(o2d2flow[origin].values()) if origin in o2d2flow else 1e-6),
            })

    edf = pd.DataFrame.from_dict(loc2cpc_numerator, columns=["cpc_num"], orient="index").reset_index().rename(columns={"index": "locID"})
    oa2tile = {oa: t for t, v in tileid2oa2features2vals.items() for oa in v.keys()}
    edf["tile"] = edf["locID"].map(oa2tile)
    edf["tot_flow"] = edf["locID"].map(lambda x: sum(o2d2flow[x].values()) if x in o2d2flow else 1e-6)
    tile_cpc = edf.groupby("tile", sort=False).apply(lambda g: g["cpc_num"].sum() / 2.0 / g["tot_flow"].sum(), include_groups=False)
    native = {
        "dim_input": dim_input,
        "n_test_origins_listed": len(test_data),
        "n_test_origins_scored": len(loc2cpc_numerator),
        "native_tile_cpc_mean": float(tile_cpc.mean()) if len(tile_cpc) else None,
        "native_tile_cpc_std": float(tile_cpc.std()) if len(tile_cpc) else None,
        "n_test_tiles_with_origins": int(tile_cpc.notna().sum()) if hasattr(tile_cpc, "notna") else int(len(tile_cpc)),
        "evaluator": "original get_cpc(numerator_only=True) then tile sum(cpc_num)/2/sum(tot_flow); tot_flow is full-table origin sum",
    }
    write_json(out / "native_tile_cpc.json", native)
    pd.DataFrame({"tile": tile_cpc.index.astype(str), "cpc": tile_cpc.values}).to_csv(out / "tile2cpc_recomputed.csv", index=False)
    pd.DataFrame(native_rows).to_csv(out / "origin_cpc_numerators.csv", index=False)

    # Common-support matrix CPC on this project's retained NY zones / splits.
    sys.path.insert(0, str(ROOT))
    from mapagents.data import load_dataset
    from mapagents.metrics import matrix_metrics, aggregate_metrics
    from mapagents.programs import haversine

    prepared = ROOT / "data" / "processed" / "new_york_dgm_mass"
    if not prepared.exists():
        prepared = ROOT / "data" / "processed" / "new_york"
    data = load_dataset(prepared)
    our_zones = set(data.zones.zone_id.astype(str))
    our_test_tiles = set(map(str, data.splits["test"]))
    records = []
    n_skipped = 0
    with torch.no_grad():
        for tile, z in data.zones.groupby("region_id", sort=False):
            tile = str(tile)
            if tile not in our_test_tiles:
                continue
            if tile not in tileid2oa2features2vals:
                n_skipped += 1
                continue
            orig_dests = list(tileid2oa2features2vals[tile].keys())
            our_ids = [str(x) for x in z.zone_id.tolist()]
            common = [oa for oa in orig_dests if oa in our_zones]
            if len(common) < 2:
                n_skipped += 1
                continue
            idx = {oa: i for i, oa in enumerate(orig_dests)}
            keep = [idx[oa] for oa in common]
            n = len(common)
            observed = np.zeros((n, n), dtype=np.float64)
            predicted = np.zeros((n, n), dtype=np.float64)
            geo = z.set_index(z.zone_id.astype(str))
            lon = geo.loc[common, "longitude"].to_numpy()
            lat = geo.loc[common, "latitude"].to_numpy()
            distances = haversine(lon[:, None], lat[:, None], lon[None, :], lat[None, :])
            for i, origin in enumerate(common):
                x, y = dataset.get_X_T([origin], [orig_dests])
                x = x.to(device)
                scores = model.forward(x).squeeze(-1)
                if scores.ndim == 1:
                    scores = scores.unsqueeze(0)
                logp = torch.log_softmax(scores, dim=-1)
                pred_full = torch.exp(logp)[0].detach().cpu().numpy()
                row_obs_full = np.array([float(o2d2flow.get(origin, {}).get(d, 0.0)) for d in orig_dests], dtype=np.float64)
                mass_full = float(row_obs_full.sum())
                observed[i] = row_obs_full[keep]
                predicted[i] = pred_full[keep] * mass_full
            records.append({"region_id": tile, **matrix_metrics(observed, predicted, distances, np.array(common), np.array(common))})
    summary = aggregate_metrics(records) if records else {}
    summary.update({
        "n_scored_tiles": len(records),
        "n_skipped_tiles": n_skipped,
        "prepared": str(prepared),
        "support": "original softmax over the full native tile; submatrix of dests retained in this project; predicted mass is the native row (tile-observed sum times softmax) sliced, not renormalized",
        "split": "this project's test tiles that also exist in the original JSON",
    })
    write_json(out / "common_support_matrix_metrics.json", summary)
    if records:
        pd.DataFrame(records).to_csv(out / "common_support_region_metrics.csv", index=False)
    print(json.dumps({"native": native, "common_support_macro": summary.get("macro")}, indent=2, default=str), flush=True)
    return native, summary


def main():
    args = parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if not args.score_only:
        run_original(args, out)
    score(out)


if __name__ == "__main__":
    main()
