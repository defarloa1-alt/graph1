// ============================================================================
// CHRYSTALLUM: MISSING DECISION TABLES (D1, D2, D3, D9, D11)
// ============================================================================
// File: 15_missing_decision_tables.cypher
// Source: DMN_DECISION_TABLES.md (2026-02-25 canonical spec)
// Purpose: The original script 11 covered D4-D14 but omitted D1, D2, D3,
//          D9, and D11. This script materializes them.
// Safe: All MERGE - idempotent
// ============================================================================


// ============================================================================
// D1: DETERMINE ASSERTION CLASS VALIDITY
// ============================================================================
// Consumer: Harvester, EdgeBuilder
// Purpose: P31 class denylist check

MERGE (dt:SYS_DecisionTable {table_id: 'D1_DETERMINE_assertion_class_validity'})
SET dt.label = 'Determine Assertion Class Validity',
    dt.description = 'Decide whether an assertion class (P31) is in the approved set. Denylist excludes Wikimedia artifacts (Q4167836 categories, Q15184295 templates, Q13406463 lists), abstract types, and other non-domain classes. Denylist currently lives in wikidata_backlink_harvest.py DEFAULT_P31_DENYLIST — should be externalized to SYS_PropertyMapping or SYS_Policy.',
    dt.hit_policy = 'FIRST',
    dt.inputs = ['assertion_class_qid'],
    dt.outputs = ['valid'],
    dt.consumers = ['Harvester', 'EdgeBuilder'],
    dt.status = 'drafted',
    dt.version = '1.0',
    dt.updated = datetime();

MERGE (r1:SYS_DecisionRow {row_id: 'D1_R01'})
SET r1.table_id = 'D1_DETERMINE_assertion_class_validity',
    r1.priority = 1,
    r1.conditions = '{"assertion_class_qid": "IN DEFAULT_P31_DENYLIST"}',
    r1.outputs = '{"valid": false}',
    r1.action_detail = 'Class is in denylist (Wikimedia categories, templates, lists, abstract types). Reject assertion.',
    r1.updated = datetime();

MERGE (r2:SYS_DecisionRow {row_id: 'D1_R02'})
SET r2.table_id = 'D1_DETERMINE_assertion_class_validity',
    r2.priority = 2,
    r2.conditions = '{"assertion_class_qid": "NOT IN DEFAULT_P31_DENYLIST"}',
    r2.outputs = '{"valid": true}',
    r2.action_detail = 'Class passes denylist check. Valid for downstream processing.',
    r2.updated = datetime();

MATCH (dt:SYS_DecisionTable {table_id: 'D1_DETERMINE_assertion_class_validity'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt.table_id
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// D2: DETERMINE VALUE TYPE CATEGORY
// ============================================================================
// Consumer: Harvester
// Exhaustive enumeration of Wikidata datatypes → categories

MERGE (dt:SYS_DecisionTable {table_id: 'D2_DETERMINE_value_type_category'})
SET dt.label = 'Determine Value Type Category',
    dt.description = 'Categorise Wikidata assertion value type (entity, quantity, time, string, etc.) for downstream routing. Exhaustive enumeration — stable, no externalisation needed.',
    dt.hit_policy = 'UNIQUE',
    dt.inputs = ['assertion_value_type'],
    dt.outputs = ['category'],
    dt.consumers = ['Harvester'],
    dt.status = 'drafted',
    dt.version = '1.0',
    dt.updated = datetime();

UNWIND [
  {row_id: 'D2_R01', priority: 1, value_type: 'wikibase-entityid', category: 'entity'},
  {row_id: 'D2_R02', priority: 2, value_type: 'time', category: 'time'},
  {row_id: 'D2_R03', priority: 3, value_type: 'quantity', category: 'quantity'},
  {row_id: 'D2_R04', priority: 4, value_type: 'string', category: 'string'},
  {row_id: 'D2_R05', priority: 5, value_type: 'monolingualtext', category: 'string'},
  {row_id: 'D2_R06', priority: 6, value_type: 'globecoordinate', category: 'coordinate'},
  {row_id: 'D2_R07', priority: 7, value_type: 'url', category: 'external_id'},
  {row_id: 'D2_R08', priority: 8, value_type: 'external-id', category: 'external_id'},
  {row_id: 'D2_R09', priority: 9, value_type: 'commonsMedia', category: 'media'},
  {row_id: 'D2_R10', priority: 10, value_type: '*', category: 'unsupported'}
] AS row
MERGE (r:SYS_DecisionRow {row_id: row.row_id})
SET r.table_id = 'D2_DETERMINE_value_type_category',
    r.priority = row.priority,
    r.conditions = '{"assertion_value_type": "' + row.value_type + '"}',
    r.outputs = '{"category": "' + row.category + '"}',
    r.updated = datetime();

MATCH (dt:SYS_DecisionTable {table_id: 'D2_DETERMINE_value_type_category'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt.table_id
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// D3: DETERMINE FRONTIER ELIGIBILITY
// ============================================================================
// Consumer: FederationDispatcher
// Depends: D1 + D2 outputs + federation_coverage

MERGE (dt:SYS_DecisionTable {table_id: 'D3_DETERMINE_frontier_eligibility'})
SET dt.label = 'Determine Frontier Eligibility',
    dt.description = 'Decide whether an entity is eligible for frontier harvest. Requires D1 pass (valid class), D2 pass (supported value type), and federation coverage. Gateway table that chains D1 and D2 outputs.',
    dt.hit_policy = 'FIRST',
    dt.inputs = ['d1_valid', 'd2_category', 'federation_coverage'],
    dt.outputs = ['frontier_eligible'],
    dt.consumers = ['FederationDispatcher'],
    dt.depends_on = ['D1_DETERMINE_assertion_class_validity', 'D2_DETERMINE_value_type_category'],
    dt.status = 'drafted',
    dt.version = '1.0',
    dt.updated = datetime();

MERGE (r1:SYS_DecisionRow {row_id: 'D3_R01'})
SET r1.table_id = 'D3_DETERMINE_frontier_eligibility',
    r1.priority = 1,
    r1.conditions = '{"d1_valid": false}',
    r1.outputs = '{"frontier_eligible": false}',
    r1.action_detail = 'D1 rejected assertion class. Not frontier eligible.',
    r1.updated = datetime();

MERGE (r2:SYS_DecisionRow {row_id: 'D3_R02'})
SET r2.table_id = 'D3_DETERMINE_frontier_eligibility',
    r2.priority = 2,
    r2.conditions = '{"d2_category": "unsupported"}',
    r2.outputs = '{"frontier_eligible": false}',
    r2.action_detail = 'D2 categorized as unsupported datatype. Not frontier eligible.',
    r2.updated = datetime();

MERGE (r3:SYS_DecisionRow {row_id: 'D3_R03'})
SET r3.table_id = 'D3_DETERMINE_frontier_eligibility',
    r3.priority = 3,
    r3.conditions = '{"d1_valid": true, "d2_category": "NOT unsupported"}',
    r3.outputs = '{"frontier_eligible": true}',
    r3.action_detail = 'Valid class + supported value type. Frontier eligible.',
    r3.updated = datetime();

MATCH (dt:SYS_DecisionTable {table_id: 'D3_DETERMINE_frontier_eligibility'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt.table_id
MERGE (dt)-[:HAS_ROW]->(r);

// Wire D3 dependency chain
MATCH (d1:SYS_DecisionTable {table_id: 'D1_DETERMINE_assertion_class_validity'})
MATCH (d3:SYS_DecisionTable {table_id: 'D3_DETERMINE_frontier_eligibility'})
MERGE (d1)-[:FEEDS_INTO]->(d3);

MATCH (d2:SYS_DecisionTable {table_id: 'D2_DETERMINE_value_type_category'})
MATCH (d3:SYS_DecisionTable {table_id: 'D3_DETERMINE_frontier_eligibility'})
MERGE (d2)-[:FEEDS_INTO]->(d3);

// D3 feeds into D4
MATCH (d3:SYS_DecisionTable {table_id: 'D3_DETERMINE_frontier_eligibility'})
MATCH (d4:SYS_DecisionTable {table_id: 'D4_DETERMINE_federation_route'})
MERGE (d3)-[:FEEDS_INTO]->(d4);


// ============================================================================
// D9: DETERMINE SFA CONSTITUTION LAYER
// ============================================================================
// Consumer: SFA constitution loader
// Maps facet → constitution document set

MERGE (dt:SYS_DecisionTable {table_id: 'D9_DETERMINE_SFA_constitution_layer'})
SET dt.label = 'Determine SFA Constitution Layer',
    dt.description = 'Map a facet to its constitution document set. Defines which documents govern interpretation for each facet. Per-facet constitution doc set to be designed — may use SYS_FacetConstitution or similar node type.',
    dt.hit_policy = 'UNIQUE',
    dt.inputs = ['facet'],
    dt.outputs = ['constitution_doc_ids'],
    dt.consumers = ['SFA_constitution_loader'],
    dt.status = 'placeholder',
    dt.version = '1.0',
    dt.note = 'Full facet-to-constitution mapping TBD. This is a placeholder table that will be populated when constitution documents are loaded. Each of the 18 canonical facets will have a row mapping to its governing document IDs.',
    dt.updated = datetime();

// Placeholder rows for the 3 active SFA facets
UNWIND [
  {row_id: 'D9_R01', facet: 'POLITICAL', docs: '["constitution_political_rr_v1"]'},
  {row_id: 'D9_R02', facet: 'MILITARY', docs: '["constitution_military_rr_v1"]'},
  {row_id: 'D9_R03', facet: 'SOCIAL', docs: '["constitution_social_rr_v1"]'}
] AS row
MERGE (r:SYS_DecisionRow {row_id: row.row_id})
SET r.table_id = 'D9_DETERMINE_SFA_constitution_layer',
    r.priority = 1,
    r.conditions = '{"facet": "' + row.facet + '"}',
    r.outputs = '{"constitution_doc_ids": ' + row.docs + '}',
    r.action_detail = 'Constitution documents for ' + row.facet + ' facet SFA.',
    r.updated = datetime();

MATCH (dt:SYS_DecisionTable {table_id: 'D9_DETERMINE_SFA_constitution_layer'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt.table_id
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// D11: DETERMINE CLAIM DISPUTE TRIGGER
// ============================================================================
// Consumer: Claim pipeline
// Depends: D10 output

MERGE (dt:SYS_DecisionTable {table_id: 'D11_DETERMINE_claim_dispute_trigger'})
SET dt.label = 'Determine Claim Dispute Trigger',
    dt.description = 'Decide when a promoted claim should be flagged for dispute. Triggers when conflicting evidence exists or agreement score is below threshold. Only evaluates claims that passed D10 (promotion eligibility).',
    dt.hit_policy = 'FIRST',
    dt.inputs = ['d10_promote', 'conflicting_evidence_count', 'agreement_score'],
    dt.outputs = ['dispute_triggered'],
    dt.consumers = ['claim_pipeline'],
    dt.depends_on = ['D10_DETERMINE_claim_promotion_eligibility'],
    dt.status = 'drafted',
    dt.version = '1.0',
    dt.note = 'Agreement score threshold TBD — currently uses confidence scoring rubric escalation rules (difference < 0.15 AND both >= 0.50).',
    dt.updated = datetime();

MERGE (r1:SYS_DecisionRow {row_id: 'D11_R01'})
SET r1.table_id = 'D11_DETERMINE_claim_dispute_trigger',
    r1.priority = 1,
    r1.conditions = '{"d10_promote": false}',
    r1.outputs = '{"dispute_triggered": false}',
    r1.action_detail = 'Claim was not promoted (D10 rejected). No dispute evaluation needed.',
    r1.updated = datetime();

MERGE (r2:SYS_DecisionRow {row_id: 'D11_R02'})
SET r2.table_id = 'D11_DETERMINE_claim_dispute_trigger',
    r2.priority = 2,
    r2.conditions = '{"d10_promote": true, "conflicting_evidence_count": "> 0"}',
    r2.outputs = '{"dispute_triggered": true}',
    r2.action_detail = 'Promoted claim has conflicting evidence. Flag for dispute resolution / multi-SME debate.',
    r2.updated = datetime();

MERGE (r3:SYS_DecisionRow {row_id: 'D11_R03'})
SET r3.table_id = 'D11_DETERMINE_claim_dispute_trigger',
    r3.priority = 3,
    r3.conditions = '{"d10_promote": true, "conflicting_evidence_count": 0, "agreement_score": "< TBD_threshold"}',
    r3.outputs = '{"dispute_triggered": true}',
    r3.action_detail = 'Promoted claim has low agreement despite no direct conflicts. Flag for review.',
    r3.updated = datetime();

MERGE (r4:SYS_DecisionRow {row_id: 'D11_R04'})
SET r4.table_id = 'D11_DETERMINE_claim_dispute_trigger',
    r4.priority = 4,
    r4.conditions = '{"d10_promote": true, "conflicting_evidence_count": 0, "agreement_score": ">= TBD_threshold"}',
    r4.outputs = '{"dispute_triggered": false}',
    r4.action_detail = 'Promoted claim has strong agreement and no conflicts. No dispute.',
    r4.updated = datetime();

MATCH (dt:SYS_DecisionTable {table_id: 'D11_DETERMINE_claim_dispute_trigger'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt.table_id
MERGE (dt)-[:HAS_ROW]->(r);

// Wire D11 dependency on D10
MATCH (d10:SYS_DecisionTable {table_id: 'D10_DETERMINE_claim_promotion_eligibility'})
MATCH (d11:SYS_DecisionTable {table_id: 'D11_DETERMINE_claim_dispute_trigger'})
MERGE (d10)-[:FEEDS_INTO]->(d11);


// ============================================================================
// WIRE TABLE DEPENDENCY CHAIN (D1 → D2 → D3 → D4 → D5 → D6 → D7)
// ============================================================================
// The DMN spec defines a pipeline: entity validation → routing → scoping → harvest

MATCH (d4:SYS_DecisionTable {table_id: 'D4_DETERMINE_federation_route'})
MATCH (d5:SYS_DecisionTable {table_id: 'D5_DETERMINE_federation_scope_match'})
MERGE (d4)-[:FEEDS_INTO]->(d5);

MATCH (d5:SYS_DecisionTable {table_id: 'D5_DETERMINE_federation_scope_match'})
MATCH (d6:SYS_DecisionTable {table_id: 'D6_DETERMINE_entity_class_validity'})
MERGE (d5)-[:FEEDS_INTO]->(d6);

MATCH (d6:SYS_DecisionTable {table_id: 'D6_DETERMINE_entity_class_validity'})
MATCH (d7:SYS_DecisionTable {table_id: 'D7_DETERMINE_harvest_allowlist_eligibility'})
MERGE (d6)-[:FEEDS_INTO]->(d7);

// SFA chain: D8 → D9 → D10 → D11
MATCH (d8:SYS_DecisionTable {table_id: 'D8_DETERMINE_SFA_facet_assignment'})
MATCH (d9:SYS_DecisionTable {table_id: 'D9_DETERMINE_SFA_constitution_layer'})
MERGE (d8)-[:FEEDS_INTO]->(d9);

MATCH (d9:SYS_DecisionTable {table_id: 'D9_DETERMINE_SFA_constitution_layer'})
MATCH (d10:SYS_DecisionTable {table_id: 'D10_DETERMINE_claim_promotion_eligibility'})
MERGE (d9)-[:FEEDS_INTO]->(d10);


// ============================================================================
// VERIFICATION
// ============================================================================

// All 14 decision tables should now exist
MATCH (dt:SYS_DecisionTable)
OPTIONAL MATCH (dt)-[:HAS_ROW]->(r)
RETURN dt.table_id AS table_id, dt.label AS label, dt.hit_policy AS hit_policy,
       count(r) AS rows, dt.status AS status
ORDER BY dt.table_id;

// Decision table dependency chain
MATCH (a:SYS_DecisionTable)-[:FEEDS_INTO]->(b:SYS_DecisionTable)
RETURN a.table_id AS from_table, b.table_id AS to_table
ORDER BY a.table_id;
