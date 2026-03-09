#!/usr/bin/env python3
"""
Fetch academic disciplines (P31=Q11862829) with authority IDs from Wikidata.
Filter: keep only items with at least one of LCSH, FAST, LCC, DDC.
Output: Disciplines/disciplines_with_authority.csv
"""
import requests
import csv
import time
from pathlib import Path

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "ChrystallumBot/1.0 (research project)"
PROJECT = Path(__file__).resolve().parents[2]

sparql = """
SELECT ?item ?itemLabel ?parent ?parentLabel
       ?lcsh ?fast ?lcc ?ddc
WHERE {
  ?item wdt:P31 wd:Q11862829 .
  OPTIONAL { ?item wdt:P279 ?parent . }
  OPTIONAL { ?item wdt:P244 ?lcsh . }
  OPTIONAL { ?item wdt:P2163 ?fast . }
  OPTIONAL { ?item wdt:P1149 ?lcc . }
  OPTIONAL { ?item wdt:P1036 ?ddc . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

def main():
    print("Querying Wikidata SPARQL (academic disciplines + authority IDs)...")
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    r = requests.get(SPARQL_URL, params={"query": sparql}, headers=headers, timeout=180)
    print(f"Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text[:500])
        return

    data = r.json()
    bindings = data["results"]["bindings"]
    print(f"Bindings: {len(bindings)}")

    items = {}
    for b in bindings:
        uri = b.get("item", {}).get("value", "")
        qid = uri.split("/")[-1]
        label = b.get("itemLabel", {}).get("value", "")
        if label.startswith("http://"):
            label = ""

        parent_uri = b.get("parent", {}).get("value", "")
        parent_qid = parent_uri.split("/")[-1] if parent_uri else ""
        parent_label = b.get("parentLabel", {}).get("value", "")
        if parent_label.startswith("http://"):
            parent_label = ""

        lcsh = b.get("lcsh", {}).get("value", "")
        fast = b.get("fast", {}).get("value", "")
        lcc = b.get("lcc", {}).get("value", "")
        ddc = b.get("ddc", {}).get("value", "")

        if qid not in items:
            items[qid] = {
                "qid": qid, "label": label or qid,
                "parents": set(), "parent_labels": {},
                "lcsh": set(), "fast": set(), "lcc": set(), "ddc": set(),
            }
        if parent_qid:
            items[qid]["parents"].add(parent_qid)
            if parent_label:
                items[qid]["parent_labels"][parent_qid] = parent_label
        if lcsh: items[qid]["lcsh"].add(lcsh)
        if fast: items[qid]["fast"].add(fast)
        if lcc: items[qid]["lcc"].add(lcc)
        if ddc: items[qid]["ddc"].add(ddc)

    print(f"Unique disciplines: {len(items)}")

    # Filter: keep only those with at least one backbone authority ID
    has_auth = {qid: item for qid, item in items.items()
                if item["lcsh"] or item["fast"] or item["lcc"] or item["ddc"]}

    no_auth = len(items) - len(has_auth)
    print(f"With LCSH|FAST|LCC|DDC: {len(has_auth)}")
    print(f"Filtered out (no authority): {no_auth}")

    has_lcsh = sum(1 for i in has_auth.values() if i["lcsh"])
    has_fast = sum(1 for i in has_auth.values() if i["fast"])
    has_lcc = sum(1 for i in has_auth.values() if i["lcc"])
    has_ddc = sum(1 for i in has_auth.values() if i["ddc"])
    print(f"  LCSH: {has_lcsh}  FAST: {has_fast}  LCC: {has_lcc}  DDC: {has_ddc}")

    # Write filtered CSV
    outpath = PROJECT / "Disciplines" / "disciplines_with_authority.csv"
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["qid", "label", "subclass_of", "subclass_of_label", "lcsh_id", "fast_id", "lcc", "ddc"]

    rows = []
    for item in sorted(has_auth.values(), key=lambda x: x["label"].lower()):
        parents = sorted(item["parents"])
        parent_labels = [item["parent_labels"].get(p, p) for p in parents]
        rows.append({
            "qid": item["qid"],
            "label": item["label"],
            "subclass_of": "|".join(parents),
            "subclass_of_label": "|".join(parent_labels),
            "lcsh_id": "|".join(sorted(item["lcsh"])),
            "fast_id": "|".join(sorted(item["fast"])),
            "lcc": "|".join(sorted(item["lcc"])),
            "ddc": "|".join(sorted(item["ddc"])),
        })

    with open(outpath, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {outpath}")


if __name__ == "__main__":
    main()
