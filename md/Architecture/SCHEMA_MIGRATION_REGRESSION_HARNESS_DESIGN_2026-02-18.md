# Schema Migration Regression Harness Design (2026-02-18)

Status: `ARB-SCHEMA-001` design baseline.

## Objective
Define a deterministic harness that verifies schema migration safety before and after applying Neo4j schema scripts.

## Scope
- Validate schema objects and core invariants for canonical migration paths.
- Detect regressions in constraints, indexes, and critical query behavior.
- Produce machine-readable PASS/FAIL artifacts.

Out of scope:
- Data-quality validation for all domain entities.
- Throughput benchmarking under production load.

## Primary Inputs
- Schema migration sequence (ordered script list), for example:
  1. `Neo4j/schema/01_schema_constraints.cypher`
  2. `Neo4j/schema/02_schema_indexes.cypher`
  3. `Neo4j/schema/03_schema_initialization.cypher`
  4. `Neo4j/schema/05_temporal_hierarchy_levels.cypher`
  5. `Neo4j/schema/17_policy_decision_subgraph_schema.cypher`
- Validator expectations:
  - `Neo4j/schema/06_bootstrap_validation_runner.cypher`
  - `Neo4j/schema/08_core_pipeline_validation_runner.py`

## Harness Phases
1. Preflight
- Confirm DB connectivity and Neo4j version.
- Confirm migration files exist and are ordered.
- Confirm execution mode (`dry_run` or `apply`).

2. Baseline Snapshot (pre-migration)
- Capture:
  - constraint names
  - index names and states
  - counts for selected labels used in fixed assertions
- Persist snapshot artifact as JSON.

3. Migration Apply
- Execute migration files in strict order.
- Stop on first execution error.
- Record per-file status and timings.

4. Post-Migration Validation
- Re-run fixed assertions against expected invariants.
- Check index online state.
- Compare pre/post snapshots for unexpected drops.

5. Report Emit
- Emit deterministic JSON report with summary and per-assertion outcomes.

## Fixed Assertions (v1)
1. Constraint integrity
- Required constraint set exists after migration.
- No required constraint is missing.

2. Index integrity
- Required index set exists after migration.
- Required indexes are `ONLINE`.

3. Core label survivability
- Critical labels remain queryable (`Human`, `Event`, `Place`, `Period`, `SubjectConcept`, `Claim`).

4. Policy subgraph schema readiness
- `PolicyVersion`, `DecisionTable`, `DecisionRule`, `DecisionCondition`, `DecisionOutcome` constraints/indexes are present when policy schema is included.

5. Deterministic validation runner compatibility
- Existing runner checks execute and return PASS/FAIL cleanly.

## Assertion Sources
- Use existing expected lists as source of truth:
  - `Neo4j/schema/06_bootstrap_validation_runner.cypher`
  - `Neo4j/schema/08_core_pipeline_validation_runner.py`

Rule:
- Do not duplicate large expectation lists in multiple places unless auto-generated.

## Execution Modes
- `dry_run`:
  - no schema writes, validates script discoverability and expected check definitions.
- `apply`:
  - runs schema scripts and validation checks.
- `apply_with_seed` (optional later):
  - adds deterministic seed/verify scripts for deeper regression coverage.

## Output Contract (for `ARB-SCHEMA-002` runner)
JSON report fields:
- `metadata_header`:
  - `contract_version`
  - `runner_version`
  - `migration_plan_id`
  - `run_fingerprint`
- `execution`:
  - `mode`
  - `started_at`
  - `completed_at`
  - `files_executed`
- `summary`:
  - `assertions_executed`
  - `errors`
  - `warnings`
  - `passes`
  - `status`
- `assertions`:
  - `assertion_id`
  - `status`
  - `severity`
  - `reason_codes`
- `diff`:
  - `missing_constraints_post`
  - `missing_indexes_post`
  - `non_online_indexes_post`
  - `unexpected_drops`

## Safety and Governance
- Default target should be isolated test DB or test namespace.
- Runner must not modify production DB without explicit operator intent.
- Preserve `U -> Pi -> Commit` for canonical mutation paths.

## Initial Command Pattern (planned for `ARB-SCHEMA-002`)
```powershell
python scripts/tools/schema_migration_regression.py `
  --mode apply `
  --plan Neo4j/schema/schema_migration_plan_v1.json `
  --output JSON/reports/schema_migration_regression_report.json
```

## Acceptance Criteria Mapping (`ARB-SCHEMA-001`)
- Pre/post test strategy defined: yes.
- Fixed assertions defined: yes.
- Regression report contract defined: yes.
- Implementation handoff ready for runner scaffold (`ARB-SCHEMA-002`): yes.

## Implementation Link (`ARB-SCHEMA-002`)
- Runner scaffold:
  - `scripts/tools/schema_migration_regression.py`
- Baseline plan:
  - `Neo4j/schema/schema_migration_plan_v1.json`
