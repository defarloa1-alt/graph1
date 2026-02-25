# Chrystallum — DMN Decision Tables D6–D14

**Date:** 2026-02-25  
**Source:** output/DMN_EXTRACTION_AUDIT.md  
**Principle (D-024):** Values subject to change by business owner or domain expert belong in decision tables, not in code. Thresholds and policies are stored in SYS_Threshold and SYS_Policy nodes; tables reference them by name.

---

## Table index

| ID | DETERMINE | Primary consumer | SYS_Threshold / SYS_Policy |
|----|-----------|------------------|----------------------------|
| D6 | entity class validity | wikidata_backlink_harvest.py | unresolved_class_threshold, unsupported_datatype_threshold, min_temporal_precision, literal_heavy_threshold; TemporalPrecisionFloor, LiteralHeavyExclusion |
| D7 | harvest allowlist eligibility | wikidata_backlink_harvest.py | max_hops_p279, sparql_limit_*, max_sources_*, max_new_nodes_*; HarvestModeBudgets |
| D8 | SFA facet assignment | subject_concept_facet_agents.py, sca_agent.py | sfa_proposal_confidence_default; NoTemporalFacet, NoClassificationFacet, SFAProposalAsClaim |
| D9 | SFA constitution layer | SFA constitution loader | — (constitution doc set per facet) |
| D10 | claim promotion eligibility | claim_ingestion_pipeline.py | claim_promotion_confidence, claim_promotion_posterior; ApprovalRequired |
| D11 | claim dispute trigger | claim pipeline | — (depends on D10 output) |
| D12 | SubjectConcept split trigger | SubjectConcept split logic | crosslink_ratio_split, level2_child_overload |
| D13 | SFA drift alert | SFA drift detector | facet_drift_alert |
| D14 | entity resolution acceptance | claim_ingestion_pipeline.py | entity_resolution_confidence, entity_resolution_fuzzy, entity_resolution_similarity_min; EntityResolutionFallback |

---

## D6 DETERMINE entity class validity

**Purpose:** Decide whether an entity batch passes quality gates before harvest. Reject if too many unresolvable classes, unsupported datatypes, or literal-heavy statements; reject temporal values below year precision.

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| unresolved_ratio | Real [0,1] | Ratio of P31 classes that failed to resolve |
| unsupported_datatype_ratio | Real [0,1] | Ratio of statements with unsupported Wikidata datatypes |
| min_temporal_precision_observed | Integer | Worst precision among temporal claims (9 = year) |
| literal_heavy_ratio | Real [0,1] | Ratio of statements that are literal-heavy |

**Output:** `entity_class_valid: Boolean`, `frontier_eligible: Boolean`

**Hit policy:** FIRST (first matching row wins)

**SYS_Threshold:** unresolved_class_threshold (0.20), unsupported_datatype_threshold (0.10), min_temporal_precision (9), literal_heavy_threshold (0.80)  
**SYS_Policy:** TemporalPrecisionFloor, LiteralHeavyExclusion

| # | unresolved_ratio | unsupported_datatype_ratio | min_temporal_precision_observed | literal_heavy_ratio | entity_class_valid | frontier_eligible |
|---|------------------|----------------------------|---------------------------------|---------------------|-------------------|-------------------|
| 1 | > unresolved_class_threshold | — | — | — | FALSE | FALSE |
| 2 | — | > unsupported_datatype_threshold | — | — | FALSE | FALSE |
| 3 | — | — | < min_temporal_precision | — | FALSE | FALSE |
| 4 | — | — | — | > literal_heavy_threshold | TRUE | FALSE |
| 5 | ≤ | ≤ | ≥ | ≤ | TRUE | TRUE |

---

## D7 DETERMINE harvest allowlist eligibility

**Purpose:** Decide whether a property (PID) is eligible for harvest, and which budget limits apply (discovery vs production mode).

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| pid | String | Wikidata property ID (e.g. P31, P710) |
| discovers_new_entities | Boolean | Whether harvest mode discovers new entities (true = discovery, false = production) |
| pid_in_allowlist | Boolean | PID in SYS_PropertyMapping / DEFAULT_PROPERTY_ALLOWLIST |
| pid_in_denylist | Boolean | PID in denylist (if any) |
| p279_hops_to_anchor | Integer | P279 ancestor traversal depth to domain anchor |

**Output:** `eligible: Boolean`, `sparql_limit: Integer`, `max_sources: Integer`, `max_new_nodes: Integer`

**Hit policy:** FIRST

**SYS_Threshold:** max_hops_p279 (4), sparql_limit_discovery (500), sparql_limit_production (2000), max_sources_discovery (200), max_sources_production (1000), max_new_nodes_discovery (100), max_new_nodes_production (1500)  
**SYS_Policy:** HarvestModeBudgets

| # | pid_in_allowlist | pid_in_denylist | p279_hops_to_anchor | discovers_new_entities | eligible | sparql_limit | max_sources | max_new_nodes |
|---|------------------|----------------|---------------------|------------------------|---------|--------------|-------------|--------------|
| 1 | FALSE | — | — | — | FALSE | — | — | — |
| 2 | — | TRUE | — | — | FALSE | — | — | — |
| 3 | TRUE | FALSE | > max_hops_p279 | — | FALSE | — | — | — |
| 4 | TRUE | FALSE | ≤ | TRUE | TRUE | sparql_limit_discovery | max_sources_discovery | max_new_nodes_discovery |
| 5 | TRUE | FALSE | ≤ | FALSE | TRUE | sparql_limit_production | max_sources_production | max_new_nodes_production |

---

## D8 DETERMINE SFA facet assignment

**Purpose:** Decide whether a proposed facet is eligible for SFA assignment. TEMPORAL, CLASSIFICATION, PATRONAGE, GENEALOGICAL are forbidden (read from SYS_Policy). All proposals are claims (SFAProposalAsClaim).

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| proposed_facet | String | Facet key (e.g. TEMPORAL, ARTISTIC, RELIGIOUS) |
| facet_in_forbidden_list | Boolean | Matches SYS_Policy NoTemporalFacet, NoClassificationFacet, or equivalent |
| facet_in_canonical_list | Boolean | In CANONICAL_FACETS (18 facets) |
| has_facet_data | Boolean | SubjectConcept has prior facet assignments |

**Output:** `eligible: Boolean`, `confidence: Real`

**Hit policy:** FIRST

**SYS_Threshold:** sfa_proposal_confidence_default (0.75)  
**SYS_Policy:** NoTemporalFacet, NoClassificationFacet, SFAProposalAsClaim

| # | proposed_facet | facet_in_forbidden_list | facet_in_canonical_list | eligible | confidence |
|---|----------------|------------------------|-------------------------|----------|------------|
| 1 | — | TRUE | — | FALSE | — |
| 2 | — | FALSE | FALSE | FALSE | — |
| 3 | — | FALSE | TRUE | TRUE | sfa_proposal_confidence_default |
| 4 | — | FALSE | TRUE | TRUE | 1.0 (if has_facet_data and no proposal) |

*Note: FORBIDDEN_FACETS should be read from graph (SYS_Policy NoTemporalFacet, NoClassificationFacet, etc.), not hardcoded in sca_agent.py or subject_concept_facet_agents.py.*

---

## D9 DETERMINE SFA constitution layer

**Purpose:** Map a facet to its constitution document set. Defines which documents govern interpretation for each facet.

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| facet | String | Canonical facet key (output of D8) |

**Output:** `constitution_doc_ids: List[String]`

**Hit policy:** UNIQUE (one row per facet)

**SYS_Threshold / SYS_Policy:** None. Constitution mapping is stored per-facet (TBD: SYS_FacetConstitution or similar).

| # | facet | constitution_doc_ids |
|---|-------|----------------------|
| 1 | ARTISTIC | [doc_id_1, doc_id_2] |
| 2 | RELIGIOUS | [doc_id_3] |
| … | … | … |

*Note: Full mapping TBD. Per-facet constitution doc set to be externalised.*

---

## D10 DETERMINE claim promotion eligibility

**Purpose:** Decide whether a claim can be auto-promoted to asserted, or requires human approval.

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| confidence | Real [0,1] | Claim confidence score |
| posterior_probability | Real [0,1] | Bayesian posterior (if computed) |
| review_count | Integer | Number of human reviews |
| ApprovalRequired | Boolean | SYS_Policy active (gate condition) |

**Output:** `promote: Boolean`, `reason: String`

**Hit policy:** FIRST

**SYS_Threshold:** claim_promotion_confidence (0.90), claim_promotion_posterior (0.90)  
**SYS_Policy:** ApprovalRequired

| # | ApprovalRequired | confidence | posterior_probability | review_count | promote | reason |
|---|-----------------|------------|----------------------|--------------|---------|--------|
| 1 | TRUE | — | — | — | FALSE | ApprovalRequired gate |
| 2 | FALSE | < claim_promotion_confidence | — | — | FALSE | Below confidence |
| 3 | FALSE | — | < claim_promotion_posterior | — | FALSE | Below posterior |
| 4 | FALSE | ≥ | ≥ | ≥ 0 | TRUE | Auto-promote |

---

## D11 DETERMINE claim dispute trigger

**Purpose:** Decide when a promoted claim should be flagged for dispute (e.g. conflicting evidence, low agreement).

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| D10_output | String | promote / reason from D10 |
| conflicting_evidence_count | Integer | Number of conflicting assertions |
| agreement_score | Real [0,1] | Agreement among sources |

**Output:** `dispute_triggered: Boolean`

**Hit policy:** FIRST

**SYS_Threshold / SYS_Policy:** TBD (depends on D10 output and future governance rules).

| # | D10_output | conflicting_evidence_count | agreement_score | dispute_triggered |
|---|------------|---------------------------|----------------|------------------|
| 1 | promote=FALSE | — | — | FALSE |
| 2 | promote=TRUE | > 0 | — | TRUE |
| 3 | promote=TRUE | 0 | < TBD | TRUE |
| 4 | promote=TRUE | 0 | ≥ TBD | FALSE |

---

## D12 DETERMINE SubjectConcept split trigger

**Purpose:** Decide when a SubjectConcept should be flagged for splitting (too many crosslinks or overloaded L2 children).

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| crosslink_ratio | Real [0,1] | Ratio of cross-facet links |
| level2_child_count | Integer | Number of direct children at L2 |

**Output:** `split_triggered: Boolean`, `reason: String`

**Hit policy:** FIRST

**SYS_Threshold:** crosslink_ratio_split (0.3), level2_child_overload (12)

| # | crosslink_ratio | level2_child_count | split_triggered | reason |
|---|-----------------|--------------------|-----------------|--------|
| 1 | > crosslink_ratio_split | — | TRUE | Crosslink overload |
| 2 | — | > level2_child_overload | TRUE | L2 child overload |
| 3 | ≤ | ≤ | FALSE | — |

---

## D13 DETERMINE SFA drift alert

**Purpose:** Decide when SFA proposal set has diverged too far from SCA baseline — flag before promotion.

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| proposal_divergence_score | Real [0,1] | Fraction of concepts with LCSH mismatched to facet |

**Output:** `alert: Boolean`

**Hit policy:** UNIQUE

**SYS_Threshold:** facet_drift_alert (0.2)

| # | proposal_divergence_score | alert |
|---|---------------------------|-------|
| 1 | ≥ facet_drift_alert | TRUE |
| 2 | < facet_drift_alert | FALSE |

---

## D14 DETERMINE entity resolution acceptance

**Purpose:** Decide whether an entity resolution match is accepted, rejected, or provisional. Match type determines which threshold applies.

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| match_type | String | exact_match, near_exact, abbreviation, semantic, fuzzy |
| similarity_score | Real [0,1] | Similarity score (for fuzzy) |
| confidence | Real [0,1] | Match confidence |

**Output:** `accepted: Boolean`, `provisional: Boolean`

**Hit policy:** FIRST

**SYS_Threshold:** entity_resolution_confidence (0.75), entity_resolution_fuzzy (0.80), entity_resolution_similarity_min (0.50)  
**SYS_Policy:** EntityResolutionFallback

*Note: claim_ingestion_pipeline has additional match-type-specific thresholds (exact 1.0, near_exact 0.92, abbreviation 0.95, semantic 0.92). These can be added as SYS_Threshold nodes or folded into match_type rules.*

| # | match_type | similarity_score | confidence | accepted | provisional |
|---|------------|-----------------|------------|----------|-------------|
| 1 | exact_match | — | ≥ 1.0 | TRUE | FALSE |
| 2 | near_exact | — | ≥ 0.92 | TRUE | FALSE |
| 3 | abbreviation | — | ≥ 0.95 | TRUE | FALSE |
| 4 | semantic | — | ≥ 0.92 | TRUE | FALSE |
| 5 | fuzzy | ≥ entity_resolution_similarity_min | ≥ entity_resolution_fuzzy | TRUE | FALSE |
| 6 | fuzzy | ≥ entity_resolution_similarity_min | < entity_resolution_fuzzy | FALSE | TRUE (EntityResolutionFallback) |
| 7 | * | < entity_resolution_similarity_min | — | FALSE | TRUE (EntityResolutionFallback) |
| 8 | * | — | < entity_resolution_confidence | FALSE | TRUE (EntityResolutionFallback) |

---

## Implementation notes

1. **Read from graph:** Scripts should query SYS_Threshold and SYS_Policy by name; do not hardcode values.
2. **FORBIDDEN_FACETS:** Both sca_agent.py and subject_concept_facet_agents.py should read NoTemporalFacet, NoClassificationFacet (and equivalents for PATRONAGE, GENEALOGICAL) from graph.
3. **D14 match-type thresholds:** Consider adding entity_resolution_near_exact (0.92), entity_resolution_abbreviation (0.95), entity_resolution_semantic (0.92) to SYS_Threshold for full externalisation.
4. **D9 constitution mapping:** Per-facet constitution doc set to be designed; may use SYS_FacetConstitution or similar node type.
