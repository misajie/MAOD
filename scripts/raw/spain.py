"""Download and align official INE residence--workplace data for two Spanish regions.

This is raw data preparation only. It creates no spatial tiles, train/test splits,
features, fitted models, predictions, or tests. Scope is province 28 (Madrid) and
province 08 (Barcelona), using municipalities as the native OD units.

Run with: E:\\conda\\envs\\my-neuro\\python.exe scripts/raw/spain.py
Dependencies: requests, pandas, pyxlsb, geopandas, pyogrio, shapely, pyproj.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests
from pyxlsb import open_workbook


ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    "matriz_ocu_anonim.xlsb": "https://www.ine.es/metodologia/t20/matriz_ocu_anonim.xlsb",
    "seccionado_2023.zip": "https://www.ine.es/prodyser/cartografia/seccionado_2023.zip",
    "ine_census_results.html": "https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736176992&menu=resultados&idp=1254735572981",
    "meto_censo_poblacion_anual.pdf": "https://www.ine.es/metodologia/t20/meto_censo_poblacion_anual.pdf",
    "ine_legal_notice.html": "https://www.ine.es/dyngs/AYU/index.htm?cid=125",
}
CITIES = {
    "madrid": ("28", "Madrid province / Community of Madrid"),
    "barcelona": ("08", "Barcelona province"),
}


def utc_timestamp(ts: float | None = None) -> str:
    d = datetime.now(timezone.utc) if ts is None else datetime.fromtimestamp(ts, timezone.utc)
    return d.isoformat()


def file_record(path: Path, base: Path) -> dict:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return {"path": path.relative_to(base).as_posix(), "bytes": path.stat().st_size,
            "sha256": h.hexdigest()}


def acquire(allow_network: bool) -> dict:
    first = ROOT / "data/raw/madrid/original"
    first.mkdir(parents=True, exist_ok=True)
    receipts = {}
    for name, url in SOURCES.items():
        target = first / name
        headers = {}
        if not target.exists():
            if not allow_network:
                raise FileNotFoundError(target)
            with requests.get(url, timeout=(20, 180), stream=True) as response:
                response.raise_for_status()
                headers = dict(response.headers)
                part = target.with_name(target.name + ".part")
                with part.open("wb") as f:
                    for block in response.iter_content(1024 * 1024):
                        f.write(block)
                part.replace(target)
        elif allow_network:
            try:
                response = requests.head(url, timeout=30)
                response.raise_for_status()
                headers = dict(response.headers)
            except requests.RequestException:
                pass
        receipts[name] = {"url": url, "retrieved_utc": utc_timestamp(target.stat().st_mtime),
                          "http_last_modified": headers.get("Last-Modified"),
                          "http_etag": headers.get("ETag"),
                          "retrieval_note": "Raw bytes preserved; existing local downloads reused when present."}
        for city in CITIES:
            dest = ROOT / "data/raw" / city / "original" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.resolve() != target.resolve() and not dest.exists():
                shutil.copy2(target, dest)
    return receipts


def read_source_flows() -> tuple[pd.DataFrame, list[str]]:
    records = []
    path = ROOT / "data/raw/madrid/original/matriz_ocu_anonim.xlsb"
    with open_workbook(str(path)) as book:
        sheets = book.sheets
        with book.get_sheet("C23") as sheet:
            for row_number, row in enumerate(sheet.rows(), start=1):
                cells = [c.v for c in row]
                if len(cells) < 9 or not isinstance(cells[8], (float, int)):
                    continue
                records.append({
                    "source_row": row_number,
                    "origin_province": str(cells[0]),
                    "origin_municipality": str(cells[2]),
                    "origin_name": str(cells[3] or ""),
                    "destination_province": str(cells[4]),
                    "destination_municipality": str(cells[6]),
                    "destination_name": str(cells[7] or ""),
                    "flow": int(cells[8]),
                })
    flows = pd.DataFrame(records)
    flows["origin"] = flows.origin_province + flows.origin_municipality
    flows["destination"] = flows.destination_province + flows.destination_municipality
    return flows, sheets


def read_source_zones() -> gpd.GeoDataFrame:
    archive = ROOT / "data/raw/madrid/original/seccionado_2023.zip"
    with zipfile.ZipFile(archive) as z:
        shp = next(n for n in z.namelist() if n.lower().endswith(".shp"))
    path = "/vsizip/" + archive.as_posix() + "/" + shp
    return gpd.read_file(path, where="CPRO IN ('28', '08')")


def prepare(city: str, all_flows: pd.DataFrame, sections: gpd.GeoDataFrame,
            sheets: list[str], receipts: dict) -> dict:
    province, scope = CITIES[city]
    base = ROOT / "data/raw" / city
    aligned = base / "aligned"
    aligned.mkdir(parents=True, exist_ok=True)
    original_sections = sections.loc[sections.CPRO == province].copy()
    municipalities = original_sections[["CUMUN", "NMUN", "CPRO", "geometry"]].dissolve(
        by="CUMUN", as_index=False, aggfunc="first")
    municipalities = municipalities.rename(columns={"CUMUN": "zone_id", "NMUN": "zone_name", "CPRO": "province_id"})
    municipalities["zone_id"] = municipalities.zone_id.astype(str)
    municipalities["boundary_reference_date"] = "2023-01-01"
    municipalities = municipalities.sort_values("zone_id").to_crs("EPSG:4326")
    repaired_ids = municipalities.loc[~municipalities.geometry.is_valid, "zone_id"].tolist()
    municipalities.geometry = municipalities.geometry.make_valid()
    zones_path = aligned / "zones.geojson"
    municipalities.to_file(zones_path, driver="GeoJSON", index=False, COORDINATE_PRECISION=17)
    municipalities.to_parquet(aligned / "zones.parquet", index=False)
    municipalities.drop(columns="geometry").to_csv(aligned / "zone_id_mapping.csv", index=False)
    municipality_ids = set(municipalities.zone_id)
    internal = all_flows.loc[(all_flows.origin_province == province)
                             & (all_flows.destination_province == province)].copy()
    located = internal.origin.isin(municipality_ids) & internal.destination.isin(municipality_ids)
    unavailable = internal.loc[~located].copy()
    unavailable["exclusion_reason"] = "Source municipality is unspecified or absent from official 2023 geography"
    unavailable.to_csv(aligned / "unlocated_flows.csv", index=False, encoding="utf-8")
    selected = internal.loc[located, ["origin", "destination", "flow"]].sort_values(["origin", "destination"])
    selected.to_csv(aligned / "flows.csv", index=False, encoding="utf-8")
    selected.to_parquet(aligned / "flows.parquet", index=False)
    # Keep named source columns for every published selected row; no inferred zeros.
    long_rows = internal.copy()
    long_rows.insert(0, "census_reference_date", "2023-01-01")
    long_rows["included_in_flows_csv"] = located.values
    long_rows.to_csv(aligned / "source_rows_2023.csv", index=False, encoding="utf-8")
    origins = set(selected.origin)
    destinations = set(selected.destination)
    missing_origin = sorted(municipality_ids - origins)
    missing_destination = sorted(municipality_ids - destinations)
    outward = all_flows.loc[(all_flows.origin_province == province) & (all_flows.destination_province != province)]
    inward = all_flows.loc[(all_flows.origin_province != province) & (all_flows.destination_province == province)]
    external = pd.concat([outward.assign(scope="outbound"), inward.assign(scope="inbound"),
                          unavailable.assign(scope="unlocated_intraprovince")], ignore_index=True)
    external.to_parquet(aligned / "external_flows.parquet", index=False)
    external.to_csv(aligned / "external_flows.csv", index=False, encoding="utf-8")
    stats = {
        "zone_count": len(municipalities), "source_census_section_count": len(original_sections),
        "published_internal_od_rows": len(selected), "published_internal_people_sum": int(selected.flow.sum()),
        "unique_origins": len(origins), "unique_destinations": len(destinations),
        "self_loop_rows": int((selected.origin == selected.destination).sum()),
        "minimum_published_flow": int(selected.flow.min()), "maximum_published_flow": int(selected.flow.max()),
        "duplicate_od_rows": int(selected.duplicated(["origin", "destination"]).sum()),
        "unlocated_intraprovince_rows": len(unavailable), "unlocated_intraprovince_people_sum": int(unavailable.flow.sum()),
        "published_outward_rows_not_in_internal_matrix": len(outward),
        "published_outward_people_not_in_internal_matrix": int(outward.flow.sum()),
        "published_inward_rows_not_in_internal_matrix": len(inward),
        "published_inward_people_not_in_internal_matrix": int(inward.flow.sum()),
        "zones_without_published_internal_outflow": missing_origin,
        "zones_without_published_internal_inflow": missing_destination,
        "national_source_rows_in_C23": len(all_flows),
        "geographic_bounds_wgs84": municipalities.total_bounds.tolist(),
        "repaired_after_wgs84_transform_zone_ids": repaired_ids,
        "aligned_invalid_geometries": int((~municipalities.geometry.is_valid).sum()),
    }
    manifest = {
        "schema_version": "1.0", "created_utc": utc_timestamp(),
        "city_key": city, "status": "raw_downloaded_and_fields_aligned",
        "scope": {"name": scope, "province_code": province, "country": "Spain", "zone_unit": "municipality",
                  "scope_caveat": "Province-wide region, not the core city municipality or an official functional urban area. No artificial grids or spatial train/test partitions were created."},
        "flow_source": {"publisher": "Instituto Nacional de Estadistica (INE)",
                        "title": "Matriz de municipio de residencia por municipio de trabajo",
                        "operation": "Censo anual de poblacion (Ocupacion y actividad)",
                        "selected_sheet": "C23", "reference_date": "2023-01-01",
                        "preserved_original_sheets": sheets,
                        "unit": "Employed persons aged 16 years and over",
                        "semantics": "Registered usual residence municipality to registered workplace municipality; administrative census OD counts, not model predictions and not a measured number of daily trips.",
                        "methodology_pages": [7, 19, 21, 22, 28],
                        "remote_work_caveat": "Registered home-work pairs can include telework; the matrix does not establish physical daily travel frequency."},
        "disclosure_and_missingness": {
            "source_note_verbatim": "* Sólo se muestran las combinaciones con al menos 5 ocupados",
            "publication_threshold_people": 5,
            "absent_pair_semantics": "Not published: true zero and suppressed counts below 5 cannot be distinguished. No missing pair has been filled with zero.",
            "source_unspecified_municipality": "No consta records are preserved in source_rows_2023.csv and unlocated_flows.csv; they are not assigned fabricated polygons.",
            "support": "Both municipalities belong to the selected province and have official 2023 geometry.",
            "cross_boundary": "Excluded from the internal aligned matrix; external_flows.parquet/csv preserves incoming/outgoing and unlocated records with a scope flag. The original national workbook also remains intact.",
            "totals": "Aligned row sums are published internal subtotals, not exact true outflow totals because of suppression, unknown municipality, and excluded cross-boundary links.",
            "self_loops": "Retained when published; same municipality residence and workplace is not evidence of zero travel."},
        "boundaries": {"publisher": "INE", "title": "Seccionado censal 2023", "reference_date": "2023-01-01",
                       "original_crs": str(sections.crs), "aligned_crs": "EPSG:4326",
                       "native_polygon_unit_in_download": "census section",
                       "alignment": "Union official census sections by their official CUMUN municipality code; preserve all municipalities in the province. After WGS84 reprojection, make_valid resolves precision-induced self-intersections in aligned copies only; repaired IDs are recorded. No simplification or synthetic zone construction; source ZIP is unchanged.",
                       "source_id": "CUMUN", "aligned_id": "zone_id",
                       "id_mapping": "two-character province + three-character municipality, preserved as a five-character string"},
        "license": {"identifier": "CC-BY-4.0", "url": "https://creativecommons.org/licenses/by/4.0/",
                    "policy_url": SOURCES["ine_legal_notice.html"],
                    "basis": "INE legal notice states CC BY 4.0 is its default statistical-information reuse license unless otherwise specified, for information originally sourced from INE.",
                    "attribution": "Elaboracion propia con datos extraidos del sitio web del INE: www.ine.es"},
        "field_alignment": {"origin": "Provincia de residencia + Municipio de residencia",
                            "destination": "Provincia de trabajo + Municipio de trabajo",
                            "flow": "Ocupados de 16 y mas anos, worksheet C23",
                            "zone_id": "Official CUMUN"},
        "sources": [dict(receipts[name], **file_record(base / "original" / name, base)) for name in SOURCES],
        "aligned_files": [file_record(p, base) for p in sorted(aligned.iterdir()) if p.is_file()],
        "statistics": stats,
        "reconstruction_script": "scripts/raw/spain.py",
        "raw_only": {"training": False, "tests": False, "spatial_partitioning": False, "osm_processing": False},
        "source_selection_notes": [
            "CommutingODGen-Dataset repository was checked and describes United States areas only; it does not supply Madrid or Barcelona.",
            "INE 2019 mobile-positioning daily mobility is a different data product and was not substituted for the residence-workplace matrix.",
            "The original national workbook retains C21, C22, and C23 separately; no years or purposes were summed."],
    }
    (base / "source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Reuse existing original files without network access")
    args = parser.parse_args()
    receipts = acquire(not args.offline)
    flows, sheets = read_source_flows()
    sections = read_source_zones()
    for city in CITIES:
        print(json.dumps({"city": city, **prepare(city, flows, sections, sheets, receipts)}, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
