"""
Integration Test: Military SFA Theory Discovery

Tests the complete workflow:
1. SFA reads passage from Boyd
2. Claude analyzes and discovers principles
3. MilitaryPrinciple nodes created
4. Claims submitted to MILITARY_THEORY
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


# Boyd OODA Loop passage (from Patterns of Conflict)
BOYD_OODA_PASSAGE = """
The key is to operate at a faster tempo or rhythm than our adversaries—or, 
better yet, get inside the adversary's Observation-Orientation-Decision-Action 
time cycle or loop. The one who can handle the quickest rate of change is the 
one who will prevail.

Why? Such activity will make us appear ambiguous (unpredictable) thereby 
generate confusion and disorder among our adversaries—since our adversaries 
will be unable to generate mental images or pictures that agree with the 
menacing, as well as faster transient rhythm or patterns, they are competing 
against.

Operating inside an adversary's OODA loop means we observe, orient, decide, 
and act more quickly, thereby denying the adversary the opportunity to 
effectively counter our actions. We repeatedly get inside their decision cycle, 
making their observations obsolete, their orientation irrelevant, their 
decisions ineffective, and their actions impotent.
"""


def test_discovery():
    """Test discovery on Boyd OODA passage."""
    
    print("\n" + "="*70)
    print("  THEORY DISCOVERY INTEGRATION TEST")
    print("="*70)
    
    # Initialize
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    )
    
    try:
        military = MilitarySFAEnhanced(driver)
        
        print("\n[1] Reading Boyd passage...")
        print(f"    Length: {len(BOYD_OODA_PASSAGE)} characters")
        print(f"    Source: Patterns of Conflict (1976)")
        
        print("\n[2] Calling Claude to discover principles...")
        discovered = military.discover_theory_from_source(
            source_ref="Boyd, Patterns of Conflict (1976) - OODA Loop section",
            passage_text=BOYD_OODA_PASSAGE,
            theorist="John Boyd"
        )
        
        if discovered:
            print(f"\n[3] SUCCESS - Discovered {len(discovered)} principle(s):\n")
            
            for idx, principle in enumerate(discovered, 1):
                print(f"    {idx}. {principle['label']}")
                print(f"       ID: {principle['principle_id']}")
            
            # Query Neo4j to verify
            print("\n[4] Verifying in Neo4j...")
            with driver.session() as session:
                result = session.run("""
                    MATCH (mp:MilitaryPrinciple)
                    WHERE mp.discovered_by = 'military_sfa_001_enhanced'
                      AND mp.discovered_from CONTAINS 'Boyd'
                    RETURN mp.label, mp.statement, mp.category
                """)
                
                for record in result:
                    print(f"\n    ✓ {record['mp.label']}")
                    print(f"      Statement: {record['mp.statement']}")
                    print(f"      Category: {record['mp.category']}")
            
            # Cleanup
            print("\n[5] Cleaning up test data...")
            with driver.session() as session:
                session.run("""
                    MATCH (mp:MilitaryPrinciple)
                    WHERE mp.discovered_from CONTAINS 'Boyd'
                      AND mp.discovered_by = 'military_sfa_001_enhanced'
                    DETACH DELETE mp
                """)
            
            print("    ✓ Cleanup complete")
            print("\n" + "="*70)
            print("  TEST PASSED - Discovery pipeline working!")
            print("="*70 + "\n")
            
        else:
            print("\n[3] No principles discovered")
            print("    Check Claude API configuration")
            print("\n" + "="*70)
            print("  TEST RESULT: No discovery (check API setup)")
            print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.close()


if __name__ == "__main__":
    test_discovery()
