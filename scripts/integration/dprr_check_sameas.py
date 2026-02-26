#!/usr/bin/env python3
"""Check if DPRR has owl:sameAs pointing to Wikidata URIs."""
import requests

ENDPOINT = "http://romanrepublic.ac.uk/rdf/endpoint/"
QUERY = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX vocab: <http://romanrepublic.ac.uk/rdf/ontology#>

SELECT ?person ?wikidataURI WHERE {
  ?person a vocab:Person .
  ?person owl:sameAs ?wikidataURI .
  FILTER(CONTAINS(STR(?wikidataURI), "wikidata.org"))
}
LIMIT 20
"""

headers = {"Accept": "application/sparql-results+json", "User-Agent": "Chrystallum/1.0"}
r = requests.get(ENDPOINT, params={"query": QUERY}, headers=headers, timeout=30)
r.raise_for_status()
data = r.json()
bindings = data.get("results", {}).get("bindings", [])
print(f"Results: {len(bindings)}")
for b in bindings:
    print(f"  {b.get('person',{}).get('value','')} -> {b.get('wikidataURI',{}).get('value','')}")
