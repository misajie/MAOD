"""Prepare public release matrices, retaining all cross-origin destinations."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mapagents.data import load_dataset
from mapagents.programs import SpatialCompiler

YEARS = {'london': 2011, 'paris': 2022, 'madrid': 2023, 'barcelona': 2023}

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')

def prepare(city, seed=1234):
    root = Path('data/raw') / city / 'aligned'
    out = Path('data/processed') / city
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'features_complete.json').exists():
        print(f'{city}: prepared features already available', flush=True)
        return
    z = gpd.read_parquet(root / 'zones.parquet').sort_values('zone_id').reset_index(drop=True)
    f = pd.read_parquet(root / 'flows.parquet')
    z['zone_id'] = z.zone_id.astype(str)
    f[['origin', 'destination']] = f[['origin', 'destination']].astype(str)
    if z.zone_id.duplicated().any() or (set(f.origin) | set(f.destination)) - set(z.zone_id):
        raise ValueError('OD IDs do not match unique zones')
    area = z.to_crs(6933).area.to_numpy() / 1e6
    cent = z.to_crs(z.estimate_utm_crs() or 6933).centroid.to_crs(4326)
    zones = pd.DataFrame({'zone_id': z.zone_id, 'region_id': city,
                          'longitude': cent.x, 'latitude': cent.y, 'area_km2': area,
                          'geometry_wkb': z.to_crs(4326).geometry.to_wkb()})
    features = pd.DataFrame({'zone_id': z.zone_id, 'area_km2': area})
    ids = zones.zone_id.tolist()
    positive = f.groupby('origin').flow.sum()
    candidates = np.array([x for x in ids if positive.get(x, 0) > 0], dtype=object)
    np.random.default_rng(seed).shuffle(candidates)
    ntest = max(1, int(round(len(candidates) * .2)))
    nval = max(1, int(round(len(candidates) * .2)))
    rows = {'test': candidates[:ntest].tolist(), 'validation': candidates[ntest:ntest+nval].tolist(),
            'train': candidates[ntest+nval:].tolist()}
    hist = json.loads((Path('data/raw') / city / 'osm/historical/manifest.json').read_text(encoding='utf-8'))
    metadata = {
        'dataset': city + '_published_commuting', 'name': city, 'split_mode': 'origin_rows',
        'split_protocol': 'fixed 60/20/20 random positive published-origin rows; complete city destination support',
        'flow_semantics': 'published internal residence-to-workplace counts; output conditioned on published row subtotals',
        'prediction_target': 'public-release matrix, not uncensored latent flows',
        'unlisted_internal_edges': 'zero RELEASED mass; not asserted to be true zero mobility',
        'flow_year': YEARS[city], 'n_zones': len(zones), 'n_regions': 1,
        'n_stored_flow_edges': len(f), 'n_complete_matrix_cells': len(zones)**2,
        'internal_flow_total': float(f.flow.sum()), 'origin_split_seed': seed,
        'origin_split_counts': {k: len(v) for k, v in rows.items()},
        'excluded_zero_published_origins': sorted(set(ids) - set(candidates)),
        'destination_support': 'all zones, including diagonal',
        'population_feature_available': False, 'flow_derived_population_feature': False,
        'production_constraint': 'published within-city row subtotals used only at output scaling',
        'osm_snapshot_date': hist['pbf_header'].get('replication_timestamp_utc'),
        'osm_temporal_alignment': hist['temporal_alignment_note'], 'raw_osm_available': True,
        'feature_source': 'historical raw OSM geometries clipped in local UTM; counts, km, km2',
        'suppression_threshold': 5 if city in {'madrid', 'barcelona'} else None,
        'raw_root': str(root.resolve()),
    }
    zones.to_parquet(out / 'zones.parquet', index=False)
    features.to_parquet(out / 'base_features.parquet', index=False)
    f[['origin', 'destination', 'flow']].to_parquet(out / 'flows.parquet', index=False)
    write_json(out / 'splits.json', {'train': [city], 'validation': [city], 'test': [city]})
    write_json(out / 'origin_splits.json', rows)
    write_json(out / 'metadata.json', metadata)
    print(city, len(zones), len(f), {k: len(v) for k, v in rows.items()}, flush=True)

def fixed_features(city):
    out = Path('data/processed') / city
    if (out / 'features_complete.json').exists(): return
    data = load_dataset(out)
    compiler = SpatialCompiler(data, out / 'osm_objects.parquet')
    specs = {}
    for tag in ['residential', 'commercial', 'industrial', 'retail', 'forest', 'farmland', 'grass']:
        specs[f'{tag}_landuse_km2'] = {'op': 'osm', 'predicate': {'landuse': tag}, 'aggregation': 'area'}
    for key, values, name in [
        ('building', '*', 'building'), ('office', '*', 'office'), ('shop', '*', 'shop'),
        ('tourism', '*', 'tourism'), ('leisure', '*', 'leisure'),
        ('amenity', ['school', 'university', 'college', 'kindergarten'], 'education'),
        ('amenity', ['hospital', 'clinic', 'doctors', 'pharmacy'], 'health'),
        ('amenity', ['restaurant', 'cafe', 'fast_food', 'bar', 'pub'], 'food'),
        ('amenity', ['bank', 'post_office', 'townhall', 'police'], 'services'),
        ('amenity', ['theatre', 'cinema', 'library', 'arts_centre'], 'culture'),
        ('railway', ['station', 'halt', 'tram_stop'], 'rail_station'),
        ('highway', ['bus_stop'], 'bus_stop'),
        ('public_transport', ['platform', 'station'], 'public_transport'),
    ]:
        specs[f'{name}_count'] = {'op': 'osm', 'predicate': {key: values}, 'aggregation': 'count'}
    specs['building_area_km2'] = {'op': 'osm', 'predicate': {'building': '*'}, 'aggregation': 'area'}
    specs['main_road_km'] = {'op': 'osm', 'predicate': {'highway': ['motorway', 'trunk', 'primary', 'secondary', 'tertiary']}, 'aggregation': 'length'}
    specs['local_road_km'] = {'op': 'osm', 'predicate': {'highway': ['residential', 'service', 'living_street', 'unclassified']}, 'aggregation': 'length'}
    specs['railway_km'] = {'op': 'osm', 'predicate': {'railway': ['rail', 'subway', 'tram', 'light_rail']}, 'aggregation': 'length'}
    frame = data.base_features.copy()
    for name, expression in specs.items():
        frame[name] = compiler._zone(expression)
        print(f'{city}: {name}, nonzero_zones={int((frame[name] != 0).sum())}', flush=True)
    frame.reset_index().to_parquet(out / 'base_features.parquet', index=False)
    metadata = data.metadata
    metadata['n_features'] = len(frame.columns)
    metadata['feature_units'] = {name: ('km2' if name.endswith('km2') else 'km' if name.endswith('_km') else 'count') for name in frame}
    write_json(out / 'metadata.json', metadata)
    write_json(out / 'fixed_osm_feature_definitions.json', specs)
    write_json(out / 'features_complete.json', {'n_features': len(frame.columns), 'osm_objects': 'osm_objects.parquet'})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', required=True, choices=list(YEARS))
    parser.add_argument('--features', action='store_true')
    args = parser.parse_args()
    if args.features: fixed_features(args.city)
    else: prepare(args.city)
