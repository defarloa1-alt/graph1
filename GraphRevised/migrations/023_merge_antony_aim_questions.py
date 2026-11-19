"""Migration 023 (2026-11-19): one Question for Antony's aim at Actium (fix 6, D-152).

    python -m GraphRevised.migrations.023_merge_antony_aim_questions [--apply]

Lange's reading was drafted twice as a Question: "Was Antony's aim in the battle of Actium
victory, or withdrawal by sea?" (two Positions) and "What was Antonius' aim in the battle: to
win it, or to break out and withdraw?" (four). One Position already answered both. The curator
chose (2026-11-19) to keep the second, with the first as an alternative name.

1. The one claim the kept Question lacks is filed on it with its existing evidence: "Antony
   fought for victory until Cleopatra fled" answers it, according to Lange, on the same
   quotation. Its other claims (about the battle, about Antony, the shared answer) are already
   on the kept Question.
2. The entity-mention note that recorded the duplicate's wording is deleted: the wording is
   kept as an alternative name.
3. merge_unreviewed_entity removes the duplicate and its claims, and records the merge on the
   kept Question (mergedIds, alternativeNames, mergeLog). Then the fact layer is rebuilt.

Nothing here is the model's: the claim is a copy of a stored proposal, onto the Question it was
always about. Without --apply it reports and rolls back. A retry finds no duplicate and stops.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit

BY = "Tony DeFarlo (curator)"
BASIS = ("The same question drafted twice from Lange's reconsideration (fix 6 of Explorer Fixes on the Stage "
         "Design); kept the wording with four Positions (curator, 2026-11-19)")
E = "chr:entity:"
DUPLICATE = E + "proposed-question-was-antony-s-aim-in-the-battle-of-actium-victory-or-withdrawal-by-sea"
KEEP = E + "proposed-question-what-was-antonius-aim-in-the-battle-to-win-it-or-to-break-out-and-withdraw"
DUPLICATE_NAME = "Was Antony's aim in the battle of Actium victory, or withdrawal by sea?"

# The duplicate's claims, read before anything is removed: what each says, and its evidence.
CLAIMS = """
MATCH (q:Entity {id: $id})<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(a:Assertion)
MATCH (a)-[:ASSERTION_SUBJECT]->(subject:Entity)
OPTIONAL MATCH (a)-[:ASSERTION_OBJECT]->(object:Entity)
OPTIONAL MATCH (a)-[:ATTRIBUTED_TO]->(work:Entity)
MATCH (p:Proposal)-[:PROPOSES]->(a)
OPTIONAL MATCH (p)-[e:PROPOSES_EVIDENCE]->(o:SourceObservation)
RETURN a.predicate AS predicate, a.mode AS mode, subject.id AS subject, object.id AS object, work.id AS work,
       p.rationale AS rationale, p.inquiryId AS inquiry, collect({observation: o.id, quotation: e.quotation}) AS evidence
"""
HELD = """
MATCH (a:Assertion {predicate: $predicate})-[:ASSERTION_SUBJECT]->(:Entity {id: $subject})
MATCH (a)-[:ASSERTION_OBJECT]->(:Entity {id: $object})
WHERE a.status IN ["accepted", "proposed"]
RETURN count(a) > 0 AS held
"""


def migrate(tx, operations, registry, at: str) -> dict:
    if tx.run("MATCH (q:Entity {id: $id}) RETURN q.id", id=DUPLICATE).single() is None:
        return {"merged": False, "reason": "no duplicate: already merged"}
    report: dict = {"refiled": [], "alreadyHeld": []}
    for claim in tx.run(CLAIMS, id=DUPLICATE).data():
        subject = KEEP if claim["subject"] == DUPLICATE else claim["subject"]
        obj = KEEP if claim["object"] == DUPLICATE else claim["object"]
        what = f"{claim['predicate']} {subject.removeprefix(E)} -> {obj.removeprefix(E)}"
        if tx.run(HELD, predicate=claim["predicate"], subject=subject, object=obj).single()["held"]:
            report["alreadyHeld"].append(what)
            continue
        evidence = [e for e in claim["evidence"] if e["observation"]]
        draft = ProposalDraft(
            predicate=claim["predicate"], subject_id=subject, object_id=obj, mode=claim["mode"] or "asserted",
            attributed_to=claim["work"], observation_ids=tuple(e["observation"] for e in evidence),
            quotations=tuple(Quotation(observation_id=e["observation"], text=e["quotation"])
                             for e in evidence if e["quotation"]),
            rationale=f"{claim['rationale']} Filed on the kept Question when its duplicate was merged (migration 023).",
            proposed_by=BY, inquiry_id=claim["inquiry"],
            relevance="Keeps the answer when two drafts of one Question become one.")
        result = submit(tx, draft, registry, operations)
        report["refiled"].append({"claim": what, "outcome": result.validation.outcome.value,
                                  "reasons": list(result.validation.reasons), "stored": result.stored})
        if not result.stored:
            raise SystemExit(f"could not file {what}: {result.validation.reasons}")
    notes = tx.run("MATCH (n:Annotation {kind: 'entity-mention'})-[:CONCERNS]->(:Entity {id: $id}) RETURN n.id AS id",
                   id=DUPLICATE).data()
    for note in notes:
        run_write(tx, operations, "delete_annotation", {"id": note["id"]})
    report["deletedNotes"] = [n["id"] for n in notes]
    report["merge"] = run_write(tx, operations, "merge_unreviewed_entity", {
        "duplicateId": DUPLICATE, "survivorId": KEEP, "alternativeName": DUPLICATE_NAME,
        "decidedAt": at, "decidedBy": BY, "decisionBasis": BASIS})
    report["factLayer"] = rebuild(tx)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    at = datetime.now(timezone.utc).isoformat()
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            tx = session.begin_transaction()
            try:
                report = migrate(tx, load_operations(), load_registry(), at)
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
