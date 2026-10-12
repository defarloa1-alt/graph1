"""Passage-level SourceObservations from a preserved Perseus TEI edition.

The passage text excludes editorial notes: in Perseus translations a `<note>`
is the modern editor's or translator's scholarship, not the ancient author's
text. Notes are kept separately so they are never cited as the source.
"""

from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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


def load_edition(path: Path, *, source_commit: str, rights: str | None = None) -> Edition:
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
        cts_urn=edition_div.get(f"{TEI}n") or edition_div.get("n"),
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


def section_refs(edition: Edition, chapters: range) -> list[str]:
    refs = []
    for chapter in edition.root.iterfind(".//t:body/t:div/t:div", NS):
        if int(chapter.get("n")) in chapters:
            refs.extend(f"{chapter.get('n')}.{section.get('n')}" for section in chapter.findall("t:div", NS))
    return refs


def passage_observation(edition: Edition, ref: str, *, retrieved_at: str, source_uri: str) -> dict[str, Any]:
    """Return parameters for the `upsert_passage_observation` operation."""
    chapter_n, section_n = ref.split(".", 1)
    section = edition.root.find(
        f".//t:body/t:div/t:div[@n='{chapter_n}']/t:div[@n='{section_n}']", NS
    )
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
