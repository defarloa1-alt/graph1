"""Identity-resolution queue: unresolved mentions -> Wikidata candidates -> curator choice.

    python -m GraphRevised.identity.queue build   <inquiry.json>
    python -m GraphRevised.identity.queue show    <inquiry.json> [--all]
    python -m GraphRevised.identity.queue resolve <inquiry.json> "<name>" --qid Q... --kind Person
                                                  [--id chr:entity:...] --by <name> --basis "<reason>"
    python -m GraphRevised.identity.queue skip    <inquiry.json> "<name>" --by <name> --basis "<reason>"

`build` gathers the unresolved mentions from the inquiry's latest reader run,
asks the model for search terms (a hint, not an identity), searches Wikidata,
and asks the model to suggest a candidate with a reason. The curator decides:
`resolve` adds the Entity with its preserved Wikidata identity and puts it in
the inquiry's scope; `skip` records that a mention will not be resolved.

The queue is workflow state and lives in GraphRevised/queues/, not in Neo4j.
Rebuilding keeps earlier decisions.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import requests
from neo4j import GraphDatabase
from pydantic import BaseModel

from GraphRevised.adapters.wikidata_identity import USER_AGENT, WIKIDATA_API_URL
from GraphRevised.operations import load_operations
from GraphRevised.proposals.passage_reader import DEFAULT_MODEL, anthropic_client
from GraphRevised.slices.add_entity import ENTITY_KINDS, persist_identity, preserved_identity_payload

GRAPH_REVISED = Path(__file__).resolve().parents[1]
QUEUE_DIRECTORY = GRAPH_REVISED / "queues"
RUNS_DIRECTORY = GRAPH_REVISED / "runs"
PROMPT_VERSION = "identity-queue-v1"
MAX_CANDIDATES = 6
SEARCH_PAUSE_SECONDS = 1.0

HINT_PROMPT = """\
You help a curator resolve names found in a historical source to Wikidata records. You do not \
decide identities. For each mention, using the quotations and the source, give the kind of thing \
it is, a canonical name that merges mentions of the same referent (for example "Eurycles" and \
"Eurycles the Laconian"), up to three Wikidata search strings likely to find the right record \
(full names, standard English forms), and how central the referent is to the inquiry's subject: \
core (acts in the subject's events), peripheral (mentioned in passing), or not_an_entity (a \
generic group or phrase not worth an identity, such as "the Greeks")."""

SUGGEST_PROMPT = """\
You help a curator resolve names in a historical source to Wikidata records. For each mention you \
get quotations and Wikidata search candidates. Suggest the candidate the mention most likely \
denotes, or none if no candidate fits. Judge by the source's period and context: a candidate who \
lived in another century, or a modern namesake, does not fit. Give a confidence (high, medium, \
low) and a short reason. The curator makes the decision; when the evidence cannot separate two \
candidates, say so and lower the confidence."""


class MentionHint(BaseModel):
    name: str
    canonical_name: str
    kind: Literal["Person", "Place", "Group", "Event", "Object", "Work", "Period", "Other"]
    search_queries: list[str]
    centrality: Literal["core", "peripheral", "not_an_entity"]
    note: str


class HintOutput(BaseModel):
    mentions: list[MentionHint]


class Suggestion(BaseModel):
    canonical_name: str
    suggested_qid: str | None
    confidence: Literal["high", "medium", "low"]
    reason: str


class SuggestOutput(BaseModel):
    suggestions: list[Suggestion]


def queue_path(inquiry: dict[str, Any]) -> Path:
    return QUEUE_DIRECTORY / f"identity-{inquiry['id'].rsplit(':', 1)[-1]}.json"


def latest_run(inquiry_id: str) -> Path:
    for path in sorted(glob.glob(str(RUNS_DIRECTORY / "passage-reader-*.jsonl")), reverse=True):
        with open(path, encoding="utf-8") as handle:
            header = json.loads(handle.readline())
        if header.get("inquiry") == inquiry_id:
            return Path(path)
    raise FileNotFoundError(f"no reader run found for {inquiry_id}")


def gather_mentions(run: Path) -> dict[str, dict[str, Any]]:
    mentions: dict[str, dict[str, Any]] = {}
    with run.open(encoding="utf-8") as handle:
        next(handle)
        for line in handle:
            record = json.loads(line)
            for mention in record.get("unresolvedMentions", []):
                entry = mentions.setdefault(mention["name"], {"name": mention["name"], "occurrences": []})
                entry["occurrences"].append({"ref": record["ref"], "quotation": mention["quotation"]})
    return mentions


def wikidata_get(params: dict[str, Any], attempts: int = 5) -> dict[str, Any]:
    """GET the Wikidata API politely: pause between requests and honour 429 Retry-After."""
    for attempt in range(attempts):
        time.sleep(SEARCH_PAUSE_SECONDS)
        response = requests.get(WIKIDATA_API_URL, params={**params, "format": "json"},
                                headers={"User-Agent": USER_AGENT}, timeout=20)
        if response.status_code != 429 or attempt == attempts - 1:
            break
        time.sleep(float(response.headers.get("Retry-After", 5 * (attempt + 1))))
    response.raise_for_status()
    return response.json()


def search_wikidata(query: str) -> list[dict[str, Any]]:
    """Candidates from both label search and full-text search.

    Label search (wbsearchentities) matches names and aliases; full-text search
    also matches descriptive queries such as "Gnaeus Domitius Ahenobarbus
    consul 32 BC", which label search misses.
    """
    by_label = wikidata_get({"action": "wbsearchentities", "search": query, "language": "en",
                             "limit": MAX_CANDIDATES, "formatversion": 2}).get("search", [])
    candidates = {
        item["id"]: {"qid": item["id"], "label": item.get("label", item["id"]), "description": item.get("description")}
        for item in by_label
    }
    full_text = [hit["title"] for hit in wikidata_get(
        {"action": "query", "list": "search", "srsearch": query, "srlimit": MAX_CANDIDATES}
    ).get("query", {}).get("search", []) if hit["title"].startswith("Q")]
    missing = [qid for qid in full_text if qid not in candidates]
    if missing:
        entities = wikidata_get({"action": "wbgetentities", "ids": "|".join(missing),
                                 "props": "labels|descriptions", "languages": "en"}).get("entities", {})
        for qid in missing:
            entity = entities.get(qid, {})
            candidates[qid] = {
                "qid": qid,
                "label": entity.get("labels", {}).get("en", {}).get("value", qid),
                "description": entity.get("descriptions", {}).get("en", {}).get("value"),
            }
    return list(candidates.values())


def ask(client, system: str, user: str, output_format):
    response = client.beta.messages.parse(
        model=DEFAULT_MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        extra_body={"fallbacks": "default"},
        system=system,
        messages=[{"role": "user", "content": user}],
        output_format=output_format,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("the model declined the request")
    return response.parsed_output, response.model


def local_entities_for(session, qids: list[str]) -> dict[str, str]:
    rows = session.run(
        """
        MATCH (entity:Entity)-[link:HAS_AUTHORITY_RECORD]->(record:AuthorityRecord {system: "Wikidata"})
        WHERE record.identifier IN $qids AND link.status = "accepted"
        RETURN record.identifier AS qid, entity.id AS entityId
        """,
        qids=qids,
    ).data()
    return {row["qid"]: row["entityId"] for row in rows}


def build(inquiry_path: Path, session) -> Path:
    inquiry = json.loads(inquiry_path.read_text(encoding="utf-8"))
    run = latest_run(inquiry["id"])
    mentions = gather_mentions(run)
    client = anthropic_client()

    listing = "\n".join(
        f"- {m['name']}: " + " | ".join(f"[{o['ref']}] {o['quotation']}" for o in m["occurrences"][:3])
        for m in mentions.values()
    )
    hints, model = ask(
        client, HINT_PROMPT,
        f"Inquiry: {inquiry['label']}\nSource: Plutarch, Life of Antony (Perrin translation)\n\nMentions:\n{listing}",
        HintOutput,
    )

    entries: dict[str, dict[str, Any]] = {}
    for hint in hints.mentions:
        if hint.name not in mentions:
            continue
        entry = entries.setdefault(hint.canonical_name, {
            "canonicalName": hint.canonical_name, "names": [], "kind": hint.kind,
            "centrality": hint.centrality, "note": hint.note, "searchQueries": [], "occurrences": [],
        })
        entry["names"].append(hint.name)
        entry["occurrences"].extend(mentions[hint.name]["occurrences"])
        entry["searchQueries"] = list(dict.fromkeys(entry["searchQueries"] + hint.search_queries))

    for entry in entries.values():
        if entry["centrality"] == "not_an_entity":
            entry["candidates"] = []
            continue
        candidates: dict[str, dict[str, Any]] = {}
        for query in entry["searchQueries"][:3]:
            for candidate in search_wikidata(query):
                candidates.setdefault(candidate["qid"], candidate)
        entry["candidates"] = list(candidates.values())[:MAX_CANDIDATES * 2]

    in_graph = local_entities_for(session, [c["qid"] for e in entries.values() for c in e["candidates"]])
    for entry in entries.values():
        for candidate in entry["candidates"]:
            candidate["localEntity"] = in_graph.get(candidate["qid"])

    to_suggest = [e for e in entries.values() if e["candidates"]]
    suggestion_text = "\n\n".join(
        f"{e['canonicalName']} ({e['kind']})\n  quotations: "
        + " | ".join(f"[{o['ref']}] {o['quotation']}" for o in e["occurrences"][:3])
        + "\n  candidates:\n"
        + "\n".join(f"    {c['qid']}: {c['label']} — {c['description'] or 'no description'}" for c in e["candidates"])
        for e in to_suggest
    )
    suggestions, _ = ask(
        client, SUGGEST_PROMPT,
        f"Source: Plutarch, Life of Antony, narrative of 32-31 BCE.\n\n{suggestion_text}",
        SuggestOutput,
    )
    for suggestion in suggestions.suggestions:
        if suggestion.canonical_name in entries:
            entries[suggestion.canonical_name]["suggestion"] = suggestion.model_dump()

    path = queue_path(inquiry)
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"entries": []}
    decisions = {e["canonicalName"]: e for e in previous["entries"] if e.get("status") != "pending"}
    for name, entry in entries.items():
        kept = decisions.get(name)
        entry["status"] = kept["status"] if kept else "pending"
        if kept:
            entry["decision"] = kept["decision"]

    QUEUE_DIRECTORY.mkdir(exist_ok=True)
    path.write_text(json.dumps({
        "inquiry": inquiry["id"],
        "builtAt": datetime.now(timezone.utc).isoformat(),
        "fromRun": run.name,
        "promptVersion": PROMPT_VERSION,
        "model": model,
        "entries": sorted(entries.values(), key=lambda e: ({"core": 0, "peripheral": 1}.get(e["centrality"], 2), e["canonicalName"])),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def show(inquiry_path: Path, show_all: bool) -> None:
    inquiry = json.loads(inquiry_path.read_text(encoding="utf-8"))
    queue = json.loads(queue_path(inquiry).read_text(encoding="utf-8"))
    for entry in queue["entries"]:
        if not show_all and (entry["status"] != "pending" or entry["centrality"] == "not_an_entity"):
            continue
        refs = ", ".join(sorted({o["ref"] for o in entry["occurrences"]}))
        print(f"[{entry['status']}] {entry['canonicalName']} ({entry['kind']}, {entry['centrality']}) — {refs}")
        suggestion = entry.get("suggestion")
        for candidate in entry["candidates"]:
            mark = "*" if suggestion and suggestion["suggested_qid"] == candidate["qid"] else " "
            local = f"  [in graph: {candidate['localEntity']}]" if candidate.get("localEntity") else ""
            print(f"   {mark} {candidate['qid']:<11} {candidate['label']} — {candidate['description'] or ''}{local}")
        if suggestion:
            print(textwrap.fill(f"suggestion ({suggestion['confidence']}): {suggestion['suggested_qid'] or 'none'} — "
                                f"{suggestion['reason']}", width=100, initial_indent="     ", subsequent_indent="     "))
        print()


def decide(inquiry_path: Path, name: str, status: str, decision: dict[str, Any]) -> None:
    inquiry = json.loads(inquiry_path.read_text(encoding="utf-8"))
    path = queue_path(inquiry)
    queue = json.loads(path.read_text(encoding="utf-8"))
    entry = next((e for e in queue["entries"] if name in (e["canonicalName"], *e["names"])), None)
    if entry is None:
        raise SystemExit(f"no queue entry named {name!r}")
    entry["status"] = status
    entry["decision"] = decision
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve(inquiry_path: Path, session, *, name: str, qid: str, kind: str, entity_id: str | None,
            by: str, basis: str) -> str:
    payload_path, metadata = preserved_identity_payload(qid)
    entity_id = entity_id or "chr:entity:" + re.sub(r"[^a-z0-9]+", "-", metadata["entityLabel"].lower()).strip("-")
    session.execute_write(
        persist_identity, load_operations(),
        entity_id=entity_id, kind=kind, payload_path=payload_path, metadata=metadata,
    )
    inquiry = json.loads(inquiry_path.read_text(encoding="utf-8"))
    if entity_id not in inquiry["candidateEntityIds"]:
        inquiry["candidateEntityIds"].append(entity_id)
        inquiry["version"] += 1
        inquiry_path.write_text(json.dumps(inquiry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    decide(inquiry_path, name, "resolved", {
        "qid": qid, "entityId": entity_id, "label": metadata["entityLabel"],
        "by": by, "basis": basis, "at": datetime.now(timezone.utc).isoformat(),
    })
    return f"{entity_id}: {metadata['entityLabel']} ({qid}) — {metadata['entityDescription']}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "show", "resolve", "skip"):
        command = commands.add_parser(name)
        command.add_argument("inquiry", type=Path)
        if name == "show":
            command.add_argument("--all", action="store_true")
        if name in ("resolve", "skip"):
            command.add_argument("name")
            command.add_argument("--by", required=True)
            command.add_argument("--basis", required=True)
        if name == "resolve":
            command.add_argument("--qid", required=True)
            command.add_argument("--kind", required=True, choices=ENTITY_KINDS)
            command.add_argument("--id", dest="entity_id")
    args = parser.parse_args(argv)

    if args.command == "show":
        show(args.inquiry, args.all)
        return 0
    if args.command == "skip":
        decide(args.inquiry, args.name, "skipped", {
            "by": args.by, "basis": args.basis, "at": datetime.now(timezone.utc).isoformat(),
        })
        print(f"skipped: {args.name}")
        return 0

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            if args.command == "build":
                print(f"queue: {build(args.inquiry, session).relative_to(GRAPH_REVISED.parent).as_posix()}")
            else:
                print(resolve(args.inquiry, session, name=args.name, qid=args.qid, kind=args.kind,
                              entity_id=args.entity_id, by=args.by, basis=args.basis))
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
