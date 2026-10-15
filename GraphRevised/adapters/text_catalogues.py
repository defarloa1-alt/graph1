"""Catalogues of the text libraries the source registry lists, for identifying and locating works.

Each catalogue is fetched once, cached outside version control with its hash
and retrieval time (like the Scaife catalogue), and only read: it says which
copies exist, never what a text says. Rights are not read here; they are
checked by the registry's rule when a copy is preserved.

    Project Gutenberg  pg_catalog.csv, the machine-readable catalogue the site offers for this use
    LacusCurtius       the index of Roman texts (Thayer/E/Roman/Texts/home.html), one link per work
"""

from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from .wikidata_identity import USER_AGENT

GUTENBERG_CATALOG_URI = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"
LACUSCURTIUS_BASE = "https://penelope.uchicago.edu/Thayer/"
LACUSCURTIUS_INDEX_URI = LACUSCURTIUS_BASE + "E/Roman/Texts/home.html"
UNNAMED = {"anonymous", "anon", "unknown", "various"}


def title_match(work: str, title: str) -> bool:
    """Whether a catalogue title names the work: at least two shared title stems, or all of them
    when the work's title has fewer ("Aeneid", "Odes"), so one common word is never enough."""
    stems = title_stems(work)
    return bool(stems) and len(stems & title_stems(title)) >= min(2, len(stems))


@dataclass(frozen=True)
class Snapshot:
    source_uri: str
    retrieved_at: str
    content_hash: str
    payload: bytes


def cached(uri: str, cache: Path, name: str, *, refresh: bool = False) -> Snapshot:
    """The catalogue at `uri`, from the cache if present; fetched once otherwise, with its metadata."""
    path, meta_path = cache / name, cache / f"{name}.metadata.json"
    if path.exists() and meta_path.exists() and not refresh:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return Snapshot(meta["sourceUri"], meta["retrievedAt"], meta["contentHash"], path.read_bytes())
    response = requests.get(uri, headers={"User-Agent": USER_AGENT}, timeout=120)
    response.raise_for_status()
    cache.mkdir(parents=True, exist_ok=True)
    payload = response.content
    meta = {"sourceUri": uri, "retrievedAt": datetime.now(timezone.utc).isoformat(),
            "contentHash": hashlib.sha256(payload).hexdigest()}
    path.write_bytes(payload)
    meta_path.write_bytes((json.dumps(meta, indent=2) + "\n").encode("utf-8"))
    return Snapshot(meta["sourceUri"], meta["retrievedAt"], meta["contentHash"], payload)


def name_stems(name: str) -> set[str]:
    """Distinctive words of a name, lower case: five letters or more (Velleius, Paterculus, Suetonius)."""
    return {w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]{5,}", name)}


def title_stems(title: str) -> set[str]:
    """Four-letter word stems, so Latin and English title forms meet (Epodes, Epodon)."""
    return {w[:4].lower() for w in re.findall(r"[A-Za-z]+", title) if len(w) >= 4}


@dataclass(frozen=True)
class GutenbergCatalog:
    books: list[dict[str, str]]
    snapshot: Snapshot

    def by_author(self, author: str, language: str | None = "en") -> list[dict[str, str]]:
        """Books by a primary author of this name: the name's surname (its last word, or the part before
        a comma in "Shakespeare, William") is a word of the author's surname, so Horace is not Horace
        Walpole. An anonymous or unknown author matches nothing."""
        words = [w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]{3,}", author.split(",")[0])]
        if not words or words[-1] in UNNAMED:
            return []

        def matches(authors: str) -> bool:
            for part in authors.split(";"):
                if "[" in part:  # translators, editors, illustrators
                    continue
                if words[-1] in {w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]{3,}", part.split(",")[0])}:
                    return True
            return False

        return [b for b in self.books
                if b["Type"] == "Text" and (language is None or b["Language"] == language) and matches(b["Authors"])]


def load_gutenberg(cache: Path, *, refresh: bool = False) -> GutenbergCatalog:
    snapshot = cached(GUTENBERG_CATALOG_URI, cache, "pg_catalog.csv", refresh=refresh)
    rows = list(csv.DictReader(io.StringIO(snapshot.payload.decode("utf-8"))))
    return GutenbergCatalog(rows, snapshot)


@dataclass(frozen=True)
class LacusCurtiusIndex:
    works: list[dict[str, str]]  # {"url", "label"}
    snapshot: Snapshot

    def by_author(self, author: str) -> list[dict[str, str]]:
        stems = name_stems(author) - UNNAMED
        return [w for w in self.works if stems and stems & name_stems(w["label"] + " " + w["url"].replace("_", " "))]


def parse_lacuscurtius_index(page: str) -> list[dict[str, str]]:
    """One entry per linked work home page, labelled by its link text (the first non-empty one)."""
    works: dict[str, str] = {}
    base_tag = re.search(r'(?i)<base\s+href\s*=\s*"\s*([^"]+?)\s*"', page)
    base = base_tag.group(1) if base_tag else LACUSCURTIUS_BASE
    # Hrefs are relative to the page's <BASE HREF> and may be wrapped in newlines inside the quotes.
    for href, text in re.findall(r'(?is)<a\s[^>]*?href\s*=\s*"\s*([^"]+?)\s*"[^>]*>(.*?)</a>', page):
        if "/Texts/" not in href or not href.endswith("home.html") or href.endswith("Texts/home.html"):
            continue
        label = re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", text))).strip(" :")
        url = href if href.startswith("http") else base.rstrip("/") + "/" + href.lstrip("/")
        if label and not works.get(url):
            works[url] = label
        works.setdefault(url, label)
    return [{"url": url, "label": label} for url, label in works.items()]


def load_lacuscurtius(cache: Path, *, refresh: bool = False) -> LacusCurtiusIndex:
    snapshot = cached(LACUSCURTIUS_INDEX_URI, cache, "lacuscurtius-roman-texts.html", refresh=refresh)
    return LacusCurtiusIndex(parse_lacuscurtius_index(snapshot.payload.decode("utf-8", errors="replace")), snapshot)


def snapshot_record(snapshot: Snapshot) -> dict[str, Any]:
    return {"sourceUri": snapshot.source_uri, "retrievedAt": snapshot.retrieved_at, "contentHash": snapshot.content_hash}
