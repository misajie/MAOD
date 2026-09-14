"""Run G, DG and the complete MapAgents search on public city matrices."""
from __future__ import annotations
import argparse
import copy
import gc
import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mapagents.settings import read_config
from mapagents.data import load_dataset
from mapagents.training import ODStore, save_json, load_checkpoint, fit_model, evaluate
from mapagents.programs import SpatialCompiler, default_program
from mapagents.pipeline import run
from mapagents.gravity import fit_gravity

METRICS = ['cpc', 'offdiagonal_cpc', 'nrmse', 'log_pearson', 'mean_row_jsd']


def configuration(city, seed, output):
    cfg = read_config(ROOT / 'configs/new_york.yaml')
    cfg['seed'] = seed
    cfg['output_dir'] = str(output / city / f'seed_{seed}' / 'mapagents')
    prepared = ROOT / 'data/processed' / city
    cfg['data'] = {'format': 'generic', 'prepared': str(prepared),
                   'osm_path': str(prepared / 'osm_objects.parquet'),
                   'spatial_cache': str(prepared / 'program_cache')}
    cfg['task'] = (
        f'Predict the published within-city commuting OD matrix for {city}. '
        'Origins are split into 60% training, 20% validation, 20% heldout; destinations are all city zones. '
        'Output is conditioned on released within-city row subtotals. The target is the public-release matrix, '
        'not uncensored latent commuting. Unpublished Spain cells can be suppressed counts below five. '
        'Use raw historical OSM tags, projected count/km/km2 covariates and retrieved mobility knowledge '
        'to discover spatial features that explain validation errors. Population is unavailable; never invent it. '
        'Keep the existing fixed features unless validation diagnostics motivate a replacement. '
        'All 15 Deep Gravity hidden layers remain trainable. No heldout OD information is available to agents.')
    cfg['training'].update({'epochs': 100, 'batch_size': 32, 'select_validation_checkpoint': True,
                           'validation_every': 5, 'patience_epochs': 30, 'min_epochs': 30})
    cfg['search'].update({'rounds': 2, 'candidates_per_round': 2, 'candidate_epochs': 30})
    cfg['llm']['rag_cache_dir'] = str(ROOT / 'runs/new_york_main/agents/rag_cache')
    return cfg


def run_city(city, seed, output):
    prepared = ROOT / 'data/processed' / city
    if not (prepared / 'features_complete.json').exists():
        raise RuntimeError(f'OSM feature preparation has not finished for {city}')
    cfg = configuration(city, seed, output)
    root = output / city
    data = load_dataset(prepared)
    store = ODStore(data)
    gravity_result = root / 'gravity/result.json'
    if not gravity_result.exists():
        print(f'{city}: fitting G', flush=True)
        fit_gravity(store, root / 'gravity')
    print(f'{city} seed {seed}: full MapAgents pipeline', flush=True)
    main_result = run(cfg)
    main_root = Path(cfg['output_dir'])
    compiler = SpatialCompiler(data, prepared / 'osm_objects.parquet', prepared / 'program_cache')
    bundle = compiler.compile(default_program(data))
    model, transform, saved = load_checkpoint(main_root / 'reference/model.pt', 'cuda')
    reference_result_path = root / f'seed_{seed}/dg_reference/result.json'
    if not reference_result_path.exists():
        metrics, _ = evaluate(store, bundle, model, transform, 'test', reference_result_path.parent / 'predictions')
        save_json(reference_result_path, {'model': 'DG-reference', 'seed': seed,
                                        'validation': json.loads((main_root / 'reference/validation.json').read_text()),
                                        'held_out': metrics, 'training': saved['training']})
    # Match the maximum continuation length along the selected MapAgents path.
    # Each branch receives the same extra 30-epoch opportunity from the same
    # parent. The fixed-feature control also retains its parent on validation.
    continuation_root = root / f'seed_{seed}/dg'
    result_path = continuation_root / 'result.json'
    if not result_path.exists():
        cfg_dg = {**cfg['training'], 'epochs': 90, 'patience_epochs': 90}
        dg, tf, trained = fit_model(store, bundle, cfg_dg, continuation_root, seed+1, model, transform)
        validation, _ = evaluate(store, bundle, dg, tf, 'validation')
        heldout, _ = evaluate(store, bundle, dg, tf, 'test', continuation_root / 'predictions')
        save_json(result_path, {'model': 'DG', 'seed': seed, 'validation': validation, 'held_out': heldout,
                               'training': trained, 'reference_training': saved['training'],
                               'feature_program': 'fixed OSM features; validation-selected continuation'})
    summarize(output)
    del compiler, bundle, model, transform, store, data
    gc.collect()
    torch.cuda.empty_cache()
    return main_result


def summarize(output):
    records = []
    for city_root in sorted(output.iterdir()):
        if not city_root.is_dir(): continue
        candidates = [('G', None, city_root / 'gravity/result.json')]
        for seed_dir in sorted(city_root.glob('seed_*')):
            seed = int(seed_dir.name.split('_')[-1])
            candidates += [(model, seed, seed_dir / sub / 'result.json') for model, sub in
                           [('DG-reference', 'dg_reference'), ('DG', 'dg'), ('MapAgents', 'mapagents')]]
        for model, seed, path in candidates:
            if not path.exists(): continue
            result = json.loads(path.read_text(encoding='utf-8'))
            records.append({'city': city_root.name, 'model': model, 'seed': seed,
                            **{key: result['held_out']['macro'].get(key) for key in METRICS},
                            'heldout_cells': result['held_out']['totals']['n_cells'],
                            'path': path.relative_to(ROOT).as_posix()})
    frame = pd.DataFrame(records)
    if frame.empty: return
    frame.to_csv(output / 'results_by_seed.csv', index=False)
    save_json(output / 'results_by_seed.json', records)
    aggregated = []
    for (city, model), group in frame.groupby(['city', 'model'], sort=False):
        row = {'city': city, 'model': model, 'n_runs': len(group)}
        for key in METRICS:
            row[key + '_mean'] = float(group[key].mean())
            row[key + '_std'] = float(group[key].std(ddof=1)) if len(group) > 1 else None
        aggregated.append(row)
    pd.DataFrame(aggregated).to_csv(output / 'main_table.csv', index=False)
    lines = ['# Public city OD experiments', '',
             'Whole-city destinations; fixed 60/20/20 positive-origin row split (1234). Model seeds vary independently.',
             'Metrics describe released counts and released row subtotals. Spain suppresses counts below five.',
             'London uses 2014 OSM with 2011 OD; Paris 2022; Madrid/Barcelona 2023. NG is excluded.', '',
             '| City | Model | Runs | CPC | Off-diagonal CPC | NRMSE | log Pearson | Row JSD |',
             '|---|---|---:|---:|---:|---:|---:|---:|']
    for row in aggregated:
        values = [f"{row[k+'_mean']:.5f}" + (f" ± {row[k+'_std']:.5f}" if row[k+'_std'] is not None else '') for k in METRICS]
        lines.append('| ' + ' | '.join([row['city'], row['model'], str(row['n_runs']), *values]) + ' |')
    lines += ['', 'G fits destination masses from training-origin flows only, with exponential/power distance decay chosen on validation.',
              'DG-reference is the fixed-feature initial training. DG receives up to 90 additional epochs with validation checkpoint selection.',
              'MapAgents uses Surveyor/RAG, Cartographer and two Adapter feedback rounds; all model layers train.',
              'G is deterministic; its one result is not counted as three seeds. No cross-city transfer is claimed by this protocol.']
    (output / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cities', nargs='+', default=['london', 'paris', 'madrid', 'barcelona'])
    parser.add_argument('--seeds', type=int, nargs='+', default=[1234, 1235, 1236])
    parser.add_argument('--output', default='runs/cities_v1')
    parser.add_argument('--summarize-only', action='store_true')
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if args.summarize_only:
        summarize(output)
        return
    status = {'cities': args.cities, 'seeds': args.seeds, 'started': time.time(), 'completed': [], 'failed': []}
    for seed in args.seeds:
        for city in args.cities:
            status['current'] = {'city': city, 'seed': seed}
            save_json(output / 'status.json', status)
            try:
                run_city(city, seed, output)
                status['completed'].append({'city': city, 'seed': seed})
            except Exception as error:
                traceback.print_exc()
                status['failed'].append({'city': city, 'seed': seed, 'error': str(error)})
            save_json(output / 'status.json', status)
    status['finished'] = time.time()
    status['current'] = None
    save_json(output / 'status.json', status)
    summarize(output)
    if status['failed']: raise SystemExit(1)

if __name__ == '__main__': main()
