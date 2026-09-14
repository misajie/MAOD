"""New York main table on one support, with both CPC conventions."""
from __future__ import annotations

import json
import os
import sys
import types
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mapagents.data import load_dataset
from mapagents.metrics import aggregate_metrics, matrix_metrics
from mapagents.programs import SpatialCompiler, default_program
from mapagents.training import ODStore, evaluate, load_checkpoint, predict_region, save_json

DGM = ROOT / "resources" / "deepgravity" / "deepgravity"
OUT = ROOT / "runs" / "new_york_main_table"
DATA = ROOT / "data" / "processed" / "new_york_dgm_mass"


def enrich(observed, predicted, distances, origin_ids, destination_ids):
    record = matrix_metrics(observed, predicted, distances, origin_ids, destination_ids)
    off = np.asarray(origin_ids)[:, None] != np.asarray(destination_ids)[None, :]
    if off.any():
        record["offdiagonal_rmse"] = float(np.sqrt(np.mean(np.square(predicted - observed)[off])))
    return record


def native_tile_cpc(records, masses):
    """Original DGM tile CPC: sum_i 2 min / 2 / sum_i M_i, then unweighted tile mean."""
    tiles = []
    for rec in records:
        origin_ids = rec["origin_ids"]
        observed, predicted = rec["observed"], rec["predicted"]
        numer = 0.0
        denom = 0.0
        for i, oid in enumerate(origin_ids):
            if observed[i].sum() <= 0:
                continue
            numer += float(np.minimum(observed[i], predicted[i]).sum())
            denom += float(masses.get(str(oid), 0.0))
        tiles.append(numer / denom if denom > 0 else 0.0)
    arr = np.asarray(tiles, dtype=np.float64)
    return {"n_tiles": int(len(arr)), "mean": float(arr.mean()) if len(arr) else None,
            "std": float(arr.std(ddof=1)) if len(arr) > 1 else None, "n_zero": int((arr == 0).sum())}


def pack(name, records, masses, extra=None):
    summary = aggregate_metrics([{k: v for k, v in r.items() if k not in {"observed", "predicted", "origin_ids", "destination_ids"}} for r in records])
    native = native_tile_cpc(records, masses)
    row = {
        "model": name,
        "n_tiles": summary["n_regions"],
        "matrix_cpc": summary["macro"].get("cpc"),
        "offdiagonal_cpc": summary["macro"].get("offdiagonal_cpc"),
        "rmse": summary["macro"].get("rmse"),
        "offdiagonal_rmse": summary["macro"].get("offdiagonal_rmse"),
        "nrmse": summary["macro"].get("nrmse"),
        "observed_diagonal_share": summary["macro"].get("observed_diagonal_share"),
        "native_tile_cpc_mean": native["mean"],
        "native_tile_cpc_std": native["std"],
        "native_tile_cpc_n_zero": native["n_zero"],
        "totals": summary.get("totals"),
    }
    if extra:
        row.update(extra)
    return row, summary, native


def predict_gravity(store, split, masses, mass_exp, decay, kernel):
    records = []
    for region_id, rows in store.rows_by_region(split).items():
        if not len(rows):
            continue
        region = store.regions[region_id]
        m = np.array([masses[str(z)] for z in region.zone_ids], dtype=np.float64)
        dist = region.distances[rows]
        decay_term = dist if kernel == "exponential" else np.log1p(dist)
        scores = mass_exp * np.log(m)[None, :] - decay * decay_term
        logp = scores - logsumexp(scores, axis=1, keepdims=True)
        pred = np.exp(logp) * region.flows[rows].sum(axis=1, keepdims=True)
        rec = enrich(region.flows[rows], pred, dist, region.zone_ids[rows], region.zone_ids)
        rec.update({"observed": region.flows[rows], "predicted": pred,
                    "origin_ids": region.zone_ids[rows], "destination_ids": region.zone_ids})
        records.append(rec)
    return records


def fit_gravity(store, masses):
    best = None
    for kernel in ("exponential", "power"):
        def nll(theta):
            a, b = float(theta[0]), float(theta[1])
            loss = mass = 0.0
            for region_id, i in store.examples("train", True):
                region = store.regions[region_id]
                m = np.array([masses[str(z)] for z in region.zone_ids], dtype=np.float64)
                decay = region.distances[i] if kernel == "exponential" else np.log1p(region.distances[i])
                scores = a * np.log(m) - b * decay
                scores = scores - scores.max()
                logz = np.log(np.exp(scores).sum())
                y = region.flows[i]
                loss -= float((y * (scores - logz)).sum())
                mass += float(y.sum())
            return loss / max(mass, 1.0)
        fitted = minimize(nll, np.array([1.0, 0.05]), method="L-BFGS-B",
                          bounds=[(0.0, 8.0), (0.0, 20.0)])
        recs = predict_gravity(store, "validation", masses, float(fitted.x[0]), float(fitted.x[1]), kernel)
        score = aggregate_metrics([{k: v for k, v in r.items() if k not in {"observed", "predicted", "origin_ids", "destination_ids"}} for r in recs])["macro"]["cpc"]
        cand = {"kernel": kernel, "mass_exponent": float(fitted.x[0]), "decay": float(fitted.x[1]),
                "validation_cpc": score, "success": bool(fitted.success)}
        if best is None or score > best["validation_cpc"]:
            best = cand
        print("gravity", cand, flush=True)
    return best


def radiation_probs(masses, distances, origin):
    d = distances[origin]
    order = np.argsort(d, kind="mergesort")
    s = np.zeros(len(masses))
    acc = 0.0
    for j in order:
        s[j] = acc
        if j != origin:
            acc += masses[j]
    mi = masses[origin]
    p = mi * masses / ((mi + s) * (mi + s + masses) + 1e-30)
    z = p.sum()
    return p / z if z > 0 else np.full(len(masses), 1.0 / len(masses))


def predict_radiation(store, split, masses):
    records = []
    for region_id, rows in store.rows_by_region(split).items():
        if not len(rows):
            continue
        region = store.regions[region_id]
        m = np.array([masses[str(z)] for z in region.zone_ids], dtype=np.float64)
        pred = np.zeros((len(rows), len(region.zone_ids)), dtype=np.float64)
        for k, i in enumerate(rows):
            pred[k] = radiation_probs(m, region.distances, int(i)) * region.flows[i].sum()
        rec = enrich(region.flows[rows], pred, region.distances[rows], region.zone_ids[rows], region.zone_ids)
        rec.update({"observed": region.flows[rows], "predicted": pred,
                    "origin_ids": region.zone_ids[rows], "destination_ids": region.zone_ids})
        records.append(rec)
    return records


def predict_compiled(store, split, program, checkpoint):
    compiler = SpatialCompiler(store.data)
    bundle = compiler.compile(program)
    model, transform, _ = load_checkpoint(checkpoint, "cuda")
    summary, _ = evaluate(store, bundle, model, transform, split)
    records = []
    for region_id, rows in store.rows_by_region(split).items():
        if not len(rows) or len(store.regions[region_id].zone_ids) < 1:
            continue
        region = store.regions[region_id]
        pred = predict_region(model, transform, bundle, region, rows)
        rec = enrich(region.flows[rows], pred, region.distances[rows], region.zone_ids[rows], region.zone_ids)
        rec.update({"observed": region.flows[rows], "predicted": pred,
                    "origin_ids": region.zone_ids[rows], "destination_ids": region.zone_ids})
        records.append(rec)
    return records, summary


def predict_project_dg(store, split):
    return predict_compiled(store, split, default_program(store.data),
                            ROOT / "runs/new_york_grounded_mass/reference/model.pt")


def predict_mapagents(store, split, run_dir):
    run_dir = Path(run_dir)
    program = json.loads((run_dir / "selected_program.json").read_text(encoding="utf-8"))
    result = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    checkpoint = run_dir / str(result["checkpoint"]).replace("\\", "/")
    records, summary = predict_compiled(store, split, program, checkpoint)
    extra = {"checkpoint": str(checkpoint.relative_to(ROOT)), "program": program.get("name"),
             "n_features": len(program.get("features") or []),
             "selection_metric": result.get("execution_report")}
    return records, summary, extra


def install_stubs():
    if "area" not in sys.modules:
        sys.modules["area"] = types.ModuleType("area")
    if "skmob" not in sys.modules:
        skmob = types.ModuleType("skmob")
        tess = types.ModuleType("skmob.tessellation")
        tilers = types.ModuleType("skmob.tessellation.tilers")
        class T:
            def get(self, *a, **k):
                raise RuntimeError("tilers must not run")
        tilers.tiler = T()
        sys.modules["skmob"] = skmob
        sys.modules["skmob.tessellation"] = tess
        sys.modules["skmob.tessellation.tilers"] = tilers


def load_native():
    install_stubs()
    import torch
    from importlib.machinery import SourceFileLoader
    cwd = Path.cwd()
    os.chdir(DGM)
    try:
        utils = SourceFileLoader("dg_utils_native", str(DGM / "utils.py")).load_module()
        dgd = SourceFileLoader("dg_data_native", str(DGM / "data_loader.py")).load_module()
        db = str(DGM / "data" / "new_york")
        tileid2oa2features2vals, oa_gdf, flow_df, oa2pop, oa2features, od2flow, oa2centroid = utils.load_data(
            db, "tile_ID", "geometry", "GEOID", "geometry", "geoid_o", "geoid_d", "pop_flows")
        oa2pop = {str(k): float(v) for k, v in oa2pop.items()}
        oa2centroid = {str(k): v for k, v in oa2centroid.items()}
        oa2features = {str(oa): [np.log(oa2pop[str(oa)])] + list(feats) for oa, feats in oa2features.items()}
        o2d2flow = {}
        for (o, d), f in od2flow.items():
            o2d2flow.setdefault(str(o), {})[str(d)] = f
        tileid2oa2features2vals = {str(t): {str(oa): v for oa, v in entries.items()}
                                   for t, entries in tileid2oa2features2vals.items()}
        test_tiles = list(tileid2oa2features2vals)
        test_data = [oa for t in test_tiles for oa in tileid2oa2features2vals[t]]
        dataset = dgd.FlowDataset(test_data, tileid2oa2features2vals=tileid2oa2features2vals, o2d2flow=o2d2flow,
                                  oa2features=oa2features, oa2pop=oa2pop, oa2centroid=oa2centroid,
                                  dim_dests=int(1e9), frac_true_dest=0.0, model="DG")
        dim = len(dataset.get_features(test_data[0], test_data[0]))
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = utils.instantiate_model(oa2centroid, oa2features, oa2pop, dim, device=device)
        ckpt = torch.load(ROOT / "runs/dgm_native_new_york/model_DG_new_york.pt", map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model_state_dict"])
        model.to(device)
        model.eval()
        return model, dataset, device
    finally:
        os.chdir(cwd)


def predict_native(store, split, model, dataset, device):
    import torch
    records = []
    skipped = 0
    with torch.no_grad():
        for region_id, rows in store.rows_by_region(split).items():
            if not len(rows):
                continue
            region = store.regions[region_id]
            dests = [str(z) for z in region.zone_ids]
            if any(oa not in dataset.oa2features for oa in dests):
                skipped += 1
                continue  # keep dest support identical across methods on scored tiles
            pred = np.zeros((len(rows), len(dests)), dtype=np.float64)
            keep = []
            for k, i in enumerate(rows):
                origin = str(region.zone_ids[i])
                if origin not in dataset.oa2features:
                    continue
                x, _ = dataset.get_X_T([origin], [dests])
                scores = model.forward(x.to(device)).squeeze(-1)
                if scores.ndim == 1:
                    scores = scores.unsqueeze(0)
                p = torch.softmax(scores, dim=-1)[0].detach().cpu().numpy()
                pred[k] = p * region.flows[i].sum()
                keep.append(k)
            if not keep:
                skipped += 1
                continue
            keep = np.asarray(keep)
            rec = enrich(region.flows[rows][keep], pred[keep], region.distances[rows][keep],
                         region.zone_ids[rows][keep], region.zone_ids)
            rec.update({"observed": region.flows[rows][keep], "predicted": pred[keep],
                        "origin_ids": region.zone_ids[rows][keep], "destination_ids": region.zone_ids})
            records.append(rec)
    return records, skipped


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapagents-run", default="")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_dataset(DATA)
    store = ODStore(data)
    masses = {str(i): float(v) for i, v in data.base_features["dgm_mass"].items()}
    rows = []
    details = {}

    print("fitting gravity on dgm_mass", flush=True)
    gfit = fit_gravity(store, masses)
    grec = predict_gravity(store, "test", masses, gfit["mass_exponent"], gfit["decay"], gfit["kernel"])
    grow, gsum, gnat = pack("Gravity", grec, masses, extra={"fit": gfit, "mass": "dgm_mass"})
    rows.append(grow); details["Gravity"] = {"summary": gsum, "native_tile": gnat, "fit": gfit}

    print("scoring radiation", flush=True)
    rrec = predict_radiation(store, "test", masses)
    rrow, rsum, rnat = pack("Radiation", rrec, masses, extra={"mass": "dgm_mass", "form": "Simini 2012 intervening opportunities, self included"})
    rows.append(rrow); details["Radiation"] = {"summary": rsum, "native_tile": rnat}

    print("scoring mapagents/training.py DG reference", flush=True)
    if args.mapagents_run and (Path(args.mapagents_run) / "reference" / "model.pt").exists():
        dg_ckpt = Path(args.mapagents_run) / "reference" / "model.pt"
        prec, pheld = predict_compiled(store, "test", default_program(store.data), dg_ckpt)
        dg_note = "same run as MapAgents; checkpoint selected on the configured training.selection_metric"
    else:
        dg_ckpt = ROOT / "runs/new_york_grounded_mass/reference/model.pt"
        prec, pheld = predict_project_dg(store, "test")
        dg_note = "15-layer network, signed-log1p; not original main.py"
    prow, psum, pnat = pack("Deep Gravity (mapagents/training.py)", prec, masses,
                            extra={"checkpoint": str(dg_ckpt.relative_to(ROOT)).replace("\\", "/"), "note": dg_note})
    rows.append(prow); details["Deep Gravity (mapagents/training.py)"] = {"summary": psum, "native_tile": pnat, "evaluate": pheld}

    print("scoring native DGM", flush=True)
    model, dataset, device = load_native()
    nrec, skipped = predict_native(store, "test", model, dataset, device)
    nrow, nsum, nnat = pack("Deep Gravity (original main.py)", nrec, masses,
                            extra={"checkpoint": "runs/dgm_native_new_york/model_DG_new_york.pt",
                                   "skipped_tiles": skipped, "softmax": "our retained destinations in each test tile"})
    rows.append(nrow); details["Deep Gravity (original main.py)"] = {"summary": nsum, "native_tile": nnat, "skipped_tiles": skipped}

    if args.mapagents_run:
        print("scoring MapAgents", args.mapagents_run, flush=True)
        mrec, mheld, mextra = predict_mapagents(store, "test", args.mapagents_run)
        n_added = sum(1 for f in json.loads((Path(args.mapagents_run) / "selected_program.json").read_text(encoding="utf-8")).get("features", [])
                      if f.get("mechanism") != "Supplied public geographic covariate")
        mrow, msum, mnat = pack("MapAgents + DG", mrec, masses, extra={**mextra, "n_agent_added_features": n_added})
        rows.append(mrow)
        details["MapAgents + DG"] = {"summary": msum, "native_tile": mnat, "evaluate": mheld, **mextra}
    else:
        mapagents = dict(prow)
        mapagents["model"] = "MapAgents + DG"
        mapagents["note"] = "No MapAgents run supplied."
        rows.append(mapagents)

    save_json(OUT / "main_table.json", rows)
    save_json(OUT / "details.json", {"protocol": {
        "data": str(DATA),
        "split": "this project's test tiles",
        "matrix_cpc": "equal-tile mean of 2 sum min / (sum obs + sum pred) on internal-tile matrices",
        "native_tile_cpc": "equal-tile mean of sum_i sum_j min / sum_i dgm_mass_i ; dgm_mass is the full-table origin sum, including out-of-tile flow",
        "why_they_differ": "Native DGM paper/code CPC divides overlap by full-table origin outflow. Matrix CPC divides by internal observed+predicted mass. Diagonal share is ~0.88 of internal mass, which inflates matrix CPC.",
        "mlp_raw_osm": "not run",
    }, "rows": rows})
    print(json.dumps(rows, indent=2, default=str), flush=True)


if __name__ == "__main__":
    main()
