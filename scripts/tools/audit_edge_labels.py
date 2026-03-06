#!/usr/bin/env python3
"""
Audit PID edges — report which have r.label (human-readable) vs missing.

Credentials: .env (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD) via config_loader.

Run: python -m scripts.tools.audit_edge_labels
"""
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_scripts))
try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = NEO4J_USERNAME = NEO4J_PASSWORD = None

from neo4j import GraphDatabase


def main():
    if not NEO4J_PASSWORD:
        print("NEO4J_PASSWORD not set. Configure .env or config_loader.")
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))

    with driver.session() as session:
        # True PID rel types only: P31, P569, WIKIDATA_P6379 (not POSITION_HELD, etc.)
        r = session.run("""
            MATCH ()-[r]->()
            WHERE type(r) =~ '^P[0-9]+$' OR type(r) =~ '^WIKIDATA_P[0-9]+$'
            WITH type(r) AS rel_type,
                 count(r) AS total,
                 sum(CASE WHEN r.label IS NULL OR r.label = '' THEN 1 ELSE 0 END) AS missing_label
            WHERE total > 0
            RETURN rel_type, total, missing_label
            ORDER BY missing_label DESC, total DESC
        """)
        rows = list(r)

    driver.close()

    if not rows:
        print("No PID-like relationship types found.")
        return 0

    total_edges = sum(x["total"] for x in rows)
    total_missing = sum(x["missing_label"] for x in rows)

    print("=" * 60)
    print("EDGE LABEL AUDIT — PID relationships")
    print("=" * 60)
    print(f"Total PID edges: {total_edges:,}")
    print(f"Missing r.label: {total_missing:,}")
    print()

    if total_missing > 0:
        print("Rel types with missing labels (top 20):")
        print("-" * 40)
        for row in rows[:20]:
            rt, total, missing = row["rel_type"], row["total"], row["missing_label"]
            status = "OK" if missing == 0 else f"MISSING {missing:,}"
            print(f"  {rt}  total={total:,}  {status}")
        print()
        print("Fix: run canonicalize_edges.py then enrich_edge_labels.py")
        return 1
    else:
        print("All PID edges have r.label set.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
