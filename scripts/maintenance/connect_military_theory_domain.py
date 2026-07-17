"""
Connect MILITARY_THEORY SubjectConcept to All Theory Nodes

Creates explicit :CONTAINS relationships from the SubjectConcept node
to all MilitaryPrinciples, Concepts, Mechanisms, Effects, etc.

This makes MILITARY_THEORY visible as a hub in graph visualizations.
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def connect_domain():
    """Create :CONTAINS relationships."""
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    print("\n" + "="*70)
    print("  CONNECTING MILITARY_THEORY DOMAIN")
    print("="*70)
    
    try:
        with driver.session() as session:
            # Connect to MilitaryPrinciples
            print("\n[1] Connecting to MilitaryPrinciple nodes...")
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: 'military_theory'})
                MATCH (mp:MilitaryPrinciple)
                WHERE mp.subject = 'military_theory'
                MERGE (sc)-[:CONTAINS]->(mp)
                RETURN count(mp) as count
            """)
            count = result.single()['count']
            print(f"    [OK] Connected {count} MilitaryPrinciple nodes")
            
            # Connect to Concepts
            print("\n[2] Connecting to Concept nodes...")
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: 'military_theory'})
                MATCH (c:Concept)
                WHERE c.domain = 'military_theory'
                MERGE (sc)-[:CONTAINS]->(c)
                RETURN count(c) as count
            """)
            count = result.single()['count']
            print(f"    [OK] Connected {count} Concept nodes")
            
            # Connect to Mechanisms
            print("\n[3] Connecting to Mechanism nodes...")
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: 'military_theory'})
                MATCH (m:Mechanism)
                WHERE m.domain = 'military_theory'
                MERGE (sc)-[:CONTAINS]->(m)
                RETURN count(m) as count
            """)
            count = result.single()['count']
            print(f"    [OK] Connected {count} Mechanism nodes")
            
            # Connect to Effects
            print("\n[4] Connecting to Effect nodes...")
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: 'military_theory'})
                MATCH (e:Effect)
                WHERE e.domain = 'military_theory'
                MERGE (sc)-[:CONTAINS]->(e)
                RETURN count(e) as count
            """)
            count = result.single()['count']
            print(f"    [OK] Connected {count} Effect nodes")
            
            # Connect to Conditions
            print("\n[5] Connecting to Condition nodes...")
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: 'military_theory'})
                MATCH (c:Condition)
                WHERE c.domain = 'military_theory'
                MERGE (sc)-[:CONTAINS]->(c)
                RETURN count(c) as count
            """)
            count = result.single()['count']
            print(f"    [OK] Connected {count} Condition nodes")
            
            # Connect to Processes
            print("\n[6] Connecting to Process nodes...")
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: 'military_theory'})
                MATCH (p:Process)
                WHERE p.domain = 'military_theory'
                MERGE (sc)-[:CONTAINS]->(p)
                RETURN count(p) as count
            """)
            count = result.single()['count']
            print(f"    [OK] Connected {count} Process nodes")
            
            # Connect to Targets
            print("\n[7] Connecting to Target nodes...")
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: 'military_theory'})
                MATCH (t:Target)
                WHERE t.domain = 'military_theory'
                MERGE (sc)-[:CONTAINS]->(t)
                RETURN count(t) as count
            """)
            count = result.single()['count']
            print(f"    [OK] Connected {count} Target nodes")
            
            # Show total
            print("\n[8] Total connections:")
            result = session.run("""
                MATCH (sc:SubjectConcept {subject_id: 'military_theory'})
                      -[:CONTAINS]->
                      (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY count DESC
            """)
            
            total = 0
            for record in result:
                count = record['count']
                total += count
                print(f"    {record['type']:<20} {count} nodes")
            
            print(f"\n    {'TOTAL':<20} {total} nodes")
            
            print("\n" + "="*70)
            print("  MILITARY_THEORY now visible as domain hub!")
            print("="*70 + "\n")
            
    finally:
        driver.close()


if __name__ == "__main__":
    connect_domain()
