#!/usr/bin/env python3
"""Pleiades tools — local dump/seed first (Domain geo enrich)."""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SEED = (
    ROOT
    / "Chrystal_2"
    / "federations"
    / "crosswalks"
    / "pleiades_roman_republic_seed.csv"
)
PLACES = ROOT / "Geographic" / "pleiades_places.csv"
CROSSWALK = (
    ROOT / "CSV" / "geographic" / "pleiades_geonames_wikidata_tgn_crosswalk_v1.csv"
)


def _f(path: Path) -> Path:
    if path.exists():
        return path
    alt = Path(str(path).replace("Chrystal_2", "chrystal_2"))
    return alt if alt.exists() else path


def _float(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def _load_seed() -> list[dict[str, Any]]:
    path = _f(SEED)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    "pleiades_id": str(r.get("pleiades_id") or "").strip(),
                    "label": (r.get("label") or "").strip(),
                    "wd_qid": (r.get("wd_qid") or "").strip() or None,
                    "lat": _float(r.get("lat")),
                    "long": _float(r.get("long")),
                    "place_type": (r.get("place_type") or "").strip() or None,
                    "uri": (r.get("uri") or "").strip() or None,
                    "domain_id": (r.get("domain_id") or "").strip() or None,
                    "role": (r.get("role") or "").strip() or None,
                    "soft": str(r.get("soft") or "").lower() in {"1", "true", "yes"},
                    "confidence": (r.get("confidence") or "").strip() or None,
                    "note": (r.get("note") or "").strip() or None,
                    "source": str(path).replace("\\", "/"),
                }
            )
    return [r for r in rows if r["pleiades_id"]]


def pleiades_lookup_seed(*, domain_id: str | None = None) -> list[dict[str, Any]]:
    rows = _load_seed()
    if domain_id:
        return [r for r in rows if r.get("domain_id") == domain_id]
    return list(rows)


def pleiades_resolve_id(pleiades_id: str) -> dict[str, Any] | None:
    pid = str(pleiades_id or "").strip()
    if not pid:
        return None
    for r in _load_seed():
        if r["pleiades_id"] == pid:
            return dict(r)
    path = PLACES
    if not path.exists():
        return None
    with path.open(encoding="utf-8", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            if str(row.get("pleiades_id") or "").strip() == pid:
                return {
                    "pleiades_id": pid,
                    "label": (row.get("label") or row.get("label_clean") or "").strip(),
                    "lat": _float(row.get("lat")),
                    "long": _float(row.get("long")),
                    "place_type": (row.get("place_type") or "").strip() or None,
                    "uri": (row.get("uri") or "").strip()
                    or f"https://pleiades.stoa.org/places/{pid}",
                    "source": str(path).replace("\\", "/"),
                }
    return None


def pleiades_resolve_qid(wd_qid: str) -> dict[str, Any] | None:
    qid = str(wd_qid or "").strip().upper()
    if not qid:
        return None
    for r in _load_seed():
        if (r.get("wd_qid") or "").upper() == qid:
            return dict(r)
    path = CROSSWALK
    if path.exists():
        with path.open(encoding="utf-8", errors="replace", newline="") as f:
            for row in csv.DictReader(f):
                if str(row.get("wikidata_qid") or "").strip().upper() == qid:
                    pid = str(row.get("pleiades_id") or "").strip()
                    resolved = pleiades_resolve_id(pid) if pid else None
                    if resolved:
                        resolved["wd_qid"] = qid
                        return resolved
                    return {
                        "pleiades_id": pid,
                        "label": (row.get("place_label") or row.get("wikidata_label") or "").strip(),
                        "wd_qid": qid,
                        "lat": _float(row.get("wikidata_latitude")),
                        "long": _float(row.get("wikidata_longitude")),
                        "place_type": (row.get("place_type") or "").strip() or None,
                        "uri": f"https://pleiades.stoa.org/places/{pid}" if pid else None,
                        "source": str(path).replace("\\", "/"),
                    }
    return None
