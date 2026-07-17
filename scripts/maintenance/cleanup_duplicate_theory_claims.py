"""
Clean up duplicate theory claims

Removes duplicate :ASSERTS relationships to MilitaryPrinciple nodes,
keeping only the most recent one for each principle.
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def cleanup_duplicates():
    """Remove duplicate theory claims."""
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    print("\n" + "="*70)
    print("  CLEANING UP DUPLICATE THEORY CLAIMS")
    print("="*70)
    
    try:
        with driver.session() as session:
            # First, show current state
            print("\n[1] Current state:\n")
            result = session.run("""
                MATCH (a:Agent)-[c:ASSERTS]->(mp:MilitaryPrinciple)
                WHERE mp.subject = 'military_theory'
                RETURN 
                    mp.label as principle,
                    count(c) as claim_count
                ORDER BY principle
            """)
            
            for record in result:
                print(f"    {record['principle']}: {record['claim_count']} claims")
            
            # Find and remove duplicates, keeping most recent
            print("\n[2] Removing duplicates (keeping most recent)...\n")
            
            result = session.run("""
                MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                      -[c:ASSERTS]->
                      (mp:MilitaryPrinciple)
                WHERE mp.subject = 'military_theory'
                  AND c.target_subject = 'military_theory'
                WITH mp, c
                ORDER BY c.submitted_at DESC
                WITH mp, collect(c) as claims
                WHERE size(claims) > 1
                UNWIND claims[1..] as duplicate
                DELETE duplicate
                RETURN count(duplicate) as deleted_count
            """)
            
            record = result.single()
            deleted = record['deleted_count'] if record else 0
            
            print(f"    Deleted {deleted} duplicate claims")
            
            # Show final state
            print("\n[3] Final state:\n")
            result = session.run("""
                MATCH (a:Agent)-[c:ASSERTS]->(mp:MilitaryPrinciple)
                WHERE mp.subject = 'military_theory'
                RETURN 
                    mp.label as principle,
                    count(c) as claim_count
                ORDER BY principle
            """)
            
            for record in result:
                print(f"    {record['principle']}: {record['claim_count']} claims")
            
            print("\n" + "="*70)
            print("  CLEANUP COMPLETE")
            print("="*70 + "\n")
            
    finally:
        driver.close()


if __name__ == "__main__":
    cleanup_duplicates()
