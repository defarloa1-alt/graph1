# Chrystallum — DMN Decision Tables D1–D14

**Date:** 2026-02-25  
**Source:** output/DMN_EXTRACTION_AUDIT.md  
**Principle (D-024):** Values subject to change by business owner or domain expert belong in decision tables, not in code. Thresholds and policies are stored in SYS_Threshold and SYS_Policy nodes; tables reference them by name.

---

## Table index

| ID | DETERMINE | Primary consumer | SYS_Threshold / SYS_Policy |
|----|-----------|------------------|----------------------------|
| D1 | assertion class validity | Harvester, EdgeBuilder | DEFAULT_P31_DENYLIST (approved class set) |
| D2 | value type category | Harvester | — (exhaustive enumeration, stable) |
| D3 | frontier eligibility | FederationDispatcher | D1+D2+federation_coverage |
| D4 | federation route | ExternalFederationGateway | LocalFirstCanonicalAuthorities |
| D5 | federation scope match | wikidata_backlink_harvest.py, cluster_assignment.py | scoping_confidence_*; DPRR_ANCHOR_QID; HubForDisambiguationOnly |
| D6 | entity class validity | wikidata_backlink_harvest.py | unresolved_class_threshold, unsupported_datatype_threshold, min_temporal_precision, literal_heavy_threshold; TemporalPrecisionFloor, LiteralHeavyExclusion |
| D7 | harvest allowlist eligibility | wikidata_backlink_harvest.py | max_hops_p279, sparql_limit_*, max_sources_*, max_new_nodes_*; HarvestModeBudgets |
| D8 | SFA facet assignment | subject_concept_facet_agents.py, sca_agent.py | sfa_proposal_confidence_default; NoTemporalFacet, NoClassificationFacet, SFAProposalAsClaim |
| D9 | SFA constitution layer | SFA constitution loader | — (constitution doc set per facet) |
| D10 | claim promotion eligibility | claim_ingestion_pipeline.py | claim_promotion_confidence, claim_promotion_posterior; ApprovalRequired |
| D11 | claim dispute trigger | claim pipeline | — (depends on D10 output) |
| D12 | SubjectConcept split trigger | SubjectConcept split logic | crosslink_ratio_split, level2_child_overload |
| D13 | SFA drift alert | SFA drift detector | facet_drift_alert |
| D14 | entity resolution acceptance | claim_ingestion_pipeline.py | entity_resolution_confidence, entity_resolution_fuzzy, entity_resolution_similarity_min; EntityResolutionFallback |
| D15 | person label application | adr007_apply_person_label.py | — (gate logic: dprr_id, P31 targets, entity_id prefix) |
| D16 | conflict type classification | person_harvest_agent.py (Layer 2) | — (taxonomy: Types 1–4 per ADR-007 §7.1) |
| D17 | conflict resolution (Type 4) | person_harvest_agent.py (Layer 2) | claim_promotion_confidence_ancient_person; source_authority_tier per ADR-007 §8 |

---

## D1 DETERMINE assertion class validity

**Purpose:** Decide whether an assertion's class (P31) is in the approved set. Denylist excludes non-domain classes.

**Inputs:** assertion.class (QID)

**Output:** `valid: Boolean`

**SYS_Threshold / SYS_Policy:** DEFAULT_P31_DENYLIST (frozenset of QIDs) — to be externalised to SYS_PropertyMapping or SYS_Policy.

**Status:** Drafted — values in wikidata_backlink_harvest.py DEFAULT_P31_DENYLIST.

---

## D2 DETERMINE value type category

**Purpose:** Categorise assertion value type (entity, quantity, time, string, etc.) for downstream routing.

**Inputs:** assertion.value_type (Wikidata datatype)

**Output:** `category: String` (exhaustive enumeration)

**Status:** Drafted — stable enumeration, no externalisation needed.

---

## D3 DETERMINE frontier eligibility

**Purpose:** Decide whether an entity is eligible for frontier harvest (D1+D2 pass, federation coverage).

**Inputs:** D1 output, D2 output, federation_coverage

**Output:** `frontier_eligible: Boolean`

**Status:** Drafted — depends on D1, D2.

---

## D4 DETERMINE federation route

**Purpose:** Decide which federation source to query first. Local canonical authorities take priority.

**Inputs:** D1+D2+D3 output, pid_in_registry

**SYS_Policy:** LocalFirstCanonicalAuthorities (priority ordering)

**Output:** `route: String` (federation source order)

**Status:** Drafted — policy to be externalised.

---

## D5 DETERMINE federation scope match

**Purpose:** Compute scoping confidence from entity external IDs (DPRR, Pleiades, etc.). DPRR temporal-scoped gets 0.85; high match 0.95; unscoped 0.40.

**Inputs:** entity external IDs, DPRR_ANCHOR_QID match

**SYS_Threshold:** scoping_confidence_temporal_high (0.95), scoping_confidence_temporal_med (0.85), scoping_confidence_domain (0.85), scoping_confidence_unscoped (0.40)  
**SYS_Policy:** HubForDisambiguationOnly (Wikidata exclusion cases)

**Output:** `scoping_status: String`, `confidence: Real`

**Status:** Drafted — values externalised in D-032 (harvester, cluster_assignment).

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

**Purpose:** Decide whether a claim can be auto-promoted to asserted, or requires human approval. Supports domain-scoped threshold override for ancient persons (ADR-007 §7.4).

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| confidence | Real [0,1] | Claim confidence score |
| posterior_probability | Real [0,1] | Bayesian posterior (if computed) |
| review_count | Integer | Number of human reviews |
| ApprovalRequired | Boolean | SYS_Policy active (gate condition) |
| domain_scope | String \| null | `ancient_person` if Person has IN_PERIOD → Periodo_Period with end_date before year 0; null otherwise |

**Output:** `promote: Boolean`, `reason: String`

**Hit policy:** FIRST

**SYS_Threshold:** claim_promotion_confidence (0.90), claim_promotion_posterior (0.90), claim_promotion_confidence_ancient_person (0.75)
**SYS_Policy:** ApprovalRequired

| # | ApprovalRequired | domain_scope | confidence | posterior_probability | review_count | promote | reason |
|---|-----------------|--------------|------------|----------------------|--------------|---------|--------|
| 1 | TRUE | — | — | — | — | FALSE | ApprovalRequired gate |
| 2 | FALSE | `ancient_person` | < claim_promotion_confidence_ancient_person | — | — | FALSE | Below ancient person confidence (0.75) |
| 3 | FALSE | null | < claim_promotion_confidence | — | — | FALSE | Below confidence (0.90) |
| 4 | FALSE | — | — | < claim_promotion_posterior | — | FALSE | Below posterior |
| 5 | FALSE | — | ≥ (scoped) | ≥ | ≥ 0 | TRUE | Auto-promote |

**ADR-007 §7.4 rationale:** The global 0.90 threshold was calibrated for modern, well-documented entities. It is too high for ancient persons where even primary sources rarely support 0.90 confidence on birth years and office dates. The domain-scoped override (0.75) calibrates the threshold to what the historical evidence can actually support.

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

## D15 DETERMINE person label application

**Purpose:** Decide whether a node receives the `:Person` label per ADR-007 §2. Three gates (any sufficient) plus a veto condition. Applied during Phase 1 of person schema implementation.

**ADR:** ADR-007 §2

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| dprr_id | String \| null | Node property |
| p31_targets | String[] | Labels of P31 target nodes |
| entity_id_prefix | String | First 7 chars of entity_id |
| entity_type | String | Node property |
| has_non_human_p31 | Boolean | EXISTS { (n)-[:P31]->(m) WHERE m.label <> 'human' AND n.dprr_id IS NULL } |

**Output:** `apply_person_label: Boolean`, `apply_mythological: Boolean`, `dq_flag: String | null`

**Hit policy:** FIRST

| # | dprr_id | p31_targets | entity_id_prefix | entity_type | has_non_human_p31 | apply_person_label | apply_mythological | dq_flag |
|---|---------|-------------|------------------|-------------|-------------------|--------------------|--------------------|---------|
| 1 | — | — | — | — | TRUE | FALSE | FALSE | DQ_WRONG_ENTITY_TYPE |
| 2 | NOT NULL | — | — | — | FALSE | TRUE | FALSE | — |
| 3 | NULL | includes 'human' | 'person_' | — | FALSE | TRUE | FALSE | — |
| 4 | NULL | includes 'human' | NOT 'person_' | 'CONCEPT' | FALSE | TRUE | FALSE | — |
| 5 | NULL | empty | — | — | FALSE | FALSE | TRUE | DQ_UNRESOLVED_PERSONHOOD |
| 6 | — | — | — | — | — | FALSE | FALSE | DQ_MISSING_P31 |

**Notes:**
- Row 1 is the veto — fires regardless of other gates if P31 resolves to non-human and no DPRR authority
- Row 2 is Gate A (DPRR authority — 4,772 nodes)
- Row 3 is Gate B (Wikidata-confirmed human in person_ namespace — 377 nodes)
- Row 4 is Gate C (namespace leak repair — concept_ entities with P31→human)
- Row 5 catches Romulus/Remus/Europa (no P31, no DPRR, but valid mythological)
- Row 6 is the fallback for biblical persons pending P31 re-fetch

---

## D16 DETERMINE conflict type classification

**Purpose:** Classify disagreements between federation sources into one of four types, each with a distinct resolution action. Only Type 4 requires human escalation. Applied by PersonReasoningAgent (Layer 2) during person harvest.

**ADR:** ADR-007 §7.1

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| source_a_value | Any | Value from Source A for the attribute |
| source_b_value | Any \| null | Value from Source B (null = silence) |
| source_a_precision | Integer | Date precision or value specificity of A |
| source_b_precision | Integer \| null | Date precision or value specificity of B |
| source_b_covers_attribute | Boolean | Whether Source B's domain includes this attribute |
| values_overlap | Boolean | Whether A and B ranges/values intersect |

**Output:** `conflict_type: Integer (1–4)`, `agent_action: String`

**Hit policy:** FIRST

| # | source_b_value | source_b_covers_attribute | source_b_precision vs source_a_precision | values_overlap | conflict_type | agent_action |
|---|---------------|---------------------------|------------------------------------------|----------------|---------------|-------------|
| 1 | null | FALSE | — | — | 2 (Silence) | Write A; silence is not contradiction |
| 2 | null | TRUE | — | — | 2 (Silence) | Write A; flag genuine absence |
| 3 | NOT null | — | B > A | — | 1 (Precision gap) | Accept B; both as provenance |
| 4 | NOT null | — | A > B | — | 1 (Precision gap) | Accept A; both as provenance |
| 5 | NOT null | TRUE | — | TRUE | 3 (Soft conflict) | Compute intersection; write as range |
| 6 | NOT null | TRUE | — | FALSE | 4 (Hard conflict) | Resolution ladder (D17) |

---

## D17 DETERMINE conflict resolution (Type 4 hard conflicts)

**Purpose:** 4-step escalation ladder for Type 4 hard conflicts where non-overlapping values come from sources that both cover the attribute. Applied by PersonReasoningAgent (Layer 2), with Step 4 deferred to human review.

**ADR:** ADR-007 §7.2

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| source_a_tier | String | primary / secondary_academic / secondary_populist / tertiary |
| source_b_tier | String | Same enum |
| tiebreaker_source_value | Any \| null | Value from a third federation source (if available) |
| tiebreaker_agrees_with | String \| null | 'A' or 'B' or null |

**Output:** `resolution: String`, `candidate_claim: String`, `challenger_claim: String`, `escalate_to_human: Boolean`

**Hit policy:** FIRST

| # | source_a_tier vs source_b_tier | tiebreaker_source_value | tiebreaker_agrees_with | resolution | escalate_to_human |
|---|-------------------------------|------------------------|------------------------|------------|-------------------|
| 1 | A outranks B | — | — | A is candidate; B writes CHALLENGES_CLAIM | FALSE |
| 2 | B outranks A | — | — | B is candidate; A writes CHALLENGES_CLAIM | FALSE |
| 3 | Same tier | NOT null | 'A' | A is candidate (2-against-1 majority) | FALSE |
| 4 | Same tier | NOT null | 'B' | B is candidate (2-against-1 majority) | FALSE |
| 5 | Same tier | null | — | Both Proposed / Under Review; write ConflictNote | TRUE |
| 6 | Same tier | NOT null | null (disagrees with both) | Both Proposed / Under Review; write ConflictNote | TRUE |

**Authority tier ranking (ADR-007 §8):**
- `primary` (DPRR for persons, Trismegistos for attested, Nomisma for numismatic) > `secondary_academic` (VIAF, FAST/LC, Trismegistos, LGPN) > `secondary_populist` (Wikidata) > `tertiary`
- Tier is attribute-level, not source-global — DPRR outranks Wikidata on offices but Wikidata may be more current on cross-IDs

**ConflictNote structure (written at Step 5/6):**
- `conflict_type: 'hard'`
- `attributes_in_dispute: String[]`
- `sources_involved: String[]`
- `tiebreaker_needed: Boolean`
- `resolution_status: 'PENDING'`
- `ocd_applicable: Boolean` (OCD reserved slot may resolve later)

---

## Implementation notes

1. **Read from graph:** Scripts should query SYS_Threshold and SYS_Policy by name; do not hardcode values.
2. **FORBIDDEN_FACETS:** Both sca_agent.py and subject_concept_facet_agents.py should read NoTemporalFacet, NoClassificationFacet (and equivalents for PATRONAGE, GENEALOGICAL) from graph.
3. **D14 match-type thresholds:** Consider adding entity_resolution_near_exact (0.92), entity_resolution_abbreviation (0.95), entity_resolution_semantic (0.92) to SYS_Threshold for full externalisation.
4. **D9 constitution mapping:** Per-facet constitution doc set to be designed; may use SYS_FacetConstitution or similar node type.
5. **D10 domain_scope:** PersonHarvestExecutor must check IN_PERIOD → Periodo_Period end_date to determine domain_scope before evaluating D10. The ancient_person threshold (0.75) must be registered as SYS_Threshold `claim_promotion_confidence_ancient_person`.
6. **D15 person label gate:** Applied as a batch operation during Phase 1; idempotent — re-running does not duplicate labels.
7. **D16/D17 conflict resolution:** Applied by PersonReasoningAgent during Layer 2 reasoning. Outputs are recorded in the PersonHarvestPlan, not executed directly. Execution happens in Layer 3 (PersonHarvestExecutor Step 11).
