#!/usr/bin/env python3
"""
OI-007-09: CITIZEN_OF backfill — connect DPRR persons to Roman Republic (Q17167).

All DPRR persons are Roman Republican citizens by definition (Digital Prosopography
of the Roman Republic). Creates CITIZEN_OF → Q17167 for persons with dprr_id or
dprr_uri who have no existing CITIZEN_OF edge.

Prerequisite: Q17167 (Roman Republic) must exist. Run polity amendment Steps 1–3
if Q17167 lacks :Polity. This script ensures Q17167 exists and has :Polity before
creating edges.

Usage:
  python scripts/maintenance/backfill_citizen_of_roman_republic.py           # dry-run
  python scripts/maintenance/backfill_citizen_of_roman_republic.py --execute
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

Q17167 = "Q17167"  # Roman Republic 509–27 BCE


def main() -> int:
    ap = argparse.ArgumentParser(description="OI-007-09: CITIZEN_OF backfill for DPRR persons")
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
        # 1. Ensure Q17167 exists and has :Polity (polity amendment Steps 1–3)
        r = session.run("""
            MATCH (n:Entity {qid: $qid})
            RETURN n.qid AS qid, labels(n) AS labels
        """, qid=Q17167).single()
        if not r:
            print(f"  WARNING: Q17167 (Roman Republic) not found. Creating minimal node.")
            if args.execute:
                session.run("""
                    MERGE (n:Entity {qid: $qid})
                    ON CREATE SET
                        n.entity_id = 'polity_q17167',
                        n.entity_type = 'POLITY',
                        n.label = 'Roman Republic',
                        n.label_latin = 'Res Publica Romana',
                        n.inception_year = -509,
                        n.dissolution_year = -27,
                        n.political_form = 'republic',
                        n.cidoc_class = 'E74_Group'
                    SET n:Polity:HistoricalPolity
                """, qid=Q17167)
        else:
            # Ensure :Polity if missing
            labels = r.get("labels") or []
            if "Polity" not in labels and args.execute:
                session.run("""
                    MATCH (n:Entity {qid: $qid})
                    SET n.entity_type = 'POLITY',
                        n.label = COALESCE(n.label, 'Roman Republic'),
                        n.label_latin = COALESCE(n.label_latin, 'Res Publica Romana'),
                        n.inception_year = COALESCE(n.inception_year, -509),
                        n.dissolution_year = COALESCE(n.dissolution_year, -27),
                        n.political_form = COALESCE(n.political_form, 'republic'),
                        n.cidoc_class = COALESCE(n.cidoc_class, 'E74_Group')
                    SET n:Polity:HistoricalPolity
                """, qid=Q17167)

        # 2. Count DPRR persons without CITIZEN_OF
        r = session.run("""
            MATCH (p:Entity)
            WHERE (p.dprr_id IS NOT NULL OR p.dprr_uri IS NOT NULL)
              AND NOT (p)-[:CITIZEN_OF]->()
            RETURN count(p) AS c
        """).single()
        count = r["c"] if r else 0

    print("OI-007-09: CITIZEN_OF backfill -> Roman Republic (Q17167)")
    print(f"  DPRR persons without CITIZEN_OF: {count}")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    if count == 0:
        driver.close()
        return 0

    if not args.execute:
        driver.close()
        return 0

    with driver.session(database=db) as session:
        r = session.run("""
            MATCH (p:Entity)
            WHERE (p.dprr_id IS NOT NULL OR p.dprr_uri IS NOT NULL)
              AND NOT (p)-[:CITIZEN_OF]->()
            MATCH (polity:Entity {qid: $qid})
            WITH p, polity LIMIT 10000
            MERGE (p)-[:CITIZEN_OF]->(polity)
            RETURN count(*) AS created
        """, qid=Q17167).single()
        created = r["created"] if r else 0
        print(f"  CITIZEN_OF created: {created}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
