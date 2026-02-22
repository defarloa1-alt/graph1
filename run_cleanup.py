from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    print("CLEANUP: Removing duplicates...\n")
    
    # Part 2: Remove duplicates
    result = session.run("""
        MATCH (n:Entity)
        WITH n.qid as qid, collect(n) as nodes
        WHERE size(nodes) > 1
        WITH qid, nodes, min([n in nodes | n.imported_at]) as keep_time
        UNWIND nodes as node
        WITH node, keep_time
        WHERE node.imported_at > keep_time
        DETACH DELETE node
        RETURN count(node) as deleted
    """)
    
    deleted = result.single()['deleted']
    print(f"  Deleted: {deleted} duplicate entities\n")
    
    # Part 3: Verification
    print("VERIFICATION:\n")
    
    result = session.run("""
        MATCH (n:Entity)
        RETURN count(n) as total_entities,
               count(DISTINCT n.qid) as unique_qids,
               count(DISTINCT n.entity_cipher) as unique_ciphers
    """)
    
    rec = result.single()
    print(f"  Total entities: {rec['total_entities']}")
    print(f"  Unique QIDs: {rec['unique_qids']}")
    print(f"  Unique ciphers: {rec['unique_ciphers']}")
    
    result = session.run("""
        MATCH (n:Entity)
        WITH n.qid as qid, count(n) as node_count
        WHERE node_count > 1
        RETURN count(qid) as remaining_duplicates
    """)
    
    remaining = result.single()['remaining_duplicates']
    print(f"  Remaining duplicates: {remaining}\n")
    
    # Part 4: Add constraints
    print("ADDING CONSTRAINTS:\n")
    
    try:
        session.run("CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS FOR (n:Entity) REQUIRE n.qid IS UNIQUE")
        print("  ✓ entity_qid_unique constraint created")
    except Exception as e:
        print(f"  ⚠ entity_qid_unique: {e}")
    
    try:
        session.run("CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS FOR (n:Entity) REQUIRE n.entity_cipher IS UNIQUE")
        print("  ✓ entity_cipher_unique constraint created")
    except Exception as e:
        print(f"  ⚠ entity_cipher_unique: {e}")
    
    print("\nCLEANUP COMPLETE!\n")

driver.close()
