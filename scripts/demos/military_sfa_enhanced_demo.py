"""
Enhanced Military SFA Demo

Demonstrates Perplexity's source tiering enhancements:
1. Tier 1 Roman primary sources (Polybius, Caesar)
2. Tier 1 with anachronism risk (Vegetius)
3. Tier 2 classical theory (Sun Tzu)
4. Tier 3 modern scholarship
5. Hierarchical predicates (strategic, tactical, doctrinal, leadership, operational)
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


def demo_source_tier_weighting(military: MilitarySFAEnhanced, driver):
    """Demonstrate source tier weighting."""
    print_banner("DEMO 1: Source Tier Weighting")
    
    # Tier 1: Polybius (weight 1.0)
    print("[1] Tier 1 - Polybius (highest weight):")
    print("   Source: Polybius 3.107-117 (Battle of Cannae)")
    print(military.get_source_tier_explanation("Polybius 3.107-117"))
    
    claim1 = military.submit_military_claim(
        entity={'type': 'EVENT', 'qid': 'Q36456', 'label': 'Battle of Cannae'},
        predicate='employed_tactic',
        confidence=0.95,
        source_ref='Polybius 3.107-117'
    )
    print(f"   [OK] Claim submitted: {claim1}")
    print(f"   Final confidence: 0.95 * 1.0 = 0.95")
    
    # Tier 1 with anachronism: Vegetius (weight 0.75)
    print("\n[2] Tier 1 - Vegetius (ANACHRONISM RISK):")
    print("   Source: Vegetius 2.1-15 (Roman legion organization)")
    print(military.get_source_tier_explanation("Vegetius 2.1-15"))
    
    claim2 = military.submit_military_claim(
        entity={'type': 'CONCEPT', 'qid': 'Q170134', 'label': 'Roman legion'},
        predicate='reflects_organizational_structure',
        confidence=0.85,
        source_ref='Vegetius 2.1-15'
    )
    print(f"   [OK] Claim submitted: {claim2}")
    print(f"   Final confidence: 0.85 * 0.75 = 0.6375")
    print(f"   [!] Anachronism risk flagged (4th c. AD on Republican subject)")
    
    # Tier 2: Sun Tzu (weight 0.75)
    print("\n[3] Tier 2 - Sun Tzu (classical theory):")
    print("   Source: Sun Tzu, Art of War 3")
    print(military.get_source_tier_explanation("Sun Tzu, Art of War 3"))
    
    claim3 = military.submit_military_claim(
        entity={'type': 'EVENT', 'qid': 'Q40979', 'label': 'Crossing the Rubicon'},
        predicate='displayed_strategic_vision',
        confidence=0.88,
        source_ref='Sun Tzu, Art of War 3 (principle of initiative)'
    )
    print(f"   [OK] Claim submitted: {claim3}")
    print(f"   Final confidence: 0.88 * 0.75 = 0.66")
    
    # Tier 3: Modern scholarship (weight 0.70)
    print("\n[4] Tier 3 - Goldsworthy (modern scholarship):")
    print("   Source: Goldsworthy, Caesar p. 342")
    print(military.get_source_tier_explanation("Goldsworthy, Caesar p. 342"))
    
    claim4 = military.submit_military_claim(
        entity={'type': 'PERSON', 'qid': 'Q1048', 'label': 'Julius Caesar'},
        predicate='demonstrated_command_quality',
        confidence=0.90,
        source_ref='Goldsworthy, Caesar p. 342'
    )
    print(f"   [OK] Claim submitted: {claim4}")
    print(f"   Final confidence: 0.90 * 0.70 = 0.63")


def demo_predicate_hierarchy(military: MilitarySFAEnhanced):
    """Demonstrate hierarchical predicates."""
    print_banner("DEMO 2: Hierarchical Predicates (5 Levels)")
    
    all_predicates = military.get_all_predicates()
    
    print(f"Total predicates: {len(all_predicates)}")
    print("\nStrategic Level:")
    for p in military.STRATEGIC_PREDICATES[:3]:
        category = military.get_predicate_category(p)
        print(f"   - {p} ({category})")
    
    print("\nTactical Level:")
    for p in military.TACTICAL_PREDICATES[:3]:
        category = military.get_predicate_category(p)
        print(f"   - {p} ({category})")
    
    print("\nDoctrinal Level:")
    for p in military.DOCTRINAL_PREDICATES[:3]:
        category = military.get_predicate_category(p)
        print(f"   - {p} ({category})")
    
    print("\nLeadership Level:")
    for p in military.LEADERSHIP_PREDICATES[:3]:
        category = military.get_predicate_category(p)
        print(f"   - {p} ({category})")
    
    print("\nOperational Level (Legacy):")
    for p in military.OPERATIONAL_PREDICATES[:3]:
        category = military.get_predicate_category(p)
        print(f"   - {p} ({category})")


def demo_enhanced_metadata(military: MilitarySFAEnhanced, driver):
    """Demonstrate enhanced metadata on claims."""
    print_banner("DEMO 3: Enhanced Metadata")
    
    # Submit claim with full metadata
    claim_id = military.submit_military_claim(
        entity={'type': 'EVENT', 'qid': 'Q2604', 'label': 'Battle of Alesia'},
        predicate='triggered_conflict',
        confidence=0.92,
        source_ref='Caesar, BGC 7.68-89',
        source_qid='Q41333',  # De Bello Gallico
        igar_chain={
            'input': 'Vercingetorix gathered all Gallic forces at Alesia',
            'goal': 'Break the siege',
            'action': 'Combined relief attack and sortie',
            'result': 'Failed, Vercingetorix surrendered'
        }
    )
    
    print(f"Claim ID: {claim_id}\n")
    
    # Query Neo4j to show all metadata
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                  -[c:ASSERTS]->
                  (e {qid: 'Q2604'})
            RETURN c
        """)
        
        record = result.single()
        if record:
            claim = record['c']
            print("Enhanced Metadata Stored in Neo4j:")
            print(f"   predicate: {claim['predicate']}")
            print(f"   confidence: {claim['confidence']}")
            print(f"   facet: {claim['facet']}")
            print(f"   source_tier: {claim['source_tier']}")
            print(f"   anachronism_risk: {claim['anachronism_risk']}")
            print(f"   predicate_category: {claim['predicate_category']}")
            print(f"   source_weight_applied: {claim['source_weight_applied']}")
            print(f"   source_uri: {claim.get('source_uri', 'N/A')}")
            print(f"   source_specialty: {claim.get('source_specialty', 'N/A')}")
            print(f"   status: {claim['status']}")


def demo_anachronism_comparison(military: MilitarySFAEnhanced, driver):
    """Compare same claim with different sources."""
    print_banner("DEMO 4: Anachronism Risk Comparison")
    
    # Same subject, different sources
    entity = {'type': 'CONCEPT', 'qid': 'Q3883', 'label': 'Roman military tactics'}
    
    print("Submitting same claim with different sources:\n")
    
    # Source 1: Polybius (contemporary, 200-118 BCE)
    claim1 = military.submit_military_claim(
        entity=entity,
        predicate='illustrates_military_doctrine',
        confidence=0.85,
        source_ref='Polybius 6.19-42'
    )
    print("[1] Polybius (200-118 BCE):")
    print(f"    Confidence: 0.85 * 1.0 = 0.85")
    print(f"    Anachronism risk: FALSE")
    
    # Source 2: Vegetius (late, 390-450 CE)
    claim2 = military.submit_military_claim(
        entity=entity,
        predicate='illustrates_military_doctrine',
        confidence=0.85,
        source_ref='Vegetius 1.1-10'
    )
    print("\n[2] Vegetius (390-450 CE):")
    print(f"    Confidence: 0.85 * 0.75 = 0.6375")
    print(f"    Anachronism risk: TRUE")
    print(f"    [!] 450-year gap from Republican period")
    
    # Query to compare
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Agent {agent_id: 'military_sfa_001_enhanced'})
                  -[c:ASSERTS]->
                  (e {qid: 'Q3883'})
            WHERE c.predicate = 'illustrates_military_doctrine'
            RETURN 
                c.source_tier as tier,
                c.confidence as confidence,
                c.anachronism_risk as risk
            ORDER BY c.confidence DESC
        """)
        
        print("\n\nComparison in Neo4j:")
        print("    Source          Tier         Confidence  Anachronism")
        print("    " + "-"*60)
        for idx, record in enumerate(result, 1):
            tier_name = record['tier'].replace('tier1_', 'Tier 1: ')
            risk_flag = "[!]" if record['risk'] else "   "
            print(f"    {risk_flag} {tier_name:<15} {record['confidence']:.4f}      {record['risk']}")


def cleanup_demo_data(driver):
    """Clean up demo data."""
    print_banner("Cleanup")
    
    with driver.session() as session:
        # Delete demo entities and claims
        session.run("""
            MATCH (e)
            WHERE e.qid IN ['Q36456', 'Q170134', 'Q40979', 'Q1048', 'Q2604', 'Q3883']
            DETACH DELETE e
        """)
    
    print("[OK] Demo data cleaned up")


def main():
    """Run all demos."""
    # Connect to Neo4j
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    # Create enhanced Military SFA
    military = MilitarySFAEnhanced(driver)
    
    print("\n")
    print("="*70)
    print("  ENHANCED MILITARY SFA DEMO")
    print("  Perplexity Source Tiering + Hierarchical Predicates")
    print("="*70)
    
    try:
        # Run demos
        demo_source_tier_weighting(military, driver)
        demo_predicate_hierarchy(military)
        demo_enhanced_metadata(military, driver)
        demo_anachronism_comparison(military, driver)
        
        # Cleanup
        cleanup_demo_data(driver)
        
        print("\n[OK] All demos completed successfully!\n")
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}\n")
        raise
    finally:
        driver.close()


if __name__ == "__main__":
    main()
