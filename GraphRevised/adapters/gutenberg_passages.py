"""Passage-level SourceObservations from preserved Project Gutenberg HTML books.

A passage is one paragraph of a chapter (`<h2>` headings "CHAPTER XVII"),
addressed as chapter.paragraph ("17.12"). Printed page numbers
(`<span class="pagenum">`) are kept as the passage's pages, so a locator can
cite the printed edition; footnote markers are left out of the text and the
footnotes kept per paragraph in `editorialNotes` (in a modern book these are
the author's own notes). Front matter, the index, and the footnote section
are not passages.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import requests

from .wikidata_identity import USER_AGENT
from .wikidata_statements import REPOSITORY_ROOT

ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
CHAPTER = re.compile(r"^CHAPTER\s+([IVXLC]+)\b")
STOP_HEADINGS = re.compile(r"^(INDEX|FOOTNOTES|APPENDIX)\b")
LANGUAGES = {"english": "en", "latin": "la", "french": "fr", "german": "de", "italian": "it"}


class PassageNotFound(LookupError):
    """The book has no passage with the requested reference."""


@dataclass(frozen=True)
class Passage:
    text: str
    pages: tuple[str, ...]
    notes: tuple[str, ...]
    chapter_title: str | None


@dataclass(frozen=True)
class Edition:
    path: Path
    ebook: str
    source_uri: str
    author: str
    title: str
    translator: str | None
    citation: str
    language: str
    retrieved_at: str
    content_hash: str
    rights: str
    passages: dict[str, Passage]

    def all_refs(self) -> list[str]:
        return list(self.passages)


def preserve_book(ebook: int, directory: Path) -> Path:
    """Fetch a Gutenberg HTML book once and preserve it byte-for-byte with metadata."""
    existing = sorted(directory.glob(f"gutenberg-{ebook}-*.htm"))
    if existing:
        return existing[-1]
    url = f"https://www.gutenberg.org/files/{ebook}/{ebook}-h/{ebook}-h.htm"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    payload = response.content
    digest = hashlib.sha256(payload).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"gutenberg-{ebook}-{digest[:8]}.htm"
    path.write_bytes(payload)
    header = _header(_decode(payload))
    catalog = _catalog(ebook)
    if not header.get("rights") and catalog.get("copyrightStatus"):
        header["rights"] = f"Project Gutenberg catalogue: {catalog['copyrightStatus']}"
    header["language"] = header.get("language") or LANGUAGES.get((catalog.get("language") or "").lower())
    metadata = {
        "sourceSystem": "Project Gutenberg",
        "sourceUri": url,
        "ebook": str(ebook),
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "contentHash": digest,
        **header,
        "catalog": catalog,
        # The book's own text names the author; the catalogue is recorded beside it, and a
        # disagreement is flagged for the curator rather than resolved here.
        "authorDisagreement": bool(catalog.get("author") and header.get("author")
                                   and _surname(catalog["author"]) != _surname(header["author"])),
    }
    path.with_suffix(".metadata.json").write_bytes((json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return path


def load_edition(path: Path, *, edition: str | None = None) -> Edition:
    payload = path.read_bytes()
    metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    if hashlib.sha256(payload).hexdigest() != metadata["contentHash"]:
        raise ValueError(f"{path.name} does not match its recorded hash")
    parser = _BookParser()
    parser.feed(_decode(payload))
    parser.close()
    passages = {
        ref: Passage(text=_normalize("".join(parts)), pages=tuple(parser.pages[ref]),
                     notes=tuple(parser.note_texts[n] for n in parser.note_refs.get(ref, []) if n in parser.note_texts),
                     chapter_title=parser.chapter_titles.get(ref.split(".")[0]))
        for ref, parts in parser.paragraphs.items()
    }
    passages = {ref: passage for ref, passage in passages.items() if passage.text}
    language = metadata.get("language")
    if not language:
        raise ValueError(f"{path.name} does not state its language")
    citation = "; ".join(part for part in (
        f"{metadata.get('author')}, {metadata.get('title')}", edition,
        f"Project Gutenberg EBook #{metadata['ebook']}") if part)
    return Edition(
        path=path, ebook=metadata["ebook"], source_uri=metadata["sourceUri"], author=metadata.get("author") or "",
        title=metadata.get("title") or "", translator=metadata.get("translator"), citation=citation,
        language=language, retrieved_at=metadata["retrievedAt"], content_hash=metadata["contentHash"],
        rights=metadata.get("rights") or "Rights not stated in the Gutenberg header.", passages=passages,
    )


def section_refs(edition: Edition, selection: str) -> list[str]:
    """Refs within an inclusive "chapter-chapter" range (chapters as numbers)."""
    first, last = (int(n) for n in selection.split("-"))
    return [ref for ref in edition.all_refs() if first <= int(ref.split(".")[0]) <= last]


def passage_observation(edition: Edition, ref: str) -> dict[str, Any]:
    """Return parameters for the `upsert_passage_observation` operation."""
    passage = edition.passages.get(ref)
    if passage is None:
        raise PassageNotFound(f"Gutenberg #{edition.ebook} {ref}")
    chapter, paragraph = ref.split(".")
    pages = "-".join(dict.fromkeys((passage.pages[0], passage.pages[-1]))) if passage.pages else None
    anchor = f"#Page_{passage.pages[0]}" if passage.pages else ""
    where = f"ch. {chapter}, para. {paragraph}" + (f", p. {pages}" if pages else "")
    return {
        "id": f"chr:observation:gutenberg:{edition.ebook}:{ref}:{edition.content_hash[:8]}",
        "label": f"{edition.author}, {edition.title}, {where}",
        "shortLabel": f"{edition.author.split()[-1] if edition.author else 'Gutenberg'} {ref}",
        "sourceSystem": "Project Gutenberg",
        "locator": f"{edition.source_uri}{anchor} ({where})",
        "passageText": passage.text,
        "passageHash": hashlib.sha256(passage.text.encode("utf-8")).hexdigest(),
        "editorialNotes": list(passage.notes),
        "language": edition.language,
        "workTitle": edition.title,
        "author": edition.author,
        "translator": edition.translator,
        "editionCitation": edition.citation,
        "rights": edition.rights,
        "sourceUri": edition.source_uri,
        "sourceRevision": f"gutenberg-{edition.ebook}:{edition.content_hash[:8]}",
        "retrievedAt": edition.retrieved_at,
        "contentHash": edition.content_hash,
        "rawPayloadUri": edition.path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "status": "observed",
    }


def _decode(payload: bytes) -> str:
    head = payload[:4000].decode("ascii", "replace")
    declared = re.search(r'charset=["\']?([\w-]+)', head)
    try:
        return payload.decode(declared.group(1) if declared else "utf-8")
    except (LookupError, UnicodeDecodeError):
        return payload.decode("utf-8", "replace")


def _catalog(ebook: int) -> dict[str, Any]:
    """Fields of the Gutenberg catalogue page: author, language, copyright status, release date."""
    try:
        page = requests.get(f"https://www.gutenberg.org/ebooks/{ebook}", headers={"User-Agent": USER_AGENT}, timeout=60)
        page.raise_for_status()
    except requests.RequestException:
        return {}
    rows = {_normalize(re.sub(r"<[^>]+>", " ", key)): _normalize(re.sub(r"<[^>]+>", " ", value))
            for key, value in re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", page.text, re.S)}
    return {"author": rows.get("Author"), "language": rows.get("Language"),
            "copyrightStatus": rows.get("Copyright") or rows.get("Copyright Status"), "releaseDate": rows.get("Release Date")}


def _surname(name: str) -> str:
    """'Hale, John Richard, 1876-' and 'John Richard Hale' both give 'hale'."""
    name = name.strip()
    word = name.split(",")[0] if "," in name else name.split()[-1]
    return re.sub(r"[^a-z]", "", word.lower())


def _header(html: str) -> dict[str, Any]:
    """Title, author, translator, language, and the licence line: from the Gutenberg header
    when present, else from the book's <title> and <html lang>."""
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "\n", html))

    def field(name: str) -> str | None:
        match = re.search(rf"\b{name}: (.+?)(?= (?:Author|Translator|Editor|Illustrator|Release Date|Posting Date|"
                          rf"Language|Character set encoding|Credits|Most recently updated):|\*\*\*)", text)
        return match.group(1).strip() if match else None

    language = field("Language")
    rights = re.search(r"This (?:e|E)(?:B|b)ook is for the use of anyone anywhere[^.]*\.", text)
    title, author = field("Title"), field("Author")
    page_title = re.search(r"<title>\s*The Project Gutenberg e[Bb]ook of (.+?), by (.+?)\s*</title>", html, re.S)
    if page_title:
        title = title or _normalize(page_title.group(1))
        author = author or _normalize(page_title.group(2)).rstrip(".")
    html_lang = re.search(r'<html[^>]*\blang="([a-z]{2})"', html)
    return {
        "title": title,
        "author": author,
        "translator": field("Translator"),
        "language": LANGUAGES.get((language or "").lower()) or (html_lang.group(1) if html_lang else None),
        "rights": (rights.group(0) + " Public domain in the United States.") if rights else None,
    }


def _roman(numeral: str) -> int:
    total = 0
    for i, char in enumerate(numeral):
        value = ROMAN[char]
        total += -value if i + 1 < len(numeral) and ROMAN[numeral[i + 1]] > value else value
    return total


class _BookParser(HTMLParser):
    """Collect chapter paragraphs with their printed pages, note markers, and footnote texts."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paragraphs: dict[str, list[str]] = {}
        self.pages: dict[str, list[str]] = {}
        self.note_refs: dict[str, list[str]] = {}
        self.note_texts: dict[str, str] = {}
        self.chapter_titles: dict[str, str] = {}
        self.chapter = 0
        self.count = 0
        self.page: str | None = None
        self.stopped = False
        self.in_heading = False
        self.heading: list[str] = []
        self.current: str | None = None
        self.paragraph_depth = 0
        self.skip_tag: str | None = None
        self.skip_depth = 0
        self.footnote_id: str | None = None
        self.footnote_parts: list[str] = []
        self.in_footnotes = False
        self.title_paragraph = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {k.lower(): (v or "") for k, v in attrs}
        css = attributes.get("class", "").lower().split()
        anchor = attributes.get("id", "") or attributes.get("name", "")
        if tag == "a" and re.fullmatch(r"Page_[\w-]+", anchor):
            # Printed page markers sit inside the skipped page-number span.
            self.page = anchor[5:]
            if self.current:
                self.pages[self.current].append(self.page)
            return
        if self.skip_depth:
            if tag == self.skip_tag:
                self.skip_depth += 1
            return
        if tag == "span" and "pagenum" in css:
            self._skip(tag)
            return
        if tag == "div" and ("footnotes" in css or "footnote" in css):
            self.in_footnotes = True
        if tag == "a" and "fnanchor" in css:
            if self.in_footnotes and attributes.get("id", "").startswith("Footnote_"):
                self._close_footnote()
                self.footnote_id = attributes["id"]
            elif self.current:
                target = re.search(r"#(Footnote_[\w-]+)", attributes.get("href", ""))
                if target:
                    self.note_refs.setdefault(self.current, []).append(target.group(1))
            self._skip(tag)
            return
        if tag in ("h1", "h2", "h3"):
            self.in_heading, self.heading = True, []
            return
        if tag == "p" and not self.in_footnotes and not self.stopped and self.chapter:
            if "title" in css:
                self.title_paragraph = True
                self.heading = []
                return
            if not ({"caption", "center"} & set(css)):
                self.count += 1
                self.current = f"{self.chapter}.{self.count}"
                self.paragraphs[self.current] = []
                self.pages[self.current] = [self.page] if self.page else []
                self.paragraph_depth = 1

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            if tag == self.skip_tag:
                self.skip_depth -= 1
            return
        if tag in ("h1", "h2", "h3") and self.in_heading:
            self.in_heading = False
            heading = _normalize("".join(self.heading))
            match = CHAPTER.match(heading)
            if match and not self.stopped:
                self.chapter, self.count = _roman(match.group(1)), 0
                title = _normalize(heading[match.end():]).strip(". ")
                if title:
                    self.chapter_titles[str(self.chapter)] = title
            elif STOP_HEADINGS.match(heading.upper()):
                self.stopped = True
                self.current = None
            return
        if tag == "p":
            if self.title_paragraph:
                self.title_paragraph = False
                self.chapter_titles.setdefault(str(self.chapter), _normalize("".join(self.heading)))
            if self.in_footnotes:
                self._close_footnote()
            self.current = None

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_heading or self.title_paragraph:
            self.heading.append(data + " ")
        elif self.in_footnotes and self.footnote_id:
            self.footnote_parts.append(data)
        elif self.current:
            self.paragraphs[self.current].append(data)
        if "*** END OF" in data:
            self.stopped = True
            self.current = None

    def close(self) -> None:
        super().close()
        self._close_footnote()

    def _skip(self, tag: str) -> None:
        self.skip_tag, self.skip_depth = tag, 1

    def _close_footnote(self) -> None:
        if self.footnote_id:
            self.note_texts[self.footnote_id] = _normalize("".join(self.footnote_parts))
        self.footnote_id, self.footnote_parts = None, []


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub("[​⁠﻿]", "", text)).strip()
