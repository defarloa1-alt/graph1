#!/usr/bin/env python3
"""
Link Discipline nodes to LCSH_Heading nodes via HAS_LCSH relationship.

Strategy:
1. Load discipline lcsh_ids from Neo4j (pipe-separated)
2. Look up each in subjects_simplified.csv for label/broader/narrower
3. MERGE LCSH_Heading nodes, then MERGE HAS_LCSH relationships
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

PROJECT = Path(__file__).resolve().parents[2]
LCSH_CSV = PROJECT / "subjects" / "subjects_simplified.csv"


def load_lcsh_lookup():
    """Build dict: sh_id -> {label, broader_ids, narrower_ids}"""
    lookup = {}
    with open(LCSH_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            uri = r["id"]
            sh_id = uri.split("/")[-1]
            broader = [u.split("/")[-1] for u in (r.get("broader", "") or "").split("|") if u.strip()]
            narrower = [u.split("/")[-1] for u in (r.get("narrower", "") or "").split("|") if u.strip()]
            lookup[sh_id] = {
                "lcsh_id": sh_id,
                "label": r.get("prefLabel", ""),
                "uri": uri,
                "broader": broader,
                "narrower": narrower,
            }
    return lookup


def main():
    print(f"Loading LCSH lookup from {LCSH_CSV.name}...")
    lookup = load_lcsh_lookup()
    print(f"  {len(lookup)} LCSH headings loaded")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. Load disciplines with lcsh_id
        result = session.run(
            "MATCH (d:Discipline) WHERE d.lcsh_id IS NOT NULL AND d.lcsh_id <> '' "
            "RETURN d.qid as qid, d.label as label, d.lcsh_id as lcsh_id"
        )
        disciplines = []
        for record in result:
            disciplines.append({
                "qid": record["qid"],
                "label": record["label"],
                "lcsh_id": record["lcsh_id"],
            })
        print(f"Disciplines with LCSH: {len(disciplines)}")

        # 2. Collect all lcsh_ids we need to create as nodes
        needed = {}
        for disc in disciplines:
            for sid in disc["lcsh_id"].split("|"):
                sid = sid.strip()
                if sid and sid in lookup:
                    needed[sid] = lookup[sid]

        print(f"LCSH headings to merge: {len(needed)}")

        # 3. MERGE LCSH_Heading nodes in batches
        BATCH = 100
        items = list(needed.values())
        created = 0
        for i in range(0, len(items), BATCH):
            batch = items[i : i + BATCH]
            result = session.run("""
                UNWIND $batch AS row
                MERGE (h:LCSH_Heading {lcsh_id: row.lcsh_id})
                SET h.label = row.label,
                    h.uri = row.uri,
                    h.source = 'loc_skos'
                RETURN count(h) as cnt
            """, batch=batch)
            created += result.single()["cnt"]
        print(f"Merged {created} LCSH_Heading nodes")

        # 4. Create HAS_LCSH relationships
        linked = 0
        not_found = []
        for disc in disciplines:
            for sid in disc["lcsh_id"].split("|"):
                sid = sid.strip()
                if not sid:
                    continue
                if sid not in lookup:
                    not_found.append((disc["label"], sid))
                    continue
                session.run("""
                    MATCH (d:Discipline {qid: $qid})
                    MATCH (h:LCSH_Heading {lcsh_id: $lcsh_id})
                    MERGE (d)-[:HAS_LCSH]->(h)
                """, qid=disc["qid"], lcsh_id=sid)
                linked += 1

        print(f"\nLinked: {linked} HAS_LCSH relationships")
        if not_found:
            print(f"Not found in LCSH dump ({len(not_found)}):")
            for label, sid in not_found:
                print(f"  {label:40s} {sid}")

        # 5. Verify
        result = session.run(
            "MATCH (:Discipline)-[r:HAS_LCSH]->(:LCSH_Heading) RETURN count(r) as count"
        )
        print(f"\nFinal: {result.single()['count']} HAS_LCSH relationships")

        result = session.run("MATCH (h:LCSH_Heading) RETURN count(h) as count")
        print(f"Total LCSH_Heading nodes: {result.single()['count']}")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
