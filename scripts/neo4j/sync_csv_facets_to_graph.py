#!/usr/bin/env python3
"""
Sync facet assignments from discipline_taxonomy.csv back into Neo4j.
For disciplines that exist in the graph but have no HAS_FACET, write from CSV.
Also creates any missing Discipline nodes from the CSV (with QID + label).
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

PROJECT = Path(__file__).resolve().parents[2]
SRC_CSV = PROJECT / "output" / "discipline_taxonomy.csv"


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Read CSV
    csv_rows = {}
    with open(SRC_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("qid") and row.get("primary_facet"):
                csv_rows[row["qid"]] = row
    print(f"CSV: {len(csv_rows)} disciplines with facet assignments")

    with driver.session() as session:
        # Get graph discipline QIDs
        result = session.run("MATCH (d:Discipline) WHERE d.qid IS NOT NULL RETURN d.qid AS qid")
        graph_qids = {r["qid"] for r in result}
        print(f"Graph: {len(graph_qids)} Discipline nodes with QIDs")

        # Get existing facet assignments
        result = session.run("""
            MATCH (d:Discipline)-[r:HAS_FACET]->(f:Facet)
            WHERE r.primary = true
            RETURN d.qid AS qid, f.key AS facet
        """)
        existing = {r["qid"]: r["facet"] for r in result}
        print(f"Graph: {len(existing)} already have primary facet")

        # Phase 1: Write facets for graph disciplines that don't have them
        to_write = []
        for qid in graph_qids:
            if qid not in existing and qid in csv_rows:
                to_write.append(csv_rows[qid])

        print(f"\nPhase 1: {len(to_write)} graph disciplines need facet from CSV")

        if to_write:
            # Write primary facets
            batch = [{"qid": r["qid"], "facet": r["primary_facet"]} for r in to_write]
            BATCH_SIZE = 100
            primary_count = 0
            for i in range(0, len(batch), BATCH_SIZE):
                chunk = batch[i:i + BATCH_SIZE]
                result = session.run("""
                    UNWIND $batch AS row
                    MATCH (d:Discipline {qid: row.qid})
                    MATCH (f:Facet {key: row.facet})
                    MERGE (d)-[r:HAS_FACET]->(f)
                    SET r.primary = true, r.weight = 1.0, r.source = 'csv_classify'
                    RETURN count(r) as cnt
                """, batch=chunk)
                primary_count += result.single()["cnt"]
            print(f"  Written {primary_count} primary HAS_FACET relationships")

            # Write related facets
            related_batch = []
            for r in to_write:
                if r.get("related_facets"):
                    for pair in r["related_facets"].split("|"):
                        if ":" in pair:
                            facet, weight = pair.split(":", 1)
                            try:
                                related_batch.append({
                                    "qid": r["qid"],
                                    "facet": facet,
                                    "weight": float(weight),
                                })
                            except ValueError:
                                pass

            related_count = 0
            for i in range(0, len(related_batch), BATCH_SIZE):
                chunk = related_batch[i:i + BATCH_SIZE]
                result = session.run("""
                    UNWIND $batch AS row
                    MATCH (d:Discipline {qid: row.qid})
                    MATCH (f:Facet {key: row.facet})
                    MERGE (d)-[r:HAS_FACET]->(f)
                    SET r.primary = false, r.weight = row.weight, r.source = 'csv_classify'
                    RETURN count(r) as cnt
                """, batch=chunk)
                related_count += result.single()["cnt"]
            print(f"  Written {related_count} related HAS_FACET relationships")

        # Phase 2: Create missing Discipline nodes from CSV
        missing_qids = set(csv_rows.keys()) - graph_qids
        print(f"\nPhase 2: {len(missing_qids)} disciplines in CSV but not in graph")

        if missing_qids:
            batch = [{"qid": qid, "label": csv_rows[qid].get("label", "")} for qid in missing_qids]
            BATCH_SIZE = 200
            created = 0
            for i in range(0, len(batch), BATCH_SIZE):
                chunk = batch[i:i + BATCH_SIZE]
                result = session.run("""
                    UNWIND $batch AS row
                    MERGE (d:Discipline {qid: row.qid})
                    ON CREATE SET d.label = row.label, d.source = 'wikidata_csv_import'
                    RETURN count(d) as cnt
                """, batch=chunk)
                created += result.single()["cnt"]
            print(f"  Created/merged {created} Discipline nodes")

            # Write facets for newly created nodes
            facet_batch = [{"qid": qid, "facet": csv_rows[qid]["primary_facet"]}
                          for qid in missing_qids if csv_rows[qid].get("primary_facet")]
            primary_count = 0
            for i in range(0, len(facet_batch), BATCH_SIZE):
                chunk = facet_batch[i:i + BATCH_SIZE]
                result = session.run("""
                    UNWIND $batch AS row
                    MATCH (d:Discipline {qid: row.qid})
                    MATCH (f:Facet {key: row.facet})
                    MERGE (d)-[r:HAS_FACET]->(f)
                    SET r.primary = true, r.weight = 1.0, r.source = 'csv_classify'
                    RETURN count(r) as cnt
                """, batch=chunk)
                primary_count += result.single()["cnt"]
            print(f"  Written {primary_count} primary HAS_FACET for new nodes")

            # Related facets for new nodes
            related_batch = []
            for qid in missing_qids:
                r = csv_rows[qid]
                if r.get("related_facets"):
                    for pair in r["related_facets"].split("|"):
                        if ":" in pair:
                            facet, weight = pair.split(":", 1)
                            try:
                                related_batch.append({"qid": qid, "facet": facet, "weight": float(weight)})
                            except ValueError:
                                pass

            related_count = 0
            for i in range(0, len(related_batch), BATCH_SIZE):
                chunk = related_batch[i:i + BATCH_SIZE]
                result = session.run("""
                    UNWIND $batch AS row
                    MATCH (d:Discipline {qid: row.qid})
                    MATCH (f:Facet {key: row.facet})
                    MERGE (d)-[r:HAS_FACET]->(f)
                    SET r.primary = false, r.weight = row.weight, r.source = 'csv_classify'
                    RETURN count(r) as cnt
                """, batch=chunk)
                related_count += result.single()["cnt"]
            print(f"  Written {related_count} related HAS_FACET for new nodes")

        # Summary
        print("\n-- Final graph state --")
        result = session.run("""
            MATCH (d:Discipline)
            OPTIONAL MATCH (d)-[r:HAS_FACET {primary: true}]->(f:Facet)
            RETURN count(d) AS total,
                   count(f) AS with_facet
        """)
        r = result.single()
        print(f"  {r['total']} Discipline nodes, {r['with_facet']} with primary facet")

        result = session.run("""
            MATCH (d:Discipline)-[r:HAS_FACET {primary: true}]->(f:Facet)
            RETURN f.key AS facet, count(d) AS cnt
            ORDER BY cnt DESC
        """)
        for r in result:
            print(f"  {r['facet']:20s} {r['cnt']}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
