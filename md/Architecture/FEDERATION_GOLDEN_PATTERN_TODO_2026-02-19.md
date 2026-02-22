# Federation Golden Pattern TODO (2026-02-19)

Status: `pending` implementation pack for geo+temporal federation hardening.

## Objective
Define and implement the Chrystallum "golden pattern" for `what+where+when` records, plus a first-class federation meta-subgraph rooted at Chrystallum.

## A) Golden Pattern Definition (Triangulated Record)

A row/entity is `gold_star` only when all of the following are true:

1. `Wikidata identity` present:
- stable `wikidata_qid`
- non-empty `wikidata_label`

2. `Pleiades identity` present:
- stable `pleiades_id`
- non-empty `pleiades_uri`

3. `GeoNames identity` present:
- stable `geonames_id`
- non-empty `geonames_feature_code`

4. `Temporal signal` present:
- at least one of `P580/P582/P2348/P9350` from Wikidata or normalized min/max year in Chrystallum temporal fields

5. `Geographic signal` present:
- at least one place relation (`P131/P17/P276/P706/P7153`) or resolvable coordinate (`P625`) mapped to canonical place context

Working formula:
- `is_fully_triangulated = has_wikidata_qid AND has_pleiades_id AND has_geonames_id AND has_temporal_signal AND has_geographic_signal`

## B) Federation Score v1 (TODO Upgrade)

Replace star-only assignment with numeric `federation_score` and pattern-based state.

### Core concept

Each row/entity gets:

1. `federation_score` (`0-100`)
2. `federation_state` (discrete band)
3. `federation_pattern_id` (which required subgraph pattern it currently satisfies)

### Base pattern (minimum useful subgraph)

`what+where+when` base anchor:

1. identity node (`QID` or canonical entity id)
2. place link (`LOCATED_IN` or equivalent geo edge)
3. temporal link (`STARTS_IN_YEAR` and/or `ENDS_IN_YEAR`, or equivalent period/date signal)

### Scoring dimensions (initial weights)

1. `federation_leg_coverage` (0-40)
- Wikidata, Pleiades, GeoNames, and other configured authority legs.

2. `spacetime_anchor_quality` (0-30)
- presence and quality of geographic + temporal anchoring.

3. `semantic_alignment_quality` (0-15)
- canonical type mapping + relation canonicalization.

4. `subgraph_integrity` (0-10)
- expected edges present for declared pattern id.

5. `cipher_key_quality` (0-5)
- deterministic key populated with normalized null token policy.

### Suggested federation_state bands

1. `FS0_UNFEDERATED` (`0-24`)
2. `FS1_MINIMAL` (`25-49`)
3. `FS2_BASE_ANCHORED` (`50-69`) - passes base `what+where+when` pattern
4. `FS3_TRIANGULATED` (`70-84`) - strong multi-leg federation
5. `FS4_REFERENCE_GRADE` (`85-100`) - high completeness + consistent semantics

## C) Chrystallum Federation Meta-Subgraph (TODO Model)

### Core nodes

1. `(:Platform {platform_id:'chrystallum', label:'Chrystallum'})`
2. `(:FederationHub {hub_qid:'Q124542039', label:'federation of databases'})`
3. `(:FederationSource {source_id, source_label, source_qid, resource_type, homepage})`
4. `(:FederationProperty {source_id, property_id, property_label, direction, required})`
5. `(:FederationIOContract {source_id, input_contract, output_contract, notes})`

### Core relationships

1. `(:Platform)-[:CONSISTS_OF]->(:FederationHub)`
2. `(:FederationHub)-[:HAS_SOURCE]->(:FederationSource)`
3. `(:FederationSource)-[:USES_PROPERTY]->(:FederationProperty)`
4. `(:FederationSource)-[:HAS_IO_CONTRACT]->(:FederationIOContract)`

### Source seed set (minimum)

1. `wikidata`
2. `pleiades`
3. `geonames`
4. `periodo`
5. `worldcat_entities` (as planned authority leg)

### Required metadata per source

1. `resource_type` (authority graph, gazetteer, bibliographic entity service, period authority, etc.)
2. `values_pulled` (explicit property list)
3. `inputs` (query keys accepted)
4. `outputs` (fields persisted)
5. `comment` (scope and confidence notes)

## D) GeoNames Lightweight Feature Ontology (TODO)

Use `CSV/geographic/geonames_feature_codes_distinct_v1.csv` as empirical guide.

Top-level super-classes:

1. `AdministrativeArea`
2. `PopulatedPlace`
3. `ArchaeologicalOrHistoricalFeature`
4. `HydrographicFeature`
5. `OrographicFeature`
6. `CoastalOrMarineFeature`
7. `BuiltStructure`
8. `OpenSpaceOrFacility`

Implementation direction:

1. Keep canonical Chrystallum place types as primary.
2. Add GeoNames feature-code layer as federation semantic overlay.
3. Store usage metrics as annotations (`row_count`, `distinct_geonames_ids`, `distinct_pleiades_ids`).
4. Add orthogonal tags:
- `is_historical`
- `is_admin_seat`
- `is_abandoned`

## E) Cipher Key Contract (Object/Where/When Subgraph)

For federation-ready test entities, build deterministic key:

`federation_cipher_key = <wikidata_qid>|<pleiades_id>|<geonames_id>|<temporal_start>|<temporal_end>|<canonical_place_type>`

Notes:

1. Keep canonical IDs first-class; federation IDs are aligned dimensions.
2. Missing fields must be normalized to explicit null tokens (for deterministic hashing).
3. Cipher key is required for fast vertex-jump and subgraph configuration in SCA/SFA workflows.

## F) TODO Backlog Items

1. `FGP-001` - Replace star logic in `scripts/backbone/geographic/build_place_type_hierarchy.py` with `federation_score`, `federation_state`, and `federation_pattern_id`.
2. `FGP-002` - Extend `scripts/backbone/geographic/build_pleiades_geonames_crosswalk.py` with scoring dimensions + deterministic `federation_cipher_key`.
3. `FGP-003` - Add seed migration file `Neo4j/schema/20_federation_meta_subgraph.cypher` for Platform/FederationHub/Source/Property/IOContract nodes.
4. `FGP-004` - Add integration loader or migration runner step for the federation meta-subgraph.
5. `FGP-005` - Add validation query pack proving counts by `federation_state` and base/triangulated pattern coverage.
6. `FGP-006` - Add lightweight GeoNames feature superclass mapping table and QA checks.
7. `FGP-007` - Add first SCA API integration spike (`openai` and optional `perplexity`) as a read-only disambiguation worker against Neo4j, with explicit input/output contract and audit log of ontology decisions.

## G) Acceptance Criteria

1. We can query all rows by `federation_state`; `FS2+` reliably satisfy the base `what+where+when` pattern and `FS3+` satisfy triangulated federation expectations.
2. Federation meta-subgraph is queryable from one root:
- `(:Platform {platform_id:'chrystallum'})-[:CONSISTS_OF]->(:FederationHub)`
3. Every federation source has explicit input/output/property contract nodes.
4. Geo feature codes are grouped into the lightweight superclass model with reproducible mapping.

## H) Current Implemented Bridge Artifact (2026-02-19)

Implemented script:

1. `scripts/backbone/geographic/build_geonames_wikidata_bridge.py`

Current output artifacts:

1. `CSV/geographic/geonames_wikidata_mapping_v1.csv`
2. `CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv`
3. `CSV/geographic/pleiades_geonames_wikidata_tgn_stats_v1.json`

Bridge chain now materialized:

1. `Pleiades -> GeoNames` (existing crosswalk)
2. `GeoNames (P1566) -> Wikidata QID` (new)
3. `Wikidata QID -> TGN` (existing `tgn_wikidata_mapping.csv`)

Facet policy artifacts drafted:

1. `md/Architecture/FEDERATION_FACET_POLICY_2026-02-19.md`
2. `CSV/geographic/federation_facet_policy_v1.csv`
3. `CSV/geographic/place_temporal_status_policy_v1.csv`
