#!/usr/bin/env python3
"""Query DPRR relationship type vocabulary and frequencies."""
import requests

ENDPOINT = "http://romanrepublic.ac.uk/rdf/endpoint/"
QUERY = """
PREFIX vocab: <http://romanrepublic.ac.uk/rdf/ontology#>

SELECT ?relType ?name (COUNT(?rel) AS ?count) WHERE {
  ?rel a vocab:RelationshipAssertion ;
       vocab:hasRelationship ?relType .
  OPTIONAL { ?relType vocab:hasName ?name }
}
GROUP BY ?relType ?name
ORDER BY DESC(?count)
"""

headers = {"Accept": "application/sparql-results+json", "User-Agent": "Chrystallum/1.0"}
r = requests.get(ENDPOINT, params={"query": QUERY}, headers=headers, timeout=60)
r.raise_for_status()
data = r.json()
bindings = data.get("results", {}).get("bindings", [])
print("DPRR Relationship Types (vocab:hasRelationship):")
print("-" * 60)
for b in bindings:
    rt = b.get("relType", {}).get("value", "")
    rid = rt.split("/")[-1] if rt else "?"
    name = b.get("name", {}).get("value", "(no name)") if b.get("name") else "(no name)"
    count = b.get("count", {}).get("value", "?")
    print(f"  {count:>6}  {rid:>3}  {name}")
