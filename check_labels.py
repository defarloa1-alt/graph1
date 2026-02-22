from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    # Find entities with "Rome" in label
    print("Entities with 'Rome' in label:")
    result = session.run("""
        MATCH (n:Entity)
        WHERE n.label CONTAINS 'Rome' OR n.label CONTAINS 'rome'
        RETURN n.qid as qid, n.label as label, n.entity_type as type
        LIMIT 20
    """)
    
    count = 0
    for r in result:
        print(f"  {r['qid']} - {r['label']} ({r['type']})")
        count += 1
    
    if count == 0:
        print("  (None found)")
    
    # Find Q17167 specifically
    print("\nSearching for Q17167 (Roman Republic):")
    result = session.run("MATCH (n:Entity {qid: 'Q17167'}) RETURN n")
    rec = result.single()
    if rec:
        node = rec['n']
        print(f"  FOUND: {node.get('label')}")
        print(f"  Cipher: {node.get('entity_cipher')}")
        print(f"  Type: {node.get('entity_type')}")
    else:
        print("  NOT FOUND")
    
    # Show all labels (first 20)
    print("\nAll entity labels (first 20):")
    result = session.run("MATCH (n:Entity) RETURN n.qid, n.label ORDER BY n.label LIMIT 20")
    for r in result:
        print(f"  {r['n.qid']} - {r['n.label']}")

driver.close()
