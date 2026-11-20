"""Migration 031 (2026-11-19): Scarpus's name parts, from Smith's heading, and his aliases proposed (46 §4.3, §4.5).

    python -m GraphRevised.migrations.031_scarpus_name_parts_and_aliases [--apply]

Scarpus has no Wikidata identity (the curator's choice while the identity Question is open,
030), so his name parts are read by code from Smith's entry heading, "SCARPUS, L. PINA'RIUS"
(cognomen, then praenomen and nomen; L. is Lucius): praenomen Lucius, nomen Pinarius, cognomen
Scarpus. Display words, never evidence (set_name_parts, D-145).

Then the alias suggester (proposals/aliases.py) reasons from them and proposes, for the curator:
"L. Pinarius Scarpus" (by convention), "Scarpus" (attested in Dio 51.5.6) and "SCARPVS"
(attested on the RRC 546 coins). "Lucius Pinarius" is refused: it is the name of Caesar's heir,
with whom Scarpus shares the open identity Question. Without --apply it reports and rolls back.
Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.aliases import parts_from_heading, propose, suggest
from GraphRevised.proposals.registry import load_registry
from GraphRevised import localdb

SCARPUS = "chr:entity:lucius-pinarius"
HEADING = "SCARPUS, L. PINA'RIUS"
SUGGESTER = "alias suggester (rule, 46 §4.5), migration 031"


def migrate(tx, operations, registry) -> dict:
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    smith = tx.run("""MATCH (o:SourceObservation)-[:IN_WORK]->(:Entity {id: 'chr:entity:smith-dictionary-of-greek-and-roman-biography'})
                      WHERE o.locator = 'p. 735, s.v. Scarpus, L. Pinarius' RETURN o.id AS id""").single()["id"]
    parts = parts_from_heading(HEADING)
    run_write(tx, operations, "set_name_parts", {"id": SCARPUS, "sourceId": smith, **parts, "decidedAt": at,
                                                 "decidedBy": "rule (D-145): read from the entry heading, migration 031"})
    report: dict = {"nameParts": parts, "nameSource": smith, "aliases": []}
    for item in suggest(tx, SCARPUS):
        entry = {"alias": item["alias"], "kind": item["kind"], "sharedWith": item["sharedWith"]}
        if item.get("refused"):
            entry["refused"] = item["refused"]
        else:
            entry["proposal"] = propose(tx, operations, registry.version, SCARPUS, item, proposed_by=SUGGESTER, at=at)["id"]
        report["aliases"].append(entry)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                report = migrate(tx, load_operations(), load_registry())
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
