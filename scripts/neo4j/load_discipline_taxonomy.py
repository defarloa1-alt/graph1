#!/usr/bin/env python3
"""
Load discipline taxonomy to Neo4j (upsert, non-destructive).

MERGE on qid — updates existing nodes, creates new ones.
Does NOT delete existing Discipline nodes (preserves HAS_FACET, ROUTES_TO, etc.).

Two-tier model:
  - backbone (has authority IDs) → cipher-addressable, corpus query keys
  - expanded  (no authority IDs)  → navigable via hierarchy, SFA working vocabulary

Properties set:
  qid, label, tier (backbone|expanded), source, harvest_date,
  subclass_of, subclass_of_label, part_of, part_of_label,
  has_parts, has_parts_label,
  fast_id, gnd_id, lcsh_id, ddc, aat_id, babelnet_id, kbpedia_id,
  world_history_id, lcc

Relationships wired:
  SUBCLASS_OF (child→parent, within set)
  PART_OF     (child→parent, within set)

Usage:
  python scripts/neo4j/load_discipline_taxonomy.py
  python scripts/neo4j/load_discipline_taxonomy.py -i output/discipline_taxonomy_new.csv --dry-run
  python scripts/neo4j/load_discipline_taxonomy.py -i output/discipline_taxonomy_new.csv
"""

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

BACKBONE_COLS = ("fast_id", "lcsh_id", "ddc", "lcc", "gnd_id", "aat_id")
AUTHORITY_COLS = ("fast_id", "gnd_id", "lcsh_id", "ddc", "aat_id",
                  "babelnet_id", "kbpedia_id", "world_history_id", "lcc")
BATCH_SIZE = 100


def _clean(val: str) -> str | None:
    """Return stripped value or None for empty."""
    v = (val or "").strip()
    return v if v else None


def _tier(row: dict) -> str:
    """Classify row as backbone or expanded."""
    return "backbone" if any((row.get(c) or "").strip() for c in BACKBONE_COLS) else "expanded"


def load_csv(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            qid = (r.get("qid") or "").strip()
            if not qid:
                continue
            rows.append(r)
    return rows


def build_params(rows: list[dict]) -> list[dict]:
    params = []
    for r in rows:
        p = {
            "qid": r["qid"].strip(),
            "label": (r.get("label") or r["qid"]).strip(),
            "tier": _tier(r),
            "subclass_of": _clean(r.get("subclass_of")),
            "subclass_of_label": _clean(r.get("subclass_of_label")),
            "part_of": _clean(r.get("part_of")),
            "part_of_label": _clean(r.get("part_of_label")),
            "has_parts": _clean(r.get("has_parts")),
            "has_parts_label": _clean(r.get("has_parts_label")),
        }
        for col in AUTHORITY_COLS:
            p[col] = _clean(r.get(col))
        params.append(p)
    return params


def upsert_nodes(session, params: list[dict]) -> int:
    total = 0
    for i in range(0, len(params), BATCH_SIZE):
        batch = params[i : i + BATCH_SIZE]
        result = session.run("""
            UNWIND $batch AS row
            MERGE (d:Discipline {qid: row.qid})
            SET d.label = row.label,
                d.tier = row.tier,
                d.subclass_of = row.subclass_of,
                d.subclass_of_label = row.subclass_of_label,
                d.part_of = row.part_of,
                d.part_of_label = row.part_of_label,
                d.has_parts = row.has_parts,
                d.has_parts_label = row.has_parts_label,
                d.fast_id = row.fast_id,
                d.gnd_id = row.gnd_id,
                d.lcsh_id = row.lcsh_id,
                d.ddc = row.ddc,
                d.aat_id = row.aat_id,
                d.babelnet_id = row.babelnet_id,
                d.kbpedia_id = row.kbpedia_id,
                d.world_history_id = row.world_history_id,
                d.lcc = row.lcc,
                d.source = 'wikidata_harvest_2026',
                d.harvest_date = date()
            RETURN count(d) AS cnt
        """, batch=batch)
        total += result.single()["cnt"]
    return total


def wire_subclass_of(session) -> int:
    result = session.run("""
        MATCH (child:Discipline)
        WHERE child.subclass_of IS NOT NULL
        WITH child, split(child.subclass_of, '|') AS parents
        UNWIND parents AS parent_qid
        WITH child, trim(parent_qid) AS pqid
        WHERE pqid <> ''
        MATCH (parent:Discipline {qid: pqid})
        WHERE parent.qid <> child.qid
        MERGE (child)-[:SUBCLASS_OF]->(parent)
        RETURN count(*) AS rels
    """)
    return result.single()["rels"]


def wire_part_of(session) -> int:
    result = session.run("""
        MATCH (child:Discipline)
        WHERE child.part_of IS NOT NULL
        WITH child, split(child.part_of, '|') AS parents
        UNWIND parents AS parent_qid
        WITH child, trim(parent_qid) AS pqid
        WHERE pqid <> ''
        MATCH (parent:Discipline {qid: pqid})
        WHERE parent.qid <> child.qid
        MERGE (child)-[:PART_OF]->(parent)
        RETURN count(*) AS rels
    """)
    return result.single()["rels"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path,
                        default=ROOT / "output" / "discipline_taxonomy_new.csv")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse CSV and print stats, no Neo4j write")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        return

    rows = load_csv(args.input)
    params = build_params(rows)

    backbone = sum(1 for p in params if p["tier"] == "backbone")
    expanded = sum(1 for p in params if p["tier"] == "expanded")
    print(f"Loaded {len(params)} disciplines ({backbone} backbone, {expanded} expanded)")

    if args.dry_run:
        # Authority coverage
        for col in AUTHORITY_COLS:
            n = sum(1 for p in params if p[col])
            if n:
                print(f"  {col}: {n}")
        print("\nDry run — no Neo4j writes.")
        return

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            # 1. Upsert nodes
            cnt = upsert_nodes(session, params)
            print(f"1. Merged {cnt} Discipline nodes")

            # 2. Wire SUBCLASS_OF
            rels_sc = wire_subclass_of(session)
            print(f"2. Wired {rels_sc} SUBCLASS_OF relationships")

            # 3. Wire PART_OF
            rels_po = wire_part_of(session)
            print(f"3. Wired {rels_po} PART_OF relationships")

            # 4. Verify
            result = session.run("""
                MATCH (d:Discipline)
                RETURN count(d) AS total,
                       sum(CASE WHEN d.tier = 'backbone' THEN 1 ELSE 0 END) AS backbone,
                       sum(CASE WHEN d.tier = 'expanded' THEN 1 ELSE 0 END) AS expanded
            """)
            r = result.single()
            print(f"\nFinal: {r['total']} Discipline nodes "
                  f"({r['backbone']} backbone, {r['expanded']} expanded)")

            result = session.run("""
                MATCH (:Discipline)-[r:SUBCLASS_OF]->(:Discipline) RETURN count(r) AS sc
            """)
            sc = result.single()["sc"]
            result = session.run("""
                MATCH (:Discipline)-[r:PART_OF]->(:Discipline) RETURN count(r) AS po
            """)
            po = result.single()["po"]
            print(f"Relationships: {sc} SUBCLASS_OF, {po} PART_OF")
    finally:
        driver.close()

    print("Done.")


if __name__ == "__main__":
    main()
