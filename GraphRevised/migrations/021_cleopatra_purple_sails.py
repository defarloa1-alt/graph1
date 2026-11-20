"""Migration 021 (2026-11-18): Cleopatra's purple sails at Actium, and which species Pliny's shellfish are.

    python -m GraphRevised.migrations.021_cleopatra_purple_sails [--apply]

The curator agreed (2026-11-18) to three things (45 §7): a colour is a link
from an object to a colour (`hadColour`, registry v19), the sails are an Object,
and a Question may be about a Type. From Pliny, Natural History 19.5 (Bostock;
the modern 19.22), stored by migration 020:

1. The Object "purple sails of Cleopatra's royal ship at Actium", according to
   Pliny: `involvedIn` the Battle of Actium in the role "distinguishing mark" (a
   new role, Pliny's words: "the distinguishing mark of the royal ship"),
   `hadColour` purple, and `madeOf` linen. Linen is a reading: the chapter is
   about dyed linen and the sails come in with "too".
2. The Question "Which modern species are Pliny's purpura and buccinum?",
   `about` each of Pliny's two kinds (9.61). It has no Positions: we hold no
   modern work that argues it. GBIF species join when one does (45 §2).

The sails do not link to Tyrian purple: Pliny does not say what they were dyed
with, and he describes cheaper purples (45 §5.3). Everything is proposed for the
curator. Without --apply it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.entities import propose_entity
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, QualifierQuotation, Quotation
from GraphRevised.proposals.store import submit
from GraphRevised import localdb

BY = "curator capture (entered by Claude, 2026-11-18)"
PLINY = "chr:entity:natural-history"
SOURCE = "Pliny, Natural History (Bostock and Riley)"
ACTIUM = "chr:entity:battle-of-actium"
PURPLE, LINEN = "chr:entity:type-purple", "chr:entity:type-linen"
PURPURA = "chr:entity:proposed-type-purpura-pliny-s-purple-shellfish"
BUCCINUM = "chr:entity:proposed-type-buccinum-pliny-s-purple-shellfish"
ROLE = {"id": "chr:entity:role-distinguishing-mark", "label": "distinguishing mark",
        "description": "An object that marks out a party in an event, as a ship's sails mark the royal ship (Pliny, "
                       "Natural History 19.5). Added 2026-11-18 for the curator to review."}
SAILED = "It was with sails of purple, too, that Cleopatra accompanied M. Antonius to the battle of Actium"
MARK = "such being the distinguishing mark of the royal ship"
LINEN_DYED = "Attempts, too, have even been made to dye linen"


def observation(tx, ref: str) -> str:
    row = tx.run("MATCH (o:SourceObservation) WHERE o.id STARTS WITH $prefix RETURN o.id AS id",
                 prefix=f"chr:observation:perseus:phi0978.phi001.perseus-eng1:{ref}:").single()
    if row is None:
        raise SystemExit(f"Pliny {ref} is not stored: run migration 020 first")
    return row["id"]


def migrate(tx, operations, registry, at: str) -> dict:
    sails_obs, kinds_obs = observation(tx, "19.5"), observation(tx, "9.61")
    exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id", id=ROLE["id"]).single() is not None
    run_write(tx, operations, "upsert_entity", {"id": ROLE["id"], "kind": "Type", "label": ROLE["label"],
                                                "shortLabel": ROLE["label"], "description": ROLE["description"],
                                                "status": None if exists else "proposed"})
    run_write(tx, operations, "set_type_category", {
        "id": ROLE["id"], "category": "role", "allowedCategories": sorted(registry.type_categories), "decidedAt": at,
        "decidedBy": BY, "decisionBasis": "a role an object plays in an event (involvedIn needs one)"})
    sails = propose_entity(tx, operations, kind="Object", label="purple sails of Cleopatra's royal ship at Actium",
                           proposed_by=BY, observation_id=sails_obs, quotation=SAILED, source=SOURCE,
                           note="Pliny names the sails, not the ship itself.")
    question = propose_entity(tx, operations, kind="Question",
                              label="Which modern species are Pliny's purpura and buccinum?", proposed_by=BY,
                              observation_id=kinds_obs, quotation='There are two kinds of fish that produce the purple colour',
                              source=SOURCE, note="Open: no Positions until we hold a modern work that argues it (45 §3).")

    def q(text: str, obs: str = sails_obs) -> Quotation:
        return Quotation(observation_id=obs, text=text)

    drafts = [
        ProposalDraft(predicate="involvedIn", subject_id=sails["id"], object_id=ACTIUM, mode="attributed",
                      attributed_to=PLINY, role_id=ROLE["id"], observation_ids=(sails_obs,),
                      quotations=(q(SAILED), q(MARK)),
                      qualifier_quotations=(QualifierQuotation(observation_id=sails_obs, supports="role", text=MARK),),
                      rationale="Pliny: Cleopatra came to Actium with purple sails, the mark of the royal ship, and fled by them.",
                      proposed_by=BY, relevance="Puts the sails at the battle: the first step of the path to the murex."),
        ProposalDraft(predicate="hadColour", subject_id=sails["id"], object_id=PURPLE, mode="attributed",
                      attributed_to=PLINY, observation_ids=(sails_obs,), quotations=(q(SAILED),),
                      rationale="Pliny gives the sails' colour as purple. A colour, not a dye: he does not say what they were dyed with.",
                      proposed_by=BY, relevance="The sails' colour, as a property of the object (45 §4.2)."),
        ProposalDraft(predicate="madeOf", subject_id=sails["id"], object_id=LINEN, mode="attributed",
                      attributed_to=PLINY, observation_ids=(sails_obs,), quotations=(q(LINEN_DYED), q(SAILED)),
                      rationale=("A reading: Pliny's chapter is on dyed linen, and the purple sails come in with "
                                 "\"too\" after Alexander's dyed sails. He does not say \"linen sails\" in so many words."),
                      proposed_by=BY, relevance="What the sails were made of."),
    ]
    for kind in (PURPURA, BUCCINUM):
        drafts.append(ProposalDraft(
            predicate="about", subject_id=question["id"], object_id=kind, mode="asserted", observation_ids=(kinds_obs,),
            quotations=(q("There are two kinds of fish that produce the purple colour", kinds_obs),),
            rationale="The Question asks which modern species this kind of Pliny's names.", proposed_by=BY,
            relevance="Puts the identification one hop from Pliny's kind, as an open question, never a fact."))
    report: dict = {"sails": sails, "question": question, "claims": []}
    for draft in drafts:
        result = submit(tx, draft, registry, operations)
        report["claims"].append({"predicate": draft.predicate, "subject": draft.subject_id, "object": draft.object_id,
                                 "outcome": result.validation.outcome.value, "reasons": list(result.validation.reasons),
                                 "stored": result.stored})
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
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                report = migrate(tx, load_operations(), load_registry(), at)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print("applied" if args.apply else "dry run, rolled back")
    print(json.dumps({k: v for k, v in report.items() if k != "factLayer"}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
