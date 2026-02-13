#!/usr/bin/env python3
"""
Comprehensive event view with canonical temporal anchors and classification backbone.
"""

import io
import sys
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DRIVER = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

QUERY = """
MATCH (e:Event)
OPTIONAL MATCH (e)-[:STARTS_IN_YEAR]->(y_start:Year)
OPTIONAL MATCH (e)-[:ENDS_IN_YEAR]->(y_end:Year)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(s_sub:Subject)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(s_con:SubjectConcept)
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
    e.start_date_min AS start_date_min,
    e.end_date_max AS end_date_max,
    y_start.year AS start_year,
    y_end.year AS end_year,
    coalesce(s_sub.lcsh_id, s_con.lcsh_id, s_con.authority_id) AS lcsh_id_P244,
    coalesce(s_sub.label, s_con.label) AS lcsh_label,
    coalesce(s_sub.lcc_code, s_con.lcc_class) AS lcc_code_P1149,
    coalesce(s_sub.dewey_decimal, s_con.dewey_decimal) AS dewey_P1036,
    coalesce(s_sub.fast_id, s_con.fast_id) AS fast_id_P2163,
    p.label AS period_context,
    p.qid AS period_qid
ORDER BY coalesce(y_start.year, y_end.year, 0), e.label
"""


def _temporal_summary(row):
    sy = row["start_year"]
    ey = row["end_year"]
    smin = row["start_date_min"]
    emax = row["end_date_max"]

    if sy is None and ey is None:
        return "No year anchors", "No bbox"

    if sy is not None and ey is not None and sy == ey:
        anchor = f"Year {sy}"
    elif sy is not None and ey is not None:
        anchor = f"{sy} to {ey}"
    elif sy is not None:
        anchor = f"Start {sy}"
    else:
        anchor = f"End {ey}"

    bbox = f"{smin or '?'} .. {emax or '?'}"
    return anchor, bbox


def main():
    print("=" * 120)
    print("COMPLETE EVENT VIEW - CANONICAL TEMPORAL + SUBJECT BACKBONES")
    print("=" * 120)

    with DRIVER.session() as session:
        records = list(session.run(QUERY))

        print(f"\nTotal Events: {len(records)}")
        print("\n" + "-" * 120)

        for i, r in enumerate(records, start=1):
            anchor, bbox = _temporal_summary(r)
            print(f"\n[EVENT {i}] {r['event_label']}")
            print(f"  QID:           {r['wikidata_qid']}")
            print(f"  Type QID:      {r['event_type_qid']}")
            print(f"  CIDOC Class:   {r['cidoc_class']}")
            print(f"  Year Anchors:  {anchor}")
            print(f"  BBox Range:    {bbox}")
            if r["iso_date"]:
                print(f"  Nominal Date:  {r['iso_date']}")
            print(f"  LCSH (P244):   {r['lcsh_id_P244'] or 'N/A'}")
            print(f"  LCC (P1149):   {r['lcc_code_P1149'] or 'N/A'}")
            print(f"  Dewey (P1036): {r['dewey_P1036'] or 'N/A'}")
            print(f"  FAST (P2163):  {r['fast_id_P2163'] or 'N/A'}")
            print(f"  Period:        {r['period_context'] or 'N/A'} ({r['period_qid'] or 'N/A'})")

        stats = session.run(
            """
            MATCH (e:Event) WHERE e.qid IS NOT NULL
            WITH count(e) AS total
            MATCH (e2:Event)-[:STARTS_IN_YEAR|ENDS_IN_YEAR]->(:Year)
            WITH total, count(DISTINCT e2) AS with_temporal
            MATCH (e3:Event)-[:SUBJECT_OF]->(s)
            RETURN total, with_temporal, count(DISTINCT e3) AS with_subject
            """
        ).single()

        print("\n" + "=" * 120)
        print("COVERAGE STATISTICS")
        print("=" * 120)
        print(f"Total Events:           {stats['total']}")
        if stats["total"]:
            print(
                f"With Temporal Backbone: {stats['with_temporal']} "
                f"({stats['with_temporal'] / stats['total'] * 100:.0f}%)"
            )
            print(
                f"With Subject Backbone:  {stats['with_subject']} "
                f"({stats['with_subject'] / stats['total'] * 100:.0f}%)"
            )

    DRIVER.close()


if __name__ == "__main__":
    main()
