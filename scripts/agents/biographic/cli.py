"""
Biographic Subject Agent — CLI entry point

Usage:
    python -m scripts.agents.biographic --dprr 1976
    python -m scripts.agents.biographic --all
    python -m scripts.agents.biographic --all --dry
"""

import argparse
import json
import time
from pathlib import Path

import requests

from .agent import harvest_person, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, SLEEP_SEC
from .decision_loader import load_decision_model
from neo4j import GraphDatabase

FAILURES_LOG = Path(__file__).resolve().parents[3] / "output" / "biographic_failures.jsonl"


def _is_timeout_like(exc: BaseException) -> bool:
    """True if error is timeout, connection, or 5xx (likely heavy entities)."""
    if isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
        return True
    if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
        return exc.response.status_code in (502, 503, 504)
    msg = str(exc).lower()
    return "timeout" in msg or "timed out" in msg or "502" in msg or "503" in msg or "504" in msg


def _log_failure(qid: str, dprr_id: str, exc: BaseException):
    """Append failed harvest to output/biographic_failures.jsonl for retry."""
    FAILURES_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "qid": qid,
        "dprr_id": dprr_id,
        "error": str(exc),
        "error_kind": "timeout" if _is_timeout_like(exc) else "other",
    }
    with open(FAILURES_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Biographic Subject Agent — harvest biographical context for Person nodes"
    )
    parser.add_argument("--dprr", help="Single DPRR ID (PoC mode)")
    parser.add_argument("--all",  action="store_true", help="All DPRR persons with QIDs (dprr_id IS NOT NULL)")
    parser.add_argument("--limit", type=int, default=None, help="Max persons to harvest (for incremental runs)")
    parser.add_argument("--dry",  action="store_true", help="Dry run — no writes")
    parser.add_argument("--backlinks", action="store_true", help="Include backlinks inline (default: skip; run backlink_harvest separately)")
    args = parser.parse_args()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        if args.dprr:
            records = session.run(
                "MATCH (p:Person {dprr_id: $dprr}) WHERE p.qid IS NOT NULL "
                "RETURN p.qid AS qid, p.dprr_id AS dprr_id",
                dprr=str(args.dprr)
            ).data()
        elif args.all:
            records = session.run(
                "MATCH (p:Person) WHERE p.qid IS NOT NULL AND p.dprr_id IS NOT NULL "
                "RETURN p.qid AS qid, p.dprr_id AS dprr_id"
            ).data()
            if args.limit:
                records = records[: args.limit]
        else:
            parser.print_help()
            driver.close()
            return

    print(f"Persons to harvest: {len(records)}")
    if not args.dry:
        confirm = input("Proceed with writes? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            driver.close()
            return

    with driver.session() as session:
        decision_model = None
        try:
            decision_model = load_decision_model(session)
            if decision_model and decision_model._backlink:
                print("  Using graph decision model (BacklinkRouting)")
        except Exception:
            print("  Using hardcoded backlink map (run migration_bio_decision_model.cypher for graph-based routing)")

        failures = []
        for i, r in enumerate(records):
            try:
                harvest_person(
                    r["qid"],
                    r["dprr_id"] or "?",
                    session,
                    dry_run=args.dry,
                    decision_model=decision_model,
                    skip_backlinks=not args.backlinks,
                )
            except Exception as e:
                print(f"  ERROR on {r['qid']}: {e}")
                _log_failure(r["qid"], r.get("dprr_id") or "?", e)
                failures.append((r["qid"], r.get("dprr_id"), _is_timeout_like(e)))
            if i < len(records) - 1:
                time.sleep(SLEEP_SEC)

    ok = len(records) - len(failures)
    print(f"\nDone. Harvested {ok} persons.")
    if failures:
        timeouts = [f for f in failures if f[2]]
        print(f"  Failures: {len(failures)} (timeouts/heavy: {len(timeouts)})")
        print(f"  Logged to: {FAILURES_LOG}")
        if timeouts:
            print(f"  Timeout QIDs (retry these): {', '.join(f[0] for f in timeouts)}")
    driver.close()


if __name__ == "__main__":
    main()
