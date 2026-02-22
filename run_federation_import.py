#!/usr/bin/env python3
from neo4j import GraphDatabase
from pathlib import Path

# Read the Cypher file
cypher_file = Path("scripts/federation/create_authority_federations.cypher")
with open(cypher_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Split into individual statements
statements = [s.strip() for s in content.split(';') if s.strip() and not s.strip().startswith('//')]

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'Chrystallum'))

with driver.session() as session:
    print("Importing federation structure...")
    
    for i, statement in enumerate(statements, 1):
        if statement:
            try:
                session.run(statement)
                if i % 5 == 0:
                    print(f"  Executed {i}/{len(statements)} statements...")
            except Exception as e:
                print(f"Error in statement {i}: {str(e)[:100]}")
    
    print(f"\n✅ Executed {len(statements)} statements")
    
    # Verify
    result = session.run("""
        MATCH (c:Chrystallum)-[:HAS_FEDERATION_CLUSTER]->(cat:Federation)-[:IS_COMPOSED_OF]->(fed)
        RETURN c.label as root, cat.label as category, count(fed) as federations
    """)
    
    record = result.single()
    print(f"\n✅ Created federation structure:")
    print(f"   Root: {record['root']}")
    print(f"   Category: {record['category']}")
    print(f"   Federations: {record['federations']}")
    
    # List federations
    result = session.run("""
        MATCH (fed:Federation:AuthoritySystem)
        RETURN fed.label, fed.role
        ORDER BY fed.id
    """)
    
    print(f"\n   Authority Systems:")
    for r in result:
        print(f"     - {r['fed.label']:50s} ({r['fed.role']})")

driver.close()

