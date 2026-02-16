"""
Test and Demo for Chrystallum Models Package

Demonstrates:
1. Registry loading and validation
2. Pydantic model validation (valid and invalid cases)
3. Neo4j constraint generation
4. Error handling

Run this to verify the validation models work correctly.
"""

import sys
from pathlib import Path
import json

# Setup path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "Python" / "models"))

from registry_loader import RegistryLoader
from validation_models import (
    initialize_registry,
    Claim,
    FacetAssignment,
    FacetAssessment,
    RelationshipAssertion,
    RelationshipEdge,
)
from neo4j_constraints import Neo4jConstraintGenerator


def test_registry_loading():
    """Test 1: Load registries and display summary."""
    print("\n" + "=" * 70)
    print("TEST 1: Registry Loading")
    print("=" * 70)

    facet_path = project_root / "Facets" / "facet_registry_master.json"
    rel_path = project_root / "Relationships" / "relationship_types_registry_master.csv"

    if not facet_path.exists():
        print(f"❌ Facet registry not found: {facet_path}")
        return False

    if not rel_path.exists():
        print(f"❌ Relationship registry not found: {rel_path}")
        return False

    try:
        loader = RegistryLoader(facet_path, rel_path)
        summary = loader.get_summary()

        print(f"\n✓ Registry loaded successfully")
        print(f"  Facets: {summary['facet_count']}")
        print(f"  Relationships: {summary['relationship_count']}")
        print(f"\nCanonical Facet Keys ({summary['facet_count']}):")
        for key in summary['facet_keys']:
            print(f"  - {key}")

        print(f"\nRelationship Categories:")
        categories = set()
        relationships = loader.load_relationships()
        for rel in relationships.values():
            categories.add(rel.category)
        for cat in sorted(categories):
            types = loader.get_relationships_by_category(cat)
            print(f"  {cat}: {len(types)} types")

        return True
    except Exception as e:
        print(f"❌ Error loading registry: {e}")
        return False


def test_facet_validation():
    """Test 2: Validate facet assignments."""
    print("\n" + "=" * 70)
    print("TEST 2: Facet Validation")
    print("=" * 70)

    facet_path = project_root / "Facets" / "facet_registry_master.json"
    rel_path = project_root / "Relationships" / "relationship_types_registry_master.csv"

    # Initialize registry for models
    initialize_registry(facet_path, rel_path)

    # Test 2a: Valid facet
    print("\n2a. Valid Facet Assignment:")
    try:
        facet = FacetAssignment(facet="diplomatic", confidence=0.85)
        print(f"✓ Created: {facet.facet} (confidence={facet.confidence})")
        print(f"  Normalized to lowercase: '{facet.facet}'")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    # Test 2b: Case-insensitive facet
    print("\n2b. Case-Insensitive Facet:")
    try:
        facet = FacetAssignment(facet="MILITARY", confidence=0.90)
        print(f"✓ Created: {facet.facet} (confidence={facet.confidence})")
        print(f"  Uppercase input normalized to lowercase: '{facet.facet}'")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 2c: Invalid facet (should fail)
    print("\n2c. Invalid Facet (Expected to Fail):")
    try:
        facet = FacetAssignment(facet="INVALID_FACET", confidence=0.85)
        print(f"❌ Should have failed but didn't: {facet}")
        return False
    except Exception as e:
        print(f"✓ Correctly rejected invalid facet")
        print(f"  Error: {str(e)[:100]}...")

    return True


def test_relationship_validation():
    """Test 3: Validate relationship assertions."""
    print("\n" + "=" * 70)
    print("TEST 3: Relationship Validation")
    print("=" * 70)

    facet_path = project_root / "Facets" / "facet_registry_master.json"
    rel_path = project_root / "Relationships" / "relationship_types_registry_master.csv"

    # Test 3a: Valid relationship
    print("\n3a. Valid Relationship Assertion:")
    try:
        rel = RelationshipAssertion(
            rel_type="COMMANDED",
            subject_id="Q1048",
            object_id="Q123456",
            confidence=0.92,
            temporal_scope="49-48 BCE",
        )
        print(f"✓ Created: {rel.rel_type}")
        print(f"  Subject: {rel.subject_id} → Object: {rel.object_id}")
        print(f"  Confidence: {rel.confidence}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    # Test 3b: Uppercase normalization
    print("\n3b. Relationship Type Uppercasing:")
    try:
        rel = RelationshipAssertion(
            rel_type="commanded",  # lowercase input
            subject_id="Q1048",
            object_id="Q123456",
        )
        print(f"✓ Created with lowercase input")
        print(f"  Normalized to: {rel.rel_type}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Test 3c: Invalid relationship
    print("\n3c. Invalid Relationship Type (Expected to Fail):")
    try:
        rel = RelationshipAssertion(
            rel_type="NONEXISTENT_RELATIONSHIP",
            subject_id="Q1048",
            object_id="Q123456",
        )
        print(f"❌ Should have failed but didn't: {rel}")
        return False
    except Exception as e:
        print(f"✓ Correctly rejected invalid relationship type")
        print(f"  Error: {str(e)[:100]}...")

    return True


def test_claim_validation():
    """Test 4: Validate complete claims."""
    print("\n" + "=" * 70)
    print("TEST 4: Claim Validation")
    print("=" * 70)

    facet_path = project_root / "Facets" / "facet_registry_master.json"
    rel_path = project_root / "Relationships" / "relationship_types_registry_master.csv"

    # Test 4a: Minimal valid claim
    print("\n4a. Minimal Valid Claim:")
    try:
        claim = Claim(
            claim_id="claim_00001",
            cipher="sha256_abc123def456",
            content="Julius Caesar commanded legions during the Gallic Wars",
            source_id="source_001",
            created_by="seed_agent_001",
        )
        print(f"✓ Created claim: {claim.claim_id}")
        print(f"  Cipher: {claim.cipher[:30]}...")
        print(f"  Status: {claim.status}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    # Test 4b: Claim with facets
    print("\n4b. Claim with Facet Assignments:")
    try:
        claim = Claim(
            claim_id="claim_00002",
            cipher="sha256_xyz789",
            content="The Roman Republic fell after civil wars",
            source_id="source_002",
            facets=[
                {"facet": "military", "confidence": 0.95, "rationale": "Military conflict"},
                {"facet": "political", "confidence": 0.98, "rationale": "State collapse"},
            ],
            created_by="seed_agent_002",
        )
        print(f"✓ Created claim with {len(claim.facets)} facets")
        for f in claim.facets:
            print(f"  - {f.facet} (confidence={f.confidence})")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    # Test 4c: Claim with relationships
    print("\n4c. Claim with Relationship Assertions:")
    try:
        claim = Claim(
            claim_id="claim_00003",
            cipher="sha256_aaa111bbb222",
            content="Caesar fought in the Gallic Wars",
            source_id="source_003",
            relationships=[
                {
                    "rel_type": "FOUGHT_IN",
                    "subject_id": "Q1048",   # Caesar
                    "object_id": "Q123456",   # Gallic Wars
                    "confidence": 0.95,
                }
            ],
            created_by="seed_agent_003",
        )
        print(f"✓ Created claim with {len(claim.relationships)} relationships")
        for r in claim.relationships:
            print(f"  - {r.rel_type}: {r.subject_id} → {r.object_id}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    return True


def test_facet_assessment():
    """Test 5: Validate facet assessments."""
    print("\n" + "=" * 70)
    print("TEST 5: Facet Assessment Validation")
    print("=" * 70)

    facet_path = project_root / "Facets" / "facet_registry_master.json"
    rel_path = project_root / "Relationships" / "relationship_types_registry_master.csv"

    print("\n5a. Valid Facet Assessment:")
    try:
        assessment = FacetAssessment(
            assessment_id="assess_001_00001",
            facet="diplomatic",
            claim_id="claim_00001",
            score=0.85,
            rationale="Clear diplomatic negotiation between two states",
            evaluated_by="facet_specialist_diplomatic_01",
        )
        print(f"✓ Created assessment: {assessment.assessment_id}")
        print(f"  Facet: {assessment.facet}")
        print(f"  Score: {assessment.score}")
        print(f"  Status: {assessment.status}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

    return True


def test_neo4j_constraints():
    """Test 6: Generate Neo4j constraints."""
    print("\n" + "=" * 70)
    print("TEST 6: Neo4j Constraint Generation")
    print("=" * 70)

    facet_path = project_root / "Facets" / "facet_registry_master.json"
    rel_path = project_root / "Relationships" / "relationship_types_registry_master.csv"

    try:
        loader = RegistryLoader(facet_path, rel_path)
        generator = Neo4jConstraintGenerator(loader)

        # Generate all constraints
        constraints_doc = generator.generate_all_constraints()
        constraint_lines = len(constraints_doc.split("\n"))

        print(f"\n✓ Generated Cypher constraints document")
        print(f"  Total lines: {constraint_lines}")

        # Get individual statements
        statements = generator.get_constraint_statements()
        print(f"  Constraint statements: {len(statements)}")

        # Show first few
        print(f"\nFirst 3 constraint statements:")
        for i, stmt in enumerate(statements[:3], 1):
            print(f"  {i}. {stmt[:70]}...")

        # Validation queries
        validation_doc = generator.generate_validation_cypher()
        validation_lines = len(validation_doc.split("\n"))
        print(f"\n✓ Generated Cypher validation queries")
        print(f"  Total lines: {validation_lines}")

        # Write to files
        output_dir = project_root / "Cypher" / "schema"
        output_dir.mkdir(parents=True, exist_ok=True)

        constraints_file = output_dir / "constraints_chrystallum_generated.cypher"
        with open(constraints_file, "w") as f:
            f.write(constraints_doc)

        validation_file = output_dir / "validation_chrystallum_generated.cypher"
        with open(validation_file, "w") as f:
            f.write(validation_doc)

        print(f"\n✓ Wrote schema files:")
        print(f"  {constraints_file.relative_to(project_root)}")
        print(f"  {validation_file.relative_to(project_root)}")

        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("CHRYSTALLUM MODELS VALIDATION TEST SUITE")
    print("=" * 70)

    results = {
        "Registry Loading": test_registry_loading(),
        "Facet Validation": test_facet_validation(),
        "Relationship Validation": test_relationship_validation(),
        "Claim Validation": test_claim_validation(),
        "Facet Assessment": test_facet_assessment(),
        "Neo4j Constraints": test_neo4j_constraints(),
    }

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
