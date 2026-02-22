from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    # Entity types
    print("ENTITY TYPE BREAKDOWN:")
    result = session.run('MATCH (n:Entity) RETURN n.entity_type as type, count(n) as count ORDER BY count DESC')
    for r in result:
        print(f"  {r['type']}: {r['count']}")
    
    # Federation scores
    print("\nFEDERATION SCORE DISTRIBUTION:")
    result = session.run('MATCH (n:Entity) RETURN n.federation_score as fed, count(n) as count ORDER BY fed DESC')
    for r in result:
        print(f"  Fed:{r['fed']}: {r['count']}")
    
    # High value entities
    print("\nHIGH FEDERATION SCORE (Fed >= 3):")
    result = session.run('MATCH (n:Entity) WHERE n.federation_score >= 3 RETURN n.qid, n.label, n.federation_score ORDER BY n.federation_score DESC LIMIT 10')
    for r in result:
        print(f"  {r['n.qid']} ({r['n.label']}) - Fed:{r['n.federation_score']}")

driver.close()
