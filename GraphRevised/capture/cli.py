"""Capture passages from your reading.

    python -m GraphRevised.capture.cli add --work <work id> --page 12 --quote "..." \\
        [--note "..."] [--type interpretation] [--concerns <entity id>,<entity id>] [--visibility private]

    python -m GraphRevised.capture.cli import <My Clippings.txt | export.csv> --format kindle|readwise \\
        [--concerns <entity id>,...] [--type interpretation] [--dry-run]

`add` records one passage. `import` reads Kindle or Readwise/Reader
highlights, matches each book to a Work through curation/reading.json, and
records each highlight; books not in the mapping are reported, never created.
An imported file is preserved with its hash in GraphRevised/private-sources/
(not in version control). Captures are private unless --visibility says
otherwise. Nothing here creates claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from collections import Counter
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.adapters.wikidata_statements import REPOSITORY_ROOT
from GraphRevised.operations import load_operations

from .core import NOTE_TYPES, CaptureError, capture
from .highlights import match_book, parse_kindle, parse_readwise

GRAPH_REVISED = Path(__file__).resolve().parents[1]
READING_MAPPING = GRAPH_REVISED / "curation" / "reading.json"
PRIVATE_SOURCES = GRAPH_REVISED / "private-sources"


def preserve(path: Path) -> tuple[str, str]:
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    PRIVATE_SOURCES.mkdir(exist_ok=True)
    target = PRIVATE_SOURCES / f"{path.stem}-{digest[:8]}{path.suffix}"
    if not target.exists():
        shutil.copyfile(path, target)
    return target.resolve().relative_to(REPOSITORY_ROOT).as_posix(), digest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add")
    add.add_argument("--work", required=True)
    where = add.add_mutually_exclusive_group(required=True)
    where.add_argument("--page")
    where.add_argument("--location", help="a Kindle location of this edition")
    add.add_argument("--quote", required=True)
    add.add_argument("--edition")
    imported = commands.add_parser("import")
    imported.add_argument("file", type=Path)
    imported.add_argument("--format", required=True, choices=("kindle", "readwise"))
    imported.add_argument("--dry-run", action="store_true")
    add.add_argument("--note")
    for command in (add, imported):
        command.add_argument("--type", choices=NOTE_TYPES)
        command.add_argument("--concerns", default="", help="comma-separated entity IDs")
        command.add_argument("--visibility", default="private", choices=("private", "team", "public"))
        command.add_argument("--by", default="curator")
    args = parser.parse_args(argv)
    concerns = [c for c in args.concerns.split(",") if c]

    if args.command == "add":
        locator = (f"p. {args.page}", "page") if args.page else (f"loc. {args.location}", "kindle-location")
        items = [{"workId": args.work, "locator": locator[0], "locatorType": locator[1], "quote": args.quote,
                  "note": args.note, "noteType": args.type, "concerns": concerns, "edition": args.edition,
                  "capturedBy": args.by, "visibility": args.visibility}]
    else:
        text = args.file.read_text(encoding="utf-8-sig")
        highlights = parse_kindle(text) if args.format == "kindle" else parse_readwise(text)
        books = json.loads(READING_MAPPING.read_text(encoding="utf-8"))["books"]
        items, unmatched = [], Counter()
        payload_uri, digest = (None, None) if args.dry_run else preserve(args.file)
        for highlight in highlights:
            book = match_book(highlight, books)
            if book is None:
                unmatched[f"{highlight.title} ({highlight.author})"] += 1
                continue
            locator, locator_type = highlight.locator
            items.append({"workId": book["workId"], "locator": locator, "locatorType": locator_type,
                          "quote": highlight.text, "note": highlight.note, "noteType": args.type,
                          "concerns": concerns, "edition": book.get("edition"), "language": book.get("language", "en"),
                          "author": highlight.author, "sourceSystem": args.format, "capturedBy": args.by,
                          "capturedAt": highlight.added, "visibility": args.visibility,
                          "rawPayloadUri": payload_uri, "contentHash": digest})
        print(f"{len(highlights)} highlight(s): {len(items)} matched to a Work")
        for book, count in unmatched.most_common():
            print(f"  not in curation/reading.json: {book} ({count})")
        if args.dry_run:
            for item in items[:10]:
                print(f"  {item['workId']} {item['locator']}: {item['quote'][:80]}")
            return 0

    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        notifications_min_severity="OFF",
    )
    operations, written, refused = load_operations(), 0, []
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            for item in items:
                try:
                    result = session.execute_write(lambda tx: capture(tx, operations, item))
                    written += 1
                    if args.command == "add":
                        print(json.dumps(result))
                except CaptureError as error:
                    refused.append(f"{item['locator']}: {error}")
    finally:
        driver.close()
    print(f"captured {written}; refused {len(refused)}")
    for reason in refused:
        print(f"  refused {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
