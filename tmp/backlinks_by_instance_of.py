#!/usr/bin/env python3
"""Categorize backlinks to historical country by their instance-of (P31) values."""
import requests

SPARQL = "https://query.wikidata.org/sparql"
headers = {"Accept": "application/json", "User-Agent": "Chrystallum/1.0"}

# Get historical countries and their P31 types in one query
q = """
SELECT ?item ?itemLabel ?type ?typeLabel WHERE {
  ?item wdt:P31 wd:Q3024240 .
  ?item wdt:P31 ?type .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""
r = requests.get(SPARQL, params={"query": q}, headers=headers, timeout=60)
rows = r.json().get("results", {}).get("bindings", [])

# Build: type -> [(qid, label)]
by_type = {}
for row in rows:
    item = row["item"]["value"].split("/")[-1]
    item_label = row.get("itemLabel", {}).get("value", "")
    typ = row["type"]["value"].split("/")[-1]
    typ_label = row.get("typeLabel", {}).get("value", typ)
    by_type.setdefault((typ, typ_label), []).append((item, item_label))

# Dedupe items per type (each item can have multiple P31)
for k in by_type:
    seen = set()
    unique = []
    for qid, lab in by_type[k]:
        if qid not in seen:
            seen.add(qid)
            unique.append((qid, lab))
    by_type[k] = unique

# Sort types by count (desc), then by label
sorted_types = sorted(by_type.items(), key=lambda x: (-len(x[1]), x[0][1]))

print("Backlinks to Q3024240 (historical country) — categorized by instance-of")
print("=" * 70)
for (typ, typ_label), items in sorted_types:
    print(f"\n{typ} ({typ_label}) — {len(items)} items:")
    for qid, lab in items[:15]:
        print(f"  {qid}: {lab}")
    if len(items) > 15:
        print(f"  ... and {len(items) - 15} more")
