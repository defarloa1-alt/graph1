#!/usr/bin/env python3
"""
Phase 4: Promote P21 (sex or gender) to gender property on Person.

Finds (person)-[:P21|WIKIDATA_P21]->(target) and sets person.gender = target.label
(lowercased: male, female, etc.). Retains P-code edges as provenance.

Usage:
  python scripts/maintenance/promote_p21_to_gender.py           # dry-run
  python scripts/maintenance/promote_p21_to_gender.py --execute
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
    ap = argparse.ArgumentParser(description="Promote P21 to gender property")
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
            MATCH (p:Entity)-[r:P21|WIKIDATA_P21]->(t:Entity)
            WHERE p.gender IS NULL AND t.label IS NOT NULL
            RETURN count(DISTINCT p) AS c
        """).single()
        count = r["c"] if r else 0

    print("Phase 4: Promote P21 to gender property")
    print(f"  Persons to update: {count}")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    if not args.execute or count == 0:
        driver.close()
        return 0

    with driver.session(database=db) as session:
        r = session.run("""
            MATCH (p:Entity)-[r:P21|WIKIDATA_P21]->(t:Entity)
            WHERE p.gender IS NULL AND t.label IS NOT NULL
            WITH p, t
            ORDER BY p.qid
            WITH p, collect(t)[0] AS first_target
            SET p.gender = toLower(trim(first_target.label))
            RETURN count(p) AS c
        """).single()
        print(f"  gender set: {r['c'] if r else 0}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
