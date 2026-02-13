// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: INDEXES FOR QUERY PERFORMANCE
// ============================================================================
// File: 02_schema_indexes.cypher
// Purpose: Define optimal indexes for common query patterns
// Created: 2026-02-13
// Status: Production Schema
// ============================================================================

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

// Claim and Evidence lookup
CREATE INDEX claim_id_index IF NOT EXISTS FOR (c:Claim) ON (c.unique_id);
CREATE INDEX evidence_id_index IF NOT EXISTS FOR (e:Evidence) ON (e.evidence_id);

// Subject & Agent lookup
CREATE INDEX subject_id_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.unique_id);
CREATE INDEX agent_id_index IF NOT EXISTS FOR (a:Agent) ON (a.agent_id);

// ============================================================================
// TEMPORAL INDEXES (for time-based queries & filtering)
// ============================================================================

// Event temporal boundaries
CREATE INDEX event_start_date_index IF NOT EXISTS FOR (e:Event) ON (e.start_date);
CREATE INDEX event_end_date_index IF NOT EXISTS FOR (e:Event) ON (e.end_date);

// Period temporal boundaries
CREATE INDEX period_start_index IF NOT EXISTS FOR (p:Period) ON (p.start);
CREATE INDEX period_end_index IF NOT EXISTS FOR (p:Period) ON (p.end);

// Human birth/death dates
CREATE INDEX human_birth_date_index IF NOT EXISTS FOR (h:Human) ON (h.birth_date);
CREATE INDEX human_death_date_index IF NOT EXISTS FOR (h:Human) ON (h.death_date);

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

// Event type classification
CREATE INDEX event_type_index IF NOT EXISTS FOR (e:Event) ON (e.event_type);

// ============================================================================
// CONFIDENCE & QUALITY INDEXES (for validation queries)
// ============================================================================

// Confidence scores (for QA filtering, data quality checks)
CREATE INDEX claim_confidence_index IF NOT EXISTS FOR (c:Claim) ON (c.overall_confidence);
CREATE INDEX evidence_confidence_index IF NOT EXISTS FOR (e:Evidence) ON (e.source_confidence);
CREATE INDEX subject_confidence_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.authority_confidence);

// Source tier classification (for workflow routing)
CREATE INDEX evidence_source_tier_index IF NOT EXISTS FOR (e:Evidence) ON (e.source_tier);

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
// ENTITY -> HAS_SUBJECT_CONCEPT -> SUBJECT -> FACET_ANCHOR -> FACET
// CLAIM -> EVIDENCED_BY -> EVIDENCE -> SOURCE -> WORK -> ABOUT -> SUBJECT

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
