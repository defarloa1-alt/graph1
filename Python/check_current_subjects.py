#!/usr/bin/env python3
"""
Check what LCSH subjects we actually have in Neo4j
"""

import sys
import io
from neo4j import GraphDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("="*80)
print("CURRENT NEO4J SUBJECTS")
print("="*80)

with driver.session() as session:
    # Sample subjects
    result = session.run("""
        MATCH (s:Subject)
        RETURN s.lcsh_id, s.label, s.lcc_code, s.dewey_decimal, s.fast_id
        ORDER BY s.label
        LIMIT 20
    """)
    
    print("\n[SAMPLE] First 20 subjects:\n")
    for r in result:
        print(f"{r['s.lcsh_id'] or 'NO_ID'}: {r['s.label']}")
        print(f"  LCC:   {r['s.lcc_code'] or 'N/A'}")
        print(f"  Dewey: {r['s.dewey_decimal'] or 'N/A'}")
        print(f"  FAST:  {r['s.fast_id'] or 'N/A'}")
        print()
    
    # Check for Rome-related
    result = session.run("""
        MATCH (s:Subject)
        WHERE s.label CONTAINS 'Rome'
        RETURN s.lcsh_id, s.label, s.lcc_code
        ORDER BY size(s.label) DESC
    """)
    
    print("\n[ROME SUBJECTS]")
    rome_count = 0
    for r in result:
        rome_count += 1
        print(f"  {r['s.lcsh_id']}: {r['s.label']}")
        print(f"    LCC: {r['s.lcc_code'] or 'N/A'}")
    
    if rome_count == 0:
        print("  (none found)")
    
    # Check LCC coverage
    result = session.run("""
        MATCH (s:Subject)
        WITH count(s) as total
        MATCH (s2:Subject)
        WHERE s2.lcc_code IS NOT NULL
        RETURN total, count(s2) as with_lcc
    """)
    
    r = result.single()
    total = r['total']
    with_lcc = r['with_lcc']
    
    print(f"\n[LCC COVERAGE]")
    print(f"  Total subjects: {total}")
    print(f"  With LCC code:  {with_lcc} ({with_lcc/total*100:.1f}%)")

driver.close()
print("\n" + "="*80)

