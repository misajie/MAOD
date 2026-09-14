"""Optional raw OSM ingestion; public feature-table mode needs no downloads."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path


def read_objects(path, target_crs=5070, predicate=None):
    import geopandas as gpd
    import pandas as pd
    import shapely
    path = Path(path)
    stream_filtered = False
    if predicate and path.suffix.lower() in {".parquet", ".pq"}:
        import pyarrow as pa
        import pyarrow.parquet as pq
        schema = pq.read_schema(path)
        stream_filtered = 'geometry_wkb' in schema.names and 'tags' in schema.names and pa.types.is_string(schema.field('tags').type)
    if stream_filtered:
        import pyarrow.compute as pc
        import pyarrow.parquet as pq
        pieces = []
        parquet = pq.ParquetFile(path)
        for batch in parquet.iter_batches(batch_size=25000):
            # The extractor stores JSON tags. Arrow rejects most objects by
            # key before Python decodes the much smaller candidate set.
            mask = None
            for key in predicate:
                found = pc.match_substring(batch.column('tags'), json.dumps(key) + ':')
                mask = found if mask is None else pc.and_(mask, found)
            part = batch.filter(mask).to_pandas()
            if part.empty: continue
            part['tags'] = part.tags.map(json.loads)
            keep = pd.Series(True, index=part.index)
            for key, wanted in predicate.items():
                options = wanted if isinstance(wanted, list) else [wanted]
                keep &= part.tags.map(lambda t: key in t if '*' in options else t.get(key) in options)
            if keep.any(): pieces.append(part.loc[keep])
        if not pieces:
            return gpd.GeoDataFrame({'tags': []}, geometry=[], crs=target_crs)
        data = pd.concat(pieces, ignore_index=True)
        frame = gpd.GeoDataFrame(data.drop(columns=['geometry_wkb']), geometry=shapely.from_wkb(data.geometry_wkb), crs=4326)
    elif path.suffix.lower() in {".parquet", ".pq"}:
        try: frame = gpd.read_parquet(path)
        except ValueError:
            data = pd.read_parquet(path)
            frame = gpd.GeoDataFrame(data.drop(columns=["geometry_wkb"]), geometry=shapely.from_wkb(data.geometry_wkb), crs=4326)
    else: frame = gpd.read_file(path)
    if frame.crs is None: raise ValueError("OSM input must declare a CRS")
    if "tags" not in frame: raise ValueError("OSM input requires a tags mapping or JSON string column")
    frame["tags"] = frame.tags.map(lambda t: json.loads(t) if isinstance(t, str) else dict(t))
    if predicate and not stream_filtered:
        for key, wanted in predicate.items():
            options = wanted if isinstance(wanted, list) else [wanted]
            frame = frame.loc[frame.tags.map(lambda t: key in t if '*' in options else t.get(key) in options)].copy()
    frame = frame.loc[frame.geometry.notna() & ~frame.geometry.is_empty & frame.geometry.is_valid].copy()
    if "element_type" in frame and "osm_id" in frame:
        # Areas are emitted after corresponding ways; prefer their assembled
        # geometry for an element represented twice by the PBF callbacks.
        frame = frame.drop_duplicates(["element_type", "osm_id"], keep="last")
    return frame.to_crs(target_crs).reset_index(drop=True)


def tag_inventory(path, limit=500):
    path = Path(path)
    cache = path.with_suffix(path.suffix + ".tag_inventory.json")
    if cache.exists() and cache.stat().st_mtime >= path.stat().st_mtime:
        return json.loads(cache.read_text(encoding="utf-8"))[:limit]
    if path.suffix.lower() in {".parquet", ".pq"}:
        import pyarrow.parquet as pq
        tags = (value for batch in pq.ParquetFile(path).iter_batches(columns=['tags'], batch_size=25000)
                for value in batch.column('tags').to_pylist())
    else: tags = read_objects(path).tags
    counts = Counter()
    for t in tags:
        t = json.loads(t) if isinstance(t, str) else t
        counts.update((str(k), str(v)) for k, v in t.items() if k not in {"name", "source", "note", "fixme", "created_by"} and not k.startswith("addr:"))
    result = [{"name": f"{k}={v}", "source": "raw_osm", "object_count": n,
               "expression": {"op": "osm", "predicate": {k: v}, "aggregation": "count"}}
              for (k, v), n in counts.most_common()]
    cache.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return result[:limit]


def extract_pbf(pbf_path, zones_path, output_path, buffer_m=3000):
    """Stream tagged objects from a regional PBF into a WGS84 WKB parquet.

    No fixed attractor/tag vocabulary is applied. The overall study bounding box
    plus halo limits ingestion; the compiler clips exact zone intersections.
    """
    import geopandas as gpd
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    import shapely
    try: import osmium
    except ImportError as e: raise RuntimeError("Install optional 'osmium' in the selected runtime for PBF ingestion") from e
    with osmium.io.Reader(str(pbf_path)) as reader:
        snapshot_date = reader.header().get("osmosis_replication_timestamp") or None
    source_manifest = None
    manifest_path = Path(pbf_path).parent / "manifest.json"
    if manifest_path.exists():
        candidate = json.loads(manifest_path.read_text(encoding="utf-8"))
        if candidate.get("raw_file") == Path(pbf_path).name:
            source_manifest = {k: candidate.get(k) for k in ("nominal_archive_date", "od_reference_year", "same_year_as_od", "temporal_alignment_note", "download")}
    zones_path = Path(zones_path)
    if zones_path.suffix == ".parquet":
        z = pd.read_parquet(zones_path)
        if "geometry_wkb" in z:
            zones = gpd.GeoDataFrame(z, geometry=shapely.from_wkb(z.geometry_wkb), crs=4326)
        else: zones = gpd.read_parquet(zones_path)
    else: zones = gpd.read_file(zones_path)
    crs = zones.estimate_utm_crs() or 6933
    bounds = zones.to_crs(crs).geometry.buffer(float(buffer_m)).to_crs(4326).total_bounds
    extent = shapely.box(*bounds)
    output_path = Path(output_path); output_path.parent.mkdir(parents=True, exist_ok=True)
    temp = output_path.with_suffix(output_path.suffix + ".partial")
    schema = pa.schema([("element_type", pa.string()), ("osm_id", pa.int64()),
                        ("tags", pa.string()), ("geometry_wkb", pa.binary())])
    writer = pq.ParquetWriter(temp, schema, compression="zstd")
    factory = osmium.geom.WKBFactory()
    class Handler(osmium.SimpleHandler):
        def __init__(self):
            super().__init__(); self.rows = []; self.count = 0; self.geometry_errors = 0
        def emit(self, obj, kind, wkb, oid=None):
            try:
                geometry = shapely.from_wkb(wkb)
                if geometry.is_empty or not geometry.is_valid or not geometry.intersects(extent): return
                tags = {str(t.k): str(t.v) for t in obj.tags}
                self.rows.append({"element_type": kind, "osm_id": int(oid if oid is not None else obj.id),
                                  "tags": json.dumps(tags, ensure_ascii=False), "geometry_wkb": shapely.to_wkb(geometry)})
                if len(self.rows) >= 25000: self.flush()
            except (ValueError, RuntimeError): self.geometry_errors += 1
        def flush(self):
            if self.rows:
                writer.write_table(pa.Table.from_pylist(self.rows, schema=schema)); self.count += len(self.rows); self.rows = []
                print(f"OSM extracted objects: {self.count}", flush=True)
        def node(self, n):
            if len(n.tags) and n.location.valid():
                if bounds[0] <= n.location.lon <= bounds[2] and bounds[1] <= n.location.lat <= bounds[3]:
                    self.emit(n, "node", bytes.fromhex(factory.create_point(n)))
        def way(self, w):
            if not len(w.tags): return
            if w.is_closed() and not any(k in w.tags for k in ("highway", "railway", "waterway", "barrier")): return
            try: self.emit(w, "way", bytes.fromhex(factory.create_linestring(w)))
            except (RuntimeError, ValueError): self.geometry_errors += 1
        def area(self, a):
            if not len(a.tags): return
            try: self.emit(a, "way" if a.from_way() else "relation", bytes.fromhex(factory.create_multipolygon(a)), a.orig_id())
            except (RuntimeError, ValueError): self.geometry_errors += 1
    handler = Handler()
    try:
        handler.apply_file(str(pbf_path), locations=True, idx="flex_mem")
        handler.flush()
    finally: writer.close()
    temp.replace(output_path)
    metadata = {"source_pbf": str(Path(pbf_path).resolve()), "study_bounds": bounds.tolist(),
                "osm_snapshot_date": snapshot_date,
                "source_manifest": source_manifest,
                "buffer_m": buffer_m, "objects": handler.count, "geometry_errors": handler.geometry_errors,
                "units": "WGS84 geometry; projected on execution", "tag_vocabulary": "all observed tagged objects"}
    output_path.with_suffix(output_path.suffix + ".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata
