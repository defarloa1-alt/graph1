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

from .historiography import (HISTORIOGRAPHY_PREDICATES, HISTORIOGRAPHY_RULES, HistoriographyOutput,
                             historiography_text)
from .lens import Lens, lens_registry, lens_text, load_lens
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
with a quotation of at least 15 characters naming or referring to them, and a role_id only when \
the passage names the part it played (captor, captive, defector, hostage, envoy: an in-scope Office \
or Type), with role_quotation copied exactly and containing the role's words; objects, the in-scope \
named things the action takes, dedicates, or destroys (a ship, a standard, a statue), never people or \
forces, each with a quotation as for participants and a role_id (seized, or another in-scope Type) \
with its role_quotation; things the passage only counts ("three hundred ships") stay in the label \
and are not objects; place_id and \
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

# Added to the system prompt only when the reader reads through a lens (39-LENS-SPECIALISTS.md).
LENS_RULES = """\
16. Lens. You read as one lens's specialist, described in the task packet. Draft a claim or a note \
only where the passage bears on the lens's scope; in relevance, say how the claim bears on the \
subject through this lens. The predicates listed are the lens's own: use no other, and where a \
relationship the lens needs fits none of them, do not stretch one. The lens's native terms help \
you read the source's words; they are never evidence and never claims. The lens rules refine \
rules 1 to 15 for this lens; they never relax them. Periods are not part of a lens reading. Draft \
depicted events (rule 15) for actions that bear on the lens, when the task packet allows Event \
proposals; reuse an event already depicted from this source rather than depicting it again.
17. Predicate needs. An act (a capture, a levy, a declaration, a dedication, a surrender) is a \
depicted event, never a predicate. Ask for a predicate only for a state that holds between two \
entities over time and that no listed predicate fits: report it under predicate_needs with a \
camelCase name, a one-line definition, the kinds it joins written as "Subject/Kinds -> Object/Kinds", \
and the exact \
quotation that shows it (rules as in 5). A need asserts nothing; it asks for the registry to grow.
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
    # Plain strings, empty when absent (as for depicted events): the part the passage gives it.
    role_id: Text
    role_quotation: Text


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
    objects: list[ReaderParticipant]  # named Objects, each through a role (registry v14 involvedIn)
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


class LensPredicateNeed(BaseModel):
    name: str
    definition: str
    # "Person/Group -> Office": one text field, not two lists, keeps the lens output's grammar under
    # the API's limit (2026-11-16); split by need_kinds.
    kinds: str
    quotation: str


def need_kinds(kinds: str) -> tuple[list[str], list[str]]:
    """"Person/Group -> Office" as (["Person", "Group"], ["Office"]); no arrow: no object kinds."""
    subject, _, obj = kinds.partition("->")

    def split(side: str) -> list[str]:
        return [kind.strip() for kind in re.split(r"[/,]| or ", side) if kind.strip()]
    return split(subject), split(obj)


class LensReaderOutput(BaseModel):
    """What a lens reading returns: no periods (the general reader's), and predicate needs (D-138)."""
    claims: list[ReaderClaim]
    unresolved_mentions: list[UnresolvedMention]
    notes: list[ReaderNote]
    depicted_events: list[ReaderDepictedEvent]
    predicate_needs: list[LensPredicateNeed]


class HistoriographyLensOutput(BaseModel):
    """A lens reading of modern scholarship also reports its historiography (44, rule 18): claims and
    historiography only. Notes, mentions, depicted events and predicate needs are left out: on a
    licensed page they would not be stored (D-156), and with any of them the output grammar passed
    the API's limit (probed 2026-11-16)."""
    claims: list[ReaderClaim]
    historiography: HistoriographyOutput


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
    graph_context: dict[str, Any] | None = None  # reviewable graph context, not passage evidence
    lens: Lens | None = None  # read through one lens in one scope (proposals/lens.py); None: the general reader
    # A lens reading of modern scholarship (44): the Questions, Positions, and holder Works already
    # known, for historiography_text; None: no historiography section.
    historiography: dict[str, Any] | None = None
    # The curator's own note on the passage (capture/note_reader.py): a prompt for Questions and
    # lenses, never a source, evidence, or quotation. None: no note.
    curator_note: str | None = None


EVENT_ROLES_PATH = GRAPH_REVISED / "curation" / "event-roles.json"


def event_role_aliases(path: Path = EVENT_ROLES_PATH) -> dict[str, list[str]]:
    """The curator's aliases for each event role, shown to the reader beside the role (they stay off the Entity)."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {role["id"]: role.get("aliases", []) for role in data.get("localEntities", [])}


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
              AND ($predicates IS NULL OR a.predicate IN $predicates)
              AND ($kinds IS NULL OR head([kind IN labels(n) WHERE kind IN $kinds]) IN $kinds)
            RETURN collect(DISTINCT n.id) AS ids
            """, ids=sorted(ids), predicates=predicates, kinds=kinds).single()["ids"])

    spec = rules.scope
    parts = set(tx.run(
        f"""
        MATCH (part:Entity:Event)<-[:ASSERTION_SUBJECT]-(a:Assertion {{predicate: 'partOf'}})
              -[:ASSERTION_OBJECT]->(:Entity {{id: $id}})
        WHERE {live} RETURN collect(DISTINCT part.id) AS ids
        """, id=event_id).single()["ids"])
    found = neighbours({event_id}) | neighbours(parts, kinds=spec["kinds"])
    found |= neighbours(found | {event_id}, predicates=spec["commandPredicates"])
    if spec.get("allConcepts"):
        found |= set(tx.run(
            "MATCH (c:Entity:Concept) WHERE NOT coalesce(c.status, '') IN ['rejected', 'deprecated'] "
            "RETURN collect(c.id) AS ids").single()["ids"])
    kinds = set(spec["kinds"]) | {"Work"}
    kept = tx.run(
        "MATCH (e:Entity) WHERE e.id IN $ids AND any(entityKind IN $kinds WHERE entityKind IN labels(e)) "
        "RETURN collect(e.id) AS ids",
                  ids=sorted(found), kinds=sorted(kinds)).single()["ids"]
    return sorted(i for i in kept if not i.startswith("chr:entity:depicted:") and i != event_id)


def graph_scope_context(tx: Any, event_id: str, scope: list[dict[str, Any]], rules: ReadingRules) -> dict[str, Any]:
    """Selected graph assertions for review; inclusion does not establish relevance or evidence."""
    ids = sorted({entity["id"] for entity in scope} | {event_id})
    assertions = tx.run(
        """
        MATCH (subject:Entity)<-[:ASSERTION_SUBJECT]-(a:Assertion)-[:ASSERTION_OBJECT]->(object:Entity)
        WHERE subject.id IN $ids AND object.id IN $ids
          AND NOT a.status IN ['rejected', 'superseded']
          AND (subject.id = $event OR object.id = $event OR a.predicate IN $predicates)
        RETURN DISTINCT a.id AS id, a.predicate AS predicate, a.status AS status,
               subject.id AS subjectId, subject.label AS subjectLabel,
               object.id AS objectId, object.label AS objectLabel
        ORDER BY subjectId, predicate, objectId, status, id
        """,
        ids=ids, event=event_id, predicates=rules.scope["commandPredicates"],
    ).data()
    foreign_events = tx.run(
        """
        MATCH (group:Entity:Group)<-[:ASSERTION_SUBJECT]-(a:Assertion)-[:ASSERTION_OBJECT]->(event:Entity:Event)
        WHERE group.id IN $ids AND event.id <> $event AND NOT event.id STARTS WITH 'chr:entity:depicted:'
          AND a.predicate = 'participatedIn' AND NOT a.status IN ['rejected', 'superseded']
        RETURN DISTINCT group.id AS groupId, group.label AS groupLabel, event.id AS eventId,
               event.label AS eventLabel, a.id AS assertionId, a.status AS status
        ORDER BY groupId, eventId, status, assertionId
        """,
        ids=ids, event=event_id,
    ).data()
    groups = [{"id": e["id"], "label": e["label"]} for e in scope if e["kind"] == "Group"]
    return {"focusId": event_id, "assertions": assertions, "groupsToReview": groups,
            "otherEventParticipations": foreign_events}


def graph_context_text(context: dict[str, Any] | None) -> str:
    if context is None:
        return ""
    lines = [
        "Graph context for review only: these are selected existing assertions, not evidence from the target passage.",
        "Proposed assertions are not accepted facts. A connection to one event does not establish participation in another.",
        "Repeated assertions do not by themselves establish independent corroboration.",
        "Review every group or force's event-specific identity; a shared commander does not make forces interchangeable.",
        "Selected graph assertions (subject | predicate | object | assertion status | assertion ID):",
    ]
    lines.extend(
        f"- {a['subjectLabel']} ({a['subjectId']}) | {a['predicate']} | "
        f"{a['objectLabel']} ({a['objectId']}) | {a['status']} | {a['id']}"
        for a in context["assertions"]
    )
    lines.append("Groups and forces requiring event-specific review:")
    lines.extend(f"- {g['label']} ({g['id']})" for g in context["groupsToReview"])
    lines.append("Existing group participation assertions for other non-depicted events:")
    lines.extend(
        f"- {a['groupLabel']} ({a['groupId']}) | {a['eventLabel']} ({a['eventId']}) | "
        f"{a['status']} | {a['assertionId']}"
        for a in context["otherEventParticipations"]
    )
    return "\n".join(lines)


def load_inquiries(path: Path, tx: Any, *, briefs: Path | None = BRIEFS_DIRECTORY) -> list[Inquiry]:
    """Read the inquiry file and resolve its scope against the graph: one Inquiry per source,
    sharing the subject, narrative event, scope, and guidance, each adding its source's own guidance.

    An inquiry with `readingRules` is told the shared rules and its sources' briefs (reading_rules.py);
    with `"scope": "computed"` its scope comes from the graph rather than `candidateEntityIds`.
    `briefs=None` leaves the briefs out (the briefing agent reads a source without its old brief)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = load_reading_rules(version=data["readingRules"]) if data.get("readingRules") else None
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
               [entity IN focus | entity {.id, .label, kind: head([label IN labels(entity) WHERE label <> 'Entity']), .description}] AS focus,
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
    roles: list[str] = []
    role_aliases: dict[str, list[str]] = {}
    if "Event" in data.get("proposableKinds", []):
        # The parts played in depicted events (curation/event-roles.json, D-138) join the scope of
        # every inquiry that may depict events, so a role the passage names can be kept.
        roles = tx.run(
            'MATCH (role:Entity:Type) WHERE role.id STARTS WITH "chr:entity:role-" '
            'AND NOT coalesce(role.status, "") IN ["deprecated", "rejected"] RETURN role.id AS id'
        ).value("id")
        role_aliases = event_role_aliases()
    forms: dict[str, str | None] = {}
    for source in inquiry_sources(data):
        work_id = source.get("workId")
        work = tx.run(        "MATCH (w:Entity:Work {id: $id}) RETURN w.form AS form", id=work_id).data() if work_id else []
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
        "MATCH (e:Entity:Event {id: $id}) RETURN count(e) AS n", id=narrative_event_id
    ).single()["n"] != 1:
        raise ValueError(f"narrativeEventId {narrative_event_id!r} is not an Event Entity")
    scope = tx.run(
        """
        MATCH (entity:Entity) WHERE entity.id IN $ids
        OPTIONAL MATCH (entity)-[link:HAS_AUTHORITY_RECORD]->(record:AuthorityRecord {system: "Wikidata"})
        WHERE link.role = "entity_identity" AND link.status = "accepted"
        WITH entity, head(collect(record)) AS record
        RETURN entity {.id, .label, kind: head([label IN labels(entity) WHERE label <> 'Entity']), .description,
                       qid: record.identifier, payloadUri: record.rawPayloadUri} AS entity
        ORDER BY entity.id
        """,
        ids=sorted(set(record["scopeIds"]) | set(mentioned) | set(roles)),
    ).value("entity")
    scope = [{**entity, "aliases": role_aliases[entity["id"]]} if role_aliases.get(entity["id"]) else entity
             for entity in scope]
    scope = [{**entity, **entity_context(entity["payloadUri"], entity["qid"])} for entity in scope]
    graph_context = (graph_scope_context(tx, narrative_event_id, scope, rules)
                     if data.get("scope") == "computed" and rules and narrative_event_id else None)
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
            graph_context=graph_context,
        )
        for source, lines, brief in composed
    ]


def anthropic_client():
    """A metered client: use ANTHROPIC_API_KEY from the environment, else only that key from .env.

    The rest of .env is deliberately not loaded: it holds legacy Neo4j
    settings that must not redirect the clean-start database connection.
    Every call is priced and capped by the named budget (spend_meter, 41 §3.8);
    with no budget named, this refuses before any client is made.
    """
    from GraphRevised.spend_meter import Meter, MeteredClient
    meter = Meter.from_environment()
    key = os.environ.get("ANTHROPIC_API_KEY") or dotenv_values(GRAPH_REVISED.parent / ".env").get("ANTHROPIC_API_KEY")
    return MeteredClient(anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic(), meter)


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
        # The historiography predicates are drafted through their own section (rule 18), never as claims.
        if "attributed" in d.modes and d.id not in HISTORIOGRAPHY_PREDICATES
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
    request = reader_request(model, inquiry, edition, ref, passage, context, registry, depicted)
    response = client.beta.messages.parse(**request)
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
    return (from_lens_output(response.parsed_output, meta) if inquiry.lens is not None
            else response.parsed_output), meta


def reader_request(
    model: str,
    inquiry: Inquiry,
    edition: PassageSource,
    ref: str,
    passage: dict[str, Any],
    context: list[tuple[str, str]],
    registry: PredicateRegistry,
    depicted: list[dict[str, Any]] = (),
) -> dict[str, Any]:
    """The request a reading sends for one passage, built without calling anything (a dry run shows it)."""
    def entity_line(entity: dict[str, Any]) -> str:
        line = f"- {entity['id']} | {entity['label']} | {entity['kind']} | {entity.get('description') or ''}"
        if entity.get("aliases"):
            line += f" | aliases: {'; '.join(entity['aliases'])}"
        if entity.get("dates"):
            line += " | " + ", ".join(f"{name} {year}" for name, year in entity["dates"].items())
        return line

    lens = inquiry.lens
    historiography = lens is not None and inquiry.historiography is not None
    if lens is not None:
        registry = lens_registry(registry, lens)
    # Everything that is the same for every passage of a run comes first and is
    # cached; only the surrounding sections and the target passage vary.
    packet = (
        (lens_text(lens) + "\n\n" if lens is not None else "") +
        f"Inquiry: {inquiry.label}\n"
        f"Subject: {inquiry.subject['label']}\n"
        f"Subject focus:\n" + "\n".join(entity_line(e) for e in inquiry.focus) + "\n\n"
        f"Inquiry guidance:\n" + "\n".join(f"- {line}" for line in inquiry.guidance) + "\n\n"
        f"Source: {edition.author}, {edition.title}"
        + (f", trans. {edition.translator}" if edition.translator else "") + f" ({edition.citation}).\n"
        f"Narrative event: {inquiry.narrative_event_id or 'none declared'}\n"
        f"Entity kinds you may propose: {', '.join(inquiry.proposable_kinds) or 'none'}\n\n"
        f"Predicates:\n{predicate_guide(registry)}\n\n"
        f"In-scope entities (id | label | kind | description):\n"
        + "\n".join(entity_line(e) for e in inquiry.scope)
        + ("\n\n" + graph_context_text(inquiry.graph_context) if inquiry.graph_context is not None else "")
    )
    already = ""
    if "Event" in inquiry.proposable_kinds:
        already = ("Events already depicted from this source (id | label):\n"
                   + ("\n".join(f"- {e['id']} | {e['label']}" for e in depicted) or "- none yet") + "\n\n")
    if historiography:
        # Per passage, not cached: the Questions and Positions grow as the reading goes (44).
        already += historiography_text(**inquiry.historiography) + "\n\n"
    if inquiry.curator_note:
        already += (
            "The curator's own note on the target passage. It is not a source: never quote it, never "
            "draft a claim from it, never attribute it to anyone. Use it only to notice what the "
            "passage itself says that bears on it, and, when historiography is asked for, a Question "
            "it raises that the passage's author answers:\n" + inquiry.curator_note + "\n\n")
    user = (
        already
        + f"Surrounding sections (context only, not evidence):\n"
        + "\n\n".join(f"[{r}] {text}" for r, text in context) + "\n\n"
        f"Target passage [{ref}]:\n{passage['passageText']}"
    )
    return {
        "model": model,
        "max_tokens": 16000,
        "betas": ["server-side-fallback-2026-07-01"],
        "extra_body": {"fallbacks": "default"},
        "system": [
            {"type": "text", "text": SYSTEM_PROMPT + (LENS_RULES if lens is not None else "")
                                     + (HISTORIOGRAPHY_RULES if historiography else "")},
            {"type": "text", "text": packet, "cache_control": {"type": "ephemeral"}},
        ],
        "messages": [{"role": "user", "content": user}],
        "output_format": (HistoriographyLensOutput if historiography
                          else LensReaderOutput if lens is not None else ReaderOutput),
    }


def from_lens_output(output: LensReaderOutput | None, meta: dict[str, Any]) -> ReaderOutput | None:
    """A lens reading as the reader's own output; its predicate needs travel in meta, checked later."""
    if output is None:
        return None
    meta["predicateNeedsDrafted"] = [
        {"name": need.name, "definition": need.definition, "quotation": need.quotation,
         "subject_kinds": need_kinds(need.kinds)[0], "object_kinds": need_kinds(need.kinds)[1]}
        for need in getattr(output, "predicate_needs", [])]
    if isinstance(output, HistoriographyLensOutput):  # converted by proposals/historiography.py (44)
        meta["historiographyDrafted"] = output.historiography.model_dump()
    return ReaderOutput(claims=output.claims, unresolved_mentions=getattr(output, "unresolved_mentions", []),
                        notes=getattr(output, "notes", []), periods=[],
                        depicted_events=getattr(output, "depicted_events", []))


PROMPT_VERSION = prompt_version("passage-reader-v14", SYSTEM_PROMPT, predicate_guide, graph_context_text,
                                read_passage, reader_request)
LENS_PROMPT_VERSION = prompt_version("lens-reader-v1", SYSTEM_PROMPT, LENS_RULES, HISTORIOGRAPHY_RULES, lens_text,
                                     historiography_text, predicate_guide,
                                     graph_context_text, read_passage, reader_request)


def proposer(inquiry: Inquiry) -> str:
    """Who drafts: the lens's specialist, or the general passage reader."""
    return inquiry.lens.specialist_id if inquiry.lens is not None else PROPOSER_ID


def reader_prompt_version(inquiry: Inquiry) -> str:
    return LENS_PROMPT_VERSION if inquiry.lens is not None else PROMPT_VERSION


def to_predicate_needs(drafted: list[dict[str, Any]], passage: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    """Predicate needs a lens reported, checked for a name, a definition, and a verbatim quotation."""
    needs, refused = [], []
    text = normalize(passage["passageText"])
    for need in drafted:
        reason = None
        if not re.fullmatch(r"[a-z][A-Za-z]+", need["name"].strip()):
            reason = "a need's name is one camelCase word"
        elif not need["definition"].strip():
            reason = "a need has a definition"
        elif len(normalize(need["quotation"])) < 15 or normalize(need["quotation"]) not in text:
            reason = "quotation does not appear verbatim in the passage"
        if reason:
            refused.append({"need": need, "reason": reason})
        else:
            needs.append({**need, "name": need["name"].strip(), "observationId": passage["id"]})
    return needs, refused


def to_drafts(
    output: ReaderOutput, observation_id: str, model_id: str, inquiry: Inquiry
) -> tuple[list[ProposalDraft], list[dict]]:
    drafts, malformed = [], []
    for claim in output.claims:
        claim = _absent(claim, CLAIM_OPTIONAL)
        if inquiry.lens is not None and claim.predicate not in inquiry.lens.predicates:
            malformed.append({"claim": claim.model_dump(),
                              "error": f"{claim.predicate} is not a predicate of the {inquiry.lens.id} lens"})
            continue
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
        proposed_by=proposer(inquiry), prompt_version=reader_prompt_version(inquiry), model_id=model_id,
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

        def checked(parts: list[ReaderParticipant], part: str) -> list[dict]:
            kept = []
            for p in parts:
                if p.entity_id not in scope_ids:
                    dropped.append({part: p.entity_id, "reason": "not in inquiry scope"})
                elif not verbatim(p.quotation):
                    dropped.append({part: p.entity_id, "reason": "quotation not verbatim"})
                else:
                    role = None
                    if p.role_id:
                        if p.role_id not in scope_ids:
                            dropped.append({part: p.entity_id, "role": p.role_id, "reason": "role not in inquiry scope"})
                        elif not verbatim(p.role_quotation):
                            dropped.append({part: p.entity_id, "role": p.role_id,
                                            "reason": "role quotation not verbatim"})
                        else:
                            role = {"id": p.role_id, "quotation": p.role_quotation}
                    kept.append({"id": p.entity_id, "quotation": p.quotation, "role": role})
            return kept

        participants = checked(event.participants, "participant")
        objects = checked(event.objects, "object")
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
            "withinNarrativeEvent": event.within_narrative_event, "participants": participants, "objects": objects,
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
            rationale=rationale, proposed_by=proposer(inquiry), prompt_version=reader_prompt_version(inquiry), model_id=model_id,
            inquiry_id=inquiry.id, relevance="A step in this source's account of the narrative event.",
            mode="attributed", attributed_to=inquiry.work_id, **extra,
        )

    narrative = inquiry.narrative_event_id
    drafts = []
    if event["withinNarrativeEvent"] and narrative:
        drafts.append(draft("partOf", event["id"], narrative, event["quotation"],
                            "The source narrates this action within the narrative event."))
    for p in event["participants"]:
        role = p.get("role")
        drafts.append(draft(
            "participatedIn", p["id"], event["id"], p["quotation"],
            "The passage names this participant in the depicted action"
            + (", and the part it played." if role else "."),
            **({"role_id": role["id"],
                "qualifier_quotations": (QualifierQuotation(observation_id=observation_id, supports="role",
                                                            text=role["quotation"]),)} if role else {}),
        ))
    for o in event.get("objects", []):
        role = o.get("role")  # involvedIn expects a role; without one the validator keeps the claim with a note
        drafts.append(draft(
            "involvedIn", o["id"], event["id"], o["quotation"],
            "The passage names this object in the depicted action" + (", and what befell it." if role else "."),
            **({"role_id": role["id"],
                "qualifier_quotations": (QualifierQuotation(observation_id=observation_id, supports="role",
                                                            text=role["quotation"]),)} if role else {}),
        ))
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
        proposed_by=proposer(inquiry),
        prompt_version=reader_prompt_version(inquiry),
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


def with_lookup_rationale(draft: ProposalDraft, selections: list[dict[str, Any]]) -> ProposalDraft:
    """Keep candidate identification reasoning on every proposal that uses it."""
    used = {draft.subject_id, draft.object_id, draft.role_id, draft.context_id} - {None}
    reasons = [
        f"{item['name']} -> {item['entity_id']}: {item['rationale']}"
        for item in selections if item["entity_id"] in used
    ]
    if not reasons:
        return draft
    data = draft.model_dump()
    data["rationale"] += " Candidate identification for review: " + "; ".join(reasons)
    return ProposalDraft.model_validate(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inquiry", type=Path, help="inquiry JSON file")
    parser.add_argument("--sections", help="comma-separated refs such as 65.1,65.2 (overrides the inquiry's chapters)")
    parser.add_argument("--chapters", help="a range in the source's own terms, such as 65-68 (overrides the inquiry's chapters)")
    parser.add_argument("--source", help="for an inquiry with several sources: read only the one with this workId")
    parser.add_argument("--found", action="store_true",
                        help="read only the passages the passage finder selected for each source (discovery/passage_finder.py)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--graph-lookup", action="store_true",
                        help="reason over local MCP graph tools per passage (extra paid model calls; no spend cap)")
    parser.add_argument("--submit", action="store_true", help="store valid drafts as submitted Proposals")
    parser.add_argument("--outputs", default=None,
                        help="which outputs to store with --submit (claims, notes, periods, events); "
                             "default all, or claims,notes,events with --lens")
    parser.add_argument("--lens", help="read through one lens (curation/lenses.json), as its specialist (39)")
    parser.add_argument("--lens-scope", default="roman-republic",
                        help="the lens's grounding: curation/lens-grounding/<scope>.json (default roman-republic)")
    args = parser.parse_args(argv)
    lens = None
    if args.lens:
        try:
            lens = load_lens(args.lens, args.lens_scope)
        except ValueError as error:
            parser.error(str(error))
        from .predicate_needs import load_queue, open_requests_text
        lens = replace(lens, requested=open_requests_text(load_queue()))
        args.outputs = args.outputs or "claims,notes,events"
        if "periods" in args.outputs.split(","):
            parser.error("a lens reading stores claims, notes, and events; periods are the general reader's")
    args.outputs = args.outputs or "claims,notes,periods,events"

    if args.graph_lookup and set(args.outputs.split(",")) != {"claims"}:
        parser.error("--graph-lookup currently requires --outputs claims to preserve identity review provenance")
    operations, registry, client = load_operations(), load_registry(), anthropic_client()
    if args.graph_lookup:
        from GraphRevised.subject_backbone import local_config
        config = local_config()
        client = client.with_options(max_retries=0)
        uri, user, password, database = config["uri"], config["user"], config["password"], config["database"]
    else:
        uri = os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
        user, password = os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]
        database = os.environ.get("NEO4J_DATABASE", "neo4j")
    driver = GraphDatabase.driver(uri, auth=(user, password), notifications_min_severity="OFF")
    RUNS_DIRECTORY.mkdir(exist_ok=True)
    run_name = f"lens-reader-{lens.id}-{lens.scope}" if lens else "passage-reader"
    run_path = RUNS_DIRECTORY / f"{run_name}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.jsonl"
    authorities = json.loads((GRAPH_REVISED / "curation" / "authorities.json").read_text(encoding="utf-8"))
    periodo = None  # loaded when a new period is first surveyed
    totals: dict[str, int] = {"stored": 0, "malformed": 0, "inputTokens": 0, "cacheReadTokens": 0,
                              "cacheWriteTokens": 0, "outputTokens": 0}
    storing = set(args.outputs.split(","))

    try:
        with driver.session(database=database) as session, \
                run_path.open("w", encoding="utf-8") as log:
            inquiries = session.execute_read(lambda tx: load_inquiries(args.inquiry, tx))
            if lens is not None:
                inquiries = [replace(inquiry, lens=lens) for inquiry in inquiries]
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
        "scope": sorted(scope_ids), "promptVersion": reader_prompt_version(inquiry), "model": args.model,
        "predicateRegistryVersion": registry.version, "draftSchemaVersion": DRAFT_SCHEMA_VERSION,
        "workId": inquiry.work_id, "narrativeEventId": inquiry.narrative_event_id, "submit": args.submit,
        "readingRulesVersion": inquiry.reading_rules_version, "brief": inquiry.brief,
        "graphLookup": bool(getattr(args, "graph_lookup", False)),
        "graphContext": inquiry.graph_context,
        "lens": {"id": inquiry.lens.id, "scope": inquiry.lens.scope, "specialist": inquiry.lens.specialist_id,
                 "predicates": list(inquiry.lens.predicates), "lensesVersion": inquiry.lens.lenses_version,
                 "groundingVersion": inquiry.lens.grounding_version} if inquiry.lens else None,
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
        active_inquiry = inquiry
        passage_scope_ids = set(scope_ids)
        lookup_report = None
        if getattr(args, "graph_lookup", False):
            from GraphRevised.discovery.passage_graph_lookup import lookup
            lookup_audit: dict[str, Any] = {}
            try:
                lookup_report = lookup(client, args.model, inquiry, passage["passageText"], context, lookup_audit)
            except Exception as error:
                log.write(json.dumps({"ref": ref, "observationId": passage["id"],
                                      "graphLookup": lookup_audit,
                                      "error": f"graph lookup failed: {error}"}) + "\n")
                log.flush()
                raise
            existing_ids = {entity["id"] for entity in inquiry.scope}
            added = []
            guidance = []
            for selection in lookup_report["selections"]:
                entity = selection["entity"]
                guidance.append(f"Candidate identification for review: {selection['name']} -> "
                                f"{entity['id']}: {selection['rationale']}")
                passage_scope_ids.add(entity["id"])
                if entity["id"] not in existing_ids:
                    added.append({"id": entity["id"], "label": entity["label"], "kind": entity["kind"],
                                  "description": entity.get("description")})
            active_inquiry = replace(inquiry, scope=inquiry.scope + added, guidance=inquiry.guidance + guidance)
        try:
            output, meta = read_passage(client, args.model, active_inquiry, edition, ref, passage, context, registry, known)
        except Exception:
            if lookup_report is not None:
                log.write(json.dumps({"ref": ref, "observationId": passage["id"], "graphLookup": lookup_report,
                                      "error": "reader call failed after graph lookup"}) + "\n")
                log.flush()
            raise
        for key in ("inputTokens", "cacheReadTokens", "cacheWriteTokens", "outputTokens"):
            totals[key] += meta[key]
        drafted_needs = meta.pop("predicateNeedsDrafted", [])
        record: dict[str, Any] = {"ref": ref, "observationId": passage["id"], **meta,
                                  "promptVersion": reader_prompt_version(inquiry)}
        if lookup_report is not None:
            record["graphLookup"] = lookup_report
        if output is None:
            record["error"] = "refusal or no parsed output"
            log.write(json.dumps(record) + "\n")
            print(f"{ref}: no output ({meta['stopReason']})")
            continue
        drafts, malformed = to_drafts(output, passage["id"], meta["model"], active_inquiry)
        if lookup_report is not None:
            try:
                drafts = [with_lookup_rationale(draft, lookup_report["selections"]) for draft in drafts]
            except ValidationError as error:
                record["error"] = f"candidate identification provenance could not be stored: {error}"
                log.write(json.dumps(record) + "\n")
                log.flush()
                raise
        totals["malformed"] += len(malformed)
        notes, refused_notes = to_notes(output, passage, passage_scope_ids)
        needs, refused_needs = to_predicate_needs(drafted_needs, passage)
        stored_notes: list[str] = []
        periods, refused_periods = to_periods(output, passage, inquiry)
        period_results: list[dict] = []
        events, refused_events = to_depicted(output, passage, active_inquiry, {e["id"] for e in known}, passage_scope_ids)
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
                        voice=inquiry.voice or edition.author, proposed_by=proposer(inquiry),
                        observation_id=passage["id"], quotation=event["quotation"])
                    if proposed["created"]:
                        known.append({"id": proposed["id"], "label": f"{event['label']} ({inquiry.voice or edition.author})"})
                scope_ids.add(event["id"])
                passage_scope_ids.add(event["id"])  # its own claims are checked against this passage's scope
                event_results.append({"id": event["id"], "new": event["new"]})
                event_drafts.extend(depicted_drafts(event, passage["id"], meta["model"], inquiry))
            for draft in drafts + event_drafts:
                named = {draft.subject_id, draft.object_id, draft.role_id, draft.context_id} - {None}
                outside = sorted(named - passage_scope_ids)
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
                                              proposed_by=proposer(inquiry), observation_id=passage["id"],
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
                    note_id = annotation_id(proposer(inquiry), passage["id"], note["note"], note["concerns"])
                    run_write(tx, operations, "upsert_annotation", {
                        "id": note_id, "kind": "passage-of-note",
                        "label": annotation_label(tx, kind="passage-of-note", note_type=note["noteType"],
                                                  observation_id=passage["id"]),
                        "noteType": note["noteType"], "note": note["note"], "author": proposer(inquiry),
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
        if inquiry.lens is not None:
            record["predicateNeeds"] = needs
            record["refusedPredicateNeeds"] = refused_needs
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
        if inquiry.lens is not None:
            totals["predicateNeeds"] = totals.get("predicateNeeds", 0) + len(needs)
            for need in needs:
                print(f"{ref}: predicate need {need['name']}: {need['definition'][:80]}")
        names = ", ".join(m.name for m in output.unresolved_mentions)
        print(f"{ref}: {len(drafts)} draft(s), {len(events)} event(s), {len(notes)} note(s); unresolved: {names or '-'}")
    return periodo


if __name__ == "__main__":
    raise SystemExit(main())
