"""Migration 024 (2026-11-19): the ancient holders Lange names, so their Positions have authors (fix 4a).

    python -m GraphRevised.migrations.024_ancient_holders [--apply]

Lange's reconsideration reports what ancient writers say, but the historiography reader could
only link a holder that is already a Work (D-156), so seven holdings were logged as unresolved
(runs/article-reader-lange-2011-*.jsonl). The curator chose (2026-11-19) to add the ancient
holders now and leave the modern scholars until we hold their works.

Four Works are proposed, standing primary: Florus's Epitome, Orosius's Histories against the
Pagans, Augustus's lost autobiography (Plutarch's "as Caesar himself wrote"; Lange p. 622 names
the book), and Livy. Each holding is a `holds` claim attributed to Lange, on the transcription
of Lange's page already stored for the reading, its whole span as the quotation. Livy's is
Lange's own inference ("we may assume that Orosius' figure derives from Livy"), and its
rationale says so. "Ancient writers (apart from Dio)" names no Work and stays unresolved.

Code writes this, not a model; everything is proposed for the curator. Without --apply it
reports and rolls back. Retry-safe: a Work is reused by name, a stored claim is not stored twice.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import rebuild
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.entities import propose_entity
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit
from GraphRevised import localdb

BY = "Tony DeFarlo (curator), entered by Claude 2026-11-19"
LANGE = "chr:entity:lange-battle-of-actium-reconsideration"
CITATION = "Lange 2011"
INQUIRY = "chr:inquiry:actium-battle"
T = "chr:observation:transcription:lange-battle-of-actium-reconsideration:"
P = "chr:entity:proposed-position-"

# (key, label, form, the transcription that names it)
WORKS = [
    ("florus", "Florus, Epitome of Roman History", "history", T + "9176456cd5e1"),
    ("orosius", "Orosius, Histories against the Pagans", "history", T + "059a5296f9c9"),
    ("augustus", "Augustus, autobiography (lost)", "commentary", T + "68ad71e7bf92"),
    ("livy", "Livy, Ab Urbe Condita", "history", T + "82f298311240"),
]
# (holder, position id, transcription, what Lange says, the ancient passage he cites)
HOLDINGS = [
    ("florus", P + "octavian-had-over-400-ships-antonius-under-200", T + "9176456cd5e1",
     "Lange reports Florus's figure for the fleets", "Flor. 2.21.5"),
    ("florus", P + "cleopatra-took-the-decisive-initiative-in-the-flight", T + "e2aa7f78c57c",
     "Lange lists Florus among the prose narratives that give the queen's initiative prominence", "Flor. 2.21.8-9"),
    ("orosius", P + "antonius-had-170-ships-octavian-230-beaked-ships", T + "059a5296f9c9",
     "Lange reports Orosius's figure for the fleets", "Oros. 6.19.8-9"),
    ("orosius", P + "cleopatra-took-the-decisive-initiative-in-the-flight", T + "e2aa7f78c57c",
     "Lange lists Orosius among the prose narratives that give the queen's initiative prominence", "Oros. 6.19.11"),
    ("orosius", P + "about-12-000-killed-and-6-000-wounded", T + "76c2cca18d8d",
     "Lange quotes Orosius's casualty figures", "Oros. 6.19.12"),
    ("augustus", P + "antonian-dead-numbered-not-more-than-5-000", T + "68ad71e7bf92",
     "Lange quotes Plutarch giving the figure 'as Caesar himself wrote', from Augustus' lost autobiography (p. 622)",
     "Plut. Ant. 68.1"),
    ("livy", P + "about-12-000-killed-and-6-000-wounded", T + "82f298311240",
     "Lange's inference, not a report: he assumes Orosius's figure derives from Livy", None),
]


def passage(tx, observation: str) -> str:
    row = tx.run("MATCH (o:SourceObservation {id: $id}) RETURN o.passageText AS text", id=observation).single()
    if row is None or not row["text"]:
        raise SystemExit(f"{observation} is not stored: the Lange reading must be stored first")
    return row["text"]


def migrate(tx, operations, registry, at: str) -> dict:
    report: dict = {"works": [], "claims": []}
    ids = {}
    for key, label, form, observation in WORKS:
        work = propose_entity(tx, operations, kind="Work", label=label, proposed_by=BY, observation_id=observation,
                              quotation=passage(tx, observation), source=CITATION,
                              note="An ancient holder Lange reports (fix 4a); proposed for the curator.")
        ids[key] = work["id"]
        run_write(tx, operations, "set_work_form", {"workId": work["id"], "form": form,
                                                    "allowedForms": sorted(registry.work_forms)})
        run_write(tx, operations, "set_work_standing", {
            "id": work["id"], "standing": "primary", "decidedAt": at, "decidedBy": BY,
            "decisionBasis": "an ancient author's own work (42); the curator chose ancient holders first (fix 4a)"})
        report["works"].append({"id": work["id"], "created": work["created"]})
    for holder, position, observation, said, cited in HOLDINGS:
        if tx.run("MATCH (p:Position {id: $id}) RETURN p.id", id=position).single() is None:
            raise SystemExit(f"no Position {position}")
        rests = f" Rests on: {cited}." if cited else ""
        draft = ProposalDraft(
            predicate="holds", subject_id=ids[holder], object_id=position, mode="attributed", attributed_to=LANGE,
            observation_ids=(observation,), quotations=(Quotation(observation_id=observation, text=passage(tx, observation)),),
            rationale=f"{said}.{rests} Logged unresolved by the historiography reader; the holder Work added by migration 024.",
            proposed_by=BY, inquiry_id=INQUIRY, relevance="Gives the Position an author, so the debate grid can place it.")
        result = submit(tx, draft, registry, operations)
        report["claims"].append({"holder": holder, "position": position.removeprefix(P),
                                 "outcome": result.validation.outcome.value, "reasons": list(result.validation.reasons),
                                 "stored": result.stored})
    report["factLayer"] = rebuild(tx)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    driver = GraphDatabase.driver(
        localdb.uri(),
        auth=localdb.auth(),
        notifications_min_severity="OFF",
    )
    at = datetime.now(timezone.utc).isoformat()
    try:
        with driver.session(database=localdb.database()) as session:
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
