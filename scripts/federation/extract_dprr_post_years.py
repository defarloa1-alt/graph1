#!/usr/bin/env python3
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
extract_dprr_post_years.py
--------------------------
Extract PostAssertion ID → year mappings from the DPRR Turtle dump.

Source: https://raw.githubusercontent.com/gillisandrew/dprr-mcp/refs/heads/main/data/dprr.ttl
Output: scripts/federation/dprr_post_years.json
  { "17": -509, "32": -308, ... }

Year convention: negative = BCE (e.g. -509 = 509 BC), positive = CE.
DPRR stores years as positive integers for BCE (509 = 509 BC); we negate them.

Usage:
    python scripts/federation/extract_dprr_post_years.py
    python scripts/federation/extract_dprr_post_years.py --ttl path/to/dprr.ttl
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

import requests

TTL_URL = "https://raw.githubusercontent.com/gillisandrew/dprr-mcp/refs/heads/main/data/dprr.ttl"
OUT_PATH = Path(__file__).parent / "dprr_post_years.json"

# DPRR uses vocab:hasDateStart / vocab:hasDateEnd (already signed: -509 = 509 BCE)
# Format: <.../PostAssertion/N> a vocab:PostAssertion ; vocab:hasDateStart -509 ; vocab:hasDateEnd -27 .
RE_POST_URI    = re.compile(r'<http://romanrepublic\.ac\.uk/rdf/entity/PostAssertion/(\d+)>')
RE_DATE_START  = re.compile(r'vocab:hasDateStart\s+(-?\d+)')
RE_DATE_END    = re.compile(r'vocab:hasDateEnd\s+(-?\d+)')


def extract_from_stream(stream) -> dict[str, dict]:
    """
    Parse Turtle line-by-line collecting PostAssertion → {start, end} year ranges.
    Subject blocks end at a line ending with ' .' or an empty line after data lines.
    Output: {"17": {"start": -509, "end": -509}, ...}
    """
    mapping: dict[str, dict] = {}
    current_id: str | None = None
    current: dict = {}

    def _flush():
        nonlocal current_id, current
        if current_id and ("start" in current or "end" in current):
            mapping[current_id] = current
        current_id = None
        current = {}

    for raw_line in stream:
        line = (raw_line.decode("utf-8", errors="replace")
                if isinstance(raw_line, bytes) else raw_line)

        # New subject starts at a line beginning with '<'
        if line.startswith("<"):
            _flush()
            m = RE_POST_URI.match(line)
            if m:
                current_id = m.group(1)
                current = {}
            continue

        if current_id:
            m = RE_DATE_START.search(line)
            if m:
                current["start"] = int(m.group(1))
            m = RE_DATE_END.search(line)
            if m:
                current["end"] = int(m.group(1))
            # Block ends with a line finishing in ' .'
            if line.rstrip().endswith("."):
                _flush()

    _flush()
    return mapping


def run(ttl_path: Path | None = None, out_path: Path = OUT_PATH) -> int:
    if ttl_path and ttl_path.exists():
        print(f"Reading local TTL: {ttl_path}")
        with open(ttl_path, encoding="utf-8", errors="replace") as f:
            mapping = extract_from_stream(f)
    else:
        print(f"Streaming TTL from GitHub: {TTL_URL}")
        headers = {"User-Agent": "Chrystallum-Research/1.0 (academic)"}
        r = requests.get(TTL_URL, headers=headers, stream=True, timeout=120)
        r.raise_for_status()
        mapping = extract_from_stream(r.iter_lines())

    print(f"Extracted {len(mapping)} PostAssertion year mappings")

    if mapping:
        starts = [v["start"] for v in mapping.values() if "start" in v]
        ends   = [v["end"]   for v in mapping.values() if "end"   in v]
        if starts:
            print(f"  Date start range: {min(starts)} to {max(starts)}")
        if ends:
            print(f"  Date end range:   {min(ends)} to {max(ends)}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, sort_keys=True)
    print(f"Saved to {out_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract DPRR PostAssertion years from Turtle")
    parser.add_argument("--ttl", type=Path, default=None,
                        help="Local dprr.ttl path (skips network fetch)")
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()
    return run(args.ttl, args.out)


if __name__ == "__main__":
    sys.exit(main())
