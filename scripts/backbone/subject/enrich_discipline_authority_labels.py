#!/usr/bin/env python3
"""
Enrich Discipline nodes with authority labels from LCSH, LCC, AAT, FAST APIs.

Fetches human-readable labels for lcsh_id, lcc, aat_id, fast_id and sets
lcsh_label, lcc_label, aat_label, fast_label on each Discipline node.

Usage:
  python scripts/backbone/subject/enrich_discipline_authority_labels.py
  python scripts/backbone/subject/enrich_discipline_authority_labels.py --limit 10 --dry-run
  # Chunked (e.g. 100 at a time): --skip 0 --limit 100, then --skip 100 --limit 100, ...
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

try:
    from neo4j import GraphDatabase
except ImportError:
    print("pip install neo4j", file=sys.stderr)
    sys.exit(1)

_PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT / "scripts"))
try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = None

USER_AGENT = "ChrystallumBot/1.0 (research project)"


def _first_preflabel(obj: dict, id_uri: str) -> str | None:
    """Extract prefLabel or authoritativeLabel from LoC JSON-LD graph."""
    for item in obj if isinstance(obj, list) else [obj]:
        if item.get("@id") == id_uri or (isinstance(id_uri, str) and id_uri in (item.get("@id") or "")):
            for key in (
                "http://www.w3.org/2004/02/skos/core#prefLabel",
                "http://www.loc.gov/mads/rdf/v1#authoritativeLabel",
                "http://www.w3.org/2000/01/rdf-schema#label",
            ):
                vals = item.get(key, [])
                if isinstance(vals, dict):
                    vals = [vals]
                for v in vals:
                    if isinstance(v, dict) and "@value" in v:
                        return v["@value"]
    return None


def fetch_lcsh_label(lcsh_id: str) -> str | None:
    """Fetch LCSH heading from id.loc.gov."""
    url = f"https://id.loc.gov/authorities/subjects/{lcsh_id}.json"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            uri = f"http://id.loc.gov/authorities/subjects/{lcsh_id}"
            return _first_preflabel(data, uri)
    except Exception:
        pass
    return None


def fetch_lcc_label(lcc_code: str) -> str | None:
    """Fetch LCC class label from id.loc.gov. Handles ranges (BP42-BP43) by using first part."""
    code = lcc_code.split("|")[0].strip().split("-")[0].strip()
    if not code:
        return None
    url = f"https://id.loc.gov/authorities/classification/{code}.json"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            uri = f"http://id.loc.gov/authorities/classification/{code}"
            label = _first_preflabel(data, uri)
            if label:
                return label
            # Try altLabel (full hierarchy string)
            for item in data if isinstance(data, list) else [data]:
                if item.get("@id") == uri:
                    for key in (
                        "http://www.w3.org/2004/02/skos/core#altLabel",
                        "http://www.w3.org/2000/01/rdf-schema#label",
                    ):
                        vals = item.get(key, [])
                        if isinstance(vals, dict):
                            vals = [vals]
                        for v in vals:
                            if isinstance(v, dict) and "@value" in v:
                                return v["@value"]
    except Exception:
        pass
    return None


def fetch_aat_label(aat_id: str) -> str | None:
    """Fetch AAT term from Getty vocab."""
    url = f"https://vocab.getty.edu/aat/{aat_id}.jsonld"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            return data.get("_label") or data.get("content")
    except Exception:
        pass
    return None


def fetch_fast_label(fast_id: str) -> str | None:
    """Fetch FAST heading from WorldCat Linked Data. Parses HTML for label."""
    url = f"http://id.worldcat.org/fast/{fast_id}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            text = r.text
            # Line after "SKOS Preferred Label" or "prefLabel" often has the value
            lines = text.replace("\r", "").split("\n")
            for i, line in enumerate(lines):
                if "prefLabel" in line.lower() or "Preferred Label" in line:
                    for j in range(i + 1, min(i + 4, len(lines))):
                        next_line = lines[j].strip()
                        # Strip HTML, bullets, dashes
                        next_line = re.sub(r"^[-–•]\s*", "", next_line)
                        next_line = re.sub(r"<[^>]+>", "", next_line).strip()
                        if next_line and 2 < len(next_line) < 150 and not next_line.startswith("http"):
                            return next_line
            m = re.search(r'property="name"[^>]*content="([^"]+)"', text)
            if m:
                return m.group(1).strip()
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Limit disciplines to enrich (0=all)")
    parser.add_argument("--skip", type=int, default=0, help="Skip first N nodes (for chunked runs)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    args = parser.parse_args()

    if not args.password:
        import getpass
        args.password = getpass.getpass("Neo4j password: ")

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    with driver.session() as session:
        q = "MATCH (d:Discipline) WHERE d.qid IS NOT NULL WITH d ORDER BY d.qid"
        if args.skip:
            q += f" SKIP {args.skip}"
        if args.limit:
            q += f" LIMIT {args.limit}"
        q += " RETURN d"
        r = session.run(q)
        disciplines = [record["d"] for record in r]

    print(f"Enriching {len(disciplines)} Discipline nodes...")

    updates = []
    for i, d in enumerate(disciplines):
        qid = d.get("qid", "")
        node_updates = {}

        if d.get("lcsh_id") and not d.get("lcsh_label"):
            first_id = (d["lcsh_id"] or "").split("|")[0].strip()
            if first_id:
                lbl = fetch_lcsh_label(first_id)
                if lbl:
                    node_updates["lcsh_label"] = lbl
                time.sleep(0.15)

        if d.get("lcc") and not d.get("lcc_label"):
            first_code = (d["lcc"] or "").split("|")[0].strip()
            if first_code:
                lbl = fetch_lcc_label(first_code)
                if lbl:
                    node_updates["lcc_label"] = lbl
                time.sleep(0.15)

        if d.get("aat_id") and not d.get("aat_label"):
            first_id = (d["aat_id"] or "").split("|")[0].strip()
            if first_id:
                lbl = fetch_aat_label(first_id)
                if lbl:
                    node_updates["aat_label"] = lbl
                time.sleep(0.15)

        if d.get("fast_id") and not d.get("fast_label"):
            first_id = (d["fast_id"] or "").split("|")[0].strip()
            if first_id:
                lbl = fetch_fast_label(first_id)
                if lbl:
                    node_updates["fast_label"] = lbl
                time.sleep(0.2)

        if node_updates:
            updates.append((qid, node_updates))

        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(disciplines)}")

    if args.dry_run:
        print(f"Would update {len(updates)} nodes")
        for qid, u in updates[:5]:
            print(f"  {qid}: {u}")
        if len(updates) > 5:
            print(f"  ... and {len(updates) - 5} more")
        driver.close()
        return

    with driver.session() as session:
        for qid, node_updates in updates:
            sets = ", ".join(f"d.{k} = ${k}" for k in node_updates)
            params = {"qid": qid, **node_updates}
            session.run(f"MATCH (d:Discipline {{qid: $qid}}) SET {sets}", params)

    print(f"Updated {len(updates)} Discipline nodes with authority labels")
    driver.close()


if __name__ == "__main__":
    main()
