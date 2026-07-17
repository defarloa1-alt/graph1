// ═══════════════════════════════════════════════════════════════
// Phase 1: Multi-Agent Claim Schema (ADR 022)
// 
// This schema implements the Canonical Entity + Facet-Scoped Claims
// architecture with proper constraints and indexes.
//
// Usage:
//   Run in Neo4j Browser or via neo4j-admin
// ═══════════════════════════════════════════════════════════════

// ───────────────────────────────────────────────────────────────
// CONSTRAINTS (Uniqueness & Existence)
// ───────────────────────────────────────────────────────────────

// Entity cipher uniqueness (Tier 1) - CRITICAL for deduplication
CREATE CONSTRAINT entity_cipher_unique IF NOT EXISTS
FOR (e) REQUIRE e.entity_cipher IS UNIQUE;

// Agent ID uniqueness
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS
FOR (a:Agent) REQUIRE a.agent_id IS UNIQUE;

// QID uniqueness (where present) - prevents duplicate Wikidata entities
CREATE CONSTRAINT entity_qid_unique IF NOT EXISTS
FOR (e) REQUIRE e.qid IS UNIQUE;

// ───────────────────────────────────────────────────────────────
// INDEXES (Query Performance)
// ───────────────────────────────────────────────────────────────

// Entity type index (for type-specific queries)
CREATE INDEX entity_type_idx IF NOT EXISTS
FOR (e) ON (e.entity_type);

// Entity label index (for label search)
CREATE INDEX entity_label_idx IF NOT EXISTS
FOR (e) ON (e.label);

// Agent facet index (for facet-specific agent queries)
CREATE INDEX agent_facet_idx IF NOT EXISTS
FOR (a:Agent) ON (a.facet);

// Claim facet index (for facet-filtered claim queries)
CREATE INDEX claim_facet_idx IF NOT EXISTS
FOR ()-[c:ASSERTS]-() ON (c.facet);

// Claim status index (for status-based queries: TBD, CONFIRMED, CONTESTED)
CREATE INDEX claim_status_idx IF NOT EXISTS
FOR ()-[c:ASSERTS]-() ON (c.status);

// Claim confidence index (for high-confidence filtering)
CREATE INDEX claim_confidence_idx IF NOT EXISTS
FOR ()-[c:ASSERTS]-() ON (c.confidence);

// Claim predicate index (for predicate-specific queries)
CREATE INDEX claim_predicate_idx IF NOT EXISTS
FOR ()-[c:ASSERTS]-() ON (c.predicate);

// Created timestamp index (for temporal queries)
CREATE INDEX entity_created_at_idx IF NOT EXISTS
FOR (e) ON (e.created_at);

// ───────────────────────────────────────────────────────────────
// RELATIONSHIP TYPES
// ───────────────────────────────────────────────────────────────

// Relationship types are defined implicitly by usage:
// - :ASSERTS (Agent → Entity) - facet-scoped claim
// - :REVIEWED (Agent → :ASSERTS edge) - Phase 2 peer review
// - :CONFLICTS_WITH (Claim → Claim) - explicit conflict (Phase 3, optional)

// ───────────────────────────────────────────────────────────────
// VALIDATION QUERIES
// ───────────────────────────────────────────────────────────────

// List all constraints
SHOW CONSTRAINTS;

// List all indexes
SHOW INDEXES;

// ───────────────────────────────────────────────────────────────
// EXAMPLE QUERIES (For Testing)
// ───────────────────────────────────────────────────────────────

// Find all entities with multiple facet claims (multi-perspective entities)
// MATCH (e)<-[c:ASSERTS]-(a:Agent)
// WITH e, count(DISTINCT c.facet) as facet_count
// WHERE facet_count >= 2
// RETURN e.label, e.entity_cipher, facet_count
// ORDER BY facet_count DESC
// LIMIT 10;

// Find claims by specific facet
// MATCH (e)<-[c:ASSERTS {facet: 'MILITARY'}]-(a:Agent)
// RETURN e.label, c.predicate, c.confidence, c.status
// ORDER BY c.confidence DESC
// LIMIT 10;

// Find contested claims (when Phase 2 is implemented)
// MATCH (e)<-[c:ASSERTS {status: 'CONTESTED'}]-(a:Agent)
// RETURN e.label, e.entity_cipher, c.facet, c.predicate
// LIMIT 10;

// Find high-confidence claims awaiting review
// MATCH (e)<-[c:ASSERTS {status: 'TBD'}]-(a:Agent)
// WHERE c.confidence >= 0.80
// RETURN e.label, c.facet, c.predicate, c.confidence
// ORDER BY c.confidence DESC
// LIMIT 10;

// Cross-facet claim analysis for a specific entity
// MATCH (e {qid: 'Q40979'})<-[c:ASSERTS]-(a:Agent)
// RETURN 
//   e.label as entity,
//   c.facet as perspective,
//   c.predicate as interpretation,
//   c.confidence as confidence,
//   c.status as status
// ORDER BY c.confidence DESC;

// ───────────────────────────────────────────────────────────────
// SCHEMA VERIFICATION
// ───────────────────────────────────────────────────────────────

// Verify entity cipher constraint exists
// SHOW CONSTRAINTS WHERE name = 'entity_cipher_unique';

// Count entities by type
// MATCH (e)
// RETURN e.entity_type as type, count(*) as count
// ORDER BY count DESC;

// Count claims by facet
// MATCH ()-[c:ASSERTS]->()
// RETURN c.facet as facet, count(*) as claims
// ORDER BY claims DESC;

// Count claims by status
// MATCH ()-[c:ASSERTS]->()
// RETURN c.status as status, count(*) as claims
// ORDER BY claims DESC;

// ═══════════════════════════════════════════════════════════════
// END OF SCHEMA
// ═══════════════════════════════════════════════════════════════
