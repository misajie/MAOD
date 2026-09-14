"""Bounded map and supplied-covariate evidence for spatial-program discovery.

The service never reads the OD matrix or splits. Supplied covariates may include
an explicitly declared OD-derived mass prior. Diagnostic inputs provide IDs only.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import numpy as np
from scipy.spatial import cKDTree

from .programs import haversine, pair_features, validate_program


MAX_ZONES = 8
MAX_PAIRS = 6
MAX_FEATURES = 80
MAX_RESPONSE_CHARS = 26000


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_json_value(v) for v in value]
    if isinstance(value, np.generic):
        return _json_value(value.item())
    if isinstance(value, float):
        return value if np.isfinite(value) else None
    if value is None or isinstance(value, (str, bool, int)):
        return value
    return str(value)


def _quantiles(values) -> dict:
    a = np.asarray(values, dtype=float)
    a = a[np.isfinite(a)]
    if not len(a):
        return {"n_finite": 0}
    return {"n_finite": len(a), **dict(zip(
        ("min", "p10", "p25", "p50", "p75", "p90", "max"),
        np.quantile(a, [0, .1, .25, .5, .75, .9, 1]).tolist()))}


def _compact(value, depth=0, width=6):
    if isinstance(value, dict):
        items = list(value.items())
        result = {k: _compact(v, depth + 1, width) for k, v in items[:width * 4]}
        if len(items) > width * 4:
            result["omitted_keys"] = len(items) - width * 4
        return result
    if isinstance(value, list):
        limit = width if depth < 3 else max(2, width - 2)
        return [_compact(v, depth + 1, width) for v in value[:limit]]
    return value[:240] if isinstance(value, str) else value


class MapEvidence:
    def __init__(self, compiler, output_dir=None, allowed_zone_ids=None):
        self.compiler = compiler
        self.zones = compiler.data.zones.copy().reset_index(drop=True)
        self.ids = self.zones.zone_id.astype(str).to_numpy()
        self.lookup = {z: i for i, z in enumerate(self.ids)}
        allowed = set(self.ids) if allowed_zone_ids is None else {str(z) for z in allowed_zone_ids}
        unknown = allowed - set(self.ids)
        if unknown:
            raise ValueError(f"Unknown allowed map zones: {sorted(unknown)[:5]}")
        if not allowed:
            raise ValueError("The allowed map domain must contain at least one zone")
        self.allowed = allowed
        self.indices = np.asarray([i for i, z in enumerate(self.ids) if z in allowed], dtype=int)
        self.base = compiler.base.reindex(self.ids)
        self.values = self.base.to_numpy(dtype=float)
        self.columns = [str(c) for c in self.base.columns]
        self.units = dict(compiler.data.metadata.get("feature_units", {}))
        self.osm_path = Path(compiler.osm_path) if compiler.osm_path else None
        self.raw_available = bool(self.osm_path and self.osm_path.is_file())
        self.output_dir = Path(output_dir) if output_dir is not None else None
        if self.output_dir is not None:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        self._inventory = None
        self._geometry = None
        self._raw_cache = {}
        self._focus = []
        self._focus_pairs = []
        geographic = self.zones.iloc[self.indices]
        lon, lat = np.radians(geographic.longitude), np.radians(geographic.latitude)
        self.xyz = np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
        self.tree = cKDTree(self.xyz) if len(self.xyz) else None
        self.local_indices = {int(g): i for i, g in enumerate(self.indices)}
        source_identity = {"zones": self.ids.tolist(), "feature_columns": self.columns,
                           "base_hash": hashlib.sha256(self.values.tobytes()).hexdigest(),
                           "geometry_hash": hashlib.sha256(self.zones[["longitude", "latitude", "area_km2"]]
                                                          .to_numpy(dtype=float).tobytes()).hexdigest()}
        if self.raw_available:
            stat = self.osm_path.stat()
            source_identity["osm"] = [str(self.osm_path.resolve()), stat.st_size, stat.st_mtime_ns]
        source_identity["allowed"] = sorted(self.allowed)
        self.identity = hashlib.sha256(json.dumps(source_identity, sort_keys=True).encode()).hexdigest()
        self.source = {"kind": "map_and_supplied_covariates", "snapshot_id": self.identity,
                       "features": compiler.data.metadata.get("feature_source", "supplied_features"),
                       "raw_osm": str(self.osm_path) if self.raw_available else None,
                       "od_matrix_accessed": False,
                       "mass_prior": compiler.data.metadata.get("mass_prior")}
        mass_column = (compiler.data.metadata.get("mass_prior") or {}).get("column")
        self.source["od_derived_covariates"] = compiler.data.metadata.get(
            "od_derived_covariates", [mass_column] if mass_column in self.columns else [])
        if self.raw_available:
            sidecar = self.osm_path.with_suffix(self.osm_path.suffix + ".json")
            if sidecar.exists():
                self.source["raw_osm_provenance"] = json.loads(sidecar.read_text(encoding="utf-8"))
        self._standardized = None

    @staticmethod
    def tool_schema() -> dict:
        return {"name": "query_map", "description": "Read local maps and supplied covariates, including declared mass priors; never queries OD matrix entries.",
                "parameters": {"type": "object", "required": ["type"], "properties": {
                    "type": {"type": "string", "enum": ["zone_profile", "pair_profile", "tag_search", "feature_probe", "pair_feature_probe"]},
                    "zone_ids": {"type": "array", "maxItems": MAX_ZONES, "items": {"type": "string"}},
                    "pairs": {"type": "array", "maxItems": MAX_PAIRS, "items": {"type": "object",
                        "required": ["origin_id", "destination_id"], "properties": {
                            "origin_id": {"type": "string"}, "destination_id": {"type": "string"}},
                        "additionalProperties": False}},
                    "query": {"type": "string", "description": "Purpose; for tag_search, literal tag/name tokens (OR match)."},
                    "keys": {"type": "array", "maxItems": MAX_FEATURES, "items": {"type": "string"}},
                    "predicate": {"type": "object", "description": "OSM tag AND predicates; string/list values; '*' means present."},
                    "expression": {"type": "object", "description": "A zone expression for feature_probe; a pair expression for pair_feature_probe, with explicit origin/destination wrappers."},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 12}},
                    "additionalProperties": False}}

    def _pairs(self, value=None):
        value = self._focus_pairs if value is None else value
        if not isinstance(value, list) or not 1 <= len(value) <= MAX_PAIRS:
            raise ValueError(f"pairs must contain 1..{MAX_PAIRS} ordered origin/destination records")
        result = []
        for pair in value:
            if not isinstance(pair, dict) or not all(k in pair for k in ("origin_id", "destination_id")):
                raise ValueError("Each pair requires origin_id and destination_id")
            origin, destination = str(pair["origin_id"]), str(pair["destination_id"])
            self._zone_ids([origin, destination])
            if (origin, destination) not in result:
                result.append((origin, destination))
        return result

    def _zone_ids(self, value=None) -> list[str]:
        if value is None:
            value = self._focus or self._representatives()
        if not isinstance(value, list) or not 1 <= len(value) <= MAX_ZONES:
            raise ValueError(f"zone_ids must contain 1..{MAX_ZONES} identifiers")
        result = list(dict.fromkeys(str(z) for z in value))
        unknown = [z for z in result if z not in self.lookup]
        denied = [z for z in result if z not in self.allowed]
        if unknown:
            raise ValueError(f"Unknown zone_ids: {unknown[:5]}")
        if denied:
            raise ValueError(f"zone_ids outside allowed map domain: {denied[:5]}")
        return result

    def _representatives(self) -> list[str]:
        if not len(self.indices):
            return []
        order = self.indices[np.argsort(self.zones.area_km2.to_numpy(dtype=float)[self.indices], kind="stable")]
        ranks = np.unique(np.rint(np.asarray([.1, .5, .9]) * (len(order) - 1)).astype(int))
        return [str(self.ids[order[i]]) for i in ranks]

    def _nearest(self, zone_id, k=5):
        i = self.local_indices[self.lookup[zone_id]]
        distance, index = self.tree.query(self.xyz[i], k=min(k + 1, len(self.indices)))
        result = []
        for d, j in zip(np.atleast_1d(distance), np.atleast_1d(index)):
            if int(j) == i:
                continue
            result.append({"zone_id": str(self.ids[self.indices[int(j)]]),
                           "centroid_distance_km": float(2 * 6371.0088 * np.arcsin(np.clip(d / 2, 0, 1)))})
        return result[:k]

    def _similar(self, zone_id):
        if self._standardized is None:
            a = self.values[self.indices]
            a = np.sign(a) * np.log1p(np.abs(a))
            scale = a.std(axis=0)
            scale = np.where(scale > 1e-12, scale, 1.)
            self._standardized = (a - a.mean(axis=0)) / scale
        i = self.local_indices[self.lookup[zone_id]]
        distances = np.mean((self._standardized - self._standardized[i]) ** 2, axis=1)
        distances[i] = np.inf
        return [{"zone_id": str(self.ids[self.indices[j]]), "standardized_distance": float(np.sqrt(distances[j]))}
                for j in np.argsort(distances)[:3] if np.isfinite(distances[j])]

    def _overview(self):
        a = self.values[self.indices]
        features = [{"name": name, "unit": self.units.get(name, "source_units_unverified"),
                     "nonzero_fraction": float(np.mean(a[:, j] != 0)), "quantiles": _quantiles(a[:, j])}
                    for j, name in enumerate(self.columns[:MAX_FEATURES])]
        similar = []
        if len(a) > 1 and a.shape[1] > 1:
            transformed = np.sign(a) * np.log1p(np.abs(a))
            good = np.flatnonzero(transformed.std(axis=0) > 1e-12)
            if len(good) > 1:
                corr = np.corrcoef(transformed[:, good], rowvar=False)
                for i, j in zip(*np.triu_indices(len(good), 1)):
                    if np.isfinite(corr[i, j]) and abs(corr[i, j]) >= .95:
                        similar.append({"left": self.columns[good[i]], "right": self.columns[good[j]],
                                        "signed_log1p_pearson": float(corr[i, j]),
                                        "exact_duplicate": bool(np.array_equal(a[:, good[i]], a[:, good[j]]))})
                similar.sort(key=lambda r: -abs(r["signed_log1p_pearson"]))
        scales = {}
        if len(self.indices) > 1:
            ds, _ = self.tree.query(self.xyz, k=min(6, len(self.indices)))
            distances = 2 * 6371.0088 * np.arcsin(np.clip(ds / 2, 0, 1))
            scales = {"nearest_other_centroid_km": _quantiles(distances[:, 1]),
                      "kth_other_centroid_km": _quantiles(distances[:, -1]),
                      "k": int(distances.shape[1] - 1)}
        return {"n_zones": len(self.ids), "n_allowed_zones": len(self.indices),
                "raw_osm_available": self.raw_available,
                "area_km2": _quantiles(self.zones.area_km2.to_numpy()[self.indices]),
                "spatial_scales": scales, "features": features,
                "feature_count": len(self.columns), "features_truncated": len(self.columns) > MAX_FEATURES,
                "near_redundant_columns": similar[:12], "representative_zone_ids": self._representatives(),
                "notes": ["Statistics use maps and supplied covariates within the allowed domain; any OD-derived mass follows its declared provenance.",
                          "Centroid proximity is not network accessibility.",
                          "Tag absence is not evidence of real-world absence or map completeness.",
                          "Unverified source units must not be interpreted as counts, meters, or square kilometers."]}

    def bootstrap(self, diagnostics=None) -> list[dict]:
        focused = []
        ordered_pairs = []
        def visit(value):
            if isinstance(value, dict):
                if all(k in value and str(value[k]) in self.allowed for k in ("origin_id", "destination_id")):
                    pair = {k: str(value[k]) for k in ("origin_id", "destination_id")}
                    if pair not in ordered_pairs:
                        ordered_pairs.append(pair)
                for key, item in value.items():
                    if key in {"zone_id", "origin_id", "destination_id"} and str(item) in self.allowed:
                        if str(item) not in focused:
                            focused.append(str(item))
                    elif isinstance(item, (dict, list)):
                        visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)
        visit(diagnostics)
        self._focus = list(dict.fromkeys(focused[:4] + self._representatives()))[:6]
        self._focus_pairs = ordered_pairs[:MAX_PAIRS]
        records = [self.query({"type": "overview"})]
        if self._focus:
            records.append(self.query({"type": "zone_profile", "zone_ids": self._focus}))
        if self._focus_pairs:
            records.append(self.query({"type": "pair_profile", "pairs": self._focus_pairs}))
        return records

    def query(self, request: dict) -> dict:
        cleaned = _json_value(request)
        try:
            if not isinstance(request, dict):
                raise ValueError("Map request must be an object")
            encoded = json.dumps(request, ensure_ascii=False, allow_nan=False, sort_keys=True)
            if len(encoded) > 10000:
                cleaned = {"type": str(request.get("type", ""))[:80], "request_omitted": True,
                           "request_sha256": hashlib.sha256(encoded.encode()).hexdigest()}
                raise ValueError("Map request exceeds 10000 characters")
            kind = request.get("type", request.get("tool"))
            if kind == "overview":
                data = self._overview()
            elif kind == "zone_profile":
                data = self._profile(request)
            elif kind == "pair_profile":
                data = self._pair_profile(request)
            elif kind == "tag_search":
                data = self._tag_search(request)
            elif kind == "feature_probe":
                data = self._probe(request)
            elif kind == "pair_feature_probe":
                data = self._pair_probe(request)
            else:
                raise ValueError(f"Unknown map query type: {kind}")
            result = {"source": self.source, "request": cleaned, "data": _json_value(data)}
        except Exception as exc:
            result = {"source": self.source, "request": cleaned,
                      "error": {"type": type(exc).__name__, "message": str(exc)[:800]}}
        if len(json.dumps(result, ensure_ascii=False)) > MAX_RESPONSE_CHARS:
            result["data"] = _compact(result.get("data"))
            result["response_truncated"] = True
        if len(json.dumps(result, ensure_ascii=False)) > MAX_RESPONSE_CHARS:
            result["data"] = _compact(result.get("data"), width=3)
        if len(json.dumps(result, ensure_ascii=False)) > MAX_RESPONSE_CHARS:
            result["data"] = {"response_omitted": "Response exceeds the size budget; request fewer zones or feature keys."}
        canonical = json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False)
        result = {"id": "map:" + hashlib.sha256(canonical.encode()).hexdigest()[:20], **result}
        if self.output_dir is not None:
            with (self.output_dir / "evidence_queries.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(result, ensure_ascii=False, allow_nan=False) + "\n")
        return result

    def _pair_profile(self, request):
        pairs = self._pairs(request.get("pairs"))
        keys = request.get("keys", self.columns[:MAX_FEATURES])
        if not isinstance(keys, list) or len(keys) > MAX_FEATURES or any(k not in self.columns for k in keys):
            raise ValueError("keys must be supplied feature names (at most 80)")
        records = []
        for origin, destination in pairs:
            oi, di = self.lookup[origin], self.lookup[destination]
            oz, dz = self.zones.iloc[oi], self.zones.iloc[di]
            contrasts = []
            for key in keys:
                j = self.columns.index(key)
                ov, dv = float(self.values[oi, j]), float(self.values[di, j])
                domain = self.values[self.indices, j]
                spread = np.std(np.sign(domain) * np.log1p(np.abs(domain)))
                if spread <= 1e-12:
                    continue
                delta = (np.sign(dv) * np.log1p(abs(dv)) - np.sign(ov) * np.log1p(abs(ov))) / spread
                contrasts.append({"column": key, "origin_value": ov, "destination_value": dv,
                                  "unit": self.units.get(key, "source_units_unverified"),
                                  "destination_minus_origin_standardized_log": float(delta)})
            contrasts.sort(key=lambda row: -abs(row["destination_minus_origin_standardized_log"]))
            retained = contrasts if "keys" in request else contrasts[:8]
            for row in contrasts:
                if any(token in row["column"].lower() for token in ("population", "mass")) and row not in retained:
                    retained.append(row)
            records.append({"origin_id": origin, "destination_id": destination,
                            "same_zone": origin == destination,
                            "same_region": str(oz.region_id) == str(dz.region_id),
                            "centroid_distance_km": float(haversine(oz.longitude, oz.latitude, dz.longitude, dz.latitude)),
                            "origin_area_km2": float(oz.area_km2), "destination_area_km2": float(dz.area_km2),
                            "source_contrasts": retained,
                            "omitted_nonconstant_features": len(contrasts) - len(retained)})
        return {"pairs": records,
                "role_contract": {"origin": "Trip-generating endpoint in this directed OD pair",
                                  "destination": "Candidate receiving endpoint in this directed OD pair",
                                  "zone_roles": "Infer open, potentially overlapping functional roles from measured features; the same zone can play either endpoint role.",
                                  "mass_prior": self.compiler.data.metadata.get("mass_prior")},
                "note": "These are ordered covariate contrasts, not observed flows or proven travel purposes. Endpoint reversal swaps roles. Default contrast list keeps the eight largest differences and available mass columns."}

    def _pair_probe(self, request):
        expression = request.get("expression")
        if not isinstance(expression, dict):
            raise ValueError("pair_feature_probe requires a pair expression")
        pairs = self._pairs(request.get("pairs"))
        bundle = self.compiler.compile({"version": 1, "features": [{"scope": "pair", "expression": expression}]})
        coords = self.zones[["longitude", "latitude"]].to_numpy(dtype=float)
        def evaluate(oi, di):
            oi, di = np.broadcast_arrays(np.asarray(oi), np.asarray(di))
            distance = haversine(coords[oi, 0], coords[oi, 1], coords[di, 0], coords[di, 1])
            values = pair_features(bundle, oi, di, distance)[..., 0]
            if not np.isfinite(values).all():
                raise ValueError("Pair expression produced nonfinite values")
            return values
        records, support = [], []
        for origin, destination in pairs:
            oi, di = self.lookup[origin], self.lookup[destination]
            forward, reverse = float(evaluate(oi, di)), float(evaluate(di, oi))
            records.append({"origin_id": origin, "destination_id": destination,
                            "value": forward, "reversed_endpoint_value": reverse,
                            "forward_minus_reverse": forward - reverse})
        for origin in dict.fromkeys(pair[0] for pair in pairs):
            oi = self.lookup[origin]
            region = str(self.zones.iloc[oi].region_id)
            candidates = self.indices[self.zones.region_id.astype(str).to_numpy()[self.indices] == region]
            if len(candidates) > 64:
                candidates = candidates[np.unique(np.rint(np.linspace(0, len(candidates) - 1, 64)).astype(int))]
            values = evaluate(oi, candidates)
            support.append({"origin_id": origin, "n_sampled_destinations": len(candidates),
                            "value_quantiles": _quantiles(values),
                            "varies_across_destinations": bool(np.ptp(values) > 1e-12)})
        return {"expression": expression, "pairs": records, "within_origin_support": support,
                "note": "Computed raw feature values only. Reverse endpoints change directed roles. Within-origin checks use up to 64 deterministic map destinations from the same region. A constant additive term cannot change row-softmax allocation. This is not a causal or prediction-effect estimate."}

    def _profile(self, request):
        zone_ids = self._zone_ids(request.get("zone_ids"))
        keys = request.get("keys", self.columns[:MAX_FEATURES])
        if not isinstance(keys, list) or len(keys) > MAX_FEATURES or any(k not in self.columns for k in keys):
            raise ValueError("keys must be supplied feature names (at most 80)")
        raw = None
        raw_error = None
        if self.raw_available:
            try:
                raw = self._raw_summaries(zone_ids, limit=3)
            except Exception as exc:
                raw_error = {"available": False, "configured": True,
                             "error": {"type": type(exc).__name__, "message": str(exc)[:500]}}
        rows = []
        for zone_id in zone_ids:
            g = self.lookup[zone_id]
            i = self.local_indices[g]
            feature_values = {}
            for key in keys:
                j = self.columns.index(key)
                value = self.values[g, j]
                population = self.values[self.indices, j]
                feature_values[key] = {"value": float(value), "unit": self.units.get(key, "source_units_unverified"),
                                       "empirical_percentile_le": float(np.mean(population <= value))}
            radius_counts = {}
            for radius in (1., 2., 5., 10.):
                chord = 2 * np.sin(radius / (2 * 6371.0088))
                radius_counts[str(radius)] = len(self.tree.query_ball_point(self.xyz[i], chord)) - 1
            row = self.zones.iloc[g]
            rows.append({"zone_id": zone_id, "region_id": str(row.region_id),
                         "longitude": float(row.longitude), "latitude": float(row.latitude),
                         "area_km2": float(row.area_km2), "features": feature_values,
                         "nearest_zones": self._nearest(zone_id),
                         "other_centroids_within_radius_km": radius_counts,
                         "numeric_similar_zones": self._similar(zone_id),
                         "raw_osm": raw.get(zone_id) if raw else raw_error or {"available": False,
                             "reason": "Raw OSM objects are not configured; supplied columns are aggregated covariates."}})
        return {"zones": rows, "similarity_definition": "RMS distance after signed log1p and per-column standardization on allowed map zones.",
                "feature_keys_truncated": "keys" not in request and len(self.columns) > MAX_FEATURES}

    def _probe(self, request):
        expression = request.get("expression")
        if not isinstance(expression, dict):
            raise ValueError("feature_probe requires a zone expression")
        validate_program({"version": 1, "features": [{"scope": "both", "expression": expression}]})
        zone_ids = self._zone_ids(request.get("zone_ids"))
        values = np.asarray(self.compiler._zone(expression), dtype=float)
        if values.shape != (len(self.ids),) or not np.isfinite(values).all():
            raise ValueError("Feature probe did not produce one finite value per zone")
        subset = values[self.indices]
        correlations = []
        if np.std(subset) > 1e-12:
            for j, name in enumerate(self.columns):
                other = self.values[self.indices, j]
                if np.std(other) > 1e-12:
                    corr = float(np.corrcoef(subset, other)[0, 1])
                    if np.isfinite(corr):
                        correlations.append({"column": name, "pearson": corr,
                                             "exact_duplicate": bool(np.array_equal(subset, other))})
            correlations.sort(key=lambda v: -abs(v["pearson"]))
        data = {"expression": expression, "purpose": str(request.get("query", ""))[:400],
                "values": [{"zone_id": z, "value": float(values[self.lookup[z]])} for z in zone_ids],
                "quantiles": _quantiles(subset), "nonzero_fraction": float(np.mean(subset != 0)),
                "constant": bool(np.ptp(subset) <= 1e-12), "nearest_source_correlations": correlations[:5],
                "note": "A computed map feature; no model or causal contribution is measured. Expression units depend on operands; unverified source units remain unverified."}
        if expression.get("op") == "neighborhood":
            radius = float(expression["radius_km"])
            chord = 2 * np.sin(min(radius / 6371.0088, np.pi) / 2)
            counts = np.asarray(self.tree.query_ball_point(self.xyz, chord, return_length=True))
            data["allowed_map_neighbor_counts_including_self"] = _quantiles(counts)
            data["allowed_map_self_only_fraction"] = float(np.mean(counts == 1))
            data["neighborhood_note"] = "Compiler aggregates all dataset map zones; coverage statistics here use the allowed map domain."
        return data

    def _load_inventory(self):
        if self._inventory is not None:
            return self._inventory
        cached = self.osm_path.with_suffix(self.osm_path.suffix + ".tag_inventory.json")
        if cached.exists() and cached.stat().st_mtime_ns >= self.osm_path.stat().st_mtime_ns:
            self._inventory = json.loads(cached.read_text(encoding="utf-8"))
        else:
            self._inventory = []
        return self._inventory

    @staticmethod
    def _predicate(value):
        if value is None:
            return {}
        if not isinstance(value, dict) or len(value) > 8:
            raise ValueError("predicate must be a tag mapping with at most 8 keys")
        for key, wanted in value.items():
            if not isinstance(key, str) or len(key) > 120:
                raise ValueError("Invalid OSM predicate key")
            options = wanted if isinstance(wanted, list) else [wanted]
            if not options or len(options) > 20 or any(not isinstance(v, str) or len(v) > 160 for v in options):
                raise ValueError("OSM predicate values must be strings or short lists of strings")
        return value

    def _tag_search(self, request):
        if not self.raw_available:
            raise ValueError("raw_osm_unavailable: cannot query tags, names, or objects from supplied aggregate columns")
        query = str(request.get("query", ""))[:500]
        tokens = re.findall(r"[\w:=-]+", query.casefold())[:12]
        predicate = self._predicate(request.get("predicate"))
        limit = max(1, min(int(request.get("limit", 8)), 12))
        inventory = self._load_inventory()
        matched = [row for row in inventory if not tokens or any(t in str(row.get("name", "")).casefold() for t in tokens)]
        zone_ids = self._zone_ids(request.get("zone_ids"))
        return {"query_interpretation": "Literal case-insensitive OR token match over tag keys, values and names; predicates combine with AND.",
                "inventory_matches": matched[:limit], "inventory_cache_available": bool(inventory),
                "inventory_scope": "Full extracted map, not restricted to requested zones.",
                "zones": self._raw_summaries(zone_ids, predicate=predicate, tokens=tokens, limit=limit)}

    def _zone_geometry(self):
        if self._geometry is not None:
            return self._geometry
        import geopandas as gpd
        import shapely
        if "geometry_wkb" in self.zones:
            frame = gpd.GeoDataFrame({"zone_id": self.ids}, geometry=shapely.from_wkb(self.zones.geometry_wkb), crs=4326)
        elif "geometry" in self.zones:
            crs = getattr(self.compiler.data.zones, "crs", None)
            if crs is None:
                raise ValueError("Zone geometry has no CRS")
            frame = gpd.GeoDataFrame(self.zones[["zone_id", "geometry"]], geometry="geometry", crs=crs)
        else:
            path = self.compiler.data.metadata.get("geometry_file")
            if not path:
                raise ValueError("Zone polygon geometry is unavailable for raw map intersections")
            path = Path(path)
            if path.suffix.lower() in {".parquet", ".pq"}:
                import pyarrow.parquet as pq
                if "geometry_wkb" in pq.read_schema(path).names:
                    raw = pq.read_table(path, columns=["zone_id", "geometry_wkb"]).to_pandas()
                    frame = gpd.GeoDataFrame(raw[["zone_id"]], geometry=shapely.from_wkb(raw.geometry_wkb), crs=4326)
                else:
                    frame = gpd.read_parquet(path)
            else:
                frame = gpd.read_file(path)
        if frame.crs is None:
            raise ValueError("Zone polygon geometry has no declared CRS")
        frame["zone_id"] = frame.zone_id.astype(str)
        frame = frame.set_index("zone_id").reindex(self.ids).to_crs(4326)
        self._geometry = frame.geometry.make_valid()
        return self._geometry

    def _raw_summaries(self, zone_ids, predicate=None, tokens=None, limit=3):
        """Stream extracted parquet batches, then intersect selected polygons exactly."""
        predicate, tokens = predicate or {}, tokens or []
        cache_key = json.dumps([zone_ids, predicate, tokens, limit], sort_keys=True)
        if cache_key in self._raw_cache:
            return self._raw_cache[cache_key]
        if self.osm_path.suffix.lower() not in {".parquet", ".pq"}:
            raise ValueError("bounded_raw_query_requires_extracted_parquet: configure extracted OSM, not a PBF")
        import geopandas as gpd
        import pyarrow as pa
        import pyarrow.compute as pc
        import pyarrow.parquet as pq
        import shapely
        schema = pq.read_schema(self.osm_path)
        if not {"tags", "geometry_wkb"}.issubset(schema.names):
            raise ValueError("Extracted OSM parquet must provide tags and geometry_wkb")
        geographic = gpd.GeoSeries(self._zone_geometry().reindex(zone_ids), crs=4326)
        if geographic.isna().any() or geographic.is_empty.any():
            raise ValueError("Requested zones have missing or empty polygon geometry")
        target_crs = geographic.estimate_utm_crs()
        if target_crs is None:
            raise ValueError("Could not choose a local metric projection for map intersections")
        metric = geographic.to_crs(target_crs)
        extent = shapely.box(*geographic.total_bounds)
        geographic_geometries = geographic.to_numpy()
        shapely.prepare(geographic_geometries)
        stored = {}
        columns = [c for c in ("element_type", "osm_id", "tags", "geometry_wkb") if c in schema.names]
        parquet = pq.ParquetFile(self.osm_path)
        row_offset = 0
        for batch in parquet.iter_batches(columns=columns, batch_size=10000):
            selected = np.arange(len(batch))
            if predicate and pa.types.is_string(schema.field("tags").type):
                mask = None
                for key in predicate:
                    present = pc.match_substring(batch.column("tags"), json.dumps(key))
                    mask = present if mask is None else pc.and_(mask, present)
                selected = np.flatnonzero(pc.fill_null(mask, False).to_numpy(zero_copy_only=False))
            filtered = batch.take(selected)
            geoms = shapely.from_wkb(filtered.column("geometry_wkb").to_pylist(), on_invalid="ignore")
            candidate = np.flatnonzero(shapely.intersects(geoms, extent))
            # Scattered dossiers can span the state. Filter against the actual
            # selected polygons before projecting or decoding local tags.
            if len(candidate):
                local = np.zeros(len(candidate), dtype=bool)
                for geometry in geographic_geometries:
                    local |= shapely.intersects(geometry, geoms[candidate])
                candidate = candidate[local]
            if not len(candidate):
                row_offset += len(batch)
                continue
            rows = filtered.take(candidate).to_pylist()
            kept_rows, kept_geometry, row_numbers = [], [], []
            for j, row in enumerate(rows):
                tags = json.loads(row["tags"]) if isinstance(row["tags"], str) else dict(row["tags"])
                if any(not (key in tags if "*" in (wanted if isinstance(wanted, list) else [wanted])
                            else tags.get(key) in (wanted if isinstance(wanted, list) else [wanted]))
                       for key, wanted in predicate.items()):
                    continue
                searchable = " ".join(f"{k}={v}" for k, v in tags.items()).casefold()
                if tokens and not any(token in searchable for token in tokens):
                    continue
                row["tags"] = tags
                kept_rows.append(row)
                kept_geometry.append(geoms[candidate[j]])
                row_numbers.append(row_offset + int(selected[candidate[j]]))
            row_offset += len(batch)
            if not kept_rows:
                continue
            projected = gpd.GeoSeries(kept_geometry, crs=4326).make_valid().to_crs(target_crs).to_numpy()
            for row, geom, row_number in zip(kept_rows, projected, row_numbers):
                hits = [z for z, zone_geom in metric.items() if geom.intersects(zone_geom)]
                if not hits:
                    continue
                object_id = (f"{row.get('element_type')}:{row['osm_id']}" if row.get("osm_id") is not None
                             else f"parquet_row:{row_number}")
                stored[object_id] = (row, geom, hits)
                if len(stored) > 50000:
                    raise ValueError("raw_query_too_broad: more than 50000 local objects; narrow zones or tag predicate")
        result = {}
        for zone_id in zone_ids:
            matched = [(oid, row, geom, hits) for oid, (row, geom, hits) in stored.items() if zone_id in hits]
            counts = Counter()
            for _, row, _, _ in matched:
                counts.update(f"{k}={v}" for k, v in row["tags"].items())
            matched.sort(key=lambda item: (-int(bool(item[1]["tags"].get("name"))), -len(item[1]["tags"]), item[0]))
            objects = []
            for oid, row, geom, hits in matched[:limit]:
                zone_geom = metric.loc[zone_id]
                clipped = geom.intersection(zone_geom)
                tags = row["tags"]
                keys = list(dict.fromkeys([k for k in ["name", *predicate] if k in tags] + sorted(tags)))
                objects.append({"source_element_id": oid, "name": str(tags.get("name", ""))[:200],
                                "tags": {k: str(tags[k])[:200] for k in keys[:16]}, "tags_truncated": len(keys) > 16,
                                "geometry_type": geom.geom_type, "intersects_requested_zones": hits,
                                "crosses_zone_boundary": bool(geom.intersects(zone_geom.boundary) and not zone_geom.covers(geom)),
                                "clipped_area_km2": float(clipped.area / 1e6) if geom.geom_type in {"Polygon", "MultiPolygon"} else None,
                                "clipped_length_km": float(clipped.length / 1000) if geom.geom_type in {"LineString", "MultiLineString"} else None})
            result[zone_id] = {"available": True, "object_count": len(matched),
                               "top_tags": [{"tag": k, "objects": v} for k, v in counts.most_common(12)],
                               "objects": objects, "objects_truncated": len(matched) > limit,
                               "sample_order": "Named objects first, then number of recorded tags; not an importance ranking.",
                               "intersection_crs": str(target_crs)}
        self._raw_cache[cache_key] = result
        if len(self._raw_cache) > 64:
            self._raw_cache.pop(next(iter(self._raw_cache)))
        return result
