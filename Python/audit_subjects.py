#!/usr/bin/env python3
"""Check Subject node data quality"""
import sys
import io
from neo4j import GraphDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

with driver.session() as session:
    print("="*80)
    print("SUBJECT NODE AUDIT")
    print("="*80)
    
    # Check for subjects WITH lcsh_id
    result = session.run("MATCH (s:Subject) WHERE s.lcsh_id IS NOT NULL RETURN count(s) as total")
    with_lcsh = result.single()['total']
    
    # Check for subjects WITHOUT lcsh_id
    result = session.run("MATCH (s:Subject) WHERE s.lcsh_id IS NULL RETURN count(s) as total, labels(s) as labels LIMIT 1")
    without_lcsh = result.single()['total']
    
    print(f"\nSubjects WITH lcsh_id:    {with_lcsh}")
    print(f"Subjects WITHOUT lcsh_id: {without_lcsh}")
    
    # Check what the NO_ID ones are
    print("\n[SUBJECTS WITHOUT LCSH_ID]:")
    result = session.run("""
        MATCH (s:Subject)
        WHERE s.lcsh_id IS NULL
        RETURN labels(s) as labels, s.label as label, keys(s) as properties
        LIMIT 5
    """)
    for r in result:
        print(f"  Labels: {r['labels']}")
        print(f"  Label: {r['label']}")
        print(f"  Properties: {r['properties']}")
        print()

driver.close()


