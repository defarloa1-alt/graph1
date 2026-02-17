// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: INDEXES FOR QUERY PERFORMANCE
// ============================================================================
// File: 02_schema_indexes.cypher
// Purpose: Define optimal indexes for common query patterns
// Created: 2026-02-13
// Status: Production Schema
// ============================================================================

// ============================================================================
// CANONICAL LABEL LOCK (2026-02-14)
// ============================================================================
// Canonical first-class labels:
//   SubjectConcept, Human, Gens, Praenomen, Cognomen, Event, Place, Period,
//   Dynasty, Institution, LegalRestriction, Claim, Organization, Year
//
// Legacy mapping (must not be materialized as active labels):
//   Subject -> SubjectConcept
//   Concept -> SubjectConcept
//   Person  -> Human
//   Communication -> facet/domain axis (not first-class node label)

// ============================================================================
// PRIMARY KEY INDEXES (used heavily in lookups & joins)
// ============================================================================

// Entity ID lookups (universal across all entity types)
CREATE INDEX entity_id_index IF NOT EXISTS FOR (e:Entity) ON (e.entity_id);
CREATE INDEX human_entity_id_index IF NOT EXISTS FOR (h:Human) ON (h.entity_id);
CREATE INDEX place_entity_id_index IF NOT EXISTS FOR (p:Place) ON (p.entity_id);
CREATE INDEX event_entity_id_index IF NOT EXISTS FOR (e:Event) ON (e.entity_id);
CREATE INDEX period_entity_id_index IF NOT EXISTS FOR (p:Period) ON (p.entity_id);
CREATE INDEX organization_entity_id_index IF NOT EXISTS FOR (o:Organization) ON (o.entity_id);
CREATE INDEX year_entity_id_index IF NOT EXISTS FOR (y:Year) ON (y.entity_id);

// Canonical ID hash lookups
CREATE INDEX subject_concept_id_hash_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.id_hash);
CREATE INDEX human_id_hash_index IF NOT EXISTS FOR (h:Human) ON (h.id_hash);
CREATE INDEX gens_id_hash_index IF NOT EXISTS FOR (g:Gens) ON (g.id_hash);
CREATE INDEX praenomen_id_hash_index IF NOT EXISTS FOR (p:Praenomen) ON (p.id_hash);
CREATE INDEX cognomen_id_hash_index IF NOT EXISTS FOR (c:Cognomen) ON (c.id_hash);
CREATE INDEX event_id_hash_index IF NOT EXISTS FOR (e:Event) ON (e.id_hash);
CREATE INDEX place_id_hash_index IF NOT EXISTS FOR (p:Place) ON (p.id_hash);
CREATE INDEX period_id_hash_index IF NOT EXISTS FOR (p:Period) ON (p.id_hash);
CREATE INDEX dynasty_id_hash_index IF NOT EXISTS FOR (d:Dynasty) ON (d.id_hash);
CREATE INDEX institution_id_hash_index IF NOT EXISTS FOR (i:Institution) ON (i.id_hash);
CREATE INDEX legal_restriction_id_hash_index IF NOT EXISTS FOR (l:LegalRestriction) ON (l.id_hash);
CREATE INDEX claim_id_hash_index IF NOT EXISTS FOR (c:Claim) ON (c.id_hash);
CREATE INDEX organization_id_hash_index IF NOT EXISTS FOR (o:Organization) ON (o.id_hash);
CREATE INDEX year_id_hash_index IF NOT EXISTS FOR (y:Year) ON (y.id_hash);

// Wikidata QID lookups (federation anchor - critical performance)
CREATE INDEX qid_lookup_index IF NOT EXISTS FOR (e:Entity) ON (e.qid);

// Authority-specific ID lookups
CREATE INDEX human_viaf_lookup IF NOT EXISTS FOR (h:Human) ON (h.viaf_id);
CREATE INDEX place_pleiades_lookup IF NOT EXISTS FOR (p:Place) ON (p.pleiades_id);
CREATE INDEX place_tgn_lookup IF NOT EXISTS FOR (p:Place) ON (p.tgn_id);
CREATE INDEX work_qid_lookup IF NOT EXISTS FOR (w:Work) ON (w.qid);

// Year backbone (heavily traversed for temporal filtering)
CREATE INDEX year_number_index IF NOT EXISTS FOR (y:Year) ON (y.year);
CREATE INDEX year_iso_index IF NOT EXISTS FOR (y:Year) ON (y.iso);

// Claim and RetrievalContext lookup
CREATE INDEX claim_id_index IF NOT EXISTS FOR (c:Claim) ON (c.claim_id);
CREATE INDEX claim_cipher_index IF NOT EXISTS FOR (c:Claim) ON (c.cipher);
CREATE INDEX retrieval_context_id_index IF NOT EXISTS FOR (rc:RetrievalContext) ON (rc.retrieval_id);
CREATE INDEX proposed_edge_id_index IF NOT EXISTS FOR (pe:ProposedEdge) ON (pe.edge_id);
CREATE INDEX proposed_edge_claim_id_index IF NOT EXISTS FOR (pe:ProposedEdge) ON (pe.claim_id);
CREATE INDEX proposed_edge_relationship_type_index IF NOT EXISTS FOR (pe:ProposedEdge) ON (pe.relationship_type);
CREATE INDEX proposed_edge_status_index IF NOT EXISTS FOR (pe:ProposedEdge) ON (pe.status);

// Subject & Agent lookup
CREATE INDEX subject_id_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.subject_id);
CREATE INDEX agent_id_index IF NOT EXISTS FOR (a:Agent) ON (a.agent_id);

// ============================================================================
// TEMPORAL INDEXES (for time-based queries & filtering)
// ============================================================================

// Event temporal boundaries
CREATE INDEX event_start_date_index IF NOT EXISTS FOR (e:Event) ON (e.start_date);
CREATE INDEX event_end_date_index IF NOT EXISTS FOR (e:Event) ON (e.end_date);
CREATE INDEX event_start_date_min_index IF NOT EXISTS FOR (e:Event) ON (e.start_date_min);
CREATE INDEX event_start_date_max_index IF NOT EXISTS FOR (e:Event) ON (e.start_date_max);
CREATE INDEX event_end_date_min_index IF NOT EXISTS FOR (e:Event) ON (e.end_date_min);
CREATE INDEX event_end_date_max_index IF NOT EXISTS FOR (e:Event) ON (e.end_date_max);
CREATE INDEX event_temporal_bbox_index IF NOT EXISTS FOR (e:Event) ON (e.start_date_min, e.end_date_max);

// Period temporal boundaries
CREATE INDEX period_start_index IF NOT EXISTS FOR (p:Period) ON (p.start);
CREATE INDEX period_end_index IF NOT EXISTS FOR (p:Period) ON (p.end);
CREATE INDEX period_earliest_start_index IF NOT EXISTS FOR (p:Period) ON (p.earliest_start);
CREATE INDEX period_latest_start_index IF NOT EXISTS FOR (p:Period) ON (p.latest_start);
CREATE INDEX period_earliest_end_index IF NOT EXISTS FOR (p:Period) ON (p.earliest_end);
CREATE INDEX period_latest_end_index IF NOT EXISTS FOR (p:Period) ON (p.latest_end);
CREATE INDEX period_start_date_min_index IF NOT EXISTS FOR (p:Period) ON (p.start_date_min);
CREATE INDEX period_start_date_max_index IF NOT EXISTS FOR (p:Period) ON (p.start_date_max);
CREATE INDEX period_end_date_min_index IF NOT EXISTS FOR (p:Period) ON (p.end_date_min);
CREATE INDEX period_end_date_max_index IF NOT EXISTS FOR (p:Period) ON (p.end_date_max);
CREATE INDEX period_temporal_bbox_index IF NOT EXISTS FOR (p:Period) ON (p.earliest_start, p.latest_end);
CREATE INDEX period_temporal_bbox_minmax_index IF NOT EXISTS FOR (p:Period) ON (p.start_date_min, p.end_date_max);

// Human birth/death dates
CREATE INDEX human_birth_date_index IF NOT EXISTS FOR (h:Human) ON (h.birth_date);
CREATE INDEX human_death_date_index IF NOT EXISTS FOR (h:Human) ON (h.death_date);
CREATE INDEX human_birth_date_min_index IF NOT EXISTS FOR (h:Human) ON (h.birth_date_min);
CREATE INDEX human_birth_date_max_index IF NOT EXISTS FOR (h:Human) ON (h.birth_date_max);
CREATE INDEX human_death_date_min_index IF NOT EXISTS FOR (h:Human) ON (h.death_date_min);
CREATE INDEX human_death_date_max_index IF NOT EXISTS FOR (h:Human) ON (h.death_date_max);
CREATE INDEX human_lifespan_bbox_index IF NOT EXISTS FOR (h:Human) ON (h.birth_date_min, h.death_date_max);

// PlaceVersion temporal bounds
CREATE INDEX place_version_start_index IF NOT EXISTS FOR (pv:PlaceVersion) ON (pv.start_date);
CREATE INDEX place_version_end_index IF NOT EXISTS FOR (pv:PlaceVersion) ON (pv.end_date);

// ============================================================================
// CLASSIFICATION INDEXES (for facet filtering & type-based queries)
// ============================================================================

// Entity type classification
CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.entity_type);

// Facet classification (facet-aware queries)
CREATE INDEX period_facet_index IF NOT EXISTS FOR (p:Period) ON (p.facet);
CREATE INDEX facet_category_key_index IF NOT EXISTS FOR (fc:FacetCategory) ON (fc.key);

// Authority tier classification
CREATE INDEX subject_tier_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.authority_tier);

// First-class node status lifecycle
CREATE INDEX subject_concept_status_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.status);
CREATE INDEX human_status_index IF NOT EXISTS FOR (h:Human) ON (h.status);
CREATE INDEX gens_status_index IF NOT EXISTS FOR (g:Gens) ON (g.status);
CREATE INDEX praenomen_status_index IF NOT EXISTS FOR (p:Praenomen) ON (p.status);
CREATE INDEX cognomen_status_index IF NOT EXISTS FOR (c:Cognomen) ON (c.status);
CREATE INDEX event_status_index IF NOT EXISTS FOR (e:Event) ON (e.status);
CREATE INDEX place_status_index IF NOT EXISTS FOR (p:Place) ON (p.status);
CREATE INDEX period_status_index IF NOT EXISTS FOR (p:Period) ON (p.status);
CREATE INDEX dynasty_status_index IF NOT EXISTS FOR (d:Dynasty) ON (d.status);
CREATE INDEX institution_status_index IF NOT EXISTS FOR (i:Institution) ON (i.status);
CREATE INDEX legal_restriction_status_index IF NOT EXISTS FOR (l:LegalRestriction) ON (l.status);
CREATE INDEX claim_status_index IF NOT EXISTS FOR (c:Claim) ON (c.status);
CREATE INDEX organization_status_index IF NOT EXISTS FOR (o:Organization) ON (o.status);
CREATE INDEX year_status_index IF NOT EXISTS FOR (y:Year) ON (y.status);

// Event type classification
CREATE INDEX event_type_index IF NOT EXISTS FOR (e:Event) ON (e.event_type);

// ============================================================================
// CONFIDENCE & QUALITY INDEXES (for validation queries)
// ============================================================================

// Confidence scores (for QA filtering, data quality checks)
CREATE INDEX claim_confidence_index IF NOT EXISTS FOR (c:Claim) ON (c.confidence);
CREATE INDEX subject_confidence_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.authority_confidence);

// Retrieval context routing/inspection (for claims provenance workflows)
CREATE INDEX retrieval_context_agent_index IF NOT EXISTS FOR (rc:RetrievalContext) ON (rc.agent_id);
CREATE INDEX retrieval_context_timestamp_index IF NOT EXISTS FOR (rc:RetrievalContext) ON (rc.timestamp);

// ============================================================================
// ANALYSIS RUN INDEXES (for A/B testing & version comparison)
// ============================================================================

// Analysis run lookups
CREATE INDEX analysis_run_id_index IF NOT EXISTS FOR (ar:AnalysisRun) ON (ar.run_id);
CREATE INDEX analysis_run_version_index IF NOT EXISTS FOR (ar:AnalysisRun) ON (ar.pipeline_version);

// Facet assessment lookups
CREATE INDEX facet_assessment_id_index IF NOT EXISTS FOR (fa:FacetAssessment) ON (fa.assessment_id);
CREATE INDEX facet_assessment_score_index IF NOT EXISTS FOR (fa:FacetAssessment) ON (fa.score);
CREATE INDEX facet_assessment_status_index IF NOT EXISTS FOR (fa:FacetAssessment) ON (fa.status);

// ============================================================================
// COMPOSITE INDEXES (for common multi-property lookups)
// ============================================================================

// Human by type and time (common query: all leaders during period X)
CREATE INDEX human_type_birth_index IF NOT EXISTS
FOR (h:Human) ON (h.entity_type, h.birth_date);

// Event by type and temporal bounds
CREATE INDEX event_type_date_index IF NOT EXISTS
FOR (e:Event) ON (e.event_type, e.start_date, e.end_date);

// Period by culture and temporal bounds
CREATE INDEX period_culture_date_index IF NOT EXISTS
FOR (p:Period) ON (p.culture, p.start, p.end);

// Place by type and geographic extent
CREATE INDEX place_type_country_index IF NOT EXISTS
FOR (p:Place) ON (p.place_type, p.modern_country);

// ============================================================================
// TEXT SEARCH INDEXES (optional: for full-text search features)
// ============================================================================

// Full-text indexes on labels/names (enable MATCH queries)
CREATE INDEX human_name_fulltext IF NOT EXISTS
FOR (h:Human) ON (h.name);

CREATE INDEX place_label_fulltext IF NOT EXISTS
FOR (p:Place) ON (p.label);

CREATE INDEX event_label_fulltext IF NOT EXISTS
FOR (e:Event) ON (e.label);

CREATE INDEX period_label_fulltext IF NOT EXISTS
FOR (p:Period) ON (p.label);

CREATE INDEX subject_label_fulltext IF NOT EXISTS
FOR (sc:SubjectConcept) ON (sc.label);

// ============================================================================
// RELATIONSHIP TYPE INDEXES (optional: for relationship traversal optimization)
// ============================================================================

// These are implicit in Neo4j but can help with large graphs
// Not explicitly created as constraints, but relationship patterns noted:

// Common traversal patterns:
// ENTITY -> LIVED_DURING -> PERIOD -> STARTS_IN_YEAR -> YEAR
// ENTITY -> HAS_SUBJECT_CONCEPT -> SUBJECT_CONCEPT -> FACET_ANCHOR -> FACET
// CLAIM -> HAS_TRACE -> REASONING_TRACE <- USED_FOR - RETRIEVAL_CONTEXT -> WORK -> ABOUT -> SUBJECT_CONCEPT

// ============================================================================
// INDEX MAINTENANCE NOTES
// ============================================================================
// Once indexes are created:
// 1. Verify: SHOW INDEXES
// 2. Monitor: Profile queries with EXPLAIN/PROFILE
// 3. Drop underutilized indexes: DROP INDEX index_name
// 4. Rebuild if needed: CALL db.indexes.rebuild()

// For large graphs (100M+ nodes), consider:
// - Partitioning by facet category
// - Sharding by time period (decade/century buckets)
// - Index compression for memory constraints

// ============================================================================
// SUMMARY
// ============================================================================
// Total indexes created: 50+
// Recommended index size monitoring: Query performance should improve 50-1000x
// Index creation time: ~1-5 minutes for initial graph load
// ============================================================================
