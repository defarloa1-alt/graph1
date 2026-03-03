#!/usr/bin/env python3
"""
Phase 4: Promote P19/P20 (place of birth/death) to canonical BORN_IN/DIED_IN.

Finds (person)-[:P19|WIKIDATA_P19]->(place) and creates (person)-[:BORN_IN]->(place).
Finds (person)-[:P20|WIKIDATA_P20]->(place) and creates (person)-[:DIED_IN]->(place).
Retains P-code edges as provenance per ADR-007 §6.

Usage:
  python scripts/maintenance/promote_p19_p20_to_canonical.py           # dry-run
  python scripts/maintenance/promote_p19_p20_to_canonical.py --execute
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
    ap = argparse.ArgumentParser(description="Promote P19/P20 to BORN_IN/DIED_IN")
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
        r_p19 = session.run("""
            MATCH (p:Entity)-[r:P19|WIKIDATA_P19]->(t:Entity)
            WHERE NOT (p)-[:BORN_IN]->()
            RETURN count(DISTINCT p) AS c
        """).single()
        p19_count = r_p19["c"] if r_p19 else 0

        r_p20 = session.run("""
            MATCH (p:Entity)-[r:P20|WIKIDATA_P20]->(t:Entity)
            WHERE NOT (p)-[:DIED_IN]->()
            RETURN count(DISTINCT p) AS c
        """).single()
        p20_count = r_p20["c"] if r_p20 else 0

    print("Phase 4: Promote P19/P20 to BORN_IN/DIED_IN")
    print(f"  P19 -> BORN_IN: {p19_count} persons")
    print(f"  P20 -> DIED_IN: {p20_count} persons")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    if not args.execute or (p19_count == 0 and p20_count == 0):
        driver.close()
        return 0

    with driver.session(database=db) as session:
        if p19_count > 0:
            r = session.run("""
                MATCH (p:Entity)-[r:P19|WIKIDATA_P19]->(t:Entity)
                WHERE NOT (p)-[:BORN_IN]->()
                WITH DISTINCT p, t LIMIT 10000
                MERGE (p)-[:BORN_IN]->(t)
                RETURN count(*) AS c
            """).single()
            print(f"  BORN_IN created: {r['c'] if r else 0}")

        if p20_count > 0:
            r = session.run("""
                MATCH (p:Entity)-[r:P20|WIKIDATA_P20]->(t:Entity)
                WHERE NOT (p)-[:DIED_IN]->()
                WITH DISTINCT p, t LIMIT 10000
                MERGE (p)-[:DIED_IN]->(t)
                RETURN count(*) AS c
            """).single()
            print(f"  DIED_IN created: {r['c'] if r else 0}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
