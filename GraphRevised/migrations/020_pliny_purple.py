"""Migration 020 (2026-11-18): Pliny on purple and the murex, the first slice of 45 §5.2.

    python -m GraphRevised.migrations.020_pliny_purple [--apply]

The curator asked (2026-11-18) for purple and the murex from Pliny. This stores
five passages of the Natural History in Bostock and Riley's translation (1855,
public domain; Perseus, preserved in phase-5-source/): 9.60 (the murex and the
purple), 9.61 (the two kinds), 9.62 (dyeing), 9.63 (purple at Rome) and 19.5
(dyed linen; Cleopatra's purple sails at Actium). Bostock numbers by chapter:
9.60-9.63 are 9.124-9.137 in the modern sections, 19.5 is 19.22. Then:

1. Pliny's two purple shellfish as Types (category taxon): "purpura" (also
   "pelagiae") and "buccinum". They are Pliny's kinds, not modern species: which
   species each names is an open question (45 §3), not drawn here.
2. Tyrian purple (from the Getty AAT harvest) `madeFrom` each, and `producedAt`
   Tyre, according to Pliny, quoting him.

The sails (19.5) are stored but not yet drawn: their colour waits on the
curator's choice of how a colour is held (45 §4.2). Everything is proposed for
the curator; this is a reading, so nothing is accepted by rule. Without --apply
it reports and rolls back. Retry-safe.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.adapters.perseus_passages import load_edition, passage_observation
from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.entities import propose_entity
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit

GRAPH_REVISED = Path(__file__).resolve().parents[1]
BY = "curator capture (entered by Claude, 2026-11-18)"
PLINY = "chr:entity:natural-history"
TYRIAN = "chr:entity:type-tyrian-purple"
TYRE = "chr:entity:tyre"
REFS = ("9.60", "9.61", "9.62", "9.63", "19.5")
KINDS = {
    "purpura": ("purpura (Pliny's purple shellfish)", "9.61", 'The other fish is known as the "purpura," or purple',
                "Pliny's larger purple-yielding shellfish, also called pelagiae: a grooved, projecting muzzle and a "
                "shell studded with points (Natural History 9.61). Which modern species it names is an open question "
                "(45 §3)."),
    "buccinum": ("buccinum (Pliny's purple shellfish)", "9.61", 'the smaller fish is that which is called the "buccinum,"',
                 "Pliny's smaller purple-yielding shellfish, named for its likeness to the trumpet-conch; it lives on "
                 "crags (Natural History 9.61). Which modern species it names is an open question (45 §3)."),
}


def migrate(tx, operations, registry, at: str) -> dict:
    path = next((GRAPH_REVISED / "phase-5-source").glob("perseus-phi0978.phi001.perseus-eng1-*.xml"))
    metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    edition = load_edition(path, source_commit=metadata["sourceRevision"], rights=metadata["rights"])
    obs = {}
    for ref in REFS:
        passage = passage_observation(edition, ref, retrieved_at=metadata["retrievedAt"], source_uri=metadata["sourceUri"])
        run_write(tx, operations, "upsert_passage_observation", passage)
        run_write(tx, operations, "link_observation_work", {"observationId": passage["id"], "workId": PLINY})
        obs[ref] = passage["id"]
    report: dict = {"passages": obs, "kinds": {}, "claims": []}

    kinds = {}
    for key, (label, ref, quote, description) in KINDS.items():
        proposed = propose_entity(tx, operations, kind="Type", label=label, proposed_by=BY, observation_id=obs[ref],
                                  quotation=quote, source="Pliny, Natural History (Bostock and Riley)",
                                  note="Pliny's kind, not a modern species (45 §3).")
        kinds[key] = proposed["id"]
        run_write(tx, operations, "upsert_entity", {"id": proposed["id"], "kind": "Type", "label": None,
                                                    "shortLabel": key, "description": description, "status": None})
        run_write(tx, operations, "set_type_category", {
            "id": proposed["id"], "category": "taxon", "allowedCategories": sorted(registry.type_categories),
            "decidedAt": at, "decidedBy": BY, "decisionBasis": "45 §3: an ancient kind of living thing, as its source names it"})
        report["kinds"][key] = proposed

    def q(ref: str, text: str) -> Quotation:
        return Quotation(observation_id=obs[ref], text=text)

    drafts = [
        ProposalDraft(predicate="madeFrom", subject_id=TYRIAN, object_id=kinds["purpura"], mode="attributed",
                      attributed_to=PLINY, observation_ids=(obs["9.61"], obs["9.62"]),
                      quotations=(q("9.61", 'Purples also have another name, that of "pelagiæ'),
                                  q("9.62", "To produce the Tyrian hue the wool is soaked in the juice of the pelagiæ")),
                      rationale=("Pliny: the Tyrian hue is made by soaking the wool in the juice of the pelagiae, his "
                                 "other name for the purpura."),
                      proposed_by=BY, relevance="What Tyrian purple was made from, in Pliny's own kinds."),
        ProposalDraft(predicate="madeFrom", subject_id=TYRIAN, object_id=kinds["buccinum"], mode="attributed",
                      attributed_to=PLINY, observation_ids=(obs["9.62"],),
                      quotations=(q("9.62", "To produce the Tyrian hue the wool is soaked in the juice of the pelagiæ"),
                                  q("9.62", "after which its tint is changed by being dipped in the juice of the buccinum")),
                      rationale="Pliny: the Tyrian hue is finished by dipping the wool in the juice of the buccinum.",
                      proposed_by=BY, relevance="What Tyrian purple was made from, in Pliny's own kinds."),
        ProposalDraft(predicate="producedAt", subject_id=TYRIAN, object_id=TYRE, mode="attributed",
                      attributed_to=PLINY, observation_ids=(obs["9.60"],),
                      quotations=(q("9.60", "In Asia the best purple is that of Tyre"),),
                      rationale=("Pliny names Tyre for the best purple of Asia (and Meninx for Africa, Laconia for "
                                 "Europe). Our reading: the purple of Tyre is Tyrian purple."),
                      proposed_by=BY, relevance="Where the dye was made: the link from the murex to a place."),
    ]
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
    driver = GraphDatabase.driver(os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
                                  auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
                                  notifications_min_severity="OFF")
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
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
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
