#!/usr/bin/env python3
"""
Phase 4: Promote P27 (country of citizenship) to canonical CITIZEN_OF.

Finds (person)-[:P27|WIKIDATA_P27]->(polity) and creates (person)-[:CITIZEN_OF]->(polity).
Ensures target nodes carry :Polity label (country/state as political entity per ADR-008).
Retains P-code edges as provenance per ADR-007 §6.
A person may have multiple citizenships; each (p,t) pair is promoted once.

Usage:
  python scripts/maintenance/promote_p27_to_citizen_of.py           # dry-run
  python scripts/maintenance/promote_p27_to_citizen_of.py --execute
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
    ap = argparse.ArgumentParser(description="Promote P27 to CITIZEN_OF")
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
            MATCH (p:Entity)-[:P27|WIKIDATA_P27]->(t:Entity)
            WHERE NOT (p)-[:CITIZEN_OF]->(t)
            RETURN count(*) AS c
        """).single()
        count = r["c"] if r else 0

    print("Phase 4: Promote P27 to CITIZEN_OF")
    print(f"  Edges to create: {count}")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    if not args.execute or count == 0:
        # Remediate existing CITIZEN_OF targets missing :Polity
        if args.execute:
            with driver.session(database=db) as session:
                r = session.run("""
                    MATCH (p)-[:CITIZEN_OF]->(t)
                    WHERE NOT t:Polity
                    SET t:Polity
                    RETURN count(t) AS c
                """).single()
                if r and r["c"] > 0:
                    print(f"  Targets labeled :Polity: {r['c']}")
        driver.close()
        return 0

    with driver.session(database=db) as session:
        r = session.run("""
            MATCH (p:Entity)-[:P27|WIKIDATA_P27]->(t:Entity)
            WHERE NOT (p)-[:CITIZEN_OF]->(t)
            WITH DISTINCT p, t LIMIT 10000
            MERGE (p)-[:CITIZEN_OF]->(t)
            SET t:Polity
            RETURN count(*) AS c
        """).single()
        print(f"  CITIZEN_OF created: {r['c'] if r else 0}")

        # Remediate existing CITIZEN_OF targets missing :Polity
        r2 = session.run("""
            MATCH (p)-[:CITIZEN_OF]->(t)
            WHERE NOT t:Polity
            SET t:Polity
            RETURN count(t) AS c
        """).single()
        if r2 and r2["c"] > 0:
            print(f"  Targets labeled :Polity: {r2['c']}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
