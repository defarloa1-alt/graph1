# KBpedia Mapping Confidence Rubric and Reviewer Gates

Status: draft
Date: 2026-02-18
Scope: KKO/KBpedia mapping proposals before canonical promotion.
Canonical architecture anchor: `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`

## Purpose
Define a deterministic review policy for:
1. `match_type`: `exact|narrow|broad|related`
2. `mapping_confidence`: `0.0..1.0`
3. reviewer gate outcomes in the `U -> Pi -> Commit` flow.

## Match Type Semantics
1. `exact`: source class and target class are materially equivalent for intended use.
2. `narrow`: source is more specific than target; some source semantics are lost.
3. `broad`: source is less specific than target; target adds constraints not guaranteed by source.
4. `related`: non-hierarchical conceptual relation; typing signal is weak.

## Confidence Bands
1. `0.90-1.00`: high confidence
2. `0.75-0.89`: medium confidence
3. `0.60-0.74`: low confidence
4. `<0.60`: insufficient confidence

## Minimum Evidence Requirements
1. all mappings require at least one stable source URI.
2. `exact` and `narrow` require at least two independent evidence links or one formal equivalence assertion plus one usage example.
3. `broad` and `related` require at least one evidence link plus rationale note.
4. plain text labels alone are never sufficient evidence.

## Gate Policy (Pi)
Promotion eligibility by tuple `(match_type, confidence)`:
1. `exact` + `>=0.90`: eligible for fast-track review; still requires Pi approval.
2. `exact` + `0.75-0.89`: standard review.
3. `narrow` + `>=0.75`: standard review with explicit semantic-loss note.
4. `broad` + `>=0.75`: review required; promotion allowed only if target constraint checks pass.
5. `related` (any confidence): proposal-only by default; no direct canonical typing promotion.
6. any mapping `<0.60`: reject or keep as research note only.

## Required Reviewer Outputs
Each Pi decision must write:
1. `decision`: `approve|reject|needs_revision`
2. `reason_code`: machine-readable code
3. `review_notes`
4. `reviewer_id`
5. `reviewed_at`

## Reason Code Taxonomy
1. `EVIDENCE_INSUFFICIENT`
2. `MATCH_TYPE_UNJUSTIFIED`
3. `CONFIDENCE_BELOW_THRESHOLD`
4. `TARGET_SCHEMA_MISMATCH`
5. `SEMANTIC_LOSS_UNACCEPTABLE`
6. `REQUIRES_SITUATION_ADR`
7. `APPROVED_WITH_CONSTRAINTS`

## Interaction with Situation Decision
Until `Situation` is canonicalized:
1. mappings requiring `Situation` target are `proposal-only`.
2. reviewer should use `REQUIRES_SITUATION_ADR` when promotion is blocked by schema state.

## Crosswalk Field Conformance
Crosswalk rows in `CSV/kko_chrystallum_crosswalk.csv` must include:
1. `match_type`
2. `mapping_confidence`
3. `review_status`
4. `notes` (for rationale and constraints)

## Acceptance Criteria
1. every promoted KKO mapping has `match_type`, `mapping_confidence`, and evidence.
2. every rejected mapping has a reason code.
3. no `related` mapping is promoted directly to canonical typing.
4. mappings blocked by schema decisions remain in proposal/scaffold state.

## Related Documents
1. `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
1. `md/Architecture/ADR-003-KBpedia-Role-and-Boundaries.md`
2. `md/Architecture/kbpedia.md`
3. `CSV/kko_chrystallum_crosswalk.csv`
