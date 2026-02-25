#!/usr/bin/env python3
"""Investigate Schema 5 and 6 - Wikidata-only nodes."""
from neo4j import GraphDatabase
from pathlib import Path
import json

env = Path(__file__).resolve().parents[2] / ".env"
vars = {}
for line in env.read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        vars[k.strip()] = v.strip()

driver = GraphDatabase.driver(
    vars["NEO4J_URI"],
    auth=(vars["NEO4J_USERNAME"], vars["NEO4J_PASSWORD"]),
)

with driver.session() as s:
    r = s.run("""
        MATCH (n:Schema)
        WHERE 'Wikidata' IN n.uses_federations AND size(n.uses_federations) = 1
        RETURN elementId(n) AS id, keys(n) AS keys, n
    """).data()

for row in r:
    n = dict(row["n"])
    for k, v in n.items():
        if hasattr(v, "isoformat"):
            n[k] = str(v)
    print("id:", row["id"], "keys:", row["keys"])
    print(json.dumps(n, indent=2, default=str))
    print("---")

driver.close()
