"""GPU training, full-destination inference, and validation-only diagnostics."""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .contracts import ODData, FeatureBundle
from .metrics import matrix_metrics, aggregate_metrics
from .model import DeepGravity, FeatureTransform
from .programs import haversine, pair_features


def save_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


@dataclass
class Region:
    region_id: str
    global_indices: np.ndarray
    zone_ids: np.ndarray
    flows: np.ndarray
    distances: np.ndarray


class ODStore:
    def __init__(self, data: ODData, row_splits=None):
        self.data = data
        self.row_splits = {k: set(v) for k, v in row_splits.items()} if row_splits else None
        self.regions: dict[str, Region] = {}
        zone_to_region = data.zones.set_index("zone_id").region_id.to_dict()
        flows = data.flows.copy()
        flows["region_id"] = flows.origin.map(zone_to_region)
        flow_groups = {str(k): g for k, g in flows.groupby("region_id", sort=False)}
        for region_id, z in data.zones.groupby("region_id", sort=False):
            region_id = str(region_id)
            idx = z.index.to_numpy(dtype=int)
            ids = z.zone_id.astype(str).to_numpy()
            lookup = {k: i for i, k in enumerate(ids)}
            matrix = np.zeros((len(z), len(z)), dtype=np.float64)
            f = flow_groups.get(region_id)
            if f is not None:
                np.add.at(matrix, (f.origin.map(lookup).to_numpy(dtype=int), f.destination.map(lookup).to_numpy(dtype=int)), f.flow.to_numpy())
            lon, lat = z.longitude.to_numpy(), z.latitude.to_numpy()
            distances = haversine(lon[:, None], lat[:, None], lon[None, :], lat[None, :]).astype(np.float32)
            self.regions[region_id] = Region(region_id, idx, ids, matrix, distances)

    def examples(self, split, positive_only=False):
        examples = []
        region_ids = self.regions if self.row_splits else self.data.splits[split]
        for region_id in region_ids:
            region = self.regions[str(region_id)]
            for i, zone_id in enumerate(region.zone_ids):
                if self.row_splits is not None and zone_id not in self.row_splits[split]: continue
                if positive_only and region.flows[i].sum() <= 0: continue
                examples.append((str(region_id), i))
        return examples

    def rows_by_region(self, split):
        output = {}
        for r, i in self.examples(split): output.setdefault(r, []).append(i)
        return output


def raw_inputs(bundle, region, origins, destinations):
    origins, destinations = np.broadcast_arrays(np.asarray(origins), np.asarray(destinations))
    gi, gj = region.global_indices[origins], region.global_indices[destinations]
    distances = region.distances[origins, destinations]
    return np.concatenate([bundle.origin[gi], bundle.destination[gj], distances[..., None],
                           pair_features(bundle, gi, gj, distances)], axis=-1)


def fit_transform(store, bundle, seed, parent=None, limit=100000):
    rng = np.random.default_rng(seed)
    examples = store.examples("train", positive_only=True)
    if not examples: raise ValueError("Training split has no observed positive rows")
    rng.shuffle(examples)
    pieces = []; n = 0
    for r, i in examples:
        region = store.regions[r]
        dest = rng.choice(len(region.zone_ids), size=min(128, len(region.zone_ids), limit-n), replace=False)
        pieces.append(raw_inputs(bundle, region, np.full(len(dest), i), dest))
        n += len(dest)
        if n >= limit: break
    return FeatureTransform.fit(np.concatenate(pieces), bundle.input_ids, parent)


def load_checkpoint(path, device):
    saved = torch.load(path, map_location="cpu", weights_only=False)
    runtime_config = saved.get("training", {}).get("config", {})
    torch.set_num_threads(int(runtime_config.get("cpu_threads", 8)))
    if str(device).startswith("cuda"):
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    model = DeepGravity(saved["input_ids"], saved["hidden_sizes"], saved["dropout"])
    model.load_state_dict(saved["model_state_dict"])
    model.to(device)
    return model, FeatureTransform.from_dict(saved["feature_transform"]), saved


def fit_model(store, bundle, config, output_dir, seed, parent_model=None, parent_transform=None):
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    device = config.get("device", "cuda")
    if str(device).startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable. Run using the configured my-neuro Conda environment.")
    torch.set_num_threads(int(config.get("cpu_threads", 8)))
    if str(device).startswith("cuda"):
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    checkpoint = out / "model.pt"
    if checkpoint.exists():
        model, transform, saved = load_checkpoint(checkpoint, device)
        if model.input_ids != bundle.input_ids: raise ValueError(f"Checkpoint feature schema mismatch: {checkpoint}")
        return model, transform, saved["training"]
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    model = DeepGravity(bundle.input_ids, config.get("hidden_sizes"), config.get("dropout", 0.))
    transfer = model.transfer_from(parent_model) if parent_model else None
    model.to(device)
    transform = fit_transform(store, bundle, seed, parent_transform)
    optimizer = torch.optim.RMSprop(model.parameters(), lr=float(config.get("learning_rate", 5e-6)), momentum=float(config.get("momentum", .9)))
    examples = store.examples("train", positive_only=True)
    batch_size = int(config.get("batch_size", 64))
    sample_size = int(config.get("sample_destinations", 512))
    epochs = int(config.get("epochs", 20))
    history = []; started = time.perf_counter()
    for epoch in range(epochs):
        model.train()
        rng = np.random.default_rng(seed + epoch + 1)
        order = rng.permutation(len(examples))
        epoch_loss, epoch_mass, skipped = 0., 0., 0
        for start in range(0, len(order), batch_size):
            batch = [examples[x] for x in order[start:start+batch_size]]
            rows = []
            for r, i in batch:
                region = store.regions[r]
                dest = rng.choice(len(region.zone_ids), size=min(sample_size, len(region.zone_ids)), replace=False)
                target = region.flows[i, dest]
                if target.sum() <= 0:
                    skipped += 1; continue
                x = transform.transform(raw_inputs(bundle, region, np.full(len(dest), i), dest))
                rows.append((x, target))
            if not rows: continue
            max_dest = max(len(t) for _, t in rows)
            xbatch = np.zeros((len(rows), max_dest, len(bundle.input_ids)), dtype=np.float32)
            targets = np.zeros((len(rows), max_dest), dtype=np.float32)
            mask = np.zeros((len(rows), max_dest), dtype=bool)
            for b, (x, target) in enumerate(rows):
                xbatch[b, :len(target)] = x; targets[b, :len(target)] = target; mask[b, :len(target)] = True
            x = torch.as_tensor(xbatch, device=device)
            y = torch.as_tensor(targets, device=device)
            valid = torch.as_tensor(mask, device=device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(x).masked_fill(~valid, -1e9)
            logp = torch.log_softmax(logits, dim=-1)
            nll = -(y * logp).sum()
            if config.get("loss", "count_weighted") == "origin_mean":
                loss = -((y / y.sum(-1, keepdim=True)) * logp).sum(-1).mean()
            else:
                loss = nll / y.sum()
            if not torch.isfinite(loss): raise RuntimeError("Non-finite training objective")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), float(config.get("gradient_clip", 5.)))
            optimizer.step()
            epoch_loss += float(nll.detach()); epoch_mass += float(y.sum())
        record = {"epoch": epoch+1, "sampled_count_nll_per_trip": epoch_loss/max(epoch_mass, 1),
                  "sampled_flow_mass": epoch_mass, "zero_sample_rows_skipped": skipped,
                  "elapsed_seconds": time.perf_counter()-started}
        history.append(record)
        with (out / "training.jsonl").open("a", encoding="utf-8") as f: f.write(json.dumps(record) + "\n")
        print(f"{out.name}: epoch {epoch+1}/{epochs}, NLL={record['sampled_count_nll_per_trip']:.5f}, elapsed={record['elapsed_seconds']:.1f}s", flush=True)
    training = {"history": history, "elapsed_seconds": time.perf_counter()-started,
                "n_training_origins": len(examples), "seed": seed, "transfer": transfer, "config": config}
    torch.save({"model_state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                "input_ids": model.input_ids, "hidden_sizes": model.hidden_sizes, "dropout": model.dropout,
                "feature_transform": transform.to_dict(), "training": training}, checkpoint)
    save_json(out / "feature_transform.json", transform.to_dict())
    save_json(out / "feature_report.json", bundle.report)
    return model, transform, training


@torch.inference_mode()
def predict_region(model, transform, bundle, region, rows, origin_batch_size=16):
    model.eval(); device = next(model.parameters()).device
    n = len(region.zone_ids)
    predicted = np.empty((len(rows), n), dtype=np.float64)
    for start in range(0, len(rows), origin_batch_size):
        chosen = np.asarray(rows[start:start+origin_batch_size])
        x = raw_inputs(bundle, region, chosen[:, None], np.arange(n)[None, :])
        x = torch.as_tensor(transform.transform(x), device=device)
        scores = model(x).float().cpu().numpy().astype(np.float64)
        # Normalize complete rows in float64 on the CPU. This keeps output mass
        # conservation independent of accelerator softmax kernel variants.
        scores -= scores.max(axis=-1, keepdims=True)
        probs = np.exp(scores)
        probs /= probs.sum(axis=-1, keepdims=True)
        predicted[start:start+len(chosen)] = probs * region.flows[chosen].sum(axis=1, keepdims=True)
    return predicted


def evaluate(store, bundle, model, transform, split, output_dir=None):
    records = []; diagnostics = []
    if output_dir: Path(output_dir).mkdir(parents=True, exist_ok=True)
    for r, rows in store.rows_by_region(split).items():
        region = store.regions[r]
        pred = predict_region(model, transform, bundle, region, rows)
        truth = region.flows[rows]
        distances = region.distances[rows]
        metrics = matrix_metrics(truth, pred, distances, region.zone_ids[rows], region.zone_ids)
        record = {"region_id": r, **metrics}; records.append(record)
        if output_dir:
            np.savez_compressed(Path(output_dir)/f"region_{r}.npz", observed=truth, predicted=pred,
                                origin_ids=region.zone_ids[rows].astype(str), destination_ids=region.zone_ids.astype(str))
        if split != "test":
            errors = (truth-pred).sum(axis=0)
            order = np.argsort(np.abs(errors))[-3:][::-1]
            destination_errors = []
            for j in order:
                g = region.global_indices[j]
                vals = {c: float(store.data.base_features.iloc[g][c]) for c in store.data.base_features.columns}
                destination_errors.append({"zone_id": str(region.zone_ids[j]), "residual": float(errors[j]), "observed_features": vals})
            bins = [0, 1, 3, 10, 30, float("inf")]
            distance_errors = []
            for lo, hi in zip(bins[:-1], bins[1:]):
                mask = (distances >= lo) & (distances < hi)
                distance_errors.append({"distance_km": [lo, hi if np.isfinite(hi) else "inf"],
                                        "observed": float(truth[mask].sum()), "predicted": float(pred[mask].sum())})
            diagnostics.append({"region_id": r, "cpc": metrics["cpc"], "destinations": destination_errors, "distance_errors": distance_errors})
    summary = aggregate_metrics(records)
    summary["split"] = split
    if output_dir:
        save_json(Path(output_dir)/"metrics.json", summary)
        pd.DataFrame(records).to_csv(Path(output_dir)/"region_metrics.csv", index=False)
    diagnostics.sort(key=lambda x: x["cpc"] if x["cpc"] is not None else 1.)
    return summary, {"split": split, "summary": summary, "largest_error_regions": diagnostics[:6]}
