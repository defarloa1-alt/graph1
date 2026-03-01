#!/usr/bin/env python3
"""
Fetch academic majors from Wikidata and compare to discipline taxonomy.

Sources:
  1. Items instance of Q4671286 (academic major)
  2. Distinct values of P812 (academic major) - majors people have studied

Output:
  - output/academic_majors.csv (all majors with labels, authority IDs)
  - output/academic_majors_vs_disciplines.csv (comparison: in_both, majors_only, disciplines_only)

Usage:
  python scripts/backbone/subject/fetch_academic_majors.py
"""

import argparse
import csv
import sys
import time
from pathlib import Path

import requests

_PROJECT = Path(__file__).resolve().parents[3]
SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "ChrystallumBot/1.0 (research project)"

AUTHORITY_PROPS = ("P2163", "P227", "P244", "P1036", "P1014", "P1149")


def query_sparql(sparql: str, max_retries: int = 3) -> dict | None:
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    for attempt in range(max_retries):
        try:
            r = requests.get(SPARQL_URL, params={"query": sparql}, headers=headers, timeout=120)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                time.sleep((attempt + 1) * 10)
            else:
                time.sleep(5)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(5)
    return None


def fetch_entities_api(qids: list[str], props: str = "labels|claims") -> dict:
    result = {}
    for i in range(0, len(qids), 50):
        batch = qids[i : i + 50]
        r = requests.get(
            WIKIDATA_API,
            params={"action": "wbgetentities", "ids": "|".join(batch), "props": props, "format": "json"},
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        if r.status_code == 200:
            result.update(r.json().get("entities", {}))
        time.sleep(0.2)
    return result


def extract_claim_value(claim: dict) -> str:
    snak = claim.get("mainsnak", {})
    if snak.get("snaktype") != "value":
        return ""
    val = snak.get("datavalue", {}).get("value")
    if isinstance(val, str):
        return val
    if isinstance(val, dict) and "id" in val:
        return val["id"]
    return str(val) if val else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output-dir", type=Path, default=_PROJECT / "output")
    parser.add_argument("--disciplines", type=Path, default=_PROJECT / "output" / "discipline_taxonomy_backbone.csv")
    args = parser.parse_args()

    all_qids = set()

    # 1. Items instance of Q4671286 (academic major)
    print("1. Fetching items instance of academic major (Q4671286)...")
    sparql = """
    SELECT ?item ?itemLabel WHERE {
      ?item wdt:P31 wd:Q4671286 .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """
    data = query_sparql(sparql)
    if data:
        for b in data.get("results", {}).get("bindings", []):
            uri = b.get("item", {}).get("value", "")
            if "wikidata.org/entity/" in uri:
                all_qids.add(uri.split("/")[-1])
    print(f"   Found {len(all_qids)} from Q4671286")

    # 2. Distinct values of P812 (academic major - what people studied)
    print("2. Fetching distinct P812 (academic major) values...")
    sparql = """
    SELECT DISTINCT ?major WHERE {
      ?person wdt:P812 ?major .
    }
    """
    data = query_sparql(sparql)
    if data:
        prev = len(all_qids)
        for b in data.get("results", {}).get("bindings", []):
            uri = b.get("major", {}).get("value", "")
            if "wikidata.org/entity/" in uri:
                all_qids.add(uri.split("/")[-1])
        print(f"   Added {len(all_qids) - prev} from P812 (total {len(all_qids)})")

    if not all_qids:
        print("No majors found")
        sys.exit(1)

    # 3. Fetch labels and authority IDs
    print("3. Fetching labels and authority IDs...")
    entities = fetch_entities_api(list(all_qids))
    labels = {}
    rows = []
    for qid, ent in entities.items():
        if ent.get("missing"):
            continue
        lbl = ent.get("labels", {}).get("en", {}).get("value", "")
        if not lbl and ent.get("labels"):
            lbl = next(iter(ent["labels"].values()), {}).get("value", qid)
        labels[qid] = lbl or qid
        claims = ent.get("claims", {})
        row = {"qid": qid, "label": labels[qid]}
        for pid in AUTHORITY_PROPS:
            col = {"P2163": "fast_id", "P227": "gnd_id", "P244": "lcsh_id", "P1036": "ddc", "P1014": "aat_id", "P1149": "lcc"}.get(pid, pid.lower())
            vals = [extract_claim_value(c) for c in claims.get(pid, []) if extract_claim_value(c)]
            row[col] = "|".join(vals) if vals else ""
        rows.append(row)

    # Filter to items with English labels
    rows = [r for r in rows if r["label"] != r["qid"]]
    rows.sort(key=lambda r: (r["label"] or r["qid"]))
    print(f"   {len(rows)} majors with labels")

    # 4. Write majors CSV
    majors_path = args.output_dir / "academic_majors.csv"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fieldnames = ["qid", "label", "fast_id", "gnd_id", "lcsh_id", "ddc", "aat_id", "lcc"]
    with open(majors_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"   Wrote {majors_path}")

    # 5. Compare to discipline taxonomy
    if not args.disciplines.exists():
        print(f"   Discipline file not found: {args.disciplines}")
        return

    discipline_by_qid = {}
    with open(args.disciplines, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            qid = (r.get("qid") or "").strip()
            if qid:
                discipline_by_qid[qid] = r

    discipline_qids = set(discipline_by_qid)
    majors_qids = {r["qid"] for r in rows}
    in_both = majors_qids & discipline_qids
    majors_only = majors_qids - discipline_qids
    disciplines_only = discipline_qids - majors_qids

    print("\n4. Comparison:")
    print(f"   Majors:        {len(majors_qids)}")
    print(f"   Disciplines:   {len(discipline_qids)}")
    print(f"   In both:       {len(in_both)}")
    print(f"   Majors only:   {len(majors_only)}")
    print(f"   Disciplines only: {len(disciplines_only)}")

    # Write comparison CSV: all majors + disciplines_only, with in_discipline_taxonomy and in_majors
    comp_path = args.output_dir / "academic_majors_vs_disciplines.csv"
    comp_rows = []
    for r in rows:
        qid = r["qid"]
        comp_rows.append({**r, "in_discipline_taxonomy": "yes" if qid in discipline_qids else "no", "in_majors": "yes"})
    for qid in disciplines_only:
        d = discipline_by_qid.get(qid, {})
        comp_rows.append({
            "qid": qid,
            "label": d.get("label", ""),
            "fast_id": d.get("fast_id", ""),
            "gnd_id": d.get("gnd_id", ""),
            "lcsh_id": d.get("lcsh_id", ""),
            "ddc": d.get("ddc", ""),
            "aat_id": d.get("aat_id", ""),
            "lcc": d.get("lcc", ""),
            "in_discipline_taxonomy": "yes",
            "in_majors": "no",
        })
    comp_rows.sort(key=lambda r: (r.get("in_discipline_taxonomy", "z"), r.get("in_majors", "z"), r.get("label", "")))
    comp_fieldnames = ["qid", "label", "in_discipline_taxonomy", "in_majors", "fast_id", "gnd_id", "lcsh_id", "ddc", "aat_id", "lcc"]
    with open(comp_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=comp_fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(comp_rows)
    print(f"   Wrote {comp_path}")

    # Write majors_only for easy review
    majors_only_path = args.output_dir / "academic_majors_not_in_disciplines.csv"
    majors_only_rows = [r for r in rows if r["qid"] in majors_only]
    with open(majors_only_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(majors_only_rows)
    print(f"   Wrote {majors_only_path} (majors not in discipline taxonomy)")


if __name__ == "__main__":
    main()
