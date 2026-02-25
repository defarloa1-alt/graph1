// DMN Extraction Audit — Add 21 SYS_Threshold and 5 SYS_Policy nodes
// Run after D-029 relabeling. Populate nodes first; do not modify scripts yet.
// Source: output/DMN_EXTRACTION_AUDIT.md

// ---------------------------------------------------------------------------
// 1. SYS_Threshold nodes (21 new — existing 3 already in graph)
// ---------------------------------------------------------------------------

// D6 — entity class validity
MERGE (t:SYS_Threshold {name: 'unresolved_class_threshold'})
SET t.value = 0.20, t.unit = 'ratio', t.decision_table = 'D6_DETERMINE_entity_class_validity',
    t.rationale = '>20% unresolvable classes = reject entity batch',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'unsupported_datatype_threshold'})
SET t.value = 0.10, t.unit = 'ratio', t.decision_table = 'D6_DETERMINE_entity_class_validity',
    t.rationale = '>10% unsupported datatypes = quality gate fail',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'min_temporal_precision'})
SET t.value = 9, t.unit = 'Wikidata precision integer', t.decision_table = 'D6_DETERMINE_entity_class_validity',
    t.rationale = 'Precision 9 = year; below = too coarse',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'literal_heavy_threshold'})
SET t.value = 0.80, t.unit = 'ratio', t.decision_table = 'D6_DETERMINE_entity_class_validity',
    t.rationale = '>80% literal-heavy = not frontier eligible',
    t.last_reviewed = '2026-02-25', t.system = true;

// D7 — harvest allowlist eligibility
MERGE (t:SYS_Threshold {name: 'max_hops_p279'})
SET t.value = 4, t.unit = 'integer', t.decision_table = 'D7_DETERMINE_harvest_allowlist_eligibility',
    t.rationale = 'P279 ancestor traversal depth',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'sparql_limit_discovery'})
SET t.value = 500, t.unit = 'integer', t.decision_table = 'D7_DETERMINE_harvest_allowlist_eligibility',
    t.rationale = 'Discovery mode budget',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'sparql_limit_production'})
SET t.value = 2000, t.unit = 'integer', t.decision_table = 'D7_DETERMINE_harvest_allowlist_eligibility',
    t.rationale = 'Production mode budget',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'max_sources_discovery'})
SET t.value = 200, t.unit = 'integer', t.decision_table = 'D7_DETERMINE_harvest_allowlist_eligibility',
    t.rationale = 'Discovery mode source budget',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'max_sources_production'})
SET t.value = 1000, t.unit = 'integer', t.decision_table = 'D7_DETERMINE_harvest_allowlist_eligibility',
    t.rationale = 'Production mode source budget',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'max_new_nodes_discovery'})
SET t.value = 100, t.unit = 'integer', t.decision_table = 'D7_DETERMINE_harvest_allowlist_eligibility',
    t.rationale = 'Discovery mode node budget',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'max_new_nodes_production'})
SET t.value = 1500, t.unit = 'integer', t.decision_table = 'D7_DETERMINE_harvest_allowlist_eligibility',
    t.rationale = 'Production mode node budget',
    t.last_reviewed = '2026-02-25', t.system = true;

// D5 — federation scope match
MERGE (t:SYS_Threshold {name: 'scoping_confidence_temporal_high'})
SET t.value = 0.95, t.unit = 'score', t.decision_table = 'D5_DETERMINE_federation_scope_match',
    t.rationale = 'DPRR + federation ID match',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'scoping_confidence_temporal_med'})
SET t.value = 0.85, t.unit = 'score', t.decision_table = 'D5_DETERMINE_federation_scope_match',
    t.rationale = 'DPRR only or single federation ID',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'scoping_confidence_domain'})
SET t.value = 0.85, t.unit = 'score', t.decision_table = 'D5_DETERMINE_federation_scope_match',
    t.rationale = 'Domain proximity without federation ID',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'scoping_confidence_unscoped'})
SET t.value = 0.40, t.unit = 'score', t.decision_table = 'D5_DETERMINE_federation_scope_match',
    t.rationale = 'No scoping signal',
    t.last_reviewed = '2026-02-25', t.system = true;

// D10 — claim promotion eligibility
MERGE (t:SYS_Threshold {name: 'claim_promotion_confidence'})
SET t.value = 0.90, t.unit = 'score', t.decision_table = 'D10_DETERMINE_claim_promotion_eligibility',
    t.rationale = 'Minimum confidence for auto-promotion',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'claim_promotion_posterior'})
SET t.value = 0.90, t.unit = 'probability', t.decision_table = 'D10_DETERMINE_claim_promotion_eligibility',
    t.rationale = 'Minimum posterior for auto-promotion',
    t.last_reviewed = '2026-02-25', t.system = true;

// D14 — entity resolution acceptance
MERGE (t:SYS_Threshold {name: 'entity_resolution_confidence'})
SET t.value = 0.75, t.unit = 'score', t.decision_table = 'D14_DETERMINE_entity_resolution_acceptance',
    t.rationale = 'Minimum for accepted entity match',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'entity_resolution_fuzzy'})
SET t.value = 0.80, t.unit = 'score', t.decision_table = 'D14_DETERMINE_entity_resolution_acceptance',
    t.rationale = 'Minimum for fuzzy name match',
    t.last_reviewed = '2026-02-25', t.system = true;

MERGE (t:SYS_Threshold {name: 'entity_resolution_similarity_min'})
SET t.value = 0.50, t.unit = 'score', t.decision_table = 'D14_DETERMINE_entity_resolution_acceptance',
    t.rationale = 'Minimum similarity to consider',
    t.last_reviewed = '2026-02-25', t.system = true;

// D8 — SFA facet assignment
MERGE (t:SYS_Threshold {name: 'sfa_proposal_confidence_default'})
SET t.value = 0.75, t.unit = 'score', t.decision_table = 'D8_DETERMINE_SFA_facet_assignment',
    t.rationale = 'Default SFA proposal confidence',
    t.last_reviewed = '2026-02-25', t.system = true;

// ---------------------------------------------------------------------------
// 2. SYS_Policy nodes (5 new — existing 5 already in graph)
// ---------------------------------------------------------------------------

MERGE (p:SYS_Policy {name: 'HarvestModeBudgets'})
SET p.description = 'Discovery mode uses conservative budgets; production mode uses full budgets',
    p.decision_table = 'D7_DETERMINE_harvest_allowlist_eligibility',
    p.active = true, p.system = true;

MERGE (p:SYS_Policy {name: 'TemporalPrecisionFloor'})
SET p.description = 'Temporal values below precision 9 (year) are not harvested',
    p.decision_table = 'D6_DETERMINE_entity_class_validity',
    p.active = true, p.system = true;

MERGE (p:SYS_Policy {name: 'LiteralHeavyExclusion'})
SET p.description = 'Entities where >80% of statements are literal-heavy are not frontier eligible',
    p.decision_table = 'D6_DETERMINE_entity_class_validity',
    p.active = true, p.system = true;

MERGE (p:SYS_Policy {name: 'EntityResolutionFallback'})
SET p.description = 'When best match is below threshold, create provisional node rather than reject',
    p.decision_table = 'D14_DETERMINE_entity_resolution_acceptance',
    p.active = true, p.system = true;

MERGE (p:SYS_Policy {name: 'SFAProposalAsClaim'})
SET p.description = 'All SFA proposals are claims with provenance, not ground truth',
    p.decision_table = 'D8_DETERMINE_SFA_facet_assignment',
    p.active = true, p.system = true;
