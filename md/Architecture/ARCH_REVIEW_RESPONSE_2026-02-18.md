# Architecture Review Response (2026-02-18)

Status: response to external architecture assessment (rating: 8.5/10 narrative with weighted subtotal 6.84 + domain adjustment).

## Scope
- Convert review findings into explicit decision posture:
  - `ACCEPT`
  - `PARTIAL_ACCEPT`
  - `CHALLENGE`
  - `DEFER`
- Map accepted gaps to implementation tracks.

## Scoring Note
- The assessment includes:
  - weighted subtotal: `6.84/10`
  - adjusted final: `8.5/10`
- We accept the qualitative conclusion (strong architecture with strategic gaps), while treating the adjustment model as non-canonical unless formalized.

## Decision Matrix

| Area                              | Review Claim                                       | Posture          | Rationale                                                                                       | Action Track                                                |
| --------------------------------- | -------------------------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Multi-standard ontology alignment | Best-in-class interoperability                     | `ACCEPT`         | Current architecture is explicitly multi-authority and policy-gated.                            | Maintain and extend through federation adapter rollout.     |
| Reification and provenance        | Advanced claim/provenance model                    | `ACCEPT`         | Claim policy + proposal/gate workflow align with model intent.                                  | Continue policy-table migration and traceability hardening. |
| Temporal modeling                 | Research-grade temporal handling                   | `ACCEPT`         | Temporal hierarchy + Period integration are core strengths.                                     | Preserve as primary differentiation.                        |
| Schema governance                 | Strong, but migration testing gap                  | `PARTIAL_ACCEPT` | Constraint/index governance exists; migration test harness is still thin.                       | Add migration regression suite.                             |
| Artifact registry governance      | Innovative strength                                | `ACCEPT`         | Registry now deterministic with overrides and closed review queue.                              | Keep as living control-plane metadata.                      |
| Graph pattern modeling / GQL      | Good patterns, limited ISO GQL alignment           | `PARTIAL_ACCEPT` | Useful long-term, low immediate ROI vs operational priorities.                                  | Track as standards watch, not near-term blocker.            |
| Federation strategy               | Solid but lacks bidirectional SPARQL federation    | `PARTIAL_ACCEPT` | Current implementation is stronger on harvest than full federation query services.              | Add staged federation query service track.                  |
| Entity resolution                 | Strong deterministic alignment, limited ML linking | `PARTIAL_ACCEPT` | Deterministic ID alignment is strong; fuzzy/semantic linking remains optional enhancement.      | Add embedding-assisted linking as controlled layer.         |
| KG embeddings                     | Major missing capability                           | `ACCEPT`         | High-ROI gap for similarity and link candidate ranking.                                         | Phase 1 ML infra (vector index + embedding pipeline).       |
| Reasoning/inference               | Lacks formal entailment stack                      | `PARTIAL_ACCEPT` | Deterministic policy reasoning exists; formal semantic reasoning is limited.                    | Add SHACL/RDFS-lite validation/inference track.             |
| GNN integration                   | Missing vs SOTA                                    | `DEFER`          | Valuable for research publication; lower immediate production ROI than embeddings + validation. | Phase 3 research track after baseline ML + reasoning.       |
| LOD compliance                    | Partial implementation                             | `PARTIAL_ACCEPT` | Some URI practices exist; publication-grade LOD surface is incomplete.                          | Add RDF export + VoID + URI policy baseline.                |

## Prioritized Execution Plan

## Phase 1 (0-8 weeks): High-ROI Baseline
Priority note: LOD baseline is treated as a high-priority deliverable in Phase 1.

1. Embedding infrastructure:
- Add vector-ready artifact path and evaluation harness for entity similarity and candidate linking.
2. Reasoning validation baseline:
- Introduce SHACL-style validation checks and constrained inference where deterministic value is clear.
3. LOD baseline:
- Produce RDF export pipeline + VoID descriptor + URI policy document.

## Phase 2 (8-16 weeks): Federation and Semantics Expansion
1. Add bidirectional federation query capabilities for priority authorities.
2. Expand entity-resolution stack with embedding-assisted disambiguation.
3. Add migration regression testing for schema/version evolution.

## Phase 3 (16+ weeks): Research-Grade Enhancements
1. GNN experimentation track for link prediction and plausibility ranking.
2. Formalize publication-oriented benchmarks and reproducible evaluation packs.

## Immediate Backlog Inserts
1. Embedding/vector index track (design + pilot script + evaluation criteria).
2. SHACL/RDFS-lite validation track (scope-limited, deterministic first).
3. LOD publication track (RDF/VoID/URI resolution policy).
4. Schema migration regression track.

## Non-Goals (Current Window)
- Full OWL reasoning stack across all graph surfaces.
- Full GNN production integration before baseline embedding and validation maturity.

## Governance Constraint
- All new tracks must preserve `U -> Pi -> Commit` and no direct bypass mutation paths.

## Progress Note (2026-02-18)
- Embedding baseline scope drafted:
  - `md/Architecture/EMBEDDING_BASELINE_SCOPE_2026-02-18.md`
- Embedding pilot scaffold added:
  - `scripts/ml/train_kg_embeddings.py`
- LOD baseline artifacts drafted:
  - `md/Architecture/LOD_BASELINE_SPEC_2026-02-18.md`
  - `md/Architecture/VOID_DATASET_DRAFT_2026-02-18.ttl`
- SHACL/RDFS-lite scope drafted:
  - `md/Architecture/SHACL_RDFS_LITE_SCOPE_2026-02-18.md`
- SHACL/RDFS-lite validator scaffold added:
  - `scripts/tools/validate_semantic_constraints.py`
- Schema migration regression harness design drafted:
  - `md/Architecture/SCHEMA_MIGRATION_REGRESSION_HARNESS_DESIGN_2026-02-18.md`
- Schema migration regression runner added:
  - `scripts/tools/schema_migration_regression.py`
  - `Neo4j/schema/schema_migration_plan_v1.json`
- Embedding vector index integration plan drafted:
  - `md/Architecture/EMBEDDING_VECTOR_INDEX_INTEGRATION_PLAN_2026-02-18.md`
- Bidirectional federation query design drafted:
  - `md/Architecture/BIDIRECTIONAL_FEDERATION_QUERY_DESIGN_2026-02-18.md`
- Embedding-assisted disambiguation policy drafted:
  - `md/Architecture/EMBEDDING_ASSISTED_DISAMBIGUATION_POLICY_2026-02-18.md`
- GNN experiment protocol drafted:
  - `md/Architecture/GNN_EXPERIMENT_PROTOCOL_2026-02-18.md`
- GNN experiment runner scaffold added:
  - `scripts/ml/link_prediction_gnn.py`
