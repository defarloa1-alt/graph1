// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: CORE PIPELINE BOOTSTRAP (PHASE 1)
// ============================================================================
// File: 07_core_pipeline_schema.cypher
// Purpose: Bootstrap core non-temporal pipeline schema on top of temporal baseline
// Scope: Human, Place, Event, Period, SubjectConcept, Claim, RetrievalContext,
//        Agent, AnalysisRun, FacetAssessment
// Notes:
// - Safe to run repeatedly (`IF NOT EXISTS` everywhere).
// - Does not alter Year/Decade/Century/Millennium backbone.
// ============================================================================

// ============================================================================
// CONSTRAINTS
// ============================================================================

// Human
CREATE CONSTRAINT human_entity_id_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.entity_id IS UNIQUE;
CREATE CONSTRAINT human_qid_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.qid IS UNIQUE;
CREATE CONSTRAINT human_viaf_id_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.viaf_id IS UNIQUE;
CREATE CONSTRAINT human_has_name IF NOT EXISTS
FOR (h:Human) REQUIRE h.name IS NOT NULL;
CREATE CONSTRAINT human_has_qid IF NOT EXISTS
FOR (h:Human) REQUIRE h.qid IS NOT NULL;
CREATE CONSTRAINT human_has_entity_type IF NOT EXISTS
FOR (h:Human) REQUIRE h.entity_type IS NOT NULL;

// Place
CREATE CONSTRAINT place_entity_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.entity_id IS UNIQUE;
CREATE CONSTRAINT place_qid_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.qid IS UNIQUE;
CREATE CONSTRAINT place_pleiades_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.pleiades_id IS UNIQUE;
CREATE CONSTRAINT place_tgn_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.tgn_id IS UNIQUE;
CREATE CONSTRAINT place_has_label IF NOT EXISTS
FOR (p:Place) REQUIRE p.label IS NOT NULL;
CREATE CONSTRAINT place_has_qid IF NOT EXISTS
FOR (p:Place) REQUIRE p.qid IS NOT NULL;
CREATE CONSTRAINT place_has_entity_type IF NOT EXISTS
FOR (p:Place) REQUIRE p.entity_type IS NOT NULL;

// Event
CREATE CONSTRAINT event_entity_id_unique IF NOT EXISTS
FOR (e:Event) REQUIRE e.entity_id IS UNIQUE;
CREATE CONSTRAINT event_qid_unique IF NOT EXISTS
FOR (e:Event) REQUIRE e.qid IS UNIQUE;
CREATE CONSTRAINT event_has_label IF NOT EXISTS
FOR (e:Event) REQUIRE e.label IS NOT NULL;
CREATE CONSTRAINT event_has_start_date IF NOT EXISTS
FOR (e:Event) REQUIRE e.start_date IS NOT NULL;
CREATE CONSTRAINT event_has_qid IF NOT EXISTS
FOR (e:Event) REQUIRE e.qid IS NOT NULL;
CREATE CONSTRAINT event_has_entity_type IF NOT EXISTS
FOR (e:Event) REQUIRE e.entity_type IS NOT NULL;

// Period
CREATE CONSTRAINT period_entity_id_unique IF NOT EXISTS
FOR (p:Period) REQUIRE p.entity_id IS UNIQUE;
CREATE CONSTRAINT period_qid_unique IF NOT EXISTS
FOR (p:Period) REQUIRE p.qid IS UNIQUE;
CREATE CONSTRAINT period_has_label IF NOT EXISTS
FOR (p:Period) REQUIRE p.label IS NOT NULL;
CREATE CONSTRAINT period_has_start IF NOT EXISTS
FOR (p:Period) REQUIRE p.start IS NOT NULL;
CREATE CONSTRAINT period_has_end IF NOT EXISTS
FOR (p:Period) REQUIRE p.end IS NOT NULL;
CREATE CONSTRAINT period_has_entity_type IF NOT EXISTS
FOR (p:Period) REQUIRE p.entity_type IS NOT NULL;

// SubjectConcept
CREATE CONSTRAINT subject_concept_id_unique IF NOT EXISTS
FOR (sc:SubjectConcept) REQUIRE sc.subject_id IS UNIQUE;
CREATE CONSTRAINT subject_concept_has_subject_id IF NOT EXISTS
FOR (sc:SubjectConcept) REQUIRE sc.subject_id IS NOT NULL;
CREATE CONSTRAINT subject_concept_has_label IF NOT EXISTS
FOR (sc:SubjectConcept) REQUIRE sc.label IS NOT NULL;
CREATE CONSTRAINT subject_concept_has_facet IF NOT EXISTS
FOR (sc:SubjectConcept) REQUIRE sc.facet IS NOT NULL;

// Claim
CREATE CONSTRAINT claim_id_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE;
CREATE CONSTRAINT claim_cipher_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.cipher IS UNIQUE;
CREATE CONSTRAINT claim_has_text IF NOT EXISTS
FOR (c:Claim) REQUIRE c.text IS NOT NULL;
CREATE CONSTRAINT claim_has_label IF NOT EXISTS
FOR (c:Claim) REQUIRE c.label IS NOT NULL;
CREATE CONSTRAINT claim_has_confidence IF NOT EXISTS
FOR (c:Claim) REQUIRE c.confidence IS NOT NULL;
CREATE CONSTRAINT claim_has_cipher IF NOT EXISTS
FOR (c:Claim) REQUIRE c.cipher IS NOT NULL;
CREATE CONSTRAINT claim_has_claim_type IF NOT EXISTS
FOR (c:Claim) REQUIRE c.claim_type IS NOT NULL;
CREATE CONSTRAINT claim_has_source_agent IF NOT EXISTS
FOR (c:Claim) REQUIRE c.source_agent IS NOT NULL;
CREATE CONSTRAINT claim_has_timestamp IF NOT EXISTS
FOR (c:Claim) REQUIRE c.timestamp IS NOT NULL;
CREATE CONSTRAINT claim_has_status IF NOT EXISTS
FOR (c:Claim) REQUIRE c.status IS NOT NULL;

// RetrievalContext
CREATE CONSTRAINT retrieval_context_id_unique IF NOT EXISTS
FOR (rc:RetrievalContext) REQUIRE rc.retrieval_id IS UNIQUE;
CREATE CONSTRAINT retrieval_context_has_id IF NOT EXISTS
FOR (rc:RetrievalContext) REQUIRE rc.retrieval_id IS NOT NULL;

// Agent
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS
FOR (a:Agent) REQUIRE a.agent_id IS UNIQUE;
CREATE CONSTRAINT agent_has_id IF NOT EXISTS
FOR (a:Agent) REQUIRE a.agent_id IS NOT NULL;
CREATE CONSTRAINT agent_has_label IF NOT EXISTS
FOR (a:Agent) REQUIRE a.label IS NOT NULL;
CREATE CONSTRAINT agent_has_agent_type IF NOT EXISTS
FOR (a:Agent) REQUIRE a.agent_type IS NOT NULL;

// AnalysisRun
CREATE CONSTRAINT analysis_run_id_unique IF NOT EXISTS
FOR (ar:AnalysisRun) REQUIRE ar.run_id IS UNIQUE;
CREATE CONSTRAINT analysis_run_has_id IF NOT EXISTS
FOR (ar:AnalysisRun) REQUIRE ar.run_id IS NOT NULL;
CREATE CONSTRAINT analysis_run_has_pipeline_version IF NOT EXISTS
FOR (ar:AnalysisRun) REQUIRE ar.pipeline_version IS NOT NULL;

// FacetAssessment
CREATE CONSTRAINT facet_assessment_id_unique IF NOT EXISTS
FOR (fa:FacetAssessment) REQUIRE fa.assessment_id IS UNIQUE;
CREATE CONSTRAINT facet_assessment_has_id IF NOT EXISTS
FOR (fa:FacetAssessment) REQUIRE fa.assessment_id IS NOT NULL;
CREATE CONSTRAINT facet_assessment_has_score IF NOT EXISTS
FOR (fa:FacetAssessment) REQUIRE fa.score IS NOT NULL;
CREATE CONSTRAINT facet_assessment_has_status IF NOT EXISTS
FOR (fa:FacetAssessment) REQUIRE fa.status IS NOT NULL;

// ============================================================================
// INDEXES
// ============================================================================

// Human
CREATE INDEX human_entity_id_index IF NOT EXISTS FOR (h:Human) ON (h.entity_id);
CREATE INDEX human_qid_index IF NOT EXISTS FOR (h:Human) ON (h.qid);
CREATE INDEX human_viaf_lookup IF NOT EXISTS FOR (h:Human) ON (h.viaf_id);
CREATE INDEX human_birth_date_index IF NOT EXISTS FOR (h:Human) ON (h.birth_date);
CREATE INDEX human_death_date_index IF NOT EXISTS FOR (h:Human) ON (h.death_date);

// Place
CREATE INDEX place_entity_id_index IF NOT EXISTS FOR (p:Place) ON (p.entity_id);
CREATE INDEX place_qid_index IF NOT EXISTS FOR (p:Place) ON (p.qid);
CREATE INDEX place_pleiades_lookup IF NOT EXISTS FOR (p:Place) ON (p.pleiades_id);
CREATE INDEX place_tgn_lookup IF NOT EXISTS FOR (p:Place) ON (p.tgn_id);
CREATE INDEX place_label_index IF NOT EXISTS FOR (p:Place) ON (p.label);

// Event
CREATE INDEX event_entity_id_index IF NOT EXISTS FOR (e:Event) ON (e.entity_id);
CREATE INDEX event_qid_index IF NOT EXISTS FOR (e:Event) ON (e.qid);
CREATE INDEX event_label_index IF NOT EXISTS FOR (e:Event) ON (e.label);
CREATE INDEX event_type_index IF NOT EXISTS FOR (e:Event) ON (e.event_type);
CREATE INDEX event_start_date_index IF NOT EXISTS FOR (e:Event) ON (e.start_date);
CREATE INDEX event_end_date_index IF NOT EXISTS FOR (e:Event) ON (e.end_date);
CREATE INDEX event_start_date_min_index IF NOT EXISTS FOR (e:Event) ON (e.start_date_min);
CREATE INDEX event_start_date_max_index IF NOT EXISTS FOR (e:Event) ON (e.start_date_max);
CREATE INDEX event_end_date_min_index IF NOT EXISTS FOR (e:Event) ON (e.end_date_min);
CREATE INDEX event_end_date_max_index IF NOT EXISTS FOR (e:Event) ON (e.end_date_max);
CREATE INDEX event_temporal_bbox_index IF NOT EXISTS FOR (e:Event) ON (e.start_date_min, e.end_date_max);

// Period
CREATE INDEX period_entity_id_index IF NOT EXISTS FOR (p:Period) ON (p.entity_id);
CREATE INDEX period_qid_index IF NOT EXISTS FOR (p:Period) ON (p.qid);
CREATE INDEX period_label_index IF NOT EXISTS FOR (p:Period) ON (p.label);
CREATE INDEX period_facet_index IF NOT EXISTS FOR (p:Period) ON (p.facet);
CREATE INDEX period_start_index IF NOT EXISTS FOR (p:Period) ON (p.start);
CREATE INDEX period_end_index IF NOT EXISTS FOR (p:Period) ON (p.end);
CREATE INDEX period_start_date_min_index IF NOT EXISTS FOR (p:Period) ON (p.start_date_min);
CREATE INDEX period_start_date_max_index IF NOT EXISTS FOR (p:Period) ON (p.start_date_max);
CREATE INDEX period_end_date_min_index IF NOT EXISTS FOR (p:Period) ON (p.end_date_min);
CREATE INDEX period_end_date_max_index IF NOT EXISTS FOR (p:Period) ON (p.end_date_max);
CREATE INDEX period_temporal_bbox_minmax_index IF NOT EXISTS FOR (p:Period) ON (p.start_date_min, p.end_date_max);

// SubjectConcept
CREATE INDEX subject_id_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.subject_id);
CREATE INDEX subject_label_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.label);
CREATE INDEX subject_facet_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.facet);
CREATE INDEX subject_tier_index IF NOT EXISTS FOR (sc:SubjectConcept) ON (sc.authority_tier);

// Claim
CREATE INDEX claim_id_index IF NOT EXISTS FOR (c:Claim) ON (c.claim_id);
CREATE INDEX claim_cipher_index IF NOT EXISTS FOR (c:Claim) ON (c.cipher);
CREATE INDEX claim_status_index IF NOT EXISTS FOR (c:Claim) ON (c.status);
CREATE INDEX claim_confidence_index IF NOT EXISTS FOR (c:Claim) ON (c.confidence);
CREATE INDEX claim_timestamp_index IF NOT EXISTS FOR (c:Claim) ON (c.timestamp);
CREATE INDEX claim_source_agent_index IF NOT EXISTS FOR (c:Claim) ON (c.source_agent);
CREATE INDEX claim_label_index IF NOT EXISTS FOR (c:Claim) ON (c.label);

// RetrievalContext
CREATE INDEX retrieval_context_id_index IF NOT EXISTS FOR (rc:RetrievalContext) ON (rc.retrieval_id);
CREATE INDEX retrieval_context_agent_index IF NOT EXISTS FOR (rc:RetrievalContext) ON (rc.agent_id);
CREATE INDEX retrieval_context_timestamp_index IF NOT EXISTS FOR (rc:RetrievalContext) ON (rc.timestamp);

// Agent
CREATE INDEX agent_id_index IF NOT EXISTS FOR (a:Agent) ON (a.agent_id);
CREATE INDEX agent_type_index IF NOT EXISTS FOR (a:Agent) ON (a.agent_type);

// AnalysisRun
CREATE INDEX analysis_run_id_index IF NOT EXISTS FOR (ar:AnalysisRun) ON (ar.run_id);
CREATE INDEX analysis_run_version_index IF NOT EXISTS FOR (ar:AnalysisRun) ON (ar.pipeline_version);
CREATE INDEX analysis_run_status_index IF NOT EXISTS FOR (ar:AnalysisRun) ON (ar.status);

// FacetAssessment
CREATE INDEX facet_assessment_id_index IF NOT EXISTS FOR (fa:FacetAssessment) ON (fa.assessment_id);
CREATE INDEX facet_assessment_score_index IF NOT EXISTS FOR (fa:FacetAssessment) ON (fa.score);
CREATE INDEX facet_assessment_status_index IF NOT EXISTS FOR (fa:FacetAssessment) ON (fa.status);

// ============================================================================
// END
// ============================================================================
