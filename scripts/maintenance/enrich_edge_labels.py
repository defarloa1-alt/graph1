#!/usr/bin/env python3
"""
Enrich PID edges with human-readable labels from Wikidata.

For edges with wikidata_pid (or typed as P* / WIKIDATA_P*), fetches the
Wikidata property label and sets r.label so edges have a readable name
instead of just the PID.

Run after canonicalize_edges.py. Idempotent — skips edges that already have r.label.

Usage:
    python scripts/maintenance/enrich_edge_labels.py
    python scripts/maintenance/enrich_edge_labels.py --dry-run
"""
import argparse
import re
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "scripts"))
sys.path.insert(0, str(_root))

import requests
from neo4j import GraphDatabase

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", os.environ.get("NEO4J_USER", "neo4j"))
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "Chrystallum-EnrichEdgeLabels/1.0 (academic)"}
BATCH_SIZE = 50


def fetch_property_labels(pids: list[str]) -> dict[str, str]:
    """Fetch English labels for Wikidata properties. Returns {P31: 'instance of', ...}"""
    if not pids:
        return {}
    ids = "|".join(pids[:BATCH_SIZE])
    params = {
        "action": "wbgetentities",
        "ids": ids,
        "props": "labels",
        "languages": "en",
        "format": "json",
    }
    try:
        r = requests.get(WIKIDATA_API, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  Wikidata API error: {e}")
        return {}
    result = {}
    for pid, entity in data.get("entities", {}).items():
        if isinstance(entity, dict) and "missing" not in entity:
            label = (entity.get("labels", {}).get("en", {}).get("value") or "").strip()
            if label:
                result[pid] = label
    return result


def extract_pid_from_rel_type(rt: str) -> str | None:
    """P31 -> P31, WIKIDATA_P6379 -> P6379"""
    if rt.startswith("WIKIDATA_"):
        return rt.replace("WIKIDATA_", "", 1)
    if re.match(r"^P\d+$", rt):
        return rt
    return None


def run(dry_run: bool = False) -> None:
    if not NEO4J_PASSWORD:
        print("Error: NEO4J_PASSWORD not set.")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # All relationship types that look like PIDs
        result = session.run("""
            CALL db.relationshipTypes() YIELD relationshipType
            WHERE relationshipType STARTS WITH 'P'
               OR relationshipType STARTS WITH 'WIKIDATA_P'
            RETURN relationshipType AS rel_type
            ORDER BY rel_type
        """)
        rel_types = [r["rel_type"] for r in result]

    rel_type_to_pid: dict[str, str] = {}
    for rt in rel_types:
        pid = extract_pid_from_rel_type(rt)
        if pid:
            rel_type_to_pid[rt] = pid

    if not rel_type_to_pid:
        print("No PID-like relationship types found.")
        driver.close()
        return

    pids_list = sorted(set(rel_type_to_pid.values()))
    print(f"Fetching labels for {len(pids_list)} PIDs from Wikidata...")

    labels: dict[str, str] = {}
    for i in range(0, len(pids_list), BATCH_SIZE):
        batch = pids_list[i : i + BATCH_SIZE]
        batch_labels = fetch_property_labels(batch)
        labels.update(batch_labels)
        time.sleep(0.5)  # Rate limit

    print(f"  Resolved {len(labels)} labels")

    updated = 0
    for rt, pid in rel_type_to_pid.items():
        label = labels.get(pid)
        if not label:
            continue
        cypher_rel = f"`{rt}`" if " " in rt or "-" in rt else rt
        if not dry_run:
            with driver.session() as session:
                r = session.run(f"""
                    MATCH ()-[r:{cypher_rel}]->()
                    WHERE r.label IS NULL
                    SET r.label = $label
                    RETURN count(r) AS c
                """, label=label).single()
                if r:
                    updated += r["c"]
        else:
            with driver.session() as session:
                r = session.run(f"""
                    MATCH ()-[r:{cypher_rel}]->()
                    WHERE r.label IS NULL
                    RETURN count(r) AS c
                """).single()
                if r:
                    updated += r["c"]

    driver.close()
    print(f"{'Would update' if dry_run else 'Updated'}: {updated:,} edges with label")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich PID edges with Wikidata labels")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
