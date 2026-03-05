// ============================================================================
// Hardcoded Rules Migration — 2026-03-03
// ============================================================================
// PURPOSE: Migrate hardcoded federation scoring rules from Python to graph.
//   D41/D42 — Federation scoring: state boundaries, weights → SYS_Threshold
//   D15-D18 already exist in 16_dm_rules_from_code.cypher; this adds
//   SYS_Threshold nodes for place_period_subgraph weights and state boundaries.
// IDEMPOTENT: All statements use MERGE
// Run after: add_dmn_threshold_policy_nodes.cypher, 16_dm_rules_from_code.cypher
// ============================================================================

// ── D41/D42: Federation scoring weights and state boundaries ─────────────────
// Source: scripts/federation/federation_scorer.py
// Decision tables: D15 (state), D16 (place), D17 (period), D18 (subject)

// Place+Period+Geo subgraph weights (score_place_period_subgraph)
MERGE (t:SYS_Threshold {name: 'federation_weight_place_qid'})
SET t.value = 30, t.unit = 'points', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'What: Place federated to Wikidata',
    t.dimension = 'place_period_subgraph', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_weight_period_qid'})
SET t.value = 30, t.unit = 'points', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'When: Period federated to Wikidata',
    t.dimension = 'place_period_subgraph', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_weight_geo_context_qid'})
SET t.value = 20, t.unit = 'points', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'Where: Geographic context federated',
    t.dimension = 'place_period_subgraph', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_weight_temporal_bounds'})
SET t.value = 15, t.unit = 'points', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'Temporal signal present',
    t.dimension = 'place_period_subgraph', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_weight_relationships'})
SET t.value = 5, t.unit = 'points', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'Vertex jump edges exist',
    t.dimension = 'place_period_subgraph', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_periodo_half_credit'})
SET t.value = 0.5, t.unit = 'ratio', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'Half credit for periodo_id without qid when scoring period',
    t.dimension = 'place_period_subgraph', t.last_reviewed = '2026-03-03', t.system = true;

// D15 state boundaries (min_score, max_score) — stored as JSON or separate rows
// FS0: 0-39, FS1: 40-59, FS2: 60-79, FS3: 80-100
MERGE (t:SYS_Threshold {name: 'federation_state_FS0_max'})
SET t.value = 39, t.unit = 'score', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'FS0_UNFEDERATED: score 0-39',
    t.state_name = 'FS0_UNFEDERATED', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_state_FS1_min'})
SET t.value = 40, t.unit = 'score', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'FS1_BASE: score 40-59',
    t.state_name = 'FS1_BASE', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_state_FS1_max'})
SET t.value = 59, t.unit = 'score', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'FS1_BASE: score 40-59',
    t.state_name = 'FS1_BASE', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_state_FS2_min'})
SET t.value = 60, t.unit = 'score', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'FS2_FEDERATED: score 60-79',
    t.state_name = 'FS2_FEDERATED', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_state_FS2_max'})
SET t.value = 79, t.unit = 'score', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'FS2_FEDERATED: score 60-79',
    t.state_name = 'FS2_FEDERATED', t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_state_FS3_min'})
SET t.value = 80, t.unit = 'score', t.decision_table = 'D15_DETERMINE_federation_state',
    t.rationale = 'FS3_WELL_FEDERATED: score 80-100',
    t.state_name = 'FS3_WELL_FEDERATED', t.last_reviewed = '2026-03-03', t.system = true;

// D16 place_simple weights (pleiades, qid, temporal, coords)
MERGE (t:SYS_Threshold {name: 'federation_place_pleiades_points'})
SET t.value = 20, t.unit = 'points', t.decision_table = 'D16_SCORE_place_federation',
    t.rationale = 'Place has Pleiades ID',
    t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_place_qid_points'})
SET t.value = 50, t.unit = 'points', t.decision_table = 'D16_SCORE_place_federation',
    t.rationale = 'Place has Wikidata QID',
    t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_place_temporal_points'})
SET t.value = 20, t.unit = 'points', t.decision_table = 'D16_SCORE_place_federation',
    t.rationale = 'Place has temporal bounds',
    t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_place_coords_points'})
SET t.value = 10, t.unit = 'points', t.decision_table = 'D16_SCORE_place_federation',
    t.rationale = 'Place has lat/long coordinates',
    t.last_reviewed = '2026-03-03', t.system = true;

// D17 period_simple weights
MERGE (t:SYS_Threshold {name: 'federation_period_periodo_points'})
SET t.value = 30, t.unit = 'points', t.decision_table = 'D17_SCORE_period_federation',
    t.rationale = 'Period has PeriodO ID',
    t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_period_qid_points'})
SET t.value = 50, t.unit = 'points', t.decision_table = 'D17_SCORE_period_federation',
    t.rationale = 'Period has Wikidata QID',
    t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_period_temporal_points'})
SET t.value = 20, t.unit = 'points', t.decision_table = 'D17_SCORE_period_federation',
    t.rationale = 'Period has temporal bounds',
    t.last_reviewed = '2026-03-03', t.system = true;

// D18 subject_authority weights
MERGE (t:SYS_Threshold {name: 'federation_subject_lcsh_points'})
SET t.value = 30, t.unit = 'points', t.decision_table = 'D18_SCORE_subject_authority',
    t.rationale = 'SubjectConcept has LCSH ID',
    t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_subject_fast_points'})
SET t.value = 30, t.unit = 'points', t.decision_table = 'D18_SCORE_subject_authority',
    t.rationale = 'SubjectConcept has FAST ID',
    t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_subject_lcc_points'})
SET t.value = 20, t.unit = 'points', t.decision_table = 'D18_SCORE_subject_authority',
    t.rationale = 'SubjectConcept has LCC class',
    t.last_reviewed = '2026-03-03', t.system = true;

MERGE (t:SYS_Threshold {name: 'federation_subject_qid_points'})
SET t.value = 20, t.unit = 'points', t.decision_table = 'D18_SCORE_subject_authority',
    t.rationale = 'SubjectConcept has Wikidata QID',
    t.last_reviewed = '2026-03-03', t.system = true;

// Link D15 to SYS_Threshold (USES_THRESHOLD)
MATCH (dt:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})
MATCH (t:SYS_Threshold) WHERE t.decision_table = 'D15_DETERMINE_federation_state'
MERGE (dt)-[:USES_THRESHOLD]->(t);

// ============================================================================
// VERIFICATION
// ============================================================================
// MATCH (t:SYS_Threshold) WHERE t.name STARTS WITH 'federation_' RETURN t.name, t.value
// MATCH (dt:SYS_DecisionTable {table_id: 'D15_DETERMINE_federation_state'})-[:USES_THRESHOLD]->(t) RETURN count(t)
