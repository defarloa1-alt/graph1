"""Reasoning on the curator's book notes: triage, then a lens reading (curator's choices, 2026-11-17).

    python -m GraphRevised.capture.note_reader triage [--note <name>] [--model ...] [--read]
    python -m GraphRevised.capture.note_reader read --note <name> --inquiry <inquiry.json>
        [--lens military] [--model ...] [--read [--submit]]

A note cannot be applied (capture/notes.py) until `concerns` names entities, and cannot be read
until it is applied, so there are two steps. Both are dry runs by default: they build the exact
request and price its worst case with the spend meter; nothing is called. A paid call needs a named
budget (CHRYSTALLUM_BUDGET) and the curator's go-ahead for that run.

- triage (a note whose `concerns` is still unfilled): one small call. The model sees the book's
  words, its footnotes, the curator's own text, the candidate entities whose labels the note's words
  touch (notes.suggest_concerns, code only), and the lenses (curation/lenses.json). It picks the
  entities the note concerns and the lenses it bears on, each with a reason. With --read the picks
  are written into the note (curator's choice): `concerns` in place of the placeholder, each line
  marked "# suggested", and `lens/<id>` tags. Only ids among the candidates, and lenses that exist,
  are written; nothing else in the file changes. A lens the note needs but the catalogue lacks is
  printed, never invented.
- read (an applied note): the lens reader on the note's transcription, as the article reader reads
  a page: claims and historiography (Questions, Positions), every quotation checked verbatim in the
  book's words. The curator's own text goes in as a prompt (Inquiry.curator_note), never as a
  source or evidence: a Question it raises may be proposed only when the book's author answers it.
  With --submit everything is stored proposed and the fact layer is rebuilt.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from GraphRevised.capture.notes import (DEFAULT_FOLDER, Neo4jNoteReader, Note, notes_in, read_note,
                                        significant_words, suggest_concerns)
from GraphRevised.proposals.lens import LENSES_PATH
from GraphRevised.proposals.passage_reader import DEFAULT_MODEL, RUNS_DIRECTORY
from GraphRevised.spend_meter import ceiling
from GraphRevised import localdb

TRIAGE_CANDIDATES = 40
PLACEHOLDER = "replace-me"


# --- Triage ---------------------------------------------------------------------------------------

class PickedEntity(BaseModel):
    id: str = Field(description="an id from the candidate list, exactly")
    reason: str = Field(description="why the note concerns it, in a few words")


class PickedLens(BaseModel):
    id: str = Field(description="a lens id from the list, exactly")
    reason: str


class NoteTriage(BaseModel):
    concerns: list[PickedEntity]
    lenses: list[PickedLens]
    missing_lens: str | None = Field(default=None, description="a lens the note needs that the list lacks, or null")


TRIAGE_SYSTEM = """You file a historian's reading note in a historical knowledge graph.
The note has the book's words (a quotation), sometimes the book's footnotes, and sometimes the
curator's own thought. Choose:
1. concerns: the entities the note is about, only from the candidate list, by id. Prefer the
   specific (a place, a group, a person) over the general; include the event when the passage is
   about it. Tell apart entities with similar names by their kind and description (a different
   person of the same name is not the one meant). Three to five is usual; never pad.
2. lenses: the lenses the note bears on, only from the lens list, by id, each with a reason.
3. missing_lens: if the note clearly needs a lens the list does not have, name it; else null.
Reasons are short. Never invent an id."""


def lenses_catalogue(path: Path = LENSES_PATH) -> list[dict[str, str]]:
    lenses = json.loads(path.read_text(encoding="utf-8"))["lenses"]
    return [{"id": l["id"], "label": l["label"], "purpose": l.get("purpose", "")} for l in lenses]


def unfilled(note: Note) -> bool:
    concerns = note.ids("concerns")
    return not concerns or any(PLACEHOLDER in c for c in concerns)


def triage_request(model: str, note: Note, candidates: list[dict[str, Any]], lenses: list[dict[str, str]],
                   descriptions: dict[str, str]) -> dict[str, Any]:
    entity_lines = "\n".join(
        f"- {c['id']} | {c['label']} | {c['kind']} | {descriptions.get(c['id']) or ''}" for c in candidates)
    lens_lines = "\n".join(f"- {l['id']} | {l['label']} | {l['purpose']}" for l in lenses)
    footnotes = "\n".join(f"[{f.mark}] {f.text}" for f in note.footnotes)
    user = (f"Book's words ({note.locator() or 'no locator'}):\n{note.quote}\n\n"
            + (f"The book's footnotes:\n{footnotes}\n\n" if footnotes else "")
            + (f"The curator's own thought:\n{note.text}\n\n" if note.text else "")
            + f"Candidate entities (id | label | kind | description):\n{entity_lines or '- none'}\n\n"
            + f"Lenses (id | label | purpose):\n{lens_lines}")
    return {"model": model, "max_tokens": 2000, "system": TRIAGE_SYSTEM,
            "messages": [{"role": "user", "content": user}], "output_format": NoteTriage}


def checked_triage(triage: NoteTriage, candidates: list[dict[str, Any]], lenses: list[dict[str, str]]
                   ) -> tuple[list[dict[str, str]], list[dict[str, str]], list[str]]:
    """The picks that name a real candidate or lens; the rest are reported, never written."""
    by_id = {c["id"]: c for c in candidates}
    lens_ids = {l["id"] for l in lenses}
    concerns, chosen_lenses, dropped = [], [], []
    for pick in triage.concerns:
        if pick.id in by_id and pick.id not in {c["id"] for c in concerns}:
            concerns.append({"id": pick.id, "label": by_id[pick.id]["label"], "reason": pick.reason})
        else:
            dropped.append(f"entity {pick.id!r} is not a candidate")
    for pick in triage.lenses:
        if pick.id in lens_ids and pick.id not in {l["id"] for l in chosen_lenses}:
            chosen_lenses.append({"id": pick.id, "reason": pick.reason})
        else:
            dropped.append(f"lens {pick.id!r} is not in the catalogue")
    return concerns, chosen_lenses, dropped


LIST_ITEM = re.compile(r"^\s*-\s")


def _replace_list(lines: list[str], key: str, items: list[str], *, keep_existing: bool) -> list[str]:
    """Set a frontmatter list (`key:` and its `  - ` lines) to `items`; with keep_existing, append."""
    start = next((i for i, line in enumerate(lines) if re.match(rf"^{key}:\s*(#.*)?$", line)), None)
    if start is None:
        return lines + [f"{key}:"] + items
    end = start + 1
    while end < len(lines) and LIST_ITEM.match(lines[end]):
        end += 1
    existing = lines[start + 1:end] if keep_existing else []
    present = {line.split("#")[0].strip() for line in existing}
    added = [item for item in items if item.split("#")[0].strip() not in present]
    return lines[:start + 1] + existing + added + lines[end:]


def write_triage(path: Path, concerns: list[dict[str, str]], lenses: list[dict[str, str]]) -> None:
    """Write the picks into the note's frontmatter: concerns replace the placeholder, lens tags are
    added. Nothing outside those two lists changes."""
    raw = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    text = raw.replace("\r\n", "\n")
    _, front, body = text.split("---", 2)
    lines = front.strip("\n").split("\n")
    lines = _replace_list(lines, "concerns", [
        f"  - {c['id']}  # suggested: {c['label']} ({c['reason']})" for c in concerns], keep_existing=False)
    lines = _replace_list(lines, "tags", [f"  - lens/{l['id']}" for l in lenses], keep_existing=True)
    text = "---\n" + "\n".join(lines) + "\n---" + body
    path.write_bytes(text.replace("\n", newline).encode("utf-8"))


def run_triage(args: argparse.Namespace, session: Any, client: Any) -> Decimal:
    lenses = lenses_catalogue()
    total = Decimal(0)
    paths = notes_in(args.folder)
    for name, path in paths.items():
        if args.note not in (None, name):
            continue
        note = read_note(path)
        if note.kind != "note" or not unfilled(note):
            continue
        tx = session.begin_transaction()
        try:
            reader = Neo4jNoteReader(tx)
            words = significant_words(" ".join([note.quote, note.text]))
            candidates = suggest_concerns(note, reader.candidates(words) if words else [], limit=TRIAGE_CANDIDATES)
            descriptions = dict(tx.run("MATCH (e:Entity) WHERE e.id IN $ids RETURN e.id, e.description",
                                       ids=[c["id"] for c in candidates]).values())
        finally:
            tx.rollback()
        request = triage_request(args.model, note, candidates, lenses, descriptions)
        top = ceiling(args.model, request)
        total += top
        if not args.read:
            print(f"{name}: {len(candidates)} candidates; worst case ${top:.4f}")
            continue
        response = client.beta.messages.parse(**request)
        triage = response.parsed_output
        if triage is None:
            print(f"{name}: no output ({response.stop_reason})")
            continue
        concerns, chosen, dropped = checked_triage(triage, candidates, lenses)
        print(f"{name}:")
        for c in concerns:
            print(f"    concerns {c['id']}  ({c['label']}: {c['reason']})")
        for l in chosen:
            print(f"    lens/{l['id']}  ({l['reason']})")
        if triage.missing_lens:
            print(f"    a lens the catalogue lacks: {triage.missing_lens}")
        for d in dropped:
            print(f"    dropped: {d}")
        if concerns:
            write_triage(path, concerns, chosen)
            print("    written into the note, marked # suggested")
        _log(args, {"step": "triage", "note": name, "model": response.model, "requestId": response._request_id,
                    "concerns": concerns, "lenses": chosen, "missingLens": triage.missing_lens, "dropped": dropped})
    return total


# --- Reading an applied note ----------------------------------------------------------------------

NOTE_TRANSCRIPTION = """
MATCH (a:Annotation {id: $id})-[:ANNOTATES]->(o:SourceObservation)-[:IN_WORK]->(w:Entity:Work)
RETURN o.id AS observationId, o.locator AS locator, o.passageText AS quote, o.editionCitation AS edition,
       w.id AS workId, w.label AS workLabel, w.standing AS standing
"""


def run_read(args: argparse.Namespace, session: Any, client: Any) -> Decimal:
    from GraphRevised.adapters.sources import PassageSource
    from GraphRevised.operations import load_operations
    from GraphRevised.proposals.article_reader import historiography_context, licensed_claim_drafts
    from GraphRevised.proposals.historiography import HistoriographyOutput, store_historiography, to_historiography
    from GraphRevised.proposals.lens import load_lens
    from GraphRevised.proposals.passage_reader import (load_inquiries, proposer, read_passage, reader_prompt_version,
                                                       reader_request)
    from GraphRevised.proposals.predicate_needs import load_queue, open_requests_text
    from GraphRevised.proposals.registry import load_registry

    paths = notes_in(args.folder)
    if args.note not in paths:
        raise SystemExit(f"no note {args.note!r} in {args.folder}")
    note = read_note(paths[args.note])
    if not note.get("id"):
        raise SystemExit(f"{args.note}: not applied yet (run capture.notes apply --apply first)")
    lens_id = args.lens or next((t.split("/", 1)[1] for t in note.ids("tags") if t.startswith("lens/")), "general")
    lens = replace(load_lens(lens_id, args.lens_scope), requested=open_requests_text(load_queue()))
    registry = load_registry()
    tx = session.begin_transaction()
    try:
        found = tx.run(NOTE_TRANSCRIPTION, id=note.get("id")).single()
        inquiry = load_inquiries(args.inquiry, tx, briefs=None)[0]
        context = historiography_context(tx)
    finally:
        tx.rollback()
    if found is None:
        raise SystemExit(f"{args.note}: its Annotation {note.get('id')} has no transcription in the graph")
    work_label = found["workLabel"]
    inquiry = replace(inquiry, lens=lens, historiography=context, work_id=found["workId"], proposable_kinds=(),
                      source={"type": "curator-transcription", "workId": found["workId"]},
                      voice=work_label, curator_note=note.text or None)
    edition = PassageSource(author=work_label.split(", ", 1)[0], title=work_label.split(", ", 1)[-1],
                            translator=None, citation=found["edition"] or work_label,
                            refs=lambda _: [], observation=lambda _: {})
    locator, quote = found["locator"], found["quote"]
    passage = {"id": found["observationId"], "passageText": quote}
    request = reader_request(args.model, inquiry, edition, locator, passage, [], registry)
    top = ceiling(args.model, request)
    print(f"{args.note}: {work_label} {locator}; lens {lens.id}; {len(quote)} characters"
          + (f"; the curator's note goes in as a prompt" if note.text else "") + f"; worst case ${top:.4f}")
    if not args.read:
        return top
    output, meta = read_passage(client, args.model, inquiry, edition, locator, passage, [], registry)
    if output is None:
        print(f"  no output ({meta['stopReason']})")
        return top
    drafted = HistoriographyOutput.model_validate(meta.get("historiographyDrafted") or
                                                  {"questions": [], "positions": [], "holdings": [], "receptions": []})
    scope_ids = {e["id"] for e in inquiry.scope}
    holder_ids = {w["id"] for w in context["holders"]} | {found["workId"]}
    existing = {q["id"] for q in context["questions"]} | {p["id"] for p in context["positions"]}
    plan = to_historiography(drafted, quote, work_id=found["workId"], locator=locator, scope_ids=scope_ids,
                             work_ids=holder_ids, proposed_by=proposer(inquiry), model_id=meta["model"],
                             prompt_version=reader_prompt_version(inquiry), inquiry_id=inquiry.id, existing=existing)
    refused = licensed_claim_drafts(output.claims, quote, locator=locator, model_id=meta["model"],
                                    inquiry=inquiry, plan=plan)
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    operations = load_operations()
    tx = session.begin_transaction()
    try:
        stored = store_historiography(tx, operations, registry, plan, work_label=work_label,
                                      edition_citation=found["edition"] or work_label, proposed_by=proposer(inquiry),
                                      at=at, submit_drafts=args.submit, source_system="curator",
                                      rights="Short quotation transcribed for study; the work may be in copyright.")
        if args.submit:
            from GraphRevised.export.fact_layer import rebuild
            rebuild(tx)
            tx.commit()
        else:
            tx.rollback()
    except BaseException:
        if not tx.closed():
            tx.rollback()
        raise
    kept = sum(d["stored"] for d in stored["drafts"]) if args.submit else \
        sum(d["outcome"] in ("valid", "adds_evidence") for d in stored["drafts"])
    print(f"  {len(stored['drafts'])} draft(s), {kept} {'stored' if args.submit else 'pass validation (rolled back)'}; "
          f"{len(stored['entities'])} question(s) and position(s); {len(plan.unresolved_holders)} unresolved "
          f"holder(s); {len(plan.refused) + len(refused)} refused")
    for d in stored["drafts"]:
        print(f"    {d['outcome']}: {d['subject']} {d['predicate']} {d['object'] or ''}"
              + (f"  ({'; '.join(d['reasons'])})" if d["reasons"] else ""))
    _log(args, {"step": "read", "note": args.note, **{k: v for k, v in meta.items() if k != "historiographyDrafted"},
                "stored": stored, "unresolvedHolders": plan.unresolved_holders, "refused": plan.refused,
                "refusedClaims": refused, "submit": args.submit})
    return top


# --- Running ----------------------------------------------------------------------------------------

def _log(args: argparse.Namespace, record: dict[str, Any]) -> None:
    RUNS_DIRECTORY.mkdir(exist_ok=True)
    path = RUNS_DIRECTORY / f"note-reader-{args.stamp}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def main(argv: list[str] | None = None) -> int:
    from neo4j import GraphDatabase
    from GraphRevised.proposals.passage_reader import anthropic_client

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("step", choices=("triage", "read"))
    parser.add_argument("--folder", type=Path, default=DEFAULT_FOLDER)
    parser.add_argument("--note", help="only the note of this name (read: required)")
    parser.add_argument("--inquiry", type=Path, help="read: the inquiry whose scope the reading uses")
    parser.add_argument("--lens", help="read: the lens (default: the note's first lens/ tag, else general)")
    parser.add_argument("--lens-scope", default="roman-republic")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--read", action="store_true", help="call the model (paid; needs CHRYSTALLUM_BUDGET)")
    parser.add_argument("--submit", action="store_true", help="read --read: store what validates, all proposed")
    args = parser.parse_args(argv)
    if args.step == "read" and (not args.note or not args.inquiry):
        parser.error("read needs --note and --inquiry")
    if args.submit and not (args.read and args.step == "read"):
        parser.error("--submit is for read --read")
    sys.stdout.reconfigure(encoding="utf-8")
    args.stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    client = anthropic_client() if args.read else None  # refuses here when no budget is named

    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            total = (run_triage if args.step == "triage" else run_read)(args, session, client)
    finally:
        driver.close()
    if not args.read:
        print(f"worst case: ${total:.4f} (dry run; nothing was spent)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
