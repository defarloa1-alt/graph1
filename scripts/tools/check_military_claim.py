"""Check what happened with the military claim"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
)

with driver.session() as session:
    # Check all entities with cipher containing Q1048
    print("All entities related to Q1048:")
    result = session.run("""
        MATCH (e)
        WHERE e.entity_cipher CONTAINS 'Q1048' OR e.qid = 'Q1048'
        RETURN e.entity_cipher, e.qid, labels(e) as labels
    """)
    
    for record in result:
        print(f'  Cipher: {record["e.entity_cipher"]}')
        print(f'  QID: {record["e.qid"]}')
        print(f'  Labels: {record["labels"]}')
        print()
    
    # Check ALL claims from military_sfa_001
    print("All claims from military_sfa_001:")
    result = session.run("""
        MATCH (a:Agent {agent_id: 'military_sfa_001'})
              -[c:ASSERTS]->
              (e)
        RETURN 
            e.entity_cipher as entity_cipher,
            e.qid as qid,
            c.predicate as predicate,
            c.facet as facet,
            c.status as status
    """)
    
    for record in result:
        print(f'  Entity: {record["entity_cipher"]} (QID: {record["qid"]})')
        print(f'  Predicate: {record["predicate"]}')
        print(f'  Facet: {record["facet"]}')
        print(f'  Status: {record["status"]}')
        print()

driver.close()
