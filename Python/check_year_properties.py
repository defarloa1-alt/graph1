#!/usr/bin/env python3
"""Check what properties Year nodes actually have"""

from neo4j import GraphDatabase

uri = 'bolt://127.0.0.1:7687'
username = 'neo4j'
password = 'Chrystallum'

driver = GraphDatabase.driver(uri, auth=(username, password))

try:
    with driver.session() as session:
        # Get sample Year node with all properties
        result = session.run("""
            MATCH (y:Year)
            RETURN y, keys(y) as props
            LIMIT 5
        """)
        
        print("=" * 70)
        print("YEAR NODE PROPERTIES")
        print("=" * 70)
        
        for i, record in enumerate(result, 1):
            year_node = record['y']
            props = record['props']
            
            print(f"\nYear node {i}:")
            print(f"  Properties: {props}")
            for prop in props:
                value = year_node.get(prop)
                print(f"    {prop}: {value}")

finally:
    driver.close()

