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
from GraphRevised.operations import load_operations, run_write

from .prompt_version import prompt_version
from .registry import PredicateRegistry, load_registry
from .schema import DRAFT_SCHEMA_VERSION, ProposalDraft, QualifierQuotation, Quotation, TimeQualifier
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
years astronomically: 1 BCE is 0000 and 31 BCE is -0030, so 2 September 31 BCE is -0030-09-02. A \
predicate's list entry says which qualifiers it takes; a claim that needs a qualifier the passage \
does not give is still drafted without it, and is held for later.
10. For predicates that take a context, set context_id to the inquiry's narrative event when the \
claim happens within it. If the passage names the event, also copy that span as context_quotation.
11. A predicate marked "no object" takes no object_id: leave it null.
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


class ReaderOutput(BaseModel):
    claims: list[ReaderClaim]
    unresolved_mentions: list[UnresolvedMention]


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

    user = (
        f"Inquiry: {inquiry.label}\n"
        f"Subject: {inquiry.subject['label']}\n"
        f"Subject focus:\n" + "\n".join(entity_line(e) for e in inquiry.focus) + "\n\n"
        f"Inquiry guidance:\n" + "\n".join(f"- {line}" for line in inquiry.guidance) + "\n\n"
        f"Source: {edition.author}, {edition.title}, trans. {edition.translator} ({edition.citation}).\n"
        f"Narrative event: {inquiry.narrative_event_id or 'none declared'}\n\n"
        f"Predicates:\n{predicate_guide(registry)}\n\n"
        f"In-scope entities (id | label | kind | description):\n"
        + "\n".join(entity_line(e) for e in inquiry.scope) + "\n\n"
        f"Surrounding sections (context only, not evidence):\n"
        + "\n\n".join(f"[{r}] {text}" for r, text in context) + "\n\n"
        f"Target passage [{ref}]:\n{passage['passageText']}"
    )
    response = client.beta.messages.parse(
        model=model,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        extra_body={"fallbacks": "default"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}],
        output_format=ReaderOutput,
    )
    meta = {
        "model": response.model,
        "stopReason": response.stop_reason,
        "inputTokens": response.usage.input_tokens,
        "outputTokens": response.usage.output_tokens,
        "requestId": response._request_id,
    }
    if response.stop_reason == "refusal":
        return None, meta
    return response.parsed_output, meta


PROMPT_VERSION = prompt_version("passage-reader-v8", SYSTEM_PROMPT, predicate_guide, read_passage)


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
        time = TimeQualifier(
            source_expression=claim.time_source_expression,
            edtf=claim.time_edtf,
            calendar="julian" if claim.time_edtf else None,
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
    args = parser.parse_args(argv)

    operations, registry, client = load_operations(), load_registry(), anthropic_client()
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    RUNS_DIRECTORY.mkdir(exist_ok=True)
    run_path = RUNS_DIRECTORY / f"passage-reader-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.jsonl"
    totals: dict[str, int] = {"stored": 0, "malformed": 0, "inputTokens": 0, "outputTokens": 0}

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
                    for r in all_refs[max(0, index - 2):index] + all_refs[index + 1:index + 2]
                ]
                output, meta = read_passage(client, args.model, inquiry, edition, ref, passage, context, registry)
                totals["inputTokens"] += meta["inputTokens"]
                totals["outputTokens"] += meta["outputTokens"]
                record: dict[str, Any] = {"ref": ref, "observationId": passage["id"], **meta, "promptVersion": PROMPT_VERSION}
                if output is None:
                    record["error"] = "refusal or no parsed output"
                    log.write(json.dumps(record) + "\n")
                    print(f"{ref}: no output ({meta['stopReason']})")
                    continue
                drafts, malformed = to_drafts(output, passage["id"], meta["model"], inquiry)
                totals["malformed"] += len(malformed)

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
                            results.append((draft, v.outcome.value, list(v.reasons), v.proposal_id, submission.stored))
                        else:
                            v = validate(draft, Neo4jReader(tx), registry)
                            results.append((draft, v.outcome.value, list(v.reasons), v.proposal_id, False))
                    if any(stored for *_, stored in results):
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
                record["unresolvedMentions"] = [m.model_dump() for m in output.unresolved_mentions]
                log.write(json.dumps(record, ensure_ascii=False) + "\n")
                for d, outcome, reasons, _, stored in results:
                    totals[outcome] = totals.get(outcome, 0) + 1
                    totals["stored"] += stored
                    print(f"{ref}: {outcome:<13} {d.subject_id} {d.predicate} {d.object_id}"
                          + (" [stored]" if stored else "") + (f" -- {reasons[0]}" if reasons else ""))
                names = ", ".join(m.name for m in output.unresolved_mentions)
                print(f"{ref}: {len(drafts)} draft(s); unresolved: {names or '-'}")
    finally:
        driver.close()

    print(f"\nlog: {run_path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    print(json.dumps(totals))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
