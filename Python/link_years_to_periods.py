#!/usr/bin/env python3
"""
Link Year nodes to Period nodes via canonical PART_OF relationships.
"""

import io
import sys
from neo4j import GraphDatabase

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def link_years_to_periods(uri="bolt://127.0.0.1:7687", user="neo4j", password="Chrystallum"):
    """
    Create canonical PART_OF relationships between Years and Periods.
    Also migrates legacy WITHIN_TIMESPAN edges to PART_OF.
    """
    print("=" * 80)
    print("LINK YEARS TO PERIODS (PART_OF)")
    print("=" * 80)

    driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with driver.session() as session:
            print("\n[STEP 1] Checking existing nodes...")
            total_years = session.run("MATCH (y:Year) RETURN count(y) AS total").single()["total"]
            total_periods = session.run("MATCH (p:Period) RETURN count(p) AS total").single()["total"]

            print(f"  Year nodes: {total_years}")
            print(f"  Period nodes: {total_periods}")

            if total_years == 0:
                print("\n  ERROR: No Year nodes found")
                print("  Run: python rebuild_year_backbone.py")
                return False

            if total_periods == 0:
                print("\n  ERROR: No Period nodes found")
                return False

            print("\n[STEP 2] Migrating legacy WITHIN_TIMESPAN edges...")
            migrated = session.run(
                """
                MATCH (y:Year)-[r:WITHIN_TIMESPAN]->(p:Period)
                MERGE (y)-[:PART_OF]->(p)
                WITH r
                DELETE r
                RETURN count(*) AS migrated
                """
            ).single()["migrated"]
            print(f"  Migrated: {migrated}")

            print("\n[STEP 3] Creating PART_OF relationships by year-range overlap...")
            created = session.run(
                """
                MATCH (y:Year), (p:Period)
                WITH y, p,
                     coalesce(y.year, y.year_value) AS year_num,
                     coalesce(p.start, p.start_year) AS start_num,
                     coalesce(p.end, p.end_year) AS end_num
                WHERE year_num IS NOT NULL
                  AND start_num IS NOT NULL
                  AND end_num IS NOT NULL
                  AND year_num >= start_num
                  AND year_num <= end_num
                MERGE (y)-[r:PART_OF]->(p)
                ON CREATE SET r.created = datetime(), r.source = "year_period_range_linker"
                RETURN count(r) AS created
                """
            ).single()["created"]
            print(f"  Created/confirmed: {created}")

            print("\n[STEP 4] Verification...")
            stats = session.run(
                """
                MATCH (y:Year)-[:PART_OF]->(p:Period)
                RETURN count(DISTINCT y) AS years_linked,
                       count(DISTINCT p) AS periods_linked,
                       count(*) AS total_links
                """
            ).single()

            print(f"  Years linked to periods: {stats['years_linked']}/{total_years}")
            print(f"  Periods linked to years: {stats['periods_linked']}/{total_periods}")
            print(f"  Total PART_OF links: {stats['total_links']}")

            print("\n[STEP 5] Sample links...")
            sample = session.run(
                """
                MATCH (y:Year)-[:PART_OF]->(p:Period)
                RETURN coalesce(y.year, y.year_value) AS year,
                       y.label AS year_label,
                       p.label AS period,
                       coalesce(p.start, p.start_year) AS p_start,
                       coalesce(p.end, p.end_year) AS p_end
                ORDER BY coalesce(y.year, y.year_value), p.label
                LIMIT 8
                """
            )

            for row in sample:
                print(
                    f"  {row['year']} ({row['year_label']}) -> "
                    f"{row['period']} ({row['p_start']} to {row['p_end']})"
                )

            print("\n" + "=" * 80)
            print("LINKING COMPLETE")
            print("=" * 80)
    finally:
        driver.close()

    return True


if __name__ == "__main__":
    link_years_to_periods()
