"""Matrix metrics over an explicit common origin/destination support."""
from __future__ import annotations

from typing import Any, Iterable

import numpy as np


def _ratio(numerator: float, denominator: float) -> float | None:
    return float(numerator / denominator) if denominator > 0 else None


def matrix_metrics(observed: np.ndarray, predicted: np.ndarray,
                   distances_km: np.ndarray | None = None,
                   origin_ids=None, destination_ids=None) -> dict[str, Any]:
    """Compute metrics without silently renormalizing predictions.

    Include all cells and the diagonal if present. Zero observed rows are
    excluded from macro origin CPC and row JSD because they contain no observed
    destination distribution; their predicted mass remains in matrix errors.
    If a positive observed row has zero predicted mass, its JSD is ln(2), the
    maximal value (an explicit missing-prediction penalty). JSD uses natural
    logarithms. Undefined ratios/correlations are JSON-safe None.
    """
    observed = np.asarray(observed, dtype=np.float64)
    predicted = np.asarray(predicted, dtype=np.float64)
    if observed.ndim != 2 or observed.shape != predicted.shape or 0 in observed.shape:
        raise ValueError("Observed/predicted must be nonempty two-dimensional matrices of the same shape")
    if not np.isfinite(observed).all() or not np.isfinite(predicted).all():
        raise ValueError("Metric inputs must be finite")
    if (observed < 0).any() or (predicted < 0).any():
        raise ValueError("OD flows must be nonnegative")
    truth_total, prediction_total = float(observed.sum()), float(predicted.sum())
    row_truth, row_prediction = observed.sum(axis=1), predicted.sum(axis=1)
    active = row_truth > 0
    error = predicted - observed
    rmse = float(np.sqrt(np.mean(np.square(error))))
    std = float(observed.std())
    log_truth, log_prediction = np.log1p(observed).ravel(), np.log1p(predicted).ravel()
    log_correlation = None
    if log_truth.size > 1 and log_truth.std() > 0 and log_prediction.std() > 0:
        log_correlation = float(np.corrcoef(log_truth, log_prediction)[0, 1])
    macro_cpc = None
    jsd = None
    if active.any():
        overlaps = 2 * np.minimum(observed[active], predicted[active]).sum(axis=1)
        macro_cpc = float(np.mean(overlaps / (row_truth[active] + row_prediction[active])))
        p = observed[active] / row_truth[active, None]
        q = np.divide(predicted[active], row_prediction[active, None],
                      out=np.zeros_like(predicted[active]), where=row_prediction[active, None] > 0)
        middle = 0.5 * (p + q)
        # Only positive probabilities contribute; no epsilon distorts the distributions.
        p_term, q_term = np.zeros_like(p), np.zeros_like(q)
        p_mask, q_mask = p > 0, q > 0
        p_term[p_mask] = p[p_mask] * np.log(p[p_mask] / middle[p_mask])
        q_term[q_mask] = q[q_mask] * np.log(q[q_mask] / middle[q_mask])
        row_jsd = 0.5 * (p_term.sum(axis=1) + q_term.sum(axis=1))
        row_jsd[row_prediction[active] == 0] = np.log(2.0)
        jsd = float(row_jsd.mean())
    result: dict[str, Any] = {
        "cpc": _ratio(2 * float(np.minimum(observed, predicted).sum()), truth_total + prediction_total),
        "macro_origin_cpc": macro_cpc,
        "rmse": rmse,
        "nrmse": _ratio(rmse, std),
        "log_pearson": log_correlation,
        "mean_row_jsd": jsd,
        "destination_relative_l1": _ratio(float(np.abs(error.sum(axis=0)).sum()), truth_total),
        "row_conservation_relative_l1": _ratio(float(np.abs(row_prediction - row_truth).sum()), truth_total),
        "row_conservation_max_abs": float(np.max(np.abs(row_prediction - row_truth))),
        "observed_total": truth_total,
        "predicted_total": prediction_total,
        "n_origins": int(observed.shape[0]),
        "n_destinations": int(observed.shape[1]),
        "n_cells": int(observed.size),
        "n_positive_observed_origins": int(active.sum()),
        "n_zero_observed_origins": int((~active).sum()),
        "zero_observed_row_predicted_mass": float(row_prediction[~active].sum()),
        "n_nonzero_observed_edges": int(np.count_nonzero(observed)),
    }
    self_cells = None
    if origin_ids is not None and destination_ids is not None:
        if len(origin_ids) != observed.shape[0] or len(destination_ids) != observed.shape[1]:
            raise ValueError("Zone ID lengths must match the OD matrix axes")
        self_cells = np.asarray(origin_ids)[:, None] == np.asarray(destination_ids)[None, :]
    elif observed.shape[0] == observed.shape[1]:
        self_cells = np.eye(observed.shape[0], dtype=bool)
    if self_cells is not None:
        result["observed_diagonal_share"] = _ratio(float(observed[self_cells].sum()), truth_total)
        result["predicted_diagonal_share"] = _ratio(float(predicted[self_cells].sum()), prediction_total)
        off = ~self_cells
        result["offdiagonal_cpc"] = _ratio(2 * float(np.minimum(observed[off], predicted[off]).sum()),
                                            float(observed[off].sum() + predicted[off].sum()))
    if distances_km is not None:
        distances = np.asarray(distances_km, dtype=np.float64)
        if distances.shape != observed.shape or not np.isfinite(distances).all() or (distances < 0).any():
            raise ValueError("Distances must be finite, nonnegative, and match the matrices")
        actual_mean = _ratio(float((observed * distances).sum()), truth_total)
        prediction_mean = _ratio(float((predicted * distances).sum()), prediction_total)
        result["observed_mean_distance_km"] = actual_mean
        result["predicted_mean_distance_km"] = prediction_mean
        result["mean_distance_abs_error_km"] = (abs(actual_mean - prediction_mean)
                                                   if actual_mean is not None and prediction_mean is not None else None)
    return result


def aggregate_metrics(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Equal-region means with explicit defined counts; never a pooled CPC.

    Accept flat metric records or {region_id: ..., metrics: {...}} records.
    Totals/counts are summed separately so a macro mean cannot be confused with
    weighting large regions more heavily. Non-numeric metadata is ignored.
    """
    rows = [r.get("metrics", r) for r in records]
    if not rows:
        return {"n_regions": 0, "macro": {}, "defined_counts": {}, "totals": {}}
    keys = sorted(set().union(*(row.keys() for row in rows)))
    counts, macro, totals = {}, {}, {}
    count_keys = {"observed_total", "predicted_total", "zero_observed_row_predicted_mass"}
    for key in keys:
        numeric = [float(row[key]) for row in rows
                   if isinstance(row.get(key), (int, float, np.number))
                   and not isinstance(row.get(key), (bool, np.bool_))
                   and np.isfinite(row[key])]
        # Ignore string descriptors such as region_id; preserve undefined metrics.
        if not numeric and not any(key in row and row[key] is None for row in rows):
            continue
        counts[key] = len(numeric)
        if key.startswith("n_") or key in count_keys:
            totals[key] = float(sum(numeric)) if numeric else None
        else:
            macro[key] = float(np.mean(numeric)) if numeric else None
    return {"n_regions": len(rows), "macro": macro, "defined_counts": counts, "totals": totals}


def selection_score(summary, metric="cpc"):
    """Numeric keep-rule score. Callers that must ignore the diagonal pass metric='offdiagonal_cpc'.
    Total matrix CPC remains the default so other datasets are unchanged.
    """
    macro = summary.get("macro", summary)
    value = macro.get(metric)
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        raise ValueError(f"Selection metric {metric!r} is undefined on this split")
    return float(value)


# Explicit alias for callers that prefer the longer name.
aggregate_region_metrics = aggregate_metrics
