// ============================================================================
// CHRYSTALLUM: ADR COMPLIANCE PATCHES
// ============================================================================
// File: 14_adr_compliance_patches.cypher
// Purpose: Layer corrections and additions on top of scripts 10-13 to align
//          with the formal ADR decisions (001-006), the DMN decision table
//          spec, the entity classification decision tree, and the
//          confidence scoring rubric.
// Depends: Scripts 10-13 already loaded
// Safe: All MERGE - idempotent
// ============================================================================


// ============================================================================
// PATCH 1: FIX FACET COUNT VALIDATION RULE (ADR-004: 18 facets)
// ============================================================================
// ADR-004 canonicalizes 18 facets including BIOGRAPHIC.
// Script 10 incorrectly said 17.

MATCH (vr:SYS_ValidationRule {name: 'facet_count'})
SET vr.rationale = 'Chrystallum defines exactly 18 canonical facets (ADR-004). BIOGRAPHIC was added 2026-02-16.',
    vr.check_description = 'MATCH (f:Facet) WITH f.key AS k, count(f) AS cnt RETURN count(DISTINCT k) = 18.',
    vr.adr_reference = 'ADR-004',
    vr.updated = datetime();


// ============================================================================
// PATCH 2: FIX EXEMPLAR CIPHER (ADR-001: Content-Only Cipher)
// ============================================================================
// ADR-001 mandates: cipher includes ONLY subject, object, relationship,
// temporal data, source work, passage hash, facet_id.
// EXCLUDES: confidence, agent, timestamp.
// The exemplar cipher 'ASSIGN(Q13377, FACET:MILITARY, CONF:0.95)' violates
// this by including confidence.

MATCH (c:Claim {claim_id: 'clm_exemplar_001'})
SET c.cipher = 'SHA256(subject=Q13377|object=MILITARY|rel=ASSIGNED_TO_FACET|facet=MILITARY)',
    c.cipher_note = 'Content-only hash per ADR-001. Excludes confidence, agent, timestamp. Same assertion by different agents = same cipher = automatic deduplication.',
    c.updated = datetime();


// ============================================================================
// PATCH 3: ADD SCAFFOLD LAYER TO META-SCHEMA (ADR-006)
// ============================================================================
// ADR-006 defines a mandatory scaffold/canonical boundary.
// Agents write to ScaffoldNode/ScaffoldEdge first.
// Only the promotion service creates canonical nodes.

// Scaffold EntityTypes
MERGE (et:EntityType {name: 'ScaffoldNode'})
SET et.tier = 5,
    et.required_properties = ['entity_id', 'label', 'analysis_run_id', 'source_qid'],
    et.optional_properties = ['entity_type_candidate', 'confidence', 'properties_json'],
    et.identity_keys = ['entity_id'],
    et.canonical_outbound = [],
    et.temporal = false,
    et.authority_sources = [],
    et.description = 'Pre-promotion staging node (ADR-006). Agents write ScaffoldNodes during bootstrap/discovery. Distinct label from canonical entities. Promotion service validates and merges into canonical graph.',
    et.adr_reference = 'ADR-006',
    et.updated = datetime();

MERGE (et2:EntityType {name: 'ScaffoldEdge'})
SET et2.tier = 5,
    et2.required_properties = ['edge_id', 'analysis_run_id', 'relationship_type', 'wd_property', 'direction', 'confidence', 'created_at'],
    et2.optional_properties = ['source_entity_id', 'target_entity_id'],
    et2.identity_keys = ['edge_id'],
    et2.canonical_outbound = ['FROM', 'TO'],
    et2.temporal = false,
    et2.authority_sources = [],
    et2.description = 'Pre-promotion staging edge-as-node (ADR-006). ScaffoldEdge pattern: (e:ScaffoldEdge)-[:FROM]->(s:ScaffoldNode), (e:ScaffoldEdge)-[:TO]->(o:ScaffoldNode). Required properties include wd_property for Wikidata alignment and direction for edge semantics.',
    et2.adr_reference = 'ADR-006',
    et2.updated = datetime();

// Scaffold relationship types
MERGE (rt1:SYS_RelationshipType {name: 'FROM'})
SET rt1.semantic = 'scaffold_source',
    rt1.source_label = 'ScaffoldEdge',
    rt1.target_label = 'ScaffoldNode',
    rt1.description = 'Source end of a scaffold edge-as-node (ADR-006).',
    rt1.cardinality = 'many_to_one',
    rt1.updated = datetime();

MERGE (rt2:SYS_RelationshipType {name: 'TO'})
SET rt2.semantic = 'scaffold_target',
    rt2.source_label = 'ScaffoldEdge',
    rt2.target_label = 'ScaffoldNode',
    rt2.description = 'Target end of a scaffold edge-as-node (ADR-006).',
    rt2.cardinality = 'many_to_one',
    rt2.updated = datetime();

// Promotion relationship type
MERGE (rt3:SYS_RelationshipType {name: 'PROMOTED_FROM'})
SET rt3.semantic = 'provenance',
    rt3.source_label = 'Entity',
    rt3.target_label = 'ScaffoldNode',
    rt3.description = 'Links a promoted canonical entity back to its scaffold origin (ADR-006). Created by promotion service.',
    rt3.cardinality = 'many_to_one',
    rt3.updated = datetime();

// Promotion contract as validation rule
MERGE (vr:SYS_ValidationRule {name: 'scaffold_canonical_boundary'})
SET vr.applies_to = 'ScaffoldNode',
    vr.severity = 'CRITICAL',
    vr.rationale = 'ADR-006: Agents NEVER write canonical labels directly. All agent output goes to ScaffoldNode/ScaffoldEdge. Promotion service validates against filter/meta-ceiling policy before merging canonical nodes.',
    vr.check_description = 'Agent AnalysisRuns should produce only ScaffoldNode/ScaffoldEdge outputs, never direct Human/Place/Event/etc. nodes.',
    vr.adr_reference = 'ADR-006',
    vr.updated = datetime();

// Bootstrap traversal controls (ADR-006 Y.5)
MERGE (tc:SYS_QueryPattern {name: 'bootstrap_traversal_controls'})
SET tc.description = 'V0 bootstrap traversal depth limits (ADR-006 Y.5). Controls how far agents traverse Wikidata during discovery.',
    tc.applicable_to = ['Agent', 'AnalysisRun'],
    tc.parameters = '{"upward_p31_p279_depth": 4, "lateral_mapped_property_hops": 2, "downward_inverse_p279_depth": 2, "inverse_p31": "sampling_only_bounded"}',
    tc.cypher_template = 'Traversal depth controlled by SYS_Threshold max_hops_p279 (currently 4). Hard caps and NOT-filters must be logged with truncation metadata.',
    tc.adr_reference = 'ADR-006',
    tc.updated = datetime();


// ============================================================================
// PATCH 4: EXPAND RELATIONSHIP KERNEL TO 48 TYPES (ADR-002)
// ============================================================================
// Script 10 defined 22 relationship types. ADR-002 specifies a v1.0 kernel
// of 48 types across 7 functional categories. Adding the missing ones.
// (Script 10 types are preserved — these are additive MERGEs.)

UNWIND [
  // === Core Traversal (12) — most already in script 10, adding missing ===
  {name: 'PARTICIPATED_IN', semantic: 'participation', source: 'Human', target: 'Event', wd: 'P710', description: 'Person participated in event.', cardinality: 'many_to_many', kernel_category: 'core_traversal'},
  {name: 'HAD_PARTICIPANT', semantic: 'participation', source: 'Event', target: 'Human', wd: 'P710', description: 'Event had this participant (inverse).', cardinality: 'many_to_many', kernel_category: 'core_traversal'},
  {name: 'BIRTHPLACE_OF', semantic: 'spatial', source: 'Place', target: 'Human', wd: 'P19', description: 'Place is birthplace of person (inverse of BORN_IN).', cardinality: 'one_to_many', kernel_category: 'core_traversal'},
  {name: 'DEATH_PLACE_OF', semantic: 'spatial', source: 'Place', target: 'Human', wd: 'P20', description: 'Place is death location of person (inverse of DIED_IN).', cardinality: 'one_to_many', kernel_category: 'core_traversal'},
  {name: 'LOCATION_OF', semantic: 'spatial_hierarchy', source: 'Place', target: 'Place', wd: 'P131', description: 'Inverse of LOCATED_IN.', cardinality: 'one_to_many', kernel_category: 'core_traversal'},
  {name: 'AUTHOR', semantic: 'authorship', source: 'Human', target: 'Work', wd: 'P50', description: 'Person is author of work.', cardinality: 'many_to_many', kernel_category: 'core_traversal'},
  {name: 'WORK_OF', semantic: 'authorship', source: 'Work', target: 'Human', wd: 'P50', description: 'Work authored by person (inverse).', cardinality: 'many_to_one', kernel_category: 'core_traversal'},
  {name: 'WITNESSED_EVENT', semantic: 'observation', source: 'Human', target: 'Event', wd: 'P1441', description: 'Person witnessed event.', cardinality: 'many_to_many', kernel_category: 'core_traversal'},
  {name: 'WITNESSED_BY', semantic: 'observation', source: 'Event', target: 'Human', wd: 'P1441', description: 'Event witnessed by person (inverse).', cardinality: 'many_to_many', kernel_category: 'core_traversal'},

  // === Familial (10) ===
  {name: 'PARENT_OF', semantic: 'kinship', source: 'Human', target: 'Human', wd: 'P40', description: 'Parent of child.', cardinality: 'one_to_many', kernel_category: 'familial'},
  {name: 'CHILD_OF', semantic: 'kinship', source: 'Human', target: 'Human', wd: 'P40', description: 'Person is child of parent.', cardinality: 'many_to_one', kernel_category: 'familial'},
  {name: 'FATHER_OF', semantic: 'kinship', source: 'Human', target: 'Human', wd: 'P40', description: 'Father of child. Enables patrilineal queries.', cardinality: 'one_to_many', kernel_category: 'familial'},
  {name: 'MOTHER_OF', semantic: 'kinship', source: 'Human', target: 'Human', wd: 'P40', description: 'Mother of child. Enables matrilineal queries.', cardinality: 'one_to_many', kernel_category: 'familial'},
  {name: 'SIBLING_OF', semantic: 'kinship', source: 'Human', target: 'Human', wd: 'P3373', description: 'Person is sibling (symmetric).', cardinality: 'many_to_many', kernel_category: 'familial'},
  {name: 'SPOUSE_OF', semantic: 'kinship', source: 'Human', target: 'Human', wd: 'P26', description: 'Person is spouse (symmetric).', cardinality: 'many_to_many', kernel_category: 'familial'},
  {name: 'GRANDPARENT_OF', semantic: 'kinship', source: 'Human', target: 'Human', wd: null, description: 'Grandparent of grandchild.', cardinality: 'one_to_many', kernel_category: 'familial'},
  {name: 'GRANDCHILD_OF', semantic: 'kinship', source: 'Human', target: 'Human', wd: null, description: 'Grandchild of grandparent.', cardinality: 'many_to_one', kernel_category: 'familial'},
  // MEMBER_OF_GENS and HAS_GENS_MEMBER already in script 10 as PART_OF_GENS — add canonical names
  {name: 'HAS_GENS_MEMBER', semantic: 'kinship', source: 'Gens', target: 'Human', wd: 'P53', description: 'Gens has this member (inverse of MEMBER_OF_GENS).', cardinality: 'one_to_many', kernel_category: 'familial'},

  // === Political (10) ===
  {name: 'CONTROLLED', semantic: 'political', source: 'Human', target: 'Place', wd: 'P17', description: 'Entity controlled territory.', cardinality: 'many_to_many', kernel_category: 'political'},
  {name: 'CONTROLLED_BY', semantic: 'political', source: 'Place', target: 'Human', wd: 'P17', description: 'Territory controlled by entity (inverse).', cardinality: 'many_to_one', kernel_category: 'political'},
  {name: 'ALLIED_WITH', semantic: 'political', source: 'Organization', target: 'Organization', wd: null, description: 'Formal or strategic alliance.', cardinality: 'many_to_many', kernel_category: 'political'},
  {name: 'CONQUERED', semantic: 'political', source: 'Human', target: 'Place', wd: null, description: 'Entity conquered territory.', cardinality: 'many_to_many', kernel_category: 'political'},
  {name: 'CONQUERED_BY', semantic: 'political', source: 'Place', target: 'Human', wd: null, description: 'Territory conquered by entity (inverse).', cardinality: 'many_to_one', kernel_category: 'political'},
  {name: 'APPOINTED', semantic: 'political', source: 'Human', target: 'Human', wd: 'P39', description: 'Entity appointed person to office.', cardinality: 'many_to_many', kernel_category: 'political'},
  {name: 'APPOINTED_BY', semantic: 'political', source: 'Human', target: 'Human', wd: 'P39', description: 'Person appointed by entity (inverse).', cardinality: 'many_to_one', kernel_category: 'political'},
  {name: 'COLLAPSED', semantic: 'political', source: 'Organization', target: 'Year', wd: 'P576', description: 'Political entity ceased to exist.', cardinality: 'many_to_one', kernel_category: 'political'},
  {name: 'CAUSED_COLLAPSE_OF', semantic: 'political', source: 'Human', target: 'Organization', wd: 'P576', description: 'Entity caused collapse of organization.', cardinality: 'many_to_one', kernel_category: 'political'},
  {name: 'DECLARED_FOR', semantic: 'political', source: 'Human', target: 'Human', wd: null, description: 'Declared support or allegiance.', cardinality: 'many_to_many', kernel_category: 'political'},

  // === Military (7) ===
  {name: 'FOUGHT_IN', semantic: 'military', source: 'Human', target: 'Event', wd: 'P607', description: 'Participated in battle or war.', cardinality: 'many_to_many', kernel_category: 'military'},
  {name: 'BATTLE_PARTICIPANT', semantic: 'military', source: 'Event', target: 'Human', wd: 'P607', description: 'Battle had this participant (inverse).', cardinality: 'many_to_many', kernel_category: 'military'},
  {name: 'DEFEATED', semantic: 'military', source: 'Human', target: 'Human', wd: null, description: 'Defeated opponent.', cardinality: 'many_to_many', kernel_category: 'military'},
  {name: 'DEFEATED_BY', semantic: 'military', source: 'Human', target: 'Human', wd: null, description: 'Was defeated by opponent.', cardinality: 'many_to_one', kernel_category: 'military'},
  {name: 'BESIEGED', semantic: 'military', source: 'Human', target: 'Place', wd: null, description: 'Laid siege to place.', cardinality: 'many_to_many', kernel_category: 'military'},
  {name: 'BESIEGED_BY', semantic: 'military', source: 'Place', target: 'Human', wd: null, description: 'Place besieged by entity.', cardinality: 'many_to_one', kernel_category: 'military'},
  {name: 'SERVED_UNDER', semantic: 'military', source: 'Human', target: 'Human', wd: null, description: 'Served under commander.', cardinality: 'many_to_one', kernel_category: 'military'},

  // === Geographic (7) — LIVED_IN already in script 10 ===
  {name: 'RESIDENCE_OF', semantic: 'spatial', source: 'Place', target: 'Human', wd: 'P551', description: 'Place was residence of person (inverse of LIVED_IN).', cardinality: 'one_to_many', kernel_category: 'geographic'},
  {name: 'FOUNDED', semantic: 'spatial', source: 'Human', target: 'Place', wd: 'P112', description: 'Established place or institution.', cardinality: 'many_to_many', kernel_category: 'geographic'},
  {name: 'MIGRATED_FROM', semantic: 'movement', source: 'Human', target: 'Place', wd: null, description: 'Group migrated from place.', cardinality: 'many_to_many', kernel_category: 'geographic'},
  {name: 'MIGRATED_TO', semantic: 'movement', source: 'Human', target: 'Place', wd: null, description: 'Group migrated to place.', cardinality: 'many_to_many', kernel_category: 'geographic'},
  {name: 'FLED_TO', semantic: 'movement', source: 'Human', target: 'Place', wd: null, description: 'Fled to location (exile or escape).', cardinality: 'many_to_many', kernel_category: 'geographic'},
  {name: 'EXILED', semantic: 'movement', source: 'Human', target: 'Place', wd: null, description: 'Person exiled to place.', cardinality: 'many_to_many', kernel_category: 'geographic'},

  // === Authorship & Attribution (7) ===
  {name: 'CREATOR', semantic: 'authorship', source: 'Human', target: 'Work', wd: 'P170', description: 'Created by.', cardinality: 'many_to_many', kernel_category: 'authorship'},
  {name: 'CREATION_OF', semantic: 'authorship', source: 'Work', target: 'Human', wd: 'P170', description: 'Created by (inverse).', cardinality: 'many_to_one', kernel_category: 'authorship'},
  {name: 'DESCRIBES', semantic: 'reference', source: 'Work', target: 'Entity', wd: null, description: 'Citation describes entity.', cardinality: 'many_to_many', kernel_category: 'authorship'},
  {name: 'MENTIONS', semantic: 'reference', source: 'Work', target: 'Entity', wd: null, description: 'Citation mentions entity.', cardinality: 'many_to_many', kernel_category: 'authorship'},
  {name: 'NAMED_AFTER', semantic: 'reference', source: 'Entity', target: 'Entity', wd: 'P138', description: 'Named for.', cardinality: 'many_to_one', kernel_category: 'authorship'},
  {name: 'NAMESAKE_OF', semantic: 'reference', source: 'Entity', target: 'Entity', wd: 'P138', description: 'Is namesake of (inverse).', cardinality: 'one_to_many', kernel_category: 'authorship'},
  {name: 'DISCOVERED_BY', semantic: 'authorship', source: 'Entity', target: 'Human', wd: 'P61', description: 'Discovered by.', cardinality: 'many_to_one', kernel_category: 'authorship'},

  // === Temporal & Institutional (5) ===
  {name: 'LEGITIMATED', semantic: 'institutional', source: 'Organization', target: 'Human', wd: null, description: 'Institution legitimated authority.', cardinality: 'many_to_many', kernel_category: 'institutional'},
  {name: 'LEGITIMATED_BY', semantic: 'institutional', source: 'Human', target: 'Organization', wd: null, description: 'Authority legitimated by institution.', cardinality: 'many_to_one', kernel_category: 'institutional'},
  {name: 'REFORMED', semantic: 'institutional', source: 'Human', target: 'Organization', wd: null, description: 'Reformed institution or system.', cardinality: 'many_to_many', kernel_category: 'institutional'},
  {name: 'ADHERES_TO', semantic: 'institutional', source: 'Human', target: 'SubjectConcept', wd: 'P1142', description: 'Person/org adheres to ideology.', cardinality: 'many_to_many', kernel_category: 'institutional'},
  {name: 'IDEOLOGY_OF', semantic: 'institutional', source: 'SubjectConcept', target: 'Human', wd: 'P1142', description: 'Ideology adhered to by person/org (inverse).', cardinality: 'one_to_many', kernel_category: 'institutional'}
] AS rel
MERGE (r:SYS_RelationshipType {name: rel.name})
SET r.semantic = rel.semantic,
    r.source_label = rel.source,
    r.target_label = rel.target,
    r.description = rel.description,
    r.cardinality = rel.cardinality,
    r.wikidata_property = rel.wd,
    r.kernel_category = rel.kernel_category,
    r.kernel_version = 'v1.0',
    r.adr_reference = 'ADR-002',
    r.updated = datetime();

// Tag the script-10 relationships with kernel metadata too
MATCH (r:SYS_RelationshipType)
WHERE r.kernel_version IS NULL
SET r.kernel_version = 'v1.0',
    r.kernel_category = CASE
      WHEN r.semantic IN ['temporal_sequence', 'temporal_hierarchy'] THEN 'temporal_backbone'
      WHEN r.semantic IN ['temporal_anchor'] THEN 'core_traversal'
      WHEN r.semantic IN ['spatial', 'spatial_hierarchy'] THEN 'core_traversal'
      WHEN r.semantic IN ['temporal_context'] THEN 'core_traversal'
      WHEN r.semantic = 'hierarchy' THEN 'core_traversal'
      WHEN r.semantic = 'kinship' THEN 'familial'
      WHEN r.semantic = 'institutional' THEN 'institutional'
      WHEN r.semantic IN ['reference', 'provenance', 'authorship'] THEN 'authorship'
      WHEN r.semantic = 'capability' THEN 'agent_pipeline'
      WHEN r.semantic = 'execution' THEN 'agent_pipeline'
      WHEN r.semantic = 'output' THEN 'agent_pipeline'
      WHEN r.semantic = 'classification' THEN 'geo_semantic'
      ELSE 'other'
    END,
    r.updated = datetime();


// ============================================================================
// PATCH 5: CONFIDENCE SCORING RUBRIC (Queryable Reference)
// ============================================================================
// Source: confidence_scoring_rubric.md
// Agents need to know source quality tiers and modifiers to compute
// confidence for their claims.

// Source quality tiers
UNWIND [
  {tier: 'primary',              floor: 0.85, ceiling: 1.0,  midpoint: 0.925, description: 'Direct evidence: legal documents, inscriptions, coins, contemporary records. Minimal interpretation.'},
  {tier: 'secondary_academic',   floor: 0.75, ceiling: 0.90, midpoint: 0.825, description: 'Peer-reviewed journal, monograph by subject expert. Interpreted by expert, citable.'},
  {tier: 'secondary_populist',   floor: 0.65, ceiling: 0.75, midpoint: 0.70,  description: 'Wikipedia articles, general history books. Well-researched but broader audience.'},
  {tier: 'tertiary',             floor: 0.50, ceiling: 0.70, midpoint: 0.60,  description: 'Textbooks, survey articles, synthesis works. Accurate but at distance from primary sources.'},
  {tier: 'llm_high_consensus',   floor: 0.70, ceiling: 0.85, midpoint: 0.775, description: 'LLM synthesis trained on multiple expert sources, no contradictions. Generated knowledge.'},
  {tier: 'llm_conflicting',      floor: 0.40, ceiling: 0.60, midpoint: 0.50,  description: 'LLM synthesis trained on contradictory sources, interpretive question. Epistemic uncertainty.'},
  {tier: 'inference',            floor: 0.30, ceiling: 0.50, midpoint: 0.40,  description: 'Plausible but not directly sourced. Reasonable inference, could be wrong.'},
  {tier: 'speculation',          floor: 0.10, ceiling: 0.30, midpoint: 0.20,  description: 'Educated guess, admitted as such. Not suitable for graph without multi-SME debate.'}
] AS t
MERGE (ct:SYS_ConfidenceTier {tier_id: t.tier})
SET ct.label = t.tier,
    ct.floor = t.floor,
    ct.ceiling = t.ceiling,
    ct.midpoint = t.midpoint,
    ct.description = t.description,
    ct.updated = datetime();

// Confidence modifiers
UNWIND [
  {modifier_id: 'multi_source_agreement',    value:  0.05, condition: '3+ independent sources with same claim'},
  {modifier_id: 'primary_source_ambiguous',   value: -0.10, condition: 'Source admits uncertainty or is unclear'},
  {modifier_id: 'archaeological_confirms',    value:  0.10, condition: 'Material/archaeological evidence confirms claim'},
  {modifier_id: 'weak_consensus',             value: -0.15, condition: 'Historiographical consensus is weak or disputed'},
  {modifier_id: 'contemporary_source',        value:  0.05, condition: 'Source was written during event period'},
  {modifier_id: 'later_interpretation',       value: -0.05, condition: 'Source written centuries after event'},
  {modifier_id: 'conflicting_sources',        value: -0.20, condition: 'Multiple sources directly contradict each other'}
] AS m
MERGE (cm:SYS_ConfidenceModifier {modifier_id: m.modifier_id})
SET cm.value = m.value,
    cm.condition = m.condition,
    cm.updated = datetime();

// CRMinf vs Chrystallum decision routing
MERGE (rd:SYS_QueryPattern {name: 'crminf_vs_chrystallum_routing'})
SET rd.description = 'Decision logic for whether a claim uses simple Chrystallum properties or requires CRMinf explicit reasoning chains. Based on confidence_scoring_rubric.md.',
    rd.applicable_to = ['Claim', 'Agent'],
    rd.parameters = '{"use_chrystallum": "confidence >= 0.80 AND single_source AND no_conflicts", "use_crminf": "confidence < 0.60 OR multiple_sources_with_confidence_below_0.80 OR conflicting_views OR explicit_reasoning_required"}',
    rd.updated = datetime();

// Claim resolution thresholds
MERGE (crt:SYS_QueryPattern {name: 'claim_resolution_rules'})
SET crt.description = 'How to resolve conflicts between multiple agent claims on the same proposition.',
    crt.applicable_to = ['Claim'],
    crt.parameters = '{"accept_no_debate": "new >= 0.80 AND (existing = 0 OR new > existing + 0.15)", "additive_coexist": "0.20 > difference > 0.15 OR both >= 0.60", "reject": "new < existing - 0.15 AND existing >= 0.60", "escalate_to_debate": "difference < 0.15 AND both >= 0.50 AND topics_overlap"}',
    crt.updated = datetime();


// ============================================================================
// PATCH 6: ENTITY CLASSIFICATION ALGORITHM (Queryable Reference)
// ============================================================================
// Source: ENTITY_CLASSIFICATION_DECISION_TREE.md
// 3-tier classification: P31/P279* → fast-path → property signature

MERGE (eca:SYS_ClassificationAlgorithm {algorithm_id: 'entity_type_classifier_v1'})
SET eca.label = 'Entity Type Classification Decision Tree',
    eca.description = 'Canonical 3-tier algorithm for classifying Wikidata entities into 9 canonical types: PERSON, PLACE, EVENT, PERIOD, ORGANIZATION, WORK, MATERIAL, OBJECT, CONCEPT.',
    eca.version = '1.0',
    eca.updated = datetime();

// Tier 1: P31/P279* traversal
MERGE (t1:SYS_ClassificationTier {tier_id: 'cls_tier_1'})
SET t1.label = 'Primary Signal: P31 + P279* Pattern',
    t1.order = 1,
    t1.method = 'P31/P279* traversal',
    t1.description = 'Follow P31 once, then P279 zero or more times to reach root ontological category. Canonical Wikidata classification pattern.',
    t1.direct_match_qids = '{"Q5": "PERSON", "Q515": "PLACE", "Q486972": "PLACE", "Q11514315": "PERIOD", "Q43229": "ORGANIZATION", "Q1656682": "EVENT"}',
    t1.root_match_qids = '{"Q5": "PERSON", "Q17334": "PLACE", "Q618123": "PLACE", "Q1656682": "EVENT", "Q43229": "ORGANIZATION", "Q15911314": "ORGANIZATION", "Q386724": "WORK", "Q47461344": "WORK", "Q214609": "MATERIAL", "Q488383": "OBJECT"}',
    t1.confidence_direct = 1.0,
    t1.confidence_root = 0.95,
    t1.updated = datetime();

// Tier 2: Fast-path property presence
MERGE (t2:SYS_ClassificationTier {tier_id: 'cls_tier_2'})
SET t2.label = 'Fast-Path Shortcuts: Property Presence',
    t2.order = 2,
    t2.method = 'Property presence check',
    t2.description = 'Before expensive P279* traversal, check for fast signals from specific properties. Only ~15 properties needed for robust classification.',
    t2.property_signals = '{"PERSON": ["P21", "P106", "P569", "P570"], "PLACE": ["P625", "P131+P17"], "ORGANIZATION": ["P571", "P576"], "WORK": ["P50", "P57"], "EVENT": ["P580", "P582", "P585"]}',
    t2.confidence = 0.9,
    t2.updated = datetime();

// Tier 3: Property signature fallback
MERGE (t3:SYS_ClassificationTier {tier_id: 'cls_tier_3'})
SET t3.label = 'Property Signature Classifier (Fallback)',
    t3.order = 3,
    t3.method = 'Signature overlap scoring',
    t3.description = 'For entities with NO P31 and NO P279. Count overlap between entity properties and canonical property signatures. Low confidence — this is inference, not direct reading.',
    t3.signatures = '{"PERSON": ["P569","P570","P21","P106","P27","P19","P20"], "PLACE": ["P625","P17","P131","P47","P36","P1376"], "ORGANIZATION": ["P571","P576","P856","P159","P112","P1454"], "EVENT": ["P580","P582","P585","P276","P710","P793"], "WORK": ["P50","P577","P495","P123","P407","P921"], "MATERIAL": ["P186","P2079","P1056"], "OBJECT": ["P186","P127","P195","P276"]}',
    t3.confidence_high = 0.7,
    t3.confidence_medium = 0.5,
    t3.confidence_low = 0.3,
    t3.confidence_default = 0.2,
    t3.updated = datetime();

// Special cases
MERGE (sc:SYS_ClassificationTier {tier_id: 'cls_special_cases'})
SET sc.label = 'Special Case Handling',
    sc.order = 0,
    sc.method = 'Pattern matching',
    sc.description = 'Handle edge cases: Deities (Q22989102/Q4271324 → PERSON with mythological flag), Wikimedia metadata (Q4167836/Q15184295/Q13406463 → METADATA, exclude from domain graph), Abstract concepts (Q17736 → CONCEPT with confidence 1.0).',
    sc.deity_qids = '["Q22989102", "Q4271324"]',
    sc.wikimedia_exclude_qids = '["Q4167836", "Q15184295", "Q13406463"]',
    sc.updated = datetime();

// Link tiers to algorithm
MATCH (alg:SYS_ClassificationAlgorithm {algorithm_id: 'entity_type_classifier_v1'})
MATCH (t:SYS_ClassificationTier)
MERGE (alg)-[:HAS_TIER]->(t);


// ============================================================================
// PATCH 7: ADR REFERENCE NODES
// ============================================================================
// So agents can discover which architectural decisions govern their behavior.

UNWIND [
  {adr_id: 'ADR-001', title: 'Content-Only Cipher', status: 'ACCEPTED', date: '2026-02-16',
   summary: 'Cipher includes ONLY: subject, object, relationship, temporal data, source work, passage hash, facet_id. EXCLUDES: confidence, agent, timestamp. Same assertion by different agents = same cipher = automatic deduplication. Enables cross-institutional verification.',
   impacts: ['Claim', 'cipher', 'deduplication', 'federation']},

  {adr_id: 'ADR-002', title: 'Function-Driven Relationship Catalog', status: 'ACCEPTED', date: '2026-02-16',
   summary: 'Maintain comprehensive 311-type catalog organized by functional capabilities. V1.0 kernel: 48 relationships across 7 categories. Staged expansion v1.1 (50-75) → v2.0 (175-200). Multiple Chrystallum rels → single Wikidata property is precision, not redundancy.',
   impacts: ['SYS_RelationshipType', 'kernel', 'federation']},

  {adr_id: 'ADR-004', title: 'Canonical 18-Facet System', status: 'ACCEPTED', date: '2026-02-16',
   summary: '18 canonical facets including BIOGRAPHIC. UPPERCASE enforcement. facet_registry_master.json is single source of truth. Pydantic FacetKey enum reflects registry. Neo4j constraints reject invalid values.',
   impacts: ['Facet', 'SubjectConcept', 'SFA', 'validation']},

  {adr_id: 'ADR-005', title: 'Federated Claims Signing', status: 'ACCEPTED', date: '2026-02-16',
   summary: 'Three-tier federated trust: institutional signing authority (Ed25519), transparency logging (Merkle trees), cryptographic verification. Per-claim signature signs content hash (cipher), not full data. Institutional keys published via DNS TXT or .well-known/chrystallum.json.',
   impacts: ['Claim', 'federation', 'SYS_FederationSource', 'signing']},

  {adr_id: 'ADR-006', title: 'Bootstrap Scaffold Contract', status: 'ACCEPTED', date: '2026-02-17',
   summary: 'Canonical writes are promotion-gated. Bootstrap/SFA pre-promotion writes use ScaffoldNode/ScaffoldEdge labels. Promotion service validates, merges canonical nodes, creates canonical relationships, records promotion event. No first-class :Occupation label — professions canonize as :SubjectConcept.',
   impacts: ['ScaffoldNode', 'ScaffoldEdge', 'promotion', 'AnalysisRun']}
] AS adr
MERGE (a:SYS_ADR {adr_id: adr.adr_id})
SET a.title = adr.title,
    a.status = adr.status,
    a.date = adr.date,
    a.summary = adr.summary,
    a.impacts = adr.impacts,
    a.updated = datetime();


// ============================================================================
// PATCH 8: ADD ONBOARDING STEPS FOR NEW MATERIAL
// ============================================================================
// Insert 4 additional onboarding steps after the existing 10.

MERGE (s11:SYS_OnboardingStep {step_id: 'onboard_s11'})
SET s11.step_order = 11,
    s11.label = 'Scaffold vs. Canonical Boundary',
    s11.learns = 'Where do I write my outputs? What is the promotion contract?',
    s11.query = 'MATCH (et:EntityType) WHERE et.name IN ["ScaffoldNode", "ScaffoldEdge"] RETURN et.name AS label, et.description AS description, et.required_properties AS required_props ORDER BY et.name',
    s11.explanation = 'You NEVER write canonical labels (Human, Place, Event, etc.) directly. All your output goes to ScaffoldNode and ScaffoldEdge. The promotion service validates your scaffold artifacts against policies, then creates canonical nodes. This is the ADR-006 bootstrap contract.',
    s11.updated = datetime();

MERGE (s12:SYS_OnboardingStep {step_id: 'onboard_s12'})
SET s12.step_order = 12,
    s12.label = 'Confidence Scoring Rubric',
    s12.learns = 'How do I compute confidence for my claims? What source quality tiers exist?',
    s12.query = 'MATCH (ct:SYS_ConfidenceTier) RETURN ct.tier_id AS tier, ct.floor AS min, ct.ceiling AS max, ct.midpoint AS base, ct.description AS description ORDER BY ct.midpoint DESC',
    s12.explanation = 'Start with the midpoint of the source tier, then apply modifiers. Primary sources (inscriptions, coins) start at 0.925. LLM synthesis with consensus starts at 0.775. Speculation starts at 0.20. Your claims must carry justified confidence scores.',
    s12.updated = datetime();

MERGE (s13:SYS_OnboardingStep {step_id: 'onboard_s13'})
SET s13.step_order = 13,
    s13.label = 'Entity Classification Algorithm',
    s13.learns = 'How do I classify a Wikidata entity into the correct canonical type?',
    s13.query = 'MATCH (alg:SYS_ClassificationAlgorithm)-[:HAS_TIER]->(t:SYS_ClassificationTier) RETURN t.order AS tier_order, t.label AS tier, t.method AS method, t.description AS description ORDER BY t.order',
    s13.explanation = 'Use the 3-tier decision tree: (1) P31/P279* traversal for direct or root classification, (2) fast-path property presence checks, (3) property signature overlap scoring as fallback. Only ~15 properties needed. Classification confidence ranges from 1.0 (direct P31 match) to 0.2 (default CONCEPT).',
    s13.updated = datetime();

MERGE (s14:SYS_OnboardingStep {step_id: 'onboard_s14'})
SET s14.step_order = 14,
    s14.label = 'Architectural Decisions (ADRs)',
    s14.learns = 'What architectural decisions constrain the entire system?',
    s14.query = 'MATCH (a:SYS_ADR) RETURN a.adr_id AS id, a.title AS title, a.summary AS summary, a.impacts AS impacts ORDER BY a.adr_id',
    s14.explanation = 'ADRs are binding architectural decisions. ADR-001 defines cipher semantics. ADR-002 defines the relationship kernel. ADR-004 defines the 18-facet system. ADR-005 defines federated signing. ADR-006 defines the scaffold/canonical boundary. These override any conflicting behavior.',
    s14.updated = datetime();

// Link new steps to protocol
MATCH (protocol:SYS_OnboardingProtocol {protocol_id: 'onboard_v1'})
MATCH (s:SYS_OnboardingStep)
WHERE s.step_id IN ['onboard_s11', 'onboard_s12', 'onboard_s13', 'onboard_s14']
MERGE (protocol)-[:HAS_STEP]->(s);

// Update protocol total
MATCH (protocol:SYS_OnboardingProtocol {protocol_id: 'onboard_v1'})
SET protocol.total_steps = 14, protocol.updated = datetime();

// Chain new steps
MATCH (s10:SYS_OnboardingStep {step_order: 10})
MATCH (s11:SYS_OnboardingStep {step_order: 11})
MERGE (s10)-[:NEXT_STEP]->(s11);

MATCH (s11:SYS_OnboardingStep {step_order: 11})
MATCH (s12:SYS_OnboardingStep {step_order: 12})
MERGE (s11)-[:NEXT_STEP]->(s12);

MATCH (s12:SYS_OnboardingStep {step_order: 12})
MATCH (s13:SYS_OnboardingStep {step_order: 13})
MERGE (s12)-[:NEXT_STEP]->(s13);

MATCH (s13:SYS_OnboardingStep {step_order: 13})
MATCH (s14:SYS_OnboardingStep {step_order: 14})
MERGE (s13)-[:NEXT_STEP]->(s14);


// ============================================================================
// PATCH 9: FEDERATION SOURCE SIGNING FIELDS (ADR-005)
// ============================================================================
// Future-proof SYS_FederationSource for institutional signing.

MATCH (fs:SYS_FederationSource)
WHERE fs.signing_key_id IS NULL
SET fs.signing_key_id = null,
    fs.registry_url = null,
    fs.transparency_log_url = null,
    fs.signing_policy = 'unsigned';

// Wikidata is special — it's open, no signing needed
MATCH (fs:SYS_FederationSource {name: 'Wikidata'})
SET fs.signing_policy = 'open_no_signing',
    fs.endpoint = 'https://query.wikidata.org/sparql',
    fs.format = 'JSON',
    fs.auth = 'none';


// ============================================================================
// PATCH 10: ADR-001 CIPHER VALIDATION RULE
// ============================================================================

MERGE (vr:SYS_ValidationRule {name: 'cipher_content_only'})
SET vr.applies_to = 'Claim',
    vr.severity = 'CRITICAL',
    vr.rationale = 'ADR-001: Cipher MUST be computed from content only (subject, object, relationship, temporal, source work, passage hash, facet_id). MUST NOT include confidence, agent, or timestamp. Same assertion by different agents at different times = same cipher.',
    vr.check_description = 'Verify no Claim cipher contains confidence or agent identifiers. Recompute cipher from content fields and compare.',
    vr.adr_reference = 'ADR-001',
    vr.updated = datetime();

// ADR-006 occupation policy
MERGE (vr2:SYS_ValidationRule {name: 'no_occupation_label'})
SET vr2.applies_to = 'ALL',
    vr2.severity = 'HIGH',
    vr2.rationale = 'ADR-006 Y.8: No first-class :Occupation node label in canonical model. Professions canonize as :SubjectConcept when approved. Human-profession assertions require temporal bounding.',
    vr2.check_description = 'MATCH (n:Occupation) RETURN count(n) should return 0.',
    vr2.adr_reference = 'ADR-006',
    vr2.updated = datetime();


// ============================================================================
// VERIFICATION
// ============================================================================

// Relationship kernel count
MATCH (r:SYS_RelationshipType)
WHERE r.kernel_version = 'v1.0'
RETURN r.kernel_category AS category, count(*) AS count
ORDER BY count DESC;

// ADR nodes
MATCH (a:SYS_ADR) RETURN a.adr_id, a.title;

// Confidence tiers
MATCH (ct:SYS_ConfidenceTier) RETURN ct.tier_id, ct.midpoint ORDER BY ct.midpoint DESC;

// Classification tiers
MATCH (alg:SYS_ClassificationAlgorithm)-[:HAS_TIER]->(t)
RETURN alg.algorithm_id, t.order, t.label;

// Onboarding steps (should be 14)
MATCH (p:SYS_OnboardingProtocol)-[:HAS_STEP]->(s)
RETURN count(s) AS total_steps;

// Scaffold entity types
MATCH (et:EntityType) WHERE et.adr_reference = 'ADR-006'
RETURN et.name, et.description;

// Validation rules count
MATCH (vr:SYS_ValidationRule) RETURN count(vr) AS total_rules;
