#!/usr/bin/env python3
"""Test Neo4j Aura connection with real password"""
from neo4j import GraphDatabase

# Aura connection details
URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"
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
        
        # Check node count
        result = session.run("MATCH (n) RETURN count(n) AS node_count")
        count = result.single()["node_count"]
        print(f"Current node count: {count}")
        
        # Check relationship count
        result = session.run("MATCH ()-[r]->() RETURN count(r) AS rel_count")
        rel_count = result.single()["rel_count"]
        print(f"Current relationship count: {rel_count}")
        
        if count == 0:
            print("\n*** Database is EMPTY - perfect for fresh rebuild! ***")
        else:
            print(f"\n*** Database has {count} nodes, {rel_count} relationships ***")
            print("We can either clear it or build on top of existing data.")
    
    driver.close()
    print("\nConnection VERIFIED - ready to proceed with rebuild!")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("\nConnection failed.")
    

