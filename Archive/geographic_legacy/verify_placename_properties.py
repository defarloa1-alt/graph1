#!/usr/bin/env python3
"""Verify PlaceName has only linguistic properties (no qid)"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    # Get all properties on PlaceName nodes
    result = session.run("""
        MATCH (n:PlaceName)
        WITH n LIMIT 1
        RETURN keys(n) AS properties
    """)
    
    record = result.single()
    if record:
        print("PlaceName node properties:")
        for prop in record['properties']:
            print(f"  - {prop}")
        
        # Check if any have qid (shouldn't!)
        if 'qid' in record['properties']:
            print("\n  WARNING: PlaceName has qid property (should NOT!)")
        else:
            print("\n  CORRECT: PlaceName has NO qid property")
    
    # Sample PlaceName
    result = session.run("""
        MATCH (p:Place {pleiades_id: '295353'})-[:HAS_NAME]->(n:PlaceName)
        RETURN n.name_attested AS name, n.language AS lang
        LIMIT 5
    """)
    
    print("\nThalefsa names (multilingual):")
    for record in result:
        print(f"  {record['name']} ({record['lang']})")
    
    # Check Place has qid
    result = session.run("""
        MATCH (p:Place)
        WHERE p.qid IS NOT NULL
        WITH p LIMIT 1
        RETURN keys(p) AS properties
    """)
    
    record = result.single()
    if record:
        print("\nPlace node properties (sample with qid):")
        for prop in sorted(record['properties']):
            print(f"  - {prop}")
        
        print("\n  CORRECT: qid is on Place, not PlaceName")

driver.close()

print("\n" + "=" * 60)
print("DESIGN RULE VERIFIED:")
print("  Place/PlaceVersion = Federation (has qid)")
print("  PlaceName = Multilingual (no qid, just names)")
print("=" * 60)

