#!/usr/bin/env python3
"""Fix Place constraint issue"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

print("=== CHECKING PLACE CONSTRAINTS ===")
with driver.session() as session:
    # Show all constraints
    result = session.run("SHOW CONSTRAINTS YIELD name, type, labelsOrTypes, properties WHERE 'Place' IN labelsOrTypes RETURN name, type, properties")
    
    place_constraints = list(result)
    
    if place_constraints:
        print("\nPlace constraints found:")
        for record in place_constraints:
            print(f"  {record['name']}: {record['type']} on {record['properties']}")
            
            # Drop the qid constraint if it exists
            if 'qid' in str(record['properties']):
                print(f"\n  Dropping problematic constraint: {record['name']}")
                try:
                    session.run(f"DROP CONSTRAINT {record['name']} IF EXISTS")
                    print(f"  ✓ Dropped {record['name']}")
                except Exception as e:
                    print(f"  Error: {e}")
    else:
        print("No Place constraints found")

    print("\n=== REMAINING CONSTRAINTS ===")
    result = session.run("SHOW CONSTRAINTS WHERE 'Place' IN labelsOrTypes RETURN name")
    remaining = list(result)
    if remaining:
        for record in remaining:
            print(f"  - {record['name']}")
    else:
        print("  All Place qid constraints removed")

driver.close()
print("\n✓ Constraint fix complete")

