#!/usr/bin/env python3
"""
Gather Books — Enrich bibliography entries with Internet Archive, TOC, publisher.

From claude/gatherbooks.md: for each work, find open TOC/preview/full-text links.
- Open Library editions have ocaid → https://archive.org/details/{ocaid}
- Editions may have lccn → https://catdir.loc.gov/catdir/toc/{lccn}.html
- Add publisher, year from edition when available.

Usage:
  from scripts.agents.gather_books import enrich_work
  work = enrich_work({"title": "...", "uri": "https://openlibrary.org/works/OL2367331W"})
  # -> adds ia_url, toc_url, publisher, year when found
"""

import json
import re
import urllib.request
from typing import Optional

LOC_TOC_BASE = "https://catdir.loc.gov/catdir/toc"
OPENLIBRARY_EDITIONS = "https://openlibrary.org"


def _ol_work_id(uri: str) -> Optional[str]:
    """Extract OL work ID from openlibrary.org/works/OLxxxW URL."""
    if not uri or "openlibrary.org/works/" not in uri:
        return None
    m = re.search(r"/works/(OL\d+W)", uri)
    return m.group(1) if m else None


def _fetch_editions(work_id: str, timeout: int = 10) -> list[dict]:
    """Fetch Open Library editions for a work. Returns list of edition dicts."""
    url = f"{OPENLIBRARY_EDITIONS}/works/{work_id}/editions.json?limit=10"
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum/1.0 (gather_books)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []
    return data.get("entries", [])


def enrich_work(work: dict, timeout: int = 10) -> dict:
    """
    Enrich a work dict with ia_url, toc_url, publisher, year from Open Library editions.

    Work should have uri (Open Library) or at least title. Modifies in place and returns.
    """
    out = dict(work)
    uri = out.get("uri") or ""
    work_id = _ol_work_id(uri)
    if not work_id:
        return out

    editions = _fetch_editions(work_id, timeout=timeout)
    if not editions:
        return out

    # Prefer edition with ocaid (Internet Archive); fallback to first with lccn
    best_ia = None
    best_toc = None
    best_pub = None
    best_year = None

    for ed in editions:
        ocaid = ed.get("ocaid")
        lccn_list = ed.get("lccn") or ed.get("lccns") or []
        lccn = lccn_list[0] if isinstance(lccn_list, list) and lccn_list else (lccn_list if isinstance(lccn_list, str) else None)
        pubs = ed.get("publishers") or []
        pub = pubs[0] if pubs else None
        year = ed.get("publish_date")

        if ocaid and not best_ia:
            best_ia = ocaid
        if lccn and not best_toc:
            best_toc = lccn
        if pub and not best_pub:
            best_pub = pub
        if year and not best_year:
            best_year = year

    if best_ia:
        out["ia_url"] = f"https://archive.org/details/{best_ia}"
    if best_toc:
        out["toc_url"] = f"{LOC_TOC_BASE}/{best_toc}.html"
    if best_pub:
        out["publisher"] = best_pub
    if best_year:
        out["year"] = best_year

    return out


def enrich_bibliography(entries: list[dict], max_enrich: int = 25, timeout: int = 8) -> list[dict]:
    """
    Enrich bibliography entries that have Open Library URIs.
    Limits to max_enrich to avoid rate limits.
    """
    enriched = []
    for i, w in enumerate(entries):
        if i >= max_enrich:
            enriched.append(w)
            continue
        if _ol_work_id(w.get("uri") or ""):
            enriched.append(enrich_work(w, timeout=timeout))
        else:
            enriched.append(w)
    return enriched
