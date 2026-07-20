# Domain events — pack significant events (Chrystal 2)

**Status:** Ownership + federation pattern locked — enrich not implemented yet.  
**Owner:** **Domain** (SCA / Domain bootstrap / curate + baseline dates).  
**Later:** **Any SFA** may *deepen* Domain Event shells in their facet lane (military campaigns, diplomatic congresses, religious rites, economic seizures, etc.) — they do not replace Domain ownership of the pack significant-event shortlist or baseline dates.  
**Bio (special case):** owns **participation** — Person↔Event links (`PARTICIPATED_IN` and related claim work) against existing Domain Event shells; not the Domain shortlist or baseline dating.

There is **no VIAF-equivalent** single authority for historical events. Stack small complementary federations by facet (date / participant / location / corroboration).

## Pivot (away from old instance)

Pack timeline events are **Domain structure + Domain enrich**, not a byproduct of
biographic harvest. Bio deals with **who participated**, not which pack events exist or how they are baselined on the Domain timeline.

## What Domain owns

1. **Which events** are pack-significant  
   - Schema apply may land WD shells from P793 (`SIGNIFICANT_EVENT`) / P1344
     (`PARTICIPATED_IN`) as provisional candidates.  
   - Domain **curates** the timeline shortlist (keep / soft / drop).  
   - Today on `roman_republic`: 7× `SIGNIFICANT_EVENT` + 2× `PARTICIPATED_IN`,
     all undated stubs.

2. **Baseline dating + three-slot tether pattern** (when implemented)  
   - Stamp `start_year` / `end_year` (+ Year edges) on kept `:Event` shells.  
   - Soft when scholarly spans disagree — same pattern as PeriodO on Periods.

3. **Acceptance payload**  
   - Timeline markers once drawable; expose via `acceptance_view` (or successor).

## Three-slot tether (locked)

Per Domain Event shell — complementary, not exclusive:

| Slot | Role | Primary candidate(s) | Notes |
|------|------|----------------------|--------|
| **Date** | Chronology for timeline X | **GODOT** (linked-data years) and/or **MRR** (Broughton — modern reconstructive fasti) | WD P580/P582 may bootstrap; soft if GODOT ≠ MRR ≠ WD |
| **Participant** | Who (via Persons) | **DPRR** | **Bio** owns Person↔Event participation links; DPRR anchors Persons |
| **Location** | Where | **Pleiades** | Same Place enrich pattern as Domain capital (`stamp_place_pleiades`) |

### Deferred / corroboration (cards later — not blocking vignette)

| Source | Facet | Status |
|--------|-------|--------|
| **Fasti Triumphales / Capitolini** | Primary-source triumph chronology (distinct from MRR reconstruction) | Deferred card |
| **EDH** | Epigraphic corroboration | Provisional `identity_tether`-style — card later |
| **Nomisma** | Numismatic corroboration | Provisional — card later (already known at pack seed level) |

Do **not** bulk-load these into Neo until FederationCards + thin seeds exist under `Chrystal_2/federations/`.

## What Bio owns vs does not

| Bio owns | Bio does **not** own |
|----------|----------------------|
| Participation — Person↔Event (`PARTICIPATED_IN`, person claims citing Events) | Seeding Domain `SIGNIFICANT_EVENT` from WD |
| Deepening participant density via DPRR Persons where biographic | Choosing the pack’s canonical event shortlist |
| | Overwriting Domain baseline event dates |

Other SFAs deepen non-participation facets (military ops, diplomatic framing, religious context, etc.) under the same Domain Event shells.

Pack timeline events remain **Domain structure + Domain enrich**, not a byproduct of biographic harvest.

## Pipeline slot (planned — thin)

```
schema apply     → provisional Event shells + SIGNIFICANT_EVENT / PARTICIPATED_IN
Domain curate    → shortlist (noop / drop / keep) — human or LLM review
Domain stamp     → years (+ optional GODOT/MRR cite props) on kept shells
                 → location Pleiades on Event Places when present
acceptance_view  → events[] with drawable flags
SFAs later       → deepen Events in facet scope (do not re-seed Domain shortlist)
Bio               → participation (Person↔Event); not Domain shortlist/dates
```
Fold into `pipeline.py bootstrap` only if it stays thin (like `stamp_place_pleiades`).
Do **not** grow a Bio-owned parallel event dating CLI for Domain timeline.

## UI (deferred)

Markers on the Republic lane vs a separate Events lane — decide after dating exists.
Undated Event shells are not drawable.

## Trap

Bulk-attaching every WD P793 hit without curation recreates old-instance clutter.
Prefer a **seed shortlist** for the pack vignette; soft-keep the rest as candidates.
There is no single event VIAF — do not force one federation to own all four facets.
