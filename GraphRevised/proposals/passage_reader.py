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
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import replace
from typing import Annotated, Any

import anthropic
from dotenv import dotenv_values
from neo4j import GraphDatabase
from pydantic import BaseModel, BeforeValidator, Field, ValidationError

from GraphRevised.adapters.wikidata_context import entity_context
from GraphRevised.adapters.sources import PassageSource, open_source
from GraphRevised.capture.core import NOTE_TYPES, annotation_id, annotation_label
from GraphRevised.operations import load_operations, run_write

from .prompt_version import prompt_version
from .reading_rules import BRIEFS_DIRECTORY, ReadingRules, brief_guidance, load_brief, load_reading_rules
from .registry import PredicateRegistry, load_registry
from .schema import DRAFT_SCHEMA_VERSION, DURATION_PATTERN, ProposalDraft, QualifierQuotation, Quotation, TimeQualifier
from .entities import depicted_event_id, depicted_events, propose_depicted_event, propose_entity
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
11. A predicate marked "no object" takes no object_id: leave it empty. Give an empty string for any \
text field that does not apply.
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
15. Depicted events. When the task packet allows Event proposals, list under depicted_events each \
distinct action or occurrence the target passage narrates as part of the narrative event or around \
it: a manoeuvre, an order carried out, a flight, a pursuit, a decision taken, a surrender. They are \
this source's depiction, never merged with another source's. For each: key, a short id unique in \
your output (e1, e2); label, a plain name of at most six words saying who did what, without the \
source's name (for example "the admiral's wing turns back"), or instead existing_id when the passage continues an \
event already listed as depicted from this source; quotation, the span narrating it (rules as in \
5); within_narrative_event, true when it happens during the narrative event, false when before or \
after it; participants, the in-scope people, groups, or forces that carry it out or take part, each \
with a quotation of at least 15 characters naming or referring to them; place_id and \
place_quotation only for an in-scope place the passage gives as where it happened; time_expression \
and time_quotation for the passage's own time marker (an hour, a day, a season, or a point such as \
dawn or nightfall; words of manner such as "suddenly" are not times), and relative_offset (an ISO 8601 duration such \
as PT6H or P4D) only when the marker counts from the start of the narrative event. links relate it \
to another event, named by key, by an id from the already-depicted list, or by the narrative \
event's id: triggered_by (the source presents it as set off by the other), resulted_in (the other is \
its stated outcome), after (the source says it came after the other). Each link quotes the words \
that show it, at least 15 characters. The order in which the source tells events is not a link. \
Depicted events replace separate claims about the same action: do not also draft participatedIn, \
partOf, or occurredAt claims for them.
"""


# Text the model leaves empty when it does not apply. The output schema says only "string":
# nullable fields would enlarge the output grammar past the API's limit once depicted events
# are added. Python callers may still pass None; empty text is read as absent (_absent).
Text = Annotated[str, BeforeValidator(lambda value: "" if value is None else value)]


def _absent(model: BaseModel, fields: tuple[str, ...]) -> BaseModel:
    """The model with empty optional text read as absent (None)."""
    return model.model_copy(update={name: getattr(model, name) or None for name in fields})


class ReaderClaim(BaseModel):
    predicate: str
    subject_id: str
    object_id: Text
    quotation: str
    rationale: str
    relevance: str
    ambiguities: list[str]
    role_id: Text
    role_quotation: Text
    time_source_expression: Text
    time_quotation: Text
    time_edtf: Text
    context_id: Text
    context_quotation: Text


CLAIM_OPTIONAL = ("object_id", "role_id", "role_quotation", "time_source_expression", "time_quotation",
                  "time_edtf", "context_id", "context_quotation")


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
    time_expression: Text
    time_quotation: Text
    time_edtf: Text


PERIOD_OPTIONAL = ("time_expression", "time_quotation", "time_edtf")


class ReaderParticipant(BaseModel):
    entity_id: str
    quotation: str


class ReaderEventLink(BaseModel):
    relation: str  # triggered_by, resulted_in, or after; checked in to_depicted
    target: str
    quotation: str


class ReaderDepictedEvent(BaseModel):
    # Plain strings, empty when absent: optional fields would enlarge the output grammar.
    key: str
    label: str
    existing_id: str
    quotation: str
    within_narrative_event: bool
    participants: list[ReaderParticipant]
    place_id: str
    place_quotation: str
    time_expression: str
    time_quotation: str
    relative_offset: str
    links: list[ReaderEventLink]


class ReaderOutput(BaseModel):
    claims: list[ReaderClaim]
    unresolved_mentions: list[UnresolvedMention]
    notes: list[ReaderNote]
    periods: list[ReaderPeriod]
    depicted_events: list[ReaderDepictedEvent] = Field(default_factory=list)


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
    voice: str | None = None  # how labels name this source's depictions (the author's short name)
    reading_rules_version: int | None = None  # shared rules composed into the guidance (reading_rules.py)
    brief: dict[str, Any] | None = None  # the source brief whose conventions the guidance includes


def inquiry_sources(data: dict[str, Any]) -> list[dict[str, Any]]:
    """An inquiry reads one source (`source`) or, for an event inquiry, several (`sources`), in order."""
    return data["sources"] if "sources" in data else [data["source"]]


def load_inquiry(path: Path, tx: Any) -> Inquiry:
    """The inquiry for its first source (see load_inquiries)."""
    return load_inquiries(path, tx)[0]


def computed_scope(tx: Any, event_id: str, rules: ReadingRules) -> list[str]:
    """An event inquiry's scope from the graph (reading_rules `scope`): the event's neighbours, the
    entities taking part in its parts, the command structure of those, and every Concept."""
    live = "NOT a.status IN ['rejected', 'superseded']"

    def neighbours(ids: set[str], predicates: list[str] | None = None, kinds: list[str] | None = None) -> set[str]:
        return set(tx.run(
            f"""
            MATCH (e:Entity)<-[:ASSERTION_SUBJECT|ASSERTION_OBJECT]-(a:Assertion)
                  -[:ASSERTION_SUBJECT|ASSERTION_OBJECT]->(n:Entity)
            WHERE e.id IN $ids AND n <> e AND {live}
              AND ($predicates IS NULL OR a.predicate IN $predicates) AND ($kinds IS NULL OR n.kind IN $kinds)
            RETURN collect(DISTINCT n.id) AS ids
            """, ids=sorted(ids), predicates=predicates, kinds=kinds).single()["ids"])

    spec = rules.scope
    parts = set(tx.run(
        f"""
        MATCH (part:Entity {{kind: 'Event'}})<-[:ASSERTION_SUBJECT]-(a:Assertion {{predicate: 'partOf'}})
              -[:ASSERTION_OBJECT]->(:Entity {{id: $id}})
        WHERE {live} RETURN collect(DISTINCT part.id) AS ids
        """, id=event_id).single()["ids"])
    found = neighbours({event_id}) | neighbours(parts, kinds=spec["kinds"])
    found |= neighbours(found | {event_id}, predicates=spec["commandPredicates"])
    if spec.get("allConcepts"):
        found |= set(tx.run(
            "MATCH (c:Entity {kind: 'Concept'}) WHERE NOT coalesce(c.status, '') IN ['rejected', 'deprecated'] "
            "RETURN collect(c.id) AS ids").single()["ids"])
    kinds = set(spec["kinds"]) | {"Work"}
    kept = tx.run("MATCH (e:Entity) WHERE e.id IN $ids AND e.kind IN $kinds RETURN collect(e.id) AS ids",
                  ids=sorted(found), kinds=sorted(kinds)).single()["ids"]
    return sorted(i for i in kept if not i.startswith("chr:entity:depicted:") and i != event_id)


def load_inquiries(path: Path, tx: Any, *, briefs: Path | None = BRIEFS_DIRECTORY) -> list[Inquiry]:
    """Read the inquiry file and resolve its scope against the graph: one Inquiry per source,
    sharing the subject, narrative event, scope, and guidance, each adding its source's own guidance.

    An inquiry with `readingRules` is told the shared rules and its sources' briefs (reading_rules.py);
    with `"scope": "computed"` its scope comes from the graph rather than `candidateEntityIds`.
    `briefs=None` leaves the briefs out (the briefing agent reads a source without its old brief)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = load_reading_rules() if data.get("readingRules") else None
    if rules is not None and data["readingRules"] != rules.version:
        raise ValueError(f"the inquiry asks for reading rules v{data['readingRules']}, not v{rules.version}")
    declared = list(data.get("candidateEntityIds", []))
    if data.get("scope") == "computed":
        if rules is None or not data.get("narrativeEventId"):
            raise ValueError("a computed scope needs readingRules and a narrativeEventId")
        declared = sorted(set(declared) | set(computed_scope(tx, data["narrativeEventId"], rules)))
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
        declared=declared,
    ).single()
    if record is None:
        raise ValueError(f"{data['subjectId']} is not a Subject with a focus Entity")
    missing = set(declared) - set(record["scopeIds"])
    if missing:
        raise ValueError(f"declared candidates are not Entities: {sorted(missing)}")
    mentioned: list[str] = []
    if data.get("scopeFromMentions"):
        # Entities named in the inquiry's own sources (their entity mentions, such as a first
        # contact's links) join the scope, so the reader can use what discovery surfaced.
        mentioned = tx.run(
            """
            MATCH (mention:Annotation {kind: "entity-mention"})-[:ANNOTATES]->(:SourceObservation)
                  -[:IN_WORK]->(work:Entity) WHERE work.id IN $works
            MATCH (mention)-[:CONCERNS]->(entity:Entity)
            WHERE NOT entity.status IN ["deprecated", "rejected"] AND NOT entity.id STARTS WITH "chr:entity:depicted:"
            RETURN DISTINCT entity.id AS id
            """,
            works=[source["workId"] for source in inquiry_sources(data)],
        ).value("id")
    forms: dict[str, str | None] = {}
    for source in inquiry_sources(data):
        work_id = source.get("workId")
        work = tx.run("MATCH (w:Entity {id: $id, kind: 'Work'}) RETURN w.form AS form", id=work_id).data() if work_id else []
        if len(work) != 1:
            raise ValueError(f"the inquiry's source needs a workId naming a Work Entity, not {work_id!r}")
        forms[work_id] = work[0]["form"]

    def guidance(source: dict[str, Any]) -> tuple[list[str], dict[str, Any] | None]:
        if rules is None:
            return data.get("guidance", []) + source.get("guidance", []), None
        brief = load_brief(source["workId"], briefs) if briefs is not None else None
        shared = rules.guidance(form=forms[source["workId"]], event_inquiry=bool(narrative_event_id),
                                predicates=list(rules.predicates))
        return shared + brief_guidance(brief) + data.get("guidance", []) + source.get("guidance", []), brief
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
        ids=sorted(set(record["scopeIds"]) | set(mentioned)),
    ).value("entity")
    scope = [{**entity, **entity_context(entity["payloadUri"], entity["qid"])} for entity in scope]
    composed = [(source, *guidance(source)) for source in inquiry_sources(data)]
    return [
        Inquiry(
            id=data["id"],
            version=data["version"],
            label=data["label"],
            subject=record["subject"],
            focus=record["focus"],
            scope=scope,
            guidance=lines,
            source=source,
            work_id=source["workId"],
            narrative_event_id=narrative_event_id,
            calendar=data.get("calendar"),
            context_before=source.get("contextWindow", {}).get("before", 2),
            context_after=source.get("contextWindow", {}).get("after", 1),
            note_visibility=data.get("noteVisibility", "private"),
            proposable_kinds=tuple(data.get("proposableKinds", [])),
            voice=source.get("voice"),
            reading_rules_version=rules.version if rules else None,
            brief={k: brief.get(k) for k in ("workId", "createdAt", "promptVersion", "model")} if brief else None,
        )
        for source, lines, brief in composed
    ]


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
    depicted: list[dict[str, Any]] = (),
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
    already = ""
    if "Event" in inquiry.proposable_kinds:
        already = ("Events already depicted from this source (id | label):\n"
                   + ("\n".join(f"- {e['id']} | {e['label']}" for e in depicted) or "- none yet") + "\n\n")
    user = (
        already
        + f"Surrounding sections (context only, not evidence):\n"
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


PROMPT_VERSION = prompt_version("passage-reader-v13", SYSTEM_PROMPT, predicate_guide, read_passage)


def to_drafts(
    output: ReaderOutput, observation_id: str, model_id: str, inquiry: Inquiry
) -> tuple[list[ProposalDraft], list[dict]]:
    drafts, malformed = [], []
    for claim in output.claims:
        claim = _absent(claim, CLAIM_OPTIONAL)
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
        period = _absent(period, PERIOD_OPTIONAL)
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


LINK_PREDICATES = {"triggered_by": "triggeredBy", "resulted_in": "resultedIn", "after": "happenedBefore"}


def to_depicted(
    output: ReaderOutput, passage: dict[str, Any], inquiry: Inquiry, known_ids: set[str], scope_ids: set[str]
) -> tuple[list[dict], list[dict]]:
    """Depicted events checked against the passage: each with its local `id` (new or existing),
    and only the participants, place, time, and links that the passage shows verbatim.
    A part that fails is dropped with its reason; an event whose core fails is refused."""
    if "Event" not in inquiry.proposable_kinds:
        return [], [{"event": e.model_dump(), "reason": "the inquiry does not allow Event proposals"}
                    for e in output.depicted_events]
    text = normalize(passage["passageText"])

    def verbatim(span: str | None, minimum: int = 15) -> bool:
        return bool(span) and len(normalize(span)) >= minimum and normalize(span) in text

    keyed: dict[str, str] = {}
    for event in output.depicted_events:
        if event.existing_id:
            keyed[event.key] = event.existing_id
        elif event.label and event.label.strip():
            keyed[event.key] = depicted_event_id(inquiry.work_id, event.label)
    events, refused = [], []
    seen: set[str] = set()
    for event in output.depicted_events:
        reason = None
        if event.key in seen:
            reason = f"duplicate key {event.key!r}"
        elif event.existing_id and event.existing_id not in known_ids:
            reason = f"existing_id {event.existing_id!r} is not an event depicted from this source"
        elif not event.existing_id and not (event.label and event.label.strip()):
            reason = "a new event needs a label"
        elif not verbatim(event.quotation):
            reason = "quotation does not appear verbatim in the passage"
        elif event.relative_offset and not (event.within_narrative_event and inquiry.narrative_event_id):
            reason = "a relative offset counts from the narrative event, so the event must be within it"
        elif event.relative_offset and not re.fullmatch(DURATION_PATTERN, event.relative_offset):
            reason = f"relative offset {event.relative_offset!r} is not an ISO 8601 duration"
        seen.add(event.key)
        if reason:
            refused.append({"event": event.model_dump(), "reason": reason})
            continue
        dropped = []
        participants = []
        for p in event.participants:
            if p.entity_id not in scope_ids:
                dropped.append({"participant": p.entity_id, "reason": "not in inquiry scope"})
            elif not verbatim(p.quotation):
                dropped.append({"participant": p.entity_id, "reason": "quotation not verbatim"})
            else:
                participants.append({"id": p.entity_id, "quotation": p.quotation})
        place = None
        if event.place_id:
            if event.place_id in scope_ids and verbatim(event.place_quotation):
                place = {"id": event.place_id, "quotation": event.place_quotation}
            else:
                dropped.append({"place": event.place_id, "reason": "not in scope or quotation not verbatim"})
        time = None
        if event.time_expression:
            if (verbatim(event.time_quotation, 3)
                    and normalize(event.time_expression) in normalize(event.time_quotation)):
                time = {"expression": event.time_expression, "quotation": event.time_quotation,
                        "offset": event.relative_offset or None}
            else:
                dropped.append({"time": event.time_expression, "reason": "the time expression must appear in a verbatim time quotation"})
        links = []
        for link in event.links:
            target = keyed.get(link.target) or (link.target if link.target in known_ids
                                                or link.target == inquiry.narrative_event_id else None)
            if link.relation not in LINK_PREDICATES:
                dropped.append({"link": link.model_dump(), "reason": f"unknown relation {link.relation!r}"})
            elif target is None:
                dropped.append({"link": link.model_dump(), "reason": "unknown target"})
            elif not verbatim(link.quotation):
                dropped.append({"link": link.model_dump(), "reason": "quotation not verbatim"})
            elif target == keyed[event.key]:
                dropped.append({"link": link.model_dump(), "reason": "an event cannot link to itself"})
            else:
                links.append({"relation": link.relation, "target": target, "quotation": link.quotation})
        events.append({
            "key": event.key, "id": keyed[event.key], "new": not event.existing_id,
            "label": (event.label or "").strip(), "quotation": event.quotation,
            "withinNarrativeEvent": event.within_narrative_event, "participants": participants,
            "place": place, "time": time, "links": links, "dropped": dropped,
        })
    return events, refused


def depicted_drafts(event: dict, observation_id: str, model_id: str, inquiry: Inquiry) -> list[ProposalDraft]:
    """The attributed claims a depicted event stands for: within the narrative event, who took part,
    where, when (as the source words it), and its links to other events."""
    def draft(predicate: str, subject: str, obj: str | None, quotation: str, rationale: str, **extra) -> ProposalDraft:
        return ProposalDraft(
            predicate=predicate, subject_id=subject, object_id=obj, observation_ids=(observation_id,),
            quotations=(Quotation(observation_id=observation_id, text=quotation),),
            rationale=rationale, proposed_by=PROPOSER_ID, prompt_version=PROMPT_VERSION, model_id=model_id,
            inquiry_id=inquiry.id, relevance="A step in this source's account of the narrative event.",
            mode="attributed", attributed_to=inquiry.work_id, **extra,
        )

    narrative = inquiry.narrative_event_id
    drafts = []
    if event["withinNarrativeEvent"] and narrative:
        drafts.append(draft("partOf", event["id"], narrative, event["quotation"],
                            "The source narrates this action within the narrative event."))
    for p in event["participants"]:
        drafts.append(draft("participatedIn", p["id"], event["id"], p["quotation"],
                            "The passage names this participant in the depicted action."))
    if event["place"]:
        drafts.append(draft("occurredAt", event["id"], event["place"]["id"], event["place"]["quotation"],
                            "The passage gives the place of the depicted action."))
    if event["time"]:
        within = event["withinNarrativeEvent"] and narrative
        drafts.append(draft(
            "occurred", event["id"], None, event["quotation"],
            f"The passage marks the time of the action: {event['time']['expression']}.",
            time=TimeQualifier(source_expression=event["time"]["expression"],
                               relative_offset=event["time"]["offset"]),
            qualifier_quotations=(QualifierQuotation(observation_id=observation_id, supports="time",
                                                     text=event["time"]["quotation"]),),
            context_id=narrative if within else None, context_basis="inquiry" if within else None,
        ))
    for link in event["links"]:
        predicate = LINK_PREDICATES[link["relation"]]
        subject, obj = (link["target"], event["id"]) if link["relation"] == "after" else (event["id"], link["target"])
        drafts.append(draft(predicate, subject, obj, link["quotation"],
                            f"The passage presents this order between the events ({link['relation'].replace('_', ' ')})."))
    return drafts


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
    parser.add_argument("--chapters", help="a range in the source's own terms, such as 65-68 (overrides the inquiry's chapters)")
    parser.add_argument("--source", help="for an inquiry with several sources: read only the one with this workId")
    parser.add_argument("--found", action="store_true",
                        help="read only the passages the passage finder selected for each source (discovery/passage_finder.py)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--submit", action="store_true", help="store valid drafts as submitted Proposals")
    parser.add_argument("--outputs", default="claims,notes,periods,events",
                        help="which outputs to store with --submit (claims, notes, periods, events)")
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
    storing = set(args.outputs.split(","))

    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session, \
                run_path.open("w", encoding="utf-8") as log:
            inquiries = session.execute_read(lambda tx: load_inquiries(args.inquiry, tx))
            if args.source:
                inquiries = [i for i in inquiries if i.work_id == args.source]
                if not inquiries:
                    raise ValueError(f"the inquiry has no source with workId {args.source!r}")
            for inquiry in inquiries:
                # A dry run keeps the whole source in one transaction, rolled back at the end, so
                # events proposed in one passage can be linked from the next; --submit commits
                # passage by passage.
                dry = None if args.submit else session.begin_transaction()
                try:
                    periodo = _read_source(args, inquiry, session, dry, operations, registry, client, log,
                                           authorities, periodo, totals, storing)
                finally:
                    if dry is not None:
                        dry.rollback()
    finally:
        driver.close()

    print(f"\nlog: {run_path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    print(json.dumps(totals))
    return 0


def _read_source(args, inquiry: Inquiry, session, dry, operations, registry, client, log, authorities,
                 periodo, totals: dict[str, int], storing: set[str]):
    scope_ids = {entity["id"] for entity in inquiry.scope}
    edition = open_source(inquiry.source, GRAPH_REVISED)
    finds = None
    if args.sections:
        refs = args.sections.split(",")
    elif getattr(args, "found", False):
        from GraphRevised.discovery.passage_finder import load_finds  # discovery builds on the reader, not the reverse
        finds = load_finds(inquiry.id, inquiry.work_id)
        if finds is None:
            raise ValueError(f"no passage finds for {inquiry.work_id}; run discovery.passage_finder first")
        refs = finds["selected"]
    else:
        refs = edition.refs(args.chapters or inquiry.source.get("chapters"))
    all_refs = edition.refs(None)
    known = (depicted_events(dry, inquiry.work_id) if dry is not None
             else session.execute_read(lambda tx: depicted_events(tx, inquiry.work_id)))
    scope_ids |= {e["id"] for e in known}
    print(f"inquiry: {inquiry.id} v{inquiry.version} -> {inquiry.subject['label']}; source: {inquiry.work_id}")
    print(f"scope: {', '.join(e['label'] for e in inquiry.scope)}\n")
    log.write(json.dumps({
        "inquiry": inquiry.id, "inquiryVersion": inquiry.version, "subject": inquiry.subject["id"],
        "scope": sorted(scope_ids), "promptVersion": PROMPT_VERSION, "model": args.model,
        "predicateRegistryVersion": registry.version, "draftSchemaVersion": DRAFT_SCHEMA_VERSION,
        "workId": inquiry.work_id, "narrativeEventId": inquiry.narrative_event_id, "submit": args.submit,
        "readingRulesVersion": inquiry.reading_rules_version, "brief": inquiry.brief,
        "finds": {k: finds[k] for k in ("createdAt", "promptVersion", "model", "passages")} | {"selected": len(refs)}
                 if finds else None,
    }) + "\n")

    for ref in refs:
        passage = edition.observation(ref)
        index = all_refs.index(ref)
        context = [
            (r, edition.observation(r)["passageText"])
            for r in all_refs[max(0, index - inquiry.context_before):index]
            + all_refs[index + 1:index + 1 + inquiry.context_after]
        ]
        output, meta = read_passage(client, args.model, inquiry, edition, ref, passage, context, registry, known)
        for key in ("inputTokens", "cacheReadTokens", "cacheWriteTokens", "outputTokens"):
            totals[key] += meta[key]
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
        events, refused_events = to_depicted(output, passage, inquiry, {e["id"] for e in known}, scope_ids)
        if "events" not in storing:
            events = []
        if "claims" not in storing:
            drafts = []

        # The observation is written first so drafts can be validated
        # against it; the transaction commits only if something was stored.
        results: list[tuple[ProposalDraft, str, list[str], str | None, bool]] = []
        event_results: list[dict] = []
        tx = dry if dry is not None else session.begin_transaction()
        try:
            run_write(tx, operations, "upsert_passage_observation", passage)
            run_write(tx, operations, "link_observation_work", {
                "observationId": passage["id"], "workId": inquiry.work_id,
            })
            # Depicted events exist before the claims that name them are validated.
            event_drafts: list[ProposalDraft] = []
            for event in events:
                if event["new"]:
                    proposed = propose_depicted_event(
                        tx, operations, work_id=inquiry.work_id, label=event["label"],
                        voice=inquiry.voice or edition.author, proposed_by=PROPOSER_ID,
                        observation_id=passage["id"], quotation=event["quotation"])
                    if proposed["created"]:
                        known.append({"id": proposed["id"], "label": f"{event['label']} ({inquiry.voice or edition.author})"})
                scope_ids.add(event["id"])
                event_results.append({"id": event["id"], "new": event["new"]})
                event_drafts.extend(depicted_drafts(event, passage["id"], meta["model"], inquiry))
            for draft in drafts + event_drafts:
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
                        "id": note_id, "kind": "passage-of-note",
                        "label": annotation_label(tx, kind="passage-of-note", note_type=note["noteType"],
                                                  observation_id=passage["id"]),
                        "noteType": note["noteType"], "note": note["note"], "author": PROPOSER_ID,
                        "visibility": inquiry.note_visibility,
                        "createdAt": datetime.now(timezone.utc).isoformat(),
                        "observationId": passage["id"], "quotation": note["quotation"],
                        "concerns": note["concerns"],
                    })
                    stored_notes.append(note_id)
            if dry is None:
                if any(stored for *_, stored in results) or stored_notes or period_results or event_results:
                    tx.commit()
                else:
                    tx.rollback()
        except BaseException:
            if dry is None:
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
        record["depictedEvents"] = events
        record["refusedEvents"] = refused_events
        record["unresolvedMentions"] = [m.model_dump() for m in output.unresolved_mentions]
        log.write(json.dumps(record, ensure_ascii=False) + "\n")
        for event in events:
            print(f"{ref}: event {'new ' if event['new'] else ''}{event['id'].rsplit(':', 1)[1]}"
                  + (f" @ {event['time']['expression']!r}" if event["time"] else "")
                  + (f" [dropped {len(event['dropped'])}]" if event["dropped"] else ""))
        for refused in refused_events:
            print(f"{ref}: event refused -- {refused['reason']}")
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
        totals["events"] = totals.get("events", 0) + len(events)
        totals["refusedEvents"] = totals.get("refusedEvents", 0) + len(refused_events)
        names = ", ".join(m.name for m in output.unresolved_mentions)
        print(f"{ref}: {len(drafts)} draft(s), {len(events)} event(s), {len(notes)} note(s); unresolved: {names or '-'}")
    return periodo


if __name__ == "__main__":
    raise SystemExit(main())
