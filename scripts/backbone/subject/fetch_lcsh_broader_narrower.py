#!/usr/bin/env python3
"""
Fetch LCSH broader/narrower terms from id.loc.gov and output BROADER_THAN edges.

For each lcsh_id in our master registry, fetches the heading from id.loc.gov
and extracts skos:broader, hasBroaderAuthority, and componentList (first element).
Only keeps LCSH-to-LCSH edges (id.loc.gov/authorities/subjects/).

Output:
  - output/lcsh_broader_than_edges.csv (child_lcsh_id, parent_lcsh_id)
  - output/lcsh_broader_than_edges.cypher (for Discipline nodes by lcsh_id)

Usage:
  python scripts/backbone/subject/fetch_lcsh_broader_narrower.py
  python scripts/backbone/subject/fetch_lcsh_broader_narrower.py --limit 50
"""

import argparse
import csv
import re
import sys
import time
from pathlib import Path

import requests

_PROJECT = Path(__file__).resolve().parents[3]
USER_AGENT = "ChrystallumBot/1.0 (research project)"
LCSH_BASE = "http://id.loc.gov/authorities/subjects/"
SKOS_BROADER = "http://www.w3.org/2004/02/skos/core#broader"
MADS_BROADER = "http://www.loc.gov/mads/rdf/v1#hasBroaderAuthority"
MADS_COMPONENT = "http://www.loc.gov/mads/rdf/v1#componentList"


def _extract_lcsh_id(uri: str) -> str | None:
    if not uri or not isinstance(uri, str):
        return None
    if LCSH_BASE in uri:
        return uri.split("/")[-1].split("#")[0]
    return None


def _extract_from_list(obj, key: str) -> list[str]:
    """Extract LCSH IDs from a property value (list of @id or single @id)."""
    ids = []
    val = obj.get(key, [])
    if isinstance(val, dict):
        val = [val]
    for item in val:
        if isinstance(item, dict):
            uri = item.get("@id")
        else:
            uri = item
        lid = _extract_lcsh_id(uri)
        if lid:
            ids.append(lid)
    return ids


def fetch_lcsh_broader(lcsh_id: str) -> list[str]:
    """Fetch broader LCSH IDs for a heading from id.loc.gov."""
    url = f"https://id.loc.gov/authorities/subjects/{lcsh_id}.json"
    broader = []
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code != 200:
            return []
        data = r.json()
        # Find the main entity (our lcsh_id)
        our_uri = f"{LCSH_BASE}{lcsh_id}"
        for item in data if isinstance(data, list) else [data]:
            if item.get("@id") == our_uri:
                broader.extend(_extract_from_list(item, SKOS_BROADER))
                broader.extend(_extract_from_list(item, MADS_BROADER))
                # componentList: first LCSH component is often the broader topic
                comp = item.get(MADS_COMPONENT, {})
                if isinstance(comp, dict) and "@list" in comp:
                    lst = comp["@list"]
                    if isinstance(lst, list) and lst:
                        first = lst[0]
                        uri = first.get("@id") if isinstance(first, dict) else first
                        lid = _extract_lcsh_id(uri)
                        if lid and lid not in broader:
                            broader.append(lid)
                break
    except Exception:
        pass
    return list(dict.fromkeys(broader))  # dedupe, preserve order


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, default=_PROJECT / "output" / "master_discipline_registry.csv")
    parser.add_argument("-o", "--output-dir", type=Path, default=_PROJECT / "output")
    parser.add_argument("--limit", type=int, default=0, help="Limit LCSH IDs to fetch (0=all)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        print("Run: python scripts/backbone/subject/build_master_discipline_registry.py")
        return

    lcsh_ids = []
    with open(args.input, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("master_id_type") == "lcsh_id":
                lcsh_ids.append(r["master_id"])
    if args.limit:
        lcsh_ids = lcsh_ids[: args.limit]
    print(f"Fetching broader terms for {len(lcsh_ids)} LCSH headings...")

    edges = []
    for i, lcsh_id in enumerate(lcsh_ids):
        parents = fetch_lcsh_broader(lcsh_id)
        for parent in parents:
            edges.append({"child_lcsh_id": lcsh_id, "parent_lcsh_id": parent})
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(lcsh_ids)}")
        time.sleep(0.15)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # CSV
    csv_path = args.output_dir / "lcsh_broader_than_edges.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["child_lcsh_id", "parent_lcsh_id"])
        w.writeheader()
        w.writerows(edges)
    print(f"Wrote {csv_path} ({len(edges)} edges)")

    # Cypher: (child:Discipline)-[:BROADER_THAN]->(parent:Discipline) when matched by lcsh_id
    cypher_path = args.output_dir / "lcsh_broader_than_edges.cypher"
    lines = [
        "// LCSH BROADER_THAN edges for Discipline nodes",
        "// Run after loading discipline_majors_mapped.csv",
        "// (parent)-[:BROADER_THAN]->(child) means parent is broader than child",
        "",
    ]
    for e in edges:
        child, parent = e["child_lcsh_id"], e["parent_lcsh_id"]
        lines.append(
            f"MATCH (child:Discipline) WHERE child.lcsh_id = '{child}' OR child.lcsh_id STARTS WITH '{child}|'"
        )
        lines.append(
            f"MATCH (parent:Discipline) WHERE parent.lcsh_id = '{parent}' OR parent.lcsh_id STARTS WITH '{parent}|'"
        )
        lines.append("MERGE (parent)-[:BROADER_THAN]->(child);")
        lines.append("")
    with open(cypher_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {cypher_path}")

    # Summary
    with_parent = len(set(e["child_lcsh_id"] for e in edges))
    print(f"\n{with_parent} LCSH headings have broader terms in our set")


if __name__ == "__main__":
    main()
