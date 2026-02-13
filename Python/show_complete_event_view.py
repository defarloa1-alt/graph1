#!/usr/bin/env python3
"""
Comprehensive view of all events with Wikidata Q/P properties
Shows complete dual backbone integration
"""

import sys
import io
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("=" * 160)
print("COMPLETE EVENT VIEW - WIKIDATA Q/P PROPERTIES + DUAL BACKBONE")
print("=" * 160)

query = """
MATCH (e:Event)
OPTIONAL MATCH (e)-[:POINT_IN_TIME]->(y_point:Year)
OPTIONAL MATCH (e)-[:STARTED_IN]->(y_start:Year)
OPTIONAL MATCH (e)-[:ENDED_IN]->(y_end:Year)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(s:Subject)
OPTIONAL MATCH (e)-[:DURING]->(p:Period)
WHERE e.qid IS NOT NULL
RETURN 
    e.qid AS wikidata_qid,
    e.label AS event_label,
    e.type_qid AS event_type_qid,
    e.cidoc_class AS cidoc_class,
    e.date_iso8601 AS iso_date,
    e.granularity AS granularity,
    e.goal_type AS goal,
    e.trigger_type AS trigger,
    e.action_type AS action,
    e.result_type AS result,
    y_point.year_value AS point_year,
    y_start.year_value AS start_year,
    y_end.year_value AS end_year,
    s.lcsh_id AS lcsh_id_P244,
    s.label AS lcsh_label,
    s.lcc_code AS lcc_code_P1149,
    s.dewey_decimal AS dewey_P1036,
    s.fast_id AS fast_id_P2163,
    p.label AS period_context,
    p.qid AS period_qid
ORDER BY coalesce(y_point.year_value, y_start.year_value, 0)
"""

with driver.session() as session:
    result = session.run(query)
    
    records = list(result)
    
    print(f"\nTotal Events: {len(records)}")
    print("\n" + "=" * 160)
    
    for i, r in enumerate(records, 1):
        print(f"\n[EVENT {i}]")
        print("-" * 160)
        
        # Basic Info
        print(f"  Label:           {r['event_label']}")
        print(f"  Wikidata QID:    {r['wikidata_qid']} (Entity identifier)")
        print(f"  Type QID:        {r['event_type_qid']} (P31 - instance of)")
        print(f"  CIDOC Class:     {r['cidoc_class']} (Cultural heritage classification)")
        
        # Temporal Properties
        print(f"\n  📅 TEMPORAL BACKBONE:")
        if r['point_year'] is not None:
            print(f"     Year:          {r['point_year']} (atomic event)")
            print(f"     ISO Date:      {r['iso_date']}")
        elif r['start_year'] is not None and r['end_year'] is not None:
            print(f"     Start Year:    {r['start_year']} (composite event)")
            print(f"     End Year:      {r['end_year']}")
            print(f"     Duration:      {r['end_year'] - r['start_year']} years")
        else:
            print(f"     Status:        ⚠️  No temporal link")
        
        # Subject Backbone
        print(f"\n  🏷️  SUBJECT BACKBONE (Classification):")
        if r['lcsh_id_P244']:
            print(f"     P244 (LCSH):   {r['lcsh_id_P244']} - {r['lcsh_label']}")
            print(f"     P1149 (LCC):   {r['lcc_code_P1149']} → Agent routing ⭐")
            if r['dewey_P1036']:
                print(f"     P1036 (Dewey): {r['dewey_P1036']}")
            else:
                print(f"     P1036 (Dewey): (not available)")
            if r['fast_id_P2163']:
                print(f"     P2163 (FAST):  {r['fast_id_P2163']}")
            else:
                print(f"     P2163 (FAST):  (not available)")
        else:
            print(f"     Status:        ⚠️  No subject link")
        
        # Context
        print(f"\n  📚 CONTEXT:")
        print(f"     Period:        {r['period_context']} ({r['period_qid']})")
        print(f"     Granularity:   {r['granularity']}")
        
        # Event Structure (Chrystallum Native)
        print(f"\n  🎯 EVENT STRUCTURE (Chrystallum):")
        print(f"     Goal Type:     {r['goal'] or 'N/A'}")
        print(f"     Trigger:       {r['trigger'] or 'N/A'}")
        print(f"     Action:        {r['action'] or 'N/A'}")
        print(f"     Result:        {r['result'] or 'N/A'}")
        
        # Agent Routing
        if r['lcc_code_P1149']:
            lcc = r['lcc_code_P1149']
            if lcc.startswith('DG23'):
                agent = "Agent_DG231-234 (Monarchy/Early Republic)"
            elif lcc.startswith('DG241') or lcc.startswith('DG247'):
                agent = "Agent_DG241-249 (Punic Wars)"
            elif lcc.startswith('DG254'):
                agent = "Agent_DG254 (Gracchi/Reforms)"
            elif lcc.startswith('DG260'):
                agent = "Agent_DG260 (Late Republic/Caesar era)"
            elif lcc.startswith('DG267'):
                agent = "Agent_DG267 (Caesar assassination)"
            elif lcc.startswith('DG27'):
                agent = "Agent_DG270-279 (Early Empire)"
            else:
                agent = f"Agent_{lcc.split('-')[0]}"
            
            print(f"\n  🤖 AGENT ROUTING:")
            print(f"     Routes to:     {agent}")
    
    print("\n" + "=" * 160)
    
    # Summary table
    print("\n[QUICK REFERENCE TABLE]")
    print("-" * 160)
    print(f"{'QID':<12} {'Event':<42} {'Temporal':<18} {'LCSH (P244)':<18} {'LCC (P1149)':<18} {'Agent Route'}")
    print("-" * 160)
    
    for r in records:
        qid = r['wikidata_qid']
        event = r['event_label'][:39] + "..." if len(r['event_label']) > 42 else r['event_label']
        
        if r['point_year']:
            temporal = f"Year {r['point_year']}"
        elif r['start_year']:
            temporal = f"{r['start_year']} to {r['end_year']}"
        else:
            temporal = "N/A"
        
        lcsh = r['lcsh_id_P244'] or "N/A"
        lcc = r['lcc_code_P1149'] or "N/A"
        
        if lcc != "N/A":
            agent = lcc.split('-')[0][:8]
        else:
            agent = "N/A"
        
        print(f"{qid:<12} {event:<42} {temporal:<18} {lcsh:<18} {lcc:<18} Agent_{agent}")
    
    print("-" * 160)
    
    # Coverage stats
    print("\n[COVERAGE STATISTICS]")
    result = session.run("""
        MATCH (e:Event)
        WHERE e.qid IS NOT NULL
        WITH count(e) as total
        MATCH (e2:Event)-[:POINT_IN_TIME|STARTED_IN]->(y:Year)
        WITH total, count(DISTINCT e2) as with_temporal
        MATCH (e3:Event)-[:SUBJECT_OF]->(s:Subject)
        RETURN total, with_temporal, count(DISTINCT e3) as with_subject
    """)
    
    stats = result.single()
    print(f"  Total Events:           {stats['total']}")
    print(f"  With Temporal Backbone: {stats['with_temporal']} ({stats['with_temporal']/stats['total']*100:.0f}%)")
    print(f"  With Subject Backbone:  {stats['with_subject']} ({stats['with_subject']/stats['total']*100:.0f}%)")
    
    # Wikidata property reference
    print("\n[WIKIDATA PROPERTY REFERENCE]")
    print("  P31   = instance of (event type)")
    print("  P244  = LCSH ID (Library of Congress Subject Headings) - Primary backbone ⭐")
    print("  P1036 = Dewey Decimal Classification (~12% coverage)")
    print("  P1149 = LCC (Library of Congress Classification) - Agent routing ⭐")
    print("  P2163 = FAST ID (Faceted Application of Subject Terminology) (~54% coverage)")

driver.close()
print("\n" + "=" * 160)
print("✅ COMPLETE VIEW!")
print("=" * 160)
print("\n[RAW CYPHER FOR NEO4J BROWSER]")
print("""
MATCH (e:Event)
OPTIONAL MATCH (e)-[:POINT_IN_TIME]->(y_point:Year)
OPTIONAL MATCH (e)-[:STARTED_IN]->(y_start:Year)
OPTIONAL MATCH (e)-[:ENDED_IN]->(y_end:Year)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(s:Subject)
OPTIONAL MATCH (e)-[:DURING]->(p:Period)
WHERE e.qid IS NOT NULL
RETURN e.qid, e.label, 
       y_point.year_value, y_start.year_value, y_end.year_value,
       s.lcsh_id AS P244_LCSH, s.lcc_code AS P1149_LCC,
       s.dewey_decimal AS P1036_Dewey, s.fast_id AS P2163_FAST,
       p.label AS period
ORDER BY coalesce(y_point.year_value, y_start.year_value, 0)
""")
print("=" * 160)

