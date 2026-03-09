# Federation to GeoNames and Wikidata — Happy Path

**Geo backbone** = Pleiades Place with `place_scope = 'v1_core'`. Federation enriches these with GeoNames IDs, Wikidata QIDs, admin hierarchy, and geo data.

---

## Prerequisites

| Requirement | Source | Notes |
|-------------|--------|-------|
| Place nodes | `import_pleiades_to_neo4j.py` | Run first |
| place_scope tagged | `tag_place_scope.py` | v1_core vs deferred |
| Crosswalk | `CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv` | From build scripts below |
| GeoNames dump | `Geographic/geonames_allCountries.zip` | ~400 MB; auto-download or manual |

---

## Happy Path (Order)

### 1. Build crosswalk (if missing)

```bash
# Pleiades → GeoNames (from pleiades_plus.csv)
python scripts/backbone/geographic/build_pleiades_geonames_crosswalk.py

# GeoNames → Wikidata bridge; merge into federated crosswalk
python scripts/backbone/geographic/build_geonames_wikidata_bridge.py
```

**Output:** `CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv`

### 2. Enrich Place from crosswalk

```bash
python scripts/backbone/geographic/enrich_places_from_crosswalk.py
```

**Effect:** Sets `Place.geonames_id`, `Place.qid`, `Place.tgn_id` from crosswalk.

### 3. GeoNames federation — admin hierarchy

```bash
python scripts/backbone/geographic/link_place_admin_hierarchy_geonames.py
```

**Effect:** Creates Place(geonames_id) parent nodes; `(Place pleiades_id)-[:LOCATED_IN]->(Place geonames_id)`. Requires `geonames_allCountries.zip`.

### 4. Wikidata federation — admin hierarchy

```bash
python scripts/backbone/geographic/link_place_admin_hierarchy.py
```

**Effect:** Fetches P131/P17 from Wikidata; creates parent Place(qid) nodes; `(Place pleiades_id)-[:LOCATED_IN]->(Place qid)`.

### 5. Wikidata federation — geo enrichment

```bash
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py --dry-run   # preview
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py
```

**Effect:** P625 (coords), P3896 (geoshape), P131/P17, labels. Fills lat/long when missing; adds geoshape_commons, country_qid, LOCATED_IN edges.

### 6. Link Pleiades_Place to backbone

```bash
python scripts/backbone/geographic/link_pleiades_place_to_geo_backbone.py
```

**Effect:** `(Pleiades_Place)-[:ALIGNED_WITH_GEO_BACKBONE]->(Place)` by pleiades_id.

---

## One-liner pipeline

```bash
# From project root
python scripts/backbone/geographic/enrich_places_from_crosswalk.py && \
python scripts/backbone/geographic/link_place_admin_hierarchy_geonames.py && \
python scripts/backbone/geographic/link_place_admin_hierarchy.py && \
python scripts/backbone/geographic/enrich_places_from_wikidata_geo.py && \
python scripts/backbone/geographic/link_pleiades_place_to_geo_backbone.py
```

Or use `run_place_enrichment_pipeline.sh` (covers steps 1, 2, 6; add 4 and 5 manually if desired).

---

## Unhappy Path — When to Discuss

| Failure | Likely cause | Discuss |
|---------|--------------|---------|
| Crosswalk missing | build_pleiades_geonames_crosswalk or build_geonames_wikidata_bridge not run | Run build scripts; check pleiades_plus.csv exists |
| enrich_places_from_crosswalk: no rows | Crosswalk empty or wrong path | Verify crosswalk has pleiades_id, geonames_id, wikidata_qid columns |
| link_place_admin_hierarchy_geonames: no geonames | geonames_allCountries.zip missing | Download to Geographic/; script can auto-download |
| link_place_admin_hierarchy: API errors | Wikidata rate limit or network | Retry with --max-places; increase pause |
| enrich_places_from_wikidata_geo: timeout | 2.8k+ QIDs, many API calls | Use --limit 500 for testing; run in batches |
| Place has qid but no geonames_id | Crosswalk row has wikidata match, no geonames | Expected for some places; GeoNames coverage is partial |
| Place has geonames_id but no qid | Crosswalk row has geonames, no wikidata | Expected; enrich_places_from_wikidata_geo won't help (needs qid) |

---

## Verification

```cypher
// Places with full federation chain
MATCH (p:Place)
WHERE p.place_scope = 'v1_core'
  AND p.pleiades_id IS NOT NULL
  AND p.geonames_id IS NOT NULL
  AND p.qid IS NOT NULL
RETURN count(p) AS fully_federated

// Places with LOCATED_IN (admin hierarchy)
MATCH (p:Place)-[:LOCATED_IN]->(parent:Place)
WHERE p.place_scope = 'v1_core'
RETURN count(DISTINCT p) AS with_admin_parent
```
