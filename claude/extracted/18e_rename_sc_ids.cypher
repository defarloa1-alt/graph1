// ============================================================
// Script 18e — Strip domain prefix from ccs_bootstrap subject_ids
// ============================================================
// Architecture principle: domain membership = edge (HAS_SUBJECT_CONCEPT),
// NOT baked into the subject_id string. The SC is a topic node, not a
// domain-scoped node. "sc_rr_constitution" wrongly encodes domain inline.
//
// Rename: sc_rr_* → sc_*  (15 ccs_bootstrap SCs)
// geo_bootstrap IDs (GEO_*) are already domain-agnostic — no change needed.
// ============================================================

MATCH (sc:SubjectConcept) WHERE sc.subject_id STARTS WITH 'sc_rr_'
SET sc.subject_id = replace(sc.subject_id, 'sc_rr_', 'sc_')
RETURN sc.subject_id AS new_id, sc.label AS label
ORDER BY sc.subject_id;
