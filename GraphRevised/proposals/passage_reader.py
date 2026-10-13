"""LLM passage reader: proposes claims from located passages for one inquiry.

    python -m GraphRevised.proposals.passage_reader GraphRevised/inquiries/actium-plutarch-antony.json
        [--sections 65.1,65.2] [--submit] [--model claude-opus-5-5]

An inquiry file binds a run to a Subject. The reader may name only entities in
the inquiry's scope (the Subject's focus, entities linked to the focus by
assertions that are not rejected or superseded, and the inquiry's declared
candidates), and every
claim must state how it bears on the Subject. Subject- and source-specific
guidance lives in the inquiry, not in the prompt.

Claims are drafted as what the source says: each is attributed to the
inquiry's source Work ("according to"), and only the curator promotes one to
an asserted claim. A claim may carry a role, a time, and a context event, each
only as the passage states it.

The model only drafts. Drafts outside the scope are refused before
validation; the rest go through the deterministic validator. With --submit,
valid drafts are stored as submitted Proposals recording the inquiry. A
section's passage observation is persisted only when one of its drafts is
stored. Every run writes a JSONL log to GraphRevised/runs/.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic
from dotenv import dotenv_values
from neo4j import GraphDatabase
from pydantic import BaseModel, ValidationError

from GraphRevised.adapters.wikidata_context import entity_context
from GraphRevised.adapters.sources import PassageSource, open_source
from GraphRevised.capture.core import NOTE_TYPES, annotation_id
from GraphRevised.operations import load_operations, run_write

from .prompt_version import prompt_version
from .registry import PredicateRegistry, load_registry
from .schema import DRAFT_SCHEMA_VERSION, ProposalDraft, QualifierQuotation, Quotation, TimeQualifier
from .entities import propose_entity
from .validator import normalize
from .store import Neo4jReader, submit
from .validator import validate

PROPOSER_ID = "passage-reader"
DEFAULT_MODEL = "claude-sonnet-5-5"
GRAPH_REVISED = Path(__file__).resolve().parents[1]
RUNS_DIRECTORY = GRAPH_REVISED / "runs"

SYSTEM_PROMPT = """\
You read one passage of a historical source and draft claims for a historical knowledge graph, \
on behalf of one inquiry into one subject. You do not decide what is true: a deterministic \
validator checks every draft and a human curator accepts or rejects it. Drafting nothing is a \
correct result for many passages.

Rules:
1. Draft a claim only when the target passage itself states it or directly entails it. The \
surrounding sections are context for understanding the passage; they are not evidence. Use \
outside knowledge only to identify whom or what a name refers to, never to add facts.
2. Draft only claims that bear on the inquiry's subject. In relevance, say in one sentence how \
the claim bears on the subject's focus. A true claim that does not bear on the subject is out \
of scope; leave it out.
3. Use only the predicates provided, respecting their subject and object kinds. If a relationship \
in the passage fits none of them, leave it out rather than stretching a predicate.
4. subject_id and object_id must be copied from the in-scope entity list. Never invent an ID. \
Report any person, group, place, or event the passage mentions that is not in the list under \
unresolved_mentions, with the name as it appears in the passage. A name you identify with a \
listed entity is resolved and is not reported.
5. quotation must be copied exactly, character for character, from the target passage: one \
contiguous span, at least 15 characters, the shortest span that supports the claim while \
still containing the words that name or refer to its subject and object when the sentence has \
them, so a reader of the quotation alone can see who is meant. Do not paraphrase, abridge, use \
ellipses, or quote the surrounding sections.
6. In-scope entities may list aliases and dates. Aliases help identification but can be shared \
by different people, so decide from the passage and its context, not from a matching alias \
alone. Explain in the rationale how you identified each name. Use ambiguities only when an \
identification or the claim itself remains genuinely uncertain; such claims are held for a human.
7. Follow the inquiry guidance. It is specific to this subject and source and takes precedence \
over your general reading where they differ.
8. Every claim records what this source says, not what you believe happened. Draft what the \
passage depicts even where other sources differ; a curator decides what is established.
9. Qualifiers are optional and come only from the target passage. Give a role (role_id, from the \
in-scope entities) only when the passage names the office or post, with role_quotation copied \
exactly. Give a time only when the passage states one: time_source_expression is the passage's \
own words and time_quotation the exact span containing them. Fill time_edtf only when the passage \
itself states the year (with or without month and day); never from editorial notes, the surrounding \
narrative, or outside knowledge, and not for a day and month given without a year. time_edtf numbers \
years astronomically: 1 BCE is 0000, 2 BCE is -0001, and 100 BCE is -0099; years CE are unchanged. A \
predicate's list entry says which qualifiers it takes; a claim whose qualifier the passage does not \
give is still drafted without it and stored as undated. A vague time phrase in the passage's own \
words is a valid time expression; it is never turned into a date.
10. For predicates that take a context, set context_id to the inquiry's narrative event when the \
claim happens within it. If the passage names the event, also copy that span as context_quotation.
11. A predicate marked "no object" takes no object_id: leave it null.
12. Passages of note. When the passage is worth reading for in-scope entities but states nothing \
you can draft as a claim, add a note: its type (characterization, anecdote, omen, motive, speech, \
atmosphere, detail, or interpretation for an author's reading of what events meant), one line on \
why it is worth reading, the exact quotation (rules as in 5), and the in-scope entities it \
concerns. A note asserts nothing. Do not add a note for what a claim already captures, and add \
none to passages with nothing notable.
13. Periods. When the task packet allows Period proposals and the passage names a historical period, \
era, or regime as a span of time (an age the author treats as one), list it under periods: the \
name exactly as the author uses it, the exact quotation naming it, and its bounds only if the \
passage states them (time_expression verbatim inside time_quotation; time_edtf only when the years \
are stated). Use one name per period; do not list a period that only appears in an in-scope \
entity list, and do not infer bounds from outside knowledge.
14. Opposition. Draft opposed only when the passage states that two people or groups were \
opponents: rivals or enemies, in politics or at war. Give the time the passage states, and the war \
or battle as context when the passage names one. Feelings alone (hatred, fear, contempt, jealousy) \
are not opposition; record them as a passage of note (motive or characterization).
"""


class ReaderClaim(BaseModel):
    predicate: str
    subject_id: str
    object_id: str | None
    quotation: str
    rationale: str
    relevance: str
    ambiguities: list[str]
    role_id: str | None
    role_quotation: str | None
    time_source_expression: str | None
    time_quotation: str | None
    time_edtf: str | None
    context_id: str | None
    context_quotation: str | None


class UnresolvedMention(BaseModel):
    name: str
    quotation: str
    note: str


class ReaderNote(BaseModel):
    note_type: str
    note: str
    quotation: str
    concerns: list[str]


class ReaderPeriod(BaseModel):
    name: str
    quotation: str
    time_expression: str | None
    time_quotation: str | None
    time_edtf: str | None


class ReaderOutput(BaseModel):
    claims: list[ReaderClaim]
    unresolved_mentions: list[UnresolvedMention]
    notes: list[ReaderNote]
    periods: list[ReaderPeriod]


@dataclass(frozen=True)
class Inquiry:
    id: str
    version: int
    label: str
    subject: dict[str, Any]
    focus: list[dict[str, Any]]
    scope: list[dict[str, Any]]
    guidance: list[str]
    source: dict[str, Any]  # adapter configuration: type, files, chapters (adapters/sources.py)
    work_id: str
    narrative_event_id: str | None
    calendar: str | None = None  # calendar of normalized dates in this source's world (julian, gregorian)
    context_before: int = 2  # sections shown before the target passage, as context only
    context_after: int = 1
    note_visibility: str = "private"  # passages of note: private, team, or public
    proposable_kinds: tuple[str, ...] = ()  # kinds the reader may propose as entities, such as Period


def load_inquiry(path: Path, tx: Any) -> Inquiry:
    """Read the inquiry file and resolve its scope against the graph."""
    data = json.loads(path.read_text(encoding="utf-8"))
    record = tx.run(
        """
        MATCH (subject:Subject {id: $subjectId})-[:HAS_SUBJECT_FOCUS]->(focus:Entity)
        OPTIONAL MATCH (focus)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(assertion:Assertion)
                       -[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(linked:Entity)
        WHERE NOT assertion.status IN ["rejected", "superseded"]
        WITH subject, collect(DISTINCT focus) AS focus, collect(DISTINCT linked) AS linked
        OPTIONAL MATCH (declared:Entity) WHERE declared.id IN $declared
        WITH subject, focus, linked, collect(DISTINCT declared) AS declared
        RETURN subject {.id, .label} AS subject,
               [entity IN focus | entity {.id, .label, .kind, .description}] AS focus,
               [entity IN focus + linked + declared | entity.id] AS scopeIds
        """,
        subjectId=data["subjectId"],
        declared=data["candidateEntityIds"],
    ).single()
    if record is None:
        raise ValueError(f"{data['subjectId']} is not a Subject with a focus Entity")
    missing = set(data["candidateEntityIds"]) - set(record["scopeIds"])
    if missing:
        raise ValueError(f"declared candidates are not Entities: {sorted(missing)}")
    work_id = data["source"].get("workId")
    if not work_id or tx.run("MATCH (w:Entity {id: $id, kind: 'Work'}) RETURN count(w) AS n", id=work_id).single()["n"] != 1:
        raise ValueError(f"the inquiry's source needs a workId naming a Work Entity, not {work_id!r}")
    narrative_event_id = data.get("narrativeEventId")
    if narrative_event_id and tx.run(
        "MATCH (e:Entity {id: $id, kind: 'Event'}) RETURN count(e) AS n", id=narrative_event_id
    ).single()["n"] != 1:
        raise ValueError(f"narrativeEventId {narrative_event_id!r} is not an Event Entity")
    scope = tx.run(
        """
        MATCH (entity:Entity) WHERE entity.id IN $ids
        OPTIONAL MATCH (entity)-[link:HAS_AUTHORITY_RECORD]->(record:AuthorityRecord {system: "Wikidata"})
        WHERE link.role = "entity_identity" AND link.status = "accepted"
        WITH entity, head(collect(record)) AS record
        RETURN entity {.id, .label, .kind, .description,
                       qid: record.identifier, payloadUri: record.rawPayloadUri} AS entity
        ORDER BY entity.id
        """,
        ids=sorted(set(record["scopeIds"])),
    ).value("entity")
    scope = [{**entity, **entity_context(entity["payloadUri"], entity["qid"])} for entity in scope]
    return Inquiry(
        id=data["id"],
        version=data["version"],
        label=data["label"],
        subject=record["subject"],
        focus=record["focus"],
        scope=scope,
        guidance=data["guidance"],
        source=data["source"],
        work_id=work_id,
        narrative_event_id=narrative_event_id,
        calendar=data.get("calendar"),
        context_before=data["source"].get("contextWindow", {}).get("before", 2),
        context_after=data["source"].get("contextWindow", {}).get("after", 1),
        note_visibility=data.get("noteVisibility", "private"),
        proposable_kinds=tuple(data.get("proposableKinds", [])),
    )


def anthropic_client() -> anthropic.Anthropic:
    """Use ANTHROPIC_API_KEY from the environment, else only that key from .env.

    The rest of .env is deliberately not loaded: it holds legacy Neo4j
    settings that must not redirect the clean-start database connection.
    """
    key = os.environ.get("ANTHROPIC_API_KEY") or dotenv_values(GRAPH_REVISED.parent / ".env").get("ANTHROPIC_API_KEY")
    return anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic()


def predicate_guide(registry: PredicateRegistry) -> str:
    def qualifiers(d) -> str:
        q = d.qualifiers
        parts = [f"{name}: {value}" for name, value in (("context", q.context), ("role", q.role)) if value != "none"]
        if q.time != "none":
            parts.append("time: required with a role" if q.time == "withRole" else f"time: {q.time}")
        return f" [{', '.join(parts)}]" if parts else ""

    return "\n".join(
        f"- {d.id} ({d.display}): {'/'.join(sorted(d.subject_kinds))} -> "
        + ("no object" if d.unary else '/'.join(sorted(d.object_kinds)))
        + (" [symmetric]" if d.symmetric else "")
        + qualifiers(d)
        + (f" -- {d.definition}" if d.definition else "")
        for d in registry.predicates.values()
        if "attributed" in d.modes
    )


def read_passage(
    client: anthropic.Anthropic,
    model: str,
    inquiry: Inquiry,
    edition: PassageSource,
    ref: str,
    passage: dict[str, Any],
    context: list[tuple[str, str]],
    registry: PredicateRegistry,
) -> tuple[ReaderOutput | None, dict[str, Any]]:
    def entity_line(entity: dict[str, Any]) -> str:
        line = f"- {entity['id']} | {entity['label']} | {entity['kind']} | {entity.get('description') or ''}"
        if entity.get("aliases"):
            line += f" | aliases: {'; '.join(entity['aliases'])}"
        if entity.get("dates"):
            line += " | " + ", ".join(f"{name} {year}" for name, year in entity["dates"].items())
        return line

    # Everything that is the same for every passage of a run comes first and is
    # cached; only the surrounding sections and the target passage vary.
    packet = (
        f"Inquiry: {inquiry.label}\n"
        f"Subject: {inquiry.subject['label']}\n"
        f"Subject focus:\n" + "\n".join(entity_line(e) for e in inquiry.focus) + "\n\n"
        f"Inquiry guidance:\n" + "\n".join(f"- {line}" for line in inquiry.guidance) + "\n\n"
        f"Source: {edition.author}, {edition.title}, trans. {edition.translator} ({edition.citation}).\n"
        f"Narrative event: {inquiry.narrative_event_id or 'none declared'}\n"
        f"Entity kinds you may propose: {', '.join(inquiry.proposable_kinds) or 'none'}\n\n"
        f"Predicates:\n{predicate_guide(registry)}\n\n"
        f"In-scope entities (id | label | kind | description):\n"
        + "\n".join(entity_line(e) for e in inquiry.scope)
    )
    user = (
        f"Surrounding sections (context only, not evidence):\n"
        + "\n\n".join(f"[{r}] {text}" for r, text in context) + "\n\n"
        f"Target passage [{ref}]:\n{passage['passageText']}"
    )
    response = client.beta.messages.parse(
        model=model,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        extra_body={"fallbacks": "default"},
        system=[
            {"type": "text", "text": SYSTEM_PROMPT},
            {"type": "text", "text": packet, "cache_control": {"type": "ephemeral"}},
        ],
        messages=[{"role": "user", "content": user}],
        output_format=ReaderOutput,
    )
    meta = {
        "model": response.model,
        "stopReason": response.stop_reason,
        "inputTokens": response.usage.input_tokens,
        "cacheReadTokens": response.usage.cache_read_input_tokens or 0,
        "cacheWriteTokens": response.usage.cache_creation_input_tokens or 0,
        "outputTokens": response.usage.output_tokens,
        "requestId": response._request_id,
    }
    if response.stop_reason == "refusal":
        return None, meta
    return response.parsed_output, meta


PROMPT_VERSION = prompt_version("passage-reader-v12", SYSTEM_PROMPT, predicate_guide, read_passage)


def to_drafts(
    output: ReaderOutput, observation_id: str, model_id: str, inquiry: Inquiry
) -> tuple[list[ProposalDraft], list[dict]]:
    drafts, malformed = [], []
    for claim in output.claims:
        try:
            drafts.append(_draft(claim, observation_id, model_id, inquiry))
        except (ValidationError, ValueError) as error:
            malformed.append({"claim": claim.model_dump(), "error": str(error)})
    return drafts, malformed


def to_periods(output: ReaderOutput, passage: dict[str, Any], inquiry: Inquiry) -> tuple[list[dict], list[dict]]:
    """Periods the passage names, checked for verbatim quotations; refused ones with the reason."""
    if "Period" not in inquiry.proposable_kinds:
        return [], [{"period": p.model_dump(), "reason": "the inquiry does not allow Period proposals"}
                    for p in output.periods]
    periods, refused = [], []
    text = normalize(passage["passageText"])
    for period in output.periods:
        reason = None
        if not period.name.strip():
            reason = "an empty name"
        elif normalize(period.quotation) not in text or len(normalize(period.quotation)) < 15:
            reason = "quotation does not appear verbatim in the passage"
        elif period.time_expression and (not period.time_quotation
                                         or normalize(period.time_quotation) not in text
                                         or normalize(period.time_expression) not in normalize(period.time_quotation)):
            reason = "the time expression must appear in a verbatim time quotation"
        elif period.time_edtf and not inquiry.calendar:
            reason = "a normalized date needs the inquiry's calendar"
        if reason:
            refused.append({"period": period.model_dump(), "reason": reason})
        else:
            periods.append(period.model_dump())
    return periods, refused


def period_draft(period: dict, entity_id: str, observation_id: str, model_id: str, inquiry: Inquiry) -> ProposalDraft:
    """The source's bounds for a period, as an attributed unary `occurred` claim."""
    return ProposalDraft(
        predicate="occurred", subject_id=entity_id, object_id=None,
        observation_ids=(observation_id,),
        quotations=(Quotation(observation_id=observation_id, text=period["quotation"]),),
        qualifier_quotations=(QualifierQuotation(observation_id=observation_id, supports="time",
                                                 text=period["time_quotation"]),),
        time=TimeQualifier(source_expression=period["time_expression"], edtf=period["time_edtf"],
                           calendar=inquiry.calendar if period["time_edtf"] else None,
                           normalization_basis="source" if period["time_edtf"] else None),
        rationale=f"The passage gives the bounds of the period it names: {period['time_expression']}.",
        proposed_by=PROPOSER_ID, prompt_version=PROMPT_VERSION, model_id=model_id,
        inquiry_id=inquiry.id, relevance="The source's own periodization of the time of the subject.",
        mode="attributed", attributed_to=inquiry.work_id,
    )


def _related_lines(result) -> list[str]:
    return [f"{item['relation']}: {item['id']} ({item['status']}, {item['mode']})" for item in result.related]


def to_notes(output: ReaderOutput, passage: dict[str, Any], scope_ids: set[str]) -> tuple[list[dict], list[dict]]:
    """Passages of note that can be stored, and those refused with the reason."""
    notes, refused = [], []
    for note in output.notes:
        concerns = sorted(set(note.concerns))
        reason = None
        if note.note_type not in NOTE_TYPES:
            reason = f"unknown note type {note.note_type!r}"
        elif not note.note.strip():
            reason = "an empty note"
        elif not concerns:
            reason = "a note concerns at least one entity"
        elif set(concerns) - scope_ids:
            reason = f"not in inquiry scope: {sorted(set(concerns) - scope_ids)}"
        elif len(normalize(note.quotation)) < 15 or normalize(note.quotation) not in normalize(passage["passageText"]):
            reason = "quotation does not appear verbatim in the passage"
        if reason:
            refused.append({"note": note.model_dump(), "reason": reason})
        else:
            notes.append({"noteType": note.note_type, "note": note.note.strip(), "quotation": note.quotation,
                          "concerns": concerns})
    return notes, refused


def _draft(claim: ReaderClaim, observation_id: str, model_id: str, inquiry: Inquiry) -> ProposalDraft:
    """An attributed draft with the qualifiers the reader found, each shown by its own span."""
    spans: list[QualifierQuotation] = []
    if claim.role_id:
        if not claim.role_quotation:
            raise ValueError("a role needs role_quotation")
        spans.append(QualifierQuotation(observation_id=observation_id, supports="role", text=claim.role_quotation))
    time = None
    if claim.time_source_expression:
        if not claim.time_quotation:
            raise ValueError("a time needs time_quotation")
        spans.append(QualifierQuotation(observation_id=observation_id, supports="time", text=claim.time_quotation))
        if claim.time_edtf and not inquiry.calendar:
            raise ValueError("a normalized date needs the inquiry's calendar")
        time = TimeQualifier(
            source_expression=claim.time_source_expression,
            edtf=claim.time_edtf,
            calendar=inquiry.calendar if claim.time_edtf else None,
            normalization_basis="source" if claim.time_edtf else None,
        )
    context_basis = None
    if claim.context_id:
        if claim.context_quotation:
            context_basis = "quotation"
            spans.append(QualifierQuotation(observation_id=observation_id, supports="context", text=claim.context_quotation))
        elif claim.context_id == inquiry.narrative_event_id:
            context_basis = "inquiry"
        else:
            raise ValueError("a context other than the narrative event needs context_quotation")
    return ProposalDraft(
        predicate=claim.predicate,
        subject_id=claim.subject_id,
        object_id=claim.object_id,
        observation_ids=(observation_id,),
        quotations=(Quotation(observation_id=observation_id, text=claim.quotation),),
        qualifier_quotations=tuple(spans),
        rationale=claim.rationale,
        proposed_by=PROPOSER_ID,
        prompt_version=PROMPT_VERSION,
        model_id=model_id,
        ambiguities=tuple(claim.ambiguities),
        inquiry_id=inquiry.id,
        relevance=claim.relevance,
        mode="attributed",
        attributed_to=inquiry.work_id,
        role_id=claim.role_id,
        time=time,
        context_id=claim.context_id,
        context_basis=context_basis,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inquiry", type=Path, help="inquiry JSON file")
    parser.add_argument("--sections", help="comma-separated refs such as 65.1,65.2 (overrides the inquiry's chapters)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--submit", action="store_true", help="store valid drafts as submitted Proposals")
    parser.add_argument("--outputs", default="claims,notes,periods",
                        help="which outputs to store with --submit (claims, notes, periods)")
    args = parser.parse_args(argv)

    operations, registry, client = load_operations(), load_registry(), anthropic_client()
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    RUNS_DIRECTORY.mkdir(exist_ok=True)
    run_path = RUNS_DIRECTORY / f"passage-reader-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.jsonl"
    authorities = json.loads((GRAPH_REVISED / "curation" / "authorities.json").read_text(encoding="utf-8"))
    periodo = None  # loaded when a new period is first surveyed
    totals: dict[str, int] = {"stored": 0, "malformed": 0, "inputTokens": 0, "cacheReadTokens": 0,
                              "cacheWriteTokens": 0, "outputTokens": 0}

    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session, \
                run_path.open("w", encoding="utf-8") as log:
            inquiry = session.execute_read(lambda tx: load_inquiry(args.inquiry, tx))
            scope_ids = {entity["id"] for entity in inquiry.scope}
            edition = open_source(inquiry.source, GRAPH_REVISED)
            refs = args.sections.split(",") if args.sections else edition.refs(inquiry.source.get("chapters"))
            all_refs = edition.refs(None)
            print(f"inquiry: {inquiry.id} v{inquiry.version} -> {inquiry.subject['label']}")
            print(f"scope: {', '.join(e['label'] for e in inquiry.scope)}\n")
            log.write(json.dumps({
                "inquiry": inquiry.id, "inquiryVersion": inquiry.version, "subject": inquiry.subject["id"],
                "scope": sorted(scope_ids), "promptVersion": PROMPT_VERSION, "model": args.model,
                "predicateRegistryVersion": registry.version, "draftSchemaVersion": DRAFT_SCHEMA_VERSION,
                "workId": inquiry.work_id, "narrativeEventId": inquiry.narrative_event_id,
            }) + "\n")

            for ref in refs:
                passage = edition.observation(ref)
                index = all_refs.index(ref)
                context = [
                    (r, edition.observation(r)["passageText"])
                    for r in all_refs[max(0, index - inquiry.context_before):index]
                    + all_refs[index + 1:index + 1 + inquiry.context_after]
                ]
                output, meta = read_passage(client, args.model, inquiry, edition, ref, passage, context, registry)
                totals["inputTokens"] += meta["inputTokens"]
                totals["cacheReadTokens"] += meta["cacheReadTokens"]
                totals["cacheWriteTokens"] += meta["cacheWriteTokens"]
                totals["outputTokens"] += meta["outputTokens"]
                record: dict[str, Any] = {"ref": ref, "observationId": passage["id"], **meta, "promptVersion": PROMPT_VERSION}
                if output is None:
                    record["error"] = "refusal or no parsed output"
                    log.write(json.dumps(record) + "\n")
                    print(f"{ref}: no output ({meta['stopReason']})")
                    continue
                drafts, malformed = to_drafts(output, passage["id"], meta["model"], inquiry)
                totals["malformed"] += len(malformed)
                notes, refused_notes = to_notes(output, passage, scope_ids)
                stored_notes: list[str] = []
                periods, refused_periods = to_periods(output, passage, inquiry)
                period_results: list[dict] = []
                storing = set(args.outputs.split(","))
                if "claims" not in storing:
                    drafts = []

                # The observation is written first so drafts can be validated
                # against it; the transaction commits only if a draft was stored.
                results: list[tuple[ProposalDraft, str, list[str], str | None, bool]] = []
                tx = session.begin_transaction()
                try:
                    run_write(tx, operations, "upsert_passage_observation", passage)
                    run_write(tx, operations, "link_observation_work", {
                        "observationId": passage["id"], "workId": inquiry.work_id,
                    })
                    for draft in drafts:
                        named = {draft.subject_id, draft.object_id, draft.role_id, draft.context_id} - {None}
                        outside = sorted(named - scope_ids)
                        if outside:
                            results.append((draft, "out_of_scope", [f"not in inquiry scope: {outside}"], None, False))
                        elif args.submit:
                            submission = submit(tx, draft, registry, operations)
                            v = submission.validation
                            results.append((draft, v.outcome.value, list(v.reasons) + list(v.notes) + _related_lines(v),
                                            v.proposal_id, submission.stored))
                        else:
                            v = validate(draft, Neo4jReader(tx), registry)
                            results.append((draft, v.outcome.value, list(v.reasons) + list(v.notes) + _related_lines(v),
                                            v.proposal_id, False))
                    if args.submit and "periods" in storing:
                        for period in periods:
                            proposed = propose_entity(tx, operations, kind="Period", label=period["name"],
                                                      proposed_by=PROPOSER_ID, observation_id=passage["id"],
                                                      quotation=period["quotation"])
                            entry = {"name": period["name"], "entityId": proposed["id"], "created": proposed["created"],
                                     "candidates": [c["id"] for c in proposed["candidates"]], "claim": None}
                            if period["time_expression"]:
                                submission = submit(tx, period_draft(period, proposed["id"], passage["id"], meta["model"],
                                                                     inquiry), registry, operations)
                                entry["claim"] = {"outcome": submission.validation.outcome.value,
                                                  "reasons": list(submission.validation.reasons),
                                                  "stored": submission.stored}
                            if proposed["created"] and authorities["kinds"].get("Period", {}).get("surveyOnPropose"):
                                # Published periodizations of the new period, found without
                                # the curator: PeriodO definitions become attributed claims.
                                from GraphRevised.discovery.period_survey import periodo_dataset, survey_period

                                periodo = periodo if periodo is not None else periodo_dataset(authorities)
                                surveyed = survey_period(tx, operations, registry, periodo, authorities,
                                                         proposed["id"], store=True)
                                entry["survey"] = [{"definition": s["definition"], "work": s["work"],
                                                    "outcome": (s["claim"] or {}).get("outcome")}
                                                   for s in surveyed["stored"]]
                            period_results.append(entry)
                    if args.submit and "notes" in storing:
                        for note in notes:
                            note_id = annotation_id(PROPOSER_ID, passage["id"], note["note"], note["concerns"])
                            run_write(tx, operations, "upsert_annotation", {
                                "id": note_id, "label": note["note"][:120], "kind": "passage-of-note",
                                "noteType": note["noteType"], "note": note["note"], "author": PROPOSER_ID,
                                "visibility": inquiry.note_visibility,
                                "createdAt": datetime.now(timezone.utc).isoformat(),
                                "observationId": passage["id"], "quotation": note["quotation"],
                                "concerns": note["concerns"],
                            })
                            stored_notes.append(note_id)
                    if any(stored for *_, stored in results) or stored_notes or period_results:
                        tx.commit()
                    else:
                        tx.rollback()
                except BaseException:
                    tx.rollback()
                    raise

                record["drafts"] = [
                    {
                        "predicate": d.predicate, "subject": d.subject_id, "object": d.object_id,
                        "mode": d.mode, "attributedTo": d.attributed_to, "role": d.role_id,
                        "time": d.time.model_dump() if d.time else None, "context": d.context_id,
                        "contextBasis": d.context_basis,
                        "qualifierQuotations": [q.model_dump() for q in d.qualifier_quotations],
                        "quotation": d.quotations[0].text, "rationale": d.rationale, "relevance": d.relevance,
                        "ambiguities": list(d.ambiguities),
                        "outcome": outcome, "reasons": reasons, "proposalId": proposal_id, "stored": stored,
                    }
                    for d, outcome, reasons, proposal_id, stored in results
                ]
                record["malformed"] = malformed
                record["notes"] = notes
                record["refusedNotes"] = refused_notes
                record["storedNotes"] = stored_notes
                record["periods"] = period_results or periods
                record["refusedPeriods"] = refused_periods
                record["unresolvedMentions"] = [m.model_dump() for m in output.unresolved_mentions]
                log.write(json.dumps(record, ensure_ascii=False) + "\n")
                for d, outcome, reasons, _, stored in results:
                    totals[outcome] = totals.get(outcome, 0) + 1
                    totals["stored"] += stored
                    print(f"{ref}: {outcome:<13} {d.subject_id} {d.predicate} {d.object_id}"
                          + (" [stored]" if stored else "") + (f" -- {reasons[0]}" if reasons else ""))
                for note in notes:
                    print(f"{ref}: note ({note['noteType']}) {note['note'][:90]}")
                for period in period_results or periods:
                    print(f"{ref}: period {period['name']}" + (f" -> {period['entityId']}" if "entityId" in period else "")
                          + (f" [bounds: {period['claim']['outcome']}]" if period.get("claim") else "")
                          + (f" [PeriodO: {len(period['survey'])} definition(s)]" if period.get("survey") else ""))
                totals["periods"] = totals.get("periods", 0) + len(period_results)
                totals["notes"] = totals.get("notes", 0) + len(stored_notes)
                totals["refusedNotes"] = totals.get("refusedNotes", 0) + len(refused_notes)
                names = ", ".join(m.name for m in output.unresolved_mentions)
                print(f"{ref}: {len(drafts)} draft(s), {len(notes)} note(s); unresolved: {names or '-'}")
    finally:
        driver.close()

    print(f"\nlog: {run_path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    print(json.dumps(totals))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
