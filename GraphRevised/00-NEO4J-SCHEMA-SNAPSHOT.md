# Neo4j Schema Snapshot

**Purpose:** Read-only Phase 0 baseline for the clean-start graph.

**Revalidated (UTC):** 2026-10-11
**Endpoint:** `neo4j://127.0.0.1:7687`
**Database:** `neo4j`
**Neo4j:** 2026.09.0 Enterprise

This snapshot records the database as observed. It does not define a target schema and does not imply that the observed names should all be retained.

## Counts

- Nodes: **4025**
- Relationships: **4024**

## Node labels

| Label | Count |
|---|---|
| Year | 4025 |

## Relationship types

| Type | Count |
|---|---|
| FOLLOWED_BY | 4024 |

## Node properties

| Labels   | Property          | Count |
| -------- | ----------------- | ----- |
| ['Year'] | created           | 4025  |
| ['Year'] | iso8601_end       | 4025  |
| ['Year'] | iso8601_start     | 4025  |
| ['Year'] | label             | 4025  |
| ['Year'] | temporal_backbone | 4025  |
| ['Year'] | year              | 4025  |
| ['Year'] | year_value        | 4025  |
==? Why year and year_value?==
## Relationship properties

| Type | Property | Count |
|---|---|---|
| FOLLOWED_BY | created | 4023 |

## Temporal backbone

| Metric | Value |
|---|---|
| count | 4025 |
| minYear | -2000 |
| maxYear | 2025 |
| exampleLabel | 1 BCE |
| anotherLabel | 999 CE |

| Metric | Value |
|---|---|
| count | 4024 |
| firstFrom | -2000 |
| lastFrom | 2024 |
| firstTo | -1999 |
| lastTo | 2025 |

### Year semantics and backbone integrity

- `Year.year` and `Year.year_value` are populated for all 4,025 nodes and
  have identical integer values.
- `Year.year` is the canonical numeric property for all revised-graph writes.
- Year zero is intentionally absent.
- The unique cross-era link is `(:Year {year: -1})-[:FOLLOWED_BY]->(:Year {year: 1})`.
- All other `FOLLOWED_BY` relationships advance by one numeric year.
- The chain has one start node (`-2000`) and one end node (`2025`).

The `created` property is present on 4,023 of 4,024 `FOLLOWED_BY`
relationships. It is legacy operational metadata and is not a correctness
requirement for the revised temporal backbone.

## Constraints

| Name | Type | Labels/types | Properties | Options |
|---|---|---|---|---|

## Indexes

| Name | Type | Entity type | Labels/types | Properties | State | Population % |
|---|---|---|---|---|---|---|
| index_1b9dcc97 | LOOKUP | RELATIONSHIP |  |  | ONLINE | 100.0 |
| index_460996c0 | LOOKUP | NODE |  |  | ONLINE | 100.0 |
