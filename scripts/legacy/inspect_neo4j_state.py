#!/usr/bin/env python3
"""Inspect current Neo4j state - nodes and relationships"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

print("="*80)
print("NEO4J CURRENT STATE INSPECTION")
print("="*80)
print()

with driver.session() as session:
    # Node count
    result = session.run("MATCH (n:Entity) RETURN count(n) as total")
    entity_count = result.single()['total']
    print(f"Entity nodes: {entity_count:,}")
    
    # Total relationships
    result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
    rel_count = result.single()['total']
    print(f"Total relationships: {rel_count:,}")
    print()
    
    # Relationship types
    print("RELATIONSHIP TYPES:")
    print("-"*80)
    result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType")
    rel_types = [r['relationshipType'] for r in result]
    print(f"Total types: {len(rel_types)}")
    print()
    
    # Show P-type relationships
    p_types = [rt for rt in rel_types if rt.startswith('P') and rt[1:].isdigit()]
    print(f"P-type (Wikidata PID) relationships: {len(p_types)}")
    print(f"First 20: {p_types[:20]}")
    print()
    
    # Show other relationships
    other_types = [rt for rt in rel_types if not (rt.startswith('P') and rt[1:].isdigit())]
    print(f"Other relationship types: {len(other_types)}")
    print(f"All: {other_types}")
    print()
    
    # Count by type
    print("TOP 20 RELATIONSHIP COUNTS:")
    print("-"*80)
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        LIMIT 20
    """)
    for r in result:
        print(f"  {r['rel_type']}: {r['count']:,}")
    print()
    
    # Test Q17167 connections
    print("Q17167 (Roman Republic) CONNECTIONS:")
    print("-"*80)
    result = session.run("""
        MATCH (rr:Entity {qid: 'Q17167'})-[r]-(connected)
        RETURN type(r) as rel_type, count(*) as count
        ORDER BY count DESC
        LIMIT 10
    """)
    rr_rels = list(result)
    if rr_rels:
        for r in rr_rels:
            print(f"  {r['rel_type']}: {r['count']}")
    else:
        print("  ⚠️ NO CONNECTIONS FOUND for Q17167!")
    print()
    
    # Check if new edges exist
    print("CHECKING FOR NEW EDGES (P31, P279, P361):")
    print("-"*80)
    for pid in ['P31', 'P279', 'P361', 'P39', 'P607']:
        result = session.run(f"MATCH ()-[r:{pid}]->() RETURN count(r) as total")
        count = result.single()['total']
        status = "✓" if count > 0 else "✗"
        print(f"  {status} :{pid} edges: {count:,}")

driver.close()

print()
print("="*80)
print("Inspection complete")
print("="*80)
