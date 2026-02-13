#!/usr/bin/env python3
"""
Link composite events to their start/end years
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("=" * 80)
print("LINKING COMPOSITE EVENTS TO YEAR BACKBONE")
print("=" * 80)

with driver.session() as session:
    
    print("\n[COMPOSITE EVENTS]")
    print("These span multiple years, so we link to START and END years\n")
    
    # Check current state
    result = session.run("""
        MATCH (e:Event {qid: "Q47084"})
        RETURN e.label, e.start_year, e.end_year
    """)
    r = result.single()
    print(f"1. {r['e.label']}")
    print(f"   Start: {r['e.start_year']} BCE")
    print(f"   End:   {r['e.end_year']} BCE")
    
    result = session.run("""
        MATCH (e:Event {qid: "Q912145"})
        RETURN e.label, e.start_year, e.end_year
    """)
    r = result.single()
    print(f"\n2. {r['e.label']}")
    print(f"   Start: {r['e.start_year']} BCE")
    print(f"   End:   {r['e.end_year']} BCE")
    
    print("\n" + "-" * 80)
    print("\n[STEP 1] Linking Punic Wars to years...")
    
    # Punic Wars: -264 to -146
    session.run("""
        MATCH (e:Event {qid: "Q47084"})
        MATCH (y_start:Year {year_value: -264})
        MERGE (e)-[:STARTED_IN]->(y_start)
    """)
    print("  ✅ Punic Wars -[:STARTED_IN]-> Year(-264)")
    
    session.run("""
        MATCH (e:Event {qid: "Q47084"})
        MATCH (y_end:Year {year_value: -146})
        MERGE (e)-[:ENDED_IN]->(y_end)
    """)
    print("  ✅ Punic Wars -[:ENDED_IN]-> Year(-146)")
    
    print("\n[STEP 2] Linking Gracchi Reforms to years...")
    
    # Gracchi Reforms: -133 to -121
    session.run("""
        MATCH (e:Event {qid: "Q912145"})
        MATCH (y_start:Year {year_value: -133})
        MERGE (e)-[:STARTED_IN]->(y_start)
    """)
    print("  ✅ Gracchi Reforms -[:STARTED_IN]-> Year(-133)")
    
    session.run("""
        MATCH (e:Event {qid: "Q912145"})
        MATCH (y_end:Year {year_value: -121})
        MERGE (e)-[:ENDED_IN]->(y_end)
    """)
    print("  ✅ Gracchi Reforms -[:ENDED_IN]-> Year(-121)")
    
    print("\n[STEP 3] Verifying all events have temporal links...")
    
    result = session.run("""
        MATCH (e:Event)
        OPTIONAL MATCH (e)-[:POINT_IN_TIME]->(y_point:Year)
        OPTIONAL MATCH (e)-[:STARTED_IN]->(y_start:Year)
        OPTIONAL MATCH (e)-[:ENDED_IN]->(y_end:Year)
        OPTIONAL MATCH (e)-[:SUBJECT_OF]->(s:Subject)
        WHERE e.qid IS NOT NULL
        RETURN 
            e.label AS event,
            e.granularity AS granularity,
            y_point.year_value AS point_year,
            y_start.year_value AS start_year,
            y_end.year_value AS end_year,
            s.lcc_code AS lcc
        ORDER BY coalesce(y_point.year_value, y_start.year_value, 0)
    """)
    
    print("\n" + "-" * 100)
    print(f"{'Event':<42} {'Type':<12} {'Temporal Link':<30} {'LCC Routing'}")
    print("-" * 100)
    
    all_have_temporal = True
    for r in result:
        event = r['event'] or 'N/A'
        granularity = r['granularity'] or 'unknown'
        point = r['point_year']
        start = r['start_year']
        end = r['end_year']
        lcc = r['lcc'] or 'N/A'
        
        if len(event) > 39:
            event = event[:36] + "..."
        
        # Determine temporal link
        if point is not None:
            temporal = f"Year {point}"
            icon = "📅"
        elif start is not None and end is not None:
            temporal = f"Years {start} to {end}"
            icon = "📅"
        else:
            temporal = "MISSING ❌"
            icon = "❌"
            all_have_temporal = False
        
        print(f"{icon} {event:<40} {granularity:<12} {temporal:<30} {lcc}")
    
    print("-" * 100)
    
    if all_have_temporal:
        print("\n🎉 SUCCESS! All events now linked to Year backbone!")
    else:
        print("\n⚠️  WARNING: Some events still missing temporal links")
    
    # Show relationship type summary
    print("\n[TEMPORAL RELATIONSHIP TYPES]")
    result = session.run("""
        MATCH (e:Event)-[r]->(y:Year)
        WHERE type(r) IN ['POINT_IN_TIME', 'STARTED_IN', 'ENDED_IN']
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY rel_type
    """)
    
    for r in result:
        rel = r['rel_type']
        count = r['count']
        
        if rel == 'POINT_IN_TIME':
            desc = "Atomic events (single moment)"
        elif rel == 'STARTED_IN':
            desc = "Composite events (start year)"
        elif rel == 'ENDED_IN':
            desc = "Composite events (end year)"
        else:
            desc = ""
        
        print(f"  {rel:<20} {count:<5} {desc}")

driver.close()
print("\n" + "=" * 80)
print("✅ COMPLETE!")
print("=" * 80)
print("\n[QUERY PATTERNS]")
print("Atomic events:    MATCH (e:Event)-[:POINT_IN_TIME]->(y:Year)")
print("Composite events: MATCH (e:Event)-[:STARTED_IN|ENDED_IN]->(y:Year)")
print("All events:       MATCH (e:Event)-[:POINT_IN_TIME|STARTED_IN|ENDED_IN]->(y:Year)")
print("=" * 80)

