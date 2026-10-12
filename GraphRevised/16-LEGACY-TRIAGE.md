# Legacy Triage and Adoption Register

## Purpose

This register establishes a non-destructive boundary between the clean-start
graph and the pre-existing repository. It is a triage artifact, not a
migration plan.

No file was moved, deleted, archived, or made authoritative by this review.
Legacy paths retain their current locations until a clean-start replacement is
implemented and validated.

## Decision categories

| Category | Meaning |
|---|---|
| `ADOPT` | Already matches the clean-start contract and may be used after focused validation. |
| `ADAPT` | Contains useful logic or UX, but must be rewritten against the clean-start contract. |
| `REFERENCE` | Useful historical/design context; not executable authority. |
| `ARCHIVE` | Retained historical material that must not run against the clean-start database. |
| `EXCLUDE` | Generated, vendored, cached, temporary, or local-environment material. |

## First-pass inventory

| Area | Category | Rationale | Next action |
|---|---|---|---|
| [GraphRevised](.) | `ADOPT` | Active clean-start architecture, direct operations, and bounded Wikidata adapter. | Maintain as the only active graph contract. |
| [viewer](../viewer) | `ADAPT` | The custom UI is a likely solution for readable captions and compact/evidence projections, but it uses legacy API/property assumptions. | Define a clean-start read API (Phase B) before adapting components; it already uses React 18 + Cytoscape.js + cola + Vite, the agreed explorer stack ([20-EXPLORER-UI.md](20-EXPLORER-UI.md)). |
| [scripts/backbone/temporal](../scripts/backbone/temporal) and [Python](../Python) year checks | `ADAPT` | The Year backbone is retained, but existing scripts require schema and safety review. | Extract read-only year validation into a tested clean-start utility when needed. |
| [scripts/tools](../scripts/tools) Wikidata retrieval utilities | `ADAPT` | They may contain reusable request/payload patterns, but predate the candidate-only adapter and source-observation contract. | Prefer [adapters/wikidata_identity.py](adapters/wikidata_identity.py); review individual utilities only for a concrete capability gap. |
| [Neo4j/schema](../Neo4j/schema) and [Cypher](../Cypher) | `ARCHIVE` | Existing schema and operations use legacy assumptions and are unsafe to apply to the clean-start database. | Do not run; retain as implementation history. |
| [scripts/agents](../scripts/agents), [Chrystal_2](../Chrystal_2), and [SCA](../SCA) | `ARCHIVE` | Legacy orchestration predates the direct-operation and proposal boundary. | Do not reuse directly; Phase 5 starts with a new bounded proposal workflow. |
| [docs](../docs), [md](../md), and [Key Files](../Key%20Files) | `REFERENCE` | Valuable design and decision history, but broadly uses legacy terms such as `Claim`, `ProposedEdge`, and `SubjectConcept`. | Consult only when an active document identifies a specific question. |
| [Archive](../Archive) | `ARCHIVE` | Already intentionally archived historical material. | Preserve in place; do not duplicate into `GraphRevised`. |
| [JSON](../JSON), [CSV](../CSV), and [output](../output) | `REFERENCE` | Contains mixed raw data, derived data, and generated results with unclear clean-start status. | Evaluate individual datasets only with provenance and a defined ingestion need. |
| [tests](../tests) and legacy test scripts | `REFERENCE` | May capture useful edge cases, but test legacy behavior and schemas. | Port only specific assertions needed by the clean-start contract. |
| `.venv`, `viewer/node_modules`, `.pytest_cache`, `tmp`, `temp`, logs, and generated assets | `EXCLUDE` | Local dependencies, caches, temporary material, or generated outputs. | Never move into `GraphRevised`; clean only under a separate, explicit maintenance task. |

## Observed legacy markers

The legacy-marker scan found substantial use of `Claim`, `ProposedEdge`,
`SubjectConcept`, Aura references, and the former Aura identifier across
hundreds of files. These terms are not automatically wrong as historical
documentation, but they identify material that must not be treated as the
active clean-start contract.

The active contract is limited to:

```text
Entity
Subject
AuthorityRecord
SourceObservation
Assertion
Proposal
Year
Annotation   (added 2026-10-12, 23-NARRATIVE-AND-NOTES.md)
```

## Adoption rules

1. Do not move legacy code into this directory merely because it is useful.
2. Start from a concrete clean-start requirement, then create a new adapter,
   query, UI component, or utility with tests.
3. Link the replacement to the legacy source in its documentation when that
   history helps explain a design decision.
4. Mark a legacy path `ARCHIVE` before withdrawing it from active use; do not
   delete it as part of a clean-start implementation task.
5. Never run legacy writes, migrations, or schema scripts against local
   clean-start database `neo4j`.

## Gate before Phase 5

Phase 5 may begin because its proposal workflow will be written as a new,
bounded workflow on top of the Phase 3 direct operations. It must not invoke
or adapt the legacy agent chain directly.

Before adopting any legacy asset during Phase 5 or later, add a row to this
register that states the exact source path, target capability, category, and
validation plan.
