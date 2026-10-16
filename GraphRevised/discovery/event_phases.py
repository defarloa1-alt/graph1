"""The event-phases agent: an event's phases, and each source's depicted events placed in them.

    python -m GraphRevised.discovery.event_phases GraphRevised/inquiries/<inquiry>.json
        [--model claude-sonnet-5-5] [--submit] [--from-plan GraphRevised/plans/<a reviewed dry run>.json]

The curator decides an event's phases, in order, with what each holds
(curation/phases.json; 29 §10 item 2). The agent reads every event the
inquiry's sources depict, as each source labels and words it, and places each
in one phase or in none, with a reason of a few words (one call per source);
then it writes a one-line description of each phase from what was placed in
it (one call). The rest is deterministic:

- each phase becomes a proposed Event of our own, `chr:entity:phase:<event>:<key>`,
  labelled as Chrystallum's;
- `<phase> partOf <event>`, asserted, evidenced by up to four of its depicted
  events' passages, from different Works, each with the words that depicted it;
- `<depicted event> partOf <phase>`, asserted, evidenced by that event's own
  passage and words.

A depicted event from a creative Work is never placed: its passage cannot
support an asserted claim (handoff rule 15), so it stays in its own lane and
is listed in the plan. Everything stored is proposed and visible at once; the
curator approves the phases and the placements. Dry run by default (one
rolled-back transaction); --submit commits. The plan, with every placement,
reason, and refusal, is a workflow file in GraphRevised/plans/.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase
from pydantic import BaseModel

from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.entities import depicted_event_id
from GraphRevised.proposals.passage_reader import anthropic_client, load_inquiries
from GraphRevised.proposals.prompt_version import prompt_version
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.schema import ProposalDraft, Quotation
from GraphRevised.proposals.store import submit

GRAPH_REVISED = Path(__file__).resolve().parents[1]
PHASES_PATH = GRAPH_REVISED / "curation" / "phases.json"
PLANS_DIRECTORY = GRAPH_REVISED / "plans"
DEFAULT_MODEL = "claude-sonnet-5-5"
PROPOSER_ID = "event-phases-agent"
EXEMPLARS = 4
OUR_VOICE = "Chrystallum"

PLACE_PROMPT = """\
You place the events that one historical source depicts into the phases of a larger event, for a \
knowledge graph. You are given the larger event, its phases in order with what each holds, and the \
source's depicted events, each with the source's label and the words that depicted it. For each \
depicted event, give the key of the one phase it belongs to, or null when it fits none: it lies \
outside the larger event and its phases, or it spans phases so that no single one is right. Judge \
by what the depicted event is, as its words show, not by where the source narrates it. Return one \
placement for every depicted event, with its ref exactly as given and a reason of a few words.
"""

DESCRIBE_PROMPT = """\
You write one plain sentence describing each phase of a larger historical event, from the events \
the sources depict in it. Say what the phase holds as the depicted events show it; where the \
sources differ, describe what the phase holds rather than choosing between them. No locators, no \
source names, no quotation marks. Return one description for every phase given, with its key.
"""


class Placement(BaseModel):
    ref: str
    phase: str | None
    why: str


class PlacementOutput(BaseModel):
    placements: list[Placement]


class Description(BaseModel):
    key: str
    description: str


class DescribeOutput(BaseModel):
    descriptions: list[Description]


def load_spine(event_id: str, path: Path = PHASES_PATH) -> dict[str, Any]:
    events = json.loads(path.read_text(encoding="utf-8"))["events"]
    if event_id not in events:
        raise SystemExit(f"no phases decided for {event_id} in {path.name}: the curator decides them first")
    return events[event_id]


def phase_id(event_id: str, key: str) -> str:
    return f"chr:entity:phase:{event_id.split(':', 2)[2]}:{key}"


def depicted_with_passages(tx: Any, work_ids: list[str]) -> list[dict[str, Any]]:
    """Each live depicted event of these Works with the passage and words that first depicted it."""
    prefixes = [depicted_event_id(w, "x")[:-1] for w in work_ids]
    return tx.run(
        """
        MATCH (e:Entity {kind: 'Event'})
        WHERE any(p IN $prefixes WHERE e.id STARTS WITH p) AND e.status <> 'deprecated'
        MATCH (a:Annotation {kind: 'entity-mention'})-[:CONCERNS]->(e)
        MATCH (a)-[l:ANNOTATES]->(o:SourceObservation)-[:IN_WORK]->(w:Entity)
        WITH e, w, o, l ORDER BY o.id
        WITH e, w, collect({id: o.id, quotation: l.quotation})[0] AS first
        RETURN e.id AS id, coalesce(e.shortLabel, e.label) AS label, w.id AS workId, w.label AS work,
               w.form AS form, first.id AS observationId, first.quotation AS quotation
        ORDER BY w.id, first.id, e.id
        """,
        prefixes=prefixes,
    ).data()


def _call(client, model: str, system: str, user: str, output_format) -> tuple[Any, dict]:
    response = client.beta.messages.parse(model=model, max_tokens=16000, system=system,
                                          messages=[{"role": "user", "content": user}], output_format=output_format)
    meta = {"model": response.model, "stopReason": response.stop_reason,
            "inputTokens": response.usage.input_tokens, "outputTokens": response.usage.output_tokens}
    return (None if response.stop_reason == "refusal" else response.parsed_output), meta


def _phase_lines(spine: dict[str, Any]) -> str:
    return "\n".join(f"- {p['key']}: {p['label']}. {p['scope']}" for p in spine["phases"])


def place(client, model: str, event: dict[str, Any], spine: dict[str, Any], work: str,
          events: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[dict]]:
    """One source's events placed in phases: {event id: {phase, why}}; an event the model does not
    return, or returns with an unknown phase, is left unplaced with that reason."""
    refs = {f"e{i + 1}": e for i, e in enumerate(events)}
    user = (f"Larger event: {event['label']} ({event.get('description') or ''})\n\n"
            f"Phases, in order:\n{_phase_lines(spine)}\n\nSource: {work}\n\nDepicted events:\n"
            + "\n".join(f"[{ref}] {e['label']} | words: {e['quotation']}" for ref, e in refs.items()))
    keys = {p["key"] for p in spine["phases"]}
    calls = []
    output = None
    for attempt in (1, 2):  # an empty or unparsed answer is retried once
        output, meta = _call(client, model, PLACE_PROMPT, user, PlacementOutput)
        calls.append(meta | {"attempt": attempt, "placements": len(output.placements) if output else 0})
        if output and output.placements:
            break
    returned = {p.ref.strip().strip("[]").strip(): p for p in (output.placements if output else [])}
    placed = {}
    for ref, e in refs.items():
        p = returned.get(ref)
        if p is None:
            placed[e["id"]] = {"phase": None, "why": "unplaced: no placement returned"}
        elif p.phase is not None and p.phase not in keys:
            placed[e["id"]] = {"phase": None, "why": f"unplaced: unknown phase {p.phase!r}"}
        else:
            placed[e["id"]] = {"phase": p.phase, "why": p.why}
    return placed, calls


def describe(client, model: str, event: dict[str, Any], spine: dict[str, Any],
             members: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, str], dict]:
    user = (f"Larger event: {event['label']}\n\n"
            + "\n\n".join(f"Phase {p['key']}: {p['label']}. {p['scope']}\nDepicted in it:\n"
                          + "\n".join(f"- {m['label']}" for m in members[p['key']])
                          for p in spine["phases"] if members[p["key"]]))
    output, meta = _call(client, model, DESCRIBE_PROMPT, user, DescribeOutput)
    return ({d.key: d.description.strip() for d in output.descriptions} if output else {}), meta


def exemplars(members: list[dict[str, Any]], limit: int = EXEMPLARS) -> list[dict[str, Any]]:
    """The evidence for a phase: the first depicted event of each Work placed in it, the Works with the most
    events placed first, up to the limit, so that the phase rests on several sources where it can."""
    by_work: dict[str, list[dict[str, Any]]] = {}
    for m in members:
        by_work.setdefault(m["workId"], []).append(m)
    ordered = sorted(by_work.values(), key=lambda ms: (-len(ms), ms[0]["workId"]))
    return [ms[0] for ms in ordered[:limit]]


def drafts(event_id: str, spine: dict[str, Any], inquiry_id: str, placed: dict[str, dict[str, Any]],
           events: dict[str, dict[str, Any]], model_id: str) -> tuple[list[tuple[str, ProposalDraft]], dict[str, list]]:
    """The asserted claims: each phase with members partOf the event, and each placed event partOf its phase."""
    members = {p["key"]: [events[i] for i, v in placed.items() if v["phase"] == p["key"]] for p in spine["phases"]}
    out: list[tuple[str, ProposalDraft]] = []

    def draft(subject: str, obj: str, evidence: list[dict[str, Any]], rationale: str, relevance: str) -> ProposalDraft:
        return ProposalDraft(
            predicate="partOf", subject_id=subject, object_id=obj,
            observation_ids=tuple(e["observationId"] for e in evidence),
            quotations=tuple(Quotation(observation_id=e["observationId"], text=e["quotation"]) for e in evidence),
            rationale=rationale, proposed_by=PROPOSER_ID, prompt_version=PROMPT_VERSION, model_id=model_id,
            inquiry_id=inquiry_id, relevance=relevance, mode="asserted",
        )

    for p in spine["phases"]:
        if not members[p["key"]]:
            continue
        shown = exemplars(members[p["key"]])
        works = len({m["workId"] for m in members[p["key"]]})
        out.append((p["key"], draft(
            phase_id(event_id, p["key"]), event_id, shown,
            f"One of the event's phases, decided by {spine['decidedBy']} ({spine['decidedAt']}): {p['scope']} "
            f"{len(members[p['key']])} depicted events from {works} sources were placed in it; the evidence is "
            f"the passages of the first of them in up to {EXEMPLARS} sources.",
            "A phase of the inquiry's event: our reading, which orders the sources' accounts and the account.")))
    for event in sorted(placed):
        phase = placed[event]["phase"]
        if phase is None:
            continue
        out.append((event, draft(
            event, phase_id(event_id, phase), [events[event]],
            f"Placed in this phase by the phase agent: {placed[event]['why']}",
            "Places one source's depicted action in a phase of the inquiry's event.")))
    return out, members


PROMPT_VERSION = prompt_version("event-phases-v1", PLACE_PROMPT + DESCRIBE_PROMPT, place, describe, exemplars, drafts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inquiry", type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--submit", action="store_true", help="commit the proposals (default: dry run)")
    parser.add_argument("--from-plan", type=Path,
                        help="store the placements and descriptions of an earlier plan (a reviewed dry run) "
                             "instead of asking the model again")
    args = parser.parse_args(argv)

    earlier = json.loads(args.from_plan.read_text(encoding="utf-8")) if args.from_plan else None
    operations, registry = load_operations(), load_registry()
    client = None if earlier else anthropic_client()
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            inquiries = session.execute_read(lambda tx: load_inquiries(args.inquiry, tx))
            event_id = inquiries[0].narrative_event_id
            event = session.run("MATCH (e:Entity {id: $id}) RETURN e {.id, .label, .description} AS e",
                                id=event_id).single()["e"]
            spine = load_spine(event_id)
            found = session.execute_read(lambda tx: depicted_with_passages(tx, [i.work_id for i in inquiries]))

            creative = [e for e in found if e["form"] in registry.creative_forms]
            readable = [e for e in found if e["form"] not in registry.creative_forms]
            events = {e["id"]: e for e in readable}
            placed: dict[str, dict[str, Any]] = {}
            calls = []
            if earlier:
                if earlier["event"] != event_id:
                    raise SystemExit(f"{args.from_plan.name} is a plan for {earlier['event']}, not {event_id}")
                placed = {i: {"phase": v["phase"], "why": v["why"]} for i, v in earlier["placements"].items() if i in events}
                calls = [c | {"fromPlan": args.from_plan.name} for c in earlier["calls"]]
                missing = sorted(set(events) - set(placed))
                if missing:
                    print(f"{len(missing)} depicted events are not in the plan and are left unplaced")
            for work_id in ([] if earlier else dict.fromkeys(e["workId"] for e in readable)):
                work_events = [e for e in readable if e["workId"] == work_id]
                result, meta = place(client, args.model, event, spine, work_events[0]["work"], work_events)
                placed |= result
                calls += [m | {"workId": work_id} for m in meta]
                print(f"{work_events[0]['work']}: {sum(1 for e in work_events if result[e['id']]['phase'])} of "
                      f"{len(work_events)} placed")

            model_id = next(c["model"] for c in reversed(calls) if c.get("model"))
            claim_drafts, members = drafts(event_id, spine, inquiries[0].id, placed, events, model_id)
            if earlier:
                descriptions = {p["key"]: p["description"] for p in earlier["phases"] if p.get("description")}
            else:
                descriptions, meta = describe(client, args.model, event, spine, members)
                calls.append(meta | {"call": "describe"})

            tx = session.begin_transaction()
            outcomes = []
            try:
                for p in spine["phases"]:
                    if members[p["key"]]:
                        # A re-run never resets the curator's decision on a phase that already exists.
                        exists = tx.run("MATCH (e:Entity {id: $id}) RETURN e.id",
                                        id=phase_id(event_id, p["key"])).single() is not None
                        run_write(tx, operations, "upsert_entity", {
                            "id": phase_id(event_id, p["key"]), "kind": "Event",
                            "label": f"{p['label']} ({OUR_VOICE})", "shortLabel": p["label"],
                            "description": descriptions.get(p["key"]), "status": None if exists else "proposed",
                        })
                for key, draft in claim_drafts:
                    submission = submit(tx, draft, registry, operations)
                    outcomes.append({"for": key, "subject": draft.subject_id, "object": draft.object_id,
                                     "outcome": submission.validation.outcome.value, "stored": submission.stored,
                                     "reasons": list(submission.validation.reasons)})
                if args.submit:
                    tx.commit()
                else:
                    tx.rollback()
            except BaseException:
                tx.rollback()
                raise
    finally:
        driver.close()

    usage = {k: sum(c.get(k, 0) for c in calls) for k in ("inputTokens", "outputTokens")}
    plan = {
        "inquiry": inquiries[0].id, "inquiryVersion": inquiries[0].version, "event": event_id,
        "createdAt": datetime.now(timezone.utc).isoformat(), "promptVersion": PROMPT_VERSION, "model": args.model,
        "submitted": args.submit, "fromPlan": args.from_plan.name if earlier else None, "usage": usage, "calls": calls,
        "phases": [{"key": p["key"], "id": phase_id(event_id, p["key"]), "label": p["label"],
                    "description": descriptions.get(p["key"]), "members": [m["id"] for m in members[p["key"]]],
                    "evidence": [m["id"] for m in exemplars(members[p["key"]])]} for p in spine["phases"]],
        "placements": {i: placed[i] | {"work": events[i]["work"], "label": events[i]["label"]} for i in sorted(placed)},
        "notPlacedCreative": [{"id": e["id"], "label": e["label"], "work": e["work"], "form": e["form"]} for e in creative],
        "outcomes": outcomes,
    }
    PLANS_DIRECTORY.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = PLANS_DIRECTORY / f"{inquiries[0].id.rsplit(':', 1)[-1]}-phases-{stamp}.json"
    path.write_bytes((json.dumps(plan, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    counts: dict[str, int] = {}
    for o in outcomes:
        counts[o["outcome"]] = counts.get(o["outcome"], 0) + 1
    print(f"\nphases: " + ", ".join(f"{p['key']} {len(members[p['key']])}" for p in spine["phases"]))
    print(f"unplaced: {sum(1 for v in placed.values() if v['phase'] is None)}; creative, not placed: {len(creative)}")
    print(f"drafts: {counts} ({'committed' if args.submit else 'dry run, rolled back'}); "
          f"{usage['inputTokens']} in, {usage['outputTokens']} out -> {path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
