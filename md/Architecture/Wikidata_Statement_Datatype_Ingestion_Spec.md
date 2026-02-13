# Wikidata Statement Datatype Ingestion Spec

Status: Active  
Last updated: 2026-02-13

## 1. Purpose
Define a schema-driven ingestion contract for Wikidata statements so Chrystallum can ingest diverse entities without property-specific custom code.

## 2. Scope
Input payloads produced by:
- `scripts/tools/wikidata_fetch_all_statements.py`

Core output targets:
- Graph topology (nodes/edges)
- Temporal backbone anchors
- Federation identity properties
- Content properties
- Qualifier/reference provenance metadata

## 3. Canonical Statement Model
Each statement is processed as:
- `property` (P-id)
- `mainsnak` (`datatype`, `snaktype`, `value_type`, `value`)
- `rank`
- optional `qualifiers`
- optional `references`

## 4. Datatype Routing Rules
| Datatype | Value Type | Ingestion Action | Chrystallum Target |
|---|---|---|---|
| `wikibase-item` | `wikibase-entityid` | Ensure target node exists; create semantic edge from source to target | Graph topology |
| `time` | `time` | Parse time + precision; anchor to temporal backbone (`Year`, optional higher granularity) | Temporal backbone |
| `external-id` | `string` | Store as federated identity key on source node (`external_ids` map + optional normalized columns) | Federation index |
| `string` | `string` | Store as scalar/text property | Node content |
| `monolingualtext` | `monolingualtext` | Store localized value with language | Labels/content |
| `quantity` | `quantity` | Store normalized numeric payload (`amount`, `unit`, bounds) | Measured attributes |
| `commonsMedia` | `string` | Store media reference/URL | Media metadata |

## 5. Temporal Rules
- Historical mode baseline: no `Year {year: 0}` node; `-1 -> 1` bridged by `FOLLOWED_BY`.
- Sequence edge for years is unidirectional: `FOLLOWED_BY` only.
- Time values are not forced into one precision bucket. Keep raw time payload and derive anchors.
- Precision interpretation:
  - day/month/year precision values can anchor to `Year`.
  - optional rollups to `Decade`/`Century`/`Millennium` should use `PART_OF` traversal, not duplicate source edges.

## 6. Qualifier and Reference Policy
- Qualifiers and references are first-class metadata.
- Do not discard qualifiers on ingestion; persist them as edge or claim metadata.
- Do not discard references; persist source property sets (for example `P248`, `P854`, `P813`) for auditability.
- Rank must be preserved (`preferred`, `normal`, `deprecated`).

## 7. Federation Identity Policy
- External IDs should be centralized under a map-like property:
  - `external_ids.<system_key> = value`
- Optionally denormalize high-priority IDs into dedicated properties for indexing.
- Presence of an `external-id` statement never creates a new entity node by itself.

## 8. Implementation Artifacts
- Full statement export:
  - `scripts/tools/wikidata_fetch_all_statements.py`
- Sampling for manual review:
  - `scripts/tools/wikidata_sample_statement_records.py`
- Datatype profile analytics:
  - `scripts/tools/wikidata_statement_datatype_profile.py`

## 9. Validation Requirements
- Every ingestion run should emit:
  - statement counts by datatype and value_type
  - qualifier/reference coverage rates
  - top properties by frequency
- Regression checks:
  - no temporal creation of year 0
  - no reintroduction of `PRECEDED_BY` in year sequence
  - no dropped references/qualifiers in transformed output
