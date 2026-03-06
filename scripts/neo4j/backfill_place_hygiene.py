#!/usr/bin/env python3
"""
Backfill missing place_id, entity_type, authority, confidence on Place nodes.

Targets:
  1. GeoNames backbone  (1,743) — place_id, entity_type, confidence
  2. Wikidata backbone   (331)  — place_id, entity_type, authority, confidence
  3. Pleiades pre-convention (~235) — place_id
  4. Resolved stubs      (~126) — place_id, authority, confidence

Usage:
    python scripts/neo4j/backfill_place_hygiene.py --dry-run
    python scripts/neo4j/backfill_place_hygiene.py
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from neo4j import GraphDatabase

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")


STEPS = [
    {
        "name": "GeoNames backbone",
        "count_query": """
            MATCH (p:Place)
            WHERE p.node_type = 'geonames_place_backbone' AND p.place_id IS NULL
            RETURN count(p) AS cnt
        """,
        "write_query": """
            MATCH (p:Place)
            WHERE p.node_type = 'geonames_place_backbone' AND p.place_id IS NULL
            SET p.place_id = 'plc_gn_' + p.geonames_id,
                p.entity_type = 'place',
                p.confidence = 0.85
            RETURN count(p) AS updated
        """,
    },
    {
        "name": "Wikidata backbone",
        "count_query": """
            MATCH (p:Place)
            WHERE p.node_type = 'wikidata_place_backbone' AND p.place_id IS NULL
            RETURN count(p) AS cnt
        """,
        "write_query": """
            MATCH (p:Place)
            WHERE p.node_type = 'wikidata_place_backbone' AND p.place_id IS NULL
            SET p.place_id = 'plc_wd_' + p.qid,
                p.entity_type = 'place',
                p.authority = 'Wikidata',
                p.confidence = 0.85
            RETURN count(p) AS updated
        """,
    },
    {
        "name": "Pleiades (pre-convention)",
        "count_query": """
            MATCH (p:Place)
            WHERE p.pleiades_id IS NOT NULL AND p.place_id IS NULL
            RETURN count(p) AS cnt
        """,
        "write_query": """
            MATCH (p:Place)
            WHERE p.pleiades_id IS NOT NULL AND p.place_id IS NULL
            SET p.place_id = 'plc_pl_' + p.pleiades_id
            RETURN count(p) AS updated
        """,
    },
    {
        "name": "Resolved stubs (qid, no backbone)",
        "count_query": """
            MATCH (p:Place)
            WHERE p.qid IS NOT NULL AND p.pleiades_id IS NULL
              AND p.node_type IS NULL AND p.authority IS NULL
            RETURN count(p) AS cnt
        """,
        "write_query": """
            MATCH (p:Place)
            WHERE p.qid IS NOT NULL AND p.pleiades_id IS NULL
              AND p.node_type IS NULL AND p.authority IS NULL
            SET p.place_id = coalesce(p.place_id, 'plc_wd_' + p.qid),
                p.authority = 'Wikidata',
                p.confidence = coalesce(p.confidence, 0.80)
            RETURN count(p) AS updated
        """,
    },
]

VERIFY = [
    ("place_id IS NULL",    "MATCH (p:Place) WHERE p.place_id IS NULL RETURN count(p) AS cnt"),
    ("authority IS NULL",   "MATCH (p:Place) WHERE p.authority IS NULL RETURN count(p) AS cnt"),
    ("entity_type IS NULL", "MATCH (p:Place) WHERE p.entity_type IS NULL RETURN count(p) AS cnt"),
]


def main():
    parser = argparse.ArgumentParser(description="Backfill Place node hygiene properties")
    parser.add_argument("--dry-run", action="store_true", help="Report counts only, don't write")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        for step in STEPS:
            result = session.run(step["count_query"])
            cnt = result.single()["cnt"]
            if args.dry_run:
                print(f"[DRY RUN] {step['name']}: {cnt} nodes to update")
            else:
                if cnt == 0:
                    print(f"[SKIP]    {step['name']}: 0 nodes to update")
                    continue
                result = session.run(step["write_query"])
                updated = result.single()["updated"]
                print(f"[DONE]    {step['name']}: {updated} nodes updated")

        print()
        for label, query in VERIFY:
            result = session.run(query)
            cnt = result.single()["cnt"]
            status = "OK" if cnt == 0 else "REMAINING"
            print(f"[{status}]  {label}: {cnt}")

    driver.close()


if __name__ == "__main__":
    main()
