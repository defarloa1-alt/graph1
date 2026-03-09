#!/usr/bin/env python3
"""
Register DOAJ and OpenAlex as FederationSource nodes and wire them to Discipline nodes.

DOAJ  — Directory of Open Access Journals (gold OA by definition)
        Linked via LCC code: https://doaj.org/api/search/journals?bibjson.subject.code={lcc}
OpenAlex — Open academic graph with gold OA filter
        Linked via openalex_id: https://api.openalex.org/works?filter=concepts.id:{id},oa_status:gold

Usage:
  python scripts/neo4j/wire_doaj_federation.py --dry-run
  python scripts/neo4j/wire_doaj_federation.py
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:

            # 1. Upsert FederationSource nodes
            result = session.run("""
                MERGE (fs:SYS_FederationSource {source_id: 'doaj'})
                SET fs.label = 'Directory of Open Access Journals',
                    fs.phase = 'operational',
                    fs.oa_type = 'gold',
                    fs.endpoint = 'https://doaj.org/api/search/journals',
                    fs.discipline_key = 'lcc',
                    fs.query_pattern = 'bibjson.subject.code={lcc}',
                    fs.description = 'Gold OA journals indexed by LCC subject code'
                RETURN fs.source_id AS id
            """)
            print(f"Upserted FederationSource: {result.single()['id']}")

            result = session.run("""
                MERGE (fs:SYS_FederationSource {source_id: 'openalex'})
                SET fs.label = 'OpenAlex',
                    fs.phase = 'operational',
                    fs.oa_type = 'gold_filter',
                    fs.endpoint = 'https://api.openalex.org/works',
                    fs.discipline_key = 'openalex_id',
                    fs.query_pattern = 'filter=concepts.id:{openalex_id},oa_status:gold',
                    fs.description = 'Open academic graph — gold OA works by concept'
                RETURN fs.source_id AS id
            """)
            print(f"Upserted FederationSource: {result.single()['id']}")

            if args.dry_run:
                print("Dry run — skipping relationship wiring.")
                return

            # 2. Wire Discipline → DOAJ via LCC
            result = session.run("""
                MATCH (d:Discipline), (fs:SYS_FederationSource {source_id: 'doaj'})
                WHERE d.lcc IS NOT NULL
                MERGE (d)-[:HAS_OA_SOURCE {key: 'lcc', via: d.lcc}]->(fs)
                RETURN count(*) AS wired
            """)
            print(f"Wired {result.single()['wired']} Discipline -> DOAJ (via lcc)")

            # 3. Wire Discipline → OpenAlex via openalex_id
            result = session.run("""
                MATCH (d:Discipline), (fs:SYS_FederationSource {source_id: 'openalex'})
                WHERE d.openalex_id IS NOT NULL
                MERGE (d)-[:HAS_OA_SOURCE {key: 'openalex_id', via: d.openalex_id}]->(fs)
                RETURN count(*) AS wired
            """)
            print(f"Wired {result.single()['wired']} Discipline -> OpenAlex (via openalex_id)")

            # Summary
            result = session.run("""
                MATCH (d:Discipline)-[:HAS_OA_SOURCE]->(fs:SYS_FederationSource)
                RETURN fs.source_id AS source, count(d) AS disciplines
                ORDER BY disciplines DESC
            """)
            print("\nOA source coverage:")
            for r in result:
                print(f"  {r['source']}: {r['disciplines']} disciplines")

    finally:
        driver.close()


if __name__ == "__main__":
    main()
