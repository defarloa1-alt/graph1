// ============================================================================
// CHRYSTALLUM NEO4J: CLAIM PROMOTION (PILOT)
// ============================================================================
// File: 14_claim_promotion_seed.cypher
// Purpose:
// - Promote one validated-ready claim into canonical state
// - Attach canonical entities/relationships (event-period-place) to claim provenance via SUPPORTED_BY
// Target claim:
//   claim_q193304_occurred_during_q17167_neg0031_09_02
// Notes:
// - Idempotent (safe to rerun)
// - Applies policy-driven guard fields persisted by Pi:
//   policy_min_confidence/policy_max_confidence, require_* flags, policy_gate_status
// - Transitional fallback: if policy fields are missing, use legacy confidence >= 0.90
// - Canonical entity IDs follow qid-concatenated pattern:
//   evt_battle_of_actium_q193304, prd_roman_republic_q17167, plc_actium_q41747
// ============================================================================

// 1) Promote claim status when guard passes (parser-safe guard pattern)
MATCH (c:Claim {claim_id: 'claim_q193304_occurred_during_q17167_neg0031_09_02'})
OPTIONAL MATCH (c)-[:USED_CONTEXT]->(rc:RetrievalContext)
WITH c, count(rc) AS rc_count
OPTIONAL MATCH (c)-[:HAS_ANALYSIS_RUN]->(ar:AnalysisRun)
WITH c, rc_count, count(ar) AS ar_count
WHERE (
    (
      c.policy_gate_status = 'auto_promote_eligible'
      AND c.confidence >= c.policy_min_confidence
      AND c.confidence <= c.policy_max_confidence
      AND coalesce(c.require_debate_bridge, false) = false
      AND coalesce(c.require_expert_review, false) = false
    )
    OR
    (
      c.policy_gate_status IS NULL
      AND c.confidence >= 0.90
    )
  )
  AND rc_count > 0
  AND ar_count > 0
SET c.status = 'validated',
    c.promotion_date = toString(datetime()),
    c.promoted = true;

// 2) Ensure canonical relationships exist and mark provenance metadata
MATCH (c:Claim {claim_id: 'claim_q193304_occurred_during_q17167_neg0031_09_02', status: 'validated'})
MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MATCH (pl:Place {entity_id: 'plc_actium_q41747'})
MERGE (e)-[r:OCCURRED_DURING]->(p)
SET r.promoted_from_claim_id = c.claim_id,
    r.promotion_date = toString(datetime()),
    r.promotion_status = 'canonical'
MERGE (e)-[ra:OCCURRED_AT]->(pl)
SET ra.promoted_from_claim_id = c.claim_id,
    ra.promotion_date = toString(datetime()),
    ra.promotion_status = 'canonical';

// 3) Link canonical facts back to claim for traceability
MATCH (c:Claim {claim_id: 'claim_q193304_occurred_during_q17167_neg0031_09_02', status: 'validated'})
MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MATCH (pl:Place {entity_id: 'plc_actium_q41747'})
MERGE (e)-[se:SUPPORTED_BY]->(c)
SET se.claim_id = c.claim_id,
    se.promotion_date = toString(datetime())
WITH c, p, pl
MERGE (p)-[sp:SUPPORTED_BY]->(c)
SET sp.claim_id = c.claim_id,
    sp.promotion_date = toString(datetime())
WITH c, pl
MERGE (pl)-[spl:SUPPORTED_BY]->(c)
SET spl.claim_id = c.claim_id,
    spl.promotion_date = toString(datetime());
