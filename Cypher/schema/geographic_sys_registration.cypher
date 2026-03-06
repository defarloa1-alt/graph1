// ==========================================================================
// GEOGRAPHIC SPATIAL-TEMPORAL SYS_ NODE REGISTRATION
// ==========================================================================
// Date: 2026-03-06
// Purpose: Register geographic node types, relationships, and federation
//   sources as SYS_ metadata nodes in Neo4j. This makes the graph
//   self-describing — agents discover the schema by querying SYS_ nodes.
//
// Source of truth: Key Files/chrystallum_geographic_constitution.jsx
// Run: After migration (geographic_spatial_temporal_migration.cypher)
// ==========================================================================


// ==========================================================================
// REGISTER NEW NODE TYPES
// ==========================================================================

MERGE (nt1:SYS_NodeType {name: 'PlaceName'})
SET nt1.description = 'Time-bounded name attestation for a Place. A Place may have multiple names across time and language (Byzantium, Constantinople, Istanbul).',
    nt1.system = true,
    nt1.domain = 'geographic',
    nt1.status = 'operational',
    nt1.required_properties = ['name_id', 'name_string', 'source'],
    nt1.optional_properties = ['attested_form', 'romanized_form', 'language', 'start_year', 'end_year', 'name_type', 'is_primary'],
    nt1.source_data = 'Pleiades names[] (each with start_date, end_date, romanized, attested, language). Wikidata labels/aliases.',
    nt1.created_at = datetime();

MERGE (nt2:SYS_NodeType {name: 'PlaceGeometry'})
SET nt2.description = 'Time-bounded spatial geometry for a Place. Supports point, bbox, polygon, polyline, multipolygon. GeoJSON property consumed directly by map renderers.',
    nt2.system = true,
    nt2.domain = 'geographic',
    nt2.status = 'operational',
    nt2.required_properties = ['geometry_id', 'geometry_type', 'source'],
    nt2.optional_properties = ['latitude', 'longitude', 'bbox', 'geojson', 'start_year', 'end_year', 'precision', 'accuracy_radius_m'],
    nt2.source_data = 'Pleiades locations[] (each with geometry, start_date, end_date, accuracy). Wikidata P625 (point), P3896 (geoshape polygon).',
    nt2.created_at = datetime();

MERGE (nt3:SYS_NodeType {name: 'GeoPlace'})
SET nt3.description = 'Modern geographic entity from GeoNames admin hierarchy. NOT a historical place. Provides containment queries (all ancient sites in modern Turkey). Connected via ADMIN_CHILD_OF to form admin tree.',
    nt3.system = true,
    nt3.domain = 'geographic',
    nt3.status = 'operational',
    nt3.required_properties = ['geonames_id', 'label', 'feature_code', 'country_code'],
    nt3.optional_properties = ['latitude', 'longitude', 'feature_class', 'admin1_code', 'admin2_code', 'population', 'boundary_geojson', 'qid'],
    nt3.created_at = datetime();


// ==========================================================================
// UPDATE EXISTING PLACE NODE TYPE
// ==========================================================================

MATCH (nt:SYS_NodeType {name: 'Place'})
SET nt.description = 'Geographic identity anchor. Persists through time with changing names and geometries. Has temporal sub-nodes: PlaceName (names via HAS_NAME), PlaceGeometry (shapes via HAS_GEOMETRY). Coordinates and names belong on sub-nodes, not Place itself.',
    nt.domain = 'geographic',
    nt.deprecated_properties = ['lat', 'long', 'bbox', 'place_type'],
    nt.deprecation_note = 'lat/long/bbox moved to PlaceGeometry nodes. place_type moved to HAS_TYPE relationship to PlaceType nodes.',
    nt.updated_at = datetime();


// ==========================================================================
// REGISTER NEW RELATIONSHIP TYPES
// ==========================================================================

MERGE (rt1:SYS_RelationshipType {name: 'HAS_NAME'})
SET rt1.source_label = 'Place', rt1.target_label = 'PlaceName',
    rt1.description = 'Place has a time-bounded name attestation. Multiple names per place (temporal, multilingual).',
    rt1.category = 'geographic', rt1.temporal = true,
    rt1.kernel_category = 'geographic',
    rt1.cardinality = 'one-to-many';

MERGE (rt2:SYS_RelationshipType {name: 'HAS_GEOMETRY'})
SET rt2.source_label = 'Place', rt2.target_label = 'PlaceGeometry',
    rt2.description = 'Place has a time-bounded spatial geometry. Multiple geometries per place (expanding footprint, shifting boundaries).',
    rt2.category = 'geographic', rt2.temporal = true,
    rt2.kernel_category = 'geographic',
    rt2.cardinality = 'one-to-many';

MERGE (rt3:SYS_RelationshipType {name: 'HAS_TYPE'})
SET rt3.source_label = 'Place', rt3.target_label = 'PlaceType',
    rt3.description = 'Place is classified as this type. Normalized from compound place_type strings.',
    rt3.category = 'geographic', rt3.temporal = false,
    rt3.kernel_category = 'geographic',
    rt3.cardinality = 'many-to-many';

MERGE (rt4:SYS_RelationshipType {name: 'LOCATED_IN_MODERN'})
SET rt4.source_label = 'Place', rt4.target_label = 'GeoPlace',
    rt4.description = 'Bridge from ancient Place to modern admin hierarchy. Enables "all ancient sites in modern Turkey".',
    rt4.category = 'geographic', rt4.temporal = false,
    rt4.kernel_category = 'geographic',
    rt4.cardinality = 'many-to-one';

MERGE (rt5:SYS_RelationshipType {name: 'ADMIN_CHILD_OF'})
SET rt5.source_label = 'GeoPlace', rt5.target_label = 'GeoPlace',
    rt5.description = 'GeoNames admin hierarchy (city in province in country). Traversable via variable-length paths.',
    rt5.category = 'geographic', rt5.temporal = false,
    rt5.kernel_category = 'geographic',
    rt5.cardinality = 'many-to-one';

MERGE (rt6:SYS_RelationshipType {name: 'CONNECTED_TO'})
SET rt6.source_label = 'Place', rt6.target_label = 'Place',
    rt6.description = 'Pleiades connection between places (road links, river connections, port relationships).',
    rt6.category = 'geographic', rt6.temporal = false,
    rt6.kernel_category = 'geographic',
    rt6.cardinality = 'many-to-many';

MERGE (rt7:SYS_RelationshipType {name: 'SAME_AS'})
SET rt7.source_label = 'Place', rt7.target_label = 'WikidataEntity',
    rt7.description = 'Wikidata identity bridge for enrichment. Links Place to its Wikidata entity for cross-reference.',
    rt7.category = 'geographic', rt7.temporal = false,
    rt7.kernel_category = 'geographic',
    rt7.cardinality = 'one-to-one';


// ==========================================================================
// REGISTER / UPDATE FEDERATION SOURCES
// ==========================================================================

MERGE (fs:SYS_FederationSource {source_id: 'geonames'})
SET fs.name = 'GeoNames', fs.label = 'GeoNames',
    fs.status = 'planned', fs.phase = 'geographic_v2',
    fs.endpoint = 'https://download.geonames.org/export/dump/',
    fs.description = 'Modern geographic admin hierarchy. Provides GeoPlace nodes and ADMIN_CHILD_OF edges. Clean containment tree: continent to country to admin1 to admin2 to city.',
    fs.scoping_role = 'spatial_hierarchy',
    fs.access = 'download',
    fs.data_types = ['GeoPlace', 'ADMIN_CHILD_OF'],
    fs.use_in_chrystallum = 'Modern spatial index for containment queries. Not historical data.',
    fs.added_date = date();

// Update existing Pleiades source with geographic role
MATCH (fs:SYS_FederationSource {source_id: 'pleiades'})
SET fs.description = 'Ancient/classical geography. Identity layer: temporal name attestations, time-bounded geometries, place connections, bibliographic references.',
    fs.scoping_role = 'geographic_identity',
    fs.data_types = ['Place', 'PlaceName', 'PlaceGeometry', 'PlaceType', 'Pleiades_Place'],
    fs.use_in_chrystallum = 'Primary source for Place identity. Current import is top-level summary only. Re-ingestion needed for names[], locations[], connections[] arrays from per-place JSON API.',
    fs.ingestion_note = 'Pleiades JSON per-place provides names[] and locations[] arrays, each with start_date, end_date. Current import flattened these.';
