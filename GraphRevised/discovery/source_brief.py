"""The source-briefing agent: a source's reading conventions, written once per Work.

    python -m GraphRevised.discovery.source_brief GraphRevised/inquiries/actium-battle.json
        [--source <workId>] [--model claude-opus-5-5] [--budget 60000]

For each source of an inquiry, the agent reads the Work's record and a sample
of its passages (those naming the most in-scope entities, within a character
budget, plus the opening passages) and writes the conventions a reader needs
before drafting claims from it: what a name denotes in this source, invented
speeches, the author's stance, apparatus mixed into the text, dating habits.

Every convention must cite a sampled passage (or the Work's record) with an
exact quotation; the checks are deterministic, and a convention that fails one
is kept under `rejected` with the reason. The reader sees only the conventions'
words, never their evidence, and those words may not point at a passage or
quote the source (18 §20). Briefs are workflow files in GraphRevised/briefs/,
one per Work, replaced when the agent runs again; git keeps the history.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from neo4j import GraphDatabase
from pydantic import BaseModel

from GraphRevised.adapters.sources import PassageSource, open_source
from GraphRevised.proposals.passage_reader import Inquiry, anthropic_client, load_inquiries
from GraphRevised.proposals.prompt_version import prompt_version
from GraphRevised.proposals.reading_rules import BRIEFS_DIRECTORY, brief_path, load_reading_rules, normalize, steering

GRAPH_REVISED = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_BUDGET = 60000  # characters of sampled passage text
OPENING_PASSAGES = 3
METADATA_REF = "record"

SYSTEM_PROMPT = """\
You prepare a reader agent to draft claims from one historical source for a knowledge graph. \
You are given the source's record, the inquiry it is read for, the in-scope entities (with \
labels, aliases, and dates), the shared rules the reader already follows, and a sample of the \
source's passages. Write the source's reading conventions: what a careful reader must know about \
this source before drafting claims from it.

Conventions worth writing (only those this source actually shows):
- naming: a name that denotes a different person than an in-scope label or alias suggests, or \
an in-scope entity the source calls by another name, for the period the inquiry covers;
- speech: speeches, letters, or dialogue the author composes for characters, whose content is \
the author's rhetoric rather than narrative;
- stance: the author's position (an ancient or modern author, a biographer, an encyclopedia, \
an apologist or a critic) where it changes how a statement should be drafted, such as an \
author's reconstruction or inference presented in the narrative;
- apparatus: notes, markers, headings, or editorial matter mixed into the passage text;
- dating: how the source gives times or dates, where that differs from plain statement;
- other: anything else that would make a careful reader draft differently.

Rules:
1. Each convention is one or two plain sentences addressed to the reader, as an instruction.
2. Never state facts about the subject or the inquiry's event, and never tell the reader where \
in the source to look, not even loosely ("in the early chapters", "in the closing pages"). Never \
give a locator (chapter, section, page), never use quotation marks in a rule, and never copy two or \
more consecutive words of the source into it; describe names, phrases, and habits in your own words \
(for example "hedged phrases of possibility" rather than the phrases themselves). A single name or \
spelling may be given without quotation marks.
3. A naming convention says how a name is used where the sample shows it; where the sample shows a \
name used in more than one way, say so and tell the reader to decide from context, rather than \
generalising from one use.
4. Do not repeat the shared rules.
5. Every convention cites evidence: one or more sampled passages by their ref, each with an exact \
quotation copied character for character from that passage, at least 15 characters, showing the \
convention. For a stance shown by the source's record, cite ref "record" with a quotation from it.
6. Write nothing you cannot show from the sample. Fewer conventions are better than doubtful ones; \
none is a valid result.
"""


class Evidence(BaseModel):
    ref: str
    quotation: str


class Convention(BaseModel):
    kind: Literal["naming", "speech", "stance", "apparatus", "dating", "other"]
    rule: str
    why: str
    evidence: list[Evidence]


class BriefOutput(BaseModel):
    conventions: list[Convention]
    notes: str


def scope_names(inquiry: Inquiry) -> dict[str, set[str]]:
    """Searchable names per in-scope entity: its label's words of five letters or more, and its aliases."""
    names: dict[str, set[str]] = {}
    for entity in inquiry.scope + inquiry.focus:
        words = {w for w in re.findall(r"[A-Za-z]{5,}", entity["label"])}
        names[entity["id"]] = {w.lower() for w in words} | {a.lower() for a in entity.get("aliases", []) if len(a) >= 5}
    return names


def sample_passages(source: PassageSource, inquiry: Inquiry, budget: int) -> list[tuple[str, str]]:
    """The opening passages, then those naming the most in-scope entities, within the budget, in document order."""
    refs = source.refs(None)
    texts = {ref: source.observation(ref)["passageText"] for ref in refs}
    names = scope_names(inquiry)

    def score(ref: str) -> int:
        text = texts[ref].lower()
        return sum(1 for terms in names.values() if any(re.search(rf"\b{re.escape(t)}\b", text) for t in terms))

    chosen = list(refs[:OPENING_PASSAGES])
    used = sum(len(texts[r]) for r in chosen)
    for ref in sorted(refs[OPENING_PASSAGES:], key=lambda r: (-score(r), refs.index(r))):
        if score(ref) == 0 or used + len(texts[ref]) > budget:
            continue
        chosen.append(ref)
        used += len(texts[ref])
    return [(ref, texts[ref]) for ref in refs if ref in set(chosen)]


def record_text(source: PassageSource, work: dict[str, Any]) -> str:
    return "\n".join(filter(None, [
        f"Work: {work['label']}", f"Form: {work.get('form') or 'unknown'}", work.get("description"),
        f"Edition: {source.author}, {source.title}" + (f", trans. {source.translator}" if source.translator else ""),
        f"Citation: {source.citation}",
    ]))


def check(output: BriefOutput, sample: list[tuple[str, str]], record: str, source_text: str) -> tuple[list, list]:
    """Conventions whose evidence is verbatim and whose words do not steer; the rest with the reason."""
    passages = {ref: normalize(text) for ref, text in sample} | {METADATA_REF: normalize(record)}
    kept, rejected = [], []
    for convention in output.conventions:
        entry = convention.model_dump()
        reason = steering(convention.rule, source_text)
        if reason is None:
            bad = [e.ref for e in convention.evidence
                   if len(e.quotation) < 15 or e.ref not in passages or normalize(e.quotation) not in passages[e.ref]]
            if not convention.evidence:
                reason = "no evidence"
            elif bad:
                reason = f"evidence not found verbatim: {bad}"
        if reason:
            rejected.append({**entry, "reason": reason})
        else:
            kept.append(entry)
    return kept, rejected


def propose(client, model: str, inquiry: Inquiry, record: str, shared: list[str],
            sample: list[tuple[str, str]]) -> tuple[BriefOutput | None, dict]:
    def entity_line(e: dict[str, Any]) -> str:
        line = f"- {e['label']} ({e['kind']}): {e.get('description') or ''}"
        if e.get("aliases"):
            line += f" | aliases: {'; '.join(e['aliases'])}"
        if e.get("dates"):
            line += " | " + ", ".join(f"{k} {v}" for k, v in e["dates"].items())
        return line

    user = (
        f"Source record:\n{record}\n\n"
        f"Inquiry: {inquiry.label}\nSubject: {inquiry.subject['label']}\n\n"
        "In-scope entities:\n" + "\n".join(entity_line(e) for e in inquiry.focus + inquiry.scope) + "\n\n"
        "Shared rules the reader already follows:\n" + "\n".join(f"- {line}" for line in shared) + "\n\n"
        "Sampled passages:\n" + "\n\n".join(f"[{ref}] {text}" for ref, text in sample)
    )
    response = client.beta.messages.parse(
        model=model, max_tokens=8000, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}], output_format=BriefOutput,
    )
    meta = {"model": response.model, "stopReason": response.stop_reason, "inputTokens": response.usage.input_tokens,
            "outputTokens": response.usage.output_tokens, "requestId": response._request_id}
    return (None if response.stop_reason == "refusal" else response.parsed_output), meta


PROMPT_VERSION = prompt_version("source-brief-v2", SYSTEM_PROMPT, propose, sample_passages, check)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inquiry", type=Path)
    parser.add_argument("--source", help="brief only the source with this workId")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET, help="characters of passage text to sample")
    args = parser.parse_args(argv)

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            inquiries = session.execute_read(lambda tx: load_inquiries(args.inquiry, tx, briefs=None))
            works = {i.work_id: session.run("MATCH (w:Entity {id: $id}) RETURN w {.label, .form, .description} AS w",
                                            id=i.work_id).single()["w"] for i in inquiries}
    finally:
        driver.close()

    rules = load_reading_rules()
    client = anthropic_client()
    BRIEFS_DIRECTORY.mkdir(exist_ok=True)
    for inquiry in inquiries:
        if args.source and inquiry.work_id != args.source:
            continue
        source = open_source(inquiry.source, GRAPH_REVISED)
        record = record_text(source, works[inquiry.work_id])
        sample = sample_passages(source, inquiry, args.budget)
        source_text = normalize(" ".join(source.observation(ref)["passageText"] for ref in source.refs(None)))
        output, meta = propose(client, args.model, inquiry, record, inquiry.guidance, sample)
        if output is None:
            print(f"{inquiry.work_id}: no brief ({meta['stopReason']})")
            continue
        kept, rejected = check(output, sample, record, source_text)
        brief = {
            "workId": inquiry.work_id, "inquiry": inquiry.id, "inquiryVersion": inquiry.version,
            "createdAt": datetime.now(timezone.utc).isoformat(), "promptVersion": PROMPT_VERSION,
            "readingRulesVersion": rules.version, **meta,
            "sample": {"refs": [ref for ref, _ in sample], "characters": sum(len(t) for _, t in sample),
                       "budget": args.budget},
            "conventions": kept, "rejected": rejected, "notes": output.notes,
        }
        path = brief_path(inquiry.work_id)
        path.write_bytes((json.dumps(brief, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"\n{inquiry.work_id}: {len(kept)} conventions, {len(rejected)} rejected "
              f"({meta['inputTokens']} in, {meta['outputTokens']} out) -> {path.relative_to(GRAPH_REVISED.parent).as_posix()}")
        for c in kept:
            print(f"  [{c['kind']}] {c['rule']}")
        for c in rejected:
            print(f"  REJECTED ({c['reason']}): {c['rule']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
