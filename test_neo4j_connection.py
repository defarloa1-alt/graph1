#!/usr/bin/env python3
"""Quick test of Neo4j connection and entity count"""

from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

try:
    with driver.session() as session:
        # Test 1: Total entities
        result = session.run("MATCH (n:Entity) RETURN count(n) as total")
        total = result.single()['total']
        print(f"✅ Connected! Total entities: {total}")
        
        # Test 2: Entity types breakdown
        result = session.run("""
            MATCH (n:Entity)
            RETURN n.entity_type as type, count(n) as count
            ORDER BY count DESC
        """)
        
        print("\nEntity types:")
        for record in result:
            print(f"  {record['type']}: {record['count']}")
        
        # Test 3: Sample entity
        result = session.run("""
            MATCH (n:Entity {qid: 'Q17167'})
            RETURN n.label as label, n.entity_type as type, n.entity_cipher as cipher
        """)
        
        if result.peek():
            record = result.single()
            print(f"\nSeed entity (Q17167):")
            print(f"  Label: {record['label']}")
            print(f"  Type: {record['type']}")
            print(f"  Cipher: {record['cipher']}")
        else:
            print("\n⚠️  Roman Republic (Q17167) not found")

finally:
    driver.close()
