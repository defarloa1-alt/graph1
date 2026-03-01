#!/usr/bin/env python3
"""
Build academic discipline taxonomy from Wikidata (no LLM).

1. Fetch items that are both academic discipline (Q11862829) and field of study (Q2267705)
2. Expand via P279 (subclass of) and P527 (has part(s))
3. Fetch authority IDs: P2163 FAST, P227 GND, P244 LCSH, P1036 DDC, P1014 AAT,
   P2581 BabelNet, P8408 KBpedia, P9000 World History, P1149 LCC
4. Output CSV with tree structure and authority IDs

Usage:
  python scripts/backbone/subject/build_discipline_taxonomy.py
  python scripts/backbone/subject/build_discipline_taxonomy.py --output output/discipline_taxonomy.csv
"""

import argparse
import csv
import sys
import time
from pathlib import Path

import requests

_PROJECT = Path(__file__).resolve().parents[3]  # Graph1 root
SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "ChrystallumBot/1.0 (research project)"

AUTHORITY_PROPS = {
    "P2163": "fast_id",
    "P227": "gnd_id",
    "P244": "lcsh_id",
    "P1036": "ddc",
    "P1014": "aat_id",
    "P2581": "babelnet_id",
    "P8408": "kbpedia_id",
    "P9000": "world_history_id",
    "P1149": "lcc",
}


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
    """Fetch entity data from Wikidata API."""
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
    """Extract main value from a claim (external ID string or entity QID)."""
    snak = claim.get("mainsnak", {})
    if snak.get("snaktype") != "value":
        return ""
    val = snak.get("datavalue", {}).get("value")
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        if "id" in val:
            return val["id"]
        if "amount" in val:
            return val.get("amount", "")
    return str(val) if val else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", "-o", type=Path, default=_PROJECT / "output" / "discipline_taxonomy.csv")
    parser.add_argument("--expand-levels", type=int, default=2, help="Levels to expand P279/P527 (default 2)")
    args = parser.parse_args()

    # 1. Seed: items that are both academic discipline and field of study
    print("1. Fetching seed items (academic discipline + field of study)...")
    sparql = """
    SELECT ?item ?itemLabel WHERE {
      ?item wdt:P31 wd:Q11862829 .
      ?item wdt:P31 wd:Q2267705 .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    ORDER BY ?itemLabel
    """
    data = query_sparql(sparql)
    if not data:
        print("  Failed to fetch seed items")
        sys.exit(1)

    seed = []
    for b in data.get("results", {}).get("bindings", []):
        uri = b.get("item", {}).get("value", "")
        qid = uri.split("/")[-1] if uri else ""
        lbl = b.get("itemLabel", {}).get("value", "")
        if lbl and lbl.startswith("http://"):
            lbl = ""  # no English label
        seed.append({"qid": qid, "label": lbl or qid})
    print(f"  Found {len(seed)} seed items")
    all_qids = set(s["qid"] for s in seed)

    # 2. Expand via P279 (subclass of) and P527 (has part(s))
    # Batch by ~50 items to avoid URL length limits (GET)
    print("2. Expanding tree via P279 and P527...")
    BATCH = 50
    for level in range(args.expand_levels - 1):
        prev = len(all_qids)
        items = list(all_qids)
        for i in range(0, len(items), BATCH):
            batch_items = items[i : i + BATCH]
            values = " ".join(f"wd:{q}" for q in batch_items)
            sparql = f"""
            SELECT DISTINCT ?expand WHERE {{
              VALUES ?item {{ {values} }}
              {{ ?item wdt:P279 ?expand }} UNION {{ ?item wdt:P527 ?expand }}
            }}
            """
            data = query_sparql(sparql)
            if data:
                for b in data.get("results", {}).get("bindings", []):
                    uri = b.get("expand", {}).get("value", "")
                    if uri and "wikidata.org/entity/" in uri:
                        all_qids.add(uri.split("/")[-1])
            time.sleep(0.3)
        if len(all_qids) == prev:
            break
    print(f"  Expanded to {len(all_qids)} items")

    # 3. Fetch labels and authority IDs via API
    print("3. Fetching labels and authority IDs...")
    entities = fetch_entities_api(list(all_qids))

    labels = {}
    for qid, ent in entities.items():
        if ent.get("missing"):
            continue
        lbl = ent.get("labels", {}).get("en", {}).get("value", "")
        if lbl:
            labels[qid] = lbl

    # Build rows: seed + expanded (only include items we have labels for, or all)
    rows_by_qid = {}
    for s in seed:
        qid = s["qid"]
        rows_by_qid[qid] = {
            "qid": qid,
            "label": labels.get(qid, s.get("label", qid)),
            "subclass_of": "",
            "subclass_of_label": "",
            "part_of": "",
            "part_of_label": "",
            "has_parts": "",
            "has_parts_label": "",
            **{v: "" for v in AUTHORITY_PROPS.values()},
        }

    # Add expanded items not in seed
    for qid in all_qids:
        if qid not in rows_by_qid:
            rows_by_qid[qid] = {
                "qid": qid,
                "label": labels.get(qid, qid),
                "subclass_of": "",
                "subclass_of_label": "",
                "part_of": "",
                "part_of_label": "",
                "has_parts": "",
                "has_parts_label": "",
                **{v: "" for v in AUTHORITY_PROPS.values()},
            }

    # Fetch P279, P527, and authority props for each
    for qid, ent in entities.items():
        if qid not in rows_by_qid:
            continue
        row = rows_by_qid[qid]
        claims = ent.get("claims", {})

        p279 = claims.get("P279", [])
        if p279:
            vals = [extract_claim_value(c) for c in p279 if extract_claim_value(c)]
            row["subclass_of"] = "|".join(vals)
            row["subclass_of_label"] = "|".join(labels.get(v, v) for v in vals)

        p361 = claims.get("P361", [])
        if p361:
            vals = [extract_claim_value(c) for c in p361 if extract_claim_value(c)]
            row["part_of"] = "|".join(vals)
            row["part_of_label"] = "|".join(labels.get(v, v) for v in vals)

        p527 = claims.get("P527", [])
        if p527:
            vals = [extract_claim_value(c) for c in p527 if extract_claim_value(c)]
            row["has_parts"] = "|".join(vals)
            row["has_parts_label"] = "|".join(labels.get(v, v) for v in vals)

        for pid, col in AUTHORITY_PROPS.items():
            cl = claims.get(pid, [])
            if cl:
                vals = [extract_claim_value(c) for c in cl if extract_claim_value(c)]
                row[col] = "|".join(vals)

    # Fill labels for referenced QIDs
    ref_qids = set()
    for row in rows_by_qid.values():
        for col in ("subclass_of", "part_of", "has_parts"):
            for q in (row.get(col) or "").split("|"):
                if q.strip() and q not in labels:
                    ref_qids.add(q)
    if ref_qids:
        extra = fetch_entities_api(list(ref_qids))
        for qid, ent in extra.items():
            lbl = ent.get("labels", {}).get("en", {}).get("value", "")
            if lbl:
                labels[qid] = lbl
        for row in rows_by_qid.values():
            for col, label_col in [
                ("subclass_of", "subclass_of_label"),
                ("part_of", "part_of_label"),
                ("has_parts", "has_parts_label"),
            ]:
                qids = [q.strip() for q in (row.get(col) or "").split("|") if q.strip()]
                row[label_col] = "|".join(labels.get(q, q) for q in qids)

    rows = list(rows_by_qid.values())
    print(f"  {len(rows)} items")

    # 4. Write CSV
    fieldnames = [
        "qid", "label", "subclass_of", "subclass_of_label",
        "part_of", "part_of_label", "has_parts", "has_parts_label",
    ] + list(AUTHORITY_PROPS.values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["label"] or r["qid"])))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
