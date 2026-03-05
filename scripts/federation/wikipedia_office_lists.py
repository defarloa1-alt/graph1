#!/usr/bin/env python3
"""
Wikipedia office-holder lists — fetch and parse for DPRR matcher.

Generalized fetcher for List of Roman praetors, consuls, quaestors, etc.
Builds year (BC/AD) -> [(display_name, article_title, qid)] lookup per list.
Caches to output/dprr_wikidata_proposals/wikipedia_<office>_cache.json.

Usage:
    python scripts/federation/wikipedia_office_lists.py --refresh
    python scripts/federation/wikipedia_office_lists.py --list consuls --refresh
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests

_root = Path(__file__).resolve().parents[2]
OUT_DIR = _root / "output" / "dprr_wikidata_proposals"
USER_AGENT = "Chrystallum/1.0 (DPRR-Wikidata matcher)"
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
QID_RE = re.compile(r"^Q[1-9]\d*$")

# Office config: page title, DPRR position IDs, keywords in pos/name
LIST_CONFIG = {
    "praetors": {
        "page": "List_of_Roman_praetors",
        "office_ids": {"42", "50", "188", "268"},
        "keywords": ["praetor"],
        "year_range": (100, 600),  # Republic BC
    },
    "consuls": {
        "page": "List_of_Roman_consuls",
        "office_ids": {"3", "4", "121"},  # consul, consul suffectus, consul designatus
        "keywords": ["consul"],
        "year_range": (27, 509),  # Republic BC (509 to 27)
    },
}

# Skip article titles that are not person pages
SKIP_PATTERNS = (
    r"_gens$",
    r"^List_of",
    r"^Template:",
    r"^Category:",
    r"^Wikipedia:",
    r"^File:",
    r"^Help:",
    r"^Portal:",
    r"^Outline_of",
    r"^Index_of",
    r"^Timeline_of",
    r"^Decemviri",
    r"^First_decemvirate",
    r"^Second_decemvirate",
    r"^Consular_tribune",
) + tuple(rf"^{g}_gens$" for g in (
    "Furia", "Valeria", "Atilia", "Cornelia", "Fabia", "Claudia", "Manlia",
    "Sempronia", "Sergia", "Licinia", "Sulpicia", "Junia", "Aurelia", "Aemilia",
    "Papiria", "Plautia", "Pomponia", "Porcia", "Quinctia", "Tremellia", "Villia",
    "Digitia", "Juventia", "Baebia", "Helvia", "Minucia", "Acilia", "Apustia",
    "Oppia", "Stertinia", "Terentia", "Maenia", "Decimia", "Naevia", "Pupia",
    "Sicinia", "Ogulnia", "Petillia", "Pinaria", "Duronia", "Cicereia", "Matiena",
    "Memmia", "Caninia", "Canuleia", "Raecia", "Hortensia", "Numisia", "Aburia",
    "Aquillia", "Cluvia", "Lucretia", "Afrania", "Atinia", "Aurunculeia", "Hostilia",
    "Mamilia", "Octavia", "Caecilia", "Marcia", "Fonteia", "Titinia", "Annia",
    "Opimia", "Salonia", "Belliena", "Cosconia", "Appuleia", "Rutilia", "Cassia",
    "Tuccia", "Perperna", "Burriena", "Antonia", "Fufidia", "Nonia", "Fannia",
    "Sentia", "Lucilia", "Caelia", "Gabinia", "Ancharia", "Magia",
))


def _skip_article(title: str) -> bool:
    t = title.replace(" ", "_")
    for pat in SKIP_PATTERNS:
        if re.search(pat, t, re.I):
            return True
    return False


def _dedupe_preserve_order(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    return [x for x in items if x not in seen and not seen.add(x)]


def _get_qid_for_article(title: str) -> str | None:
    """Get Wikidata QID for a Wikipedia article."""
    try:
        r = requests.get(
            WIKIPEDIA_API,
            params={
                "action": "query",
                "titles": title.replace(" ", "_"),
                "prop": "pageprops",
                "format": "json",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for pid, p in pages.items():
            if pid == "-1":
                continue
            qid = (p.get("pageprops") or {}).get("wikibase_item", "")
            if qid and QID_RE.match(str(qid)):
                return str(qid)
    except Exception:
        pass
    return None


def _parse_office_list_html(html: str, year_range: tuple[int, int]) -> dict[int, list[tuple[str, str]]]:
    """
    Parse HTML to extract year -> [(display_name, article_title)].
    Works for praetors, consuls, etc. — table with year in first cell, person links in row.
    """
    out: dict[int, list[tuple[str, str]]] = {}
    year_re = re.compile(
        r'<td[^>]*>\s*(\d{2,4})\s*<|'
        r"<td[^>]*>\s*(\d{2,4})\s*</td>",
        re.I,
    )
    link_re = re.compile(r'<a\s+href="/wiki/([^"#]+)"[^>]*>([^<]+)</a>')

    rows = re.split(r"<tr", html, flags=re.I)
    current_year: int | None = None
    lo, hi = year_range

    for row in rows:
        year_m = year_re.search(row)
        if year_m:
            y = int(next(g for g in year_m.groups() if g))
            if lo <= y <= hi:
                current_year = y
        # suff. / consular tribunes rows continue previous year
        if current_year is None:
            continue
        names: list[tuple[str, str]] = []
        for m in link_re.finditer(row):
            article = m.group(1).replace("_", " ")
            display = m.group(2).strip()
            if not display or len(display) < 3:
                continue
            if _skip_article(article):
                continue
            if (display, article) not in names:
                names.append((display, article))
        if names:
            out.setdefault(current_year, []).extend(names)
            out[current_year] = _dedupe_preserve_order(out[current_year])

    return out


def load_cache(office_key: str = "praetors") -> dict:
    """Load cache from disk if it exists. Does not fetch."""
    cache_path = OUT_DIR / f"wikipedia_{office_key}_cache.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def fetch_and_build_cache(
    office_key: str = "praetors",
    force_refresh: bool = False,
) -> dict:
    """
    Fetch Wikipedia list, parse, resolve QIDs, cache.
    Returns {year: [{"name": str, "article": str, "qid": str}], ...}
    """
    cfg = LIST_CONFIG.get(office_key)
    if not cfg:
        raise ValueError(f"Unknown office_key: {office_key}. Choose from {list(LIST_CONFIG)}")

    if not force_refresh:
        cached = load_cache(office_key)
        if cached:
            return cached

    print(f"Fetching Wikipedia {cfg['page']}...")
    try:
        r = requests.get(
            WIKIPEDIA_API,
            params={
                "action": "parse",
                "page": cfg["page"],
                "format": "json",
                "prop": "text",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=60,
        )
        r.raise_for_status()
        html = r.json()["parse"]["text"]["*"]
    except Exception as e:
        print(f"  Failed to fetch: {e}")
        return {}

    raw = _parse_office_list_html(html, cfg["year_range"])
    for y, entries in raw.items():
        raw[y] = _dedupe_preserve_order(entries)
    print(f"  Parsed {len(raw)} years")

    out: dict[str, list[dict]] = {}
    total = 0
    for year, entries in sorted(raw.items()):
        resolved = []
        for display, article in entries:
            qid = _get_qid_for_article(article)
            resolved.append({"name": display, "article": article, "qid": qid or ""})
            if qid:
                total += 1
        out[str(year)] = resolved

    print(f"  Resolved {total} QIDs")

    cache_path = OUT_DIR / f"wikipedia_{office_key}_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"  Cached to {cache_path}")
    return out


def get_candidates_for_year(
    cache: dict,
    year: int | None,
    offices: list[dict],
    office_key: str = "praetors",
) -> list[dict]:
    """
    If offices include the given office type and we have year, return candidates.
    Returns [{id, label, description, source: "wikipedia_<office>"}]
    """
    if not year or not cache:
        return []

    cfg = LIST_CONFIG.get(office_key)
    if not cfg:
        return []

    office_ids = cfg["office_ids"]
    keywords = cfg["keywords"]
    matched = False
    for o in offices:
        name = (o.get("name") or o.get("label_name") or "").lower()
        pos = str(o.get("pos") or "")
        if any(kw in name or kw in pos.lower() for kw in keywords) or pos in office_ids:
            matched = True
            break
    if not matched:
        return []

    year_str = str(abs(year))
    entries = cache.get(year_str, [])
    source = f"wikipedia_{office_key}"
    out = []
    for e in entries:
        qid = e.get("qid", "")
        if not qid or not QID_RE.match(qid):
            continue
        out.append({
            "id": qid,
            "label": e.get("name", ""),
            "description": f"Roman {office_key[:-1]} {year_str} BC (from Wikipedia list)",
            "source": source,
        })
    return out


def extract_year_from_offices(offices: list[dict], prefer_office: str | None = None) -> int | None:
    """
    Extract year_start from offices (BC). When prefer_office is set, use year from
    that office type first (e.g. "praetors" or "consuls").
    """
    if not prefer_office:
        for o in offices:
            ys = o.get("year_start")
            if ys is not None:
                try:
                    return int(ys)
                except (TypeError, ValueError):
                    pass
        return None

    cfg = LIST_CONFIG.get(prefer_office)
    if not cfg:
        return extract_year_from_offices(offices, prefer_office=None)

    office_ids = cfg["office_ids"]
    keywords = cfg["keywords"]
    chosen = None
    for o in offices:
        ys = o.get("year_start")
        if ys is None:
            continue
        try:
            y = int(ys)
        except (TypeError, ValueError):
            continue
        name = (o.get("name") or o.get("label_name") or "").lower()
        pos = str(o.get("pos") or "")
        if any(kw in name or kw in pos.lower() for kw in keywords) or pos in office_ids:
            return y
        if chosen is None:
            chosen = y
    return chosen


if __name__ == "__main__":
    refresh = "--refresh" in sys.argv
    list_arg = "praetors"
    for i, a in enumerate(sys.argv):
        if a == "--list" and i + 1 < len(sys.argv):
            list_arg = sys.argv[i + 1]
            break
    fetch_and_build_cache(office_key=list_arg, force_refresh=refresh)
