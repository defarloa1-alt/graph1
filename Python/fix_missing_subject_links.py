#!/usr/bin/env python3
"""
Fix missing subject links for major Roman events
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("=" * 80)
print("FIXING MISSING SUBJECT LINKS")
print("=" * 80)

with driver.session() as session:
    
    print("\n[STEP 1] Creating missing subject nodes...")
    
    # Subject for Establishment of Roman Republic
    # This transitions FROM monarchy TO republic
    session.run("""
        MERGE (s:Subject {lcsh_id: "sh85115113"})
        SET s.label = "Rome--History--Kings, 753-510 B.C.",
            s.lcc_code = "DG231-234",
            s.dewey_decimal = null,
            s.fast_id = null,
            s.unique_id = "lcsh:sh85115113",
            s.source = "manual_completion"
    """)
    print("  ✅ Created: sh85115113 (Rome--History--Kings) LCC: DG231-234")
    
    # Subject for Establishment of Roman Empire
    # This transitions FROM republic TO empire
    session.run("""
        MERGE (s:Subject {lcsh_id: "sh85115120"})
        SET s.label = "Rome--History--Empire, 30 B.C.-476 A.D.",
            s.lcc_code = "DG270-279",
            s.dewey_decimal = "937.06",
            s.fast_id = null,
            s.unique_id = "lcsh:sh85115120",
            s.source = "manual_completion"
    """)
    print("  ✅ Created: sh85115120 (Rome--History--Empire) LCC: DG270-279")
    
    # Subject for Gracchi Reforms (more specific)
    session.run("""
        MERGE (s:Subject {lcsh_id: "sh85056427"})
        SET s.label = "Gracchi",
            s.lcc_code = "DG254.2-254.4",
            s.dewey_decimal = null,
            s.fast_id = "fst00945942",
            s.unique_id = "lcsh:sh85056427",
            s.source = "manual_completion"
    """)
    print("  ✅ Created: sh85056427 (Gracchi) LCC: DG254.2-254.4")
    
    print("\n[STEP 2] Linking events to subjects...")
    
    # Link Establishment of Roman Republic
    # This event marks END of monarchy period
    session.run("""
        MATCH (e:Event {qid: "Q23402"})
        MATCH (s:Subject {lcsh_id: "sh85115113"})
        MERGE (e)-[:SUBJECT_OF]->(s)
    """)
    print("  ✅ Establishment of Roman Republic → sh85115113 (Kings period)")
    
    # Link Establishment of Roman Empire
    # This event marks START of empire period
    session.run("""
        MATCH (e:Event {qid: "Q23401"})
        MATCH (s:Subject {lcsh_id: "sh85115120"})
        MERGE (e)-[:SUBJECT_OF]->(s)
    """)
    print("  ✅ Establishment of Roman Empire → sh85115120 (Empire period)")
    
    # Link Gracchi Reforms
    session.run("""
        MATCH (e:Event {qid: "Q912145"})
        MATCH (s:Subject {lcsh_id: "sh85056427"})
        MERGE (e)-[:SUBJECT_OF]->(s)
    """)
    print("  ✅ Gracchi Reforms → sh85056427 (Gracchi)")
    
    print("\n[STEP 3] Verifying all events have subjects...")
    
    result = session.run("""
        MATCH (e:Event)
        OPTIONAL MATCH (e)-[:STARTS_IN_YEAR]->(y_start:Year)
        OPTIONAL MATCH (e)-[:ENDS_IN_YEAR]->(y_end:Year)
        OPTIONAL MATCH (e)-[:SUBJECT_OF]->(s:Subject)
        WHERE e.qid IS NOT NULL
        RETURN
            e.label AS event,
            e.date_iso8601 AS date,
            coalesce(y_start.year, y_end.year, y_start.year_value, y_end.year_value) AS year,
            s.lcsh_id AS subject_id,
            s.lcc_code AS lcc,
            s.label AS subject
        ORDER BY coalesce(y_start.year, y_end.year, y_start.year_value, y_end.year_value)
    """)
    
    print("\n" + "-" * 120)
    print(f"{'Event':<40} {'Date':<12} {'Year':<6} {'LCSH':<18} {'LCC':<18} {'Subject'}")
    print("-" * 120)
    
    all_have_subjects = True
    for r in result:
        event = r['event'] or 'N/A'
        date = r['date'] or 'N/A'
        year = str(r['year']) if r['year'] is not None else 'N/A'
        lcsh = r['subject_id'] or 'MISSING ❌'
        lcc = r['lcc'] or 'N/A'
        subject = r['subject'] or 'N/A'
        
        if lcsh == 'MISSING ❌':
            all_have_subjects = False
        
        if len(event) > 37:
            event = event[:34] + "..."
        if len(subject) > 40:
            subject = subject[:37] + "..."
        
        icon = "✅" if lcsh != 'MISSING ❌' else "❌"
        
        print(f"{icon} {event:<38} {date:<12} {year:<6} {lcsh:<18} {lcc:<18} {subject}")
    
    print("-" * 120)
    
    if all_have_subjects:
        print("\n🎉 SUCCESS! All events now have subject backbone links!")
    else:
        print("\n⚠️  WARNING: Some events still missing subjects")
    
    # Show LCC routing hierarchy
    print("\n[LCC ROUTING HIERARCHY]")
    result = session.run("""
        MATCH (s:Subject)
        WHERE s.lcc_code STARTS WITH 'DG' AND size(s.lcc_code) < 20
        RETURN s.lcc_code, s.label
        ORDER BY s.lcc_code
    """)
    
    print("\n  LCC Code         Subject")
    print("  " + "-" * 80)
    for r in result:
        lcc = r['s.lcc_code']
        label = r['s.label']
        if len(label) > 60:
            label = label[:57] + "..."
        print(f"  {lcc:<16} {label}")

driver.close()
print("\n" + "=" * 80)
print("✅ COMPLETE!")
print("=" * 80)

