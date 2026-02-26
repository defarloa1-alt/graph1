#!/usr/bin/env python3
"""Check relationships in Neo4j database"""

from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session() as session:
    print('=' * 80)
    print('NEO4J RELATIONSHIP CHECK')
    print('=' * 80)
    print()
    
    # Total relationships
    result = session.run('MATCH ()-[r]->() RETURN count(r) as total')
    total_rels = result.single()['total']
    print(f'Total Relationships: {total_rels:,}')
    print()
    
    # Relationship types with counts
    print('Relationship Types (Top 30):')
    print('-' * 80)
    result = session.run('''
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        LIMIT 30
    ''')
    
    for record in result:
        print(f'  {record["rel_type"]}: {record["count"]:,}')
    
    print()
    
    # Entity-related relationships
    print('Entity Node Relationships:')
    print('-' * 80)
    result = session.run('''
        MATCH (e:Entity)-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    ''')
    
    entity_rels = list(result)
    if entity_rels:
        for record in entity_rels:
            print(f'  {record["rel_type"]}: {record["count"]:,}')
    else:
        print('  [NONE] No relationships from Entity nodes')
    
    print()
    
    # Check incoming relationships to Entity
    print('Relationships TO Entity Nodes:')
    print('-' * 80)
    result = session.run('''
        MATCH ()-[r]->(e:Entity)
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    ''')
    
    incoming_rels = list(result)
    if incoming_rels:
        for record in incoming_rels:
            print(f'  {record["rel_type"]}: {record["count"]:,}')
    else:
        print('  [NONE] No relationships to Entity nodes')
    
    print()
    
    # Sample relationships (first 10)
    print('Sample Relationships (first 10):')
    print('-' * 80)
    result = session.run('''
        MATCH (a)-[r]->(b)
        RETURN labels(a)[0] as from_label, type(r) as rel_type, 
               labels(b)[0] as to_label,
               coalesce(a.label, a.name, id(a)) as from_name, 
               coalesce(b.label, b.name, id(b)) as to_name
        LIMIT 10
    ''')
    
    samples = list(result)
    for i, record in enumerate(samples, 1):
        from_label = record['from_label'] or 'Unknown'
        to_label = record['to_label'] or 'Unknown'
        from_name = str(record['from_name'])[:30]
        to_name = str(record['to_name'])[:30]
        rel_type = record['rel_type']
        
        print(f'{i}. ({from_label})-[{rel_type}]->({to_label})')
        print(f'   "{from_name}" -> "{to_name}"')
    
    if not samples:
        print('  [NONE] No relationships found in database')

driver.close()

print()
print('=' * 80)
print('SUMMARY')
print('=' * 80)
if total_rels > 0:
    print(f'✅ Database has {total_rels:,} relationships')
else:
    print('⚠️  Database has NO relationships (only nodes)')
