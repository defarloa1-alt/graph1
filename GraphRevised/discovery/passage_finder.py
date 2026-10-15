"""The passage finder: which passages of a whole work the reader should read for an event inquiry.

    python -m GraphRevised.discovery.passage_finder GraphRevised/inquiries/actium-battle.json
        [--source <workId>] [--model claude-haiku-5-5] [--batch 20]

Inquiries name whole works (18 §20) and the reader finds passages itself; for
a long work most passages say nothing about the event. Two steps, both
recorded, before the reader runs with --found:

1. a name match, without a model: a passage is a candidate when it names the
   event (a word of the event's label, or its adjective: Pharsalus, Pharsalian), or at
   least two different in-scope people or forces (labels and aliases);
2. a small model's verdict on each candidate, in batches: does it bear on the
   event (its lead-up, the action, its end, its aftermath, its place, or an
   author's reading of it)? When unsure, keep it; the reader decides what to draft.

A passage the model does not return is kept. The finds are workflow files in
GraphRevised/finds/, one per inquiry source; the reader records which it used.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase
from pydantic import BaseModel

from GraphRevised.adapters.sources import PassageSource, open_source
from GraphRevised.proposals.passage_reader import Inquiry, anthropic_client, load_inquiries
from GraphRevised.proposals.prompt_version import prompt_version

GRAPH_REVISED = Path(__file__).resolve().parents[1]
FINDS_DIRECTORY = GRAPH_REVISED / "finds"
DEFAULT_MODEL = "claude-haiku-5-5"
DEFAULT_BATCH = 20
ACTOR_KINDS = {"Person", "Group"}

SYSTEM_PROMPT = """\
You screen passages of a historical source for a reader agent that will draft claims about one \
event. For each passage, say whether it bears on the event: it narrates the event or a step of it, \
its lead-up or its end as the passage ties them to it, its aftermath or commemoration, a \
participant's part in it, the place where it happened, or an author's reading of what it meant. A \
passage that mentions the same people in an unrelated matter does not bear on it. When you are \
unsure, answer relevant: the reader makes the final judgement, and a missed passage is lost. \
Return one verdict for every passage, with its ref exactly as given and a reason of a few words.
"""


class Verdict(BaseModel):
    ref: str
    relevant: bool
    why: str


class FinderOutput(BaseModel):
    verdicts: list[Verdict]


def event_terms(label: str) -> list[re.Pattern]:
    """Patterns for the event's own name: each capitalised word of five letters or more in its label
    (Pharsalus), and its adjectives formed on the same stem (Pharsalian)."""
    words = [w for w in re.findall(r"[A-Z][a-z]{4,}", label) if w.lower() not in {"battle", "siege", "treaty"}]
    return [re.compile(rf"\b{re.escape(w[:-2])}[a-z]{{1,4}}\b") for w in words]


def actor_terms(inquiry: Inquiry) -> dict[str, list[re.Pattern]]:
    """Patterns per in-scope person or force: its label's capitalised words of five letters or more, and its aliases."""
    terms: dict[str, list[re.Pattern]] = {}
    for entity in inquiry.scope:
        if entity["kind"] not in ACTOR_KINDS or entity["id"].startswith("chr:entity:depicted:"):
            continue
        names = [w for w in re.findall(r"[A-Z][a-z]{4,}", entity["label"])]
        names += [a for a in entity.get("aliases", []) if len(a) >= 5]
        if names:
            terms[entity["id"]] = [re.compile(rf"\b{re.escape(n)}\b") for n in dict.fromkeys(names)]
    return terms


def name_candidates(texts: dict[str, str], event: list[re.Pattern], actors: dict[str, list[re.Pattern]]) -> dict[str, str]:
    """Refs that name the event or two different in-scope actors, with why; and the passages on either
    side of one that names the event, since a scene often names its event once (a poem's battle scene)."""
    found = {}
    for ref, text in texts.items():
        if any(p.search(text) for p in event):
            found[ref] = "names the event"
            continue
        named = [entity for entity, patterns in actors.items() if any(p.search(text) for p in patterns)]
        if len(named) >= 2:
            found[ref] = f"names {len(named)} in-scope actors"
    refs = list(texts)
    for index, ref in enumerate(refs):
        if found.get(ref) == "names the event":
            for neighbour in refs[max(0, index - 1):index] + refs[index + 1:index + 2]:
                found.setdefault(neighbour, "next to a passage naming the event")
    return found


def screen(client, model: str, event: dict[str, Any], batch: list[tuple[str, str]]) -> tuple[FinderOutput | None, dict]:
    user = (f"Event: {event['label']} ({event.get('description') or ''})\n\nPassages:\n"
            + "\n\n".join(f"[{ref}] {text}" for ref, text in batch))
    response = client.beta.messages.parse(model=model, max_tokens=8000, system=SYSTEM_PROMPT,
                                          messages=[{"role": "user", "content": user}], output_format=FinderOutput)
    meta = {"model": response.model, "stopReason": response.stop_reason, "inputTokens": response.usage.input_tokens,
            "outputTokens": response.usage.output_tokens}
    return (None if response.stop_reason == "refusal" else response.parsed_output), meta


PROMPT_VERSION = prompt_version("passage-finder-v1", SYSTEM_PROMPT, screen, event_terms, actor_terms, name_candidates)


def finds_path(inquiry_id: str, work_id: str, directory: Path = FINDS_DIRECTORY) -> Path:
    return directory / f"{inquiry_id.rsplit(':', 1)[-1]}--{work_id.rsplit(':', 1)[-1]}.json"


def load_finds(inquiry_id: str, work_id: str, directory: Path = FINDS_DIRECTORY) -> dict[str, Any] | None:
    path = finds_path(inquiry_id, work_id, directory)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def find(client, model: str, inquiry: Inquiry, source: PassageSource, event: dict[str, Any], batch_size: int) -> dict[str, Any]:
    refs = source.refs(None)
    texts = {ref: source.observation(ref)["passageText"] for ref in refs}
    candidates = name_candidates(texts, event_terms(event["label"]), actor_terms(inquiry))
    verdicts: dict[str, dict[str, Any]] = {}
    usage = {"inputTokens": 0, "outputTokens": 0, "calls": 0}
    batches = []
    ordered = [ref for ref in refs if ref in candidates]
    for start in range(0, len(ordered), batch_size):
        batch = [(ref, texts[ref]) for ref in ordered[start:start + batch_size]]
        for attempt in (1, 2):  # an empty or unparsed answer is retried once, then its passages are kept
            output, meta = screen(client, model, event, batch)
            usage = {k: usage[k] + meta.get(k, 0) for k in ("inputTokens", "outputTokens")} | {"calls": usage["calls"] + 1}
            batches.append({"first": batch[0][0], "attempt": attempt, "stopReason": meta["stopReason"],
                            "verdicts": len(output.verdicts) if output else 0})
            if output and output.verdicts:
                break
        # Refs come back as given, or wrapped as they were shown ("[50.12.5]").
        returned = {v.ref.strip().strip("[]").strip(): v for v in (output.verdicts if output else [])}
        for ref, _ in batch:
            v = returned.get(ref)
            verdicts[ref] = ({"relevant": v.relevant, "why": v.why} if v
                             else {"relevant": True, "why": "kept: no verdict returned"})
    selected = [ref for ref in ordered if verdicts[ref]["relevant"]]
    return {
        "inquiry": inquiry.id, "inquiryVersion": inquiry.version, "workId": inquiry.work_id,
        "createdAt": datetime.now(timezone.utc).isoformat(), "promptVersion": PROMPT_VERSION, "model": model,
        "usage": usage, "batches": batches, "passages": len(refs), "nameCandidates": len(ordered), "selected": selected,
        "verdicts": {ref: {"byName": candidates[ref], **verdicts[ref]} for ref in ordered},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inquiry", type=Path)
    parser.add_argument("--source", help="only the source with this workId")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH)
    args = parser.parse_args(argv)

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            inquiries = session.execute_read(lambda tx: load_inquiries(args.inquiry, tx))
            event = session.run("MATCH (e:Entity {id: $id}) RETURN e {.label, .description} AS e",
                                id=inquiries[0].narrative_event_id).single()["e"]
    finally:
        driver.close()

    client = anthropic_client()
    FINDS_DIRECTORY.mkdir(exist_ok=True)
    for inquiry in inquiries:
        if args.source and inquiry.work_id != args.source:
            continue
        found = find(client, args.model, inquiry, open_source(inquiry.source, GRAPH_REVISED), event, args.batch)
        path = finds_path(inquiry.id, inquiry.work_id)
        path.write_bytes((json.dumps(found, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"{inquiry.work_id}: {found['passages']} passages, {found['nameCandidates']} by name, "
              f"{len(found['selected'])} selected ({found['usage']['calls']} calls, {found['usage']['inputTokens']} in, "
              f"{found['usage']['outputTokens']} out) -> {path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
