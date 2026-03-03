// ============================================================================
// CHRYSTALLUM: DISCIPLINE BOOTSTRAP ONBOARDING PROTOCOL
// ============================================================================
// File: 18_discipline_bootstrap_protocol.cypher
// Purpose:
//   Add a deterministic protocol for discipline-subgraph construction so
//   agents do not drift into free-form web synthesis.
//
// Design:
//   - Protocol id: onboard_discipline_v1
//   - Root input: $root_qid (e.g., Q36442 political science)
//   - Method: recursive backlink harvest + authority validation + scaffold-only
//
// Safety:
//   - MERGE only, idempotent
//   - No domain node writes here; protocol metadata only
// ============================================================================


// ============================================================================
// ROOT PROTOCOL NODE
// ============================================================================

MERGE (p:SYS_OnboardingProtocol {protocol_id: 'onboard_discipline_v1'})
SET p.label = 'Discipline Bootstrap Protocol v1',
    p.description = 'Deterministic sequence for building discipline subgraphs from federation data. Enforces recursive harvest, authority validation, scaffold-first writes, and promotion-gated canonicalization.',
    p.version = '1.0',
    p.total_steps = 12,
    p.updated = datetime();


// ============================================================================
// STEP DEFINITIONS
// ============================================================================

// Step 1: Confirm agent identity and contract
MERGE (s1:SYS_OnboardingStep {step_id: 'disc_onboard_s01'})
SET s1.step_order = 1,
    s1.label = 'Agent Identity and Contract',
    s1.learns = 'Load agent type, facet, policy and table obligations before discipline processing.',
    s1.query = 'MATCH (a:Agent {name: $agent_name}) OPTIONAL MATCH (a)-[:INSTANCE_OF_TYPE]->(at:SYS_AgentType) RETURN a.name AS agent, a.agent_type AS type, a.governed_by_policies AS policies, a.governed_by_tables AS tables, at.capabilities AS capabilities',
    s1.explanation = 'Do not start discipline traversal until policy/table obligations are loaded.',
    s1.updated = datetime();

// Step 2: Resolve root discipline
MERGE (s2:SYS_OnboardingStep {step_id: 'disc_onboard_s02'})
SET s2.step_order = 2,
    s2.label = 'Resolve Root Discipline Node',
    s2.learns = 'Locate canonical Discipline root and verify authority anchors.',
    s2.query = 'MATCH (d:Discipline {qid: $root_qid}) RETURN d.qid AS qid, d.label AS label, d.lcsh_id AS lcsh_id, d.fast_id AS fast_id, d.ddc AS ddc, d.gnd_id AS gnd_id, d.aat_id AS aat_id',
    s2.explanation = 'If root discipline is missing, protocol stops and raises provisioning request.',
    s2.updated = datetime();

// Step 3: Load recursive budgets and thresholds
MERGE (s3:SYS_OnboardingStep {step_id: 'disc_onboard_s03'})
SET s3.step_order = 3,
    s3.label = 'Load Traversal Budgets',
    s3.learns = 'Load D7/threshold controls for recursive harvest bounds.',
    s3.query = 'MATCH (t:SYS_Threshold) WHERE t.name IN ["max_hops_p279","max_sources_per_seed","max_new_nodes_per_seed","scoping_confidence_domain"] RETURN t.name AS threshold, t.value AS value, t.unit AS unit ORDER BY t.name',
    s3.explanation = 'Recursive exploration is bounded by graph thresholds, never by ad hoc agent choice.',
    s3.updated = datetime();

// Step 4: Load predicate roles and weights
MERGE (s4:SYS_OnboardingStep {step_id: 'disc_onboard_s04'})
SET s4.step_order = 4,
    s4.label = 'Load Predicate Weight Model',
    s4.learns = 'Load semantic roles and signal weights from SYS_WikidataProperty.',
    s4.query = 'MATCH (p:SYS_WikidataProperty) WHERE p.pid IN ["P279","P31","P361","P527","P101","P2578","P921","P1269"] RETURN p.pid AS pid, p.semantic_role AS semantic_role, p.signal_weight AS signal_weight ORDER BY p.signal_weight DESC, p.pid',
    s4.explanation = 'Backlink quality is predicate-aware, not raw-link-count only.',
    s4.updated = datetime();

// Step 5: Recursive backlink discovery (Wikidata-first)
MERGE (s5:SYS_OnboardingStep {step_id: 'disc_onboard_s05'})
SET s5.step_order = 5,
    s5.label = 'Recursive Backlink Discovery',
    s5.learns = 'Harvest candidate nodes by recursive inbound relation traversal from root.',
    s5.query = 'MATCH (dt:SYS_DecisionTable {table_id:"D7_DETERMINE_harvest_allowlist_eligibility"})-[:HAS_ROW]->(r:SYS_DecisionRow) RETURN dt.table_id AS table_id, collect({row:r.row_id, cond:r.conditions, action:r.action}) AS rows',
    s5.explanation = 'Execution engine uses D7 + thresholds to recurse over allowed properties/hops from root_qid.',
    s5.updated = datetime();

// Step 6: Class/type validity gate
MERGE (s6:SYS_OnboardingStep {step_id: 'disc_onboard_s06'})
SET s6.step_order = 6,
    s6.label = 'Entity Validity Gate',
    s6.learns = 'Apply D1/D2/D3/D6 to candidate entities before scope and scoring.',
    s6.query = 'MATCH (dt:SYS_DecisionTable) WHERE dt.table_id IN ["D1_DETERMINE_assertion_class_validity","D2_DETERMINE_value_type_category","D3_DETERMINE_frontier_eligibility","D6_DETERMINE_entity_class_validity"] OPTIONAL MATCH (dt)-[:HAS_ROW]->(r:SYS_DecisionRow) RETURN dt.table_id AS table_id, count(r) AS row_count ORDER BY dt.table_id',
    s6.explanation = 'Reject unsupported datatypes/classes early to control recursion quality.',
    s6.updated = datetime();

// Step 7: Federation scope match
MERGE (s7:SYS_OnboardingStep {step_id: 'disc_onboard_s07'})
SET s7.step_order = 7,
    s7.label = 'Federation Scope Match',
    s7.learns = 'Apply D5 scope logic and route-by-policy before scoring/promotion.',
    s7.query = 'MATCH (dt:SYS_DecisionTable {table_id:"D5_DETERMINE_federation_scope_match"})-[:HAS_ROW]->(r:SYS_DecisionRow) RETURN dt.table_id AS table_id, r.row_id AS row_id, r.conditions AS conditions, r.action AS action ORDER BY r.priority',
    s7.explanation = 'Only in-scope candidates proceed to scaffold and authority scoring.',
    s7.updated = datetime();

// Step 8: Type-target decision (Discipline vs SubjectConcept)
MERGE (s8:SYS_OnboardingStep {step_id: 'disc_onboard_s08'})
SET s8.step_order = 8,
    s8.label = 'Target Type Decision',
    s8.learns = 'Determine promotion target class for each candidate (Discipline or SubjectConcept).',
    s8.query = 'MATCH (et:EntityType) WHERE et.name IN ["Discipline","SubjectConcept","ScaffoldNode"] RETURN et.name AS entity_type, et.required_properties AS required_properties, et.canonical_outbound AS canonical_outbound',
    s8.explanation = 'Candidates are typed before proposal; ambiguous cases become review-required claims.',
    s8.updated = datetime();

// Step 9: Authority scoring + link signal scoring
MERGE (s9:SYS_OnboardingStep {step_id: 'disc_onboard_s09'})
SET s9.step_order = 9,
    s9.label = 'Authority and Signal Scoring',
    s9.learns = 'Run D20 + D21 scoring and map to federation state through D15.',
    s9.query = 'MATCH (a:SYS_DecisionTable)-[:FEEDS_INTO]->(d15:SYS_DecisionTable {table_id:"D15_DETERMINE_federation_state"}) WHERE a.table_id IN ["D20_SCORE_discipline_authority","D21_SCORE_weighted_link_signals"] RETURN a.table_id AS feeder, d15.table_id AS target',
    s9.explanation = 'Confidence is produced from explicit score tables, not narrative heuristics.',
    s9.updated = datetime();

// Step 10: Scaffold-only write discipline
MERGE (s10:SYS_OnboardingStep {step_id: 'disc_onboard_s10'})
SET s10.step_order = 10,
    s10.label = 'Scaffold-Only Writes',
    s10.learns = 'Ensure discovery outputs are scaffolded (ADR-006) before promotion.',
    s10.query = 'MATCH (et:EntityType) WHERE et.name IN ["ScaffoldNode","ScaffoldEdge"] RETURN et.name AS scaffold_type, et.required_properties AS required_properties',
    s10.explanation = 'No direct canonical writes from discovery agents.',
    s10.updated = datetime();

// Step 11: Constitution mapping
MERGE (s11:SYS_OnboardingStep {step_id: 'disc_onboard_s11'})
SET s11.step_order = 11,
    s11.label = 'Constitution Layer Resolution',
    s11.learns = 'Resolve D9 outputs to machine-usable constitution_doc_ids for facet interpretation.',
    s11.query = 'MATCH (dt:SYS_DecisionTable {table_id:"D9_DETERMINE_SFA_constitution_layer"})-[:HAS_ROW]->(r:SYS_DecisionRow) RETURN r.row_id AS row_id, r.conditions AS conditions, r.outputs AS outputs ORDER BY r.row_id',
    s11.explanation = 'Facet-specific interpretation must be retrieved from D9 outputs, not free-form prose.',
    s11.updated = datetime();

// Step 12: Promotion gate and exemplar alignment
MERGE (s12:SYS_OnboardingStep {step_id: 'disc_onboard_s12'})
SET s12.step_order = 12,
    s12.label = 'Promotion Gate and Exemplar Check',
    s12.learns = 'Validate proposed claims against D10 and golden exemplar shape before promotion request.',
    s12.query = 'MATCH (dt:SYS_DecisionTable {table_id:"D10_DETERMINE_claim_promotion_eligibility"})-[:HAS_ROW]->(r:SYS_DecisionRow) RETURN dt.table_id AS table_id, r.row_id AS row_id, r.conditions AS conditions, r.action AS action ORDER BY r.priority',
    s12.explanation = 'Canonical graph change happens only through promotion-gated claim lifecycle.',
    s12.updated = datetime();


// ============================================================================
// LINK STEPS TO PROTOCOL + CHAIN ORDER
// ============================================================================

MATCH (p:SYS_OnboardingProtocol {protocol_id: 'onboard_discipline_v1'})
MATCH (s:SYS_OnboardingStep)
WHERE s.step_id STARTS WITH 'disc_onboard_s'
MERGE (p)-[:HAS_STEP]->(s);

UNWIND range(1, 11) AS i
MATCH (curr:SYS_OnboardingStep {step_order: i})
MATCH (next:SYS_OnboardingStep {step_order: i + 1})
WHERE curr.step_id STARTS WITH 'disc_onboard_s'
  AND next.step_id STARTS WITH 'disc_onboard_s'
MERGE (curr)-[:NEXT_STEP]->(next);


// ============================================================================
// VERIFICATION
// ============================================================================

MATCH (p:SYS_OnboardingProtocol {protocol_id: 'onboard_discipline_v1'})-[:HAS_STEP]->(s:SYS_OnboardingStep)
RETURN p.protocol_id AS protocol,
       count(s) AS step_count,
       min(s.step_order) AS first_step,
       max(s.step_order) AS last_step;

MATCH (s1:SYS_OnboardingStep)-[:NEXT_STEP]->(s2:SYS_OnboardingStep)
WHERE s1.step_id STARTS WITH 'disc_onboard_s' AND s2.step_id STARTS WITH 'disc_onboard_s'
RETURN count(*) AS next_step_edges;
