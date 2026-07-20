#!/usr/bin/env python3
"""One-shot: drop generic History FAST tether from roman_republic Domain."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

DOMAIN_ID = "roman_republic"
DROP_FAST = "fst00958235"  # generic History


def main() -> int:
    if "7fe339d2" not in (NEO4J_URI or ""):
        print(f"Refusing: not chrystal_2: {NEO4J_URI}")
        return 2
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as s:
            before = s.run(
                """
                MATCH (sd:SubjectDomain {domain_id:$d})-[r:HAS_FAST_AUTHORITY]->(f:FAST_Heading)
                RETURN f.fast_id AS id, f.label AS label, r.role AS role
                ORDER BY id
                """,
                d=DOMAIN_ID,
            ).data()
            print("BEFORE", before)
            deleted = s.run(
                """
                MATCH (sd:SubjectDomain {domain_id:$d})-[r:HAS_FAST_AUTHORITY]->(f:FAST_Heading {fast_id:$fid})
                DELETE r
                RETURN count(*) AS n
                """,
                d=DOMAIN_ID,
                fid=DROP_FAST,
            ).single()
            print("deleted_edges", dict(deleted) if deleted else None)
            # orphan cleanup if unused
            orphan = s.run(
                """
                MATCH (f:FAST_Heading {fast_id:$fid})
                WHERE NOT (f)<-[:HAS_FAST_AUTHORITY]-()
                DETACH DELETE f
                RETURN count(*) AS n
                """,
                fid=DROP_FAST,
            ).single()
            print("deleted_orphan_nodes", dict(orphan) if orphan else None)
            after = s.run(
                """
                MATCH (sd:SubjectDomain {domain_id:$d})-[r:HAS_FAST_AUTHORITY]->(f:FAST_Heading)
                RETURN f.fast_id AS id, f.label AS label, r.role AS role
                ORDER BY id
                """,
                d=DOMAIN_ID,
            ).data()
            print("AFTER", after)
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
