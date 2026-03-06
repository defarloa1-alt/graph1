// ==========================================================================
// GEOGRAPHIC SPATIAL-TEMPORAL CONSTRAINTS AND INDEXES
// ==========================================================================
// Generated: 2026-03-06
// Purpose: Schema constraints for the temporal Place decomposition model
//   - PlaceName: time-bounded name attestations
//   - PlaceGeometry: time-bounded spatial geometries
//   - GeoPlace: modern admin hierarchy from GeoNames
// Source of truth: Key Files/chrystallum_geographic_constitution.jsx
// ==========================================================================


// ==========================================================================
// PLACE CONSTRAINTS (updated)
// ==========================================================================

CREATE CONSTRAINT place_id_unique IF NOT EXISTS
FOR (p:Place) REQUIRE p.place_id IS UNIQUE;

CREATE INDEX place_pleiades_id IF NOT EXISTS
FOR (p:Place) ON (p.pleiades_id);

CREATE INDEX place_qid IF NOT EXISTS
FOR (p:Place) ON (p.qid);

CREATE INDEX place_min_date IF NOT EXISTS
FOR (p:Place) ON (p.min_date);

CREATE INDEX place_max_date IF NOT EXISTS
FOR (p:Place) ON (p.max_date);


// ==========================================================================
// PLACE NAME CONSTRAINTS
// ==========================================================================

CREATE CONSTRAINT place_name_id_unique IF NOT EXISTS
FOR (pn:PlaceName) REQUIRE pn.name_id IS UNIQUE;

CREATE INDEX place_name_string IF NOT EXISTS
FOR (pn:PlaceName) ON (pn.name_string);

CREATE INDEX place_name_language IF NOT EXISTS
FOR (pn:PlaceName) ON (pn.language);

CREATE INDEX place_name_start_year IF NOT EXISTS
FOR (pn:PlaceName) ON (pn.start_year);

CREATE INDEX place_name_end_year IF NOT EXISTS
FOR (pn:PlaceName) ON (pn.end_year);

CREATE INDEX place_name_source IF NOT EXISTS
FOR (pn:PlaceName) ON (pn.source);


// ==========================================================================
// PLACE GEOMETRY CONSTRAINTS
// ==========================================================================

CREATE CONSTRAINT place_geometry_id_unique IF NOT EXISTS
FOR (pg:PlaceGeometry) REQUIRE pg.geometry_id IS UNIQUE;

CREATE INDEX place_geometry_type IF NOT EXISTS
FOR (pg:PlaceGeometry) ON (pg.geometry_type);

CREATE INDEX place_geometry_start_year IF NOT EXISTS
FOR (pg:PlaceGeometry) ON (pg.start_year);

CREATE INDEX place_geometry_end_year IF NOT EXISTS
FOR (pg:PlaceGeometry) ON (pg.end_year);

CREATE INDEX place_geometry_precision IF NOT EXISTS
FOR (pg:PlaceGeometry) ON (pg.precision);

CREATE INDEX place_geometry_source IF NOT EXISTS
FOR (pg:PlaceGeometry) ON (pg.source);

// Neo4j spatial point index (uncomment after migration creates point properties)
// CREATE POINT INDEX place_geometry_point IF NOT EXISTS
// FOR (pg:PlaceGeometry) ON (pg.location);


// ==========================================================================
// GEO PLACE CONSTRAINTS (modern admin hierarchy)
// ==========================================================================

CREATE CONSTRAINT geo_place_geonames_id_unique IF NOT EXISTS
FOR (gp:GeoPlace) REQUIRE gp.geonames_id IS UNIQUE;

CREATE INDEX geo_place_feature_code IF NOT EXISTS
FOR (gp:GeoPlace) ON (gp.feature_code);

CREATE INDEX geo_place_country_code IF NOT EXISTS
FOR (gp:GeoPlace) ON (gp.country_code);

CREATE INDEX geo_place_label IF NOT EXISTS
FOR (gp:GeoPlace) ON (gp.label);

CREATE INDEX geo_place_qid IF NOT EXISTS
FOR (gp:GeoPlace) ON (gp.qid);

// Neo4j spatial point index (uncomment after GeoNames load)
// CREATE POINT INDEX geo_place_point IF NOT EXISTS
// FOR (gp:GeoPlace) ON (gp.location);
