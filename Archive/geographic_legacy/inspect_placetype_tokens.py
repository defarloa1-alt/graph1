#!/usr/bin/env python3
"""Inspect PlaceTypeTokenMap nodes"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    # Get all PlaceTypeTokenMap nodes
    result = session.run("""
        MATCH (n:PlaceTypeTokenMap)
        RETURN n
        LIMIT 20
    """)
    
    print("PlaceTypeTokenMap nodes (first 20):")
    print("=" * 80)
    
    for i, record in enumerate(result, 1):
        node = record['n']
        print(f"\n{i}. Node properties:")
        for key, value in node.items():
            print(f"   {key}: {value}")
    
    # Count total
    result = session.run("MATCH (n:PlaceTypeTokenMap) RETURN count(n) AS total")
    total = result.single()['total']
    print(f"\nTotal PlaceTypeTokenMap nodes: {total}")
    
    # Check relationships
    result = session.run("""
        MATCH (n:PlaceTypeTokenMap)-[r]->(m)
        RETURN type(r) AS rel_type, labels(m) AS target_labels, count(*) AS count
    """)
    
    print("\nRelationships FROM PlaceTypeTokenMap:")
    for record in result:
        print(f"  -{record['rel_type']}-> {record['target_labels']}: {record['count']}")
    
    # Check incoming
    result = session.run("""
        MATCH (m)-[r]->(n:PlaceTypeTokenMap)
        RETURN type(r) AS rel_type, labels(m) AS source_labels, count(*) AS count
    """)
    
    print("\nRelationships TO PlaceTypeTokenMap:")
    for record in result:
        print(f"  {record['source_labels']} -{record['rel_type']}->: {record['count']}")

driver.close()

