#!/usr/bin/env python3
"""
Clean PeriodO CSV for Roman Republic domain.

Rules:
  1. Remove rows with special characters in label (control chars, newlines, tabs, quotes, pipe)
  2. Remove rows with no spatial_anchor
  3. Remove rows with temporal span > 3000 years (end - start)
  4. Sort by QID (extracted from spatial_anchor)

Usage:
  python scripts/backbone/subject/clean_periodo_csv.py
  python scripts/backbone/subject/clean_periodo_csv.py --in output/nodes/periodo_roman_republic.csv --out output/nodes/periodo_roman_republic_clean.csv
"""
import argparse
import csv
import re
from pathlib import Path

DEFAULT_IN = Path("output/nodes/periodo_roman_republic.csv")
DEFAULT_OUT = Path("output/nodes/periodo_roman_republic_clean.csv")
MAX_SPAN_YEARS = 3000

# Label: reject control chars, non-ASCII, slash, pipe, and other problematic chars.
CONTROL_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\"\n\r\t|]")


def _has_special_chars(s: str) -> bool:
    """True if label has control chars, non-ASCII, /, or other problematic chars."""
    if not s:
        return False
    if CONTROL_PATTERN.search(s):
        return True
    if "/" in s:
        return True
    # Non-ASCII (e.g. Cyrillic, Japanese, Greek, accented Latin)
    if any(ord(c) > 127 for c in s):
        return True
    return False


def _extract_qid(spatial_anchor: str) -> str | None:
    """Extract QID from Wikidata URI, e.g. http://www.wikidata.org/entity/Q801 -> Q801."""
    if not spatial_anchor or not isinstance(spatial_anchor, str):
        return None
    m = re.search(r"/(Q\d+)(?:/|$)", spatial_anchor)
    return m.group(1) if m else None


def _parse_int(val) -> int | None:
    if val is None or val == "":
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def run(
    in_path: Path,
    out_path: Path,
    max_span_years: int = MAX_SPAN_YEARS,
) -> None:
    rows = []
    with open(in_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            rows.append(row)

    before = len(rows)
    dropped_special = 0
    dropped_no_anchor = 0
    dropped_span = 0
    # 1. Remove special chars in label
    rows = [r for r in rows if not _has_special_chars(r.get("label", "")) or (dropped_special := dropped_special + 1) and False]
    # Fix: the above is wrong. Let me do it properly.
    filtered = []
    for r in rows:
        if _has_special_chars(r.get("label", "")):
            dropped_special += 1
            continue
        filtered.append(r)
    rows = filtered

    # 2. Remove no spatial_anchor
    filtered = []
    for r in rows:
        anchor = (r.get("spatial_anchor") or "").strip()
        if not anchor:
            dropped_no_anchor += 1
            continue
        filtered.append(r)
    rows = filtered

    # 3. Remove span > max_span_years
    filtered = []
    for r in rows:
        start = _parse_int(r.get("temporal_start"))
        end = _parse_int(r.get("temporal_end"))
        if start is not None and end is not None:
            span = abs(end - start)
            if span > max_span_years:
                dropped_span += 1
                continue
        filtered.append(r)
    rows = filtered

    # 4. Sort by QID (rows without QID sort last)
    def _sort_key(r):
        qid = _extract_qid(r.get("spatial_anchor", ""))
        return (qid or "zzz")

    rows.sort(key=_sort_key)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"[clean_periodo_csv] {in_path.name}")
    print(f"  Input:  {before} rows")
    print(f"  Dropped special chars: {dropped_special}")
    print(f"  Dropped no spatial_anchor: {dropped_no_anchor}")
    print(f"  Dropped span > {max_span_years} years: {dropped_span}")
    print(f"  Output: {len(rows)} rows (sorted by QID) -> {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean PeriodO CSV")
    parser.add_argument("--in", dest="in_path", type=Path, default=DEFAULT_IN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max-span", type=int, default=MAX_SPAN_YEARS, help=f"Max temporal span in years (default {MAX_SPAN_YEARS})")
    args = parser.parse_args()
    run(args.in_path, args.out, args.max_span)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
