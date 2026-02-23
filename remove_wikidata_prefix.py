#!/usr/bin/env python3
"""
Remove WIKIDATA_ Prefix from Relationship Types

Renames: WIKIDATA_P31 → P31, WIKIDATA_P361 → P361, etc.
Preserves all edge properties.
Processes in batches for performance.
"""

from neo4j import GraphDatabase
from datetime import datetime

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

print("="*80)
print("REMOVE WIKIDATA_ PREFIX FROM EDGES")
print("="*80)
print(f"Start: {datetime.now()}")
print()

# Get all WIKIDATA_P* relationship types
with driver.session() as session:
    result = session.run("""
        CALL db.relationshipTypes() YIELD relationshipType
        WHERE relationshipType STARTS WITH 'WIKIDATA_P'
        RETURN relationshipType as old_type
        ORDER BY old_type
    """)
    
    wikidata_rel_types = [r['old_type'] for r in result]

print(f"Relationship types to rename: {len(wikidata_rel_types)}")
print()

total_renamed = 0

for old_type in wikidata_rel_types:
    new_type = old_type.replace('WIKIDATA_', '')
    
    print(f"Renaming: {old_type} -> {new_type}...")
    
    # Process in batches (Neo4j can't rename relationship types directly)
    with driver.session() as session:
        # Count edges to rename
        result = session.run(f"""
            MATCH ()-[r:{old_type}]->()
            RETURN count(r) as total
        """)
        total = result.single()['total']
        
        if total == 0:
            print(f"  No edges found")
            continue
        
        # Rename: Create new edge with copied properties, delete old
        result = session.run(f"""
            MATCH (a)-[old:{old_type}]->(b)
            WITH a, old, b, properties(old) as props
            LIMIT 10000
            CALL apoc.create.relationship(a, '{new_type}', props, b)
            YIELD rel
            DELETE old
            RETURN count(rel) as renamed
        """)
        
        renamed = result.single()['renamed']
        total_renamed += renamed
        
        print(f"  Renamed: {renamed:,} edges")

driver.close()

print()
print("="*80)
print("CLEANUP COMPLETE")
print("="*80)
print(f"End: {datetime.now()}")
print()
print(f"Total edges renamed: {total_renamed:,}")
print()
print("Verification:")
print("  MATCH ()-[r]->() WHERE type(r) STARTS WITH 'WIKIDATA_'")
print("  RETURN count(r)")
print("  // Should return 0")
print()
print("New edge types:")
print("  :P31, :P361, :P39, :P279, :P607, etc.")
print()
