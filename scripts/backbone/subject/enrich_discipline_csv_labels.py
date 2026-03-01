#!/usr/bin/env python3
"""
Enrich discipline CSV with authority labels from LCSH, LCC, AAT, FAST APIs.

Adds lcsh_label, lcc_label, aat_label, fast_label columns for curation.
Output: discipline_majors_consolidated_enriched.csv (or _mapped_enriched.csv)

Usage:
  python scripts/backbone/subject/enrich_discipline_csv_labels.py
  python scripts/backbone/subject/enrich_discipline_csv_labels.py -i output/discipline_majors_mapped.csv
  python scripts/backbone/subject/enrich_discipline_csv_labels.py --limit 50
"""

import argparse
import csv
import re
import time
from pathlib import Path

import requests

_PROJECT = Path(__file__).resolve().parents[3]
USER_AGENT = "ChrystallumBot/1.0 (research project)"


def _first_preflabel(obj, id_uri: str) -> str | None:
    """Extract prefLabel or authoritativeLabel from LoC JSON-LD graph."""
    for item in obj if isinstance(obj, list) else [obj]:
        if item.get("@id") == id_uri or (isinstance(id_uri, str) and id_uri in (item.get("@id") or "")):
            for key in (
                "http://www.w3.org/2004/02/skos/core#prefLabel",
                "http://www.loc.gov/mads/rdf/v1#authoritativeLabel",
                "http://www.w3.org/2000/01/rdf-schema#label",
            ):
                vals = item.get(key, [])
                if isinstance(vals, dict):
                    vals = [vals]
                for v in vals:
                    if isinstance(v, dict) and "@value" in v:
                        return v["@value"]
    return None


def fetch_lcsh_label(lcsh_id: str) -> str | None:
    url = f"https://id.loc.gov/authorities/subjects/{lcsh_id}.json"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            uri = f"http://id.loc.gov/authorities/subjects/{lcsh_id}"
            return _first_preflabel(data, uri)
    except Exception:
        pass
    return None


def fetch_lcc_label(lcc_code: str) -> str | None:
    code = lcc_code.split("|")[0].strip().split("-")[0].strip()
    if not code:
        return None
    url = f"https://id.loc.gov/authorities/classification/{code}.json"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            uri = f"http://id.loc.gov/authorities/classification/{code}"
            return _first_preflabel(data, uri)
    except Exception:
        pass
    return None


def fetch_aat_label(aat_id: str) -> str | None:
    url = f"https://vocab.getty.edu/aat/{aat_id}.jsonld"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            return data.get("_label") or data.get("content")
    except Exception:
        pass
    return None


def fetch_fast_label(fast_id: str) -> str | None:
    url = f"http://id.worldcat.org/fast/{fast_id}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        if r.status_code == 200:
            text = r.text
            lines = text.replace("\r", "").split("\n")
            for i, line in enumerate(lines):
                if "prefLabel" in line.lower() or "Preferred Label" in line:
                    for j in range(i + 1, min(i + 4, len(lines))):
                        next_line = lines[j].strip()
                        next_line = re.sub(r"^[-–•]\s*", "", next_line)
                        next_line = re.sub(r"<[^>]+>", "", next_line).strip()
                        if next_line and 2 < len(next_line) < 150 and not next_line.startswith("http"):
                            return next_line
            m = re.search(r'property="name"[^>]*content="([^"]+)"', text)
            if m:
                return m.group(1).strip()
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=Path, default=_PROJECT / "output" / "discipline_majors_consolidated.csv")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Default: input stem + _enriched.csv")
    parser.add_argument("--limit", type=int, default=0, help="Limit rows to enrich (0=all)")
    parser.add_argument("--skip", type=int, default=0, help="Skip first N rows (for chunked runs)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input not found: {args.input}")
        return

    if args.output is None:
        args.output = args.input.parent / f"{args.input.stem}_enriched.csv"

    rows = []
    with open(args.input, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for r in reader:
            rows.append(r)

    # Add label columns if missing
    for col in ("lcsh_label", "lcc_label", "aat_label", "fast_label"):
        if col not in fieldnames:
            fieldnames.append(col)

    subset = rows[args.skip : (args.skip + args.limit) if args.limit else None]
    total = len(subset)
    print(f"Enriching {total} rows from {args.input}...")

    for i, row in enumerate(subset):
        # LCSH
        lcsh = (row.get("lcsh_id") or "").split("|")[0].strip()
        if lcsh and not row.get("lcsh_label"):
            lbl = fetch_lcsh_label(lcsh)
            if lbl:
                row["lcsh_label"] = lbl
            time.sleep(0.15)

        # LCC
        lcc = (row.get("lcc") or "").split("|")[0].strip()
        if lcc and not row.get("lcc_label"):
            lbl = fetch_lcc_label(lcc)
            if lbl:
                row["lcc_label"] = lbl
            time.sleep(0.15)

        # AAT
        aat = (row.get("aat_id") or "").split("|")[0].strip()
        if aat and not row.get("aat_label"):
            lbl = fetch_aat_label(aat)
            if lbl:
                row["aat_label"] = lbl
            time.sleep(0.15)

        # FAST
        fast = (row.get("fast_id") or "").split("|")[0].strip()
        if fast and not row.get("fast_label"):
            lbl = fetch_fast_label(fast)
            if lbl:
                row["fast_label"] = lbl
            time.sleep(0.2)

        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{total}")

    # Write full file (subset was modified in-place; if skip/limit we only enriched a slice)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {args.output}")
    print("Curate this file, then re-run build_master_discipline_registry.py on the curated CSV.")


if __name__ == "__main__":
    main()
