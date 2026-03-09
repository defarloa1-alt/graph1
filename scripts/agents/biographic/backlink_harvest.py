#!/usr/bin/env python3
"""
Person Backlink Harvest — standalone pass for Wikidata backlinks.

Run after biographic harvest (bio anchors + events + marriages).
Fetches items that reference each person via BACKLINK_PREDICATE_MAP,
routes via BacklinkRouting, writes BIO_CANDIDATE_REL.

Usage:
  python -m scripts.agents.biographic.backlink_harvest --from-graph --limit 10
  python -m scripts.agents.biographic.backlink_harvest --from-graph --dry --verbose
  python -m scripts.agents.biographic.backlink_harvest --qids Q125414 Q1048
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import requests
from neo4j import GraphDatabase

from .agent import (
    BACKLINK_PREDICATE_MAP,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USER,
    SLEEP_SEC,
    WRITE_BACKLINK_CANDIDATE,
    _entity_type_from_item_type,
    fetch_backlinks,
)
from .decision_loader import load_decision_model
from scripts.tools.entity_cipher import generate_entity_cipher

FAILURES_LOG = _root / "output" / "biographic_failures.jsonl"


def _is_timeout_like(exc: BaseException) -> bool:
    if isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
        return True
    if isinstance(exc, requests.exceptions.HTTPError) and getattr(exc, "response", None) is not None:
        return exc.response.status_code in (502, 503, 504)
    msg = str(exc).lower()
    return "timeout" in msg or "timed out" in msg or "502" in msg or "503" in msg or "504" in msg


def _log_failure(qid: str, dprr_id: str, exc: BaseException):
    FAILURES_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "qid": qid,
        "dprr_id": dprr_id,
        "error": str(exc),
        "error_kind": "timeout" if _is_timeout_like(exc) else "other",
        "phase": "backlink_harvest",
    }
    with open(FAILURES_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def harvest_backlinks_for_person(
    qid: str,
    dprr_id: str,
    session,
    decision_model,
    dry_run: bool = False,
    verbose: bool = False,
) -> tuple[int, bool]:
    """
    Fetch Wikidata backlinks for one person and write BIO_CANDIDATE_REL.
    Returns (backlink_count, success).
    """
    if verbose:
        print(f"\n  [{qid}] dprr:{dprr_id} — fetching backlinks...")

    backlinks = fetch_backlinks(qid)

    if decision_model and decision_model._backlink:
        for bl in backlinks:
            r = decision_model.route_backlink(bl["pred_pid"], bl["item_type_label"])
            bl["edge_type"] = r["edge_type"]
            bl["direction"] = r["direction"]
            bl["qualifier"] = r.get("qualifier")
            bl["sfa_queue"] = r["sfa_queue"]

    by_queue = Counter(b["sfa_queue"] for b in backlinks)
    by_pred = Counter(b["pred_pid"] for b in backlinks)

    if verbose:
        print(f"    backlinks: {len(backlinks)} total")
        print(f"    by queue: {dict(by_queue)}")
        print(f"    by pred:  {dict(by_pred)}")
        for i, b in enumerate(backlinks[:10]):
            lbl = (b.get("item_label") or b["item_qid"])[:40]
            print(f"      [{i+1}] {b['pred_pid']} -> {b['item_qid']} ({lbl}) [{b['sfa_queue']}]")
        if len(backlinks) > 10:
            print(f"      ... and {len(backlinks) - 10} more")

    if dry_run:
        if verbose:
            print(f"    [DRY RUN] would write {len(backlinks)} BIO_CANDIDATE_REL edges")
        return len(backlinks), True

    written = 0
    for bl in backlinks:
        try:
            entity_type = _entity_type_from_item_type(bl.get("item_type_label"))
            session.run(WRITE_BACKLINK_CANDIDATE, {
                "person_qid":      qid,
                "item_qid":        bl["item_qid"],
                "item_label":      bl["item_label"],
                "entity_type":     entity_type,
                "entity_cipher":   generate_entity_cipher(bl["item_qid"], entity_type, "wd"),
                "item_type_qid":   bl["item_type_qid"],
                "item_type_label": bl["item_type_label"],
                "pred_pid":        bl["pred_pid"],
                "edge_type":       bl["edge_type"],
                "direction":       bl["direction"],
                "qualifier":       bl["qualifier"],
                "sfa_queue":       bl["sfa_queue"],
            })
            written += 1
        except Exception as e:
            if verbose:
                print(f"    WARN backlink write failed for {bl['item_qid']}: {e}")

    if verbose:
        print(f"    written: {written} BIO_CANDIDATE_REL edges")
    return len(backlinks), True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Person Backlink Harvest — fetch Wikidata backlinks for persons, write BIO_CANDIDATE_REL"
    )
    parser.add_argument("--from-graph", action="store_true", help="Load persons from graph (bio_harvested_at IS NOT NULL)")
    parser.add_argument("--qids", nargs="+", help="Explicit QID list (e.g. --qids Q125414 Q1048)")
    parser.add_argument("--limit", type=int, default=None, help="Max persons to process")
    parser.add_argument("--dry", action="store_true", help="Dry run — no writes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output per person")
    args = parser.parse_args()

    if not args.from_graph and not args.qids:
        parser.error("Use --from-graph or --qids Q1 Q2 ...")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        if args.from_graph:
            records = session.run("""
                MATCH (p:Person)
                WHERE p.qid IS NOT NULL AND p.bio_harvested_at IS NOT NULL
                RETURN p.qid AS qid, p.dprr_id AS dprr_id
                ORDER BY p.bio_harvested_at DESC
            """).data()
            if args.limit:
                records = records[: args.limit]
        else:
            records = [{"qid": q, "dprr_id": "?"} for q in args.qids]
            if args.limit:
                records = records[: args.limit]

    print("=" * 60)
    print("Person Backlink Harvest")
    print("=" * 60)
    print(f"Mode:        {'dry run' if args.dry else 'write'}")
    print(f"Verbose:     {args.verbose}")
    print(f"Persons:     {len(records)}")
    print(f"Predicates:  {list(BACKLINK_PREDICATE_MAP.keys())}")
    print(f"Predicate map (pid -> edge_type, sfa_queue):")
    for pid, tup in sorted(BACKLINK_PREDICATE_MAP.items(), key=lambda x: x[0]):
        edge, direction, qual, queue = tup if isinstance(tup, tuple) else (tup.get("edge_type"), tup.get("direction"), tup.get("qualifier"), tup.get("sfa_queue"))
        print(f"  {pid}: {edge} ({direction}) -> {queue}")
    print()

    decision_model = None
    with driver.session() as session:
        try:
            decision_model = load_decision_model(session)
            if decision_model and decision_model._backlink:
                print("  Using graph decision model (BacklinkRouting)")
            else:
                print("  Using hardcoded BACKLINK_PREDICATE_MAP")
        except Exception as e:
            print(f"  WARN decision model: {e}")

        total_backlinks = 0
        failures = []
        for i, r in enumerate(records):
            qid = r["qid"]
            dprr_id = r.get("dprr_id") or "?"
            if args.verbose:
                print(f"\n--- Person {i+1}/{len(records)}: {qid} (dprr:{dprr_id}) ---")
            else:
                print(f"  [{i+1}/{len(records)}] {qid} ...", end=" ", flush=True)
            try:
                count, ok = harvest_backlinks_for_person(
                    qid, dprr_id, session, decision_model,
                    dry_run=args.dry, verbose=args.verbose,
                )
                total_backlinks += count
                if not args.verbose:
                    print(f"{count} backlinks")
            except Exception as e:
                print(f"ERROR: {e}" if not args.verbose else f"    ERROR: {e}")
                _log_failure(qid, dprr_id, e)
                failures.append((qid, dprr_id, _is_timeout_like(e)))
            if i < len(records) - 1:
                time.sleep(SLEEP_SEC)

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Persons processed:  {len(records) - len(failures)}")
    print(f"Persons failed:     {len(failures)}")
    print(f"Total backlinks:   {total_backlinks}")
    ok_count = max(1, len(records) - len(failures))
    print(f"Avg per person:     {total_backlinks / ok_count:.1f}")
    if failures:
        timeouts = [f for f in failures if f[2]]
        print(f"  (timeouts/heavy:  {len(timeouts)})")
        print(f"  Logged to:        {FAILURES_LOG}")
        print(f"  Failed QIDs:      {', '.join(f[0] for f in failures)}")
    print()

    driver.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
