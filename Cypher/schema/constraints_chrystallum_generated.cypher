// Chrystallum Neo4j Constraints
// Generated: 2026-02-16T16:43:57.887312
// Enforce canonical facets, relationships, and schema constraints

// ========================================================================
// FACET CONSTRAINTS
// ========================================================================

// Facet key must be unique and lowercase
CREATE CONSTRAINT facet_key_unique IF NOT EXISTS
FOR (f:FacetCategory) REQUIRE f.key IS UNIQUE;

// Facet key must be in canonical registry
// Valid facet keys (18): 'archaeological', 'artistic', 'biographic', 'communication', 'cultural', 'demographic', 'diplomatic'...
// Note: This is validated at application level; Neo4j 4.x doesn't support CHECK constraints
// So we enforce via application Pydantic models and migration validation

// Create index on facet key for fast lookups
CREATE INDEX facet_key_index IF NOT EXISTS FOR (f:FacetCategory) ON (f.key);


// ========================================================================
// RELATIONSHIP CONSTRAINTS
// ========================================================================

// Relationship type validation
// Note: Neo4j relationship types are fixed at schema-definition time;
// we validate via application models and this comment documents valid types
// Total valid relationship types: 310

// Create indexes for relationship pattern matching
CREATE INDEX rel_edge_id IF NOT EXISTS FOR ()-[e:EDGE_ID]->() ON (e.edge_id);
CREATE INDEX rel_confidence IF NOT EXISTS FOR ()-[r]->() ON (r.confidence);

// Unique constraint on (source, rel_type, target, facet_scope)
// Prevents duplicate relationships within same facet
CREATE CONSTRAINT edge_source_rel_target_unique IF NOT EXISTS
FOR ()-[e:RELATED_TO]->() REQUIRE e.edge_id IS UNIQUE;


// ========================================================================
// CLAIM CONSTRAINTS
// ========================================================================

// Claim uniqueness by cipher (content-addressable identity)
CREATE CONSTRAINT claim_cipher_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.cipher IS UNIQUE;

// Claim ID uniqueness (operational identifier)
CREATE CONSTRAINT claim_id_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE;

// Index for claim status queries
CREATE INDEX claim_status IF NOT EXISTS FOR (c:Claim) ON (c.status);

// Index for claim creation date queries
CREATE INDEX claim_created_at IF NOT EXISTS FOR (c:Claim) ON (c.created_at);

// FacetAssessment uniqueness by (claim, facet, assessment_run)
CREATE CONSTRAINT facet_assessment_unique IF NOT EXISTS
FOR (fa:FacetAssessment) REQUIRE fa.assessment_id IS UNIQUE;

// Index on FacetAssessment facet for facet-specific queries
CREATE INDEX facet_assessment_facet IF NOT EXISTS (fa:FacetAssessment) ON (fa.facet);


// ========================================================================
// EDGE CONSTRAINTS
// ========================================================================

// Edge uniqueness (edges within a claim cluster)
CREATE CONSTRAINT edge_unique_id IF NOT EXISTS
FOR ()-[e:EDGE]->() REQUIRE e.edge_id IS UNIQUE;

// Edge version tracking (allows re-versioning)
CREATE INDEX edge_version IF NOT EXISTS FOR ()-[e:EDGE]->() ON (e.version);

// Edge confidence for filtering/ranking
CREATE INDEX edge_confidence IF NOT EXISTS FOR ()-[e:EDGE]->() ON (e.confidence);
