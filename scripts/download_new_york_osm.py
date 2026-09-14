"""Acquire a dated New York state OSM archive without claiming an unknown OD date."""
from __future__ import annotations

import argparse
import ipaddress
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data" / "raw" / "_tools"))
from fetch_osm import digest, fetch, pbf_header


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-date", default="200101", help="YYMMDD Geofabrik annual archive label")
    parser.add_argument("--od-year", type=int, help="Only supply when established by OD provenance")
    parser.add_argument("--resolved-ip", help="Official DNS address for public HTTP transport when local DNS is broken")
    args = parser.parse_args()
    date = args.archive_date
    if len(date) != 6 or not date.isdigit(): raise ValueError("Archive date must be YYMMDD")
    filename = f"new-york-{date}.osm.pbf"
    folder = ROOT / "data" / "raw" / "new_york" / "osm" / "historical"
    url = "https://download.geofabrik.de/north-america/us/" + filename
    existing_manifest = folder / "manifest.json"
    target = folder / filename
    if target.exists() and existing_manifest.exists():
        saved = json.loads(existing_manifest.read_text(encoding="utf-8"))
        receipt = saved.get("download", {})
        if (saved.get("official_source_url") == url and saved.get("od_reference_year") == args.od_year
                and target.stat().st_size == receipt.get("size_bytes")
                and digest(target, "sha256") == receipt.get("sha256")):
            print(json.dumps(saved, indent=2), flush=True)
            return
    transport_url = url
    resolution = None
    if args.resolved_ip:
        address = str(ipaddress.ip_address(args.resolved_ip))
        response = requests.get("https://dns.google/resolve", params={"name": "download.geofabrik.de", "type": "A"}, timeout=20)
        response.raise_for_status()
        resolution = response.json()
        if address not in {a.get("data") for a in resolution.get("Answer", []) if a.get("type") == 1}:
            raise ValueError("Requested address is not an official DNS answer for download.geofabrik.de")
        parsed = urlsplit(url)
        transport_url = urlunsplit(("http", address, parsed.path, "", ""))
    receipt = fetch(transport_url, folder / filename)
    header = pbf_header(folder / filename)
    manifest = {"dataset": "deepgravity_new_york_public", "coverage": "New York state",
                "raw_file": filename, "provider": "Geofabrik", "download": receipt,
                "official_source_url": url, "dns_resolution": resolution,
                "pbf_header": header, "nominal_archive_date": f"20{date[:2]}-{date[2:4]}-{date[4:]}",
                "od_reference_year": args.od_year, "same_year_as_od": None if args.od_year is None else args.od_year == int('20'+date[:2]),
                "temporal_alignment_note": "The released DGM flow file has no date column. A historical development snapshot is not proof of an exact temporal match. Preserve OD date as unknown until supported by provenance.",
                "not_the_exact_deepgravity_osm": True, "raw_tags_filtered": False,
                "license": "ODbL 1.0; OpenStreetMap contributors"}
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
