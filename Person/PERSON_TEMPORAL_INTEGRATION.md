# Person Dates → Temporal Backbone Integration

**Status:** Design / TODO  
**Depends on:** Year backbone (-2000 to 2025), dprr_layer1 date normalisation

---

## Date Sources

| Source | Property / Edge | Format | Example |
|--------|-----------------|--------|---------|
| Wikidata | P569 (birth), P570 (death) | `{"time": "-0106-09-29T00:00:00Z", "precision": 9}` | 106 BCE |
| DPRR | POSITION_HELD.year, HAS_STATUS.year | String | "-509", "509" |
| DPRR | PostAssertion inYear | RDF literal | 509 (BCE) |

---

## Temporal Backbone (Existing)

- **:Year** nodes: `year` property (integer; negative = BCE, no year 0)
- Range: -2000 to 2025 (genYearsToNeo.py)
- Roman Republic: -509 to -27 BCE ✓ within range
- **Relationships:** `BORN_IN_YEAR`, `DIED_IN_YEAR` (Person → Year) — already in SYS_RelationshipType

### Exact dates vs Year backbone

| What | Where | Purpose |
|------|-------|---------|
| **Exact date** (day/month/year) | Property on Person: `birth_date`, `death_date` | ISO 8601 string (e.g. `-0106-09-29`) for display, precision, provenance |
| **Year linkage** | Edge: `(Person)-[:BORN_IN_YEAR]->(Year)` | Temporal backbone traversal, period overlap, "who in year X?" |

The exact date is **not** an edge to Year. Year nodes represent full years (iso8601_start..iso8601_end). For day precision you store the full date as a property; the edge to Year anchors the person in the backbone for year-level queries.

---

## Integration Points

### 1. Person → Year (birth/death)

When P569/P570 are available (from context_packet wikidata_raw):

```
MERGE (y:Year {year: $year})
MERGE (p:Person {qid: $qid})-[:BORN_IN_YEAR]->(y)   // from P569
MERGE (p:Person {qid: $qid})-[:DIED_IN_YEAR]->(y)   // from P570
```

- Use `normalise_wikidata_date()` → extract year from ISO range
- For precision 7 (century): use midpoint or skip (too coarse)
- For precision 9 (year): use year directly
- Store `birth_date` (point) or `birth_date_min`/`birth_date_max` (range) as Person properties per schema
- Link BORN_IN_YEAR to Year using earliest year when range; use point year when exact

### 2. POSITION_HELD → Year

Currently: `(person)-[:POSITION_HELD {year: "-509"}]->(position)`

Option A: Keep `year` on edge; add optional `(position)-[:HELD_IN_YEAR]->(y:Year)` for backbone queries  
Option B: Add `(person)-[:HELD_OFFICE_IN_YEAR]->(y:Year)` with office_id on edge  
Option C: Leave as literal; temporal queries use r.year string

**Recommendation:** Option A — add HELD_IN_YEAR from POSITION_HELD edge to Year when year parses to integer.

### 3. Person → Period (LIVED_DURING)

When birth/death years are known, infer overlap with Roman Republic (-509 to -27):

```
(p:Person)-[:BORN_IN_YEAR]->(yb:Year)
(p:Person)-[:DIED_IN_YEAR]->(yd:Year)
(yrr:Period {qid: 'Q17167'})  // Roman Republic
WHERE yb.year >= -509 AND yd.year <= -27
MERGE (p)-[:LIVED_DURING]->(yrr)
```

Defer to Phase 4 (P-code promotion) — P2348 IN_PERIOD already maps to Period.

---

## Implementation Checklist

- [x] **dprr_layer1:** parse_time_value_to_year_and_iso() for SPARQL time strings
- [x] **orchestrator:** _derive_birth_death_from_wikidata() from wikidata_raw P569/P570
- [x] **executor:** _write_temporal_to_entity() — MERGE Year, BORN_IN_YEAR, DIED_IN_YEAR, birth_date, death_date
- [ ] **dprr_import:** When promoting P569/P570 (Phase 4), same logic
- [ ] **POSITION_HELD:** Optional pass to add (pos)-[:HELD_IN_YEAR]->(y) from r.year
- [ ] **Year backbone:** Verify range includes -509..-27 (Roman Republic); extend if needed

---

## References

- `scripts/federation/dprr_layer1.py` — normalise_wikidata_date, format_iso_bce
- `scripts/backbone/temporal/genYearsToNeo.py` — Year node creation
- `scripts/maintenance/enrich_rel_type_domain_range.py` — BORN_IN_YEAR, DIED_IN_YEAR
- `md/Guides/Temporal_Comprehensive_Documentation.md` — Year/Period architecture
