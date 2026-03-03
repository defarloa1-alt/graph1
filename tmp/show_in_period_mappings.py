#!/usr/bin/env python3
"""Show sample IN_PERIOD person-to-period mappings."""
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_root))
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
pw = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(uri, auth=(user, pw))

with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as s:
    r = s.run("""
        MATCH (p:Entity)-[:IN_PERIOD]->(t)
        RETURN p.label AS person, p.entity_id AS person_id, t.label AS period, t.entity_id AS period_id
        ORDER BY t.label, p.label
        LIMIT 30
    """).data()

    print(f"{'Person':<42} | {'Period':<38} | period_id")
    print("-" * 95)
    for row in r:
        person = (row["person"] or "")[:42]
        period = (row["period"] or "")[:38]
        pid = row["period_id"] or ""
        print(f"{person:<42} | {period:<38} | {pid}")

    # Count by period
    print("\n--- By period (top 15) ---")
    r2 = s.run("""
        MATCH (p:Entity)-[:IN_PERIOD]->(t)
        RETURN t.label AS period, t.entity_id AS period_id, count(p) AS n
        ORDER BY n DESC
        LIMIT 15
    """).data()
    for row in r2:
        period = (row["period"] or "")[:50]
        print(f"  {row['n']:4} | {period:<50} | {row['period_id']}")

driver.close()
