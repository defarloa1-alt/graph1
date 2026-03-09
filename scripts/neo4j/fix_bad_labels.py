#!/usr/bin/env python3
"""
Fix Place nodes where label is set to a QID or GeoNames ID instead of a real name.

Two passes:
  1. Nodes where label = qid  -> fetch from Wikidata SPARQL (batch)
  2. Nodes where label = geonames_id -> lookup from:
     a) CSV/geographic/geonames_labels_cache_v1.json (local cache)
     b) Geographic/geonames_allCountries.zip (GeoNames dump, col 0=id, col 1=name)
        Auto-downloads ~1.5 GB if not present.

Usage:
    python scripts/neo4j/fix_bad_labels.py --dry-run
    python scripts/neo4j/fix_bad_labels.py
    python scripts/neo4j/fix_bad_labels.py --skip-download   # skip allCountries if missing
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
import zipfile
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

GEONAMES_CACHE = ROOT / "CSV" / "geographic" / "geonames_labels_cache_v1.json"
GEONAMES_ZIP = ROOT / "Geographic" / "geonames_allCountries.zip"
GEONAMES_ZIP_URL = "http://download.geonames.org/export/dump/allCountries.zip"


# ── Wikidata SPARQL ──────────────────────────────────────────────────────────

def fetch_wikidata_labels(qids):
    """Fetch English labels for a batch of QIDs via Wikidata SPARQL."""
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


# ── GeoNames dump lookup ─────────────────────────────────────────────────────

def load_geonames_cache():
    """Load the local JSON cache if it exists."""
    if GEONAMES_CACHE.exists():
        with open(GEONAMES_CACHE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def download_geonames_zip():
    """Download allCountries.zip (~1.5 GB)."""
    GEONAMES_ZIP.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Downloading {GEONAMES_ZIP_URL} (~1.5 GB)...")
    req = urllib.request.Request(GEONAMES_ZIP_URL,
                                headers={"User-Agent": "Chrystallum-Graph1/1.0"})
    with urllib.request.urlopen(req, timeout=3600) as resp:
        GEONAMES_ZIP.write_bytes(resp.read())
    print(f"  Saved to {GEONAMES_ZIP}")


def lookup_geonames_from_zip(target_ids):
    """
    Stream allCountries.txt from zip, extracting names only for target IDs.
    Returns dict {geonames_id: name}.
    """
    if not GEONAMES_ZIP.exists():
        return {}

    target_set = set(target_ids)
    labels = {}
    count = 0

    with zipfile.ZipFile(GEONAMES_ZIP, "r") as zf:
        txt_name = next((n for n in zf.namelist() if n.lower().endswith(".txt")), None)
        if not txt_name:
            print("  [WARN] No .txt file found in zip")
            return {}

        print(f"  Streaming {txt_name} for {len(target_set)} IDs...")
        with zf.open(txt_name, "r") as fh:
            for raw in fh:
                count += 1
                if count % 5_000_000 == 0:
                    print(f"    ...scanned {count:,} rows, found {len(labels)}/{len(target_set)}")
                try:
                    line = raw.decode("utf-8", errors="replace").rstrip("\n")
                except Exception:
                    continue
                parts = line.split("\t")
                if len(parts) < 2:
                    continue
                gid = parts[0].strip()
                if gid in target_set:
                    name = (parts[1] or parts[2] if len(parts) > 2 else parts[1]).strip()
                    if name:
                        labels[gid] = name
                    if len(labels) == len(target_set):
                        break  # found all

    print(f"  Scanned {count:,} rows total, resolved {len(labels)}/{len(target_set)} IDs")
    return labels


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fix bad labels on Place nodes")
    parser.add_argument("--dry-run", action="store_true", help="Report only, no writes")
    parser.add_argument("--skip-download", action="store_true",
                        help="Don't download allCountries.zip if missing")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # ── Pass 1: QID labels via Wikidata ──
    print("=== Pass 1: Fix label = QID (Wikidata SPARQL) ===")
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Place) WHERE p.label = p.qid RETURN p.qid AS qid"
        )
        qids = [r["qid"] for r in result]

    print(f"  Found {len(qids)} nodes with label = qid")

    if qids:
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
                print(f"  Updated {updated} labels from Wikidata")
        else:
            for qid, label in list(wd_labels.items())[:10]:
                print(f"    {qid} -> {label}")
            if len(wd_labels) > 10:
                print(f"    ... and {len(wd_labels) - 10} more")

    # ── Pass 2: GeoNames labels ──
    print()
    print("=== Pass 2: Fix label = geonames_id ===")
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Place) WHERE p.label = p.geonames_id "
            "RETURN p.geonames_id AS gid"
        )
        gids = [r["gid"] for r in result]

    print(f"  Found {len(gids)} nodes with label = geonames_id")

    if not gids:
        driver.close()
        print("\nDone.")
        return

    # Step 2a: local JSON cache
    cache = load_geonames_cache()
    gn_labels = {}
    remaining = []
    for gid in gids:
        if gid in cache:
            gn_labels[gid] = cache[gid]
        elif str(gid) in cache:
            gn_labels[gid] = cache[str(gid)]
        else:
            remaining.append(gid)

    print(f"  From local cache: {len(gn_labels)} resolved, {len(remaining)} remaining")

    # Step 2b: allCountries.zip dump
    if remaining:
        if not GEONAMES_ZIP.exists() and not args.skip_download:
            download_geonames_zip()

        if GEONAMES_ZIP.exists():
            zip_labels = lookup_geonames_from_zip(remaining)
            gn_labels.update(zip_labels)
            still_missing = len(remaining) - len(zip_labels)
            if still_missing > 0:
                print(f"  Still missing after dump: {still_missing}")
        else:
            print("  [SKIP] allCountries.zip not found. Use --skip-download=false or download manually:")
            print(f"    wget -O {GEONAMES_ZIP} {GEONAMES_ZIP_URL}")

    print(f"  Total resolved: {len(gn_labels)}/{len(gids)}")

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
            print(f"  Updated {updated} labels from GeoNames")
    else:
        for gid, label in list(gn_labels.items())[:10]:
            print(f"    {gid} -> {label}")
        if len(gn_labels) > 10:
            print(f"    ... and {len(gn_labels) - 10} more")

    # Update the local cache with new lookups for future runs
    if gn_labels and not args.dry_run:
        cache.update(gn_labels)
        GEONAMES_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with open(GEONAMES_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print(f"  Updated cache ({len(cache)} total entries)")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
