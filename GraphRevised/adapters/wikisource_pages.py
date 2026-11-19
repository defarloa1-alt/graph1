"""Transcription passages from preserved Wikisource page revisions (2026-11-19).

Wikisource transcribes public-domain books page by page (the `Page:` namespace, one scan page
each). A page revision is fetched once through the MediaWiki API and preserved byte for byte with
its revision id, timestamp and proofreading level (1 not proofread, 2 problematic, 3 proofread,
4 validated). An entry is cut from the page's wikitext, either by its `<section>` markers or
between two verbatim strings, and becomes plain text: `<noinclude>` headers and markup removed, a
word broken across lines rejoined, other line breaks turned into spaces. The scan's OCR errors
are kept as they are (a quotation must be verbatim); a page below level 3 says so in its
metadata, so its passage is shown as unproofread.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from .wikidata_identity import USER_AGENT
from .wikidata_statements import REPOSITORY_ROOT

API = "https://en.wikisource.org/w/api.php"
QUALITY = re.compile(r'<pagequality level="(\d)"')


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:120]


def preserve_page(title: str, directory: Path) -> Path:
    """Fetch the current revision of a Wikisource page once and preserve it with metadata."""
    existing = sorted(directory.glob(f"wikisource-{_slug(title)}-r*.json"))
    existing = [p for p in existing if not p.name.endswith(".metadata.json")]
    if existing:
        return existing[-1]
    response = requests.get(API, params={"action": "query", "prop": "revisions", "rvprop": "content|ids|timestamp",
                                         "rvslots": "main", "format": "json", "titles": title},
                            headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    payload = response.content
    page = next(iter(json.loads(payload)["query"]["pages"].values()))
    if "revisions" not in page:
        raise ValueError(f"no Wikisource page {title!r}")
    revision = page["revisions"][0]
    quality = QUALITY.search(revision["slots"]["main"]["*"])
    metadata = {
        "sourceSystem": "Wikisource",
        "title": title,
        "sourceUri": f"https://en.wikisource.org/w/index.php?title={quote(title.replace(' ', '_'))}&oldid={revision['revid']}",
        "revision": revision["revid"],
        "revisionTimestamp": revision["timestamp"],
        "proofreadLevel": int(quality.group(1)) if quality else None,
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "contentHash": hashlib.sha256(payload).hexdigest(),
    }
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"wikisource-{_slug(title)}-r{revision['revid']}.json"
    path.write_bytes(payload)
    path.with_suffix(".metadata.json").write_bytes((json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return path


def page_wikitext(path: Path) -> str:
    return next(iter(json.loads(path.read_bytes())["query"]["pages"].values()))["revisions"][0]["slots"]["main"]["*"]


def plain(wikitext: str) -> str:
    """Wikitext to plain text: headers, section markers, templates and markup out; broken words rejoined."""
    text = re.sub(r"<noinclude>.*?</noinclude>", "", wikitext, flags=re.S)
    text = re.sub(r"<section[^>]*/>", "", text)
    text = re.sub(r"\{\{polytonic\|([^}]*)\}\}", r"\1", text)
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    text = re.sub(r"'{2,}", "", text)
    text = re.sub(r"(\w)- *\n *(\w)", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip()


def section(wikitext: str, name: str) -> str:
    """The text between <section begin="name" /> and <section end="name" />."""
    match = re.search(rf'<section begin="{re.escape(name)}"\s*/>(.*?)<section end="{re.escape(name)}"\s*/>', wikitext, re.S)
    if match is None:
        raise ValueError(f"no section {name!r}")
    return plain(match.group(1))


def between(text: str, start: str, end: str | None = None) -> str:
    """The plain text from `start` (included) up to `end` (excluded), both verbatim."""
    begin = text.find(start)
    if begin < 0:
        raise ValueError(f"{start!r} not found")
    stop = text.find(end, begin) if end else len(text)
    if stop < 0:
        raise ValueError(f"{end!r} not found after {start!r}")
    return text[begin:stop].strip()


def transcription(path: Path, text: str, *, work_id: str, work_label: str, locator: str, edition_citation: str,
                  rights: str, captured_by: str, captured_at: str) -> dict[str, Any]:
    """Parameters for `upsert_transcription_observation`: one entry of a preserved page."""
    metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    level = metadata.get("proofreadLevel")
    return {
        "id": f"chr:observation:wikisource:{work_id.split(':', 2)[2]}:{_slug(locator)}:{digest[:12]}",
        "workId": work_id,
        "label": f"{work_label}, {locator} (Wikisource{'' if level and level >= 3 else ', not proofread'})",
        "shortLabel": f"{work_label} {locator}",
        "sourceSystem": "Wikisource", "locator": locator, "locatorType": "entry",
        "passageText": text, "passageHash": digest, "language": "en",
        "workTitle": work_label, "author": None, "editionCitation": edition_citation,
        "rights": f"{rights}; transcription: Wikisource page revision {metadata['revision']}",
        "visibility": "public", "capturedBy": captured_by, "capturedAt": captured_at,
        "contentHash": metadata["contentHash"],
        "rawPayloadUri": path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "footnotes": None,
    }
