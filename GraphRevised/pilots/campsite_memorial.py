"""The Campsite Memorial of Augustus becomes an Object (curator, 2026-11-13).

    python -m GraphRevised.pilots.campsite_memorial [--apply]

Strauss (p. 5, the curator's transcription): "he dedicated the monument on the
site of his headquarters". The dedication's claimed place was the monument
itself, filed as a Place. In one transaction:

1. The dedication `occurredAt` Octavian's camp at Actium (a local Place from
   curation/campsite-memorial.json), attributed to Strauss, on the same passage.
2. The old `occurredAt` claim's open Proposal is rejected (malformed: it named
   the monument as the place) and the claim superseded by the new one.
3. The memorial moves from Place to Object (`entity-kind`; no open claim names
   it now).
4. The memorial is `involvedIn` the dedication with role dedicated, attributed
   to Strauss.

Where the memorial stands waits for a predicate: `locatedAt` (Object to Place)
is queued in curation/predicate-needs.json. Without --apply it reports and
rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
import sys

from neo4j import GraphDatabase

from GraphRevised.operations import load_operations
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.review import set_entity_kind
from GraphRevised.proposals.schema import ProposalDraft, QualifierQuotation, Quotation
from GraphRevised.proposals.store import reject, submit, supersede
from GraphRevised import localdb

MEMORIAL = "chr:entity:campsite-memorial-of-augustus"
CAMP = "chr:entity:octavian-camp-at-actium"
DEDICATION = ("chr:entity:depicted:strauss-war-that-made-the-roman-empire:"
              "octavian-dedicates-the-monument-at-his-headquarters")
STRAUSS = "chr:entity:strauss-war-that-made-the-roman-empire"
PASSAGE = "chr:observation:transcription:strauss-war-that-made-the-roman-empire:e4c5516b254f"
QUOTE = "he dedicated the monument on the site of his headquarters"
OLD = f"{DEDICATION.replace('chr:entity:', 'chr:assertion:')}:occurred-at:campsite-memorial-of-augustus:q02310b84a7"
BY = "Claude for the curator (approved 2026-11-13)"
PROPOSER = "curator-decision-campsite-memorial-v1"


def draft(predicate: str, subject: str, obj: str, rationale: str, role: str | None = None) -> ProposalDraft:
    return ProposalDraft(
        predicate=predicate, subject_id=subject, object_id=obj, role_id=role,
        observation_ids=(PASSAGE,), quotations=(Quotation(observation_id=PASSAGE, text=QUOTE),),
        qualifier_quotations=(QualifierQuotation(observation_id=PASSAGE, supports="role", text="dedicated the monument"),)
        if role else (),
        mode="attributed", attributed_to=STRAUSS, rationale=rationale, proposed_by=PROPOSER)


def apply(tx, at: str) -> list[str]:
    operations, registry = load_operations(), load_registry()
    lines = []
    placed = submit(tx, draft("occurredAt", DEDICATION, CAMP,
                              "Strauss places the dedication on the site of Octavian's headquarters, not at the "
                              "monument it dedicates (curator, 2026-11-13)."), registry, operations)
    lines.append(f"occurredAt camp: {placed.validation.outcome.value} {placed.validation.assertion_id}")
    new_id = placed.validation.assertion_id

    old = tx.run("MATCH (a:Assertion {id: $id}) OPTIONAL MATCH (p:Proposal {status: 'submitted'})-[:PROPOSES]->(a) "
                 "RETURN a.status AS status, collect(p.id) AS open", id=OLD).single()
    if old is None:
        raise SystemExit(f"{OLD} not found")
    for proposal_id in old["open"]:
        reject(tx, proposal_id, decided_by=BY, decided_at=at, reason="malformed", operations=operations,
               decision_basis="The claim names the monument as the place of its own dedication; Strauss says "
                              "the site of Octavian's headquarters.")
        lines.append(f"rejected proposal {proposal_id}")
    if old["status"] != "superseded":
        supersede(tx, OLD, [new_id], decided_by=BY, decided_at=at, reason="malformed", operations=operations,
                  decision_basis="Re-pointed to Octavian's camp at Actium; the memorial is an Object (curator, 2026-11-13).")
        lines.append(f"superseded {OLD}")

    kind = tx.run("MATCH (e:Entity {id: $id}) RETURN [l IN labels(e) WHERE l <> 'Entity'][0] AS kind",
                  id=MEMORIAL).single()["kind"]
    if kind == "Place":
        set_entity_kind(tx, operations, MEMORIAL, "Place", "Object", decided_by=BY, decided_at=at,
                        decision_basis="A monument (a trophy), not a place; it stands on the site of Octavian's "
                                       "headquarters (curator, 2026-11-13).")
        lines.append("memorial: Place -> Object")

    involved = submit(tx, draft("involvedIn", MEMORIAL, DEDICATION,
                                "The monument Strauss says Octavian dedicated (the Campsite Memorial of Augustus, "
                                "curator's identification).", role="chr:entity:role-dedicated"), registry, operations)
    lines.append(f"involvedIn dedicated: {involved.validation.outcome.value} {involved.validation.assertion_id}"
                 + (f" [{'; '.join(involved.validation.reasons)}]" if involved.validation.reasons else ""))
    return lines


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
                lines = apply(tx, datetime.now(timezone.utc).isoformat())
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("" if args.apply else "(dry run, rolled back)\n") + "\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
