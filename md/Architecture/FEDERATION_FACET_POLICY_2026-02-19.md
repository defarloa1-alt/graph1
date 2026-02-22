# Federation-Facet Policy (2026-02-19)

Status: draft policy for SCA/SFA routing and promotion gates.

## Purpose
Align federation behavior with facet intent while preserving a Pleiades-seeded historical pipeline.

## Core Policy

1. Seed authority for historical place workflows is `Pleiades`.
2. `Wikidata` is the identity/ontology bridge for all facets.
3. `GeoNames` is the modern normalization layer, not the historical seed.
4. `TGN` is a cultural/art-historical enrichment layer.
5. `PeriodO` is period authority where available.

## Place Time-State Policy

Use one stable place identity with state classification:

1. `Historical`
2. `Modern`
3. `Continuous`
4. `Unknown`

State assignment table:

1. `CSV/geographic/place_temporal_status_policy_v1.csv`

## Facet Federation Routing Table

Deterministic facet policy table:

1. `CSV/geographic/federation_facet_policy_v1.csv`

This table defines:

1. `seed_authority`
2. `required_federations`
3. `preferred_federations`
4. `golden_profile`
5. `place_status_requirement`
6. `temporal_gate`

## Golden Pattern Clarification

Current default geo-temporal golden pattern:

1. `Pleiades + Wikidata + GeoNames + temporal signal + geographic signal`

Facet-conditional extension:

1. Cultural/art-focused facets may treat `TGN` as required for facet-gold.
2. Geo/political/military remain primarily `Pleiades+Wikidata+GeoNames`.

## Promotion Gate Advice

1. Keep `TGN` optional for global geo gold until TGN chain coverage improves.
2. Enforce strict temporal gate (`end date`) for period claims sourced from historical place seed.
3. Use `Unknown` place state as review trigger, not rejection trigger.

## Next Execution Order

1. Wire `federation_facet_policy_v1.csv` into SCA/SFA routing logic as read-only policy.
2. Add `place_temporal_status` columns to crosswalk builders and assign values deterministically.
3. Update star logic to support facet-conditional gold profile selection.
4. Add QA report: per facet, count rows by `Historical/Modern/Continuous/Unknown`.
5. After QA stabilization, seed policy subgraph nodes for this table.
