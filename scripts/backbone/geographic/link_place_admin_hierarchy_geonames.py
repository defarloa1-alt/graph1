#!/usr/bin/env python3
"""
Link Place nodes (Pleiades backbone) to admin hierarchy via GeoNames.

Uses the crosswalk's geonames_id and GeoNames allCountries.txt admin codes
to resolve parent (country/region). Creates Place nodes with geonames_id for
parents and (Place pleiades_id)-[:LOCATED_IN]->(Place geonames_id).

Run after:
  1. import_pleiades_to_neo4j.py
  2. link_place_admin_hierarchy.py (optional; Wikidata path)

Input:
  - CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv
  - Geographic/geonames_allCountries.zip (or download)

Usage:
  python scripts/backbone/geographic/link_place_admin_hierarchy_geonames.py
  python scripts/backbone/geographic/link_place_admin_hierarchy_geonames.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GEONAMES_ZIP_URL = "http://download.geonames.org/export/dump/allCountries.zip"

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")


def _download_geonames_zip(url: str, out_path: Path, timeout: int = 3600) -> None:
    import urllib.request
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum-Graph1/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        out_path.write_bytes(resp.read())


def _parse_geonames_row(parts: List[str]) -> Optional[dict]:
    """Parse allCountries tab row. Cols: 0=id, 1=name, 7=feature_code, 8=cc, 10=adm1, 11=adm2, 12=adm3, 13=adm4."""
    if len(parts) < 14:
        return None
    return {
        "geonameid": parts[0].strip(),
        "name": (parts[1] or parts[2] or "").strip(),
        "feature_code": (parts[7] or "").strip(),
        "country_code": (parts[8] or "").strip(),
        "admin1": (parts[10] or "").strip(),
        "admin2": (parts[11] or "").strip(),
        "admin3": (parts[12] or "").strip(),
        "admin4": (parts[13] or "").strip(),
    }


def _build_admin_lookups_and_records(
    zip_path: Path,
    target_geonameids: Set[str],
) -> Tuple[Dict[tuple, str], Dict[str, dict], Dict[str, str]]:
    """
    Stream allCountries.txt from zip.
    Returns (admin_lookup, geonameid->record, geonameid->label).
    admin_lookup keys: (cc,) for PCLI, (cc, adm1) for ADM1, etc.
    """
    admin_lookup: Dict[tuple, str] = {}
    records: Dict[str, dict] = {}
    labels: Dict[str, str] = {}

    if not zip_path.exists():
        return admin_lookup, records, labels

    with zipfile.ZipFile(zip_path, "r") as zf:
        txt_name = next((n for n in zf.namelist() if n.lower().endswith(".txt")), None)
        if not txt_name:
            return admin_lookup, records, labels

        with zf.open(txt_name, "r") as fh:
            for raw in fh:
                try:
                    line = raw.decode("utf-8", errors="replace").rstrip("\n")
                except Exception:
                    continue
                parts = line.split("\t")
                row = _parse_geonames_row(parts)
                if not row:
                    continue
                gid = row["geonameid"]
                fc = row["feature_code"]
                cc = row["country_code"]
                a1, a2, a3, a4 = row["admin1"], row["admin2"], row["admin3"], row["admin4"]

                # Admin hierarchy lookups
                if fc == "PCLI" and cc:
                    admin_lookup[(cc,)] = gid
                elif fc == "ADM1" and cc and a1:
                    admin_lookup[(cc, a1)] = gid
                elif fc == "ADM2" and cc and a1 and a2:
                    admin_lookup[(cc, a1, a2)] = gid
                elif fc == "ADM3" and cc and a1 and a2 and a3:
                    admin_lookup[(cc, a1, a2, a3)] = gid
                elif fc == "ADM4" and cc and a1 and a2 and a3 and a4:
                    admin_lookup[(cc, a1, a2, a3, a4)] = gid

                # Target records and labels
                if gid in target_geonameids:
                    records[gid] = row
                    if row["name"]:
                        labels[gid] = row["name"]

    return admin_lookup, records, labels


def _resolve_parent_geonames_id(record: dict, admin_lookup: Dict[tuple, str]) -> Optional[str]:
    """Get parent geonameid from record's admin codes."""
    cc = record.get("country_code", "").strip()
    a1 = record.get("admin1", "").strip()
    a2 = record.get("admin2", "").strip()
    a3 = record.get("admin3", "").strip()
    a4 = record.get("admin4", "").strip()

    if not cc:
        return None
    # Prefer most specific parent
    if a4 and (cc, a1, a2, a3, a4) in admin_lookup:
        return admin_lookup[(cc, a1, a2, a3, a4)]
    if a3 and (cc, a1, a2, a3) in admin_lookup:
        return admin_lookup[(cc, a1, a2, a3)]
    if a2 and (cc, a1, a2) in admin_lookup:
        return admin_lookup[(cc, a1, a2)]
    if a1 and (cc, a1) in admin_lookup:
        return admin_lookup[(cc, a1)]
    if (cc,) in admin_lookup:
        return admin_lookup[(cc,)]
    return None


def build_pleiades_to_geonames_parent(
    crosswalk_path: Path,
    admin_lookup: Dict[tuple, str],
    records: Dict[str, dict],
    labels: Dict[str, str],
    *,
    max_places: Optional[int] = None,
) -> Tuple[Dict[str, str], List[dict], List[dict]]:
    """
    Build pleiades_id -> best geonames_id, parent Place rows, link rows.
    Prefer rows with geonames_id; pick one per pleiades_id (first by sort).
    """
    pleiades_to_gn: Dict[str, str] = {}
    with crosswalk_path.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            pid = (row.get("pleiades_id") or "").strip()
            gid = (row.get("geonames_id") or "").strip()
            if not pid or not gid:
                continue
            if pid not in pleiades_to_gn:
                pleiades_to_gn[pid] = gid

    pids = sorted(pleiades_to_gn.keys())
    if max_places and max_places > 0:
        pids = pids[:max_places]

    place_rows: List[dict] = []
    link_rows: List[dict] = []
    seen_parents: Set[str] = set()

    for pid in pids:
        gid = pleiades_to_gn[pid]
        rec = records.get(gid)
        if not rec:
            continue
        parent_gid = _resolve_parent_geonames_id(rec, admin_lookup)
        if not parent_gid or parent_gid == gid:
            continue
        label = labels.get(parent_gid, parent_gid)
        if parent_gid not in seen_parents:
            seen_parents.add(parent_gid)
            place_rows.append({"geonames_id": parent_gid, "label": label})
        link_rows.append({"pleiades_id": pid, "parent_geonames_id": parent_gid})

    return pleiades_to_gn, place_rows, link_rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Link Place to admin hierarchy via GeoNames"
    )
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--crosswalk", default="CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv")
    parser.add_argument("--geonames-zip", default="Geographic/geonames_allCountries.zip")
    parser.add_argument("--geonames-zip-url", default=DEFAULT_GEONAMES_ZIP_URL)
    parser.add_argument("--skip-download", action="store_true", help="Do not download zip if missing")
    parser.add_argument("--max-places", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.password:
        print("NEO4J_PASSWORD required (set in .env or --password)", file=sys.stderr)
        return 1

    crosswalk_path = _PROJECT_ROOT / args.crosswalk
    zip_path = _PROJECT_ROOT / args.geonames_zip

    if not crosswalk_path.exists():
        print(f"ERROR: crosswalk not found: {crosswalk_path}", file=sys.stderr)
        return 1

    # Collect target geonames_ids from crosswalk
    target_gids: Set[str] = set()
    with crosswalk_path.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            gid = (row.get("geonames_id") or "").strip()
            if gid:
                target_gids.add(gid)

    if not target_gids:
        print("No geonames_ids in crosswalk")
        return 0

    print(f"Target geonames_ids: {len(target_gids)}", flush=True)

    if not zip_path.exists() and not args.skip_download:
        print(f"Downloading {args.geonames_zip_url} (~1.5GB)...", flush=True)
        _download_geonames_zip(args.geonames_zip_url, zip_path)

    if not zip_path.exists():
        print(f"ERROR: geonames zip not found: {zip_path}", file=sys.stderr)
        return 1

    print("Building admin lookups and loading records from allCountries...", flush=True)
    admin_lookup, records, labels = _build_admin_lookups_and_records(zip_path, target_gids)
    print(f"  Admin lookup entries: {len(admin_lookup)}, records found: {len(records)}", flush=True)

    _, place_rows, link_rows = build_pleiades_to_geonames_parent(
        crosswalk_path, admin_lookup, records, labels, max_places=args.max_places
    )

    if args.dry_run:
        print("DRY RUN")
        print(f"  Would create {len(place_rows)} parent Place nodes (geonames_id)")
        print(f"  Would create {len(link_rows)} LOCATED_IN edges")
        for r in link_rows[:5]:
            print(f"    {r['pleiades_id']} -> {r['parent_geonames_id']}")
        return 0

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j", file=sys.stderr)
        return 1

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    with driver.session() as session:
        if place_rows:
            session.run(
                """
                UNWIND $rows AS row
                MERGE (pl:Place {geonames_id: row.geonames_id})
                ON CREATE SET
                    pl.created = datetime(),
                    pl.node_type = 'geonames_place_backbone',
                    pl.authority = 'GeoNames',
                    pl.uri = 'https://www.geonames.org/' + row.geonames_id
                SET
                    pl.label = coalesce(row.label, pl.label, row.geonames_id),
                    pl.updated = datetime()
                """,
                rows=place_rows,
            )
            print(f"Ensured {len(place_rows)} parent Place nodes (geonames_id)", flush=True)

        if link_rows:
            result = session.run(
                """
                UNWIND $rows AS row
                MATCH (child:Place {pleiades_id: row.pleiades_id})
                MATCH (parent:Place {geonames_id: row.parent_geonames_id})
                MERGE (child)-[r:LOCATED_IN]->(parent)
                SET
                    r.source = 'geonames',
                    r.mapping_note = 'admin_containment'
                RETURN count(r) AS linked
                """,
                rows=link_rows,
            )
            linked = sum(1 for _ in result)
            print(f"Created {linked} LOCATED_IN edges (Place pleiades_id -> Place geonames_id)", flush=True)

        stats = session.run(
            """
            MATCH (p:Place)
            WHERE p.pleiades_id IS NOT NULL
            OPTIONAL MATCH (p)-[:LOCATED_IN]->(parent:Place)
            RETURN
                count(DISTINCT p) AS places_with_pleiades,
                count(DISTINCT CASE WHEN parent IS NOT NULL THEN p END) AS places_with_parent
            """
        ).single()
        print(
            f"Stats: {stats['places_with_pleiades']} Place(pleiades_id), "
            f"{stats['places_with_parent']} with LOCATED_IN parent",
            flush=True,
        )

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
