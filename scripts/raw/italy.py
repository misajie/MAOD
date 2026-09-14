"""Prepare ISTAT 2011 municipality commuting raw data, without grids or modelling.

E:\\conda\\envs\\my-neuro\\python.exe scripts/raw/italy.py [--offline]
Uses only S (summary) records and actual Numero di individui for work-purpose OD.
L records describe overlapping detailed transport strata and are never added to S.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "data/raw/italy"
ORIGINAL = BASE / "original"
ALIGNED = BASE / "aligned"
SOURCES = {
    "matrici_pendolarismo_2011.zip": "https://www.istat.it/storage/cartografia/matrici_pendolarismo/matrici_pendolarismo_2011.zip",
    "Limiti_2011_WGS84.zip": "https://www.istat.it/storage/cartografia/confini_amministrativi/non_generalizzati/2011/Limiti_2011_WGS84.zip",
    "istat_pendolarismo_2011.html": "https://www.istat.it/non-categorizzato/matrici-del-pendolarismo/",
    "istat_boundaries.html": "https://www.istat.it/it/archivio/222527",
    "istat_legal_notice.html": "https://www.istat.it/note-legali/",
}
FIELD_SPECS = [
    ("record_type", 1, 1), ("residence_type", 3, 1), ("origin_province", 5, 3),
    ("origin_municipality", 9, 3), ("sex", 14, 1), ("purpose", 16, 1),
    ("destination_location_type", 18, 1), ("destination_province", 20, 3),
    ("destination_municipality", 24, 3), ("foreign_country", 28, 3),
    ("transport_mode", 32, 2), ("departure_time", 35, 1), ("duration", 37, 1),
    ("estimated_persons", 39, 12), ("persons", 51, 10),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record(path: Path) -> dict:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"path": path.relative_to(BASE).as_posix(), "bytes": path.stat().st_size,
            "sha256": digest.hexdigest()}


def download(offline: bool) -> list[dict]:
    ORIGINAL.mkdir(parents=True, exist_ok=True)
    receipt_path = ORIGINAL / "download_receipts.json"
    receipts = {}
    if receipt_path.exists():
        receipts = {x["name"]: x for x in json.loads(receipt_path.read_text(encoding="utf-8"))}
    for name, url in SOURCES.items():
        target = ORIGINAL / name
        if target.exists():
            receipts.setdefault(name, {"name": name, "url": url, "resolved_url": url,
                "retrieved_utc": datetime.fromtimestamp(target.stat().st_mtime, timezone.utc).isoformat()})
            continue
        if offline:
            raise FileNotFoundError(target)
        with requests.get(url, stream=True, timeout=(20, 180)) as response:
            response.raise_for_status()
            partial = target.with_name(target.name + ".part")
            with partial.open("wb") as stream:
                for chunk in response.iter_content(1024 * 1024):
                    stream.write(chunk)
            partial.replace(target)
            receipts[name] = {"name": name, "url": url, "resolved_url": response.url,
                "retrieved_utc": now(), "http_last_modified": response.headers.get("Last-Modified")}
    receipt_path.write_text(json.dumps(list(receipts.values()), indent=2) + "\n", encoding="utf-8")
    return [dict(receipts[name], **record(ORIGINAL / name)) for name in SOURCES]


def extract_documentation() -> list[dict]:
    members = []
    for archive_name in ["matrici_pendolarismo_2011.zip", "Limiti_2011_WGS84.zip"]:
        with zipfile.ZipFile(ORIGINAL / archive_name) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                members.append({"archive": archive_name, "member": info.filename,
                    "uncompressed_bytes": info.file_size, "zip_crc32": f"{info.CRC:08x}"})
                if info.filename.lower().endswith((".doc", ".xls", ".xlsx", ".csv", ".pdf")):
                    name = Path(info.filename).name
                    target = ORIGINAL / name
                    if not target.exists():
                        target.write_bytes(archive.read(info))
    (ORIGINAL / "archive_members.json").write_text(json.dumps(members, indent=2) + "\n", encoding="utf-8")
    return members


def write_dictionaries() -> None:
    dictionary = {
        "source": "leggimi file matrix_pendo2011_10112014.doc (inside original archive)",
        "format": "Fixed-width ASCII data; positions below are 1-based, including spaces",
        "fields": [{"name": n, "start_1_based": s, "length": length} for n, s, length in FIELD_SPECS],
        "record_type": {"S": "Summary: actual counts by residence/sex/purpose/location/OD/country", "L": "Overlapping detailed strata including mode/departure/duration; sample-based estimates in municipalities >=20,000 residents"},
        "residence_type": {"1": "private household (famiglia)", "2": "communal establishment (convivenza)"},
        "sex": {"1": "male", "2": "female"},
        "purpose": {"1": "study (includes nursery, preschool and vocational education)", "2": "work"},
        "destination_location_type": {"1": "same municipality", "2": "another Italian municipality", "3": "abroad"},
        "transport_mode": {"01": "train", "02": "tram", "03": "metro", "04": "urban bus/trolleybus", "05": "interurban bus", "06": "company/school bus", "07": "private car driver", "08": "private car passenger", "09": "motorcycle/moped/scooter", "10": "bicycle", "11": "other", "12": "on foot"},
        "departure_time": {"1": "before 07:15", "2": "07:15-08:14", "3": "08:15-09:14", "4": "after 09:14"},
        "duration": {"1": "up to 15 minutes", "2": "16-30 minutes", "3": "31-60 minutes", "4": "more than 60 minutes"},
        "tokens": {"ND": "not available; never a numeric zero", "+": "dimension aggregated/not applicable on S record", "000": "not an Italian municipality ID by itself; see destination_location_type and foreign_country"},
        "selected_count": "persons (Numero di individui) on S records; do not use estimated_persons and do not sum S+L",
        "commuting_universe": "Residents declaring daily travel from their residence to their usual work/study location and daily return, census 2011-10-09",
    }
    (BASE / "data_dictionary.json").write_text(json.dumps(dictionary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    municipal = pd.read_excel(ORIGINAL / "Codici Comuni italiani_1 gennaio 2011.xls", sheet_name="COMUNI 01_01_2011", dtype=str)
    municipal.columns = [re.sub(r"\s+", " ", str(x)).strip() for x in municipal.columns]
    municipal.insert(0, "zone_id", municipal.iloc[:, 1].str.zfill(3) + municipal.iloc[:, 2].str.zfill(3))
    municipal.to_parquet(ALIGNED / "municipality_codebook.parquet", index=False)
    foreign = pd.read_excel(ORIGINAL / "Codici Stati Esteri_8 ottobre 2011.xls", header=None, dtype=str)
    foreign = foreign.loc[foreign[0].fillna("").str.fullmatch(r"\d{3}"), [0, 1, 2]].copy()
    foreign.columns = ["foreign_country", "name_it", "name_en"]
    foreign.to_parquet(ALIGNED / "foreign_country_codebook.parquet", index=False)


def read_s_records() -> tuple[pd.DataFrame, dict]:
    raw_counts = Counter()
    rows = []
    with zipfile.ZipFile(ORIGINAL / "matrici_pendolarismo_2011.zip") as archive:
        member = "MATRICE PENDOLARISMO 2011/matrix_pendo2011_10112014.txt"
        with archive.open(member) as stream:
            for source_line, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                rtype = line[:1].decode("ascii")
                raw_counts[rtype] += 1
                if rtype != "S":
                    continue
                values = [line[start - 1:start - 1 + length].decode("ascii").strip()
                          for _, start, length in FIELD_SPECS]
                rows.append([source_line] + values)
    table = pd.DataFrame(rows, columns=["source_line"] + [f[0] for f in FIELD_SPECS])
    table["persons"] = pd.to_numeric(table.persons.replace("ND", pd.NA)).astype("Int64")
    table["estimated_persons"] = pd.to_numeric(table.estimated_persons.replace("ND", pd.NA)).astype("Float64")
    table["origin"] = table.origin_province + table.origin_municipality
    table["destination"] = table.destination_province + table.destination_municipality
    abroad = table.destination_location_type == "3"
    table.loc[abroad, "destination"] = "EXT:" + table.loc[abroad, "foreign_country"]
    table.to_parquet(ALIGNED / "source_summary_records.parquet", index=False)
    stats = {"raw_records_by_type": dict(raw_counts), "summary_records": len(table),
             "all_purpose_persons": int(table.persons.sum()),
             "persons_by_purpose": {str(k): int(v) for k, v in table.groupby("purpose").persons.sum().items()},
             "persons_by_residence_type": {str(k): int(v) for k, v in table.groupby("residence_type").persons.sum().items()},
             "summary_missing_persons": int(table.persons.isna().sum()),
             "summary_zero_persons": int((table.persons == 0).sum()),
             "summary_minimum_persons": int(table.persons.min())}
    return table, stats


def read_zones() -> tuple[gpd.GeoDataFrame, str]:
    archive = ORIGINAL / "Limiti_2011_WGS84.zip"
    member = "Limiti_2011_WGS84/Com2011_WGS84/Com2011_WGS84.shp"
    zones = gpd.read_file("/vsizip/" + archive.as_posix() + "/" + member)
    original_crs = str(zones.crs)
    zones["zone_id"] = zones.PRO_COM.astype(int).astype(str).str.zfill(6)
    zones["province_id"] = zones.COD_PRO.astype(int).astype(str).str.zfill(3)
    zones["region_id"] = zones.COD_REG.astype(int).astype(str).str.zfill(2)
    zones = zones.rename(columns={"COMUNE": "zone_name"})
    zones = zones[["zone_id", "zone_name", "province_id", "region_id", "geometry"]].sort_values("zone_id").to_crs("EPSG:4326")
    repaired = zones.loc[~zones.geometry.is_valid, "zone_id"].tolist()
    zones.geometry = zones.geometry.make_valid()
    zones.attrs["repaired_zone_ids"] = repaired
    zones.to_parquet(ALIGNED / "zones.parquet", index=False)
    zones.to_file(ALIGNED / "zones.geojson", driver="GeoJSON", index=False, COORDINATE_PRECISION=17)
    return zones, original_crs


def align_flows(table: pd.DataFrame, zones: gpd.GeoDataFrame) -> dict:
    zone_ids = set(zones.zone_id)
    work = table.loc[table.purpose == "2"].copy()
    foreign = work.destination_location_type == "3"
    located = work.origin.isin(zone_ids) & work.destination.isin(zone_ids) & ~foreign
    domestic = work.loc[located].groupby(["origin", "destination"], as_index=False).persons.sum().rename(columns={"persons": "flow"})
    domestic["flow"] = domestic.flow.astype("int64")
    domestic.to_parquet(ALIGNED / "flows.parquet", index=False)
    domestic.to_csv(ALIGNED / "flows.csv", index=False)
    external = work.loc[foreign].groupby(["origin", "destination", "foreign_country"], as_index=False).persons.sum().rename(columns={"persons": "flow"})
    external.to_parquet(ALIGNED / "external_flows.parquet", index=False)
    unresolved = work.loc[~located & ~foreign].copy()
    unresolved["reason"] = "Origin or domestic destination municipality not matched to official 2011 geometry"
    text_columns = [n for n, _, _ in FIELD_SPECS if n not in {"persons", "estimated_persons"}]
    unresolved = unresolved.astype({n: "string" for n in text_columns + ["origin", "destination", "reason"]})
    unresolved.to_parquet(ALIGNED / "unlocated_flows.parquet", index=False)
    combined = work.groupby(["origin", "destination", "destination_location_type", "foreign_country"], as_index=False).persons.sum().rename(columns={"persons": "flow"})
    combined.to_parquet(ALIGNED / "work_flows_all_destinations.parquet", index=False)
    by_purpose = table.groupby(["origin", "destination", "purpose", "destination_location_type", "foreign_country"], as_index=False).persons.sum().rename(columns={"persons": "flow"})
    by_purpose.to_parquet(ALIGNED / "flows_by_purpose.parquet", index=False)
    return {"work_summary_rows": len(work), "work_persons_total": int(work.persons.sum()),
            "domestic_work_od_rows": len(domestic), "domestic_work_persons": int(domestic.flow.sum()),
            "unique_domestic_origins": int(domestic.origin.nunique()), "unique_domestic_destinations": int(domestic.destination.nunique()),
            "self_loop_rows": int((domestic.origin == domestic.destination).sum()),
            "domestic_min_flow": int(domestic.flow.min()), "domestic_max_flow": int(domestic.flow.max()),
            "external_work_od_rows": len(external), "external_work_persons": int(external.flow.sum()),
            "unlocated_work_summary_rows": len(unresolved), "unlocated_work_persons": int(unresolved.persons.sum()),
            "zones_without_published_domestic_outflow": sorted(zone_ids - set(domestic.origin)),
            "zones_without_published_domestic_inflow": sorted(zone_ids - set(domestic.destination))}


def write_readme(stats: dict) -> None:
    text = f"""# Italy: ISTAT 2011 raw commuting data

Official municipality (comune) residence-to-usual-workplace counts for Italy,
census reference date **9 October 2011**. Main files contain work purpose only,
residents in private households and communal establishments, both sexes.

This is raw download and field alignment. No grids, spatial tiles, model
features, train/validation/test split, training, prediction, or tests were produced.
Original OSM files are separately acquired in `osm/`, including a current
snapshot and a 2014 historical snapshot. Dates/checksums are in their manifests.

## Files and use

- `original/matrici_pendolarismo_2011.zip`: unchanged official archive, containing
  all 4,876,242 records, study/work purposes, summary and detailed records,
  methods/record layout, classification workbooks, and census questionnaires.
- `original/Limiti_2011_WGS84.zip`: unchanged official non-generalized boundaries,
  with municipality, province, and region shapefiles and municipality list.
- `original/`: downloaded source/license pages and separately extracted official
  documentation/classifications. The DOC was also converted to TXT for reading;
  that TXT is a local derived document (GBK encoding), not an official raw file.
- `aligned/flows.parquet` and `flows.csv`: `origin,destination,flow`; six-character
  strings, domestic municipality endpoints matched to 2011 geometry, work only.
- `aligned/zones.parquet`: GeoParquet, EPSG:4326, `zone_id` string; municipality
  polygons also available as `zones.geojson`. No simplification. Precision-induced
  self-intersections after reprojection are repaired in aligned copies only;
  repaired IDs are recorded. The original ZIP remains unchanged.
- `aligned/source_summary_records.parquet`: all S rows with original dimensions,
  counts, sampled estimates, source line numbers, and code-derived endpoint IDs.
- `aligned/flows_by_purpose.parquet`: study and work retained as separate rows.
- `aligned/work_flows_all_destinations.parquet`: work totals including abroad.
- `aligned/external_flows.parquet`: foreign destinations coded `EXT:<country>`;
  no invented foreign or Italian polygons.
- `aligned/unlocated_flows.parquet`: any domestic S work record whose endpoints
  cannot match geometry, preserving source fields rather than assigning a zone.
- `data_dictionary.json`: fixed-width positions, categorical codes, selection rules.
- `source_manifest.json`: URLs, dates, SHA-256, archive membership and statistics.

## Exact counting rule

Read **record type S**, **purpose 2 (work)**, and the actual **Numero di individui**
field (columns 51-60, 1-based). Sum the disjoint sex and residence-type strata once
per OD pair. Retain self-loops. Do not sum S and L: L is an overlapping detailed
representation by mode, departure time, and duration. Do not use `Stima numero di
individui` for aggregate OD. Its decimals and occasional zeros arise from sampling;
the codebook explicitly recommends the actual-count field for S-level analyses.
Study is purpose 1 and is never added to work. `ND` means unavailable, not zero;
`+` marks an aggregated dimension.

The commuting universe is people declaring daily travel from their residence to a
usual work/study location and return to that residence. It excludes noncommuters,
non-daily trips and other trip purposes. Counts are commuters, not two-way trip legs.
Abroad is explicit and remains separate. Domestic row sums exclude foreign workers.
No suppression threshold is declared by the attached codebook; observed counts
include 1. Absent pairs are unreported in this sparse release; this preparation
does not densify or claim that every absent pair is an independently observed zero.

## Deep Gravity relationship

The local paper `P03_deepgravity.pdf`, Methods pp. 10-11, says Italy uses
**402,678 Census Areas (CAs)** and reports 15,003,287 commuters after its processing.
The directly downloadable ISTAT 2011 matrix explicitly uses **municipalities**.
This package is therefore a genuine, fully documented municipality-level 2011
alternative, **not an exact reconstruction of the paper's CA-level OD benchmark**.
Municipality flows are not disaggregated to census areas. The legacy paper-linked
`datiopen.istat.it/datasetPND.php` endpoint was unavailable during this download.
ISTAT's official platform notice says "La piattaforma non è più attiva."
The notice is at https://www.istat.it/notizia/linked-open-data/ and is archived in
`data/raw/_documentation/deepgravity/istat_lod_platform_closed.html`.

The separate `original/census_sections/` contains all 20 regional 2011 census
boundary ZIPs and the original census attribute archive `dati-cpa_2011.zip`.
Their national index in `census_sections/section_id_mapping.parquet` contains
402,678 section IDs, matching the paper count. These are boundaries and attributes,
not the missing section-to-section OD. See `census_sections/manifest.json`.

## Statistics

- Official municipalities: {stats['zone_count']:,}
- Main domestic work OD pairs: {stats['domestic_work_od_rows']:,}
- Domestic work commuters: {stats['domestic_work_persons']:,}
- Work commuters to foreign countries: {stats['external_work_persons']:,}
- Unmatched domestic work persons: {stats['unlocated_work_persons']:,}
- All work + study actual persons in S records: {stats['all_purpose_persons']:,}

## Rebuild and license

Run `E:\\conda\\envs\\my-neuro\\python.exe scripts/raw/italy.py` from the project.
Use `--offline` to reuse downloaded originals. Dependencies are requests, pandas,
pyarrow, geopandas/pyogrio, and xlrd. Original ZIP files remain unchanged.

ISTAT's legal notice specifies Creative Commons Attribution 4.0 unless otherwise
indicated. Attribute ISTAT, link CC BY 4.0, and identify this field-alignment work.
Original source URLs are in `source_manifest.json`.
"""
    (BASE / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    sources = download(args.offline)
    ALIGNED.mkdir(parents=True, exist_ok=True)
    members = extract_documentation()
    write_dictionaries()
    table, stats = read_s_records()
    zones, original_crs = read_zones()
    stats.update(align_flows(table, zones))
    stats.update({"zone_count": len(zones), "zone_id_unique_count": int(zones.zone_id.nunique()),
                  "bounds_wgs84": zones.total_bounds.tolist(),
                  "repaired_zone_ids": zones.attrs.get("repaired_zone_ids", []),
                  "aligned_invalid_geometries": int((~zones.is_valid).sum())})
    write_readme(stats)
    manifest = {
        "schema_version": "1.0", "created_utc": now(), "status": "raw_downloaded_and_aligned",
        "country": "Italy", "geographic_scope": "Nationwide, municipalities (comuni), no grids or partitions",
        "reference_date": "2011-10-09", "publisher": "Istituto Nazionale di Statistica (ISTAT)",
        "flow_semantics": "Actual census count of residents declaring daily home-to-usual-workplace commute and daily return; work purpose 2 only for main flows",
        "native_od_unit": "municipality", "zone_id_type": "six-character string: 3-digit province + 3-digit municipality",
        "selection": {"record_type": "S", "purpose": "2", "count_field": "Numero di individui (columns 51-60, 1-based)",
                      "residence_type": ["1", "2"], "sex": ["1", "2"], "aggregation": "Sum mutually exclusive sex/residence strata once per OD", "self_loops": "retained"},
        "boundaries": {"reference_date": "2011-10-09", "original_crs": original_crs,
                       "aligned_crs": "EPSG:4326", "native_id_field": "PRO_COM", "processing": "Zero-pad native municipality code to 6 digits and reproject; make_valid on aligned geometries resolves precision-induced self-intersections; repaired IDs recorded. Original ZIP unchanged. No dissolve, simplify, or subdivision", "geo_parquet": "aligned/zones.parquet"},
        "missingness": {"ND": "not available, not zero", "+": "aggregated dimension on S rows", "L": "overlapping sampled detail, excluded from main aggregation", "suppression_threshold": None,
                        "threshold_evidence": "No threshold is stated in official attached record layout; positive actual counts include 1",
                        "absent_pairs": "not explicitly present in sparse file; not filled with zero",
                        "external": "foreign-country endpoints retained separately, with EXT: prefix",
                        "unlocated": "domestic records unmatched to 2011 boundaries retained separately",
                        "outflow": "main row sums include domestic workplaces only"},
        "dgm_alignment": {"exact_replication": False, "paper_local_path": "resources/aamas2027literature/cited/sources/pdf/P03_deepgravity.pdf", "paper_pages": [10, 11], "paper_italy_unit": "402678 Census Areas", "downloaded_unit": "8092 municipalities", "limitation": "Public municipality OD cannot be disaggregated into the paper's CA-level OD without fabrication", "legacy_endpoint": "http://datiopen.istat.it/datasetPND.php", "legacy_access_status": "HTTP 502 and HTTPS SSL connection failure at time of retrieval", "official_closure_notice": "https://www.istat.it/notizia/linked-open-data/", "official_closure_quote": "La piattaforma non è più attiva.", "official_closure_archive": "data/raw/_documentation/deepgravity/istat_lod_platform_closed.html"},
        "license": {"id": "CC-BY-4.0", "url": "https://creativecommons.org/licenses/by/4.0/", "policy_url": SOURCES["istat_legal_notice.html"], "attribution": "ISTAT; derived field alignment by this project; changes indicated"},
        "sources": sources, "archive_members": members,
        "documentary_provenance": {"official_files": "ZIP originals and byte-identical archive documentation/codebook members", "derived_readable_document": {"path": "original/leggimi file matrix_pendo2011_10112014.txt", "source": "original/leggimi file matrix_pendo2011_10112014.doc", "conversion": "LibreOffice headless TXT export", "encoding": "GBK", "official_original": False}, "local_metadata": ["original/download_receipts.json", "original/archive_members.json"]},
        "original_files": [record(p) for p in sorted(ORIGINAL.iterdir()) if p.is_file()],
        "aligned_files": [record(p) for p in sorted(ALIGNED.iterdir()) if p.is_file()],
        "statistics": stats, "reconstruction_script": "scripts/raw/italy.py",
        "raw_only": {"osm": False, "tiles": False, "splits": False, "training": False, "tests": False},
    }
    (BASE / "source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=True, indent=2), flush=True)


if __name__ == "__main__":
    main()
