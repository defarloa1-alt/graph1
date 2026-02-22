# Embedding-Assisted Disambiguation Policy (2026-02-18)

Status: `ARB-ER-001` policy baseline.

## Objective
Define how embedding similarity is used in entity resolution without allowing ML signals to bypass deterministic governance.

## Policy Principle
Embeddings are advisory evidence.
- They can rank candidates.
- They cannot alone authorize canonical promotion.

## Inputs (v1)
- `embedding_similarity` (`0.0..1.0`)
- `authority_id_exact_match` (`true|false`)
- `label_match` (`exact|close|none`)
- `temporal_compatibility` (`compatible|uncertain|conflict`)
- `conflict_flags_present` (`true|false`)

## Output Decisions
- `resolution_band` (`high|medium|low|reject`)
- `action` (`promotable_candidate|review_required|advisory_only|reject`)
- `reason_codes[]`

## Ordered Decision Policy (single-hit style)

| Row | embedding_similarity | authority_id_exact_match | temporal_compatibility | conflict_flags_present | action | resolution_band |
|---|---|---|---|---|---|---|
| ER1 | `>=0.92` | `true` | `compatible` | `false` | `promotable_candidate` | `high` |
| ER2 | `>=0.85` | `true` | `uncertain` | `false` | `review_required` | `medium` |
| ER3 | `>=0.88` | `false` | `compatible` | `false` | `review_required` | `medium` |
| ER4 | `>=0.75` | `false` | `uncertain` | `false` | `advisory_only` | `low` |
| ER5 | `any` | `any` | `conflict` | `any` | `reject` | `reject` |
| ER6 | `any` | `any` | `any` | `true` | `reject` | `reject` |
| ER7 | `any` | `any` | `any` | `any` | `advisory_only` | `low` |

Notes:
- Rows are evaluated top-down.
- First match wins.
- Rows `ER5` and `ER6` are hard safety guards.

## Promotion Boundary
`promotable_candidate` means:
- eligible to enter existing promotion workflow,
- not auto-promoted directly by embedding output.

Required for promotion path:
1. deterministic identity checks pass,
2. no unresolved conflict flags,
3. policy gate records decision trace.

## Required Output Artifact Fields
For each disambiguation decision, emit:
- `candidate_id`
- `target_id`
- `embedding_similarity`
- `resolution_band`
- `action`
- `matched_rule_id`
- `reason_codes`
- `analysis_run_id`
- `policy_version`

## Review Queue Policy
- `review_required` rows go to analyst queue with top-k alternatives.
- `advisory_only` rows remain non-mutating hints.
- `reject` rows are retained only for audit and error analysis.

## Quality Metrics (v1)
- precision@k on curated disambiguation set
- false-positive rate for `promotable_candidate`
- reviewer override rate for `review_required`
- unresolved conflict rate

## Governance
- Preserve `U -> Pi -> Commit`.
- Keep embedding-assisted decisions explainable via `matched_rule_id`.
- Store reason codes for every non-passive action.

## Acceptance Criteria Mapping (`ARB-ER-001`)
- Advisory vs promotable boundary explicitly defined: yes.
- Ordered decision behavior defined: yes.
- Governance-safe promotion boundary defined: yes.
