# ADR-002: Policy Gate and Update Operator Separation

Status: proposed
Date: 2026-02-18

## Context
The architecture contains governance checks, debate/review behavior, and graph update logic spread across multiple documents and phases. This makes it harder to:
1) reason about safety guarantees,
2) test update behavior independently from governance policy,
3) maintain deterministic failure modes.

Legacy conceptual artifacts reinforced a useful split:
1) proposal/update generation,
2) policy/gate enforcement,
3) commit or reject behavior.

## Decision
Adopt an explicit conceptual separation:
1) `U` (update operator): generates candidate graph deltas and evidence.
2) `Pi` (policy gate): validates candidate deltas against governance rules.
3) `Commit`: applies approved deltas; rejected deltas are persisted as decisions with reasons.

In practical flow:
1) Candidate generation produces `ProposedEdge`/proposal artifacts.
2) Policy gate checks constraints, provenance, coverage, and run-scope rules.
3) Commit writes canonical graph changes only for approved candidates.
4) Rejections are logged and queryable; no silent drops.

## Boundaries
`U` responsibilities:
1) discovery and ranking,
2) proposal packaging,
3) evidence attachment.

`Pi` responsibilities:
1) schema and policy conformance checks,
2) threshold and gate evaluation,
3) approval/rejection decision recording.

`Commit` responsibilities:
1) idempotent canonical writes,
2) provenance linkage to proposal and analysis run,
3) audit event emission.

## Consequences
Positive:
1) clearer safety model and testability,
2) deterministic and auditable rejection behavior,
3) easier migration of policy rules without rewriting proposal logic.

Tradeoffs:
1) more explicit interfaces and event records,
2) additional implementation effort for gate orchestration,
3) short-term duplication during transition.

## Invariants
1) No canonical mutation without passing `Pi`.
2) Every commit references a proposal artifact and run context.
3) Every rejection is persisted with machine-readable reason codes.
4) Gate failures never mutate canonical graph.

## Implementation Notes
1) Align with existing promotion governance in `md/Architecture/2-17-26-CHRYSTALLUM_v0_AGENT_BOOTSTRAP_SPEC.md`.
2) Reuse existing proposal and run entities where possible.
3) Add explicit reason-code taxonomy for rejection events.

## Rollout Plan
1) Phase 1: formalize interfaces and reason codes.
2) Phase 2: route one pipeline through `U -> Pi -> Commit`.
3) Phase 3: enforce policy gate as mandatory for all mutation paths.

## Decision Outcome
If accepted, this ADR becomes the conceptual boundary used by:
1) federation adapters,
2) scenario generation QA gates,
3) presentation orchestration proposals that request mutations.

