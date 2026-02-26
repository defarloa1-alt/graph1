#!/usr/bin/env python3
"""
Category contamination diagnostics.

Runs the queries from RELATIONSHIP_TYPE_CONVENTIONS.md and outputs results.
"""

import json
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
    if not NEO4J_PASSWORD:
        print("Error: NEO4J_PASSWORD not set.")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    out_dir = ROOT / "output" / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}

    with driver.session() as session:
        # Count category entities
        r = session.run("""
            MATCH (e:Entity)
            WHERE e.label STARTS WITH 'Category:'
            RETURN count(e) AS category_entity_count
        """)
        results["category_entity_count"] = r.single()["category_entity_count"]

        # Edge contamination from category sources
        r = session.run("""
            MATCH (e:Entity)-[r]->(b)
            WHERE e.label STARTS WITH 'Category:'
            RETURN type(r) AS edge_type, count(r) AS count
            ORDER BY count DESC
        """)
        results["edge_contamination"] = [{"edge_type": row["edge_type"], "count": row["count"]} for row in r]

    driver.close()

    out_path = out_dir / "category_diagnostics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("Category diagnostics:")
    print(f"  Category entities: {results['category_entity_count']:,}")
    print(f"  Edge types from Category sources: {len(results['edge_contamination'])}")
    for item in results["edge_contamination"][:10]:
        print(f"    {item['edge_type']}: {item['count']:,}")
    print(f"\nOutput: {out_path}")


if __name__ == "__main__":
    main()
