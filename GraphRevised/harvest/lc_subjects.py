"""Library of Congress subject headings into the graph: a book's subjects, and each heading's neighbours.

    python -m GraphRevised.harvest.lc_subjects [--apply]

Curator, 2026-11-16: capture all of a record's subjects, not only those an Entity holds.

1. **A book's subjects.** For each Work with a Library of Congress catalog record
   (an LCCN authority record, read by harvest/lc_record.py), every subject heading
   the record assigns that resolves at id.loc.gov becomes a link from the book to
   the heading's AuthorityRecord (`HAS_SUBJECT_HEADING`), whether or not an Entity
   holds that heading yet. When an Entity later gets the heading as its identity,
   the book is one hop away through it.
2. **A heading's neighbours, one hop.** For each LCSH record in the graph, the
   record's broader, narrower and related headings (skos) become records too, with
   `BROADER_HEADING` (narrower read in reverse) and `RELATED_HEADING` links. One hop
   only: the neighbours' own neighbours are not followed.

Both are the records' own statements, read by code: accepted by rule (D-145).
Which Entity a heading is stays the curator's: a heading's close match in Wikidata
(LC states it) is listed as an identity lead, never linked. Headings LC has no
record for (a string with subdivisions) are listed. Without --apply it reports and
rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.adapters.lc_catalog import parse_record, preserved_record
from GraphRevised.adapters.library_headings import LCSH_URI, preserved_heading
from GraphRevised.operations import load_operations, run_write
from GraphRevised import localdb

GRAPH_REVISED = Path(__file__).resolve().parents[1]
REPOSITORY = GRAPH_REVISED.parent
RUNS = GRAPH_REVISED / "runs"
RULE = "rule: code-made extraction (D-145): the Library of Congress record's own headings"
SKOS = "http://www.w3.org/2004/02/skos/core#"
LABELS = (f"{SKOS}prefLabel", "http://www.loc.gov/mads/rdf/v1#authoritativeLabel")
LCSH_PREFIX = LCSH_URI.format(identifier="")
WIKIDATA_PREFIX = "http://www.wikidata.org/entity/"

BOOKS = """
MATCH (w:Entity:Work)-[:HAS_AUTHORITY_RECORD]->(r:AuthorityRecord {system: "LCCN"})
RETURN w.id AS work, r.identifier AS lccn ORDER BY w.id
"""
# Only headings an Entity holds or a book is about: a neighbour's own neighbours are never followed.
LCSH_RECORDS = """
MATCH (r:AuthorityRecord {system: 'LCSH'})
WHERE EXISTS { (:Entity)-[:HAS_AUTHORITY_RECORD]->(r) } OR EXISTS { (:Work)-[:HAS_SUBJECT_HEADING]->(r) }
RETURN r.identifier AS id ORDER BY id
"""
HOLDERS = """
MATCH (e:Entity)-[:HAS_AUTHORITY_RECORD]->(:AuthorityRecord {system: $system, identifier: $identifier})
RETURN e.id AS id
"""


def neighbours(payload: list[dict[str, Any]], identifier: str) -> dict[str, Any]:
    """An LCSH record's broader, narrower and related headings, with their labels, and its close matches."""
    nodes = {n.get("@id"): n for n in payload}
    labels = {uri: next((v[0]["@value"] for key in LABELS for v in [n.get(key)] if v), None) for uri, n in nodes.items()}
    me = nodes.get(LCSH_URI.format(identifier=identifier), {})

    def targets(key: str) -> list[tuple[str, str | None]]:
        return [(t["@id"][len(LCSH_PREFIX):], labels.get(t["@id"])) for t in me.get(f"{SKOS}{key}", [])
                if t.get("@id", "").startswith(LCSH_PREFIX)]

    return {"broader": targets("broader"), "narrower": targets("narrower"), "related": targets("related"),
            "wikidata": [(t["@id"][len(WIKIDATA_PREFIX):], labels.get(t["@id"])) for t in me.get(f"{SKOS}closeMatch", [])
                         if t.get("@id", "").startswith(WIKIDATA_PREFIX)]}


def record_params(system: str, identifier: str, label: str, path: Path | None, metadata: dict | None) -> dict:
    return {"id": f"chr:authority:{system.lower()}:{identifier}", "system": system, "identifier": identifier,
            "label": label, "sourceUri": (metadata or {}).get("uri") or LCSH_URI.format(identifier=identifier),
            "retrievedAt": (metadata or {}).get("retrievedAt"), "contentHash": (metadata or {}).get("contentHash"),
            "rawPayloadUri": path.relative_to(REPOSITORY).as_posix() if path else None}


def harvest(tx, operations, at: str) -> dict[str, Any]:
    report: dict[str, Any] = {"books": [], "unresolved": [], "neighbours": Counter(), "leads": []}
    signed = {"decidedAt": at, "decidedBy": RULE}
    for book in tx.run(BOOKS).data():
        path, record_metadata = preserved_record(book["lccn"])
        record = parse_record(path.read_bytes())
        resolved_path = path.with_suffix(".headings.json")
        resolved = json.loads(resolved_path.read_text(encoding="utf-8")) if resolved_path.exists() else {}
        observation = f"chr:observation:lc-catalog:{record.lccn}:{record_metadata['contentHash'][:12]}"  # as lc_record
        linked = []
        for heading in (h for h in record.subjects if h.thesaurus == "lcsh"):
            found = resolved.get(heading.text)
            if not found:
                report["unresolved"].append({"work": book["work"], "heading": heading.text})
                continue
            run_write(tx, operations, "upsert_heading_record",
                      record_params(found["system"], found["identifier"], found["label"], None, {"uri": found["uri"]}))
            run_write(tx, operations, "link_subject_heading", {
                "workId": book["work"], "system": found["system"], "identifier": found["identifier"],
                "heading": heading.text, "observationId": observation, **signed,
                "decisionBasis": f"LC's record {record.lccn} assigns the subject heading \"{heading.text}\""})
            linked.append(f"{found['label']} ({found['system']} {found['identifier']})")
        report["books"].append({"work": book["work"], "lccn": record.lccn, "subjects": linked})

    for identifier in tx.run(LCSH_RECORDS).value():
        path, metadata = preserved_heading("LCSH", identifier)
        found = neighbours(json.loads(path.read_bytes()), identifier)
        tx.run("MATCH (r:AuthorityRecord {system: 'LCSH', identifier: $i}) WHERE r.rawPayloadUri IS NULL "
               "SET r.rawPayloadUri = $uri, r.contentHash = $hash, r.retrievedAt = $at",
               i=identifier, uri=path.relative_to(REPOSITORY).as_posix(), hash=metadata["contentHash"],
               at=metadata["retrievedAt"])
        for relation, pairs in (("broader", found["broader"]), ("narrower", found["narrower"]),
                                ("related", found["related"])):
            for other, label in pairs:
                run_write(tx, operations, "upsert_heading_record",
                          record_params("LCSH", other, label or other, None, None))
                start, end = (other, identifier) if relation == "narrower" else (identifier, other)
                run_write(tx, operations, "link_heading_relation", {
                    "system": "LCSH", "from": start, "to": end, "sourceIdentifier": identifier,
                    "relation": "broader" if relation == "narrower" else relation, **signed})
                report["neighbours"][relation] += 1
        holders = tx.run(HOLDERS, system="LCSH", identifier=identifier).value()
        for qid, label in found["wikidata"]:
            same = tx.run("MATCH (e:Entity)-[:HAS_AUTHORITY_RECORD]->(:AuthorityRecord {system: 'Wikidata', "
                          "identifier: $q}) RETURN e.id", q=qid).value()
            if set(same) != set(holders):
                report["leads"].append({"lcsh": identifier, "wikidata": f"{label} ({qid})", "entities with it": same,
                                        "entities with the heading": holders})
    return report


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
                report = harvest(tx, load_operations(), at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print("applied" if args.apply else "dry run, rolled back")
    for book in report["books"]:
        print(f"  {book['work']} (LCCN {book['lccn']}): {len(book['subjects'])} subject headings")
        for s in book["subjects"]:
            print(f"    {s}")
    for u in report["unresolved"]:
        print(f"  no LC record for the heading \"{u['heading']}\" ({u['work']})")
    print(f"  heading neighbours linked: {dict(report['neighbours']) or 'none'}")
    for lead in report["leads"]:
        print(f"  identity lead: LCSH {lead['lcsh']} closely matches {lead['wikidata']}; "
              f"held by {lead['entities with it'] or 'no Entity'}; heading held by {lead['entities with the heading'] or 'no Entity'}")
    RUNS.mkdir(exist_ok=True)
    (RUNS / f"lc-subjects-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json").write_text(
        json.dumps(report | {"applied": args.apply}, indent=2, ensure_ascii=False, default=dict), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
