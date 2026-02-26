#!/usr/bin/env python3
"""
Self-describing subgraph cleanup — remove orphaned and staging nodes.

Advisor-approved deletions (2026-02-25):
- Period (1,077) — Option B: remove pre-imported PeriodO nodes; temporal_anchor model per perplexity-on-periods.md
- GeoCoverageCandidate (357) — staging join; delete with Period/PeriodCandidate
- PeriodCandidate (1,077) — staging complete
- PlaceTypeTokenMap (212) — pipeline lookup table, confirmed safe
- FacetedEntity (360) — orphaned, 0 edges

Expected total: ~3,083 nodes. PeriodO stays as federation for on-demand lookup; no pre-import.

Usage:
    python scripts/neo4j/self_describing_subgraph_cleanup.py --dry-run   # Report only
    python scripts/neo4j/self_describing_subgraph_cleanup.py             # Execute deletes
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

# Order: Period first (removes HAS_GEO_COVERAGE, BROADER_THAN, etc.), then staging, then orphaned
TARGETS = [
    ("Period", "Option B: remove pre-imported PeriodO; temporal_anchor model"),
    ("GeoCoverageCandidate", "Staging join; delete with Period/PeriodCandidate"),
    ("PeriodCandidate", "Staging complete"),
    ("PlaceTypeTokenMap", "Pipeline lookup table"),
    ("FacetedEntity", "Orphaned, 0 edges"),
]


def main():
    parser = argparse.ArgumentParser(
        description="Remove orphaned and staging nodes from self-describing subgraph"
    )
    parser.add_argument("--dry-run", action="store_true", help="Report only, no deletes")
    args = parser.parse_args()

    if not NEO4J_PASSWORD:
        print("Error: NEO4J_PASSWORD not set.")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        total_deleted = 0
        dry_run_total = 0

        for label, reason in TARGETS:
            r = session.run(
                f"MATCH (n:{label}) RETURN count(n) AS n",
            )
            count = r.single()["n"]

            if count == 0:
                print(f"  {label}: 0 (skip)")
                continue

            print(f"  {label}: {count:,} - {reason}")

            if args.dry_run:
                dry_run_total += count
                continue

            session.run(f"MATCH (n:{label}) DETACH DELETE n")
            remaining = session.run(f"MATCH (n:{label}) RETURN count(n) AS r").single()["r"]
            if remaining == 0:
                total_deleted += count
                print(f"    -> Deleted {count:,}")
            else:
                print(f"    -> WARNING: {remaining} remaining after delete")

        if args.dry_run:
            print(f"\nExpected total: {dry_run_total:,} nodes")
            print("Run without --dry-run to execute deletes.")
        else:
            print(f"\nTotal nodes removed: {total_deleted:,}")

    driver.close()


if __name__ == "__main__":
    main()
