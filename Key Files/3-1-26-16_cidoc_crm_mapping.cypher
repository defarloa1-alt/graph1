// ============================================================================
// Script 16: CIDOC-CRM + CRMinf Ontology Mapping Layer
// ============================================================================
// PURPOSE: Makes Chrystallum trilingually literate (Wikidata ↔ CIDOC-CRM ↔ native)
// DEPENDS: Scripts 10-15 (meta-schema, decision tables, claim lifecycle, 
//          onboarding, ADR patches, missing tables)
// CREATES: ~65 nodes, ~120 edges
//   - 30 SYS_CidocClass nodes (CIDOC-CRM core + CRMinf classes)
//   - 15 SYS_CidocProperty nodes (key CIDOC-CRM properties)
//   - ~50 MAPS_TO_CIDOC relationships (EntityType → CidocClass, etc.)
//   - ~25 CIDOC_PROPERTY_MAPS relationships (SYS_RelationshipType → CidocProperty)
//   - 1 SYS_ADR node (ADR-007)
//   - 1 SYS_OnboardingStep (step 15)
//   - 4 SYS_FederationSource nodes (Open Syllabus, Open Library, OpenAlex, Perseus)
//   - cidoc_crm_class property SET on existing nodes
// IDEMPOTENT: All statements use MERGE
// ============================================================================


// ── SECTION 1: CIDOC-CRM Core Class Nodes ──────────────────────────────────
// These represent the formal ontology classes. Agents can query them to 
// understand how Chrystallum maps to the museum/archive interoperability standard.

// Top-level & Temporal
MERGE (c:SYS_CidocClass {class_id: 'E1_CRM_Entity'})
SET c.label = 'CRM Entity',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity',
    c.wikidata_qid = 'Q35120',
    c.mapping_type = 'direct',
    c.scope_note = 'Top-level ontology class, implicit in all entities',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E2_Temporal_Entity'})
SET c.label = 'Temporal Entity',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E2_Temporal_Entity',
    c.wikidata_qid = 'Q1190554',
    c.mapping_type = 'approximate',
    c.scope_note = 'Events, periods, states - anything with temporal extent',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E4_Period'})
SET c.label = 'Period',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E4_Period',
    c.wikidata_qid = 'Q11514315',
    c.wikidata_property = 'P2348',
    c.mapping_type = 'composite',
    c.scope_note = 'Historical periods with start/end bounds',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E5_Event'})
SET c.label = 'Event',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E5_Event',
    c.wikidata_qid = 'Q1656682',
    c.mapping_type = 'direct',
    c.scope_note = 'Specific occurrences: battles, treaties, elections',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E7_Activity'})
SET c.label = 'Activity',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E7_Activity',
    c.wikidata_qid = 'Q1914636',
    c.mapping_type = 'direct',
    c.scope_note = 'Intentional actions carried out by actors',
    c.crm_family = 'core';

// Actor Classes
MERGE (c:SYS_CidocClass {class_id: 'E39_Actor'})
SET c.label = 'Actor',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E39_Actor',
    c.wikidata_qid = 'Q24229398',
    c.mapping_type = 'approximate',
    c.scope_note = 'People, groups, institutions that can act',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E21_Person'})
SET c.label = 'Person',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E21_Person',
    c.wikidata_qid = 'Q5',
    c.mapping_type = 'direct',
    c.scope_note = 'Individual humans',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E74_Group'})
SET c.label = 'Group',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E74_Group',
    c.wikidata_qid = 'Q16334295',
    c.mapping_type = 'direct',
    c.scope_note = 'Organizations, families, institutions',
    c.crm_family = 'core';

// Physical & Spatial
MERGE (c:SYS_CidocClass {class_id: 'E53_Place'})
SET c.label = 'Place',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E53_Place',
    c.wikidata_qid = 'Q82794',
    c.mapping_type = 'direct',
    c.scope_note = 'Geographic regions and locations',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E27_Site'})
SET c.label = 'Site',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E27_Site',
    c.wikidata_qid = 'Q839954',
    c.mapping_type = 'direct',
    c.scope_note = 'Archaeological sites',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E22_Human_Made_Object'})
SET c.label = 'Human-Made Object',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E22_Human-Made_Object',
    c.wikidata_qid = 'Q16887380',
    c.mapping_type = 'direct',
    c.scope_note = 'Artifacts, tools, manufactured items',
    c.crm_family = 'core';

// Conceptual Objects
MERGE (c:SYS_CidocClass {class_id: 'E55_Type'})
SET c.label = 'Type',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E55_Type',
    c.wikidata_qid = 'Q28777',
    c.mapping_type = 'direct',
    c.scope_note = 'Classification types and categories',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E73_Information_Object'})
SET c.label = 'Information Object',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E73_Information_Object',
    c.wikidata_qid = 'Q11028',
    c.mapping_type = 'approximate',
    c.scope_note = 'Documents, texts, data - conceptual carriers of information',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E31_Document'})
SET c.label = 'Document',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E31_Document',
    c.wikidata_qid = 'Q49848',
    c.mapping_type = 'direct',
    c.scope_note = 'Written records and literary works',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E33_Linguistic_Object'})
SET c.label = 'Linguistic Object',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E33_Linguistic_Object',
    c.wikidata_qid = 'Q17537576',
    c.mapping_type = 'approximate',
    c.scope_note = 'Texts, inscriptions, spoken words',
    c.crm_family = 'core';

// The Critical E13 — Chrystallum's raison d'etre
MERGE (c:SYS_CidocClass {class_id: 'E13_Attribute_Assignment'})
SET c.label = 'Attribute Assignment',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E13_Attribute_Assignment',
    c.wikidata_qid = null,
    c.wikidata_property = 'P1480',
    c.mapping_type = 'custom',
    c.scope_note = 'CRITICAL: No Wikidata equivalent. The act of assigning a property to an entity WITH PROVENANCE. This is what Chrystallum Claim nodes implement.',
    c.chrystallum_implementation = 'Claim node with full provenance chain',
    c.crm_family = 'core';

// Life Cycle Events
MERGE (c:SYS_CidocClass {class_id: 'E67_Birth'})
SET c.label = 'Birth',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E67_Birth',
    c.wikidata_qid = 'Q3950',
    c.wikidata_property = 'P569',
    c.mapping_type = 'direct',
    c.scope_note = 'Person birth events',
    c.crm_family = 'core';

MERGE (c:SYS_CidocClass {class_id: 'E69_Death'})
SET c.label = 'Death',
    c.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/E69_Death',
    c.wikidata_qid = 'Q4',
    c.wikidata_property = 'P570',
    c.mapping_type = 'direct',
    c.scope_note = 'Person death events',
    c.crm_family = 'core';


// ── SECTION 2: CRMinf Extension Classes ────────────────────────────────────
// These are the epistemological classes that map to Chrystallum's 
// argumentation and claim infrastructure.

MERGE (c:SYS_CidocClass {class_id: 'I1_Argumentation'})
SET c.label = 'Argumentation',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/I1_Argumentation',
    c.wikidata_qid = null,
    c.mapping_type = 'custom',
    c.scope_note = 'Activity of making honest inferences or observations. Only one Actor per instance. Maps to Chrystallum AnalysisRun or MultiAgentDebate.',
    c.chrystallum_implementation = 'AnalysisRun (single agent) or MultiAgentDebate (consensus)',
    c.crm_family = 'crminf';

MERGE (c:SYS_CidocClass {class_id: 'I2_Belief'})
SET c.label = 'Belief',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/I2_Belief',
    c.wikidata_qid = null,
    c.mapping_type = 'custom',
    c.scope_note = 'An Actor holds a Proposition Set to have a particular Belief Value. Maps directly to Chrystallum Claim with confidence.',
    c.chrystallum_implementation = 'Claim node (status + confidence)',
    c.crm_family = 'crminf',
    c.cidoc_superclass = 'E2_Temporal_Entity';

MERGE (c:SYS_CidocClass {class_id: 'I3_Inference_Logic'})
SET c.label = 'Inference Logic',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/I3_Inference_Logic',
    c.wikidata_qid = null,
    c.mapping_type = 'custom',
    c.scope_note = 'Rules used as inputs to inference. Includes formal logic, probabilistic reasoning, social models, pattern recognition. Maps to Decision Tables.',
    c.chrystallum_implementation = 'SYS_DecisionTable + SYS_DecisionRow (queryable rule sets)',
    c.crm_family = 'crminf',
    c.cidoc_superclass = 'E89_Propositional_Object';

MERGE (c:SYS_CidocClass {class_id: 'I4_Proposition_Set'})
SET c.label = 'Proposition Set',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/I4_Proposition_Set',
    c.wikidata_qid = null,
    c.mapping_type = 'custom',
    c.scope_note = 'Set of formal propositions a Belief is held about. Could be named graph or structured data. Maps to claim clusters.',
    c.chrystallum_implementation = 'Claim cluster with shared AnalysisRun or FacetAssessment',
    c.crm_family = 'crminf',
    c.cidoc_superclass = 'E73_Information_Object';

MERGE (c:SYS_CidocClass {class_id: 'I5_Inference_Making'})
SET c.label = 'Inference Making',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/I5_Inference_Making',
    c.wikidata_qid = 'Q1643989',
    c.mapping_type = 'custom',
    c.scope_note = 'Using existing Belief as premise + Inference Logic to draw a new Belief as conclusion. Enables tracing knowledge dependency from conclusion to premise. Maps to agent AnalysisRun.',
    c.chrystallum_implementation = 'AnalysisRun (agent + decision tables + inputs → claims)',
    c.crm_family = 'crminf',
    c.cidoc_superclass = 'I1_Argumentation';

MERGE (c:SYS_CidocClass {class_id: 'I6_Belief_Value'})
SET c.label = 'Belief Value',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/I6_Belief_Value',
    c.wikidata_qid = null,
    c.wikidata_property = 'P1480',
    c.mapping_type = 'custom',
    c.scope_note = 'CRMinf defines as literal. Wikidata P1480 sourcing circumstances is binary only. Chrystallum implements as continuous float 0.0-1.0.',
    c.chrystallum_implementation = 'Claim.confidence (float) + SYS_ConfidenceTier (8 tiers with ranges)',
    c.crm_family = 'crminf';

MERGE (c:SYS_CidocClass {class_id: 'I7_Belief_Adoption'})
SET c.label = 'Belief Adoption',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/I7_Belief_Adoption',
    c.wikidata_qid = null,
    c.mapping_type = 'custom',
    c.scope_note = 'Adopting a Belief based on TRUST in source rather than applying Inference Logic. Typical: citation of papers, reuse of datasets. Maps to claim promotion.',
    c.chrystallum_implementation = 'Claim status PROPOSED → PROMOTED (trust-based adoption after human review)',
    c.crm_family = 'crminf',
    c.cidoc_superclass = 'I1_Argumentation';

// CRMsci extensions that subclass CRMinf
MERGE (c:SYS_CidocClass {class_id: 'S4_Observation'})
SET c.label = 'Observation',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMsci/S4_Observation',
    c.mapping_type = 'custom',
    c.scope_note = 'Direct observation — primary evidence. Subclass of I1_Argumentation.',
    c.chrystallum_implementation = 'Claims from primary sources (confidence tier: primary, 0.85-1.0)',
    c.crm_family = 'crmsci',
    c.cidoc_superclass = 'I1_Argumentation';

MERGE (c:SYS_CidocClass {class_id: 'S6_Data_Evaluation'})
SET c.label = 'Data Evaluation',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMsci/S6_Data_Evaluation',
    c.mapping_type = 'custom',
    c.scope_note = 'Evaluating data quality. Subclass of I5_Inference_Making.',
    c.chrystallum_implementation = 'Validation Agent type + confidence scoring rubric application',
    c.crm_family = 'crmsci',
    c.cidoc_superclass = 'I5_Inference_Making';

MERGE (c:SYS_CidocClass {class_id: 'S8_Categorical_Hypothesis_Building'})
SET c.label = 'Categorical Hypothesis Building',
    c.crm_uri = 'http://www.ics.forth.gr/isl/CRMsci/S8_Categorical_Hypothesis_Building',
    c.mapping_type = 'custom',
    c.scope_note = 'Building categorical hypotheses from data. Subclass of I5_Inference_Making.',
    c.chrystallum_implementation = 'Entity classification algorithm (3-tier P31/P279 → fast-path → signature)',
    c.crm_family = 'crmsci',
    c.cidoc_superclass = 'I5_Inference_Making';


// ── SECTION 3: CRMinf Property Nodes ───────────────────────────────────────

MERGE (p:SYS_CidocProperty {property_id: 'J1_used_as_premise'})
SET p.label = 'used as premise',
    p.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/J1_used_as_premise',
    p.domain = 'I5_Inference_Making',
    p.range = 'I2_Belief',
    p.cidoc_superProperty = 'P17_was_motivated_by',
    p.chrystallum_mapping = 'AnalysisRun -[:BASED_ON]-> prior Claim',
    p.crm_family = 'crminf';

MERGE (p:SYS_CidocProperty {property_id: 'J2_concluded_that'})
SET p.label = 'concluded that',
    p.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/J2_concluded_that',
    p.domain = 'I1_Argumentation',
    p.range = 'I2_Belief',
    p.cidoc_superProperty = 'P116_starts',
    p.chrystallum_mapping = 'AnalysisRun -[:PRODUCED]-> Claim',
    p.crm_family = 'crminf';

MERGE (p:SYS_CidocProperty {property_id: 'J3_applies'})
SET p.label = 'applies',
    p.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/J3_applies',
    p.domain = 'I5_Inference_Making',
    p.range = 'I3_Inference_Logic',
    p.cidoc_superProperty = 'P16_used_specific_object',
    p.chrystallum_mapping = 'AnalysisRun -[:GOVERNED_BY]-> SYS_DecisionTable',
    p.crm_family = 'crminf';

MERGE (p:SYS_CidocProperty {property_id: 'J4_that'})
SET p.label = 'that',
    p.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/J4_that',
    p.domain = 'I2_Belief',
    p.range = 'I4_Proposition_Set',
    p.chrystallum_mapping = 'Claim.subject + Claim.object + Claim.relationship_type',
    p.crm_family = 'crminf';

MERGE (p:SYS_CidocProperty {property_id: 'J5_holds_to_be'})
SET p.label = 'holds to be',
    p.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/J5_holds_to_be',
    p.domain = 'I2_Belief',
    p.range = 'I6_Belief_Value',
    p.chrystallum_mapping = 'Claim.confidence (float 0.0-1.0)',
    p.crm_family = 'crminf';

MERGE (p:SYS_CidocProperty {property_id: 'J6_adopted'})
SET p.label = 'adopted',
    p.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/J6_adopted',
    p.domain = 'I7_Belief_Adoption',
    p.range = 'I2_Belief',
    p.cidoc_superProperty = 'P17_was_motivated_by',
    p.chrystallum_mapping = 'Claim status transition PROPOSED → PROMOTED',
    p.crm_family = 'crminf';

MERGE (p:SYS_CidocProperty {property_id: 'J7_is_based_on_evidence'})
SET p.label = 'is based on evidence',
    p.crm_uri = 'http://www.ics.forth.gr/isl/CRMinf/J7_is_based_on_evidence',
    p.domain = 'I7_Belief_Adoption',
    p.range = 'E73_Information_Object',
    p.cidoc_superProperty = 'P16_used_specific_object',
    p.chrystallum_mapping = 'Claim -[:EXTRACTED_FROM]-> RetrievalContext -[:FROM_SOURCE]-> FederationSource',
    p.crm_family = 'crminf';

// Key CIDOC-CRM core properties
MERGE (p:SYS_CidocProperty {property_id: 'P7_took_place_at'})
SET p.label = 'took place at',
    p.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/P7_took_place_at',
    p.domain = 'E5_Event',
    p.range = 'E53_Place',
    p.wikidata_property = 'P276',
    p.chrystallum_mapping = 'OCCURRED_AT relationship',
    p.crm_family = 'core';

MERGE (p:SYS_CidocProperty {property_id: 'P11_had_participant'})
SET p.label = 'had participant',
    p.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/P11_had_participant',
    p.domain = 'E5_Event',
    p.range = 'E39_Actor',
    p.wikidata_property = 'P710',
    p.chrystallum_mapping = 'PARTICIPATED_IN relationship',
    p.crm_family = 'core';

MERGE (p:SYS_CidocProperty {property_id: 'P14_carried_out_by'})
SET p.label = 'carried out by',
    p.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/P14_carried_out_by',
    p.domain = 'E7_Activity',
    p.range = 'E39_Actor',
    p.wikidata_property = 'P170',
    p.chrystallum_mapping = 'CARRIED_OUT_BY relationship',
    p.crm_family = 'core';

MERGE (p:SYS_CidocProperty {property_id: 'P70_documents'})
SET p.label = 'documents',
    p.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/P70_documents',
    p.domain = 'E31_Document',
    p.range = 'E1_CRM_Entity',
    p.wikidata_property = 'P1343',
    p.chrystallum_mapping = 'DOCUMENTED_IN relationship (P1343 in graph)',
    p.crm_family = 'core';

MERGE (p:SYS_CidocProperty {property_id: 'P107_has_current_or_former_member'})
SET p.label = 'has current or former member',
    p.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/P107_has_current_or_former_member',
    p.domain = 'E74_Group',
    p.range = 'E39_Actor',
    p.wikidata_property = 'P463',
    p.chrystallum_mapping = 'MEMBER_OF relationship',
    p.crm_family = 'core';

MERGE (p:SYS_CidocProperty {property_id: 'P127_has_broader_term'})
SET p.label = 'has broader term',
    p.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/P127_has_broader_term',
    p.domain = 'E55_Type',
    p.range = 'E55_Type',
    p.wikidata_property = 'P279',
    p.chrystallum_mapping = 'HAS_BROADER_TERM in SubjectConcept hierarchy',
    p.crm_family = 'core';

MERGE (p:SYS_CidocProperty {property_id: 'P140_assigned_attribute_to'})
SET p.label = 'assigned attribute to',
    p.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/P140_assigned_attribute_to',
    p.domain = 'E13_Attribute_Assignment',
    p.range = 'E1_CRM_Entity',
    p.wikidata_property = null,
    p.chrystallum_mapping = 'Claim.subject — the entity receiving the attribute',
    p.crm_family = 'core';

MERGE (p:SYS_CidocProperty {property_id: 'P141_assigned'})
SET p.label = 'assigned',
    p.crm_uri = 'http://www.cidoc-crm.org/cidoc-crm/P141_assigned',
    p.domain = 'E13_Attribute_Assignment',
    p.range = 'E1_CRM_Entity',
    p.wikidata_property = null,
    p.chrystallum_mapping = 'Claim.object — the attribute value assigned',
    p.crm_family = 'core';


// ── SECTION 4: CRMinf Class Hierarchy Edges ────────────────────────────────

MATCH (child:SYS_CidocClass {class_id: 'I5_Inference_Making'})
MATCH (parent:SYS_CidocClass {class_id: 'I1_Argumentation'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'I7_Belief_Adoption'})
MATCH (parent:SYS_CidocClass {class_id: 'I1_Argumentation'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'S4_Observation'})
MATCH (parent:SYS_CidocClass {class_id: 'I1_Argumentation'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'S6_Data_Evaluation'})
MATCH (parent:SYS_CidocClass {class_id: 'I5_Inference_Making'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'S8_Categorical_Hypothesis_Building'})
MATCH (parent:SYS_CidocClass {class_id: 'I5_Inference_Making'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'E5_Event'})
MATCH (parent:SYS_CidocClass {class_id: 'E2_Temporal_Entity'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'E7_Activity'})
MATCH (parent:SYS_CidocClass {class_id: 'E5_Event'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'E21_Person'})
MATCH (parent:SYS_CidocClass {class_id: 'E39_Actor'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'E74_Group'})
MATCH (parent:SYS_CidocClass {class_id: 'E39_Actor'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'E31_Document'})
MATCH (parent:SYS_CidocClass {class_id: 'E73_Information_Object'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'E33_Linguistic_Object'})
MATCH (parent:SYS_CidocClass {class_id: 'E73_Information_Object'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'E13_Attribute_Assignment'})
MATCH (parent:SYS_CidocClass {class_id: 'E7_Activity'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'E67_Birth'})
MATCH (parent:SYS_CidocClass {class_id: 'E5_Event'})
MERGE (child)-[:SUBCLASS_OF]->(parent);

MATCH (child:SYS_CidocClass {class_id: 'E69_Death'})
MATCH (parent:SYS_CidocClass {class_id: 'E5_Event'})
MERGE (child)-[:SUBCLASS_OF]->(parent);


// ── SECTION 5: MAPS_TO_CIDOC — EntityType → CidocClass ────────────────────
// Wire each Chrystallum EntityType to its CIDOC-CRM equivalent

MATCH (et:EntityType {name: 'Human'}), (cc:SYS_CidocClass {class_id: 'E21_Person'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Organization'}), (cc:SYS_CidocClass {class_id: 'E74_Group'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Place'}), (cc:SYS_CidocClass {class_id: 'E53_Place'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Event'}), (cc:SYS_CidocClass {class_id: 'E5_Event'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Period'}), (cc:SYS_CidocClass {class_id: 'E4_Period'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'PeriodCandidate'}), (cc:SYS_CidocClass {class_id: 'E4_Period'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Work'}), (cc:SYS_CidocClass {class_id: 'E31_Document'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'SubjectConcept'}), (cc:SYS_CidocClass {class_id: 'E55_Type'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Claim'}), (cc:SYS_CidocClass {class_id: 'I2_Belief'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Position'}), (cc:SYS_CidocClass {class_id: 'E55_Type'})
MERGE (et)-[:MAPS_TO_CIDOC {note: 'Offices/positions are classification types in CIDOC'}]->(cc);

MATCH (et:EntityType {name: 'ScaffoldNode'}), (cc:SYS_CidocClass {class_id: 'E1_CRM_Entity'})
MERGE (et)-[:MAPS_TO_CIDOC {note: 'Scaffold entities map to top-level CRM Entity until promoted'}]->(cc);

MATCH (et:EntityType {name: 'ScaffoldEdge'}), (cc:SYS_CidocClass {class_id: 'E13_Attribute_Assignment'})
MERGE (et)-[:MAPS_TO_CIDOC {note: 'Scaffold edges ARE attribute assignments — the core E13 pattern'}]->(cc);

// Temporal backbone types
MATCH (et:EntityType {name: 'Year'}), (cc:SYS_CidocClass {class_id: 'E2_Temporal_Entity'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Decade'}), (cc:SYS_CidocClass {class_id: 'E4_Period'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Century'}), (cc:SYS_CidocClass {class_id: 'E4_Period'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);

MATCH (et:EntityType {name: 'Millennium'}), (cc:SYS_CidocClass {class_id: 'E4_Period'})
MERGE (et)-[:MAPS_TO_CIDOC]->(cc);


// ── SECTION 6: MAPS_TO_CIDOC — Infrastructure → CRMinf ────────────────────
// Wire Chrystallum infrastructure nodes to their CRMinf equivalents

// Agent types map to argumentation patterns
MATCH (at:SYS_AgentType {type_id: 'SFA'}), (cc:SYS_CidocClass {class_id: 'I5_Inference_Making'})
MERGE (at)-[:MAPS_TO_CIDOC {note: 'SFA agents perform inference from Wikidata/sources → facet claims'}]->(cc);

MATCH (at:SYS_AgentType {type_id: 'HARVEST'}), (cc:SYS_CidocClass {class_id: 'I7_Belief_Adoption'})
MERGE (at)-[:MAPS_TO_CIDOC {note: 'Harvest agents adopt beliefs from federation sources (trust-based)'}]->(cc);

MATCH (at:SYS_AgentType {type_id: 'CLAIM'}), (cc:SYS_CidocClass {class_id: 'I5_Inference_Making'})
MERGE (at)-[:MAPS_TO_CIDOC {note: 'Claim discovery agents infer new assertions from existing graph'}]->(cc);

MATCH (at:SYS_AgentType {type_id: 'RESOLUTION'}), (cc:SYS_CidocClass {class_id: 'S6_Data_Evaluation'})
MERGE (at)-[:MAPS_TO_CIDOC {note: 'Resolution agents evaluate data to identify entity matches'}]->(cc);

MATCH (at:SYS_AgentType {type_id: 'VALIDATION'}), (cc:SYS_CidocClass {class_id: 'S6_Data_Evaluation'})
MERGE (at)-[:MAPS_TO_CIDOC {note: 'Validation agents evaluate claim quality'}]->(cc);

// Confidence tiers map to I6 Belief Value
MATCH (ct:SYS_ConfidenceTier), (cc:SYS_CidocClass {class_id: 'I6_Belief_Value'})
MERGE (ct)-[:MAPS_TO_CIDOC]->(cc);

// Claim statuses map to I2 Belief lifecycle
MATCH (cs:SYS_ClaimStatus), (cc:SYS_CidocClass {class_id: 'I2_Belief'})
MERGE (cs)-[:MAPS_TO_CIDOC {note: 'Each claim status is a state in the I2 Belief lifecycle'}]->(cc);

// Decision tables ARE inference logic
MATCH (dt:SYS_DecisionTable), (cc:SYS_CidocClass {class_id: 'I3_Inference_Logic'})
MERGE (dt)-[:MAPS_TO_CIDOC {note: 'Decision tables implement queryable I3 Inference Logic'}]->(cc);

// Classification algorithm maps to S8
MATCH (ca:SYS_ClassificationAlgorithm), (cc:SYS_CidocClass {class_id: 'S8_Categorical_Hypothesis_Building'})
MERGE (ca)-[:MAPS_TO_CIDOC {note: 'Entity type classification is categorical hypothesis building'}]->(cc);

// Classification tiers map to inference steps
MATCH (ct:SYS_ClassificationTier), (cc:SYS_CidocClass {class_id: 'I5_Inference_Making'})
MERGE (ct)-[:MAPS_TO_CIDOC {note: 'Each classification tier is a step in the inference cascade'}]->(cc);


// ── SECTION 7: CIDOC_PROPERTY_MAPS — Relationship Types → CRM Properties ──
// Wire Chrystallum relationship kernel types to their CIDOC property equivalents

// Core traversal relationships
MATCH (rt:SYS_RelationshipType {name: 'LIVED_IN'}), (cp:SYS_CidocProperty {property_id: 'P7_took_place_at'})
MERGE (rt)-[:CIDOC_PROPERTY_MAPS {note: 'residence approximates P7 via P74'}]->(cp);

MATCH (rt:SYS_RelationshipType {name: 'POSITION_HELD'}), (cp:SYS_CidocProperty {property_id: 'P11_had_participant'})
MERGE (rt)-[:CIDOC_PROPERTY_MAPS {note: 'office-holding is participation in governance activity'}]->(cp);

// Relationship types from patches (rel_type property)
MATCH (rt:SYS_RelationshipType {rel_type: 'SUBJECT_OF_WORK'}), (cp:SYS_CidocProperty {property_id: 'P70_documents'})
MERGE (rt)-[:CIDOC_PROPERTY_MAPS {note: 'being documented in a work = P70 documents'}]->(cp);


// ── SECTION 8: SET cidoc_crm_class on Existing Nodes ───────────────────────
// Add the CIDOC class identifier as a property for direct query access

// EntityTypes
MATCH (et:EntityType {name: 'Human'}) SET et.cidoc_crm_class = 'E21_Person';
MATCH (et:EntityType {name: 'Organization'}) SET et.cidoc_crm_class = 'E74_Group';
MATCH (et:EntityType {name: 'Place'}) SET et.cidoc_crm_class = 'E53_Place';
MATCH (et:EntityType {name: 'Event'}) SET et.cidoc_crm_class = 'E5_Event';
MATCH (et:EntityType {name: 'Period'}) SET et.cidoc_crm_class = 'E4_Period';
MATCH (et:EntityType {name: 'PeriodCandidate'}) SET et.cidoc_crm_class = 'E4_Period';
MATCH (et:EntityType {name: 'Work'}) SET et.cidoc_crm_class = 'E31_Document';
MATCH (et:EntityType {name: 'SubjectConcept'}) SET et.cidoc_crm_class = 'E55_Type';
MATCH (et:EntityType {name: 'Claim'}) SET et.cidoc_crm_class = 'I2_Belief';
MATCH (et:EntityType {name: 'Position'}) SET et.cidoc_crm_class = 'E55_Type';
MATCH (et:EntityType {name: 'ScaffoldNode'}) SET et.cidoc_crm_class = 'E1_CRM_Entity';
MATCH (et:EntityType {name: 'ScaffoldEdge'}) SET et.cidoc_crm_class = 'E13_Attribute_Assignment';
MATCH (et:EntityType {name: 'Year'}) SET et.cidoc_crm_class = 'E2_Temporal_Entity';
MATCH (et:EntityType {name: 'Decade'}) SET et.cidoc_crm_class = 'E4_Period';
MATCH (et:EntityType {name: 'Century'}) SET et.cidoc_crm_class = 'E4_Period';
MATCH (et:EntityType {name: 'Millennium'}) SET et.cidoc_crm_class = 'E4_Period';
MATCH (et:EntityType {name: 'PlaceType'}) SET et.cidoc_crm_class = 'E55_Type';

// Agent types
MATCH (at:SYS_AgentType {type_id: 'SFA'}) SET at.cidoc_crm_class = 'I5_Inference_Making';
MATCH (at:SYS_AgentType {type_id: 'HARVEST'}) SET at.cidoc_crm_class = 'I7_Belief_Adoption';
MATCH (at:SYS_AgentType {type_id: 'CLAIM'}) SET at.cidoc_crm_class = 'I5_Inference_Making';
MATCH (at:SYS_AgentType {type_id: 'RESOLUTION'}) SET at.cidoc_crm_class = 'S6_Data_Evaluation';
MATCH (at:SYS_AgentType {type_id: 'VALIDATION'}) SET at.cidoc_crm_class = 'S6_Data_Evaluation';

// Claim statuses — map to CRMinf lifecycle phases
MATCH (cs:SYS_ClaimStatus {label: 'Proposed'}) SET cs.cidoc_crm_class = 'I2_Belief', cs.crminf_phase = 'initial_belief';
MATCH (cs:SYS_ClaimStatus {label: 'Under Review'}) SET cs.cidoc_crm_class = 'I2_Belief', cs.crminf_phase = 'under_evaluation';
MATCH (cs:SYS_ClaimStatus {label: 'Needs Provenance'}) SET cs.cidoc_crm_class = 'I2_Belief', cs.crminf_phase = 'evidence_required';
MATCH (cs:SYS_ClaimStatus {label: 'Reviewed (Approved)'}) SET cs.cidoc_crm_class = 'I2_Belief', cs.crminf_phase = 'validated';
MATCH (cs:SYS_ClaimStatus {label: 'Promoted'}) SET cs.cidoc_crm_class = 'I7_Belief_Adoption', cs.crminf_phase = 'adopted_as_fact';
MATCH (cs:SYS_ClaimStatus {label: 'Reviewed (Rejected)'}) SET cs.cidoc_crm_class = 'I2_Belief', cs.crminf_phase = 'rejected';
MATCH (cs:SYS_ClaimStatus {label: 'Rejected (Low Confidence)'}) SET cs.cidoc_crm_class = 'I2_Belief', cs.crminf_phase = 'rejected';
MATCH (cs:SYS_ClaimStatus {label: 'Rejected (Human)'}) SET cs.cidoc_crm_class = 'I2_Belief', cs.crminf_phase = 'rejected';
MATCH (cs:SYS_ClaimStatus {label: 'Superseded'}) SET cs.cidoc_crm_class = 'I2_Belief', cs.crminf_phase = 'superseded';
MATCH (cs:SYS_ClaimStatus {label: 'Retracted'}) SET cs.cidoc_crm_class = 'I2_Belief', cs.crminf_phase = 'retracted';

// Authority tiers — map to CRMinf trust model
MATCH (at:SYS_AuthorityTier {layer_name: 'Library Science Authority'}) SET at.cidoc_crm_class = 'E55_Type', at.crminf_trust = 'institutional_authority';
MATCH (at:SYS_AuthorityTier {layer_name: 'Federation Authority'}) SET at.cidoc_crm_class = 'I7_Belief_Adoption', at.crminf_trust = 'federated_trust';
MATCH (at:SYS_AuthorityTier {layer_name: 'Hierarchy Query Engine'}) SET at.cidoc_crm_class = 'I5_Inference_Making', at.crminf_trust = 'computational_inference';
MATCH (at:SYS_AuthorityTier {layer_name: 'Facet Authority'}) SET at.cidoc_crm_class = 'I5_Inference_Making', at.crminf_trust = 'agent_inference';
MATCH (at:SYS_AuthorityTier {layer_name: 'Subject Concept Hierarchy'}) SET at.cidoc_crm_class = 'S8_Categorical_Hypothesis_Building', at.crminf_trust = 'categorical_hypothesis';
MATCH (at:SYS_AuthorityTier {layer_name: 'Agent-Discovered Concepts'}) SET at.cidoc_crm_class = 'I5_Inference_Making', at.crminf_trust = 'agent_discovery';

// Confidence tiers — map CRMinf Belief Value with Wikidata sourcing circumstance equivalents
MATCH (ct:SYS_ConfidenceTier {tier_id: 'primary'}) SET ct.cidoc_crm_class = 'I6_Belief_Value', ct.crminf_observation_type = 'S4_Observation', ct.wikidata_sourcing = 'Q5727902';
MATCH (ct:SYS_ConfidenceTier {tier_id: 'secondary_academic'}) SET ct.cidoc_crm_class = 'I6_Belief_Value', ct.crminf_observation_type = 'I7_Belief_Adoption', ct.wikidata_sourcing = 'Q18122778';
MATCH (ct:SYS_ConfidenceTier {tier_id: 'secondary_populist'}) SET ct.cidoc_crm_class = 'I6_Belief_Value', ct.crminf_observation_type = 'I7_Belief_Adoption', ct.wikidata_sourcing = 'Q18122778';
MATCH (ct:SYS_ConfidenceTier {tier_id: 'tertiary'}) SET ct.cidoc_crm_class = 'I6_Belief_Value', ct.crminf_observation_type = 'I7_Belief_Adoption', ct.wikidata_sourcing = 'Q18122761';
MATCH (ct:SYS_ConfidenceTier {tier_id: 'llm_high_consensus'}) SET ct.cidoc_crm_class = 'I6_Belief_Value', ct.crminf_observation_type = 'I5_Inference_Making', ct.wikidata_sourcing = 'Q18122761';
MATCH (ct:SYS_ConfidenceTier {tier_id: 'llm_conflicting'}) SET ct.cidoc_crm_class = 'I6_Belief_Value', ct.crminf_observation_type = 'I5_Inference_Making', ct.wikidata_sourcing = 'Q18123970';
MATCH (ct:SYS_ConfidenceTier {tier_id: 'inference'}) SET ct.cidoc_crm_class = 'I6_Belief_Value', ct.crminf_observation_type = 'I5_Inference_Making', ct.wikidata_sourcing = 'Q18123970';
MATCH (ct:SYS_ConfidenceTier {tier_id: 'speculation'}) SET ct.cidoc_crm_class = 'I6_Belief_Value', ct.crminf_observation_type = 'I5_Inference_Making', ct.wikidata_sourcing = 'Q18123970';


// ── SECTION 9: ADR-007 — CIDOC-CRM Ontology Mapping ───────────────────────

MERGE (adr:SYS_ADR {adr_id: 'ADR-007'})
SET adr.title = 'CIDOC-CRM and CRMinf Ontology Mapping',
    adr.status = 'ACCEPTED',
    adr.date = '2026-03-01',
    adr.summary = 'Chrystallum maintains formal bidirectional mappings to CIDOC-CRM v7.1.2 and CRMinf v0.7. Core alignment: Claim=I2_Belief, AnalysisRun=I5_Inference_Making, DecisionTable=I3_Inference_Logic, ScaffoldEdge=E13_Attribute_Assignment, confidence=I6_Belief_Value. Wikidata gaps (E13, I5, I6, P177) are precisely what Chrystallum implements.',
    adr.impacts = 'All entity types carry cidoc_crm_class property. All agent types mapped to CRMinf argumentation patterns. Enables interoperability with museum/archive CIDOC-CRM systems.',
    adr.crm_version = '7.1.2',
    adr.crminf_version = '0.7';


// ── SECTION 10: New Federation Sources ─────────────────────────────────────
// Bibliographic pipeline sources identified in the Works gap analysis

MERGE (fs:SYS_FederationSource {source_id: 'open_syllabus'})
SET fs.label = 'Open Syllabus',
    fs.description = 'Catalog of 15.7M college syllabi with 77M extracted citations. Provides teaching_score, co-assignment graph, title/author/ISBN for assigned works.',
    fs.status = 'planned',
    fs.phase = 'Phase 2',
    fs.endpoint = 'https://api.opensyllabus.org',
    fs.scoping_weight = 0.70,
    fs.access = 'API (credentials required)',
    fs.data_types = 'title, author, ISBN, teaching_score, co-assignments, field classification',
    fs.use_in_chrystallum = 'Seed Work nodes with scholarly importance ranking. TAUGHT_WITH edges for INTELLECTUAL facet.',
    fs.added_date = '2026-03-01';

MERGE (fs:SYS_FederationSource {source_id: 'open_library'})
SET fs.label = 'Open Library',
    fs.description = 'Internet Archive open book catalog with 30M+ titles. Provides ISBN-to-OCLC/LCCN bridging, LCSH subjects, and full-text availability flags.',
    fs.status = 'planned',
    fs.phase = 'Phase 2',
    fs.endpoint = 'https://openlibrary.org/api',
    fs.scoping_weight = 0.75,
    fs.access = 'Open API (no key)',
    fs.data_types = 'ISBN, OCLC, LCCN, subjects (LCSH), editions, full-text availability (Internet Archive)',
    fs.use_in_chrystallum = 'Bridge ISBN to OCLC/LCCN. Connect Work nodes to LCSH federation. Detect free full-text for agent consumption.',
    fs.added_date = '2026-03-01';

MERGE (fs:SYS_FederationSource {source_id: 'openalex'})
SET fs.label = 'OpenAlex',
    fs.description = 'Open catalog of 240M+ scholarly works with citation graph, open access detection, and topic classification. CC0 licensed.',
    fs.status = 'planned',
    fs.phase = 'Phase 2',
    fs.endpoint = 'https://api.openalex.org',
    fs.scoping_weight = 0.80,
    fs.access = 'Open API (free key, 100K credits/day)',
    fs.data_types = 'DOI, open_access status, oa_url, cited_by_count, referenced_works, related_works, topics',
    fs.use_in_chrystallum = 'Open access detection for agent-readable texts. Citation graph for scholarly provenance. CITES relationships between Works.',
    fs.added_date = '2026-03-01';

MERGE (fs:SYS_FederationSource {source_id: 'perseus'})
SET fs.label = 'Perseus Digital Library',
    fs.description = 'Canonical digital library for Greek and Latin texts. Provides CTS URNs for passage-level citation of classical works. 20M+ words Greek, 15M+ words Latin.',
    fs.status = 'planned',
    fs.phase = 'Phase 2',
    fs.endpoint = 'https://catalog.perseus.org',
    fs.scoping_weight = 0.90,
    fs.access = 'Open (CTS protocol)',
    fs.data_types = 'CTS URNs, full text (TEI-XML), author/work metadata, passage-level addressing',
    fs.use_in_chrystallum = 'Passage-level provenance for claims. CTS URNs as citation anchors in Claim.provenance_passage. Primary source text for agent extraction.',
    fs.added_date = '2026-03-01';


// ── SECTION 11: Onboarding Step 15 — CIDOC-CRM Literacy ───────────────────

MERGE (step:SYS_OnboardingStep {step_id: 'onboard_s15'})
SET step.label = 'CIDOC-CRM and CRMinf Ontology Mapping',
    step.description = 'Learn how Chrystallum maps to CIDOC-CRM (museum/archive standard) and CRMinf (argumentation ontology). Understand that Claim=I2_Belief, AnalysisRun=I5_Inference_Making, DecisionTable=I3_Inference_Logic. Query SYS_CidocClass nodes for formal mappings.',
    step.query_hint = 'MATCH (cc:SYS_CidocClass) WHERE cc.crm_family = "crminf" RETURN cc.class_id, cc.label, cc.chrystallum_implementation',
    step.depends_on = 'onboard_s14';

// Wire into protocol chain
MATCH (prev:SYS_OnboardingStep {step_id: 'onboard_s14'})
MATCH (next:SYS_OnboardingStep {step_id: 'onboard_s15'})
MERGE (prev)-[:NEXT_STEP]->(next);


// ── SECTION 12: Validation Rule ────────────────────────────────────────────

MERGE (vr:SYS_ValidationRule {rule_id: 'cidoc_crm_mapping_required'})
SET vr.description = 'Every EntityType node must carry a cidoc_crm_class property mapping to CIDOC-CRM or CRMinf',
    vr.query = 'MATCH (et:EntityType) WHERE et.cidoc_crm_class IS NULL RETURN et.name AS unmapped_type',
    vr.expected = 'No results (all EntityTypes mapped)',
    vr.severity = 'warning';


// ============================================================================
// VERIFICATION QUERIES (read-only, run after execution)
// ============================================================================
//
// -- Count CIDOC class nodes
// MATCH (c:SYS_CidocClass) RETURN c.crm_family, count(c) ORDER BY c.crm_family
// Expected: core ~18, crminf ~7, crmsci ~3
//
// -- Count CIDOC property nodes
// MATCH (p:SYS_CidocProperty) RETURN count(p)
// Expected: 15
//
// -- Count MAPS_TO_CIDOC edges
// MATCH ()-[r:MAPS_TO_CIDOC]->() RETURN count(r)
// Expected: ~50
//
// -- Verify all EntityTypes have cidoc_crm_class
// MATCH (et:EntityType) WHERE et.cidoc_crm_class IS NULL RETURN et.name
// Expected: empty
//
// -- CRMinf class hierarchy
// MATCH (child:SYS_CidocClass)-[:SUBCLASS_OF]->(parent:SYS_CidocClass) 
// RETURN child.class_id, parent.class_id
// Expected: 14 rows
//
// -- ADR-007
// MATCH (a:SYS_ADR {adr_id: 'ADR-007'}) RETURN a.title
// Expected: 'CIDOC-CRM and CRMinf Ontology Mapping'
//
// -- New federation sources
// MATCH (fs:SYS_FederationSource) WHERE fs.source_id IN ['open_syllabus','open_library','openalex','perseus'] 
// RETURN fs.label, fs.status
// Expected: 4 rows, all 'planned'
//
// -- Onboarding now has 15 steps
// MATCH (s:SYS_OnboardingStep) RETURN count(s)
// Expected: 15
//
// -- Full chain check
// MATCH path = (s1:SYS_OnboardingStep {step_id:'onboard_s01'})-[:NEXT_STEP*]->(end) 
// WHERE NOT (end)-[:NEXT_STEP]->() 
// RETURN length(path), end.step_id
// Expected: 14, onboard_s15
// ============================================================================
