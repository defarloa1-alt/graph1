#!/usr/bin/env python3
"""
Link Place nodes (Pleiades backbone) to admin hierarchy via Wikidata P131/P17.

Uses the pleiades_geonames_wikidata_tgn crosswalk to get wikidata_qid for each
pleiades_id, fetches P131 (located in) and P17 (country) from Wikidata, creates
parent Place nodes (by qid) if needed, and creates (:Place)-[:LOCATED_IN]->(:Place).

Run after:
  1. import_pleiades_to_neo4j.py (creates Place nodes with pleiades_id)
  2. link_pleiades_place_to_geo_backbone.py (optional; links Pleiades_Place to Place)
  3. build_wikidata_period_geo_backbone.py (optional; creates some parent Place nodes)

Input:
  CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv

Creates:
  - Place nodes with qid for parents (country/region) if not exist
  - (Place {pleiades_id})-[:LOCATED_IN]->(Place {qid}) for admin containment

Usage:
  python scripts/backbone/geographic/link_place_admin_hierarchy.py
  python scripts/backbone/geographic/link_place_admin_hierarchy.py --dry-run
  python scripts/backbone/geographic/link_place_admin_hierarchy.py --max-places 100
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
LANG_PREF = ["en", "sv", "de", "fr", "es", "it", "ru", "ja", "zh", "ar", "la", "mul"]

# Prefer admin-like feature codes when picking best wikidata_qid per pleiades_id
ADMIN_CODES_PREFERRED = frozenset({"PCLI", "ADM1", "ADM2", "ADM3", "ADM4", "ADMD", "RGN", "RGNH"})


def _best_label(labels_obj: dict) -> str:
    for lang in LANG_PREF:
        if lang in labels_obj:
            return labels_obj[lang].get("value", "")
    if labels_obj:
        return next(iter(labels_obj.values())).get("value", "")
    return ""


def _statement_qid(stmt: dict) -> Optional[str]:
    mainsnak = stmt.get("mainsnak", {})
    if mainsnak.get("snaktype") != "value":
        return None
    if mainsnak.get("datatype") != "wikibase-item":
        return None
    value = mainsnak.get("datavalue", {}).get("value", {})
    qid = value.get("id")
    if qid:
        return qid
    numeric_id = value.get("numeric-id")
    if numeric_id is None:
        return None
    return f"Q{numeric_id}"


def _chunked(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _fetch_entities(qids: List[str], *, timeout: int = 180, pause: float = 0.5) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for batch in _chunked(qids, 40):
        params = urllib.parse.urlencode(
            {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "format": "json",
                "props": "labels|aliases|claims",
                "languages": "|".join(LANG_PREF),
            }
        )
        req = urllib.request.Request(
            f"{WIKIDATA_API}?{params}",
            headers={"User-Agent": "Chrystallum-Graph1/1.0 (link-place-admin-hierarchy)"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        out.update(payload.get("entities", {}))
        time.sleep(pause)
    return out


def build_pleiades_to_wikidata(
    crosswalk_path: Path,
    *,
    max_places: Optional[int] = None,
) -> Dict[str, str]:
    """
    Build pleiades_id -> best wikidata_qid from crosswalk.
    Prefer rows with has_wikidata_match=true; prefer admin-like feature codes.
    """
    pleiades_to_qid: Dict[str, str] = {}
    pleiades_scores: Dict[str, Tuple[bool, str]] = {}  # (has_admin_code, feature_code)

    with crosswalk_path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            pid = (row.get("pleiades_id") or "").strip()
            qid = (row.get("wikidata_qid") or "").strip()
            has_match = (row.get("has_wikidata_match") or "").strip().lower() == "true"
            code = (row.get("geonames_feature_code") or "").strip()

            if not pid or not qid or not has_match or not qid.startswith("Q"):
                continue

            is_admin = code in ADMIN_CODES_PREFERRED
            score = (is_admin, code)

            if pid not in pleiades_scores or score > pleiades_scores[pid]:
                pleiades_scores[pid] = score
                pleiades_to_qid[pid] = qid

    pids = sorted(pleiades_to_qid.keys())
    if max_places and max_places > 0:
        pids = pids[:max_places]
    return {p: pleiades_to_qid[p] for p in pids}


def fetch_parent_qids(
    qids: List[str],
    *,
    max_depth: int = 2,
    timeout: int = 180,
    pause: float = 0.5,
) -> Tuple[Dict[str, List[str]], Dict[str, dict]]:
    """
    Fetch P131 and P17 for each qid, and recursively for parents up to max_depth.
    Returns (child_qid -> [parent_qids], qid -> entity for label/alias).
    """
    child_to_parents: Dict[str, List[str]] = {}
    entity_by_qid: Dict[str, dict] = {}
    frontier: Set[str] = set(qids)
    seen_depth: Dict[str, int] = {q: 0 for q in frontier}

    while frontier and max(seen_depth.values()) < max_depth:
        batch = sorted(frontier)[:50]
        frontier = set()
        entities = _fetch_entities(batch, timeout=timeout, pause=pause)

        for qid in batch:
            entity = entities.get(qid, {})
            entity_by_qid[qid] = entity
            claims = entity.get("claims", {})

            parent_qids: List[str] = []
            for stmt in claims.get("P131", []):
                p = _statement_qid(stmt)
                if p and p not in parent_qids:
                    parent_qids.append(p)
            for stmt in claims.get("P17", []):
                p = _statement_qid(stmt)
                if p and p not in parent_qids:
                    parent_qids.append(p)

            child_to_parents[qid] = parent_qids
            depth = seen_depth.get(qid, 0)
            for p in parent_qids:
                if p not in seen_depth:
                    seen_depth[p] = depth + 1
                    if depth + 1 < max_depth:
                        frontier.add(p)

    return child_to_parents, entity_by_qid


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Link Place (pleiades_id) to admin hierarchy via Wikidata P131/P17"
    )
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USERNAME)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--crosswalk", default="CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv")
    parser.add_argument(
        "--pleiades-wikidata-csv",
        default=None,
        help="Extra pleiades_id->qid from P3813 fetch (CSV/geographic/pleiades_wikidata_p3813.csv)",
    )
    parser.add_argument("--max-places", type=int, default=None, help="Limit places to process (for testing)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.password:
        print("NEO4J_PASSWORD required (set in .env or --password)", file=sys.stderr)
        return 1

    crosswalk_path = _PROJECT_ROOT / args.crosswalk
    if not crosswalk_path.exists():
        print(f"ERROR: crosswalk not found: {crosswalk_path}", file=sys.stderr)
        return 1

    pleiades_to_qid = build_pleiades_to_wikidata(crosswalk_path, max_places=args.max_places)

    # Merge extra mappings from P3813 fetch if provided
    if args.pleiades_wikidata_csv:
        p3813_path = _PROJECT_ROOT / args.pleiades_wikidata_csv
        if p3813_path.exists():
            with p3813_path.open("r", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    pid = (row.get("pleiades_id") or "").strip()
                    qid = (row.get("qid") or "").strip()
                    if pid and qid and qid.startswith("Q"):
                        pleiades_to_qid[pid] = qid
            print(f"Merged P3813 mappings from {p3813_path}", flush=True)
    if not pleiades_to_qid:
        print("No pleiades_id -> wikidata_qid mappings from crosswalk (has_wikidata_match=true)")
        return 0

    qids = list(set(pleiades_to_qid.values()))
    print(f"Fetching P131/P17 for {len(qids)} distinct Wikidata entities...", flush=True)
    child_to_parents, entity_by_qid = fetch_parent_qids(qids)

    # Build place rows for parent Place nodes (by qid)
    parent_qids = set()
    for parents in child_to_parents.values():
        parent_qids.update(parents)

    # Fetch any parent entities not yet in entity_by_qid
    missing = [q for q in parent_qids if q not in entity_by_qid]
    if missing:
        extra = _fetch_entities(missing, timeout=180, pause=0.5)
        entity_by_qid.update(extra)

    place_rows: List[dict] = []
    for qid in parent_qids:
        entity = entity_by_qid.get(qid, {})
        labels = entity.get("labels", {})
        label = _best_label(labels) or qid
        place_rows.append({"qid": qid, "label": label})

    # Also ensure child Place (by pleiades_id) has a parent - we link pleiades_id -> parent_qid
    link_rows: List[dict] = []
    for pleiades_id, child_qid in pleiades_to_qid.items():
        parents = child_to_parents.get(child_qid, [])
        for parent_qid in parents:
            link_rows.append({"pleiades_id": pleiades_id, "parent_qid": parent_qid})

    if args.dry_run:
        print("DRY RUN")
        print(f"  Would create/update {len(place_rows)} parent Place nodes (by qid)")
        print(f"  Would create {len(link_rows)} LOCATED_IN edges (Place pleiades_id -> Place qid)")
        for r in link_rows[:10]:
            print(f"    {r['pleiades_id']} -> {r['parent_qid']}")
        if len(link_rows) > 10:
            print(f"    ... and {len(link_rows) - 10} more")
        return 0

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("pip install neo4j", file=sys.stderr)
        return 1

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    with driver.session() as session:
        # Create parent Place nodes (by qid) if not exist
        if place_rows:
            session.run(
                """
                UNWIND $rows AS row
                MERGE (pl:Place {qid: row.qid})
                ON CREATE SET
                    pl.created = datetime(),
                    pl.node_type = 'wikidata_place_backbone',
                    pl.authority = 'Wikidata',
                    pl.uri = 'https://www.wikidata.org/wiki/' + row.qid
                SET
                    pl.label = coalesce(row.label, pl.label, row.qid),
                    pl.updated = datetime()
                """,
                rows=place_rows,
            )
            print(f"Ensured {len(place_rows)} parent Place nodes (by qid)", flush=True)

        # Create (Place pleiades_id)-[:LOCATED_IN]->(Place qid)
        if link_rows:
            result = session.run(
                """
                UNWIND $rows AS row
                MATCH (child:Place {pleiades_id: row.pleiades_id})
                MATCH (parent:Place {qid: row.parent_qid})
                MERGE (child)-[r:LOCATED_IN]->(parent)
                SET
                    r.source = 'wikidata',
                    r.wikidata_pid = 'P131',
                    r.mapping_note = 'admin_containment'
                RETURN count(r) AS linked
                """,
                rows=link_rows,
            )
            # Sum linked - each row is one MERGE
            linked = sum(1 for _ in result)
            print(f"Created {linked} LOCATED_IN edges (Place pleiades_id -> Place qid)", flush=True)

        stats = session.run(
            """
            MATCH (p:Place)
            WHERE p.pleiades_id IS NOT NULL
            OPTIONAL MATCH (p)-[:LOCATED_IN]->(parent:Place)
            RETURN
                count(DISTINCT p) AS places_with_pleiades,
                count(DISTINCT CASE WHEN parent IS NOT NULL THEN p END) AS places_with_parent
            """
        ).single()

        print(
            f"Stats: {stats['places_with_pleiades']} Place(pleiades_id), "
            f"{stats['places_with_parent']} with LOCATED_IN parent",
            flush=True,
        )

    driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
