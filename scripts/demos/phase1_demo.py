"""
Phase 1 Demonstration: Canonical Entity + Facet-Scoped Claims

This demo shows how the Claim Registry prevents entity fragmentation
by deduplicating entities while preserving multiple facet perspectives.

Scenario: Caesar crossing the Rubicon (49 BCE)
- 3 SFAs (Military, Biographic, Political) each submit claims
- Result: 1 canonical entity, 3 facet-specific interpretations
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from scripts.agents.claim_registry import create_claim_registry

load_dotenv()

def main():
    print("=" * 70)
    print("Phase 1 Demo: Multi-Agent Canonical Entity Claims")
    print("=" * 70)
    
    # Create registry
    registry = create_claim_registry(
        neo4j_uri=os.getenv('NEO4J_URI'),
        neo4j_user=os.getenv('NEO4J_USERNAME'),
        neo4j_password=os.getenv('NEO4J_PASSWORD')
    )
    
    print("\n[SCENARIO] Caesar crossing the Rubicon (49 BCE)")
    print("   3 SFAs analyze the same event from different perspectives\n")
    
    # Define the event (same for all)
    caesar_rubicon = {
        'type': 'EVENT',
        'qid': 'Q40979',
        'label': 'Caesar crossing the Rubicon',
        'canonical_properties': {
            'name': 'Crossing of the Rubicon',
            'date': '-49',
            'location': 'Rubicon River',
            'participants': 'Julius Caesar'
        }
    }
    
    # Military SFA perspective
    print("[MILITARY SFA] analyzing...")
    claim_1 = registry.submit_claim(
        entity=caesar_rubicon,
        predicate='military_escalation',
        facet='MILITARY',
        agent_id='military_sfa_001',
        confidence=0.92,
        source_qid='Q103082',  # Plutarch's Life of Caesar
        passage_locator='Plutarch, Caesar 32.8',
        igar_chain={
            'input': 'Legion stationed in Gaul, Senate recall order',
            'goal': 'Maintain military command and protect veterans',
            'action': 'Cross Rubicon with armed legion (alea iacta est)',
            'result': 'Declaration of war against Senate'
        }
    )
    print(f"   [OK] Submitted claim: {claim_1}")
    print(f"   [DATA] Interpretation: 'military_escalation' (confidence: 0.92)")
    
    # Biographic SFA perspective
    print("\n[BIOGRAPHIC SFA] analyzing...")
    claim_2 = registry.submit_claim(
        entity=caesar_rubicon,  # SAME entity!
        predicate='career_defining_act',
        facet='BIOGRAPHIC',
        agent_id='bio_sfa_001',
        confidence=0.95,
        source_qid='Q185118',  # Suetonius' Lives of the Caesars
        passage_locator='Suetonius, Julius 31-32',
        igar_chain={
            'input': 'Senate refuses negotiation, threatens prosecution',
            'goal': 'Preserve personal dignitas and political career',
            'action': 'Cross Rubicon, commit to civil war',
            'result': 'Point of no return in political trajectory'
        }
    )
    print(f"   [OK] Submitted claim: {claim_2}")
    print(f"   [DATA] Interpretation: 'career_defining_act' (confidence: 0.95)")
    
    # Political SFA perspective
    print("\n[POLITICAL SFA] analyzing...")
    claim_3 = registry.submit_claim(
        entity=caesar_rubicon,  # SAME entity!
        predicate='constitutional_crisis',
        facet='POLITICAL',
        agent_id='political_sfa_001',
        confidence=0.88,
        source_qid='Q1403',  # Appian's Civil Wars
        passage_locator='Appian, Civil Wars 2.35',
        igar_chain={
            'input': 'Senate ultimatum, Optimates block compromise',
            'goal': 'Break political deadlock, challenge Optimate control',
            'action': 'Violate sacred boundary with armed force',
            'result': 'Breakdown of Republican constitutional norms'
        }
    )
    print(f"   [OK] Submitted claim: {claim_3}")
    print(f"   [DATA] Interpretation: 'constitutional_crisis' (confidence: 0.88)")
    
    # Verify deduplication
    print("\n" + "-" * 70)
    print("[RESULTS]")
    print("-" * 70)
    
    # Check entity count
    with registry.driver.session() as session:
        result = session.run("""
            MATCH (e {qid: 'Q40979'})
            RETURN count(e) as entity_count
        """)
        entity_count = result.single()['entity_count']
        print(f"   Canonical Entities Created: {entity_count}")
        assert entity_count == 1, "[FAIL] Deduplication failed!"
        print("   [OK] Deduplication successful: 1 canonical entity")
    
    # Check claim count
    with registry.driver.session() as session:
        result = session.run("""
            MATCH (e {qid: 'Q40979'})<-[c:ASSERTS]-()
            RETURN count(c) as claim_count
        """)
        claim_count = result.single()['claim_count']
        print(f"   Facet-Specific Claims: {claim_count}")
        assert claim_count == 3, "[FAIL] Claims not created!"
        print("   [OK] All 3 perspectives preserved")
    
    # Retrieve all claims
    print("\n[CROSS-FACET ANALYSIS]")
    print("-" * 70)
    claims = registry.get_claims_for_entity('ent_evt_Q40979')
    
    for claim in claims:
        print(f"\n   {claim['facet']} Perspective:")
        print(f"      Predicate: {claim['predicate']}")
        print(f"      Agent: {claim['agent_id']}")
        print(f"      Confidence: {claim['confidence']}")
        print(f"      Status: {claim['status']}")
        if claim.get('source_qid'):
            print(f"      Source: {claim['source_qid']}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] Phase 1 Demo Complete!")
    print("=" * 70)
    print("\n[KEY ACHIEVEMENTS]")
    print("   * Entity fragmentation PREVENTED (1 entity, not 3)")
    print("   * Semantic richness PRESERVED (3 distinct interpretations)")
    print("   * Full provenance MAINTAINED (agent, source, IGAR chain)")
    print("   * Status lifecycle READY (all claims start at TBD)")
    print("\n[NEXT] Ready for Phase 2: Peer Review and Conflict Detection\n")
    
    registry.driver.close()


if __name__ == "__main__":
    main()
