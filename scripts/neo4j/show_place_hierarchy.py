#!/usr/bin/env python3
"""Print sample place hierarchy from Neo4j."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD or ""))
with driver.session() as s:
    # Stats
    total = s.run("MATCH (p:Place) WHERE p.pleiades_id IS NOT NULL RETURN count(p) AS c").single()["c"]
    with_parent = s.run("""
        MATCH (p:Place)-[:LOCATED_IN]->()
        WHERE p.pleiades_id IS NOT NULL
        RETURN count(DISTINCT p) AS c
    """).single()["c"]
    print(f"Place hierarchy: {with_parent} of {total} Pleiades places have LOCATED_IN parent\n")

    # Pleiades Place -> parent (Wikidata)
    r = s.run("""
        MATCH (c:Place)-[:LOCATED_IN]->(p:Place)
        WHERE c.pleiades_id IS NOT NULL
        RETURN c.label AS child, c.pleiades_id AS pid, p.label AS parent, p.qid AS parent_qid
        LIMIT 10
    """)
    rows = list(r)

    # Multi-level chain if any (place -> region -> country)
    chains = s.run("""
        MATCH path = (a:Place)-[:LOCATED_IN*2..3]->(top:Place)
        WHERE a.pleiades_id IS NOT NULL AND NOT (top)-[:LOCATED_IN]->()
        WITH nodes(path) AS nds
        RETURN [n IN nds | n.label + ' (' + coalesce(n.pleiades_id, n.qid, '') + ')'] AS chain
        LIMIT 3
    """)
    chain_rows = list(chains)
driver.close()

print("LOCATED_IN examples: Pleiades Place -> parent (Wikidata qid)")
print("-" * 60)
for row in rows:
    print(f"  {row['child']} ({row['pid']}) -> {row['parent']} ({row['parent_qid']})")

if chain_rows:
    print("\nMulti-level chains (place -> region -> country):")
    print("-" * 60)
    for row in chain_rows:
        print("  " + " -> ".join(row["chain"]))
print(f"\n(Showing {len(rows)} examples)")
