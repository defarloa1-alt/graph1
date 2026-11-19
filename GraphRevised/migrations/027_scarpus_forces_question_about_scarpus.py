"""Migration 027 (2026-11-19): "What forces did Scarpus command?" is about Scarpus too.

    python -m GraphRevised.migrations.027_scarpus_forces_question_about_scarpus [--apply]

On 2026-11-18 the curator rejected this Question `about` Lucius Pinarius Scarpus ("not
critical and ambiguous"). On 2026-11-19 the curator ruled that a Question keeps its
links to the persons, places and events the source evidences. López Sánchez (2010,
p. 130) names Scarpus in the line that raises the Question, so:

1. The rejected claim is reopened, decided by the curator.
2. It is proposed again, according to López Sánchez, quoting the page's line on Scarpus's
   forces at Corcyra (the line that raises the Question was the rejected proposal's own
   evidence, so it cannot be proposed again). The curator accepts it.

The Question's accepted link to the Battle of Actium is kept. Without --apply it
reports and rolls back. Retry-safe: a claim already reopened is not reopened twice.
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
from GraphRevised.proposals.store import reopen, submit

BY = "curator capture (entered by Claude, 2026-11-19)"
WORK = "chr:entity:lopez-sanchez-military-units-of-mark-antony"
SCARPUS = "chr:entity:lucius-pinarius"
QUESTION = "chr:entity:proposed-question-what-forces-did-scarpus-command-in-32-31-bce-and-where"
CLAIM = "chr:assertion:proposed-question-what-forces-did-scarpus-command-in-32-31-bce-and-where:about:lucius-pinarius:q4f6334d471"
# The line that raises the Question was the rejected proposal's evidence, and a proposal's id is
# keyed by its evidence, so the same line cannot be proposed again. The page's other line naming
# Scarpus's forces (the source's own answer, already accepted on that answer) is cited instead.
OBSERVATION = "chr:observation:transcription:lopez-sanchez-military-units-of-mark-antony:05c9709158ac"
QUOTE = "In Corcyra in 32 BCE Scarpus might have already been commander of legiones XII Antiqua, XVII Lybica and XVIII Classica"


def migrate(tx, operations, registry) -> dict:
    report: dict = {}
    status = tx.run("MATCH (a:Assertion {id: $id}) RETURN a.status AS s", id=CLAIM).single()["s"]
    if status == "rejected":
        reopen(tx, CLAIM, decided_by="TD", operations=operations,
               decided_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
               decision_basis="Curator, chat 2026-11-19: a Question keeps its links to the persons, "
                              "places and events the source evidences; the passage names Scarpus.")
        report["reopened"] = CLAIM
    draft = ProposalDraft(predicate="about", subject_id=QUESTION, object_id=SCARPUS, mode="attributed",
                          attributed_to=WORK, observation_ids=(OBSERVATION,),
                          quotations=(Quotation(observation_id=OBSERVATION, text=QUOTE),),
                          rationale="The Question asks which forces Scarpus commanded, and where; the passage names him.",
                          proposed_by=BY, relevance="Puts the Question on Scarpus's page, one hop (D-144).")
    result = submit(tx, draft, registry, operations)
    report["claim"] = {"outcome": result.validation.outcome.value, "reasons": list(result.validation.reasons),
                       "stored": result.stored}
    report["factLayer"] = rebuild(tx)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
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
