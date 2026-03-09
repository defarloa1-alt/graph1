"""
load_openalex_ids_to_graph.py

Loads validated OpenAlex concept IDs from discipline_taxonomy_openalex_final.csv
into Neo4j Aura. Companion to script 17 (handles the LOAD CSV step that
cannot run on Aura directly).

Sets on each Discipline node:
  openalex_id           — primary validated concept ID (C-prefix)
  openalex_display      — OpenAlex canonical name
  openalex_alternatives — pipe-separated alt IDs (from multi-ID resolution)
  openalex_status       — verified | verified_multi | no_id

Also wires ROUTES_TO edges to SYS_FederationSource {source_id: 'open_alex'}
for all verified disciplines.

Usage:
  python scripts/neo4j/load_openalex_ids_to_graph.py [--dry-run]
"""

import csv
import argparse
from pathlib import Path
from sys import path as syspath

syspath.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

CSV_PATH = Path("output/discipline_taxonomy_openalex_final.csv")
BATCH    = 200


def load(driver, dry_run: bool):
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    verified   = [r for r in rows if r["openalex_status"] in ("verified", "verified_multi")]
    no_id      = [r for r in rows if r["openalex_status"] == "no_id"]

    print(f"Verified:  {len(verified)}")
    print(f"No-ID:     {len(no_id)}")

    if dry_run:
        print("[dry-run] No writes.")
        return

    with driver.session() as s:
        # Set openalex props on verified disciplines
        set_q = """
        UNWIND $rows AS row
        MATCH (d:Discipline {qid: row.qid})
        SET d.openalex_id           = row.openalex_id
          , d.openalex_display      = row.openalex_display
          , d.openalex_alternatives = CASE WHEN row.openalex_alternatives <> '' THEN row.openalex_alternatives ELSE null END
          , d.openalex_status       = row.openalex_status
        RETURN count(d) AS n
        """
        total = 0
        for i in range(0, len(verified), BATCH):
            batch = [
                {
                    "qid":                   r["qid"],
                    "openalex_id":           r["openalex_primary"],
                    "openalex_display":      r["openalex_display"],
                    "openalex_alternatives": r["openalex_alternatives"],
                    "openalex_status":       r["openalex_status"],
                }
                for r in verified[i:i+BATCH]
            ]
            result = s.run(set_q, rows=batch)
            n = result.single()["n"]
            total += n
            print(f"  Set {total} / {len(verified)} disciplines...")
        print(f"openalex props written: {total}")

        # Mark no_id disciplines
        noid_q = """
        UNWIND $qids AS qid
        MATCH (d:Discipline {qid: qid})
        SET d.openalex_status = 'no_id'
        RETURN count(d) AS n
        """
        qids = [r["qid"] for r in no_id]
        noid_total = 0
        for i in range(0, len(qids), BATCH):
            result = s.run(noid_q, qids=qids[i:i+BATCH])
            noid_total += result.single()["n"]
        print(f"no_id disciplines marked: {noid_total}")

        # Wire ROUTES_TO open_alex for verified disciplines
        routes_q = """
        MATCH (oa:SYS_FederationSource {source_id: 'open_alex'})
        UNWIND $rows AS row
        MATCH (d:Discipline {qid: row.qid})
        WHERE d.openalex_status IN ['verified', 'verified_multi']
          AND d.openalex_id IS NOT NULL
        MERGE (d)-[r:ROUTES_TO]->(oa)
        SET r.scope_basis    = 'openalex_concept_id'
          , r.concept_id     = d.openalex_id
          , r.corpus_capable = true
        RETURN count(r) AS n
        """
        routes_total = 0
        for i in range(0, len(verified), BATCH):
            batch = [{"qid": r["qid"]} for r in verified[i:i+BATCH]]
            result = s.run(routes_q, rows=batch)
            routes_total += result.single()["n"]
        print(f"ROUTES_TO open_alex wired: {routes_total}")

        # Verify final counts
        result = s.run("""
        MATCH (d:Discipline)
        RETURN d.openalex_status AS status, count(d) AS count
        ORDER BY count DESC
        """)
        print("\n--- Discipline openalex_status ---")
        for rec in result:
            print(f"  {rec['status']:25s} {rec['count']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        load(driver, args.dry_run)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
