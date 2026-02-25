# Complete List of Federations Available to Chrystallum

**Sources:** META_MODEL_SELF_DESCRIBING_GRAPH.md, prosopographic_federation_design.md, load_federation_metadata.py, wikidata_backlink_harvest.py

---

## Summary

| # | Federation | Type | Mode | Wikidata PID | Coverage | Status |
|---|------------|------|------|---------------|----------|--------|
| 1 | Wikidata | universal | hub_api | — | — | Hub; discovery & disambiguation |
| 2 | Pleiades | geographic | local | P1584 | 41,993 places | Scoping + Phase 2 |
| 3 | PeriodO | temporal | local | — | 8,959 periods | Local CSV |
| 4 | LCSH | conceptual | local | P244 (LC) | — | Subject backbone |
| 5 | FAST | topical | local | — | — | Subject backbone |
| 6 | LCC | classification | local | — | — | Subject backbone |
| 7 | MARC | bibliographic | local | — | — | MARC records |
| 8 | GeoNames | geographic | hybrid | P1566 | — | Crosswalk + API |
| 9 | BabelNet | linguistic | api | — | — | External API |
| 10 | WorldCat | bibliographic | api | P10832 | — | External API |
| 11 | Trismegistos | prosopographic | api | P1696 | 575,000+ persons | Scoping + Phase 2 |
| 12 | LGPN | prosopographic | api | P1838 | 400,000+ Greeks | Scoping + Phase 2 |
| 13 | SNAP:DRGN | prosopographic | standard | — | 0 (standard only) | Interchange format, not live |

**Total: 13 federations**

---

## Scoping (Phase 1)

The harvester uses these Wikidata external-id properties for scoping:

| Property | Federation | Scoping signal |
|----------|-------------|----------------|
| P1696 | Trismegistos | temporal_scoped (0.95) |
| P1838 | LGPN | temporal_scoped (0.95) |
| P1584 | Pleiades | temporal_scoped (0.95) |
| P214 | VIAF | domain_scoped (0.85) when + domain proximity |

**Note:** VIAF is not a Chrystallum federation node; it is a Wikidata property (P214) that links to the Virtual International Authority File. Entities with VIAF + domain backlink get domain_scoped.

---

## Phase 2 Interrogation Targets

| Federation | Wikidata PID | API / Source |
|------------|--------------|--------------|
| Trismegistos | P1696 | https://www.trismegistos.org/dataservices/per/index.php?id={id}&format=json |
| LGPN | P1838 | http://www.lgpn.ox.ac.uk/id/{volume}-{id} |
| Pleiades | P1584 | pleiades_places.csv (local) + API |

---

## Meta-Model (Neo4j Graph)

The self-describing meta-model has **10 Federation nodes** (pre–prosopographic additions):

- Wikidata, Pleiades, PeriodO, LCSH, FAST, LCC, MARC, GeoNames, BabelNet, WorldCat

Trismegistos and LGPN are documented but may not yet be in the graph. SNAP:DRGN is a standard, not a data source.

---

## load_federation_metadata.py (6 AuthoritySources)

- Pleiades, PeriodO, LCSH, FAST, LCC, Wikidata

---

## Other Wikidata External-ID Properties (Harvester Captures All)

The harvester's `_extract_external_ids()` captures every external-id typed property on an entity. Common ones beyond the scoping set:

| PID | Authority |
|-----|-----------|
| P214 | VIAF |
| P268 | BnF |
| P227 | GND |
| P244 | LC (LCSH) |
| P213 | ISNI |
| P1566 | GeoNames |
| P2950 | Nomisma |
| P4212 | PACTOLS |
| P8313 | Trismegistos (alternate) |

These are stored in `entity.external_ids` for Phase 2 lookup; only P1696, P1838, P1584, P214 drive scoping.
