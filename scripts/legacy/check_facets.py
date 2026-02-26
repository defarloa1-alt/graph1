#!/usr/bin/env python3
"""Check facet nodes"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    # Check Facet nodes
    result = session.run("MATCH (f:Facet) RETURN count(f) AS count")
    facet_count = result.single()['count']
    print(f"Facet nodes: {facet_count}")
    
    if facet_count > 0:
        result = session.run("MATCH (f:Facet) RETURN f.key AS key LIMIT 20")
        print("\nFacet keys:")
        for record in result:
            print(f"  - {record['key']}")
    
    # Check relationship
    result = session.run("""
        MATCH (fed:FederationRoot)-[r:HAS_FACET_REGISTRY]->(f:Facet)
        RETURN count(r) AS rel_count
    """)
    rel_count = result.single()['rel_count']
    print(f"\nHAS_FACET_REGISTRY relationships: {rel_count}")
    
    # Check FederationRoot
    result = session.run("MATCH (f:FederationRoot) RETURN count(f) AS count")
    fed_count = result.single()['count']
    print(f"FederationRoot nodes: {fed_count}")

driver.close()

