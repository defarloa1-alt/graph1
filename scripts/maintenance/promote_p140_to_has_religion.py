#!/usr/bin/env python3
"""
Phase 4: Promote P140 (religion) to canonical HAS_RELIGION.

Finds (person)-[:P140|WIKIDATA_P140]->(religion) and creates (person)-[:HAS_RELIGION]->(religion).
Ensures target nodes carry :Religion label per ADR-008.
Retains P-code edges as provenance per ADR-007 §6.

Usage:
  python scripts/maintenance/promote_p140_to_has_religion.py           # dry-run
  python scripts/maintenance/promote_p140_to_has_religion.py --execute
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
    ap = argparse.ArgumentParser(description="Promote P140 to HAS_RELIGION")
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
            MATCH (p:Entity)-[:P140|WIKIDATA_P140]->(t:Entity)
            WHERE NOT (p)-[:HAS_RELIGION]->(t)
            RETURN count(*) AS c
        """).single()
        count = r["c"] if r else 0

    print("Phase 4: Promote P140 to HAS_RELIGION")
    print(f"  Edges to create: {count}")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    if not args.execute or count == 0:
        if args.execute:
            with driver.session(database=db) as session:
                r = session.run("""
                    MATCH (p)-[:HAS_RELIGION]->(t)
                    WHERE NOT t:Religion
                    SET t:Religion
                    RETURN count(t) AS c
                """).single()
                if r and r["c"] > 0:
                    print(f"  Targets labeled :Religion: {r['c']}")
        driver.close()
        return 0

    with driver.session(database=db) as session:
        r = session.run("""
            MATCH (p:Entity)-[:P140|WIKIDATA_P140]->(t:Entity)
            WHERE NOT (p)-[:HAS_RELIGION]->(t)
            WITH DISTINCT p, t LIMIT 10000
            MERGE (p)-[:HAS_RELIGION]->(t)
            SET t:Religion
            RETURN count(*) AS c
        """).single()
        print(f"  HAS_RELIGION created: {r['c'] if r else 0}")

        r2 = session.run("""
            MATCH (p)-[:HAS_RELIGION]->(t)
            WHERE NOT t:Religion
            SET t:Religion
            RETURN count(t) AS c
        """).single()
        if r2 and r2["c"] > 0:
            print(f"  Targets labeled :Religion: {r2['c']}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
