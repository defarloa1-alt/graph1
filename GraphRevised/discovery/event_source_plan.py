"""The event source plan (29 §3 step 3, §6): which works to read for an event, chosen by the agent.

    python -m GraphRevised.discovery.event_source_plan GraphRevised/inquiries/actium-battle.json
        [--budget 4] [--model claude-opus-5-5]

Candidates come from five channels: the works the inquiry already reads; the
references of its Wikipedia article; citations of other accounts inside the
passages already preserved; the event's Wikidata "described by source"; and
the agent's own knowledge of the witnesses, which also reads the first three
into candidate works. Every candidate is then checked deterministically at the
catalogues of the source registry (Scaife, Project Gutenberg, LacusCurtius),
and its status is given in words, never as a confidence:

    found       proposed by a channel
    identified  the work confirmed at a catalogue
    located     a copy found in a system the registry reads (rights are checked by the
                registry's rule when the copy is preserved)
    chosen      chosen by the agent within the budget, with its reason
    read        already a source of the inquiry

Work, edition, and copy are separate fields. The model's own certainty stays a
note. The plan is a workflow file in GraphRevised/plans/; it changes nothing in
the graph. The inquiry builder preserves the chosen copies and adds them to the
inquiry.
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

from GraphRevised.adapters.scaife_catalog import load_catalog
from GraphRevised.adapters.text_catalogues import load_gutenberg, load_lacuscurtius, snapshot_record, title_match, title_stems
from GraphRevised.adapters.wikidata_identity import polite_get
from GraphRevised.adapters.wikidata_statements import REPOSITORY_ROOT
from GraphRevised.adapters.wikipedia_passages import references
from GraphRevised.discovery.source_plan import CITATION_PATTERNS, RELATION_ORDER, check_catalog, cited_sources
from GraphRevised.proposals.passage_reader import Inquiry, anthropic_client, load_inquiries
from GraphRevised.proposals.prompt_version import prompt_version
from GraphRevised.proposals.registry import load_registry

GRAPH_REVISED = Path(__file__).resolve().parents[1]
PLANS_DIRECTORY = GRAPH_REVISED / "plans"
CACHE_DIRECTORY = GRAPH_REVISED / "cache"
REGISTRY_PATH = GRAPH_REVISED / "curation" / "sources.json"
DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_BUDGET = 4
CHANNELS = ("wikipedia-reference", "passage-citation", "wikidata-described-by", "agent")

PROPOSE_PROMPT = """\
You plan the reading for one historical event in a knowledge graph. The graph already reads some \
sources; you are given those, the references of the event's Wikipedia article, citations of other \
accounts found in the passages already read, and the works Wikidata says describe the event. List \
the works worth reading for the event: ancient witnesses first, also later ancient and medieval \
accounts, modern histories, and imaginative works (poems, plays, novels, paintings) that depict it. \
A deterministic step then checks every candidate at library catalogues; your list is a plan, not evidence.

Rules:
1. One candidate per work. Read the given references and citations into works (a footnote such as \
an author's name with a book and chapter names a work), and add the witnesses you know of that they \
miss. Do not list the works already read.
2. channels: which inputs name the work (wikipedia-reference, passage-citation, wikidata-described-by), \
and agent when you add it yourself.
3. locator: where the work treats the event (book, chapter, poem, lines), only as precisely as you \
reliably know it; otherwise "unknown". Never invent one.
4. cts_work_urn: the CTS work URN only if you are sure of it; otherwise empty.
5. composition_year: approximate year, negative for BCE with no year zero; empty if unknown. \
relation: contemporary (written by someone alive and active at the time), near-contemporary \
(within about two generations), or later.
6. form: one of the given Work forms. author: the name a library catalogue would use.
7. A lost work cited by others is listed with form "lost" and no locator.
8. coverage: one sentence on what the work contributes about the event. certainty: a short note \
on how sure you are that the work treats the event; it is recorded, never used as a score.
"""

CHOOSE_PROMPT = """\
You choose which located sources a knowledge graph reads next for one historical event, within a \
budget. Each candidate has a status and its copies. Choose only located candidates. Prefer, in \
order: ancient witnesses the graph does not yet read, especially contemporary ones; works that give \
a different voice (a poet, a later epitomator, a modern historian whose copy is public domain); and \
copies in English translation where the reader reads English. Give a reason for each choice in one \
sentence, and for each located candidate you leave out, one sentence on why.
"""


class EventCandidate(BaseModel):
    author: str
    work: str
    locator: str
    cts_work_urn: str
    composition: str
    composition_year: int | None
    form: str
    relation: Literal["contemporary", "near-contemporary", "later"]
    depends_on: list[str]
    coverage: str
    channels: list[str]
    certainty: str


class ProposeOutput(BaseModel):
    candidates: list[EventCandidate]
    notes: str


class Choice(BaseModel):
    candidate: int
    copy_index: int
    reason: str


class LeftOut(BaseModel):
    candidate: int
    reason: str


class ChooseOutput(BaseModel):
    chosen: list[Choice]
    left_out: list[LeftOut]


def _call(client, model: str, system: str, user: str, output_format):
    response = client.beta.messages.parse(model=model, max_tokens=16000, system=system,
                                          messages=[{"role": "user", "content": user}], output_format=output_format)
    meta = {"model": response.model, "stopReason": response.stop_reason, "inputTokens": response.usage.input_tokens,
            "outputTokens": response.usage.output_tokens, "requestId": response._request_id}
    return (None if response.stop_reason == "refusal" else response.parsed_output), meta


def propose(client, model: str, event: dict[str, Any], read: list[dict[str, Any]], wiki_refs: list[str],
            citations: list[dict[str, str]], described_by: list[str], forms: list[str]):
    user = (
        f"Event: {event['label']} ({event.get('description') or ''})\n\n"
        "Works already read:\n" + "\n".join(f"- {w['label']} (form {w.get('form') or 'unknown'})" for w in read) + "\n\n"
        f"Work forms: {', '.join(forms)}, lost\n\n"
        "References of the event's Wikipedia article:\n" + ("\n".join(f"- {r}" for r in wiki_refs) or "- none") + "\n\n"
        "Citations of other accounts in passages already read:\n"
        + ("\n".join(f"- [{c['work']} {c['locator']}] {c['context']}" for c in citations) or "- none") + "\n\n"
        "Wikidata, described by source:\n" + ("\n".join(f"- {d}" for d in described_by) or "- none")
    )
    return _call(client, model, PROPOSE_PROMPT, user, ProposeOutput)


def choose(client, model: str, event: dict[str, Any], candidates: list[dict[str, Any]], budget: int):
    lines = []
    for index, c in enumerate(candidates):
        copies = "; ".join(f"copy_index {i}: {copy['system']} {copy['label']} ({copy['language'] or 'language unknown'})"
                           for i, copy in enumerate(c["copies"])) or "no copy"
        lines.append(f"[{index}] {c['status']}: {c['author']}, {c['work']} ({c['composition']}, {c['relation']}, "
                     f"form {c['form']}; {c['coverage']}) -- {copies}")
    user = f"Event: {event['label']}\nBudget: {budget} sources\n\nCandidates:\n" + "\n".join(lines)
    return _call(client, model, CHOOSE_PROMPT, user, ChooseOutput)


PROMPT_VERSION = prompt_version("event-source-plan-v1", PROPOSE_PROMPT, CHOOSE_PROMPT, propose, choose)


def readable_systems(registry_path: Path = REGISTRY_PATH) -> dict[str, str]:
    """Registry systems with an adapter: their id and adapter type (the copies the reader can read)."""
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    return {s["id"]: s["adapter"]["type"] for s in registry["sources"] if s["status"] == "read" and s.get("adapter")}


def _title_score(work: str, label: str) -> int:
    return len(title_stems(work) & title_stems(label))


def locate(candidate: EventCandidate, scaife, gutenberg, lacuscurtius, systems: dict[str, str]) -> dict[str, Any]:
    """What the catalogues say about one candidate: whether the work is identified, and its copies.
    A lost work has no copy, whatever a catalogue lists under its author."""
    copies: list[dict[str, Any]] = []
    identified: list[str] = []
    scaife_check = check_catalog(candidate, scaife)
    if scaife_check.get("workUrn") and "perseus" in systems:
        identified.append(f"Scaife: {scaife_check['workLabel']} ({scaife_check['workUrn']}, {scaife_check['status']})")
        for edition in scaife_check["editions"]:
            language = edition.rsplit(".", 1)[-1].split("-")[-1].rstrip("0123456789") or None
            copies.append({"system": "perseus", "adapter": systems["perseus"], "identifier": edition,
                           "label": f"Perseus {edition.rsplit(':', 1)[-1]}", "language": language})
    if "gutenberg" in systems:
        books = sorted(((_title_score(candidate.work, b["Title"]), b) for b in gutenberg.by_author(candidate.author)
                        if title_match(candidate.work, b["Title"])), key=lambda pair: -pair[0])
        for score, book in books[:3]:
            identified.append(f"Project Gutenberg: {book['Title'].splitlines()[0]} (ebook {book['Text#']})")
            copies.append({"system": "gutenberg", "adapter": systems["gutenberg"], "identifier": book["Text#"],
                           "label": f"Gutenberg {book['Text#']}: {book['Title'].splitlines()[0]}",
                           "language": book["Language"], "translators": [p.strip() for p in book["Authors"].split(";")
                                                                         if "[Translator]" in p]})
    if "lacuscurtius" in systems:
        works = lacuscurtius.by_author(candidate.author)
        scored = sorted(works, key=lambda w: -_title_score(candidate.work, w["label"]))
        if scored and (len(scored) == 1 or title_match(candidate.work, scored[0]["label"])):
            work = scored[0]
            identified.append(f"LacusCurtius: {work['label']}")
            copies.append({"system": "lacuscurtius", "adapter": systems["lacuscurtius"], "identifier": work["url"],
                           "label": f"LacusCurtius: {work['label']}", "language": "en"})
    if candidate.form == "lost":
        copies = []
    status = "located" if copies else "identified" if identified else "found"
    return {"status": status, "identifiedAt": identified, "copies": copies, "scaife": scaife_check}


def already_read(candidate: EventCandidate, read: list[dict[str, Any]]) -> str | None:
    """The id of a Work the inquiry already reads that this candidate names, matched by author and title."""
    author_words = {w.lower() for w in re.findall(r"[A-Za-z]{4,}", candidate.author)}
    for work in read:
        label = work["label"].lower()
        if any(w in label for w in author_words) and _title_score(candidate.work, work["label"]) > 0:
            return work["id"]
    return None


def described_by_labels(record_path: Path | None) -> list[str]:
    """The event's Wikidata "described by source" (P1343), labelled from Wikidata."""
    if record_path is None or not record_path.exists():
        return []
    data = json.loads(record_path.read_text(encoding="utf-8"))
    entity = next(iter(data["entities"].values())) if "entities" in data else data
    ids = [c["mainsnak"]["datavalue"]["value"]["id"] for c in entity.get("claims", {}).get("P1343", [])
           if c["mainsnak"].get("datavalue")]
    if not ids:
        return []
    labels = polite_get("https://www.wikidata.org/w/api.php", params={
        "action": "wbgetentities", "ids": "|".join(ids), "props": "labels|descriptions", "languages": "en",
        "format": "json"}).json()["entities"]
    return [f"{labels[i].get('labels', {}).get('en', {}).get('value', i)} ({i}): "
            f"{labels[i].get('descriptions', {}).get('en', {}).get('value', '')}" for i in ids]


def rank_key(candidate: dict[str, Any]) -> tuple:
    order = {"read": 0, "chosen": 1, "located": 2, "identified": 3, "found": 4}
    year = candidate["composition_year"] if candidate["composition_year"] is not None else 10**6
    return order[candidate["status"]], RELATION_ORDER[candidate["relation"]], year


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inquiry", type=Path)
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET, help="how many new sources the agent may choose")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args(argv)

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            inquiries: list[Inquiry] = session.execute_read(lambda tx: load_inquiries(args.inquiry, tx))
            event_id = inquiries[0].narrative_event_id
            if not event_id:
                raise ValueError("an event source plan needs an inquiry with a narrativeEventId")
            event = session.run(
                "MATCH (e:Entity {id: $id}) OPTIONAL MATCH (e)-[l:HAS_AUTHORITY_RECORD]->(r:AuthorityRecord {system: 'Wikidata'}) "
                "WHERE l.role = 'entity_identity' RETURN e {.id, .label, .description} AS e, head(collect(r.rawPayloadUri)) AS uri",
                id=event_id).single()
            read = session.run("MATCH (w:Entity) WHERE w.id IN $ids RETURN w {.id, .label, .form} AS w",
                               ids=[i.work_id for i in inquiries]).value("w")
            passages = session.run(
                "MATCH (o:SourceObservation)-[:IN_WORK]->(w:Entity) WHERE w.id IN $ids "
                "RETURN w.label AS work, o.locator AS locator, o.passageText AS passageText, o.language AS language",
                ids=[i.work_id for i in inquiries]).data()
    finally:
        driver.close()

    citations = [{**c, "work": p["work"]} for p in passages for c in cited_sources([p])]
    wiki_refs = [r for i in inquiries if i.source.get("type") == "wikipedia-html"
                 for r in references(GRAPH_REVISED / i.source["article"])]
    record_path = REPOSITORY_ROOT / event["uri"] if event["uri"] else None
    described = described_by_labels(record_path)
    forms = sorted(load_registry().work_forms)

    client = anthropic_client()
    proposed, propose_meta = propose(client, args.model, event["e"], read, wiki_refs, citations, described, forms)
    if proposed is None:
        print(f"no plan: {propose_meta['stopReason']}")
        return 1

    scaife, gutenberg, lacuscurtius = load_catalog(CACHE_DIRECTORY), load_gutenberg(CACHE_DIRECTORY), load_lacuscurtius(CACHE_DIRECTORY)
    systems = readable_systems()
    candidates = []
    for c in proposed.candidates:
        work_id = already_read(c, read)
        found = locate(c, scaife, gutenberg, lacuscurtius, systems)
        candidates.append({**c.model_dump(), **found, "status": "read" if work_id else found["status"],
                           "readAs": work_id, "channels": [ch for ch in c.channels if ch in CHANNELS]})
    for work in read:  # the works read are in the plan whether or not the agent named them
        if not any(c["readAs"] == work["id"] for c in candidates):
            candidates.append({"author": "", "work": work["label"], "locator": "", "cts_work_urn": "", "composition": "",
                               "composition_year": None, "form": work.get("form") or "", "relation": "later",
                               "depends_on": [], "coverage": "", "channels": [], "certainty": "", "status": "read",
                               "readAs": work["id"], "identifiedAt": [], "copies": [], "scaife": {}})

    choice, choose_meta = choose(client, args.model, event["e"], candidates, args.budget)
    refused = []
    for pick in (choice.chosen if choice else [])[:args.budget]:
        if not (0 <= pick.candidate < len(candidates)) or candidates[pick.candidate]["status"] != "located" \
                or not (0 <= pick.copy_index < len(candidates[pick.candidate]["copies"])):
            refused.append(pick.model_dump())
            continue
        candidates[pick.candidate] |= {"status": "chosen", "chosenCopy": pick.copy_index, "reason": pick.reason}
    for left in (choice.left_out if choice else []):
        if 0 <= left.candidate < len(candidates):
            candidates[left.candidate].setdefault("reasonLeftOut", left.reason)
    candidates.sort(key=rank_key)

    plan = {
        "inquiry": inquiries[0].id, "inquiryVersion": inquiries[0].version, "event": event_id,
        "createdAt": datetime.now(timezone.utc).isoformat(), "promptVersion": PROMPT_VERSION, "budget": args.budget,
        "propose": propose_meta, "choose": choose_meta,
        "catalogues": {"scaife": {"sourceUri": scaife.source_uri, "retrievedAt": scaife.retrieved_at,
                                  "contentHash": scaife.content_hash},
                       "gutenberg": snapshot_record(gutenberg.snapshot),
                       "lacuscurtius": snapshot_record(lacuscurtius.snapshot)},
        "channels": {"wikipediaReferences": wiki_refs, "passageCitations": citations, "wikidataDescribedBy": described,
                     "citationsNotScanned": sorted({p["language"] for p in passages
                                                    if p.get("language") not in CITATION_PATTERNS} - {None})},
        "candidates": candidates, "refusedChoices": refused, "notes": proposed.notes,
    }
    PLANS_DIRECTORY.mkdir(exist_ok=True)
    stem = inquiries[0].id.rsplit(":", 1)[-1]
    path = PLANS_DIRECTORY / f"{stem}-event-sources-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    path.write_bytes((json.dumps(plan, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))

    for c in candidates:
        copy = c["copies"][c["chosenCopy"]]["label"] if c["status"] == "chosen" else ""
        print(f"{c['status']:<10} {c['relation']:<18} {c['composition']:<14} {c['author']}, {c['work']} "
              f"[{c['locator']}] ({c['form']}) {copy}")
        if c.get("reason"):
            print(f"{'':>11}why: {c['reason']}")
    print(f"\nreferences {len(wiki_refs)}, passage citations {len(citations)}, described by {len(described)}; "
          f"refused choices {len(refused)}")
    print(f"plan: {path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    print(json.dumps({"propose": {k: propose_meta[k] for k in ("inputTokens", "outputTokens")},
                      "choose": {k: choose_meta[k] for k in ("inputTokens", "outputTokens")}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
