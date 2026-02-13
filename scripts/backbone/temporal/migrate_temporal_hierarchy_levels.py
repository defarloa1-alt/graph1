#!/usr/bin/env python3
"""
Build Decade/Century/Millennium hierarchy from Year nodes.

Phase-safe behavior:
- Adds canonical PART_OF hierarchy and FOLLOWED_BY links
"""

import argparse
from neo4j import GraphDatabase


def run_scalar(session, query):
    return session.run(query).single()["c"]


def count_if_label_exists(session, label):
    labels = session.run("CALL db.labels() YIELD label RETURN collect(label) AS labels").single()[
        "labels"
    ]
    if label not in labels:
        return 0
    return run_scalar(session, f"MATCH (n:{label}) RETURN count(n) AS c")


def audit(session):
    print("\n[Audit]")
    print(
        "  Year nodes:",
        run_scalar(session, "MATCH (y:Year) RETURN count(y) AS c"),
    )
    print("  Decade nodes:", count_if_label_exists(session, "Decade"))
    print("  Century nodes:", count_if_label_exists(session, "Century"))
    print("  Millennium nodes:", count_if_label_exists(session, "Millennium"))

    for rel in ["FOLLOWED_BY", "PART_OF"]:
        count = run_scalar(session, f"MATCH ()-[r:{rel}]->() RETURN count(r) AS c")
        print(f"  {rel} edges: {count}")


def apply_hierarchy(session):
    print("\n[Apply] Normalizing Year.year")
    normalized = run_scalar(
        session,
        """
        MATCH (y:Year)
        WHERE y.year IS NULL AND y.year_value IS NOT NULL
        SET y.year = y.year_value
        RETURN count(y) AS c
        """,
    )
    print(f"  Normalized Year.year from year_value: {normalized}")

    print("\n[Apply] Constraints/Indexes")
    session.run(
        "CREATE CONSTRAINT decade_start_unique IF NOT EXISTS FOR (d:Decade) REQUIRE d.start_year IS UNIQUE"
    )
    session.run(
        "CREATE CONSTRAINT century_start_unique IF NOT EXISTS FOR (c:Century) REQUIRE c.start_year IS UNIQUE"
    )
    session.run(
        "CREATE CONSTRAINT millennium_start_unique IF NOT EXISTS FOR (m:Millennium) REQUIRE m.start_year IS UNIQUE"
    )
    session.run("CREATE INDEX decade_label_index IF NOT EXISTS FOR (d:Decade) ON (d.label)")
    session.run("CREATE INDEX century_label_index IF NOT EXISTS FOR (c:Century) ON (c.label)")
    session.run(
        "CREATE INDEX millennium_label_index IF NOT EXISTS FOR (m:Millennium) ON (m.label)"
    )
    print("  Done")

    print("\n[Apply] Creating temporal level nodes")
    decades = run_scalar(
        session,
        """
        MATCH (y:Year)
        WITH DISTINCT toInteger(floor(toFloat(y.year) / 10.0) * 10) AS start_year
        MERGE (d:Decade {start_year: start_year})
        SET d.end_year = start_year + 9,
            d.entity_type = 'Decade',
            d.era = CASE WHEN start_year < 0 THEN 'BCE' ELSE 'CE' END,
            d.range_label = toString(start_year) + ' to ' + toString(start_year + 9),
            d.label = CASE
                WHEN start_year < 0 THEN toString(abs(start_year)) + 's BCE'
                ELSE toString(start_year) + 's CE'
            END
        RETURN count(d) AS c
        """,
    )
    centuries = run_scalar(
        session,
        """
        MATCH (y:Year)
        WITH DISTINCT toInteger(floor(toFloat(y.year) / 100.0) * 100) AS start_year
        MERGE (c:Century {start_year: start_year})
        WITH c, start_year, (start_year + 99) AS end_year,
             CASE
                 WHEN start_year < 0 THEN toInteger(abs(start_year) / 100)
                 ELSE toInteger(start_year / 100) + 1
             END AS ordinal_num,
             CASE WHEN start_year < 0 THEN 'BCE' ELSE 'CE' END AS era
        SET c.end_year = end_year,
            c.entity_type = 'Century',
            c.era = era,
            c.ordinal = ordinal_num,
            c.range_label = toString(start_year) + ' to ' + toString(end_year),
            c.label = toString(ordinal_num) +
                CASE
                    WHEN ordinal_num % 100 IN [11, 12, 13] THEN 'th'
                    WHEN ordinal_num % 10 = 1 THEN 'st'
                    WHEN ordinal_num % 10 = 2 THEN 'nd'
                    WHEN ordinal_num % 10 = 3 THEN 'rd'
                    ELSE 'th'
                END +
                ' Century ' + era
        RETURN count(c) AS c
        """,
    )
    millennia = run_scalar(
        session,
        """
        MATCH (y:Year)
        WITH DISTINCT toInteger(floor(toFloat(y.year) / 1000.0) * 1000) AS start_year
        MERGE (m:Millennium {start_year: start_year})
        WITH m, start_year, (start_year + 999) AS end_year,
             CASE
                 WHEN start_year < 0 THEN toInteger(abs(start_year) / 1000)
                 ELSE toInteger(start_year / 1000) + 1
             END AS ordinal_num,
             CASE WHEN start_year < 0 THEN 'BCE' ELSE 'CE' END AS era
        SET m.end_year = end_year,
            m.entity_type = 'Millennium',
            m.era = era,
            m.ordinal = ordinal_num,
            m.range_label = toString(start_year) + ' to ' + toString(end_year),
            m.label = toString(ordinal_num) +
                CASE
                    WHEN ordinal_num % 100 IN [11, 12, 13] THEN 'th'
                    WHEN ordinal_num % 10 = 1 THEN 'st'
                    WHEN ordinal_num % 10 = 2 THEN 'nd'
                    WHEN ordinal_num % 10 = 3 THEN 'rd'
                    ELSE 'th'
                END +
                ' Millennium ' + era
        RETURN count(m) AS c
        """,
    )
    print(f"  Decades touched: {decades}")
    print(f"  Centuries touched: {centuries}")
    print(f"  Millennia touched: {millennia}")

    print("\n[Apply] Wiring PART_OF hierarchy")
    y_to_d = run_scalar(
        session,
        """
        MATCH (y:Year)
        WITH y, toInteger(floor(toFloat(y.year) / 10.0) * 10) AS decade_start
        MATCH (d:Decade {start_year: decade_start})
        MERGE (y)-[r:PART_OF]->(d)
        RETURN count(r) AS c
        """,
    )
    d_to_c = run_scalar(
        session,
        """
        MATCH (d:Decade)
        WITH d, toInteger(floor(toFloat(d.start_year) / 100.0) * 100) AS century_start
        MATCH (c:Century {start_year: century_start})
        MERGE (d)-[r:PART_OF]->(c)
        RETURN count(r) AS c
        """,
    )
    c_to_m = run_scalar(
        session,
        """
        MATCH (c:Century)
        WITH c, toInteger(floor(toFloat(c.start_year) / 1000.0) * 1000) AS millennium_start
        MATCH (m:Millennium {start_year: millennium_start})
        MERGE (c)-[r:PART_OF]->(m)
        RETURN count(r) AS c
        """,
    )
    print(f"  Year->Decade PART_OF: {y_to_d}")
    print(f"  Decade->Century PART_OF: {d_to_c}")
    print(f"  Century->Millennium PART_OF: {c_to_m}")

    print("\n[Apply] Adding FOLLOWED_BY by granularity")
    d_follow = run_scalar(
        session,
        """
        MATCH (a:Decade), (b:Decade)
        WHERE b.start_year = a.start_year + 10
        MERGE (a)-[r:FOLLOWED_BY]->(b)
        RETURN count(r) AS c
        """,
    )
    c_follow = run_scalar(
        session,
        """
        MATCH (a:Century), (b:Century)
        WHERE b.start_year = a.start_year + 100
        MERGE (a)-[r:FOLLOWED_BY]->(b)
        RETURN count(r) AS c
        """,
    )
    m_follow = run_scalar(
        session,
        """
        MATCH (a:Millennium), (b:Millennium)
        WHERE b.start_year = a.start_year + 1000
        MERGE (a)-[r:FOLLOWED_BY]->(b)
        RETURN count(r) AS c
        """,
    )
    print(f"  Decade FOLLOWED_BY: {d_follow}")
    print(f"  Century FOLLOWED_BY: {c_follow}")
    print(f"  Millennium FOLLOWED_BY: {m_follow}")

    print("\n[Apply] Enforcing unidirectional temporal sequence (FOLLOWED_BY only)")
    dropped = run_scalar(session, "MATCH ()-[r:PRECEDED_BY]->() DELETE r RETURN count(r) AS c")
    print(f"  PRECEDED_BY deleted: {dropped}")


def main():
    parser = argparse.ArgumentParser(description="Migrate Neo4j temporal hierarchy levels")
    parser.add_argument("--uri", default="neo4j://127.0.0.1:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="Chrystallum")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes. Without this flag, run audit only.",
    )
    args = parser.parse_args()

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    try:
        with driver.session() as session:
            print("Connected:", args.uri)
            audit(session)
            if args.apply:
                apply_hierarchy(session)
                audit(session)
            else:
                print("\nAudit-only mode. Re-run with --apply to execute migration.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
