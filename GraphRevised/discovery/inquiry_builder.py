"""The inquiry builder: the event source plan's chosen sources become the inquiry's sources.

    python -m GraphRevised.discovery.inquiry_builder GraphRevised/inquiries/actium-battle.json
        [--plan <plan file>] [--apply]

Dry run by default: lists what would be preserved and added. With --apply,
each chosen copy is preserved by its system's adapter under the registry's
rights rule (a Perseus translation public domain in the US by its publication
year; a LacusCurtius page marked public domain by exactly one asterisk; a
Gutenberg book whose catalogue page reads public domain in the USA), opened by
the reader's own interface to prove it can be read, and added to the inquiry
as a source; its Work becomes a proposed Entity with the plan's form; the
inquiry's version goes up; and the briefing agent writes the new sources'
briefs. A copy that cannot be preserved or read is reported and skipped. The
report goes to GraphRevised/runs/.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from neo4j import GraphDatabase

from GraphRevised.adapters import gutenberg_passages, lacuscurtius_passages, perseus_passages
from GraphRevised.adapters.sources import open_source
from GraphRevised.adapters.wikidata_identity import USER_AGENT
from GraphRevised.discovery import source_brief
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.entities import proposed_entity_id
from GraphRevised.proposals.registry import load_registry

GRAPH_REVISED = Path(__file__).resolve().parents[1]
PLANS_DIRECTORY = GRAPH_REVISED / "plans"
RUNS_DIRECTORY = GRAPH_REVISED / "runs"
SOURCE_DIRECTORY = GRAPH_REVISED / "phase-9-source"
CONTEXT_WINDOW = {"before": 2, "after": 1}


def latest_plan(inquiry_id: str) -> Path:
    stem = inquiry_id.rsplit(":", 1)[-1]
    plans = sorted(PLANS_DIRECTORY.glob(f"{stem}-event-sources-*.json"))
    if not plans:
        raise FileNotFoundError(f"no event source plan for {inquiry_id} in {PLANS_DIRECTORY}")
    return plans[-1]


def lacuscurtius_text_pages(home_url: str) -> list[str]:
    response = requests.get(home_url, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    return text_pages(response.content.decode("utf-8", "replace"), home_url)


def text_pages(page: str, home_url: str) -> list[str]:
    """A work's text pages from its home page: pages in the work's own folder (so the same language),
    named by a book or part number, marked public domain (one asterisk); introductions and the like left out."""
    base_tag = re.search(r'(?i)<base\s+href\s*=\s*"\s*([^"]+?)\s*"', page)
    base = base_tag.group(1) if base_tag else home_url.rsplit("/", 1)[0] + "/"
    folder = home_url.rsplit("/", 1)[0] + "/"
    pages = []
    for href in re.findall(r'(?is)<a\s[^>]*?href\s*=\s*"\s*([^"]+?)\s*"', page):
        url = html.unescape(href if href.startswith("http") else base.rstrip("/") + "/" + href.lstrip("/")).split("#")[0]
        name = url.rsplit("/", 1)[-1]
        if url.startswith(folder) and re.match(r"^\d[\w]*\*\.html$", name) and url.count("*") == 1 and url not in pages:
            pages.append(url)
    return pages


def preserve(copy: dict[str, Any], directory: Path, author: str) -> dict[str, Any]:
    """Preserve one chosen copy and return its source configuration (adapters/sources.py)."""
    base = GRAPH_REVISED
    if copy["system"] == "perseus":
        path = perseus_passages.preserve_edition(copy["identifier"], directory)
        return {"type": "perseus-tei", "edition": path.relative_to(base).as_posix()}
    if copy["system"] == "lacuscurtius":
        pages = lacuscurtius_text_pages(copy["identifier"])
        if not pages:
            raise ValueError(f"no public-domain text pages linked from {copy['identifier']}")
        return {"type": "lacuscurtius-html", "author": author,
                "pages": [lacuscurtius_passages.preserve_page(url, directory).relative_to(base).as_posix() for url in pages]}
    if copy["system"] == "gutenberg":
        status = gutenberg_passages._catalog(int(copy["identifier"])).get("copyrightStatus") or ""
        if not status.startswith("Public domain in the USA"):
            raise ValueError(f"Gutenberg {copy['identifier']}: catalogue copyright status {status!r}")
        path = gutenberg_passages.preserve_book(int(copy["identifier"]), directory)
        return {"type": "gutenberg-html", "book": path.relative_to(base).as_posix()}
    raise ValueError(f"no adapter preserves copies from {copy['system']}")


def voice(author: str) -> str:
    """How labels name the source: the author's name as the plan gives it, without a catalogue's inversion."""
    return author.split(",")[0].strip()


def build(inquiry_path: Path, plan: dict[str, Any], *, apply: bool, tx=None, operations=None) -> dict[str, Any]:
    inquiry = json.loads(inquiry_path.read_text(encoding="utf-8"))
    known = {s["workId"] for s in inquiry["sources"]}
    forms = load_registry().work_forms
    report: dict[str, Any] = {"inquiry": inquiry["id"], "fromVersion": inquiry["version"], "added": [], "skipped": []}
    for candidate in plan["candidates"]:
        if candidate["status"] != "chosen":
            continue
        copy = candidate["copies"][candidate["chosenCopy"]]
        label = f"{voice(candidate['author'])}, {candidate['work']}"
        work_id = proposed_entity_id("Work", label)
        entry = {"work": label, "workId": work_id, "copy": copy["label"], "reason": candidate.get("reason")}
        if work_id in known:
            report["skipped"].append({**entry, "why": "already a source of the inquiry"})
            continue
        if not apply:
            report["added"].append({**entry, "dryRun": True})
            continue
        try:
            config = preserve(copy, SOURCE_DIRECTORY, voice(candidate["author"]))
            refs = open_source(config, GRAPH_REVISED).refs(None)
            if not refs:
                raise ValueError("the reader finds no passages in the preserved copy")
        except (ValueError, KeyError, requests.RequestException) as error:
            report["skipped"].append({**entry, "why": str(error)})
            continue
        run_write(tx, operations, "upsert_entity", {
            "id": work_id, "kind": "Work", "label": label, "status": "proposed", "shortLabel": candidate["work"],
            "description": f"{candidate['form']} by {voice(candidate['author'])} ({candidate['composition']}); "
                           f"chosen by the event source plan: {candidate.get('reason') or ''}"[:500]})
        if candidate["form"] in forms:
            run_write(tx, operations, "set_work_form", {"workId": work_id, "form": candidate["form"],
                                                        "allowedForms": sorted(forms)})
        inquiry["sources"].append({**config, "workId": work_id, "voice": voice(candidate["author"]),
                                   "contextWindow": CONTEXT_WINDOW})
        known.add(work_id)
        report["added"].append({**entry, "passages": len(refs), "config": config})
    if apply and report["added"]:
        inquiry["version"] += 1
        inquiry_path.write_bytes((json.dumps(inquiry, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    report["toVersion"] = inquiry["version"]
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inquiry", type=Path)
    parser.add_argument("--plan", type=Path, help="the event source plan (default: the inquiry's latest)")
    parser.add_argument("--apply", action="store_true", help="preserve, add the sources, and write their briefs")
    args = parser.parse_args(argv)

    inquiry = json.loads(args.inquiry.read_text(encoding="utf-8"))
    plan_path = args.plan or latest_plan(inquiry["id"])
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan["inquiry"] != inquiry["id"]:
        raise ValueError(f"{plan_path.name} is a plan for {plan['inquiry']}, not {inquiry['id']}")

    if not args.apply:
        report = build(args.inquiry, plan, apply=False)
    else:
        driver = GraphDatabase.driver(
            os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
            auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
            notifications_min_severity="OFF",
        )
        try:
            with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
                operations = load_operations()
                report = session.execute_write(lambda tx: build(args.inquiry, plan, apply=True, tx=tx, operations=operations))
        finally:
            driver.close()
        for added in report["added"]:
            source_brief.main([str(args.inquiry), "--source", added["workId"]])

    report |= {"plan": plan_path.relative_to(GRAPH_REVISED.parent).as_posix(), "apply": args.apply,
               "createdAt": datetime.now(timezone.utc).isoformat()}
    if args.apply:
        RUNS_DIRECTORY.mkdir(exist_ok=True)
        path = RUNS_DIRECTORY / f"inquiry-builder-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
        path.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(f"report: {path.relative_to(GRAPH_REVISED.parent).as_posix()}")
    for added in report["added"]:
        print(f"{'would add' if not args.apply else 'added'}: {added['work']} <- {added['copy']}"
              + (f" ({added['passages']} passages)" if "passages" in added else ""))
    for skipped in report["skipped"]:
        print(f"skipped: {skipped['work']} ({skipped['why']})")
    print(f"inquiry v{report['fromVersion']} -> v{report['toVersion']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
