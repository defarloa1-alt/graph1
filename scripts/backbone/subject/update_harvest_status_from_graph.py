#!/usr/bin/env python3
"""
Update harvest_status on SubjectConcepts based on MEMBER_OF edges.

De facto confirmation: if a SubjectConcept has at least one MEMBER_OF edge,
it is confirmed (entity_count > 0). Updates the graph to reflect reality.

Run after cluster assignment --write. Safe to re-run.

Usage:
    python scripts/backbone/subject/update_harvest_status_from_graph.py
"""
import os
import sys
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:
    print("Error: pip install neo4j", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[3]
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def main():
    uri = os.getenv("NEO4J_URI", "")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")

    if not uri or not password:
        print("Set NEO4J_URI and NEO4J_PASSWORD", file=sys.stderr)
        sys.exit(1)

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (sc:SubjectConcept)
                WHERE EXISTS((sc)<-[:MEMBER_OF]-())
                SET sc.harvest_status = 'confirmed'
                RETURN count(sc) AS updated
            """)
            row = result.single()
            updated = row["updated"] if row else 0
        print(f"harvest_status updated: {updated} SubjectConcepts marked confirmed")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
