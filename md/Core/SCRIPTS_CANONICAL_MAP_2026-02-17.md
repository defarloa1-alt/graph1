# Scripts Canonical Map (2026-02-17)

Purpose: keep one source of truth per workflow while preserving older entrypoints.

## Canonical Roots

- `scripts/agents/` - runtime agent orchestration
- `scripts/tools/` - claim, Wikidata, registry pipelines
- `scripts/backbone/` - temporal, subject, geographic backbone workflows
- `scripts/setup/` - environment and DB checks
- `Neo4j/schema/` - schema and pipeline runners

## Cleanup Applied

1. Moved geographic ingest script to canonical backbone location:
- from `Python/federation/pleiades_bulk_ingest.py`
- to `scripts/backbone/geographic/pleiades_bulk_ingest_roman_republic.py`

2. Moved period facet tagging script to canonical temporal location:
- from `Facets/Scripts/period_facet_tagger.py`
- to `scripts/backbone/temporal/period_facet_tagger.py`

3. Removed duplicate maintenance targets by converting duplicates to wrappers:
- `Python/migrate_temporal_hierarchy_levels.py` -> wrapper to `scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py`
- `subjectsAgentsProposal/files3/ingest_claims.py` -> wrapper to `subjectsAgentsProposal/files4/ingest_claims.py`
- `subjectsAgentsProposal/files3/validate_claims.py` -> wrapper to `subjectsAgentsProposal/files4/validate_claims.py`

## Compatibility Policy

- Old paths continue to work through thin wrappers.
- New work should only modify canonical paths.
- If old wrappers are still required after migration, keep them read-only.

## Next Cleanup Pass (Recommended)

- Replace legacy OpenAI calls (`openai.ChatCompletion.create`) in:
  - `scripts/agents/facet_agent_framework.py`
  - `scripts/agents/query_executor_agent_test.py`
- Normalize schema label usage in legacy subject scripts (`Subject`/`Person` vs `SubjectConcept`/`Human`).
- Migrate additional `Python/` one-off scripts into `scripts/backbone/` or archive with wrappers.
