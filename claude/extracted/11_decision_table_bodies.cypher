// ============================================================================
// CHRYSTALLUM: DECISION TABLE BODIES (Von Halle/Goldberg/Feldman)
// ============================================================================
// File: 11_decision_table_bodies.cypher
// Purpose: Materialize the condition/action rows for each decision table
//          referenced by SYS_Policy nodes, making policy logic
//          queryable and executable by agents.
// Pattern: SYS_Policy -[:GOVERNED_BY]-> SYS_DecisionTable -[:HAS_ROW]-> SYS_DecisionRow
// Safe: All MERGE - idempotent
// ============================================================================

// ============================================================================
// D10: DETERMINE CLAIM PROMOTION ELIGIBILITY
// ============================================================================
// Referenced by: ApprovalRequired policy
// Thresholds: claim_promotion_confidence (0.9), claim_promotion_posterior (0.9)

MERGE (dt:SYS_DecisionTable {table_id: 'D10_DETERMINE_claim_promotion_eligibility'})
SET dt.label = 'Determine Claim Promotion Eligibility',
    dt.description = 'Evaluates whether an agent-proposed Claim should be promoted to a first-class graph edge. All conditions must be met. Human approval is always required (ApprovalRequired policy).',
    dt.conditions = ['confidence', 'posterior', 'provenance_exists', 'human_approval'],
    dt.actions = ['promote', 'flag_for_review', 'reject'],
    dt.version = '1.0',
    dt.updated = datetime();

MATCH (p:SYS_Policy {name: 'ApprovalRequired'})
MATCH (dt:SYS_DecisionTable {table_id: 'D10_DETERMINE_claim_promotion_eligibility'})
MERGE (p)-[:GOVERNED_BY]->(dt);

// Row 1: Full promotion (all conditions met)
MERGE (r1:SYS_DecisionRow {row_id: 'D10_R01'})
SET r1.table_id = 'D10_DETERMINE_claim_promotion_eligibility',
    r1.priority = 1,
    r1.conditions = '{"confidence": ">=0.9", "posterior": ">=0.9", "provenance_exists": true, "human_approval": true}',
    r1.action = 'promote',
    r1.action_detail = 'Create first-class edge from ProposedEdge. Set Claim.status = promoted. Set Claim.promoted_at = now().',
    r1.updated = datetime();

// Row 2: High confidence but missing provenance
MERGE (r2:SYS_DecisionRow {row_id: 'D10_R02'})
SET r2.table_id = 'D10_DETERMINE_claim_promotion_eligibility',
    r2.priority = 2,
    r2.conditions = '{"confidence": ">=0.9", "posterior": ">=0.9", "provenance_exists": false, "human_approval": "-"}',
    r2.action = 'flag_for_review',
    r2.action_detail = 'Set Claim.status = needs_provenance. Agent must attach RetrievalContext before re-evaluation.',
    r2.updated = datetime();

// Row 3: Below threshold
MERGE (r3:SYS_DecisionRow {row_id: 'D10_R03'})
SET r3.table_id = 'D10_DETERMINE_claim_promotion_eligibility',
    r3.priority = 3,
    r3.conditions = '{"confidence": "<0.9", "posterior": "-", "provenance_exists": "-", "human_approval": "-"}',
    r3.action = 'reject',
    r3.action_detail = 'Set Claim.status = rejected_low_confidence. Log rejection reason.',
    r3.updated = datetime();

// Row 4: Human denied
MERGE (r4:SYS_DecisionRow {row_id: 'D10_R04'})
SET r4.table_id = 'D10_DETERMINE_claim_promotion_eligibility',
    r4.priority = 4,
    r4.conditions = '{"confidence": ">=0.9", "posterior": ">=0.9", "provenance_exists": true, "human_approval": false}',
    r4.action = 'reject',
    r4.action_detail = 'Set Claim.status = rejected_human. Preserve reviewer notes for agent learning.',
    r4.updated = datetime();

MATCH (dt:SYS_DecisionTable {table_id: 'D10_DETERMINE_claim_promotion_eligibility'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt.table_id
MERGE (dt)-[:HAS_ROW]->(r);


// ============================================================================
// D8: DETERMINE SFA FACET ASSIGNMENT
// ============================================================================
// Referenced by: NoTemporalFacet, NoClassificationFacet, NoGenealogicalFacet,
//                NoPatronageFacet, SFAProposalAsClaim policies
// Threshold: sfa_proposal_confidence_default (0.75)

MERGE (dt8:SYS_DecisionTable {table_id: 'D8_DETERMINE_SFA_facet_assignment'})
SET dt8.label = 'Determine Subject-Facet Assignment',
    dt8.description = 'Routes a SubjectConcept to one of the 18 canonical facets. Certain facets are excluded by policy (Temporal, Classification, Genealogical, Patronage). Assignments below confidence threshold are wrapped as Claims via SFAProposalAsClaim.',
    dt8.conditions = ['facet_candidate', 'excluded_by_policy', 'confidence', 'wikidata_anchor_match'],
    dt8.actions = ['assign', 'propose_as_claim', 'reject'],
    dt8.version = '1.0',
    dt8.updated = datetime();

// Link all referencing policies
UNWIND ['NoTemporalFacet', 'NoClassificationFacet', 'NoGenealogicalFacet', 'NoPatronageFacet', 'SFAProposalAsClaim'] AS pname
MATCH (p:SYS_Policy {name: pname})
MATCH (dt8:SYS_DecisionTable {table_id: 'D8_DETERMINE_SFA_facet_assignment'})
MERGE (p)-[:GOVERNED_BY]->(dt8);

MERGE (r81:SYS_DecisionRow {row_id: 'D8_R01'})
SET r81.table_id = 'D8_DETERMINE_SFA_facet_assignment',
    r81.priority = 1,
    r81.conditions = '{"excluded_by_policy": true}',
    r81.action = 'reject',
    r81.action_detail = 'Facet is in the exclusion list (Temporal, Classification, Genealogical, Patronage). Do not assign.',
    r81.updated = datetime();

MERGE (r82:SYS_DecisionRow {row_id: 'D8_R02'})
SET r82.table_id = 'D8_DETERMINE_SFA_facet_assignment',
    r82.priority = 2,
    r82.conditions = '{"excluded_by_policy": false, "confidence": ">=0.75", "wikidata_anchor_match": true}',
    r82.action = 'assign',
    r82.action_detail = 'Direct assignment: create ASSIGNED_TO_FACET edge. Set SubjectConcept.facet property.',
    r82.updated = datetime();

MERGE (r83:SYS_DecisionRow {row_id: 'D8_R03'})
SET r83.table_id = 'D8_DETERMINE_SFA_facet_assignment',
    r83.priority = 3,
    r83.conditions = '{"excluded_by_policy": false, "confidence": "<0.75"}',
    r83.action = 'propose_as_claim',
    r83.action_detail = 'Wrap assignment as Claim with claim_type = sfa_proposal. Requires human review before facet assignment.',
    r83.updated = datetime();

MATCH (dt8:SYS_DecisionTable {table_id: 'D8_DETERMINE_SFA_facet_assignment'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt8.table_id
MERGE (dt8)-[:HAS_ROW]->(r);


// ============================================================================
// D5: DETERMINE FEDERATION SCOPE MATCH
// ============================================================================
// Referenced by: HubForDisambiguationOnly policy
// Thresholds: scoping_confidence_domain (0.85), scoping_confidence_temporal_high (0.95),
//             scoping_confidence_temporal_med (0.85), scoping_confidence_unscoped (0.4)

MERGE (dt5:SYS_DecisionTable {table_id: 'D5_DETERMINE_federation_scope_match'})
SET dt5.label = 'Determine Federation Scope Match',
    dt5.description = 'Evaluates whether an entity from a federation source falls within Chrystallum scope. Uses domain confidence, temporal overlap, and scoping weights. Hub entities (Wikidata disambiguation pages) are accepted only for disambiguation, never as first-class entities.',
    dt5.conditions = ['domain_confidence', 'temporal_overlap', 'is_hub_entity', 'scoping_weight'],
    dt5.actions = ['accept_in_scope', 'accept_disambiguation_only', 'reject_out_of_scope'],
    dt5.version = '1.0',
    dt5.updated = datetime();

MATCH (p5:SYS_Policy {name: 'HubForDisambiguationOnly'})
MATCH (dt5:SYS_DecisionTable {table_id: 'D5_DETERMINE_federation_scope_match'})
MERGE (p5)-[:GOVERNED_BY]->(dt5);

MERGE (r51:SYS_DecisionRow {row_id: 'D5_R01'})
SET r51.table_id = 'D5_DETERMINE_federation_scope_match',
    r51.priority = 1,
    r51.conditions = '{"is_hub_entity": true}',
    r51.action = 'accept_disambiguation_only',
    r51.action_detail = 'Hub entity (e.g. Wikidata disambiguation page). Accept for entity resolution but do NOT create first-class node.',
    r51.updated = datetime();

MERGE (r52:SYS_DecisionRow {row_id: 'D5_R02'})
SET r52.table_id = 'D5_DETERMINE_federation_scope_match',
    r52.priority = 2,
    r52.conditions = '{"is_hub_entity": false, "domain_confidence": ">=0.85", "temporal_overlap": ">=0.85"}',
    r52.action = 'accept_in_scope',
    r52.action_detail = 'Entity is within Chrystallum domain and temporal scope. Create or merge as first-class entity.',
    r52.updated = datetime();

MERGE (r53:SYS_DecisionRow {row_id: 'D5_R03'})
SET r53.table_id = 'D5_DETERMINE_federation_scope_match',
    r53.priority = 3,
    r53.conditions = '{"is_hub_entity": false, "domain_confidence": "<0.4"}',
    r53.action = 'reject_out_of_scope',
    r53.action_detail = 'Entity falls outside Chrystallum scope. Do not import.',
    r53.updated = datetime();

MATCH (dt5:SYS_DecisionTable {table_id: 'D5_DETERMINE_federation_scope_match'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt5.table_id
MERGE (dt5)-[:HAS_ROW]->(r);


// ============================================================================
// D6: DETERMINE ENTITY CLASS VALIDITY
// ============================================================================
// Referenced by: LiteralHeavyExclusion, TemporalPrecisionFloor
// Thresholds: literal_heavy_threshold (0.8), min_temporal_precision (9),
//             unresolved_class_threshold (0.2), unsupported_datatype_threshold (0.1)

MERGE (dt6:SYS_DecisionTable {table_id: 'D6_DETERMINE_entity_class_validity'})
SET dt6.label = 'Determine Entity Class Validity',
    dt6.description = 'Validates whether an entity from Wikidata should be accepted based on its class structure. Rejects literal-heavy entities (>80% literal properties), low temporal precision (<9), and unresolved/unsupported datatypes.',
    dt6.conditions = ['literal_ratio', 'temporal_precision', 'unresolved_class_ratio', 'unsupported_datatype_ratio'],
    dt6.actions = ['accept', 'reject_literal_heavy', 'reject_low_precision', 'reject_unresolved'],
    dt6.version = '1.0',
    dt6.updated = datetime();

UNWIND ['LiteralHeavyExclusion', 'TemporalPrecisionFloor'] AS pname
MATCH (p:SYS_Policy {name: pname})
MATCH (dt6:SYS_DecisionTable {table_id: 'D6_DETERMINE_entity_class_validity'})
MERGE (p)-[:GOVERNED_BY]->(dt6);

MERGE (r61:SYS_DecisionRow {row_id: 'D6_R01'})
SET r61.table_id = 'D6_DETERMINE_entity_class_validity',
    r61.priority = 1,
    r61.conditions = '{"literal_ratio": ">=0.8"}',
    r61.action = 'reject_literal_heavy',
    r61.action_detail = 'Entity is >80% literal properties (e.g. a dataset, not a historical entity). Exclude.',
    r61.updated = datetime();

MERGE (r62:SYS_DecisionRow {row_id: 'D6_R02'})
SET r62.table_id = 'D6_DETERMINE_entity_class_validity',
    r62.priority = 2,
    r62.conditions = '{"temporal_precision": "<9"}',
    r62.action = 'reject_low_precision',
    r62.action_detail = 'Temporal precision below year-level (Wikidata precision 9 = year). Cannot anchor to Year backbone.',
    r62.updated = datetime();

MERGE (r63:SYS_DecisionRow {row_id: 'D6_R03'})
SET r63.table_id = 'D6_DETERMINE_entity_class_validity',
    r63.priority = 3,
    r63.conditions = '{"literal_ratio": "<0.8", "temporal_precision": ">=9", "unresolved_class_ratio": "<0.2", "unsupported_datatype_ratio": "<0.1"}',
    r63.action = 'accept',
    r63.action_detail = 'Entity passes all validity checks. Proceed to federation scope matching (D5).',
    r63.updated = datetime();

MATCH (dt6:SYS_DecisionTable {table_id: 'D6_DETERMINE_entity_class_validity'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt6.table_id
MERGE (dt6)-[:HAS_ROW]->(r);


// ============================================================================
// D7: DETERMINE HARVEST ALLOWLIST ELIGIBILITY
// ============================================================================
// Referenced by: HarvestModeBudgets
// Thresholds: max_hops_p279, max_new_nodes_discovery/production, etc.

MERGE (dt7:SYS_DecisionTable {table_id: 'D7_DETERMINE_harvest_allowlist_eligibility'})
SET dt7.label = 'Determine Harvest Allowlist Eligibility',
    dt7.description = 'Controls how many entities an agent can harvest from Wikidata in a single run. Discovery mode has tighter limits than production. Limits apply to P279 hop depth, SPARQL result count, new nodes created, and sources consulted.',
    dt7.conditions = ['mode', 'p279_hops', 'new_node_count', 'source_count', 'sparql_results'],
    dt7.actions = ['allow_harvest', 'throttle', 'block'],
    dt7.version = '1.0',
    dt7.updated = datetime();

MATCH (p7:SYS_Policy {name: 'HarvestModeBudgets'})
MATCH (dt7:SYS_DecisionTable {table_id: 'D7_DETERMINE_harvest_allowlist_eligibility'})
MERGE (p7)-[:GOVERNED_BY]->(dt7);

MERGE (r71:SYS_DecisionRow {row_id: 'D7_R01'})
SET r71.table_id = 'D7_DETERMINE_harvest_allowlist_eligibility',
    r71.priority = 1,
    r71.conditions = '{"mode": "discovery", "p279_hops": "<=4", "new_node_count": "<=100", "source_count": "<=200", "sparql_results": "<=500"}',
    r71.action = 'allow_harvest',
    r71.action_detail = 'Discovery mode within budget. Proceed with harvest.',
    r71.updated = datetime();

MERGE (r72:SYS_DecisionRow {row_id: 'D7_R02'})
SET r72.table_id = 'D7_DETERMINE_harvest_allowlist_eligibility',
    r72.priority = 2,
    r72.conditions = '{"mode": "production", "p279_hops": "<=4", "new_node_count": "<=1500", "source_count": "<=1000", "sparql_results": "<=2000"}',
    r72.action = 'allow_harvest',
    r72.action_detail = 'Production mode within budget. Proceed with harvest.',
    r72.updated = datetime();

MERGE (r73:SYS_DecisionRow {row_id: 'D7_R03'})
SET r73.table_id = 'D7_DETERMINE_harvest_allowlist_eligibility',
    r73.priority = 3,
    r73.conditions = '{"new_node_count": ">budget OR source_count > budget"}',
    r73.action = 'throttle',
    r73.action_detail = 'Budget exceeded. Complete current batch, then pause and report.',
    r73.updated = datetime();

MATCH (dt7:SYS_DecisionTable {table_id: 'D7_DETERMINE_harvest_allowlist_eligibility'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt7.table_id
MERGE (dt7)-[:HAS_ROW]->(r);


// ============================================================================
// D4: DETERMINE FEDERATION ROUTE
// ============================================================================

MERGE (dt4:SYS_DecisionTable {table_id: 'D4_DETERMINE_federation_route'})
SET dt4.label = 'Determine Federation Route',
    dt4.description = 'Routes an entity lookup to the correct federation source. Local canonical authorities (LCSH/FAST/LCC) are preferred over remote sources. Wikidata is the universal fallback.',
    dt4.conditions = ['entity_type', 'has_local_authority', 'has_qid'],
    dt4.actions = ['route_local_first', 'route_wikidata', 'route_specialized'],
    dt4.version = '1.0',
    dt4.updated = datetime();

MATCH (p4:SYS_Policy {name: 'LocalFirstCanonicalAuthorities'})
MATCH (dt4:SYS_DecisionTable {table_id: 'D4_DETERMINE_federation_route'})
MERGE (p4)-[:GOVERNED_BY]->(dt4);

MERGE (r41:SYS_DecisionRow {row_id: 'D4_R01'})
SET r41.table_id = 'D4_DETERMINE_federation_route',
    r41.priority = 1,
    r41.conditions = '{"entity_type": "SubjectConcept", "has_local_authority": true}',
    r41.action = 'route_local_first',
    r41.action_detail = 'Check LCSH/FAST/LCC first. Only fall back to Wikidata if local authority is insufficient.',
    r41.updated = datetime();

MERGE (r42:SYS_DecisionRow {row_id: 'D4_R02'})
SET r42.table_id = 'D4_DETERMINE_federation_route',
    r42.priority = 2,
    r42.conditions = '{"entity_type": "Place", "has_qid": true}',
    r42.action = 'route_specialized',
    r42.action_detail = 'Route to Pleiades (ancient places), TGN (modern), GeoNames. Cross-reference with Wikidata QID.',
    r42.updated = datetime();

MERGE (r43:SYS_DecisionRow {row_id: 'D4_R03'})
SET r43.table_id = 'D4_DETERMINE_federation_route',
    r43.priority = 3,
    r43.conditions = '{"has_local_authority": false, "has_qid": true}',
    r43.action = 'route_wikidata',
    r43.action_detail = 'No local authority available. Use Wikidata as primary source.',
    r43.updated = datetime();

MATCH (dt4:SYS_DecisionTable {table_id: 'D4_DETERMINE_federation_route'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt4.table_id
MERGE (dt4)-[:HAS_ROW]->(r);


// ============================================================================
// D12: DETERMINE SUBJECTCONCEPT SPLIT TRIGGER
// ============================================================================

MERGE (dt12:SYS_DecisionTable {table_id: 'D12_DETERMINE_SubjectConcept_split_trigger'})
SET dt12.label = 'Determine SubjectConcept Split Trigger',
    dt12.description = 'Detects when a SubjectConcept node is overloaded (too many children at level 2, or cross-link ratio indicates mixed semantics) and should be split into more specific concepts.',
    dt12.conditions = ['level2_child_count', 'crosslink_ratio'],
    dt12.actions = ['no_action', 'flag_for_split', 'auto_split'],
    dt12.version = '1.0',
    dt12.updated = datetime();

MERGE (r121:SYS_DecisionRow {row_id: 'D12_R01'})
SET r121.table_id = 'D12_DETERMINE_SubjectConcept_split_trigger',
    r121.priority = 1,
    r121.conditions = '{"level2_child_count": "<=12", "crosslink_ratio": "<0.3"}',
    r121.action = 'no_action',
    r121.action_detail = 'SubjectConcept is healthy. No split needed.',
    r121.updated = datetime();

MERGE (r122:SYS_DecisionRow {row_id: 'D12_R02'})
SET r122.table_id = 'D12_DETERMINE_SubjectConcept_split_trigger',
    r122.priority = 2,
    r122.conditions = '{"level2_child_count": ">12 OR crosslink_ratio >= 0.3"}',
    r122.action = 'flag_for_split',
    r122.action_detail = 'SubjectConcept is overloaded or semantically mixed. Flag for human review and potential split.',
    r122.updated = datetime();

MATCH (dt12:SYS_DecisionTable {table_id: 'D12_DETERMINE_SubjectConcept_split_trigger'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt12.table_id
MERGE (dt12)-[:HAS_ROW]->(r);


// ============================================================================
// D13: DETERMINE SFA DRIFT ALERT
// ============================================================================

MERGE (dt13:SYS_DecisionTable {table_id: 'D13_DETERMINE_SFA_drift_alert'})
SET dt13.label = 'Determine SFA Drift Alert',
    dt13.description = 'Monitors facet assignment drift. If >20% of recent assignments for a facet deviate from expected Wikidata anchors, trigger an alert for the domain specialist.',
    dt13.conditions = ['drift_ratio'],
    dt13.actions = ['no_alert', 'alert_specialist'],
    dt13.version = '1.0',
    dt13.updated = datetime();

MERGE (r131:SYS_DecisionRow {row_id: 'D13_R01'})
SET r131.table_id = 'D13_DETERMINE_SFA_drift_alert',
    r131.priority = 1,
    r131.conditions = '{"drift_ratio": "<0.2"}',
    r131.action = 'no_alert',
    r131.action_detail = 'Facet assignments are within expected range.',
    r131.updated = datetime();

MERGE (r132:SYS_DecisionRow {row_id: 'D13_R02'})
SET r132.table_id = 'D13_DETERMINE_SFA_drift_alert',
    r132.priority = 2,
    r132.conditions = '{"drift_ratio": ">=0.2"}',
    r132.action = 'alert_specialist',
    r132.action_detail = 'Drift detected. Notify facet domain specialist agent for review.',
    r132.updated = datetime();

MATCH (dt13:SYS_DecisionTable {table_id: 'D13_DETERMINE_SFA_drift_alert'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt13.table_id
MERGE (dt13)-[:HAS_ROW]->(r);


// ============================================================================
// D14: DETERMINE ENTITY RESOLUTION ACCEPTANCE
// ============================================================================

MERGE (dt14:SYS_DecisionTable {table_id: 'D14_DETERMINE_entity_resolution_acceptance'})
SET dt14.label = 'Determine Entity Resolution Acceptance',
    dt14.description = 'Evaluates whether two entity candidates refer to the same real-world entity. Uses fuzzy name matching, confidence scoring, and QID alignment.',
    dt14.conditions = ['fuzzy_score', 'confidence', 'similarity_min', 'qid_match'],
    dt14.actions = ['merge', 'flag_ambiguous', 'keep_separate'],
    dt14.version = '1.0',
    dt14.updated = datetime();

MATCH (p14:SYS_Policy {name: 'EntityResolutionFallback'})
MATCH (dt14:SYS_DecisionTable {table_id: 'D14_DETERMINE_entity_resolution_acceptance'})
MERGE (p14)-[:GOVERNED_BY]->(dt14);

MERGE (r141:SYS_DecisionRow {row_id: 'D14_R01'})
SET r141.table_id = 'D14_DETERMINE_entity_resolution_acceptance',
    r141.priority = 1,
    r141.conditions = '{"fuzzy_score": ">=0.8", "confidence": ">=0.75", "qid_match": true}',
    r141.action = 'merge',
    r141.action_detail = 'High confidence match with QID alignment. Merge entities, preserve both source IDs.',
    r141.updated = datetime();

MERGE (r142:SYS_DecisionRow {row_id: 'D14_R02'})
SET r142.table_id = 'D14_DETERMINE_entity_resolution_acceptance',
    r142.priority = 2,
    r142.conditions = '{"fuzzy_score": ">=0.8", "confidence": ">=0.75", "qid_match": false}',
    r142.action = 'flag_ambiguous',
    r142.action_detail = 'Name matches but QIDs differ. Flag for human disambiguation.',
    r142.updated = datetime();

MERGE (r143:SYS_DecisionRow {row_id: 'D14_R03'})
SET r143.table_id = 'D14_DETERMINE_entity_resolution_acceptance',
    r143.priority = 3,
    r143.conditions = '{"similarity_min": "<0.5"}',
    r143.action = 'keep_separate',
    r143.action_detail = 'Below similarity floor. Entities are distinct.',
    r143.updated = datetime();

MATCH (dt14:SYS_DecisionTable {table_id: 'D14_DETERMINE_entity_resolution_acceptance'})
MATCH (r:SYS_DecisionRow) WHERE r.table_id = dt14.table_id
MERGE (dt14)-[:HAS_ROW]->(r);


// ============================================================================
// LINK THRESHOLDS TO DECISION TABLES
// ============================================================================

MATCH (t:SYS_Threshold)
WHERE t.decision_table IS NOT NULL
MATCH (dt:SYS_DecisionTable {table_id: t.decision_table})
MERGE (dt)-[:USES_THRESHOLD]->(t);


// ============================================================================
// VERIFICATION
// ============================================================================

MATCH (dt:SYS_DecisionTable)
OPTIONAL MATCH (dt)-[:HAS_ROW]->(r:SYS_DecisionRow)
OPTIONAL MATCH (dt)-[:USES_THRESHOLD]->(t:SYS_Threshold)
RETURN dt.table_id AS table_id,
       dt.label AS label,
       count(DISTINCT r) AS row_count,
       count(DISTINCT t) AS threshold_count
ORDER BY dt.table_id;
