#!/usr/bin/env python3
"""Check current Neo4j schema state"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    # Check constraints
    print("=" * 60)
    print("CURRENT CONSTRAINTS:")
    print("=" * 60)
    result = session.run('SHOW CONSTRAINTS')
    for r in result:
        print(f"{r['name']}")
        print(f"  Type: {r['type']}")
        print(f"  Labels/Types: {r['labelsOrTypes']}")
        print(f"  Properties: {r['properties']}")
        print()
    
    # Check indexes
    print("=" * 60)
    print("CURRENT INDEXES:")
    print("=" * 60)
    result = session.run('SHOW INDEXES')
    for r in result:
        print(f"{r['name']}")
        print(f"  Type: {r['type']}")
        print(f"  Labels/Types: {r['labelsOrTypes']}")
        print(f"  Properties: {r['properties']}")
        print()
    
    # Check entity schema
    print("=" * 60)
    print("SAMPLE ENTITY SCHEMA:")
    print("=" * 60)
    result = session.run('''
        MATCH (n:Entity)
        RETURN n.entity_cipher as cipher,
               n.entity_type as type,
               n.qid as qid,
               n.label as label,
               n.temporal_start_year as temp_start,
               n.temporal_end_year as temp_end,
               labels(n) as all_labels
        LIMIT 5
    ''')
    for r in result:
        print(f"QID: {r['qid']}")
        print(f"  Label: {r['label']}")
        print(f"  Cipher: {r['cipher']}")
        print(f"  Type: {r['type']}")
        print(f"  Labels: {r['all_labels']}")
        print(f"  Temporal: {r['temp_start']} to {r['temp_end']}")
        print()
    
    # Check if TemporalAnchor label exists
    print("=" * 60)
    print("TEMPORAL ANCHOR CHECK:")
    print("=" * 60)
    result = session.run('MATCH (n:TemporalAnchor) RETURN count(n) as total')
    temporal_count = result.single()['total']
    print(f"Nodes with :TemporalAnchor label: {temporal_count}")

driver.close()
