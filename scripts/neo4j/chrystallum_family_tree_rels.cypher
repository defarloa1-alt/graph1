// ============================================================================
// Chrystallum Family Tree Relationship Types — 2026-03-03
// ============================================================================
// PURPOSE: Register PARENT_OF and STEPPARENT_OF in SYS_RelationshipType
//          before person harvest executor writes edges.
// BLOCKING: Run this before python -m scripts.person_harvest.orchestrator
// IDEMPOTENT: All statements use MERGE
// ============================================================================

// PARENT_OF — gender-neutral parent→child (P40 fallback when P21 unknown)
MERGE (rt:SYS_RelationshipType {name: 'PARENT_OF', rel_type: 'PARENT_OF'})
SET rt.domain = 'Person',
    rt.range = 'Person',
    rt.source = 'ADR-007',
    rt.added_date = '2026-03-03',
    rt.description = 'Parent of child. Gender-neutral. Used when P40 (child) is present but parent P21 (sex) is unknown. Wikidata P40.',
    rt.wikidata_pid = 'P40',
    rt.symmetric = false;

// STEPPARENT_OF — stepparent→stepchild (Wikidata P3448)
MERGE (rt:SYS_RelationshipType {name: 'STEPPARENT_OF', rel_type: 'STEPPARENT_OF'})
SET rt.domain = 'Person',
    rt.range = 'Person',
    rt.source = 'ADR-007',
    rt.added_date = '2026-03-03',
    rt.description = 'Stepparent relationship. Derived from Wikidata P3448 (stepparent).',
    rt.wikidata_pid = 'P3448',
    rt.symmetric = false;

// Bootstrap: Create at least one relationship of each type so Neo4j schema
// recognizes them (fixes "relationship type does not exist" warning in MATCH).
MERGE (bootstrap:SYS_SchemaBootstrap {id: 'family_tree_rels'})
WITH bootstrap
MERGE (bootstrap)-[:PARENT_OF {bootstrap: true}]->(bootstrap)
WITH bootstrap
MERGE (bootstrap)-[:STEPPARENT_OF {bootstrap: true}]->(bootstrap);

// ============================================================================
// VERIFICATION
// ============================================================================
// MATCH (rt:SYS_RelationshipType) WHERE rt.name IN ('PARENT_OF', 'STEPPARENT_OF')
// RETURN rt.name, rt.domain, rt.range, rt.wikidata_pid
// Expected: 2 rows
