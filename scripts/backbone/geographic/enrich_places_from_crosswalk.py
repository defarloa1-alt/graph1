#!/usr/bin/env python3
"""
Enrich Place nodes with Wikidata QID, GeoNames ID, and TGN from the crosswalk.

Uses CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv to add:
  - qid (wikidata_qid)
  - geonames_id
  - geonames_feature_code
  - tgn_id (when available; some pleiades_id map to multiple TGN rows — first wins)

Run after: import_pleiades_to_neo4j.py (creates Place nodes with pleiades_id)

Usage:
  python scripts/backbone/geographic/enrich_places_from_crosswalk.py
  python scripts/backbone/geographic/enrich_places_from_crosswalk.py --dry-run
  python scripts/backbone/geographic/enrich_places_from_crosswalk.py --crosswalk path/to/crosswalk.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
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

DEFAULT_CROSSWALK = _PROJECT_ROOT / "CSV" / "geographic" / "pleiades_geonames_wikidata_tgn_crosswalk_v1.csv"


def _load_crosswalk(path: Path) -> dict:
    """Load pleiades_id -> {qid, geonames_id, geonames_feature_code, tgn_id} (first per pleiades_id)."""
    out: dict[str, dict] = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = (row.get("pleiades_id") or "").strip()
            if not pid:
                continue
            if pid in out:
                continue  # keep first
            qid = (row.get("wikidata_qid") or "").strip()
            geonames_id = (row.get("geonames_id") or "").strip()
            geonames_feature_code = (row.get("geonames_feature_code") or "").strip()
            tgn_id = (row.get("tgn_id") or "").strip()
            out[pid] = {
                "qid": qid if qid else None,
                "geonames_id": geonames_id if geonames_id else None,
                "geonames_feature_code": geonames_feature_code if geonames_feature_code else None,
                "tgn_id": tgn_id if tgn_id else None,
            }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich Place nodes from crosswalk")
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--crosswalk", type=Path, default=DEFAULT_CROSSWALK)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.password:
        print("NEO4J_PASSWORD required (set in .env or --password)", file=sys.stderr)
        return 1

    if not args.crosswalk.exists():
        print(f"Crosswalk not found: {args.crosswalk}", file=sys.stderr)
        return 1

    crosswalk = _load_crosswalk(args.crosswalk)
    with_qid = sum(1 for v in crosswalk.values() if v.get("qid"))
    with_geonames = sum(1 for v in crosswalk.values() if v.get("geonames_id"))
    with_tgn = sum(1 for v in crosswalk.values() if v.get("tgn_id"))

    print("Enrich Place nodes from crosswalk")
    print(f"  Crosswalk: {args.crosswalk.name} ({len(crosswalk):,} pleiades_ids)")
    print(f"  With QID: {with_qid:,} | GeoNames: {with_geonames:,} | TGN: {with_tgn:,}")

    if args.dry_run:
        print("  DRY RUN — no writes")
        return 0

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j", file=sys.stderr)
        return 1

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    batch_size = 500
    batch: list[dict] = []
    updated = 0

    with driver.session() as session:
        for pleiades_id, attrs in crosswalk.items():
            if not any(attrs.values()):
                continue
            batch.append({
                "pleiades_id": pleiades_id,
                "qid": attrs.get("qid"),
                "geonames_id": attrs.get("geonames_id"),
                "geonames_feature_code": attrs.get("geonames_feature_code"),
                "tgn_id": attrs.get("tgn_id"),
            })
            if len(batch) >= batch_size:
                result = session.run("""
                    UNWIND $batch AS row
                    MATCH (p:Place)
                    WHERE toString(p.pleiades_id) = row.pleiades_id
                    SET p.qid = coalesce(row.qid, p.qid),
                        p.geonames_id = coalesce(row.geonames_id, p.geonames_id),
                        p.geonames_feature_code = coalesce(row.geonames_feature_code, p.geonames_feature_code),
                        p.tgn_id = coalesce(row.tgn_id, p.tgn_id)
                    RETURN count(p) AS n
                """, batch=batch)
                n = result.single()["n"]
                updated += n
                print(f"  Enriched {n} places (total: {updated})")
                batch = []

        if batch:
            result = session.run("""
                UNWIND $batch AS row
                MATCH (p:Place)
                WHERE toString(p.pleiades_id) = row.pleiades_id
                SET p.qid = coalesce(row.qid, p.qid),
                    p.geonames_id = coalesce(row.geonames_id, p.geonames_id),
                    p.geonames_feature_code = coalesce(row.geonames_feature_code, p.geonames_feature_code),
                    p.tgn_id = coalesce(row.tgn_id, p.tgn_id)
                RETURN count(p) AS n
            """, batch=batch)
            updated += result.single()["n"]

        # Stats
        stats = session.run("""
            MATCH (p:Place)
            RETURN count(p) AS total,
                   count(p.qid) AS with_qid,
                   count(p.geonames_id) AS with_geonames,
                   count(p.tgn_id) AS with_tgn
        """).single()
        total = stats["total"] or 0
        with_qid_n = stats["with_qid"] or 0
        with_geonames_n = stats["with_geonames"] or 0
        with_tgn_n = stats["with_tgn"] or 0

    driver.close()

    print(f"\nEnrichment complete: {updated} places updated")
    print(f"  Total Place: {total:,} | With QID: {with_qid_n:,} | GeoNames: {with_geonames_n:,} | TGN: {with_tgn_n:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
