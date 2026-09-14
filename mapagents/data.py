"""Rebuild explicit, auditable OD datasets without importing upstream code.

The bundled DeepGravity example contains aggregated OSM variables and GeoDS
movement flows. It is neither raw OSM nor a census commuting dataset. The
adapter preserves the stored OSM values and fixes geometry measurements. The
explicit DGM mass-prior import additionally exposes full-table origin totals.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .contracts import ODData


def _json_write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def _ids(series: pd.Series, name: str) -> pd.Series:
    if series.isna().any():
        raise ValueError(f"{name} contains missing identifiers")
    values = series.astype(str).str.strip()
    if values.eq("").any():
        raise ValueError(f"{name} contains empty identifiers")
    return values


def _read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    # String ingestion is deliberate: Census IDs must keep leading zeroes.
    return pd.read_csv(path, dtype=str)


def _geometry_table(path: Path, id_column: str | None = None) -> pd.DataFrame:
    import geopandas as gpd

    frame = gpd.read_file(path)
    if id_column is None:
        id_column = next((c for c in ("zone_id", "GEOID", "geo_code", "OA11CD", "oa_id") if c in frame), None)
    if id_column is None:
        raise ValueError(f"Cannot identify the zone ID column in {path}; found {list(frame.columns)}")
    if frame.crs is None:
        raise ValueError(f"Geometry file {path} has no CRS; assign its actual CRS before preparation")
    frame = frame.loc[frame.geometry.notna() & ~frame.geometry.is_empty].copy()
    frame = frame.loc[frame.geometry.is_valid].copy()
    if frame.empty:
        raise ValueError(f"No valid zone geometries in {path}")
    frame["zone_id"] = _ids(frame[id_column], id_column)
    if frame.zone_id.duplicated().any():
        raise ValueError("Zone geometry IDs must be unique; dissolve duplicate parts before preparation")
    # Equal-area projection supplies area; projected centroids avoid geographic
    # CRS centroids (and the degree-squared area error in upstream preprocessing).
    areas = frame.to_crs(6933).area.to_numpy(dtype=float) / 1e6
    centroid_crs = frame.estimate_utm_crs() or "EPSG:6933"
    centroids = frame.to_crs(centroid_crs).centroid.to_crs(4326)
    wgs = frame.to_crs(4326)
    result = pd.DataFrame({
        "zone_id": frame.zone_id.to_numpy(),
        "longitude": centroids.x.to_numpy(),
        "latitude": centroids.y.to_numpy(),
        "area_km2": areas,
        "geometry_wkb": wgs.geometry.to_wkb().to_numpy(),
    })
    if "region_id" in frame:
        result["region_id"] = _ids(frame.region_id, "region_id").to_numpy()
    return result


def _validate_zones(zones: pd.DataFrame) -> pd.DataFrame:
    required = {"zone_id", "region_id", "longitude", "latitude", "area_km2"}
    if missing := required - set(zones):
        raise ValueError(f"Missing zone columns: {sorted(missing)}")
    zones = zones.copy()
    for key in ("zone_id", "region_id"):
        zones[key] = _ids(zones[key], key)
    if zones.zone_id.duplicated().any():
        raise ValueError("zone_id must be globally unique across regions")
    for key in ("longitude", "latitude", "area_km2"):
        zones[key] = pd.to_numeric(zones[key], errors="raise")
    numeric = zones[["longitude", "latitude", "area_km2"]].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise ValueError("Zone coordinates and area must be finite")
    if not zones.longitude.between(-180, 180).all() or not zones.latitude.between(-90, 90).all():
        raise ValueError("Zone coordinates must be WGS84 longitude/latitude degrees")
    if zones.area_km2.le(0).any():
        raise ValueError("Every zone must have positive projected area_km2")
    return zones.reset_index(drop=True)


def _validate_flows(flows: pd.DataFrame) -> pd.DataFrame:
    required = {"origin", "destination", "flow"}
    if missing := required - set(flows):
        raise ValueError(f"Missing flow columns: {sorted(missing)}")
    flows = flows[["origin", "destination", "flow"]].copy()
    for key in ("origin", "destination"):
        flows[key] = _ids(flows[key], key)
    flows["flow"] = pd.to_numeric(flows.flow, errors="raise").astype(float)
    if not np.isfinite(flows.flow).all() or flows.flow.lt(0).any():
        raise ValueError("Flow values must be finite and nonnegative; missing observations are not zero")
    return flows.groupby(["origin", "destination"], as_index=False, sort=False).flow.sum()


def _validate_features(features: pd.DataFrame, zones: pd.DataFrame) -> pd.DataFrame:
    features = features.copy()
    if "zone_id" in features:
        features["zone_id"] = _ids(features.zone_id, "feature zone_id")
        features = features.set_index("zone_id")
    features.index = features.index.astype(str)
    features.index.name = "zone_id"
    if features.index.duplicated().any():
        raise ValueError("Feature zone IDs must be unique")
    missing = set(zones.zone_id) - set(features.index)
    if missing:
        raise ValueError(f"Features missing for {len(missing)} zones, e.g. {sorted(missing)[:5]}")
    features = features.reindex(zones.zone_id.tolist())
    if features.columns.duplicated().any():
        raise ValueError("Feature columns must have unique semantic names")
    features.columns = features.columns.astype(str)
    features = features.apply(pd.to_numeric, errors="raise").astype(float)
    if not np.isfinite(features.to_numpy()).all():
        raise ValueError("Base features must be finite; explicitly impute and document missing measurements")
    return features


def _split_train_tiles(tiles: list[str], seed: int, validation_fraction: float) -> tuple[list[str], list[str]]:
    if not 0 < validation_fraction < 1:
        raise ValueError("validation_fraction must be between zero and one")
    if len(tiles) < 2:
        raise ValueError("At least two usable training regions are required for independent validation")
    shuffled = np.asarray(sorted(set(tiles)), dtype=object)
    np.random.default_rng(seed).shuffle(shuffled)
    count = max(1, min(len(shuffled) - 1, int(round(len(shuffled) * validation_fraction))))
    validation = set(shuffled[:count].tolist())
    return ([r for r in tiles if r not in validation], [r for r in tiles if r in validation])


def _finish_dataset(zones: pd.DataFrame, features: pd.DataFrame, raw_flows: pd.DataFrame,
                    splits: dict[str, list[str]], metadata: dict[str, Any], output: Path) -> ODData:
    zones = _validate_zones(zones)
    features = _validate_features(features, zones)
    raw_flows = _validate_flows(raw_flows)
    region_map = zones.set_index("zone_id").region_id
    origin_region = raw_flows.origin.map(region_map)
    destination_region = raw_flows.destination.map(region_map)
    internal = origin_region.notna() & destination_region.notna() & origin_region.eq(destination_region)
    flows = raw_flows.loc[internal].reset_index(drop=True)
    if flows.flow.sum() <= 0:
        raise ValueError("Dataset has no positive internal-region OD flow")
    assigned: list[str] = []
    all_regions = set(zones.region_id)
    for split in ("train", "validation", "test"):
        splits[split] = [str(r) for r in splits.get(split, [])]
        if set(splits[split]) - all_regions:
            raise ValueError(f"{split} references regions missing from zones")
        assigned.extend(splits[split])
    if len(assigned) != len(set(assigned)):
        raise ValueError("Train, validation, and test region assignments must be disjoint and unique")
    if set(assigned) != all_regions:
        raise ValueError("Every retained region must have exactly one split assignment")
    # The optional DGM protocol separately declares its flow-derived mass prior.
    source_totals = raw_flows.groupby("origin").flow.sum()
    internal_totals = flows.groupby("origin").flow.sum()
    metadata = dict(metadata)
    metadata.update({
        "format_version": 1,
        "n_zones": len(zones), "n_regions": len(all_regions),
        "n_features": features.shape[1], "n_stored_flow_edges": len(flows),
        "n_complete_matrix_cells": int(zones.groupby("region_id").size().pow(2).sum()),
        "raw_flow_total": float(raw_flows.flow.sum()),
        "internal_flow_total": float(flows.flow.sum()),
        "excluded_flow_total": float(raw_flows.loc[~internal, "flow"].sum()),
        "retained_origins_raw_outflow": float(source_totals.reindex(zones.zone_id, fill_value=0).sum()),
        "retained_origins_external_outflow": float(
            source_totals.reindex(zones.zone_id, fill_value=0).sum() - internal_totals.sum()),
        "zero_internal_outflow_zones": int(internal_totals.reindex(zones.zone_id, fill_value=0).eq(0).sum()),
        "destination_support": "all retained zones in each origin's region, including self",
        "unlisted_internal_edges": "zero within the supplied complete flow table",
        "production_constraint": "observed internal-region row totals supplied only to output scaling",
        "flow_derived_population_feature": bool(metadata.get("flow_derived_population_feature", False)),
        "split_region_counts": {s: len(v) for s, v in splits.items()},
    })
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    zones.to_parquet(output / "zones.parquet", index=False)
    features.reset_index().to_parquet(output / "base_features.parquet", index=False)
    flows.to_parquet(output / "flows.parquet", index=False)
    _json_write(output / "splits.json", splits)
    _json_write(output / "metadata.json", metadata)
    return ODData(zones, flows, features, splits, metadata, output)


def _source_directory(source: Path) -> Path:
    source = Path(source)
    options = [source, source / "deepgravity/data/new_york", source / "data/new_york"]
    if source.name == "processed":
        options.insert(0, source.parent)
    for option in options:
        if (option / "processed/tileid2oa2handmade_features.json").exists():
            return option
    raise FileNotFoundError(f"Cannot locate DeepGravity processed example beneath {source}")


def _tile_list(path: Path) -> list[str]:
    # Upstream split CSVs are one column with NO header.
    return list(dict.fromkeys(pd.read_csv(path, header=None, dtype=str).iloc[:, 0].str.strip().tolist()))


def prepare_deepgravity(source: Path, output: Path, seed: int = 1234,
                        validation_fraction: float = 0.2) -> ODData:
    """Prepare the public example, preserving supplied test-tile assignments.

    Validation is selected deterministically from supplied training tiles, so
    complete spatial regions are withheld. Empty, invalid, and zero-flow tiles
    are recorded and removed. No pickle deserialization is performed.
    """
    source = _source_directory(Path(source))
    processed = source / "processed"
    mapping = json.loads((processed / "tileid2oa2handmade_features.json").read_text(encoding="utf-8"))
    widths: dict[str, int] = {}
    for entries in mapping.values():
        for entry in entries.values():
            for name, values in entry.items():
                widths[name] = max(widths.get(name, 0), len(values) if isinstance(values, list) else 1)
    columns = [name if width == 1 else f"{name}__{i}"
               for name, width in sorted(widths.items()) for i in range(width)]
    if len(columns) != len(set(columns)):
        raise ValueError("Flattened upstream feature names collide")
    rows: list[dict[str, Any]] = []
    assignments: list[dict[str, str]] = []
    for region, entries in mapping.items():
        for zone, entry in entries.items():
            row: dict[str, Any] = {"zone_id": str(zone)}
            for name, width in sorted(widths.items()):
                values = entry.get(name, [0.0] * width)
                values = values if isinstance(values, list) else [values]
                if len(values) != width:
                    raise ValueError(f"Inconsistent feature width for {zone}/{name}")
                for i, value in enumerate(values):
                    row[name if width == 1 else f"{name}__{i}"] = value
            rows.append(row)
            assignments.append({"zone_id": str(zone), "region_id": str(region)})
    feature_table = pd.DataFrame(rows)
    assignment = pd.DataFrame(assignments)
    if assignment.zone_id.duplicated().any():
        raise ValueError("Upstream zone IDs appear in more than one tile")
    shape_path = next((source / name for name in ("output_areas.shp", "output_areas.geojson")
                       if (source / name).exists()), None)
    if shape_path is None:
        raise FileNotFoundError("Original output-area geometry is required to rebuild valid areas and centroids")
    geometric = _geometry_table(shape_path)
    zones = assignment.merge(geometric.drop(columns=["region_id"], errors="ignore"), on="zone_id", how="inner", validate="one_to_one")
    # Retain all legitimate destinations, including zero-outflow destination zones.
    zones = zones.loc[zones.area_km2.gt(0)].copy()
    raw_flows = pd.read_csv(processed / "flows_oa.csv.zip", dtype={"residence": str, "workplace": str})
    raw_flows = _validate_flows(raw_flows.rename(columns={"residence": "origin", "workplace": "destination", "commuters": "flow"}))
    region_map = zones.set_index("zone_id").region_id
    oi, di = raw_flows.origin.map(region_map), raw_flows.destination.map(region_map)
    usable = set(oi.loc[oi.notna() & oi.eq(di) & raw_flows.flow.gt(0)])
    supplied_train = _tile_list(processed / "train_tiles.csv")
    supplied_test = _tile_list(processed / "test_tiles.csv")
    if set(supplied_train) & set(supplied_test):
        raise ValueError("Upstream train/test tiles overlap")
    train_tiles = [r for r in supplied_train if r in usable]
    test_tiles = [r for r in supplied_test if r in usable]
    train, validation = _split_train_tiles(train_tiles, seed, validation_fraction)
    retained = set(train + validation + test_tiles)
    zones = zones.loc[zones.region_id.isin(retained)].reset_index(drop=True)
    feature_descriptions = {
        name if width == 1 else f"{name}__{i}": {
            "source_key": name,
            "source_component": i,
            "description": (f"Stored DeepGravity aggregate {name}" + (f", list component {i}; component semantics not asserted" if width > 1 else "")),
            "units": "upstream stored units; not recalibrated from raw OSM",
        }
        for name, width in sorted(widths.items()) for i in range(width)
    }
    metadata = {
        "dataset": "deepgravity_new_york_public",
        "source_directory": str(source.resolve()),
        "flow_semantics": "Public DeepGravity New York example derived from GeoDS COVID-19 movement data; not asserted to be commuting trips",
        "flow_year": None,
        "osm_snapshot_date": None,
        "feature_source": "processed/tileid2oa2handmade_features.json",
        "raw_osm_available": False,
        "feature_descriptions": feature_descriptions,
        "feature_measurement_note": "Aggregated public values are preserved; original line/area units may be inconsistent. Corrected zone area does not repair upstream aggregate measurements. Raw OSM is required to recompute them.",
        "geometry_area_crs": "EPSG:6933 equal-area",
        "geometry_coordinate_crs": "EPSG:4326",
        "seed": int(seed), "validation_fraction": float(validation_fraction),
        "split_protocol": "provided test tiles; seeded region holdout drawn only from provided train tiles",
        "original_train_tiles": supplied_train, "original_test_tiles": supplied_test,
        "dropped_train_tiles": [r for r in supplied_train if r not in usable],
        "dropped_test_tiles": [r for r in supplied_test if r not in usable],
        "dropped_zone_count": int(len(assignment) - len(zones)),
        "unassigned_tiles": sorted(set(mapping) - set(supplied_train) - set(supplied_test)),
    }
    return _finish_dataset(zones, feature_table, raw_flows,
                           {"train": train, "validation": validation, "test": test_tiles}, metadata, Path(output))


def prepare_generic(zones_path: Path, flows_path: Path, features_path: Path, output: Path,
                    splits_path: Path | None = None, seed: int = 1234,
                    validation_fraction: float = 0.2, test_fraction: float = 0.2,
                    metadata: dict[str, Any] | None = None, target_only: bool = False) -> ODData:
    """Import future data with explicitly named columns.

    CSV/parquet zones require zone_id, region_id, longitude, latitude, area_km2.
    GeoJSON/GPKG/shapefile zones require zone_id and region_id plus a known CRS.
    Features require zone_id and numeric columns. Flows require origin,
    destination, flow and must describe complete observed rows: omitted cells
    are zero, not unknown. Optional splits.json defines disjoint region lists.
    """
    zones_path = Path(zones_path)
    zones = (_geometry_table(zones_path, "zone_id")
             if zones_path.suffix.lower() in {".shp", ".geojson", ".gpkg", ".json"}
             else _read_table(zones_path))
    zones = _validate_zones(zones)
    features, flows = _read_table(Path(features_path)), _read_table(Path(flows_path))
    if splits_path is not None:
        splits = json.loads(Path(splits_path).read_text(encoding="utf-8"))
    elif target_only:
        splits = {"train": [], "validation": [], "test": sorted(zones.region_id.unique().tolist())}
    else:
        if not 0 < test_fraction < 1:
            raise ValueError("test_fraction must be between zero and one")
        regions = sorted(zones.region_id.unique().tolist())
        if len(regions) < 3:
            raise ValueError("Automatic train/validation/test split requires at least three regions")
        shuffled = np.asarray(regions, dtype=object)
        np.random.default_rng(seed).shuffle(shuffled)
        n_test = max(1, min(len(regions) - 2, int(round(len(regions) * test_fraction))))
        test = shuffled[:n_test].tolist()
        train, validation = _split_train_tiles(shuffled[n_test:].tolist(), seed + 1, validation_fraction)
        splits = {"train": train, "validation": validation, "test": test}
    details = dict(metadata or {})
    details.setdefault("dataset", "generic_od")
    details.setdefault("flow_semantics", "user-supplied; document observation period and meaning")
    details.setdefault("raw_osm_available", False)
    details["seed"] = int(seed)
    return _finish_dataset(zones, features, flows, splits, details, Path(output))


def prepare_dgm_mass_prior(prepared: Path, source: Path, output: Path) -> ODData:
    """Retain the prepared supports and expose the public DGM 18+1 inputs."""
    prepared, output = Path(prepared), Path(output)
    if prepared.resolve() == output.resolve() or output.exists():
        raise ValueError("DGM mass-prior preparation requires a new output directory")
    data = load_dataset(prepared)
    source = _source_directory(Path(source))
    mapping = json.loads((source / "processed/tileid2oa2handmade_features.json").read_text())
    entries = {zone: values for tile in mapping.values() for zone, values in tile.items()}
    names = sorted(next(iter(entries.values())))
    if len(names) != 18: raise ValueError("Expected the 18 geographic fields in the public DGM example")
    rows = []
    for zone in data.zones.zone_id:
        entry = entries[zone]
        rows.append({"zone_id": zone, **{name: entry[name][0] if isinstance(entry[name], list) else entry[name] for name in names}})
    features = pd.DataFrame(rows).set_index("zone_id")
    raw = pd.read_csv(source / "processed/flows_oa.csv.zip", dtype={"residence": str, "workplace": str})
    raw = _validate_flows(raw.rename(columns={"residence": "origin", "workplace": "destination", "commuters": "flow"}))
    mass = raw.groupby("origin").flow.sum().reindex(features.index, fill_value=0.)
    features.insert(0, "dgm_mass", mass.where(mass > 0, 1e-6))
    metadata = dict(data.metadata)
    metadata.update({
        "dataset": "deepgravity_new_york_public_dgm_mass",
        "flow_derived_population_feature": True,
        "population_feature_available": False,
        "mass_prior": {"column": "dgm_mass", "definition": "M_z = sum_d raw_OD[z,d] over the complete source table before tile filtering",
                       "zero_or_missing_value": 1e-6, "units": "source movement counts, not census residents",
                       "available_for": "all zones, including validation and heldout zones, as an explicitly supplied aggregate covariate",
                       "source": "resources/deepgravity/deepgravity/utils.py:149-160",
                       "destination_meaning": "M_j is the outflow from j, not the inflow to j"},
        "base_feature_expressions": {"dgm_mass": {"op": "log", "arg": {"op": "source", "column": "dgm_mass"}, "epsilon": 1e-6}},
        "feature_units": {"dgm_mass": "source movement counts, OD-derived"},
        "feature_descriptions": {name: {"description": "Public DGM stored geographic aggregate; first component only"} for name in names},
        "feature_source": "processed/tileid2oa2handmade_features.json first components, matching oa2features.pkl; full source OD row sums for dgm_mass",
        "feature_measurement_note": "The public New York oa2features.pkl matches the 18 stored raw first components; it does not divide them by zone area at load time. Preserve these values. Raw OSM-derived additions use separately documented projected units.",
        "prior_catalog": "resources/priors/deepgravity.json",
        "input_protocol": "39 backbone inputs: log(M_i), 18 stored origin aggregates, log(M_j), 18 stored destination aggregates, centroid distance",
        "label_access_protocol": "Individual OD targets are used for training/validation only. Full-table origin sums, including withheld zones, are supplied as DGM mass covariates by explicit protocol; heldout pair metrics are not evaluated during discovery.",
    })
    result = _finish_dataset(data.zones.copy(), features.reset_index(), raw,
                             {k: list(v) for k, v in data.splits.items()}, metadata, output)
    _json_write(output / "dgm_input_audit.json", {
        "geographic_columns": names, "n_geographic_columns": len(names), "n_backbone_inputs": 39,
        "mass_source_rows": len(raw), "zero_or_missing_mass_zones": int((mass <= 0).sum()),
        "raw_mass_quantiles": {str(k): float(v) for k, v in mass.quantile([0, .25, .5, .75, 1]).items()},
        "mass_before_region_filtering": True, "density_normalization_applied": False,
        "retained_support": "same zones and split assignments as " + str(prepared),
    })
    return result


def load_dataset(root: Path) -> ODData:
    """Read a prepared dataset, checking its stable schema and split boundaries."""
    root = Path(root)
    zones = _validate_zones(pd.read_parquet(root / "zones.parquet"))
    features = _validate_features(pd.read_parquet(root / "base_features.parquet"), zones)
    flows = _validate_flows(pd.read_parquet(root / "flows.parquet"))
    splits = json.loads((root / "splits.json").read_text(encoding="utf-8"))
    metadata = json.loads((root / "metadata.json").read_text(encoding="utf-8"))
    assignments = [str(r) for s in ("train", "validation", "test") for r in splits[s]]
    # A single-city origin-row protocol keeps the complete OD matrix while
    # withholding origins. In this mode all zones share one spatial region and
    # row_splits supplied to ODStore define train/validation/test origins.
    if metadata.get("split_mode") != "origin_rows":
        if len(assignments) != len(set(assignments)) or set(assignments) != set(zones.region_id):
            raise ValueError("Prepared dataset has overlapping or incomplete region splits")
    region_map = zones.set_index("zone_id").region_id
    origins, destinations = flows.origin.map(region_map), flows.destination.map(region_map)
    if origins.isna().any() or destinations.isna().any() or not origins.eq(destinations).all():
        raise ValueError("Prepared flows contain unknown or cross-region endpoints")
    return ODData(zones, flows, features, splits, metadata, root)
