#!/usr/bin/env python3
"""
Import Year nodes to Neo4j (historical style: no Year 0).

Creates:
- Year nodes for specified range
- FOLLOWED_BY chains between years
- Explicit bridge from -1 to 1
"""

import argparse
import io
import sys
from neo4j import GraphDatabase

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def import_year_nodes(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="Chrystallum",
    database="neo4j",
    start_year=-2000,
    end_year=2025,
):
    total_target = (end_year - start_year + 1) - (1 if start_year <= 0 <= end_year else 0)
    print("=" * 80)
    print("IMPORT YEAR NODES (HISTORICAL STYLE)")
    print("=" * 80)
    print(f"URI: {uri}")
    print(f"Database: {database}")
    print(f"Range: {start_year} to {end_year} ({total_target} years, no year 0)")
    print()

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session(database=database) as session:
        print("[STEP 1] Creating Year nodes (bulk)...")
        created = session.run(
            """
            UNWIND [y IN range($start_year, $end_year) WHERE y <> 0] AS year
            WITH year,
                 CASE WHEN year < 0 THEN toString(abs(year)) + ' BCE' ELSE toString(year) + ' CE' END AS label,
                 CASE WHEN year < 0 THEN '-' + right('0000' + toString(abs(year)), 4) ELSE right('0000' + toString(year), 4) END AS year_str
            MERGE (y:Year {year: year})
            ON CREATE SET
                y.year_value = year,
                y.label = label,
                y.iso8601_start = year_str + '-01-01',
                y.iso8601_end = year_str + '-12-31',
                y.temporal_backbone = true,
                y.created = datetime()
            ON MATCH SET
                y.year_value = coalesce(y.year_value, year),
                y.label = coalesce(y.label, label),
                y.iso8601_start = coalesce(y.iso8601_start, year_str + '-01-01'),
                y.iso8601_end = coalesce(y.iso8601_end, year_str + '-12-31')
            RETURN count(y) AS c
            """,
            {"start_year": start_year, "end_year": end_year},
        ).single()["c"]

        print(f"  Created/updated {created} Year nodes")
        print()

        print("[STEP 2] Creating year chain relationships...")
        chain_count = session.run(
            """
            MATCH (y1:Year), (y2:Year)
            WHERE y2.year = y1.year + 1
            MERGE (y1)-[r:FOLLOWED_BY]->(y2)
            ON CREATE SET r.created = datetime()
            RETURN count(r) AS c
            """
        ).single()["c"]

        bridge_count = session.run(
            """
            MATCH (y_neg:Year {year: -1})
            MATCH (y_pos:Year {year: 1})
            MERGE (y_neg)-[r:FOLLOWED_BY]->(y_pos)
            RETURN count(r) AS c
            """
        ).single()["c"]
        print(f"  Chain relationships: {chain_count}, bridge relationships: {bridge_count}")
        print()

        total_years = session.run("MATCH (y:Year) RETURN count(y) AS c").single()["c"]
        followed = session.run("MATCH (:Year)-[r:FOLLOWED_BY]->(:Year) RETURN count(r) AS c").single()[
            "c"
        ]
        year0 = session.run("MATCH (:Year {year: 0}) RETURN count(*) AS c").single()["c"]

        print("=" * 80)
        print("YEAR IMPORT COMPLETE")
        print("=" * 80)
        print(f"Total Year nodes: {total_years}")
        print(f"FOLLOWED_BY edges: {followed}")
        print(f"Year 0 nodes: {year0}")

    driver.close()
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import year nodes and temporal backbone")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", default="Chrystallum", help="Neo4j password")
    parser.add_argument("--database", default="neo4j", help="Neo4j database name")
    parser.add_argument("--start", type=int, default=-2000, help="Start year (negative for BCE)")
    parser.add_argument("--end", type=int, default=2025, help="End year")
    args = parser.parse_args()

    ok = import_year_nodes(
        uri=args.uri,
        user=args.user,
        password=args.password,
        database=args.database,
        start_year=args.start,
        end_year=args.end,
    )
    sys.exit(0 if ok else 1)
