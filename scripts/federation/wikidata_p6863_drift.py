#!/usr/bin/env python3
"""
Wikidata P6863 drift detection — OPS-001 Section 6.

While the DPRR SPARQL endpoint is blocked, changes to the DPRR corpus can be
partially detected via Wikidata through P6863 (DPRR person ID). Run periodically
against the Wikidata SPARQL endpoint.

Detects: New Wikidata items with P6863 set after snapshot date; changes to
existing items. Does NOT detect: New DPRR persons without Wikidata alignment;
DPRR assertion corrections not yet in Wikidata.

Usage:
    python scripts/federation/wikidata_p6863_drift.py
    python scripts/federation/wikidata_p6863_drift.py --since 2026-02-25
    python scripts/federation/wikidata_p6863_drift.py --out output/federation/p6863_drift.json
"""

import argparse
import json
import sys
from pathlib import Path

import requests

_scripts = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_scripts))
try:
    from config_loader import WIKIDATA_SPARQL_ENDPOINT
except ImportError:
    WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

USER_AGENT = "Chrystallum/1.0 (DPRR federation drift detection)"
DEFAULT_SINCE = "2026-02-25T00:00:00Z"


def run_drift_query(since: str, timeout: int = 60) -> list[dict]:
    sparql = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX schema: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?person ?dprr_id ?label ?modified WHERE {{
      ?person wdt:P6863 ?dprr_id .
      ?person rdfs:label ?label FILTER(lang(?label) = "en") .
      ?person schema:dateModified ?modified .
      FILTER(?modified > "{since}"^^xsd:dateTime)
    }}
    ORDER BY DESC(?modified)
    """
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    r = requests.get(
        WIKIDATA_SPARQL_ENDPOINT,
        params={"query": sparql},
        headers=headers,
        timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()
    bindings = data.get("results", {}).get("bindings", [])

    rows = []
    for b in bindings:
        person = b.get("person", {}).get("value", "")
        qid = person.split("/")[-1] if person else ""
        dprr_id = b.get("dprr_id", {}).get("value", "")
        label = b.get("label", {}).get("value", "")
        modified = b.get("modified", {}).get("value", "")
        rows.append({"qid": qid, "dprr_id": dprr_id, "label": label, "modified": modified})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Wikidata P6863 drift detection (OPS-001)")
    ap.add_argument("--since", default=DEFAULT_SINCE, help="Filter items modified after this (xsd:dateTime)")
    ap.add_argument("--out", default=None, help="Write JSON report to path")
    args = ap.parse_args()

    since = args.since
    if "T" not in since:
        since = f"{since}T00:00:00Z"

    print("Wikidata P6863 drift detection")
    print(f"  Since: {since}")
    print()

    try:
        rows = run_drift_query(since)
    except requests.RequestException as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    report = {"since": since, "count": len(rows), "items": rows}

    if rows:
        print(f"  {len(rows)} Wikidata item(s) with P6863 modified since snapshot:")
        for r in rows[:20]:
            print(f"    {r['qid']} | dprr:{r['dprr_id']} | {r['label'][:40]} | {r['modified']}")
        if len(rows) > 20:
            print(f"    ... and {len(rows) - 20} more")
    else:
        print("  No drift detected (no P6863 items modified since snapshot)")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n  Report: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
