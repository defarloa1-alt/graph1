#!/usr/bin/env python3
"""
Phase 3: Create onomastic nodes (:Gens, :Praenomen, :Nomen, :Cognomen, :Tribe)
from DPRR label parse and wire Person nodes.

Uses parse_dprr_label from dprr_layer1. Creates nodes with MERGE, then
Person -[:HAS_PRAENOMEN|HAS_NOMEN|HAS_COGNOMEN|MEMBER_OF_GENS|MEMBER_OF_TRIBE]->.

Usage:
  python scripts/maintenance/create_onomastic_nodes.py           # dry-run
  python scripts/maintenance/create_onomastic_nodes.py --execute
"""
import argparse
import os
import sys
from pathlib import Path
from collections import defaultdict

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase

from scripts.federation.dprr_layer1 import (
    parse_dprr_label,
    PRAENOMEN_ABBREV_TO_FULL,
    TRIBE_ABBREV,
)


# Tribe abbreviation -> label_latin (standard Roman tribe names)
TRIBE_ABBREV_TO_FULL: dict[str, str] = {
    "Aem.": "Aemilia", "Ani.": "Aniensis", "Arn.": "Arnensis", "Cam.": "Camilia",
    "Clu.": "Clustumina", "Col.": "Collina", "Cor.": "Cornelia", "Esq.": "Esquilina",
    "Fab.": "Fabia", "Fal.": "Falerna", "Gal.": "Galeria", "Hor.": "Horatia",
    "Lem.": "Lemonia", "Mac.": "Maccia", "Men.": "Menenia", "Ouf.": "Oufentina",
    "Pal.": "Palatina", "Pap.": "Papiria", "Pol.": "Pollia", "Pom.": "Pomptina",
    "Pup.": "Pupinia", "Qui.": "Quirina", "Rom.": "Romilia", "Sab.": "Sabatina",
    "Scap.": "Scaptia", "Ser.": "Sergia", "Ste.": "Stellatina", "Sub.": "Suburana",
    "Suc.": "Sucusana", "Ter.": "Teretina", "Tro.": "Tromentina", "Vel.": "Velina",
    "Vol.": "Voltinia", "Vot.": "Voturia",
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Create onomastic nodes from DPRR parse")
    ap.add_argument("--execute", action="store_true", help="Write to graph (default: dry-run)")
    args = ap.parse_args()

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD required")
        return 1

    driver = GraphDatabase.driver(uri, auth=(user, password))
    db = os.getenv("NEO4J_DATABASE", "neo4j")

    # 1. Fetch Person nodes with label_dprr
    with driver.session(database=db) as session:
        r = session.run("""
            MATCH (p:Person)
            WHERE p.label_dprr IS NOT NULL AND p.label_dprr <> ''
            RETURN p.entity_id AS entity_id, p.label_dprr AS label_dprr
        """)
        persons = [dict(row) for row in r]

    # 2. Parse and collect
    gens_set: set[tuple[str, str]] = set()  # (gens_id, label_latin)
    praenomen_set: set[tuple[str, str, str]] = set()  # (id, label_latin, abbrev)
    nomen_set: set[str] = set()
    cognomen_set: set[str] = set()
    tribe_set: set[tuple[str, str]] = set()  # (id, label_latin)
    person_links: list[dict] = []  # entity_id -> gens, praenomen, nomen, cognomen[], tribe

    for row in persons:
        entity_id = row["entity_id"]
        label_dprr = row["label_dprr"]
        parsed = parse_dprr_label(label_dprr)

        links = {"entity_id": entity_id, "gens": None, "praenomen": None, "nomen": None, "cognomen": [], "tribe": None}

        if parsed.gens_prefix:
            label_latin = parsed.gens_prefix  # Can enrich with GENS_PREFIX_TO_LATIN later
            gens_set.add((parsed.gens_prefix, label_latin))
            links["gens"] = parsed.gens_prefix

        if parsed.praenomen_abbrev and parsed.praenomen_abbrev != "-.":
            full = PRAENOMEN_ABBREV_TO_FULL.get(parsed.praenomen_abbrev, parsed.praenomen_abbrev)
            praenomen_set.add((parsed.praenomen_abbrev, full, parsed.praenomen_abbrev))
            links["praenomen"] = parsed.praenomen_abbrev

        if parsed.nomen:
            nomen_set.add(parsed.nomen)
            links["nomen"] = parsed.nomen

        for c in parsed.cognomen or []:
            cognomen_set.add(c)
            links["cognomen"].append(c)

        if parsed.tribe_abbrev:
            full = TRIBE_ABBREV_TO_FULL.get(parsed.tribe_abbrev, parsed.tribe_abbrev)
            tribe_set.add((parsed.tribe_abbrev, full))
            links["tribe"] = parsed.tribe_abbrev

        person_links.append(links)

    print("Phase 3: Create onomastic nodes")
    print(f"  Persons parsed: {len(persons)}")
    print(f"  Unique Gens: {len(gens_set)}, Praenomen: {len(praenomen_set)}, Nomen: {len(nomen_set)}, Cognomen: {len(cognomen_set)}, Tribe: {len(tribe_set)}")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    if not args.execute:
        driver.close()
        return 0

    with driver.session(database=db) as session:
        # 3. Create Gens nodes
        for gens_id, label_latin in gens_set:
            session.run("""
                MERGE (g:Gens {gens_id: $gens_id})
                SET g.label_latin = $label_latin, g.gens_prefix = $gens_id
            """, gens_id=gens_id, label_latin=label_latin)
        print(f"  Gens nodes: {len(gens_set)}")

        # 4. Create Praenomen nodes
        for abbrev, label_latin, _ in praenomen_set:
            session.run("""
                MERGE (p:Praenomen {praenomen_id: $praenomen_id})
                SET p.label_latin = $label_latin, p.abbreviation = $abbreviation
            """, praenomen_id=abbrev, label_latin=label_latin, abbreviation=abbrev)
        print(f"  Praenomen nodes: {len(praenomen_set)}")

        # 5. Create Nomen nodes
        for nomen in nomen_set:
            session.run("""
                MERGE (n:Nomen {nomen_id: $nomen_id})
                SET n.label_latin = $label_latin
            """, nomen_id=nomen, label_latin=nomen)
        print(f"  Nomen nodes: {len(nomen_set)}")

        # 6. Create Cognomen nodes
        for cognomen in cognomen_set:
            session.run("""
                MERGE (c:Cognomen {cognomen_id: $cognomen_id})
                SET c.label_latin = $label_latin
            """, cognomen_id=cognomen, label_latin=cognomen)
        print(f"  Cognomen nodes: {len(cognomen_set)}")

        # 7. Create Tribe nodes
        for tribe_id, label_latin in tribe_set:
            session.run("""
                MERGE (t:Tribe {tribe_id: $tribe_id})
                SET t.label_latin = $label_latin, t.abbreviation = $abbreviation
            """, tribe_id=tribe_id, label_latin=label_latin, abbreviation=tribe_id)
        print(f"  Tribe nodes: {len(tribe_set)}")

        # 8. Wire Person -> onomastic (batched in chunks of 500)
        BATCH = 500

        def run_batched(pairs: list, rel_type: str, eid_key: str, target_key: str, target_label: str, id_prop: str):
            for i in range(0, len(pairs), BATCH):
                chunk = pairs[i : i + BATCH]
                session.run(f"""
                    UNWIND $pairs AS pair
                    MATCH (p:Person {{entity_id: pair.eid}})
                    MATCH (t:{target_label} {{{id_prop}: pair.tid}})
                    MERGE (p)-[:{rel_type}]->(t)
                """, pairs=[{"eid": e, "tid": t} for e, t in chunk])

        gens_pairs = [(l["entity_id"], l["gens"]) for l in person_links if l["gens"]]
        praenomen_pairs = [(l["entity_id"], l["praenomen"]) for l in person_links if l["praenomen"]]
        nomen_pairs = [(l["entity_id"], l["nomen"]) for l in person_links if l["nomen"]]
        cognomen_pairs = [(l["entity_id"], c) for l in person_links for c in l["cognomen"]]
        tribe_pairs = [(l["entity_id"], l["tribe"]) for l in person_links if l["tribe"]]

        if gens_pairs:
            run_batched(gens_pairs, "MEMBER_OF_GENS", "eid", "gens_id", "Gens", "gens_id")
        if praenomen_pairs:
            run_batched(praenomen_pairs, "HAS_PRAENOMEN", "eid", "pid", "Praenomen", "praenomen_id")
        if nomen_pairs:
            run_batched(nomen_pairs, "HAS_NOMEN", "eid", "nid", "Nomen", "nomen_id")
        if cognomen_pairs:
            run_batched(cognomen_pairs, "HAS_COGNOMEN", "eid", "cid", "Cognomen", "cognomen_id")
        if tribe_pairs:
            run_batched(tribe_pairs, "MEMBER_OF_TRIBE", "eid", "tid", "Tribe", "tribe_id")

        print(f"  Wired: MEMBER_OF_GENS={len(gens_pairs)}, HAS_PRAENOMEN={len(praenomen_pairs)}, HAS_NOMEN={len(nomen_pairs)}, HAS_COGNOMEN={len(cognomen_pairs)}, MEMBER_OF_TRIBE={len(tribe_pairs)}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
