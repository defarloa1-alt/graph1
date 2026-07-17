"""
Populate MILITARY_THEORY with Boyd Principles

Uses Cursor Claude's analysis of Boyd's OODA Loop passage
to create MilitaryPrinciple nodes.

This demonstrates the discovery pipeline without needing API calls.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

load_dotenv()

from scripts.agents.military.agent_enhanced import MilitarySFAEnhanced


# Principles discovered by Claude (Cursor session) from Boyd passage
BOYD_PRINCIPLES = [
    {
        'label': 'OODA Loop',
        'statement': 'Decision advantage comes from cycling through Observe-Orient-Decide-Act faster than opponent, rendering their decisions obsolete',
        'category': 'decision_cycle',
        'applicability': 'universal',
        'confidence': 0.95
    },
    {
        'label': 'Operational Tempo Advantage',
        'statement': 'Operating at faster rhythm than adversaries generates confusion and makes you appear unpredictable',
        'category': 'tactical_principle',
        'applicability': 'universal',
        'confidence': 0.90
    },
    {
        'label': 'Inside the Loop Superiority',
        'statement': 'Getting inside adversary\'s decision cycle makes their observations obsolete, orientation irrelevant, decisions ineffective, and actions impotent',
        'category': 'command_doctrine',
        'applicability': 'universal',
        'confidence': 0.93
    }
]


def populate_principles():
    """Populate MILITARY_THEORY with Boyd principles."""
    
    print("\n" + "="*70)
    print("  POPULATING MILITARY_THEORY WITH BOYD PRINCIPLES")
    print("  (Discovered by Claude in Cursor session)")
    print("="*70)
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    try:
        military = MilitarySFAEnhanced(driver)
        
        print(f"\n[1] Creating {len(BOYD_PRINCIPLES)} principles from Boyd...")
        
        created_ids = []
        for idx, principle in enumerate(BOYD_PRINCIPLES, 1):
            print(f"\n    {idx}. {principle['label']}")
            
            # Create principle node
            principle_id = military._create_theory_principle(
                principle=principle,
                source_ref="Boyd, Patterns of Conflict (1976) - OODA Loop section",
                theorist="John Boyd"
            )
            
            print(f"       ID: {principle_id}")
            print(f"       Category: {principle['category']}")
            
            # Submit claim about this principle
            claim_id = military.submit_theory_claim(
                principle_id=principle_id,
                predicate='defines_principle',
                confidence=principle['confidence'],
                source_ref="Boyd, Patterns of Conflict (1976)"
            )
            
            print(f"       Claim: {claim_id}")
            
            created_ids.append(principle_id)
        
        # Verify in Neo4j
        print("\n[2] Verifying in Neo4j...")
        with driver.session() as session:
            result = session.run("""
                MATCH (mp:MilitaryPrinciple)
                WHERE mp.discovered_by = 'military_sfa_001_enhanced'
                  AND mp.theorist = 'John Boyd'
                RETURN 
                    mp.label as label,
                    mp.category as category,
                    mp.statement as statement
                ORDER BY mp.discovered_at ASC
            """)
            
            records = list(result)
            print(f"\n    Found {len(records)} Boyd principles:\n")
            
            for idx, record in enumerate(records, 1):
                print(f"    {idx}. {record['label']}")
                print(f"       Category: {record['category']}")
                print(f"       Statement: {record['statement'][:60]}...")
                print()
        
        # Now demonstrate linking to Roman history
        print("[3] Linking to Roman historical events...")
        
        # Link Battle of Cannae to OODA Loop
        with driver.session() as session:
            # Ensure Cannae exists
            session.run("""
                MERGE (e:EVENT {qid: 'Q36456'})
                SET e.label = 'Battle of Cannae',
                    e.date = '-216-08-02',
                    e.subject = 'roman_republic',
                    e.entity_cipher = 'ent_evt_Q36456'
            """)
        
        ooda_id = created_ids[0]  # First principle is OODA Loop
        
        link_claim = military.link_event_to_theory(
            event_qid='Q36456',
            principle_id=ooda_id,
            predicate='exemplifies_principle',
            confidence=0.89,
            analysis="Hannibal's cavalry creating dust clouds disrupted Roman observation and orientation phases, getting inside their OODA loop and causing decision paralysis at Cannae",
            source_ref='Polybius 3.116'
        )
        
        print(f"\n    [OK] Linked Battle of Cannae to OODA Loop")
        print(f"      Claim ID: {link_claim}")
        
        # Query the link
        print("\n[4] Querying cross-domain links...")
        with driver.session() as session:
            result = session.run("""
                MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                      -[claim:ASSERTS]->
                      (event:EVENT {qid: 'Q36456'})
                WHERE claim.predicate = 'exemplifies_principle'
                RETURN 
                    event.label as battle,
                    claim.principle_applied as theory,
                    claim.framework_analysis as analysis
            """)
            
            record = result.single()
            if record:
                print(f"\n    Battle: {record['battle']}")
                print(f"    Theory: {record['theory']}")
                print(f"    Analysis: {record['analysis'][:80]}...")
        
        print("\n" + "="*70)
        print("  SUCCESS - MILITARY_THEORY populated with Boyd principles!")
        print("  The SFA now has theory knowledge to apply to Roman history.")
        print("="*70 + "\n")
        
        # Don't cleanup - keep the data!
        print("[NOTE] Principles kept in graph for ongoing use\n")
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.close()


if __name__ == "__main__":
    populate_principles()
