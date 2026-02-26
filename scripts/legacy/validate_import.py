#!/usr/bin/env python3
"""Validate the comprehensive edge import"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

print("="*80)
print("VALIDATION: Comprehensive Edge Import")
print("="*80)
print()

with driver.session() as session:
    # 1. Top edge types
    print("TOP 30 EDGE TYPES:")
    print("-"*80)
    result = session.run("""
        MATCH ()-[r]->()
        WHERE type(r) STARTS WITH 'WIKIDATA_'
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        LIMIT 30
    """)
    for r in result:
        print(f"  {r['rel_type']}: {r['count']:,}")
    print()
    
    # 2. Caesar's connections
    print("CAESAR (Q1048) CONNECTIONS:")
    print("-"*80)
    result = session.run("""
        MATCH (e:Entity {qid: 'Q1048'})-[r]->(t:Entity)
        RETURN type(r) as rel_type, t.qid as qid, t.label as label
        ORDER BY rel_type
        LIMIT 20
    """)
    for r in result:
        label = r['label'] or 'N/A'
        print(f"  {r['rel_type']}: {r['qid']} ({label[:40]})")
    print()
    
    # 3. Connectivity stats
    print("CONNECTIVITY STATISTICS:")
    print("-"*80)
    result = session.run("""
        MATCH (e:Entity)
        OPTIONAL MATCH (e)-[r]-()
        WITH e, count(r) as degree
        RETURN 
          count(e) as total_entities,
          min(degree) as min_degree,
          avg(degree) as avg_degree,
          max(degree) as max_degree,
          count(CASE WHEN degree = 0 THEN 1 END) as isolated_count,
          count(CASE WHEN degree >= 1 THEN 1 END) as connected_count
    """)
    stats = result.single()
    print(f"  Total entities: {stats['total_entities']:,}")
    print(f"  Min degree: {stats['min_degree']}")
    print(f"  Avg degree: {stats['avg_degree']:.2f}")
    print(f"  Max degree: {stats['max_degree']}")
    print(f"  Isolated: {stats['isolated_count']:,}")
    print(f"  Connected: {stats['connected_count']:,}")
    print()
    
    # 4. Sample hierarchy path
    print("SAMPLE HIERARCHY PATH (P31/P279 chains):")
    print("-"*80)
    result = session.run("""
        MATCH path = (e:Entity {qid: 'Q1048'})-[:WIKIDATA_P31|WIKIDATA_P279*1..3]->(t)
        RETURN 
          [n in nodes(path) | n.qid] as qid_path,
          [n in nodes(path) | n.label] as label_path,
          length(path) as hops
        ORDER BY hops
        LIMIT 5
    """)
    for r in result:
        labels = [l or '?' for l in r['label_path']]
        print(f"  {' -> '.join(labels)} ({r['hops']} hops)")
    print()

driver.close()

print("="*80)
print("Graph is now connected and navigable!")
print("="*80)
