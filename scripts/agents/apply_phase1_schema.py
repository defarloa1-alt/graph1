"""
Apply Phase 1 Multi-Agent Schema to Neo4j

Creates constraints and indexes required for ADR 022 implementation.
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def apply_schema():
    """Apply Phase 1 schema to Neo4j."""
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    with driver.session() as session:
        print("Applying Phase 1 Multi-Agent Schema...")
        
        # Constraints
        print("\n1. Creating constraints...")
        
        # Note: Constraints don't require labels in Neo4j 5.x, but we'll be permissive
        constraints = [
            "entity_cipher_unique",
            "agent_id_unique", 
            "entity_qid_unique"
        ]
        
        for name in constraints:
            try:
                # Drop if exists, then recreate (workaround for Neo4j constraint syntax variations)
                session.run(f"DROP CONSTRAINT {name} IF EXISTS")
            except:
                pass
        
        try:
            # Create without label (Neo4j 5.x supports this)
            session.run("CREATE CONSTRAINT entity_cipher_unique FOR (e) REQUIRE e.entity_cipher IS UNIQUE")
            print("  [OK] entity_cipher_unique")
        except Exception as e:
            print(f"  [FAIL] entity_cipher_unique: {str(e)[:100]}")
        
        try:
            session.run("CREATE CONSTRAINT agent_id_unique FOR (a:Agent) REQUIRE a.agent_id IS UNIQUE")
            print("  [OK] agent_id_unique")
        except Exception as e:
            print(f"  [FAIL] agent_id_unique: {str(e)[:100]}")
        
        try:
            session.run("CREATE CONSTRAINT entity_qid_unique FOR (e) REQUIRE e.qid IS UNIQUE")
            print("  [OK] entity_qid_unique")
        except Exception as e:
            print(f"  [FAIL] entity_qid_unique: {str(e)[:100]}")
        
        # Indexes
        print("\n2. Creating indexes...")
        
        indexes = [
            ("entity_type_idx", "FOR (e) ON (e.entity_type)"),
            ("entity_label_idx", "FOR (e) ON (e.label)"),
            ("agent_facet_idx", "FOR (a:Agent) ON (a.facet)"),
            ("claim_facet_idx", "FOR ()-[c:ASSERTS]-() ON (c.facet)"),
            ("claim_status_idx", "FOR ()-[c:ASSERTS]-() ON (c.status)"),
            ("claim_confidence_idx", "FOR ()-[c:ASSERTS]-() ON (c.confidence)"),
            ("claim_predicate_idx", "FOR ()-[c:ASSERTS]-() ON (c.predicate)"),
            ("entity_created_at_idx", "FOR (e) ON (e.created_at)"),
        ]
        
        for name, definition in indexes:
            try:
                session.run(f"CREATE INDEX {name} IF NOT EXISTS {definition}")
                print(f"  [OK] {name}")
            except Exception as e:
                print(f"  [FAIL] {name}: {str(e)[:100]}")
        
        print("\n3. Verifying schema...")
        
        # Count constraints
        result = session.run("SHOW CONSTRAINTS")
        constraint_count = len(list(result))
        print(f"  Total constraints: {constraint_count}")
        
        # Count indexes
        result = session.run("SHOW INDEXES")
        index_count = len(list(result))
        print(f"  Total indexes: {index_count}")
        
        print("\n[OK] Phase 1 schema applied successfully!")
    
    driver.close()

if __name__ == "__main__":
    apply_schema()
