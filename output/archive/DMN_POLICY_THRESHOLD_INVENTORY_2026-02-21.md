# DMN Policy & Threshold Inventory — Extraction Audit

**Date:** 2026-02-21  
**Purpose:** Map existing Policy and Threshold nodes to DMN decision tables. Identify what's missing. Design SYS_Policy / SYS_Threshold node model for DMN table reads.  
**Context:** Graph already contains the embryo of rule externalisation. D-029 reclassifies these into Metanode. This inventory supports the DMN governance layer.  
**Status:** Architecture confirmed. D12 and D13 added to inventory.

---

## 1. Current Policy Nodes (5) — Architecture Confirmed

| name | description | priority | decision_table |
|------|-------------|----------|----------------|
| LocalFirstCanonicalAuthorities | Always check local authorities before hub API | 1 | D4_DETERMINE_federation_route |
| HubForDisambiguationOnly | Use Wikidata for discovery/disambiguation, not as primary source | 2 | D5_DETERMINE_federation_scope_match |
| NoTemporalFacet | TEMPORAL is NOT a facet — use Year backbone, Period, Event | 3 | D8_DETERMINE_SFA_facet_assignment |
| NoClassificationFacet | CLASSIFICATION via LCC properties, not facet | 4 | D8_DETERMINE_SFA_facet_assignment |
| ApprovalRequired | All discoveries require human approval before promotion | 5 | D10_DETERMINE_claim_promotion_eligibility |

---

## 2. Current Threshold Nodes (3) — Architecture Confirmed

| name | description | value | decision_table |
|------|-------------|-------|----------------|
| crosslink_ratio_split | Split SFA when cross-link ratio exceeds 30% | 0.3 | D12_DETERMINE_SubjectConcept_split_trigger |
| level2_child_overload | Split when L2 node has >12 children | 12 | D12_DETERMINE_SubjectConcept_split_trigger |
| facet_drift_alert | Alert when 20%+ concepts have LCSH mismatched to facet | 0.2 | D13_DETERMINE_SFA_drift_alert |

---

## 3. Mapping to Decision Tables (Architecture Confirmed)

| DMN decision | Policy/Threshold source | Notes |
|--------------|-------------------------|-------|
| D4 DETERMINE federation route | LocalFirstCanonicalAuthorities | Condition column ordering — local authority precedence |
| D5 DETERMINE federation scope match | HubForDisambiguationOnly | Wikidata absence as scoping source is explicit |
| D8 DETERMINE SFA facet assignment | NoTemporalFacet, NoClassificationFacet | Top rows, eligible: FALSE |
| D10 DETERMINE claim promotion eligibility | ApprovalRequired | Mandatory condition column |
| **D12 DETERMINE SubjectConcept split trigger** | crosslink_ratio_split, level2_child_overload | **New table** — inputs: crosslink_ratio, level2_child_count |
| **D13 DETERMINE SFA drift alert** | facet_drift_alert | **New table** — input: proposal_divergence_score |

---

## 4. SYS_Policy / SYS_Threshold Node Model (Architecture Confirmed)

### SYS_Policy
- `name: String` (unique)
- `description: String`
- `decision_table: String` — which DETERMINE table enforces this
- `active: Boolean` — can be toggled without code change (e.g. ApprovalRequired = false → auto-promote)
- `system: true`

### SYS_Threshold
- `name: String` (unique)
- `value: Real`
- `unit: String` — what the value measures
- `decision_table: String` — which DETERMINE table reads this
- `rationale: String` — why this value was chosen
- `last_reviewed: String` — date; thresholds should be reviewed periodically
- `system: true`

---

## 5. What's Missing (gaps to add later)

| Decision | Missing policy/threshold | Suggested name |
|----------|--------------------------|----------------|
| ScopingService | — | TBD |
| HarvestAllowlistService | — | PropertyMapping covers this |
| ClaimPromotionService | Confidence floor | promotion_confidence_floor |
| EdgeBuilder | Unmapped PID ceiling | unmapped_pid_ceiling (0.19) |
| Harvester | Unresolved class threshold | unresolved_class_threshold (0.20) |
| Harvester | Unsupported datatype threshold | unsupported_datatype_threshold (0.10) |
