"""A book's Library of Congress record into the graph: evidence, an identifier, and claims for review.

    python -m GraphRevised.harvest.lc_record <lccn> --work <the book's Entity id> [--apply]

The record (preserved by adapters/lc_catalog.py) becomes a `record` observation of the catalog, a
local Work of form `dataset`: its text is the record's own wording, line by line, and every claim
quotes it verbatim. Then, all proposed and visible at once, nothing accepted:

- the book's LCCN as an identifier record (crosswalk, proposed), with its LCC and DDC numbers as
  the record gives them (a book's call numbers, never a hierarchy; D-094);
- `<author> authorOf <book>` from the author heading and the title page's statement of
  responsibility, when exactly one local Person is that author: by the LCNAF id the heading resolves
  to, or else by the heading's name read in direct order;
- `<entity> describedBy <book>` for each subject heading whose authority id, resolved at id.loc.gov,
  an Entity already holds;
- everything else listed for the curator: headings no Entity holds (identity is the curator's), and
  subject strings that are candidates for subject buckets (28).

Dry run by default: one transaction, rolled back. --apply commits. A report goes to runs/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.adapters.lc_catalog import (CatalogRecord, PERMALINK, RIGHTS, parse_record, preserved_record,
                                              resolve_heading)
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit

GRAPH_REVISED = Path(__file__).resolve().parents[1]
RUNS = GRAPH_REVISED / "runs"
CATALOG_WORK = {"id": "chr:entity:library-of-congress-catalog", "kind": "Work", "label": "Library of Congress catalog",
                "shortLabel": "LC catalog", "form": "dataset",
                "description": "The Library of Congress's bibliographic records: what LC's catalogers recorded "
                               "about an edition, never what the book says."}
PROPOSER = "lc-catalog-record"
VERSION = "lc-record-v1"


def record_lines(record: CatalogRecord) -> list[str]:
    """The record's own wording, one field a line: what claims may quote."""
    lines = [f"{n.text}, {n.relator}." if n.relator else n.text for n in record.names[:1]]
    lines.append(f"{record.title} / {record.responsibility}." if record.responsibility else record.title)
    lines += [x for x in (record.edition, record.publication, record.extent) if x]
    lines += [f"ISBN {d} {q or ''}".strip() for d, q, cancelled in record.isbns if not cancelled]
    lines += [f"LCC {record.lcc}"] if record.lcc else []
    lines += [f"DDC {record.ddc}" + (f" (edition {record.ddc_edition})" if record.ddc_edition else "")] if record.ddc else []
    lines += [f"Contents: {' -- '.join(record.contents)}"] if record.contents else []
    lines += [record.bibliography_note] if record.bibliography_note else []
    lines += [f"Subject: {s.text}" for s in record.subjects if s.thesaurus == "lcsh"]
    return lines


def direct_order(heading: str) -> str:
    """"Surname, Forenames" as "Forenames Surname"; dates and other parts after a second comma dropped."""
    parts = [p.strip() for p in heading.split(",")]
    return f"{parts[1]} {parts[0]}" if len(parts) >= 2 and parts[1] else heading


def holders(tx: Any, system: str, identifier: str) -> list[str]:
    return tx.run("MATCH (e:Entity)-[:HAS_AUTHORITY_RECORD]->(:AuthorityRecord {system: $s, identifier: $i}) "
                  "WHERE e.status <> 'deprecated' RETURN e.id AS id", s=system, i=identifier).value()


def persons_named(tx: Any, name: str) -> list[str]:
    return tx.run("MATCH (e:Entity {kind: 'Person'}) WHERE e.status <> 'deprecated' "
                  "AND (toLower(e.label) = toLower($n) OR toLower(e.shortLabel) = toLower($n)) RETURN e.id AS id",
                  n=name).value()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lccn")
    parser.add_argument("--work", required=True, help="the book's Work Entity id")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    path, metadata = preserved_record(args.lccn)
    record = parse_record(path.read_bytes())
    resolved_path = path.with_suffix(".headings.json")
    if resolved_path.exists():
        resolved = json.loads(resolved_path.read_text(encoding="utf-8"))
    else:  # each heading resolved once, kept beside the record
        resolved = {h.text: resolve_heading(h.text)
                    for h in (*record.names, *record.subjects) if h.thesaurus in ("", "lcsh")}
        resolved_path.write_bytes((json.dumps(resolved, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    text = "\n".join(record_lines(record))
    observation_id = f"chr:observation:lc-catalog:{record.lccn}:{metadata['contentHash'][:12]}"
    operations, registry = load_operations(), load_registry()
    report: dict[str, Any] = {"lccn": record.lccn, "work": args.work, "version": VERSION, "applied": args.apply,
                              "createdAt": datetime.now(timezone.utc).isoformat(), "outcomes": [], "forCurator": []}

    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                book = tx.run("MATCH (w:Entity {id: $id, kind: 'Work'}) RETURN w.label AS label", id=args.work).single()
                if book is None:
                    raise SystemExit(f"{args.work} is not a Work in the graph")
                exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=CATALOG_WORK["id"]).single() is not None
                run_write(tx, operations, "upsert_entity", {k: CATALOG_WORK[k] for k in ("id", "kind", "label", "shortLabel", "description")}
                          | {"status": None if exists else "proposed"})
                run_write(tx, operations, "set_work_form", {"workId": CATALOG_WORK["id"], "form": CATALOG_WORK["form"],
                                                            "allowedForms": sorted(registry.work_forms)})
                run_write(tx, operations, "upsert_record_observation", {
                    "id": observation_id, "label": f"Library of Congress catalog record: {record.title} (LCCN {record.lccn})",
                    "shortLabel": f"LC record {record.lccn}", "sourceSystem": "Library of Congress catalog",
                    "sourceEntityId": record.lccn, "locator": PERMALINK.format(lccn=record.lccn),
                    "passageText": text, "passageHash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    "editorialNotes": [], "language": "en", "workTitle": record.title,
                    "author": record.names[0].text if record.names else None, "editionCitation": record.publication,
                    "rights": RIGHTS, "sourceUri": metadata["sourceUri"], "sourceRevision": record.revised,
                    "retrievedAt": metadata["retrievedAt"], "contentHash": metadata["contentHash"],
                    "rawPayloadUri": f"GraphRevised/phase-5-source/{path.name}", "workId": CATALOG_WORK["id"]})
                calls = "; ".join(x for x in (f"LCC {record.lcc}" if record.lcc else None,
                                              f"DDC {record.ddc}" if record.ddc else None) if x)
                run_write(tx, operations, "upsert_authority", {
                    "entityId": args.work, "id": f"chr:authority:lccn:{record.lccn}", "system": "LCCN",
                    "identifier": record.lccn, "label": f"Library of Congress record: {record.title} (LCCN {record.lccn})",
                    "shortLabel": f"LCCN {record.lccn}", "description": calls or None,
                    "retrievedAt": metadata["retrievedAt"], "sourceUri": PERMALINK.format(lccn=record.lccn),
                    "sourceRevision": None, "contentHash": metadata["contentHash"],
                    "rawPayloadUri": f"GraphRevised/phase-5-source/{path.name}",
                    "role": "crosswalk", "relation": "closeMatch", "linkStatus": "proposed"})

                drafts: list[tuple[str, ProposalDraft]] = []
                if record.names:
                    author = record.names[0]
                    lcnaf = resolved.get(author.text)
                    by_id = holders(tx, "LCNAF", lcnaf["identifier"]) if lcnaf else []
                    people = by_id or persons_named(tx, direct_order(author.text))
                    basis = "its LCNAF id" if by_id else f"the name {direct_order(author.text)!r} in direct order"
                    if len(people) == 1:
                        quote = f"{record_lines(record)[0]}\n{record_lines(record)[1]}"
                        drafts.append(("authorOf", ProposalDraft(
                            predicate="authorOf", subject_id=people[0], object_id=args.work,
                            observation_ids=(observation_id,), quotations=(Quotation(observation_id=observation_id, text=quote),),
                            rationale=f"LC's record names {author.text} as {author.relator or 'author'}, and the title "
                                      f"page's statement reads \"{record.responsibility}\"; the Person was matched by {basis}.",
                            proposed_by=PROPOSER, prompt_version=VERSION,
                            relevance="Who wrote the book, so attestation counts its author, not the book.")))
                    else:
                        report["forCurator"].append({"author heading": author.text, "resolves to": lcnaf,
                                                     "local persons": people, "why": "not exactly one Person"})
                    if lcnaf and people and len(people) == 1 and not by_id:
                        report["forCurator"].append({"identity candidate": people[0], "LCNAF": lcnaf,
                                                     "why": "the author's LC name record; linking it is the curator's"})
                for heading in record.subjects:
                    if heading.thesaurus != "lcsh":
                        continue
                    found = resolved.get(heading.text)
                    entities = holders(tx, found["system"], found["identifier"]) if found else []
                    if len(entities) == 1:
                        drafts.append((heading.text, ProposalDraft(
                            predicate="describedBy", subject_id=entities[0], object_id=args.work,
                            observation_ids=(observation_id,),
                            quotations=(Quotation(observation_id=observation_id, text=f"Subject: {heading.text}"),),
                            rationale=f"LC assigns the book the heading \"{heading.text}\" ({found['system']} "
                                      f"{found['identifier']}), the authority record this Entity already holds.",
                            proposed_by=PROPOSER, prompt_version=VERSION,
                            relevance="A book about the entity, by LC's own subject analysis: its Read more list.")))
                    else:
                        report["forCurator"].append({"heading": heading.text, "resolves to": found, "holders": entities,
                                                     "why": ("LC has no record of exactly this heading" if not found
                                                                else "no Entity holds this record" if not entities
                                                                else "more than one Entity holds it")})
                for key, draft in drafts:
                    result = submit(tx, draft, registry, operations)
                    report["outcomes"].append({"for": key, "subject": draft.subject_id, "predicate": draft.predicate,
                                               "outcome": result.validation.outcome.value, "stored": result.stored,
                                               "reasons": list(result.validation.reasons)})
                if args.apply:
                    tx.commit()
                else:
                    tx.rollback()
            except BaseException:
                if tx.closed() is False:
                    tx.rollback()
                raise
    finally:
        driver.close()

    RUNS.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = RUNS / f"lc-record-{record.lccn}-{stamp}.json"
    out.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    for o in report["outcomes"]:
        print(f"{o['outcome']:12} {o['subject']} {o['predicate']} {args.work}" + (f"  {o['reasons']}" if o["reasons"] else ""))
    for c in report["forCurator"]:
        print("for the curator:", c)
    print(f"{'applied' if args.apply else 'dry run, rolled back'} -> {out.relative_to(GRAPH_REVISED.parent).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
