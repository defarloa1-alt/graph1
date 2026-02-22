# Embedding Baseline Scope (2026-02-18)

Status: `ARB-EMB-001` scope definition.

## Objective
Define the first embedding scope for Chrystallum to support similarity, candidate-link ranking, and disambiguation assistance without bypassing policy gates.

## Baseline Node Cohorts
- `Human`
- `Event`
- `Place`
- `SubjectConcept`

Rationale:
- These cohorts are central to current claim/federation workflows and provide immediate value for similarity and candidate ranking.

## Embedding Inputs (v1)
- Canonical label and aliases (where available)
- Core type/facet signals
- Selected graph-neighborhood features:
  - degree and typed-edge counts
  - authority-link presence (Wikidata/LCSH/FAST/Pleiades/etc.)
  - temporal anchors for `Event` and `Period` links

## Output Artifacts (v1)
- Node embedding vectors keyed by canonical node IDs
- Run metadata:
  - model family/version
  - dimensionality
  - training timestamp
  - source cohort counts
  - quality metrics summary

## Refresh Cadence
- Initial cadence: weekly batch refresh.
- Incremental updates deferred until baseline quality and cost are stable.

## Primary Use Cases
1. Candidate relationship ranking (advisory, not auto-write)
2. Entity disambiguation assistance
3. Similarity retrieval for analyst workflows

## Governance Constraints
- Embedding outputs are advisory signals.
- No direct canonical mutation from embedding inference.
- All promotion paths remain `U -> Pi -> Commit`.

## Success Metrics (Baseline)
- Coverage:
  - percentage of scoped nodes with valid vectors
- Retrieval quality:
  - top-k similarity sanity checks on curated test set
- Operational:
  - deterministic run metadata and reproducible outputs

## Out of Scope (v1)
- GNN training/inference in production
- Fully automated link creation from embedding similarity
- Real-time embedding updates

## Dependencies
- Stable canonical IDs for scoped cohorts
- Registry/routing metadata for embedding artifacts
- Agreement on vector dimensionality and distance metric in follow-on task (`ARB-EMB-003`)

## Completion Criteria for ARB-EMB-001
- Cohorts are explicitly defined.
- Input signals and output contract are explicit.
- Refresh cadence and success metrics are documented.
- Governance boundaries are explicit and consistent with policy gates.
