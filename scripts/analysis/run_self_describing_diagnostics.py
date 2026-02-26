#!/usr/bin/env python3
"""
Run self-describing subgraph diagnostic queries and print results.

Uses NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD from .env.

Usage:
    python scripts/analysis/run_self_describing_diagnostics.py
    python scripts/analysis/run_self_describing_diagnostics.py --output output/analysis/self_describing_diagnostics.txt
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

QUERIES = [
    ("1. Chrystallum-connected labels", """
        MATCH (sys:Chrystallum)-[*..4]->(n)
        RETURN labels(n) AS label, count(n) AS count
        ORDER BY count DESC
    """),
    ("2. PropertyMapping connection to system", """
        MATCH (n:PropertyMapping) 
        OPTIONAL MATCH (sys:Chrystallum)-[*..10]->(n)
        RETURN count(n) AS total_pm, count(sys) AS connected_to_system
    """),
    ("3. GeoCoverageCandidate - any direction", """
        MATCH (gcc:GeoCoverageCandidate)-[r]-(n)
        RETURN type(r) AS rel, labels(n) AS target, count(*) AS cnt
        ORDER BY cnt DESC
    """),
    ("4. KnowledgeDomain connections", """
        MATCH (kd:KnowledgeDomain)-[r]-(n)
        RETURN type(r) AS rel, labels(n) AS other, count(*) AS cnt
        ORDER BY cnt DESC
    """),
    ("5. FacetedEntity edges (confirm orphaned)", """
        MATCH (n:FacetedEntity)
        OPTIONAL MATCH (n)-[r]-()
        RETURN count(n) AS total, count(r) AS with_edges
    """),
    ("6. PropertyMapping sample", """
        MATCH (pm:PropertyMapping)-[:HAS_PRIMARY_FACET]->(f:Facet)
        RETURN pm.property_id AS property, f.key AS primary_facet
        LIMIT 10
    """),
    ("7a. Policy contents", """
        MATCH (n:Policy) RETURN properties(n) AS props LIMIT 5
    """),
    ("7b. Threshold contents", """
        MATCH (n:Threshold) RETURN properties(n) AS props LIMIT 5
    """),
    ("8. Place nodes edge count", """
        MATCH (p:Place)
        OPTIONAL MATCH (p)-[r]-()
        RETURN count(p) AS total_place, count(r) AS total_edges
    """),
]


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", help="Write results to file")
    args = parser.parse_args()

    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("Error: Set NEO4J_URI and NEO4J_PASSWORD in .env")
        sys.exit(1)

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("Error: pip install neo4j")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    out_lines = []
    def log(s=""):
        out_lines.append(s)
        print(s)

    try:
        with driver.session() as session:
            for name, query in QUERIES:
                log(f"\n{'='*60}")
                log(name)
                log("=" * 60)
                try:
                    result = session.run(query.strip())
                    rows = list(result)
                    if not rows:
                        log("  (no results)")
                        continue
                    for i, row in enumerate(rows[:20]):
                        log(f"  {dict(row)}")
                    if len(rows) > 20:
                        log(f"  ... and {len(rows) - 20} more")
                except Exception as e:
                    log(f"  ERROR: {e}")
    finally:
        driver.close()

    log("\nDone.")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(out_lines), encoding="utf-8")
        print(f"\nResults written: {out_path}")


if __name__ == "__main__":
    main()
