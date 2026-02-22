#!/usr/bin/env python3
"""
Check what classification codes we actually have
"""

import sys
import io
from neo4j import GraphDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("="*80)
print("CLASSIFICATION CODE AUDIT")
print("="*80)

with driver.session() as session:
    # Total subjects
    result = session.run("MATCH (s:Subject) WHERE s.lcsh_id IS NOT NULL RETURN count(s) as total")
    total = result.single()['total']
    
    # With Dewey
    result = session.run("MATCH (s:Subject) WHERE s.dewey_decimal IS NOT NULL RETURN count(s) as total, collect(s.label)[0..5] as examples")
    record = result.single()
    with_dewey = record['total']
    dewey_examples = record['examples']
    
    # With LCC
    result = session.run("MATCH (s:Subject) WHERE s.lcc_code IS NOT NULL RETURN count(s) as total, collect(s.label)[0..5] as examples")
    record = result.single()
    with_lcc = record['total']
    lcc_examples = record['examples']
    
    # With FAST
    result = session.run("MATCH (s:Subject) WHERE s.fast_id IS NOT NULL RETURN count(s) as total, collect(s.label)[0..5] as examples")
    record = result.single()
    with_fast = record['total']
    fast_examples = record['examples']
    
    print(f"\nTotal LCSH Subjects: {total}")
    print()
    print(f"With Dewey Decimal:  {with_dewey} ({with_dewey/total*100:.1f}%)")
    if dewey_examples:
        print("  Examples:")
        for ex in dewey_examples:
            print(f"    - {ex}")
    
    print()
    print(f"With LCC Code:       {with_lcc} ({with_lcc/total*100:.1f}%)")
    if lcc_examples:
        print("  Examples:")
        for ex in lcc_examples:
            print(f"    - {ex}")
    
    print()
    print(f"With FAST ID:        {with_fast} ({with_fast/total*100:.1f}%)")
    if fast_examples:
        print("  Examples:")
        for ex in fast_examples:
            print(f"    - {ex}")
    
    # Check if ANY have all three
    result = session.run("""
        MATCH (s:Subject) 
        WHERE s.dewey_decimal IS NOT NULL 
          AND s.lcc_code IS NOT NULL 
          AND s.fast_id IS NOT NULL
        RETURN count(s) as total
    """)
    with_all = result.single()['total']
    
    print()
    print(f"With ALL THREE:      {with_all} ({with_all/total*100:.1f}%)")
    
    # Show Rome subjects
    print()
    print("="*80)
    print("ROME-RELATED SUBJECTS (Classification Codes)")
    print("="*80)
    result = session.run("""
        MATCH (s:Subject)
        WHERE s.label CONTAINS 'Rome'
        RETURN s.lcsh_id, s.label, s.dewey_decimal, s.lcc_code, s.fast_id
        ORDER BY size(s.label) DESC
    """)
    
    for r in result:
        print(f"\n{r['s.lcsh_id']}: {r['s.label']}")
        print(f"  Dewey: {r['s.dewey_decimal'] or 'MISSING'}")
        print(f"  LCC:   {r['s.lcc_code'] or 'MISSING'}")
        print(f"  FAST:  {r['s.fast_id'] or 'MISSING'}")

driver.close()
print("\n" + "="*80)

