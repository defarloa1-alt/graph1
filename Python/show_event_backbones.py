#!/usr/bin/env python3
"""
Show how events are tethered to both temporal and subject backbones
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("=" * 140)
print("EVENTS TETHERED TO DUAL BACKBONE (YEAR + SUBJECT)")
print("=" * 140)

query = """
MATCH (e:Event)
OPTIONAL MATCH (e)-[:POINT_IN_TIME]->(y:Year)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(s:Subject)
OPTIONAL MATCH (e)-[:DURING]->(p:Period)
WHERE e.qid IS NOT NULL
RETURN 
    e.label AS event,
    e.date_iso8601 AS event_date,
    y.year_value AS year_backbone,
    s.lcsh_id AS subject_lcsh,
    s.label AS subject_label,
    s.lcc_code AS lcc_routing,
    p.label AS period_context
ORDER BY y.year_value, e.label
"""

with driver.session() as session:
    result = session.run(query)
    
    records = list(result)
    
    if not records:
        print("\n[NO EVENTS FOUND]")
        print("Run: python graph3-1\\python\\import_roman_republic_subgraph.py")
    else:
        print(f"\nTotal Events: {len(records)}")
        print("\n" + "-" * 140)
        
        # Print header
        print(f"{'Event':<40} {'Date':<12} {'Year':<6} {'LCSH ID':<18} {'LCC Routing':<18} {'Subject / Period':<45}")
        print("-" * 140)
        
        # Print each record
        for r in records:
            event = r['event'] or 'N/A'
            date = r['event_date'] or 'N/A'
            year = str(r['year_backbone']) if r['year_backbone'] is not None else 'N/A'
            lcsh = r['subject_lcsh'] or 'N/A'
            lcc = r['lcc_routing'] or 'N/A'
            subject = r['subject_label'] or r['period_context'] or 'N/A'
            
            # Truncate long labels
            if len(event) > 37:
                event = event[:34] + "..."
            if len(subject) > 42:
                subject = subject[:39] + "..."
            
            # Visual indicators
            year_icon = "📅" if year != 'N/A' else "  "
            subject_icon = "🏷️ " if lcsh != 'N/A' else "  "
            
            print(f"{event:<40} {date:<12} {year_icon}{year:<6} {subject_icon}{lcsh:<18} {lcc:<18} {subject:<45}")

driver.close()
print("\n" + "=" * 140)
print("\n[LEGEND]")
print("  📅 = Connected to Year backbone (temporal routing)")
print("  🏷️  = Connected to Subject backbone (topic routing via LCC)")
print("\n[LCC ROUTING]")
print("  DG235-254  → Agent_DG235-254 (Roman Republic specialist)")
print("  DG260      → Agent_DG260 (Late Republic / Caesar specialist)")
print("  DG261-267  → Agent_DG261-267 (Caesar-specific specialist)")
print("  DG279      → Agent_DG279 (Augustus / Early Empire specialist)")
print("=" * 140)

