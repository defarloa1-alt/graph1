#!/usr/bin/env python3
"""
Create D22_SCORE_person_federation decision table and rescore all Person nodes.

11 rules, max 100 points:
  r1:  qid IS NOT NULL                              → +20  wikidata_alignment
  r2:  dprr_id IS NOT NULL                           → +15  domain_authority
  r3:  loc_authority_id OR lcnaf_id IS NOT NULL       → +10  library_authority
  r4:  viaf_id IS NOT NULL                            → +10  crosswalk_authority
  r5:  gnd_id IS NOT NULL                             → +5   crosswalk_authority
  r6:  isni IS NOT NULL                               → +5   crosswalk_authority
  r7:  birth_year OR death_year IS NOT NULL            → +10  temporal_bounds
  r8:  occupation IS NOT NULL                          → +10  class_signal
  r9:  instance_of IS NOT NULL                         → +5   type_signal
  r10: gender IS NOT NULL                              → +5   demographic_signal
  r11: citizenship IS NOT NULL                         → +5   affiliation_signal

Usage:
  python scripts/neo4j/create_d22_person_scoring.py --dry-run
  python scripts/neo4j/create_d22_person_scoring.py --write
"""

import argparse
import io
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

from neo4j import GraphDatabase

D22_ROWS = [
    {
        "row_id": "D22_r1_qid",
        "conditions": "qid IS NOT NULL",
        "action": "add_score",
        "action_detail": "20",
        "score_points": 20,
        "dimension": "wikidata_alignment",
        "priority": 1,
    },
    {
        "row_id": "D22_r2_dprr",
        "conditions": "dprr_id IS NOT NULL",
        "action": "add_score",
        "action_detail": "15",
        "score_points": 15,
        "dimension": "domain_authority",
        "priority": 2,
    },
    {
        "row_id": "D22_r3_library_auth",
        "conditions": "loc_authority_id IS NOT NULL OR lcnaf_id IS NOT NULL",
        "action": "add_score",
        "action_detail": "10",
        "score_points": 10,
        "dimension": "library_authority",
        "priority": 3,
    },
    {
        "row_id": "D22_r4_viaf",
        "conditions": "viaf_id IS NOT NULL",
        "action": "add_score",
        "action_detail": "10",
        "score_points": 10,
        "dimension": "crosswalk_authority",
        "priority": 4,
    },
    {
        "row_id": "D22_r5_gnd",
        "conditions": "gnd_id IS NOT NULL",
        "action": "add_score",
        "action_detail": "5",
        "score_points": 5,
        "dimension": "crosswalk_authority",
        "priority": 5,
    },
    {
        "row_id": "D22_r6_isni",
        "conditions": "isni IS NOT NULL",
        "action": "add_score",
        "action_detail": "5",
        "score_points": 5,
        "dimension": "crosswalk_authority",
        "priority": 6,
    },
    {
        "row_id": "D22_r7_temporal",
        "conditions": "birth_year IS NOT NULL OR death_year IS NOT NULL",
        "action": "add_score",
        "action_detail": "10",
        "score_points": 10,
        "dimension": "temporal_bounds",
        "priority": 7,
    },
    {
        "row_id": "D22_r8_occupation",
        "conditions": "occupation IS NOT NULL",
        "action": "add_score",
        "action_detail": "10",
        "score_points": 10,
        "dimension": "class_signal",
        "priority": 8,
    },
    {
        "row_id": "D22_r9_instance_of",
        "conditions": "instance_of IS NOT NULL",
        "action": "add_score",
        "action_detail": "5",
        "score_points": 5,
        "dimension": "type_signal",
        "priority": 9,
    },
    {
        "row_id": "D22_r10_gender",
        "conditions": "gender IS NOT NULL",
        "action": "add_score",
        "action_detail": "5",
        "score_points": 5,
        "dimension": "demographic_signal",
        "priority": 10,
    },
    {
        "row_id": "D22_r11_citizenship",
        "conditions": "citizenship IS NOT NULL",
        "action": "add_score",
        "action_detail": "5",
        "score_points": 5,
        "dimension": "affiliation_signal",
        "priority": 11,
    },
]

CREATE_TABLE = """
MERGE (dt:SYS_DecisionTable {table_id: 'D22_SCORE_person_federation'})
SET dt.description = 'Component scoring rubric for Person nodes. 11 rules, max 100 points. '
    + 'Weights: QID(20), DPRR(15), LoC(10), VIAF(10), GND(5), ISNI(5), temporal(10), '
    + 'occupation(10), instance_of(5), gender(5), citizenship(5). '
    + 'Created 2026-03-08 based on Wikidata enrichment survey of 3,336 Person entities.',
    dt.updated = date('2026-03-08'),
    dt.entity_type = 'Person',
    dt.max_score = 100
RETURN dt.table_id AS tid
"""

CREATE_ROWS = """
UNWIND $rows AS row
MATCH (dt:SYS_DecisionTable {table_id: 'D22_SCORE_person_federation'})
MERGE (dr:SYS_DecisionRow {row_id: row.row_id})
SET dr.conditions    = row.conditions,
    dr.action        = row.action,
    dr.action_detail = row.action_detail,
    dr.score_points  = row.score_points,
    dr.dimension     = row.dimension,
    dr.priority      = row.priority
MERGE (dt)-[:HAS_ROW]->(dr)
RETURN count(dr) AS created
"""

RESCORE_QUERY = """
MATCH (p:Person)
SET p.federation_score =
    CASE WHEN p.qid IS NOT NULL THEN 20 ELSE 0 END +
    CASE WHEN p.dprr_id IS NOT NULL THEN 15 ELSE 0 END +
    CASE WHEN p.loc_authority_id IS NOT NULL OR p.lcnaf_id IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.viaf_id IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.gnd_id IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.isni IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.birth_year IS NOT NULL OR p.death_year IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.occupation IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.instance_of IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.gender IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.citizenship IS NOT NULL THEN 5 ELSE 0 END,
    p.federation_score_version = 'D22_v1_11rule',
    p.federation_score_updated = date('2026-03-08')
RETURN count(p) AS rescored
"""

PREVIEW_QUERY = """
MATCH (p:Person)
WITH p,
    CASE WHEN p.qid IS NOT NULL THEN 20 ELSE 0 END +
    CASE WHEN p.dprr_id IS NOT NULL THEN 15 ELSE 0 END +
    CASE WHEN p.loc_authority_id IS NOT NULL OR p.lcnaf_id IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.viaf_id IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.gnd_id IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.isni IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.birth_year IS NOT NULL OR p.death_year IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.occupation IS NOT NULL THEN 10 ELSE 0 END +
    CASE WHEN p.instance_of IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.gender IS NOT NULL THEN 5 ELSE 0 END +
    CASE WHEN p.citizenship IS NOT NULL THEN 5 ELSE 0 END AS new_score
RETURN new_score, count(p) AS cnt
ORDER BY new_score
"""


def main():
    parser = argparse.ArgumentParser(description="Create D22 Person scoring table + rescore")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    write_mode = args.write and not args.dry_run
    print(f"D22 Person Federation Scoring [{'WRITE' if write_mode else 'DRY RUN'}]")
    print("=" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Preview score distribution
    print("\nScore distribution (preview):")
    with driver.session() as session:
        result = session.run(PREVIEW_QUERY)
        rows = list(result)
        total = 0
        for r in rows:
            score = r["new_score"]
            cnt = r["cnt"]
            total += cnt
            bar = "#" * (cnt // 50)
            print(f"  {score:>3} pts:  {cnt:>6}  {bar}")
        print(f"\n  Total: {total}")

    # Show rules
    print(f"\nD22 rules ({len(D22_ROWS)} rules, max 100):")
    for row in D22_ROWS:
        print(f"  {row['row_id']:25s}  +{row['score_points']:2d}  {row['dimension']:25s}  {row['conditions']}")

    if not write_mode:
        print("\n  [DRY RUN] Re-run with --write to apply.")
        driver.close()
        return

    # Step 1: Create decision table
    print("\nStep 1: Creating D22 decision table...")
    with driver.session() as session:
        session.run(CREATE_TABLE)
        print("  D22_SCORE_person_federation created")

    # Step 2: Create decision rows
    print("\nStep 2: Creating decision rows...")
    with driver.session() as session:
        result = session.run(CREATE_ROWS, rows=D22_ROWS)
        created = result.single()["created"]
        print(f"  {created} rows created")

    # Step 3: Rescore all Persons
    print("\nStep 3: Rescoring all Person nodes...")
    with driver.session() as session:
        result = session.run(RESCORE_QUERY)
        rescored = result.single()["rescored"]
        print(f"  Rescored {rescored} Person nodes")

    # Verify
    print(f"\n{'=' * 60}")
    print("Verification:")
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Person) WHERE p.federation_score IS NOT NULL
            RETURN avg(p.federation_score) AS avg,
                   min(p.federation_score) AS min,
                   max(p.federation_score) AS max,
                   count(p) AS cnt
        """)
        v = result.single()
        print(f"  Scores: avg={v['avg']:.1f}, min={v['min']}, max={v['max']} ({v['cnt']} nodes)")

        result = session.run("""
            MATCH (dt:SYS_DecisionTable {table_id: 'D22_SCORE_person_federation'})-[:HAS_ROW]->(r:SYS_DecisionRow)
            RETURN count(r) AS rows
        """)
        rows = result.single()["rows"]
        print(f"  D22 has {rows} rules in graph")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
