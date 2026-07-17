"""Debug entity cipher mismatch"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'),
    auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
)

with driver.session() as session:
    # Check all entities with QID Q1048
    result = session.run("""
        MATCH (e)
        WHERE e.qid = 'Q1048'
        RETURN e.entity_cipher, e.qid, labels(e) as labels
    """)
    
    print('Entities with QID Q1048:')
    for record in result:
        print(f'  Cipher: {record["e.entity_cipher"]}')
        print(f'  Labels: {record["labels"]}')
    print()
    
    # Check Phase 2 claim
    result = session.run("""
        MATCH (a:Agent {agent_id: 'military_sfa_001'})
              -[c:ASSERTS]->
              (e)
        WHERE c.predicate = 'commanded_gallic_wars'
        RETURN e.entity_cipher, e.qid, c.facet
    """)
    
    record = result.single()
    if record:
        print('Phase 2 claim found:')
        print(f'  Target entity: {record["e.entity_cipher"]}')
        print(f'  Target QID: {record["e.qid"]}')
        print(f'  Facet: {record["c.facet"]}')
    else:
        print('Phase 2 claim NOT found')

driver.close()
