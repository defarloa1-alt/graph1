"""
Decompose Boyd Principles into SPO Triples

Takes the 3 Boyd MilitaryPrinciple nodes (text statements)
and adds SPO triple structure for queryable knowledge.

Ontology:
- Concept: Abstract military ideas (tempo, decision cycle)
- Mechanism: How things work (iteration, disruption)
- Effect: Outcomes (advantage, confusion)
- Condition: Requirements (faster than opponent)
- Process: Action sequences (observe-orient-decide-act)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
load_dotenv()


def decompose_principles():
    """Add SPO structure to Boyd principles."""
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    print("\n" + "="*70)
    print("  DECOMPOSING BOYD PRINCIPLES INTO SPO TRIPLES")
    print("="*70)
    
    try:
        with driver.session() as session:
            
            # ============================================
            # 1. OODA Loop
            # ============================================
            
            print("\n[1] Decomposing: OODA Loop\n")
            
            session.run("""
                // Find the OODA Loop principle
                MATCH (mp:MilitaryPrinciple {label: 'OODA Loop'})
                
                // Define core concepts
                MERGE (c1:Concept {name: 'decision cycle', domain: 'military_theory'})
                MERGE (c2:Concept {name: 'operational tempo', domain: 'military_theory'})
                MERGE (mp)-[:DEFINES_CONCEPT]->(c1)
                MERGE (mp)-[:DEFINES_CONCEPT]->(c2)
                
                // Define the mechanism
                MERGE (m:Mechanism {
                    name: 'iterative decision cycle',
                    description: 'Four-phase loop of observe-orient-decide-act',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:IDENTIFIES_MECHANISM]->(m)
                
                // Define the process
                MERGE (p:Process {
                    name: 'OODA cycle',
                    phases: ['Observe', 'Orient', 'Decide', 'Act'],
                    domain: 'military_theory'
                })
                MERGE (mp)-[:INVOLVES_PROCESS]->(p)
                MERGE (m)-[:IMPLEMENTS]->(p)
                
                // Define effects
                MERGE (e1:Effect {
                    type: 'decision advantage',
                    description: 'Ability to decide and act before opponent',
                    domain: 'military_theory'
                })
                MERGE (e2:Effect {
                    type: 'cognitive disruption',
                    description: 'Adversary mental model becomes obsolete',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:PRODUCES_EFFECT]->(e1)
                MERGE (mp)-[:PRODUCES_EFFECT]->(e2)
                
                // Define conditions
                MERGE (cond:Condition {
                    requirement: 'faster cycle iteration',
                    description: 'Must complete OODA loop faster than adversary',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:REQUIRES_CONDITION]->(cond)
                MERGE (e1)-[:REQUIRES]->(cond)
                
                // Define targets
                MERGE (t:Target {
                    entity: 'adversary decision-making',
                    aspect: 'orientation and decision phases',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:TARGETS]->(t)
                MERGE (e2)-[:AFFECTS]->(t)
            """)
            
            print("    [OK] Concepts: decision cycle, operational tempo")
            print("    [OK] Mechanism: iterative decision cycle")
            print("    [OK] Process: OODA cycle (4 phases)")
            print("    [OK] Effects: decision advantage, cognitive disruption")
            print("    [OK] Condition: faster cycle iteration")
            print("    [OK] Target: adversary decision-making")
            
            # ============================================
            # 2. Operational Tempo Advantage
            # ============================================
            
            print("\n[2] Decomposing: Operational Tempo Advantage\n")
            
            session.run("""
                MATCH (mp:MilitaryPrinciple {label: 'Operational Tempo Advantage'})
                
                // Reuse tempo concept
                MATCH (c:Concept {name: 'operational tempo'})
                MERGE (mp)-[:DEFINES_CONCEPT]->(c)
                
                // Define rhythm concept
                MERGE (c2:Concept {name: 'operational rhythm', domain: 'military_theory'})
                MERGE (mp)-[:DEFINES_CONCEPT]->(c2)
                
                // Define mechanism
                MERGE (m:Mechanism {
                    name: 'speed differential',
                    description: 'Operating at faster rhythm creates perception gap',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:IDENTIFIES_MECHANISM]->(m)
                
                // Define effects
                MERGE (e1:Effect {
                    type: 'confusion',
                    description: 'Adversary unable to predict actions',
                    domain: 'military_theory'
                })
                MERGE (e2:Effect {
                    type: 'unpredictability',
                    description: 'Appear ambiguous to adversary',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:PRODUCES_EFFECT]->(e1)
                MERGE (mp)-[:PRODUCES_EFFECT]->(e2)
                
                // Define condition
                MERGE (cond:Condition {
                    requirement: 'faster rhythm than adversaries',
                    description: 'Maintain higher operational tempo',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:REQUIRES_CONDITION]->(cond)
                
                // Define target
                MERGE (t:Target {
                    entity: 'adversary perception',
                    aspect: 'pattern recognition',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:TARGETS]->(t)
                MERGE (e1)-[:AFFECTS]->(t)
            """)
            
            print("    [OK] Concepts: operational tempo, operational rhythm")
            print("    [OK] Mechanism: speed differential")
            print("    [OK] Effects: confusion, unpredictability")
            print("    [OK] Condition: faster rhythm than adversaries")
            print("    [OK] Target: adversary perception")
            
            # ============================================
            # 3. Inside the Loop Superiority
            # ============================================
            
            print("\n[3] Decomposing: Inside the Loop Superiority\n")
            
            session.run("""
                MATCH (mp:MilitaryPrinciple {label: 'Inside the Loop Superiority'})
                
                // Define concept
                MERGE (c:Concept {
                    name: 'decision cycle penetration',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:DEFINES_CONCEPT]->(c)
                
                WITH mp
                // Reuse decision cycle concept
                MATCH (dc:Concept {name: 'decision cycle'})
                MERGE (mp)-[:RELATES_TO]->(dc)
                
                // Define mechanism
                MERGE (m:Mechanism {
                    name: 'cycle disruption',
                    description: 'Operate inside adversary OODA loop to render phases ineffective',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:IDENTIFIES_MECHANISM]->(m)
                
                // Define cascading effects
                MERGE (e1:Effect {
                    type: 'observation obsolescence',
                    description: 'Adversary observations become outdated',
                    phase: 'Observe',
                    domain: 'military_theory'
                })
                MERGE (e2:Effect {
                    type: 'orientation irrelevance',
                    description: 'Adversary mental model misaligned with reality',
                    phase: 'Orient',
                    domain: 'military_theory'
                })
                MERGE (e3:Effect {
                    type: 'decision ineffectiveness',
                    description: 'Adversary decisions no longer applicable',
                    phase: 'Decide',
                    domain: 'military_theory'
                })
                MERGE (e4:Effect {
                    type: 'action impotence',
                    description: 'Adversary actions fail to achieve goals',
                    phase: 'Act',
                    domain: 'military_theory'
                })
                
                MERGE (mp)-[:PRODUCES_EFFECT]->(e1)
                MERGE (mp)-[:PRODUCES_EFFECT]->(e2)
                MERGE (mp)-[:PRODUCES_EFFECT]->(e3)
                MERGE (mp)-[:PRODUCES_EFFECT]->(e4)
                
                // Effects cascade
                MERGE (e1)-[:LEADS_TO]->(e2)
                MERGE (e2)-[:LEADS_TO]->(e3)
                MERGE (e3)-[:LEADS_TO]->(e4)
                
                // Define condition
                MERGE (cond:Condition {
                    requirement: 'operating inside adversary cycle',
                    description: 'Must complete your OODA faster than adversary completes theirs',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:REQUIRES_CONDITION]->(cond)
                
                // Define target
                MERGE (t:Target {
                    entity: 'adversary OODA loop',
                    aspect: 'all four phases',
                    domain: 'military_theory'
                })
                MERGE (mp)-[:TARGETS]->(t)
            """)
            
            print("    [OK] Concept: decision cycle penetration")
            print("    [OK] Mechanism: cycle disruption")
            print("    [OK] Effects (cascading): observation obsolescence ->")
            print("          orientation irrelevance -> decision ineffectiveness ->")
            print("          action impotence")
            print("    [OK] Condition: operating inside adversary cycle")
            print("    [OK] Target: adversary OODA loop (all phases)")
            
            # ============================================
            # Show Statistics
            # ============================================
            
            print("\n[4] SPO Structure Statistics:\n")
            
            result = session.run("""
                MATCH (n)
                WHERE n.domain = 'military_theory'
                  AND n:Concept OR n:Mechanism OR n:Effect OR n:Condition OR n:Process OR n:Target
                WITH labels(n)[0] as type, count(n) as count
                RETURN type, count
                ORDER BY count DESC
            """)
            
            for record in result:
                print(f"    {record['type']:<15} {record['count']} nodes")
            
            print("\n" + "="*70)
            print("  SPO DECOMPOSITION COMPLETE")
            print("  Boyd principles now queryable as knowledge graph!")
            print("="*70 + "\n")
            
    finally:
        driver.close()


if __name__ == "__main__":
    decompose_principles()
