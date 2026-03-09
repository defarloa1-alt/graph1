#!/usr/bin/env python3
"""
Update D16_SCORE_place_federation with new scoring rows based on geographic survey findings.

Current D16 (4 rules, max 100):
  r1: pleiades_id IS NOT NULL → +20 (place_authority)
  r2: qid IS NOT NULL → +50 (wikidata_alignment)
  r3: temporal bounds → +20 (temporal_bounds)
  r4: coords → +10 (geospatial)

New D16 (9 rules, max 100 — rebalanced):
  r1: qid IS NOT NULL → +25 (wikidata_alignment)
  r2: pleiades_id IS NOT NULL → +20 (place_authority)
  r3: geonames_id IS NOT NULL → +10 (crosswalk_authority)
  r4: tgn_id IS NOT NULL → +5 (crosswalk_authority)
  r5: loc_authority_id OR viaf_id OR gnd_id → +10 (library_authority)
  r6: osm_relation_id IS NOT NULL → +5 (modern_reference)
  r7: lat IS NOT NULL AND long IS NOT NULL → +10 (geospatial)
  r8: inception_year IS NOT NULL OR dissolved_year IS NOT NULL → +10 (temporal_bounds)
  r9: instance_of IS NOT NULL → +5 (class_signal)

Also adds bypass rule for atemporal physical features (river, mountain, lake, sea, etc.)
to the class hierarchy annotation on D16.
"""

import io
import sys
import os
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


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Delete existing D16 rows
        result = session.run("""
            MATCH (dt:SYS_DecisionTable {table_id: 'D16_SCORE_place_federation'})-[r:HAS_ROW]->(dr:SYS_DecisionRow)
            DETACH DELETE dr
            RETURN count(dr) AS deleted
        """)
        deleted = result.single()["deleted"]
        print(f"Deleted {deleted} old D16 rows")

        # New rows — rebalanced to max 100
        new_rows = [
            {
                "row_id": "D16_r1_qid",
                "conditions": "qid IS NOT NULL",
                "action": "add_score",
                "action_detail": "25",
                "score_points": 25,
                "dimension": "wikidata_alignment",
                "priority": 1,
            },
            {
                "row_id": "D16_r2_pleiades",
                "conditions": "pleiades_id IS NOT NULL",
                "action": "add_score",
                "action_detail": "20",
                "score_points": 20,
                "dimension": "place_authority",
                "priority": 2,
            },
            {
                "row_id": "D16_r3_geonames",
                "conditions": "geonames_id IS NOT NULL",
                "action": "add_score",
                "action_detail": "10",
                "score_points": 10,
                "dimension": "crosswalk_authority",
                "priority": 3,
            },
            {
                "row_id": "D16_r4_tgn",
                "conditions": "tgn_id IS NOT NULL",
                "action": "add_score",
                "action_detail": "5",
                "score_points": 5,
                "dimension": "crosswalk_authority",
                "priority": 4,
            },
            {
                "row_id": "D16_r5_library_auth",
                "conditions": "loc_authority_id IS NOT NULL OR viaf_id IS NOT NULL OR gnd_id IS NOT NULL",
                "action": "add_score",
                "action_detail": "10",
                "score_points": 10,
                "dimension": "library_authority",
                "priority": 5,
            },
            {
                "row_id": "D16_r6_osm",
                "conditions": "osm_relation_id IS NOT NULL",
                "action": "add_score",
                "action_detail": "5",
                "score_points": 5,
                "dimension": "modern_reference",
                "priority": 6,
            },
            {
                "row_id": "D16_r7_coords",
                "conditions": "lat IS NOT NULL AND long IS NOT NULL",
                "action": "add_score",
                "action_detail": "10",
                "score_points": 10,
                "dimension": "geospatial",
                "priority": 7,
            },
            {
                "row_id": "D16_r8_temporal",
                "conditions": "inception_year IS NOT NULL OR dissolved_year IS NOT NULL",
                "action": "add_score",
                "action_detail": "10",
                "score_points": 10,
                "dimension": "temporal_bounds",
                "priority": 8,
            },
            {
                "row_id": "D16_r9_class",
                "conditions": "instance_of IS NOT NULL",
                "action": "add_score",
                "action_detail": "5",
                "score_points": 5,
                "dimension": "class_signal",
                "priority": 9,
            },
        ]

        # Write new rows
        result = session.run("""
            UNWIND $rows AS row
            MATCH (dt:SYS_DecisionTable {table_id: 'D16_SCORE_place_federation'})
            CREATE (dr:SYS_DecisionRow {
                row_id: row.row_id,
                conditions: row.conditions,
                action: row.action,
                action_detail: row.action_detail,
                score_points: row.score_points,
                dimension: row.dimension,
                priority: row.priority
            })
            CREATE (dt)-[:HAS_ROW]->(dr)
            RETURN count(dr) AS created
        """, rows=new_rows)
        created = result.single()["created"]
        print(f"Created {created} new D16 rows")

        # Update the table description
        session.run("""
            MATCH (dt:SYS_DecisionTable {table_id: 'D16_SCORE_place_federation'})
            SET dt.description = 'Component scoring rubric for Place nodes. 9 rules, max 100 points. ' +
                'Rebalanced 2026-03-08 based on geographic property survey (264 Wikidata entities, ' +
                '25 classes). Added: GeoNames (+10), TGN (+5), library authority (+10), OSM (+5), ' +
                'instance_of class (+5). Temporal bypass: physical features (river, mountain, lake, ' +
                'sea, peninsula, valley, continent) skip temporal check — always in scope if spatially relevant.',
                dt.updated = date('2026-03-08'),
                dt.note = 'Atemporal bypass classes: river (Q4022), mountain (Q8502), lake (Q23397), ' +
                    'sea (Q165), peninsula (Q34763), valley (Q39816), continent (Q5107), waterfall (Q34038), ' +
                    'island (Q23442). These have 0% temporal coverage in survey — no P571/P576. ' +
                    'Scoring still applies but D5 temporal_overlap should skip for these instance_of classes.'
            RETURN dt.table_id AS tid
        """)
        print("Updated D16 description and note")

        # Verify
        result = session.run("""
            MATCH (dt:SYS_DecisionTable {table_id: 'D16_SCORE_place_federation'})-[:HAS_ROW]->(r:SYS_DecisionRow)
            RETURN r.row_id AS rid, r.conditions AS conds, r.score_points AS pts, r.dimension AS dim
            ORDER BY r.priority
        """)
        print("\n-- New D16 scoring rules --")
        total_max = 0
        for r in result:
            pts = r["pts"]
            total_max += pts
            print(f"  {r['rid']:25s}  +{pts:2d}  {r['dim']:25s}  {r['conds']}")
        print(f"\n  Max possible score: {total_max}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
