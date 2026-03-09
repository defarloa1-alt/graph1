#!/usr/bin/env python3
"""
Materialize cipher strings on external ID nodes and on the HAS_* relationships.

Cipher format: {discipline_qid}:{wikidata_pid}:{ext_id_value}

Each external ID node gets:
  - cipher: the cipher string
  - pid: the Wikidata property ID that maps to this authority

Each HAS_* relationship gets:
  - cipher: same string (queryable from the edge)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

# (rel_type, node_label, id_key, wikidata_pid)
ID_TYPES = [
    ("HAS_LCSH",       "LCSH_Heading",      "lcsh_id",     "P244"),
    ("HAS_FAST",       "FAST_Heading",      "fast_id",     "P2163"),
    ("HAS_LCC_CLASS",  "LCC_Class",         "code",        "P1149"),
    ("HAS_GETTY_AAT",  "Getty_AAT_Concept", "aat_id",      "P1014"),
    ("HAS_OPENALEX",   "OpenAlex_Concept",  "openalex_id", "P10283"),
    ("HAS_GND",        "GND_Concept",       "gnd_id",      "P227"),
    ("HAS_BNF",        "BnF_Concept",       "bnf_id",      "P268"),
    ("HAS_MESH",       "MeSH_Descriptor",   "mesh_id",     "P486"),
    ("HAS_BNCF",       "BNCF_Concept",      "bncf_id",     "P508"),
    ("HAS_NDL",        "NDL_Concept",       "ndl_id",      "P349"),
    ("HAS_UNESCO",     "UNESCO_Concept",    "unesco_id",   "P3916"),
    ("HAS_BABELNET",   "BabelNet_Concept",  "babelnet_id", "P2581"),
    ("HAS_OPENLIBRARY","OpenLibrary_Work",  "ol_work_id",  "P3847"),
    ("HAS_PACTOLS",    "PACTOLS_Concept",   "pactols_id",  "P4212"),
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        total_nodes = 0
        total_rels = 0

        for rel_type, node_label, id_key, pid in ID_TYPES:
            # Set pid on nodes
            session.run(f"""
                MATCH (n:{node_label})
                SET n.pid = $pid
            """, pid=pid)

            # Materialize cipher on relationships and nodes
            result = session.run(f"""
                MATCH (d:Discipline)-[r:{rel_type}]->(n:{node_label})
                SET r.cipher = d.qid + ':' + $pid + ':' + n.{id_key},
                    r.pid = $pid,
                    n.cipher = d.qid + ':' + $pid + ':' + n.{id_key}
                RETURN count(r) as cnt
            """, pid=pid)
            cnt = result.single()["cnt"]
            total_rels += cnt

            # Count nodes that got ciphers
            result2 = session.run(f"""
                MATCH (n:{node_label}) WHERE n.cipher IS NOT NULL
                RETURN count(n) as cnt
            """)
            ncnt = result2.single()["cnt"]
            total_nodes += ncnt

            print(f"  {rel_type:20s} {node_label:25s} {cnt:>4d} rels, {ncnt:>4d} nodes  (pid={pid})")

        print(f"\nTotal: {total_nodes} nodes + {total_rels} rels with ciphers")

        # Sample ciphers
        print("\nSample ciphers (archaeology):")
        result = session.run("""
            MATCH (d:Discipline {label: 'archaeology'})-[r]->(n)
            WHERE r.cipher IS NOT NULL
            RETURN r.cipher as cipher, type(r) as rel, n.label as target
            ORDER BY r.cipher
        """)
        for record in result:
            print(f"  {record['cipher']:45s} {record['rel']:20s} -> {record['target']}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
