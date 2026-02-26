#!/usr/bin/env python3
"""Test Neo4j Aura connection"""
from neo4j import GraphDatabase

# Aura connection details
URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "Chrystallum"
DATABASE = "neo4j"

print("Testing connection to Neo4j Aura...")
print(f"  URI: {URI}")
print(f"  Username: {USERNAME}")
print(f"  Database: {DATABASE}")
print()

try:
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    driver.verify_connectivity()
    print("SUCCESS: Connected to Aura instance!")
    
    # Quick health check
    with driver.session(database=DATABASE) as session:
        result = session.run("RETURN 1 AS test")
        record = result.single()
        print(f"Query test: {record['test']}")
        
        # Check if database is empty
        result = session.run("MATCH (n) RETURN count(n) AS node_count")
        count = result.single()["node_count"]
        print(f"Current node count: {count}")
        
        if count == 0:
            print("✓ Database is empty - ready for fresh rebuild!")
        else:
            print(f"⚠ Database has {count} nodes - may need to clear first")
    
    driver.close()
    print("\nConnection verified - ready to rebuild!")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("\nConnection failed. Check:")
    print("  1. Password is correct")
    print("  2. Instance is running in Aura console")
    print("  3. Network/firewall allows connection")

