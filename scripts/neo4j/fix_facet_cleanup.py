#!/usr/bin/env python3
"""
Fix FacetRouter display labels + normalize primary_facet to uppercase.
Delete FacetRoot convenience node.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

from neo4j import GraphDatabase


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. Set label = pattern on all FacetRouter nodes (so viewer shows the pattern)
        result = session.run("""
            MATCH (r:SYS_FacetRouter)
            SET r.label = r.pattern
            RETURN count(r) as cnt
        """)
        print(f"  FacetRouter: {result.single()['cnt']} nodes got label = pattern")

        # 2. Normalize primary_facet to uppercase (match Facet.key)
        result = session.run("""
            MATCH (r:SYS_FacetRouter)
            SET r.primary_facet = toUpper(r.primary_facet)
            RETURN count(r) as cnt
        """)
        print(f"  FacetRouter: {result.single()['cnt']} primary_facet normalized to uppercase")

        # 3. Also normalize secondary_facets if present
        result = session.run("""
            MATCH (r:SYS_FacetRouter)
            WHERE r.secondary_facets IS NOT NULL
            SET r.secondary_facets = [x IN r.secondary_facets | toUpper(x)]
            RETURN count(r) as cnt
        """)
        print(f"  FacetRouter: {result.single()['cnt']} secondary_facets normalized")

        # 4. Delete FacetRoot node and its relationships
        result = session.run("""
            MATCH (fr:FacetRoot)
            OPTIONAL MATCH (fr)-[r]-()
            DELETE r, fr
            RETURN count(fr) as nodes_deleted
        """)
        print(f"  FacetRoot: {result.single()['nodes_deleted']} node(s) deleted")

        # Verify
        print("\n-- FacetRouter sample --")
        result = session.run("""
            MATCH (r:SYS_FacetRouter)
            RETURN r.label AS label, r.primary_facet AS pf, r.match_type AS mt
            ORDER BY r.primary_facet, r.label
            LIMIT 10
        """)
        for r in result:
            print(f"  {r['label']:30s} primary={r['pf']:15s} match={r['mt']}")

        print("\n-- FacetRoot check --")
        result = session.run("MATCH (fr:FacetRoot) RETURN count(fr) as cnt")
        print(f"  FacetRoot nodes remaining: {result.single()['cnt']}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
