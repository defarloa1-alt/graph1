#!/usr/bin/env python3
"""
Rebuild Year backbone in Neo4j (historical style: no Year 0).
Creates Year nodes and FOLLOWED_BY chain with a bridge -1 -> 1.
"""

import argparse
from neo4j import GraphDatabase


def rebuild_year_backbone(
    uri="bolt://127.0.0.1:7687",
    user="neo4j",
    password="Chrystallum",
    start_year=-753,
    end_year=-82,
):
    target_years = (end_year - start_year + 1) - (1 if start_year <= 0 <= end_year else 0)
    print("=" * 80)
    print("REBUILD YEAR BACKBONE (HISTORICAL STYLE)")
    print("=" * 80)
    print(f"URI: {uri}")
    print(f"Range: {start_year} to {end_year} ({target_years} years, no year 0)")
    print()

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            existing = session.run("MATCH (y:Year) RETURN count(y) AS total").single()["total"]
            print(f"[STEP 0] Existing Year nodes: {existing}")

            if existing > 0:
                response = input(f"Delete {existing} existing Year nodes? (yes/no): ").strip().lower()
                if response == "yes":
                    session.run("MATCH (y:Year) DETACH DELETE y")
                    print(f"  Deleted {existing} Year nodes")
                else:
                    print("  Keeping existing Years, merging updates")

            print("\n[STEP 1] Creating Year nodes...")
            created = 0
            for year in range(start_year, end_year + 1):
                if year == 0:
                    continue

                if year < 0:
                    abs_year = f"{abs(year):04d}"
                    iso_start = f"-{abs_year}-01-01"
                    iso_end = f"-{abs_year}-12-31"
                    label = f"{abs(year)} BCE"
                else:
                    year_str = f"{year:04d}"
                    iso_start = f"{year_str}-01-01"
                    iso_end = f"{year_str}-12-31"
                    label = f"{year} CE"

                session.run(
                    """
                    MERGE (y:Year {year: $year})
                    ON CREATE SET
                        y.year_value = $year,
                        y.label = $label,
                        y.name = $label,
                        y.iso8601_start = $iso_start,
                        y.iso8601_end = $iso_end,
                        y.cidoc_crm_class = 'E52_Time-Span',
                        y.unique_id = 'YEAR_' + toString($year),
                        y.temporal_backbone = true,
                        y.created = datetime()
                    ON MATCH SET
                        y.year_value = coalesce(y.year_value, $year),
                        y.label = $label,
                        y.name = $label,
                        y.iso8601_start = $iso_start,
                        y.iso8601_end = $iso_end,
                        y.cidoc_crm_class = 'E52_Time-Span'
                    """,
                    {
                        "year": year,
                        "label": label,
                        "iso_start": iso_start,
                        "iso_end": iso_end,
                    },
                )
                created += 1
                if created % 100 == 0:
                    print(f"  Progress: {created}/{target_years}")

            print(f"  Created/updated {created} Year nodes")

            print("\n[STEP 2] Creating year chain relationships...")
            chain_count = session.run(
                """
                MATCH (y1:Year), (y2:Year)
                WHERE y2.year = y1.year + 1
                MERGE (y1)-[r:FOLLOWED_BY]->(y2)
                RETURN count(r) AS count
                """
            ).single()["count"]

            bridge_count = session.run(
                """
                MATCH (y_neg:Year {year: -1})
                MATCH (y_pos:Year {year: 1})
                MERGE (y_neg)-[r:FOLLOWED_BY]->(y_pos)
                RETURN count(r) AS count
                """
            ).single()["count"]

            print(f"  Chain relationships: {chain_count}, bridge relationships: {bridge_count}")

            print("\n[STEP 3] Verification...")
            stats = session.run(
                """
                MATCH (y:Year)
                RETURN count(y) AS total_years, min(y.year) AS min_year, max(y.year) AS max_year
                """
            ).single()
            chain_length = session.run(
                "MATCH (:Year)-[r:FOLLOWED_BY]->(:Year) RETURN count(r) AS c"
            ).single()["c"]
            has_zero = session.run("MATCH (:Year {year: 0}) RETURN count(*) AS c").single()["c"]

            print(f"  Total Year nodes: {stats['total_years']}")
            print(f"  Year range: {stats['min_year']} to {stats['max_year']}")
            print(f"  FOLLOWED_BY count: {chain_length}")
            print(f"  Year 0 nodes: {has_zero}")

            expected_chain = stats["total_years"] - 1
            if chain_length == expected_chain and has_zero == 0:
                print("  Verification passed")
            else:
                print(f"  Verification warning: expected chain {expected_chain}, got {chain_length}")

            print("\n" + "=" * 80)
            print("YEAR BACKBONE REBUILT")
            print("=" * 80)
    finally:
        driver.close()

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild year backbone (historical style)")
    parser.add_argument("--start", type=int, default=-753, help="Start year (negative for BCE)")
    parser.add_argument("--end", type=int, default=-82, help="End year")
    args = parser.parse_args()
    rebuild_year_backbone(start_year=args.start, end_year=args.end)
