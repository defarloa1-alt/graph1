"""
Show all SubjectConcept domains in the graph
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def show_subject_concepts():
    """Show all SubjectConcept nodes."""
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    print("\n" + "="*70)
    print("  SUBJECT CONCEPTS IN GRAPH")
    print("="*70)
    
    try:
        with driver.session() as session:
            # Query all SubjectConcept nodes
            result = session.run("""
                MATCH (sc:SubjectConcept)
                RETURN 
                    sc.subject_id as subject_id,
                    sc.label as label,
                    sc.scope as scope,
                    sc.period as period,
                    sc.description as description,
                    sc.discovery_based as discovery_based
                ORDER BY sc.subject_id
            """)
            
            records = list(result)
            
            if records:
                print(f"\nFound {len(records)} SubjectConcept domain(s):\n")
                
                for idx, record in enumerate(records, 1):
                    print(f"{idx}. {record['label']}")
                    print(f"   ID: {record['subject_id']}")
                    print(f"   Scope: {record['scope']}")
                    print(f"   Period: {record['period']}")
                    if record.get('discovery_based'):
                        print(f"   Discovery-based: {record['discovery_based']}")
                    if record.get('description'):
                        print(f"   Description: {record['description']}")
                    print()
            else:
                print("\n[!] No SubjectConcept nodes found!")
                print("    Creating MILITARY_THEORY now...\n")
                
                # Create it if missing
                session.run("""
                    MERGE (sc:SubjectConcept {subject_id: 'military_theory'})
                    SET sc.label = 'Military Theory',
                        sc.description = 'Universal principles of military strategy, tactics, and command',
                        sc.scope = 'theoretical',
                        sc.period = 'timeless',
                        sc.discovery_based = true,
                        sc.created_at = datetime()
                """)
                
                print("[OK] MILITARY_THEORY SubjectConcept created")
            
            # Show what entities belong to each
            print("\n" + "="*70)
            print("  ENTITIES BY SUBJECT")
            print("="*70 + "\n")
            
            for record in records:
                subject_id = record['subject_id']
                
                # Count entities for this subject
                count_result = session.run("""
                    MATCH (n)
                    WHERE n.subject = $subject_id
                    RETURN count(n) as count
                """, subject_id=subject_id)
                
                count = count_result.single()['count']
                
                print(f"{record['label']}:")
                print(f"  Entities with subject='{subject_id}': {count}")
                
                # Sample entities
                if count > 0:
                    sample = session.run("""
                        MATCH (n)
                        WHERE n.subject = $subject_id
                        RETURN labels(n) as labels, n.label as name
                        LIMIT 3
                    """, subject_id=subject_id)
                    
                    for s in sample:
                        label_str = ':'.join(s['labels'])
                        print(f"    - {label_str}: {s['name']}")
                
                print()
            
            # Special check for MilitaryPrinciple nodes
            print("\nMilitaryPrinciple nodes (MILITARY_THEORY):")
            mp_result = session.run("""
                MATCH (mp:MilitaryPrinciple)
                RETURN count(mp) as count
            """)
            mp_count = mp_result.single()['count']
            print(f"  Count: {mp_count}")
            
            if mp_count > 0:
                sample = session.run("""
                    MATCH (mp:MilitaryPrinciple)
                    RETURN mp.label as name
                    LIMIT 3
                """)
                for s in sample:
                    print(f"    - {s['name']}")
            
            print("\n" + "="*70 + "\n")
            
    finally:
        driver.close()


if __name__ == "__main__":
    show_subject_concepts()
