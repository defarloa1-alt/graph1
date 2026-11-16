"""Propose when each Polity existed, from its Wikidata record (D-040; README review item 3).

    python -m GraphRevised.slices.polity_spans [--apply]

For every Polity with an accepted Wikidata identity and no live `occurred`
claim, the preserved record's start and end become one proposed `occurred`
claim (registry: "the state existed over the time given"), evidenced by both
statements as observations, attributed to Wikidata (a voice, not our own
statement: D-145) and accepted by rule (proposals/rule_accept.py), not here.

- Start: inception (P571), else start time (P580). End: dissolved, abolished or
  demolished date (P576), else end time (P582).
- Of several values, the best rank wins (preferred over normal; deprecated never).
  A tie between different values is reported and nothing is proposed: choosing
  between them is the curator's call. The values passed over are named in the
  rationale, so a reader sees the alternatives Wikidata gives.
- A Polity with no start or no end is reported, not guessed.

Without --apply it reports and rolls back. Retry-safe: a submitted span is an
already-proposed duplicate.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.proposals.wikidata_proposer import WIKIDATA_WORK

from GraphRevised.adapters.wikidata_statements import display_edtf, statement_observation
from GraphRevised.harvest.apply import TIME_FIELDS
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, TimeQualifier
from GraphRevised.proposals.store import submit
from GraphRevised.proposals.temporal import wikidata_time
from GraphRevised.slices.add_entity import preserved_identity_payload

PROPOSER_ID = "polity-span-proposer-v1"
START, END = ("P571", "P580"), ("P576", "P582")
NAMES = {"P571": "inception", "P580": "start time", "P576": "dissolved", "P582": "end time"}
RANKS = {"preferred": 0, "normal": 1}

POLITIES = """
MATCH (polity:Entity:Polity)-[link:HAS_AUTHORITY_RECORD {role: "entity_identity", status: "accepted"}]->
      (record:AuthorityRecord {system: "Wikidata"})
WHERE NOT polity.status IN ["deprecated", "rejected"]
OPTIONAL MATCH (span:Assertion {predicate: "occurred"})-[:ASSERTION_SUBJECT]->(polity)
WHERE span.status IN ["proposed", "accepted"]
RETURN polity.id AS id, polity.label AS label, record.identifier AS qid, count(span) AS spans
ORDER BY id
"""


class SpanProblem(ValueError):
    """The record gives no single best value for an end of the span."""


def best(claims: dict[str, list[dict]], pids: tuple[str, ...]) -> tuple[dict, list[dict]]:
    """The best-ranked statement of the first property that has one, and the other values given."""
    for pid in pids:
        usable = [c for c in claims.get(pid, []) if c["rank"] in RANKS
                  and c["mainsnak"].get("snaktype") == "value"]
        if not usable:
            continue
        top = min(RANKS[c["rank"]] for c in usable)
        winners = [c for c in usable if RANKS[c["rank"]] == top]
        values = {wikidata_time(c["mainsnak"]["datavalue"]["value"]) for c in winners}
        if len(values) > 1:
            shown = ", ".join(sorted(display_edtf(edtf) for edtf, _ in values))
            raise SpanProblem(f"{NAMES[pid]} ({pid}) has {len(values)} equally ranked values: {shown}")
        others = [c for c in usable if c not in winners]
        return winners[0], others
    raise SpanProblem(f"no {' or '.join(f'{NAMES[p]} ({p})' for p in pids)}")


def _shown(statement: dict) -> str:
    edtf, _ = wikidata_time(statement["mainsnak"]["datavalue"]["value"])
    return display_edtf(edtf)


def propose_span(tx: Any, operations: dict[str, str], registry, row: dict) -> str:
    path, _ = preserved_identity_payload(row["qid"])
    entity = json.loads(path.read_bytes())["entities"][row["qid"]]
    claims = entity.get("claims", {})
    start, start_others = best(claims, START)
    end, end_others = best(claims, END)

    observation_ids, times = [], []
    for statement in (start, end):
        pid = statement["mainsnak"]["property"]
        observation = statement_observation(
            path, statement["id"],
            label=f"Wikidata observation: {row['label']} {NAMES[pid]} {_shown(statement)}",
            short_label=f"Wikidata: {row['label']} {NAMES[pid]} -> {_shown(statement)}")
        run_write(tx, operations, "upsert_observation", observation)
        run_write(tx, operations, "record_statement_time", {"id": observation["id"]} | {k: observation[k] for k in TIME_FIELDS})
        observation_ids.append(observation["id"])
        times.append(wikidata_time(statement["mainsnak"]["datavalue"]["value"]))
    (start_edtf, start_calendar), (end_edtf, end_calendar) = times
    if start_calendar != end_calendar:
        raise SpanProblem(f"start and end are in different calendars ({start_calendar}, {end_calendar})")
    start_edtf, end_edtf = start_edtf.split("/")[0], end_edtf.split("/")[-1]  # a decade or century: its outer years

    start_pid, end_pid = start["mainsnak"]["property"], end["mainsnak"]["property"]
    expression = f"{NAMES[start_pid]} {_shown(start)}; {NAMES[end_pid]} {_shown(end)} (Wikidata)"
    passed_over = [f"{NAMES[c['mainsnak']['property']]} {_shown(c)} ({c['rank']} rank)"
                   for c in start_others + end_others]
    rationale = (f"Wikidata {row['qid']} ({row['label']}) at revision {entity['lastrevid']}: "
                 f"{NAMES[start_pid]} ({start_pid}) {_shown(start)}, {NAMES[end_pid]} ({end_pid}) {_shown(end)}, "
                 f"the best-ranked values.")
    if passed_over:
        rationale += " Also given, at a lower rank: " + "; ".join(passed_over) + "."
    draft = ProposalDraft(
        predicate="occurred", subject_id=row["id"], observation_ids=tuple(observation_ids),
        time=TimeQualifier(source_expression=expression, edtf=f"{start_edtf}/{end_edtf}",
                           calendar=start_calendar, normalization_basis="source"),
        rationale=rationale[:2000], proposed_by=PROPOSER_ID, mode="attributed", attributed_to=WIKIDATA_WORK,
        relevance="When the state existed, as Wikidata records it; other authorities may draw its edges elsewhere.")
    result = submit(tx, draft, registry, operations)
    return f"{result.validation.outcome.value}: {expression}" + (
        f" [{'; '.join(result.validation.reasons)}]" if result.validation.reasons else "")


def propose(tx: Any) -> list[str]:
    operations, registry = load_operations(), load_registry()
    lines = []
    for row in tx.run(POLITIES).data():
        if row["spans"]:
            lines.append(f"{row['label']}: already has {row['spans']} live occurred claim(s); left alone")
            continue
        try:
            lines.append(f"{row['label']}: {propose_span(tx, operations, registry, row)}")
        except SpanProblem as problem:
            lines.append(f"{row['label']}: not proposed: {problem}")
    return lines


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
                lines = propose(tx)
                tx.commit() if args.apply else tx.rollback()
            except BaseException:
                if not tx.closed():
                    tx.rollback()
                raise
    finally:
        driver.close()
    print(("" if args.apply else "(dry run, rolled back)\n") + "\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
