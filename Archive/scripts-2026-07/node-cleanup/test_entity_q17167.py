from neo4j import GraphDatabase
import os
import json
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
)

session = driver.session()

# Check entity
result = session.run('MATCH (n {qid: "Q17167"}) RETURN n LIMIT 1')
record = result.single()

if record:
    entity = record['n']
    print("Entity found!")
    print(f"Label: {entity.get('label')}")
    print(f"Entity Type: {entity.get('entity_type')}")
    print(f"Entity Cipher: {entity.get('entity_cipher')}")
    print(f"Properties Count: {entity.get('properties_count')}")
    print(f"\nAll properties:")
    for key, value in entity.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"  {key}: {value[:100]}...")
        else:
            print(f"  {key}: {value}")
    
    # Check relationships
    print("\n\nChecking relationships...")
    rel_result = session.run(
        'MATCH (n {qid: "Q17167"})-[r]-(m) RETURN type(r) as relType, m.label as targetLabel LIMIT 10'
    )
    rels = list(rel_result)
    print(f"Found {len(rels)} relationships")
    for rel in rels:
        print(f"  {rel['relType']} -> {rel['targetLabel']}")
else:
    print("Entity NOT found!")

session.close()
driver.close()
