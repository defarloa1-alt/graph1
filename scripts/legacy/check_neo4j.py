from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    # Count entities
    result = session.run('MATCH (n:Entity) RETURN count(n) as total')
    total = result.single()['total']
    print(f"Total Entity nodes: {total}\n")
    
    # Sample entities
    result = session.run('''
        MATCH (n:Entity) 
        RETURN n.qid as qid, n.label as label, n.entity_cipher as cipher, 
               n.entity_type as type, n.federation_score as fed
        ORDER BY n.entity_id
        LIMIT 10
    ''')
    
    print("First 10 entities:")
    for r in result:
        print(f"  {r['qid']} ({r['label']}) - {r['type']} - Fed:{r['fed']} - {r['cipher']}")
    
    # Check indexes
    print(f"\nIndexes:")
    result = session.run('SHOW INDEXES')
    for r in result:
        if 'entity' in r.get('name', '').lower():
            print(f"  {r.get('name', 'N/A')} on {r.get('labelsOrTypes', 'N/A')}")

driver.close()
