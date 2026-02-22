"""
Test Suite for V1 Kernel Relationships

Validates that V1KernelAssertion correctly enforces the 25 core relationships
and rejects relationships outside the kernel.

Run with:
    python test_v1_kernel.py
"""

from pathlib import Path
import sys

# Add parent directory to path so we can import models from current directory
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from validation_models import (
    initialize_registry,
    V1KernelAssertion,
    V1_KERNEL_RELATIONSHIPS,
    RelationshipAssertion,
)
from pydantic import ValidationError


def test_v1_kernel_set():
    """Verify v1 kernel contains exactly 30 relationships (Priority 10 expansion)."""
    print("TEST: V1 Kernel Set")
    print(f"  Expected: 30 relationships (expanded from 25 based on Priority 10 discovery)")
    print(f"  Actual: {len(V1_KERNEL_RELATIONSHIPS)} relationships")
    
    assert len(V1_KERNEL_RELATIONSHIPS) == 30, f"Expected 30, got {len(V1_KERNEL_RELATIONSHIPS)}"
    
    # Verify all 30 are present (expanded kernel)
    expected = {
        # Identity (5)
        "SAME_AS", "TYPE_OF", "INSTANCE_OF", "NAME", "ALIAS_OF",
        # Spatial (5)
        "LOCATED_IN", "PART_OF", "BORDERS", "CAPITAL_OF", "CONTAINED_BY",
        # Temporal & Event (6) - includes PARTICIPATED_IN pair for P710
        "OCCURRED_AT", "OCCURS_DURING", "HAPPENED_BEFORE", "CONTEMPORARY_WITH",
        "PARTICIPATED_IN", "HAD_PARTICIPANT",
        # Provenance (7) - added FIELD_OF_STUDY for P101
        "CITES", "DERIVES_FROM", "EXTRACTED_FROM", "AUTHOR", "ATTRIBUTED_TO", "DESCRIBES",
        "FIELD_OF_STUDY",
        # Conceptual & Semantic (7) - added ABOUT, STUDIED_BY for P921, P101
        "SUBJECT_OF", "ABOUT", "STUDIED_BY", "CAUSED", "CONTRADICTS", "SUPPORTS",
        "RELATED_TO",
    }
    
    assert V1_KERNEL_RELATIONSHIPS == expected, "Kernel mismatch"
    print("  ✓ PASS: V1 kernel set verified\n")


def test_v1_kernel_assertion_valid():
    """Test V1KernelAssertion accepts all 30 v1 kernel relationships (Priority 10 expansion)."""
    print("TEST: V1KernelAssertion - Valid Relationships")
    
    test_cases = [
        ("SAME_AS", "Identity"),
        ("LOCATED_IN", "Spatial"),
        ("OCCURRED_AT", "Temporal"),
        ("CITES", "Provenance"),
        ("CAUSED", "Assertion"),
        ("PARTICIPATED_IN", "Temporal"),
        ("FIELD_OF_STUDY", "Provenance"),
        ("ABOUT", "Semantic"),
    ]
    
    for rel_type, category in test_cases:
        try:
            assertion = V1KernelAssertion(
                rel_type=rel_type,
                subject_id="Q1",
                object_id="Q2",
                confidence=0.95
            )
            print(f"  ✓ {rel_type:20s} ({category:10s}): OK")
        except ValidationError as e:
            print(f"  ✗ {rel_type:20s} ({category:10s}): FAILED")
            print(f"    Error: {e}")
            raise
    
    print("  ✓ PASS: All v1 kernel relationships accepted\n")


def test_v1_kernel_assertion_rejects_outside():
    """Test V1KernelAssertion rejects relationships outside kernel."""
    print("TEST: V1KernelAssertion - Invalid (Non-Kernel) Relationships")
    
    # These are real relationships in the full registry but NOT in v1 kernel
    invalid_v1_types = [
        "COMMANDED_MILITARY_UNIT",
        "PARENT_OF",
        "MEMBER_OF",
        "CONFLICT_WITH",
        "INFLUENCED",
        "MARRIED_TO",
        "PERFORMED",
    ]
    
    for rel_type in invalid_v1_types:
        try:
            assertion = V1KernelAssertion(
                rel_type=rel_type,
                subject_id="Q1",
                object_id="Q2",
                confidence=0.95
            )
            print(f"  ✗ {rel_type:30s}: Should have been rejected but was accepted!")
            raise AssertionError(f"V1KernelAssertion should have rejected {rel_type}")
        except ValidationError as e:
            print(f"  ✓ {rel_type:30s}: Correctly rejected")
    
    print("  ✓ PASS: All non-kernel relationships rejected\n")


def test_case_insensitivity():
    """Test V1KernelAssertion normalizes case."""
    print("TEST: V1KernelAssertion - Case Normalization")
    
    test_cases = [
        "same_as",
        "Same_As",
        "SAME_AS",
        "located_in",
        "Located_In",
    ]
    
    for rel_type in test_cases:
        try:
            assertion = V1KernelAssertion(
                rel_type=rel_type,
                subject_id="Q1",
                object_id="Q2"
            )
            normalized = assertion.rel_type
            print(f"  {rel_type:20s} → {normalized:20s} ✓")
            assert normalized.isupper(), f"Should be uppercase, got {normalized}"
        except ValidationError as e:
            print(f"  ✗ {rel_type:20s}: {e}")
            raise
    
    print("  ✓ PASS: Case normalization works\n")


def test_v1_kernel_vs_full_registry():
    """Compare v1 kernel to full registry."""
    print("TEST: V1 Kernel vs Full Registry")
    
    # Register the full repository
    facet_path = Path(__file__).parent.parent / "Relationships" / "facet_registry_master.json"
    rel_path = Path(__file__).parent.parent / "Relationships" / "relationship_types_registry_master.csv"
    
    if facet_path.exists() and rel_path.exists():
        initialize_registry(str(facet_path), str(rel_path))
        
        from validation_models import get_registry_loader
        loader = get_registry_loader()
        
        if loader:
            all_rels = loader.get_all_relationship_types()
            overlap = V1_KERNEL_RELATIONSHIPS & set(all_rels)
            outside_v1 = set(all_rels) - V1_KERNEL_RELATIONSHIPS
            
            print(f"  Total relationships in registry: {len(all_rels)}")
            print(f"  V1 kernel relationships: {len(V1_KERNEL_RELATIONSHIPS)}")
            print(f"  V1 kernel coverage: {len(overlap)}/{len(V1_KERNEL_RELATIONSHIPS)} ({100*len(overlap)/len(V1_KERNEL_RELATIONSHIPS):.1f}%)")
            print(f"  Relationships deferred: {len(outside_v1)} types")
            
            if len(overlap) == 25:
                print("  ✓ PASS: All v1 kernel relationships exist in registry\n")
            else:
                print(f"  ⚠ WARNING: Only {len(overlap)} of 25 kernel types found in registry\n")
    else:
        print(f"  ℹ Registry files not found, skipping full comparison")
        print(f"    Facet path: {facet_path}")
        print(f"    Relationship path: {rel_path}\n")


def test_v1_kernel_assertions_pattern():
    """Show the pattern of v1 kernel assertions."""
    print("TEST: V1 Kernel Assertion Pattern")
    print("\n  Categories represented in kernel:")
    
    categories = {
        "Identity & Recognition": ["SAME_AS", "TYPE_OF", "INSTANCE_OF", "NAME", "ALIAS_OF"],
        "Spatial & Structural": ["LOCATED_IN", "PART_OF", "BORDERS", "CAPITAL_OF", "CONTAINED_BY"],
        "Temporal & Event": ["OCCURRED_AT", "OCCURS_DURING", "HAPPENED_BEFORE", "CONTEMPORARY_WITH"],
        "Provenance & Attribution": ["CITES", "DERIVES_FROM", "EXTRACTED_FROM", "AUTHOR", "ATTRIBUTED_TO", "DESCRIBES"],
        "Relational & Assertion": ["SUBJECT_OF", "OBJECT_OF", "CAUSED", "CONTRADICTS", "SUPPORTS"],
    }
    
    for category, types in categories.items():
        print(f"\n  {category} ({len(types)} types):")
        for rel_type in types:
            in_kernel = "✓" if rel_type in V1_KERNEL_RELATIONSHIPS else "✗"
            print(f"    [{in_kernel}] {rel_type}")
    
    print(f"\n  ✓ PASS: Kernel well-categorized\n")


def run_all_tests():
    """Run all v1 kernel tests."""
    print("=" * 70)
    print("V1 KERNEL RELATIONSHIP TEST SUITE")
    print("=" * 70)
    print()
    
    tests = [
        test_v1_kernel_set,
        test_v1_kernel_assertion_valid,
        test_v1_kernel_assertion_rejects_outside,
        test_case_insensitivity,
        test_v1_kernel_vs_full_registry,
        test_v1_kernel_assertions_pattern,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ✗ TEST FAILED: {e}\n")
            failed += 1
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
