# Reference Backlog (Consolidated)

## Purpose
- Preserve useful ideas from non-canonical `md/reference` analysis docs in one actionable backlog.
- Reduce folder sprawl while keeping a clear re-entry point for future design work.

## Current Status
- Relationship registry is now canonical in `Relationships/relationship_types_registry_master.csv`.
- Facet registry is canonical in `Facets/facet_registry_master.json` and `Facets/facet_registry_master.csv`.
- Architecture primary source is `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md` for implementation crosswalks.

## Consolidated Ideas To Revisit

### 1) Relationship Discovery Proposals
- Discovery/extraction proposals are largely already present in `Relationships/relationship_types_registry_master.csv` (verified for sampled candidates including typological, evolution, functional, production, comparative, and extraction additions).
- Remaining work is governance, not invention:
- Define which `candidate` rows are promoted to runtime seed.
- Define naming/inverse conventions where duplicates or near-synonyms exist.

### 2) Action Structure Standardization
- Keep one canonical vocabulary source (`Action_Structure_Vocabularies.md` + data source used by pipeline).
- Normalize mapping references to current paths (remove historical `Reference/...`/`relations/...` path drift).
- If action-to-Wikidata mappings are needed at runtime, generate from one source of truth and version it.

### 3) Identifier Atomicity Enforcement
- Canonical guidance is retained in:
- `md/reference/IDENTIFIER_ATOMICITY_AUDIT.md`
- `md/reference/IDENTIFIER_CHEAT_SHEET.md`
- Operational follow-up:
- Add validation checks in extraction/import paths so QID/FAST/LCC/MARC/Pleiades IDs are treated as opaque tool-resolved identifiers.

### 4) Material/Object Modeling
- Proposed material/object extensions should be reconciled against current entity schema in the golden architecture before implementation.
- Focus on:
- property naming consistency,
- authority ID handling,
- overlap with existing relationship types already in the registry.

### 5) MCP Architecture Track
- MCP docs contain strategy options and migration patterns but are design-stage.
- Reopen when implementation scope is approved:
- decide whether MCP is required platform architecture vs optional integration layer.
- lock server/tool boundaries (Neo4j/Wikidata/FAST/VIAF responsibilities).

### 6) Reasoning Model Track
- Reasoning-model docs are conceptual alternatives (rule/probabilistic/hybrid).
- Reopen only when:
- claim validation lifecycle and confidence policy are finalized,
- required runtime and explainability constraints are explicit.

### 7) Wikidata Coverage Metrics
- Historic coverage numbers in archived analysis docs are not authoritative for current state.
- If needed, regenerate coverage from current canonical registries and current entity schema only.

### 8) KBpedia/KKO Mapping Track
- Active files:
- `md/Architecture/kbpedia.md`
- `md/Architecture/ADR-003-KBpedia-Role-and-Boundaries.md`
- `md/Architecture/KBPEDIA_MAPPING_CONFIDENCE_RUBRIC.md`
- `CSV/kko_chrystallum_crosswalk.csv`
- `scripts/tools/kko_mapping_proposal_loader.py`
- Current policy:
- Keep KKO mappings in proposal/scaffold flow only.
- Do not aggregate into federation master crosswalk until rows pass reviewer gates.
- Open decisions:
- canonical `Situation` node type remains deferred pending schema ADR.

### 9) Claim Confidence Decision Model Track
- Active architecture file:
- `md/Architecture/ADR-006-Claim-Confidence-Decision-Model.md`
- Core implementation work:
- add versioned policy artifact for ordered single-hit decision tables,
- map existing claim types (`factual`, `temporal`, etc.) to `epistemic_type`,
- map authority-tier evidence depth to `federation_depth`,
- migrate fixed `confidence >= threshold` promotion paths to policy-gate outputs.
- Governance rule:
- confidence policy runs in `Pi`; it never bypasses `U -> Pi -> Commit`.
- Implemented baseline:
- `JSON/policy/claim_confidence_policy_v1.json`
- `scripts/tools/claim_confidence_policy_engine.py`
- `scripts/tools/policy_subgraph_loader.py`
- `Neo4j/schema/17_policy_decision_subgraph_schema.cypher`
- Follow-on decision-table candidates (ordered single-hit):
- authority edge type (`SAME_AS`, `ALIGNED_WITH`, `CONFLICTS_WITH`, `NONE`),
- agent routing (facet/period/subject-type to SFA assignment),
- sub-SFA spawn policy from categorized backlink density,
- period/presentism checks (valid/suspicious/presentist),
- entity-to-SubjectConcept promotion policy.

### 10) Project Artifact Registry Track (SCA/SFA Routing)
- Goal:
- create an agent-facing registry that points SCA/SFA/Pi to the right files, tools, and schemas by task type.
- Why:
- current script lists and canonical maps are useful but not enough for deterministic agent routing and handoff.
- Scope (minimum):
- scripts, cypher/schema files, SysML artifacts (BDD/sequence/contracts), ADRs, policies, prompts, registries, and key architecture docs.
- Required fields per artifact:
- `artifact_id`, `artifact_type`, `path`, `status`, `canonicality`, `owner_role`, `used_by_agent_roles`,
- `when_to_use`, `inputs`, `outputs`, `mutation_scope`, `gates`, `dependencies`,
- `example_invocation_or_query`, `validation_command`, `source_of_truth_ref`, `last_validated_at`.
- Initial outputs (TODO):
- `CSV/registry/project_artifact_registry.csv`
- `JSON/registry/project_artifact_registry.json`
- `md/Core/AGENT_ARTIFACT_ROUTING_GUIDE.md`
- Implemented baseline (2026-02-18):
- generator script: `scripts/tools/build_project_artifact_registry.py`
- first snapshot generated (274 indexed artifacts across scripts/schema/sysml/docs/registries/policies/diagrams)
- review queue generated and closed:
- `CSV/registry/project_artifact_registry_review_queue.csv` (0 open rows after override pass)
- deterministic overrides and decisions:
- `JSON/registry/project_artifact_registry_overrides.json`
- `md/Core/PROJECT_ARTIFACT_REGISTRY_DECISIONS.md`
- follow-on needed:
- maintain prefix/path overrides as new artifacts are introduced.
- Suggested execution order:
- inventory -> classify -> annotate routing semantics -> validate entry points -> publish registry snapshots.
- Governance:
- registry is advisory for discovery, but canonical mutation paths still require `U -> Pi -> Commit`.

### 11) External Architecture Review Response Track (2026-02-18)
- Response document:
- `md/Architecture/ARCH_REVIEW_RESPONSE_2026-02-18.md`
- Execution backlog:
- `md/Architecture/ARCH_REVIEW_EXECUTION_BACKLOG_2026-02-18.md`
- Embedding baseline draft:
- `md/Architecture/EMBEDDING_BASELINE_SCOPE_2026-02-18.md`
- Embedding pilot scaffold:
- `scripts/ml/train_kg_embeddings.py`
- Embedding vector index integration plan:
- `md/Architecture/EMBEDDING_VECTOR_INDEX_INTEGRATION_PLAN_2026-02-18.md`
- Bidirectional federation query design:
- `md/Architecture/BIDIRECTIONAL_FEDERATION_QUERY_DESIGN_2026-02-18.md`
- Embedding-assisted disambiguation policy:
- `md/Architecture/EMBEDDING_ASSISTED_DISAMBIGUATION_POLICY_2026-02-18.md`
- GNN experiment protocol:
- `md/Architecture/GNN_EXPERIMENT_PROTOCOL_2026-02-18.md`
- GNN experiment runner scaffold:
- `scripts/ml/link_prediction_gnn.py`
- SHACL/RDFS-lite scope draft:
- `md/Architecture/SHACL_RDFS_LITE_SCOPE_2026-02-18.md`
- SHACL/RDFS-lite validator scaffold:
- `scripts/tools/validate_semantic_constraints.py`
- Schema migration regression harness design:
- `md/Architecture/SCHEMA_MIGRATION_REGRESSION_HARNESS_DESIGN_2026-02-18.md`
- Schema migration regression runner:
- `scripts/tools/schema_migration_regression.py`
- `Neo4j/schema/schema_migration_plan_v1.json`
- LOD baseline drafts:
- `md/Architecture/LOD_BASELINE_SPEC_2026-02-18.md`
- `md/Architecture/VOID_DATASET_DRAFT_2026-02-18.ttl`
- Core decision posture:
- convert external review into explicit `ACCEPT` / `PARTIAL_ACCEPT` / `CHALLENGE` / `DEFER` outcomes.
- Immediate inserts:
- embeddings/vector-index baseline track,
- SHACL/RDFS-lite validation track,
- LOD publication baseline (RDF export + VoID + URI policy),
- schema migration regression testing track.
- Sequencing principle:
- deterministic validation and governance first, advanced ML/GNN second.

## Reopen Triggers
- Need to promote additional relationship types from registry into runtime seed.
- Need to formalize action structure as runtime-enforced schema.
- Need to implement MCP in production architecture.
- Need to ship material/object ingestion and query support.
- Need a fresh Wikidata alignment report based on current canonical files.
- Need gate-qualified KKO mappings ready for federation master crosswalk aggregation.
- Need claim confidence policy artifact and one claims path migrated to policy-gate decision tables.
- Need deterministic file/tool routing for SCA/SFA without relying on prompt memory.
- Need architecture-review response milestones converted to executable tasks.
