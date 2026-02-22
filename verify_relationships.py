from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    # Total relationships
    result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
    total_rels = result.single()['total']
    
    # Entity relationships
    result = session.run("MATCH (:Entity)-[r]->(:Entity) RETURN count(r) as entity_rels")
    entity_rels = result.single()['entity_rels']
    
    print(f"RELATIONSHIP VERIFICATION:\n")
    print(f"  Total relationships: {total_rels}")
    print(f"  Entity-to-Entity: {entity_rels}")
    print()
    
    # Relationship types
    result = session.run("""
        MATCH (:Entity)-[r]->(:Entity)
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    
    print(f"Relationship types:")
    for r in result:
        print(f"  {r['rel_type']}: {r['count']}")
    print()
    
    # Connectivity
    result = session.run("""
        MATCH (n:Entity)
        OPTIONAL MATCH (n)-[r]-()
        WITH n, count(r) as rel_count
        RETURN 
          count(CASE WHEN rel_count > 0 THEN 1 END) as connected,
          count(CASE WHEN rel_count = 0 THEN 1 END) as isolated,
          count(n) as total
    """)
    
    rec = result.single()
    connected_pct = rec['connected'] / rec['total'] * 100
    
    print(f"Connectivity:")
    print(f"  Connected entities: {rec['connected']} ({connected_pct:.1f}%)")
    print(f"  Isolated entities: {rec['isolated']}")
    print()
    
    # Sample relationships
    result = session.run("""
        MATCH (from:Entity)-[r]->(to:Entity)
        RETURN from.qid, from.label, type(r), to.qid, to.label
        LIMIT 10
    """)
    
    print(f"Sample relationships:")
    for r in result:
        print(f"  {r['from.qid']} ({r['from.label'][:30]}) --{r['type(r)']}-> {r['to.qid']} ({r['to.label'][:30]})")

driver.close()
