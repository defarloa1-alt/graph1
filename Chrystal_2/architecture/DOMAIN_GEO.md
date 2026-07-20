# Domain geo — thin approach (Chrystal 2)

**Status:** Thin path implemented (Rome seed + stamp).  
**Owner:** Domain agent (structure at schema apply; enrich via `stamp_place_geo`).  
**Depth:** Thin Domain — **not** a full Pleiades / GeoNames load.  
**Card:** `federations/pleiades.json`  
**Seed:** `federations/crosswalks/pleiades_roman_republic_seed.csv` (Roma `423025` ↔ Q220)

## Parallel to temporal

| Temporal | Geo |
|----------|-----|
| Global **Year** backbone (already loaded) | Optional later: shared Place-type taxonomy only — **no** world Place lattice preload |
| Pack bounds on **SubjectDomain** (`start_year`/`end_year`) | Pack “where” on Domain via **edges to Places**, not a single geo property dump |
| WD `:Period` shells + soft **PeriodO** citation | WD `:Place` shells + soft **Pleiades** (etc.) citation |
| PeriodO seed CSV, not bulk survey | Tiny Domain **geo seed** from pack + curated ids — not `pleiades_roman_republic.csv` bulk |

## What Domain owns

1. **Structural Places from the pack** (Schema propose → Domain apply)  
   - Clear kinds only: capital, core territory / country (when structural), maybe seat of government.  
   - Today on `roman_republic`: `(:SubjectDomain)-[:CAPITAL]->(:Place {qid:Q220})` Rome.  
   - Do **not** mint every WD location/event locale as Domain structure.

2. **Soft containment / type** (enrich, not exclusive shelves)  
   - e.g. Rome soft-within Latium / Italy when federations support it.  
   - Place-type tokens from `CSV/geographic/place_type_hierarchy_v1.csv` when useful — apply sparingly.

3. **Federation enrich on Place shells** (like PeriodO on Period)  
   - **Pleiades-first** for ancient RR context (see legacy `federation_facet_policy` geographic/archaeological rows).  
   - WD remains federation hub / discovery, **not** sole authority.  
   - Store coords / pleiades_id as citation props on the shell (`soft` when non-exclusive).  
   - Meiji / modern packs may prefer GeoNames — card + Domain choose; do not hardcode Pleiades globally.

## What Domain does **not** own (yet)

- Bulk Pleiades / GeoNames ingest into Neo  
- Full modern admin hierarchy for every Place  
- SC-level / claim-level geo (SFA / later harvest)  
- Replacing biblio aboutness (`Rome (Empire)` FAST) with geo Places — biblio stays Librarian strand

## Pipeline slot

```
schema apply     → Place shells + CAPITAL / (optional) territorial edges
bootstrap        → biblio + PeriodO + stamp_place_pleiades (enrich only)
acceptance_view  → sidebar capital includes pleiades_id / lat / long
```

Prefer **one** Domain path via `pipeline.py bootstrap`. `stamp_place_geo.py` is legacy.

## Tools

```python
from pleiades_tools import pleiades_lookup_seed, pleiades_resolve_id, pleiades_resolve_qid
pleiades_lookup_seed(domain_id="roman_republic")
pleiades_resolve_qid("Q220")  # → 423025 + lat/long
```

```powershell
python chrystal_2/bootstrap/seed_federation_registry.py
python chrystal_2/agents/domain/stamp_place_geo.py --domain-id roman_republic --dry-run
python chrystal_2/agents/domain/stamp_place_geo.py --domain-id roman_republic --write
python chrystal_2/agents/domain/acceptance_view.py --domain-id roman_republic
```

## RR acceptance vignette

| Surface | Expectation |
|---------|-------------|
| Sidebar | Capital **Rome** + `pleiades_id` / lat / long |
| Later | Soft territory / broader frame if pack nominates |
| Map pin | Roma `423025` on WD shell `Q220` |

Timeline acceptance stays temporal; geo acceptance is additive, not a second Domain.

## Trap

`CSV/pleiades_roman_republic.csv` and broad geographic crosswalks are **pack dumps**, not bootstrap loads. Same lesson as PeriodO survey CSV: seed tiny; enrich shells; skip noise.
