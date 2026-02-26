from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

with driver.session() as session:
    print("Replacing indexes with uniqueness constraints...\n")
    
    # Step 1: Drop existing indexes
    print("Step 1: Dropping existing indexes...")
    
    try:
        session.run("DROP INDEX entity_cipher_idx IF EXISTS")
        print("  Dropped: entity_cipher_idx")
    except Exception as e:
        print(f"  Skip: {e}")
    
    try:
        session.run("DROP INDEX entity_qid_idx IF EXISTS")
        print("  Dropped: entity_qid_idx")
    except Exception as e:
        print(f"  Skip: {e}")
    
    print()
    
    # Step 2: Create uniqueness constraints (include indexing)
    print("Step 2: Creating uniqueness constraints...")
    
    try:
        session.run("CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_cipher IS UNIQUE")
        print("  SUCCESS: entity_cipher_unique (with index)")
    except Exception as e:
        print(f"  FAILED: {e}")
    
    try:
        session.run("CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.qid IS UNIQUE")
        print("  SUCCESS: entity_qid_unique (with index)")
    except Exception as e:
        print(f"  FAILED: {e}")
    
    print()
    
    # Step 3: Verify
    print("Step 3: Verification...")
    
    result = session.run("""
        SHOW CONSTRAINTS
        YIELD name, type, entityType, labelsOrTypes, properties
        WHERE 'entity_cipher' IN properties OR 'qid' IN properties
        RETURN name, type, properties
    """)
    
    constraints = list(result)
    
    if constraints:
        print(f"  Found {len(constraints)} Entity uniqueness constraints:")
        for c in constraints:
            print(f"    - {c['name']}: {c['properties']}")
    else:
        print("  WARNING: No constraints found!")

driver.close()
print("\nDone!")
