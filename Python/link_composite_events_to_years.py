#!/usr/bin/env python3
"""
Link event start/end year anchors using canonical temporal edges.
"""

import io
import sys
from neo4j import GraphDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Chrystallum"))

print("=" * 80)
print("LINKING EVENTS TO YEAR BACKBONE (STARTS_IN_YEAR / ENDS_IN_YEAR)")
print("=" * 80)

with driver.session() as session:
    # Ensure links for events with year integer properties.
    session.run(
        """
        MATCH (e:Event)
        WHERE e.start_year IS NOT NULL AND e.end_year IS NOT NULL
        MATCH (ys:Year {year: e.start_year})
        MATCH (ye:Year {year: e.end_year})
        MERGE (e)-[:STARTS_IN_YEAR]->(ys)
        MERGE (e)-[:ENDS_IN_YEAR]->(ye)
        """
    )

    # Fallback for events with bbox/date strings but no integer year fields.
    session.run(
        """
        MATCH (e:Event)
        WHERE e.start_year IS NULL AND e.start_date_min IS NOT NULL AND e.end_date_max IS NOT NULL
        WITH e,
             toInteger(substring(replace(e.start_date_min, '+', ''), 0, 5)) AS start_y,
             toInteger(substring(replace(e.end_date_max, '+', ''), 0, 5)) AS end_y
        MATCH (ys:Year {year: start_y})
        MATCH (ye:Year {year: end_y})
        MERGE (e)-[:STARTS_IN_YEAR]->(ys)
        MERGE (e)-[:ENDS_IN_YEAR]->(ye)
        """
    )

    rows = list(
        session.run(
            """
            MATCH (e:Event)
            OPTIONAL MATCH (e)-[:STARTS_IN_YEAR]->(ys:Year)
            OPTIONAL MATCH (e)-[:ENDS_IN_YEAR]->(ye:Year)
            RETURN e.label AS event, ys.year AS start_year, ye.year AS end_year
            ORDER BY coalesce(ys.year, ye.year), e.label
            """
        )
    )

    print("\n" + "-" * 80)
    print(f"{'Event':<46} {'Start':<10} {'End':<10}")
    print("-" * 80)
    for r in rows:
        event = (r["event"] or "N/A")[:46]
        print(f"{event:<46} {str(r['start_year']):<10} {str(r['end_year']):<10}")

    rel_counts = list(
        session.run(
            """
            MATCH (e:Event)-[r]->(:Year)
            WHERE type(r) IN ['STARTS_IN_YEAR', 'ENDS_IN_YEAR']
            RETURN type(r) AS rel_type, count(r) AS count
            ORDER BY rel_type
            """
        )
    )

    print("\n[TEMPORAL RELATIONSHIP COUNTS]")
    for r in rel_counts:
        print(f"  {r['rel_type']:<16} {r['count']}")

driver.close()
print("\nDone.")
