// ============================================================================
// CHRYSTALLUM: DISCIPLINE BOOTSTRAP RUN CHECKS
// ============================================================================
// File: 19_discipline_bootstrap_run_checks.cypher
// Purpose:
//   Read-only verification checks for discipline kernel/scoring/protocol wiring.
//   Safe to rerun anytime after scripts 17 and 18.
// ============================================================================


// 1) Legacy Discipline rel names should be gone
MATCH (:Discipline)-[r]->(:Discipline)
WHERE type(r) IN ['SUBCLASS_OF', 'BROADER_THAN', 'PART_OF', 'HAS_PART']
RETURN 'legacy_discipline_relationships' AS check_name,
       type(r) AS rel_type,
       count(*) AS cnt
ORDER BY rel_type;


// 2) Canonical discipline relationship counts
MATCH (:Discipline)-[r]->(:Discipline)
WHERE type(r) IN ['DISCIPLINE_SUBCLASS_OF', 'DISCIPLINE_BROADER_THAN', 'DISCIPLINE_PART_OF', 'DISCIPLINE_HAS_PART']
RETURN 'canonical_discipline_relationships' AS check_name,
       type(r) AS rel_type,
       count(*) AS cnt
ORDER BY rel_type;


// 3) D20/D21 table + row counts
MATCH (dt:SYS_DecisionTable)
WHERE dt.table_id IN ['D20_SCORE_discipline_authority', 'D21_SCORE_weighted_link_signals']
OPTIONAL MATCH (dt)-[:HAS_ROW]->(r:SYS_DecisionRow)
RETURN 'd20_d21_row_counts' AS check_name,
       dt.table_id AS table_id,
       count(r) AS row_count
ORDER BY dt.table_id;


// 4) D20/D21 -> D15 FEEDS_INTO wiring
MATCH (a:SYS_DecisionTable)-[:FEEDS_INTO]->(d15:SYS_DecisionTable {table_id:'D15_DETERMINE_federation_state'})
WHERE a.table_id IN ['D20_SCORE_discipline_authority', 'D21_SCORE_weighted_link_signals']
RETURN 'd20_d21_feeds_d15' AS check_name,
       collect(a.table_id) AS feeders,
       count(*) AS edge_count;


// 5) D9 outputs should be machine-usable constitution_doc_ids
MATCH (d9:SYS_DecisionTable {table_id:'D9_DETERMINE_SFA_constitution_layer'})
OPTIONAL MATCH (d9)-[:HAS_ROW]->(r:SYS_DecisionRow)
RETURN 'd9_machine_outputs' AS check_name,
       d9.outputs AS table_outputs,
       collect({row_id:r.row_id, conditions:r.conditions, outputs:r.outputs}) AS rows;


// 6) Protocol cardinality and bounds
MATCH (p:SYS_OnboardingProtocol {protocol_id:'onboard_discipline_v1'})-[:HAS_STEP]->(s:SYS_OnboardingStep)
RETURN 'protocol_step_count' AS check_name,
       p.protocol_id AS protocol,
       count(s) AS step_count,
       min(s.step_order) AS first_step,
       max(s.step_order) AS last_step;


// 7) NEXT_STEP chain edge count should be 11 for 12-step protocol
MATCH (s1:SYS_OnboardingStep)-[:NEXT_STEP]->(s2:SYS_OnboardingStep)
WHERE s1.step_id STARTS WITH 'disc_onboard_s'
  AND s2.step_id STARTS WITH 'disc_onboard_s'
RETURN 'protocol_next_edges' AS check_name,
       count(*) AS next_step_edges;


// 8) Detect missing chain transitions (should return no rows)
UNWIND range(1, 11) AS i
MATCH (curr:SYS_OnboardingStep {step_order:i})
MATCH (next:SYS_OnboardingStep {step_order:i+1})
WHERE curr.step_id STARTS WITH 'disc_onboard_s'
  AND next.step_id STARTS WITH 'disc_onboard_s'
  AND NOT (curr)-[:NEXT_STEP]->(next)
RETURN 'missing_chain_transition' AS check_name,
       curr.step_order AS from_step,
       next.step_order AS to_step;
