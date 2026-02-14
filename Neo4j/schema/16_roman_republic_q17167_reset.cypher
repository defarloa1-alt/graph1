// ============================================================================
// CHRYSTALLUM NEO4J: ROMAN REPUBLIC (Q17167) PILOT RESET
// ============================================================================
// File: 16_roman_republic_q17167_reset.cypher
// Purpose:
// - Clear disposable pilot data for the Roman Republic flow
// - Remove both legacy IDs and current deterministic IDs
// Notes:
// - Safe to rerun
// - Keeps global schema/index/constraint/year backbone intact
// ============================================================================

// 1) Remove claims first (detaches all promotion/provenance rels)
MATCH (c:Claim)
WHERE c.claim_id IN [
  'claim_roman_republic_end_27bce_001',
  'claim_actium_in_republic_31bce_001',
  'claim_q17167_end_date_neg0027',
  'claim_q193304_occurred_during_q17167_neg0031_09_02'
]
DETACH DELETE c;

// 2) Remove retrieval context + analysis artifacts
MATCH (rc:RetrievalContext)
WHERE rc.retrieval_id IN [
  'retr_roman_republic_q17167_001',
  'retr_actium_q193304_001',
  'retr_q17167_wikidata_end_date_neg0027',
  'retr_q193304_wikidata_occurred_during_q17167'
]
DETACH DELETE rc;

MATCH (run:AnalysisRun)
WHERE run.run_id IN [
  'run_roman_republic_001',
  'run_actium_001',
  'run_q17167_end_date_neg0027',
  'run_q193304_occurred_during_q17167'
]
DETACH DELETE run;

MATCH (fa:FacetAssessment)
WHERE fa.assessment_id IN [
  'fa_roman_republic_pol_001',
  'fa_actium_mil_001',
  'fa_q17167_political_end_date_neg0027',
  'fa_q193304_military_occurred_during_q17167'
]
DETACH DELETE fa;

// 3) Remove domain anchor + agent
MATCH (a:Agent)
WHERE a.agent_id IN ['agent_roman_republic_v1', 'agent_q17167_roman_republic_v1']
DETACH DELETE a;

MATCH (sc:SubjectConcept)
WHERE sc.subject_id IN ['subj_roman_republic_001', 'subj_q17167_roman_republic']
DETACH DELETE sc;

// 4) Remove seeded event-period-place cluster for this pilot
MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
DETACH DELETE e;

MATCH (pl:Place {entity_id: 'plc_actium_q41747'})
DETACH DELETE pl;

MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
DETACH DELETE p;

RETURN 'roman_republic_q17167_reset_complete' AS status;
