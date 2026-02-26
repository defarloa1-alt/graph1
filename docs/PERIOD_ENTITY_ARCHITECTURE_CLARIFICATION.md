# Period Entity — Architecture Clarification

**Date:** 2026-02-25  
**Status:** Resolved — Option B adopted  
**Context:** User asked to clarify Period entity before running self-describing subgraph cleanup. Architect decision: Option B. Period nodes (1,077) added to cleanup script. PeriodO stays as federation for on-demand lookup; temporal_anchor model going forward.

---

## Current State (What Exists in Neo4j)

| Component | Count | Range / Notes |
|-----------|-------|---------------|
| **Year backbone** | 4,025 nodes | -2000 to 2025 CE |
| **Period** | 1,077 nodes | begin_year: -1,399,999 to -2001 |
| **PeriodCandidate** | 1,077 nodes | Staging; all CANONICALIZED_AS → Period |
| **GeoCoverageCandidate** | 357 nodes | Staging join PeriodCandidate ↔ Period |
| **Period–Year links** | **0** | No STARTS_IN_YEAR or ENDS_IN_YEAR edges exist |

---

## The Incompleteness

**Periods are not connected to the Year backbone.**

The import script (`import_enriched_periods.py`) is designed to create:

```cypher
(p:Period)-[:STARTS_IN_YEAR]->(ys:Year {year: pc.begin_year})
(p:Period)-[:ENDS_IN_YEAR]->(ye:Year {year: pc.end_year})
```

But this step fails silently because:

- **Period range:** -1.4M (Paleolithic) to -2001 BCE
- **Year backbone:** -2000 to 2025 only
- **Overlap:** None — the Year backbone does not contain years like -10000, -50000, -1399999

So 1,077 Period nodes exist with `begin_year`/`end_year` properties, but **zero** have `STARTS_IN_YEAR` or `ENDS_IN_YEAR` edges. The temporal backbone linkage was never materialized.

---

## Two Competing Architectural Views

### View A: PeriodO Pipeline (What Was Built)

- **Source:** PeriodO gazetteer (periodo-dataset.csv, filtered to end_year < -2000)
- **Flow:** PeriodCandidate (staging) → Period:E4_Period (canonical)
- **Design:** Period nodes are temporal definitions with CIDOC-CRM E4_Period
- **Geo:** GeoCoverageCandidate links Period to geographic tokens (unnormalized; Place has 0 edges)
- **Scope:** Global prehistoric/ancient (Paleolithic, Mesolithic, Neolithic, regional periods)
- **Roman Republic fit:** Poor — Roman Republic (509–27 BCE) is *after* the -2000 cutoff, so it is excluded from this filtered set

### View B: Perplexity-on-Periods (Architect Decision)

- **Source:** `md/Architecture/perplexity-on-periods.md`
- **Core idea:** "Period" is overloaded. Decompose into:
  1. **Temporal span** — `temporal_scope` on claims/entities (not Period nodes)
  2. **Entity with dates** — Q17167 (Roman Republic) = ORGANIZATION + `is_temporal_anchor: true`
  3. **SubjectConcept** — thematic anchor (already solved)
  4. **Geographic scope** — time-stamped GEOGRAPHIC claims, not period property
  5. **Classification label** — temporal qualifier on claims

- **PeriodO role:** Authority for temporal definitions only. Map `temporal_scope` to PeriodO; store `periodo_id` as authority identifier.
- **No "Period Discovery" pipeline** — use `temporal_anchor` on existing entities + small harvest of pure periods (Hellenistic, Iron Age, etc.).

---

## Tension

| Aspect | PeriodO Pipeline | Perplexity View |
|--------|------------------|-----------------|
| Period nodes | 1,077 from PeriodO (prehistoric/ancient) | Avoid monolithic Period; use temporal_anchor on entities |
| Roman Republic | Excluded (end -27 > -2000) | Q17167 as ORGANIZATION + temporal_anchor |
| Year backbone | Designed to link via STARTS_IN_YEAR/ENDS_IN_YEAR | Year backbone is index; temporal_scope on claims |
| GeoCoverageCandidate | Staging join to Period | Geographic scope = GEOGRAPHIC_SFA claims, not period property |

---

## Open Decisions (Before Cleanup)

1. **Keep or delete Period nodes?**
   - If **keep:** They are disconnected from Year backbone; need either (a) extend Year backbone to cover -1.4M to -2001, or (b) accept Period as standalone temporal taxonomy without Year linkage.
   - If **delete:** Align with Perplexity view; rebuild temporal model via temporal_anchor on entities.

2. **PeriodCandidate / GeoCoverageCandidate cleanup:**
   - Advisor approved delete (staging complete). But if we delete Period too, we are removing the entire PeriodO-derived temporal layer.
   - If we keep Period, we should still delete PeriodCandidate and GeoCoverageCandidate (staging is done).

3. **Roman Republic temporal coverage:**
   - PeriodO filtered set excludes Roman Republic (509–27 BCE).
   - For Chrystallum’s Roman Republic focus, the relevant temporal designations may need to come from Entity temporal_anchor (Q17167, Q201038, etc.) and SubjectConcepts, not from PeriodO.

4. **Document the decision:**
   - Whatever we choose, it should be written into `docs/` or `md/Architecture/` so future work is consistent.

---

## Recommendation (For Architect/Advisor)

Before running the cleanup script:

1. **Decide:** Keep Period nodes as-is (disconnected taxonomy) or remove them and align with Perplexity temporal_anchor model.
2. **If keep Period:** Proceed with cleanup (delete PeriodCandidate, GeoCoverageCandidate). Period stays; document that STARTS_IN_YEAR/ENDS_IN_YEAR are not materialized due to Year backbone range mismatch.
3. **If remove Period:** Add Period to the cleanup script; then rebuild temporal model per Perplexity (temporal_anchor on entities, small pure-period harvest).

---

## References

- `md/Architecture/perplexity-on-periods.md` — Decompose Period into roles
- `scripts/backbone/temporal/import_enriched_periods.py` — PeriodO pipeline
- `md/Architecture/TEMPORAL_GEO_BACKBONE_MODEL_2026-02-18.md` — Year/Period backbone spec
- `Temporal/PeriodRecommendations.md` — Dual-node (PeriodCandidate → Period) design
- `Temporal/periodo_filtered_end_before_minus2000_with_geography.csv` — 1,077 rows, end < -2000
