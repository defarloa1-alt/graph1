# Wikidata Period Geo Schema Binding (2026-02-18)

Scope: wiki-pure period cohort with `P9350` + `P580` + `P582` and `end < -2000`.

Extended scope also generated: wiki-pure period cohort with `P9350` + `P580` + `P582` + geo signal (no end cutoff).

## Cohort Artifacts
- `Temporal/wikidata_period_geo_edges_end_before_minus2000_2026-02-18.csv`
- `Temporal/wikidata_period_geo_coordinates_end_before_minus2000_2026-02-18.csv`
- `Temporal/wikidata_period_geo_property_coverage_end_before_minus2000_2026-02-18.csv`
- `Temporal/wikidata_period_geo_place_candidates_end_before_minus2000_2026-02-18.csv`
- `Temporal/wikidata_period_geo_period_coordinate_signals_end_before_minus2000_2026-02-18.csv`
- `Temporal/wikidata_period_geo_edges_all_geo_2026-02-18.csv`
- `Temporal/wikidata_period_geo_coordinates_all_geo_2026-02-18.csv`
- `Temporal/wikidata_period_geo_property_coverage_all_geo_2026-02-18.csv`
- `Temporal/wikidata_period_geo_place_candidates_all_geo_2026-02-18.csv`
- `Temporal/wikidata_period_geo_period_coordinate_signals_all_geo_2026-02-18.csv`

## Canonical Mapping Rules
1. `P131` -> `LOCATED_IN` (admin containment, highest geographic authority when present).
2. `P276` -> `LOCATED_IN` (location context).
3. `P17` -> `LOCATED_IN` (country-level context for period/place anchoring).
4. `P706` -> `LOCATED_IN` (physical feature context).
5. `P7153` -> `LOCATED_IN` with `mapping_note=geo_authority_signal` (significant-place signal, lower confidence than `P131`).
6. `P625` -> coordinate signal for place-candidate enrichment (not a relationship by itself).

## Geo Coverage in Current Ancient Cohort
- Subjects: `32`
- Geo edge rows: `14`
- Coordinate rows: `6`
- Place candidates from geo edges: `11`

Property coverage:
- `P131`: `0`
- `P17`: `5`
- `P276`: `4`
- `P706`: `0`
- `P7153`: `5`
- `P625`: `6`

## Geo Coverage in Full Wiki-Pure Cohort (No End Cutoff)
- Subjects: `51` (includes one duplicated `QID` with two PeriodO IDs)
- Geo edge rows: `92`
- Coordinate rows: `12`
- Place candidates from geo edges: `64`

Property coverage:
- `P131`: `4` edges (`3` subjects)
- `P17`: `41` edges (`35` subjects)
- `P276`: `37` edges (`26` subjects)
- `P706`: `5` edges (`1` subject)
- `P7153`: `5` edges (`5` subjects)
- `P625`: `12` coordinate rows (`12` subjects)

## Integration Guidance
1. Ingest geo edges as `(:Period)-[:LOCATED_IN {wikidata_pid, source:'wikidata'}]->(:Place)` when place QID exists.
2. Seed/update `:Place` by `qid` from place-candidate CSV before linking.
3. Apply coordinate signals (`P625`) to place candidates if the place identity is known; otherwise keep as unresolved coordinate evidence attached to the period candidate.
4. Keep `P7153` links provenance-tagged and reviewable (do not treat as strict containment).

## Open Schema Question
- If you need to distinguish strict containment vs associated landmark context, add a new canonical relationship type (for example `ASSOCIATED_WITH_PLACE`) and map `P7153` there. Until then, keep `P7153` under `LOCATED_IN` with explicit provenance metadata.
