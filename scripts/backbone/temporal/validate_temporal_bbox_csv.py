#!/usr/bin/env python3
"""Validate temporal bounding-box fields in CSV exports before Neo4j import.

Checks:
1. min <= max for start/end ranges
2. alias consistency (earliest/latest vs _min/_max) when both are present

Usage:
  python scripts/backbone/temporal/validate_temporal_bbox_csv.py --input path/to/file.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple


DATE_RE = re.compile(r"^([+-]?\d{1,6})(?:-(\d{1,2}))?(?:-(\d{1,2}))?$")


def _clean_date(value: str) -> str:
    if not value:
        return ""
    v = value.strip()
    if "T" in v:
        v = v.split("T", 1)[0]
    return v


def parse_iso_partial(value: str, for_max: bool = False) -> Optional[Tuple[int, int, int]]:
    v = _clean_date(value)
    if not v:
        return None
    m = DATE_RE.match(v)
    if not m:
        return None
    year = int(m.group(1))
    month = int(m.group(2)) if m.group(2) else (12 if for_max else 1)
    day = int(m.group(3)) if m.group(3) else (31 if for_max else 1)
    return (year, month, day)


def compare_dates(a: str, b: str) -> Optional[int]:
    """Return -1 if a<b, 0 if equal, 1 if a>b, None if parse failed."""
    pa = parse_iso_partial(a, for_max=False)
    pb = parse_iso_partial(b, for_max=True)
    if pa is None or pb is None:
        return None
    if pa < pb:
        return -1
    if pa > pb:
        return 1
    return 0


def validate_row(row: Dict[str, str], rownum: int) -> list[str]:
    errs: list[str] = []
    label = row.get("label") or row.get("name") or row.get("qid") or f"row_{rownum}"

    s_min = row.get("start_date_min", "")
    s_max = row.get("start_date_max", "")
    e_min = row.get("end_date_min", "")
    e_max = row.get("end_date_max", "")

    if s_min and s_max:
        c = compare_dates(s_min, s_max)
        if c is None:
            errs.append(f"{label}: unparsable start bounds ({s_min}, {s_max})")
        elif c == 1:
            errs.append(f"{label}: start_date_min > start_date_max ({s_min} > {s_max})")

    if e_min and e_max:
        c = compare_dates(e_min, e_max)
        if c is None:
            errs.append(f"{label}: unparsable end bounds ({e_min}, {e_max})")
        elif c == 1:
            errs.append(f"{label}: end_date_min > end_date_max ({e_min} > {e_max})")

    # Alias consistency checks when both naming families are present.
    alias_pairs = [
        ("earliest_start", "start_date_min"),
        ("latest_start", "start_date_max"),
        ("earliest_end", "end_date_min"),
        ("latest_end", "end_date_max"),
    ]
    for alias, canon in alias_pairs:
        av = _clean_date(row.get(alias, ""))
        cv = _clean_date(row.get(canon, ""))
        if av and cv and av != cv:
            errs.append(f"{label}: alias mismatch {alias}={av} vs {canon}={cv}")

    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="CSV file to validate")
    args = ap.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"[ERROR] File not found: {path}")
        return 2

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    all_errs: list[str] = []
    for i, row in enumerate(rows, start=2):  # CSV header is row 1
        all_errs.extend(validate_row(row, i))

    print(f"rows={len(rows)}")
    print(f"errors={len(all_errs)}")
    if all_errs:
        print("\nSample errors:")
        for e in all_errs[:50]:
            print(f"- {e}")
        return 1

    print("bbox_validation=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
