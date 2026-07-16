// ============================================================
// MIGRATION: Chrystallum Consolidation
// File: scripts/migrations/migration_chrystallum_consolidate.cypher
// Purpose: Merge multiple Chrystallum nodes into one canonical root.
//          Use id: 'CHRYSTALLUM_ROOT' as the unique key.
// Spec: docs/CHRYSTALLUM_SUBGRAPH_SPEC.md
// ============================================================

// ── 0. Ensure canonical node exists ───────────────────────────────────────────
MERGE (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
SET canon.label = 'Chrystallum',
    canon.name = 'Chrystallum Knowledge Graph',
    canon.type = 'knowledge_graph_root',
    canon.version = '1.0',
    canon.description = 'Root node of the Chrystallum federated knowledge graph';

// ── 1. Reattach outgoing relationships from duplicates to canonical ───────────
//     (Run per relationship type; MERGE avoids duplicate edges)

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_FACET_CLUSTER]->(target)
MERGE (canon)-[:HAS_FACET_CLUSTER]->(target);

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_FEDERATION_CLUSTER]->(target)
MERGE (canon)-[:HAS_FEDERATION_CLUSTER]->(target);

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_SUBJECT_CONCEPT_ROOT]->(target)
MERGE (canon)-[:HAS_SUBJECT_CONCEPT_ROOT]->(target);

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_FEDERATION]->(target)
MERGE (canon)-[:HAS_FEDERATION]->(target);

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_BIBLIOGRAPHY]->(target)
MERGE (canon)-[:HAS_BIBLIOGRAPHY]->(target);

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_SELF_DESCRIPTION]->(target)
MERGE (canon)-[:HAS_SELF_DESCRIPTION]->(target);

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_FACET_ROOT]->(target)
MERGE (canon)-[:HAS_FACET_ROOT]->(target);

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_FEDERATION_ROOT]->(target)
MERGE (canon)-[:HAS_FEDERATION_ROOT]->(target);

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_SUBCLUSTER]->(target)
MERGE (canon)-[:HAS_SUBCLUSTER]->(target);

MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
MATCH (canon:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (dup)-[r:HAS_ENTITY_ROOT]->(target)
MERGE (canon)-[:HAS_ENTITY_ROOT]->(target);

// ── 2. Reattach incoming relationships (if any) ──────────────────────────────
//     Incoming rels to Chrystallum are uncommon. If duplicates have incoming
//     edges, use APOC apoc.refactor.mergeNodes or migrate manually per rel type.

// ── 3. Delete duplicate Chrystallum nodes ─────────────────────────────────────
MATCH (dup:Chrystallum) WHERE dup.id IS NULL OR dup.id <> 'CHRYSTALLUM_ROOT'
DETACH DELETE dup;

// ── 4. Verification (run separately) ─────────────────────────────────────────
// MATCH (c:Chrystallum) RETURN count(c) AS chrystallum_count;
// Expected: 1
