"""Migration 025 (2026-11-19): the cited books' authors by their LC names, and buckets on their headings.

    python -m GraphRevised.migrations.025_authors_and_heading_buckets [--apply]

The curator chose (2026-11-19) to link the authors the LC records name and to make subject
buckets of the headings no Subject held (D-164's follow-up).

1. Authors. John Richard Hale is in the graph: his LC name record (LCNAF no2010057455, which the
   Methuen record's heading resolves to) is linked to him. Ronald Syme, Duane W. Roller and
   T. Robert S. Broughton are not: each is proposed as a Person on the author heading of his own
   book's LC record, and his LC name record linked. lc_record then finds exactly one local
   Person by that LCNAF id and drafts `authorOf` (run it again after this migration).
2. Buckets (28). plans/lc-heading-buckets.json: four new Subjects (Civil War, 43-31 B.C.; Rome
   under Augustus; Roman magistrates; Roman nobility), each anchored to its LCSH record as
   subject_access in LC's own words, about its focus Entities where they exist, placed under
   the Roman Republic backbone with a reason; the Actium and Philippi Subjects go under the
   civil war, as LC places their headings. Membership stays computed (28 §3).

Without --apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.adapters.library_headings import display, preserved_heading
from GraphRevised.harvest.lc_identities import REPOSITORY, record_params
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.entities import propose_entity
from GraphRevised.subject_backbone import apply_manifest
from GraphRevised import localdb

BY = "Tony DeFarlo (curator), entered by Claude 2026-11-19"
MANIFEST = Path(__file__).resolve().parents[1] / "plans" / "lc-heading-buckets.json"
O = "chr:observation:lc-catalog:"
# (local Person or None, name to propose, LCNAF id, the book's record observation, the author heading as quoted)
AUTHORS = [
    ("chr:entity:john-richard-hale", None, "no2010057455", None, None),
    (None, "Ronald Syme", "n50012944", O + "88033679:070ac2106c4d", "Syme, Ronald, 1903-1989"),
    (None, "Duane W. Roller", "nr89016976", O + "2002037175:089f8897251a", "Roller, Duane W."),
    (None, "T. Robert S. Broughton", "n84161676", O + "84023590:ba9918d53649",
     "Broughton, T. Robert S. (Thomas Robert Shannon), 1900-1993"),
]


def migrate(tx, operations) -> dict:
    report: dict = {"authors": [], "buckets": None, "headings": [], "focus": []}
    for person, name, lcnaf, observation, heading in AUTHORS:
        if person is None:
            proposed = propose_entity(tx, operations, kind="Person", label=name, proposed_by=BY,
                                      observation_id=observation, quotation=heading,
                                      source="Library of Congress catalog record",
                                      note="The author of a book we cite, from its LC record's author heading.")
            person = proposed["id"]
        path, metadata = preserved_heading("LCNAF", lcnaf)
        existing = tx.run("MATCH (a:AuthorityRecord {system: 'LCNAF', identifier: $i}) RETURN a.id AS id",
                          i=lcnaf).single()
        params = record_params(person, "LCNAF", lcnaf, existing and existing["id"], path, metadata)
        run_write(tx, operations, "upsert_authority", params)
        run_write(tx, operations, "link_authority", {
            "entityId": person, "system": "LCNAF", "identifier": lcnaf, "role": "crosswalk", "relation": "closeMatch",
            "linkStatus": "accepted", "statementRank": None, "statementReferences": None})
        report["authors"].append({"person": person, "record": params["label"]})

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report["buckets"] = apply_manifest(tx, manifest)
    for subject in manifest["subjects"]:
        if "heading" in subject:
            system, identifier = subject["heading"]["system"], subject["heading"]["identifier"]
            path, metadata = preserved_heading(system, identifier)
            existing = tx.run("MATCH (a:AuthorityRecord {system: $s, identifier: $i}) RETURN a.id AS id",
                              s=system, i=identifier).single()
            run_write(tx, operations, "upsert_subject_authority", {
                "subjectId": subject["id"], "id": existing["id"] if existing else f"chr:authority:{system.lower()}:{identifier}",
                "system": system, "identifier": identifier, "label": display(system, identifier, metadata["label"]),
                "shortLabel": f"{system}: {metadata['label']}", "description": None,
                "retrievedAt": metadata["retrievedAt"], "sourceUri": metadata["sourceUri"],
                "contentHash": metadata["contentHash"], "rawPayloadUri": path.resolve().relative_to(REPOSITORY).as_posix(),
                "license": metadata.get("license"), "role": "subject_access", "relation": "closeMatch",
                "linkStatus": "accepted"})
            report["headings"].append(f"{subject['label']}: {metadata['label']}")
        for entity in subject.get("focus", []):
            run_write(tx, operations, "link_subject_focus", {"subjectId": subject["id"], "entityId": entity})
            report["focus"].append(f"{subject['label']} -> {entity}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(
        localdb.uri(),
        auth=localdb.auth(),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                report = migrate(tx, load_operations())
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                tx.rollback()
                raise
    finally:
        driver.close()
    print(json.dumps(report, indent=1, ensure_ascii=False))
    print("applied" if args.apply else "dry run: rolled back")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
