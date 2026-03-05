#!/usr/bin/env python3
"""For each historical country (backlink to Q3024240), get its P31 (instance of) values."""
import requests

SPARQL = "https://query.wikidata.org/sparql"
headers = {"Accept": "application/json", "User-Agent": "Chrystallum/1.0"}

# 1) Get the historical countries (backlinks to Q3024240 via P31)
q_list = """
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q3024240 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 50
"""
r = requests.get(SPARQL, params={"query": q_list}, headers=headers, timeout=60)
items = [
    (row["item"]["value"].split("/")[-1], row.get("itemLabel", {}).get("value", ""))
    for row in r.json().get("results", {}).get("bindings", [])
]

# 2) For each item, get its P31 values (what is it instance of?)
# Batch query: all items and their P31 types
qids = [x[0] for x in items]
ids_str = " ".join(f"wd:{q}" for q in qids[:50])

q_p31 = f"""
SELECT ?item ?type ?typeLabel WHERE {{
  VALUES ?item {{ {ids_str} }}
  ?item wdt:P31 ?type .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""
r2 = requests.get(SPARQL, params={"query": q_p31}, headers=headers, timeout=60)
rows = r2.json().get("results", {}).get("bindings", [])

# Build item -> [types]
by_item = {}
for row in rows:
    item = row["item"]["value"].split("/")[-1]
    typ = row["type"]["value"].split("/")[-1]
    typ_label = row.get("typeLabel", {}).get("value", typ)
    by_item.setdefault(item, []).append((typ, typ_label))

# Print
label_map = {qid: lab for qid, lab in items}
print("Instance-of (P31) for each historical country:")
print("=" * 60)
for qid, lab in items[:30]:
    types = by_item.get(qid, [])
    type_str = ", ".join(f"{t[0]} ({t[1]})" for t in types)
    print(f"{qid} {lab}:")
    print(f"  P31: {type_str}")
    print()
