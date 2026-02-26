#!/usr/bin/env python3
"""
Count entities with P1696 (Trismegistos) overlap — one SPARQL query instead of 6,989 API calls.

Uses member_of_edges.json to get entity QIDs, then queries Wikidata SPARQL for which have P1696.
Report: if under 500, run crosswalk now; if over 1,000, schedule with rate limiting.

Usage:
    python scripts/analysis/count_p1696_overlap.py
    python scripts/analysis/count_p1696_overlap.py --output output/analysis/p1696_qids.json
"""

import argparse
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "Chrystallum/1.0 (P1696 overlap count)"


def load_qids(edges_path: Path) -> list[str]:
    """Unique entity QIDs from member_of_edges.json."""
    with open(edges_path, encoding="utf-8") as f:
        edges = json.load(f)
    qids = set()
    for e in edges:
        q = e.get("entity_qid")
        if q and str(q).startswith("Q"):
            qids.add(str(q))
    return sorted(qids)


def build_sparql(qids: list[str]) -> str:
    """SPARQL to find which of our QIDs have P1696."""
    values = " ".join(f"wd:{q}" for q in qids)
    return f"""
SELECT ?item (SAMPLE(?tmid) AS ?tm) WHERE {{
  VALUES ?item {{ {values} }}
  ?item wdt:P1696 ?tmid .
}}
GROUP BY ?item
"""


def run_sparql_batched(qids: list[str], batch_size: int = 500) -> list[dict]:
    """Run SPARQL in batches to avoid timeout/limits."""
    all_rows = []
    for i in range(0, len(qids), batch_size):
        batch = qids[i : i + batch_size]
        query = build_sparql(batch)
        rows = run_sparql(query)
        all_rows.extend(rows)
        if (i + batch_size) < len(qids):
            import time
            time.sleep(1)  # Be nice to the endpoint
    return all_rows


def run_sparql(query: str) -> list[dict]:
    """Execute SPARQL against Wikidata."""
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    resp = requests.post(
        SPARQL_ENDPOINT,
        data={"query": query, "format": "json"},
        headers=headers,
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", {}).get("bindings", [])


def main():
    ap = argparse.ArgumentParser(description="Count entity QIDs with P1696 overlap")
    ap.add_argument("--edges", default="output/cluster_assignment/member_of_edges.json")
    ap.add_argument("--output", "-o", default=None, help="Write QID list to JSON")
    args = ap.parse_args()

    edges_path = ROOT / args.edges
    if not edges_path.exists():
        print(f"Error: {edges_path} not found", file=sys.stderr)
        sys.exit(1)

    qids = load_qids(edges_path)
    print(f"Entity QIDs in member_of_edges: {len(qids)}")

    if not qids:
        print("No QIDs to query.")
        sys.exit(0)

    print("Running SPARQL (P1696 overlap)...")
    try:
        rows = run_sparql_batched(qids)
    except Exception as e:
        print(f"SPARQL failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract QIDs from ?item (e.g. http://www.wikidata.org/entity/Q12345)
    with_p1696 = []
    for r in rows:
        uri = r.get("item", {}).get("value", "")
        if "/entity/" in uri:
            qid = uri.split("/entity/")[-1]
            with_p1696.append(qid)

    count = len(with_p1696)
    print(f"Entities with P1696: {count}")

    if count == 0:
        print("-> Defer crosswalk (no overlap in current entity set)")
    elif count < 500:
        print("-> Run crosswalk now (under 500)")
    elif count > 1000:
        print("-> Schedule as Phase A task with rate limiting (over 1,000)")
    else:
        print("-> Run crosswalk; monitor for rate limits (500-1,000)")

    if args.output:
        out_path = ROOT / args.output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"count": count, "qids": sorted(with_p1696)}, f, indent=2)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
