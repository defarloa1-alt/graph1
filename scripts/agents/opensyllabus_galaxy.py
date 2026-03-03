#!/usr/bin/env python3
"""
Open Syllabus Galaxy — Fetch syllabus-assigned works from Galaxy search API.

API: https://galaxy-api-prod.opensyllabus.org/os-titles/search-works/{query}?size=N

Returns works frequently assigned in syllabi matching the query (e.g. "Roman Republic").
No per-work URLs in API; we add galaxy_search_url and optionally try Open Library for links.

Usage:
  from scripts.agents.opensyllabus_galaxy import fetch_galaxy_works
  works = fetch_galaxy_works("Roman Republic", size=25)
"""

import json
import urllib.parse
import urllib.request
from typing import Optional

GALAXY_SEARCH = "https://galaxy-api-prod.opensyllabus.org/os-titles/search-works"
OPENLIBRARY_SEARCH = "https://openlibrary.org/search.json"


def _openlibrary_lookup(title: str, authors: str, timeout: int = 5) -> Optional[str]:
    """Try Open Library search for a work URL. Returns first result URL or None."""
    if not title or not title.strip():
        return None
    q = f"{title.strip()}"
    if authors:
        q = f"{q} {authors.split(',')[0].strip()}"
    params = urllib.parse.urlencode({"q": q[:200], "limit": 1})
    url = f"{OPENLIBRARY_SEARCH}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum/1.0 (bibliography)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return None
    docs = data.get("docs", [])
    if not docs:
        return None
    d = docs[0]
    key = d.get("key")  # e.g. /works/OL123W
    if key:
        return f"https://openlibrary.org{key}"
    return None


def fetch_galaxy_works(
    query: str,
    size: int = 25,
    resolve_openlibrary: bool = True,
    timeout: int = 20,
) -> list[dict]:
    """
    Fetch works from Open Syllabus Galaxy search.

    Each work: title, authors, match_count, field, source, galaxy_search_url,
    uri (from Open Library if resolve_openlibrary and found).
    """
    if not query or not query.strip():
        return []
    encoded = urllib.parse.quote(query.strip())
    url = f"{GALAXY_SEARCH}/{encoded}?size={min(size, 100)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum/1.0 (bibliography)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []

    hits = data.get("hits", [])
    galaxy_url = f"https://galaxy.opensyllabus.org/#!search/works/{encoded}"

    results = []
    seen_titles: set[str] = set()
    for hit in hits:
        src = hit.get("source", {}) or {}
        title = (src.get("title") or "").strip()
        if not title or title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())

        authors = (src.get("authors") or "").strip()
        match_count = src.get("match_count", 0)
        field = src.get("field")

        entry = {
            "title": title,
            "authors": authors,
            "match_count": match_count,
            "field": field,
            "source": "OpenSyllabus",
            "galaxy_search_url": galaxy_url,
        }
        if resolve_openlibrary:
            ol_url = _openlibrary_lookup(title, authors)
            if ol_url:
                entry["uri"] = ol_url
        if not entry.get("uri"):
            entry["uri"] = galaxy_url

        results.append(entry)
        if len(results) >= size:
            break

    return results
