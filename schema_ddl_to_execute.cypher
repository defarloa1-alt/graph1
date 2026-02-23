// CHRYSTALLUM NEO4J SCHEMA DDL
// Execute in Neo4j Browser in sections

// SECTION 1: TIER 1 CONSTRAINTS (Entity) - 4 constraints
CREATE CONSTRAINT entity_cipher_exists IF NOT EXISTS FOR (n:Entity) REQUIRE n.entity_cipher IS NOT NULL;
CREATE CONSTRAINT entity_type_exists IF NOT EXISTS FOR (n:Entity) REQUIRE n.entity_type IS NOT NULL;

// SECTION 2: TIER 1 INDEXES (Entity) - 2 indexes  
CREATE INDEX entity_type_cipher_idx IF NOT EXISTS FOR (n:Entity) ON (n.entity_type, n.entity_cipher);
CREATE INDEX entity_namespace_idx IF NOT EXISTS FOR (n:Entity) ON (n.namespace);

// SECTION 3: TIER 2 CONSTRAINTS (FacetedEntity) - 6 constraints
CREATE CONSTRAINT faceted_cipher_unique IF NOT EXISTS FOR (n:FacetedEntity) REQUIRE n.faceted_cipher IS UNIQUE;
CREATE CONSTRAINT faceted_composite_unique IF NOT EXISTS FOR (n:FacetedEntity) REQUIRE (n.entity_cipher, n.facet_id, n.subjectconcept_id) IS UNIQUE;
CREATE CONSTRAINT faceted_entity_cipher_exists IF NOT EXISTS FOR (n:FacetedEntity) REQUIRE n.entity_cipher IS NOT NULL;
CREATE CONSTRAINT faceted_facet_id_exists IF NOT EXISTS FOR (n:FacetedEntity) REQUIRE n.facet_id IS NOT NULL;
CREATE CONSTRAINT faceted_subjectconcept_exists IF NOT EXISTS FOR (n:FacetedEntity) REQUIRE n.subjectconcept_id IS NOT NULL;

// SECTION 4: TIER 2 INDEXES (FacetedEntity) - 3 indexes
CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS FOR (n:FacetedEntity) ON (n.entity_cipher, n.facet_id);
CREATE INDEX faceted_subj_facet_idx IF NOT EXISTS FOR (n:FacetedEntity) ON (n.subjectconcept_id, n.facet_id);
CREATE INDEX faceted_subj_idx IF NOT EXISTS FOR (n:FacetedEntity) ON (n.subjectconcept_id);

// SECTION 5: TIER 3 CONSTRAINTS (FacetClaim) - 4 constraints
CREATE CONSTRAINT claim_cipher_unique IF NOT EXISTS FOR (c:FacetClaim) REQUIRE c.cipher IS UNIQUE;
CREATE CONSTRAINT claim_subject_exists IF NOT EXISTS FOR (c:FacetClaim) REQUIRE c.subject_entity_cipher IS NOT NULL;
CREATE CONSTRAINT claim_facet_exists IF NOT EXISTS FOR (c:FacetClaim) REQUIRE c.facet_id IS NOT NULL;
CREATE CONSTRAINT claim_analysis_layer_exists IF NOT EXISTS FOR (c:FacetClaim) REQUIRE c.analysis_layer IS NOT NULL;

// SECTION 6: TIER 3 INDEXES (FacetClaim) - 10 indexes
CREATE INDEX claim_entity_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.subject_entity_cipher);
CREATE INDEX claim_entity_facet_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.subject_entity_cipher, c.facet_id);
CREATE INDEX claim_subj_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.subjectconcept_cipher);
CREATE INDEX claim_analysis_layer_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.analysis_layer);
CREATE INDEX claim_confidence_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.confidence);
CREATE INDEX claim_wikidata_triple_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.subject_entity_cipher, c.wikidata_pid, c.object_qid);
CREATE INDEX claim_temporal_start_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p580_normalized);
CREATE INDEX claim_temporal_end_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p582_normalized);
CREATE INDEX claim_location_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p276_qid);
CREATE INDEX claim_ordinal_idx IF NOT EXISTS FOR (c:FacetClaim) ON (c.qualifier_p1545_ordinal);

// SECTION 7: TEMPORAL ANCHOR CONSTRAINTS - 3 constraints
CREATE CONSTRAINT temporal_start_year_exists IF NOT EXISTS FOR (n:TemporalAnchor) REQUIRE n.temporal_start_year IS NOT NULL;
CREATE CONSTRAINT temporal_end_year_exists IF NOT EXISTS FOR (n:TemporalAnchor) REQUIRE n.temporal_end_year IS NOT NULL;
CREATE CONSTRAINT temporal_scope_exists IF NOT EXISTS FOR (n:TemporalAnchor) REQUIRE n.temporal_scope IS NOT NULL;

// SECTION 8: TEMPORAL ANCHOR INDEXES - 3 indexes
CREATE INDEX temporal_range_idx IF NOT EXISTS FOR (n:TemporalAnchor) ON (n.temporal_start_year, n.temporal_end_year);
CREATE INDEX temporal_nesting_idx IF NOT EXISTS FOR (n:TemporalAnchor) ON (n.temporal_start_year);
CREATE INDEX temporal_calendar_idx IF NOT EXISTS FOR (n:TemporalAnchor) ON (n.temporal_calendar);

// Total: 17 constraints + 18 indexes = 35 DDL statements
