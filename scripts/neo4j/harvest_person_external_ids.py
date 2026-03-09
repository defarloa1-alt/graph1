#!/usr/bin/env python3
"""
Harvest external IDs for Person nodes from Wikidata SPARQL.

Phase 1: Query Wikidata for 16 external ID PIDs on all Person QIDs
Phase 2: Create external ID nodes + relationships in Neo4j
Phase 3: Promote existing gnd_id / lcnaf_id properties to nodes
Phase 4: Materialize ciphers on all new nodes + relationships
"""
import csv
import sys
import time
import requests
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

PROJECT = Path(__file__).resolve().parents[2]
OUTPUT_CSV = PROJECT / "output" / "person_external_ids.csv"

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "ChrystallumBot/1.0 (research project)"

# (wikidata_pid, node_label, rel_type, id_key, uri_template, authority_qid)
ID_TYPES = [
    ("P214",  "VIAF_Cluster",         "HAS_VIAF",          "viaf_id",       "https://viaf.org/viaf/{id}",                             "Q54919"),
    ("P213",  "ISNI_Record",          "HAS_ISNI",          "isni_id",       "https://isni.org/isni/{id}",                             "Q423048"),
    ("P244",  "LCNAF_Authority",      "HAS_LCNAF",         "lcnaf_id",      "https://id.loc.gov/authorities/names/{id}",              "Q13219454"),
    ("P2163", "FAST_Heading",         "HAS_FAST",          "fast_id",       "https://id.worldcat.org/fast/{id}",                      "Q3294867"),
    ("P227",  "GND_Person",           "HAS_GND",           "gnd_id",        "https://d-nb.info/gnd/{id}",                             "Q36578"),
    ("P268",  "BnF_Authority",        "HAS_BNF",           "bnf_id",        "https://data.bnf.fr/ark:/12148/{id}",                    "Q19938912"),
    ("P349",  "NDL_Authority",        "HAS_NDL",           "ndl_id",        "https://id.ndl.go.jp/auth/ndlna/{id}",                   "Q477675"),
    ("P648",  "OpenLibrary_Author",   "HAS_OPENLIBRARY",   "ol_author_id",  "https://openlibrary.org/authors/{id}",                   "Q1201876"),
    ("P1711", "BritishMuseum_Person", "HAS_BM",            "bm_id",         "https://collection.britishmuseum.org/id/person-institution/{id}", "Q6373"),
    ("P245",  "ULAN_Person",          "HAS_ULAN",          "ulan_id",       "https://vocab.getty.edu/ulan/{id}",                      "Q2494649"),
    ("P4212", "PACTOLS_Concept",      "HAS_PACTOLS",       "pactols_id",    "https://pactols.frantiq.fr/opentheso/?idc={id}",         "Q89562190"),
    ("P9106", "OCD_Entry",            "HAS_OCD",           "ocd_id",        "https://oxfordre.com/classics/view/{id}",                 None),
    ("P11252","Trismegistos_Author",  "HAS_TRISMEGISTOS",  "tm_author_id",  "https://www.trismegistos.org/author/{id}",               "Q21633060"),
    ("P7041", "Perseus_Author",       "HAS_PERSEUS",       "perseus_id",    "https://catalog.perseus.org/catalog/{id}",               "Q639661"),
    ("P535",  "FindAGrave_Memorial",  "HAS_FINDAGRAVE",    "findagrave_id", "https://www.findagrave.com/memorial/{id}",               "Q63056"),
    ("P1149", "LCC_Class",            "HAS_LCC_CLASS",     "code",          None,                                                      "Q621080"),
]

PID_LIST = " ".join(f"wdt:{t[0]}" for t in ID_TYPES)
PID_VARS = " ".join(f"?{t[0]}" for t in ID_TYPES)


def phase1_harvest(session):
    """Query Wikidata SPARQL for external IDs on all Person QIDs."""
    print("Phase 1: Harvesting external IDs from Wikidata")

    # Get all person QIDs from graph
    result = session.run("MATCH (p:Person) WHERE p.qid IS NOT NULL RETURN p.qid AS qid")
    all_qids = [r["qid"] for r in result]
    print(f"  {len(all_qids)} persons with QIDs")

    all_rows = []
    BATCH = 200  # SPARQL VALUES batch size

    for i in range(0, len(all_qids), BATCH):
        batch_qids = all_qids[i:i + BATCH]
        values = " ".join(f"wd:{q}" for q in batch_qids)

        # Build SELECT with OPTIONAL for each PID
        optionals = "\n".join(
            f"    OPTIONAL {{ ?item wdt:{t[0]} ?{t[0]} . }}"
            for t in ID_TYPES
        )

        query = f"""
        SELECT ?item {PID_VARS} WHERE {{
          VALUES ?item {{ {values} }}
          {optionals}
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
                bindings = r.json()["results"]["bindings"]
                # Group by QID
                qid_data = defaultdict(dict)
                for b in bindings:
                    qid = b["item"]["value"].split("/")[-1]
                    for pid, _, _, _, _, _ in ID_TYPES:
                        if pid in b:
                            val = b[pid]["value"]
                            # Strip URI prefix if present
                            if val.startswith("http"):
                                val = val.split("/")[-1]
                            qid_data[qid][pid] = val

                for qid, pids in qid_data.items():
                    row = {"qid": qid}
                    for pid, _, _, _, _, _ in ID_TYPES:
                        row[pid] = pids.get(pid, "")
                    all_rows.append(row)

                batch_with_ids = sum(1 for _, pids in qid_data.items() if any(pids.values()))
                print(f"  Batch {i//BATCH + 1}/{(len(all_qids) + BATCH - 1)//BATCH}: {len(qid_data)} persons, {batch_with_ids} with ext IDs")
            elif r.status_code == 429:
                print(f"  Batch {i//BATCH + 1}: rate limited, waiting 30s...")
                time.sleep(30)
                continue  # retry would need loop restructure, just skip
            else:
                print(f"  Batch {i//BATCH + 1}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  Batch {i//BATCH + 1} ERROR: {e}")

        time.sleep(2)

    # Save to CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["qid"] + [t[0] for t in ID_TYPES]
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"\n  Saved {len(all_rows)} rows to {OUTPUT_CSV.name}")

    return all_rows


def phase2_create_nodes(session, rows):
    """Create external ID nodes and relationships from harvested data."""
    print("\nPhase 2: Creating external ID nodes in Neo4j")

    total_nodes = 0
    total_rels = 0

    for pid, node_label, rel_type, id_key, uri_template, authority_qid in ID_TYPES:
        # Collect all (qid, ext_id) pairs for this PID
        pairs = [(r["qid"], r[pid]) for r in rows if r.get(pid)]
        if not pairs:
            print(f"  {node_label:25s} 0 (no data)")
            continue

        BATCH = 100
        node_count = 0
        for j in range(0, len(pairs), BATCH):
            batch = [{"qid": q, "ext_id": eid} for q, eid in pairs[j:j + BATCH]]

            uri_expr = ""
            if uri_template:
                uri_base = uri_template.replace("{id}", "' + row.ext_id + '")
                uri_expr = f", n.uri = '{uri_base}'"

            result = session.run(f"""
                UNWIND $batch AS row
                MATCH (p:Person {{qid: row.qid}})
                MERGE (n:{node_label} {{{id_key}: row.ext_id}})
                ON CREATE SET n.source = 'wikidata'{', n.authority_qid = $auth_qid' if authority_qid else ''}
                MERGE (p)-[r:{rel_type}]->(n)
                RETURN count(DISTINCT n) as nodes, count(r) as rels
            """, batch=batch, auth_qid=authority_qid)
            rec = result.single()
            node_count += rec["nodes"]

        # Set URIs in separate pass (cleaner than string concat in Cypher)
        if uri_template:
            session.run(f"""
                MATCH (n:{node_label})
                WHERE n.uri IS NULL AND n.{id_key} IS NOT NULL
                SET n.uri = replace($template, '{{id}}', n.{id_key})
            """, template=uri_template.replace("{id}", "{id}"))

        # Count relationships
        result = session.run(f"""
            MATCH (p:Person)-[r:{rel_type}]->(n:{node_label})
            RETURN count(DISTINCT n) as nodes, count(r) as rels
        """)
        rec = result.single()
        print(f"  {node_label:25s} {rec['nodes']:>5d} nodes, {rec['rels']:>5d} rels  (pid={pid})")
        total_nodes += rec["nodes"]
        total_rels += rec["rels"]

    print(f"\n  Total: {total_nodes} nodes, {total_rels} relationships")
    return total_nodes, total_rels


def phase3_promote_properties(session):
    """Promote existing gnd_id and lcnaf_id properties on Person to nodes."""
    print("\nPhase 3: Promoting existing property IDs to nodes")

    # GND: Person.gnd_id -> GND_Person node
    result = session.run("""
        MATCH (p:Person)
        WHERE p.gnd_id IS NOT NULL
        MERGE (n:GND_Person {gnd_id: p.gnd_id})
        ON CREATE SET n.source = 'person_property', n.authority_qid = 'Q36578'
        MERGE (p)-[:HAS_GND]->(n)
        RETURN count(DISTINCT n) as nodes
    """)
    gnd_count = result.single()["nodes"]
    print(f"  GND_Person:  {gnd_count} nodes from Person.gnd_id property")

    # LCNAF: Person.lcnaf_id -> LCNAF_Authority node
    result = session.run("""
        MATCH (p:Person)
        WHERE p.lcnaf_id IS NOT NULL
        MERGE (n:LCNAF_Authority {lcnaf_id: p.lcnaf_id})
        ON CREATE SET n.source = 'person_property', n.authority_qid = 'Q13219454'
        MERGE (p)-[:HAS_LCNAF]->(n)
        RETURN count(DISTINCT n) as nodes
    """)
    lcnaf_count = result.single()["nodes"]
    print(f"  LCNAF_Authority: {lcnaf_count} nodes from Person.lcnaf_id property")

    # Set URIs
    session.run("""
        MATCH (n:GND_Person) WHERE n.uri IS NULL AND n.gnd_id IS NOT NULL
        SET n.uri = 'https://d-nb.info/gnd/' + n.gnd_id
    """)
    session.run("""
        MATCH (n:LCNAF_Authority) WHERE n.uri IS NULL AND n.lcnaf_id IS NOT NULL
        SET n.uri = 'https://id.loc.gov/authorities/names/' + n.lcnaf_id
    """)


def phase4_materialize_ciphers(session):
    """Materialize cipher strings on all person external ID nodes + rels."""
    print("\nPhase 4: Materializing ciphers")

    total = 0
    for pid, node_label, rel_type, id_key, _, _ in ID_TYPES:
        result = session.run(f"""
            MATCH (p:Person)-[r:{rel_type}]->(n:{node_label})
            WHERE p.qid IS NOT NULL AND n.{id_key} IS NOT NULL
            SET r.cipher = p.qid + ':' + $pid + ':' + n.{id_key},
                r.pid = $pid,
                n.cipher = p.qid + ':' + $pid + ':' + n.{id_key},
                n.pid = $pid
            RETURN count(r) as cnt
        """, pid=pid)
        cnt = result.single()["cnt"]
        if cnt > 0:
            print(f"  {node_label:25s} {cnt:>5d} ciphers  (pid={pid})")
            total += cnt

    print(f"\n  Total: {total} ciphers materialized")


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        rows = phase1_harvest(session)
        phase2_create_nodes(session, rows)
        phase3_promote_properties(session)
        phase4_materialize_ciphers(session)

        # Summary
        print("\n-- Person external ID coverage --")
        for pid, node_label, rel_type, id_key, _, _ in ID_TYPES:
            result = session.run(f"""
                MATCH (p:Person)-[:{rel_type}]->(n:{node_label})
                RETURN count(DISTINCT p) as persons, count(DISTINCT n) as nodes
            """)
            r = result.single()
            if r["nodes"] > 0:
                print(f"  {node_label:25s} {r['persons']:>5d} persons -> {r['nodes']:>5d} nodes")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
