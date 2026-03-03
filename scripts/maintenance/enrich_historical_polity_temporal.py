#!/usr/bin/env python3
"""
OI-007-10: Populate inception_year / dissolution_year on :HistoricalPolity nodes.

Fetches P571 (inception) and P576 (dissolved/abolished) from Wikidata for each
:HistoricalPolity node. Parses year from Wikidata time format (+YYYY-MM-DD or
-YYYY for BCE). Creates STARTS_IN_YEAR and ENDS_IN_YEAR edges to Year backbone.

Usage:
  python scripts/maintenance/enrich_historical_polity_temporal.py           # dry-run
  python scripts/maintenance/enrich_historical_polity_temporal.py --execute
"""
import argparse
import os
import re
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass

import requests
from neo4j import GraphDatabase

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
USER_AGENT = "Chrystallum/1.0 (polity temporal enrichment)"


def _parse_wikidata_year(value: str) -> int | None:
    """Parse Wikidata time value to integer year. BCE = negative."""
    if not value:
        return None
    # Format: -0508-01-01T00:00:00Z (BCE) or 0754-01-01T00:00:00Z (CE, no +)
    m = re.match(r"([+-]?)(\d{4})", value)
    if not m:
        return None
    sign, year_str = m.group(1), m.group(2)
    year = int(year_str)
    return -year if sign == "-" else year


def _query_wikidata(sparql: str) -> list[dict]:
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    r = requests.get(WIKIDATA_SPARQL, params={"query": sparql}, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data.get("results", {}).get("bindings", [])


def main() -> int:
    ap = argparse.ArgumentParser(description="OI-007-10: Enrich HistoricalPolity temporal")
    ap.add_argument("--execute", action="store_true", help="Write to graph (default: dry-run)")
    ap.add_argument("--debug", action="store_true", help="Print Wikidata raw values per polity")
    args = ap.parse_args()

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    if not password:
        print("NEO4J_PASSWORD required")
        return 1

    driver = GraphDatabase.driver(uri, auth=(user, password))
    db = os.getenv("NEO4J_DATABASE", "neo4j")

    # 1. Fetch :HistoricalPolity nodes with qid
    with driver.session(database=db) as session:
        r = session.run("""
            MATCH (n:HistoricalPolity)
            WHERE n.qid IS NOT NULL
            RETURN n.qid AS qid, n.label AS label,
                   n.inception_year AS inception_year,
                   n.dissolution_year AS dissolution_year
        """)
        polities = [dict(rec) for rec in r]

    if not polities:
        print("OI-007-10: No :HistoricalPolity nodes with qid found")
        driver.close()
        return 0

    qids = [p["qid"] for p in polities]
    polity_by_qid = {p["qid"]: p for p in polities}

    # 2. SPARQL: P571 and P576 for these QIDs
    values_clause = " ".join(f"wd:{q}" for q in qids)
    sparql = f"""
    SELECT ?item ?inception ?dissolved WHERE {{
      VALUES ?item {{ {values_clause} }}
      OPTIONAL {{ ?item wdt:P571 ?inception . }}
      OPTIONAL {{ ?item wdt:P576 ?dissolved . }}
    }}
    """
    print("OI-007-10: Enrich HistoricalPolity inception_year / dissolution_year")
    print(f"  Polities to enrich: {len(polities)}")
    print(f"  Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")

    try:
        rows = _query_wikidata(sparql)
    except Exception as e:
        print(f"  Wikidata SPARQL error: {e}")
        driver.close()
        return 1

    # Build qid -> best Wikidata row (dedupe if multiple rows per item)
    wd_by_qid: dict[str, dict] = {}
    for b in rows:
        item_uri = b.get("item", {}).get("value", "")
        qid = item_uri.split("/")[-1] if "/" in item_uri else ""
        if not qid or qid not in polity_by_qid:
            continue
        inc_val = b.get("inception", {}).get("value", "")
        dis_val = b.get("dissolved", {}).get("value", "")
        inc_year = _parse_wikidata_year(inc_val)
        dis_year = _parse_wikidata_year(dis_val)
        wd_by_qid[qid] = {"inc_val": inc_val, "dis_val": dis_val, "inc_year": inc_year, "dis_year": dis_year}

    updates = {}
    for qid, wd in wd_by_qid.items():
        p = polity_by_qid[qid]
        inc_year, dis_year = wd["inc_year"], wd["dis_year"]
        needs_update = False
        if inc_year is not None and p.get("inception_year") is None:
            needs_update = True
        if dis_year is not None and p.get("dissolution_year") is None:
            needs_update = True
        if needs_update and (inc_year is not None or dis_year is not None):
            updates[qid] = {"qid": qid, "label": p.get("label"), "inception_year": inc_year, "dissolution_year": dis_year}
    updates = list(updates.values())

    if args.debug:
        print("\n  [DEBUG] Wikidata vs graph per polity:")
        for p in polities:
            qid = p["qid"]
            wd = wd_by_qid.get(qid, {})
            inc_val = wd.get("inc_val", "(no row)")
            dis_val = wd.get("dis_val", "(no row)")
            inc_year = wd.get("inc_year")
            dis_year = wd.get("dis_year")
            g_inc = p.get("inception_year")
            g_dis = p.get("dissolution_year")
            action = "UPDATE" if qid in {u["qid"] for u in updates} else "skip"
            print(f"    {qid} {p.get('label','')[:30]:<30} | graph: inc={g_inc} dis={g_dis} | wd_raw: P571={inc_val!r} P576={dis_val!r} | parsed: inc={inc_year} dis={dis_year} | {action}")
        print()

    print(f"  Wikidata returned: {len(rows)} rows")
    print(f"  Nodes to update: {len(updates)}")
    for u in updates[:10]:
        print(f"    {u['qid']} {u.get('label','')}: inception={u['inception_year']}, dissolution={u['dissolution_year']}")
    if len(updates) > 10:
        print(f"    ... and {len(updates) - 10} more")

    if args.execute:
        with driver.session(database=db) as session:
            for u in updates:
                session.run("""
                    MATCH (n:HistoricalPolity {qid: $qid})
                    SET n.inception_year = COALESCE(n.inception_year, $inception_year),
                        n.dissolution_year = COALESCE(n.dissolution_year, $dissolution_year)
                """, qid=u["qid"], inception_year=u["inception_year"], dissolution_year=u["dissolution_year"])
            print(f"  Updated {len(updates)} nodes")

    # 3. Tie to temporal backbone: STARTS_IN_YEAR, ENDS_IN_YEAR -> Year nodes
    with driver.session(database=db) as session:
        r = session.run("""
            MATCH (n:HistoricalPolity)
            WHERE n.inception_year IS NOT NULL OR n.dissolution_year IS NOT NULL
            RETURN n.qid AS qid, n.inception_year AS inc, n.dissolution_year AS dis
        """)
        to_link = [dict(rec) for rec in r]

    print(f"  Polities to link to Year backbone: {len(to_link)}")

    if args.execute and to_link:
        with driver.session(database=db) as session:
            starts = ends = 0
            for p in to_link:
                if p.get("inc") is not None:
                    r = session.run("""
                        MATCH (n:HistoricalPolity {qid: $qid})
                        MERGE (y:Year {year: $year})
                        MERGE (n)-[:STARTS_IN_YEAR]->(y)
                        RETURN 1 AS c
                    """, qid=p["qid"], year=p["inc"]).single()
                    if r:
                        starts += 1
                if p.get("dis") is not None:
                    r = session.run("""
                        MATCH (n:HistoricalPolity {qid: $qid})
                        MERGE (y:Year {year: $year})
                        MERGE (n)-[:ENDS_IN_YEAR]->(y)
                        RETURN 1 AS c
                    """, qid=p["qid"], year=p["dis"]).single()
                    if r:
                        ends += 1
            print(f"  Backbone links: STARTS_IN_YEAR={starts}, ENDS_IN_YEAR={ends}")

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
