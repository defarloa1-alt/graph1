#!/usr/bin/env python3
"""
Enrich Discipline nodes with external IDs harvested from Wikidata,
then wire FEDERATED_BY relationships to matching SYS_FederationSource nodes.

Source: Disciplines/disciplines_external_ids.csv
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

PROJECT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT / "Disciplines" / "disciplines_external_ids.csv"

# Map CSV column -> federation source_id (only for our federations)
FEDERATION_MAP = {
    "getty_aat_id": "getty_aat",
    "openalex_id": "open_alex",
    "viaf_id": "viaf",
}


def main():
    rows = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    print(f"Loaded {len(rows)} rows from {CSV_PATH.name}")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. Set external ID properties on Discipline nodes
        BATCH = 50
        updated = 0
        for i in range(0, len(rows), BATCH):
            batch = []
            for r in rows[i : i + BATCH]:
                entry = {"qid": r["qid"]}
                for col in r:
                    if col != "qid" and r[col]:
                        entry[col] = r[col]
                batch.append(entry)

            result = session.run("""
                UNWIND $batch AS row
                MATCH (d:Discipline {qid: row.qid})
                SET d += row
                RETURN count(d) as cnt
            """, batch=batch)
            updated += result.single()["cnt"]
        print(f"Updated {updated} Discipline nodes with external IDs")

        # 2. Wire FEDERATED_BY for matching federations
        for id_col, source_id in FEDERATION_MAP.items():
            result = session.run("""
                MATCH (d:Discipline) WHERE d[$prop] IS NOT NULL
                MATCH (f:SYS_FederationSource {source_id: $source_id})
                MERGE (d)-[r:FEDERATED_BY]->(f)
                SET r.id_property = $prop
                RETURN count(r) as cnt
            """, prop=id_col, source_id=source_id)
            cnt = result.single()["cnt"]
            print(f"  FEDERATED_BY {source_id}: {cnt}")

        # 3. Summary
        result = session.run("""
            MATCH (:Discipline)-[r:FEDERATED_BY]->(f:SYS_FederationSource)
            RETURN f.source_id as source, count(r) as cnt
            ORDER BY cnt DESC
        """)
        print("\nAll FEDERATED_BY counts:")
        for record in result:
            print(f"  {record['source']:20s} {record['cnt']}")

        # 4. External ID coverage summary
        id_props = ["getty_aat_id", "openalex_id", "gnd_id", "bnf_id",
                     "unesco_id", "mesh_id", "jstor_id", "viaf_id",
                     "bncf_id", "ndl_id", "nci_id", "babelnet_id",
                     "enc_universalis_id"]
        print("\nExternal ID coverage on Discipline nodes:")
        for prop in id_props:
            result = session.run(
                f"MATCH (d:Discipline) WHERE d.{prop} IS NOT NULL RETURN count(d) as cnt"
            )
            cnt = result.single()["cnt"]
            if cnt > 0:
                print(f"  {prop:25s} {cnt}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
