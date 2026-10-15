"""Passage-level SourceObservations from preserved LacusCurtius HTML pages.

LacusCurtius (Bill Thayer, penelope.uchicago.edu) transcribes public-domain
Loeb translations as one HTML page per book, with anchors for chapters
(`<A CLASS="chapter" NAME="31">`) and sections (`<A CLASS="sec"
NAME="31.1">`). A page is in the public domain only when its URL has exactly
one asterisk; the page states what it reproduces.

The passage text excludes page numbers and note markers. The Loeb editor's
endnotes are kept per section in `editorialNotes`, so a modern editor's note
is never cited as the ancient author's text.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import requests

from .wikidata_identity import USER_AGENT
from .wikidata_statements import REPOSITORY_ROOT

# LacusCurtius keeps texts by language in the path: /Thayer/E/ English, /Thayer/L/ Latin, /Thayer/G/ Greek.
PATH_LANGUAGES = {"E": "en", "L": "la", "G": "grc"}

REPRODUCES = re.compile(
    r"This webpage reproduces (?:a|an|the) (?:Book|Part|Chapter)?\s*(?:of )?(?P<title>.+?) by (?P<author>.+?) "
    r"published in (?P<publication>.+?\d{4})"
)
# Some works name no author in the statement ("a section of The Res Gestae ... as published in ...");
# the author then comes from the source configuration.
REPRODUCES_UNSIGNED = re.compile(
    r"This webpage reproduces (?:a|an|the) (?:section|Book|Part|Chapter)\s+of (?P<title>.+?) "
    r"as published in (?P<publication>.+?\d{4})"
)


class PassageNotFound(LookupError):
    """No preserved page has a section with the requested reference."""


@dataclass(frozen=True)
class Page:
    book: str
    path: Path
    source_uri: str
    retrieved_at: str
    content_hash: str
    page_updated: str | None
    public_domain_statement: str | None
    sections: dict[str, str]  # "31.1" -> text
    notes: dict[str, list[str]]  # "31.1" -> editorial notes referenced there


@dataclass(frozen=True)
class Edition:
    """One work across its preserved book pages."""

    author: str
    title: str
    translator: str | None
    citation: str
    work_slug: str
    language: str
    pages: tuple[Page, ...] = field(default_factory=tuple)

    def all_refs(self) -> list[str]:
        return [f"{page.book}.{ref}" for page in self.pages for ref in page.sections]


def preserve_page(url: str, directory: Path) -> Path:
    """Fetch a public-domain page once and preserve it byte-for-byte with metadata."""
    if url.count("*") != 1:
        raise ValueError(f"{url} is not marked public domain (exactly one asterisk)")
    existing = sorted(directory.glob(f"lacuscurtius-{_slug(url)}-*.html"))
    if existing:
        return existing[-1]
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    payload = response.content
    digest = hashlib.sha256(payload).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"lacuscurtius-{_slug(url)}-{digest[:8]}.html"
    path.write_bytes(payload)
    text = _plain(payload.decode("utf-8", "replace"))
    updated = re.search(r"Page updated: ([^<]+?\d{2})\b", text)
    rights = REPRODUCES.search(text) or REPRODUCES_UNSIGNED.search(text)
    metadata = {
        "sourceSystem": "LacusCurtius",
        "sourceUri": url,
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "contentHash": digest,
        "pageUpdated": updated.group(1).strip() if updated else None,
        "reproduces": rights.group(0) if rights else None,
        "publicDomainStatement": "The text is in the public domain." if "The text is in the public domain" in text else None,
        "proofread": "This text has not yet been proofread" not in text,
    }
    path.with_suffix(".metadata.json").write_bytes((json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return path


def load_edition(paths: list[Path], *, translator: str | None = None, language: str | None = None,
                 author: str | None = None) -> Edition:
    """Load preserved pages. The language comes from `language` or the page's /Thayer/<letter>/ path;
    the author from the page's statement of what it reproduces, else from `author`."""
    pages = [_load_page(path) for path in paths]
    if not pages:
        raise ValueError("no pages")
    if language is None:
        letter = re.search(r"/Thayer/([A-Z])/", pages[0].source_uri)
        language = PATH_LANGUAGES.get(letter.group(1)) if letter else None
        if language is None:
            raise ValueError(f"the language of {pages[0].source_uri} is not known; give it in the source config")
    first = pages[0].path.read_bytes().decode("utf-8", "replace")
    match = REPRODUCES.search(_plain(first))
    unsigned = None if match else REPRODUCES_UNSIGNED.search(_plain(first))
    if not match and not (unsigned and author):
        raise ValueError(f"{pages[0].path.name} does not say what it reproduces"
                         + (" or by whom; give the author in the source config" if unsigned else ""))
    match = match or unsigned
    citation = "; ".join(part for part in (
        f"{match['title']}", f"trans. {translator}" if translator else None, match["publication"],
        "transcribed by Bill Thayer, LacusCurtius",
    ) if part)
    return Edition(
        author=match.groupdict().get("author") or author, title=match["title"], translator=translator, citation=citation,
        work_slug=_work_slug(pages[0].source_uri), language=language, pages=tuple(pages),
    )


def section_refs(edition: Edition, selection: str) -> list[str]:
    """Refs within an inclusive "book.chapter-book.chapter" range, in page order."""
    start, end = (tuple(int(n) for n in part.split(".")) for part in selection.split("-"))
    return [ref for ref in edition.all_refs() if start <= tuple(int(n) for n in ref.split(".")[:2]) <= end]


def passage_observation(edition: Edition, ref: str) -> dict[str, Any]:
    """Return parameters for the `upsert_passage_observation` operation."""
    book, local = ref.split(".", 1)
    page = next((p for p in edition.pages if p.book == book and local in p.sections), None)
    if page is None:
        raise PassageNotFound(f"{edition.work_slug} {ref}")
    text = page.sections[local]
    return {
        "id": f"chr:observation:lacuscurtius:{edition.work_slug}:{ref}:{page.content_hash[:8]}",
        "label": f"{edition.author}, {edition.title} {ref} ({edition.translator or 'translation'})",
        "shortLabel": f"{edition.author} {ref}",
        "sourceSystem": "LacusCurtius",
        "locator": f"{page.source_uri}#{local}",
        "passageText": text,
        "passageHash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "editorialNotes": page.notes.get(local, []),
        "language": edition.language,
        "workTitle": edition.title,
        "author": edition.author,
        "translator": edition.translator,
        "editionCitation": edition.citation,
        "rights": f"{page.public_domain_statement or 'Rights not stated on the page.'} ({edition.citation})",
        "sourceUri": page.source_uri,
        "sourceRevision": f"{page.page_updated or 'undated'}:{page.content_hash[:8]}",
        "retrievedAt": page.retrieved_at,
        "contentHash": page.content_hash,
        "rawPayloadUri": page.path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "status": "observed",
    }


def _load_page(path: Path) -> Page:
    payload = path.read_bytes()
    metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    if hashlib.sha256(payload).hexdigest() != metadata["contentHash"]:
        raise ValueError(f"{path.name} does not match its recorded hash")
    parser = _BookParser()
    parser.feed(payload.decode("utf-8", "replace"))
    parser.close()
    sections = {ref: _normalize("".join(parts)) for ref, parts in parser.sections.items()}
    notes = {ref: [parser.note_texts[n] for n in ids if n in parser.note_texts] for ref, ids in parser.note_refs.items()}
    # The book is the page's number; a book split over pages adds a letter (2A*.html ... 2D*.html).
    book = re.search(r"/(\d+)[A-Z]?\*\.html", metadata["sourceUri"])
    return Page(
        book=book.group(1) if book else path.stem, path=path, source_uri=metadata["sourceUri"],
        retrieved_at=metadata["retrievedAt"], content_hash=metadata["contentHash"],
        page_updated=metadata.get("pageUpdated"), public_domain_statement=metadata.get("publicDomainStatement"),
        sections={k: v for k, v in sections.items() if v}, notes=notes,
    )


class _BookParser(HTMLParser):
    """Collect section text, note markers per section, and the endnotes' text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: dict[str, list[str]] = {}
        self.note_refs: dict[str, list[str]] = {}
        self.note_texts: dict[str, str] = {}
        self.current: str | None = None
        self.skip_depth = 0  # inside an anchor numeral, page number, or note marker
        self.skip_tag: str | None = None
        self.in_endnotes = False
        self.note_id: str | None = None
        self.note_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {k.lower(): (v or "") for k, v in attrs}
        css = attributes.get("class", "").lower()
        if tag == "hr" and css == "endnotes":
            self.in_endnotes, self.current = True, None
            return
        if self.in_endnotes:
            if tag == "a" and css == "note":
                self._close_note()
                self.note_id = attributes.get("id")
                self._skip(tag)
            elif tag == "p" and css == "ivy":
                self._close_note()
            return
        if tag == "a" and css == "chapter":
            self.current = f"{attributes.get('name')}.1"
            self._skip(tag)
        elif tag == "a" and css == "sec":
            self.current = attributes.get("name")
            self._skip(tag)
        elif tag == "span" and css == "pagenum":
            self._skip(tag)
        elif tag == "a" and css == "ref":
            if self.current:
                note = re.search(r"#(note\d+)", attributes.get("href", ""))
                if note:
                    self.note_refs.setdefault(self.current, []).append(note.group(1))
            self._skip(tag)
        elif self.skip_depth and tag == self.skip_tag:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth and tag == self.skip_tag:
            self.skip_depth -= 1
            if not self.skip_depth:
                self.skip_tag = None

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_endnotes:
            if self.note_id:
                self.note_parts.append(data)
        elif self.current:
            self.sections.setdefault(self.current, []).append(data)

    def close(self) -> None:
        super().close()
        self._close_note()

    def _skip(self, tag: str) -> None:
        self.skip_tag, self.skip_depth = tag, 1

    def _close_note(self) -> None:
        if self.note_id:
            self.note_texts[self.note_id] = _normalize("".join(self.note_parts))
        self.note_id, self.note_parts = None, []


def _plain(html: str) -> str:
    return _normalize(re.sub(r"<[^>]+>", " ", html))


def _normalize(text: str) -> str:
    """Collapse whitespace and drop zero-width characters left where note markers were."""
    return re.sub(r"\s+", " ", re.sub("[\u200b\u2060\ufeff]", "", text)).strip()


def _slug(url: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", url.split("/Texts/", 1)[-1].lower()).strip("-")


def _work_slug(url: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", url.split("/Texts/", 1)[-1].rsplit("/", 1)[0].lower()).strip("-")
