# Place-Related Nodes: Regroup Summary

**Date:** 2026-02-27  
**Purpose:** Clarify Place, PlaceName, PlaceType, PlaceVersion, Pleiades_Place, and how they relate.

---

## Overview

| Node | Purpose | Loader / Source | Status |
|------|---------|-----------------|--------|
| **Place** | Geographic backbone entity | Pleiades import, Wikidata backbone | ✅ Populated |
| **PlaceName** | Historical name variants | Pleiades import | ✅ Populated |
| **Location** | Coordinates (lat/long) | Pleiades import | ✅ Populated |
| **PlaceType** | Place-type taxonomy (settlement, region, temple, etc.) | build_place_type_hierarchy | ✅ Populated |
| **PlaceVersion** | Time-scoped place (shifting borders) | — | ⏳ Schema only, deferred |
| **Pleiades_Place** | Federation survey node (domain subset) | load_federation_survey | ✅ Populated |

---

## 1. Place

**Core geographic entity.** Two identification schemes:

| Key | Source | Description |
|-----|--------|-------------|
| `pleiades_id` | Pleiades import | ~42k places from pleiades-places CSV |
| `qid` | Wikidata backbone | Countries, regions from P131/P17 |

**Properties:** `label`, `place_type`, `lat`, `long`, `min_date`, `max_date`, `uri`, `authority`, `entity_type`, etc.

**Relationships:**
- `(Place)-[:HAS_NAME]->(PlaceName)`
- `(Place)-[:HAS_LOCATION]->(Location)`
- `(Place)-[:INSTANCE_OF_PLACE_TYPE]->(PlaceType)`
- `(Place)-[:LOCATED_IN]->(Place)` — admin hierarchy (country/region)
- `(Pleiades_Place)-[:ALIGNED_WITH_GEO_BACKBONE]->(Place)` — when pleiades_id matches

**Loaders:**
- `import_pleiades_to_neo4j.py` — Place with pleiades_id
- `build_wikidata_period_geo_backbone.py` — Place with qid (period geo)
- `link_place_admin_hierarchy_geonames.py` — Place with geonames_id (parents) + LOCATED_IN (~2.5k)
- `link_place_admin_hierarchy.py` — Place with qid (parents) + LOCATED_IN

---

## 2. PlaceName

**Historical and alternate names** for a Place (multilingual).

**Properties:** `name_id`, `name_attested`, `language`, etc.

**Relationship:** `(Place)-[:HAS_NAME]->(PlaceName)`

**Loader:** `import_pleiades_to_neo4j.py` (from pleiades_names.csv)

---

## 3. Location

**Coordinates** for a Place (one or more per place).

**Properties:** `location_id`, `lat`, `long`, `precision`, etc.

**Relationship:** `(Place)-[:HAS_LOCATION]->(Location)`

**Loader:** `import_pleiades_to_neo4j.py` (from pleiades_coordinates.csv)

---

## 4. PlaceType

**Taxonomy of place types** (settlement, region, water feature, temple, etc.).

**Properties:** `type_id`, `label`, `parent_type_id`, etc.

**Relationships:**
- `(PlaceType)-[:SUBCLASS_OF]->(PlaceType)` — hierarchy
- `(Place)-[:INSTANCE_OF_PLACE_TYPE]->(PlaceType)` — Pleiades places
- `(PlaceType)-[:HAS_GEO_SEMANTIC_TYPE]->(GeoSemanticType)` — SETTLEMENT, REGION, etc.

**Loader:** `build_place_type_hierarchy.py` — loads PlaceType, PlaceTypeTokenMap, links Place to PlaceType

---

## 5. PlaceVersion

**Time-scoped place instance** for “shifting borders” (e.g. “Gaul (independent)” vs “Gaul (Roman province)”).

**Status:** Schema constraints and indexes exist; **no loader populates it**. Deferred to Phase 3+/4+.

**Intended pattern:**
```
(Place)-[:HAS_VERSION]->(PlaceVersion)-[:VERSION_OF]->(Place)
(Event)-[:TOOK_PLACE_AT]->(PlaceVersion)
```

**Docs:** `Archive/Key Files/2-12-26 Chrystallum Architecture`, `CHRYSTALLUM_PHASE2_INTEGRATION.md`

---

## 6. Pleiades_Place

**Federation survey node** — domain subset (e.g. roman_republic) from survey JSON.

**Properties:** `pleiades_id`, `label`, `uri`, `domain`, `semantic_facet`, `temporal_start`, `temporal_end`, etc.

**Relationships:**
- `(Pleiades_Place)-[:MAPS_TO_FACET]->(CanonicalFacet)`
- `(Pleiades_Place)-[:ALIGNED_WITH_GEO_BACKBONE]->(Place)` — when Place exists with same pleiades_id

**Loader:** `load_federation_survey.py --survey output/nodes/pleiades_roman_republic.json`  
**Post-load:** `link_pleiades_place_to_geo_backbone.py`

---

## Data Flow (Simplified)

```
Pleiades bulk CSV
    │
    ├─► import_pleiades_to_neo4j.py
    │       Place (pleiades_id)
    │       PlaceName (HAS_NAME)
    │       Location (HAS_LOCATION)
    │
    ├─► build_place_type_hierarchy.py
    │       PlaceType taxonomy
    │       (Place)-[:INSTANCE_OF_PLACE_TYPE]->(PlaceType)
    │
    └─► link_place_admin_hierarchy.py
            Place (qid) for parents
            (Place pleiades_id)-[:LOCATED_IN]->(Place qid)

Survey JSON (pleiades_roman_republic.json)
    │
    └─► load_federation_survey.py
            Pleiades_Place
            + link_pleiades_place_to_geo_backbone.py
            (Pleiades_Place)-[:ALIGNED_WITH_GEO_BACKBONE]->(Place)
```

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/backbone/geographic/import_pleiades_to_neo4j.py` | Place, PlaceName, Location |
| `scripts/backbone/geographic/build_place_type_hierarchy.py` | PlaceType, INSTANCE_OF_PLACE_TYPE |
| `scripts/backbone/geographic/link_place_admin_hierarchy.py` | LOCATED_IN hierarchy |
| `scripts/backbone/geographic/link_pleiades_place_to_geo_backbone.py` | Pleiades_Place → Place |
| `scripts/backbone/subject/load_federation_survey.py` | Pleiades_Place |
| `docs/NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md` | Full node reference |
