"""
Test suite for Claim cipher integration with canonicalization.

Tests:
- Automatic cipher computation
- Cipher verification
- create_with_cipher factory method
- Cipher reproducibility across claim instances
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
from canonicalization import compute_claim_cipher


def setup_registry():
    """Initialize registry for testing."""
    base_path = Path(__file__).parent.parent.parent
    facet_json = base_path / "JSON" / "facets.json"
    rel_csv = base_path / "CSV" / "relationship_types.csv"
    
    if facet_json.exists() and rel_csv.exists():
        initialize_registry(str(facet_json), str(rel_csv))
        return True
    else:
        print(f"⚠️  Registry files not found:")
        print(f"   Facet JSON: {facet_json}")
        print(f"   Relationship CSV: {rel_csv}")
        print(f"   Skipping registry validation tests")
        return False


def test_compute_canonical_cipher():
    """Test that Claim can compute its own canonical cipher."""
    print("\n" + "="*70)
    print("TEST: Compute Canonical Cipher")
    print("="*70)
    
    # Create claim with manual cipher
    claim = Claim(
        claim_id="test_001",
        cipher="placeholder",
        content="Julius Caesar crossed the Rubicon in 49 BCE",
        source_id="source_001",
        facets=[],
        relationships=[],
        created_by="test_agent"
    )
    
    # Compute canonical cipher
    computed_cipher = claim.compute_canonical_cipher()
    
    print(f"Content: {claim.content}")
    print(f"Computed cipher: {computed_cipher}")
    print(f"Cipher length: {len(computed_cipher)} chars")
    
    assert len(computed_cipher) == 64, "SHA256 should be 64 hex chars"
    assert computed_cipher.isalnum(), "Cipher should be alphanumeric"
    assert computed_cipher.lower() == computed_cipher, "Cipher should be lowercase"
    
    print("✓ Cipher format valid")
    print("✓ PASS")


def test_verify_cipher():
    """Test cipher verification."""
    print("\n" + "="*70)
    print("TEST: Verify Cipher")
    print("="*70)
    
    # Create claim with correct cipher
    content = "Julius Caesar crossed the Rubicon"
    metadata = {
        "source_id": "source_001",
        "facets": [],
        "relationships": []
    }
    
    correct_cipher = compute_claim_cipher(content, metadata)
    
    claim_valid = Claim(
        claim_id="test_002",
        cipher=correct_cipher,
        content=content,
        source_id="source_001",
        facets=[],
        relationships=[],
        created_by="test_agent"
    )
    
    claim_invalid = Claim(
        claim_id="test_003",
        cipher="0" * 64,  # Wrong cipher
        content=content,
        source_id="source_001",
        facets=[],
        relationships=[],
        created_by="test_agent"
    )
    
    print(f"Valid claim cipher: {claim_valid.cipher}")
    print(f"Valid claim verify: {claim_valid.verify_cipher()}")
    print(f"Invalid claim cipher: {claim_invalid.cipher}")
    print(f"Invalid claim verify: {claim_invalid.verify_cipher()}")
    
    assert claim_valid.verify_cipher() is True, "Valid cipher should verify"
    assert claim_invalid.verify_cipher() is False, "Invalid cipher should not verify"
    
    print("✓ Cipher verification works correctly")
    print("✓ PASS")


def test_create_with_cipher():
    """Test create_with_cipher factory method."""
    print("\n" + "="*70)
    print("TEST: Create With Cipher Factory Method")
    print("="*70)
    
    # Create claim using factory method
    claim = Claim.create_with_cipher(
        claim_id="test_004",
        content="Octavian defeated Mark Antony at Actium",
        source_id="source_002",
        created_by="test_agent",
        confidence=0.92
    )
    
    print(f"Claim ID: {claim.claim_id}")
    print(f"Content: {claim.content}")
    print(f"Cipher: {claim.cipher}")
    print(f"Cipher verification: {claim.verify_cipher()}")
    
    assert len(claim.cipher) == 64, "Cipher should be SHA256"
    assert claim.verify_cipher() is True, "Auto-generated cipher should be valid"
    
    print("✓ Factory method creates valid cipher")
    print("✓ PASS")


def test_create_with_cipher_facets():
    """Test create_with_cipher with facets and relationships."""
    print("\n" + "="*70)
    print("TEST: Create With Cipher (Facets & Relationships)")
    print("="*70)
    
    setup_registry()
    
    # Create claim with facets and relationships
    claim = Claim.create_with_cipher(
        claim_id="test_005",
        content="Caesar Augustus established the Pax Romana",
        source_id="source_003",
        created_by="test_agent",
        facets=[
            FacetAssignment(facet="political", confidence=0.95),
            FacetAssignment(facet="military", confidence=0.85)
        ],
        relationships=[
            RelationshipAssertion(
                rel_type="RULED",
                subject_id="person_augustus",
                object_id="location_rome",
                confidence=0.98
            )
        ],
        confidence=0.90
    )
    
    print(f"Claim ID: {claim.claim_id}")
    print(f"Content: {claim.content}")
    print(f"Facets: {[f.facet for f in claim.facets]}")
    print(f"Relationships: {[r.rel_type for r in claim.relationships]}")
    print(f"Cipher: {claim.cipher}")
    print(f"Cipher verification: {claim.verify_cipher()}")
    
    assert len(claim.facets) == 2, "Should have 2 facets"
    assert len(claim.relationships) == 1, "Should have 1 relationship"
    assert claim.verify_cipher() is True, "Cipher should be valid"
    
    print("✓ Factory method handles facets and relationships")
    print("✓ PASS")


def test_cipher_reproducibility():
    """Test that equivalent claims produce identical ciphers."""
    print("\n" + "="*70)
    print("TEST: Cipher Reproducibility")
    print("="*70)
    
    setup_registry()
    
    # Create two identical claims
    claim1 = Claim.create_with_cipher(
        claim_id="test_006a",
        content="Julius Caesar crossed the Rubicon",
        source_id="source_001",
        created_by="agent_001",
        facets=[
            FacetAssignment(facet="military", confidence=0.95)
        ],
        confidence=0.90
    )
    
    claim2 = Claim.create_with_cipher(
        claim_id="test_006b",  # Different claim_id (not part of cipher)
        content="Julius Caesar crossed the Rubicon",
        source_id="source_001",
        created_by="agent_002",  # Different agent (not part of cipher)
        facets=[
            FacetAssignment(facet="military", confidence=0.95)
        ],
        confidence=0.85  # Different confidence (not part of cipher)
    )
    
    print(f"Claim 1 ID: {claim1.claim_id}")
    print(f"Claim 1 Agent: {claim1.created_by}")
    print(f"Claim 1 Confidence: {claim1.confidence}")
    print(f"Claim 1 Cipher: {claim1.cipher}")
    print()
    print(f"Claim 2 ID: {claim2.claim_id}")
    print(f"Claim 2 Agent: {claim2.created_by}")
    print(f"Claim 2 Confidence: {claim2.confidence}")
    print(f"Claim 2 Cipher: {claim2.cipher}")
    print()
    
    assert claim1.cipher == claim2.cipher, "Identical content should produce identical cipher"
    
    print("✓ Equivalent claims have identical ciphers")
    print("✓ Content-addressability verified")
    print("✓ PASS")


def test_cipher_uniqueness():
    """Test that different content produces different ciphers."""
    print("\n" + "="*70)
    print("TEST: Cipher Uniqueness")
    print("="*70)
    
    claim1 = Claim.create_with_cipher(
        claim_id="test_007a",
        content="Julius Caesar crossed the Rubicon",
        source_id="source_001",
        created_by="agent_001"
    )
    
    claim2 = Claim.create_with_cipher(
        claim_id="test_007b",
        content="Julius Caesar crossed the Tiber",  # Different content
        source_id="source_001",
        created_by="agent_001"
    )
    
    claim3 = Claim.create_with_cipher(
        claim_id="test_007c",
        content="Julius Caesar crossed the Rubicon",
        source_id="source_002",  # Different source
        created_by="agent_001"
    )
    
    print(f"Claim 1 (Rubicon): {claim1.cipher[:16]}...")
    print(f"Claim 2 (Tiber):   {claim2.cipher[:16]}...")
    print(f"Claim 3 (diff src): {claim3.cipher[:16]}...")
    
    assert claim1.cipher != claim2.cipher, "Different content should have different cipher"
    assert claim1.cipher != claim3.cipher, "Different source should have different cipher"
    
    print("✓ Different content produces different ciphers")
    print("✓ PASS")


def run_all_tests():
    """Run all cipher integration tests."""
    print("\n" + "="*70)
    print("CLAIM CIPHER INTEGRATION TEST SUITE")
    print("="*70)
    
    tests = [
        test_compute_canonical_cipher,
        test_verify_cipher,
        test_create_with_cipher,
        test_create_with_cipher_facets,
        test_cipher_reproducibility,
        test_cipher_uniqueness,
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
        print("\n✅ All cipher integration tests passed!")
        print("✅ Claim model ready for production use")
        print("✅ Federation-ready with reproducible ciphers")
    else:
        print(f"\n✗ {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
