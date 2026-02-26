#!/usr/bin/env python3
"""
Remove Wikimedia category entities and their edges from the graph.

Category entities (label STARTS WITH 'Category:') are Wikipedia's filing system,
not domain entities. They inflate counts and add noise (e.g. P971 edges).

Usage:
    python scripts/neo4j/category_cleanup.py --dry-run   # Report only
    python scripts/neo4j/category_cleanup.py             # Delete category nodes and edges
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


def main():
    parser = argparse.ArgumentParser(description="Remove Wikimedia category entities")
    parser.add_argument("--dry-run", action="store_true", help="Report only, no deletes")
    args = parser.parse_args()

    if not NEO4J_PASSWORD:
        print("Error: NEO4J_PASSWORD not set.")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Count
        r = session.run("""
            MATCH (e:Entity)
            WHERE e.label STARTS WITH 'Category:'
            RETURN count(e) AS n
        """)
        count = r.single()["n"]

        if count == 0:
            print("No category entities found.")
            driver.close()
            return

        print(f"Category entities to remove: {count:,}")

        if args.dry_run:
            # Sample
            r = session.run("""
                MATCH (e:Entity)
                WHERE e.label STARTS WITH 'Category:'
                RETURN e.qid, e.label
                LIMIT 5
            """)
            print("Sample:")
            for row in r:
                print(f"  {row['e.qid']}: {row['e.label'][:60]}...")
            print("\nRun without --dry-run to delete.")
            driver.close()
            return

        # Delete edges first, then nodes
        r = session.run("""
            MATCH (e:Entity)-[r]->()
            WHERE e.label STARTS WITH 'Category:'
            WITH r LIMIT 10000
            DELETE r
            RETURN count(r) AS deleted
        """)
        # Neo4j doesn't return count from DELETE easily; use DETACH DELETE
        session.run("""
            MATCH (e:Entity)
            WHERE e.label STARTS WITH 'Category:'
            DETACH DELETE e
        """)
        print(f"Deleted {count:,} category entities and their edges.")

    driver.close()


if __name__ == "__main__":
    main()
