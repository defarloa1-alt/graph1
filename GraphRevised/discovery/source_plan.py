"""Source discovery: a ranked plan of candidate sources for one inquiry.

    python -m GraphRevised.discovery.source_plan GraphRevised/inquiries/actium-plutarch-antony.json
        [--model claude-opus-5-5]

Three channels, combined:

1. citations inside passages already preserved for the inquiry's source
   ("as Caesar himself has written"), found deterministically;
2. candidate witnesses proposed by a model, each with a locator, approximate
   date, genre, relation to the event, and known dependencies; these are
   candidates for the curator, never facts;
3. a check of each candidate against the Scaife (Perseus) catalogue: which
   editions exist, in which languages.

The plan is a workflow artifact written to GraphRevised/plans/; it changes
nothing in the graph. A curator decides which works become entities and which
are read.
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

from GraphRevised.adapters.scaife_catalog import CatalogSnapshot, load_catalog
from GraphRevised.proposals.passage_reader import anthropic_client, load_inquiry
from GraphRevised.proposals.prompt_version import prompt_version

GRAPH_REVISED = Path(__file__).resolve().parents[1]
PLANS_DIRECTORY = GRAPH_REVISED / "plans"
CACHE_DIRECTORY = GRAPH_REVISED / "cache"
DEFAULT_MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = """\
You help plan source reading for a historical knowledge graph. Given an inquiry into one subject \
and the source already read, list the other primary witnesses to the subject: ancient or \
contemporary texts, and also inscriptions, coins, or monuments when they bear on it. A curator \
verifies every candidate; your list is a plan, not evidence.

Rules:
1. List only works you are confident treat the subject. Mark confidence honestly; leave a work out \
rather than guess.
2. locator: the book, chapter, poem, or lines where the subject is treated, as precisely as you \
reliably know it; otherwise "unknown". Never invent a locator.
3. cts_work_urn: the CTS work URN (for example urn:cts:latinLit:phi0893.phi001) only if you are \
sure of it; otherwise null.
4. composition_year: approximate year of composition, negative for BCE with no year zero \
(-31 = 31 BCE); null if unknown. composition: the same in words ("c. 30 BCE").
5. relation: contemporary (written by someone alive and active at the time), near-contemporary \
(within about two generations), or later.
6. depends_on: sources this work is known or widely believed to draw on, including lost ones. \
Say "likely" in the name when it is a scholarly inference.
7. Include lost works that later sources cite (for example a memoir cited in a passage) with \
genre "lost" and no locator.
8. coverage: one sentence on what the work contributes about the subject.
"""


class SourceCandidate(BaseModel):
    author: str
    work: str
    locator: str
    cts_work_urn: str | None
    composition: str
    composition_year: int | None
    genre: str
    relation: Literal["contemporary", "near-contemporary", "later"]
    depends_on: list[str]
    coverage: str
    confidence: Literal["high", "medium", "low"]


class SourcePlanOutput(BaseModel):
    candidates: list[SourceCandidate]
    notes: str


# Phrases by which a narrative cites another account, in English translation.
CITATION = re.compile(
    r"(?:as|according to)\s+(?P<who>[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)*)\s*(?:himself|herself)?\s*"
    r"(?P<verb>has written|had written|wrote|writes|says|said|tells us|records|relates)?",
)


def cited_sources(passages: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Places where a preserved passage cites another account."""
    found = []
    for passage in passages:
        for match in CITATION.finditer(passage["passageText"]):
            if match["verb"] or match.group(0).lower().startswith("according to"):
                start = max(0, match.start() - 80)
                found.append({
                    "locator": passage["locator"],
                    "who": match["who"],
                    "context": passage["passageText"][start:match.end() + 40].strip(),
                })
    return found


def check_catalog(candidate: SourceCandidate, catalog: CatalogSnapshot) -> dict[str, Any]:
    """What the catalogue confirms about a candidate's availability."""
    if candidate.cts_work_urn and candidate.cts_work_urn in catalog.works:
        return {
            "status": "work found",
            "workUrn": candidate.cts_work_urn,
            "workLabel": catalog.works[candidate.cts_work_urn],
            "languages": catalog.languages_of(candidate.cts_work_urn),
            "editions": catalog.editions_of(candidate.cts_work_urn),
        }
    authors = catalog.author_matches(candidate.author)
    author_works = {urn: label for urn, label in catalog.works.items() if any(urn.startswith(a + ".") for a in authors)}
    match = _title_match(candidate.work, author_works)
    if match:
        return {
            "status": "work matched by title (verify)",
            "workUrn": match,
            "workLabel": author_works[match],
            "languages": catalog.languages_of(match),
            "editions": catalog.editions_of(match),
        }
    status = "author found, work not matched" if authors else "not in catalogue"
    if candidate.cts_work_urn:
        status += f" (proposed URN {candidate.cts_work_urn} not found)"
    return {"status": status, "authorUrns": authors, "authorWorks": author_works}


def _stems(title: str) -> set[str]:
    """Four-letter word stems, so Latin and English title forms meet (Epodes, Epodon)."""
    return {word[:4].lower() for word in re.findall(r"[A-Za-z]+", title) if len(word) >= 4}


def _title_match(title: str, works: dict[str, str]) -> str | None:
    """The author's catalogued work sharing the most title stems, if exactly one does best."""
    scored = sorted(((len(_stems(title) & _stems(label)), urn) for urn, label in works.items()), reverse=True)
    if not scored or scored[0][0] == 0 or (len(scored) > 1 and scored[1][0] == scored[0][0]):
        return None
    return scored[0][1]


RELATION_ORDER = {"contemporary": 0, "near-contemporary": 1, "later": 2}


def rank(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Earliest and most direct witnesses first: relation, then composition year."""
    return sorted(candidates, key=lambda c: (
        RELATION_ORDER[c["relation"]], c["composition_year"] if c["composition_year"] is not None else 10**6,
    ))


def propose(client, model: str, inquiry, source_label: str, citations: list[dict[str, str]]) -> tuple[SourcePlanOutput | None, dict]:
    focus = "; ".join(f"{e['label']} ({e['kind']})" for e in inquiry.focus)
    user = (
        f"Inquiry: {inquiry.label}\nSubject: {inquiry.subject['label']}\nSubject focus: {focus}\n"
        f"Source already read: {source_label}\n\n"
        "Citations of other accounts found in the passages already read:\n"
        + ("\n".join(f"- [{c['locator']}] {c['context']}" for c in citations) or "- none")
        + "\n\nList the other primary witnesses to the subject focus."
    )
    response = client.beta.messages.parse(
        model=model, max_tokens=16000, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user}], output_format=SourcePlanOutput,
    )
    meta = {"model": response.model, "stopReason": response.stop_reason, "inputTokens": response.usage.input_tokens,
            "outputTokens": response.usage.output_tokens, "requestId": response._request_id}
    return (None if response.stop_reason == "refusal" else response.parsed_output), meta


PROMPT_VERSION = prompt_version("source-plan-v1", SYSTEM_PROMPT, propose)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inquiry", type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args(argv)

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            inquiry = session.execute_read(lambda tx: load_inquiry(args.inquiry, tx))
            source = session.run("MATCH (w:Entity {id: $id}) RETURN w.label AS label", id=inquiry.work_id).single()
            passages = session.run(
                "MATCH (o:SourceObservation)-[:IN_WORK]->(:Entity {id: $id}) "
                "RETURN o.locator AS locator, o.passageText AS passageText ORDER BY locator",
                id=inquiry.work_id,
            ).data()
    finally:
        driver.close()

    citations = cited_sources(passages)
    catalog = load_catalog(CACHE_DIRECTORY)
    output, meta = propose(anthropic_client(), args.model, inquiry, source["label"], citations)
    if output is None:
        print(f"no plan: {meta['stopReason']}")
        return 1

    candidates = rank([{**c.model_dump(), "catalog": check_catalog(c, catalog)} for c in output.candidates])
    plan = {
        "inquiry": inquiry.id, "inquiryVersion": inquiry.version, "sourceRead": inquiry.work_id,
        "createdAt": datetime.now(timezone.utc).isoformat(), "promptVersion": PROMPT_VERSION, **meta,
        "catalog": {"sourceUri": catalog.source_uri, "retrievedAt": catalog.retrieved_at,
                    "contentHash": catalog.content_hash},
        "citationsInSourceRead": citations, "candidates": candidates, "notes": output.notes,
    }
    PLANS_DIRECTORY.mkdir(exist_ok=True)
    stem = inquiry.id.rsplit(":", 1)[-1]
    path = PLANS_DIRECTORY / f"{stem}-sources-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    path.write_bytes((json.dumps(plan, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    for c in candidates:
        print(f"{c['relation']:<18} {c['composition']:<14} {c['author']}, {c['work']} [{c['locator']}] "
              f"({c['genre']}, {c['confidence']}) -> {c['catalog']['status']} {c['catalog'].get('languages', '')}")
    print(f"\ncitations in the source read: {len(citations)}")
    print(f"plan: {path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    print(json.dumps({k: meta[k] for k in ("model", "inputTokens", "outputTokens")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
