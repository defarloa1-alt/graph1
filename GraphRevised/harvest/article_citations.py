"""A modern article's ancient citations, as leads (D-148, 42 §5).

    python -m GraphRevised.harvest.article_citations <article id> [--save]

Reads a licensed article PDF named in curation/article-citations.json (git-ignored,
in copyright: only citations and page numbers leave it, never its text) and finds
each citation of an ancient Work, such as "50.15, 30.3-4" after an abbreviation
from curation/citation-aliases.json. A shorter locator borrows the leading parts of
the one before it (book 50 in that example), and an abbreviated range end is
filled in (33-4 is 33-34). Each citation is one of:

- **held, passage held**: an ancient Work we hold, and our passages at that locator;
- **held, passage not held**: the Work is ours but not that passage (a passage to fetch);
- **not held**: an ancient Work we do not hold (a source to acquire);
- **unresolved**: one bare number where a locator needs more (often a note number
  printed after the abbreviation), shown for the curator, never followed.

Modern works cited in full ("Name, Title (City, Year)") are listed too, by pattern,
for the curator to check. Nothing is written to the graph: these are leads for the
lens reading of the article, whose claims will rest on the passages found here.
With --save the report goes to runs/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from GraphRevised.harvest.wikipedia_footnotes import HELD, OBSERVATION_REF, _numbers, within
from GraphRevised import localdb

GRAPH_REVISED = Path(__file__).resolve().parents[1]
ARTICLES = GRAPH_REVISED / "curation" / "article-citations.json"
ALIASES = GRAPH_REVISED / "curation" / "citation-aliases.json"
RUNS = GRAPH_REVISED / "runs"
# Lines a download service stamps on every page (who downloaded it, when, from where): never read.
STAMP = re.compile(r"This content downloaded from|All use subject to|^\s*\d{1,3}(?:\.\d{1,3}){3} on ", re.I)
ONE = r"\d+(?:\.\d+)*[a-z]?(?:\s*[–-]\s*\d+(?:\.\d+)*)?"
LOCATORS = re.compile(rf"\s*({ONE}(?:\s*,\s*{ONE})*)")
MODERN = re.compile(r"((?:[A-Z]\.\s?)+(?:[a-z]+\s)?[A-Z][\w'’-]+(?:\s(?:and|&)\s(?:[A-Z]\.\s?)+[A-Z][\w'’-]+)?),"
                    r"\s([^()]{4,160}?)\s\(([^()]{0,60}?\b1[5-9]\d\d|[^()]{0,60}?\b20\d\d)[a-z0-9]*\)")


def article_pages(pdf: Path, skip: list[int], first_page: int) -> list[tuple[int, str]]:
    """(printed page, text) for each article page, stamps removed and split numbers joined (50. 13. 8)."""
    import pypdf

    pages = []
    for index, page in enumerate(pypdf.PdfReader(pdf).pages):
        if index in skip:
            continue
        lines = [line for line in (page.extract_text() or "").splitlines() if not STAMP.search(line)]
        text = re.sub(r"(\d)\.\s+(?=\d)", r"\1.", " ".join(lines))
        text = re.sub(r"-\s+(?=[a-z])", "", text)  # a word broken across lines
        pages.append((first_page + len(pages), re.sub(r"\s+", " ", text)))
    return pages


def expand(text: str, depth: int) -> list[tuple[str, tuple[int, ...], tuple[int, ...]]]:
    """Each locator in a list ("50.15, 30.3-4") as (as written, start, end), shorter ones completed
    from the one before; an abbreviated range end is filled in (33-4 is 33-34)."""
    found, before = [], ()
    for piece in (p.strip() for p in text.split(",") if p.strip()):
        head, _, tail = (s.strip() for s in re.split(r"([–-])", piece, maxsplit=1)) if re.search(r"[–-]", piece) \
            else (piece, "", "")
        start = _numbers(re.sub(r"[a-z]$", "", head))
        if not start:
            continue
        if len(start) < depth and before:
            start = before[:depth - len(start)] + start
        end = start
        if tail:
            parts = _numbers(tail)
            if parts:
                last, written = str(start[-1]), str(parts[-1])
                if len(parts) == 1 and len(written) < len(last):
                    parts = (int(last[:len(last) - len(written)] + written),)
                end = start[:len(start) - len(parts)] + parts
                if end < start:  # a note number run into the range ("33-4.67" is 33-34, then note 67)
                    written = str(parts[0])
                    end = start[:-1] + (int(last[:max(len(last) - len(written), 0)] + written),)
        found.append((piece, start, end))
        before = start
    return found


def citations(pages: list[tuple[int, str]], table: dict[str, Any]) -> list[dict[str, Any]]:
    held = [(alias, work) for work, names in table["works"].items() for alias in names]
    names = sorted([*held, *((n, None) for n in table["notHeld"])], key=lambda x: -len(x[0]))
    pattern = re.compile(r"(?<![\w.])(" + "|".join(re.escape(n) for n, _ in names) + r")(?=[\s\d])")
    work_of = dict(names)
    found = []
    for page, text in pages:
        for match in pattern.finditer(text):
            locs = LOCATORS.match(text, match.end())
            if not locs:
                continue
            alias, work = match.group(1), work_of[match.group(1)]
            depth = table.get("locatorDepth", {}).get(work, 3)
            for written, start, end in expand(locs.group(1), depth):
                shown = ".".join(map(str, start)) + (f"-{'.'.join(map(str, end[len(end) - 1:]))}" if end != start else "")
                found.append({"page": page, "alias": alias, "cited": f"{alias} {shown}", "written": written,
                              "work": work, "start": start, "end": end,
                              # one bare number where a full locator has more parts is no locator at all,
                              # most often a note number printed after the abbreviation
                              "incomplete": len(start) < min(depth, 2)})
    return found


def resolve(found: list[dict[str, Any]], held: dict[str, list[tuple[tuple[int, ...], str]]]) -> None:
    for c in found:
        if c["incomplete"]:
            c["kind"], c["passages"] = "unresolved", []
            continue
        if c["work"] is None:
            c["kind"], c["passages"] = "not held", []
            continue
        c["passages"] = [oid for nums, oid in held.get(c["work"], []) if within(nums, c["start"], c["end"])]
        c["kind"] = "held, passage held" if c["passages"] else "held, passage not held"


def modern_works(pages: list[tuple[int, str]]) -> list[dict[str, Any]]:
    seen, works = set(), []
    for page, text in pages:
        for m in MODERN.finditer(text):
            key = (m.group(1), m.group(3)[-4:])
            if key not in seen:
                seen.add(key)
                works.append({"page": page, "author": m.group(1), "title": m.group(2).strip(), "published": m.group(3)})
    return works


def held_passages(tx, works: set[str]) -> dict[str, list[tuple[tuple[int, ...], str]]]:
    return {w: [(_numbers(m.group(1)), r["id"]) for r in tx.run(HELD, work=w)
                for m in [OBSERVATION_REF.search(r["id"])] if m] for w in works}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("article", help="an article id in curation/article-citations.json")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    config = next((a for a in json.loads(ARTICLES.read_text(encoding="utf-8"))["articles"] if a["id"] == args.article),
                  None)
    if config is None:
        parser.error(f"{args.article} is not in {ARTICLES.name}")
    table = json.loads(ALIASES.read_text(encoding="utf-8"))
    pages = article_pages(GRAPH_REVISED.parent / config["pdf"], config["skipPages"], config["firstPage"])
    found = citations(pages, table)
    driver = GraphDatabase.driver(localdb.uri(),
                                  auth=localdb.auth(),
                                  notifications_min_severity="OFF")
    try:
        with driver.session(database=localdb.database()) as session:
            held = session.execute_read(held_passages, {c["work"] for c in found if c["work"]})
    finally:
        driver.close()
    resolve(found, held)
    modern = modern_works(pages)

    kinds = Counter(c["kind"] for c in found)
    print(f"{config['citeAs']}: {len(pages)} pages, {len(found)} ancient citations "
          f"({', '.join(f'{n} {k}' for k, n in kinds.most_common())}), {len(modern)} modern works by pattern")
    by_work: dict[str, list[dict]] = defaultdict(list)
    for c in found:
        by_work[c["work"] or c["alias"]].append(c)
    for work, items in sorted(by_work.items(), key=lambda x: -len(x[1])):
        print(f"\n  {work}  ({len(items)})")
        for c in items:
            mark = {"held, passage held": "have", "held, passage not held": "FETCH", "not held": "ACQUIRE",
                    "unresolved": f"unresolved: '{c['written']}' is not a full locator"}[c["kind"]]
            print(f"    p.{c['page']}  {c['cited']:28} {mark}" + (f"  {len(c['passages'])} passage(s)" if c["passages"] else ""))
    print("\n  modern works cited in full (by pattern; check):")
    for w in modern:
        print(f"    p.{w['page']}  {w['author']}, {w['title'][:70]} ({w['published']})")
    if args.save:
        RUNS.mkdir(exist_ok=True)
        out = RUNS / f"article-citations-{args.article}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
        out.write_text(json.dumps({"article": config, "citations": found, "modern": modern},
                                  indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nsaved {out.relative_to(GRAPH_REVISED.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
