#!/usr/bin/env python3
"""Verify OI-008-06 promotion status."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from neo4j import GraphDatabase
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
with driver.session() as s:
    r = s.run("""
        MATCH (n:Entity)
        WHERE n.entity_type = 'CONCEPT'
          AND n.qid =~ '^Q[0-9]+$'
          AND (()-[:FATHER_OF|MOTHER_OF|SIBLING_OF|SPOUSE_OF]->(n)
            OR (n)-[:FATHER_OF|MOTHER_OF|SIBLING_OF|SPOUSE_OF]->())
        RETURN count(n) AS remaining
    """).single()
    remaining = r["remaining"] if r else None
    print(f"CONCEPT nodes with family edges + real QID remaining: {remaining}")

    r2 = s.run(
        "MATCH (n:Person) WHERE n.entity_id STARTS WITH 'person_q' RETURN count(n) AS promoted"
    ).single()
    promoted = r2["promoted"] if r2 else 0
    print(f"Person nodes with entity_id person_q*: {promoted}")

driver.close()
