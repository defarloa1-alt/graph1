#!/usr/bin/env python3
"""
OpenAlex OA Works — Fetch open-access works with free full text from OpenAlex API.

Domain-level search only (e.g. "Roman Republic") — per-discipline search returns
irrelevant matches. Uses filter=is_oa:true for gold/bronze/green/diamond OA.

Usage:
  from scripts.agents.openalex_oa_works import fetch_oa_works
  works = fetch_oa_works("Roman Republic", per_page=25)
"""

import urllib.parse
import urllib.request
import json
from typing import Optional


OPENALEX_WORKS = "https://api.openalex.org/works"


def fetch_oa_works(
    search: str,
    per_page: int = 25,
    cursor: Optional[str] = None,
    use_semantic: bool = False,
    api_key: Optional[str] = None,
) -> list[dict]:
    """
    Fetch open-access works from OpenAlex. Domain-level search (e.g. "Roman Republic")
    returns relevant results; per-discipline search is noisy.

    Each work dict: title, doi, oa_url, year, oa_status (gold/bronze/green/diamond), openalex_id, source
    """
    if not search or not search.strip():
        return []
    params = {
        "filter": "is_oa:true",
        "per_page": min(per_page, 200),
        "sort": "relevance_score:desc",
    }
    if use_semantic and api_key:
        params["search.semantic"] = search.strip()
        params["api_key"] = api_key
    else:
        params["search"] = search.strip()
    if cursor:
        params["cursor"] = cursor
    qs = urllib.parse.urlencode(params)
    url = f"{OPENALEX_WORKS}?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum/1.0 (bibliography)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []

    results = []
    for hit in data.get("results", []):
        oa = hit.get("open_access", {}) or {}
        oa_url = oa.get("oa_url")
        if not oa_url and hit.get("best_oa_location"):
            loc = hit["best_oa_location"]
            if isinstance(loc, dict):
                oa_url = loc.get("url") or loc.get("landing_page_url")
        entry = {
            "title": hit.get("title") or hit.get("display_name", "") or "",
            "doi": hit.get("doi"),
            "oa_url": oa_url,
            "year": hit.get("publication_year"),
            "oa_status": oa.get("oa_status"),
            "openalex_id": hit.get("id", "").replace("https://openalex.org/", ""),
            "source": "OpenAlex",
        }
        doi = entry.get("doi") or ""
        entry["uri"] = oa_url or (doi if doi.startswith("http") else f"https://doi.org/{doi}") if doi else f"https://openalex.org/{entry['openalex_id']}"
        results.append(entry)
    return results
