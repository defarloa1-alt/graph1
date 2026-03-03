#!/usr/bin/env python3
"""Inspect Entity nodes whose label looks like a hash (32 hex chars)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
except ImportError:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

from neo4j import GraphDatabase

def main():
    if not NEO4J_PASSWORD:
        print("NEO4J_PASSWORD required")
        return 1
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
    with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
        # Search for nodes with hash-like values in any property
        # Find Entity nodes where qid looks like a hash (32 hex chars) not a Wikidata QID
        count_result = session.run("""
            MATCH (e:Entity) WHERE e.qid =~ '[0-9a-f]{32}' AND e.qid IS NOT NULL
            RETURN count(e) AS n
        """)
        total = count_result.single()["n"]
        result = session.run("""
            MATCH (e:Entity)
            WHERE e.qid =~ '[0-9a-f]{32}' AND e.qid IS NOT NULL
            RETURN e.entity_id AS entity_id, e.label AS label, e.qid AS qid,
                   e.dprr_id AS dprr_id, e.entity_cipher AS entity_cipher
            LIMIT 20
        """)
        rows = result.data()
        if not rows:
            print("No Entity nodes with hash-like qid found.")
            driver.close()
            return 0
        print(f"Found {total} Entity nodes with qid = 32-char hex (not Wikidata QID). Showing up to 20:\n")
        print("  Root cause: qid stores id_hash instead of Q-prefixed Wikidata ID.")
        print("  Display shows qid when label is empty.\n")
        for r in rows:
            print(f"  entity_id:   {r.get('entity_id')}")
            print(f"  label:      {r.get('label')!r}")
            print(f"  qid:        {r.get('qid')}")
            print(f"  dprr_id:    {r.get('dprr_id')}")
            print("  ---")
    driver.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
