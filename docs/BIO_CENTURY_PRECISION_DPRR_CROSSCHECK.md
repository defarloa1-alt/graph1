# Birth/Death Century Precision & DPRR Cross-Check

## Issue: Q1777350 / DPRR 1084 (Publius Porcius Laeca)

**Harvest output:**
- birth: -250  death: -250
- Wikidata: P569/P570 both say "3rd century BCE"

**Root cause:** Wikidata stores century-level dates with precision 7. The time value is the century midpoint (e.g. `-0250-00-00T00:00:00Z` for 3rd c. BCE). Our `parse_year()` extracts -250 for both birth and death, producing the misleading `birth_year == death_year`.

**Reality:** Birth and death are almost never the same year. When both come from century precision, we are over-interpreting imprecise data.

## Wikidata API Structure

Time claims (P569, P570) include `datavalue.value.precision`:

| Precision | Meaning |
|-----------|---------|
| 7 | century |
| 8 | decade |
| 9 | year |
| 10 | month |
| 11 | day |

For Q1777350:
- P569: `{"time":"-0250-00-00T00:00:00Z","precision":7}`
- P570: `{"time":"-0250-01-01T00:00:00Z","precision":7}`

## DPRR Cross-Check

Wikidata description: *"tribune of the plebs in 199 BC"* — DPRR has more precise office data.

**Graph query to inspect DPRR office years for a person:**
```cypher
MATCH (e:Entity {dprr_id: '1084'})-[r:POSITION_HELD]->(p:Position)
RETURN p.label_name AS office, r.start_year AS start, r.end_year AS end, r.year AS year
```

When DPRR has office years (e.g. 199 BC) and Wikidata only has century, prefer DPRR for floruit/active-in-year; treat birth/death as uncertain.

## Possible Enhancements

1. **Parse precision** in `_parse_entity_to_props` — read `datavalue.value.precision` for time claims.
2. **Flag century-only dates** — when precision ≤ 8 and birth_year == death_year, either:
   - Don't write birth_year/death_year (treat as unknown), or
   - Write with `birth_precision: 'century'` / `death_precision: 'century'` for downstream handling.
3. **DPRR-informed floruit** — when person has `dprr_id` and POSITION_HELD with years, use those for ACTIVE_IN_YEAR even when Wikidata birth/death are imprecise.
