#!/usr/bin/env python3
"""
Rescore all Place nodes using the new 9-rule D16_SCORE_place_federation.

Reads rules from graph, translates to a single Cypher SET that computes
federation_score as sum of applicable rule points. Idempotent.

Usage:
  python scripts/neo4j/rescore_places_d16.py --dry-run
  python scripts/neo4j/rescore_places_d16.py --write
"""

import argparse
import io
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
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

from neo4j import GraphDatabase


# Single-pass Cypher that implements all 9 D16 rules inline.
# Each CASE adds rule points when condition is met.
RESCORE_QUERY = """
MATCH (p:Place)
SET p.federation_score =
    CASE WHEN p.qid IS NOT NULL THEN 25 ELSE 0 END +
    CASE WHEN p.pleiades_id IS NOT NULL THEN 20 ELSE 0 END +
    CASE WHEN p.geonames_id IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.tgn_id IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.loc_authority_id IS NOT NULL OR p.viaf_id IS NOT NULL OR p.gnd_id IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.osm_relation_id IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.lat IS NOT NULL AND p.long IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.inception_year IS NOT NULL OR p.dissolved_year IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.instance_of IS NOT NULL THEN 5 ELSE 0 END,
    p.federation_score_version = 'D16_v2_9rule',
    p.federation_score_updated = date('2026-03-08')
RETURN count(p) AS rescored
"""

# Preview query to see score distribution before/after
PREVIEW_QUERY = """
MATCH (p:Place)
WITH p,
    CASE WHEN p.qid IS NOT NULL THEN 25 ELSE 0 END +
    CASE WHEN p.pleiades_id IS NOT NULL THEN 20 ELSE 0 END +
    CASE WHEN p.geonames_id IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.tgn_id IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.loc_authority_id IS NOT NULL OR p.viaf_id IS NOT NULL OR p.gnd_id IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.osm_relation_id IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.lat IS NOT NULL AND p.long IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.inception_year IS NOT NULL OR p.dissolved_year IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.instance_of IS NOT NULL THEN 5 ELSE 0 END AS new_score
RETURN new_score, count(p) AS cnt
ORDER BY new_score
"""


def main():
    parser = argparse.ArgumentParser(description="Rescore Places with 9-rule D16")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    write_mode = args.write and not args.dry_run
    print(f"Place Rescore — D16 v2 (9 rules) [{'WRITE' if write_mode else 'DRY RUN'}]")
    print("=" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Preview new score distribution
    print("\nNew score distribution (preview):")
    with driver.session() as session:
        result = session.run(PREVIEW_QUERY)
        rows = list(result)
        total = 0
        for r in rows:
            score = r["new_score"]
            cnt = r["cnt"]
            total += cnt
            bar = "#" * (cnt // 200)
            print(f"  {score:>3} pts:  {cnt:>6}  {bar}")
        print(f"\n  Total: {total}")

    # Current scores for comparison
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place) WHERE p.federation_score IS NOT NULL
            RETURN avg(p.federation_score) AS old_avg,
                   min(p.federation_score) AS old_min,
                   max(p.federation_score) AS old_max
        """)
        old = result.single()
        if old and old["old_avg"] is not None:
            print(f"\n  Current scores: avg={old['old_avg']:.1f}, min={old['old_min']}, max={old['old_max']}")

    if not write_mode:
        print("\n  [DRY RUN] Re-run with --write to apply.")
        driver.close()
        return

    # Apply rescore
    print("\nApplying rescore...")
    with driver.session() as session:
        result = session.run(RESCORE_QUERY)
        rescored = result.single()["rescored"]
        print(f"  Rescored {rescored} Place nodes")

    # Verify
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place) WHERE p.federation_score IS NOT NULL
            RETURN avg(p.federation_score) AS avg,
                   min(p.federation_score) AS min,
                   max(p.federation_score) AS max,
                   count(p) AS cnt
        """)
        v = result.single()
        print(f"\n  New scores: avg={v['avg']:.1f}, min={v['min']}, max={v['max']} ({v['cnt']} nodes)")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
