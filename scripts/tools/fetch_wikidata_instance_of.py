#!/usr/bin/env python3
"""
Fetch all Wikidata items that are instance of a given class (e.g. Q11862829 = academic discipline).

Usage:
  python scripts/tools/fetch_wikidata_instance_of.py Q11862829
  python scripts/tools/fetch_wikidata_instance_of.py Q11862829 --output output/disciplines.csv
  python scripts/tools/fetch_wikidata_instance_of.py Q11862829 --and-instance-of Q2267705 --output output/disciplines_academic_field.csv
  # Q11862829 = academic discipline, Q2267705 = field of study
"""

import argparse
import csv
import sys
import time
from pathlib import Path

import requests

SPARQL_URL = "https://query.wikidata.org/sparql"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "ChrystallumBot/1.0 (research project)"


def query_wikidata(sparql: str, max_retries: int = 3) -> dict | None:
    """Execute SPARQL query with retry logic."""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": USER_AGENT,
    }
    for attempt in range(max_retries):
        try:
            r = requests.get(SPARQL_URL, params={"query": sparql}, headers=headers, timeout=120)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                wait = (attempt + 1) * 10
                print(f"  Rate limit, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  HTTP {r.status_code}: {r.reason}")
                time.sleep(5)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(5)
    return None


def _val(binding: dict | None, key: str) -> str:
    if not binding or key not in binding:
        return ""
    v = binding[key]
    if isinstance(v, dict) and "value" in v:
        val = v["value"]
        if val.startswith("http://www.wikidata.org/entity/"):
            return val.split("/")[-1]  # QID
        return val  # Label or description string
    return str(v) if v else ""


def _qid(b: dict | None, key: str) -> str:
    return _val(b, key)


def _label(b: dict | None, key: str) -> str:
    """Get label; if value is entity URI (no label fallback), return empty."""
    if not b or key not in b:
        return ""
    v = b[key]
    if isinstance(v, dict) and "value" in v:
        val = v["value"]
        if val.startswith("http://www.wikidata.org/entity/"):
            return ""
        return val
    return str(v) if v else ""


def fetch_labels_via_api(qids: list[str]) -> dict[str, str]:
    """Fetch labels for QIDs via Wikidata API (for items with no label in SPARQL)."""
    if not qids:
        return {}
    result = {}
    for i in range(0, len(qids), 50):
        batch = qids[i : i + 50]
        ids = "|".join(batch)
        r = requests.get(
            WIKIDATA_API,
            params={
                "action": "wbgetentities",
                "ids": ids,
                "props": "labels",
                "languages": "en",
                "format": "json",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        if r.status_code != 200:
            continue
        data = r.json()
        for qid in batch:
            ent = data.get("entities", {}).get(qid, {})
            labels = ent.get("labels", {})
            if "en" in labels:
                result[qid] = labels["en"].get("value", "")
        time.sleep(0.2)  # be nice to the API
    return result


def fetch_instance_of(class_qid: str, class_label: str = "", and_instance_of: str | None = None) -> list[dict]:
    """Fetch all items that are instance of the given class. If and_instance_of is set, require both P31 values."""
    qid = class_qid.strip().upper()
    if not qid.startswith("Q"):
        qid = "Q" + qid
    label = class_label or qid

    and_filter = ""
    and_qid = ""
    if and_instance_of:
        and_qid = and_instance_of.strip().upper()
        if not and_qid.startswith("Q"):
            and_qid = "Q" + and_qid
        and_filter = f"\n      ?item wdt:P31 wd:{and_qid} ."

    sparql = f"""
    SELECT ?item ?itemLabel ?itemDescription
      (GROUP_CONCAT(DISTINCT ?p31; SEPARATOR="|") AS ?instanceOf)
      (GROUP_CONCAT(DISTINCT ?p361; SEPARATOR="|") AS ?partOf)
      (GROUP_CONCAT(DISTINCT ?p279; SEPARATOR="|") AS ?subclassOf)
      (GROUP_CONCAT(DISTINCT ?p31Label; SEPARATOR="|") AS ?instanceOfLabel)
      (GROUP_CONCAT(DISTINCT ?p361Label; SEPARATOR="|") AS ?partOfLabel)
      (GROUP_CONCAT(DISTINCT ?p279Label; SEPARATOR="|") AS ?subclassOfLabel)
    WHERE {{
      ?item wdt:P31 wd:{qid} .{and_filter}
      OPTIONAL {{ ?item wdt:P31 ?p31 . }}
      OPTIONAL {{ ?item wdt:P361 ?p361 . }}
      OPTIONAL {{ ?item wdt:P279 ?p279 . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    GROUP BY ?item ?itemLabel ?itemDescription
    ORDER BY ?itemLabel
    """
    msg = f"Querying items instance of {qid} ({label})"
    if and_instance_of:
        msg += f" AND {and_qid} (field of study)"
    print(f"{msg}...")
    data = query_wikidata(sparql)
    if not data:
        return []

    def _qids_from_concat(b: dict, key: str) -> str:
        """Extract pipe-separated QIDs from GROUP_CONCAT of URIs."""
        raw = _val(b, key)
        if not raw:
            return ""
        parts = raw.replace("http://www.wikidata.org/entity/", "").split("|")
        return "|".join(p.split("/")[-1] for p in parts if p.strip())

    def _labels_from_concat(b: dict, key: str) -> str:
        """Get pipe-separated labels, skipping URIs (no-label fallback)."""
        raw = _val(b, key)
        if not raw:
            return ""
        parts = raw.split("|")
        keep = [p for p in parts if p and not p.startswith("http://www.wikidata.org/entity/")]
        return "|".join(keep)

    rows = []
    for b in data.get("results", {}).get("bindings", []):
        item_qid = _qid(b, "item")
        lbl = _label(b, "itemLabel")
        rows.append({
            "qid": item_qid,
            "label": lbl or item_qid,
            "description": _label(b, "itemDescription"),
            "instance_of": _qids_from_concat(b, "instanceOf"),
            "instance_of_label": _labels_from_concat(b, "instanceOfLabel"),
            "part_of": _qids_from_concat(b, "partOf"),
            "part_of_label": _labels_from_concat(b, "partOfLabel"),
            "subclass_of": _qids_from_concat(b, "subclassOf"),
            "subclass_of_label": _labels_from_concat(b, "subclassOfLabel"),
        })

    # Second pass: fetch labels via API for items that still have QID-as-label
    need_labels = [r["qid"] for r in rows if r["label"] == r["qid"]]
    if need_labels:
        print(f"  Fetching labels for {len(need_labels)} items via API...")
        api_labels = fetch_labels_via_api(need_labels)
        for r in rows:
            if r["qid"] in api_labels:
                r["label"] = api_labels[r["qid"]]

    # Filter out items whose label is just the QID (no English label)
    rows = [r for r in rows if r["label"] != r["qid"]]

    # Third pass: fetch labels for all referenced QIDs (instance_of, part_of, subclass_of)
    ref_qids = set()
    for r in rows:
        for col in ("instance_of", "part_of", "subclass_of"):
            for q in (r.get(col) or "").split("|"):
                if q.strip():
                    ref_qids.add(q.strip())
    if ref_qids:
        print(f"  Fetching labels for {len(ref_qids)} referenced QIDs...")
        ref_labels = fetch_labels_via_api(list(ref_qids))
        for r in rows:
            for qid_col, label_col in [
                ("instance_of", "instance_of_label"),
                ("part_of", "part_of_label"),
                ("subclass_of", "subclass_of_label"),
            ]:
                qids = [q.strip() for q in (r.get(qid_col) or "").split("|") if q.strip()]
                labels = [ref_labels.get(q, q) for q in qids]
                r[label_col] = "|".join(labels)

    return rows


def main():
    parser = argparse.ArgumentParser(description="Fetch Wikidata items instance of a class")
    parser.add_argument("class_qid", help="Class QID (e.g. Q11862829 for academic discipline)")
    parser.add_argument("--and-instance-of", metavar="QID", default=None,
        help="Require items to also be instance of this class (e.g. Q2267705 = field of study)")
    parser.add_argument("--label", default="", help="Optional class label for display")
    parser.add_argument("--output", "-o", type=Path, help="Output CSV path")
    args = parser.parse_args()

    rows = fetch_instance_of(args.class_qid, args.label, args.and_instance_of)
    print(f"Found {len(rows)} items")

    if not rows:
        return

    fieldnames = ["qid", "label", "description", "instance_of", "instance_of_label", "part_of", "part_of_label", "subclass_of", "subclass_of_label"]
    out = args.output
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        print(f"Wrote {out}")
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
