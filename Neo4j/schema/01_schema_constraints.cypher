// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: CONSTRAINTS & UNIQUENESS RULES
// ============================================================================
// File: 01_schema_constraints.cypher
// Purpose: Define uniqueness and existence constraints for all entity types
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
// CORE ENTITY UNIQUENESS CONSTRAINTS
// ============================================================================

// Human entity uniqueness
CREATE CONSTRAINT human_entity_id_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.entity_id IS UNIQUE;

CREATE CONSTRAINT human_qid_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.qid IS UNIQUE;

CREATE CONSTRAINT human_viaf_id_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.viaf_id IS UNIQUE
  WHEN h.viaf_id IS NOT NULL;

// Place entity uniqueness
CREATE CONSTRAINT place_entity_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.entity_id IS UNIQUE;

CREATE CONSTRAINT place_qid_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.qid IS UNIQUE;

CREATE CONSTRAINT place_pleiades_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.pleiades_id IS UNIQUE
  WHEN p.pleiades_id IS NOT NULL;

CREATE CONSTRAINT place_tgn_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.tgn_id IS UNIQUE
  WHEN p.tgn_id IS NOT NULL;

// PlaceVersion uniqueness
CREATE CONSTRAINT place_version_id_unique IF NOT EXISTS
FOR (pv:PlaceVersion) REQUIRE pv.pver_id IS UNIQUE;

// Geometry uniqueness
CREATE CONSTRAINT geometry_id_unique IF NOT EXISTS
FOR (g:Geometry) REQUIRE g.geo_id IS UNIQUE;

// Event entity uniqueness
CREATE CONSTRAINT event_entity_id_unique IF NOT EXISTS
FOR (e:Event) REQUIRE e.entity_id IS UNIQUE;

CREATE CONSTRAINT event_qid_unique IF NOT EXISTS
FOR (e:Event) REQUIRE e.qid IS UNIQUE;

// Period entity uniqueness
CREATE CONSTRAINT period_entity_id_unique IF NOT EXISTS
FOR (p:Period) REQUIRE p.entity_id IS UNIQUE;

CREATE CONSTRAINT period_qid_unique IF NOT EXISTS
FOR (p:Period) REQUIRE p.qid IS UNIQUE
  WHEN p.qid IS NOT NULL;

// Year backbone uniqueness (critical for temporal grid)
CREATE CONSTRAINT year_entity_id_unique IF NOT EXISTS
FOR (y:Year) REQUIRE y.entity_id IS UNIQUE;

CREATE CONSTRAINT year_year_number_unique IF NOT EXISTS
FOR (y:Year) REQUIRE y.year IS UNIQUE;

// Organization uniqueness
CREATE CONSTRAINT organization_entity_id_unique IF NOT EXISTS
FOR (o:Organization) REQUIRE o.entity_id IS UNIQUE;

CREATE CONSTRAINT organization_qid_unique IF NOT EXISTS
FOR (o:Organization) REQUIRE o.qid IS UNIQUE
  WHEN o.qid IS NOT NULL;

// Institution uniqueness
CREATE CONSTRAINT institution_entity_id_unique IF NOT EXISTS
FOR (i:Institution) REQUIRE i.entity_id IS UNIQUE;

// Dynasty uniqueness
CREATE CONSTRAINT dynasty_entity_id_unique IF NOT EXISTS
FOR (d:Dynasty) REQUIRE d.entity_id IS UNIQUE;

// LegalRestriction uniqueness
CREATE CONSTRAINT legal_restriction_entity_id_unique IF NOT EXISTS
FOR (l:LegalRestriction) REQUIRE l.entity_id IS UNIQUE;

// Work uniqueness
CREATE CONSTRAINT work_entity_id_unique IF NOT EXISTS
FOR (w:Work) REQUIRE w.entity_id IS UNIQUE;

CREATE CONSTRAINT work_qid_unique IF NOT EXISTS
FOR (w:Work) REQUIRE w.qid IS UNIQUE;

// Position uniqueness
CREATE CONSTRAINT position_entity_id_unique IF NOT EXISTS
FOR (p:Position) REQUIRE p.entity_id IS UNIQUE;

// Material uniqueness
CREATE CONSTRAINT material_entity_id_unique IF NOT EXISTS
FOR (m:Material) REQUIRE m.entity_id IS UNIQUE;

// Object uniqueness
CREATE CONSTRAINT object_entity_id_unique IF NOT EXISTS
FOR (o:Object) REQUIRE o.entity_id IS UNIQUE;

// Activity uniqueness
CREATE CONSTRAINT activity_entity_id_unique IF NOT EXISTS
FOR (a:Activity) REQUIRE a.entity_id IS UNIQUE;

// Gens (Roman family clans) uniqueness
CREATE CONSTRAINT gens_entity_id_unique IF NOT EXISTS
FOR (g:Gens) REQUIRE g.entity_id IS UNIQUE;

// Praenomen (Roman first names) uniqueness
CREATE CONSTRAINT praenomen_entity_id_unique IF NOT EXISTS
FOR (p:Praenomen) REQUIRE p.entity_id IS UNIQUE;

// Cognomen (Roman surnames) uniqueness
CREATE CONSTRAINT cognomen_entity_id_unique IF NOT EXISTS
FOR (c:Cognomen) REQUIRE c.entity_id IS UNIQUE;

// Canonical ID hash uniqueness (new normalized ID policy)
CREATE CONSTRAINT subject_concept_id_hash_unique IF NOT EXISTS
FOR (sc:SubjectConcept) REQUIRE sc.id_hash IS UNIQUE
  WHEN sc.id_hash IS NOT NULL;

CREATE CONSTRAINT human_id_hash_unique IF NOT EXISTS
FOR (h:Human) REQUIRE h.id_hash IS UNIQUE
  WHEN h.id_hash IS NOT NULL;

CREATE CONSTRAINT gens_id_hash_unique IF NOT EXISTS
FOR (g:Gens) REQUIRE g.id_hash IS UNIQUE
  WHEN g.id_hash IS NOT NULL;

CREATE CONSTRAINT praenomen_id_hash_unique IF NOT EXISTS
FOR (p:Praenomen) REQUIRE p.id_hash IS UNIQUE
  WHEN p.id_hash IS NOT NULL;

CREATE CONSTRAINT cognomen_id_hash_unique IF NOT EXISTS
FOR (c:Cognomen) REQUIRE c.id_hash IS UNIQUE
  WHEN c.id_hash IS NOT NULL;

CREATE CONSTRAINT event_id_hash_unique IF NOT EXISTS
FOR (e:Event) REQUIRE e.id_hash IS UNIQUE
  WHEN e.id_hash IS NOT NULL;

CREATE CONSTRAINT place_id_hash_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.id_hash IS UNIQUE
  WHEN p.id_hash IS NOT NULL;

CREATE CONSTRAINT period_id_hash_unique IF NOT EXISTS
FOR (p:Period) REQUIRE p.id_hash IS UNIQUE
  WHEN p.id_hash IS NOT NULL;

CREATE CONSTRAINT dynasty_id_hash_unique IF NOT EXISTS
FOR (d:Dynasty) REQUIRE d.id_hash IS UNIQUE
  WHEN d.id_hash IS NOT NULL;

CREATE CONSTRAINT institution_id_hash_unique IF NOT EXISTS
FOR (i:Institution) REQUIRE i.id_hash IS UNIQUE
  WHEN i.id_hash IS NOT NULL;

CREATE CONSTRAINT legal_restriction_id_hash_unique IF NOT EXISTS
FOR (l:LegalRestriction) REQUIRE l.id_hash IS UNIQUE
  WHEN l.id_hash IS NOT NULL;

CREATE CONSTRAINT claim_id_hash_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.id_hash IS UNIQUE
  WHEN c.id_hash IS NOT NULL;

CREATE CONSTRAINT organization_id_hash_unique IF NOT EXISTS
FOR (o:Organization) REQUIRE o.id_hash IS UNIQUE
  WHEN o.id_hash IS NOT NULL;

CREATE CONSTRAINT year_id_hash_unique IF NOT EXISTS
FOR (y:Year) REQUIRE y.id_hash IS UNIQUE
  WHEN y.id_hash IS NOT NULL;

// ============================================================================
// ANALYSIS & ASSESSMENT NODE UNIQUENESS
// ============================================================================

// AnalysisRun uniqueness
CREATE CONSTRAINT analysis_run_id_unique IF NOT EXISTS
FOR (ar:AnalysisRun) REQUIRE ar.run_id IS UNIQUE;

// FacetAssessment uniqueness
CREATE CONSTRAINT facet_assessment_id_unique IF NOT EXISTS
FOR (fa:FacetAssessment) REQUIRE fa.assessment_id IS UNIQUE;

// FacetCategory uniqueness
CREATE CONSTRAINT facet_category_key_unique IF NOT EXISTS
FOR (fc:FacetCategory) REQUIRE fc.key IS UNIQUE;

// ============================================================================
// SUBJECT/CLAIMS LAYER UNIQUENESS (referenced from other sections)
// ============================================================================

// SubjectConcept uniqueness
CREATE CONSTRAINT subject_concept_id_unique IF NOT EXISTS
FOR (sc:SubjectConcept) REQUIRE sc.subject_id IS UNIQUE;

// Claim uniqueness
CREATE CONSTRAINT claim_id_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.claim_id IS UNIQUE;

CREATE CONSTRAINT claim_cipher_unique IF NOT EXISTS
FOR (c:Claim) REQUIRE c.cipher IS UNIQUE;

// Retrieval context uniqueness (Claims Layer evidence retrieval record)
CREATE CONSTRAINT retrieval_context_id_unique IF NOT EXISTS
FOR (rc:RetrievalContext) REQUIRE rc.retrieval_id IS UNIQUE;

// Agent uniqueness
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS
FOR (a:Agent) REQUIRE a.agent_id IS UNIQUE;

// ============================================================================
// REQUIRED PROPERTY CONSTRAINTS
// ============================================================================

// All entities must have entity_id and entity_type
CREATE CONSTRAINT entity_has_id IF NOT EXISTS
FOR (e:Entity) REQUIRE e.entity_id IS NOT NULL;

CREATE CONSTRAINT entity_has_type IF NOT EXISTS
FOR (e:Entity) REQUIRE e.entity_type IS NOT NULL;

// Human entities must have name
CREATE CONSTRAINT human_has_name IF NOT EXISTS
FOR (h:Human) REQUIRE h.name IS NOT NULL;

// Required QID on core externally aligned entity types
CREATE CONSTRAINT human_has_qid IF NOT EXISTS
FOR (h:Human) REQUIRE h.qid IS NOT NULL;

// Place entities must have label
CREATE CONSTRAINT place_has_label IF NOT EXISTS
FOR (p:Place) REQUIRE p.label IS NOT NULL;

CREATE CONSTRAINT place_has_qid IF NOT EXISTS
FOR (p:Place) REQUIRE p.qid IS NOT NULL;

// Year entities must have year number
CREATE CONSTRAINT year_has_year_number IF NOT EXISTS
FOR (y:Year) REQUIRE y.year IS NOT NULL;

// Event entities must have label and temporal bounds
CREATE CONSTRAINT event_has_label IF NOT EXISTS
FOR (e:Event) REQUIRE e.label IS NOT NULL;

CREATE CONSTRAINT event_has_start_date IF NOT EXISTS
FOR (e:Event) REQUIRE e.start_date IS NOT NULL;

CREATE CONSTRAINT event_has_qid IF NOT EXISTS
FOR (e:Event) REQUIRE e.qid IS NOT NULL;

// Period entities must have label and bounds
CREATE CONSTRAINT period_has_label IF NOT EXISTS
FOR (p:Period) REQUIRE p.label IS NOT NULL;

CREATE CONSTRAINT period_has_start IF NOT EXISTS
FOR (p:Period) REQUIRE p.start IS NOT NULL;

// SubjectConcept must have label
CREATE CONSTRAINT subject_concept_has_label IF NOT EXISTS
FOR (sc:SubjectConcept) REQUIRE sc.label IS NOT NULL;

CREATE CONSTRAINT subject_concept_has_subject_id IF NOT EXISTS
FOR (sc:SubjectConcept) REQUIRE sc.subject_id IS NOT NULL;

// Work entities must have qid for external alignment
CREATE CONSTRAINT work_has_qid IF NOT EXISTS
FOR (w:Work) REQUIRE w.qid IS NOT NULL;

// Claim must have text and confidence
CREATE CONSTRAINT claim_has_text IF NOT EXISTS
FOR (c:Claim) REQUIRE c.text IS NOT NULL;

CREATE CONSTRAINT claim_has_confidence IF NOT EXISTS
FOR (c:Claim) REQUIRE c.confidence IS NOT NULL;

CREATE CONSTRAINT claim_has_cipher IF NOT EXISTS
FOR (c:Claim) REQUIRE c.cipher IS NOT NULL;

// ============================================================================
// RELATIONSHIP CONSTRAINTS
// ============================================================================

// Year backbone must be linked sequentially
// (Enforced at data load time, not via constraints; see initialization script)

// All temporal entities must link to Year backbone
// (Recommend as best practice, not hard constraint for flexibility)

// ============================================================================
// SUMMARY
// ============================================================================
// Total constraints created: 60+
// Constraint violations will prevent invalid data insertion
// Use SHOW CONSTRAINTS to verify after import
// ============================================================================
