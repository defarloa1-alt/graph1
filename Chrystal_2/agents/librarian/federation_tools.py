#!/usr/bin/env python3
"""FederationCard-backed tools for Librarian (lcsh_fast_lcc)."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from scripts.agents.lcsh_resolve import resolve_lcsh

HEADERS = {"User-Agent": "Chrystallum/1.0 (Librarian; lcsh_fast_lcc)"}
FAST_SUGGEST = "https://fast.oclc.org/searchfast/fastsuggest"
FAST_RDF = "https://id.worldcat.org/fast/{numeric_id}"


def loc_fetch_heading(lcsh_id: str) -> dict[str, Any] | None:
    """Card tool: loc_fetch_heading."""
    return resolve_lcsh(lcsh_id)


def _http_get(url: str, timeout: int = 25) -> bytes | None:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception:
        return None


def _norm_fast_id(raw: Any) -> str | None:
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if not raw:
        return None
    s = str(raw).strip()
    m = re.search(r"(fst\d+|\d{5,})", s, re.I)
    if not m:
        return None
    token = m.group(1).lower()
    if token.startswith("fst"):
        return token
    return f"fst{int(token):08d}"


def _numeric_fast(fast_id: str) -> str:
    return re.sub(r"^fst0*", "", fast_id.lower()) or "0"


def fast_suggest(query: str, *, query_index: str = "suggestall", rows: int = 10) -> list[dict[str, Any]]:
    """Card tool helper: OCLC searchfast suggest."""
    q = (query or "").strip()
    if not q:
        return []
    params = urllib.parse.urlencode(
        {
            "query": q,
            "queryIndex": query_index,
            "queryReturn": "suggestall,idroot,auth,tag,type,raw",
            "suggest": "autoSubject",
            "rows": str(rows),
        }
    )
    url = f"{FAST_SUGGEST}?{params}"
    raw = _http_get(url)
    if not raw or not raw.strip().startswith(b"{"):
        time.sleep(0.6)
        raw = _http_get(url)
    if not raw or not raw.strip().startswith(b"{"):
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    out: list[dict[str, Any]] = []
    for doc in data.get("response", {}).get("docs", []) or []:
        fid = _norm_fast_id(doc.get("idroot"))
        if not fid:
            continue
        label = doc.get("auth") or doc.get("suggestall")
        if isinstance(label, list):
            label = label[0] if label else None
        out.append(
            {
                "fast_id": fid,
                "label": label,
                "tag": doc.get("tag"),
                "type": doc.get("type"),
                "query": q,
                "query_index": query_index,
            }
        )
    return out


GENERIC_TOPIC_LABELS = frozenset(
    {
        "history",
        "civilization",
        "culture",
        "politics",
        "government",
        "war",
        "religion",
        "society",
        "economics",
        "geography",
    }
)


def fetch_fast_heading(fast_id: str) -> dict[str, Any] | None:
    """Resolve a FAST id to a label (+ chrono strings if present) via id.worldcat.org RDF."""
    fid = _norm_fast_id(fast_id)
    if not fid:
        return None
    numeric = _numeric_fast(fid)
    raw = _http_get(FAST_RDF.format(numeric_id=numeric))
    if not raw:
        return None
    text = raw.decode("utf-8", "replace")
    prefs = re.findall(r"<skos:prefLabel[^>]*>([^<]+)</skos:prefLabel>", text)
    if not prefs:
        prefs = re.findall(r"prefLabel[^>]*>([^<]+)<", text)
    label = prefs[0].strip() if prefs else None
    if not label:
        return None
    chrono = sorted(
        {
            s.strip()
            for s in re.findall(r">([^<]*(?:Republic|Kingdom|Empire|--\d)[^<]*)<", text)
            if s.strip() and s.strip() != label and len(s.strip()) < 120
        }
    )
    return {
        "fast_id": fid,
        "label": label,
        "uri": f"https://id.worldcat.org/fast/{numeric}",
        "chrono_facets": chrono,
    }


def _score_fast_candidate(query: str, cand: dict[str, Any]) -> float:
    label = (cand.get("label") or "").strip()
    if not label:
        return 0.0
    q = query.strip().casefold()
    lab = label.casefold()
    if lab == q:
        return 100.0
    if lab.startswith(q) or q.startswith(lab):
        return 80.0
    q_toks = {t for t in re.split(r"[^\w]+", q) if len(t) >= 3}
    l_toks = {t for t in re.split(r"[^\w]+", lab) if len(t) >= 3}
    if not q_toks or not l_toks:
        return 0.0
    overlap = len(q_toks & l_toks) / max(len(q_toks), 1)
    score = 40.0 * overlap
    tag = str(cand.get("tag") or "")
    if tag in {"151", "150", "155"}:
        score += 5.0
    if "rome" in q and "dominican" in lab:
        return 0.0
    if "rome" in q and lab in {"romania", "romanian"}:
        return 0.0
    return score


def derive_fast_facets_from_lcsh_heading(heading: str) -> list[dict[str, Any]]:
    """
    Soft FAST for chronological LCSH: geographic umbrella + chrono facet text.

    Does **not** mint bare topical middles (e.g. History from Rome--History--…).
    """
    heading = (heading or "").strip()
    if not heading:
        return []

    parts = [p.strip() for p in heading.split("--") if p.strip()]
    queries: list[tuple[str, str, str]] = []
    if parts:
        queries.append(("geographic", parts[0], "suggest51"))

    chosen: list[dict[str, Any]] = []
    seen: set[str] = set()
    for role, query, idx in queries:
        if query.casefold() in GENERIC_TOPIC_LABELS:
            continue
        cands = fast_suggest(query, query_index=idx, rows=12)
        ranked = sorted(
            ((_score_fast_candidate(query, c), c) for c in cands),
            key=lambda x: -x[0],
        )
        best_score, best = (ranked[0] if ranked else (0.0, None))
        if not best or best_score < 35.0:
            continue
        fid = best["fast_id"]
        if fid in seen:
            continue
        resolved = fetch_fast_heading(fid) or {
            "fast_id": fid,
            "label": best.get("label"),
            "uri": f"https://id.worldcat.org/fast/{_numeric_fast(fid)}",
            "chrono_facets": [],
        }
        lab = (resolved.get("label") or "").casefold()
        if lab in GENERIC_TOPIC_LABELS or not resolved.get("label"):
            continue
        seen.add(fid)
        chrono = resolved.get("chrono_facets") or []
        heading_l = heading.casefold()
        chrono_hit = next(
            (
                c
                for c in chrono
                if "republic" in c.casefold()
                or any(tok in c.casefold() for tok in ("510", "30 b"))
                or c.casefold() in heading_l
            ),
            chrono[0] if chrono else None,
        )
        chosen.append(
            {
                **resolved,
                "facet_role": role,
                "match_score": round(best_score, 1),
                "query_used": query,
                "soft": True,
                "chrono_facet": chrono_hit,
            }
        )
        time.sleep(0.35)
    return chosen


def lcc_lookup_class(
    *,
    domain_id: str,
    csv_path: Path,
    heading: str | None = None,
) -> list[dict[str, Any]]:
    """
    Card tool: lcc_lookup_class — soft catalog correlation from Domain LCC CSV slice.
    Prefers Republic period history ranges when heading mentions Republic.
    """
    if not csv_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("domain") or "").strip() != domain_id:
                continue
            if (row.get("federation") or "").strip().lower() != "lcc":
                continue
            rows.append(row)

    heading_l = (heading or "").casefold()
    picks: list[dict[str, Any]] = []

    # Soft default for Roman Republic chronological LCSH: DG Republic slices
    if "republic" in heading_l and domain_id == "roman_republic":
        want = {"DG221-239", "DG241-259", "DG261-269"}
        for row in rows:
            cid = (row.get("id") or "").strip()
            if cid in want:
                picks.append(
                    {
                        "class_number": cid,
                        "label": row.get("label"),
                        "uri": row.get("uri")
                        or f"https://id.loc.gov/authorities/classification/{cid}",
                        "soft": True,
                        "role": "soft_period_slice",
                        "source": str(csv_path).replace("\\", "/"),
                    }
                )
        if picks:
            return picks

    # Fallback: seeded rows only
    for row in rows:
        if str(row.get("is_seed", "")).lower() in {"true", "1", "yes"}:
            cid = (row.get("id") or "").strip()
            if not cid:
                continue
            picks.append(
                {
                    "class_number": cid,
                    "label": row.get("label"),
                    "uri": row.get("uri")
                    or f"https://id.loc.gov/authorities/classification/{cid}",
                    "soft": True,
                    "role": "soft_seed_slice",
                    "source": str(csv_path).replace("\\", "/"),
                }
            )
    return picks
