"""Migration 017 (2026-11-18): Scarpus's refusal of Antony, placed in the flight from Actium.

    python -m GraphRevised.migrations.017_scarpus_refusal_in_actium [--apply]

The curator asked (2026-11-18) how Scarpus's refusal (Dio 51.5.6) stands in time
and to the battle. Dio gives no date, and "autumn 31 BC" is a modern inference,
so no time is stored. The refusal's place is its order: the depicted events either
side of it ("Antony sails to Scarpus in Africa", "Antony proceeds to Alexandria
unsuccessful") are already in the phase "Antony follows Cleopatra" of the Battle
of Actium, and the refusal was not. So:

1. The refusal is `partOf` that phase (our placement, as the phase agent's are),
   cited to Dio 51.5.6. Through the phase it falls after the battle (2 September
   31 BC) and before Antony reaches Alexandria.
2. The refusal is `triggeredBy` Antony's sailing to Scarpus, according to Dio:
   Scarpus refused the approach. This closes sailing -> refusal -> Alexandria.

Both proposed for the curator. Without --apply it reports and rolls back.
Retry-safe (claims are keyed).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit

BY = "curator capture (entered by Claude, 2026-11-18)"
DIO = "chr:entity:cassius-dio-roman-history"
OBS = "chr:observation:lacuscurtius:cassius-dio:51.5.6:688a84b4"
PREFIX = "chr:entity:depicted:cassius-dio-roman-history:"
REFUSAL = PREFIX + "scarpus-refuses-antony-and-kills-his-envoys"
SAILING = PREFIX + "antony-sails-to-scarpus-in-africa"
PHASE = "chr:entity:phase:battle-of-actium:antony-follows"
SAILED = "Antony, for his part, had sailed to Pinarius Scarpus in Africa"
REFUSED = "this general not only refused to receive him but furthermore slew the men sent ahead by Antony"


def migrate(tx, operations, registry) -> dict:
    drafts = [
        ProposalDraft(predicate="partOf", subject_id=REFUSAL, object_id=PHASE, mode="asserted",
                      observation_ids=(OBS,), quotations=(Quotation(observation_id=OBS, text=REFUSED),),
                      rationale=("Dio tells the refusal between Antony's sailing to Scarpus and his going on to "
                                 "Alexandria, both already in this phase of the flight from Actium. Dio gives no "
                                 "date; the placement dates it after the battle and before Alexandria."),
                      proposed_by=BY, relevance="Connects Scarpus's refusal to the Battle of Actium."),
        ProposalDraft(predicate="triggeredBy", subject_id=REFUSAL, object_id=SAILING, mode="attributed",
                      attributed_to=DIO, observation_ids=(OBS,),
                      quotations=(Quotation(observation_id=OBS, text=SAILED), Quotation(observation_id=OBS, text=REFUSED)),
                      rationale="In Dio's account Scarpus refuses Antony's approach: the sailing sets off the refusal.",
                      proposed_by=BY, relevance="Closes the chain: sailing to Scarpus, refusal, Alexandria."),
    ]
    report: dict = {"claims": []}
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
