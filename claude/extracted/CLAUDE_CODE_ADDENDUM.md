# Claude Code Addendum: ADR Compliance Patch

## Context

After the initial 4 scripts (10-13) were generated, the user provided 6 formal
ADR documents plus a DMN decision table spec, confidence scoring rubric, and
entity classification decision tree. Script 14 patches the infrastructure to
align with these canonical specifications.

## Execute After Scripts 10-13

### `14_adr_compliance_patches.cypher`

**Run this AFTER scripts 10-13 are loaded.** It layers corrections on top.

**What it does (10 patches):**

| Patch | What | Why |
|-------|------|-----|
| 1 | Fix facet count rule → 18 | ADR-004 added BIOGRAPHIC |
| 2 | Fix exemplar cipher to content-only | ADR-001: no confidence/agent/timestamp in cipher |
| 3 | Add ScaffoldNode/ScaffoldEdge to meta-schema | ADR-006: scaffold/canonical boundary |
| 4 | Expand relationship kernel from 22 → 48+ types | ADR-002: v1.0 kernel across 7 categories |
| 5 | Add confidence scoring rubric (8 tiers + 7 modifiers) | From confidence_scoring_rubric.md |
| 6 | Add entity classification algorithm (3-tier + special cases) | From ENTITY_CLASSIFICATION_DECISION_TREE.md |
| 7 | Add ADR reference nodes (5 ADRs) | Agents can read architectural decisions |
| 8 | Add 4 onboarding steps (11-14) | Scaffold boundary, confidence, classification, ADRs |
| 9 | Add signing fields to federation sources | ADR-005 future-proofing |
| 10 | Add cipher and occupation validation rules | ADR-001, ADR-006 |

**Validate:**
```cypher
-- Relationship kernel expanded
MATCH (r:SYS_RelationshipType) WHERE r.kernel_version = 'v1.0'
RETURN r.kernel_category AS cat, count(*) AS cnt ORDER BY cnt DESC;
-- Expect 7 categories totaling 48+

-- ADR nodes exist
MATCH (a:SYS_ADR) RETURN count(a);  -- expect 5

-- Onboarding expanded
MATCH (p:SYS_OnboardingProtocol)-[:HAS_STEP]->(s)
RETURN count(s);  -- expect 14

-- Confidence tiers
MATCH (ct:SYS_ConfidenceTier) RETURN count(ct);  -- expect 8

-- Classification algorithm
MATCH (alg:SYS_ClassificationAlgorithm)-[:HAS_TIER]->(t)
RETURN count(t);  -- expect 4 (3 tiers + special cases)

-- Scaffold types exist
MATCH (et:EntityType {name: 'ScaffoldNode'}) RETURN et.description;
MATCH (et:EntityType {name: 'ScaffoldEdge'}) RETURN et.description;

-- Exemplar cipher is content-only (no CONF: in string)
MATCH (c:Claim {claim_id: 'clm_exemplar_001'})
WHERE c.cipher CONTAINS 'SHA256'
RETURN c.cipher;  -- should show SHA256(...) pattern, no confidence
```

## New Node Types Created by Patch 14

| Label | Count | Purpose |
|-------|-------|---------|
| SYS_ConfidenceTier | 8 | Source quality tiers for claim confidence |
| SYS_ConfidenceModifier | 7 | Confidence adjustments (+/- values) |
| SYS_ClassificationAlgorithm | 1 | Entity type classifier root |
| SYS_ClassificationTier | 4 | Classification algorithm tiers |
| SYS_ADR | 5 | Architectural decision records |
| EntityType (ScaffoldNode) | 1 | Scaffold node definition |
| EntityType (ScaffoldEdge) | 1 | Scaffold edge definition |
| SYS_ValidationRule | +2 | cipher_content_only, no_occupation_label |
| SYS_RelationshipType | +30 | Expanded kernel relationships |
| SYS_OnboardingStep | +4 | Steps 11-14 |

**Total additional nodes:** ~58
**Total additional edges:** ~30

## Still Pending (Phase 2 from original brief)

These items from the original CLAUDE_CODE_BRIEF.md are NOT addressed by
script 14 and still need Claude Code attention:

1. **Deduplicate Facet nodes** (36 → 18)
2. **Deduplicate Federation Source nodes** (26 → 13)
3. **Populate federation source operational metadata** (endpoints, rate limits)
4. **Wire FederationPositioningHopsSemantics policy**
5. **Add exemplar indexes** (is_exemplar)
6. **Build rejection taxonomy** (SYS_RejectionReason nodes)
## Execution Order Summary

```
1. 10_agent_meta_schema.cypher          (meta-schema layer)
2. 11_decision_table_bodies.cypher      (D4-D14 tables)
3. 12_claim_lifecycle_and_agents.cypher  (state machine + exemplar)
4. 13_onboarding_protocol.cypher        (10-step startup sequence)
5. 14_adr_compliance_patches.cypher     (ADR alignment + expansion)
6. 15_missing_decision_tables.cypher    (D1, D2, D3, D9, D11 + dependency chain)
```

### Script 15 Validation
```cypher
-- All 14 tables exist (D1-D14, note: no D0)
MATCH (dt:SYS_DecisionTable) RETURN count(dt);  -- expect ~14

-- Dependency chain wired
MATCH (a:SYS_DecisionTable)-[:FEEDS_INTO]->(b:SYS_DecisionTable)
RETURN a.table_id, b.table_id ORDER BY a.table_id;
-- expect: D1→D3, D2→D3, D3→D4, D4→D5, D5→D6, D6→D7, D8→D9, D9→D10, D10→D11
```
