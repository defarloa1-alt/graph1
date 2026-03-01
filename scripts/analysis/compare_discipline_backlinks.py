#!/usr/bin/env python3
"""
Compare backlink (P31 instance-of) counts between academic-discipline-only vs academic+field-of-study lists.

For each discipline QID, counts how many Wikidata items have wdt:P31 pointing to it.
Compares totals, coverage, and distribution between the two lists.

Usage:
  python scripts/analysis/compare_discipline_backlinks.py
  python scripts/analysis/compare_discipline_backlinks.py --acad CSV/disciplines_academic.csv --field CSV/disciplines_academic_field.csv
"""

import argparse
import csv
import sys
import time
from pathlib import Path

import requests

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "ChrystallumBot/1.0 (research project)"
BATCH_SIZE = 100


def query_wikidata(sparql: str) -> dict | None:
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    try:
        r = requests.get(SPARQL_URL, params={"query": sparql}, headers=headers, timeout=120)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"  Error: {e}")
    return None


def fetch_backlink_counts(qids: list[str]) -> dict[str, int]:
    """Fetch backlink count for each QID: P31 (instance of) + P279 (subclass of) + P361 (part of).
    Batches of BATCH_SIZE."""
    result = {q: 0 for q in qids}
    for i in range(0, len(qids), BATCH_SIZE):
        batch = qids[i : i + BATCH_SIZE]
        values = " ".join(f"wd:{q}" for q in batch)
        # Union: items that have this as P31, P279, or P361
        sparql = f"""
        SELECT ?target (COUNT(DISTINCT ?item) as ?count) WHERE {{
          VALUES ?target {{ {values} }}
          {{
            ?item wdt:P31 ?target .
          }} UNION {{
            ?item wdt:P279 ?target .
          }} UNION {{
            ?item wdt:P361 ?target .
          }}
        }}
        GROUP BY ?target
        """
        data = query_wikidata(sparql)
        if data:
            for b in data.get("results", {}).get("bindings", []):
                uri = b.get("target", {}).get("value", "")
                qid = uri.split("/")[-1] if uri else ""
                count = int(b.get("count", {}).get("value", 0))
                if qid:
                    result[qid] = count
        time.sleep(0.5)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--acad", type=Path, default=Path("CSV/disciplines_academic.csv"))
    parser.add_argument("--field", type=Path, default=Path("CSV/disciplines_academic_field.csv"))
    parser.add_argument("--output", "-o", type=Path, help="Write comparison report")
    args = parser.parse_args()

    if not args.acad.exists():
        print(f"Not found: {args.acad}")
        sys.exit(1)
    if not args.field.exists():
        print(f"Not found: {args.field}")
        sys.exit(1)

    acad_rows = list(csv.DictReader(open(args.acad, encoding="utf-8")))
    field_rows = list(csv.DictReader(open(args.field, encoding="utf-8")))

    acad_qids = [r["qid"] for r in acad_rows]
    field_qids = [r["qid"] for r in field_rows]
    acad_by_qid = {r["qid"]: r for r in acad_rows}
    field_by_qid = {r["qid"]: r for r in field_rows}

    print(f"Academic only: {len(acad_qids)} disciplines")
    print(f"Academic+Field: {len(field_qids)} disciplines")
    print()

    # Fetch backlink counts for both (field is subset, but we need both for comparison)
    all_qids = list(dict.fromkeys(acad_qids + field_qids))
    print(f"Fetching P31 backlink counts for {len(all_qids)} unique QIDs (batches of {BATCH_SIZE})...")
    counts = fetch_backlink_counts(all_qids)
    print(f"  Got counts for {len(counts)} QIDs")
    print()

    # Aggregate for each list
    def stats(qids: list[str], label: str) -> dict:
        c = [counts.get(q, 0) for q in qids]
        total = sum(c)
        with_backlinks = sum(1 for x in c if x > 0)
        return {
            "label": label,
            "n": len(qids),
            "total_backlinks": total,
            "with_backlinks": with_backlinks,
            "pct_with": 100 * with_backlinks / len(qids) if qids else 0,
            "mean": total / len(qids) if qids else 0,
            "counts": c,
        }

    acad_s = stats(acad_qids, "Academic only")
    field_s = stats(field_qids, "Academic+Field")

    print("=" * 60)
    print("BACKLINK COMPARISON (P31 + P279 + P361)")
    print("=" * 60)
    print(f"{'Metric':<25} {'Academic only':>15} {'Academic+Field':>15}")
    print("-" * 60)
    print(f"{'Disciplines':<25} {acad_s['n']:>15} {field_s['n']:>15}")
    print(f"{'Total backlinks':<25} {acad_s['total_backlinks']:>15,} {field_s['total_backlinks']:>15,}")
    print(f"{'With any backlinks':<25} {acad_s['with_backlinks']:>15} {field_s['with_backlinks']:>15}")
    print(f"{'% with backlinks':<25} {acad_s['pct_with']:>14.1f}% {field_s['pct_with']:>14.1f}%")
    print(f"{'Mean backlinks/discipline':<25} {acad_s['mean']:>14.1f} {field_s['mean']:>14.1f}")
    print()

    # Backlinks per discipline (field gets more on average per discipline)
    if field_s["n"]:
        print(f"Academic+Field: {field_s['total_backlinks']:,} total backlinks / {field_s['n']} disciplines")
        print(f"  = {field_s['mean']:.1f} per discipline on average")
    if acad_s["n"]:
        print(f"Academic only:  {acad_s['total_backlinks']:,} total backlinks / {acad_s['n']} disciplines")
        print(f"  = {acad_s['mean']:.1f} per discipline on average")
    print()

    # Top disciplines by backlinks in each list
    def top_n(qids: list[str], label: str, n: int = 15):
        ranked = [(q, counts.get(q, 0), acad_by_qid.get(q, field_by_qid.get(q, {})).get("label", "")) for q in qids]
        ranked.sort(key=lambda x: -x[1])
        print(f"Top {n} by backlinks ({label}):")
        for q, c, lbl in ranked[:n]:
            print(f"  {c:>8,}  {q}  {lbl[:50]}")
        print()

    top_n(acad_qids, "Academic only")
    top_n(field_qids, "Academic+Field")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("qid,label,list,backlinks\n")
            for q in acad_qids:
                r = acad_by_qid.get(q, {})
                f.write(f"{q},{r.get('label','')!r},academic_only,{counts.get(q,0)}\n")
            for q in field_qids:
                r = field_by_qid.get(q, {})
                f.write(f"{q},{r.get('label','')!r},academic_field,{counts.get(q,0)}\n")
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
