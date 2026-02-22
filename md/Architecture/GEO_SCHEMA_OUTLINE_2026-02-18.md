# Geo Schema Outline (2026-02-18)

Status: Working canonical outline for Chrystallum geographic typing and placement.

## 1) Top-Level Distinction Model

All geographic type mappings roll up to one of three roots:

1. `MAN_MADE_STRUCTURE`
2. `PHYSICAL_FEATURE`
3. `SETTLEMENT_TYPE`

Fallback:

1. `UNKNOWN_OR_NEEDS_REVIEW`

## 2) Canonical Place-Type Hierarchy

Source of truth:

- `CSV/geographic/place_type_hierarchy_v1.csv`

Hierarchy:

1. `PLACE_TYPE_ROOT`
2. `MAN_MADE_STRUCTURE` -> `PLACE_TYPE_ROOT`
3. `PHYSICAL_FEATURE` -> `PLACE_TYPE_ROOT`
4. `SETTLEMENT_TYPE` -> `PLACE_TYPE_ROOT`
5. `SETTLEMENT` -> `SETTLEMENT_TYPE`
6. `REGION` -> `SETTLEMENT_TYPE`
7. `WATER_FEATURE` -> `PHYSICAL_FEATURE`
8. `LAND_FEATURE` -> `PHYSICAL_FEATURE`
9. `BUILT_FEATURE` -> `MAN_MADE_STRUCTURE`
10. `DEFENSIVE_BUILT_FEATURE` -> `MAN_MADE_STRUCTURE`
11. `SACRED_BUILT_FEATURE` -> `MAN_MADE_STRUCTURE`
12. `ARCHAEOLOGICAL_SITE` -> `MAN_MADE_STRUCTURE`
13. `TRANSPORT_FEATURE` -> `MAN_MADE_STRUCTURE`
14. `UNKNOWN_OR_NEEDS_REVIEW` -> `PLACE_TYPE_ROOT`

## 3) Core Node Types

1. `:Place`
2. `:Period`
3. `:PlaceType`
4. `:PlaceTypeTokenMap`
5. `:GeoSemanticType`

Optional next-step semantic nodes (recommended):

1. `:Material`
2. `:FunctionType`
3. `:ObjectType`

## 4) Canonical Relationships

Core geo:

1. `(:Place)-[:LOCATED_IN]->(:Place)`
2. `(:Period)-[:LOCATED_IN]->(:Place)`
3. `(:Place)-[:INSTANCE_OF_PLACE_TYPE]->(:PlaceType)`
4. `(:PlaceType)-[:SUBCLASS_OF]->(:PlaceType)`
5. `(:PlaceTypeTokenMap)-[:MAPS_TO]->(:PlaceType)`
6. `(:PlaceType)-[:HAS_GEO_SEMANTIC_TYPE]->(:GeoSemanticType)`
7. `(:Place)-[:HAS_GEO_SEMANTIC_TYPE]->(:GeoSemanticType)` (derived)
8. `(:ObjectType)-[:BELONGS_TO_GEO_SEMANTIC_TYPE]->(:GeoSemanticType)`

Temporal+geo link points:

1. `(:Period)-[:STARTS_IN_YEAR]->(:Year)` (temporal backbone)
2. `(:Period)-[:ENDS_IN_YEAR]->(:Year)` (temporal backbone)

## 5) Source Property Binding (Wikidata)

Geo-to-canonical mapping:

1. `P131` -> `LOCATED_IN`
2. `P276` -> `LOCATED_IN`
3. `P17` -> `LOCATED_IN`
4. `P706` -> `LOCATED_IN`
5. `P7153` -> `LOCATED_IN` with provenance note
6. `P625` -> coordinate signal (evidence/properties, not direct edge by itself)

## 6) Place-Type Token Mapping Pipeline

Script:

- `scripts/backbone/geographic/build_place_type_hierarchy.py`

Input:

1. `Geographic/pleiades_place_type_distinct_tokens_2026-02-18.csv`
2. `CSV/geographic/place_type_hierarchy_v1.csv`

Outputs:

1. `CSV/geographic/pleiades_place_type_token_mapping_v1.csv`
2. `CSV/geographic/pleiades_place_type_token_mapping_review_v1.csv`
3. `CSV/geographic/pleiades_place_type_wikidata_cache_v1.json`
4. `Geographic/pleiades_plus.csv` (Pleiades+ from `ryanfb/pleiades-plus`)
5. `CSV/geographic/pleiades_geonames_crosswalk_v1.csv`
6. `CSV/geographic/pleiades_geonames_place_summary_v1.csv`

Mapping methods:

1. `exact:*` (deterministic)
2. `heuristic:*` (keyword-based)
3. `wikidata:<qid>:<matches>` (API-backed inference)
4. `fallback:unmapped`

Wikidata signal capture in mapping output:

1. `wikidata_geo_pids_present`, `wikidata_geo_pid_count`
2. `wikidata_time_pids_present`, `wikidata_time_pid_count`
3. `wikidata_periodo_ids`
4. `wikidata_start_time_values`, `wikidata_end_time_values`
5. `wikidata_label_match_strength`

## 7) Review Policy

Buckets:

1. `AUTO_MAPPED`
2. `REVIEW_REQUIRED`
3. `LOW_SIGNAL_SKIP_REVIEW`

Review file contents:

1. `REVIEW_REQUIRED` only

Low-signal terms (examples):

1. `unlocated`
2. `label`
3. `people`
4. `feature`
5. `unknown`

## 8) Star Policy

Columns in mapping outputs:

1. `quality_star`
2. `quality_star_reason`
3. `is_fully_triangulated` (v2 target)

Assignment rules:

1. Current v1:
- `gold_star`: `Pleiades-backed token` + `Wikidata QID identity` + `temporal indicator`.
- `silver_star`: mapped but partially federalized.
- `bronze_star`: unresolved/needs-review rows.

2. Planned v2 (triangulated):
- `gold_star`: `Wikidata QID` + `Pleiades ID` + `GeoNames ID` + temporal signal + geographic signal.
- `silver_star`: one federation leg missing, but temporal+geo signals present.
- `bronze_star`: unresolved or weak-signal rows.

3. v2 design source:
- `md/Architecture/FEDERATION_GOLDEN_PATTERN_TODO_2026-02-19.md`

Temporal indicator fields:

1. `wikidata_time_pid_count > 0` OR
2. non-empty `wikidata_periodo_ids` OR
3. non-empty `wikidata_start_time_values` / `wikidata_end_time_values`.

## 9) Operational Settings (Wikidata Throttle)

CLI controls:

1. `--wikidata-min-interval-seconds`
2. `--wikidata-max-retries`
3. `--wikidata-search-limit`

Current safe defaults:

1. `min_interval=0.8s`
2. `max_retries=6`

## 10) Schema Migration Artifact

Neo4j schema extension file:

1. `Neo4j/schema/18_geo_semantic_extension.cypher`

Purpose:

1. Seeds `GeoSemanticType` roots.
2. Seeds `ObjectType` and `FunctionType` stubs.
3. Adds safe derived `Place -> GeoSemanticType` links when place types exist.

Building object subgraph file:

1. `Neo4j/schema/19_building_object_where_backbone.cypher`

Purpose:

1. Materialize `:Building` from man-made `:Place`.
2. Link `Building -> Place` via `LOCATED_IN`.
3. Link `Building -> Year` via `STARTS_IN_YEAR/ENDS_IN_YEAR` from date hints.
4. Emit deterministic `object_where_cipher_key` for object subgraph tests.

## 11) GeoNames Federation Path

Builder script:

1. `scripts/backbone/geographic/build_pleiades_geonames_crosswalk.py`

Purpose:

1. Pull latest Pleiades+ CSV from GitHub (`ryanfb/pleiades-plus`)
2. Normalize `pleiades_url` to `pleiades_id`
3. Normalize `geonames_url` to `geonames_id`
4. Enrich with local Pleiades label/type/date fields
5. Emit row-level and per-place crosswalks for federation joins
6. Feed triangulation coverage (`Wikidata+Pleiades+GeoNames`) for star-v2 policy

## 12) Object Subgraph Note

Current scope:

1. Building objects only (no full material/function schema required yet).
2. Full details like `:Material` relations can be added later without breaking key model.
3. Federation key test path uses IDs + optional Wikidata QID + date hints.

## 13) Modeling Guidance for SCA/SFA

SCA:

1. Preserve source-faithful claims/properties (`P31/P279/P361/P186/P131/...`)
2. Assign canonical type path + distinction root
3. Send unresolved terms to `REVIEW_REQUIRED`

SFA:

1. Refine unresolved terms with facet context
2. Resolve ambiguous terms (`polis`, `nome`, `limes`, `archive-repository`) with domain evidence
3. Propose new canonical type nodes only when reusable across many entities
