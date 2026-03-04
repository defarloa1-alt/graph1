#!/usr/bin/env python3
"""
Person Harvest Orchestrator — ADR-008 main loop

Discovery → ancestry traversal → context packet → agent → executor.
One person at a time, depth-first along paternal line until leafs.
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1]
_root = _scripts.parents[0]
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_scripts))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
except ImportError:
    NEO4J_URI = NEO4J_USERNAME = NEO4J_PASSWORD = NEO4J_DATABASE = None

from neo4j import GraphDatabase

from scripts.federation.dprr_import import get_dprr_federation_status
from scripts.person_harvest.discovery import discover_roman_republic_persons, fetch_ancestry_qids, discover_from_graph
from scripts.person_harvest.context_packet import build_context_packet
from scripts.person_harvest.agent import produce_harvest_plan
from scripts.person_harvest.executor import execute_plan

try:
    from scripts.federation.dprr_layer1 import (
        parse_dprr_label,
        derive_label_latin,
        derive_label_sort,
        parse_time_value_to_year_and_iso,
    )
except ImportError:
    parse_dprr_label = derive_label_latin = derive_label_sort = parse_time_value_to_year_and_iso = None


def _derive_birth_death_from_wikidata(claims: dict) -> dict:
    """Extract birth_year, death_year, birth_date, death_date from P569/P570 claims."""
    out = {}
    for prop, key, prec in [("P569", "birth", 11), ("P570", "death", 11)]:
        vals = claims.get(prop, [])
        if not vals:
            continue
        v = vals[0]
        time_str = v.get("value") if isinstance(v, dict) else v
        if not time_str or "/" in str(time_str):  # Skip entity refs
            continue
        year, earliest, _ = parse_time_value_to_year_and_iso(time_str, prec) if parse_time_value_to_year_and_iso else (None, None, None)
        if year is not None:
            out[f"{key}_year"] = year
        if earliest:
            out[f"{key}_date"] = earliest.split("T")[0] if "T" in str(earliest) else earliest
    return out


def _derive_labels_from_dprr_string(raw: str) -> tuple[str | None, str | None]:
    """When dprr_raw has DPRR string but no label_latin/label_sort, derive from parse."""
    if not raw or not parse_dprr_label:
        return (None, None)
    parsed = parse_dprr_label(raw)
    return (derive_label_latin(parsed) if derive_label_latin else None, derive_label_sort(parsed) if derive_label_sort else None)


def main() -> int:
    ap = argparse.ArgumentParser(description="Person Harvest — Roman Republic ancestry construction")
    ap.add_argument("--limit", type=int, default=10, help="Max persons to harvest")
    ap.add_argument("--dry-run", action="store_true", help="No graph writes")
    ap.add_argument("--from-graph", action="store_true", help="Discover from graph instead of Wikidata")
    ap.add_argument("--seed-qid", default=None, help="Start from this QID (single person)")
    args = ap.parse_args()

    dprr_blocked = get_dprr_federation_status() == "blocked"

    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("NEO4J_URI and NEO4J_PASSWORD required (.env)")
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"

    # Discovery
    if args.seed_qid:
        queue = [{"qid": args.seed_qid, "label": "", "dprr_id": None}]
    elif args.from_graph:
        with driver.session(database=db) as session:
            queue = discover_from_graph(session, limit=args.limit)
            # Require qid for family traversal — null-QID persons cannot be Wikidata-fetched
            queue = [{"qid": r.get("qid"), "label": r.get("label", ""), "dprr_id": r.get("dprr_id")} for r in queue if r.get("qid")]
    else:
        queue = discover_roman_republic_persons(limit=args.limit)
        queue = [q for q in queue if q.get("qid")]

    if not queue:
        print("No persons to harvest.")
        return 0

    print(f"Person Harvest — {len(queue)} persons, dry_run={args.dry_run}")
    print(f"  DPRR blocked: {dprr_blocked} (using graph-local dprr_raw)")
    print()

    seen = set()
    total_stats = {"created": 0, "updated": 0, "skipped": 0}
    frontier = deque(queue)
    MAX_SIBLINGS_ENQUEUE = 8  # Cap sibling fan-out before unlimited runs

    with driver.session(database=db) as session:
        while frontier and len(seen) < args.limit:
            person = frontier.popleft()
            qid = person.get("qid")
            dprr_id = person.get("dprr_id")
            key = qid or f"dprr_{dprr_id}"
            if key in seen:
                continue
            seen.add(key)

            # Skip null-QID persons — no Wikidata fetch possible; log and don't process
            if not qid:
                print(f"  SKIP DQ_MISSING_QID {key}")
                continue

            # Build context, plan, execute
            try:
                packet = build_context_packet(qid or "", dprr_id, session, dprr_blocked=dprr_blocked)
                plan = produce_harvest_plan(packet, qid or "", dprr_id)
                stub = packet.get("person_stub") or {}
                dprr_raw = packet.get("dprr_raw") or {}
                plan["label"] = person.get("label", "") or stub.get("label", "")
                plan["label_dprr"] = stub.get("label_dprr") or dprr_raw.get("label_dprr")
                plan["label_latin"] = stub.get("label_latin") or dprr_raw.get("label_latin")
                plan["label_sort"] = stub.get("label_sort") or dprr_raw.get("label_sort")
                # Derive from DPRR string when graph has old schema (label only)
                raw = dprr_raw.get("label") or ""
                is_dprr_format = raw and len(raw.split()) >= 2 and len(raw.split()[0]) >= 5 and raw.split()[0][:4].isalpha() and raw.split()[0][4:].isdigit()
                if not plan["label_dprr"] and is_dprr_format:
                    plan["label_dprr"] = raw
                    lat, srt = _derive_labels_from_dprr_string(raw)
                    if lat and not plan["label_latin"]:
                        plan["label_latin"] = lat
                        if plan["label"] == raw:
                            plan["label"] = lat  # Use tria nomina as display per ADR-007
                    if srt and not plan["label_sort"]:
                        plan["label_sort"] = srt
                # Derive birth/death from wikidata_raw for temporal backbone
                wd = packet.get("wikidata_raw") or {}
                for k, v in _derive_birth_death_from_wikidata(wd.get("claims", {})).items():
                    plan[k] = v
                stats = execute_plan(plan, session, dry_run=args.dry_run)
            except Exception as e:
                label = person.get("label", "") or qid or str(dprr_id)
                print(f"  ERROR {label[:30]}: {e}")
                continue

            for k, v in stats.items():
                if k != "errors" and isinstance(v, int):
                    total_stats[k] = total_stats.get(k, 0) + v

            label = person.get("label", "") or qid or str(dprr_id)
            print(f"  {label[:40]:<40} | updated={stats.get('updated',0)} created={stats.get('created',0)}")

            # Enqueue family for full tree traversal (skip if MythologicalPerson — ADR-008)
            if not args.dry_run and qid and plan.get("person_class") != "MYTHOLOGICAL":
                ancestry = fetch_ancestry_qids(qid)
                for parent_qid in [ancestry.get("father_qid"), ancestry.get("mother_qid")]:
                    if parent_qid and parent_qid not in seen:
                        frontier.append({"qid": parent_qid, "label": "", "dprr_id": None})
                # From packet: children (P40), siblings (P3373), spouses (P26), stepparents (P3448)
                wd = packet.get("wikidata_raw") or {}
                claims = wd.get("claims", {})
                for prop in ("P40", "P26", "P3448"):
                    for v in claims.get(prop, []):
                        other_qid = (v.get("value") or "").split("/")[-1]
                        if other_qid and other_qid.startswith("Q") and other_qid not in seen:
                            frontier.append({"qid": other_qid, "label": "", "dprr_id": None})
                # Siblings: cap to avoid frontier balloon (Caesar/Pompey gens)
                sibling_count = 0
                for v in claims.get("P3373", []):
                    if sibling_count >= MAX_SIBLINGS_ENQUEUE:
                        break
                    other_qid = (v.get("value") or "").split("/")[-1]
                    if other_qid and other_qid.startswith("Q") and other_qid not in seen:
                        frontier.append({"qid": other_qid, "label": "", "dprr_id": None})
                        sibling_count += 1

    driver.close()
    print()
    print(f"Done. updated={total_stats['updated']} created={total_stats['created']} skipped={total_stats['skipped']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
