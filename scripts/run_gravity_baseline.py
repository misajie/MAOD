"""Classical destination-attractiveness gravity baseline on prepared ODData."""
import sys, json, argparse
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mapagents.data import load_dataset
from mapagents.training import ODStore
from mapagents.metrics import matrix_metrics, aggregate_metrics

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data/processed/new_york')
ap.add_argument('--out', default='runs/new_york_baselines/gravity')
ap.add_argument('--alpha-max', type=float, default=4.0)
ap.add_argument('--alpha-steps', type=int, default=401)
a = ap.parse_args()
d = load_dataset(Path(a.data)); s = ODStore(d)
zmap = d.zones.set_index('zone_id').region_id.to_dict()
train_regions = set(d.splits['train'])
train_flows = d.flows[d.flows.origin.map(zmap).isin(train_regions)]
ids = d.zones.zone_id.astype(str).tolist()
inbound = train_flows.groupby('destination').flow.sum().reindex(ids, fill_value=0.).to_numpy(float)
beta = np.log1p(inbound)
def nll(alpha):
    val = mass = 0.
    for r, i in s.examples('train', True):
        reg = s.regions[r]; gi = reg.global_indices
        logits = beta[gi] - alpha * reg.distances[i]; logits -= logits.max()
        logz = np.log(np.exp(logits).sum()); y = reg.flows[i]
        val -= float((y * (logits - logz)).sum()); mass += float(y.sum())
    return val / max(mass, 1.)
grid = np.linspace(0., a.alpha_max, a.alpha_steps)
alpha = float(grid[int(np.argmin([nll(x) for x in grid]))])
print('fitted alpha=', alpha, flush=True)
def evaluate(split):
    rows = []
    for r, origins in s.rows_by_region(split).items():
        reg = s.regions[r]; pred = []
        for i in origins:
            logits = beta[reg.global_indices] - alpha * reg.distances[i]; logits -= logits.max()
            p = np.exp(logits); p /= p.sum(); pred.append(p * reg.flows[i].sum())
        pred = np.asarray(pred)
        rows.append({'region_id': r, **matrix_metrics(reg.flows[origins], pred, reg.distances[origins], reg.zone_ids[origins], reg.zone_ids)})
    return aggregate_metrics(rows)
result = {'model': 'Gravity destination-attractiveness + distance decay', 'alpha': alpha,
          'attractiveness_source': 'training-region destination inflows only',
          'validation': evaluate('validation'), 'held_out': evaluate('test')}
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
(out / 'metrics.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result['held_out'], indent=2))
