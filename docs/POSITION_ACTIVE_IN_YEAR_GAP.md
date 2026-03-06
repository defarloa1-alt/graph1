# Position ↔ Active-in-Year Link Gap

## Issue

Position data and "active in year" are written, but there is **no graph link** between them:

1. **POSITION_HELD** edges have `r.year` (and optionally `r.start_year`, `r.end_year`) as properties
2. **Floruit** is derived on Person: `floruit_start`, `floruit_end` from position years
3. **No edges to Year backbone**: Neither Person nor POSITION_HELD connects to `:Year` nodes
4. **Property name mismatch**: `survey_dprr_from_graph` expects `r.year_start` / `r.year_end`, but `enrich_position_held_temporal` sets `r.start_year` / `r.end_year`

## Current State

| Component | Property | Value |
|-----------|----------|-------|
| dprr_import | r.year | string e.g. "-43" |
| enrich_position_held_temporal | r.start_year, r.end_year | from r.year |
| survey_dprr_from_graph | r.year_start, r.year_end | **never set** — query returns 0 rows |
| Floruit derivation | p.floruit_start, p.floruit_end | from r.year / r.start_year |
| Year backbone link | — | **none** — no ACTIVE_IN_YEAR or STARTS_IN_YEAR from position |

## Fixes (implemented)

### 1. Align property names ✓

Standardized on `start_year` / `end_year`. Updated:
- `survey_dprr_from_graph`: queries `coalesce(r.start_year, r.year)` and `coalesce(r.end_year, r.start_year, r.year)`
- `context_packet`, `dprr_wikidata_matcher`: use `coalesce(r.start_year, r.year)` for year

### 2. Link position to Year backbone ✓

Migration `migration_position_active_in_year.cypher` creates `(Person)-[:ACTIVE_IN_YEAR]->(Year)` for each year in each position's range. Run after `enrich_position_held_temporal`. Enables:
- Year-by-year queries: "who was active in -59?"
- Temporal backbone traversal
- UI timeline materialization

### 3. Optional: dprr_post_years.json enrichment

`extract_dprr_post_years.py` extracts hasDateStart/hasDateEnd from Turtle (richer than SPARQL inYear). A separate enrichment could set `r.start_year`, `r.end_year` from `dprr_post_years.json` keyed by PostAssertion ID (`r.dprr_assertion_uri`).
