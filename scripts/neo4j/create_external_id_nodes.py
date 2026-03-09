#!/usr/bin/env python3
"""
Create proper nodes for all external IDs on Discipline nodes,
replacing property-only storage with traversable graph structure.

For each ID type:
  1. MERGE a node with the appropriate label
  2. MERGE a relationship from Discipline to that node

Node labels and relationship types:
  FAST_Heading          -[:HAS_FAST]->
  Getty_AAT_Concept     -[:HAS_GETTY_AAT]->
  OpenAlex_Concept      -[:HAS_OPENALEX]->
  MeSH_Descriptor       -[:HAS_MESH]->
  PACTOLS_Concept       -[:HAS_PACTOLS]->
  OpenLibrary_Work      -[:HAS_OPENLIBRARY]->
  GND_Concept           -[:HAS_GND]->
  BnF_Concept           -[:HAS_BNF]->
  BNCF_Concept          -[:HAS_BNCF]->
  NDL_Concept           -[:HAS_NDL]->
  UNESCO_Concept        -[:HAS_UNESCO]->
  BabelNet_Concept      -[:HAS_BABELNET]->

Sources:
  - fast_id: from Discipline.fast_id property (Wikidata P2163)
  - getty_aat_id, openalex_id, gnd_id, bnf_id, mesh_id, bncf_id,
    ndl_id, unesco_id, babelnet_id: from disciplines_external_ids.csv
  - openlibrary_work_id: from disciplines_openlibrary_work_id.csv
  - pactols_id: from disciplines_pactols_id.csv
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

PROJECT = Path(__file__).resolve().parents[2]
DISC_DIR = PROJECT / "Disciplines"

# ── ID type definitions ──────────────────────────────────────────────────
# Each: (property_name, node_label, rel_type, id_key_on_node, uri_template)
ID_TYPES = [
    ("fast_id",              "FAST_Heading",      "HAS_FAST",       "fast_id",    "https://id.worldcat.org/fast/{id}"),
    ("getty_aat_id",         "Getty_AAT_Concept", "HAS_GETTY_AAT",  "aat_id",     "http://vocab.getty.edu/aat/{id}"),
    ("openalex_id",         "OpenAlex_Concept",  "HAS_OPENALEX",   "openalex_id","https://openalex.org/concepts/{id}"),
    ("gnd_id",              "GND_Concept",       "HAS_GND",        "gnd_id",     "https://d-nb.info/gnd/{id}"),
    ("bnf_id",              "BnF_Concept",       "HAS_BNF",        "bnf_id",     "https://data.bnf.fr/ark:/12148/cb{id}"),
    ("mesh_id",             "MeSH_Descriptor",   "HAS_MESH",       "mesh_id",    "https://id.nlm.nih.gov/mesh/{id}"),
    ("bncf_id",             "BNCF_Concept",      "HAS_BNCF",       "bncf_id",    "https://thes.bncf.firenze.sbn.it/termine.php?id={id}"),
    ("ndl_id",              "NDL_Concept",        "HAS_NDL",       "ndl_id",     "https://id.ndl.go.jp/auth/ndlna/{id}"),
    ("unesco_id",           "UNESCO_Concept",    "HAS_UNESCO",     "unesco_id",  "http://vocabularies.unesco.org/thesaurus/{id}"),
    ("babelnet_id",         "BabelNet_Concept",  "HAS_BABELNET",   "babelnet_id","https://babelnet.org/synset?id={id}"),
    ("openlibrary_work_id", "OpenLibrary_Work",  "HAS_OPENLIBRARY","ol_work_id", "https://openlibrary.org/works/{id}"),
    ("pactols_id",          "PACTOLS_Concept",   "HAS_PACTOLS",    "pactols_id", "https://pactols.frantiq.fr/opentheso/ark:/{id}"),
]


def load_external_ids():
    """Load all external IDs from CSV files into a dict: qid -> {prop: value}."""
    data = {}

    # Main external IDs CSV
    csv_path = DISC_DIR / "disciplines_external_ids.csv"
    if csv_path.exists():
        with open(csv_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                qid = r["qid"]
                data.setdefault(qid, {})
                for k, v in r.items():
                    if k != "qid" and v:
                        data[qid][k] = v

    # Open Library work IDs
    csv_path = DISC_DIR / "disciplines_openlibrary_work_id.csv"
    if csv_path.exists():
        with open(csv_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                data.setdefault(r["qid"], {})["openlibrary_work_id"] = r["openlibrary_work_id"]

    # PACTOLS IDs
    csv_path = DISC_DIR / "disciplines_pactols_id.csv"
    if csv_path.exists():
        with open(csv_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                data.setdefault(r["qid"], {})["pactols_id"] = r["pactols_id"]

    return data


def main():
    ext_data = load_external_ids()
    print(f"External ID data for {len(ext_data)} disciplines")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Load FAST IDs from existing Discipline properties
        result = session.run(
            "MATCH (d:Discipline) WHERE d.fast_id IS NOT NULL AND d.fast_id <> '' "
            "RETURN d.qid as qid, d.fast_id as fast_id"
        )
        for r in result:
            ext_data.setdefault(r["qid"], {})["fast_id"] = r["fast_id"]

        # Process each ID type
        for prop_name, node_label, rel_type, id_key, uri_template in ID_TYPES:
            # Collect all (qid, id_value) pairs for this type
            pairs = []
            for qid, props in ext_data.items():
                val = props.get(prop_name)
                if val:
                    # Handle pipe-separated IDs (e.g. fast_id)
                    for v in val.split("|"):
                        v = v.strip()
                        if v:
                            pairs.append({"qid": qid, "ext_id": v})

            if not pairs:
                continue

            # Deduplicate ext_ids for node creation
            unique_ids = list(set(p["ext_id"] for p in pairs))

            # MERGE nodes in batches
            BATCH = 100
            node_count = 0
            for i in range(0, len(unique_ids), BATCH):
                batch = [{"ext_id": eid, "uri": uri_template.format(id=eid)}
                         for eid in unique_ids[i : i + BATCH]]
                # Dynamic label requires string formatting in Cypher
                result = session.run(f"""
                    UNWIND $batch AS row
                    MERGE (n:{node_label} {{{id_key}: row.ext_id}})
                    SET n.uri = row.uri,
                        n.source = 'wikidata_harvest'
                    RETURN count(n) as cnt
                """, batch=batch)
                node_count += result.single()["cnt"]

            # MERGE relationships in batches
            rel_count = 0
            for i in range(0, len(pairs), BATCH):
                batch = pairs[i : i + BATCH]
                result = session.run(f"""
                    UNWIND $batch AS row
                    MATCH (d:Discipline {{qid: row.qid}})
                    MATCH (n:{node_label} {{{id_key}: row.ext_id}})
                    MERGE (d)-[r:{rel_type}]->(n)
                    RETURN count(r) as cnt
                """, batch=batch)
                rel_count += result.single()["cnt"]

            print(f"  {node_label:25s} {node_count:>4d} nodes, {rel_count:>4d} rels ({rel_type})")

        # Summary
        print("\n-- Summary --")
        for _, node_label, rel_type, _, _ in ID_TYPES:
            result = session.run(f"MATCH (n:{node_label}) RETURN count(n) as cnt")
            cnt = result.single()["cnt"]
            if cnt > 0:
                result2 = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as cnt")
                rcnt = result2.single()["cnt"]
                print(f"  {node_label:25s} {cnt:>4d} nodes  {rcnt:>4d} rels")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
