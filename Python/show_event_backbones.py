#!/usr/bin/env python3
"""
Show how events tether to temporal and subject backbones (canonical edges).
"""

import io
import sys
from neo4j import GraphDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

query = """
MATCH (e:Event)
OPTIONAL MATCH (e)-[:STARTS_IN_YEAR]->(y_start:Year)
OPTIONAL MATCH (e)-[:ENDS_IN_YEAR]->(y_end:Year)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(s_sub:Subject)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(s_con:SubjectConcept)
OPTIONAL MATCH (e)-[:DURING]->(p:Period)
WHERE e.qid IS NOT NULL
RETURN
    e.label AS event,
    e.date_iso8601 AS event_date,
    y_start.year AS start_year,
    y_end.year AS end_year,
    coalesce(s_sub.lcsh_id, s_con.lcsh_id, s_con.authority_id) AS subject_lcsh,
    coalesce(s_sub.label, s_con.label) AS subject_label,
    coalesce(s_sub.lcc_code, s_con.lcc_class) AS lcc_routing,
    p.label AS period_context
ORDER BY coalesce(y_start.year, y_end.year), e.label
"""

print("=" * 120)
print("EVENTS TETHERED TO DUAL BACKBONE (YEAR + SUBJECT)")
print("=" * 120)

with driver.session() as session:
    records = list(session.run(query))

    print(f"\nTotal Events: {len(records)}")
    print("\n" + "-" * 120)
    print(f"{'Event':<38} {'Date':<12} {'Temporal':<18} {'LCSH ID':<18} {'LCC Routing':<18} {'Subject / Period'}")
    print("-" * 120)

    for r in records:
        event = (r["event"] or "N/A")[:38]
        date = r["event_date"] or "N/A"
        sy = r["start_year"]
        ey = r["end_year"]

        if sy is not None and ey is not None and sy == ey:
            temporal = f"Year {sy}"
        elif sy is not None and ey is not None:
            temporal = f"{sy}..{ey}"
        elif sy is not None:
            temporal = f"Start {sy}"
        elif ey is not None:
            temporal = f"End {ey}"
        else:
            temporal = "N/A"

        lcsh = r["subject_lcsh"] or "N/A"
        lcc = r["lcc_routing"] or "N/A"
        subject = r["subject_label"] or r["period_context"] or "N/A"
        print(f"{event:<38} {date:<12} {temporal:<18} {lcsh:<18} {lcc:<18} {subject}")

driver.close()
print("\n" + "=" * 120)
print("Temporal edges: STARTS_IN_YEAR / ENDS_IN_YEAR")
print("=" * 120)
