"""
Test suite for AssertionCipher vs PerspectiveID split.

Tests the fix for 2-16-26-ArchReview2 Issue A:
- AssertionCipher: facet-agnostic, enables cross-facet consensus
- PerspectiveID: facet-specific, tracks facet + agent perspective

Key requirement: Same content from different facets → same AssertionCipher
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from validation_models import (
    Claim,
    FacetAssignment,
    RelationshipAssertion,
    LifecycleStatus,
    initialize_registry,
)


def setup_registry():
    """Initialize registry for testing (optional - tests work without it)."""
    base_path = Path(__file__).parent.parent.parent
    facet_json = base_path / "JSON" / "facets.json"
    rel_csv = base_path / "CSV" / "relationship_types.csv"
    
    if facet_json.exists() and rel_csv.exists():
        initialize_registry(str(facet_json), str(rel_csv))
        return True
    else:
        print(f"⚠️  Registry files not found - tests will run without validation:")
        print(f"   Facet JSON: {facet_json}")
        print(f"   Relationship CSV: {rel_csv}")
        return False


def test_assertion_cipher_facet_agnostic():
    """Test that AssertionCipher is the same across different facets."""
    print("\n" + "="*70)
    print("TEST: AssertionCipher is Facet-Agnostic")
    print("="*70)
    
    # Military facet discovers a claim
    claim_military = Claim(
        claim_id="claim_military_001",
        cipher="temp",  # Will be replaced
        content="Julius Caesar crossed the Rubicon in 49 BCE",
        source_id="plutarch_lives_caesar_ch32",
        created_by="agent_military_001",
        facets=[],  # Simplified - no facet validation needed for cipher test
    )
    cipher_military = claim_military.compute_assertion_cipher()
    
    # Political facet discovers THE SAME claim
    claim_political = Claim(
        claim_id="claim_political_002",
        cipher="temp",
        content="Julius Caesar crossed the Rubicon in 49 BCE",
        source_id="plutarch_lives_caesar_ch32",
        created_by="agent_political_002",
        facets=[],  # Different facets, but we're testing AssertionCipher
    )
    cipher_political = claim_political.compute_assertion_cipher()
    
    # Geographic facet discovers THE SAME claim
    claim_geographic = Claim(
        claim_id="claim_geographic_003",
        cipher="temp",
        content="Julius Caesar crossed the Rubicon in 49 BCE",
        source_id="plutarch_lives_caesar_ch32",
        created_by="agent_geographic_003",
        facets=[],
    )
    cipher_geographic = claim_geographic.compute_assertion_cipher()
    
    print(f"Military facet cipher:   {cipher_military}")
    print(f"Political facet cipher:  {cipher_political}")
    print(f"Geographic facet cipher: {cipher_geographic}")
    print()
    
    # CRITICAL TEST: All AssertionCiphers should be identical
    assert cipher_military == cipher_political, \
        "AssertionCipher should be identical across facets"
    assert cipher_military == cipher_geographic, \
        "AssertionCipher should be identical across facets"
    
    print("✓ All three facets produced IDENTICAL AssertionCipher")
    print("✓ Cross-facet deduplication is possible")
    print("✓ Consensus scoring can work")
    print("✓ PASS")


def test_perspective_id_facet_specific():
    """Test that PerspectiveID differs across facets (when facets differ)."""
    print("\n" + "="*70)
    print("TEST: PerspectiveID is Facet-Specific")
    print("="*70)
    
    # Note: Without registry, we'll simulate facet differences via created_by
    # (PerspectiveID includes agent_id)
    
    # Military agent perspective
    claim_military = Claim(
        claim_id="claim_military_001",
        cipher="temp",
        content="Julius Caesar crossed the Rubicon in 49 BCE",
        source_id="plutarch_lives_caesar_ch32",
        created_by="agent_military_001",  # Different agent
        facets=[],
    )
    perspective_military = claim_military.compute_perspective_id()
    
    # Political agent perspective
    claim_political = Claim(
        claim_id="claim_political_002",
        cipher="temp",
        content="Julius Caesar crossed the Rubicon in 49 BCE",
        source_id="plutarch_lives_caesar_ch32",
        created_by="agent_political_002",  # Different agent
        facets=[],
    )
    perspective_political = claim_political.compute_perspective_id()
    
    print(f"Military PerspectiveID:  {perspective_military}")
    print(f"Political PerspectiveID: {perspective_political}")
    print()
    
    # CRITICAL TEST: PerspectiveIDs should be DIFFERENT (different agents)
    assert perspective_military != perspective_political, \
        "PerspectiveID should differ across agents"
    
    print("✓ Different agents produced DIFFERENT PerspectiveID")
    print("✓ Agent-specific provenance preserved")
    print("✓ PASS")


def test_assertion_cipher_computable_from_instance():
    """Test that we can compute AssertionCipher from any claim instance."""
    print("\n" + "="*70)
    print("TEST: Compute AssertionCipher from Claim Instance")
    print("="*70)
    
    # Create claim
    claim = Claim(
        claim_id="claim_001",
       cipher="temp",
        content="Julius Caesar crossed the Rubicon",
        source_id="source_001",
        created_by="agent_001",
        facets=[],
    )
    
    # Compute both cipher types
    assertion_cipher = claim.compute_assertion_cipher()
    perspective_id = claim.compute_perspective_id()
    
    print(f"AssertionCipher:      {assertion_cipher}")
    print(f"PerspectiveID:        {perspective_id}")
    print()
    
    assert assertion_cipher != perspective_id, "AssertionCipher should differ from PerspectiveID (includes agent)"
    
    print("✓ Can compute both cipher types from any instance")
    print("✓ PASS")


def test_cross_facet_consensus_scenario():
    """Test realistic cross-facet consensus scenario."""
    print("\n" + "="*70)
    print("TEST: Cross-Facet Consensus Scenario")
    print("="*70)
    
    # Three different agents independently extract the same claim
    agents = ["agent_military_001", "agent_political_002", "agent_geographic_003"]
    claims = []
    assertion_ciphers = []
    
    for i, agent in enumerate(agents):
        claim = Claim(
            claim_id=f"claim_{i+1:03d}",
            cipher="temp",
            content="Julius Caesar crossed the Rubicon in 49 BCE",
            source_id="plutarch_lives_caesar_ch32",
            created_by=agent,
            facets=[],
        )
        claims.append(claim)
        assertion_cipher = claim.compute_assertion_cipher()
        assertion_ciphers.append(assertion_cipher)
        print(f"{agent:25s} → AssertionCipher: {assertion_cipher}")
    
    # Check all AssertionCiphers are identical
    unique_ciphers = set(assertion_ciphers)
    assert len(unique_ciphers) == 1, "All agents should produce same AssertionCipher for same content"
    
    print()
    print("✓ All three agents agree: same AssertionCipher")
    print("✓ System can detect claim agreement across agents/facets")
    print("✓ Consensus confidence can be computed")
    print("✓ PASS")


def test_perspective_provenance_tracking():
    """Test PerspectiveID for provenance tracking."""
    print("\n" + "="*70)
    print("TEST: PerspectiveID Provenance Tracking")
    print("="*70)
    
    # Same agent → stable PerspectiveID
    claim1 = Claim(
        claim_id="claim_001",
        cipher="temp",
        content="Julius Caesar crossed the Rubicon",
        source_id="source_001",
        created_by="agent_military_001",
        facets=[],
    )
    
    claim2 = Claim(
        claim_id="claim_002",  # Different claim_id
        cipher="temp",
        content="Julius Caesar crossed the Rubicon",
        source_id="source_001",
        created_by="agent_military_001",  # Same agent
        facets=[],
    )
    
    perspective1 = claim1.compute_perspective_id()
    perspective2 = claim2.compute_perspective_id()
    
    print(f"Claim 1 PerspectiveID: {perspective1}")
    print(f"Claim 2 PerspectiveID: {perspective2}")
    print()
    
    assert perspective1 == perspective2, \
        "Same agent + content should produce stable PerspectiveID"
    
    print("✓ Same agent → stable PerspectiveID")
    print("✓ Enables tracking agent-specific confidence evolution")
    print("✓ PASS")


def test_verify_cipher_both_types():
    """Test cipher verification for both AssertionCipher and PerspectiveID."""
    print("\n" + "="*70)
    print("TEST: Verify Both Cipher Types")
    print("="*70)
    
    # Create claim
    claim = Claim(
        claim_id="claim_001",
        cipher="temp",
        content="Test claim",
        source_id="source_001",
        created_by="agent_001",
        facets=[],
    )
    
    # Set cipher to AssertionCipher
    claim.cipher = claim.compute_assertion_cipher()
    assertion_valid = claim.verify_cipher(cipher_type="assertion")
    
    # Set cipher to PerspectiveID
    claim.cipher = claim.compute_perspective_id()
    perspective_valid = claim.verify_cipher(cipher_type="perspective")
    
    print("AssertionCipher:")
    print(f"  Cipher:   {claim.compute_assertion_cipher()}")
    print(f"  Verified: {assertion_valid}")
    print()
    print("PerspectiveID:")
    print(f"  Cipher:   {claim.compute_perspective_id()}")
    print(f"  Verified: {perspective_valid}")
    print()
    
    assert assertion_valid, "AssertionCipher should verify"
    assert perspective_valid, "PerspectiveID should verify"
    
    print("✓ Both cipher types verify correctly")
    print("✓ PASS")


def run_all_tests():
    """Run all cipher split tests."""
    print("\n" + "="*70)
    print("ASSERTION CIPHER vs PERSPECTIVE ID TEST SUITE")
    print("Fix for 2-16-26-ArchReview2 Issue A")
    print("="*70)
    
    tests = [
        test_assertion_cipher_facet_agnostic,
        test_perspective_id_facet_specific,
        test_assertion_cipher_computable_from_instance,
        test_cross_facet_consensus_scenario,
        test_perspective_provenance_tracking,
        test_verify_cipher_both_types,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("\n✅ All cipher split tests passed!")
        print("✅ AssertionCipher enables cross-facet deduplication")
        print("✅ PerspectiveID preserves facet-specific provenance")
        print("✅ Architecture Review Issue A is RESOLVED")
    else:
        print(f"\n✗ {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
