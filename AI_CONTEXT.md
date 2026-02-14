# AI Context and Handover Log
Maintained by LLM agents to preserve context across sessions.

---

## ⚠️ Important: Persistence Workflow

**This file only works as a memory bank if committed and pushed regularly.**

- **Local sessions**: Updates are visible in real-time ✅
- **Future sessions**: Only see last pushed version ⚠️
- **Other AI agents**: Need to pull latest from GitHub ⚠️

**Workflow for AI agents:**
1. **Start of session**: Read this file first (pull latest if stale)
2. **During session**: Update as you complete milestones
3. **End of session**: Commit and push this file so next agent sees current state

**Without regular pushes, this becomes a local-only scratchpad.**

---

## Project
Chrystallum Knowledge Graph
Goal: Build a federated historical knowledge graph using Neo4j, Python, and LangGraph.

## Current Architecture State (verified 2026-02-13)

### 1. Temporal Backbone (Calendrical Spine)
Structure:
`Year -> PART_OF -> Decade -> PART_OF -> Century -> PART_OF -> Millennium`

Status: Implemented.

Decisions locked in:
- Historical mode: no `Year {year: 0}` node.
- Year sequence is unidirectional: `FOLLOWED_BY` only.
- BCE/CE labels are historical-style while IDs remain numeric buckets.

Canonical implementation files:
- `scripts/backbone/temporal/genYearsToNeo.py`
- `scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py`
- `scripts/backbone/temporal/05_temporal_hierarchy_levels.cypher`

### 2. Historical Period Spine
Status in clean baseline: not materialized in the live DB.

Notes:
- `scripts/backbone/temporal/create_canonical_spine.py` exists for period/era modeling.
- `scripts/backbone/temporal/link_years_to_periods.py` does not exist.

### 3. Live Neo4j Baseline (clean)
Only temporal backbone labels are present:
- `Year: 4025` (`-2000..2025`, no year 0)
- `Decade: 403`
- `Century: 41`
- `Millennium: 5`

Relationships:
- `FOLLOWED_BY` (Year chain): 4024
- `PART_OF`: 4469
- `PRECEDED_BY`: 0
- Bridge exists: `(-1)-[:FOLLOWED_BY]->(1)`

## Key Corrections (important)
- Previous notes claiming `link_years_to_periods.py` were inaccurate.
- Migration scripts were synced to corrected historical logic (BCE-safe bucketing and labels).
- Documentation was updated to reflect `FOLLOWED_BY`-only year sequencing.

## Concept Label Canonicalization (verified 2026-02-14)

Decision locked:
- `Concept` is deprecated as a node label.
- `SubjectConcept` is canonical.

Migration note:
- `md/Architecture/CONCEPT_TO_SUBJECTCONCEPT_MIGRATION_2026-02-14.md`

Applied updates:
- Removed legacy multi-label examples like `:Person:Concept`, `:Place:Concept`, `:Event:Concept`.
- Updated prompts/guides/roadmap snippets to map concept-like targets to `:SubjectConcept`.
- Updated canonical source index to point to the migration note.

## Main-Node Baseline Sync (verified 2026-02-14)

- `md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md` now references `Key Files/Main nodes.md` as the current operational main-node baseline.
- The operational list was synchronized to:
  - `Subject, Person, Gens, Praenomen, Cognomen, Event, Place, Period, Concept, Dynasty, Institution, LegalRestriction, Claim, Organization, Year, Communication`
- A normalization gap note is retained to map legacy labels (`Subject`/`Concept`) to consolidated architecture terminology (`SubjectConcept`).

## Consolidated Doc Consistency Pass (verified 2026-02-14)

- Performed a wording/structure pass for Section `8.6 Federation Dispatcher and Backlink Control Plane` and Appendix K pipeline wording.
- Clarified dispatcher no-bypass rule and aligned terminology between:
  - Section `8.6` route/gate rules
  - Appendix `K.4-K.6` operational contract

## Federation Datatype Work (verified 2026-02-13)

### New capability
- Full statement export and datatype profiling are now in place for federation design.

Artifacts:
- Full statements export: `JSON/wikidata/statements/Q1048_statements_full.json`
- 100-row flattened sample: `JSON/wikidata/statements/Q1048_statements_sample_100.csv`
- Datatype profile summary: `JSON/wikidata/statements/Q1048_statement_datatype_profile_summary.json`
- Datatype profile by property: `JSON/wikidata/statements/Q1048_statement_datatype_profile_by_property.csv`
- Datatype/value-type pairs: `JSON/wikidata/statements/Q1048_statement_datatype_profile_datatype_pairs.csv`

Scripts:
- `scripts/tools/wikidata_fetch_all_statements.py`
- `scripts/tools/wikidata_sample_statement_records.py`
- `scripts/tools/wikidata_statement_datatype_profile.py`

Spec:
- `md/Architecture/Wikidata_Statement_Datatype_Ingestion_Spec.md`

Observed Q1048 profile baseline:
- statements: 451
- properties: 324
- datatypes: 7
- value types: 5
- qualifier coverage: 23.28%
- reference coverage: 24.17%

## Backlink Policy Refinement (verified 2026-02-13)

- Canonical backlink policy was cleaned and tightened:
  - `Neo4j/FEDERATION_BACKLINK_STRATEGY.md`
- Key lock-ins:
  - Backlink source is semantic reverse triples, not MediaWiki page `linkshere`.
  - `datatype` + `value_type` are mandatory routing gates, not optional metadata.
  - Stop conditions are required (`max_depth`, per-seed budgets, class/property allowlists).
  - Backlink candidates must pass the same datatype profiling workflow as direct statements.

## Backlink Harvester Implementation (verified 2026-02-13)

- New script:
  - `scripts/tools/wikidata_backlink_harvest.py`
- Report output location:
  - `JSON/wikidata/backlinks/`
- Sample run artifact:
  - `JSON/wikidata/backlinks/Q1048_backlink_harvest_report.json`

Q1048 sample (bounded run):
- backlink rows: 87
- candidate sources considered: 25
- accepted: 10
- unresolved class rate: 20.00% (gate pass at default 20%)
- unsupported datatype pair rate: 0.00% (gate pass)
- overall status: `pass`
- dispatcher route metrics now emitted in report (`route_counts`, `quarantine_reasons`)
- frontier metrics now emitted (`frontier_eligible`, `frontier_excluded`, per-entity `frontier_eligible`)
- consolidated architecture updated:
  - `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
  - new normative section `8.6 Federation Dispatcher and Backlink Control Plane`
  - Appendix K updated with dispatcher/backlink operational contract

## Backlink Profiler Implementation (verified 2026-02-13)

- New script:
  - `scripts/tools/wikidata_backlink_profile.py`
- Profiling artifacts (Q1048 accepted candidates):
  - `JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_summary.json`
  - `JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_by_entity.csv`
  - `JSON/wikidata/backlinks/Q1048_backlink_profile_accepted_pair_counts.csv`

Q1048 profile sample:
- requested QIDs: 10
- resolved entities: 10
- statements: 342
- unsupported pair rate: 0.00%
- overall status: `pass`

## Recommended Next Steps
- If rebuilding backbone from scratch:
  1. Run `python scripts/backbone/temporal/genYearsToNeo.py --start -2000 --end 2025`
  2. Run `python scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py --apply`
- Verify with:
  - `python Python/check_year_range.py`
  - graph checks for orphan years (`Year` without `PART_OF -> Decade`).
