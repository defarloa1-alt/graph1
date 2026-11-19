"""Migration 029 (2026-11-19): Questions, Positions and Works with accepted claims become provisional.

    python -m GraphRevised.migrations.029_provisional_questions_positions_works [--apply]

Curator, chat 2026-11-19: an entity of an accepted claim stayed `proposed`. Making an entity
provisional vouches for its identity, which a claim's acceptance does not. For a Question, a
Position or a Work read from a source there is no identity left to decide: the source defines
it. So each one still proposed that an accepted claim names (as subject, object or attributed
Work) is made provisional by rule. Persons, Places, Groups, Offices and depicted Events are not
swept: their identity is the curator's (an authority identity, `depictsSameAs`, the Office
review). One not yet named by an accepted claim waits for its review bucket.

Without --apply it reports and rolls back. Retry-safe (decide_entity keeps the first decision).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations, run_write

CANDIDATES = """
MATCH (e:Entity {status: 'proposed'}) WHERE (e:Question OR e:Position OR e:Work)
  AND EXISTS { MATCH (:Assertion {status: 'accepted'})-[:ASSERTION_SUBJECT|ASSERTION_OBJECT|ATTRIBUTED_TO]->(e) }
RETURN e.id AS id, [l IN labels(e) WHERE l <> 'Entity'][0] AS kind ORDER BY kind, id
"""
DECISION = {"decidedBy": "rule (migration 029, curator-approved 2026-11-19)",
            "decisionBasis": "Named by an accepted claim; a Question, Position or Work read from a source is "
                             "defined by that source, so no identity is left to decide (curator, chat 2026-11-19)."}


def migrate(tx, operations) -> dict:
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = tx.run(CANDIDATES).data()
    for row in rows:
        run_write(tx, operations, "decide_entity", {"id": row["id"], "status": "provisional", "decidedAt": at, **DECISION})
    return {"provisional": dict(Counter(row["kind"] for row in rows)), "factLayer": rebuild(tx)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                report = migrate(tx, load_operations())
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print("applied" if args.apply else "dry run, rolled back")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
