#!/usr/bin/env python3
"""Generate Cypher script to rename WIKIDATA_P* edges (no APOC needed)"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

print("Generating rename Cypher...")

with driver.session() as session:
    result = session.run("""
        CALL db.relationshipTypes() YIELD relationshipType
        WHERE relationshipType STARTS WITH 'WIKIDATA_P'
        RETURN relationshipType ORDER BY relationshipType
    """)
    
    types = [r['relationshipType'] for r in result]

driver.close()

print(f"Found {len(types)} types to rename")

# Generate Cypher
cypher_lines = []
cypher_lines.append("// Remove WIKIDATA_ prefix from relationship types")
cypher_lines.append(f"// Generated: {datetime.now()}")
cypher_lines.append("")

for old_type in types:
    new_type = old_type.replace('WIKIDATA_', '')
    
    cypher = f"""
// {old_type} -> {new_type}
MATCH (a)-[old:{old_type}]->(b)
CREATE (a)-[new:{new_type}]->(b)
SET new = properties(old)
WITH old
DELETE old;
"""
    cypher_lines.append(cypher)

# Save
with open('output/remove_wikidata_prefix.cypher', 'w') as f:
    f.write('\n'.join(cypher_lines))

print(f"Saved: output/remove_wikidata_prefix.cypher")
print(f"Lines: {len(cypher_lines)}")
print()
print("Run in Neo4j Browser or cypher-shell")
