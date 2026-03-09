#!/usr/bin/env python3
"""
Remove backbone Discipline nodes that have none of: lcc, lcsh_id, fast_id, ddc.

These nodes have only GND or AAT identifiers — no major library classification.
Safe to prune: 399 nodes, 1,624 relationships (mostly SUBCLASS_OF/PART_OF).

Usage:
  python scripts/neo4j/prune_weak_disciplines.py --dry-run
  python scripts/neo4j/prune_weak_disciplines.py
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

MATCH_WEAK = """
MATCH (d:Discipline)
WHERE d.tier = 'backbone'
  AND d.lcc IS NULL
  AND d.lcsh_id IS NULL
  AND d.fast_id IS NULL
  AND d.ddc IS NULL
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Count nodes to delete, no writes")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            # Count first
            result = session.run(
                MATCH_WEAK +
                "OPTIONAL MATCH (d)-[r]-() "
                "RETURN count(DISTINCT d) AS nodes, count(r) AS rels"
            )
            row = result.single()
            print(f"Weak backbone disciplines: {row['nodes']} nodes, {row['rels']} relationships")

            if args.dry_run:
                print("Dry run — no deletions.")
                return

            # Sample a few so user can see what's being removed
            result = session.run(
                MATCH_WEAK +
                "RETURN d.qid AS qid, d.label AS label, d.gnd_id AS gnd_id, d.aat_id AS aat_id "
                "LIMIT 10"
            )
            print("\nSample nodes being deleted:")
            for r in result:
                ids = []
                if r["gnd_id"]: ids.append(f"GND:{r['gnd_id']}")
                if r["aat_id"]: ids.append(f"AAT:{r['aat_id']}")
                print(f"  {r['qid']} — {r['label']} [{', '.join(ids) or 'no IDs'}]")

            confirm = input(f"\nDelete {row['nodes']} nodes? [y/N] ")
            if confirm.strip().lower() != "y":
                print("Aborted.")
                return

            result = session.run(
                MATCH_WEAK +
                "DETACH DELETE d "
                "RETURN count(d) AS deleted"
            )
            deleted = result.single()["deleted"]
            print(f"\nDeleted {deleted} Discipline nodes.")

            # Verify
            result = session.run(
                "MATCH (d:Discipline) WHERE d.tier = 'backbone' "
                "RETURN count(d) AS remaining"
            )
            print(f"Remaining backbone disciplines: {result.single()['remaining']}")

    finally:
        driver.close()


if __name__ == "__main__":
    main()
