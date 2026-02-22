#!/usr/bin/env python3
"""
Check LCSH Hierarchy in Neo4j
Shows the BROADER_THAN relationships we imported
"""

import sys
import io
from neo4j import GraphDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("="*80)
print("LCSH HIERARCHY IN NEO4J")
print("="*80)

with driver.session() as session:
    # Count hierarchy relationships
    result = session.run("""
        MATCH ()-[r:BROADER_THAN]->()
        RETURN count(r) as total
    """)
    total = result.single()['total']
    print(f"\nTotal BROADER_THAN relationships: {total}")
    
    # Show some hierarchy examples
    print("\n[SAMPLE HIERARCHIES]")
    print("(Showing parent -> child relationships)\n")
    
    result = session.run("""
        MATCH (parent:Subject)-[r:BROADER_THAN]->(child:Subject)
        WHERE parent.lcsh_id IS NOT NULL AND child.lcsh_id IS NOT NULL
        RETURN parent.lcsh_id as parent_id, 
               parent.label as parent_label,
               child.lcsh_id as child_id,
               child.label as child_label
        ORDER BY parent_label
        LIMIT 20
    """)
    
    for record in result:
        print(f"Parent: {record['parent_id']:15s} | {record['parent_label'][:50]}")
        print(f"  └─> Child: {record['child_id']:15s} | {record['child_label'][:50]}")
        print()
    
    # Find multi-level hierarchies
    print("\n[MULTI-LEVEL HIERARCHY PATHS]")
    result = session.run("""
        MATCH path = (top:Subject)-[:BROADER_THAN*2..3]->(bottom:Subject)
        WHERE top.lcsh_id IS NOT NULL AND bottom.lcsh_id IS NOT NULL
        RETURN 
          [node IN nodes(path) | node.label] as hierarchy_path,
          length(path) as depth
        LIMIT 5
    """)
    
    for record in result:
        depth = record['depth']
        path = record['hierarchy_path']
        print(f"\nDepth {depth}: {' -> '.join(path)}")
    
    # Rome-related hierarchy
    print("\n[ROME SUBJECT HIERARCHY]")
    result = session.run("""
        MATCH (s:Subject)
        WHERE s.label CONTAINS 'Rome' AND s.lcsh_id IS NOT NULL
        OPTIONAL MATCH (parent:Subject)-[:BROADER_THAN]->(s)
        OPTIONAL MATCH (s)-[:BROADER_THAN]->(child:Subject)
        RETURN s.lcsh_id, s.label, 
               parent.label as parent_subject,
               collect(child.label)[0..3] as children
        LIMIT 10
    """)
    
    for record in result:
        print(f"\n{record['s.lcsh_id']}: {record['s.label']}")
        if record['parent_subject']:
            print(f"  Parent: {record['parent_subject']}")
        if record['children']:
            print(f"  Children: {record['children']}")

driver.close()
print("\n" + "="*80)


