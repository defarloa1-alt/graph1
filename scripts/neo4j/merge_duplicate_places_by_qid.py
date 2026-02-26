#!/usr/bin/env python3
"""
Merge duplicate Place nodes by qid.

Run before creating place_qid_unique constraint.
Uses APOC apoc.refactor.mergeNodes (install APOC if not present).
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from neo4j import GraphDatabase

# Configure for your instance
NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"


def merge_duplicates(driver):
    """Merge duplicate Place nodes using APOC mergeNodes."""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Place)
            WHERE p.qid IS NOT NULL
            WITH p.qid AS qid, collect(p) AS nodes
            WHERE size(nodes) > 1
            CALL apoc.refactor.mergeNodes(nodes) YIELD node
            RETURN count(*) AS merged
        """)
        row = result.single()
        merged = row["merged"] if row else 0

    print(f"Merged {merged} duplicate Place groups.")
    return merged


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        merge_duplicates(driver)
        print("Done. Re-run 01_schema_constraints.cypher to create place_qid_unique.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
