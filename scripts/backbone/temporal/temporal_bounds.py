#!/usr/bin/env python3
"""Utility helpers for Chrystallum temporal bounding-box normalization."""

from __future__ import annotations

from typing import Dict


def _pick(*values: str) -> str:
    for v in values:
        if v and str(v).strip():
            return str(v).strip()
    return ""


def build_temporal_bbox(
    *,
    start_date: str = "",
    end_date: str = "",
    start_date_min: str = "",
    start_date_max: str = "",
    end_date_min: str = "",
    end_date_max: str = "",
    earliest_start: str = "",
    latest_start: str = "",
    earliest_end: str = "",
    latest_end: str = "",
) -> Dict[str, str]:
    """Return a normalized temporal envelope with alias fields.

    Canonical behavior:
    - If explicit min/max fields are missing, fall back to earliest/latest aliases.
    - If both are missing, fall back to start_date/end_date point values.
    - Emits both naming families for compatibility:
      start_date_min/max + end_date_min/max
      earliest_start/latest_start + earliest_end/latest_end
    """
    s_min = _pick(start_date_min, earliest_start, start_date)
    s_max = _pick(start_date_max, latest_start, start_date)
    e_min = _pick(end_date_min, earliest_end, end_date)
    e_max = _pick(end_date_max, latest_end, end_date)

    # Backfill point values if only bounds are present.
    start_point = _pick(start_date, s_min, s_max)
    end_point = _pick(end_date, e_min, e_max)

    return {
        "start_date": start_point,
        "end_date": end_point,
        "start_date_min": s_min,
        "start_date_max": s_max,
        "end_date_min": e_min,
        "end_date_max": e_max,
        "earliest_start": s_min,
        "latest_start": s_max,
        "earliest_end": e_min,
        "latest_end": e_max,
    }
