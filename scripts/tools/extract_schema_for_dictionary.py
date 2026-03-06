#!/usr/bin/env python3
"""
Extract schema from Neo4j for data dictionary: node labels, relationship types,
counts, and sample properties including source/creator hints.
"""
import json
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
        print("NEO4J_PASSWORD not set. Use .env")
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))

    out = {"node_labels": [], "relationship_types": []}

    with driver.session() as session:
        # Node labels with counts
        r = session.run("CALL db.labels() YIELD label RETURN label ORDER BY label")
        labels = [row["label"] for row in r]

        for lbl in labels:
            # Count
            c = session.run(f"MATCH (n:`{lbl}`) RETURN count(n) AS c").single()["c"]
            # Sample properties (including source, imported_at, etc.)
            r2 = session.run(f"""
                MATCH (n:`{lbl}`)
                WITH n LIMIT 100
                UNWIND keys(n) AS k
                WITH k, count(*) AS cnt
                RETURN collect({{key: k, count: cnt}}) AS props
            """)
            row = r2.single()
            props = row["props"] if row else []
            # Source hints from sample
            r3 = session.run(f"""
                MATCH (n:`{lbl}`)
                WHERE n.source IS NOT NULL OR n.imported_at IS NOT NULL OR n.source_script IS NOT NULL
                RETURN n.source AS source, n.imported_at AS imported_at, n.source_script AS source_script
                LIMIT 5
            """)
            sources = [dict(s) for s in r3]
            out["node_labels"].append({
                "label": lbl,
                "count": c,
                "property_keys": sorted(set(p["key"] for p in props)),
                "source_hints": sources[:3] if sources else None,
            })

        # Relationship types with counts
        r = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType")
        rel_types = [row["relationshipType"] for row in r]

        for rt in rel_types:
            cypher_rt = f"`{rt}`" if " " in rt or "-" in rt else rt
            c = session.run(f"MATCH ()-[r:{cypher_rt}]->() RETURN count(r) AS c").single()["c"]
            r2 = session.run(f"""
                MATCH ()-[r:{cypher_rt}]->()
                WITH r LIMIT 100
                UNWIND keys(r) AS k
                WITH k, count(*) AS cnt
                RETURN collect({{key: k, count: cnt}}) AS props
            """)
            row = r2.single()
            props = row["props"] if row else []
            r3 = session.run(f"""
                MATCH ()-[r:{cypher_rt}]->()
                WHERE r.source IS NOT NULL OR r.imported_at IS NOT NULL
                RETURN r.source AS source, r.imported_at AS imported_at
                LIMIT 3
            """)
            sources = [dict(s) for s in r3]
            out["relationship_types"].append({
                "type": rt,
                "count": c,
                "property_keys": sorted(set(p["key"] for p in props)),
                "source_hints": sources[:3] if sources else None,
            })

    driver.close()

    out_path = Path(__file__).resolve().parents[2] / "output" / "schema_extract.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
