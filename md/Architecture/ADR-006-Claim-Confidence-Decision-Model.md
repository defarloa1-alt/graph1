# ADR-006: Claim Confidence Decision Model (Ordered Single-Hit Tables)

Status: proposed
Date: 2026-02-18
Canonical architecture anchor: `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`

## Context
Claim confidence behavior is currently spread across:
1. fixed threshold promotion checks,
2. heuristic scoring in scripts,
3. review/debate handling described in architecture prose.

This makes claims lifecycle behavior harder to:
1. test deterministically,
2. explain in audit trails,
3. evolve without hidden regressions.

## Decision
Adopt a deterministic claim confidence decision kernel using ordered, single-hit decision tables:
1. `SourceStrength`,
2. `ConflictCode`,
3. `ClaimConfidenceProfile`.

Execution model:
1. evaluate rows top-down,
2. first matching row wins,
3. include an explicit default row at the bottom.

Operational placement:
1. `U` computes raw inputs and proposes claim payload,
2. `Pi` executes decision tables and emits gate outputs,
3. `Commit` persists only approved writes with recorded decision trace.

## Inputs and Outputs
Inputs:
1. `primary_count`, `secondary_count`, `tertiary_count`,
2. `has_conflicts`,
3. `epistemic_type`,
4. `federation_depth`.

Outputs:
1. `source_strength`,
2. `conflict_code`,
3. `min_confidence`,
4. `max_confidence`,
5. `require_debate_bridge`,
6. `require_expert_review`.

## Decision Tables (Normative)
Use the ordered rules exactly as specified in the approved decision model package:
1. Table A: `SourceStrength`,
2. Table B: `ConflictCode`,
3. Table C: `ClaimConfidenceProfile`.

The approved table package must be versioned (for example `claim_confidence_policy_v1`) and treated as policy configuration, not inline code logic.

## Mapping Rules for Current Schema
To avoid schema breakage in rollout:
1. map existing claim types (`factual`, `temporal`, etc.) into the decision model `epistemic_type` via explicit mapping table,
2. map current authority tier evidence into `federation_depth` via explicit mapping table,
3. persist both raw and normalized values in proposal/policy artifacts for auditability.

## Policy Subgraph Projection
To align policy transparency with graph-native architecture:
1. keep JSON policy artifact canonical and hash-pinned,
2. project policy into Neo4j policy subgraph as read-only decision metadata,
3. bind runtime decisions to `policy_hash` + matched row ids.

Reference implementation assets:
1. `scripts/tools/policy_subgraph_loader.py`
2. `Neo4j/schema/17_policy_decision_subgraph_schema.cypher`

Initial federation-depth mapping policy (v1):
1. depth `1`: single-layer support (broker-level only),
2. depth `2`: broker + one corroborating external layer,
3. depth `3`: multi-layer corroboration including domain authority evidence.

## Boundaries
1. This model governs confidence and routing outcomes; it does not redefine claim identity/cipher semantics.
2. This model does not bypass `U -> Pi -> Commit`.
3. Debate and expert review flags are gate outputs; they are not direct mutation permissions.

## Invariants
1. No canonical mutation occurs from this model alone.
2. Every policy decision stores policy version, matched row ids, and reason metadata.
3. Every rejection or hold path is persisted with machine-readable reason codes.
4. Default row behavior must be explicit and test-covered.

## Consequences
Positive:
1. deterministic confidence behavior,
2. consistent review/debate routing,
3. easier audit and regression testing.

Tradeoffs:
1. adds policy-config maintenance,
2. requires claim-type and tier-to-depth mapping governance,
3. requires migration of hardcoded threshold paths.

## Rollout Plan
1. Phase 1: add policy artifact + mapping tables + pure evaluation function (no mutation changes).
2. Phase 2: route one claims proposal path through `Pi` decision tables and log matched rows.
3. Phase 3: replace fixed promotion thresholds with decision-model outputs where approved.
4. Phase 4: add QA pack for row-order correctness, default-row safety, and explainability traces.

## Extension Candidates
After claim confidence rollout stabilizes, apply the same ordered single-hit policy style to:
1. federation authority edge typing (`SAME_AS`/`ALIGNED_WITH`/`CONFLICTS_WITH`),
2. agent routing decisions,
3. subagent spawning from categorized backlink density,
4. period/presentism validation,
5. entity-to-SubjectConcept promotion decisions.

## Related Documents
1. `md/Architecture/ADR-002-Policy-Gate-and-Update-Operator-Separation.md`
2. `md/Architecture/ADR-003-KBpedia-Role-and-Boundaries.md`
3. `md/Architecture/KBPEDIA_MAPPING_CONFIDENCE_RUBRIC.md`
4. `Neo4j/schema/07_core_pipeline_schema.cypher`
5. `Neo4j/schema/14_claim_promotion_seed.cypher`
6. `Neo4j/schema/run_qid_pipeline.py`
