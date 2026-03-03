#!/usr/bin/env python3
"""
Phase 1: Apply :Person label to qualifying Entity nodes (ADR-007 §2).

Gates per Person/3-3-26-plan.txt:
  Gate A: DPRR authority — dprr_id IS NOT NULL, person_ prefix, no P31→non-human
  Gate B: Wikidata-confirmed humans — P31→human, person_ prefix, no dprr_id
  Gate C: Namespace leak repair — entity_type=CONCEPT with P31→human

Supports both P31 and WIKIDATA_P31 relationship types.

Usage:
  python scripts/maintenance/apply_person_label_gates.py           # dry-run
  python scripts/maintenance/apply_person_label_gates.py --execute
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
    ap = argparse.ArgumentParser(description="Apply :Person label per ADR-007 Phase 1 gates")
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
        # Count candidates per gate (dry-run)
        r_a = session.run("""
            MATCH (n:Entity)
            WHERE n.dprr_id IS NOT NULL
              AND (n.entity_id STARTS WITH 'person_' OR (n.entity_cipher STARTS WITH 'ent_per_' AND n.entity_type = 'PERSON'))
              AND NOT EXISTS {
                (n)-[r:P31|WIKIDATA_P31]->(m)
                WHERE m.label <> 'human' AND (m.qid IS NULL OR m.qid <> 'Q5')
              }
              AND NOT n:Person
            RETURN count(n) AS c
        """)
        gate_a = r_a.single()["c"]

        r_b = session.run("""
            MATCH (n:Entity)-[r:P31|WIKIDATA_P31]->(m)
            WHERE (m.label = 'human' OR m.qid = 'Q5')
              AND (n.entity_id STARTS WITH 'person_' OR (n.entity_cipher STARTS WITH 'ent_per_' AND n.entity_type = 'PERSON'))
              AND n.dprr_id IS NULL
              AND NOT EXISTS {
                (n)-[r2:P31|WIKIDATA_P31]->(x)
                WHERE (x.label <> 'human' AND (x.qid IS NULL OR x.qid <> 'Q5'))
              }
              AND NOT n:Person
            RETURN count(DISTINCT n) AS c
        """)
        gate_b = r_b.single()["c"]

        r_c = session.run("""
            MATCH (n:Entity)-[r:P31|WIKIDATA_P31]->(m)
            WHERE n.entity_type = 'CONCEPT'
              AND (m.label = 'human' OR m.qid = 'Q5')
              AND (n.entity_id STARTS WITH 'person_' OR n.entity_cipher STARTS WITH 'ent_per_')
              AND NOT n:Person
            RETURN count(DISTINCT n) AS c
        """)
        gate_c = r_c.single()["c"]

    total = gate_a + gate_b + gate_c
    print("Phase 1: Apply :Person label")
    print(f"  Gate A (DPRR):     {gate_a}")
    print(f"  Gate B (Wikidata): {gate_b}")
    print(f"  Gate C (leak):     {gate_c}")
    print(f"  Total:             {total}")
    print(f"  Mode:              {'EXECUTE' if args.execute else 'DRY-RUN'}")

    if not args.execute or total == 0:
        driver.close()
        return 0

    with driver.session(database=db) as session:
        # Gate A
        r = session.run("""
            MATCH (n:Entity)
            WHERE n.dprr_id IS NOT NULL
              AND (n.entity_id STARTS WITH 'person_' OR (n.entity_cipher STARTS WITH 'ent_per_' AND n.entity_type = 'PERSON'))
              AND NOT EXISTS {
                (n)-[r:P31|WIKIDATA_P31]->(m)
                WHERE m.label <> 'human' AND (m.qid IS NULL OR m.qid <> 'Q5')
              }
              AND NOT n:Person
            SET n:Person
            RETURN count(n) AS c
        """)
        applied_a = r.single()["c"]

        # Gate B
        r = session.run("""
            MATCH (n:Entity)-[r:P31|WIKIDATA_P31]->(m)
            WHERE (m.label = 'human' OR m.qid = 'Q5')
              AND (n.entity_id STARTS WITH 'person_' OR (n.entity_cipher STARTS WITH 'ent_per_' AND n.entity_type = 'PERSON'))
              AND n.dprr_id IS NULL
              AND NOT EXISTS {
                (n)-[r2:P31|WIKIDATA_P31]->(x)
                WHERE (x.label <> 'human' AND (x.qid IS NULL OR x.qid <> 'Q5'))
              }
              AND NOT n:Person
            WITH DISTINCT n
            SET n:Person
            RETURN count(n) AS c
        """)
        applied_b = r.single()["c"]

        # Gate C
        r = session.run("""
            MATCH (n:Entity)-[r:P31|WIKIDATA_P31]->(m)
            WHERE n.entity_type = 'CONCEPT'
              AND (m.label = 'human' OR m.qid = 'Q5')
              AND (n.entity_id STARTS WITH 'person_' OR n.entity_cipher STARTS WITH 'ent_per_')
              AND NOT n:Person
            WITH DISTINCT n
            SET n:Person, n.entity_type = 'PERSON'
            RETURN count(n) AS c
        """)
        applied_c = r.single()["c"]

    print(f"Applied: A={applied_a} B={applied_b} C={applied_c} total={applied_a + applied_b + applied_c}")
    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
