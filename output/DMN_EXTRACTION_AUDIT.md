# Chrystallum — DMN Extraction Audit
**Date:** 2026-02-25  
**Audited scripts:** sca_agent.py, subject_concept_facet_agents.py, cluster_assignment.py,
wikidata_backlink_harvest.py, claim_ingestion_pipeline.py  
**Method:** Grep for hardcoded numeric values, thresholds, lists, and classification logic  
**Principle (D-024):** Any value subject to change by a business owner or domain expert
belongs in a DMN decision table, not in code. Owner = who should change it, not who wrote it.

---

## Summary: Values Found by Script

### wikidata_backlink_harvest.py

| Value | Line | Current value | Owner | Decision table |
|-------|------|---------------|-------|----------------|
| unresolved_class_threshold | ~917 | 0.20 | Architect | D6 DETERMINE entity class validity |
| unsupported_datatype_threshold | ~923 | 0.10 | Architect | D6 DETERMINE entity class validity |
| min_temporal_precision | ~929 | 9 | Domain expert | D6 DETERMINE entity class validity |
| literal_heavy_threshold | ~935 | 0.80 | Architect | D6 DETERMINE entity class validity |
| max_hops (P279 ancestor traversal) | ~941 | 4 | Architect | D7 DETERMINE harvest allowlist eligibility |
| sparql_limit (discovery mode) | ~78 | 500 | Architect | D7 DETERMINE harvest allowlist eligibility |
| sparql_limit (production mode) | ~83 | 2000 | Architect | D7 DETERMINE harvest allowlist eligibility |
| max_sources_per_seed (discovery) | ~79 | 200 | Architect | D7 DETERMINE harvest allowlist eligibility |
| max_sources_per_seed (production) | ~84 | 1000 | Architect | D7 DETERMINE harvest allowlist eligibility |
| max_new_nodes_per_seed (discovery) | ~80 | 100 | Architect | D7 DETERMINE harvest allowlist eligibility |
| max_new_nodes_per_seed (production) | ~85 | 1500 | Architect | D7 DETERMINE harvest allowlist eligibility |
| temporal_scoped confidence (high) | ~592 | 0.95 | Architect | D5 DETERMINE federation scope match |
| temporal_scoped confidence (med) | ~594 | 0.85 | Architect | D5 DETERMINE federation scope match |
| domain_scoped confidence | ~596-599 | 0.85 | Architect | D5 DETERMINE federation scope match |
| unscoped confidence | ~600 | 0.40 | Architect | D5 DETERMINE federation scope match |
| DEFAULT_PROPERTY_ALLOWLIST | ~41 | [P710, P1441, P138, P112, P737, P828] | Architect | D7 DETERMINE harvest allowlist eligibility |
| DEFAULT_P31_DENYLIST | ~49 | frozenset (multiple QIDs) | Architect | D1 DETERMINE assertion class validity |
| batch_size (entity API) | ~946 | 40 | Dev | operational — not a decision |
| sleep_ms | ~945 | 100 | Dev | operational — not a decision |
| timeout_s | ~944 | 45 | Dev | operational — not a decision |

### cluster_assignment.py

| Value | Location | Current value | Owner | Decision table |
|-------|----------|---------------|-------|----------------|
| scoping_confidence (DPRR temporal) | load_dprr_from_neo4j | 0.85 | Architect | D5 DETERMINE federation scope match |
| scoping_status (DPRR) | load_dprr_from_neo4j | "temporal_scoped" | Architect | D5 DETERMINE federation scope match |
| DPRR_ANCHOR_QID | module level | "Q899409" | Domain expert | D5 DETERMINE federation scope match |
| batch_size (Neo4j write) | write_to_neo4j default | 500 | Dev | operational — not a decision |
| confidence default (no facet data) | build_edges | 1.0 | Architect | D8 DETERMINE SFA facet assignment |

### claim_ingestion_pipeline.py

| Value | Line | Current value | Owner | Decision table |
|-------|------|---------------|-------|----------------|
| confidence_threshold (entity resolution) | ~52 | 0.75 | Architect | new — D14 DETERMINE entity resolution acceptance |
| fuzzy_threshold (name match) | ~285 | 0.80 | Architect | D14 DETERMINE entity resolution acceptance |
| exact_match confidence | ~299 | 1.0 | Architect | D14 DETERMINE entity resolution acceptance |
| near_exact confidence | ~309 | 0.92 | Architect | D14 DETERMINE entity resolution acceptance |
| abbreviation confidence | ~348 | 0.95 | Architect | D14 DETERMINE entity resolution acceptance |
| semantic confidence hardcoded | ~408 | 0.92 | Architect | D14 DETERMINE entity resolution acceptance |
| similarity_min_threshold | ~448 | 0.50 | Architect | D14 DETERMINE entity resolution acceptance |
| wikidata_search limit | ~98, ~134 | 10 | Architect | D14 DETERMINE entity resolution acceptance |
| promotion confidence gate | ~633 | 0.90 | Domain expert | D10 DETERMINE claim promotion eligibility |
| promotion posterior_probability gate | ~634 | 0.90 | Domain expert | D10 DETERMINE claim promotion eligibility |

### subject_concept_facet_agents.py

| Value | Line | Current value | Owner | Decision table |
|-------|------|---------------|-------|----------------|
| FORBIDDEN_FACETS list | ~41 | [TEMPORAL, CLASSIFICATION, PATRONAGE, GENEALOGICAL] | Architect | D8 DETERMINE SFA facet assignment |
| CANONICAL_FACETS list | ~30 | 18 facets | Architect | D8 DETERMINE SFA facet assignment |
| proposal confidence default | ~261, ~289 | 0.8 | Domain expert | D8 DETERMINE SFA facet assignment |

### sca_agent.py

| Value | Location | Current value | Owner | Decision table |
|-------|----------|---------------|-------|----------------|
| bootstrap facet count assertion | _validate_bootstrap | 18 | Architect | D8 DETERMINE SFA facet assignment |
| forbidden facet list (hardcoded again) | _validate_bootstrap | [TEMPORAL, CLASSIFICATION, PATRONAGE, GENEALOGICAL] | Architect | D8 DETERMINE SFA facet assignment |
| perplexity model | query_perplexity | "llama-3.1-sonar-large-128k-online" | Dev | operational — not a decision |

---

## Cross-Script Duplications (Rule Fragmentation)

These values appear in more than one script — meaning a change requires finding and updating multiple files:

| Value | Scripts | Risk |
|-------|---------|------|
| **FORBIDDEN_FACETS** | subject_concept_facet_agents.py, sca_agent.py | **HIGH — two places, one truth. Both should read from graph (SYS_Policy NoTemporalFacet, NoClassificationFacet etc.)** |
| Scoping confidence 0.85 | wikidata_backlink_harvest.py, cluster_assignment.py | HIGH — same value, different contexts |
| Scoping confidence thresholds (0.95, 0.85, 0.40) | wikidata_backlink_harvest.py | MED — single file but multiple branches |
| confidence = 0.75 | claim_ingestion_pipeline.py, SCA/SFA contract | MED — contract says 0.75, code says 0.75 separately |

---

## Existing SYS_Threshold Nodes (already in graph, not yet read by code)

From dev's investigation — these already exist and should be the canonical source:

| Node name | Current value | Maps to |
|-----------|---------------|---------|
| crosslink_ratio_split | 0.3 | D12 DETERMINE SubjectConcept split trigger |
| level2_child_overload | 12 | D12 DETERMINE SubjectConcept split trigger |
| facet_drift_alert | 0.2 | D13 DETERMINE SFA drift alert |

These three are correctly externalised but not yet read. The code equivalents (if any) should be removed once the decision tables read from SYS_Threshold.

---

## Existing SYS_Policy Nodes (already in graph, not yet read by code)

| Node name | Maps to |
|-----------|---------|
| NoTemporalFacet | D8 DETERMINE SFA facet assignment — row 1 |
| NoClassificationFacet | D8 DETERMINE SFA facet assignment — row 2 |
| LocalFirstCanonicalAuthorities | D4 DETERMINE federation route — priority ordering |
| HubForDisambiguationOnly | D5 DETERMINE federation scope match — Wikidata exclusion |
| ApprovalRequired | D10 DETERMINE claim promotion eligibility — gate condition |

---

## Revised Full DMN Table Inventory

| ID | DETERMINE | Primary inputs | Key values to externalise | Status |
|----|-----------|---------------|--------------------------|--------|
| D1 | assertion class validity | assertion.class | DEFAULT_P31_DENYLIST (approved class set) | Drafted |
| D2 | value type category | assertion.value_type | — (exhaustive enumeration, stable) | Drafted |
| D3 | frontier eligibility | D1+D2+federation_coverage | — | Drafted |
| D4 | federation route | D1+D2+D3+pid_in_registry | LocalFirstCanonicalAuthorities policy | Drafted |
| D5 | federation scope match | entity external IDs | 0.95, 0.85, 0.85, 0.40 confidence values; DPRR_ANCHOR_QID | Drafted — values need externalising |
| D6 | entity class validity | unresolved_ratio, datatype_ratio, temporal_precision, literal_heavy_ratio | 0.20, 0.10, 9, 0.80 thresholds | New |
| D7 | harvest allowlist eligibility | PID, discovers_new_entities | allowlist PIDs, denylist QIDs, mode budgets | New |
| D8 | SFA facet assignment | SubjectConcept anchor, facet_match | FORBIDDEN_FACETS, CANONICAL_FACETS, 0.8 default confidence | Partially drafted |
| D9 | SFA constitution layer | D8 output (facet) | constitution doc set per facet | New |
| D10 | claim promotion eligibility | confidence, posterior_probability, review_count, ApprovalRequired | 0.90, 0.90 thresholds; ApprovalRequired policy | New |
| D11 | claim dispute trigger | D10 output | — | New |
| D12 | SubjectConcept split trigger | crosslink_ratio, level2_child_count | 0.3, 12 (in SYS_Threshold already) | New |
| D13 | SFA drift alert | proposal_divergence_score | 0.2 (in SYS_Threshold already) | New |
| D14 | entity resolution acceptance | match_type, similarity_score, confidence | 0.75, 0.80, 1.0, 0.92, 0.95, 0.50 thresholds | New — claim_ingestion_pipeline |

---

## Priority Order for Table Build

**Tier 1 — highest fragmentation risk, most values in code:**
1. D6 DETERMINE entity class validity — 4 threshold values, all in harvester code
2. D10 DETERMINE claim promotion eligibility — governance gate, currently hardcoded 0.90/0.90
3. D5 DETERMINE federation scope match — confidence values duplicated across two scripts
4. D8 DETERMINE SFA facet assignment — FORBIDDEN_FACETS duplicated in two scripts

**Tier 2 — important but lower immediate risk:**
5. D7 DETERMINE harvest allowlist eligibility — allowlist and denylist in code
6. D14 DETERMINE entity resolution acceptance — multiple thresholds in claim_ingestion_pipeline
7. D12 DETERMINE SubjectConcept split trigger — SYS_Threshold nodes already exist
8. D13 DETERMINE SFA drift alert — SYS_Threshold node already exists

**Tier 3 — complete the set:**
9. D1 DETERMINE assertion class validity — DEFAULT_P31_DENYLIST needs externalising
10. D4 DETERMINE federation route — LocalFirstCanonicalAuthorities policy
11. D9 DETERMINE SFA constitution layer — per-facet constitution doc mapping
12. D11 DETERMINE claim dispute trigger — depends on D10

---

## Operational Values — Exclude from DMN

These are infrastructure/operational values that developers own and should stay in code or config:

- batch_size (Neo4j write): 500 — performance tuning, not a business decision
- sleep_ms: 100 — rate limiting, not a business decision
- timeout_s: 45 — infrastructure, not a business decision
- Perplexity model name — API configuration, not a business decision

---

## Notes for SYS_Threshold Node Model

Values to add as SYS_Threshold nodes (not yet in graph):

| Proposed name | Value | Unit | Decision table | Rationale |
|--------------|-------|------|----------------|-----------|
| unresolved_class_threshold | 0.20 | ratio | D6 | >20% unresolvable classes = reject entity batch |
| unsupported_datatype_threshold | 0.10 | ratio | D6 | >10% unsupported datatypes = quality gate fail |
| min_temporal_precision | 9 | Wikidata precision integer | D6 | Precision 9 = year; below = too coarse |
| literal_heavy_threshold | 0.80 | ratio | D6 | >80% literal-heavy = not frontier eligible |
| max_hops_p279 | 4 | integer | D7 | P279 ancestor traversal depth |
| sparql_limit_discovery | 500 | integer | D7 | Discovery mode budget |
| sparql_limit_production | 2000 | integer | D7 | Production mode budget |
| max_sources_discovery | 200 | integer | D7 | Discovery mode source budget |
| max_sources_production | 1000 | integer | D7 | Production mode source budget |
| max_new_nodes_discovery | 100 | integer | D7 | Discovery mode node budget |
| max_new_nodes_production | 1500 | integer | D7 | Production mode node budget |
| scoping_confidence_temporal_high | 0.95 | score | D5 | DPRR + federation ID match |
| scoping_confidence_temporal_med | 0.85 | score | D5 | DPRR only or single federation ID |
| scoping_confidence_domain | 0.85 | score | D5 | Domain proximity without federation ID |
| scoping_confidence_unscoped | 0.40 | score | D5 | No scoping signal |
| claim_promotion_confidence | 0.90 | score | D10 | Minimum confidence for auto-promotion |
| claim_promotion_posterior | 0.90 | probability | D10 | Minimum posterior for auto-promotion |
| entity_resolution_confidence | 0.75 | score | D14 | Minimum for accepted entity match |
| entity_resolution_fuzzy | 0.80 | score | D14 | Minimum for fuzzy name match |
| entity_resolution_similarity_min | 0.50 | score | D14 | Minimum similarity to consider |
| sfa_proposal_confidence_default | 0.75 | score | D8 | Default SFA proposal confidence |

---

## Notes for SYS_Policy Node Model

Policies to add (not yet in graph, complement existing 5):

| Proposed name | Statement | Decision table |
|--------------|-----------|----------------|
| HarvestModeBudgets | Discovery mode uses conservative budgets; production mode uses full budgets | D7 |
| TemporalPrecisionFloor | Temporal values below precision 9 (year) are not harvested | D6 |
| LiteralHeavyExclusion | Entities where >80% of statements are literal-heavy are not frontier eligible | D6 |
| EntityResolutionFallback | When best match is below threshold, create provisional node rather than reject | D14 |
| SFAProposalAsClaim | All SFA proposals are claims with provenance, not ground truth | D8 |
