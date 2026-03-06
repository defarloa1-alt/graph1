#!/usr/bin/env python3
"""
Fix Place nodes where label is set to a QID or GeoNames ID instead of a real name.

Two passes:
  1. 70 nodes where label = qid  → fetch from Wikidata SPARQL (batch)
  2. 1,147 nodes where label = geonames_id → fetch from GeoNames API

Usage:
    python scripts/neo4j/fix_bad_labels.py --dry-run
    python scripts/neo4j/fix_bad_labels.py
    python scripts/neo4j/fix_bad_labels.py --geonames-user YOUR_USERNAME
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from neo4j import GraphDatabase

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")


def fetch_wikidata_labels(qids):
    """Fetch labels for a batch of QIDs via Wikidata SPARQL."""
    values = " ".join(f"wd:{q}" for q in qids)
    sparql = f"""
    SELECT ?item ?label WHERE {{
      VALUES ?item {{ {values} }}
      ?item rdfs:label ?label .
      FILTER(LANG(?label) = "en")
    }}
    """
    url = "https://query.wikidata.org/sparql"
    params = urllib.parse.urlencode({"query": sparql, "format": "json"})
    req = urllib.request.Request(f"{url}?{params}",
                                headers={"User-Agent": "Chrystallum/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    labels = {}
    for row in data["results"]["bindings"]:
        qid = row["item"]["value"].split("/")[-1]
        labels[qid] = row["label"]["value"]
    return labels


def fetch_geonames_name(geonames_id, username):
    """Fetch place name for a single GeoNames ID."""
    url = f"http://api.geonames.org/getJSON?geonameId={geonames_id}&username={username}"
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if "name" in data:
            return data["name"]
        if "status" in data:
            print(f"  [WARN] GeoNames API error for {geonames_id}: {data['status']}")
            return None
    except Exception as e:
        print(f"  [WARN] GeoNames API failed for {geonames_id}: {e}")
    return None


def main():
    parser = argparse.ArgumentParser(description="Fix bad labels on Place nodes")
    parser.add_argument("--dry-run", action="store_true", help="Report only")
    parser.add_argument("--geonames-user", default="demo",
                        help="GeoNames API username (default: demo, register at geonames.org)")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # --- Pass 1: QID labels via Wikidata ---
    print("=== Pass 1: Fix label = QID (Wikidata SPARQL) ===")
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Place) WHERE p.label = p.qid RETURN p.qid AS qid"
        )
        qids = [r["qid"] for r in result]

    print(f"  Found {len(qids)} nodes with label = qid")

    if qids:
        # Batch in groups of 50 for SPARQL
        wd_labels = {}
        for i in range(0, len(qids), 50):
            batch = qids[i:i+50]
            print(f"  Fetching Wikidata labels {i+1}-{i+len(batch)}...")
            batch_labels = fetch_wikidata_labels(batch)
            wd_labels.update(batch_labels)
            if i + 50 < len(qids):
                time.sleep(1)

        print(f"  Got {len(wd_labels)} labels from Wikidata")

        if not args.dry_run:
            with driver.session() as session:
                updated = 0
                for qid, label in wd_labels.items():
                    session.run(
                        "MATCH (p:Place {qid: $qid}) WHERE p.label = p.qid "
                        "SET p.label = $label, p.label_clean = $label",
                        qid=qid, label=label
                    )
                    updated += 1
                print(f"  [DONE] Updated {updated} labels from Wikidata")
        else:
            for qid, label in list(wd_labels.items())[:5]:
                print(f"    {qid} -> {label}")
            if len(wd_labels) > 5:
                print(f"    ... and {len(wd_labels) - 5} more")

    # --- Pass 2: GeoNames labels ---
    print()
    print("=== Pass 2: Fix label = geonames_id (GeoNames API) ===")
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Place) WHERE p.label = p.geonames_id "
            "RETURN p.geonames_id AS gid LIMIT 1200"
        )
        gids = [r["gid"] for r in result]

    print(f"  Found {len(gids)} nodes with label = geonames_id")

    if gids:
        if args.geonames_user == "demo":
            print("  [WARN] Using 'demo' username — limited to ~100 requests/day.")
            print("  Register at geonames.org and use --geonames-user YOUR_USERNAME")

        gn_labels = {}
        errors = 0
        for i, gid in enumerate(gids):
            if args.dry_run and i >= 5:
                break
            name = fetch_geonames_name(gid, args.geonames_user)
            if name:
                gn_labels[gid] = name
            else:
                errors += 1
            if (i + 1) % 100 == 0:
                print(f"  Fetched {i+1}/{len(gids)} ({errors} errors)...")
            # GeoNames rate limit: ~1 req/sec for free accounts
            time.sleep(0.5)

        print(f"  Got {len(gn_labels)} labels from GeoNames ({errors} errors)")

        if not args.dry_run:
            with driver.session() as session:
                updated = 0
                for gid, label in gn_labels.items():
                    session.run(
                        "MATCH (p:Place {geonames_id: $gid}) "
                        "WHERE p.label = p.geonames_id "
                        "SET p.label = $label, p.label_clean = $label",
                        gid=gid, label=label
                    )
                    updated += 1
                print(f"  [DONE] Updated {updated} labels from GeoNames")
        else:
            for gid, label in list(gn_labels.items())[:5]:
                print(f"    {gid} -> {label}")

    driver.close()
    print()
    print("Done.")


if __name__ == "__main__":
    main()
