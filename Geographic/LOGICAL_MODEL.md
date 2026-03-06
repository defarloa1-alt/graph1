# Place Logical Model

**Purpose:** Logical model of geographic entities in Chrystallum.  
**Source:** `import_pleiades_to_neo4j.py`, `ARCHITECTURE_ONTOLOGY.md`, `link_pleiades_place_to_geo_backbone.py`, `link_place_admin_hierarchy.py`

---

## Current Implementation (What You Have)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         GEOGRAPHIC LAYER                                          │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┐         ALIGNED_WITH_GEO_BACKBONE         ┌──────────────────┐
  │  Pleiades_Place   │ ───────────────────────────────────────► │      Place        │
  │  (federation)     │         (link by pleiades_id)             │  (geo backbone)   │
  └──────────────────┘                                           └────────┬─────────┘
        │                                                                 │
        │ MAPS_TO_FACET                                                   │
        ▼                                                                 │
  ┌──────────────┐                                                        │
  │ CanonicalFacet│                                                        │
  └──────────────┘                                                        │
                                                                         │
         ┌────────────────────────────────────────────────────────────────┼────────────────────┐
         │                                                                │                    │
         ▼                                                                ▼                    ▼
  ┌──────────────────┐                                           ┌──────────────┐      ┌──────────────┐
  │    PlaceName      │                                           │   Location   │      │    Place     │
  │  (name variants)  │                                           │ (coordinates)│      │  (parent)    │
  └──────────────────┘                                           └──────────────┘      └──────────────┘
         ▲                                                                ▲                    ▲
         │ HAS_NAME                                                       │ HAS_LOCATION       │ LOCATED_IN
         │                                                                │                    │
  ┌──────┴────────────────────────────────────────────────────────────────┴────────────────────┴──────┐
  │                                                    Place                                              │
  │  pleiades_id | geonames_id | qid (PK by source); label, lat, long, place_type, min_date, max_date      │
  │  geonames_id (from crosswalk); authority: Pleiades | GeoNames | wikidata                            │
  └─────────────────────────────────────────────────────────────────────────────────────────────────────┘
         │
         │ LOCATED_IN (admin hierarchy)
         ▼
  ┌──────────────────┐     ┌──────────────────┐
  │ Place (geonames_id)│     │  Place (qid)      │  ← GeoNames or Wikidata parents
  └──────────────────┘     └──────────────────┘
```

---

## Node Definitions

| Node               | Purpose                                             | Key Properties                                                                              | Created By                                                                                                                            |
| ------------------ | --------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Place**          | Stable geographic identity (canonical geo backbone) | `pleiades_id` or `geonames_id` or `qid` (PK by source); `label`, `lat`, `long`, `place_type`, `min_date`, `max_date`; `geonames_id` (crosswalk); `authority`: Pleiades \| GeoNames \| wikidata | `import_pleiades_to_neo4j.py`, `link_place_admin_hierarchy_geonames.py`, `build_wikidata_period_geo_backbone.py`, `link_place_admin_hierarchy.py`, `enrich_places_from_crosswalk.py` |
| **PlaceName**      | Attested name in a language                         | `name_id`, `name_attested`, `language`, `name_type`, `romanized`                            | `import_pleiades_to_neo4j.py`                                                                                                         |
| **Location**       | Coordinate point (alternative geometry)             | `location_id`, `lat`, `long`, `title`, `location_type`, `precision`                         | `import_pleiades_to_neo4j.py`                                                                                                         |
| **Pleiades_Place** | Federation survey node (subject discovery)          | `pleiades_id`, `label`, `uri`, `domain`, `semantic_facet`, `temporal_start`, `temporal_end` | `load_federation_survey.py`                                                                                                           |
| **PlaceType**      | Place type taxonomy                                 | `type_id`, hierarchy                                                                        | `build_place_type_hierarchy.py`                                                                                                       |

---

## Relationships

| Relationship | From → To | Purpose |
|--------------|-----------|---------|
| **HAS_NAME** | Place → PlaceName | Place has attested name variant (e.g. Latin, Greek) |
| **HAS_LOCATION** | Place → Location | Place has coordinate representation (Pleiades can have multiple locations per place) |
| **LOCATED_IN** | Place → Place | Administrative containment. Child (pleiades_id) → parent (geonames_id or qid). Sources: GeoNames (`link_place_admin_hierarchy_geonames.py`) or Wikidata P131/P17 (`link_place_admin_hierarchy.py`). |
| **ALIGNED_WITH_GEO_BACKBONE** | Pleiades_Place → Place | Federation survey node links to canonical Place by `pleiades_id` |

---

## Data Flow

```
Pleiades CSV (download_pleiades_bulk.py)
    │
    ├── pleiades_places.csv ──────► Place (import_pleiades_to_neo4j)
    ├── pleiades_names.csv ───────► PlaceName + HAS_NAME
    └── pleiades_coordinates.csv ─► Location + HAS_LOCATION

pleiades_plus.csv (ryanfb/pleiades-plus)
    └── build_pleiades_geonames_crosswalk.py ─► pleiades_geonames_crosswalk_v1.csv

geonames_allCountries.zip + crosswalk
    └── build_geonames_wikidata_bridge.py ─► pleiades_geonames_wikidata_tgn_crosswalk_v1.csv

enrich_places_from_crosswalk.py
    └── Place.geonames_id, Place.wikidata_qid, Place.tgn_id (from crosswalk)

link_place_admin_hierarchy_geonames.py (crosswalk + geonames_allCountries)
    └── Place(geonames_id) parent nodes; (Place pleiades_id)-[:LOCATED_IN]->(Place geonames_id)

load_federation_survey (pleiades_roman_republic.json)
    └── Pleiades_Place

link_pleiades_place_to_geo_backbone.py
    └── Pleiades_Place -[:ALIGNED_WITH_GEO_BACKBONE]-> Place

link_place_admin_hierarchy.py (crosswalk + Wikidata P131/P17)
    └── Place -[:LOCATED_IN]-> Place (by qid)
```

---

## Proposed: Property-based multilingual (Option 2)

**Preferred alternative to PlaceName nodes.** Store multilingual labels as properties on Place, enriched from BabelNet:

```cypher
(Place {
  pleiades_id: "423025",
  label: "Rome",
  babelnet_id: "bn:00068294n",
  alt_labels: {en: ["Rome"], la: ["Roma"], grc: ["Ῥώμη"], fr: ["Rome"]}
})
```

- **No PlaceName nodes** — all names are properties; `same_as` is implicit.
- **BabelNet** — source for multilingual lexicalizations; enrich once, cache on Place.
- **Migration:** Enrich Place from BabelNet (or Wikidata P2581); optionally fold existing PlaceName data into `alt_labels`; deprecate PlaceName.

See `Key Files/Appendices/02_Authority_Integration/Temporal_Authority_Alignment.md` Appendix S (BabelNet integration).

---

## Architecture vs Implementation Gap

**Architecture (ARCHITECTURE_ONTOLOGY §3.1.2):** Defines a three-tier model:

1. **Place** — stable identity
2. **PlaceVersion** — time-scoped instantiation (e.g. "Antioch (Roman Period)")
3. **PlaceName** — attached to PlaceVersion
4. **Geometry** — attached to PlaceVersion via HAS_GEOMETRY

**Current implementation:** Place links directly to PlaceName and Location. PlaceVersion and Geometry are **planned** (0 count). See `docs/architecture/PLACE_MODEL_ANALYSIS.md` for the migration gap.

---

## Example Queries

```cypher
// Place with names and coordinates
MATCH (p:Place {pleiades_id: '423025'})
OPTIONAL MATCH (p)-[:HAS_NAME]->(n:PlaceName)
OPTIONAL MATCH (p)-[:HAS_LOCATION]->(l:Location)
RETURN p, n, l

// Federation alignment
MATCH (pp:Pleiades_Place)-[:ALIGNED_WITH_GEO_BACKBONE]->(p:Place)
WHERE pp.pleiades_id = p.pleiades_id
RETURN pp, p

// Admin hierarchy (Pleiades → GeoNames or Wikidata parents)
MATCH path = (child:Place)-[:LOCATED_IN*1..3]->(top:Place)
WHERE child.pleiades_id = '423025'
RETURN path

// Places with GeoNames link (from crosswalk)
MATCH (p:Place) WHERE p.geonames_id IS NOT NULL
RETURN p.pleiades_id, p.label, p.geonames_id
LIMIT 10
```
