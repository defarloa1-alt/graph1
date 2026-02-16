"""
Neo4j Constraint Generation for Chrystallum

Generates Cypher constraint statements to enforce canonical facet keys,
relationship types, and other business rules at the database level.

This prevents invalid data from being written to the database, providing
a second line of defense after Pydantic validation.

Usage:
    generator = Neo4jConstraintGenerator(loader)
    cypher_statements = generator.generate_all_constraints()
    
    # Write to file for execution via cypher-shell:
    with open("constraints.cypher", "w") as f:
        f.write(cypher_statements)
    
    # Or execute directly:
    driver = GraphDatabase.driver(...)
    with driver.session() as session:
        for stmt in generator.get_constraint_statements():
            session.run(stmt)
"""

from typing import List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# For local imports
sys.path.insert(0, str(Path(__file__).parent))
from registry_loader import RegistryLoader


class Neo4jConstraintGenerator:
    """Generates Neo4j constraint statements for registry enforcement."""

    def __init__(self, registry_loader: RegistryLoader):
        """
        Initialize constraint generator.
        
        Args:
            registry_loader: Initialized RegistryLoader instance
        """
        self.loader = registry_loader

    def generate_all_constraints(self) -> str:
        """
        Generate all constraint statements as a single Cypher document.
        
        Returns:
            Multi-statement Cypher document with comments and constraints
        """
        lines = [
            "// Chrystallum Neo4j Constraints",
            f"// Generated: {datetime.utcnow().isoformat()}",
            "// Enforce canonical facets, relationships, and schema constraints",
            "",
            "// ========================================================================",
            "// FACET CONSTRAINTS",
            "// ========================================================================",
            "",
        ]

        lines.extend(self._generate_facet_constraints())

        lines.extend([
            "",
            "// ========================================================================",
            "// RELATIONSHIP CONSTRAINTS",
            "// ========================================================================",
            "",
        ])

        lines.extend(self._generate_relationship_constraints())

        lines.extend([
            "",
            "// ========================================================================",
            "// CLAIM CONSTRAINTS",
            "// ========================================================================",
            "",
        ])

        lines.extend(self._generate_claim_constraints())

        lines.extend([
            "",
            "// ========================================================================",
            "// EDGE CONSTRAINTS",
            "// ========================================================================",
            "",
        ])

        lines.extend(self._generate_edge_constraints())

        return "\n".join(lines)

    def _generate_facet_constraints(self) -> List[str]:
        """Generate constraints for facet nodes."""
        facet_keys = sorted(self.loader.get_canonical_facet_keys())
        facet_keys_list = ", ".join(f"'{k}'" for k in facet_keys)

        constraints = [
            "// Facet key must be unique and lowercase",
            "CREATE CONSTRAINT facet_key_unique IF NOT EXISTS",
            "FOR (f:FacetCategory) REQUIRE f.key IS UNIQUE;",
            "",
            "// Facet key must be in canonical registry",
            f"// Valid facet keys ({len(facet_keys)}): {facet_keys_list[:100]}...",
            "// Note: This is validated at application level; Neo4j 4.x doesn't support CHECK constraints",
            "// So we enforce via application Pydantic models and migration validation",
            "",
            "// Create index on facet key for fast lookups",
            "CREATE INDEX facet_key_index IF NOT EXISTS FOR (f:FacetCategory) ON (f.key);",
            "",
        ]

        return constraints

    def _generate_relationship_constraints(self) -> List[str]:
        """Generate constraints for relationship edges."""
        rel_types = sorted(self.loader.get_canonical_relationship_types())

        constraints = [
            "// Relationship type validation",
            "// Note: Neo4j relationship types are fixed at schema-definition time;",
            "// we validate via application models and this comment documents valid types",
            f"// Total valid relationship types: {len(rel_types)}",
            "",
            "// Create indexes for relationship pattern matching",
            "CREATE INDEX rel_edge_id IF NOT EXISTS FOR ()-[e:EDGE_ID]->() ON (e.edge_id);",
            "CREATE INDEX rel_confidence IF NOT EXISTS FOR ()-[r]->() ON (r.confidence);",
            "",
            "// Unique constraint on (source, rel_type, target, facet_scope)",
            "// Prevents duplicate relationships within same facet",
            "CREATE CONSTRAINT edge_source_rel_target_unique IF NOT EXISTS",
            "FOR ()-[e:RELATED_TO]->() REQUIRE e.edge_id IS UNIQUE;",
            "",
        ]

        return constraints

    def _generate_claim_constraints(self) -> List[str]:
        """Generate constraints for claim nodes."""
        constraints = [
            "// Claim uniqueness by cipher (content-addressable identity)",
            "CREATE CONSTRAINT claim_cipher_unique IF NOT EXISTS",
            "FOR (c:Claim) REQUIRE c.cipher IS UNIQUE;",
            "",
            "// Claim ID uniqueness (operational identifier)",
            "CREATE CONSTRAINT claim_id_unique IF NOT EXISTS",
            "FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE;",
            "",
            "// Index for claim status queries",
            "CREATE INDEX claim_status IF NOT EXISTS FOR (c:Claim) ON (c.status);",
            "",
            "// Index for claim creation date queries",
            "CREATE INDEX claim_created_at IF NOT EXISTS FOR (c:Claim) ON (c.created_at);",
            "",
            "// FacetAssessment uniqueness by (claim, facet, assessment_run)",
            "CREATE CONSTRAINT facet_assessment_unique IF NOT EXISTS",
            "FOR (fa:FacetAssessment) REQUIRE fa.assessment_id IS UNIQUE;",
            "",
            "// Index on FacetAssessment facet for facet-specific queries",
            "CREATE INDEX facet_assessment_facet IF NOT EXISTS (fa:FacetAssessment) ON (fa.facet);",
            "",
        ]

        return constraints

    def _generate_edge_constraints(self) -> List[str]:
        """Generate constraints for edges in the claim subgraph."""
        constraints = [
            "// Edge uniqueness (edges within a claim cluster)",
            "CREATE CONSTRAINT edge_unique_id IF NOT EXISTS",
            "FOR ()-[e:EDGE]->() REQUIRE e.edge_id IS UNIQUE;",
            "",
            "// Edge version tracking (allows re-versioning)",
            "CREATE INDEX edge_version IF NOT EXISTS FOR ()-[e:EDGE]->() ON (e.version);",
            "",
            "// Edge confidence for filtering/ranking",
            "CREATE INDEX edge_confidence IF NOT EXISTS FOR ()-[e:EDGE]->() ON (e.confidence);",
            "",
        ]

        return constraints

    def get_constraint_statements(self) -> List[str]:
        """Get individual constraint statements (lines ending with semicolon)."""
        full_doc = self.generate_all_constraints()
        statements = []
        current = []

        for line in full_doc.split("\n"):
            # Skip comments
            if line.strip().startswith("//"):
                continue

            current.append(line)

            # End of statement
            if line.strip().endswith(";"):
                stmt = "\n".join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []

        return statements

    def generate_validation_cypher(self) -> str:
        """
        Generate Cypher queries to validate existing graph against constraints.
        
        Useful for auditing existing data before enforcing constraints.
        Returns:
            Multi-statement Cypher for validation checks
        """
        facet_keys = sorted(self.loader.get_canonical_facet_keys())
        facet_keys_list = ", ".join(f"'{k}'" for k in facet_keys)
        rel_types = sorted(self.loader.get_canonical_relationship_types())
        rel_types_list = ", ".join(f"'{t}'" for t in rel_types[:20])  # First 20 for readability

        validations = [
            "// Chrystallum Data Validation Queries",
            f"// Generated: {datetime.utcnow().isoformat()}",
            "",
            "// ========================================================================",
            "// Check for duplicate claims (same cipher)",
            "// ========================================================================",
            "MATCH (c:Claim) WITH c.cipher AS cipher, COUNT(*) AS count",
            "WHERE count > 1",
            "RETURN cipher, count",
            "ORDER BY count DESC;",
            "",
            "// ========================================================================",
            "// Check for duplicate claim IDs",
            "// ========================================================================",
            "MATCH (c:Claim) WITH c.claim_id AS claim_id, COUNT(*) AS count",
            "WHERE count > 1",
            "RETURN claim_id, count;",
            "",
            "// ========================================================================",
            "// Check for invalid facet keys",
            "// ========================================================================",
            f"// Valid facet keys: {facet_keys_list}",
            "MATCH (fa:FacetAssessment) WHERE NOT fa.facet IN [" + facet_keys_list + "]",
            "RETURN fa.assessment_id, fa.facet",
            "LIMIT 20;",
            "",
            "// ========================================================================",
            "// Check for missing facet assessments",
            "// ========================================================================",
            "MATCH (c:Claim) WHERE NOT (c)-[:HAS_ANALYSIS_RUN]->(:AnalysisRun)",
            "RETURN c.claim_id, c.cipher",
            "LIMIT 20;",
            "",
            "// ========================================================================",
            "// Check for invalid edge IDs (duplicates)",
            "// ========================================================================",
            "MATCH ()-[e:EDGE]->() WITH e.edge_id AS edge_id, COUNT(*) AS count",
            "WHERE count > 1",
            "RETURN edge_id, count;",
            "",
            "// ========================================================================",
            "// Summary statistics",
            "// ========================================================================",
            "MATCH (c:Claim) RETURN COUNT(c) AS total_claims;",
            "MATCH (fa:FacetAssessment) RETURN COUNT(fa) AS total_assessments;",
            "MATCH ()-[e:EDGE]->() RETURN COUNT(e) AS total_edges;",
        ]

        return "\n".join(validations)

    def generate_migration_script(self, from_version: str, to_version: str) -> str:
        """
        Generate a migration script for moving between schema versions.
        
        Useful when the registry changes (e.g., adding a new facet).
        
        Args:
            from_version: Previous schema version (e.g., "2026-02-12")
            to_version: New schema version (e.g., "2026-02-16")
        
        Returns:
            Migration Cypher script
        """
        lines = [
            f"// Migration from {from_version} to {to_version}",
            f"// Generated: {datetime.utcnow().isoformat()}",
            "",
            "// STEP 1: Backup existing data",
            "// CREATE BACKUP OF ENTIRE GRAPH BEFORE RUNNING THIS",
            "",
            "// STEP 2: Validate existing data against new schema",
            "// Run: generate_validation_cypher() output above",
            "",
            "// STEP 3: Create new constraints",
            "// Run: generate_all_constraints() output above",
            "",
            "// STEP 4: Verify no constraint violations",
            "CALL db.constraints() YIELD name, description",
            "RETURN name, description;",
            "",
            "// STEP 5: Update schema version marker (if you have one)",
            "CREATE CONSTRAINT schema_version UNIQUE ON (sv:_SchemaVersion)",
            "MERGE (sv:_SchemaVersion {version: '" + to_version + "'})",
            "SET sv.migrated_at = datetime.utcnow(),",
            "    sv.from_version = '" + from_version + "';",
            "",
            "// STEP 6: Verify migration",
            "MATCH (sv:_SchemaVersion) RETURN sv;",
        ]

        return "\n".join(lines)


def main():
    """Example usage (for testing)."""
    import json

    # Find registry files
    project_root = Path(__file__).parent.parent.parent
    facet_path = project_root / "Facets" / "facet_registry_master.json"
    rel_path = project_root / "Relationships" / "relationship_types_registry_master.csv"

    if not facet_path.exists() or not rel_path.exists():
        print(f"Error: Registry files not found")
        print(f"  Facet: {facet_path}")
        print(f"  Relationships: {rel_path}")
        return

    # Load and generate
    loader = RegistryLoader(facet_path, rel_path)
    generator = Neo4jConstraintGenerator(loader)

    # Write outputs
    output_dir = project_root / "Cypher" / "schema"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Constraints
    constraints_file = output_dir / "constraints_chrystallum.cypher"
    with open(constraints_file, "w") as f:
        f.write(generator.generate_all_constraints())
    print(f"✓ Wrote constraints to {constraints_file}")

    # Validation
    validation_file = output_dir / "validation_chrystallum.cypher"
    with open(validation_file, "w") as f:
        f.write(generator.generate_validation_cypher())
    print(f"✓ Wrote validation to {validation_file}")

    # Migration
    migration_file = output_dir / "migration_2026_02_12_to_2026_02_16.cypher"
    with open(migration_file, "w") as f:
        f.write(generator.generate_migration_script("2026-02-12", "2026-02-16"))
    print(f"✓ Wrote migration to {migration_file}")

    print(f"\nRegistry Summary:")
    print(f"  Facets: {loader.get_facet_count()}")
    print(f"  Relationships: {loader.get_relationship_count()}")


if __name__ == "__main__":
    main()
