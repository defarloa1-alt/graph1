"""
Military Theory Discovery Demo

Demonstrates:
1. Military SFA discovering universal theories from sources
2. Creating MilitaryPrinciple nodes in MILITARY_THEORY SubjectConcept
3. Linking historical Roman events to discovered theories
4. Cross-SubjectConcept claims (ROMAN_REPUBLIC → MILITARY_THEORY)

Option A: One SFA (Military), Two Target Domains
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


def print_banner(text):
    """Print formatted banner."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def demo_discover_boyd_ooda(military: MilitarySFAEnhanced):
    """Demonstrate discovering OODA Loop from Boyd."""
    print_banner("DEMO 1: Discover Boyd's OODA Loop")
    
    # Manually create principle (simulating discovery)
    principle_id = military._create_theory_principle(
        principle={
            'label': 'OODA Loop',
            'statement': 'Decision advantage comes from cycling Observe-Orient-Decide-Act faster than opponent',
            'category': 'decision_cycle',
            'applicability': 'universal'
        },
        source_ref='Boyd, Patterns of Conflict (1976)',
        theorist='John Boyd'
    )
    
    print(f"[OK] Discovered principle: OODA Loop")
    print(f"     ID: {principle_id}")
    print(f"     Category: decision_cycle")
    print(f"     Applicability: universal")
    
    # Submit claim about the discovery
    claim_id = military.submit_theory_claim(
        principle_id=principle_id,
        predicate='defines_principle',
        confidence=0.95,
        source_ref='Boyd, Patterns of Conflict (1976)'
    )
    
    print(f"\n[OK] Submitted claim: {claim_id}")
    print(f"     Predicate: defines_principle")
    print(f"     Target: MILITARY_THEORY SubjectConcept")
    
    return principle_id


def demo_discover_clausewitz_friction(military: MilitarySFAEnhanced):
    """Demonstrate discovering Friction from Clausewitz."""
    print_banner("DEMO 2: Discover Clausewitz's Friction")
    
    principle_id = military._create_theory_principle(
        principle={
            'label': 'Friction in War',
            'statement': 'Accumulated small difficulties create gap between war on paper and war in reality',
            'category': 'command_doctrine',
            'applicability': 'universal'
        },
        source_ref='Clausewitz, On War Book 1 Ch. 7',
        theorist='Carl von Clausewitz'
    )
    
    print(f"[OK] Discovered principle: Friction in War")
    print(f"     ID: {principle_id}")
    print(f"     Category: command_doctrine")
    print(f"     Source: Clausewitz, On War (1832)")
    
    claim_id = military.submit_theory_claim(
        principle_id=principle_id,
        predicate='defines_principle',
        confidence=0.94,
        source_ref='Clausewitz, On War Book 1 Ch. 7'
    )
    
    print(f"\n[OK] Submitted claim: {claim_id}")
    
    return principle_id


def demo_discover_liddell_hart(military: MilitarySFAEnhanced):
    """Demonstrate discovering Indirect Approach from Liddell Hart."""
    print_banner("DEMO 3: Discover Liddell Hart's Indirect Approach")
    
    principle_id = military._create_theory_principle(
        principle={
            'label': 'Indirect Approach',
            'statement': 'Decisive results come from dislocating enemy psychologically and physically rather than direct confrontation',
            'category': 'strategic_framework',
            'applicability': 'universal'
        },
        source_ref='Liddell Hart, Strategy (1954)',
        theorist='B.H. Liddell Hart'
    )
    
    print(f"[OK] Discovered principle: Indirect Approach")
    print(f"     ID: {principle_id}")
    print(f"     Category: strategic_framework")
    print(f"     Key concept: Dislocation > Destruction")
    
    claim_id = military.submit_theory_claim(
        principle_id=principle_id,
        predicate='establishes_framework',
        confidence=0.93,
        source_ref='Liddell Hart, Strategy (1954)'
    )
    
    print(f"\n[OK] Submitted claim: {claim_id}")
    
    return principle_id


def demo_link_cannae_to_ooda(military: MilitarySFAEnhanced, ooda_id: str, driver):
    """Link Battle of Cannae to OODA Loop theory."""
    print_banner("DEMO 4: Link Battle of Cannae to OODA Loop")
    
    print("Analyzing: Battle of Cannae (216 BCE)")
    print("Theory: OODA Loop (Boyd 1976)")
    
    # First, ensure Cannae entity exists
    with driver.session() as session:
        session.run("""
            MERGE (e:EVENT {qid: 'Q36456'})
            SET e.label = 'Battle of Cannae',
                e.date = '-216-08-02',
                e.subject = 'roman_republic',
                e.entity_cipher = 'ent_evt_Q36456'
        """)
    
    # Create cross-SubjectConcept link
    claim_id = military.link_event_to_theory(
        event_qid='Q36456',
        principle_id=ooda_id,
        predicate='exemplifies_principle',
        confidence=0.89,
        analysis="Hannibal's cavalry creating dust clouds disrupted Roman observation and orientation phases, getting inside their OODA loop and causing decision paralysis",
        source_ref='Polybius 3.116'
    )
    
    print(f"\n[OK] Created cross-SubjectConcept link")
    print(f"     From: ROMAN_REPUBLIC (Battle of Cannae)")
    print(f"     To: MILITARY_THEORY (OODA Loop)")
    print(f"     Predicate: exemplifies_principle")
    print(f"     Analysis: Hannibal disrupted Roman OODA cycle with cavalry dust")
    print(f"\n[OK] Claim ID: {claim_id}")


def demo_link_alesia_to_indirect(military: MilitarySFAEnhanced, indirect_id: str, driver):
    """Link Siege of Alesia to Indirect Approach."""
    print_banner("DEMO 5: Link Siege of Alesia to Indirect Approach")
    
    print("Analyzing: Siege of Alesia (52 BCE)")
    print("Theory: Indirect Approach (Liddell Hart 1954)")
    
    # Ensure Alesia entity exists
    with driver.session() as session:
        session.run("""
            MERGE (e:EVENT {qid: 'Q2604'})
            SET e.label = 'Siege of Alesia',
                e.date = '-52',
                e.subject = 'roman_republic',
                e.entity_cipher = 'ent_per_Q2604'
        """)
    
    # Create link
    claim_id = military.link_event_to_theory(
        event_qid='Q2604',
        principle_id=indirect_id,
        predicate='exemplifies_principle',
        confidence=0.92,
        analysis="Caesar's double circumvallation avoided direct assault on Vercingetorix's fortifications, instead isolating him psychologically and physically to force surrender without battle",
        source_ref='Caesar BGC 7.68-89'
    )
    
    print(f"\n[OK] Created cross-SubjectConcept link")
    print(f"     From: ROMAN_REPUBLIC (Siege of Alesia)")
    print(f"     To: MILITARY_THEORY (Indirect Approach)")
    print(f"     Predicate: exemplifies_principle")
    print(f"     Analysis: Caesar used dislocation over destruction")
    print(f"\n[OK] Claim ID: {claim_id}")


def query_discovered_theories(driver):
    """Query what theories the Military SFA has discovered."""
    print_banner("DEMO 6: Query Discovered Theories")
    
    with driver.session() as session:
        # Count principles by category
        result = session.run("""
            MATCH (mp:MilitaryPrinciple)
            WHERE mp.discovered_by = 'military_sfa_001_enhanced'
            RETURN mp.category as category, count(*) as count
            ORDER BY count DESC
        """)
        
        print("Principles discovered by Military SFA:\n")
        total = 0
        for record in result:
            count = record['count']
            total += count
            print(f"  {record['category']:<25} {count} principle(s)")
        
        print(f"\n  Total: {total} principles\n")
        
        # List all principles
        result = session.run("""
            MATCH (mp:MilitaryPrinciple)
            WHERE mp.discovered_by = 'military_sfa_001_enhanced'
            RETURN mp.label, mp.theorist, mp.discovered_from
            ORDER BY mp.discovered_at ASC
        """)
        
        print("Detailed list:\n")
        for idx, record in enumerate(result, 1):
            print(f"  {idx}. {record['mp.label']}")
            print(f"     Theorist: {record['mp.theorist']}")
            print(f"     Source: {record['mp.discovered_from']}\n")


def query_theory_applications(driver):
    """Query which Roman events exemplify discovered theories."""
    print_banner("DEMO 7: Query Theory Applications")
    
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                  -[claim:ASSERTS]->
                  (event:EVENT)
            WHERE claim.predicate = 'exemplifies_principle'
              AND event.subject = 'roman_republic'
            RETURN 
                event.label as battle,
                claim.principle_applied as theory_id,
                claim.framework_analysis as analysis
        """)
        
        print("Roman events that exemplify universal theories:\n")
        for idx, record in enumerate(result, 1):
            print(f"  {idx}. {record['battle']}")
            print(f"     Theory: {record['theory_id']}")
            print(f"     Analysis: {record['analysis'][:80]}...")
            print()


def cleanup_demo_data(driver):
    """Clean up demo data."""
    print_banner("Cleanup")
    
    with driver.session() as session:
        # Delete demo principles and claims
        session.run("""
            MATCH (mp:MilitaryPrinciple)
            WHERE mp.discovered_by = 'military_sfa_001_enhanced'
            DETACH DELETE mp
        """)
        
        # Clean up demo events
        session.run("""
            MATCH (e:EVENT)
            WHERE e.qid IN ['Q36456', 'Q2604']
            DETACH DELETE e
        """)
    
    print("[OK] Demo data cleaned up")


def main():
    """Run all demos."""
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    military = MilitarySFAEnhanced(driver)
    
    print("\n")
    print("="*70)
    print("  MILITARY THEORY DISCOVERY DEMO")
    print("  Option A: One SFA, Two Target Domains")
    print("="*70)
    print("\n  Military SFA claims against:")
    print("    1. ROMAN_REPUBLIC (historical entities)")
    print("    2. MILITARY_THEORY (discovered principles)")
    
    try:
        # Discover theories
        ooda_id = demo_discover_boyd_ooda(military)
        friction_id = demo_discover_clausewitz_friction(military)
        indirect_id = demo_discover_liddell_hart(military)
        
        # Link theories to historical events
        demo_link_cannae_to_ooda(military, ooda_id, driver)
        demo_link_alesia_to_indirect(military, indirect_id, driver)
        
        # Query results
        query_discovered_theories(driver)
        query_theory_applications(driver)
        
        # Cleanup
        cleanup_demo_data(driver)
        
        print("\n[OK] All demos completed successfully!\n")
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}\n")
        import traceback
        traceback.print_exc()
        raise
    finally:
        driver.close()


if __name__ == "__main__":
    main()
