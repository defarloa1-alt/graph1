#!/usr/bin/env python3
"""
Tag Place nodes with place_scope = 'v1_core' or 'deferred'.

v1_core: settlements, villas, forts, stations, colonies, regions, provinces
deferred: everything else (rivers, mountains, temples, roads, tombs, etc.)

Usage:
    python scripts/neo4j/tag_place_scope.py --dry-run
    python scripts/neo4j/tag_place_scope.py
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

# place_type substrings that qualify as v1_core
V1_CORE_KEYWORDS = [
    'settlement', 'villa', 'fort', 'station', 'colony',
    'region', 'province', 'camp', 'city', 'town', 'village',
]

STEPS = [
    {
        "name": "Tag v1_core (settlements, villas, forts, stations, colonies, regions)",
        "count_query": """
            MATCH (p:Place)
            WHERE p.place_type IS NOT NULL
              AND (p.place_type CONTAINS 'settlement'
                OR p.place_type CONTAINS 'villa'
                OR p.place_type CONTAINS 'fort'
                OR p.place_type CONTAINS 'station'
                OR p.place_type CONTAINS 'colony'
                OR p.place_type CONTAINS 'region'
                OR p.place_type CONTAINS 'province'
                OR p.place_type CONTAINS 'camp'
                OR p.place_type CONTAINS 'city'
                OR p.place_type CONTAINS 'town'
                OR p.place_type CONTAINS 'village')
            RETURN count(p) AS cnt
        """,
        "write_query": """
            MATCH (p:Place)
            WHERE p.place_type IS NOT NULL
              AND (p.place_type CONTAINS 'settlement'
                OR p.place_type CONTAINS 'villa'
                OR p.place_type CONTAINS 'fort'
                OR p.place_type CONTAINS 'station'
                OR p.place_type CONTAINS 'colony'
                OR p.place_type CONTAINS 'region'
                OR p.place_type CONTAINS 'province'
                OR p.place_type CONTAINS 'camp'
                OR p.place_type CONTAINS 'city'
                OR p.place_type CONTAINS 'town'
                OR p.place_type CONTAINS 'village')
            SET p.place_scope = 'v1_core'
            RETURN count(p) AS updated
        """,
    },
    {
        "name": "Tag deferred (everything else with a place_type)",
        "count_query": """
            MATCH (p:Place)
            WHERE p.place_type IS NOT NULL
              AND p.place_scope IS NULL
            RETURN count(p) AS cnt
        """,
        "write_query": """
            MATCH (p:Place)
            WHERE p.place_type IS NOT NULL
              AND p.place_scope IS NULL
            SET p.place_scope = 'deferred'
            RETURN count(p) AS updated
        """,
    },
    {
        "name": "Tag deferred (no place_type at all)",
        "count_query": """
            MATCH (p:Place)
            WHERE p.place_type IS NULL
              AND p.place_scope IS NULL
            RETURN count(p) AS cnt
        """,
        "write_query": """
            MATCH (p:Place)
            WHERE p.place_type IS NULL
              AND p.place_scope IS NULL
            SET p.place_scope = 'deferred'
            RETURN count(p) AS updated
        """,
    },
]


def main():
    parser = argparse.ArgumentParser(description="Tag Place nodes with place_scope")
    parser.add_argument("--dry-run", action="store_true", help="Report counts only")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        for step in STEPS:
            result = session.run(step["count_query"])
            cnt = result.single()["cnt"]
            if args.dry_run:
                print(f"[DRY RUN] {step['name']}: {cnt} nodes")
            else:
                if cnt == 0:
                    print(f"[SKIP]    {step['name']}: 0 nodes")
                    continue
                result = session.run(step["write_query"])
                updated = result.single()["updated"]
                print(f"[DONE]    {step['name']}: {updated} nodes tagged")

        print()
        result = session.run("MATCH (p:Place) RETURN p.place_scope, count(p) AS cnt ORDER BY cnt DESC")
        for record in result:
            print(f"  {record['p.place_scope']}: {record['cnt']}")

    driver.close()


if __name__ == "__main__":
    main()
