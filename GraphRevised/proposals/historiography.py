"""The historiography section of a lens reading (44-HISTORIOGRAPHY-AND-DEBATES.md, D-153).

A lens reading of a modern work (a Work of standing secondary) also reports how historians have
thought about the subject: the questions the work treats, the positions it describes, which works
it says held or rejected each and when, on which passages, how each position was received, and
the work's own position. This module holds that section of the prompt, the shape of its output,
and the conversion of that output into proposals. It names no source and no subject.

Every link it drafts is attributed to the Work being read: the work's own position is its own
claim; a holder it reports (a scholar of 1899 held it) is its report, until the holder is read. A holder
is a Work: one the inquiry already holds, by id, or one the passage names, listed as unresolved
for the curator (a cited work is seeded as a Work by code, D-145, never invented by the model).

Licensed texts (13d): the page is read where it lies and never stored. Each draft cites a
transcription, the shortest span of the page that holds all of the draft's quotations, checked
verbatim against the page here, and kept short (MAX_SPAN) with the page as its locator.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from .entities import proposed_entity_id
from .schema import ProposalDraft, QualifierQuotation, Quotation, TimeQualifier

HISTORIOGRAPHY_PREDICATES = ("about", "answers", "holds", "rejects", "hadReception")
STANCES = ("originates", "adopts", "modifies")
RECEPTIONS = ("dominant", "contested", "minority", "abandoned")
MAX_SPAN = 600  # characters of a licensed page kept as one transcription

# Added to the system prompt only when the reading includes historiography.
HISTORIOGRAPHY_RULES = """\
18. Historiography. This source is modern scholarship. Besides the lens's claims, report how \
historians have thought about the subject, under historiography, as this source describes it. \
A question is one scholars answer differently ("What did the defeated commander intend in the battle?"), never a \
question of fact the sources agree on; give its wording, the in-scope entities it is about \
(events, people, groups), and the quotation that raises it, or existing_id when it is already \
listed. A position is one answer to a question, in at most twelve words, shared by everyone who \
holds it; reuse a listed position by existing_id rather than restating it. A holding says that \
a work holds or rejects a position: holder_id is an in-scope Work when the holder is one; \
otherwise holder_id is empty and holder_name is the name as the passage gives it (an author, or \
author and year), with holder_year only when the passage states the year. Ancient authors are \
holders too: an ancient historian holds a view as a modern scholar does. own is true only for this source's own \
position. stance, only when the passage says so: originates (the first to argue it), adopts, or \
modifies, with stance_quotation copied exactly. time (when the holder argued it) follows rule 9. \
rests_on lists the passages the holder relies on, exactly as cited ("Hist. 5.12"). A reception \
says how a position stood in scholarship over a span, only as the passage says it: dominant, \
contested, minority, or abandoned, with the quotation and the span's time (rule 9). Every \
quotation follows rule 5. Never judge a position yourself, never count its holders as evidence, \
and report nothing the passage does not say.
"""


class ReaderQuestion(BaseModel):
    key: str
    question: str
    existing_id: str
    about_ids: list[str]
    quotation: str


class ReaderPosition(BaseModel):
    key: str
    label: str
    existing_id: str
    question: str  # a question key or an existing Question id
    quotation: str


class ReaderHolding(BaseModel):
    position: str  # a position key or an existing Position id
    verb: str  # holds or rejects
    holder_id: str
    holder_name: str
    holder_year: str
    own: bool
    quotation: str
    stance: str
    stance_quotation: str
    time_source_expression: str
    time_quotation: str
    time_edtf: str
    rests_on: list[str]


class ReaderReception(BaseModel):
    position: str
    reception: str
    quotation: str
    time_source_expression: str
    time_quotation: str
    time_edtf: str


class HistoriographyOutput(BaseModel):
    questions: list[ReaderQuestion]
    positions: list[ReaderPosition]
    holdings: list[ReaderHolding]
    receptions: list[ReaderReception]


def historiography_text(questions: list[dict[str, Any]], positions: list[dict[str, Any]],
                        holders: list[dict[str, Any]]) -> str:
    """The packet block: the Questions and Positions already in the graph, and the Works that may
    be holders. The same for every passage of a run, so cached."""
    return "\n".join([
        "Historiography (rule 18). Questions already listed (id | question):",
        *([f"- {q['id']} | {q['label']}" for q in questions] or ["- none yet"]),
        "Positions already listed (id | position | question id):",
        *([f"- {p['id']} | {p['label']} | {p.get('questionId') or 'no question yet'}" for p in positions]
          or ["- none yet"]),
        "Works that may be holders (id | label):",
        *([f"- {w['id']} | {w['label']}" for w in holders] or ["- none yet"]),
    ])


def transcription_id(work_id: str, locator: str, text: str) -> str:
    """As capture.core.transcription_id: the same span of the same page is one observation."""
    digest = hashlib.sha256(f"{locator}\n{text}".encode("utf-8")).hexdigest()[:12]
    return f"chr:observation:transcription:{work_id.split(':', 2)[2]}:{digest}"


@dataclass
class HistoriographyPlan:
    """What a reading's historiography section would write: nothing is written here."""
    entities: list[dict[str, Any]] = field(default_factory=list)  # proposed Questions and Positions
    transcriptions: list[dict[str, Any]] = field(default_factory=list)
    drafts: list[ProposalDraft] = field(default_factory=list)
    unresolved_holders: list[dict[str, Any]] = field(default_factory=list)
    refused: list[dict[str, Any]] = field(default_factory=list)


def span_of(page: str, quotes: list[str]) -> tuple[str | None, str | None]:
    """The shortest stretch of the page holding every quotation, or the reason there is none."""
    places = []
    for quote in quotes:
        start = page.find(quote)
        if start < 0:
            return None, f"quotation does not appear verbatim on the page: {quote[:60]!r}"
        places.append((start, start + len(quote)))
    span = page[min(s for s, _ in places):max(e for _, e in places)]
    if len(span) > MAX_SPAN:
        return None, f"the quotations span {len(span)} characters of the page; at most {MAX_SPAN} are kept"
    return span, None


def to_historiography(output: HistoriographyOutput, page: str, *, work_id: str, locator: str,
                      scope_ids: set[str], work_ids: set[str], proposed_by: str, model_id: str | None,
                      prompt_version: str | None, inquiry_id: str | None, calendar: str = "gregorian",
                      existing: set[str] = frozenset()) -> HistoriographyPlan:
    """Turn one page's historiography into proposed entities and drafts attributed to `work_id`.

    `page` is the page's text as read (never stored); `locator` its page ("p. 608"); `scope_ids`
    the in-scope entities a question may be about; `work_ids` the Works a holder may be;
    `existing` the Question and Position ids already in the graph."""
    plan = HistoriographyPlan()
    page = " ".join(page.split())
    keys: dict[str, str] = {}  # a question or position key -> its entity id

    def evidence(quotes: list[tuple[str | None, str]]) -> tuple[str, list[Quotation], list[QualifierQuotation]] | None:
        """One transcription for the draft, with its main quotation and its qualifier quotations."""
        texts = [" ".join(text.split()) for _, text in quotes if text]
        span, reason = span_of(page, texts)
        if span is None:
            raise ValueError(reason)
        observation = transcription_id(work_id, locator, span)
        if observation not in {t["id"] for t in plan.transcriptions}:
            plan.transcriptions.append({"id": observation, "workId": work_id, "locator": locator, "quote": span})
        main = [Quotation(observation_id=observation, text=span)]
        qualifiers = [QualifierQuotation(observation_id=observation, supports=supports, text=" ".join(text.split()))
                      for supports, text in quotes if supports and text]
        return observation, main, qualifiers

    def draft(predicate: str, subject: str, obj: str | None, quotes: list[tuple[str | None, str]],
              rationale: str, **extra: Any) -> None:
        try:
            observation, main, qualifiers = evidence(quotes)
            plan.drafts.append(ProposalDraft(
                predicate=predicate, subject_id=subject, object_id=obj, observation_ids=(observation,),
                quotations=tuple(main), qualifier_quotations=tuple(qualifiers), rationale=rationale,
                proposed_by=proposed_by, model_id=model_id, prompt_version=prompt_version,
                inquiry_id=inquiry_id, mode="attributed", attributed_to=work_id, **extra))
        except ValueError as error:
            plan.refused.append({"predicate": predicate, "subject": subject, "object": obj, "reason": str(error)})

    def entity(kind: str, label: str, existing_id: str, key: str, quotation: str) -> str | None:
        if existing_id:
            if existing_id not in existing:
                plan.refused.append({"key": key, "reason": f"{existing_id} is not a listed {kind}"})
                return None
            keys[key] = existing_id
            return existing_id
        id_ = proposed_entity_id(kind, label)
        if id_ not in {e["id"] for e in plan.entities}:
            try:
                observation, main, _ = evidence([(None, quotation)])
            except ValueError as error:
                plan.refused.append({"key": key, "reason": str(error)})
                return None
            plan.entities.append({"id": id_, "kind": kind, "label": label, "observationId": observation,
                                  "quotation": main[0].text})
        keys[key] = id_
        return id_

    def time(source: str, edtf: str) -> TimeQualifier | None:
        if not source:
            return None
        if edtf:
            return TimeQualifier(source_expression=source, edtf=edtf, calendar=calendar, normalization_basis="source")
        return TimeQualifier(source_expression=source)

    for q in output.questions:
        question = entity("Question", q.question.strip(), q.existing_id, q.key, q.quotation)
        if question is None:
            continue
        for about in q.about_ids:
            if about not in scope_ids:
                plan.refused.append({"key": q.key, "reason": f"{about} is not in scope"})
                continue
            draft("about", question, about, [(None, q.quotation)],
                  f"The source raises the question “{q.question.strip()}” about this entity.")

    for p in output.positions:
        position = entity("Position", p.label.strip(), p.existing_id, p.key, p.quotation)
        question = keys.get(p.question) or (p.question if p.question in existing else None)
        if position is None:
            continue
        if question is None:
            plan.refused.append({"key": p.key, "reason": f"answers an unknown question {p.question!r}"})
            continue
        draft("answers", position, question, [(None, p.quotation)],
              f"The source gives “{p.label.strip()}” as one answer to the question.")

    for h in output.holdings:
        position = keys.get(h.position) or (h.position if h.position in existing else None)
        if h.verb not in ("holds", "rejects") or position is None:
            plan.refused.append({"holding": h.model_dump(), "reason": "an unknown verb or position"})
            continue
        holder = work_id if h.own else h.holder_id
        if not holder:
            plan.unresolved_holders.append({"name": h.holder_name, "year": h.holder_year, "verb": h.verb,
                                            "position": position, "quotation": h.quotation,
                                            "restsOn": h.rests_on, "locator": locator})
            continue
        if holder not in work_ids:
            plan.refused.append({"holding": h.model_dump(), "reason": f"{holder} is not a Work in scope"})
            continue
        stance = h.stance if h.verb == "holds" and h.stance in STANCES else None
        quotes = [(None, h.quotation)]
        if stance:
            quotes.append(("stance", h.stance_quotation))
        when = time(h.time_source_expression, h.time_edtf)
        if when:
            quotes.append(("time", h.time_quotation))
        who = "its own position" if h.own else f"{h.holder_name or holder} {h.verb} it, as this source reports"
        rests = f" Rests on: {', '.join(h.rests_on)}." if h.rests_on else ""
        draft(h.verb, holder, position, quotes, f"The source says {who}.{rests}", stance=stance, time=when)

    for r in output.receptions:
        position = keys.get(r.position) or (r.position if r.position in existing else None)
        if position is None or r.reception not in RECEPTIONS:
            plan.refused.append({"reception": r.model_dump(), "reason": "an unknown position or reception"})
            continue
        when = time(r.time_source_expression, r.time_edtf)
        quotes = [(None, r.quotation), ("reception", r.quotation)] + ([("time", r.time_quotation)] if when else [])
        draft("hadReception", position, None, quotes,
              f"The source describes the position as {r.reception} over this span.", reception=r.reception, time=when)
    return plan


# --- Storing (in the caller's transaction) -------------------------------------------------------

RIGHTS = "Short quotation of a work in copyright, kept for study; the page itself is not stored (13d)."


def store_historiography(tx: Any, operations: dict[str, str], registry: Any, plan: HistoriographyPlan, *,
                         work_label: str, edition_citation: str, proposed_by: str, at: str,
                         submit_drafts: bool = True) -> dict[str, Any]:
    """Write a plan: its transcriptions, its Questions and Positions (proposed, or an existing entity
    of the same name and kind reused), and its drafts, validated and stored as Proposals. Agents never
    accept: everything stays proposed for the curator. With submit_drafts False the drafts are only
    validated. Returns what was stored and each draft's outcome."""
    from GraphRevised.operations import run_write

    from .entities import propose_entity
    from .store import Neo4jReader, submit
    from .validator import validate

    for item in plan.transcriptions:
        run_write(tx, operations, "upsert_transcription_observation", {
            "id": item["id"], "workId": item["workId"],
            "label": f"{work_label}, {item['locator']} (transcription)",
            "shortLabel": f"{work_label} {item['locator']}", "sourceSystem": "licensed-pdf",
            "locator": item["locator"], "locatorType": "page", "passageText": item["quote"],
            "passageHash": hashlib.sha256(item["quote"].encode("utf-8")).hexdigest(), "language": "en",
            "workTitle": work_label, "author": None, "editionCitation": edition_citation, "rights": RIGHTS,
            "visibility": "private", "capturedBy": proposed_by, "capturedAt": at,
            "contentHash": hashlib.sha256(item["quote"].encode("utf-8")).hexdigest(), "rawPayloadUri": None,
        })
    ids: dict[str, str] = {}
    entities = []
    for item in plan.entities:
        proposed = propose_entity(tx, operations, kind=item["kind"], label=item["label"], proposed_by=proposed_by,
                                  observation_id=item["observationId"], quotation=item["quotation"],
                                  source=edition_citation)
        ids[item["id"]] = proposed["id"]
        entities.append({"kind": item["kind"], "label": item["label"], "id": proposed["id"],
                         "created": proposed["created"], "candidates": [c["id"] for c in proposed["candidates"]]})
    results = []
    for draft in plan.drafts:
        draft = draft.model_copy(update={"subject_id": ids.get(draft.subject_id, draft.subject_id),
                                         "object_id": ids.get(draft.object_id, draft.object_id)})
        if submit_drafts:
            submission = submit(tx, draft, registry, operations)
            outcome, reasons, stored = submission.validation.outcome.value, submission.validation.reasons, \
                submission.stored
        else:
            checked = validate(draft, Neo4jReader(tx), registry)
            outcome, reasons, stored = checked.outcome.value, checked.reasons, False
        results.append({"predicate": draft.predicate, "subject": draft.subject_id, "object": draft.object_id,
                        "stance": draft.stance, "reception": draft.reception,
                        "time": draft.time.source_expression if draft.time else None,
                        "outcome": outcome, "reasons": list(reasons), "stored": stored})
    return {"transcriptions": len(plan.transcriptions), "entities": entities, "drafts": results}
