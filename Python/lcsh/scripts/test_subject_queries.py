#!/usr/bin/env python3
"""
Test Subject Node Queries
"""

import sys
import io
from neo4j import GraphDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("="*80)
print("TESTING SUBJECT NODE QUERIES")
print("="*80)

with driver.session() as session:
    # Test 1: Count all
    result = session.run("MATCH (s:Subject) RETURN count(s) as total")
    total = result.single()['total']
    print(f"\n[TEST 1] Total Subject nodes: {total}")
    
    # Test 2: Sample 10
    print("\n[TEST 2] Sample 10 subjects:")
    result = session.run("""
        MATCH (s:Subject)
        RETURN s.lcsh_id as id, s.label as label, s.dewey_decimal as dewey
        LIMIT 10
    """)
    for r in result:
        id_str = r['id'] or 'NO_ID'
        dewey_str = r['dewey'] or 'N/A'
        label_str = r['label'] or 'NO_LABEL'
        print(f"  {id_str:15s} | Dewey: {dewey_str:10s} | {label_str[:50]}")
    
    # Test 3: Find Rome subjects
    print("\n[TEST 3] Rome-related subjects:")
    result = session.run("""
        MATCH (s:Subject)
        WHERE s.label CONTAINS 'Rome'
        RETURN s.lcsh_id, s.label, s.dewey_decimal
        LIMIT 10
    """)
    count = 0
    for r in result:
        count += 1
        print(f"  {r['s.lcsh_id']:15s} | {r['s.label']}")
    
    if count == 0:
        print("  [NONE FOUND] - Try broader search")
    
    # Test 4: All with dewey
    print("\n[TEST 4] Subjects with Dewey codes:")
    result = session.run("""
        MATCH (s:Subject)
        WHERE s.dewey_decimal IS NOT NULL
        RETURN s.lcsh_id, s.label, s.dewey_decimal
        ORDER BY s.dewey_decimal
    """)
    for r in result:
        print(f"  {r['s.dewey_decimal']:10s} | {r['s.lcsh_id']:15s} | {r['s.label'][:50]}")

driver.close()
print("\n" + "="*80)

