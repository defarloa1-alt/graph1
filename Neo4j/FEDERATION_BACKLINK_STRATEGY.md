# Wikidata Backlink Enrichment Strategy

Status: Active  
Last updated: 2026-02-13

## 1. Purpose
Define a controlled backlink expansion policy for federation enrichment.

Backlink means semantic reverse triples from Wikidata statements:
- `?source ?property ?target`
- target is our seed QID (for example `Q1048`)

This is not MediaWiki page `linkshere`. We use structured statement data only.

## 2. What Is Worth Keeping
From prior exploration, these points are useful and retained:
- Reverse traversal finds context not present in a seed node's outbound statements.
- Filtering by `P31` and `P279` is required to avoid graph noise.
- Backlink ingestion must enforce stop conditions (depth, budget, class/property allowlists).
- Datatype profiling should gate ingestion before write.

## 3. Why `datatype` and `value_type` Matter
`property` alone is not enough to ingest safely.  
`datatype` and `value_type` tell us what the value actually is and how to process it.

| `datatype` | `value_type` | Use in pipeline |
|---|---|---|
| `wikibase-item` | `wikibase-entityid` | Create/merge node-to-node edge candidate (topology expansion). |
| `time` | `time` | Parse precision and uncertainty; anchor to temporal backbone (`Year` etc.). |
| `external-id` | `string` | Write to federation identity map, never a new entity by itself. |
| `quantity` | `quantity` | Numeric normalization (`amount`, `unit`, bounds). |
| `monolingualtext` | `monolingualtext` | Store localized literal, no graph expansion. |
| `string` | `string` | Store literal metadata, no graph expansion. |
| `commonsMedia` | `string` | Store media pointer/URL metadata. |
| `globecoordinate` | `globecoordinate` | Route to geographic handler or hold queue if handler unavailable. |

Operationally, this gives three benefits:
- Correct routing: edge vs property vs temporal anchor.
- Safety: reject or defer unsupported pairs instead of polluting schema.
- Cost control: skip expensive expansion for literal-only statements.

## 4. Backlink Ingestion Policy
For each seed QID:
1. Fetch reverse triples with property allowlist.
2. Resolve each source node class (`P31`), with optional parent walk (`P279`) to approved superclass.
3. Pull full statements for accepted source QIDs.
4. Run datatype/value-type gate using the same logic as direct ingestion.
5. Materialize only allowed node/edge shapes with provenance.

Required provenance on every materialized edge:
- `source_system = "wikidata"`
- `source_mode = "backlink"`
- `source_property = "Pxxx"`
- `retrieved_at`

## 5. Stop Conditions
Mandatory controls per run:
- `max_depth`: default `1` (no recursive walk unless explicitly requested).
- `max_sources_per_seed`: default `200`.
- `max_new_nodes_per_seed`: default `100`.
- `property_allowlist`: explicit set only.
- `class_allowlist`: schema-backed set only.
- `denylist_namespaces`: non-item namespaces excluded.

Abort run if:
- unsupported datatype pair rate exceeds threshold (default `>10%`),
- unresolved class mapping rate exceeds threshold (default `>20%`).

## 6. Minimal SPARQL Pattern
```sparql
SELECT ?source ?sourceLabel ?prop ?p31 WHERE {
  BIND(wd:Q1048 AS ?target)
  VALUES ?prop { wdt:P710 wdt:P1441 wdt:P138 wdt:P112 wdt:P737 wdt:P828 }
  ?source ?prop ?target .
  ?source wdt:P31 ?p31 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 500
```

## 7. Integration With Existing Datatype Workflow
Existing artifacts used as baseline:
- `scripts/tools/wikidata_fetch_all_statements.py`
- `scripts/tools/wikidata_statement_datatype_profile.py`
- `md/Architecture/Wikidata_Statement_Datatype_Ingestion_Spec.md`

Backlink workflow must emit the same profile outputs so we can compare:
- direct seed profile vs backlink candidate profile
- qualifier/reference coverage deltas
- unsupported datatype pair rates

## 8. Immediate Implementation Plan
1. Add `scripts/tools/wikidata_backlink_harvest.py` (seed query + class filter).
2. Add `scripts/tools/wikidata_backlink_profile.py` (datatype/value-type gating on candidates).
3. Add run report in `JSON/wikidata/backlinks/` with accepted/rejected reasons.
4. Keep depth at `1` until false positive rate is measured.
