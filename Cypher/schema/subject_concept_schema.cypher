// ============================================================================
// SUBJECT CONCEPT SCHEMA - Constraints, Indexes, and Base Structure
// ============================================================================

// PHASE 1: Create Constraints
// ============================================================================

// SubjectConcept unique constraints
CREATE CONSTRAINT subject_concept_id IF NOT EXISTS
  FOR (n:SubjectConcept) REQUIRE n.concept_id IS UNIQUE;

CREATE CONSTRAINT subject_concept_label_wikidata IF NOT EXISTS
  FOR (n:SubjectConcept) REQUIRE (n.label, n.wikidata_qid) IS UNIQUE;

// SubjectConceptRegistry unique constraints
CREATE CONSTRAINT registry_id IF NOT EXISTS
  FOR (n:SubjectConceptRegistry) REQUIRE n.registry_id IS UNIQUE;

// Authority node unique constraints
CREATE CONSTRAINT lcc_class_code IF NOT EXISTS
  FOR (n:LCC_Class) REQUIRE n.code IS UNIQUE;

CREATE CONSTRAINT lcsh_subject_id IF NOT EXISTS
  FOR (n:LCSH_Subject) REQUIRE n.lcsh_id IS UNIQUE;

CREATE CONSTRAINT fast_subject_id IF NOT EXISTS
  FOR (n:FAST_Subject) REQUIRE n.fast_id IS UNIQUE;

CREATE CONSTRAINT claim_id IF NOT EXISTS
  FOR (n:Claim) REQUIRE n.claim_id IS UNIQUE;


// PHASE 2: Create Indexes (for query performance)
// ============================================================================

// SubjectConcept indexes
CREATE INDEX subject_concept_label IF NOT EXISTS
  FOR (n:SubjectConcept) ON (n.label);

CREATE INDEX subject_concept_wikidata_qid IF NOT EXISTS
  FOR (n:SubjectConcept) ON (n.wikidata_qid);

CREATE INDEX subject_concept_parent IF NOT EXISTS
  FOR (n:SubjectConcept) ON (n.parent_concept_id);

CREATE INDEX subject_concept_source IF NOT EXISTS
  FOR (n:SubjectConcept) ON (n.source);

CREATE INDEX subject_concept_is_agent_created IF NOT EXISTS
  FOR (n:SubjectConcept) ON (n.is_agent_created);

CREATE INDEX subject_concept_validation_status IF NOT EXISTS
  FOR (n:SubjectConcept) ON (n.validation_status);

// Claim indexes
CREATE INDEX claim_primary_facet IF NOT EXISTS
  FOR (n:Claim) ON (n.primary_facet);

CREATE INDEX claim_confidence IF NOT EXISTS
  FOR (n:Claim) ON (n.confidence);

CREATE INDEX claim_source_agent IF NOT EXISTS
  FOR (n:Claim) ON (n.source_agent);

// Authority indexes
CREATE INDEX lcc_class_label IF NOT EXISTS
  FOR (n:LCC_Class) ON (n.label);

CREATE INDEX lcsh_subject_heading IF NOT EXISTS
  FOR (n:LCSH_Subject) ON (n.heading);

CREATE INDEX fast_subject_label IF NOT EXISTS
  FOR (n:FAST_Subject) ON (n.preferred_label);

// Registry indexes
CREATE INDEX registry_parent_concept IF NOT EXISTS
  FOR (n:SubjectConceptRegistry) ON (n.parent_concept_id);

CREATE INDEX registry_updated IF NOT EXISTS
  FOR (n:SubjectConceptRegistry) ON (n.last_updated);


// PHASE 3: Verify Schema
// ============================================================================

// Check constraints created
SHOW CONSTRAINTS;

// Check indexes created
SHOW INDEXES;
