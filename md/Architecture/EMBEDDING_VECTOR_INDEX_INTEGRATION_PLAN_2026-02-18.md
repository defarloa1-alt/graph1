# Embedding Vector Index Integration Plan (2026-02-18)

Status: `ARB-EMB-003` design baseline.

## Objective
Define a production-safe Neo4j vector-index plan for embedding retrieval so embedding outputs become operational for advisory ranking and disambiguation.

## Decisions (v1)
1. Index name
- `chr_embedding_v1_cosine_384_idx`

2. Vector dimensions
- `384`

3. Similarity metric
- `cosine`

4. Embedding property
- `embedding_v1`

5. Index cohort strategy
- Single shared retrieval label for scoped cohorts:
  - `:EmbeddingCandidate`
- Expected cohort labels (from `ARB-EMB-001`):
  - `Human`, `Event`, `Place`, `SubjectConcept`

Reason:
- One index and one dimension/metric profile reduce operational drift during baseline rollout.

## Data Model Additions (v1)
- Nodes eligible for vector retrieval should carry:
  - label: `EmbeddingCandidate`
  - property: `embedding_v1` (float array length 384)
  - metadata:
    - `embedding_model_family`
    - `embedding_model_version`
    - `embedding_run_fingerprint`
    - `embedding_updated_at`

## Planned Schema Artifacts
- Planned bootstrap file:
  - `Neo4j/schema/18_embedding_vector_index.cypher` (planned)
- Planned runner integration:
  - `scripts/tools/schema_migration_regression.py` plan update once cypher exists.

## Backfill Policy
1. Initial backfill (batch)
- Populate vectors for all in-scope cohorts present at rollout.

2. Incremental refresh (batch)
- Weekly batch refresh for changed/new nodes.
- No real-time write-through in v1.

3. Re-embed trigger policy
- Re-embed when:
  - canonical label changes,
  - major alias/property updates affecting semantic representation,
  - model version changes.

4. Null/invalid vectors
- Nodes with missing or malformed vectors are excluded from retrieval index until corrected.

## Query Pattern (Advisory)
- Top-k nearest-neighbor retrieval for:
  - candidate-link ranking,
  - disambiguation support,
  - related-entity suggestion.

Governance:
- Vector results remain advisory.
- No direct canonical mutation from vector similarity alone.
- Promotion remains gated by `U -> Pi -> Commit`.

## Quality and Validation Checks
1. Index health
- index exists with expected name/profile.
- index state is online before use.

2. Vector shape
- embedding length equals `384` for indexed rows.

3. Coverage
- report coverage ratio by cohort.

4. Drift control
- include model/version/fingerprint metadata in every embedding run artifact.

## Rollout Sequence
1. Create index cypher artifact (`18_embedding_vector_index.cypher`).
2. Execute in isolated environment and validate index health.
3. Backfill baseline vectors from embedding pipeline.
4. Enable advisory retrieval calls in selected workflows.
5. Expand only after quality gates pass.

## Acceptance Criteria Mapping (`ARB-EMB-003`)
- Index name defined: yes (`chr_embedding_v1_cosine_384_idx`).
- Dimensions defined: yes (`384`).
- Similarity metric defined: yes (`cosine`).
- Backfill policy defined: yes (initial + weekly incremental + re-embed triggers).
