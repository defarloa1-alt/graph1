# Reference Backlog (Consolidated)

## Purpose
- Preserve useful ideas from non-canonical `md/reference` analysis docs in one actionable backlog.
- Reduce folder sprawl while keeping a clear re-entry point for future design work.

## Current Status
- Relationship registry is now canonical in `Relationships/relationship_types_registry_master.csv`.
- Facet registry is canonical in `Facets/facet_registry_master.json` and `Facets/facet_registry_master.csv`.
- Architecture baseline is `Key Files/2-12-26 Chrystallum Architecture - DRAFT.md` (golden) with consolidated counterpart for implemented decisions.

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

## Reopen Triggers
- Need to promote additional relationship types from registry into runtime seed.
- Need to formalize action structure as runtime-enforced schema.
- Need to implement MCP in production architecture.
- Need to ship material/object ingestion and query support.
- Need a fresh Wikidata alignment report based on current canonical files.
