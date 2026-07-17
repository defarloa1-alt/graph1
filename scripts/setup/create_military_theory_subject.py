"""
Create MILITARY_THEORY SubjectConcept

This is a peer SubjectConcept to ROMAN_REPUBLIC.
The Military SFA will populate it by discovering theories from sources.

Empty at creation - the SFA discovers and adds principles through training.
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def create_military_theory_subject():
    """Create empty MILITARY_THEORY SubjectConcept."""
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    try:
        with driver.session() as session:
            # Create the SubjectConcept node
            result = session.run("""
                MERGE (sc:SubjectConcept {subject_id: 'military_theory'})
                SET sc.label = 'Military Theory',
                    sc.description = 'Universal principles of military strategy, tactics, and command discovered from theoretical literature',
                    sc.scope = 'theoretical',
                    sc.period = 'timeless',
                    sc.discovery_based = true,
                    sc.created_at = datetime()
                RETURN sc
            """)
            
            record = result.single()
            if record:
                print("[OK] Created SubjectConcept: MILITARY_THEORY")
                print("     Scope: theoretical")
                print("     Period: timeless")
                print("     Discovery-based: true")
                print("\n     The Military SFA will populate this domain by discovering")
                print("     principles from Boyd, Clausewitz, Liddell Hart, etc.")
            else:
                print("[INFO] MILITARY_THEORY SubjectConcept already exists")
        
        # Create indexes for MilitaryPrinciple nodes
        with driver.session() as session:
            session.run("""
                CREATE INDEX military_principle_id IF NOT EXISTS
                FOR (mp:MilitaryPrinciple)
                ON (mp.principle_id)
            """)
            print("\n[OK] Created index on MilitaryPrinciple.principle_id")
            
            session.run("""
                CREATE INDEX military_principle_category IF NOT EXISTS
                FOR (mp:MilitaryPrinciple)
                ON (mp.category)
            """)
            print("[OK] Created index on MilitaryPrinciple.category")
        
        print("\n[SUCCESS] MILITARY_THEORY domain ready for SFA discovery")
        
    except Exception as e:
        print(f"[FAIL] Error creating MILITARY_THEORY: {e}")
        raise
    finally:
        driver.close()


if __name__ == "__main__":
    create_military_theory_subject()
