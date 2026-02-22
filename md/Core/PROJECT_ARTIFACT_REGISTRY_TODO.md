# Project Artifact Registry TODO (SCA/SFA-Oriented)

Status: pinned TODO for next execution window.

## Progress (2026-02-18)
- Initial generator implemented: `scripts/tools/build_project_artifact_registry.py`
- Initial outputs generated:
- `CSV/registry/project_artifact_registry.csv` (274 artifacts)
- `CSV/registry/project_artifact_registry_review_queue.csv` (0 open review items after overrides)
- `JSON/registry/project_artifact_registry.json`
- `JSON/registry/project_artifact_registry_overrides.json`
- `md/Core/AGENT_ARTIFACT_ROUTING_GUIDE.md`
- `md/Core/PROJECT_ARTIFACT_REGISTRY_DECISIONS.md`
- Coverage now includes:
- scripts/tooling, Neo4j schema/pipeline files, SysML contracts, architecture/ADR docs, key registries, policy artifacts, and diagram assets.
- Current state is first-pass and intentionally conservative:
- many artifacts are tagged `read_only` unless deterministic write intent is clear from filename/type.
- Queue hardening complete:
- override mechanism now applies deterministic path/prefix decisions before review-queue generation.
- Next pass can focus on adding prefix-level policies as registry grows (instead of per-path overrides).

## Objective
Build a machine-readable project registry that routes SCA/SFA/Pi to the correct artifacts with minimal ambiguity.

## What This Must Solve
- Given a task, identify the right files/tools immediately.
- Distinguish read-only references from mutation-capable pipelines.
- Encode governance constraints so agents do not bypass gates.
- Reduce prompt-memory dependence by making routing explicit.

## Core Artifact Types
- `script` (Python/PowerShell/shell)
- `schema_cypher` (Neo4j constraints/indexes/schema/pipeline cypher)
- `pipeline_runner` (entrypoint scripts such as `run_qid_pipeline.py`)
- `policy` (JSON decision models, rubric artifacts)
- `sysml_contract` (inputs/outputs/error envelopes/dispatch contracts)
- `sysml_bdd` (block definitions and responsibilities)
- `sysml_sequence` (execution sequence logic)
- `registry` (CSV/JSON canonical tables)
- `architecture_doc` (canonical implementation guidance)
- `adr` (decision boundaries and invariants)
- `prompt_or_agent_spec`

## Required Columns/Fields
- `artifact_id` (stable slug)
- `artifact_type`
- `path`
- `status` (`active`, `draft`, `deprecated`, `archived`)
- `canonicality` (`canonical`, `compatible_wrapper`, `legacy_reference`)
- `owner_role` (`SCA`, `SFA`, `Pi`, `Platform`)
- `used_by_agent_roles` (list)
- `task_tags` (list, e.g., `federation`, `claims`, `temporal`, `routing`)
- `when_to_use` (one-line trigger condition)
- `inputs` (typed payload summary)
- `outputs` (typed payload summary)
- `mutation_scope` (`read_only`, `proposal_only`, `canonical_write`)
- `gates` (required gates before use/write)
- `dependencies` (critical upstream artifacts)
- `example_invocation_or_query`
- `validation_command`
- `source_of_truth_ref` (canonical doc/section)
- `last_validated_at` (YYYY-MM-DD)

## Minimum Deliverables
1. `CSV/registry/project_artifact_registry.csv`
2. `JSON/registry/project_artifact_registry.json`
3. `md/Core/AGENT_ARTIFACT_ROUTING_GUIDE.md`

## Build Phases
1. Inventory pass:
- Enumerate candidate artifacts from `scripts/`, `Neo4j/schema/`, `sysml/`, `md/Architecture/`, `md/Agents/`, `JSON/policy/`, `Relationships/`, `Facets/`.
2. Classification pass:
- Assign `artifact_type`, `task_tags`, `canonicality`, and `owner_role`.
3. Routing semantics pass:
- Fill `when_to_use`, `mutation_scope`, `gates`, and dependencies.
4. Validation pass:
- Run sample commands/queries for active executable entries and record `last_validated_at`.
5. Publish pass:
- Emit CSV + JSON snapshots and a concise agent routing guide.

## SCA/SFA Routing Views (Derived)
- `by_task`: task tag -> top artifacts in preferred order.
- `by_agent_role`: role -> allowed artifacts and mutation scope.
- `by_lifecycle`: bootstrap vs extraction vs proposal vs promotion.

## Non-Negotiable Constraints
- Registry never overrides canonical governance: `U -> Pi -> Commit`.
- Canonical source remains `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`.
- Legacy wrappers are listed but flagged as non-edit targets.

## Rebuild Command
- `python scripts/tools/build_project_artifact_registry.py`
