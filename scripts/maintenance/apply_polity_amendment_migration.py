#!/usr/bin/env python3
"""
Polity Amendment Migration (ADR-007 Amendment)

Runs Steps 1-5 from Person/chrystallum_adr007_polity_amendment.docx.
Steps 1-3: Additive, idempotent.
Steps 4-5: Modify edges/labels; verify counts before committing.

Usage:
  python scripts/maintenance/apply_polity_amendment_migration.py           # dry-run
  python scripts/maintenance/apply_polity_amendment_migration.py --execute
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
    ap = argparse.ArgumentParser(description="Polity amendment migration Steps 1-5")
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

    print("Polity Amendment Migration (ADR-007)")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    with driver.session(database=db) as session:
        # Step 1: Count nodes to update
        r1 = session.run("""
            MATCH (n:Entity)
            WHERE n.qid IN [
                'Q17167', 'Q42834', 'Q131964', 'Q34266', 'Q28513',
                'Q170174', 'Q3755547', 'Q1206012', 'Q1003997'
            ]
            RETURN count(n) AS c
        """).single()
        step1_count = r1["c"] if r1 else 0

        # Step 4: Verify CITIZEN_OF to Q1747689 count
        r4 = session.run("""
            MATCH ()-[r:CITIZEN_OF]->(n:Entity {qid: "Q1747689"})
            RETURN count(r) AS to_migrate
        """).single()
        step4_count = r4["to_migrate"] if r4 else 0

        # Step 5: Count contemporary states with :Polity
        r5 = session.run("""
            MATCH (n:Polity)
            WHERE n.qid IN [
                'Q38', 'Q183', 'Q142', 'Q145', 'Q237', 'Q40',
                'Q28', 'Q36', 'Q30', 'Q414', 'Q39'
            ]
            RETURN count(n) AS c
        """).single()
        step5_count = r5["c"] if r5 else 0

    print(f"  Step 1: Historical nodes to set entity_type=POLITY: {step1_count}")
    print(f"  Step 4: CITIZEN_OF to Q1747689 (Ancient Rome) to re-target: {step4_count}")
    print(f"  Step 5: Contemporary states to remove :Polity: {step5_count}")

    if not args.execute:
        driver.close()
        return 0

    with driver.session(database=db) as session:
        # Step 1
        r = session.run("""
            MATCH (n:Entity)
            WHERE n.qid IN [
                'Q17167', 'Q42834', 'Q131964', 'Q34266', 'Q28513',
                'Q170174', 'Q3755547', 'Q1206012', 'Q1003997'
            ]
            SET n.entity_type = 'POLITY'
            RETURN count(n) AS c
        """).single()
        print(f"  Step 1 done: {r['c'] if r else 0} nodes")

        # Step 2
        r = session.run("""
            MATCH (n:Entity)
            WHERE n.entity_type = 'POLITY'
            SET n:Polity:HistoricalPolity
            RETURN count(n) AS c
        """).single()
        print(f"  Step 2 done: {r['c'] if r else 0} nodes labeled :Polity:HistoricalPolity")

        # Step 3
        r = session.run("""
            MATCH (n:Entity {qid: "Q17167"})
            SET n.entity_type = 'POLITY',
                n.label = 'Roman Republic',
                n.label_latin = 'Res Publica Romana',
                n.inception_year = -509,
                n.dissolution_year = -27,
                n.political_form = 'republic',
                n.cidoc_class = 'E74_Group'
            SET n:Polity:HistoricalPolity
            RETURN count(n) AS c
        """).single()
        print(f"  Step 3 done: Q17167 enriched ({r['c'] if r else 0})")

        # Step 4: Re-target CITIZEN_OF from Q1747689 to Q17167
        if step4_count > 0:
            r = session.run("""
                MATCH (person:Entity)-[r:CITIZEN_OF]->(wrong:Entity {qid: "Q1747689"})
                MATCH (correct:Entity {qid: "Q17167"})
                MERGE (person)-[r2:CITIZEN_OF]->(correct)
                ON CREATE SET r2 = properties(r)
                DELETE r
                RETURN count(r2) AS migrated
            """).single()
            print(f"  Step 4 done: {r['migrated'] if r else 0} CITIZEN_OF re-targeted")
        else:
            print("  Step 4 skipped: no CITIZEN_OF to Q1747689")

        # Step 5
        r = session.run("""
            MATCH (n:Polity)
            WHERE n.qid IN [
                'Q38', 'Q183', 'Q142', 'Q145', 'Q237', 'Q40',
                'Q28', 'Q36', 'Q30', 'Q414', 'Q39'
            ]
            REMOVE n:Polity:HistoricalPolity
            SET n.entity_type = 'CONCEPT'
            RETURN count(n) AS c
        """).single()
        print(f"  Step 5 done: {r['c'] if r else 0} contemporary states reclassified")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
