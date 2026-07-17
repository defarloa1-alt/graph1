"""
Phase 2 Demo - Peer Review and Cross-Facet Consensus

Demonstrates:
1. Multiple SFAs submit claims about the same entity
2. Peer review workflow - SFAs validate each other's claims
3. Agreement scoring and consensus building
4. Automatic status promotion (TBD -> PROPOSED -> CONFIRMED/CONTESTED)
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.agents.claim_registry import create_claim_registry
from scripts.agents.peer_reviewer import create_peer_reviewer

load_dotenv()


def print_section(title):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def phase2_demo():
    """Demonstrate Phase 2: Peer Review and Consensus Building."""
    
    print_section("Phase 2: Peer Review & Cross-Facet Consensus")
    print("This demo shows how multiple SFAs review each other's claims")
    print("and build consensus through agreement scoring.\n")
    
    # Initialize services
    registry = create_claim_registry(
        os.getenv('NEO4J_URI'),
        os.getenv('NEO4J_USERNAME'),
        os.getenv('NEO4J_PASSWORD')
    )
    
    reviewer = create_peer_reviewer(
        os.getenv('NEO4J_URI'),
        os.getenv('NEO4J_USERNAME'),
        os.getenv('NEO4J_PASSWORD')
    )
    
    # Cleanup test data
    print("[SETUP] Cleaning up any existing test data...")
    registry.driver.execute_query("""
        MATCH (e {qid: 'Q1048_DEMO_P2'})
        DETACH DELETE e
    """)
    registry.driver.execute_query("""
        MATCH (a:Agent)
        WHERE a.agent_id STARTS WITH 'demo_p2_'
        DETACH DELETE a
    """)
    print("[OK] Cleanup complete\n")
    
    # ==========================================
    # STEP 1: Multiple SFAs submit claims
    # ==========================================
    print_section("Step 1: Multiple SFAs Submit Claims")
    
    entity = {
        'type': 'PERSON',
        'qid': 'Q1048_DEMO_P2',
        'label': 'Julius Caesar',
        'description': 'Roman military and political leader'
    }
    
    # Military SFA submits high-confidence claim
    print("[MILITARY SFA] Submitting claim: Caesar crossed Rubicon in -49")
    registry.submit_claim(
        entity=entity,
        predicate='crossed_rubicon',
        facet='MILITARY',
        agent_id='demo_p2_military_sfa',
        confidence=0.95
    )
    print("  -> Status: TBD (awaiting peer review)")
    
    # Political SFA submits medium-confidence claim
    print("\n[POLITICAL SFA] Submitting claim: Caesar declared dictator")
    registry.submit_claim(
        entity=entity,
        predicate='became_dictator',
        facet='POLITICAL',
        agent_id='demo_p2_political_sfa',
        confidence=0.75
    )
    print("  -> Status: TBD (awaiting peer review)")
    
    # Economic SFA submits low-confidence claim
    print("\n[ECONOMIC SFA] Submitting claim: Caesar reformed currency")
    registry.submit_claim(
        entity=entity,
        predicate='reformed_currency',
        facet='ECONOMIC',
        agent_id='demo_p2_economic_sfa',
        confidence=0.60
    )
    print("  -> Status: TBD (awaiting peer review)")
    
    # ==========================================
    # STEP 2: Peer Review Phase
    # ==========================================
    print_section("Step 2: Cross-Facet Peer Review")
    
    print("[POLITICAL SFA] Reviewing claims from other facets...")
    reviews_pol = reviewer.review_entity_claims(
        'ent_per_Q1048_DEMO_P2',
        'POLITICAL',
        'demo_p2_political_reviewer'
    )
    print(f"  -> Reviewed {len(reviews_pol)} claims:")
    for r in reviews_pol:
        status_icon = "[AGREE]" if r['agrees'] else "[DISAGREE]"
        print(f"     {status_icon} {r['reviewed_facet']} claim '{r['reviewed_predicate']}'")
    
    print("\n[ECONOMIC SFA] Reviewing claims from other facets...")
    reviews_eco = reviewer.review_entity_claims(
        'ent_per_Q1048_DEMO_P2',
        'ECONOMIC',
        'demo_p2_economic_reviewer'
    )
    print(f"  -> Reviewed {len(reviews_eco)} claims:")
    for r in reviews_eco:
        status_icon = "[AGREE]" if r['agrees'] else "[DISAGREE]"
        print(f"     {status_icon} {r['reviewed_facet']} claim '{r['reviewed_predicate']}'")
    
    print("\n[SOCIAL SFA] Reviewing claims from other facets...")
    reviews_soc = reviewer.review_entity_claims(
        'ent_per_Q1048_DEMO_P2',
        'SOCIAL',
        'demo_p2_social_reviewer'
    )
    print(f"  -> Reviewed {len(reviews_soc)} claims:")
    for r in reviews_soc:
        status_icon = "[AGREE]" if r['agrees'] else "[DISAGREE]"
        print(f"     {status_icon} {r['reviewed_facet']} claim '{r['reviewed_predicate']}'")
    
    # ==========================================
    # STEP 3: Agreement Scoring
    # ==========================================
    print_section("Step 3: Agreement Score Calculation")
    
    claims = [
        ('MILITARY', 'crossed_rubicon'),
        ('POLITICAL', 'became_dictator'),
        ('ECONOMIC', 'reformed_currency')
    ]
    
    print("Agreement scores for each claim:")
    print("(Score range: -1.0 = all disagree, +1.0 = all agree)\n")
    
    for facet, predicate in claims:
        score = reviewer.get_agreement_score(
            'ent_per_Q1048_DEMO_P2',
            predicate,
            facet
        )
        
        if score >= 0.80:
            status = "[HIGH CONSENSUS]"
        elif score >= 0.50:
            status = "[MODERATE AGREEMENT]"
        elif score >= 0.0:
            status = "[WEAK AGREEMENT]"
        else:
            status = "[CONTESTED]"
        
        print(f"  {status} {facet} '{predicate}': {score:.2f}")
    
    # ==========================================
    # STEP 4: Status Promotion
    # ==========================================
    print_section("Step 4: Claim Status Promotion")
    
    print("Promoting high-agreement claims to CONFIRMED...")
    promoted = reviewer.promote_high_agreement_claims(
        min_agreement=0.80,
        min_reviews=2
    )
    print(f"  -> [OK] {promoted} claims promoted to CONFIRMED")
    
    print("\nFlagging low-agreement claims as CONTESTED...")
    contested = reviewer.flag_contested_claims(
        max_agreement=0.40,
        min_reviews=2
    )
    print(f"  -> [OK] {contested} claims flagged as CONTESTED")
    
    # ==========================================
    # STEP 5: Contested Claims Detection
    # ==========================================
    print_section("Step 5: Contested Claims Detection")
    
    contested_claims = reviewer.find_contested_claims(min_reviews=1, max_agreement=0.50)
    
    if contested_claims:
        print(f"Found {len(contested_claims)} contested claim(s):\n")
        for claim in contested_claims:
            print(f"  [CONTESTED] {claim['facet']} '{claim['predicate']}'")
            print(f"    Entity: {claim['entity_label']}")
            print(f"    Agreement: {claim['agreement_score']:.2f}")
            print(f"    Reviews: {claim['review_count']} ({claim['agrees']} agree, {claim['disagrees']} disagree)")
            print(f"    Agent: {claim['agent_id']}\n")
    else:
        print("  [OK] No contested claims found.")
    
    # ==========================================
    # SUMMARY
    # ==========================================
    print_section("Phase 2 Summary")
    
    print("Key Achievements:")
    print("  [OK] Multiple SFAs submitted claims")
    print("  [OK] Cross-facet peer review completed")
    print("  [OK] Agreement scores calculated")
    print("  [OK] Auto-promotion: TBD -> PROPOSED -> CONFIRMED/CONTESTED")
    print("  [OK] Contested claims detected and flagged")
    
    print("\n[ARCHITECTURE]")
    print("  * Canonical Entity: 1 node for Caesar (ent_per_Q1048_DEMO_P2)")
    print("  * Facet-Scoped Claims: Each SFA has separate :ASSERTS edges")
    print("  * Peer Reviews: :REVIEWED edges track cross-facet validation")
    print("  * Status Lifecycle: TBD -> PROPOSED -> CONFIRMED/CONTESTED")
    print("  * Agreement Scoring: Consensus-based promotion")
    
    print("\n[NEXT STEPS]")
    print("  * Phase 3: Conflict Resolution UI")
    print("  * Phase 4: SFA Integration & Migration")
    print("  * Phase 5: Production Deployment")
    
    print("\nDemo complete!")


if __name__ == "__main__":
    try:
        phase2_demo()
    except Exception as e:
        print(f"\n[FAIL] Demo encountered an error: {e}")
        import traceback
        traceback.print_exc()
