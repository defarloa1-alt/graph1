// ============================================================================
// CHRYSTALLUM NEO4J: EVENT + PERIOD + CLAIM PILOT SEED
// ============================================================================
// File: 11_event_period_claim_seed.cypher
// Purpose:
// - Add one concrete Period + Event (+ Place) cluster
// - Add a second claim tied to concrete entities for promotion-flow testing
// Notes:
// - Safe to rerun (MERGE used throughout)
// - Requires Year backbone to include years -510, -27, -31
// ============================================================================

// 1) Period: Roman Republic (Q17167)
MERGE (p:Period {entity_id: 'prd_roman_republic_q17167'})
SET p.label = 'Roman Republic',
    p.qid = 'Q17167',
    p.start = '-0510',
    p.end = '-0027',
    p.start_date_min = '-0510-01-01',
    p.start_date_max = '-0510-12-31',
    p.end_date_min = '-0027-01-01',
    p.end_date_max = '-0027-12-31',
    p.entity_type = 'Period',
    p.facet = 'Political',
    p.status = 'active';

MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MATCH (y_start:Year {year: -510})
MATCH (y_end:Year {year: -27})
MERGE (p)-[:STARTS_IN_YEAR]->(y_start)
MERGE (p)-[:ENDS_IN_YEAR]->(y_end);

// 2) Place: Actium (Q41747)
MERGE (pl:Place {entity_id: 'plc_actium_q41747'})
SET pl.label = 'Actium',
    pl.qid = 'Q41747',
    pl.place_type = 'place',
    pl.modern_country = 'Greece',
    pl.entity_type = 'Place',
    pl.status = 'active';

// 3) Event: Battle of Actium (Q193304)
MERGE (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
SET e.label = 'Battle of Actium',
    e.qid = 'Q193304',
    e.entity_type = 'Event',
    e.event_type = 'battle',
    e.start_date = '-0031-09-02',
    e.end_date = '-0031-09-02',
    e.start_date_min = '-0031-09-02',
    e.start_date_max = '-0031-09-02',
    e.end_date_min = '-0031-09-02',
    e.end_date_max = '-0031-09-02',
    e.date_precision = 'day',
    e.status = 'active';

MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MATCH (pl:Place {entity_id: 'plc_actium_q41747'})
MATCH (y_event:Year {year: -31})
MERGE (e)-[:OCCURRED_DURING]->(p)
MERGE (e)-[:OCCURRED_AT]->(pl)
MERGE (e)-[:STARTS_IN_YEAR]->(y_event)
MERGE (e)-[:ENDS_IN_YEAR]->(y_event);

// 4) Tie entities to existing SubjectConcept domain
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167_roman_republic'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MERGE (p)-[:HAS_SUBJECT_CONCEPT]->(sc)
MERGE (e)-[:HAS_SUBJECT_CONCEPT]->(sc);

// 5) Second claim: event-period temporal grounding
MERGE (c2:Claim {claim_id: 'claim_q193304_occurred_during_q17167_neg0031_09_02'})
SET c2.cipher = 'b2a2c3d4e5f60718293a4b5c6d7e8f90112233445566778899aabbccddeeff01',
    c2.label = 'Battle of Actium Occurred During Roman Republic',
    c2.text = 'The Battle of Actium occurred during the Roman Republic in 31 BCE.',
    c2.claim_type = 'temporal',
    c2.source_agent = 'agent_q17167_roman_republic_v1',
    c2.timestamp = toString(datetime()),
    c2.status = 'proposed',
    c2.confidence = 0.94,
    c2.subject_entity_qid = 'Q193304',
    c2.object_entity_qid = 'Q17167',
    c2.relationship_type = 'OCCURRED_DURING',
    c2.temporal_data = '-0031-09-02';

MATCH (a:Agent {agent_id: 'agent_q17167_roman_republic_v1'})
MATCH (sc:SubjectConcept {subject_id: 'subj_q17167_roman_republic'})
MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MATCH (c2:Claim {claim_id: 'claim_q193304_occurred_during_q17167_neg0031_09_02'})
MERGE (a)-[:MADE_CLAIM]->(c2)
MERGE (sc)-[:SUBJECT_OF]->(c2)
MERGE (e)-[:SUBJECT_OF]->(c2)
MERGE (p)-[:SUBJECT_OF]->(c2);

// 6) Retrieval context + analysis for second claim
MERGE (rc2:RetrievalContext {retrieval_id: 'retr_q193304_wikidata_occurred_during_q17167'})
SET rc2.agent_id = 'agent_q17167_roman_republic_v1',
    rc2.timestamp = toString(datetime()),
    rc2.source = 'wikidata',
    rc2.seed_qid = 'Q193304';

MATCH (c2:Claim {claim_id: 'claim_q193304_occurred_during_q17167_neg0031_09_02'})
MATCH (rc2:RetrievalContext {retrieval_id: 'retr_q193304_wikidata_occurred_during_q17167'})
MERGE (c2)-[:USED_CONTEXT]->(rc2);

MERGE (run2:AnalysisRun {run_id: 'run_q193304_occurred_during_q17167'})
SET run2.pipeline_version = 'v1.0',
    run2.status = 'completed',
    run2.created_at = toString(datetime());

MATCH (c2:Claim {claim_id: 'claim_q193304_occurred_during_q17167_neg0031_09_02'})
MATCH (run2:AnalysisRun {run_id: 'run_q193304_occurred_during_q17167'})
MERGE (c2)-[:HAS_ANALYSIS_RUN]->(run2);

MERGE (f2:Facet {facet_id: 'facet_military', label: 'Military'});

MERGE (fa2:FacetAssessment {assessment_id: 'fa_q193304_military_occurred_during_q17167'})
SET fa2.score = 0.93,
    fa2.status = 'supported',
    fa2.rationale = 'Event date and period boundaries align and historical consensus is high.',
    fa2.created_at = toString(datetime()),
    fa2.evidence_count = 1;

MATCH (run2:AnalysisRun {run_id: 'run_q193304_occurred_during_q17167'})
MATCH (fa2:FacetAssessment {assessment_id: 'fa_q193304_military_occurred_during_q17167'})
MATCH (f2:Facet {facet_id: 'facet_military'})
MATCH (a:Agent {agent_id: 'agent_q17167_roman_republic_v1'})
MERGE (run2)-[:HAS_FACET_ASSESSMENT]->(fa2)
MERGE (fa2)-[:ASSESSES_FACET]->(f2)
MERGE (fa2)-[:EVALUATED_BY]->(a);
