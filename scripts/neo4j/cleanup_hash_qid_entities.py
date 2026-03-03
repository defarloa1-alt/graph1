#!/usr/bin/env python3
"""
Cleanup Entity nodes with qid = 32-char hex (id_hash mistaken for Wikidata QID).

These nodes have no dprr_id, empty label, and were incorrectly included in
person harvest discovery. Origin: likely cluster_assignment or harvest reports
where id_hash was used as entity_qid.

Usage:
  python scripts/neo4j/cleanup_hash_qid_entities.py          # count only
  python scripts/neo4j/cleanup_hash_qid_entities.py --execute   # delete
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]  # project root (scripts/neo4j/ -> root)
sys.path.insert(0, str(_root))
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase
import os

def main():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD required")
        return 1

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
        r = session.run("""
            MATCH (e:Entity)
            WHERE e.qid =~ '[0-9a-f]{32}' AND e.qid IS NOT NULL
            RETURN count(e) AS n
        """)
        count = r.single()["n"]

    print(f"Entity nodes with hash-like qid: {count}")

    if "--execute" in sys.argv and count > 0:
        with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            session.run("""
                MATCH (e:Entity)
                WHERE e.qid =~ '[0-9a-f]{32}' AND e.qid IS NOT NULL
                DETACH DELETE e
            """)
        print(f"Deleted {count} hash-qid Entity nodes.")
    elif "--execute" in sys.argv:
        print("Nothing to delete.")
    else:
        print("Run with --execute to delete.")

    driver.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
