#!/usr/bin/env python3
"""
Display all LCC codes with full details including LCSH labels
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("=" * 120)
print("ALL LCC CODES WITH LCSH LABELS")
print("=" * 120)

query = """
MATCH (s:Subject)
WHERE s.lcc_code IS NOT NULL
RETURN s.lcc_code AS lcc_code,
       s.lcsh_id AS lcsh_id,
       s.label AS lcsh_label,
       CASE 
         WHEN s.dewey_decimal IS NOT NULL THEN s.dewey_decimal 
         ELSE 'N/A' 
       END AS dewey,
       CASE 
         WHEN s.fast_id IS NOT NULL THEN s.fast_id 
         ELSE 'N/A' 
       END AS fast
ORDER BY s.lcc_code
"""

with driver.session() as session:
    result = session.run(query)
    
    records = list(result)
    
    print(f"\nTotal Subjects with LCC Codes: {len(records)}")
    print("\n" + "-" * 120)
    
    # Print header
    print(f"{'LCC Code':<20} {'LCSH ID':<15} {'LCSH Label':<50} {'Dewey':<12} {'FAST':<12}")
    print("-" * 120)
    
    # Print each record
    for r in records:
        lcc = r['lcc_code'] or 'N/A'
        lcsh_id = r['lcsh_id'] or 'N/A'
        lcsh_label = r['lcsh_label'] or 'N/A'
        dewey = r['dewey'] or 'N/A'
        fast = r['fast'] or 'N/A'
        
        # Truncate long labels
        if len(lcsh_label) > 47:
            lcsh_label = lcsh_label[:44] + "..."
        
        print(f"{lcc:<20} {lcsh_id:<15} {lcsh_label:<50} {dewey:<12} {fast:<12}")

driver.close()
print("\n" + "=" * 120)

