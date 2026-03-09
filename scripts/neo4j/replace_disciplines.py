#!/usr/bin/env python3
"""
Replace Discipline and SubjectConcept nodes with 675 clean connected disciplines.

1. DETACH DELETE all Discipline nodes (1,363 + 6,081 rels)
2. DETACH DELETE all SubjectConcept nodes (22 + 134 rels)
3. MERGE 675 Discipline nodes from disciplines_connected.csv
4. Wire SUBCLASS_OF relationships within the set
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

PROJECT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT / "Disciplines" / "disciplines_connected.csv"


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. Delete old Discipline nodes
        result = session.run("MATCH (n:Discipline) DETACH DELETE n RETURN count(n) as deleted")
        deleted_disc = result.single()["deleted"]
        print(f"1. Deleted {deleted_disc} Discipline nodes")

        # 2. Delete old SubjectConcept nodes
        result = session.run("MATCH (n:SubjectConcept) DETACH DELETE n RETURN count(n) as deleted")
        deleted_sc = result.single()["deleted"]
        print(f"2. Deleted {deleted_sc} SubjectConcept nodes")

        # 3. Load CSV
        rows = []
        with open(CSV_PATH, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows.append(r)
        print(f"3. Loaded {len(rows)} rows from {CSV_PATH.name}")

        # 4. MERGE Discipline nodes in batches
        BATCH = 50
        created = 0
        for i in range(0, len(rows), BATCH):
            batch = rows[i : i + BATCH]
            params = []
            for r in batch:
                params.append({
                    "qid": r["qid"],
                    "label": r["label"],
                    "lcsh_id": r.get("lcsh_id", "") or None,
                    "fast_id": r.get("fast_id", "") or None,
                    "lcc": r.get("lcc", "") or None,
                    "ddc": r.get("ddc", "") or None,
                    "subclass_of": r.get("subclass_of", "") or None,
                })
            result = session.run("""
                UNWIND $batch AS row
                MERGE (d:Discipline {qid: row.qid})
                SET d.label = row.label,
                    d.lcsh_id = row.lcsh_id,
                    d.fast_id = row.fast_id,
                    d.lcc = row.lcc,
                    d.ddc = row.ddc,
                    d.subclass_of = row.subclass_of,
                    d.source = 'wikidata_sparql',
                    d.harvest_date = date()
                RETURN count(d) as cnt
            """, batch=params)
            created += result.single()["cnt"]
        print(f"4. Merged {created} Discipline nodes")

        # 5. Wire SUBCLASS_OF relationships within the set
        result = session.run("""
            MATCH (child:Discipline)
            WHERE child.subclass_of IS NOT NULL
            WITH child, split(child.subclass_of, '|') AS parents
            UNWIND parents AS parent_qid
            WITH child, trim(parent_qid) AS pqid
            WHERE pqid <> ''
            MATCH (parent:Discipline {qid: pqid})
            WHERE parent.qid <> child.qid
            MERGE (child)-[:SUBCLASS_OF]->(parent)
            RETURN count(*) as rels_created
        """)
        rels = result.single()["rels_created"]
        print(f"5. Created {rels} SUBCLASS_OF relationships")

        # 6. Verify
        result = session.run("MATCH (n:Discipline) RETURN count(n) as count")
        final_count = result.single()["count"]
        result = session.run("MATCH (:Discipline)-[r:SUBCLASS_OF]->(:Discipline) RETURN count(r) as count")
        final_rels = result.single()["count"]
        print(f"\nFinal: {final_count} Discipline nodes, {final_rels} SUBCLASS_OF relationships")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
