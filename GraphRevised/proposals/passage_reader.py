"""LLM passage reader: proposes claims from one located passage.

    python -m GraphRevised.proposals.passage_reader --chapters 61-68 [--submit] [--model claude-opus-5-5]

The model only drafts. Every draft goes through the deterministic validator;
with --submit, valid drafts are stored as submitted Proposals for curator
review. A section's passage observation is persisted only when at least one
of its drafts is stored. Every run writes a JSONL log to GraphRevised/runs/.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic
from dotenv import dotenv_values
from neo4j import GraphDatabase
from pydantic import BaseModel, ValidationError

from GraphRevised.adapters.perseus_passages import Edition, load_edition, passage_observation, section_refs
from GraphRevised.operations import load_operations, run_write

from .registry import PredicateRegistry, load_registry
from .schema import ProposalDraft, Quotation
from .store import Neo4jReader, submit
from .validator import Outcome, validate

PROMPT_VERSION = "passage-reader-v2"
PROPOSER_ID = "passage-reader"
DEFAULT_MODEL = "claude-sonnet-5-5"
GRAPH_REVISED = Path(__file__).resolve().parents[1]
RUNS_DIRECTORY = GRAPH_REVISED / "runs"
EDITION_PATH = next((GRAPH_REVISED / "phase-5-source").glob("perseus-tlg0007.tlg058.perseus-eng2-*.xml"))
EDITION_COMMIT = EDITION_PATH.stem.rsplit("-", 1)[1]

SYSTEM_PROMPT = """\
You read one passage of a historical source and draft claims for a historical knowledge graph. \
You do not decide what is true: a deterministic validator checks every draft and a human curator \
accepts or rejects it. Drafting nothing is a correct result for many passages.

Rules:
1. Draft a claim only when the target passage itself states it or directly entails it. The \
surrounding sections are context for understanding the passage; they are not evidence. Use \
outside knowledge only to identify whom or what a name refers to, never to add facts.
2. Use only the predicates provided, respecting their subject and object kinds. If a relationship \
in the passage fits none of them, leave it out rather than stretching a predicate.
3. subject_id and object_id must be copied from the candidate entity list. Never invent an ID. \
Report any person, group, place, or event the passage mentions that is not in the list under \
unresolved_mentions, with the name as it appears in the passage.
4. quotation must be copied exactly, character for character, from the target passage: one \
contiguous span, at least 15 characters, the shortest span that supports the claim while \
still containing the words that name or refer to its subject and object when the sentence has \
them, so a reader of the quotation alone can see who is meant. Do not paraphrase, abridge, use \
ellipses, or quote the surrounding sections.
5. Names can need judgment: in Plutarch's Antony, "Caesar" in the Actium narrative denotes \
Octavian, not Julius Caesar. Explain how you identified each name in the rationale. Use \
ambiguities only when the identification remains genuinely uncertain; such claims are held for \
a human.
6. participatedIn requires that the passage connect the person or group to the event itself, for \
example by placing them in the battle's line or action.
"""


class ReaderClaim(BaseModel):
    predicate: str
    subject_id: str
    object_id: str
    quotation: str
    rationale: str
    ambiguities: list[str]


class UnresolvedMention(BaseModel):
    name: str
    quotation: str
    note: str


class ReaderOutput(BaseModel):
    claims: list[ReaderClaim]
    unresolved_mentions: list[UnresolvedMention]


def anthropic_client() -> anthropic.Anthropic:
    """Use ANTHROPIC_API_KEY from the environment, else only that key from .env.

    The rest of .env is deliberately not loaded: it holds legacy Neo4j
    settings that must not redirect the clean-start database connection.
    """
    key = os.environ.get("ANTHROPIC_API_KEY") or dotenv_values(GRAPH_REVISED.parent / ".env").get("ANTHROPIC_API_KEY")
    return anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic()


def predicate_guide(registry: PredicateRegistry) -> str:
    return "\n".join(
        f"- {d.id} ({d.display}): {'/'.join(sorted(d.subject_kinds))} -> {'/'.join(sorted(d.object_kinds))}"
        + (" [symmetric]" if d.symmetric else "")
        for d in registry.predicates.values()
    )


def read_passage(
    client: anthropic.Anthropic,
    model: str,
    edition: Edition,
    ref: str,
    passage: dict[str, Any],
    context: list[tuple[str, str]],
    entities: list[dict[str, Any]],
    registry: PredicateRegistry,
) -> tuple[ReaderOutput | None, dict[str, Any]]:
    entity_lines = "\n".join(
        f"- {e['id']} | {e['label']} | {e['kind']} | {e.get('description') or ''}" for e in entities
    )
    context_text = "\n\n".join(f"[{r}] {text}" for r, text in context)
    user = (
        f"Source: {edition.author}, {edition.title}, trans. {edition.translator} ({edition.citation}).\n\n"
        f"Predicates:\n{predicate_guide(registry)}\n\n"
        f"Candidate entities (id | label | kind | description):\n{entity_lines}\n\n"
        f"Surrounding sections (context only, not evidence):\n{context_text}\n\n"
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


def to_drafts(output: ReaderOutput, observation_id: str, model_id: str) -> tuple[list[ProposalDraft], list[dict]]:
    drafts, malformed = [], []
    for claim in output.claims:
        try:
            drafts.append(ProposalDraft(
                predicate=claim.predicate,
                subject_id=claim.subject_id,
                object_id=claim.object_id,
                observation_ids=(observation_id,),
                quotations=(Quotation(observation_id=observation_id, text=claim.quotation),),
                rationale=claim.rationale,
                proposed_by=PROPOSER_ID,
                prompt_version=PROMPT_VERSION,
                model_id=model_id,
                ambiguities=tuple(claim.ambiguities),
            ))
        except ValidationError as error:
            malformed.append({"claim": claim.model_dump(), "error": str(error)})
    return drafts, malformed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--chapters", default="61-68")
    parser.add_argument("--sections", help="comma-separated refs such as 65.1,65.2 (overrides --chapters)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--submit", action="store_true", help="store valid drafts as submitted Proposals")
    args = parser.parse_args(argv)

    first, last = (int(n) for n in args.chapters.split("-"))
    edition = load_edition(EDITION_PATH, source_commit=EDITION_COMMIT)
    refs = args.sections.split(",") if args.sections else section_refs(edition, range(first, last + 1))
    metadata = json.loads(EDITION_PATH.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    operations, registry, client = load_operations(), load_registry(), anthropic_client()

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
    )
    RUNS_DIRECTORY.mkdir(exist_ok=True)
    run_path = RUNS_DIRECTORY / f"passage-reader-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.jsonl"
    totals = {outcome.value: 0 for outcome in Outcome} | {"stored": 0, "malformed": 0, "inputTokens": 0, "outputTokens": 0}

    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session, \
                run_path.open("w", encoding="utf-8") as log:
            entities = session.execute_read(lambda tx: Neo4jReader(tx).entities())
            all_refs = section_refs(edition, range(1, 200))
            for ref in refs:
                passage = passage_observation(edition, ref, retrieved_at=metadata["retrievedAt"], source_uri=metadata["sourceUri"])
                index = all_refs.index(ref)
                context = [
                    (r, passage_observation(edition, r, retrieved_at="", source_uri="")["passageText"])
                    for r in all_refs[max(0, index - 2):index] + all_refs[index + 1:index + 2]
                ]
                output, meta = read_passage(client, args.model, edition, ref, passage, context, entities, registry)
                totals["inputTokens"] += meta["inputTokens"]
                totals["outputTokens"] += meta["outputTokens"]
                record: dict[str, Any] = {"ref": ref, "observationId": passage["id"], **meta, "promptVersion": PROMPT_VERSION}
                if output is None:
                    record["error"] = "refusal or no parsed output"
                    log.write(json.dumps(record) + "\n")
                    print(f"{ref}: no output ({meta['stopReason']})")
                    continue
                drafts, malformed = to_drafts(output, passage["id"], meta["model"])
                totals["malformed"] += len(malformed)

                # The observation is written first so drafts can be validated
                # against it; the transaction commits only if a draft was stored.
                tx = session.begin_transaction()
                try:
                    run_write(tx, operations, "upsert_passage_observation", passage)
                    results = []
                    for draft in drafts:
                        if args.submit:
                            submission = submit(tx, draft, registry, operations)
                            results.append((draft, submission.validation, submission.stored))
                        else:
                            results.append((draft, validate(draft, Neo4jReader(tx), registry), False))
                    if any(stored for _, _, stored in results):
                        tx.commit()
                    else:
                        tx.rollback()
                except BaseException:
                    tx.rollback()
                    raise

                record["drafts"] = [
                    {
                        "predicate": d.predicate, "subject": d.subject_id, "object": d.object_id,
                        "quotation": d.quotations[0].text, "rationale": d.rationale,
                        "ambiguities": list(d.ambiguities),
                        "outcome": v.outcome.value, "reasons": list(v.reasons),
                        "proposalId": v.proposal_id, "stored": stored,
                    }
                    for d, v, stored in results
                ]
                record["malformed"] = malformed
                record["unresolvedMentions"] = [m.model_dump() for m in output.unresolved_mentions]
                log.write(json.dumps(record, ensure_ascii=False) + "\n")
                for d, v, stored in results:
                    totals[v.outcome.value] += 1
                    totals["stored"] += stored
                    print(f"{ref}: {v.outcome.value:<13} {d.subject_id} {d.predicate} {d.object_id}"
                          + (" [stored]" if stored else "") + (f" -- {v.reasons[0]}" if v.reasons else ""))
                names = ", ".join(m.name for m in output.unresolved_mentions)
                print(f"{ref}: {len(drafts)} draft(s); unresolved: {names or '-'}")
    finally:
        driver.close()

    print(f"\nlog: {run_path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    print(json.dumps(totals))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
