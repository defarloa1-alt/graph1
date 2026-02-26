from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    print("Adding uniqueness constraints...\n")
    
    # Try entity_cipher_unique
    try:
        session.run("CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_cipher IS UNIQUE")
        print("SUCCESS: entity_cipher_unique constraint created")
    except Exception as e:
        print(f"FAILED entity_cipher_unique: {e}")
    
    # Try entity_qid_unique
    try:
        session.run("CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.qid IS UNIQUE")
        print("SUCCESS: entity_qid_unique constraint created")
    except Exception as e:
        print(f"FAILED entity_qid_unique: {e}")
    
    print("\nVerifying constraints...")
    result = session.run("SHOW CONSTRAINTS")
    
    found = []
    for rec in result:
        name = rec['name']
        if 'entity_cipher' in name or 'entity_qid' in name:
            found.append(name)
    
    print(f"\nEntity uniqueness constraints:")
    for c in found:
        print(f"  - {c}")
    
    if not found:
        print("  (None found - check errors above)")

driver.close()
