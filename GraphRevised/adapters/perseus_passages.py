"""Passage-level SourceObservations from a preserved Perseus TEI edition.

The passage text excludes editorial notes: in Perseus translations a `<note>`
is the modern editor's or translator's scholarship, not the ancient author's
text. Notes are kept separately so they are never cited as the source.

A passage is a deepest text division, at any depth (chapter.section in a Life,
book.card in a poem, book.chapter.section in a geography), its ref the divisions'
numbers joined by dots. Divisions numbered without a digit (front matter, a
translator's preface or argument) are apparatus, not the author's text, and are
not passages.
"""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from .wikidata_identity import USER_AGENT
from .wikidata_statements import REPOSITORY_ROOT

TEI = "{http://www.tei-c.org/ns/1.0}"
NS = {"t": TEI[1:-1]}
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
# TEI uses ISO 639-2 codes; observations use ISO 639-1 where one exists.
LANGUAGE_CODES = {"eng": "en", "lat": "la", "deu": "de", "ger": "de", "fre": "fr", "fra": "fr", "ita": "it"}


class PassageNotFound(LookupError):
    """The edition has no section with the requested reference."""


@dataclass(frozen=True)
class Edition:
    path: Path
    cts_urn: str
    title: str
    author: str
    translator: str | None
    citation: str
    licence: str | None
    source_commit: str
    content_hash: str
    root: ET.Element
    language: str
    rights: str | None = None  # the preserved metadata's rights statement, when recorded


def load_edition(path: Path, *, source_commit: str, rights: str | None = None, cts_urn: str | None = None) -> Edition:
    payload = path.read_bytes()
    root = ET.fromstring(payload)
    text_element = root.find(".//t:text", NS)
    language = text_element.get(XML_LANG) if text_element is not None else None
    if not language:
        raise ValueError(f"{path.name} does not declare the language of its text")
    title_stmt = root.find(".//t:titleStmt", NS)
    translator = title_stmt.find("t:editor[@role='translator']", NS)
    edition_div = root.find(".//t:body/t:div", NS)
    monogr = root.find(".//t:sourceDesc//t:monogr", NS)
    imprint = monogr.find("t:imprint", NS)
    volume = monogr.find("t:biblScope[@unit='volume']", NS)
    series = root.find(".//t:sourceDesc//t:series/t:title", NS)
    citation = "; ".join(
        part
        for part in (
            _text(monogr.find("t:title", NS)),
            f"trans. {_text(translator)}" if translator is not None else None,
            series is not None and _text(series),
            volume is not None and f"vol. {_text(volume)}",
            ", ".join(_text(p) for p in imprint.findall("t:publisher", NS)),
            _text(imprint.find("t:date", NS)),
        )
        if part
    )
    licence = root.find(".//t:availability/t:licence", NS)
    return Edition(
        path=path,
        cts_urn=edition_div.get(f"{TEI}n") or edition_div.get("n") or cts_urn,
        title=_text(title_stmt.find("t:title", NS)),
        author=_text(title_stmt.find("t:author", NS)),
        translator=_text(translator) if translator is not None else None,
        citation=citation,
        licence=licence.get("target") if licence is not None else None,
        source_commit=source_commit,
        content_hash=hashlib.sha256(payload).hexdigest(),
        root=root,
        language=LANGUAGE_CODES.get(language, language),
        rights=rights,
    )


def passages(edition: Edition) -> list[tuple[str, ET.Element]]:
    """Every passage in document order: (ref, its deepest text division)."""
    found: list[tuple[str, ET.Element]] = []

    def walk(element: ET.Element, numbers: list[str]) -> None:
        divisions = element.findall("t:div", NS)
        if not divisions:
            if numbers:
                found.append((".".join(numbers), element))
            return
        for division in divisions:
            n = division.get("n") or ""
            if re.search(r"\d", n):
                walk(division, numbers + [n])

    walk(edition.root.find(".//t:body/t:div", NS), [])
    return found


_INDEXES: dict[str, dict[str, ET.Element]] = {}


def _index(edition: Edition) -> dict[str, ET.Element]:
    """The passages by ref, built once per edition (by its hash)."""
    if edition.content_hash not in _INDEXES:
        _INDEXES[edition.content_hash] = dict(passages(edition))
    return _INDEXES[edition.content_hash]


def section_refs(edition: Edition, chapters: range) -> list[str]:
    """The passages whose first number (the chapter, or the book) is in the range."""
    return [ref for ref, _ in passages(edition) if ref.split(".")[0].isdigit() and int(ref.split(".")[0]) in chapters]


def passage_observation(edition: Edition, ref: str, *, retrieved_at: str, source_uri: str) -> dict[str, Any]:
    """Return parameters for the `upsert_passage_observation` operation."""
    section = _index(edition).get(ref)
    if section is None:
        raise PassageNotFound(f"{edition.cts_urn}:{ref}")

    text, notes = _section_text(section)
    locator = f"{edition.cts_urn}:{ref}"
    work_slug = edition.cts_urn.rsplit(":", 1)[-1]
    return {
        "id": f"chr:observation:perseus:{work_slug}:{ref}:{edition.source_commit[:8]}",
        "label": f"{edition.author}, {edition.title} {ref} ({edition.translator or 'original'})",
        "shortLabel": f"{edition.author} {edition.title} {ref}",
        "sourceSystem": "Perseus",
        "locator": locator,
        "passageText": text,
        "passageHash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "editorialNotes": notes,
        "language": edition.language,
        "workTitle": edition.title,
        "author": edition.author,
        "translator": edition.translator,
        "editionCitation": edition.citation,
        "rights": edition.rights or f"rights not recorded; TEI markup {edition.licence or 'licence unknown'}",
        "sourceUri": source_uri,
        "sourceRevision": edition.source_commit,
        "retrievedAt": retrieved_at,
        "contentHash": edition.content_hash,
        "rawPayloadUri": edition.path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "status": "observed",
    }


def normalize(text: str) -> str:
    """Whitespace-normalized text used for passage storage and quote matching."""
    return re.sub(r"\s+", " ", text).strip()


def _section_text(section: ET.Element) -> tuple[str, list[str]]:
    parts: list[str] = []
    notes: list[str] = []

    def walk(element: ET.Element) -> None:
        if element.tag == f"{TEI}note":
            notes.append(normalize("".join(element.itertext())))
        else:
            parts.append(element.text or "")
            for child in element:
                walk(child)
        parts.append(element.tail or "")

    parts.append(section.text or "")
    for child in section:
        walk(child)
    return normalize("".join(parts)), notes


def _text(element: ET.Element | None) -> str:
    return normalize("".join(element.itertext())) if element is not None else ""


# The Perseus repositories whose README licenses all their contents CC BY-SA 4.0 (checked 2026-10-15,
# curation/sources.json); editions in other repositories carry their own terms and are not preserved here.
REPOSITORIES = {"greekLit": "PerseusDL/canonical-greekLit", "latinLit": "PerseusDL/canonical-latinLit"}
MARKUP_RIGHTS = ("TEI markup CC BY-SA 4.0, Perseus Digital Library, Tufts University; redistribution of this "
                 "file requires attribution and the same licence.")


def public_domain_in_us(year: int, today: datetime | None = None) -> bool:
    """Published more than 95 years before this year (US term for works published 1929 and later)."""
    return year <= (today or datetime.now(timezone.utc)).year - 96


def preserve_edition(edition_urn: str, directory: Path) -> Path:
    """Fetch a Perseus TEI edition at the repository's current commit, once, with its metadata.

    Refused unless the repository licenses its contents openly and the translation's own
    publication year makes it public domain in the US."""
    namespace, rest = edition_urn.removeprefix("urn:cts:").split(":", 1)
    if namespace not in REPOSITORIES:
        raise ValueError(f"{edition_urn}: no openly licensed Perseus repository for {namespace}")
    repository = REPOSITORIES[namespace]
    textgroup, work, _ = rest.split(".", 2)
    commit = requests.get(f"https://api.github.com/repos/{repository}/commits/master",
                          headers={"User-Agent": USER_AGENT}, timeout=60).json()["sha"]
    path = directory / f"perseus-{rest}-{commit}.xml"
    if path.exists():
        return path
    file_path = f"data/{textgroup}/{work}/{rest}.xml"
    source_uri = f"https://raw.githubusercontent.com/{repository}/{commit}/{file_path}"
    response = requests.get(source_uri, headers={"User-Agent": USER_AGENT}, timeout=120)
    response.raise_for_status()
    payload = response.content
    root = ET.fromstring(payload)
    imprint_date = root.find(".//t:sourceDesc//t:imprint/t:date", NS)
    years = [int(y) for y in re.findall(r"\b(1[5-9]\d\d|20\d\d)\b", _text(imprint_date))]
    if not years or not public_domain_in_us(max(years)):
        raise ValueError(f"{edition_urn}: the edition's publication year ({_text(imprint_date) or 'none'}) "
                         "does not make it public domain in the US")
    directory.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    translator = root.find(".//t:titleStmt/t:editor[@role='translator']", NS)
    metadata = {
        "sourceSystem": "Perseus",
        "repository": repository,
        "path": file_path,
        "sourceRevision": commit,
        "sourceUri": source_uri,
        "ctsUrn": edition_urn,
        "work": f"{_text(root.find('.//t:titleStmt/t:author', NS))}, {_text(root.find('.//t:titleStmt/t:title', NS))}",
        "translator": _text(translator) or None,
        "edition": _text(root.find(".//t:sourceDesc//t:monogr/t:title", NS)) + f" ({_text(imprint_date)})",
        "rights": f"Translation public domain in the US (published {max(years)}). {MARKUP_RIGHTS}",
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "contentHash": hashlib.sha256(payload).hexdigest(),
    }
    path.with_suffix(".metadata.json").write_bytes((json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return path
