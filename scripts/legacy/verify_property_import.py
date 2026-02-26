#!/usr/bin/env python3
"""Quick verification of property mapping import"""

from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    # Total count
    result = session.run("MATCH (pm:PropertyMapping) RETURN count(pm) as total")
    total = result.single()['total']
    print(f"Total PropertyMapping nodes: {total}")
    print()
    
    # By resolution method
    result = session.run("""
        MATCH (pm:PropertyMapping)
        WHERE pm.resolved_by IS NOT NULL
        RETURN pm.resolved_by as method, count(pm) as count
        ORDER BY count DESC
    """)
    print("By resolution method:")
    for rec in result:
        print(f"  {rec['method']:20} {rec['count']:>4}")
    print()
    
    # By facet
    result = session.run("""
        MATCH (pm:PropertyMapping)
        RETURN pm.primary_facet as facet, count(pm) as count
        ORDER BY count DESC
        LIMIT 10
    """)
    print("Top 10 facets:")
    for rec in result:
        print(f"  {rec['facet']:20} {rec['count']:>4}")
    print()
    
    # Sample properties
    result = session.run("""
        MATCH (pm:PropertyMapping)
        WHERE pm.resolved_by = 'claude'
        RETURN pm.property_id, pm.property_label, pm.primary_facet, pm.confidence
        ORDER BY pm.confidence DESC
        LIMIT 10
    """)
    print("Sample Claude-resolved properties:")
    for rec in result:
        print(f"  {rec['property_id']:6} {rec['property_label'][:35]:35} -> {rec['primary_facet']:15} ({rec['confidence']:.2f})")
    print()
    
    # Facet relationships
    result = session.run("""
        MATCH (pm:PropertyMapping)-[:HAS_PRIMARY_FACET]->(f:Facet)
        RETURN count(pm) as linked
    """)
    linked = result.single()['linked']
    print(f"Properties linked to Facets: {linked}")

driver.close()
print()
print("Verification complete!")
