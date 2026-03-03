# Event Design Decision — Defer Event Nodes

**Status:** Design decision (Mar 2026)  
**Scope:** Marriage, divorce, office assumed/left, status acquired — temporal data

---

## Decision

**Store temporal data on edges** (start_year, end_year, end_reason, etc.) for now. **Defer Event nodes** until OI-02 or until a clear need emerges (complex event queries, provenance, multi-participant events).

---

## Rationale

- Edge properties are sufficient for current queries (who held office when, who was married when)
- Event nodes require a fuller design (event types, participants, temporal bounds, provenance)
- Data is sparse — DPRR gives inYear for posts; marriage/divorce dates often missing
- OI-02 already defines migration path: POSITION_HELD pre-populated → OfficeHolding event nodes later

---

## Edge Properties (Phase 4.3)

| Edge | Properties |
|------|------------|
| SPOUSE_OF | start_year, end_year, end_reason, series_ordinal |
| POSITION_HELD | start_year, end_year, colleague_ids[], location_id, source_id |
| HAS_STATUS | year (already present) |

---

## When to Revisit

- Need to query "all events in year X" across types
- Need event-level provenance (who asserted, when)
- Multi-participant events (e.g. treaty signing)
- OI-02 OfficeHolding migration triggered
