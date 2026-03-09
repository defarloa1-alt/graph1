#!/usr/bin/env python3
"""
Wire Person -> Discipline via Wikidata P101 (field of work).

Phase 1: Harvest P101 from Wikidata for all Person QIDs
Phase 2: MERGE FIELD_OF_WORK relationships where target QID matches a Discipline node
"""
import sys
import time
import requests
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "ChrystallumBot/1.0 (research project)"


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Get all person QIDs
        result = session.run("MATCH (p:Person) WHERE p.qid IS NOT NULL RETURN p.qid AS qid")
        all_qids = [r["qid"] for r in result]
        print(f"{len(all_qids)} persons with QIDs")

        # Get all discipline QIDs for matching
        result = session.run("MATCH (d:Discipline) RETURN d.qid AS qid")
        disc_qids = {r["qid"] for r in result}
        print(f"{len(disc_qids)} discipline QIDs to match against")

        # Also harvest P106 (occupation) since occupations often map to disciplines
        pairs = []  # (person_qid, discipline_qid)
        BATCH = 200

        for i in range(0, len(all_qids), BATCH):
            batch_qids = all_qids[i:i + BATCH]
            values = " ".join(f"wd:{q}" for q in batch_qids)

            query = f"""
            SELECT ?person ?field WHERE {{
              VALUES ?person {{ {values} }}
              {{ ?person wdt:P101 ?field . }}
              UNION
              {{ ?person wdt:P106 ?field . }}
            }}
            """
            try:
                r = requests.get(
                    SPARQL_URL,
                    params={"query": query, "format": "json"},
                    headers={"User-Agent": USER_AGENT},
                    timeout=60,
                )
                if r.status_code == 200:
                    for b in r.json()["results"]["bindings"]:
                        pqid = b["person"]["value"].split("/")[-1]
                        fqid = b["field"]["value"].split("/")[-1]
                        if fqid in disc_qids:
                            pairs.append((pqid, fqid))

                    print(f"  Batch {i//BATCH + 1}/{(len(all_qids) + BATCH - 1)//BATCH}: {len(pairs)} matches so far")
                else:
                    print(f"  Batch {i//BATCH + 1}: HTTP {r.status_code}")
            except Exception as e:
                print(f"  Batch {i//BATCH + 1} ERROR: {e}")

            time.sleep(2)

        # Deduplicate
        pairs = list(set(pairs))
        print(f"\n{len(pairs)} unique Person -> Discipline pairs")

        # Write to Neo4j
        WRITE_BATCH = 100
        total = 0
        for i in range(0, len(pairs), WRITE_BATCH):
            batch = [{"person_qid": p, "disc_qid": d} for p, d in pairs[i:i + WRITE_BATCH]]
            result = session.run("""
                UNWIND $batch AS row
                MATCH (p:Person {qid: row.person_qid})
                MATCH (d:Discipline {qid: row.disc_qid})
                MERGE (p)-[r:FIELD_OF_WORK]->(d)
                SET r.source = 'wikidata_p101_p106'
                RETURN count(r) as cnt
            """, batch=batch)
            total += result.single()["cnt"]

        print(f"  {total} FIELD_OF_WORK relationships written")

        # Summary: how many persons now connect to disciplines
        result = session.run("""
            MATCH (p:Person)-[:FIELD_OF_WORK]->(d:Discipline)
            RETURN count(DISTINCT p) as persons, count(DISTINCT d) as disciplines, count(*) as rels
        """)
        r = result.single()
        print(f"\n  {r['persons']} persons -> {r['disciplines']} disciplines ({r['rels']} rels)")

        # Top disciplines by person count
        print("\n-- Top disciplines by person count --")
        result = session.run("""
            MATCH (p:Person)-[:FIELD_OF_WORK]->(d:Discipline)
            RETURN d.label AS discipline, d.qid AS qid, count(p) AS persons
            ORDER BY persons DESC LIMIT 15
        """)
        for r in result:
            print(f"  {r['discipline']:35s} {r['qid']:12s} {r['persons']:>5d} persons")

        # Verify chain: Person -> Discipline -> Facet
        print("\n-- Person -> Discipline -> Facet chain --")
        result = session.run("""
            MATCH (p:Person)-[:FIELD_OF_WORK]->(d:Discipline)-[hf:HAS_FACET]->(f:Facet)
            WHERE hf.primary = true
            RETURN f.key AS facet, count(DISTINCT p) AS persons
            ORDER BY persons DESC
        """)
        for r in result:
            print(f"  {r['facet']:20s} {r['persons']:>5d} persons")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
