# Federation Score Model (2026-02-19)

Status: `draft` for implementation in geo/temporal federation pipelines.

## Objective
Score each entity/subgraph by how fully it is federalized and structurally usable for `what+where+when` traversal.

## Required Output Fields

1. `federation_score` (0-100)
2. `federation_state` (`FS0_UNFEDERATED`, `FS1_MINIMAL`, `FS2_BASE_ANCHORED`, `FS3_TRIANGULATED`, `FS4_REFERENCE_GRADE`)
3. `federation_pattern_id` (`PATTERN_NONE`, `PATTERN_BASE_WWW`, `PATTERN_TRIANGULATED_WWW`, `PATTERN_REFERENCE`)
4. `federation_cipher_key` (deterministic)

## Base Pattern

`PATTERN_BASE_WWW` is true if all are present:

1. identity (`wikidata_qid` or canonical id)
2. geographic edge/signal (`LOCATED_IN` or equivalent)
3. temporal edge/signal (`STARTS_IN_YEAR`/`ENDS_IN_YEAR` or equivalent)

## Scoring Dimensions

`federation_score = leg + spacetime + semantic + integrity + cipher`

1. `leg` (0-40): coverage across configured federation legs (Wikidata, Pleiades, GeoNames, etc.).
2. `spacetime` (0-30): quality/completeness of geo and temporal anchoring.
3. `semantic` (0-15): canonical type + canonical relation alignment.
4. `integrity` (0-10): required edges for pattern id are present.
5. `cipher` (0-5): key is deterministic and complete with normalized null tokens.

## State Decision Table (ordered)

1. If `federation_score >= 85` and `pattern = PATTERN_REFERENCE` -> `FS4_REFERENCE_GRADE`
2. Else if `federation_score >= 70` and `pattern = PATTERN_TRIANGULATED_WWW` -> `FS3_TRIANGULATED`
3. Else if `federation_score >= 50` and `pattern = PATTERN_BASE_WWW` -> `FS2_BASE_ANCHORED`
4. Else if `federation_score >= 25` -> `FS1_MINIMAL`
5. Else -> `FS0_UNFEDERATED`

## Cipher Contract

`federation_cipher_key = <qid>|<pleiades_id>|<geonames_id>|<start>|<end>|<canonical_type>`

Rules:

1. Use explicit null token for missing fields.
2. Keep field order fixed.
3. Keep key stable across reruns unless source values change.

## Implementation Targets

1. `scripts/backbone/geographic/build_place_type_hierarchy.py`
2. `scripts/backbone/geographic/build_pleiades_geonames_crosswalk.py`
3. federation QA query pack (new)

