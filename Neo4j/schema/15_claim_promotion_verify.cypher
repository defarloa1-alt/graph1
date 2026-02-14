// ============================================================================
// CHRYSTALLUM NEO4J: CLAIM PROMOTION VERIFY (PILOT)
// ============================================================================
// File: 15_claim_promotion_verify.cypher
// ============================================================================

MATCH (c:Claim {claim_id: 'claim_actium_in_republic_31bce_001'})
MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
OPTIONAL MATCH (e)-[r:OCCURRED_DURING]->(p)
OPTIONAL MATCH (e)-[se:SUPPORTED_BY]->(c)
OPTIONAL MATCH (p)-[sp:SUPPORTED_BY]->(c)
RETURN
  c.claim_id AS claim_id,
  c.label AS claim_label,
  c.status AS claim_status,
  c.promoted AS claim_promoted,
  c.promotion_date AS claim_promotion_date,
  type(r) AS canonical_rel_type,
  r.promoted_from_claim_id AS rel_promoted_from_claim_id,
  r.promotion_status AS rel_promotion_status,
  se.claim_id AS event_supported_by_claim_id,
  sp.claim_id AS period_supported_by_claim_id;

