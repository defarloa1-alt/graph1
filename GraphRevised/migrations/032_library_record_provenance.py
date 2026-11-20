"""Migration 032 (2026-11-20): library records describe the fetch they were read from (02 §1).

    python -m GraphRevised.migrations.032_library_record_provenance [--apply]

The alignment review of 2026-11-20 found LCNAF, LCSH and FAST records whose label had been
relabelled from the authority itself (harvest/lc_identities.py, D-164) while their sourceUri,
contentHash and rawPayloadUri still described the Wikidata payload the record was first made
from: upsert_authority updated only the words and retrievedAt on a match. The operation now
replaces a fetch's fields together; this migration repairs the records already written.

For each such record, the heading preserved in phase-5-source/ (adapters/library_headings.py)
is read from disk, never fetched: its sourceUri, contentHash and retrievedAt, and its path as the
rawPayloadUri. A record whose heading is not preserved is reported and left. No label, link or
claim changes. Without --apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from neo4j import GraphDatabase

from GraphRevised.adapters.library_headings import SOURCE_DIRECTORY
from GraphRevised.harvest.lc_identities import REPOSITORY
from GraphRevised.operations import load_operations, run_write
from GraphRevised import localdb

STALE = """
MATCH (e:Entity)-[:HAS_AUTHORITY_RECORD]->(a:AuthorityRecord)
WHERE a.system IN ['LCSH', 'LCNAF', 'FAST'] AND a.sourceUri CONTAINS 'wikidata.org'
WITH a, min(e.id) AS entity
RETURN entity, a.id AS id, a.system AS system, a.identifier AS identifier, a.label AS label,
       a.shortLabel AS shortLabel, a.sourceUri AS sourceUri
ORDER BY a.system, a.identifier
"""


def preserved(system: str, identifier: str):
    """The heading as preserved on disk, or None; never fetched."""
    stem = f"{system.lower()}-{identifier}"
    metadata_path = SOURCE_DIRECTORY / f"{stem}.metadata.json"
    payloads = [p for p in SOURCE_DIRECTORY.glob(f"{stem}.*") if p != metadata_path]
    if not metadata_path.exists() or len(payloads) != 1:
        return None
    return payloads[0], json.loads(metadata_path.read_text(encoding="utf-8"))


def migrate(tx, operations) -> dict:
    report: dict = {"repaired": [], "notPreserved": []}
    for row in tx.run(STALE).data():
        found = preserved(row["system"], row["identifier"])
        if found is None:
            report["notPreserved"].append(f"{row['system']} {row['identifier']}: {row['label']}")
            continue
        path, metadata = found
        run_write(tx, operations, "upsert_authority", {
            "entityId": row["entity"], "id": row["id"], "system": row["system"], "identifier": row["identifier"],
            "label": None, "shortLabel": None, "description": None,  # the words stay as they are
            "retrievedAt": metadata["retrievedAt"], "sourceUri": metadata["sourceUri"], "sourceRevision": None,
            "contentHash": metadata["contentHash"],
            "rawPayloadUri": path.resolve().relative_to(REPOSITORY).as_posix(),
            "role": "crosswalk", "relation": "closeMatch", "linkStatus": "accepted",  # existing links unchanged
        })
        report["repaired"].append(f"{row['system']} {row['identifier']}: {row['label']} "
                                  f"({row['sourceUri']} -> {metadata['sourceUri']})")
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
