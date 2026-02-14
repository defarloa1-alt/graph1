// ============================================================================
// CHRYSTALLUM NEO4J: CLAIM PROMOTION (PILOT)
// ============================================================================
// File: 14_claim_promotion_seed.cypher
// Purpose:
// - Promote one validated-ready claim into canonical state
// - Attach canonical entities/relationship to claim provenance via SUPPORTED_BY
// Target claim:
//   claim_actium_in_republic_31bce_001
// Notes:
// - Idempotent (safe to rerun)
// - Applies a simple guard: confidence >= 0.90 and required context edges present
// ============================================================================

// 1) Promote claim status when guard passes
MATCH (c:Claim {claim_id: 'claim_actium_in_republic_31bce_001'})
WHERE c.confidence >= 0.90
  AND EXISTS { MATCH (c)-[:USED_CONTEXT]->(:RetrievalContext) }
  AND EXISTS { MATCH (c)-[:HAS_ANALYSIS_RUN]->(:AnalysisRun) }
SET c.status = 'validated',
    c.promotion_date = toString(datetime()),
    c.promoted = true;

// 2) Ensure canonical relationship exists and mark provenance metadata
MATCH (c:Claim {claim_id: 'claim_actium_in_republic_31bce_001', status: 'validated'})
MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MERGE (e)-[r:OCCURRED_DURING]->(p)
SET r.promoted_from_claim_id = c.claim_id,
    r.promotion_date = toString(datetime()),
    r.promotion_status = 'canonical';

// 3) Link canonical facts back to claim for traceability
MATCH (c:Claim {claim_id: 'claim_actium_in_republic_31bce_001', status: 'validated'})
MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MERGE (e)-[se:SUPPORTED_BY]->(c)
SET se.claim_id = c.claim_id,
    se.promotion_date = toString(datetime());

MERGE (p)-[sp:SUPPORTED_BY]->(c)
SET sp.claim_id = c.claim_id,
    sp.promotion_date = toString(datetime());

