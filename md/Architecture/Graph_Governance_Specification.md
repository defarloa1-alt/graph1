
# SCHEMA GOVERNANCE SPECIFICATION

## Purpose
This document defines how the Neo4j knowledge graph schema is applied, validated, and maintained.

## Three-Layer Architecture

### Layer 1: Canonical Schema (Immutable CSVs)
- JSON/chrystallum_schema.json (121 entity types + Q-IDs)
- relations/neo4j_entity_hierarchy.csv (248 parent-child relationships)
- Relationships/relationship_types_registry_master.csv (235 relationships + P-properties)
- Source of truth for schema enforcement
- Changes require review and approval
- **Last Updated:** 2025-12-10

### Layer 2: Governance Layer (Human-Readable Specification)
- Entity type hierarchy with preference ordering
- Relationship directionality rules
- Type validation rules
- Bidirectionality guidelines
- Confidence scoring rubrics

### Layer 3: Operational Tools (Query & Code Patterns)
- cypher_template_library.json - Query blueprints
- llm_system_prompt.txt - LLM extraction guidance
- validation_code.py - Type validation functions

## Enforcement Rules

### Type Specificity
Rule: Use the MOST SPECIFIC applicable type.
- If context allows Battle (Q178561), use it instead of Event (Q1656682)
- If context allows Bishop (Q29182), use it instead of Religious Office
- Only use parent type if specific type cannot be determined with confidence ≥ 0.80

### Bidirectionality
Rule: Relationships are stored bidirectionally ONLY when both directions are explicitly defined.
- MEMBER_OF and HAS_MEMBER are both defined → both can be used
- Only one direction in source → do not invent the inverse
- Query layer can use either direction via relationship specification

### Wikidata Grounding
Rule: All entities and relationships must have Wikidata identifiers.
- Entity must have Q-ID or be flagged for addition to Wikidata
- Relationship must have P-property or be marked as domain-specific
- Missing mappings require manual review before ingestion

### Confidence Thresholds
- 0.95+: Auto-ingest, no review needed
- 0.80-0.94: Auto-ingest with provenance logging
- 0.70-0.79: Flag for review, hold pending approval
- <0.70: Require manual verification before ingestion

## Hierarchy Validation

For each entity type, confirm:
1. Parent type exists in schema
2. Child type exists in schema
3. No circular relationships
4. Depth is reasonable (max 4 levels recommended)

## Adding New Types

Process for adding new entity or relationship types:
1. Verify type is not already in schema (including hierarchy)
2. Find Wikidata Q-ID or P-property
3. Determine parent type from hierarchy
4. Add to appropriate CSV with documentation
5. Update hierarchy if introducing new parent
6. Update LLM system prompt
7. Add Cypher templates if new relationship
8. Publish updated schema version

## Query Compliance

All Neo4j queries must:
1. Use only defined relationship types (from bidirectional set)
2. Use only defined entity types (respecting hierarchy)
3. Include direction specification (forward/inverse/symmetric)
4. Log Wikidata properties used
5. Track confidence scores in provenance

## Versioning

Schema versions follow MAJOR.MINOR.PATCH:
- MAJOR: Breaking changes (entity removal, relationship redefinition)
- MINOR: Non-breaking additions (new types, new relationships)
- PATCH: Documentation, clarification, hierarchy reordering

Current Version: 3.3.0
Last Updated: 2025-12-10
Canonical Relationships: 235 (from Relationships/relationship_types_registry_master.csv)
Canonical Entities: 121 (from JSON/chrystallum_schema.json)
Approval: [Schema Governance Board]
