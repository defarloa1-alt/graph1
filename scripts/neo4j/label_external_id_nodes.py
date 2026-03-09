#!/usr/bin/env python3
"""
Add labels to all external ID nodes.

Phase 1: Copy discipline label via graph traversal (instant, covers all 3,028)
Phase 2: Fetch authoritative labels from APIs for actionable sources
"""
import sys
import json
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase

USER_AGENT = "ChrystallumBot/1.0 (research project)"

# (rel_type, node_label, id_key, authority_qid)
# authority_qid = Wikidata QID of the authority system itself
ID_TYPES = [
    ("HAS_FAST",       "FAST_Heading",      "fast_id",     "Q3294867"),
    ("HAS_GETTY_AAT",  "Getty_AAT_Concept", "aat_id",      "Q1417088"),
    ("HAS_OPENALEX",   "OpenAlex_Concept",  "openalex_id", "Q107507571"),
    ("HAS_GND",        "GND_Concept",       "gnd_id",      "Q36578"),
    ("HAS_BNF",        "BnF_Concept",       "bnf_id",      "Q19938912"),
    ("HAS_MESH",       "MeSH_Descriptor",   "mesh_id",     "Q199897"),
    ("HAS_BNCF",       "BNCF_Concept",      "bncf_id",     None),
    ("HAS_NDL",        "NDL_Concept",        "ndl_id",     "Q477675"),
    ("HAS_UNESCO",     "UNESCO_Concept",    "unesco_id",   "Q2467479"),
    ("HAS_BABELNET",   "BabelNet_Concept",  "babelnet_id", "Q4837690"),
    ("HAS_OPENLIBRARY","OpenLibrary_Work",  "ol_work_id",  "Q1201876"),
    ("HAS_PACTOLS",    "PACTOLS_Concept",   "pactols_id",  "Q89562190"),
]


def phase0_stamp_authority_qids(session):
    """Set authority_qid on all external ID nodes."""
    print("Phase 0: Stamp authority QIDs")
    for rel_type, node_label, id_key, authority_qid in ID_TYPES:
        if not authority_qid:
            continue
        result = session.run(f"""
            MATCH (n:{node_label})
            SET n.authority_qid = $qid
            RETURN count(n) as cnt
        """, qid=authority_qid)
        cnt = result.single()["cnt"]
        print(f"  {node_label:25s} {cnt:>4d} <- {authority_qid}")


def phase1_copy_labels(session):
    """Copy discipline label to external ID nodes via relationship traversal."""
    print("\nPhase 1: Copy discipline labels")
    for rel_type, node_label, id_key, _ in ID_TYPES:
        result = session.run(f"""
            MATCH (d:Discipline)-[:{rel_type}]->(n:{node_label})
            WHERE n.label IS NULL
            SET n.label = d.label
            RETURN count(n) as cnt
        """)
        cnt = result.single()["cnt"]
        if cnt > 0:
            print(f"  {node_label:25s} {cnt:>4d} labeled from discipline")


def fetch_openalex_labels(session):
    """Fetch display_name from OpenAlex API."""
    print("\nPhase 2a: OpenAlex API labels")
    result = session.run(
        "MATCH (n:OpenAlex_Concept) RETURN n.openalex_id as id LIMIT 500"
    )
    ids = [r["id"] for r in result]

    updated = 0
    for i in range(0, len(ids), 25):
        batch = ids[i:i+25]
        pipe = "|".join(batch)
        try:
            r = requests.get(
                f"https://api.openalex.org/concepts",
                params={"filter": f"ids.openalex:{pipe}", "per_page": 25},
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
            if r.status_code == 200:
                for item in r.json().get("results", []):
                    oa_id = item["id"].split("/")[-1]
                    label = item.get("display_name", "")
                    if label:
                        session.run(
                            "MATCH (n:OpenAlex_Concept {openalex_id: $id}) "
                            "SET n.label = $label",
                            id=oa_id, label=label,
                        )
                        updated += 1
        except Exception as e:
            print(f"    Error: {e}")
        time.sleep(0.5)
    print(f"  OpenAlex_Concept: {updated} labels from API")


def fetch_getty_labels(session):
    """Fetch prefLabel from Getty AAT SPARQL."""
    print("\nPhase 2b: Getty AAT SPARQL labels")
    result = session.run(
        "MATCH (n:Getty_AAT_Concept) RETURN n.aat_id as id"
    )
    ids = [r["id"] for r in result]

    updated = 0
    BATCH = 50
    for i in range(0, len(ids), BATCH):
        batch = ids[i:i+BATCH]
        values = " ".join(f"<http://vocab.getty.edu/aat/{eid}>" for eid in batch)
        query = f"""
            SELECT ?s ?label WHERE {{
              VALUES ?s {{ {values} }}
              ?s skos:prefLabel ?label .
              FILTER(lang(?label) = 'en' || lang(?label) = '')
            }}
        """
        try:
            r = requests.get(
                "http://vocab.getty.edu/sparql",
                params={"query": query},
                headers={"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT},
                timeout=30,
            )
            if r.status_code == 200:
                for b in r.json()["results"]["bindings"]:
                    aat_id = b["s"]["value"].split("/")[-1]
                    label = b["label"]["value"]
                    session.run(
                        "MATCH (n:Getty_AAT_Concept {aat_id: $id}) SET n.label = $label",
                        id=aat_id, label=label,
                    )
                    updated += 1
        except Exception as e:
            print(f"    Error: {e}")
        time.sleep(1)
    print(f"  Getty_AAT_Concept: {updated} labels from SPARQL")


def fetch_mesh_labels(session):
    """Fetch labels from MeSH RDF."""
    print("\nPhase 2c: MeSH labels")
    result = session.run(
        "MATCH (n:MeSH_Descriptor) RETURN n.mesh_id as id"
    )
    ids = [r["id"] for r in result]

    updated = 0
    for mid in ids:
        try:
            r = requests.get(
                f"https://id.nlm.nih.gov/mesh/{mid}.json",
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                label = data.get("label", {}).get("@value", "")
                if label:
                    session.run(
                        "MATCH (n:MeSH_Descriptor {mesh_id: $id}) SET n.label = $label",
                        id=mid, label=label,
                    )
                    updated += 1
        except Exception:
            pass
        time.sleep(0.3)
    print(f"  MeSH_Descriptor: {updated} labels from API")


def fetch_fast_labels(session):
    """Fetch labels from FAST linked data."""
    print("\nPhase 2d: FAST labels")
    result = session.run(
        "MATCH (n:FAST_Heading) RETURN n.fast_id as id"
    )
    ids = [r["id"] for r in result]

    updated = 0
    for fid in ids:
        try:
            r = requests.get(
                f"https://id.worldcat.org/fast/{fid}.jsonld",
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                # FAST JSONLD structure varies; look for prefLabel
                if isinstance(data, list):
                    for item in data:
                        pref = item.get("http://www.w3.org/2004/02/skos/core#prefLabel", [])
                        if pref:
                            label = pref[0].get("@value", "")
                            if label:
                                session.run(
                                    "MATCH (n:FAST_Heading {fast_id: $id}) SET n.label = $label",
                                    id=fid, label=label,
                                )
                                updated += 1
                                break
                elif isinstance(data, dict):
                    pref = data.get("http://www.w3.org/2004/02/skos/core#prefLabel", [])
                    if pref:
                        label = pref[0].get("@value", "") if isinstance(pref, list) else ""
                        if label:
                            session.run(
                                "MATCH (n:FAST_Heading {fast_id: $id}) SET n.label = $label",
                                id=fid, label=label,
                            )
                            updated += 1
        except Exception:
            pass
        time.sleep(0.3)
    print(f"  FAST_Heading: {updated} labels from API")


def fetch_openlibrary_labels(session):
    """Fetch titles from Open Library API."""
    print("\nPhase 2e: Open Library labels")
    result = session.run(
        "MATCH (n:OpenLibrary_Work) RETURN n.ol_work_id as id"
    )
    ids = [r["id"] for r in result]

    updated = 0
    for olid in ids:
        try:
            r = requests.get(
                f"https://openlibrary.org/works/{olid}.json",
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                title = data.get("title", "")
                if title:
                    session.run(
                        "MATCH (n:OpenLibrary_Work {ol_work_id: $id}) SET n.label = $label",
                        id=olid, label=title,
                    )
                    updated += 1
        except Exception:
            pass
        time.sleep(0.5)
    print(f"  OpenLibrary_Work: {updated} labels from API")


def fetch_gnd_labels(session):
    """Fetch preferredName from lobid.org GND API."""
    print("\nPhase 2f: GND labels")
    result = session.run(
        "MATCH (n:GND_Concept) RETURN n.gnd_id as id"
    )
    ids = [r["id"] for r in result]

    updated = 0
    for gid in ids:
        try:
            r = requests.get(
                f"https://lobid.org/gnd/{gid}.json",
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                label = data.get("preferredName", "")
                if label:
                    session.run(
                        "MATCH (n:GND_Concept {gnd_id: $id}) SET n.label = $label",
                        id=gid, label=label,
                    )
                    updated += 1
        except Exception:
            pass
        time.sleep(0.3)
    print(f"  GND_Concept: {updated} labels from API")


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Phase 0: stamp authority QIDs
        phase0_stamp_authority_qids(session)

        # Phase 1: instant label copy from disciplines
        phase1_copy_labels(session)

        # Phase 2: authoritative labels from APIs
        fetch_openalex_labels(session)
        fetch_getty_labels(session)
        fetch_mesh_labels(session)
        fetch_fast_labels(session)
        fetch_openlibrary_labels(session)
        fetch_gnd_labels(session)

        # Summary
        print("\n-- Label coverage --")
        for _, node_label, _, _ in ID_TYPES:
            result = session.run(f"""
                MATCH (n:{node_label})
                RETURN count(n) as total,
                       count(CASE WHEN n.label IS NOT NULL THEN 1 END) as labeled
            """)
            r = result.single()
            print(f"  {node_label:25s} {r['labeled']:>4d}/{r['total']:<4d} labeled")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
