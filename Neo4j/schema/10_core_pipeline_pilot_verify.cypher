// ============================================================================
// CHRYSTALLUM NEO4J: CORE PIPELINE PILOT VERIFY
// ============================================================================
// File: 10_core_pipeline_pilot_verify.cypher
// Purpose: Verify seeded pilot cluster for SubjectConcept + Agent + Claim flow.
// ============================================================================

MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_001'})
OPTIONAL MATCH (a:Agent {agent_id: 'agent_roman_republic_v1'})-[:OWNS_DOMAIN]->(sc)
OPTIONAL MATCH (a)-[:MADE_CLAIM]->(c:Claim {claim_id: 'claim_roman_republic_end_27bce_001'})
OPTIONAL MATCH (sc)-[:SUBJECT_OF]->(c)
OPTIONAL MATCH (c)-[:USED_CONTEXT]->(rc:RetrievalContext {retrieval_id: 'retr_roman_republic_q17167_001'})
OPTIONAL MATCH (c)-[:HAS_ANALYSIS_RUN]->(run:AnalysisRun {run_id: 'run_roman_republic_001'})
OPTIONAL MATCH (run)-[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment {assessment_id: 'fa_roman_republic_pol_001'})
OPTIONAL MATCH (fa)-[:ASSESSES_FACET]->(f:Facet {facet_id: 'facet_political'})
RETURN
  sc.subject_id AS subject_id,
  sc.label AS subject_label,
  a.agent_id AS agent_id,
  c.claim_id AS claim_id,
  c.label AS claim_label,
  c.status AS claim_status,
  rc.retrieval_id AS retrieval_id,
  run.run_id AS run_id,
  fa.assessment_id AS assessment_id,
  f.label AS assessed_facet;
