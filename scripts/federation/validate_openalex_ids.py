"""
validate_openalex_ids.py

Validates and resolves OpenAlex concept IDs in discipline_taxonomy_p31_only.csv.

Three passes:
  1. Flag P-prefix IDs (invalid concept IDs)
  2. For multi-ID rows: call OpenAlex API for each C-ID, pick best match by
     display_name fuzzy similarity to discipline label. Write primary + alternatives.
  3. For single C-IDs: verify against OpenAlex API, flag mismatches.

Output:
  output/discipline_taxonomy_openalex_validated.csv  — clean IDs + status column
  output/discipline_taxonomy_openalex_review.csv     — rows needing manual review

Usage:
  python scripts/federation/validate_openalex_ids.py [--dry-run]
"""

import csv
import time
import json
import argparse
import re
from pathlib import Path

import requests
from difflib import SequenceMatcher

INPUT_CSV  = Path("output/discipline_taxonomy_p31_only.csv")
OUTPUT_CSV = Path("output/discipline_taxonomy_openalex_validated.csv")
REVIEW_CSV = Path("output/discipline_taxonomy_openalex_review.csv")
CACHE_FILE = Path("output/openalex_concept_cache.json")

OPENALEX_BASE = "https://api.openalex.org"
MAILTO        = "chrystallum@localhost"   # polite pool
FUZZY_FLOOR   = 0.60                      # minimum similarity to accept a match
SLEEP_BETWEEN = 0.12                      # ~8 req/sec, well inside polite pool


def fuzzy(a: str, b: str) -> float:
    a = a.lower().strip()
    b = b.lower().strip()
    return SequenceMatcher(None, a, b).ratio()


def load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict):
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch_concept(concept_id: str, cache: dict, dry_run: bool) -> dict | None:
    """Fetch concept metadata from OpenAlex. Returns dict with display_name, level, works_count."""
    if concept_id in cache:
        return cache[concept_id]

    if dry_run:
        return None

    url = f"{OPENALEX_BASE}/concepts/{concept_id}?mailto={MAILTO}"
    try:
        r = requests.get(url, timeout=15)
        time.sleep(SLEEP_BETWEEN)
        if r.status_code == 200:
            data = r.json()
            result = {
                "display_name": data.get("display_name", ""),
                "level": data.get("level"),
                "works_count": data.get("works_count", 0),
                "description": data.get("description", ""),
            }
            cache[concept_id] = result
            return result
        elif r.status_code == 404:
            cache[concept_id] = None
            return None
        else:
            print(f"  [WARN] {concept_id} → HTTP {r.status_code}")
            return None
    except Exception as e:
        print(f"  [ERROR] {concept_id}: {e}")
        return None


def resolve_ids(label: str, raw_ids: str, cache: dict, dry_run: bool) -> dict:
    """
    Given a discipline label and raw pipe-separated IDs, return:
      primary_id, primary_display, primary_sim, alternatives, status, notes
    """
    parts = [x.strip() for x in raw_ids.split("|") if x.strip()]

    p_ids = [p for p in parts if p.startswith("P")]
    c_ids = [p for p in parts if p.startswith("C")]
    other = [p for p in parts if not p.startswith("C") and not p.startswith("P")]

    notes = []
    if p_ids:
        notes.append(f"stripped_p_ids:{','.join(p_ids)}")
    if other:
        notes.append(f"unknown_prefix:{','.join(other)}")

    if not c_ids:
        return {
            "primary_id": "",
            "primary_display": "",
            "primary_sim": 0.0,
            "alternatives": "",
            "status": "id_type_error",
            "notes": "; ".join(notes) if notes else "no_valid_c_ids",
        }

    # Single valid C-ID
    if len(c_ids) == 1:
        cid = c_ids[0]
        meta = fetch_concept(cid, cache, dry_run)
        if meta is None:
            return {
                "primary_id": cid,
                "primary_display": "",
                "primary_sim": 0.0,
                "alternatives": "",
                "status": "not_found" if not dry_run else "dry_run",
                "notes": "; ".join(notes),
            }
        sim = fuzzy(label, meta["display_name"])
        status = "verified" if sim >= FUZZY_FLOOR else "needs_review"
        return {
            "primary_id": cid,
            "primary_display": meta["display_name"],
            "primary_sim": round(sim, 3),
            "alternatives": "",
            "status": status,
            "notes": "; ".join(notes),
        }

    # Multiple C-IDs — fetch all, pick best by similarity then works_count
    candidates = []
    for cid in c_ids:
        meta = fetch_concept(cid, cache, dry_run)
        if meta:
            sim = fuzzy(label, meta["display_name"])
            candidates.append((cid, meta, sim))
        else:
            candidates.append((cid, None, 0.0))

    if not dry_run:
        # Sort: verified first (sim >= floor), then by sim desc, then works_count desc
        candidates.sort(
            key=lambda x: (
                1 if x[2] >= FUZZY_FLOOR else 0,
                x[2],
                x[1]["works_count"] if x[1] else 0,
            ),
            reverse=True,
        )

    best_id, best_meta, best_sim = candidates[0]
    alts = "|".join(cid for cid, _, _ in candidates[1:])

    if dry_run:
        status = "dry_run"
    elif best_sim >= FUZZY_FLOOR:
        status = "verified_multi"
    else:
        status = "needs_review"

    notes.append(f"had_{len(c_ids)}_candidates")

    return {
        "primary_id": best_id,
        "primary_display": best_meta["display_name"] if best_meta else "",
        "primary_sim": round(best_sim, 3),
        "alternatives": alts,
        "status": status,
        "notes": "; ".join(notes),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Skip API calls, show what would happen")
    args = parser.parse_args()

    cache = load_cache()

    with open(INPUT_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    fieldnames = list(rows[0].keys()) + [
        "openalex_primary", "openalex_display", "openalex_sim",
        "openalex_alternatives", "openalex_status", "openalex_notes"
    ]

    out_rows = []
    review_rows = []

    total = len(rows)
    needs_api = sum(1 for r in rows if r.get("openalex_id", "").strip())
    print(f"Total rows: {total} | With existing IDs: {needs_api} | Dry-run: {args.dry_run}")

    for i, row in enumerate(rows):
        raw = row.get("openalex_id", "").strip()
        label = row.get("label", "")

        if not raw:
            row.update({
                "openalex_primary": "",
                "openalex_display": "",
                "openalex_sim": "",
                "openalex_alternatives": "",
                "openalex_status": "no_id",
                "openalex_notes": "",
            })
            out_rows.append(row)
            continue

        result = resolve_ids(label, raw, cache, args.dry_run)

        row.update({
            "openalex_primary": result["primary_id"],
            "openalex_display": result["primary_display"],
            "openalex_sim": result["primary_sim"],
            "openalex_alternatives": result["alternatives"],
            "openalex_status": result["status"],
            "openalex_notes": result["notes"],
        })
        out_rows.append(row)

        if result["status"] in ("needs_review", "id_type_error", "not_found"):
            review_rows.append(row)

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{total}] processed... cache={len(cache)}")
            if not args.dry_run:
                save_cache(cache)

    if not args.dry_run:
        save_cache(cache)

    # Write outputs
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    with open(REVIEW_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(review_rows)

    # Summary
    statuses = {}
    for r in out_rows:
        s = r["openalex_status"]
        statuses[s] = statuses.get(s, 0) + 1

    print("\n--- Summary ---")
    for s, count in sorted(statuses.items()):
        print(f"  {s:25s} {count}")
    print(f"\nOutput: {OUTPUT_CSV}")
    print(f"Review: {REVIEW_CSV} ({len(review_rows)} rows)")


if __name__ == "__main__":
    main()
