"""Passage-level SourceObservations from a preserved Wikipedia article (29-EVENT-CENTRED-INQUIRY.md §5).

The article is fetched once at a fixed revision through the MediaWiki parse API and
preserved byte-for-byte with its revision, retrieval time, hash, and the wiki's own
rights statement (read from the API, never assumed). A passage is one paragraph or
list item of the article's body, addressed as section.paragraph ("2.3"; section 0
is the lead); citation markers are left out of the text. The sections after the
body (see also, notes, references, sources, further reading, external links) and
the navigation boxes are not passages. Each passage keeps the articles it links
to, and the infobox's links are kept apart (ref "infobox"): they are how the
article's people, places, and events are found (doc 29 §3 step 2).
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

from bs4 import BeautifulSoup

from .wikidata_identity import polite_get
from .wikidata_statements import REPOSITORY_ROOT

API = "https://{lang}.wikipedia.org/w/api.php"
# Sections that follow an article's body and are apparatus, not text.
END_SECTIONS = {"see also", "notes", "references", "sources", "further reading", "external links",
                "bibliography", "citations", "footnotes"}
SKIP_CLASSES = {"navbox", "reflist", "references", "infobox", "hatnote", "metadata", "ambox", "sidebar",
                "thumb", "mw-editsection", "shortdescription", "noprint"}


class PassageNotFound(LookupError):
    """The article has no passage with the requested reference."""


@dataclass(frozen=True)
class Passage:
    text: str
    section: str
    links: tuple[tuple[str, str], ...]  # (linked article's title, the passage's words for it)


@dataclass(frozen=True)
class Article:
    path: Path
    title: str
    language: str
    revision: int
    source_uri: str
    retrieved_at: str
    content_hash: str
    rights: str
    passages: dict[str, Passage]
    infobox_links: tuple[str, ...]

    @property
    def author(self) -> str:
        return "Wikipedia"

    @property
    def citation(self) -> str:
        return f"Wikipedia, \"{self.title}\", revision {self.revision} (retrieved {self.retrieved_at[:10]})"

    def all_refs(self) -> list[str]:
        return list(self.passages)


def preserve_article(title: str, directory: Path, language: str = "en") -> Path:
    """Fetch an article's current revision once and preserve the parse response with metadata."""
    api = API.format(lang=language)
    response = polite_get(api, params={"action": "parse", "page": title, "prop": "text|revid|displaytitle",
                                       "redirects": 1, "format": "json", "formatversion": "2"})
    payload = response.content
    parsed = json.loads(payload)["parse"]
    slug = re.sub(r"[^a-z0-9]+", "-", parsed["title"].lower()).strip("-")
    path = directory / f"wikipedia-{language}-{slug}-r{parsed['revid']}.json"
    if path.exists():
        return path
    rights = polite_get(api, params={"action": "query", "meta": "siteinfo", "siprop": "rightsinfo",
                                     "format": "json"}).json()["query"]["rightsinfo"]
    directory.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    metadata = {
        "sourceSystem": "Wikipedia",
        "sourceUri": f"https://{language}.wikipedia.org/w/index.php?title={quote(parsed['title'].replace(' ', '_'))}"
                     f"&oldid={parsed['revid']}",
        "title": parsed["title"],
        "language": language,
        "revision": parsed["revid"],
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "contentHash": hashlib.sha256(payload).hexdigest(),
        "rights": f"{rights['text']} ({rights['url']}), as the wiki states it",
    }
    path.with_suffix(".metadata.json").write_bytes((json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return path


def load_article(path: Path) -> Article:
    payload = path.read_bytes()
    metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    if hashlib.sha256(payload).hexdigest() != metadata["contentHash"]:
        raise ValueError(f"{path.name} does not match its recorded hash")
    passages, infobox = parse_html(json.loads(payload)["parse"]["text"])
    return Article(path=path, title=metadata["title"], language=metadata["language"], revision=metadata["revision"],
                   source_uri=metadata["sourceUri"], retrieved_at=metadata["retrievedAt"],
                   content_hash=metadata["contentHash"], rights=metadata["rights"], passages=passages,
                   infobox_links=infobox)


def _title(href: str | None) -> str | None:
    """The article an internal link points to, or None for any other link."""
    if not href or not href.startswith("/wiki/"):
        return None
    title = unquote(href[len("/wiki/"):]).split("#")[0].replace("_", " ")
    return None if ":" in title else title  # namespaces (File:, Help:, Category: ...) are not articles


def _skipped(element) -> bool:
    for parent in [element, *element.parents]:
        classes = set(parent.get("class") or []) if hasattr(parent, "get") else set()
        if classes & SKIP_CLASSES or (hasattr(parent, "name") and parent.name in ("table", "figure", "style")):
            return True
    return False


def parse_html(html: str) -> tuple[dict[str, Passage], tuple[str, ...]]:
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("table", class_="infobox")
    infobox_links = tuple(dict.fromkeys(t for a in (infobox.find_all("a") if infobox else [])
                                        for t in [_title(a.get("href"))] if t))
    for marker in soup.select("sup.reference, sup.noprint, span.mw-editsection"):
        marker.decompose()
    passages: dict[str, Passage] = {}
    section, heading, count = 0, "Lead", 0
    root = soup.find(class_="mw-parser-output") or soup
    for element in root.find_all(["h2", "p", "li"]):
        if element.name == "h2":
            heading = element.get_text(" ", strip=True)
            if heading.lower() in END_SECTIONS:
                break
            section, count = section + 1, 0
            continue
        if _skipped(element) or (element.name == "li" and element.find_parent(["ol"], class_="references")):
            continue
        text = re.sub(r"\s+", " ", element.get_text()).strip()  # the HTML's own spacing, so quotations match
        if len(text) < 20:
            continue
        count += 1
        links = tuple(dict.fromkeys((t, re.sub(r"\s+", " ", a.get_text()).strip())
                                    for a in element.find_all("a") for t in [_title(a.get("href"))] if t))
        passages[f"{section}.{count}"] = Passage(text=text, section=heading, links=links)
    return passages, infobox_links


def section_refs(article: Article, selection: str) -> list[str]:
    """Refs within an inclusive "section-section" range (sections as numbers; 0 is the lead)."""
    first, last = (int(n) for n in selection.split("-"))
    return [ref for ref in article.all_refs() if first <= int(ref.split(".")[0]) <= last]


def passage_observation(article: Article, ref: str) -> dict[str, Any]:
    """Return parameters for the `upsert_passage_observation` operation."""
    passage = article.passages.get(ref)
    if passage is None:
        raise PassageNotFound(f"Wikipedia {article.title} {ref}")
    slug = re.sub(r"[^a-z0-9]+", "-", article.title.lower()).strip("-")
    where = f"{passage.section}, para. {ref.split('.')[1]}"
    return {
        "id": f"chr:observation:wikipedia:{article.language}:{slug}:{ref}:r{article.revision}",
        "label": f"Wikipedia, {article.title}, {where}",
        "shortLabel": f"Wikipedia {ref}",
        "sourceSystem": "Wikipedia",
        "locator": f"{article.source_uri} ({where})",
        "passageText": passage.text,
        "passageHash": hashlib.sha256(passage.text.encode("utf-8")).hexdigest(),
        "editorialNotes": [],
        "language": article.language,
        "workTitle": article.title,
        "author": article.author,
        "translator": None,
        "editionCitation": article.citation,
        "rights": article.rights,
        "sourceUri": article.source_uri,
        "sourceRevision": f"wikipedia-{article.language}:{article.revision}",
        "retrievedAt": article.retrieved_at,
        "contentHash": article.content_hash,
        "rawPayloadUri": article.path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "status": "observed",
    }


def resolve_qids(titles: list[str], directory: Path, stem: str, language: str = "en") -> dict[str, str]:
    """Each linked article's Wikidata item, through the wiki's own page properties (redirects followed).
    The responses are preserved once beside the article (`<stem>-qids.json`) and reused."""
    path = directory / f"{stem}-qids.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["qids"]
    qids: dict[str, str] = {}
    for start in range(0, len(titles), 50):
        chunk = titles[start:start + 50]
        query = polite_get(API.format(lang=language), params={
            "action": "query", "titles": "|".join(chunk), "prop": "pageprops", "ppprop": "wikibase_item",
            "redirects": 1, "format": "json", "formatversion": "2"}).json()["query"]
        target = {t: t for t in chunk}
        for step in query.get("normalized", []) + query.get("redirects", []):
            for original, current in list(target.items()):
                if current == step["from"]:
                    target[original] = step["to"]
        items = {page["title"]: page.get("pageprops", {}).get("wikibase_item") for page in query.get("pages", [])}
        for original, final in target.items():
            if items.get(final):
                qids[original] = items[final]
    path.write_bytes((json.dumps({"retrievedAt": datetime.now(timezone.utc).isoformat(), "qids": qids},
                                 ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    return qids
