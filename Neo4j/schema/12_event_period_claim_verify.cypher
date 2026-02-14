// ============================================================================
// CHRYSTALLUM NEO4J: EVENT + PERIOD + CLAIM PILOT VERIFY
// ============================================================================
// File: 12_event_period_claim_verify.cypher
// ============================================================================

MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MATCH (pl:Place {entity_id: 'plc_actium_q41747'})
OPTIONAL MATCH (e)-[:OCCURRED_DURING]->(p)
OPTIONAL MATCH (e)-[:OCCURRED_AT]->(pl)
OPTIONAL MATCH (e)-[:STARTS_IN_YEAR]->(ys:Year)
OPTIONAL MATCH (e)-[:ENDS_IN_YEAR]->(ye:Year)
OPTIONAL MATCH (e)-[:SUBJECT_OF]->(c2:Claim {claim_id: 'claim_actium_in_republic_31bce_001'})
OPTIONAL MATCH (p)-[:SUBJECT_OF]->(c2)
OPTIONAL MATCH (c2)-[:USED_CONTEXT]->(rc2:RetrievalContext {retrieval_id: 'retr_actium_q193304_001'})
OPTIONAL MATCH (c2)-[:HAS_ANALYSIS_RUN]->(run2:AnalysisRun {run_id: 'run_actium_001'})
OPTIONAL MATCH (run2)-[:HAS_FACET_ASSESSMENT]->(fa2:FacetAssessment {assessment_id: 'fa_actium_mil_001'})
OPTIONAL MATCH (fa2)-[:ASSESSES_FACET]->(f2:Facet {facet_id: 'facet_military'})
RETURN
  e.label AS event_label,
  e.qid AS event_qid,
  p.label AS period_label,
  p.qid AS period_qid,
  pl.label AS place_label,
  ys.year AS event_start_year,
  ye.year AS event_end_year,
  c2.claim_id AS claim_id,
  c2.label AS claim_label,
  c2.status AS claim_status,
  rc2.retrieval_id AS retrieval_id,
  run2.run_id AS run_id,
  fa2.assessment_id AS assessment_id,
  f2.label AS assessed_facet;
