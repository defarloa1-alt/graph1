#!/usr/bin/env python3
"""
Wikipedia List of Roman praetors — fetch and parse for DPRR matcher.

Thin wrapper over wikipedia_office_lists. Kept for backward compatibility.
"""

from __future__ import annotations

import sys
from pathlib import Path

_fed = Path(__file__).resolve().parent
if str(_fed) not in sys.path:
    sys.path.insert(0, str(_fed))

from wikipedia_office_lists import (
    fetch_and_build_cache as _fetch,
    get_candidates_for_year,
    extract_year_from_offices as _extract_year_from_offices,
)


def fetch_and_build_cache(force_refresh: bool = False) -> dict:
    """Fetch praetors list. Returns {year: [{"name", "article", "qid"}], ...}"""
    return _fetch(office_key="praetors", force_refresh=force_refresh)


def get_praetor_candidates_for_year(cache: dict, year: int | None, offices: list[dict]) -> list[dict]:
    """If offices include praetor and we have year, return candidates."""
    return get_candidates_for_year(cache, year, offices, office_key="praetors")


def extract_year_from_offices(offices: list[dict], prefer_praetor: bool = False) -> int | None:
    """Extract year from offices. prefer_praetor=True uses year from praetor office first."""
    return _extract_year_from_offices(offices, prefer_office="praetors" if prefer_praetor else None)
