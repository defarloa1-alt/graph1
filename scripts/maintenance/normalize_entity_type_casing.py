#!/usr/bin/env python3
"""
Normalize entity_type Casing in Neo4j

One-time pass: lowercase entity_type (e.g. "concept") -> uppercase ("CONCEPT").
Fixes inconsistency where cluster_assignment wrote "concept" and other paths wrote "CONCEPT".

Usage:
    python scripts/maintenance/normalize_entity_type_casing.py --dry-run
    python scripts/maintenance/normalize_entity_type_casing.py
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
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", os.environ.get("NEO4J_USER", "neo4j"))
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")


def main():
    parser = argparse.ArgumentParser(description="Normalize entity_type casing to uppercase")
    parser.add_argument("--dry-run", action="store_true", help="Report only, no writes")
    args = parser.parse_args()

    if not NEO4J_PASSWORD:
        print("Error: NEO4J_PASSWORD not set.")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Count entities with lowercase entity_type
        r = session.run("""
            MATCH (e:Entity)
            WHERE e.entity_type IS NOT NULL
              AND e.entity_type <> toUpper(e.entity_type)
            RETURN e.entity_type as t, count(*) as c
            ORDER BY c DESC
        """)
        to_fix = [(row["t"], row["c"]) for row in r]
        total = sum(c for _, c in to_fix)

        if not to_fix:
            print("No entities need normalization. All entity_type values are already uppercase.")
            driver.close()
            return

        print("Entities to normalize (lowercase -> UPPERCASE):")
        for t, c in to_fix:
            print(f"  {t} -> {t.upper()}: {c:,}")
        print(f"  Total: {total:,}")
        print()

        if args.dry_run:
            print("[DRY RUN] No changes made.")
            driver.close()
            return

        # Normalize
        result = session.run("""
            MATCH (e:Entity)
            WHERE e.entity_type IS NOT NULL
              AND e.entity_type <> toUpper(e.entity_type)
            SET e.entity_type = toUpper(e.entity_type)
            RETURN count(e) as updated
        """)
        updated = result.single()["updated"]
        print(f"Normalized {updated:,} entities.")
        driver.close()


if __name__ == "__main__":
    main()
