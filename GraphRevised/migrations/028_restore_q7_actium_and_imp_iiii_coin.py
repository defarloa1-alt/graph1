"""Migration 028 (2026-11-19): Q7 keeps its Actium link; the Imp IIII Question is about Scarpus on the coin.

    python -m GraphRevised.migrations.028_restore_q7_actium_and_imp_iiii_coin [--apply]

Two curator decisions (chat, 2026-11-19), both following the rule that a Question keeps
every person, place and event link its source evidences:

1. **Restore.** Migration 026 superseded "Why was Scarpus sent to Cyrenaica in 31 BCE?"
   `about` Battle of Actium by its link to Scarpus, before that rule was made. López
   Sánchez's answer names Actium ("provisioning of Antony's army from Egypt to Actium"),
   so the link is restored to accepted (`restore_superseded_assertion`). Its link to
   Scarpus stays.
2. **The coin is the evidence.** "To which victory did Antony's fourth imperial salutation
   (Imp IIII) relate?" `about` Scarpus was proposed according to López Sánchez, but its
   only line says "for himself" and does not name him; the curator rejected that evidence
   ("no clear evidence"). The curator's evidence is the coin: RRC 546/1 strikes Antony's
   IMP IIII on the obverse and SCARPVS IMP on the reverse. A claim according to López
   Sánchez can cite only his passages, so the link is made our own (asserted) on the
   coin, as the Question's link to Antony's acclamation already is (016), and accepted by
   the curator. The evidence-less claim according to López Sánchez is superseded by it.

Without --apply it reports and rolls back. Retry-safe: a restored claim is not restored
twice, claims are keyed, and a second supersede names the same replacement.
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
from GraphRevised.proposals.store import accept, restore, submit, supersede
from GraphRevised import localdb

BY = "curator capture (entered by Claude, 2026-11-19)"
Q7_ACTIUM = "chr:assertion:proposed-question-why-was-scarpus-sent-to-cyrenaica-in-31-bce:about:battle-of-actium:q4f6334d471"
QUESTION = "chr:entity:proposed-question-to-which-victory-did-antony-s-fourth-imperial-salutation-imp-iiii-in-31-bce-relate"
SCARPUS = "chr:entity:lucius-pinarius"
OLD_CLAIM = ("chr:assertion:proposed-question-to-which-victory-did-antony-s-fourth-imperial-salutation-imp-iiii"
             "-in-31-bce-relate:about:lucius-pinarius:q4f6334d471")
COIN = "chr:observation:crro:rrc-546.1:31f2fec34998"
QUOTES = ("Obverse legend: M·ANTO·COS·III·IMP·IIII", "Reverse legend: SCARPVS IMP LEG VIII")


def migrate(tx, operations, registry) -> dict:
    report: dict = {}
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    status = tx.run("MATCH (a:Assertion {id: $id}) RETURN a.status AS s", id=Q7_ACTIUM).single()["s"]
    if status == "superseded":
        restored = restore(tx, Q7_ACTIUM, decided_by="TD", decided_at=at, operations=operations,
                           decision_basis="Curator, chat 2026-11-19: restore. A Question keeps every link its "
                                          "source evidences; López Sánchez's answer names Actium.")
        report["restored"] = {"id": Q7_ACTIUM, "status": restored["assertion"]["status"],
                              "formerReplacements": restored["formerReplacementIds"]}

    draft = ProposalDraft(
        predicate="about", subject_id=QUESTION, object_id=SCARPUS, mode="asserted",
        observation_ids=(COIN,), quotations=tuple(Quotation(observation_id=COIN, text=q) for q in QUOTES),
        rationale="The coin that carries Antony's IMP IIII names Scarpus as imperator on its reverse: the "
                  "Question of which victory earned the salutation is about Scarpus too.",
        proposed_by=BY, relevance="Puts the Imp IIII Question on Scarpus's page, one hop (D-144).")
    result = submit(tx, draft, registry, operations)
    new_claim, proposal = result.validation.assertion_id, result.validation.proposal_id
    report["claim"] = {"id": new_claim, "outcome": result.validation.outcome.value,
                       "reasons": list(result.validation.reasons), "stored": result.stored}
    if result.stored:
        accept(tx, proposal, decided_by="TD", decided_at=at, registry=registry, operations=operations,
               decision_basis="Curator, chat 2026-11-19: the coin is the evidence.")
        report["claim"]["accepted"] = proposal
    if new_claim and tx.run("MATCH (a:Assertion {id: $id}) RETURN a.status AS s", id=new_claim).single()["s"] == "accepted":
        superseded = supersede(tx, OLD_CLAIM, [new_claim], decided_by="TD", decided_at=at, reason="unsupported",
                               operations=operations,
                               decision_basis="Curator, chat 2026-11-19: the coin is the evidence; López Sánchez's "
                                              "line does not name Scarpus, so the link is our own, on RRC 546/1.")
        report["superseded"] = {"old": OLD_CLAIM, "new": superseded["replacementIds"]}
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
