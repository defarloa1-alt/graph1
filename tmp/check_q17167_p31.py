#!/usr/bin/env python3
"""Check Q17167 P31: what it is instance of, and what instances point to it."""
import requests

SPARQL = "https://query.wikidata.org/sparql"
headers = {"Accept": "application/json", "User-Agent": "Chrystallum/1.0"}

# 1) What is Q17167 (Roman Republic) an instance OF? (outbound P31)
q1 = """
SELECT ?type ?typeLabel WHERE {
  wd:Q17167 wdt:P31 ?type .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""
# 2) What entities are instance OF Q17167? (inbound P31 - instances of Roman Republic)
q2 = """
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q17167 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 50
"""

for name, q in [
    ("Q17167 instance of (outbound - what Roman Republic IS)", q1),
    ("Entities instance OF Q17167 (inbound - instances of Roman Republic)", q2),
]:
    r = requests.get(SPARQL, params={"query": q}, headers=headers, timeout=30)
    rows = r.json().get("results", {}).get("bindings", [])
    print(name)
    for row in rows:
        lab = row.get("typeLabel", row.get("itemLabel", {}))
        val = lab.get("value", "") if isinstance(lab, dict) else str(lab)
        uri = row.get("type", row.get("item", {}))
        qid = uri.get("value", "").split("/")[-1] if isinstance(uri, dict) else ""
        print(f"  {qid}: {val}")
    print()
