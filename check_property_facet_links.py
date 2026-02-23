#!/usr/bin/env python3
"""Check if PropertyMapping -> Facet -> Agent relationships exist"""

from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session() as session:
    print("Checking PropertyMapping -> Facet -> Agent relationships...")
    print()
    
    # Check HAS_PRIMARY_FACET relationships
    result = session.run("MATCH (pm:PropertyMapping)-[:HAS_PRIMARY_FACET]->() RETURN count(*) as c")
    has_primary = result.single()['c']
    print(f"HAS_PRIMARY_FACET relationships: {has_primary}")
    
    # Check ASSIGNED_TO_FACET relationships
    result = session.run("MATCH ()-[:ASSIGNED_TO_FACET]->(f:Facet) RETURN count(*) as c")
    assigned_to = result.single()['c']
    print(f"ASSIGNED_TO_FACET relationships: {assigned_to}")
    
    # Check Agents for Q17167
    result = session.run("""
        MATCH (a:Agent)-[:ASSIGNED_TO_FACET]->(f:Facet) 
        WHERE a.subject_id = 'Q17167' 
        RETURN count(a) as c
    """)
    q17167_agents = result.single()['c']
    print(f"Agents for Q17167 (Roman Republic): {q17167_agents}")
    print()
    
    # Check what relationships PropertyMapping actually has
    print("PropertyMapping relationships:")
    result = session.run("""
        MATCH (pm:PropertyMapping)-[r]->()
        RETURN type(r) as rel_type, count(*) as count
    """)
    pm_rels = list(result)
    if pm_rels:
        for rel in pm_rels:
            print(f"  {rel['rel_type']}: {rel['count']}")
    else:
        print("  [NONE] PropertyMapping nodes have NO outgoing relationships")
    print()
    
    # Check what Agent nodes exist
    print("Agent nodes:")
    result = session.run("MATCH (a:Agent) RETURN count(a) as count")
    agent_count = result.single()['count']
    print(f"  Total Agent nodes: {agent_count}")
    
    if agent_count > 0:
        result = session.run("""
            MATCH (a:Agent) 
            RETURN a.id, a.subject_id 
            LIMIT 5
        """)
        print("  Sample agents:")
        for r in result:
            print(f"    {r['a.id']}: subject={r['a.subject_id']}")

driver.close()

print()
print("=" * 80)
print("DIAGNOSIS:")
if has_primary == 0:
    print("[ISSUE] PropertyMapping nodes not linked to Facet nodes")
    print("  - HAS_PRIMARY_FACET relationships missing")
    print("  - PropertyMapping import may not have created relationships")
if assigned_to == 0:
    print("[ISSUE] No Agent -> Facet relationships")
    print("  - Agents may not be assigned to facets yet")
if q17167_agents == 0:
    print("[ISSUE] No agents for Roman Republic (Q17167)")
    print("  - Agent creation may not have happened")
