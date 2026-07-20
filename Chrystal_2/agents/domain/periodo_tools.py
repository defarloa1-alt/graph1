#!/usr/bin/env python3
"""PeriodO tools for Domain — local dump / seed first (FederationCard: periodo)."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SEED = (
    ROOT
    / "Chrystal_2"
    / "federations"
    / "crosswalks"
    / "periodo_roman_republic_seed.csv"
)
if not SEED.exists():
    SEED = (
        ROOT
        / "chrystal_2"
        / "federations"
        / "crosswalks"
        / "periodo_roman_republic_seed.csv"
    )

DUMP = ROOT / "Temporal" / "periodo-dataset.csv"
RR_CLEAN = ROOT / "CSV" / "periodo_roman_republic_clean2.csv"


def _as_int(raw: Any) -> int | None:
    if raw is None or raw == "":
        return None
    try:
        return int(float(str(raw).strip()))
    except ValueError:
        return None


def _norm_row(row: dict[str, str], *, source: str) -> dict[str, Any]:
    pid = (row.get("periodo_id") or row.get("id") or "").strip()
    if not pid and row.get("period"):
        # Temporal/periodo-dataset.csv uses full ARK URI in `period`
        uri = (row.get("period") or "").strip()
        pid = uri.rsplit("/", 1)[-1] if uri else ""
    spat = (row.get("spatial_qid") or row.get("spatial_anchor") or row.get("qid") or "").strip()
    if "wikidata.org" in spat:
        spat = spat.rsplit("/", 1)[-1]
    spat = spat.strip("()")  # some dump rows wrap QIDs
    start = row.get("start_year") or row.get("temporal_start") or row.get("start")
    end = row.get("end_year") or row.get("temporal_end") or row.get("stop")
    auth = (row.get("authority_id") or row.get("authority") or "").strip()
    if "ark:" in auth:
        auth = auth.rsplit("/", 1)[-1]
    uri = (row.get("uri") or row.get("period") or "").strip()
    if not uri and pid:
        uri = f"https://n2t.net/ark:/99152/{pid}"
    return {
        "periodo_id": pid,
        "label": (row.get("label") or "").strip(),
        "start_year": _as_int(start),
        "end_year": _as_int(end),
        "spatial_qid": spat or None,
        "authority_id": auth or None,
        "uri": uri,
        "role": row.get("role"),
        "soft": str(row.get("soft", "")).lower() in {"true", "1", "yes"},
        "confidence": row.get("confidence"),
        "note": row.get("note"),
        "source": source,
    }


def load_seed(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or SEED
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return [_norm_row(r, source=str(path).replace("\\", "/")) for r in csv.DictReader(f)]


def periodo_lookup_seed(
    *,
    domain_id: str = "roman_republic",
    pack_qid: str | None = "Q17167",
) -> list[dict[str, Any]]:
    """Card tool: periodo_lookup_seed — curated soft/hard variants for a pack."""
    del pack_qid  # seed is RR-scoped; reserved for multi-pack later
    if domain_id and domain_id != "roman_republic":
        return []
    return load_seed()


def periodo_resolve_id(periodo_id: str) -> dict[str, Any] | None:
    """Card tool: periodo_resolve_id — seed first, then RR clean2, then full dump."""
    pid = (periodo_id or "").strip()
    if not pid:
        return None

    for row in load_seed():
        if row["periodo_id"] == pid:
            return row

    for path in (RR_CLEAN, DUMP):
        if not path.exists():
            continue
        with path.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                rid = (row.get("id") or row.get("periodo_id") or "").strip()
                if not rid and row.get("period"):
                    rid = str(row["period"]).rstrip("/").rsplit("/", 1)[-1]
                if rid != pid:
                    continue
                return _norm_row(row, source=str(path).replace("\\", "/"))
    return None