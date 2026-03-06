#!/usr/bin/env python3
"""
survey_dprr_from_graph.py
─────────────────────────
Phase 0a (re-run): DPRR survey sourced from the local Neo4j graph.

The original survey_dprr.py queries the DPRR SPARQL endpoint, which is
blocked by Anubis/within.website bot protection. This script reads the
same data from the local Neo4j graph (already imported via dprr_import.py)
and emits a FederationSurvey in the standard Phase 0 format.

SELF-DEFINING GRAPH CONTRACT
─────────────────────────────
Survey parameters are read from the graph, not hardcoded:
  MATCH (fs:SYS_FederationSource {source_id: 'dprr'})
  RETURN fs.domain_start_year, fs.domain_end_year,
         fs.pleiades_spatial_anchor

After the survey completes, the script updates the SYS_FederationSource node:
  - survey_status:    'complete'
  - last_surveyed:    <ISO timestamp>
  - survey_node_count: <count>

This makes the survey provenance visible to agents querying the graph.

Usage:
  python scripts/backbone/subject/survey_dprr_from_graph.py
  python scripts/backbone/subject/survey_dprr_from_graph.py --dry-run
  python scripts/backbone/subject/survey_dprr_from_graph.py --out output/nodes/dprr_roman_republic.json
"""
import argparse
import sys
import io
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_ROOT    = Path(__file__).resolve().parents[3]
_SCRIPTS = Path(__file__).resolve().parents[2]
for p in [str(_SCRIPTS), str(_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase
from scripts.federation_node_schema import (
    Federation,
    FederationSurvey,
    new_node,
    new_survey,
    validate_survey,
)

DOMAIN           = "roman_republic"
OUT_DEFAULT      = _ROOT / "output" / "nodes" / "dprr_roman_republic.json"
PLEIADES_ROMA    = "https://pleiades.stoa.org/places/423025"   # fallback


def load_survey_config(session) -> dict:
    """
    Read survey parameters from SYS_FederationSource {source_id: 'dprr'}.
    Returns dict with keys: domain_start_year, domain_end_year, pleiades_spatial_anchor.
    Falls back to hardcoded defaults if graph node is missing fields.
    """
    result = session.run("""
        MATCH (fs:SYS_FederationSource {source_id: 'dprr'})
        RETURN fs.domain_start_year    AS start_year,
               fs.domain_end_year      AS end_year,
               fs.pleiades_spatial_anchor AS spatial_anchor,
               fs.survey_strategy      AS strategy
    """)
    rec = result.single()
    if rec:
        return {
            "start_year":      rec["start_year"]     or -509,
            "end_year":        rec["end_year"]        or -27,
            "spatial_anchor":  rec["spatial_anchor"]  or PLEIADES_ROMA,
            "strategy":        rec["strategy"]        or "graph_query",
        }
    print("[WARN] SYS_FederationSource {source_id: 'dprr'} not found — using defaults",
          file=sys.stderr)
    return {"start_year": -509, "end_year": -27,
            "spatial_anchor": PLEIADES_ROMA, "strategy": "graph_query"}


def mark_survey_running(session) -> None:
    session.run("""
        MATCH (fs:SYS_FederationSource {source_id: 'dprr'})
        SET fs.survey_status = 'running',
            fs.last_surveyed = $ts
    """, ts=datetime.now(timezone.utc).isoformat())


def mark_survey_complete(session, node_count: int) -> None:
    session.run("""
        MATCH (fs:SYS_FederationSource {source_id: 'dprr'})
        SET fs.survey_status     = 'complete',
            fs.survey_node_count = $n,
            fs.last_surveyed     = $ts
    """, n=node_count, ts=datetime.now(timezone.utc).isoformat())


def query_post_assertions(session, start_year: int, end_year: int) -> list[dict]:
    """
    Return POSITION_HELD data from Neo4j.
    Each row: {post_uri, person_uri, position_id, position_label, year_start, year_end}
    Filtered to year_start within [start_year, end_year].
    """
    result = session.run("""
        MATCH (e:Entity)-[r:POSITION_HELD]->(p:Position)
        WHERE (r.start_year IS NOT NULL OR r.year IS NOT NULL)
          AND toInteger(coalesce(r.start_year, r.year)) >= $start_year
          AND toInteger(coalesce(r.start_year, r.year)) <= $end_year
        RETURN r.dprr_assertion_uri  AS post_uri,
               e.dprr_uri            AS person_uri,
               e.entity_id           AS entity_id,
               p.label               AS position_id,
               p.label_name          AS position_label,
               toInteger(coalesce(r.start_year, r.year)) AS year_start,
               toInteger(coalesce(r.end_year, r.start_year, r.year)) AS year_end
        ORDER BY year_start, r.dprr_assertion_uri
    """, start_year=start_year, end_year=end_year)
    return [dict(rec) for rec in result]


def build_survey(rows: list[dict], config: dict) -> FederationSurvey:
    spatial_anchor = config["spatial_anchor"]

    survey = new_survey(
        Federation.DPRR,
        DOMAIN,
        seed_id="graph",
        seed_label="DPRR PostAssertions (from Neo4j graph)",
        meta={
            "source":       "neo4j_graph",
            "strategy":     config["strategy"],
            "domain_range": f"{config['start_year']} to {config['end_year']}",
            "note":         "Years from DPRR Turtle hasDateStart/hasDateEnd via dprr_post_years.json",
        },
    )

    seen_post_uris: set[str] = set()
    skipped = 0

    for row in rows:
        post_uri = row.get("post_uri") or ""

        # Deduplicate on post URI
        if post_uri and post_uri in seen_post_uris:
            skipped += 1
            continue
        if post_uri:
            seen_post_uris.add(post_uri)

        # Build stable node id from post URI or entity+position+year
        if post_uri:
            node_id = post_uri.split("/")[-1]
        else:
            node_id = f"{row.get('entity_id','?')}_{row.get('position_id','?')}_{row.get('year_start','?')}"

        year_start = row.get("year_start")
        year_end   = row.get("year_end") or year_start

        pos_label  = row.get("position_label") or row.get("position_id") or "?"
        person_uri = (row.get("person_uri")
                      or f"http://romanrepublic.ac.uk/rdf/entity/Person/{row.get('entity_id','?')}")

        node = new_node(
            id             = node_id,
            label          = pos_label,
            federation     = Federation.DPRR,
            domain         = DOMAIN,
            uri            = post_uri,
            depth          = 0,
            is_seed        = False,
            spatial_anchor = spatial_anchor,
            temporal_range = (year_start, year_end) if year_start is not None else None,
            person_ref     = person_uri,
            properties     = {
                "position_id":    str(row.get("position_id", "")),
                "position_label": pos_label,
                "year_start":     year_start,
                "year_end":       year_end,
                "post_uri":       post_uri,
                "entity_id":      row.get("entity_id", ""),
            },
        )
        survey.add_node(node)

    if skipped:
        print(f"  [info] {skipped} duplicate post URIs skipped")
    return survey


def run(out_path: Path, dry_run: bool = False) -> int:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # 1. Read config from graph (self-defining)
        config = load_survey_config(session)
        print(f"[dprr-survey] Config from graph: range={config['start_year']} to {config['end_year']}, "
              f"anchor={config['spatial_anchor']}")

        if not dry_run:
            mark_survey_running(session)

        # 2. Query PostAssertions
        print(f"[dprr-survey] Querying POSITION_HELD in range...")
        rows = query_post_assertions(session, config["start_year"], config["end_year"])
        print(f"[dprr-survey] {len(rows)} PostAssertion rows")

        # 3. Build survey
        survey = build_survey(rows, config)
        print(f"[dprr-survey] {survey.node_count} survey nodes built")

        for w in validate_survey(survey):
            print(f"  [WARN] {w}", file=sys.stderr)

        # 4. Update graph provenance
        if not dry_run:
            mark_survey_complete(session, survey.node_count)
            print(f"[dprr-survey] Graph updated: survey_status=complete, node_count={survey.node_count}")

    driver.close()

    # 5. Write output
    if dry_run:
        s = survey.summary()
        print(f"[DRY RUN] Would write {survey.node_count} nodes to {out_path}")
        print(f"  survivors={s['survivors']} ({s['survival_rate']*100:.1f}%)")
        print(f"  field_coverage={s['field_coverage']}")
    else:
        survey.save(out_path)

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="DPRR survey from local Neo4j graph (bypasses blocked SPARQL endpoint)"
    )
    parser.add_argument("--out", type=Path, default=OUT_DEFAULT,
                        help=f"Output path (default: {OUT_DEFAULT})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be written without saving")
    args = parser.parse_args()
    return run(args.out, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
