"""Reading highlights from Kindle (`My Clippings.txt`) and Readwise/Reader (CSV export).

Both become one shape: book title and author, highlight text, the reader's
note if any, a locator (page when given, else Kindle location), and when it
was highlighted. Matching a book to a Work entity is a curated mapping
(curation/reading.json); an unmatched book is reported, never created.
"""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from typing import Any

KINDLE_SEPARATOR = "=========="
KINDLE_META = re.compile(
    r"^- Your (?P<kind>Highlight|Note|Bookmark)\b(?: on page (?P<page>[\w-]+))?"
    r"(?:.*?[Ll]ocation (?P<start>\d+)(?:-(?P<end>\d+))?)?(?:.*?Added on (?P<added>.+))?$"
)


@dataclass
class Highlight:
    title: str
    author: str | None
    text: str
    page: str | None = None
    location_start: int | None = None
    location_end: int | None = None
    added: str | None = None
    note: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def locator(self) -> tuple[str, str]:
        """(locator, locator type): the page when known, else the Kindle location."""
        if self.page:
            return f"p. {self.page}", "page"
        if self.location_start is not None:
            end = f"-{self.location_end}" if self.location_end and self.location_end != self.location_start else ""
            return f"loc. {self.location_start}{end}", "kindle-location"
        return "unknown", "unknown"


def parse_kindle(text: str) -> list[Highlight]:
    """Highlights from My Clippings.txt, with each note attached to the highlight it falls in."""
    highlights: list[Highlight] = []
    notes: list[Highlight] = []
    for block in text.lstrip("﻿").split(KINDLE_SEPARATOR):
        lines = [line.strip() for line in block.strip().splitlines()]
        if len(lines) < 2:
            continue
        title, author = _title_author(lines[0])
        meta = KINDLE_META.match(lines[1])
        if not meta or meta["kind"] == "Bookmark":
            continue
        body = " ".join(line for line in lines[2:] if line)
        if not body:
            continue
        item = Highlight(
            title=title, author=author, text=body, page=meta["page"],
            location_start=int(meta["start"]) if meta["start"] else None,
            location_end=int(meta["end"] or meta["start"]) if meta["start"] else None,
            added=meta["added"].strip() if meta["added"] else None,
        )
        (notes if meta["kind"] == "Note" else highlights).append(item)
    for note in notes:
        target = next((h for h in highlights if h.title == note.title and h.location_start is not None
                       and note.location_start is not None
                       and h.location_start <= note.location_start <= (h.location_end or h.location_start)), None)
        if target is not None:
            target.note = f"{target.note}\n{note.text}" if target.note else note.text
    return highlights


def parse_readwise(text: str) -> list[Highlight]:
    """Highlights from a Readwise/Reader CSV export."""
    highlights = []
    for row in csv.DictReader(io.StringIO(text.lstrip("﻿"))):
        body = (row.get("Highlight") or "").strip()
        if not body:
            continue
        location_type = (row.get("Location Type") or "").strip().lower()
        location = (row.get("Location") or "").strip()
        highlights.append(Highlight(
            title=(row.get("Book Title") or "").strip(),
            author=(row.get("Book Author") or "").strip() or None,
            text=body,
            page=location if location_type == "page" and location else None,
            location_start=int(location) if location_type in ("location", "order") and location.isdigit() else None,
            added=(row.get("Highlighted at") or "").strip() or None,
            note=(row.get("Note") or "").strip() or None,
            extra={"tags": (row.get("Tags") or "").strip()},
        ))
    return highlights


def match_book(highlight: Highlight, books: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The curated mapping entry for a highlight's book: titles compared case-insensitively,
    the mapping's title being a prefix of the export's (exports often add subtitles)."""
    title = _normalize(highlight.title)
    for book in books:
        if title.startswith(_normalize(book["title"])):
            if book.get("author") and highlight.author and _normalize(book["author"]) not in _normalize(highlight.author):
                continue
            return book
    return None


def _title_author(line: str) -> tuple[str, str | None]:
    line = line.lstrip("﻿")
    match = re.match(r"^(?P<title>.*)\((?P<author>[^()]*)\)\s*$", line)
    return (match["title"].strip(), match["author"].strip()) if match else (line.strip(), None)


def _normalize(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()
