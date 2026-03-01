#!/usr/bin/env python3
"""Print DG/DE/DF/KJA/PA-Roman LCC hierarchy as indented outline."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session() as s:
    r = s.run(
        "MATCH (l:LCC_Class) WHERE l.prefix IN ['DG','DE','DF','KJA'] "
        "OR (l.prefix = 'PA' AND l.label CONTAINS 'Roman') "
        "RETURN l.code as code, l.label as label, l.prefix as prefix ORDER BY l.prefix, l.start"
    ).data()

    edges = s.run(
        "MATCH (p:LCC_Class)-[:BROADER_THAN]->(c:LCC_Class) "
        "WHERE p.prefix IN ['DG','DE','DF','KJA'] OR (p.prefix = 'PA' AND p.label CONTAINS 'Roman') "
        "RETURN p.code as parent, c.code as child"
    ).data()

driver.close()

children = {}
for e in edges:
    children.setdefault(e["parent"], []).append(e["child"])

has_parent = {e["child"] for e in edges}
roots = [x["code"] for x in r if x["code"] not in has_parent]

code_to_label = {x["code"]: x["label"] for x in r}
code_to_prefix = {x["code"]: x["prefix"] for x in r}


def outline(code, depth=0):
    indent = "  " * depth
    label = code_to_label.get(code, code)
    print(f"{indent}{code}  {label}")
    for child in sorted(children.get(code, []), key=lambda c: code_to_label.get(c, c)):
        outline(child, depth + 1)


for root in sorted(roots, key=lambda c: (code_to_prefix.get(c, ""), c)):
    outline(root)
