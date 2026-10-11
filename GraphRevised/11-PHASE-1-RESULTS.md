# Phase 1 Schema Results

## Applied target

- Endpoint: `neo4j://127.0.0.1:7687`
- Database: `neo4j`
- Neo4j: 2026.09.0 Enterprise
- Applied: 2026-10-11

The schema was applied from
[10-PHASE-1-SCHEMA.cypher](10-PHASE-1-SCHEMA.cypher).

## Applied constraints

| Constraint | Label | Properties |
|---|---|---|
| `year_year_unique` | `Year` | `year` |
| `entity_id_unique` | `Entity` | `id` |
| `subject_id_unique` | `Subject` | `id` |
| `authority_record_id_unique` | `AuthorityRecord` | `id` |
| `authority_record_system_identifier_unique` | `AuthorityRecord` | `system`, `identifier` |
| `source_observation_id_unique` | `SourceObservation` | `id` |
| `assertion_id_unique` | `Assertion` | `id` |
| `proposal_id_unique` | `Proposal` | `id` |

All constraint-backed indexes were verified `ONLINE`.

## Data-preservation verification

The local database was counted immediately before and after schema application:

| Measure | Before | After |
|---|---:|---:|
| Nodes | 4,025 | 4,025 |
| Relationships | 4,024 | 4,024 |

No application data was created, changed, or deleted. Phase 1 changed schema
metadata only.

## Confirmed temporal contract

- `Year.year` is the canonical numeric property.
- `Year.year_value` remains equal to `Year.year` in the starting backbone but
  is not used for revised-graph writes.
- Years run from `-2000` through `2025`.
- Year zero is intentionally absent.
- `FOLLOWED_BY` links `-1` directly to `1`; every other link advances one
  numeric year.

## Deferred deliberately

Phase 1 does not add:

- non-unique indexes;
- property-existence constraints;
- relationship-property constraints;
- assertion-predicate registries;
- agent, governance, authority, or source-content data;
- Entity, Subject, AuthorityRecord, SourceObservation, Assertion, or Proposal
  nodes.

Those additions require a demonstrated Phase 2 or Phase 3 write/query need.
