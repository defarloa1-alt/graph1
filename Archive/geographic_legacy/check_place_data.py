#!/usr/bin/env python3
"""Check current place data and missing properties"""
from neo4j import GraphDatabase

URI = "neo4j+s://f7b612a3.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    # Check Thalefsa specifically
    result = session.run("""
        MATCH (p:Place {pleiades_id: '295353'})
        RETURN properties(p) AS props
    """)
    
    record = result.single()
    if record:
        print("Current Thalefsa properties:")
        for key, value in record['props'].items():
            print(f"  {key}: {value}")
    
    print()
    
    # Check how many places have qid
    result = session.run("""
        MATCH (p:Place)
        RETURN 
            count(p) AS total,
            count(p.qid) AS with_qid,
            count(p.bbox) AS with_bbox
    """)
    
    stats = result.single()
    print(f"Place statistics:")
    print(f"  Total places: {stats['total']}")
    print(f"  With Wikidata QID: {stats['with_qid']}")
    print(f"  With bbox: {stats['with_bbox']}")

driver.close()

