# Geographic Backbone: Country/Region Mapping Status

**Date:** 2026-02-27  
**Source:** Key Files, md/Architecture

---

## What the Architecture Specifies

### Place hierarchy (from arch docs)

- **`(:Place)-[:LOCATED_IN]->(:Place)`** — child place contained in parent (city → region → country)
- **`(:Period)-[:LOCATED_IN]->(:Place)`** — period geographic scope
- **Wikidata mapping:** P131 (admin entity), P17 (country), P276 (location) → `LOCATED_IN`

### Place-type taxonomy (GEO_SCHEMA_OUTLINE_2026-02-18.md)

- `SETTLEMENT`, `REGION`, `WATER_FEATURE`, `LAND_FEATURE`, `BUILT_FEATURE`, etc.
- `(:Place)-[:HAS_PLACE_TYPE]->(:PlaceType)` — implemented via `build_place_type_hierarchy.py`

---

## What Exists Today

| Component | Status | Script / Source |
|-----------|--------|----------------|
| **Place nodes** | ✅ | `import_pleiades_to_neo4j.py` — ~42k from Pleiades |
| **PlaceType hierarchy** | ✅ | `build_place_type_hierarchy.py` — settlement, region, temple, etc. |
| **Pleiades_Place → Place link** | ✅ | `link_pleiades_place_to_geo_backbone.py` |
| **Place LOCATED_IN Place** (hierarchy) | ⚠️ Partial | `link_place_admin_hierarchy.py`, `link_place_admin_hierarchy_geonames.py` |
| **Pleiades → country/region** | ✅ ~2.6k | GeoNames admin codes + Wikidata P131/P17 |

---

## Gap: Pleiades Place Hierarchy

Pleiades places are **flat** in the import. The architecture expects:

```
(city:Place)-[:LOCATED_IN]->(region:Place)-[:LOCATED_IN]->(country:Place)
```

**Available data for hierarchy:**

1. **CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv** (~4,555 rows)
   - `pleiades_id`, `geonames_id`, `geonames_feature_code` (ADM1, ADM2, ADM3, ADM4, PPLA, etc.)
   - `wikidata_qid` when triangulated
   - GeoNames feature codes imply admin level (ADM1=region, ADM2=state, etc.)

2. **GeoNames** — has `countryCode`, `admin1`, `admin2`, `admin3` in the dump
   - `build_pleiades_geonames_crosswalk.py` produces the crosswalk
   - GeoNames hierarchy can be resolved via `allCountries.txt` (parent_id, admin codes)

3. **Wikidata** — P131/P17 give containment for places with QIDs
   - `build_wikidata_period_geo_backbone.py` does this for period-related places only

---

## Implemented (2026-02-27)

1. **`link_place_admin_hierarchy.py`** — Links Place (pleiades_id) to parent Place (qid) via Wikidata P131/P17
   - Input: crosswalk + optional `pleiades_wikidata_p3813.csv`
   - Creates parent Place nodes by qid, `(Place)-[:LOCATED_IN]->(Place)`

2. **`link_place_admin_hierarchy_geonames.py`** — Links Place via GeoNames admin codes
   - Uses allCountries.txt (country_code, admin1-4) to resolve parent
   - Creates Place nodes with `geonames_id`, `(Place)-[:LOCATED_IN]->(Place)`
   - **~2.5k+ places** linked (main expansion path)

3. **`fetch_pleiades_wikidata_p3813.py`** — Enriches with Wikidata QIDs via P3813 (Pleiades ID)

## Recommended Run Order

**Quick fix for sparse Place attributes:**

```bash
# Run full pipeline (enrich + link + hierarchy)
scripts/run_place_enrichment_pipeline.bat   # Windows
./scripts/run_place_enrichment_pipeline.sh # Unix
```

**Manual steps:**

1. `enrich_places_from_crosswalk.py` — add qid, geonames_id, tgn_id from crosswalk
2. `link_pleiades_place_to_geo_backbone.py` — link Pleiades_Place → Place
3. `link_place_admin_hierarchy_geonames.py` — primary hierarchy coverage
4. `link_place_admin_hierarchy.py --pleiades-wikidata-csv ...` — Wikidata supplement

---

## Key Files

- `scripts/backbone/geographic/enrich_places_from_crosswalk.py` — Enrich Place with qid, geonames_id, tgn_id
- `scripts/run_place_enrichment_pipeline.bat` / `.sh` — One-shot pipeline
- `scripts/backbone/geographic/link_place_admin_hierarchy_geonames.py` — Place hierarchy via GeoNames (primary)
- `scripts/backbone/geographic/link_place_admin_hierarchy.py` — Place hierarchy via Wikidata
- `scripts/backbone/geographic/fetch_pleiades_wikidata_p3813.py` — P3813 enrichment
- `CSV/geographic/pleiades_geonames_wikidata_tgn_crosswalk_v1.csv`
- `CSV/geographic/pleiades_wikidata_p3813.csv` — P3813 fetch output (optional input for link script)
- `scripts/backbone/geographic/build_wikidata_period_geo_backbone.py`
- `scripts/backbone/geographic/build_pleiades_geonames_crosswalk.py`
- `md/Architecture/TEMPORAL_GEO_BACKBONE_MODEL_2026-02-18.md`
