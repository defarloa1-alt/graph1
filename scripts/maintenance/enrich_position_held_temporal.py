#!/usr/bin/env python3
"""
Phase 4.3: Enrich POSITION_HELD with start_year, end_year from r.year.

DPRR stores a single year on POSITION_HELD (r.year as string, e.g. "-43").
Sets r.start_year = r.end_year = toInteger(r.year) for single-year offices.
Idempotent: skips edges that already have start_year.

Usage:
  python scripts/maintenance/enrich_position_held_temporal.py           # dry-run
  python scripts/maintenance/enrich_position_held_temporal.py --execute
"""
import argparse
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase


def parse_year(val) -> int | None:
    """Parse r.year string to integer. BCE negative."""
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Enrich POSITION_HELD with start_year, end_year")
    ap.add_argument("--execute", action="store_true", help="Write to graph (default: dry-run)")
    args = ap.parse_args()

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD required")
        return 1

    driver = GraphDatabase.driver(uri, auth=(user, password))
    db = os.getenv("NEO4J_DATABASE", "neo4j")

    with driver.session(database=db) as session:
        r = session.run("""
            MATCH ()-[r:POSITION_HELD]->()
            WHERE r.year IS NOT NULL
              AND (r.start_year IS NULL OR r.end_year IS NULL)
            RETURN count(r) AS c
        """).single()
        count = r["c"] if r else 0

    print("Phase 4.3: Enrich POSITION_HELD with start_year, end_year")
    print(f"  Edges to enrich: {count}")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    if not args.execute or count == 0:
        driver.close()
        return 0

    with driver.session(database=db) as session:
        r = session.run("""
            MATCH ()-[r:POSITION_HELD]->()
            WHERE r.year IS NOT NULL
              AND (r.start_year IS NULL OR r.end_year IS NULL)
            WITH r, toInteger(r.year) AS yr
            WHERE yr IS NOT NULL
            SET r.start_year = yr, r.end_year = yr
            RETURN count(r) AS c
        """).single()
        print(f"  Enriched: {r['c'] if r else 0}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
