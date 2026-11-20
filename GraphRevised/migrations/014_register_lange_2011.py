"""Migration 014 (2026-11-15): register Lange 2011 as a secondary Work.

    python -m GraphRevised.migrations.014_register_lange_2011 [--apply]

Carsten Hjort Lange, "The Battle of Actium: A Reconsideration", Classical
Quarterly 61.2 (2011), 608-623, the article the Wikipedia article cites and the
first item on the military frame's reading list (43 §7). The curator holds a
licensed JSTOR copy (docs/actium/, git-ignored: in copyright, and each page
carries the downloader's IP). Its text is not stored: passages from it are
page locators with short quotations. Standing secondary: a modern study by a
named author (D-148). Form `history`: the registry has no journal-article form.
Without --apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised import localdb

WORK = {
    "id": "chr:entity:lange-battle-of-actium-reconsideration",
    "label": "Lange, The Battle of Actium: A Reconsideration",
    "shortLabel": "The Battle of Actium: A Reconsideration",
    "description": ("Carsten Hjort Lange, \"The Battle of Actium: A Reconsideration\", The Classical Quarterly, "
                    "New Series 61.2 (December 2011), 608-623 (Cambridge University Press for the Classical "
                    "Association); doi:10.1017/S0009838811000139; JSTOR 41301557. Modern scholarship, in copyright: "
                    "cited by page with short quotations, the text is not stored. No Wikidata record checked."),
}


def migrate(tx, operations, at: str) -> list[str]:
    exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=WORK["id"]).single() is not None
    run_write(tx, operations, "upsert_entity", WORK | {"kind": "Work", "status": None if exists else "provisional"})
    run_write(tx, operations, "set_work_form", {"workId": WORK["id"], "form": "history",
                                                "allowedForms": sorted(load_registry().work_forms)})
    run_write(tx, operations, "set_work_standing", {"id": WORK["id"], "standing": "secondary", "decidedAt": at,
                                                    "decidedBy": "Claude (agent), migration 014; for the curator to check",
                                                    "decisionBasis": "a modern study by a named author"})
    return [f"{'kept' if exists else 'registered'} {WORK['id']}: {WORK['label']} (secondary, history)"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=localdb.database()) as session:
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
