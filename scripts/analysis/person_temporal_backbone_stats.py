#!/usr/bin/env python3
"""
Report what percent of Person nodes are linked to the temporal Year backbone
for birth (BORN_IN_YEAR) and death (DIED_IN_YEAR).

Usage: python scripts/analysis/person_temporal_backbone_stats.py
"""
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
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD required (.env)")
        return 1

    driver = GraphDatabase.driver(uri, auth=(user, password))
    db = os.getenv("NEO4J_DATABASE", "neo4j")

    with driver.session(database=db) as session:
        total = session.run("MATCH (p:Person) RETURN count(p) AS c").single()["c"]
        if total == 0:
            print("No Person nodes found.")
            driver.close()
            return 0

        with_birth = session.run(
            "MATCH (p:Person)-[:BORN_IN_YEAR]->(:Year) RETURN count(DISTINCT p) AS c"
        ).single()["c"]
        with_death = session.run(
            "MATCH (p:Person)-[:DIED_IN_YEAR]->(:Year) RETURN count(DISTINCT p) AS c"
        ).single()["c"]
        with_either = session.run(
            "MATCH (p:Person)-[:BORN_IN_YEAR|DIED_IN_YEAR]->(:Year) RETURN count(DISTINCT p) AS c"
        ).single()["c"]

    driver.close()

    if total == 0:
        print("No Person nodes in graph.")
        return 0

    pct_birth = 100 * with_birth / total if total else 0
    pct_death = 100 * with_death / total if total else 0
    pct_either = 100 * with_either / total if total else 0

    print("Person -> Year temporal backbone")
    print("=" * 50)
    print(f"Total Person nodes:        {total:,}")
    print(f"With BORN_IN_YEAR:        {with_birth:,}  ({pct_birth:.1f}%)")
    print(f"With DIED_IN_YEAR:        {with_death:,}  ({pct_death:.1f}%)")
    print(f"With birth OR death:     {with_either:,}  ({pct_either:.1f}%)")
    print(f"With neither:             {total - with_either:,}  ({100 - pct_either:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
