#!/usr/bin/env python3
"""
Phase 4: Promote P2348 (period of time of subject) to canonical IN_PERIOD.

Finds (person)-[:P2348|WIKIDATA_P2348]->(period) and creates (person)-[:IN_PERIOD]->(period).
Targets are Entity nodes representing periods (e.g. Roman Republic); no label change.
Retains P-code edges as provenance per ADR-007 §6.

Usage:
  python scripts/maintenance/promote_p2348_to_in_period.py           # dry-run
  python scripts/maintenance/promote_p2348_to_in_period.py --execute
"""
import argparse
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote P2348 to IN_PERIOD")
    ap.add_argument("--execute", action="store_true", help="Write to graph (default: dry-run)")
    args = ap.parse_args()

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD required")
        return 1

    driver = GraphDatabase.driver(uri, auth=(user, password))
    db = os.getenv("NEO4J_DATABASE", "neo4j")

    with driver.session(database=db) as session:
        r = session.run("""
            MATCH (p:Entity)-[:P2348|WIKIDATA_P2348]->(t:Entity)
            WHERE NOT (p)-[:IN_PERIOD]->(t)
            RETURN count(*) AS c
        """).single()
        count = r["c"] if r else 0

    print("Phase 4: Promote P2348 to IN_PERIOD")
    print(f"  Edges to create: {count}")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    if not args.execute or count == 0:
        driver.close()
        return 0

    with driver.session(database=db) as session:
        r = session.run("""
            MATCH (p:Entity)-[:P2348|WIKIDATA_P2348]->(t:Entity)
            WHERE NOT (p)-[:IN_PERIOD]->(t)
            WITH DISTINCT p, t LIMIT 10000
            MERGE (p)-[:IN_PERIOD]->(t)
            RETURN count(*) AS c
        """).single()
        print(f"  IN_PERIOD created: {r['c'] if r else 0}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
