#!/usr/bin/env python3
"""
Link Discipline nodes to SYS_FederationSource nodes via FEDERATED_BY relationship.

Rules:
- Every discipline has qid -> wikidata
- lcsh_id or fast_id or lcc present -> lcsh_fast_lcc
- Relationship carries which identifier properties are present
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. All disciplines -> wikidata (they all have qid)
        result = session.run("""
            MATCH (d:Discipline)
            MATCH (f:SYS_FederationSource {source_id: 'wikidata'})
            MERGE (d)-[r:FEDERATED_BY]->(f)
            SET r.id_property = 'qid'
            RETURN count(r) as cnt
        """)
        wikidata_cnt = result.single()["cnt"]
        print(f"FEDERATED_BY wikidata: {wikidata_cnt}")

        # 2. Disciplines with any LCSH/FAST/LCC -> lcsh_fast_lcc
        result = session.run("""
            MATCH (d:Discipline)
            WHERE d.lcsh_id IS NOT NULL OR d.fast_id IS NOT NULL OR d.lcc IS NOT NULL
            MATCH (f:SYS_FederationSource {source_id: 'lcsh_fast_lcc'})
            WITH d, f,
                 CASE WHEN d.lcsh_id IS NOT NULL THEN ['lcsh_id'] ELSE [] END +
                 CASE WHEN d.fast_id IS NOT NULL THEN ['fast_id'] ELSE [] END +
                 CASE WHEN d.lcc IS NOT NULL THEN ['lcc'] ELSE [] END AS ids
            MERGE (d)-[r:FEDERATED_BY]->(f)
            SET r.id_properties = ids
            RETURN count(r) as cnt
        """)
        lcsh_cnt = result.single()["cnt"]
        print(f"FEDERATED_BY lcsh_fast_lcc: {lcsh_cnt}")

        # 3. Verify
        result = session.run("""
            MATCH (:Discipline)-[r:FEDERATED_BY]->(f:SYS_FederationSource)
            RETURN f.source_id as source, count(r) as cnt
            ORDER BY cnt DESC
        """)
        print("\nFinal FEDERATED_BY counts:")
        for record in result:
            print(f"  {record['source']:20s} {record['cnt']}")

        result = session.run(
            "MATCH (:Discipline)-[r:FEDERATED_BY]->(:SYS_FederationSource) RETURN count(r) as total"
        )
        print(f"\nTotal: {result.single()['total']} FEDERATED_BY relationships")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
