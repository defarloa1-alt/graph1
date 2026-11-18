"""Migration 015 (2026-11-18): register López Sánchez 2010 as a secondary Work.

    python -m GraphRevised.migrations.015_register_lopez_sanchez_2010 [--apply]

Fernando López Sánchez, "Military Units of Mark Antony and Lucius Verus:
Numismatic Recognition of Distinction", Israel Numismatic Research 5 (2010),
123-138: the study of Antony's titled legionary coins (RRC 544/8-12) and the
Corcyra campaign of 32/1 BC. The curator holds a copy (docs/Actium/,
git-ignored; © the Israel Numismatic Society). Its text is not stored: passages
from it are page locators with short quotations. Standing secondary: a modern
study by a named author (D-148). Form `history`: the registry has no
journal-article form. Without --apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry

WORK = {
    "id": "chr:entity:lopez-sanchez-military-units-of-mark-antony",
    "label": "López Sánchez, Military Units of Mark Antony and Lucius Verus",
    "shortLabel": "Military Units of Mark Antony and Lucius Verus",
    "description": ("Fernando López Sánchez, \"Military Units of Mark Antony and Lucius Verus: Numismatic "
                    "Recognition of Distinction\", Israel Numismatic Research 5 (2010), 123-138 (The Israel "
                    "Numismatic Society); ISSN 1565-8449. Modern scholarship, in copyright: cited by page with "
                    "short quotations, the text is not stored. No Wikidata record checked."),
}


def migrate(tx, operations, at: str) -> list[str]:
    exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=WORK["id"]).single() is not None
    run_write(tx, operations, "upsert_entity", WORK | {"kind": "Work", "status": None if exists else "provisional"})
    run_write(tx, operations, "set_work_form", {"workId": WORK["id"], "form": "history",
                                                "allowedForms": sorted(load_registry().work_forms)})
    run_write(tx, operations, "set_work_standing", {"id": WORK["id"], "standing": "secondary", "decidedAt": at,
                                                    "decidedBy": "Claude (agent), migration 015; for the curator to check",
                                                    "decisionBasis": "a modern study by a named author"})
    return [f"{'kept' if exists else 'registered'} {WORK['id']}: {WORK['label']} (secondary, history)"]


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
    print(("applied" if args.apply else "dry run, rolled back") + ":", *lines, sep="\n  ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
