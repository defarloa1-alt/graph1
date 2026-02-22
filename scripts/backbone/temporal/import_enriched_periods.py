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
import hashlib
import io
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase


if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


END_YEAR_CUTOFF = -2000
DEFAULT_UNIVERSAL_SPAN_THRESHOLD_YEARS = 1000

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


def period_span_years(begin_year: Optional[int], end_year: Optional[int]) -> Optional[int]:
    if begin_year is None or end_year is None:
        return None
    span = end_year - begin_year
    # Historical backbone uses no year 0.
    if begin_year < 0 < end_year:
        span -= 1
    return max(span, 0)


def classify_period_granularity(span_years: Optional[int], threshold_years: int) -> str:
    if span_years is None:
        return "unknown"
    return "universal" if span_years >= threshold_years else "granular"


def normalize_periodo_ark(value: Optional[str]) -> str:
    if value is None:
        return ""
    v = value.strip()
    if not v:
        return ""
    if v.startswith("https://n2t.net/ark:/99152/"):
        return "http://" + v[len("https://") :]
    if v.startswith("ark:/99152/"):
        return f"http://n2t.net/{v}"
    return v


def parse_ark_list(value: Optional[str]) -> List[str]:
    if value is None:
        return []
    text = value.strip()
    if not text:
        return []
    matches = re.findall(r"(?:https?://n2t\.net/)?ark:/99152/[A-Za-z0-9]+", text)
    out: List[str] = []
    for m in matches:
        normalized = normalize_periodo_ark(m)
        if normalized and normalized not in out:
            out.append(normalized)
    return out


def parse_qid(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    m = re.search(r"Q\d+", value)
    return m.group(0) if m else None


def year_iso(year: Optional[int]) -> Optional[str]:
    if year is None:
        return None
    sign = "-" if year < 0 else ""
    return f"{sign}{abs(year):04d}"


def period_token(periodo_ark: str) -> str:
    if not periodo_ark:
        return "unknown"
    token = periodo_ark.rsplit("/", 1)[-1]
    token = re.sub(r"[^a-zA-Z0-9]+", "_", token).strip("_")
    return token.lower() or "unknown"


def periodo_id_value(periodo_ark_or_id: Optional[str]) -> str:
    if not periodo_ark_or_id:
        return ""
    v = normalize_periodo_ark(periodo_ark_or_id)
    if not v:
        return ""
    if "ark:/99152/" in v:
        return v.rsplit("/", 1)[-1]
    return v.strip()


def normalize_label(raw_label: str, qid: Optional[str], periodo_ark: str) -> str:
    label = (raw_label or "").strip()
    if re.match(r"^https?://", label, flags=re.IGNORECASE):
        label = ""
    if qid and label.upper() == qid.upper():
        label = ""
    if label:
        return label
    if qid:
        return qid
    return f"PeriodO {period_token(periodo_ark).replace('_', ' ')}"


def split_geo_tokens(raw_region: str) -> List[str]:
    parts = re.split(r"\s*\|\s*|\s*,\s*|\s*;\s*|\s*/\s*", raw_region or "")
    out: List[str] = []
    seen = set()
    for p in parts:
        token = re.sub(r"\s+", " ", p).strip()
        if not token:
            continue
        key = token.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(token)
    return out


def canonical_period_signature(
    *,
    qid: Optional[str],
    periodo_ark: str,
    label: str,
    category: str,
    region: str,
    begin_year: int,
    end_year: int,
    authority_uri: str,
    source_label: str,
    publication_year: Optional[int],
    broader_arks: List[str],
    narrower_arks: List[str],
) -> str:
    parts = [
        qid or "",
        periodo_ark,
        label,
        category,
        region,
        str(begin_year),
        str(end_year),
        authority_uri,
        source_label,
        str(publication_year or ""),
        "|".join(sorted(broader_arks)),
        "|".join(sorted(narrower_arks)),
    ]
    return hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()[:16]


def load_periodo_qid_map(project_root: Path) -> Dict[str, str]:
    qid_map: Dict[str, str] = {}
    candidate_files = [
        project_root / "Temporal" / "periodo_wikidata_crosswalk.csv",
        project_root / "Temporal" / "wikidata_periodo_start_end_unique_items_2026-02-18.csv",
        project_root / "Temporal" / "wikidata_periodo_end_before_minus2000_2026-02-18.csv",
    ]
    for fp in candidate_files:
        if not fp.exists():
            continue
        try:
            with open(fp, "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    qid = parse_qid(row.get("wikidata_qid") or row.get("qid"))
                    if not qid:
                        continue
                    pid_raw = (
                        row.get("periodo_id")
                        or row.get("periodo_id_sample")
                        or row.get("period")
                        or row.get("ark_uri")
                        or row.get("periodo_ark")
                    )
                    pid = periodo_id_value(pid_raw)
                    if pid and pid not in qid_map:
                        qid_map[pid] = qid
        except Exception:
            continue
    return qid_map


def load_period_rows(
    csv_path: Path,
    qid_map: Optional[Dict[str, str]] = None,
    universal_span_threshold_years: int = DEFAULT_UNIVERSAL_SPAN_THRESHOLD_YEARS,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    qid_map = qid_map or {}
    with open(csv_path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            periodo_ark = normalize_periodo_ark(row.get("ark_uri") or row.get("period"))
            # Filter 1: must have PeriodO federation identifier.
            if not periodo_ark:
                continue
            pid = periodo_id_value(periodo_ark)
            qid = parse_qid(row.get("qid")) or qid_map.get(pid)
            label = normalize_label((row.get("label") or "").strip(), qid, periodo_ark)
            begin_year = parse_int(row.get("start"))
            end_year = parse_int(row.get("stop"))
            # Filter 2: must have both start/end years, and end must be before -2000.
            if begin_year is None or end_year is None or end_year >= END_YEAR_CUTOFF:
                continue
            # Filter 3: must have geography/spatial coverage.
            raw_region = (row.get("spatial_coverage") or "").strip()
            if not raw_region:
                continue
            geo_tokens = split_geo_tokens(raw_region)
            if not geo_tokens:
                continue
            start_iso = year_iso(begin_year)
            end_iso = year_iso(end_year)
            span_years = period_span_years(begin_year, end_year)
            granularity_class = classify_period_granularity(
                span_years, universal_span_threshold_years
            )
            token = period_token(periodo_ark)
            raw_category = (row.get("category") or "").strip() or "PeriodO"
            authority_uri = normalize_periodo_ark(row.get("authority"))
            source_label = (row.get("source") or "").strip()
            publication_year = parse_int(row.get("publication_year"))
            broader_arks = parse_ark_list(row.get("broader_periods"))
            narrower_arks = parse_ark_list(row.get("narrower_periods"))
            signature = canonical_period_signature(
                qid=qid,
                periodo_ark=periodo_ark,
                label=label,
                category=raw_category,
                region=raw_region,
                begin_year=begin_year,
                end_year=end_year,
                authority_uri=authority_uri,
                source_label=source_label,
                publication_year=publication_year,
                broader_arks=broader_arks,
                narrower_arks=narrower_arks,
            )
            entity_id = (
                f"prd_{qid.lower()}_{signature}"
                if qid
                else f"prd_periodo_{token}_{signature}"
            )
            rows.append(
                {
                    "periodo_ark": periodo_ark,
                    "periodo_id": pid,
                    "raw_label": label,
                    "raw_category": raw_category,
                    "raw_region": raw_region,
                    "geo_tokens": geo_tokens,
                    "begin_year": begin_year,
                    "end_year": end_year,
                    "span_years": span_years,
                    "granularity_class": granularity_class,
                    "start": start_iso,
                    "end": end_iso,
                    "start_date_min": f"{start_iso}-01-01" if start_iso else None,
                    "start_date_max": f"{start_iso}-12-31" if start_iso else None,
                    "end_date_min": f"{end_iso}-01-01" if end_iso else None,
                    "end_date_max": f"{end_iso}-12-31" if end_iso else None,
                    "broader_arks": broader_arks,
                    "narrower_arks": narrower_arks,
                    "authority_uri": authority_uri,
                    "source_label": source_label,
                    "publication_year": publication_year,
                    "wikidata_qid": qid,
                    "entity_id": entity_id,
                    "id_hash": signature,
                }
            )
    return rows


def import_periods(
    uri: str = "bolt://localhost:7687",
    user: str = "neo4j",
    password: str = "Chrystallum",
    database: str = "neo4j",
    input_file: Optional[Path] = None,
    universal_span_threshold_years: int = DEFAULT_UNIVERSAL_SPAN_THRESHOLD_YEARS,
) -> bool:
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent
    default_primary = project_root / "Temporal" / "PERIODS_GRAPH1_RANGE.csv"
    default_fallback = project_root / "Temporal" / "periodo-dataset.csv"
    if input_file:
        csv_path = input_file
    else:
        csv_path = default_primary if default_primary.exists() else default_fallback

    print("=" * 80)
    print("Importing Enriched Periods to Neo4j")
    print("=" * 80)
    print(f"Input: {csv_path}")
    print(f"Neo4j: {uri}")
    print(f"Database: {database}")
    print(f"Universal span threshold (years): {universal_span_threshold_years}")
    print()

    if not csv_path.exists():
        print(f"ERROR: File not found: {csv_path}")
        return False

    qid_map = load_periodo_qid_map(project_root)
    rows = load_period_rows(
        csv_path,
        qid_map=qid_map,
        universal_span_threshold_years=universal_span_threshold_years,
    )
    if not rows:
        print("No valid rows found in CSV.")
        return False

    print(f"Loaded {len(rows)} period rows")
    print(f"Supplemental PeriodO->QID mappings loaded: {len(qid_map)}")
    print()

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session(database=database) as session:
        session.run(
            """
            UNWIND $rows AS row
            MERGE (pc:PeriodCandidate {periodo_ark: row.periodo_ark})
            ON CREATE SET
                pc.created = datetime()
            SET
                pc.raw_label = row.raw_label,
                pc.periodo_id = row.periodo_id,
                pc.raw_category = row.raw_category,
                pc.raw_region = row.raw_region,
                pc.geo_tokens = row.geo_tokens,
                pc.begin_year = row.begin_year,
                pc.end_year = row.end_year,
                pc.span_years = row.span_years,
                pc.granularity_class = row.granularity_class,
                pc.start = row.start,
                pc.end = row.end,
                pc.start_date_min = row.start_date_min,
                pc.start_date_max = row.start_date_max,
                pc.end_date_min = row.end_date_min,
                pc.end_date_max = row.end_date_max,
                pc.earliest_start = row.start_date_min,
                pc.latest_start = row.start_date_max,
                pc.earliest_end = row.end_date_min,
                pc.latest_end = row.end_date_max,
                pc.broader_arks = row.broader_arks,
                pc.narrower_arks = row.narrower_arks,
                pc.authority_uri = row.authority_uri,
                pc.source_label = row.source_label,
                pc.publication_year = row.publication_year,
                pc.wikidata_qid = row.wikidata_qid,
                pc.entity_id = row.entity_id,
                pc.id_hash = row.id_hash,
                pc.source = 'PeriodO',
                pc.node_type = 'periodO_candidate',
                pc.temporal_tag = 'unknown',
                pc.triage_status = 'PENDING',
                pc.normalization_needed = true,
                pc.updated = datetime()
            """,
            rows=rows,
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate)
            WHERE pc.begin_year IS NOT NULL
              AND pc.end_year IS NOT NULL
              AND pc.end_year >= pc.begin_year
              AND pc.periodo_ark IS NOT NULL
              AND pc.raw_region IS NOT NULL
              AND size(coalesce(pc.geo_tokens, [])) > 0
            SET pc.triage_status = 'ELIGIBLE'
            """,
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate)
            UNWIND coalesce(pc.broader_arks, []) AS broader_ark
            MATCH (parent:PeriodCandidate {periodo_ark: broader_ark})
            MERGE (pc)-[:CANDIDATE_BROADER_THAN]->(parent)
            """
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate)
            UNWIND coalesce(pc.narrower_arks, []) AS narrower_ark
            MATCH (child:PeriodCandidate {periodo_ark: narrower_ark})
            MERGE (pc)-[:CANDIDATE_NARROWER_THAN]->(child)
            """
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate {triage_status: 'ELIGIBLE'})
            UNWIND coalesce(pc.geo_tokens, []) AS token
            WITH pc, trim(token) AS token
            WHERE token <> ''
            MERGE (gc:GeoCoverageCandidate {token_norm: toLower(token)})
            ON CREATE SET gc.created = datetime(), gc.source = 'PeriodO'
            SET gc.token = token, gc.updated = datetime(), gc.node_type = 'geo_coverage_candidate'
            MERGE (pc)-[:HAS_GEO_COVERAGE_CANDIDATE]->(gc)
            """
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate {triage_status: 'ELIGIBLE'})
            WHERE pc.normalization_needed = true
              AND pc.periodo_ark IS NOT NULL
              AND pc.periodo_ark <> ''
              AND pc.start IS NOT NULL
              AND pc.end IS NOT NULL
            MERGE (p:Period:E4_Period {periodo_ark: pc.periodo_ark})
            ON CREATE SET
                p.id = pc.entity_id,
                p.created = datetime()
            SET
                p.periodo_id = pc.periodo_id,
                p.entity_id = pc.entity_id,
                p.id_hash = pc.id_hash,
                p.label = pc.raw_label,
                p.start = pc.start,
                p.end = pc.end,
                p.begin_year = pc.begin_year,
                p.end_year = pc.end_year,
                p.span_years = pc.span_years,
                p.start_date_min = pc.start_date_min,
                p.start_date_max = pc.start_date_max,
                p.end_date_min = pc.end_date_min,
                p.end_date_max = pc.end_date_max,
                p.earliest_start = pc.earliest_start,
                p.latest_start = pc.latest_start,
                p.earliest_end = pc.earliest_end,
                p.latest_end = pc.latest_end,
                p.period_type = pc.raw_category,
                p.entity_type = 'Period',
                p.node_type = 'periodO',
                p.authority_tier = 'PeriodO-Verified',
                p.confidence = 0.95,
                p.crm_class = 'E4_Period',
                p.source = 'PeriodO',
                p.temporal_tag = coalesce(p.temporal_tag, 'unknown'),
                p.granularity_class = pc.granularity_class,
                p.granularity_rule = 'span_threshold_v1',
                p.granularity_threshold_years = $universal_span_threshold_years,
                p.authority_uri = pc.authority_uri,
                p.source_label = pc.source_label,
                p.publication_year = pc.publication_year,
                p.spatial_coverage_raw = pc.raw_region,
                p.qid = coalesce(pc.wikidata_qid, p.qid),
                p.updated = datetime()
            MERGE (pc)-[:CANONICALIZED_AS]->(p)
            SET pc.triage_status = 'CANONICALIZED'
            """
            ,
            universal_span_threshold_years=universal_span_threshold_years
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate {triage_status: 'CANONICALIZED'})-[:CANONICALIZED_AS]->(p:Period)
            MATCH (pc)-[:HAS_GEO_COVERAGE_CANDIDATE]->(gc:GeoCoverageCandidate)
            MERGE (p)-[:HAS_GEO_COVERAGE]->(gc)
            """
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate {triage_status: 'CANONICALIZED'})-[:CANONICALIZED_AS]->(p:Period)
            MATCH (ys:Year {year: pc.begin_year})
            MATCH (ye:Year {year: pc.end_year})
            MERGE (p)-[:STARTS_IN_YEAR]->(ys)
            MERGE (p)-[:ENDS_IN_YEAR]->(ye)
            """
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate)-[:CANONICALIZED_AS]->(p:Period)
            MATCH (pc)-[:CANDIDATE_BROADER_THAN]->(pc_parent:PeriodCandidate)-[:CANONICALIZED_AS]->(parent:Period)
            MERGE (p)-[:PART_OF]->(parent)
            MERGE (p)-[:SUB_PERIOD_OF]->(parent)
            MERGE (parent)-[:BROADER_THAN]->(p)
            MERGE (p)-[:NARROWER_THAN]->(parent)
            """
        )

        session.run(
            """
            MATCH (pc:PeriodCandidate)-[:CANONICALIZED_AS]->(p:Period)
            MATCH (pc)-[:CANDIDATE_NARROWER_THAN]->(pc_child:PeriodCandidate)-[:CANONICALIZED_AS]->(child:Period)
            MERGE (p)-[:BROADER_THAN]->(child)
            MERGE (child)-[:NARROWER_THAN]->(p)
            MERGE (child)-[:PART_OF]->(p)
            MERGE (child)-[:SUB_PERIOD_OF]->(p)
            """
        )

        stats = session.run(
            """
            RETURN
                count { MATCH (:PeriodCandidate) } AS candidates,
                count { MATCH (:PeriodCandidate {triage_status: 'ELIGIBLE'}) } AS eligible,
                count { MATCH (:PeriodCandidate {triage_status: 'CANONICALIZED'}) } AS canonicalized_candidates,
                count { MATCH (:Period) } AS periods,
                count { MATCH (:Period)-[:HAS_GEO_COVERAGE]->(:GeoCoverageCandidate) } AS geo_links,
                count { MATCH (:Period)-[:STARTS_IN_YEAR]->(:Year) } AS starts_in_year,
                count { MATCH (:Period)-[:ENDS_IN_YEAR]->(:Year) } AS ends_in_year,
                count { MATCH (:Period)-[:PART_OF]->(:Period) } AS part_of_links,
                count { MATCH (:Period)-[:BROADER_THAN]->(:Period) } AS broader_links,
                count { MATCH (:Period)-[:NARROWER_THAN]->(:Period) } AS narrower_links,
                count { MATCH (:Period)-[:SUB_PERIOD_OF]->(:Period) } AS sub_period_links
            """
        ).single()

        print("=" * 80)
        print("Verification")
        print("=" * 80)
        print(f"PeriodCandidate nodes: {stats['candidates']}")
        print(f"ELIGIBLE candidates: {stats['eligible']}")
        print(f"CANONICALIZED candidates: {stats['canonicalized_candidates']}")
        print(f"Period nodes: {stats['periods']}")
        print(f"HAS_GEO_COVERAGE relationships: {stats['geo_links']}")
        print(f"STARTS_IN_YEAR relationships: {stats['starts_in_year']}")
        print(f"ENDS_IN_YEAR relationships: {stats['ends_in_year']}")
        print(f"PART_OF relationships: {stats['part_of_links']}")
        print(f"BROADER_THAN relationships: {stats['broader_links']}")
        print(f"NARROWER_THAN relationships: {stats['narrower_links']}")
        print(f"SUB_PERIOD_OF relationships: {stats['sub_period_links']}")

        sample = session.run(
            """
            MATCH (p:Period)
            WHERE p.label IS NOT NULL
            RETURN p.label AS label, p.start_date_min AS start_date_min, p.end_date_max AS end_date_max, p.node_type AS node_type
            ORDER BY p.begin_year
            LIMIT 5
            """
        )
        print("\nSample periods:")
        for record in sample:
            print(f"  - {record['label']} ({record['start_date_min']} to {record['end_date_max']}) [{record['node_type']}]")

    driver.close()
    print("\nImport complete.")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import enriched periods CSV to Neo4j.")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", default="Chrystallum", help="Neo4j password")
    parser.add_argument("--database", default="neo4j", help="Neo4j database name")
    parser.add_argument(
        "--input-file",
        default="",
        help="Optional path to PERIODS_GRAPH1_RANGE.csv (defaults to Temporal/PERIODS_GRAPH1_RANGE.csv)",
    )
    parser.add_argument(
        "--universal-span-threshold",
        type=int,
        default=DEFAULT_UNIVERSAL_SPAN_THRESHOLD_YEARS,
        help="Threshold in years for classifying period granularity as universal vs granular.",
    )
    args = parser.parse_args()

    input_path = Path(args.input_file).resolve() if args.input_file else None
    ok = import_periods(
        uri=args.uri,
        user=args.user,
        password=args.password,
        database=args.database,
        input_file=input_path,
        universal_span_threshold_years=args.universal_span_threshold,
    )
    sys.exit(0 if ok else 1)
