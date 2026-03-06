// ==========================================================================
// GEOGRAPHIC SPATIAL-TEMPORAL MIGRATION
// ==========================================================================
// Date: 2026-03-06
// Source of truth: Key Files/chrystallum_geographic_constitution.jsx
//
// PREREQUISITES:
//   1. Run geographic_spatial_temporal_constraints.cypher first
//   2. Back up the database before running
//   3. Run steps in order — each depends on the previous
//
// WHAT THIS DOES:
//   Step 1:  Create PlaceGeometry nodes from existing Place.lat/long/bbox
//   Step 1b: Create PlaceGeometry for bbox-only Places
//   Step 2:  Create PlaceName nodes from existing Place.label
//   Step 3:  Link Place to PlaceType via HAS_TYPE
//   Step 4:  Re-label GeoNames backbone Place nodes as :GeoPlace
//   Step 5:  Tag Wikidata backbone stubs
//   Step 6:  Convert LOCATED_IN to LOCATED_IN_MODERN where target is GeoPlace
//
// WHAT THIS DOES NOT DO (requires re-ingestion from source APIs):
//   - Decompose into multiple temporal name attestations (needs Pleiades names[])
//   - Create polygon/polyline geometries (needs Pleiades locations[] GeoJSON)
//   - Fetch Wikidata P3896 geoshapes for region boundaries
//   - Build full GeoNames admin hierarchy (needs GeoNames dump)
//
// After migration, run: geographic_sys_registration.cypher
// ==========================================================================


// ==========================================================================
// STEP 1: Create PlaceGeometry from existing Place coordinates
// ==========================================================================
// ~34,331 nodes created (one per Place with lat/long)

CALL apoc.periodic.iterate(
  "MATCH (p:Place)
   WHERE p.lat IS NOT NULL AND p.long IS NOT NULL
   RETURN p",
  "CREATE (pg:PlaceGeometry {
     geometry_id: 'geo_' + p.place_id + '_0',
     geometry_type: 'point',
     latitude: p.lat,
     longitude: p.long,
     start_year: p.min_date,
     end_year: p.max_date,
     precision: CASE
       WHEN p.place_type = 'unlocated' THEN 'unlocated'
       ELSE 'approximate'
     END,
     source: 'pleiades',
     source_id: p.pleiades_id
   })
   CREATE (p)-[:HAS_GEOMETRY]->(pg)",
  {batchSize: 500, parallel: false}
);


// ==========================================================================
// STEP 1b: Create PlaceGeometry for bbox-only Places (no centroid)
// ==========================================================================
// ~7,553 Places have bbox but no lat/long
// Parse the comma-separated bbox string and compute centroid

CALL apoc.periodic.iterate(
  "MATCH (p:Place)
   WHERE p.lat IS NULL AND p.bbox IS NOT NULL
   RETURN p",
  "WITH p,
     split(p.bbox, ', ') AS parts
   WHERE size(parts) = 4
   WITH p,
     toFloat(parts[0]) AS minLon,
     toFloat(parts[1]) AS minLat,
     toFloat(parts[2]) AS maxLon,
     toFloat(parts[3]) AS maxLat
   CREATE (pg:PlaceGeometry {
     geometry_id: 'geo_' + p.place_id + '_0',
     geometry_type: CASE
       WHEN minLon = maxLon AND minLat = maxLat THEN 'point'
       ELSE 'bbox'
     END,
     latitude: (minLat + maxLat) / 2.0,
     longitude: (minLon + maxLon) / 2.0,
     bbox: [minLon, minLat, maxLon, maxLat],
     start_year: p.min_date,
     end_year: p.max_date,
     precision: 'rough',
     source: 'pleiades',
     source_id: p.pleiades_id
   })
   CREATE (p)-[:HAS_GEOMETRY]->(pg)",
  {batchSize: 500, parallel: false}
);


// ==========================================================================
// STEP 2: Create PlaceName from existing Place.label
// ==========================================================================
// ~44,000 nodes created (one per Place)
// This is a placeholder — real temporal names require Pleiades re-ingestion

CALL apoc.periodic.iterate(
  "MATCH (p:Place)
   WHERE p.label IS NOT NULL
   RETURN p",
  "CREATE (pn:PlaceName {
     name_id: 'pname_' + p.place_id + '_0',
     name_string: p.label,
     start_year: p.min_date,
     end_year: p.max_date,
     source: CASE
       WHEN p.pleiades_id IS NOT NULL THEN 'pleiades'
       WHEN p.node_type = 'geonames_place_backbone' THEN 'geonames'
       WHEN p.node_type = 'wikidata_place_backbone' THEN 'wikidata'
       ELSE 'manual'
     END,
     is_primary: true
   })
   CREATE (p)-[:HAS_NAME]->(pn)",
  {batchSize: 500, parallel: false}
);


// ==========================================================================
// STEP 3: Link Place to PlaceType via HAS_TYPE
// ==========================================================================
// Splits compound place_type strings on ', ' and links to each PlaceType

CALL apoc.periodic.iterate(
  "MATCH (p:Place)
   WHERE p.place_type IS NOT NULL
   RETURN p",
  "WITH p, split(p.place_type, ', ') AS types
   UNWIND types AS typeName
   WITH p, trim(typeName) AS typeName
   WHERE typeName <> ''
   MERGE (pt:PlaceType {name: typeName})
   MERGE (p)-[:HAS_TYPE]->(pt)",
  {batchSize: 500, parallel: false}
);


// ==========================================================================
// STEP 4: Re-label GeoNames backbone nodes as :GeoPlace
// ==========================================================================
// ~1,743 nodes. Adds GeoPlace label, sets required properties.

MATCH (p:Place)
WHERE p.node_type = 'geonames_place_backbone'
SET p:GeoPlace
SET p.feature_code = coalesce(p.feature_code, 'UNKNOWN')
SET p.country_code = coalesce(p.country_code, 'XX')
RETURN count(p) AS geonames_migrated;


// ==========================================================================
// STEP 5: Tag Wikidata backbone Place nodes
// ==========================================================================
// ~331 nodes. Tags for future Wikidata enrichment.

MATCH (p:Place)
WHERE p.node_type = 'wikidata_place_backbone' AND p.qid IS NOT NULL
SET p:WikidataPlaceStub
RETURN count(p) AS wikidata_stubs_tagged;


// ==========================================================================
// STEP 6: Convert LOCATED_IN to LOCATED_IN_MODERN for GeoPlace targets
// ==========================================================================

MATCH (p:Place)-[r:LOCATED_IN]->(gp:GeoPlace)
CREATE (p)-[:LOCATED_IN_MODERN]->(gp)
DELETE r
RETURN count(r) AS converted_to_modern;


// ==========================================================================
// VERIFICATION QUERIES (uncomment and run manually)
// ==========================================================================

// MATCH (pg:PlaceGeometry) RETURN count(pg) AS geometry_count;
// MATCH (pn:PlaceName) RETURN count(pn) AS name_count;
// MATCH (gp:GeoPlace) RETURN count(gp) AS geo_place_count;
// MATCH (p:Place)-[:HAS_TYPE]->(pt:PlaceType) RETURN pt.name, count(p) ORDER BY count(p) DESC LIMIT 20;
// MATCH (p:Place {place_id: 'plc_265880'})-[r]->(sub) RETURN p.label, type(r), labels(sub), sub LIMIT 10;
