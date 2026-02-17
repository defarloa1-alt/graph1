#!/usr/bin/env python3
"""
Import enriched periods from PERIODS_GRAPH1_RANGE.csv into Neo4j.

Pipeline:
1. Create/refresh :PeriodCandidate staging nodes from CSV rows.
2. Triage fast-lane candidates with deterministic rules.
3. Link candidates to :Place nodes using region text/TGN matching.
4. Canonicalize eligible candidates into :Period:E4_Period nodes.
5. Link canonical periods to normalized regions.
"""

import argparse
import csv
import io
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase


if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


FAST_LANE_CATEGORIES = [
    "Historical Epoch",
    "Political-Dynastic",
    "Archaeological Age",
]


def parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def load_period_rows(csv_path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(csv_path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            periodo_ark = (row.get("ark_uri") or "").strip()
            label = (row.get("label") or "").strip()
            if not periodo_ark and not label:
                continue
            rows.append(
                {
                    "periodo_ark": periodo_ark,
                    "raw_label": label,
                    "raw_category": (row.get("category") or "").strip(),
                    "raw_region": (row.get("spatial_coverage") or "").strip(),
                    "begin_year": parse_int(row.get("start")),
                    "end_year": parse_int(row.get("stop")),
                }
            )
    return rows


def import_periods(
    uri: str = "bolt://localhost:7687",
    user: str = "neo4j",
    password: str = "Chrystallum",
    input_file: Optional[Path] = None,
) -> bool:
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent
    csv_path = input_file or (project_root / "Temporal" / "PERIODS_GRAPH1_RANGE.csv")

    print("=" * 80)
    print("Importing Enriched Periods to Neo4j")
    print("=" * 80)
    print(f"Input: {csv_path}")
    print(f"Neo4j: {uri}")
    print()

    if not csv_path.exists():
        print(f"ERROR: File not found: {csv_path}")
        return False

    rows = load_period_rows(csv_path)
    if not rows:
        print("No valid rows found in CSV.")
        return False

    print(f"Loaded {len(rows)} period rows")
    print()

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row
            MERGE (pc:PeriodCandidate {periodo_ark: row.periodo_ark})
            ON CREATE SET
                pc.created = datetime()
            SET
                pc.raw_label = row.raw_label,
                pc.raw_category = row.raw_category,
                pc.raw_region = row.raw_region,
                pc.begin_year = row.begin_year,
                pc.end_year = row.end_year,
                pc.source = 'PeriodO',
                pc.triage_status = 'PENDING',
                pc.normalization_needed = true,
                pc.updated = datetime()
            """,
            rows=rows,
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate)
            WHERE pc.raw_category IN $categories
              AND pc.begin_year IS NOT NULL
              AND pc.end_year IS NOT NULL
              AND pc.end_year >= pc.begin_year
            SET pc.triage_status = 'FAST_LANE'
            """,
            categories=FAST_LANE_CATEGORIES,
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate {triage_status: 'FAST_LANE'})
            MATCH (place:Place)
            WHERE pc.raw_region IS NOT NULL
              AND (
                   toLower(pc.raw_region) CONTAINS toLower(coalesce(place.label, ''))
                   OR (
                       place.getty_tgn IS NOT NULL
                       AND pc.raw_region CONTAINS toString(place.getty_tgn)
                   )
              )
            MERGE (pc)-[:REGION_CANDIDATE]->(place)
            """
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate {triage_status: 'FAST_LANE'})
            WHERE pc.normalization_needed = true
              AND pc.periodo_ark IS NOT NULL
              AND pc.periodo_ark <> ''
              AND EXISTS((pc)-[:REGION_CANDIDATE]->())
            MERGE (p:Period:E4_Period {periodo_ark: pc.periodo_ark})
            ON CREATE SET
                p.id = 'period_' + toLower(replace(coalesce(pc.raw_label, 'unknown'), ' ', '_')),
                p.created = datetime()
            SET
                p.label = pc.raw_label,
                p.begin_year = pc.begin_year,
                p.end_year = pc.end_year,
                p.period_type = pc.raw_category,
                p.authority_tier = 'PeriodO-Verified',
                p.confidence = 0.95,
                p.crm_class = 'E4_Period',
                p.updated = datetime()
            MERGE (pc)-[:CANONICALIZED_AS]->(p)
            SET pc.triage_status = 'CANONICALIZED'
            """
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate {triage_status: 'CANONICALIZED'})-[:CANONICALIZED_AS]->(p:Period)
            MATCH (pc)-[:REGION_CANDIDATE]->(place:Place)
            MERGE (p)-[:VALID_IN_REGION]->(place)
            """
        )

        stats = session.run(
            """
            RETURN
                count { MATCH (:PeriodCandidate) } AS candidates,
                count { MATCH (:PeriodCandidate {triage_status: 'FAST_LANE'}) } AS fast_lane,
                count { MATCH (:PeriodCandidate {triage_status: 'CANONICALIZED'}) } AS canonicalized_candidates,
                count { MATCH (:Period) } AS periods,
                count { MATCH (:Period)-[:VALID_IN_REGION]->(:Place) } AS region_links
            """
        ).single()

        print("=" * 80)
        print("Verification")
        print("=" * 80)
        print(f"PeriodCandidate nodes: {stats['candidates']}")
        print(f"FAST_LANE candidates: {stats['fast_lane']}")
        print(f"CANONICALIZED candidates: {stats['canonicalized_candidates']}")
        print(f"Period nodes: {stats['periods']}")
        print(f"VALID_IN_REGION relationships: {stats['region_links']}")

        sample = session.run(
            """
            MATCH (p:Period)
            WHERE p.label IS NOT NULL
            RETURN p.label AS label, p.begin_year AS begin_year, p.end_year AS end_year
            ORDER BY p.begin_year
            LIMIT 5
            """
        )
        print("\nSample periods:")
        for record in sample:
            print(f"  - {record['label']} ({record['begin_year']} to {record['end_year']})")

    driver.close()
    print("\nImport complete.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import enriched periods CSV to Neo4j.")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", default="Chrystallum", help="Neo4j password")
    parser.add_argument(
        "--input-file",
        default="",
        help="Optional path to PERIODS_GRAPH1_RANGE.csv (defaults to Temporal/PERIODS_GRAPH1_RANGE.csv)",
    )
    args = parser.parse_args()

    input_path = Path(args.input_file).resolve() if args.input_file else None
    ok = import_periods(
        uri=args.uri,
        user=args.user,
        password=args.password,
        input_file=input_path,
    )
    sys.exit(0 if ok else 1)
