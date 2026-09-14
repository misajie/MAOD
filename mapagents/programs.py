"""Executable spatial feature expressions with stable semantic column IDs.

Programs contain expression trees, never Python or SQL. The same operators work
on the supplied Deep Gravity features and on optional raw OSM objects.
"""
from __future__ import annotations

import json
import copy
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import cKDTree

from .contracts import ODData, FeatureBundle


class ProgramError(ValueError):
    pass


def semantic_id(expression: dict) -> str:
    return json.dumps(expression, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def normalize_program(program: dict) -> dict:
    """Canonicalize redundant scope wrappers and merge identical zone columns.

    This is a semantics-preserving compiler pass, not an LLM substitute.
    """
    p = copy.deepcopy(program)
    grouped = {}
    for feature in p.get("features", []):
        scope = feature.get("scope", "both")
        expr = feature.get("expression", {})
        if scope in {"origin", "destination"} and expr.get("op") == scope:
            feature["expression"] = expr = expr["arg"]
        key = ("pair" if scope == "pair" else "zone", semantic_id(expr))
        if key not in grouped:
            grouped[key] = feature
        elif scope != "pair":
            old = grouped[key]
            channels = {old.get("scope", "both"), scope}
            if "both" in channels or channels == {"origin", "destination"}: old["scope"] = "both"
    p["features"] = list(grouped.values())
    return p


def haversine(lon1, lat1, lon2, lat2):
    lat1, lat2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(np.asarray(lon2) - np.asarray(lon1))
    dp = lat2 - lat1
    a = np.sin(dp / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dl / 2) ** 2
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def default_program(data: ODData) -> dict:
    return {"version": 1, "name": "supplied_geographic_features", "features": [
        {"name": str(c), "scope": "both", "expression": {"op": "source", "column": str(c)},
         "evidence": ["dataset:" + str(c)], "mechanism": "Supplied public geographic covariate"}
        for c in data.base_features.columns
    ]}


OPERATORS = {
    "source": "{op:source,column:<catalog name>} (zone only)",
    "area": "{op:area} gives zone area in km2 (zone only)",
    "constant": "{op:constant,value:number}",
    "log1p": "{op:log1p,arg:expression} uses signed log1p",
    "sqrt": "{op:sqrt,arg:expression} nonnegative square root",
    "add": "{op:add,left:expression,right:expression}",
    "subtract": "{op:subtract,left:expression,right:expression}",
    "multiply": "{op:multiply,left:expression,right:expression}",
    "ratio": "{op:ratio,left:expression,right:expression,epsilon:1e-6}",
    "clip": "{op:clip,arg:expression,min:0,max:100}",
    "neighborhood": "{op:neighborhood,arg:zone_expression,radius_km:2,aggregation:sum|mean|decay}",
    "osm": "{op:osm,predicate:{amenity:[hospital,clinic]},aggregation:count|area|length|sum|mean,field:optional_numeric_tag,buffer_m:0}; different predicate keys are AND; values list is OR; '*' means present",
    "origin": "{op:origin,arg:zone_expression} (pair only)",
    "destination": "{op:destination,arg:zone_expression} (pair only)",
    "distance": "{op:distance} in km (pair only)",
    "exp_decay": "{op:exp_decay,arg:expression,scale:5}",
}


def validate_program(program: dict, max_features: int = 128):
    if not isinstance(program, dict) or program.get("version") != 1:
        raise ProgramError("Program must be an object with version=1")
    feats = program.get("features")
    if not isinstance(feats, list) or not 1 <= len(feats) <= max_features:
        raise ProgramError(f"features must have 1..{max_features} entries")
    seen = set()
    for f in feats:
        if not isinstance(f, dict) or not isinstance(f.get("expression"), dict):
            raise ProgramError("Each feature requires an expression object")
        scope = f.get("scope", "both")
        if scope not in {"both", "origin", "destination", "pair"}:
            raise ProgramError(f"Invalid feature scope: {scope}")
        sid = (scope, semantic_id(f["expression"]))
        if sid in seen:
            raise ProgramError("Duplicate expression and scope")
        seen.add(sid)
        _validate_expr(f["expression"], pair=(scope == "pair"))


def _validate_expr(e: dict, pair=False, depth=0):
    if depth > 12 or not isinstance(e, dict) or e.get("op") not in OPERATORS:
        raise ProgramError("Unknown operator, malformed expression, or excessive expression depth")
    op = e["op"]
    if op in {"origin", "destination", "distance"} and not pair:
        raise ProgramError(f"{op} is a pair-only operator")
    if pair and op in {"source", "area", "osm", "neighborhood"}:
        raise ProgramError(f"Wrap zone operator {op} in origin or destination")
    for key in ("arg", "left", "right"):
        if key in e:
            _validate_expr(e[key], False if op in {"origin", "destination"} else pair, depth + 1)
    required = {"source": ["column"], "constant": ["value"], "osm": ["predicate"],
                "origin": ["arg"], "destination": ["arg"], "log1p": ["arg"],
                "sqrt": ["arg"], "clip": ["arg"], "neighborhood": ["arg", "radius_km"],
                "exp_decay": ["arg", "scale"], "add": ["left", "right"],
                "subtract": ["left", "right"], "multiply": ["left", "right"],
                "ratio": ["left", "right"]}
    if any(k not in e for k in required.get(op, [])):
        raise ProgramError(f"Missing argument for {op}")
    for key in ("radius_km", "scale", "epsilon"):
        if key in e and (not np.isfinite(float(e[key])) or float(e[key]) <= 0):
            raise ProgramError(f"{key} must be positive and finite")


def _arithmetic(e, child):
    op = e["op"]
    if op == "constant":
        return float(e["value"])
    if op == "log1p":
        v = child(e["arg"]); return np.sign(v) * np.log1p(np.abs(v))
    if op == "sqrt":
        return np.sqrt(np.maximum(child(e["arg"]), 0))
    if op == "clip":
        return np.clip(child(e["arg"]), e.get("min", -np.inf), e.get("max", np.inf))
    if op == "exp_decay":
        return np.exp(np.clip(-child(e["arg"]) / float(e["scale"]), -60, 60))
    a, b = child(e["left"]), child(e["right"])
    if op == "add": return a + b
    if op == "subtract": return a - b
    if op == "multiply": return a * b
    if op == "ratio":
        eps = float(e.get("epsilon", 1e-6))
        denominator = np.where(np.abs(b) < eps, np.where(np.asarray(b) < 0, -eps, eps), b)
        return a / denominator
    raise ProgramError(f"Unsupported arithmetic operator {op}")


class SpatialCompiler:
    def __init__(self, data: ODData, osm_path=None, cache_dir=None):
        self.data = data
        self.n = len(data.zones)
        self.base = data.base_features.reindex(data.zones.zone_id.astype(str))
        self.cache: dict[str, np.ndarray] = {}
        self.osm_path = Path(osm_path) if osm_path else None
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir: self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._objects = None
        self._zones_geo = None
        self._neighbors = {}

    def catalog(self) -> list[dict]:
        records = []
        for name in self.base.columns:
            v = self.base[name].to_numpy(dtype=float)
            records.append({"name": str(name), "expression": {"op": "source", "column": str(name)},
                            "nonzero_fraction": float(np.mean(v != 0)),
                            "min": float(np.nanmin(v)), "max": float(np.nanmax(v)),
                            "source": self.data.metadata.get("feature_source", "supplied_features"),
                            "unit": self.data.metadata.get("feature_units", {}).get(str(name), "source_units")})
        if self.osm_path:
            from .osm import tag_inventory
            records.extend(tag_inventory(self.osm_path, limit=500))
        return records

    def profile(self) -> dict:
        z = self.data.zones
        return {"dataset": self.data.metadata.get("name", "dataset"),
                "flow_semantics": self.data.metadata.get("flow_semantics", "OD counts"),
                "n_zones": self.n, "n_regions": int(z.region_id.nunique()),
                "bounds": [float(z.longitude.min()), float(z.latitude.min()),
                           float(z.longitude.max()), float(z.latitude.max())],
                "area_km2_quantiles": [float(x) for x in z.area_km2.quantile([0, .25, .5, .75, 1])],
                "raw_osm_available": bool(self.osm_path),
                "feature_observations": self.catalog(), "operators": OPERATORS,
                "note": "Map covariates only. Nonzero frequency is not a measurement of map completeness."}

    def _zone(self, e: dict) -> np.ndarray:
        sid = semantic_id(e)
        if sid in self.cache: return self.cache[sid]
        op = e["op"]
        if op == "source":
            if e["column"] not in self.base.columns:
                raise ProgramError(f"Unknown source column: {e['column']}")
            v = self.base[e["column"]].to_numpy(dtype=float)
        elif op == "area":
            v = self.data.zones.area_km2.to_numpy(dtype=float)
        elif op == "osm":
            v = self._osm_aggregate(e)
        elif op == "neighborhood":
            radius = float(e["radius_km"])
            values = self._zone(e["arg"])
            if radius not in self._neighbors:
                z = self.data.zones
                lon, lat = np.radians(z.longitude), np.radians(z.latitude)
                xyz = np.column_stack([np.cos(lat)*np.cos(lon), np.cos(lat)*np.sin(lon), np.sin(lat)])
                chord = 2 * np.sin(min(radius / 6371.0088, np.pi) / 2)
                self._neighbors[radius] = cKDTree(xyz).query_ball_point(xyz, chord)
            agg = e.get("aggregation", "sum")
            if agg not in {"sum", "mean", "decay"}: raise ProgramError("Invalid neighborhood aggregation")
            v = np.empty(self.n)
            z = self.data.zones
            for i, idx in enumerate(self._neighbors[radius]):
                selected = values[idx]
                if agg == "sum": v[i] = selected.sum()
                elif agg == "mean": v[i] = selected.mean()
                else:
                    d = haversine(z.longitude.iloc[i], z.latitude.iloc[i], z.longitude.iloc[idx].to_numpy(), z.latitude.iloc[idx].to_numpy())
                    v[i] = np.sum(selected * np.exp(-d / radius))
        else:
            v = _arithmetic(e, self._zone)
        v = np.broadcast_to(np.asarray(v, dtype=np.float64), (self.n,)).copy()
        if not np.isfinite(v).all(): raise ProgramError(f"Non-finite values from {op}")
        self.cache[sid] = v
        return v

    def _osm_aggregate(self, e):
        if not self.osm_path:
            raise ProgramError("Raw OSM is unavailable; use supplied source expressions or configure osm.path")
        import geopandas as gpd
        from .osm import read_objects
        if self._zones_geo is None:
            geometry_file = self.data.metadata.get("geometry_file")
            if geometry_file:
                geographic = gpd.read_parquet(geometry_file)
            elif "geometry_wkb" in self.data.zones:
                import shapely
                geographic = gpd.GeoDataFrame(self.data.zones.copy(), geometry=shapely.from_wkb(self.data.zones.geometry_wkb), crs=4326)
            else: raise ProgramError("Dataset needs zone geometry for OSM aggregation")
            target_crs = geographic.estimate_utm_crs() or 6933
            self._zones_geo = geographic.set_index("zone_id").reindex(self.data.zones.zone_id).to_crs(target_crs)
        if self._objects is None:
            self._objects = read_objects(self.osm_path, self._zones_geo.crs)
        objects = self._objects
        predicate = e["predicate"]
        if not isinstance(predicate, dict) or not predicate: raise ProgramError("OSM predicate must be a nonempty tag mapping")
        keep = np.ones(len(objects), dtype=bool)
        for key, wanted in predicate.items():
            options = wanted if isinstance(wanted, list) else [wanted]
            keep &= objects.tags.map(lambda t: key in t if "*" in options else t.get(key) in options).to_numpy()
        obj = objects.loc[keep].copy()
        agg = e.get("aggregation", "count")
        if agg not in {"count", "area", "length", "sum", "mean"}: raise ProgramError("Invalid OSM aggregation")
        buffer_m = float(e.get("buffer_m", 0))
        if not 0 <= buffer_m <= 50000: raise ProgramError("buffer_m must be between 0 and 50000")
        zones = self._zones_geo.copy()
        if buffer_m: zones.geometry = zones.geometry.buffer(buffer_m)
        if obj.empty: return np.zeros(self.n)
        if agg == "area": obj = obj[obj.geom_type.isin(["Polygon", "MultiPolygon"])]
        if agg == "length": obj = obj[obj.geom_type.isin(["LineString", "MultiLineString"])]
        if obj.empty: return np.zeros(self.n)
        pairs = gpd.sjoin(zones[["geometry"]], obj[["geometry", "tags"]], how="inner", predicate="intersects")
        out = np.zeros(self.n)
        if pairs.empty: return out
        accum = {}; counts = {}
        for zone_id, row in pairs.iterrows():
            object_row = obj.loc[row.index_right]
            if agg == "count": value = 1.0
            elif agg in {"area", "length"}:
                clipped = object_row.geometry.intersection(zones.loc[zone_id].geometry)
                value = clipped.area / 1e6 if agg == "area" else clipped.length / 1000
            else:
                field = e.get("field")
                if not field: raise ProgramError("Numeric OSM aggregation requires field")
                try: value = float(object_row.tags.get(field, "nan"))
                except (TypeError, ValueError): continue
                if not np.isfinite(value): continue
            accum[zone_id] = accum.get(zone_id, 0.) + value
            counts[zone_id] = counts.get(zone_id, 0) + 1
        for i, zone_id in enumerate(self.data.zones.zone_id):
            out[i] = accum.get(zone_id, 0.) / (counts.get(zone_id, 1) if agg == "mean" else 1)
        return out

    def compile(self, program: dict) -> FeatureBundle:
        program = normalize_program(program)
        validate_program(program)
        origins, destinations, oi, di, ps, pi, report = [], [], [], [], [], [], []
        for f in program["features"]:
            e = f["expression"]; sid = semantic_id(e); scope = f.get("scope", "both")
            if scope == "pair":
                ps.append(e); pi.append(sid)
                def visit(node):
                    if node["op"] in {"origin", "destination"}: self._zone(node["arg"])
                    else:
                        for k in ("arg", "left", "right"):
                            if k in node: visit(node[k])
                visit(e)
                report.append({"name": f.get("name", sid), "scope": scope, "semantic_id": sid})
                continue
            v = self._zone(e)
            if scope in {"both", "origin"}: origins.append(v); oi.append(sid)
            if scope in {"both", "destination"}: destinations.append(v); di.append(sid)
            report.append({"name": f.get("name", sid), "scope": scope, "semantic_id": sid,
                           "nonzero_fraction": float(np.mean(v != 0)), "std": float(v.std()),
                           "min": float(v.min()), "max": float(v.max())})
        if len(oi) != len(set(oi)) or len(di) != len(set(di)) or len(pi) != len(set(pi)):
            raise ProgramError("Overlapping scopes create duplicate input columns")
        bundle = FeatureBundle(
            np.column_stack(origins) if origins else np.empty((self.n, 0)),
            np.column_stack(destinations) if destinations else np.empty((self.n, 0)),
            oi, di, ps, pi, dict(self.cache), {"features": report, "input_mode": "raw_osm_and_supplied" if self.osm_path else "supplied_public_features"})
        # Evaluate pair expressions on actual map indices during compilation.
        if ps:
            sample = np.arange(min(self.n, 64))
            vals = pair_features(bundle, sample, sample[::-1], np.ones(len(sample)))
            if not np.isfinite(vals).all(): raise ProgramError("Non-finite pair feature")
        return bundle


def pair_features(bundle: FeatureBundle, origins, destinations, distances_km):
    origins, destinations, distances_km = np.broadcast_arrays(origins, destinations, distances_km)
    def calc(e):
        op = e["op"]
        if op == "distance": return distances_km
        if op == "origin": return bundle.zone_values[semantic_id(e["arg"])][origins]
        if op == "destination": return bundle.zone_values[semantic_id(e["arg"])][destinations]
        return _arithmetic(e, calc)
    if not bundle.pair_specs: return np.empty(origins.shape + (0,))
    return np.stack([np.broadcast_to(calc(e), origins.shape) for e in bundle.pair_specs], axis=-1)
