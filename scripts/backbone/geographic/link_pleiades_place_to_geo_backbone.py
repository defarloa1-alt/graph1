#!/usr/bin/env python3
"""
Link Pleiades_Place nodes to the geographic backbone (Place) by pleiades_id.

Run after:
  1. import_pleiades_to_neo4j.py (creates Place nodes from pleiades-places CSV/gz)
  2. load_federation_survey.py --survey output/nodes/pleiades_roman_republic.json

Creates (pp:Pleiades_Place)-[:ALIGNED_WITH_GEO_BACKBONE]->(place:Place) where
pleiades_id matches. Safe to re-run (MERGE).

Usage:
  python scripts/backbone/subject/link_pleiades_place_to_geo_backbone.py
  python scripts/backbone/subject/link_pleiades_place_to_geo_backbone.py --dry-run
"""

import argparse
import os
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")


def main() -> int:
    parser = argparse.ArgumentParser(description="Link Pleiades_Place to Place backbone by pleiades_id")
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.password:
        print("NEO4J_PASSWORD required (set in .env or --password)", file=sys.stderr)
        return 1

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j", file=sys.stderr)
        return 1

    if args.dry_run:
        print("DRY RUN — would execute:")
        print("  MATCH (pp:Pleiades_Place), (place:Place)")
        print("  WHERE toString(place.pleiades_id) = toString(pp.pleiades_id)")
        print("  MERGE (pp)-[:ALIGNED_WITH_GEO_BACKBONE]->(place)")
        return 0

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    with driver.session() as session:
        result = session.run("""
            MATCH (pp:Pleiades_Place)
            MATCH (place:Place)
            WHERE toString(place.pleiades_id) = toString(pp.pleiades_id)
            MERGE (pp)-[r:ALIGNED_WITH_GEO_BACKBONE]->(place)
            RETURN count(r) AS linked
        """)
        row = result.single()
        linked = row["linked"] if row else 0

        # Count totals for report
        pp_count = session.run("MATCH (n:Pleiades_Place) RETURN count(n) AS c").single()["c"]
        place_count = session.run("MATCH (n:Place) RETURN count(n) AS c").single()["c"]

    driver.close()

    print(f"Linked {linked} Pleiades_Place -> Place (Pleiades_Place: {pp_count}, Place: {place_count})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
