"""Migration 013 (2026-11-15, D-152): Antony's titled legions merged into their numbers.

    python -m GraphRevised.migrations.013_merge_titled_legions [--apply]

The first coin harvest (crro_coins, D-151) made "legion 12 Antiqua", "legion 17
Classica" and "legion 18 Libyca" separate Groups from legions 12, 17 and 18. The
curator merged each pair (2026-11-15): the coins are not a system of unit names,
so a title is an alternative name of the numbered legion. Each titled Group, with
its code-made claims (none decided by a person), is merged into its number
(merge_unreviewed_entity). The harvest, which now folds titles, is run again so
the titled coins become evidence for the numbered legion: an addEvidence Proposal
on its `partOf` claim for the curator, and on its `instanceOf` claim, accepted by
rule. Then the fact layer is rebuilt. Without --apply it reports and rolls back.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import rebuild
from GraphRevised.harvest.crro_coins import DUMP, SERIES, harvest, read_series
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.rule_accept import accept_by_rule

BY = "Tony DeFarlo (curator)"
BASIS = "a title on the coins names the numbered legion, not another unit (the coins are not a system of unit names)"
E = "chr:entity:antony-legion-"
PAIRS = (("12-antiqua", "12", "Legio XII Antiqua"), ("17-classica", "17", "Legio XVII Classica"),
         ("18-libyca", "18", "Legio XVIII Libyca"))


def migrate(tx, operations, at: str) -> list[str]:
    lines = []
    for duplicate, survivor, name in PAIRS:
        exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=E + duplicate).single()
        if exists is None:
            lines.append(f"{E + duplicate}: already merged")
            continue
        row = run_write(tx, operations, "merge_unreviewed_entity", {
            "duplicateId": E + duplicate, "survivorId": E + survivor, "alternativeName": name,
            "decidedAt": at, "decidedBy": BY, "decisionBasis": BASIS})
        lines.append(f"{E + duplicate} -> {E + survivor} ({row[0]['removedClaims']} claims removed)")
    config = next(s for s in json.loads(SERIES.read_text(encoding="utf-8"))["series"] if s["id"] == "rrc-544")
    report = harvest(tx, operations, load_registry(), config, read_series(DUMP, "rrc-544"), at)
    lines += [f"harvest: {o['outcome']:13} {o['unit']}" for o in report["outcomes"] if o["stored"]]
    accepted = accept_by_rule(tx, at)
    lines.append(f"accepted by rule: {accepted}")
    lines.append(f"fact layer: {rebuild(tx)}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                lines = migrate(tx, load_operations(), at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("applied" if args.apply else "dry run, rolled back") + ":")
    print("\n".join(f"  {line}" for line in lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
