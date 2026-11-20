"""A lens reading of a licensed article, with historiography (44, D-156).

    python -m GraphRevised.proposals.article_reader <article id> --inquiry <inquiry.json>
        [--lens military] [--pages 608-609] [--model claude-sonnet-5-5] [--show]
        [--read [--submit]]

The article comes from curation/article-citations.json: a PDF the curator holds, git-ignored and
in copyright (13d). Its pages are read where they lie and are never stored, logged, or printed.

- Without --read (the default) it is a dry run: for each page it builds the exact request a
  paid reading would send (reader_request: the lens, rule 18, the Questions, Positions and
  holder Works already known) and prices its worst case with the spend meter. No call is made.
- With --read it calls the model, one page at a time, through the metered client: a budget must
  be named (CHRYSTALLUM_BUDGET, 41 §3.8), and the curator's go-ahead is needed for the run. Each
  page's drafts are validated in a transaction that is rolled back, and logged to runs/.
- With --read --submit the page's transcriptions, proposed Questions and Positions, and drafts
  are stored, everything proposed for the curator, and the fact layer is rebuilt (D-144).

What a page yields: the lens's claims and the historiography (Questions, Positions, holdings,
receptions), each draft citing a transcription, the shortest span of the page holding its
quotations (at most 600 characters), checked verbatim here. Nothing else is asked for (notes,
mentions, depicted events and predicate needs rest on a stored passage, and with them the output
grammar passes the API's limit). A holder the graph does not hold as a Work is logged for the
curator, never created.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase
from pydantic import ValidationError

from GraphRevised.adapters.sources import PassageSource
from GraphRevised.harvest.article_citations import ARTICLES, article_pages
from GraphRevised.operations import load_operations
from GraphRevised.proposals.historiography import (HistoriographyOutput, store_historiography, span_of,
                                                   to_historiography, transcription_id, HistoriographyPlan)
from GraphRevised.proposals.lens import load_lens
from GraphRevised.proposals.passage_reader import (CLAIM_OPTIONAL, DEFAULT_MODEL, RUNS_DIRECTORY, Inquiry, _absent,
                                                   _draft, anthropic_client, load_inquiries, proposer,
                                                   read_passage, reader_prompt_version, reader_request)
from GraphRevised.proposals.predicate_needs import load_queue, open_requests_text
from GraphRevised.proposals.registry import load_registry
from GraphRevised.spend_meter import ceiling
from GraphRevised import localdb

ROOT = Path(__file__).resolve().parents[2]

KNOWN = """
MATCH (q:Entity:Question) WHERE NOT coalesce(q.status, "") IN ["deprecated", "rejected"]
RETURN collect(q {.id, .label}) AS questions
"""
POSITIONS = """
MATCH (p:Entity:Position) WHERE NOT coalesce(p.status, "") IN ["deprecated", "rejected"]
OPTIONAL MATCH (a:Assertion {predicate: "answers"})-[:ASSERTION_SUBJECT]->(p)
WHERE a.status IN ["accepted", "proposed"]
OPTIONAL MATCH (a)-[:ASSERTION_OBJECT]->(q:Entity:Question)
RETURN collect(p {.id, .label, questionId: q.id}) AS positions
"""
HOLDERS = """
MATCH (w:Entity:Work) WHERE w.standing IN ["primary", "secondary"]
RETURN collect(w {.id, .label}) AS holders
"""


def historiography_context(tx) -> dict:
    """The Questions, Positions, and holder Works already in the graph (historiography_text)."""
    return {"questions": tx.run(KNOWN).single()["questions"],
            "positions": tx.run(POSITIONS).single()["positions"],
            "holders": sorted(tx.run(HOLDERS).single()["holders"], key=lambda w: w["label"])}


def page_range(text: str) -> tuple[int, int]:
    first, _, last = text.partition("-")
    return int(first), int(last or first)


def licensed_claim_drafts(claims: list[Any], page: str, *, locator: str, model_id: str, inquiry: Inquiry,
                          plan: HistoriographyPlan) -> list[dict[str, Any]]:
    """The lens's own claims, each citing a transcription of the page span holding its quotations
    (added to `plan`); returns the claims refused, with the reason."""
    page = " ".join(page.split())
    refused = []
    for claim in claims:
        claim = _absent(claim, CLAIM_OPTIONAL)
        if inquiry.lens is not None and claim.predicate not in inquiry.lens.predicates:
            refused.append({"claim": claim.model_dump(), "reason": f"{claim.predicate} is not a lens predicate"})
            continue
        quotes = [" ".join(q.split()) for q in (claim.quotation, claim.role_quotation, claim.time_quotation,
                                                 claim.context_quotation) if q]
        span, reason = span_of(page, quotes)
        if span is None:
            refused.append({"claim": claim.model_dump(), "reason": reason})
            continue
        observation = transcription_id(inquiry.work_id, locator, span)
        try:
            draft = _draft(claim, observation, model_id, inquiry)
        except (ValidationError, ValueError) as error:
            refused.append({"claim": claim.model_dump(), "reason": str(error)})
            continue
        # The transcription is the span; the claim's own quotation stays its shortest support.
        if observation not in {t["id"] for t in plan.transcriptions}:
            plan.transcriptions.append({"id": observation, "workId": inquiry.work_id, "locator": locator,
                                        "quote": span})
        plan.drafts.append(draft)
    return refused


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("article", help="an article id in curation/article-citations.json")
    parser.add_argument("--inquiry", required=True, type=Path, help="the inquiry file whose scope the reading uses")
    parser.add_argument("--lens", default="military")
    parser.add_argument("--lens-scope", default="roman-republic")
    parser.add_argument("--pages", default=None, help="printed pages, such as 608-609 (default: the first two)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--show", action="store_true", help="print the prompt, the page itself left out")
    parser.add_argument("--read", action="store_true", help="call the model (paid; needs CHRYSTALLUM_BUDGET)")
    parser.add_argument("--submit", action="store_true", help="with --read: store what validates, all proposed")
    args = parser.parse_args(argv)
    if args.submit and not args.read:
        parser.error("--submit needs --read")
    sys.stdout.reconfigure(encoding="utf-8")

    article = next((a for a in json.loads(ARTICLES.read_text(encoding="utf-8"))["articles"]
                    if a["id"] == args.article), None)
    if article is None:
        parser.error(f"no article {args.article!r} in {ARTICLES.name}")
    pages = dict(article_pages(ROOT / article["pdf"], article.get("skipPages", []), article["firstPage"]))
    first, last = page_range(args.pages) if args.pages else (article["firstPage"], article["firstPage"] + 1)
    lens = replace(load_lens(args.lens, args.lens_scope), requested=open_requests_text(load_queue()))
    registry = load_registry()
    operations = load_operations()
    client = anthropic_client() if args.read else None  # refuses here when no budget is named

    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    log = None
    try:
        with driver.session(database=localdb.database()) as session:
            tx = session.begin_transaction()
            try:
                inquiry = load_inquiries(args.inquiry, tx, briefs=None)[0]
                work = tx.run("MATCH (w:Entity:Work {id: $id}) RETURN w.label AS label, w.standing AS standing",
                              id=article["work"]).single()
                context = historiography_context(tx)
            finally:
                tx.rollback()  # read only
            if work is None:
                parser.error(f"{article['work']} is not a Work in the graph")
            if work["standing"] != "secondary":
                print(f"note: {article['work']} has standing {work['standing']!r}; "
                      "historiography is for modern scholarship")
            # No entity kinds proposed by the lens: depicted events and periods rest on a stored passage.
            inquiry = replace(inquiry, lens=lens, historiography=context, work_id=article["work"], proposable_kinds=(),
                              source={"type": "licensed-pdf", "workId": article["work"]},
                              voice=article.get("citeAs"))
            edition = PassageSource(author=work["label"].split(", ", 1)[0], title=work["label"].split(", ", 1)[-1],
                                    translator=None, citation=article.get("citeAs", article["id"]),
                                    refs=lambda _: [], observation=lambda _: {})
            scope_ids = {e["id"] for e in inquiry.scope}
            holder_ids = {w["id"] for w in context["holders"]} | {article["work"]}
            existing = {q["id"] for q in context["questions"]} | {p["id"] for p in context["positions"]}

            mode = "submit" if args.submit else "read (validated, rolled back)" if args.read else "dry run, no model call"
            print(f"{mode}: {article['citeAs']} pp. {first}-{last}, lens {lens.id}/{lens.scope}, model {args.model}; "
                  f"{len(context['questions'])} questions, {len(context['positions'])} positions, "
                  f"{len(context['holders'])} holder works known")
            if args.read:
                RUNS_DIRECTORY.mkdir(exist_ok=True)
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                log = (RUNS_DIRECTORY / f"article-reader-{args.article}-{stamp}.jsonl").open("w", encoding="utf-8")
                log.write(json.dumps({"article": args.article, "work": article["work"], "inquiry": inquiry.id,
                                      "lens": lens.specialist_id, "model": args.model, "submit": args.submit,
                                      "promptVersion": reader_prompt_version(inquiry),
                                      "registry": registry.version}) + "\n")
            total = Decimal(0)
            for number in range(first, last + 1):
                if number not in pages:
                    print(f"  p. {number}: not in the article")
                    continue
                locator = f"p. {number}"
                before = [(f"p. {number - 1}", pages[number - 1])] if number - 1 in pages else []
                passage = {"id": f"(not stored) {locator}", "passageText": pages[number]}
                request = reader_request(args.model, inquiry, edition, locator, passage, before, registry)
                top = ceiling(args.model, request)
                total += top
                if not args.read:
                    system = sum(len(block["text"]) for block in request["system"])
                    print(f"  {locator}: page {len(pages[number]):,} characters; system and packet {system:,}; "
                          f"output {request['output_format'].__name__}; worst case ${top:.4f}")
                    if args.show:
                        print("\n".join(block["text"] for block in request["system"]))
                        print("[user message: the previous page and this page, not shown]")
                    continue
                known = read_page(session, args, client, inquiry, edition, registry, operations, article, work,
                                  locator, pages[number], before, passage, scope_ids, holder_ids, existing, log)
                # The next page sees this page's Questions and Positions, so it reuses them (44).
                context = {"questions": context["questions"] + known["questions"],
                           "positions": context["positions"] + known["positions"], "holders": context["holders"]}
                inquiry = replace(inquiry, historiography=context)
            if not args.read:
                print(f"worst case for these pages: ${total:.4f} (the ceiling, before caching; nothing was spent)")
    finally:
        if log is not None:
            log.close()
        driver.close()
    return 0


def read_page(session, args, client, inquiry, edition, registry, operations, article, work, locator, page, before,
              passage, scope_ids, holder_ids, existing, log) -> dict[str, list[dict[str, Any]]]:
    """One paid page: read, convert, validate or store, log (quotations only, never the page).
    Returns the Questions and Positions it named that are new to the list the reader is shown."""
    output, meta = read_passage(client, args.model, inquiry, edition, locator, passage, before, registry)
    record: dict[str, Any] = {"page": locator, **{k: v for k, v in meta.items() if k != "historiographyDrafted"}}
    if output is None:
        record["error"] = "refusal or no parsed output"
        log.write(json.dumps(record) + "\n")
        print(f"  {locator}: no output ({meta['stopReason']})")
        return {"questions": [], "positions": []}
    drafted = HistoriographyOutput.model_validate(meta.get("historiographyDrafted") or
                                                  {"questions": [], "positions": [], "holdings": [], "receptions": []})
    plan = to_historiography(drafted, page, work_id=article["work"], locator=locator, scope_ids=scope_ids,
                             work_ids=holder_ids, proposed_by=proposer(inquiry), model_id=meta["model"],
                             prompt_version=reader_prompt_version(inquiry), inquiry_id=inquiry.id, existing=existing)
    refused_claims = licensed_claim_drafts(output.claims, page, locator=locator, model_id=meta["model"],
                                           inquiry=inquiry, plan=plan)
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tx = session.begin_transaction()
    try:
        stored = store_historiography(tx, operations, registry, plan, work_label=work["label"],
                                      edition_citation=article.get("citeAs", article["id"]),
                                      proposed_by=proposer(inquiry), at=at, submit_drafts=args.submit)
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
    existing_before = set(existing)
    existing |= {e["id"] for e in stored["entities"]}  # later pages reuse them
    record |= {"stored": stored, "unresolvedHolders": plan.unresolved_holders, "refused": plan.refused,
               "refusedClaims": refused_claims}
    log.write(json.dumps(record, ensure_ascii=False) + "\n")
    log.flush()
    kept = sum(d["stored"] for d in stored["drafts"])
    print(f"  {locator}: {len(stored['drafts'])} draft(s), {kept} stored; {len(stored['entities'])} question(s) "
          f"and position(s); {len(plan.unresolved_holders)} unresolved holder(s); "
          f"{len(plan.refused) + len(refused_claims)} refused")
    answered = {d["subject"]: d["object"] for d in stored["drafts"] if d["predicate"] == "answers"}
    shown = {"Question": "questions", "Position": "positions"}
    known: dict[str, list[dict[str, Any]]] = {"questions": [], "positions": []}
    for entity in stored["entities"]:
        if entity["id"] not in existing_before:
            item = {"id": entity["id"], "label": entity["label"]}
            if entity["kind"] == "Position":
                item["questionId"] = answered.get(entity["id"])
            known[shown[entity["kind"]]].append(item)
    return known


if __name__ == "__main__":
    raise SystemExit(main())
