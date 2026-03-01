#!/usr/bin/env python3
"""
Load discipline taxonomy registry into Neo4j.

Creates :Discipline nodes from discipline_taxonomy_backbone.csv, hierarchy
relationships (SUBCLASS_OF, PART_OF, HAS_PART), and ANCHORED_IN links to
Federation:AuthoritySystem when authority IDs exist.

Usage:
  python scripts/backbone/subject/load_discipline_taxonomy.py
  python scripts/backbone/subject/load_discipline_taxonomy.py -i output/discipline_taxonomy_backbone.csv --dry-run
"""

import argparse
import csv
import sys
from pathlib import Path

try:
    from neo4j import GraphDatabase
except ImportError:
    print("pip install neo4j", file=sys.stderr)
    sys.exit(1)

_PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT / "scripts"))
try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = None

# Federation IDs from create_authority_federations.cypher (GND not yet in registry)
FED_BY_PROP = {
    "fast_id": "FED_FAST",
    "lcsh_id": "FED_LCSH",
    "ddc": "FED_DEWEY",
    "lcc": "FED_LCC",
    "aat_id": "FED_GETTY_AAT",
}

# Human-readable labels for node display
FED_LABELS = {
    "fast_id": "FAST",
    "lcsh_id": "LCSH",
    "ddc": "Dewey",
    "lcc": "LCC",
    "aat_id": "Getty AAT",
}


def ensure_constraint(session):
    """Create Discipline qid constraint if not exists."""
    session.run("""
        CREATE CONSTRAINT discipline_qid_unique IF NOT EXISTS
        FOR (d:Discipline) REQUIRE d.qid IS UNIQUE
    """)


def ensure_registry_root(session):
    """Ensure DisciplineRegistry root exists and is linked to Chrystallum."""
    session.run("""
        MERGE (reg:DisciplineRegistry {id: 'DISCIPLINE_REGISTRY'})
        SET reg.label = 'Discipline Taxonomy Registry',
            reg.description = 'Academic disciplines with subject backbone authority IDs'
        WITH reg
        OPTIONAL MATCH (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
        FOREACH (_ IN CASE WHEN c IS NOT NULL THEN [1] ELSE [] END |
            MERGE (c)-[:HAS_DISCIPLINE_REGISTRY]->(reg)
        )
    """)


def load_disciplines(tx, rows):
    """Create Discipline nodes."""
    query = """
    UNWIND $rows AS r
    MERGE (d:Discipline {qid: r.qid})
    SET d.label = r.label,
        d.federation_labels = r.federation_labels,
        d.fast_id = CASE WHEN trim(r.fast_id) <> '' THEN r.fast_id ELSE null END,
        d.gnd_id = CASE WHEN trim(r.gnd_id) <> '' THEN r.gnd_id ELSE null END,
        d.lcsh_id = CASE WHEN trim(r.lcsh_id) <> '' THEN r.lcsh_id ELSE null END,
        d.ddc = CASE WHEN trim(r.ddc) <> '' THEN r.ddc ELSE null END,
        d.aat_id = CASE WHEN trim(r.aat_id) <> '' THEN r.aat_id ELSE null END,
        d.lcc = CASE WHEN trim(r.lcc) <> '' THEN r.lcc ELSE null END,
        d.babelnet_id = CASE WHEN trim(r.babelnet_id) <> '' THEN r.babelnet_id ELSE null END,
        d.kbpedia_id = CASE WHEN trim(r.kbpedia_id) <> '' THEN r.kbpedia_id ELSE null END,
        d.world_history_id = CASE WHEN trim(r.world_history_id) <> '' THEN r.world_history_id ELSE null END
    RETURN count(d) AS n
    """
    r = tx.run(query, rows=rows)
    return r.single()["n"]


def link_to_registry(tx, qids):
    """Link Discipline nodes to DisciplineRegistry."""
    if not qids:
        return 0
    r = tx.run("""
        MATCH (reg:DisciplineRegistry {id: 'DISCIPLINE_REGISTRY'})
        MATCH (d:Discipline) WHERE d.qid IN $qids
        MERGE (reg)-[:CONTAINS]->(d)
        RETURN count(*) AS n
    """, qids=qids)
    return r.single()["n"]


def create_subclass_of(tx, edges):
    """Create SUBCLASS_OF relationships."""
    if not edges:
        return 0
    r = tx.run("""
        UNWIND $edges AS e
        MATCH (child:Discipline {qid: e.child})
        MATCH (parent:Discipline {qid: e.parent})
        MERGE (child)-[:SUBCLASS_OF]->(parent)
        RETURN count(*) AS n
    """, edges=edges)
    return r.single()["n"]


def create_part_of(tx, edges):
    """Create PART_OF relationships."""
    if not edges:
        return 0
    r = tx.run("""
        UNWIND $edges AS e
        MATCH (child:Discipline {qid: e.child})
        MATCH (parent:Discipline {qid: e.parent})
        MERGE (child)-[:PART_OF]->(parent)
        RETURN count(*) AS n
    """, edges=edges)
    return r.single()["n"]


def create_has_part(tx, edges):
    """Create HAS_PART relationships."""
    if not edges:
        return 0
    r = tx.run("""
        UNWIND $edges AS e
        MATCH (parent:Discipline {qid: e.parent})
        MATCH (child:Discipline {qid: e.child})
        MERGE (parent)-[:HAS_PART]->(child)
        RETURN count(*) AS n
    """, edges=edges)
    return r.single()["n"]


def create_anchored_in(tx, links):
    """Create ANCHORED_IN to Federation when authority ID exists."""
    if not links:
        return 0
    r = tx.run("""
        UNWIND $links AS link
        MATCH (d:Discipline {qid: link.qid})
        MATCH (fed:Federation {id: link.fed_id})
        MERGE (d)-[r:ANCHORED_IN]->(fed)
        SET r.authority_id = link.authority_id
        RETURN count(*) AS n
    """, links=links)
    return r.single()["n"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, default=_PROJECT / "output" / "discipline_taxonomy_backbone.csv")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        print("Run: python scripts/backbone/subject/filter_discipline_backbone.py")
        sys.exit(1)

    rows = []
    with open(args.input, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("qid") or "").strip():
                row = {k: (v or "").strip() for k, v in r.items()}
                # Add federation_labels for node display (e.g. "FAST, LCSH, Dewey")
                labels = [FED_LABELS[prop] for prop in FED_BY_PROP if (row.get(prop) or "").strip()]
                row["federation_labels"] = ", ".join(labels) if labels else ""
                rows.append(row)
    print(f"Loaded {len(rows)} rows from {args.input}")

    # Build edges from pipe-separated columns
    subclass_edges = []
    part_of_edges = []
    has_part_edges = []
    for r in rows:
        qid = r.get("qid", "")
        for parent in (r.get("subclass_of") or "").split("|"):
            if parent.strip():
                subclass_edges.append({"child": qid, "parent": parent.strip()})
        for parent in (r.get("part_of") or "").split("|"):
            if parent.strip():
                part_of_edges.append({"child": qid, "parent": parent.strip()})
        for child in (r.get("has_parts") or "").split("|"):
            if child.strip():
                has_part_edges.append({"parent": qid, "child": child.strip()})

    # Build ANCHORED_IN links (only for federations we have)
    anchored_links = []
    for r in rows:
        qid = r.get("qid", "")
        for prop, fed_id in FED_BY_PROP.items():
            val = (r.get(prop) or "").strip()
            if val:
                # Take first value if pipe-separated
                first = val.split("|")[0].strip()
                if first:
                    anchored_links.append({"qid": qid, "fed_id": fed_id, "authority_id": first})

    if args.dry_run:
        print("Dry run - would create:")
        print(f"  {len(rows)} Discipline nodes")
        print(f"  {len(subclass_edges)} SUBCLASS_OF edges")
        print(f"  {len(part_of_edges)} PART_OF edges")
        print(f"  {len(has_part_edges)} HAS_PART edges")
        print(f"  {len(anchored_links)} ANCHORED_IN links")
        return

    if not args.password:
        import getpass
        args.password = getpass.getpass("Neo4j password: ")

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    with driver.session() as session:
        ensure_constraint(session)
        ensure_registry_root(session)
        n = session.execute_write(load_disciplines, rows)
        print(f"  Created/updated {n} Discipline nodes")
        session.execute_write(link_to_registry, [r["qid"] for r in rows])
        print(f"  Linked to DisciplineRegistry")
        n = session.execute_write(create_subclass_of, subclass_edges)
        print(f"  Created {n} SUBCLASS_OF relationships")
        n = session.execute_write(create_part_of, part_of_edges)
        print(f"  Created {n} PART_OF relationships")
        n = session.execute_write(create_has_part, has_part_edges)
        print(f"  Created {n} HAS_PART relationships")
        # ANCHORED_IN: only FED_GND may not exist; others from create_authority_federations
        n = session.execute_write(create_anchored_in, anchored_links)
        print(f"  Created {n} ANCHORED_IN links to federations")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
