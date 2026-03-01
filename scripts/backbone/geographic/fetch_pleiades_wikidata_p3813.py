#!/usr/bin/env python3
"""
Fetch Wikidata QIDs for Pleiades IDs via P3813 (Pleiades ID property).

Wikidata property P3813 = "Pleiades ID". Enriches the crosswalk with more
pleiades_id -> wikidata_qid mappings for places not in pleiades-plus.

Input: List of pleiades_ids (from Place nodes, crosswalk, or CSV)
Output: CSV/geographic/pleiades_wikidata_p3813.csv (pleiades_id, qid, label)

Usage:
  python scripts/backbone/geographic/fetch_pleiades_wikidata_p3813.py
  python scripts/backbone/geographic/fetch_pleiades_wikidata_p3813.py --max-ids 500
  python scripts/backbone/geographic/fetch_pleiades_wikidata_p3813.py --pleiades-ids-csv path/to/ids.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import List, Set

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
USER_AGENT = "Chrystallum-Graph1/1.0 (fetch-pleiades-p3813)"


def _fetch_sparql(ids: List[str], *, timeout: int = 120, pause: float = 1.0) -> List[dict]:
    """Query Wikidata for ?item wdt:P3813 ?id for each pleiades_id."""
    if not ids:
        return []
    values = " ".join(f'"{i}"' for i in ids)
    query = f"""
    SELECT ?item ?id ?label WHERE {{
      VALUES ?id {{ {values} }}
      ?item wdt:P3813 ?id .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,la". }}
      OPTIONAL {{ ?item rdfs:label ?label . }}
    }}
    """
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(
        f"{WIKIDATA_SPARQL}?{params}",
        headers={"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    time.sleep(pause)
    out = []
    for b in data.get("results", {}).get("bindings", []):
        item = b.get("item", {}).get("value", "")
        qid = item.split("/")[-1] if "/" in item else ""
        pid = (b.get("id", {}).get("value", "") or "").strip()
        label = (b.get("label", {}).get("value", "") or "").strip()
        if qid and pid:
            out.append({"pleiades_id": pid, "qid": qid, "label": label})
    return out


def _collect_pleiades_ids(
    crosswalk_path: Path,
    places_csv_path: Path,
    *,
    exclude_in_crosswalk: bool = False,
    max_ids: int | None = None,
    from_neo4j: bool = False,
) -> List[str]:
    """Collect pleiades_ids from crosswalk, places CSV, and/or Neo4j."""
    in_crosswalk: Set[str] = set()
    if crosswalk_path.exists():
        with crosswalk_path.open("r", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                pid = (row.get("pleiades_id") or "").strip()
                if pid and (row.get("has_wikidata_match") or "").strip().lower() == "true":
                    in_crosswalk.add(pid)

    from_ids: Set[str] = set()
    if places_csv_path.exists():
        with places_csv_path.open("r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            col = "pleiades_id" if "pleiades_id" in (reader.fieldnames or []) else "id"
            for row in reader:
                pid = (row.get(col) or row.get("pleiades_id") or "").strip()
                if pid and pid.isdigit():
                    from_ids.add(pid)

    if from_neo4j:
        try:
            import os
            _scripts = Path(__file__).resolve().parents[2]
            if str(_scripts) not in sys.path:
                sys.path.insert(0, str(_scripts))
            from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD or ""))
            with driver.session() as s:
                r = s.run("MATCH (p:Place) WHERE p.pleiades_id IS NOT NULL RETURN p.pleiades_id AS pid")
                for rec in r:
                    pid = (rec.get("pid") or "").strip()
                    if pid and pid.isdigit():
                        from_ids.add(pid)
            driver.close()
        except Exception as e:
            print(f"Neo4j fallback failed: {e}", file=sys.stderr)

    if exclude_in_crosswalk:
        candidates = sorted(from_ids - in_crosswalk)
    else:
        candidates = sorted(from_ids | in_crosswalk)

    if max_ids and max_ids > 0:
        candidates = candidates[:max_ids]
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Wikidata QIDs for Pleiades IDs via P3813")
    parser.add_argument("--crosswalk", default="CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv")
    parser.add_argument("--places-csv", default="Geographic/pleiades_places.csv")
    parser.add_argument("--out-csv", default="CSV/geographic/pleiades_wikidata_p3813.csv")
    parser.add_argument("--exclude-in-crosswalk", action="store_true", help="Only fetch IDs not already in crosswalk")
    parser.add_argument("--from-neo4j", action="store_true", help="Use Place.pleiades_id from Neo4j when CSV missing")
    parser.add_argument("--max-ids", type=int, default=None, help="Limit number of IDs to query")
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    crosswalk_path = _PROJECT_ROOT / args.crosswalk
    places_path = _PROJECT_ROOT / args.places_csv
    out_path = _PROJECT_ROOT / args.out_csv

    ids = _collect_pleiades_ids(
        crosswalk_path, places_path,
        exclude_in_crosswalk=args.exclude_in_crosswalk,
        max_ids=args.max_ids,
        from_neo4j=args.from_neo4j or not places_path.exists(),
    )
    if not ids:
        print("No pleiades_ids to fetch. Check --places-csv and --crosswalk paths.")
        return 1

    print(f"Fetching P3813 for {len(ids)} pleiades_ids (batch_size={args.batch_size})...", flush=True)

    if args.dry_run:
        print(f"Would query batches: {len(ids) // args.batch_size + 1}")
        return 0

    seen: Set[tuple] = set()
    all_rows: List[dict] = []
    for i in range(0, len(ids), args.batch_size):
        batch = ids[i : i + args.batch_size]
        rows = _fetch_sparql(batch)
        for r in rows:
            key = (r["pleiades_id"], r["qid"])
            if key not in seen:
                seen.add(key)
                all_rows.append(r)
        print(f"  Batch {i // args.batch_size + 1}: {len(rows)} matches", flush=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["pleiades_id", "qid", "label"])
        w.writeheader()
        w.writerows(all_rows)

    print(f"Wrote {len(all_rows)} rows to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
