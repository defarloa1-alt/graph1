#!/usr/bin/env python3
"""Direct database check"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Check all available databases
print("=== AVAILABLE DATABASES ===")
with driver.session() as session:
    result = session.run("SHOW DATABASES YIELD name, currentStatus RETURN name, currentStatus")
    for record in result:
        print(f"  {record['name']}: {record['currentStatus']}")

print()

# Check default database
print("=== CHECKING DEFAULT DATABASE (neo4j) ===")
with driver.session(database="neo4j") as session:
    result = session.run("MATCH (n) RETURN labels(n) AS labels, count(n) AS count")
    for record in result:
        print(f"  {record['labels']}: {record['count']}")

driver.close()

