// ============================================================================
// CHRYSTALLUM NEO4J: CLAIM PROMOTION VERIFY (PILOT)
// ============================================================================
// File: 15_claim_promotion_verify.cypher
// ============================================================================

MATCH (c:Claim {claim_id: 'claim_q193304_occurred_during_q17167_neg0031_09_02'})
MATCH (e:Event {entity_id: 'evt_battle_of_actium_q193304'})
MATCH (p:Period {entity_id: 'prd_roman_republic_q17167'})
MATCH (pl:Place {entity_id: 'plc_actium_q41747'})
OPTIONAL MATCH (e)-[r:OCCURRED_DURING]->(p)
OPTIONAL MATCH (e)-[ra:OCCURRED_AT]->(pl)
OPTIONAL MATCH (e)-[se:SUPPORTED_BY]->(c)
OPTIONAL MATCH (p)-[sp:SUPPORTED_BY]->(c)
OPTIONAL MATCH (pl)-[spl:SUPPORTED_BY]->(c)
WITH c, r, ra, pl,
     count(DISTINCT se) AS event_supported_by_count,
     count(DISTINCT sp) AS period_supported_by_count,
     count(DISTINCT spl) AS place_supported_by_count
RETURN
  c.claim_id AS claim_id,
  c.label AS claim_label,
  c.status AS claim_status,
  c.promoted AS claim_promoted,
  c.promotion_date AS claim_promotion_date,
  type(r) AS canonical_rel_type,
  r.promoted_from_claim_id AS rel_promoted_from_claim_id,
  r.promotion_status AS rel_promotion_status,
  type(ra) AS canonical_place_rel_type,
  ra.promoted_from_claim_id AS place_rel_promoted_from_claim_id,
  ra.promotion_status AS place_rel_promotion_status,
  pl.entity_id AS place_entity_id,
  pl.qid AS place_qid,
  event_supported_by_count,
  period_supported_by_count,
  place_supported_by_count;
