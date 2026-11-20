"""Migration 016 (2026-11-18): the Imp IIII acclamations on Scarpus's coins, and Sear's "occasion uncertain".

    python -m GraphRevised.migrations.016_imp_iiii_acclamations [--apply]

The curator asked (2026-11-18) for the one secure fact under the Imp IIII
Question: Scarpus's coins of 31 BC (RRC 546, harvested by harvest/crro_coins.py)
name Antony imperator for the fourth time (M·ANTO·COS·III·IMP·IIII) and Scarpus
imperator (SCARPVS IMP). They do not name the victory, and the striking date
does not date it. So:

1. Two proposed Events, "Antony hailed imperator for the fourth time" and
   "Pinarius Scarpus hailed imperator", each resting on a coin's legend.
2. Antony and Scarpus each `participatedIn` their acclamation, attributed to
   the coinage, quoting the legend. No time: the coin is a date by which, not
   the date of the acclamation.
3. The Imp IIII Question is `about` Antony's acclamation (our own link, cited
   to the coin).
4. Sear's answer, as López Sánchez reports it (p. 126 n. 5): "the occasion for
   his fourth is uncertain" (Sear 1998: 238), a Position answering the
   Question. Sear 1998 is not a Work yet, so the holding is logged unresolved.

Everything is proposed for the curator. Without --apply it reports and rolls
back. Retry-safe (entities are reused by name, claims by their key).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.export.fact_layer import rebuild
from GraphRevised.harvest.article_citations import ARTICLES, article_pages
from GraphRevised.operations import load_operations
from GraphRevised.proposals.entities import propose_entity
from GraphRevised.proposals.historiography import (HistoriographyOutput, ReaderHolding, ReaderPosition,
                                                   store_historiography, to_historiography)
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit
from GraphRevised import localdb

ROOT = Path(__file__).resolve().parents[2]
BY = "curator capture (entered by Claude, 2026-11-18)"
COINS = "chr:entity:pinarius-scarpus-coinage-rrc-546"
QUESTION = ("chr:entity:proposed-question-to-which-victory-did-antony-s-fourth-imperial-salutation-"
            "imp-iiii-in-31-bce-relate")
ANTONY, SCARPUS = "chr:entity:mark-antony", "chr:entity:lucius-pinarius"
SEAR_QUOTE = "the occasion for his fourth is uncertain” (Sear 1998:238)"


def legend(tx, label: str, side: str) -> tuple[str, str]:
    """A coin type's observation id and its legend line, as stored."""
    row = tx.run("MATCH (o:SourceObservation {shortLabel: $label, sourceSystem: 'Coinage of the Roman Republic Online'}) "
                 "RETURN o.id AS id, o.passageText AS text", label=label).single()
    if row is None:
        raise SystemExit(f"{label} is not stored: run harvest/crro_coins.py rrc-546 --apply first")
    line = next(l for l in row["text"].splitlines() if l.startswith(f"{side} legend: "))
    return row["id"], line


def migrate(tx, operations, registry, at: str) -> dict:
    report: dict = {"events": [], "claims": [], "historiography": None}
    antony_obs = [legend(tx, label, "Obverse") for label in ("RRC 546/1", "RRC 546/2a", "RRC 546/3a")]
    scarpus_obs = [legend(tx, "RRC 546/1", "Reverse"), legend(tx, "RRC 546/7", "Obverse")]

    events = {}
    for key, label, (obs, quote) in (("antony", "Antony hailed imperator for the fourth time", antony_obs[0]),
                                     ("scarpus", "Pinarius Scarpus hailed imperator", scarpus_obs[0])):
        proposed = propose_entity(tx, operations, kind="Event", label=label, proposed_by=BY, observation_id=obs,
                                  quotation=quote, source="Coinage of the Roman Republic Online",
                                  note="The coin records the title; it does not name the victory or date it.")
        events[key] = proposed["id"]
        report["events"].append({"label": label, "id": proposed["id"], "created": proposed["created"]})

    drafts = [
        ProposalDraft(predicate="participatedIn", subject_id=ANTONY, object_id=events["antony"], mode="attributed",
                      attributed_to=COINS, observation_ids=tuple(o for o, _ in antony_obs),
                      quotations=tuple(Quotation(observation_id=o, text=q) for o, q in antony_obs),
                      rationale=("Scarpus's coins of 31 BC style Antony IMP IIII, imperator for the fourth time: an "
                                 "acclamation after a victory. The coins do not name the victory, and their date is "
                                 "a date by which, not the date of the acclamation."),
                      proposed_by=BY, relevance="The one attested fact under the Imp IIII Question."),
        ProposalDraft(predicate="participatedIn", subject_id=SCARPUS, object_id=events["scarpus"], mode="attributed",
                      attributed_to=COINS, observation_ids=tuple(o for o, _ in scarpus_obs),
                      quotations=tuple(Quotation(observation_id=o, text=q) for o, q in scarpus_obs),
                      rationale=("Scarpus's own coins of 31 BC style him IMP, imperator, on issues for Antony and "
                                 "again on issues for Octavian; the occasion is not named."),
                      proposed_by=BY, relevance="Scarpus's acclamation, which López Sánchez ties to Antony's fourth."),
        ProposalDraft(predicate="about", subject_id=QUESTION, object_id=events["antony"], mode="asserted",
                      observation_ids=(antony_obs[0][0],),
                      quotations=(Quotation(observation_id=antony_obs[0][0], text=antony_obs[0][1]),),
                      rationale="The Question asks which victory this acclamation, recorded on the coin, followed.",
                      proposed_by=BY, relevance="Puts the debate one hop from the attested acclamation."),
    ]
    for draft in drafts:
        result = submit(tx, draft, registry, operations)
        report["claims"].append({"predicate": draft.predicate, "subject": draft.subject_id, "object": draft.object_id,
                                 "outcome": result.validation.outcome.value, "reasons": list(result.validation.reasons),
                                 "stored": result.stored})

    article = next(a for a in json.loads(ARTICLES.read_text(encoding="utf-8"))["articles"]
                   if a["id"] == "lopez-sanchez-2010")
    page = dict(article_pages(ROOT / article["pdf"], article["skipPages"], article["firstPage"]))[126]
    output = HistoriographyOutput(questions=[], receptions=[], positions=[ReaderPosition(
        key="sear", label="The occasion of Antony's fourth acclamation is unknown", existing_id="",
        question=QUESTION, quotation=SEAR_QUOTE)], holdings=[ReaderHolding(
            position="sear", verb="holds", holder_id="", holder_name="Sear", holder_year="1998", own=False,
            quotation=SEAR_QUOTE, stance="", stance_quotation="", time_source_expression="", time_quotation="",
            time_edtf="", rests_on=[])])
    plan = to_historiography(output, page, work_id=article["work"], locator="p. 126", scope_ids=set(),
                             work_ids={article["work"]}, proposed_by=BY, model_id=None, prompt_version=None,
                             inquiry_id=None, existing={QUESTION})
    stored = store_historiography(tx, operations, registry, plan, work_label="López Sánchez, Military Units of "
                                  "Mark Antony and Lucius Verus", edition_citation=article["citeAs"], proposed_by=BY,
                                  at=at)
    report["historiography"] = stored | {"unresolvedHolders": plan.unresolved_holders, "refused": plan.refused}
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
    print(json.dumps(report, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
