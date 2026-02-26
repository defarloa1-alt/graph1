#!/usr/bin/env python3
"""Sample query: Entity nodes with pleiades_id or lgpn_id populated (post D-022 backfill)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        # Counts
        r = session.run("MATCH (e:Entity) WHERE e.pleiades_id IS NOT NULL RETURN count(e) AS c")
        pleiades_count = r.single()["c"]
        r = session.run("MATCH (e:Entity) WHERE e.lgpn_id IS NOT NULL RETURN count(e) AS c")
        lgpn_count = r.single()["c"]
        print(f"Entities with pleiades_id: {pleiades_count}")
        print(f"Entities with lgpn_id: {lgpn_count}")

        # Sample
        r = session.run("""
            MATCH (e:Entity)
            WHERE e.pleiades_id IS NOT NULL OR e.lgpn_id IS NOT NULL
            RETURN e.qid AS qid, e.label AS label, e.pleiades_id AS pleiades_id, e.lgpn_id AS lgpn_id
            LIMIT 10
        """)
        print("\nSample (first 10):")
        for row in r:
            print(f"  {row['qid']} | {row['label'][:40] if row['label'] else 'N/A':40} | pleiades={row['pleiades_id'] or '-'} | lgpn={row['lgpn_id'] or '-'}")
    driver.close()

if __name__ == "__main__":
    main()
