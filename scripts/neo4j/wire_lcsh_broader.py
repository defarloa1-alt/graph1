#!/usr/bin/env python3
"""
Wire BROADER_THAN relationships between LCSH_Heading nodes already in the graph,
using the LOC SKOS broader/narrower data from subjects_simplified.csv.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

PROJECT = Path(__file__).resolve().parents[2]
LCSH_CSV = PROJECT / "subjects" / "subjects_simplified.csv"


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. Get all LCSH_Heading lcsh_ids in graph
        result = session.run("MATCH (h:LCSH_Heading) RETURN h.lcsh_id as id")
        in_graph = set(r["id"] for r in result)
        print(f"LCSH_Heading nodes in graph: {len(in_graph)}")

        # 2. Scan CSV for broader links between in-graph nodes
        pairs = []
        with open(LCSH_CSV, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                sh_id = r["id"].split("/")[-1]
                if sh_id not in in_graph:
                    continue
                for b in (r.get("broader", "") or "").split("|"):
                    b = b.strip()
                    if not b:
                        continue
                    b_id = b.split("/")[-1]
                    if b_id in in_graph:
                        pairs.append({"child": sh_id, "parent": b_id})

        print(f"BROADER pairs to wire: {len(pairs)}")

        # 3. MERGE relationships in batches
        BATCH = 100
        created = 0
        for i in range(0, len(pairs), BATCH):
            batch = pairs[i : i + BATCH]
            result = session.run("""
                UNWIND $batch AS row
                MATCH (child:LCSH_Heading {lcsh_id: row.child})
                MATCH (parent:LCSH_Heading {lcsh_id: row.parent})
                MERGE (child)-[:BROADER_THAN]->(parent)
                RETURN count(*) as cnt
            """, batch=batch)
            created += result.single()["cnt"]

        print(f"Created {created} BROADER_THAN relationships")

        # 4. Verify
        result = session.run(
            "MATCH (:LCSH_Heading)-[r:BROADER_THAN]->(:LCSH_Heading) RETURN count(r) as count"
        )
        print(f"Final: {result.single()['count']} BROADER_THAN relationships")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
