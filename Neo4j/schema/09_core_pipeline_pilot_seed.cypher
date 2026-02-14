// ============================================================================
// CHRYSTALLUM NEO4J: CORE PIPELINE PILOT SEED
// ============================================================================
// File: 09_core_pipeline_pilot_seed.cypher
// Purpose: Seed a minimal non-temporal pilot flow:
//   SubjectConcept <-domain- Agent -> Claim -> AnalysisRun -> FacetAssessment
// Notes:
// - Uses MERGE so it is safe to rerun.
// - Assumes 07_core_pipeline_schema.cypher has already been applied.
// ============================================================================

// 1) Subject concept domain anchor
MERGE (sc:SubjectConcept {subject_id: 'subj_q17167_roman_republic'})
SET sc.label = 'Roman Republic',
    sc.facet = 'Political',
    sc.authority_id = 'sh85115055',
    sc.fast_id = 'fst01204885',
    sc.lcc_class = 'DG',
    sc.entity_type = 'SubjectConcept',
    sc.status = 'active';

// 2) Agent specialized in that domain
MERGE (a:Agent {agent_id: 'agent_q17167_roman_republic_v1'})
SET a.label = 'Roman Republic Specialist',
    a.agent_type = 'subject',
    a.description = 'Pilot subject agent for Roman Republic claim flow',
    a.version = 'v1.0',
    a.created_at = toString(datetime());

MATCH (a:Agent {agent_id: 'agent_q17167_roman_republic_v1'})
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167_roman_republic'})
MERGE (a)-[:OWNS_DOMAIN]->(sc);

// 3) Core claim
MERGE (c:Claim {claim_id: 'claim_q17167_end_date_neg0027'})
SET c.cipher = '8a8f9e79c1f271d90a0afad7d7d1f3e2b7e572f3bb8db4c8e0a4215ef3a27f12',
    c.label = 'Roman Republic Ended in 27 BCE',
    c.text = 'The Roman Republic ended in 27 BCE.',
    c.claim_type = 'factual',
    c.source_agent = 'agent_q17167_roman_republic_v1',
    c.timestamp = toString(datetime()),
    c.status = 'proposed',
    c.confidence = 0.92,
    c.subject_entity_qid = 'Q17167',
    c.property_name = 'end_date',
    c.property_value = '-0027';

MATCH (a:Agent {agent_id: 'agent_q17167_roman_republic_v1'})
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167_roman_republic'})
MATCH (c:Claim {claim_id: 'claim_q17167_end_date_neg0027'})
MERGE (a)-[:MADE_CLAIM]->(c)
MERGE (sc)-[:SUBJECT_OF]->(c);

// 4) Retrieval context (provenance container)
MERGE (rc:RetrievalContext {retrieval_id: 'retr_q17167_wikidata_end_date_neg0027'})
SET rc.agent_id = 'agent_q17167_roman_republic_v1',
    rc.timestamp = toString(datetime()),
    rc.source = 'wikidata',
    rc.seed_qid = 'Q17167';

MATCH (c:Claim {claim_id: 'claim_q17167_end_date_neg0027'})
MATCH (rc:RetrievalContext {retrieval_id: 'retr_q17167_wikidata_end_date_neg0027'})
MERGE (c)-[:USED_CONTEXT]->(rc);

// 5) Analysis run + one facet assessment
MERGE (run:AnalysisRun {run_id: 'run_q17167_end_date_neg0027'})
SET run.pipeline_version = 'v1.0',
    run.status = 'completed',
    run.created_at = toString(datetime());

MATCH (c:Claim {claim_id: 'claim_q17167_end_date_neg0027'})
MATCH (run:AnalysisRun {run_id: 'run_q17167_end_date_neg0027'})
MERGE (c)-[:HAS_ANALYSIS_RUN]->(run);

MERGE (f:Facet {facet_id: 'facet_political', label: 'Political'});

MERGE (fa:FacetAssessment {assessment_id: 'fa_q17167_political_end_date_neg0027'})
SET fa.score = 0.95,
    fa.status = 'supported',
    fa.rationale = 'Direct alignment with canonical period boundary (27 BCE).',
    fa.created_at = toString(datetime()),
    fa.evidence_count = 1;

MATCH (run:AnalysisRun {run_id: 'run_q17167_end_date_neg0027'})
MATCH (fa:FacetAssessment {assessment_id: 'fa_q17167_political_end_date_neg0027'})
MATCH (f:Facet {facet_id: 'facet_political'})
MATCH (a:Agent {agent_id: 'agent_q17167_roman_republic_v1'})
MERGE (run)-[:HAS_FACET_ASSESSMENT]->(fa)
MERGE (fa)-[:ASSESSES_FACET]->(f)
MERGE (fa)-[:EVALUATED_BY]->(a);
