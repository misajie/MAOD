"""Singly constrained gravity with destination masses from visible origin rows."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp
from .training import save_json
from .metrics import aggregate_metrics, matrix_metrics, selection_score


def fit_gravity(store, output):
    if store.row_splits is None:
        raise ValueError('Fitted destination masses require the city origin-row protocol; do not use train-tile masses in unseen tiles')
    output = Path(output)
    masses = {}
    for r, region in store.regions.items():
        rows = store.rows_by_region('train').get(r, [])
        if not rows: raise ValueError('No fit origins for this destination set')
        # Standard destination mass is estimated from visible flows only.
        # Laplace smoothing retains a nonzero prior for unseen destinations.
        masses[r] = region.flows[rows].sum(axis=0) + 1.
    fits = []
    for kernel in ('exponential', 'power'):
        examples = []
        for r, rows in store.rows_by_region('train').items():
            region = store.regions[r]
            dist = region.distances[rows].astype(float)
            decay = dist if kernel == 'exponential' else np.log1p(dist)
            examples.append((np.log(masses[r])[None, :], decay, region.flows[rows]))
        def objective(theta):
            total_loss, total_mass = 0., 0.
            grad = np.zeros(2)
            for log_mass, decay, y in examples:
                scores = theta[0] * log_mass - theta[1] * decay
                logp = scores - logsumexp(scores, axis=1, keepdims=True)
                error = np.exp(logp) * y.sum(axis=1, keepdims=True) - y
                total_loss -= float((y * logp).sum())
                total_mass += float(y.sum())
                grad += [float((error * log_mass).sum()), -float((error * decay).sum())]
            return total_loss / total_mass, grad / total_mass
        fitted = minimize(objective, [1., .2 if kernel == 'exponential' else 1.],
                          jac=True, method='L-BFGS-B', bounds=[(0., 5.), (0., 50.)],
                          options={'maxiter': 500, 'ftol': 1e-12})
        model = {'kernel': kernel, 'mass_exponent': float(fitted.x[0]), 'decay_coefficient': float(fitted.x[1]),
                 'optimizer_success': bool(fitted.success), 'optimizer_message': str(fitted.message),
                 'train_nll': float(fitted.fun), 'masses': {r: m.tolist() for r, m in masses.items()}}
        validation = evaluate_gravity(store, model, 'validation')
        fits.append((selection_score(validation, 'cpc'), model, validation))
    _, model, validation = max(fits, key=lambda x: x[0])
    model['selection'] = [{'kernel': m['kernel'], 'selection_metric': 'cpc',
                           'selection_score': selection_score(v, 'cpc'),
                           'validation_cpc': v['macro']['cpc'],
                           'validation_offdiagonal_cpc': v['macro'].get('offdiagonal_cpc'),
                           'mass_exponent': m['mass_exponent'], 'decay_coefficient': m['decay_coefficient']} for _, m, v in fits]
    model['mass_source'] = 'destination sums over training-origin rows plus one; no validation/heldout destination sums'
    save_json(output / 'model.json', model)
    result = {'model': 'G', 'validation': validation,
              'held_out': evaluate_gravity(store, model, 'test', output / 'predictions')}
    save_json(output / 'result.json', result)
    return result


def evaluate_gravity(store, model, split, output=None):
    records = []
    if output: Path(output).mkdir(parents=True, exist_ok=True)
    for r, rows in store.rows_by_region(split).items():
        reg = store.regions[r]
        distances = reg.distances[rows].astype(float)
        decay = distances if model['kernel'] == 'exponential' else np.log1p(distances)
        scores = model['mass_exponent'] * np.log(model['masses'][r])[None, :] - model['decay_coefficient'] * decay
        probabilities = np.exp(scores - logsumexp(scores, axis=1, keepdims=True))
        truth = reg.flows[rows]
        pred = probabilities * truth.sum(axis=1, keepdims=True)
        records.append({'region_id': r, **matrix_metrics(truth, pred, distances, reg.zone_ids[rows], reg.zone_ids)})
        if output:
            np.savez_compressed(Path(output) / f'region_{r}.npz', observed=truth, predicted=pred,
                                origin_ids=reg.zone_ids[rows].astype(str), destination_ids=reg.zone_ids.astype(str))
    summary = aggregate_metrics(records)
    summary['split'] = split
    if output:
        save_json(Path(output) / 'metrics.json', summary)
        pd.DataFrame(records).to_csv(Path(output) / 'region_metrics.csv', index=False)
    return summary
