#!/usr/bin/env python3
"""Backlinks to Q3024240 (historical country) - what entities point TO historical country?"""
import requests

SPARQL = "https://query.wikidata.org/sparql"
headers = {"Accept": "application/json", "User-Agent": "Chrystallum/1.0"}

# Backlinks to historical country (Q3024240) - entities that have any property pointing to it
# Focus on P31 (instance of) first - entities that ARE instance of historical country
q = """
SELECT ?source ?sourceLabel ?prop WHERE {
  BIND(wd:Q3024240 AS ?target)
  ?source ?prop ?target .
  FILTER(?prop IN (wdt:P31, wdt:P279))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
"""

r = requests.get(SPARQL, params={"query": q}, headers=headers, timeout=60)
rows = r.json().get("results", {}).get("bindings", [])

# Group by property
by_prop = {}
for row in rows:
    src = row.get("source", {}).get("value", "").split("/")[-1]
    lab = row.get("sourceLabel", {}).get("value", "")
    prop = row.get("prop", {}).get("value", "").split("/")[-1]
    by_prop.setdefault(prop, []).append((src, lab))

print("Backlinks to Q3024240 (historical country)")
print("=" * 50)
for prop, items in sorted(by_prop.items()):
    print(f"\n{prop}:")
    for qid, label in items[:30]:
        print(f"  {qid}: {label}")
    if len(items) > 30:
        print(f"  ... and {len(items) - 30} more")
