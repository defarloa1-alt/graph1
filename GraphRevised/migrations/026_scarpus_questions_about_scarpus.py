"""Migration 026 (2026-11-19): two Scarpus Questions are about Scarpus, not the battle.

    python -m GraphRevised.migrations.026_scarpus_questions_about_scarpus [--apply]

The lens reader linked two Questions it found in López Sánchez (2010, p. 130), "What
forces did Scarpus command in 32-31 BCE, and where?" and "Why was Scarpus sent to
Cyrenaica in 31 BCE?", to the Battle of Actium. The curator accepted both and asked
(chat, 2026-11-19) for them to be pointed at Scarpus instead. So:

1. Each Question is proposed `about` Lucius Pinarius Scarpus, according to López
   Sánchez, quoting the same lines the reader quoted.
2. The accepted `about` Battle of Actium claim is superseded by it (reason
   underspecified: Scarpus is the more precise subject), decided by the curator.

As applied (2026-11-19): both `about` Scarpus claims already existed. Q7's was accepted
(2026-11-18), so its Actium link was superseded. Q6's had been rejected by the curator
(2026-11-18, "not critical and ambiguous"), so step 1 was refused as a duplicate of a
rejected claim and nothing was superseded; Q6 waits on the curator.

New claims would be left proposed for the curator to accept. Without --apply it reports
and rolls back. Retry-safe (claims are keyed; a second supersede names the same
replacement).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit, supersede
from GraphRevised import localdb

BY = "curator capture (entered by Claude, 2026-11-19)"
WORK = "chr:entity:lopez-sanchez-military-units-of-mark-antony"
SCARPUS = "chr:entity:lucius-pinarius"
ACTIUM = "chr:entity:battle-of-actium"
QUESTIONS = [
    ("chr:entity:proposed-question-what-forces-did-scarpus-command-in-32-31-bce-and-where",
     "chr:observation:transcription:lopez-sanchez-military-units-of-mark-antony:c280a849ca8a",
     "Schmitthenner, Crawford, Sear and Keppie claimed that Scarpus commanded four legions, which were very African in character",
     "The Question asks which forces Scarpus commanded, and where: it is about him."),
    ("chr:entity:proposed-question-why-was-scarpus-sent-to-cyrenaica-in-31-bce",
     "chr:observation:transcription:lopez-sanchez-military-units-of-mark-antony:9107a5fd9fb6",
     "which leads us to believe that he was sent there on a special mission",
     "The Question asks why Scarpus (the passage's 'he') was sent to Cyrenaica: it is about him."),
]
DECISION = {"decided_by": "TD", "reason": "underspecified",
            "decision_basis": "Curator, chat 2026-11-19: the Question is about Scarpus, not the battle."}


def migrate(tx, operations, registry) -> dict:
    report: dict = {"claims": [], "superseded": []}
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for question, observation, quote, why in QUESTIONS:
        draft = ProposalDraft(predicate="about", subject_id=question, object_id=SCARPUS, mode="attributed",
                              attributed_to=WORK, observation_ids=(observation,),
                              quotations=(Quotation(observation_id=observation, text=quote),),
                              rationale=why, proposed_by=BY,
                              relevance="Puts the Question on Scarpus's page, one hop (D-144).")
        result = submit(tx, draft, registry, operations)
        report["claims"].append({"subject": question, "outcome": result.validation.outcome.value,
                                 "reasons": list(result.validation.reasons), "stored": result.stored})
        ids = {r["predicate"] + ":" + r["object"]: r["id"] for r in tx.run(
            """MATCH (a:Assertion {predicate: 'about'})-[:ASSERTION_SUBJECT]->(:Entity {id: $q})
               MATCH (a)-[:ASSERTION_OBJECT]->(o:Entity) WHERE o.id IN [$scarpus, $actium]
                 AND a.status IN ['proposed', 'accepted']
               RETURN a.id AS id, a.predicate AS predicate, o.id AS object""",
            q=question, scarpus=SCARPUS, actium=ACTIUM)}
        old, new = ids.get("about:" + ACTIUM), ids.get("about:" + SCARPUS)
        if old and new:
            supersede(tx, old, [new], decided_at=at, operations=operations, **DECISION)
            report["superseded"].append({"old": old, "new": new})
    report["factLayer"] = rebuild(tx)
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
