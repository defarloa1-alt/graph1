"""Migration 033 (2026-11-23): Eurycles opposed Antony, according to Plutarch, Antony 67.2.

    python -m GraphRevised.migrations.033_eurycles_opposed_antony [--apply]

The curator asked for Eurycles' side at Actium to be filed (chat, 2026-11-23). His only link to
the battle was "participated in", so the order of battle could not place him on a side. Plutarch
67.2 has his ship attack Antony's and has him say Caesar's fortune lets him avenge his father, so
the claim is `opposed` (Eurycles, Mark Antony), attributed to Plutarch's Life of Antony, on the
passage the participation claim already rests on. The order of battle puts a person opposed to
someone on a side on the other side.

It is filed as proposed, not accepted: which side a man fought on is read from the passage, and
the curator reviews that reading. No context is set, since the passage does not name the battle.
The quotations avoid the passage's apostrophes, which are stored mis-encoded.

Without --apply it reports and rolls back. Retry-safe: the claim is keyed, so a second run finds it.
"""

from __future__ import annotations

import argparse
import json
import sys

from neo4j import GraphDatabase

from GraphRevised import localdb
from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit

BY = "Claude, at the curator's request (chat, 2026-11-23)"
EURYCLES = "chr:entity:gaius-julius-eurycles"
ANTONY = "chr:entity:mark-antony"
PLUTARCH = "chr:entity:plutarch-life-of-antony"
PASSAGE = "chr:observation:perseus:tlg0007.tlg058.perseus-eng2:67.2:70427323"
QUOTES = (
    "except the ship of Eurycles the Laconian, who attacked vigorously, and brandished a spear on the deck "
    "as though he would cast it at Antony",
    "whom the fortune of Caesar enables to avenge the death of his father",
)


def migrate(tx, operations, registry) -> dict:
    draft = ProposalDraft(
        predicate="opposed", subject_id=EURYCLES, object_id=ANTONY,
        mode="attributed", attributed_to=PLUTARCH,
        observation_ids=(PASSAGE,), quotations=tuple(Quotation(observation_id=PASSAGE, text=q) for q in QUOTES),
        rationale="Plutarch has Eurycles' ship attack Antony's in the pursuit, Eurycles brandishing a spear at "
                  "Antony, and Eurycles saying that Caesar's fortune lets him avenge his father: he fought "
                  "against Antony, on Caesar's (Octavian's) side.",
        proposed_by=BY,
        relevance="Places Eurycles on Octavian's side in the order of battle; until now he had no side.")
    result = submit(tx, draft, registry, operations)
    report = {"claim": result.validation.assertion_id, "proposal": result.validation.proposal_id,
              "outcome": result.validation.outcome.value, "reasons": list(result.validation.reasons),
              "stored": result.stored}
    report["factLayer"] = rebuild(tx)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    driver = GraphDatabase.driver(localdb.uri(), auth=localdb.auth(), notifications_min_severity="OFF")
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
    print(json.dumps(report, indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
