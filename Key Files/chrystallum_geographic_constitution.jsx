import { useState } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — GEOGRAPHIC SPATIAL-TEMPORAL CONSTITUTION                    ║
// ║  Integration: Pleiades (identity) → GeoNames (hierarchy) → Wikidata (bridge)║
// ║  Self-describing: data constants below are mirrored as SYS_ nodes in Neo4j ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  bg:"#0F1923", panel:"#162330", border:"#1E3347",
  bright:"#E8F4FD", dim:"#5A7A94",
  pleiades:"#E07C3E", geonames:"#2E8B57", wikidata:"#006699",
  neo:"#00C2A8", cypher:"#B5860D",
  point:"#4ECDC4", polygon:"#FF6B6B", polyline:"#45B7D1",
  temporal:"#9B59B6", name:"#F39C12", geometry:"#1ABC9C",
  pass:"#2ECC71", warn:"#F5A623", fail:"#E74C3C",
};

const STATUS_COL = { operational:C.pass, planned:C.warn, migration_pending:C.warn, blocked:C.fail };

// ══════════════════════════════════════════════════════════════════════════════
// GEO BACKBONE — Pleiades Place filtered to settlements and regions
// ══════════════════════════════════════════════════════════════════════════════
const GEO_BACKBONE = {
  definition: "Place nodes with place_scope = 'v1_core'",
  v1_core_types: ["settlement","villa","fort","station","colony","region","province","camp","city","town","village"],
  deferred: "rivers, mountains, temples, roads, tombs, etc. — in graph but not backbone",
  total_places: 44193,
  sc_candidates: {
    total: 4868,
    pct: "11.0%",
    principle: "Entity with ≥1 bibliographic authority ID (VIAF, GND, LoC, FAST, GeoNames) is recognized by the bibliographic control universe → SubjectConcept candidate",
    biblio_distribution: [
      { biblio_ids:0, count:39325, note:"Not a subject — just a graph node" },
      { biblio_ids:1, count:3307, note:"Mostly GeoNames-only" },
      { biblio_ids:2, count:304 }, { biblio_ids:3, count:432 },
      { biblio_ids:4, count:423 }, { biblio_ids:5, count:402 },
    ],
    avg_biblio_ids: 1.8,
    candidate_facets: ["GEOGRAPHIC"],
    script: "scripts/neo4j/compute_sc_candidates.py",
  },
  query: "MATCH (p:Place) WHERE p.place_scope = 'v1_core' RETURN p",
  tagging_script: "scripts/neo4j/tag_place_scope.py",
};

// ══════════════════════════════════════════════════════════════════════════════
// DESIGN PRINCIPLES — agent reads these to understand geographic architecture
// ══════════════════════════════════════════════════════════════════════════════
const PRINCIPLES = [
  { id:"P-01", name:"Place is identity, not a point",
    desc:"A Place node represents a continuous identity across time. It may have had different names, different geometries, different administrative statuses — but it is the same place. Coordinates belong on PlaceGeometry, names belong on PlaceName." },
  { id:"P-02", name:"Three sources, three roles",
    desc:"Pleiades provides historical identity (temporal names, ancient geometries, date ranges). GeoNames provides the modern spatial hierarchy (admin containment tree). Wikidata bridges them (cross-references, multilingual labels, structured facts)." },
  { id:"P-03", name:"Time-bounded sub-nodes",
    desc:"Names and geometries are first-class nodes with start_year/end_year, not flat properties. A Place may have multiple PlaceName nodes (Byzantium, Constantinople, Istanbul) and multiple PlaceGeometry nodes (expanding city walls over centuries)." },
  { id:"P-04", name:"Multi-fidelity spatial model",
    desc:"Three levels of geometry: point (marker pins), bbox (zoom-to-fit), GeoJSON polygon/polyline (rendered shapes). Map renderers consume PlaceGeometry.geojson directly." },
  { id:"P-05", name:"GeoPlace is not Place",
    desc:"GeoPlace nodes from GeoNames are the modern admin hierarchy — not historical places. They enable containment queries ('all ancient sites in modern Turkey') but are structurally separate from Place." },
];

// ══════════════════════════════════════════════════════════════════════════════
// NODE TYPE SCHEMAS — maps to SYS_NodeType in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const NODE_TYPES = [
  { name:"Place", status:"operational", color:C.pleiades,
    desc:"Identity anchor for a geographic entity. Persists through time with changing names and geometries.",
    required_props:[
      { name:"place_id",    type:"string",  pattern:"plc_{pleiades_id} or plc_{qid}", desc:"Unique identifier" },
      { name:"label",       type:"string",  desc:"Current preferred display name" },
    ],
    optional_props:[
      { name:"pleiades_id",       type:"string",  desc:"Pleiades identifier (42,065 Places)" },
      { name:"qid",               type:"string",  pattern:"Q[0-9]+", desc:"Wikidata QID (2,808 Places)" },
      { name:"place_scope",       type:"enum",    values:["v1_core","deferred"], desc:"v1_core = backbone (settlements, regions); deferred = rivers, temples, etc." },
      { name:"description",       type:"string",  desc:"Brief description" },
      { name:"min_date",          type:"integer", desc:"Earliest attested date (derived from sub-nodes)" },
      { name:"max_date",          type:"integer", desc:"Latest attested date (derived from sub-nodes)" },
      { name:"geonames_id",       type:"string",  desc:"GeoNames ID (P1566) — crosswalk authority" },
      { name:"tgn_id",            type:"string",  desc:"Getty TGN ID (P1667) — crosswalk authority" },
      { name:"viaf_id",           type:"string",  desc:"VIAF cluster ID (P214) — library authority" },
      { name:"gnd_id",            type:"string",  desc:"GND ID (P227) — library authority" },
      { name:"loc_authority_id",  type:"string",  desc:"LoC authority ID (P244). sh-prefix = LCSH subject heading; n-prefix = NAF named entity" },
      { name:"fast_id",           type:"string",  desc:"FAST subject heading ID (P2163)" },
      { name:"osm_relation_id",   type:"string",  desc:"OpenStreetMap relation ID (P402) — modern reference" },
      { name:"instance_of",       type:"string",  desc:"Wikidata P31 instance_of labels (pipe-separated)" },
      { name:"inception_year",    type:"integer", desc:"Year of founding/inception (P571)" },
      { name:"dissolved_year",    type:"integer", desc:"Year of dissolution (P576)" },
      { name:"federation_score",  type:"integer", desc:"D16 v2 score (0-100). 9 rules: qid(25)+pleiades(20)+geonames(10)+tgn(5)+library(10)+osm(5)+coords(10)+temporal(10)+class(5)" },
      { name:"federation_score_version", type:"string", desc:"Scoring rubric version (D16_v2_9rule)" },
    ],
    deprecated_props:[
      { name:"lat",         reason:"Moved to PlaceGeometry" },
      { name:"long",        reason:"Moved to PlaceGeometry" },
      { name:"bbox",        reason:"Moved to PlaceGeometry" },
      { name:"place_type",  reason:"Moved to HAS_TYPE → PlaceType relationship" },
    ],
    current_count: 44193,
    enrichment_stats: {
      with_qid: 2808, with_pleiades: 42065, with_loc: 1071, with_viaf: 1483,
      with_gnd: 1112, with_osm: 1051, with_tgn: 510, with_instance_of: 2737,
      with_inception_year: 491, scored: 44193,
    },
  },
  { name:"PlaceName", status:"migration_pending", color:C.name,
    desc:"Time-bounded name attestation. A Place may have multiple names across time and language (Byzantium → Constantinople → Istanbul).",
    required_props:[
      { name:"name_id",     type:"string",  pattern:"pname_{source_id}_{index}", desc:"Unique identifier" },
      { name:"name_string", type:"string",  desc:"The name as attested or romanized" },
      { name:"source",      type:"enum",    values:["pleiades","wikidata","geonames","manual"], desc:"Authority that provided this name" },
    ],
    optional_props:[
      { name:"attested_form",  type:"string",  desc:"Name in original script (Greek, Latin inscription)" },
      { name:"romanized_form", type:"string",  desc:"Transliterated form" },
      { name:"language",       type:"string",  desc:"ISO 639 code (la, grc, ar, tr)" },
      { name:"start_year",    type:"integer", desc:"Year name enters use (negative for BCE)" },
      { name:"end_year",      type:"integer", desc:"Year name exits use (negative for BCE)" },
      { name:"name_type",     type:"enum",    values:["geographic","ethnic","administrative","modern","ancient","alternative"], desc:"Usage context" },
      { name:"is_primary",    type:"boolean", desc:"Preferred display name for its period" },
    ],
    current_count: 0,
    source_data:"Pleiades names[] (each with start_date, end_date, romanized, attested, language). Wikidata labels/aliases.",
  },
  { name:"PlaceGeometry", status:"migration_pending", color:C.geometry,
    desc:"Time-bounded spatial geometry. A Place may have multiple geometries representing different periods (city walls expanding, river course shifting).",
    required_props:[
      { name:"geometry_id",   type:"string", pattern:"geo_{source_id}_{index}", desc:"Unique identifier" },
      { name:"geometry_type", type:"enum",   values:["point","bbox","polygon","polyline","multipolygon"], desc:"Spatial type" },
      { name:"source",        type:"enum",   values:["pleiades","wikidata","geonames","manual"], desc:"Authority that provided this geometry" },
    ],
    optional_props:[
      { name:"latitude",          type:"float",   desc:"WGS84 latitude (required for point type)" },
      { name:"longitude",         type:"float",   desc:"WGS84 longitude (required for point type)" },
      { name:"bbox",              type:"float[]", desc:"[minLon, minLat, maxLon, maxLat]" },
      { name:"geojson",           type:"string",  desc:"Full GeoJSON for polygons/polylines — consumed directly by Leaflet/Mapbox/Deck.gl" },
      { name:"start_year",        type:"integer", desc:"Year geometry becomes valid (negative for BCE)" },
      { name:"end_year",          type:"integer", desc:"Year geometry ceases to be valid (negative for BCE)" },
      { name:"precision",         type:"enum",    values:["exact","approximate","rough","unlocated"], desc:"Spatial confidence" },
      { name:"accuracy_radius_m", type:"float",   desc:"Accuracy radius in meters" },
    ],
    current_count: 0,
    source_data:"Pleiades locations[] (each with geometry, start_date, end_date, accuracy). Wikidata P625 (point), P3896 (geoshape polygon).",
  },
  { name:"GeoPlace", status:"migration_pending", color:C.geonames,
    desc:"Modern geographic entity from GeoNames. Provides the spatial admin hierarchy for containment queries. NOT a historical place.",
    required_props:[
      { name:"geonames_id",  type:"string", desc:"GeoNames identifier" },
      { name:"label",        type:"string", desc:"Primary modern name" },
      { name:"feature_code", type:"string", desc:"GeoNames code (ADM1, PCLI, PPL, etc.)" },
      { name:"country_code", type:"string", pattern:"[A-Z]{2}", desc:"ISO 3166-1 alpha-2" },
    ],
    optional_props:[
      { name:"latitude",         type:"float",   desc:"WGS84 latitude" },
      { name:"longitude",        type:"float",   desc:"WGS84 longitude" },
      { name:"feature_class",    type:"enum",    values:["A","H","L","P","R","S","T","U","V"], desc:"GeoNames class" },
      { name:"admin1_code",      type:"string",  desc:"State/province code" },
      { name:"admin2_code",      type:"string",  desc:"County/district code" },
      { name:"population",       type:"integer", desc:"Population" },
      { name:"boundary_geojson", type:"string",  desc:"Admin boundary polygon (from GADM/Natural Earth)" },
      { name:"qid",              type:"string",  pattern:"Q[0-9]+", desc:"Wikidata QID cross-reference" },
    ],
    current_count: 1743,
    note:"Currently exists as Place nodes with node_type='geonames_place_backbone'. Migration re-labels these as :GeoPlace.",
  },
  { name:"Pleiades_Place", status:"operational", color:C.pleiades,
    desc:"Federation metadata wrapper for Pleiades. Retains domain, semantic_facet, survey_depth. Links to Place via ALIGNED_WITH_GEO_BACKBONE.",
    required_props:[
      { name:"pleiades_id",     type:"string",  desc:"Pleiades identifier" },
      { name:"label",           type:"string",  desc:"Place name from Pleiades" },
      { name:"temporal_start",  type:"integer", desc:"Earliest date" },
      { name:"temporal_end",    type:"integer", desc:"Latest date" },
      { name:"spatial_anchor",  type:"string",  desc:"Pleiades URI (used for re-ingestion)" },
    ],
    optional_props:[
      { name:"domain",          type:"string", desc:"e.g. roman_republic" },
      { name:"semantic_facet",  type:"string", desc:"e.g. GEOGRAPHIC, INTELLECTUAL" },
      { name:"survey_depth",    type:"integer", desc:"Federation survey depth" },
      { name:"is_seed",         type:"boolean", desc:"Federation seed flag" },
    ],
    current_count: 32572,
  },
  { name:"PlaceType", status:"operational", color:C.dim,
    desc:"Classification of place function. Normalized from Pleiades compound place_type strings.",
    required_props:[
      { name:"name", type:"string", desc:"e.g. settlement, fort, river, road, temple-2" },
    ],
    current_count: 14,
    note:"Migration Step 3 splits compound strings ('settlement, archaeological-site') and MERGE creates additional PlaceType nodes.",
  },
  { name:"ClassificationAnchor", status:"operational", color:C.wikidata,
    desc:"Bibliographic classification coordinate for a Place with an LCSH subject heading. Bridges geographic backbone to LCSH/FAST/LCC authority system. Created from Place nodes whose loc_authority_id starts with 'sh'.",
    required_props:[
      { name:"qid",          type:"string",  pattern:"Q[0-9]+", desc:"Wikidata QID (same as owning Place)" },
      { name:"label",        type:"string",  desc:"English label from Wikidata" },
      { name:"anchor_type",  type:"enum",    values:["HistoricalPlace","PhysicalFeature","Hydrography","GeographicPlace","AdministrativeDivision","Settlement","PoliticalEntity"], desc:"Classification derived from instance_of" },
      { name:"federation",   type:"string",  desc:"Always 'wikidata'" },
    ],
    optional_props:[
      { name:"lcsh_id",       type:"string", desc:"LCSH subject heading ID (sh-prefix)" },
      { name:"fast_id",       type:"string", desc:"FAST ID" },
      { name:"gnd_id",        type:"string", desc:"GND ID" },
      { name:"lcc",           type:"string", desc:"Library of Congress Classification notation" },
      { name:"dewey",         type:"string", desc:"Dewey Decimal Classification notation" },
      { name:"source_type",   type:"string", desc:"Always 'geographic_lcsh'" },
    ],
    current_count: 201,
    note:"Created by wire_place_classification_anchors.py. 93 HistoricalPlace, 54 PhysicalFeature, 26 Hydrography, 19 GeographicPlace, 4 AdminDiv, 3 Settlement, 2 PoliticalEntity.",
  },
  { name:"SubjectConcept", status:"operational", color:"#9B59B6",
    desc:"Geographic subject classification node. 7 concepts bootstrapped from ClassificationAnchor types. Places with instance_of are wired via MEMBER_OF.",
    required_props:[
      { name:"subject_id",    type:"string", desc:"e.g. GEO_HIST_PLACES, GEO_HYDROGRAPHY" },
      { name:"label",         type:"string", desc:"Human-readable label" },
      { name:"seed_domain",   type:"string", desc:"Always 'geographic' for these" },
      { name:"anchor_type",   type:"string", desc:"Maps to ClassificationAnchor.anchor_type" },
    ],
    optional_props:[
      { name:"scope_note",    type:"string", desc:"Description of what this concept covers" },
      { name:"lcsh_heading",  type:"string", desc:"Canonical LCSH heading" },
      { name:"lcsh_id",       type:"string", desc:"LCSH ID (sh-prefix)" },
      { name:"lcc_primary",   type:"string", desc:"Primary LCC class" },
      { name:"entity_count",  type:"integer", desc:"Number of MEMBER_OF Place nodes" },
    ],
    current_count: 7,
    subjects: [
      { id:"GEO_SETTLEMENTS",       members:1612, anchors:3,  label:"Settlements & Urban Places" },
      { id:"GEO_HIST_PLACES",       members:520,  anchors:93, label:"Historical Places & Archaeological Sites" },
      { id:"GEO_GENERAL",           members:345,  anchors:19, label:"General Geographic Places" },
      { id:"GEO_ADMIN_DIVISIONS",   members:316,  anchors:4,  label:"Administrative & Political Divisions" },
      { id:"GEO_HYDROGRAPHY",       members:254,  anchors:26, label:"Hydrography & Water Bodies" },
      { id:"GEO_PHYS_FEATURES",     members:248,  anchors:54, label:"Physical Geography & Landforms" },
      { id:"GEO_POLITICAL_ENTITIES", members:140, anchors:2,  label:"States, Empires & Political Entities" },
    ],
    note:"3,435 Places classified via instance_of pattern matching. 41k Pleiades-only Places unclassified (no instance_of data).",
  },
];

// ══════════════════════════════════════════════════════════════════════════════
// RELATIONSHIP TYPES — maps to SYS_RelationshipType in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const REL_TYPES = [
  { name:"HAS_NAME",                  source:"Place",          target:"PlaceName",     status:"migration_pending",
    desc:"Place has a time-bounded name attestation", category:"geographic", temporal:true },
  { name:"HAS_GEOMETRY",              source:"Place",          target:"PlaceGeometry", status:"migration_pending",
    desc:"Place has a time-bounded spatial geometry", category:"geographic", temporal:true },
  { name:"HAS_TYPE",                  source:"Place",          target:"PlaceType",     status:"migration_pending",
    desc:"Place is classified as this type (normalized from place_type string)", category:"geographic", temporal:false },
  { name:"LOCATED_IN",                source:"Place",          target:"Place",         status:"operational",
    desc:"Ancient spatial containment (Ostia in Latium)", category:"geographic", temporal:false,
    current_count: 3126 },
  { name:"LOCATED_IN_MODERN",         source:"Place",          target:"GeoPlace",      status:"migration_pending",
    desc:"Bridge from ancient Place to modern admin hierarchy", category:"geographic", temporal:false },
  { name:"ADMIN_CHILD_OF",            source:"GeoPlace",       target:"GeoPlace",      status:"migration_pending",
    desc:"GeoNames admin hierarchy (city → province → country)", category:"geographic", temporal:false },
  { name:"CONNECTED_TO",              source:"Place",          target:"Place",         status:"planned",
    desc:"Pleiades connection (road links, river connections, etc.)", category:"geographic", temporal:false },
  { name:"SAME_AS",                   source:"Place",          target:"WikidataEntity",status:"planned",
    desc:"Wikidata identity bridge for enrichment", category:"geographic", temporal:false },
  { name:"ALIGNED_WITH_GEO_BACKBONE", source:"Pleiades_Place", target:"Place",         status:"operational",
    desc:"Federation alignment from Pleiades survey to Place node", category:"federation", temporal:false,
    current_count: 32480 },
  { name:"BORN_IN_PLACE",             source:"Person",         target:"Place",         status:"operational",
    desc:"Person born at this place", category:"biographic", temporal:false,
    current_count: 1635 },
  { name:"DIED_IN_PLACE",             source:"Person",         target:"Place",         status:"operational",
    desc:"Person died at this place", category:"biographic", temporal:false,
    current_count: 313 },
  { name:"BURIED_AT",                 source:"Person",         target:"Place",         status:"operational",
    desc:"Person buried at this place", category:"biographic", temporal:false,
    current_count: 15 },
  // ── New relationships from geographic classification bootstrap (2026-03-08) ──
  { name:"MEMBER_OF",                 source:"Place",          target:"SubjectConcept", status:"operational",
    desc:"Place classified into geographic SubjectConcept by instance_of pattern matching", category:"classification", temporal:false,
    current_count: 3435 },
  { name:"POSITIONED_AS",             source:"Place",          target:"ClassificationAnchor", status:"operational",
    desc:"Place self-anchored to its ClassificationAnchor (hops=0, confidence=1.0)", category:"classification", temporal:false,
    current_count: 201 },
  { name:"PROVIDES_ANCHOR",           source:"SYS_FederationSource", target:"ClassificationAnchor", status:"operational",
    desc:"Wikidata federation source provides this classification anchor", category:"federation", temporal:false,
    current_count: 201 },
  { name:"ANCHORS",                   source:"ClassificationAnchor", target:"SubjectConcept", status:"operational",
    desc:"ClassificationAnchor grounds a SubjectConcept via shared anchor_type", category:"classification", temporal:false,
    current_count: 201 },
  { name:"HAS_PRIMARY_FACET",         source:"SubjectConcept", target:"Facet",          status:"operational",
    desc:"SubjectConcept belongs to Geographic facet", category:"classification", temporal:false,
    current_count: 7 },
  { name:"MANAGES_FACET",             source:"SYS_SFAAgent",   target:"Facet",          status:"operational",
    desc:"Geographic SFA agent manages the Geographic facet", category:"system", temporal:false,
    current_count: 1 },
];

// ══════════════════════════════════════════════════════════════════════════════
// FEDERATION SOURCES — geographic layer
// ══════════════════════════════════════════════════════════════════════════════
const GEO_FED = [
  { id:"pleiades", name:"Pleiades", color:C.pleiades, status:"operational",
    role:"identity_layer",
    desc:"Ancient/classical geography. Provides temporal name attestations, time-bounded geometries, place connections, bibliographic references.",
    endpoint:"https://atlantides.org/downloads/pleiades/dumps/",
    api:"https://pleiades.stoa.org/places/{pleiades_id}/json",
    provides:["PlaceName (names[] with date ranges, languages)", "PlaceGeometry (locations[] with GeoJSON, accuracy)", "PlaceType (place_types[])", "Place connections"],
    current_state:"32,572 Pleiades_Place nodes. Top-level summary imported. names[], locations[], connections[] NOT decomposed — re-ingestion required.",
    ingestion_notes:"Pleiades JSON per-place provides names[] and locations[] arrays. Each entry has start_date, end_date. Current import flattened these to single label + lat/long on Place." },
  { id:"geonames", name:"GeoNames", color:C.geonames, status:"planned",
    role:"spatial_hierarchy_layer",
    desc:"Modern geographic admin hierarchy. Clean containment tree: continent → country → admin1 → admin2 → city. Authoritative modern coordinates.",
    endpoint:"https://download.geonames.org/export/dump/",
    api:"http://api.geonames.org/getJSON?geonameId={id}&username={user}",
    provides:["GeoPlace nodes with feature codes", "ADMIN_CHILD_OF hierarchy", "Modern coordinates", "Admin boundary polygons (via GADM/Natural Earth)"],
    current_state:"1,743 backbone stubs as Place nodes (node_type='geonames_place_backbone'). No coordinates, no feature codes, no hierarchy edges.",
    ingestion_notes:"Full GeoNames dump (allCountries.zip) is 1.5GB. For Chrystallum, filter to countries with Pleiades coverage (IT, GR, TR, EG, TN, LY, SY, etc.) + admin levels 0-2." },
  { id:"wikidata_geo", name:"Wikidata (geographic)", color:C.wikidata, status:"operational",
    role:"bridge_layer",
    desc:"Universal knowledge bridge. Cross-references (GeoNames ID P1566, Pleiades ID P4145). Multilingual labels. Modern coordinates P625. External authority IDs. Classification anchors via LCSH.",
    endpoint:"https://query.wikidata.org/sparql",
    api:"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json",
    provides:["External authority IDs (VIAF, GND, LoC, FAST, OSM, TGN, GeoNames)", "instance_of classification", "Temporal bounds (inception/dissolved year)", "ClassificationAnchor nodes (LCSH-grounded)", "Modern coordinates (P625)", "Geoshape polygons (P3896 → Commons Data)", "Multilingual labels"],
    current_state:"2,808 Places have qid. 2,739 enriched with external IDs (2026-03-08). 201 ClassificationAnchors with LCSH subject headings. VIAF: 1,483 | GND: 1,112 | LoC: 1,071 | OSM: 1,051 | TGN: 510 | instance_of: 2,737 | inception_year: 491.",
    ingestion_notes:"Enrichment via Wikidata API (wbgetentities, 50/batch). Scripts: enrich_place_external_ids.py (bulk IDs), wire_place_classification_anchors.py (LCSH anchors). P3896 geoshapes NOT yet harvested." },
];

// ══════════════════════════════════════════════════════════════════════════════
// RULES — geographic domain rules
// ══════════════════════════════════════════════════════════════════════════════
const GEO_RULES = [
  { id:"GR-01", name:"Temporal Name Decomposition",
    facets:["Geographic"],
    trigger:"Place has label property but no HAS_NAME edges",
    action:"Fetch Pleiades JSON for place. UNWIND names[] array. CREATE PlaceName per entry with start_year, end_year, language, romanized, attested. CREATE (Place)-[:HAS_NAME]->(PlaceName). Mark first name is_primary=true.",
    rationale:"A place with a single label loses its temporal identity. Byzantium/Constantinople/Istanbul are the same Place — the names are time-bounded attestations, not alternatives." },
  { id:"GR-02", name:"Temporal Geometry Decomposition",
    facets:["Geographic"],
    trigger:"Place has lat/long properties but no HAS_GEOMETRY edges",
    action:"Fetch Pleiades JSON for place. UNWIND locations[] array. CREATE PlaceGeometry per entry with geometry_type, lat/long or geojson, start_year, end_year, precision. CREATE (Place)-[:HAS_GEOMETRY]->(PlaceGeometry).",
    rationale:"A city's footprint changes over centuries. Pleiades provides multiple time-bounded locations per place. Single lat/long loses this and makes temporal map rendering impossible." },
  { id:"GR-03", name:"PlaceType Normalization",
    facets:["Geographic"],
    trigger:"Place has place_type string containing comma (compound value)",
    action:"Split place_type on ', '. For each value: MERGE PlaceType {name: value}. MERGE (Place)-[:HAS_TYPE]->(PlaceType). This normalizes 'settlement, archaeological-site' into two edges.",
    rationale:"Compound place_type strings prevent faceted filtering. Normalization to edges enables queries like 'all settlements' without string parsing." },
  { id:"GR-04", name:"Modern Containment Bridge",
    facets:["Geographic"],
    trigger:"Place has coordinates (via PlaceGeometry) but no LOCATED_IN_MODERN edge",
    action:"Find nearest GeoPlace using Neo4j point.distance(). If distance < threshold for feature_code (50km for ADM1, 10km for PPL): CREATE (Place)-[:LOCATED_IN_MODERN]->(GeoPlace).",
    rationale:"Modern containment enables the query 'all ancient sites in modern Turkey' without manual mapping. Uses spatial proximity since ancient sites rarely align with modern admin centers." },
  { id:"GR-05", name:"Wikidata Geoshape Harvest",
    facets:["Geographic"],
    trigger:"Place has qid but no PlaceGeometry with geometry_type='polygon'",
    action:"Query Wikidata for P3896 (geoshape). If present: fetch GeoJSON from Commons Data. CREATE PlaceGeometry {geometry_type:'polygon', geojson: fetched_data, source:'wikidata'}. Wire HAS_GEOMETRY.",
    rationale:"Wikidata geoshapes provide region/territory boundaries (provinces, kingdoms, trade routes) that Pleiades typically lacks. Essential for map rendering of areas, not just points." },
  { id:"GR-06", name:"GeoNames Hierarchy Construction",
    facets:["Geographic"],
    trigger:"GeoPlace nodes exist but no ADMIN_CHILD_OF edges",
    action:"For each GeoPlace: lookup parent admin in GeoNames hierarchy. MERGE parent GeoPlace if absent. CREATE (child)-[:ADMIN_CHILD_OF]->(parent). Repeat up to country level.",
    rationale:"The admin tree is what makes 'ancient sites in Andalusia' work. Without it, GeoPlace nodes are isolated stubs." },
  // ── Decision table rules (implemented in Neo4j, 2026-03-08) ──
  { id:"GR-07", name:"D16 Federation Scoring (9-rule)",
    facets:["Geographic"],
    trigger:"Place node exists (any Place, scored on write/rescore)",
    action:"Apply D16_SCORE_place_federation: qid(+25) + pleiades(+20) + geonames(+10) + tgn(+5) + library_auth(+10) + osm(+5) + coords(+10) + temporal(+10) + instance_of(+5) = max 100. Write federation_score, federation_score_version.",
    rationale:"Quantifies Place data richness. Score drives SFA prioritization — high-scoring Places are processed first. Rebalanced from 4-rule (max 100) to 9-rule (max 100) based on geographic property survey of 264 Wikidata entities across 25 classes." },
  { id:"GR-08", name:"D5 Temporal Bypass for Physical Features",
    facets:["Geographic"],
    trigger:"Place has instance_of matching atemporal physical feature class",
    action:"Skip D5_SCOPE_temporal_overlap check. Bypass classes: river (Q4022), mountain (Q8502), lake (Q23397), sea (Q165), peninsula (Q34763), valley (Q39816), continent (Q5107), waterfall (Q34038), island (Q23442), ocean, strait, cape.",
    rationale:"Physical features have 0% temporal coverage in Wikidata (no P571 inception / P576 dissolution). They are permanent geographic fixtures — always in scope if spatially relevant. Without bypass, every river and mountain would fail temporal overlap and be excluded." },
  { id:"GR-09", name:"LCSH Classification Anchor Wiring",
    facets:["Geographic"],
    trigger:"Place has loc_authority_id starting with 'sh' (LCSH subject heading)",
    action:"Create ClassificationAnchor node with same QID. Fetch Dewey/LCC/FAST/GND from Wikidata. Wire POSITIONED_AS (Place→Anchor, hops=0, confidence=1.0). Wire PROVIDES_ANCHOR (Wikidata→Anchor). Classify anchor_type from instance_of.",
    rationale:"201 Places have LCSH subject headings — they ARE subjects in the Library of Congress classification. Wiring them as ClassificationAnchors bridges the geographic backbone to the bibliographic authority system that SubjectConcepts are built on." },
  { id:"GR-10", name:"SubjectConcept Membership by instance_of",
    facets:["Geographic"],
    trigger:"Place has instance_of property (from Wikidata P31 enrichment)",
    action:"Pattern-match instance_of labels against 7 SubjectConcept definitions. Wire MEMBER_OF to matching SubjectConcept. Unmatched Places fall back to GEO_GENERAL.",
    rationale:"Automated classification of 3,435 Places into 7 geographic SubjectConcepts. Uses Wikidata instance_of as the routing signal — the same property that drives ClassificationAnchor type classification." },
];

// ══════════════════════════════════════════════════════════════════════════════
// SFA AGENT & CLASSIFICATION INFRASTRUCTURE
// ══════════════════════════════════════════════════════════════════════════════
const GEO_SFA = {
  agent_id: "sfa_geographic",
  label: "Geographic SFA",
  status: "bootstrap",
  facet: "Geographic",
  entity_types: ["Place"],
  description: "Subject Facet Agent for the Geographic facet. Manages Place entities, spatial relationships, and geographic classification anchors. Covers 7 SubjectConcepts.",
  decision_tables: [
    { id:"D16_SCORE_place_federation", rules:9, max_score:100,
      desc:"Component scoring rubric for Place nodes. Rebalanced 2026-03-08 from geographic property survey.",
      dimensions:["wikidata_alignment(25)","place_authority(20)","crosswalk_authority(15)","library_authority(10)","modern_reference(5)","geospatial(10)","temporal_bounds(10)","class_signal(5)"] },
    { id:"D5_SCOPE_temporal_overlap", rules:1,
      desc:"Temporal bypass for atemporal physical features (river, mountain, lake, sea, etc.)" },
  ],
  classification_pipeline: {
    step_1: "enrich_place_external_ids.py — bulk Wikidata API harvest of authority IDs for Places with QIDs",
    step_2: "wire_place_classification_anchors.py — create ClassificationAnchors for Places with LCSH (sh-prefix) IDs",
    step_3: "bootstrap_geo_subject_concepts.py — create 7 SubjectConcepts, wire MEMBER_OF by instance_of pattern",
    step_4: "rescore_places_d16.py — apply 9-rule D16 scoring to all 44,193 Places",
    step_5: "compute_sc_candidates.py — flag 4,868 Places as sc_candidate=true based on biblio authority ID presence, route to GEOGRAPHIC facet",
  },
  coverage: {
    total_places: 44193,
    classified_places: 3435,
    unclassified_places: 41456,
    unclassified_reason: "Pleiades-only imports with no Wikidata instance_of data. Needs Pleiades→class mapping or QID alignment.",
    classification_anchors: 201,
    subject_concepts: 7,
  },
};

// ══════════════════════════════════════════════════════════════════════════════
// NAMED QUERIES
// ══════════════════════════════════════════════════════════════════════════════
const GEO_QUERIES = [
  { id:"GQ-01", label:"Cypher", name:"Place with all temporal sub-nodes",
    purpose:"Full temporal profile of a place — all names, geometries, and types across time.",
    code:`MATCH (p:Place {place_id: $place_id})
OPTIONAL MATCH (p)-[:HAS_NAME]->(pn:PlaceName)
OPTIONAL MATCH (p)-[:HAS_GEOMETRY]->(pg:PlaceGeometry)
OPTIONAL MATCH (p)-[:HAS_TYPE]->(pt:PlaceType)
RETURN p, collect(DISTINCT pn) AS names,
       collect(DISTINCT pg) AS geometries,
       collect(DISTINCT pt) AS types
ORDER BY pn.start_year` },

  { id:"GQ-02", label:"Cypher", name:"What was this place called in year X?",
    purpose:"Temporal name resolution — returns the active name(s) for a place at a given year.",
    code:`MATCH (p:Place {place_id: $place_id})-[:HAS_NAME]->(pn:PlaceName)
WHERE (pn.start_year IS NULL OR pn.start_year <= $year)
  AND (pn.end_year IS NULL OR pn.end_year >= $year)
RETURN pn.name_string AS name, pn.language AS lang,
       pn.start_year AS from_year, pn.end_year AS to_year,
       pn.is_primary AS is_primary
ORDER BY pn.is_primary DESC` },

  { id:"GQ-03", label:"Cypher", name:"All ancient sites in a modern country",
    purpose:"Containment query bridging ancient Place to modern GeoPlace hierarchy.",
    code:`MATCH (gp:GeoPlace {country_code: $country_code, feature_code: 'PCLI'})
MATCH (p:Place)-[:LOCATED_IN_MODERN]->(child:GeoPlace)
WHERE (child)-[:ADMIN_CHILD_OF*0..4]->(gp)
OPTIONAL MATCH (p)-[:HAS_GEOMETRY]->(pg:PlaceGeometry)
WHERE pg.geometry_type = 'point'
RETURN p.place_id, p.label, pg.latitude, pg.longitude,
       child.label AS modern_region
LIMIT 500` },

  { id:"GQ-04", label:"Cypher", name:"Map layer — points in time window",
    purpose:"Returns all point geometries valid in a given time range. For map time-slider.",
    code:`MATCH (p:Place)-[:HAS_GEOMETRY]->(pg:PlaceGeometry)
WHERE pg.geometry_type = 'point'
  AND (pg.start_year IS NULL OR pg.start_year <= $end_year)
  AND (pg.end_year IS NULL OR pg.end_year >= $start_year)
RETURN p.place_id, p.label, pg.latitude, pg.longitude,
       pg.start_year, pg.end_year, pg.precision` },

  { id:"GQ-05", label:"Cypher", name:"Map layer — polygons in time window",
    purpose:"Returns polygon/multipolygon geometries for territory rendering. GeoJSON passed to map renderer.",
    code:`MATCH (p:Place)-[:HAS_GEOMETRY]->(pg:PlaceGeometry)
WHERE pg.geometry_type IN ['polygon', 'multipolygon']
  AND (pg.start_year IS NULL OR pg.start_year <= $end_year)
  AND (pg.end_year IS NULL OR pg.end_year >= $start_year)
RETURN p.place_id, p.label, pg.geojson,
       pg.start_year, pg.end_year` },

  { id:"GQ-06", label:"Cypher", name:"Places within radius of point",
    purpose:"Spatial proximity query using Neo4j point.distance(). Requires Neo4j spatial index.",
    code:`MATCH (p:Place)-[:HAS_GEOMETRY]->(pg:PlaceGeometry)
WHERE pg.geometry_type = 'point'
  AND point.distance(
    point({latitude: pg.latitude, longitude: pg.longitude}),
    point({latitude: $lat, longitude: $lon})
  ) < $radius_m
RETURN p.place_id, p.label, pg.latitude, pg.longitude,
       point.distance(
         point({latitude: pg.latitude, longitude: pg.longitude}),
         point({latitude: $lat, longitude: $lon})
       ) AS distance_m
ORDER BY distance_m` },

  { id:"GQ-07", label:"Cypher", name:"Person birth/death places with temporal names",
    purpose:"For a person, resolve birth/death places with the name active at that time.",
    code:`MATCH (person:Person {qid: $qid})
OPTIONAL MATCH (person)-[:BORN_IN_PLACE]->(bp:Place)-[:HAS_NAME]->(bn:PlaceName)
  WHERE (bn.start_year IS NULL OR bn.start_year <= person.birth_year)
    AND (bn.end_year IS NULL OR bn.end_year >= person.birth_year)
    AND bn.is_primary = true
OPTIONAL MATCH (person)-[:DIED_IN_PLACE]->(dp:Place)-[:HAS_NAME]->(dn:PlaceName)
  WHERE (dn.start_year IS NULL OR dn.start_year <= person.death_year)
    AND (dn.end_year IS NULL OR dn.end_year >= person.death_year)
    AND dn.is_primary = true
RETURN person.label, bn.name_string AS birth_place_name,
       dn.name_string AS death_place_name` },

  { id:"GQ-08", label:"Cypher", name:"Migration readiness check",
    purpose:"Pre-migration diagnostic — counts Places with/without sub-nodes.",
    code:`MATCH (p:Place)
RETURN count(p) AS total_places,
  count(CASE WHEN (p)-[:HAS_NAME]->() THEN 1 END) AS has_names,
  count(CASE WHEN (p)-[:HAS_GEOMETRY]->() THEN 1 END) AS has_geometry,
  count(CASE WHEN (p)-[:HAS_TYPE]->() THEN 1 END) AS has_type,
  count(CASE WHEN (p)-[:LOCATED_IN_MODERN]->() THEN 1 END) AS has_modern_loc,
  count(CASE WHEN p.lat IS NOT NULL THEN 1 END) AS has_flat_coords,
  count(CASE WHEN p.place_type IS NOT NULL THEN 1 END) AS has_flat_type` },
];

// ══════════════════════════════════════════════════════════════════════════════
// MAP RENDERING LAYERS — for front-end map integration
// ══════════════════════════════════════════════════════════════════════════════
const MAP_LAYERS = [
  { id:"ML-01", name:"Ancient Sites", color:C.point,
    source_query:"GQ-04", geometry_type:"point",
    desc:"Primary data layer. Marker pins for all ancient places with point geometry. Clustered at low zoom, individual at high zoom.",
    time_filtered: true },
  { id:"ML-02", name:"Ancient Regions", color:C.polygon,
    source_query:"GQ-05", geometry_type:"polygon",
    desc:"Territory boundaries from Pleiades polygons and Wikidata geoshapes. Semi-transparent fill with labeled border.",
    time_filtered: true },
  { id:"ML-03", name:"Routes & Rivers", color:C.polyline,
    source_query:"GQ-05 (polyline variant)", geometry_type:"polyline",
    desc:"Road networks and river courses. Dashed line style for uncertain routes.",
    time_filtered: true },
  { id:"ML-04", name:"Modern Admin Context", color:C.geonames,
    source_query:"GeoPlace boundary_geojson", geometry_type:"polygon",
    desc:"Background layer. Modern country/province boundaries for geographic context. Low opacity, no interaction.",
    time_filtered: false },
];

// ══════════════════════════════════════════════════════════════════════════════
// MIGRATION STATE — current progress
// ══════════════════════════════════════════════════════════════════════════════
const MIGRATION = {
  status:"pending",
  prerequisites:["Back up database", "Run geographic_spatial_temporal_constraints.cypher"],
  steps:[
    { id:"M-01", name:"Create PlaceGeometry from Place.lat/long",       status:"pending", nodes_affected:"~34,331", script:"geographic_spatial_temporal_migration.cypher Step 1" },
    { id:"M-02", name:"Create PlaceGeometry from Place.bbox (no centroid)", status:"pending", nodes_affected:"~7,553", script:"Step 1b" },
    { id:"M-03", name:"Create PlaceName from Place.label",              status:"pending", nodes_affected:"~44,064", script:"Step 2" },
    { id:"M-04", name:"Link Place → PlaceType via HAS_TYPE",            status:"pending", nodes_affected:"~41,929", script:"Step 3" },
    { id:"M-05", name:"Re-label GeoNames backbone as :GeoPlace",        status:"pending", nodes_affected:"~1,743",  script:"Step 4" },
    { id:"M-06", name:"Tag Wikidata backbone stubs",                    status:"pending", nodes_affected:"~331",    script:"Step 5" },
    { id:"M-07", name:"Convert LOCATED_IN → LOCATED_IN_MODERN for GeoPlace targets", status:"pending", nodes_affected:"varies", script:"Step 6" },
  ],
  post_migration:[
    "Re-ingest from Pleiades JSON API for full temporal names[] and locations[]",
    "Harvest Wikidata P3896 geoshapes for region boundaries",
    "Load GeoNames admin hierarchy with ADMIN_CHILD_OF edges",
    "Create Neo4j spatial point indexes on PlaceGeometry and GeoPlace",
    "Remove deprecated flat properties (lat, long, bbox, place_type) from Place",
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// SYS_ NODE CYPHER — creates self-describing metadata in Neo4j
// ══════════════════════════════════════════════════════════════════════════════
const SYS_CYPHER = `// Geographic Spatial-Temporal SYS_ Node Registration
// Run after migration to make the graph self-describing for agents

// ── Register new node types ──
MERGE (nt1:SYS_NodeType {name: 'PlaceName'})
SET nt1.description = 'Time-bounded name attestation for a Place',
    nt1.system = true,
    nt1.domain = 'geographic',
    nt1.status = 'operational',
    nt1.required_properties = ['name_id', 'name_string', 'source'],
    nt1.optional_properties = ['attested_form', 'romanized_form', 'language', 'start_year', 'end_year', 'name_type', 'is_primary'],
    nt1.created_at = datetime();

MERGE (nt2:SYS_NodeType {name: 'PlaceGeometry'})
SET nt2.description = 'Time-bounded spatial geometry for a Place',
    nt2.system = true,
    nt2.domain = 'geographic',
    nt2.status = 'operational',
    nt2.required_properties = ['geometry_id', 'geometry_type', 'source'],
    nt2.optional_properties = ['latitude', 'longitude', 'bbox', 'geojson', 'start_year', 'end_year', 'precision', 'accuracy_radius_m'],
    nt2.created_at = datetime();

MERGE (nt3:SYS_NodeType {name: 'GeoPlace'})
SET nt3.description = 'Modern geographic entity from GeoNames admin hierarchy',
    nt3.system = true,
    nt3.domain = 'geographic',
    nt3.status = 'operational',
    nt3.required_properties = ['geonames_id', 'label', 'feature_code', 'country_code'],
    nt3.optional_properties = ['latitude', 'longitude', 'feature_class', 'admin1_code', 'admin2_code', 'population', 'boundary_geojson', 'qid'],
    nt3.created_at = datetime();

// ── Update existing Place node type ──
MATCH (nt:SYS_NodeType {name: 'Place'})
SET nt.description = 'Geographic identity anchor. Has temporal sub-nodes: PlaceName (names), PlaceGeometry (shapes). Coordinates and names are on sub-nodes, not Place itself.',
    nt.domain = 'geographic',
    nt.deprecated_properties = ['lat', 'long', 'bbox', 'place_type'],
    nt.updated_at = datetime();

// ── Register new relationship types ──
MERGE (rt1:SYS_RelationshipType {name: 'HAS_NAME'})
SET rt1.source_label = 'Place', rt1.target_label = 'PlaceName',
    rt1.description = 'Place has a time-bounded name attestation',
    rt1.category = 'geographic', rt1.temporal = true,
    rt1.kernel_category = 'geographic';

MERGE (rt2:SYS_RelationshipType {name: 'HAS_GEOMETRY'})
SET rt2.source_label = 'Place', rt2.target_label = 'PlaceGeometry',
    rt2.description = 'Place has a time-bounded spatial geometry',
    rt2.category = 'geographic', rt2.temporal = true,
    rt2.kernel_category = 'geographic';

MERGE (rt3:SYS_RelationshipType {name: 'HAS_TYPE'})
SET rt3.source_label = 'Place', rt3.target_label = 'PlaceType',
    rt3.description = 'Place is classified as this type',
    rt3.category = 'geographic', rt3.temporal = false,
    rt3.kernel_category = 'geographic';

MERGE (rt4:SYS_RelationshipType {name: 'LOCATED_IN_MODERN'})
SET rt4.source_label = 'Place', rt4.target_label = 'GeoPlace',
    rt4.description = 'Bridge from ancient Place to modern admin hierarchy',
    rt4.category = 'geographic', rt4.temporal = false,
    rt4.kernel_category = 'geographic';

MERGE (rt5:SYS_RelationshipType {name: 'ADMIN_CHILD_OF'})
SET rt5.source_label = 'GeoPlace', rt5.target_label = 'GeoPlace',
    rt5.description = 'GeoNames admin hierarchy (city in province in country)',
    rt5.category = 'geographic', rt5.temporal = false,
    rt5.kernel_category = 'geographic';

MERGE (rt6:SYS_RelationshipType {name: 'CONNECTED_TO'})
SET rt6.source_label = 'Place', rt6.target_label = 'Place',
    rt6.description = 'Pleiades connection (road links, river connections)',
    rt6.category = 'geographic', rt6.temporal = false,
    rt6.kernel_category = 'geographic';

MERGE (rt7:SYS_RelationshipType {name: 'SAME_AS'})
SET rt7.source_label = 'Place', rt7.target_label = 'WikidataEntity',
    rt7.description = 'Wikidata identity bridge for enrichment',
    rt7.category = 'geographic', rt7.temporal = false,
    rt7.kernel_category = 'geographic';

// ── Register federation sources for geographic layer ──
MERGE (fs:SYS_FederationSource {source_id: 'geonames'})
SET fs.name = 'GeoNames', fs.label = 'GeoNames',
    fs.status = 'planned', fs.phase = 'geographic_v2',
    fs.endpoint = 'https://download.geonames.org/export/dump/',
    fs.description = 'Modern geographic admin hierarchy. Provides GeoPlace nodes and ADMIN_CHILD_OF edges.',
    fs.scoping_role = 'spatial_hierarchy',
    fs.added_date = date();

// Update existing Pleiades source
MATCH (fs:SYS_FederationSource {source_id: 'pleiades'})
SET fs.description = 'Ancient/classical geography. Identity layer: temporal name attestations, time-bounded geometries, place connections.',
    fs.scoping_role = 'geographic_identity',
    fs.ingestion_note = 'Current: top-level summary only. Re-ingestion needed for names[], locations[], connections[] arrays from JSON API.';
`;

// ══════════════════════════════════════════════════════════════════════════════
// AGENT BOOTSTRAP QUERY — how a new agent discovers the geographic schema
// ══════════════════════════════════════════════════════════════════════════════
const AGENT_BOOTSTRAP = {
  description:"A newly instantiated agent runs these queries to understand the geographic architecture from Neo4j itself.",
  queries:[
    { step:1, name:"Discover geographic node types",
      query:`MATCH (nt:SYS_NodeType)
WHERE nt.domain = 'geographic'
RETURN nt.name, nt.description, nt.required_properties, nt.optional_properties, nt.deprecated_properties, nt.status` },
    { step:2, name:"Discover geographic relationships",
      query:`MATCH (rt:SYS_RelationshipType)
WHERE rt.kernel_category = 'geographic'
RETURN rt.name, rt.source_label, rt.target_label, rt.description, rt.temporal` },
    { step:3, name:"Discover geographic federation sources",
      query:`MATCH (fs:SYS_FederationSource)
WHERE fs.scoping_role IN ['geographic_identity', 'spatial_hierarchy']
RETURN fs.source_id, fs.name, fs.status, fs.endpoint, fs.description, fs.scoping_role` },
    { step:4, name:"Check migration state",
      query:`MATCH (p:Place)
RETURN count(p) AS total_places,
  count(CASE WHEN (p)-[:HAS_NAME]->() THEN 1 END) AS has_temporal_names,
  count(CASE WHEN (p)-[:HAS_GEOMETRY]->() THEN 1 END) AS has_temporal_geometry,
  count(CASE WHEN p.lat IS NOT NULL THEN 1 END) AS has_flat_coords_deprecated` },
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// UI HELPERS
// ══════════════════════════════════════════════════════════════════════════════
function Tag({ label, color, size=8 }) {
  return <span style={{background:color+"20",border:`1px solid ${color}`,borderRadius:10,
    padding:"1px 7px",fontSize:size,color,fontWeight:"bold",margin:"1px",display:"inline-block"}}>{label}</span>;
}
function SHead({ children, col=C.dim }) {
  return <div style={{fontSize:7.5,fontWeight:"bold",color:col,letterSpacing:"0.1em",
    textTransform:"uppercase",marginBottom:6}}>{children}</div>;
}
function Mono({ children, col=C.neo, s=8.5 }) {
  return <span style={{fontFamily:"'Courier New',monospace",fontSize:s,color:col}}>{children}</span>;
}
function CopyBtn({ text }) {
  const [ok,setOk]=useState(false);
  return <button onClick={()=>{navigator.clipboard?.writeText(text);setOk(true);setTimeout(()=>setOk(false),1200);}}
    style={{background:ok?C.pass+"30":C.border,color:ok?C.pass:C.dim,
      border:`1px solid ${ok?C.pass:C.border}`,borderRadius:3,
      padding:"1px 8px",fontSize:7.5,cursor:"pointer",transition:"all .2s"}}>{ok?"copied":"copy"}</button>;
}

// ── PRINCIPLES TAB ───────────────────────────────────────────────────────────
function PrinciplesTab() {
  return (
    <div>
      {PRINCIPLES.map(p=>(
        <div key={p.id} style={{borderLeft:`3px solid ${C.neo}`,padding:"8px 12px",
          marginBottom:8,background:C.panel,borderRadius:"0 4px 4px 0"}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <Mono col={C.neo}>{p.id}</Mono>
            <span style={{fontWeight:"bold",color:C.bright,fontSize:10}}>{p.name}</span>
          </div>
          <div style={{fontSize:8.5,color:C.dim,lineHeight:1.5}}>{p.desc}</div>
        </div>
      ))}
    </div>
  );
}

// ── NODE TYPES TAB ───────────────────────────────────────────────────────────
function NodeTypesTab() {
  const [sel,setSel]=useState("Place");
  const nt = NODE_TYPES.find(n=>n.name===sel);
  return (
    <div style={{display:"grid",gridTemplateColumns:"180px 1fr",gap:12}}>
      <div>
        {NODE_TYPES.map(n=>(
          <div key={n.name} onClick={()=>setSel(n.name)}
            style={{border:`1px solid ${sel===n.name?n.color:C.border}`,
              borderLeft:`3px solid ${n.color}`,borderRadius:4,
              padding:"6px 10px",marginBottom:5,cursor:"pointer",
              background:sel===n.name?n.color+"10":C.panel}}>
            <div style={{display:"flex",gap:6,alignItems:"center"}}>
              <span style={{fontWeight:"bold",color:n.color,fontSize:9.5}}>:{n.name}</span>
              <div style={{marginLeft:"auto",width:6,height:6,borderRadius:"50%",
                background:STATUS_COL[n.status]||C.dim}}/>
            </div>
            {n.current_count>0 && <div style={{fontSize:7.5,color:C.dim}}>{n.current_count.toLocaleString()} nodes</div>}
          </div>
        ))}
      </div>
      {nt&&(
        <div style={{border:`1px solid ${nt.color}40`,borderLeft:`3px solid ${nt.color}`,
          borderRadius:6,padding:12,background:C.panel}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:6}}>
            <span style={{fontWeight:"bold",color:nt.color,fontSize:13}}>:{nt.name}</span>
            <Tag label={nt.status} color={STATUS_COL[nt.status]||C.dim}/>
            {nt.current_count>0 && <Tag label={`${nt.current_count.toLocaleString()} nodes`} color={C.dim}/>}
          </div>
          <div style={{fontSize:9,color:C.dim,marginBottom:10,lineHeight:1.5}}>{nt.desc}</div>

          <SHead col={nt.color}>REQUIRED PROPERTIES</SHead>
          {nt.required_props.map(p=>(
            <div key={p.name} style={{display:"flex",gap:8,marginBottom:3,paddingLeft:8,
              borderLeft:`2px solid ${nt.color}`}}>
              <Mono col={nt.color} s={8}>{p.name}</Mono>
              <span style={{fontSize:8,color:C.dim}}>{p.type}{p.pattern?` (${p.pattern})`:""}</span>
              <span style={{fontSize:8,color:C.dim,marginLeft:"auto"}}>{p.desc}</span>
            </div>
          ))}

          {nt.optional_props?.length>0 && <>
            <SHead col={C.dim}>OPTIONAL PROPERTIES</SHead>
            {nt.optional_props.map(p=>(
              <div key={p.name} style={{display:"flex",gap:8,marginBottom:3,paddingLeft:8,
                borderLeft:`2px solid ${C.border}`}}>
                <Mono col={C.dim} s={8}>{p.name}</Mono>
                <span style={{fontSize:8,color:C.dim}}>{p.type}{p.values?` [${p.values.join(", ")}]`:""}</span>
                <span style={{fontSize:8,color:C.dim,marginLeft:"auto"}}>{p.desc}</span>
              </div>
            ))}
          </>}

          {nt.deprecated_props?.length>0 && <>
            <SHead col={C.fail}>DEPRECATED (moved to sub-nodes)</SHead>
            {nt.deprecated_props.map(p=>(
              <div key={p.name} style={{display:"flex",gap:8,marginBottom:3,paddingLeft:8,
                borderLeft:`2px solid ${C.fail}`}}>
                <Mono col={C.fail} s={8}>{p.name}</Mono>
                <span style={{fontSize:8,color:C.fail}}>{p.reason}</span>
              </div>
            ))}
          </>}

          {nt.source_data && <div style={{marginTop:8,background:nt.color+"10",borderRadius:3,
            padding:"4px 8px",fontSize:7.5,color:nt.color}}>{nt.source_data}</div>}
          {nt.note && <div style={{marginTop:4,fontSize:7.5,color:C.dim,fontStyle:"italic"}}>{nt.note}</div>}
        </div>
      )}
    </div>
  );
}

// ── RELATIONSHIPS TAB ────────────────────────────────────────────────────────
function RelsTab() {
  return (
    <div>
      {REL_TYPES.map(r=>(
        <div key={r.name} style={{display:"flex",gap:8,marginBottom:5,
          borderLeft:`3px solid ${r.status==='operational'?C.pass:C.warn}`,
          padding:"6px 10px",background:C.panel,borderRadius:"0 4px 4px 0",
          alignItems:"center"}}>
          <div style={{width:6,height:6,borderRadius:"50%",
            background:STATUS_COL[r.status]||C.dim,flexShrink:0}}/>
          <Mono col={C.neo} s={9}>{r.name}</Mono>
          <Tag label={`:${r.source}`} color={C.pleiades} size={7}/>
          <span style={{color:C.dim,fontSize:8}}>-&gt;</span>
          <Tag label={`:${r.target}`} color={C.geonames} size={7}/>
          {r.temporal && <Tag label="temporal" color={C.temporal} size={7}/>}
          <span style={{fontSize:8,color:C.dim,flex:1,marginLeft:8}}>{r.desc}</span>
          {r.current_count && <span style={{fontSize:7.5,color:C.dim}}>{r.current_count.toLocaleString()}</span>}
        </div>
      ))}
    </div>
  );
}

// ── FEDERATION TAB ───────────────────────────────────────────────────────────
function FedTab() {
  const [sel,setSel]=useState(null);
  return (
    <div>
      {GEO_FED.map(src=>(
        <div key={src.id} style={{border:`1px solid ${src.color}30`,
          borderLeft:`3px solid ${src.color}`,borderRadius:4,marginBottom:6}}>
          <div onClick={()=>setSel(sel===src.id?null:src.id)}
            style={{padding:"8px 12px",cursor:"pointer",display:"flex",
              gap:8,alignItems:"center",background:C.panel}}>
            <div style={{width:8,height:8,borderRadius:"50%",
              background:STATUS_COL[src.status],flexShrink:0}}/>
            <span style={{fontWeight:"bold",color:src.color,fontSize:10,flex:1}}>{src.name}</span>
            <Tag label={src.role} color={src.color} size={7.5}/>
            <Tag label={src.status} color={STATUS_COL[src.status]} size={7}/>
            <span style={{color:C.dim}}>{sel===src.id?"\u25B2":"\u25BC"}</span>
          </div>
          {sel===src.id&&(
            <div style={{padding:"10px 12px",background:C.bg,borderTop:`1px solid ${C.border}`}}>
              <div style={{fontSize:8.5,color:C.dim,marginBottom:8,lineHeight:1.5}}>{src.desc}</div>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
                <div>
                  <SHead col={src.color}>PROVIDES</SHead>
                  {src.provides.map(p=>(
                    <div key={p} style={{fontSize:8,color:C.bright,marginBottom:2,
                      paddingLeft:8,borderLeft:`2px solid ${src.color}`}}>{p}</div>
                  ))}
                </div>
                <div>
                  <SHead col={C.dim}>CURRENT STATE</SHead>
                  <div style={{fontSize:8,color:C.warn,marginBottom:6,lineHeight:1.5}}>{src.current_state}</div>
                  <SHead col={C.dim}>ENDPOINT</SHead>
                  <Mono col={src.color} s={7.5}>{src.endpoint}</Mono>
                </div>
              </div>
              {src.ingestion_notes && <div style={{marginTop:8,background:src.color+"10",
                borderRadius:3,padding:"5px 8px",fontSize:7.5,color:src.color}}>{src.ingestion_notes}</div>}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── RULES TAB ────────────────────────────────────────────────────────────────
function RulesTab() {
  const [sel,setSel]=useState(null);
  return (
    <div>
      {GEO_RULES.map(r=>(
        <div key={r.id} style={{border:`1px solid ${sel===r.id?C.neo:C.border}`,
          borderLeft:`3px solid ${C.neo}`,borderRadius:4,marginBottom:5}}>
          <div onClick={()=>setSel(sel===r.id?null:r.id)}
            style={{padding:"6px 10px",cursor:"pointer",display:"flex",
              gap:8,alignItems:"center",background:C.panel}}>
            <Mono col={C.neo} s={8.5}>{r.id}</Mono>
            <span style={{fontWeight:"bold",color:C.bright,fontSize:9.5,flex:1}}>{r.name}</span>
            {r.facets.map(f=><Tag key={f} label={f} color={C.geonames} size={7}/>)}
            <span style={{color:C.dim}}>{sel===r.id?"\u25B2":"\u25BC"}</span>
          </div>
          {sel===r.id&&(
            <div style={{padding:"8px 10px",background:C.bg,borderTop:`1px solid ${C.border}`,
              display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
              <div>
                <SHead col={C.warn}>TRIGGER</SHead>
                <div style={{fontSize:8.5,color:C.dim,marginBottom:8,lineHeight:1.5}}>{r.trigger}</div>
                <SHead col={C.neo}>ACTION</SHead>
                <div style={{fontFamily:"'Courier New',monospace",fontSize:8,color:C.neo,
                  background:C.neo+"08",borderRadius:3,padding:"5px 7px",lineHeight:1.5}}>{r.action}</div>
              </div>
              <div>
                <SHead col={C.dim}>RATIONALE</SHead>
                <div style={{fontSize:8.5,color:C.dim,lineHeight:1.5}}>{r.rationale}</div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── QUERIES TAB ──────────────────────────────────────────────────────────────
function QueriesTab() {
  const [sel,setSel]=useState("GQ-01");
  const q=GEO_QUERIES.find(q=>q.id===sel);
  return (
    <div style={{display:"grid",gridTemplateColumns:"220px 1fr",gap:12}}>
      <div>
        {GEO_QUERIES.map(q=>(
          <div key={q.id} onClick={()=>setSel(q.id)}
            style={{border:`1px solid ${sel===q.id?C.neo:C.border}`,
              borderLeft:`3px solid ${sel===q.id?C.neo:C.border}`,
              borderRadius:3,padding:"5px 8px",marginBottom:3,cursor:"pointer",
              background:sel===q.id?C.neo+"12":C.panel}}>
            <div style={{fontWeight:"bold",color:sel===q.id?C.neo:C.dim,fontSize:8.5}}>{q.id}</div>
            <div style={{fontSize:7.5,color:C.dim,marginTop:1}}>{q.name}</div>
          </div>
        ))}
      </div>
      {q&&(
        <div>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <Tag label={q.label} color={C.neo}/>
            <span style={{fontWeight:"bold",color:C.neo,fontSize:11}}>{q.name}</span>
          </div>
          <div style={{fontSize:8.5,color:C.dim,marginBottom:8,
            background:C.neo+"08",borderRadius:3,padding:"4px 8px"}}>{q.purpose}</div>
          <div style={{display:"flex",justifyContent:"flex-end",marginBottom:4}}>
            <CopyBtn text={q.code}/>
          </div>
          <pre style={{fontFamily:"'Courier New',monospace",fontSize:8.5,color:C.neo,
            background:C.neo+"08",borderRadius:4,padding:10,margin:0,
            overflow:"auto",maxHeight:400,whiteSpace:"pre-wrap",lineHeight:1.6}}>{q.code}</pre>
        </div>
      )}
    </div>
  );
}

// ── MAP LAYERS TAB ───────────────────────────────────────────────────────────
function MapTab() {
  return (
    <div>
      <div style={{fontSize:9,color:C.dim,marginBottom:12,lineHeight:1.5}}>
        Front-end composites these layers. PlaceGeometry.geojson is passed directly to Leaflet/Mapbox/Deck.gl.
        Time slider filters by PlaceGeometry.start_year / end_year.
      </div>
      {MAP_LAYERS.map(ml=>(
        <div key={ml.id} style={{border:`1px solid ${ml.color}30`,
          borderLeft:`3px solid ${ml.color}`,borderRadius:4,padding:"8px 12px",
          marginBottom:6,background:C.panel,display:"flex",gap:10,alignItems:"flex-start"}}>
          <div style={{width:24,height:24,borderRadius:4,background:ml.color+"30",
            border:`2px solid ${ml.color}`,display:"flex",alignItems:"center",justifyContent:"center",
            fontSize:10,flexShrink:0}}>
            {ml.geometry_type==="point"?"\u2022":ml.geometry_type==="polygon"?"\u25A0":"\u2014"}
          </div>
          <div style={{flex:1}}>
            <div style={{display:"flex",gap:6,alignItems:"center",marginBottom:3}}>
              <span style={{fontWeight:"bold",color:ml.color,fontSize:10}}>{ml.name}</span>
              <Tag label={ml.geometry_type} color={ml.color} size={7}/>
              {ml.time_filtered && <Tag label="time-filtered" color={C.temporal} size={7}/>}
              <Mono col={C.dim} s={7}>{ml.source_query}</Mono>
            </div>
            <div style={{fontSize:8.5,color:C.dim}}>{ml.desc}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── MIGRATION TAB ────────────────────────────────────────────────────────────
function MigrationTab() {
  return (
    <div>
      <div style={{display:"flex",gap:6,marginBottom:10}}>
        <Tag label={`Overall: ${MIGRATION.status}`} color={STATUS_COL[MIGRATION.status]||C.warn}/>
      </div>
      <SHead col={C.warn}>PREREQUISITES</SHead>
      {MIGRATION.prerequisites.map(p=>(
        <div key={p} style={{fontSize:8.5,color:C.dim,marginBottom:3,paddingLeft:8,
          borderLeft:`2px solid ${C.warn}`}}>{p}</div>
      ))}
      <div style={{marginTop:10}}>
        <SHead col={C.neo}>MIGRATION STEPS</SHead>
        {MIGRATION.steps.map(s=>(
          <div key={s.id} style={{display:"flex",gap:8,marginBottom:5,
            borderLeft:`3px solid ${STATUS_COL[s.status]||C.warn}`,
            padding:"5px 10px",background:C.panel,borderRadius:"0 4px 4px 0",
            alignItems:"center"}}>
            <div style={{width:6,height:6,borderRadius:"50%",
              background:STATUS_COL[s.status]||C.warn,flexShrink:0}}/>
            <Mono col={C.neo} s={8}>{s.id}</Mono>
            <span style={{fontSize:9,color:C.bright,flex:1}}>{s.name}</span>
            <Tag label={s.nodes_affected} color={C.dim} size={7}/>
            <Mono col={C.dim} s={7}>{s.script}</Mono>
          </div>
        ))}
      </div>
      <div style={{marginTop:10}}>
        <SHead col={C.pleiades}>POST-MIGRATION (re-ingestion)</SHead>
        {MIGRATION.post_migration.map((p,i)=>(
          <div key={i} style={{fontSize:8.5,color:C.pleiades,marginBottom:3,paddingLeft:8,
            borderLeft:`2px solid ${C.pleiades}`}}>{p}</div>
        ))}
      </div>
    </div>
  );
}

// ── SFA TAB ─────────────────────────────────────────────────────────────────
function SfaTab() {
  return (
    <div>
      <div style={{border:`1px solid ${C.neo}40`,borderLeft:`3px solid ${C.neo}`,
        borderRadius:6,padding:12,background:C.panel,marginBottom:12}}>
        <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:6}}>
          <span style={{fontWeight:"bold",color:C.neo,fontSize:13}}>{GEO_SFA.label}</span>
          <Tag label={GEO_SFA.status} color={C.warn}/>
          <Tag label={`agent_id: ${GEO_SFA.agent_id}`} color={C.dim}/>
        </div>
        <div style={{fontSize:9,color:C.dim,marginBottom:8,lineHeight:1.5}}>{GEO_SFA.description}</div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
          <div>
            <SHead col={C.neo}>DECISION TABLES</SHead>
            {GEO_SFA.decision_tables.map(dt=>(
              <div key={dt.id} style={{marginBottom:6,paddingLeft:8,borderLeft:`2px solid ${C.neo}`}}>
                <Mono col={C.neo} s={8.5}>{dt.id}</Mono>
                <span style={{fontSize:8,color:C.dim,marginLeft:6}}>{dt.rules} rules{dt.max_score?`, max ${dt.max_score}`:""}</span>
                <div style={{fontSize:7.5,color:C.dim}}>{dt.desc}</div>
                {dt.dimensions && <div style={{marginTop:2,display:"flex",gap:3,flexWrap:"wrap"}}>
                  {dt.dimensions.map(d=><Tag key={d} label={d} color={C.neo} size={6.5}/>)}
                </div>}
              </div>
            ))}
          </div>
          <div>
            <SHead col={C.wikidata}>CLASSIFICATION PIPELINE</SHead>
            {Object.entries(GEO_SFA.classification_pipeline).map(([step,desc])=>(
              <div key={step} style={{fontSize:8,color:C.dim,marginBottom:4,paddingLeft:8,
                borderLeft:`2px solid ${C.wikidata}`}}>
                <Mono col={C.wikidata} s={7.5}>{step}</Mono>
                <span style={{marginLeft:6}}>{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <SHead col={C.pleiades}>COVERAGE</SHead>
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8,marginBottom:12}}>
        {[["Total Places",GEO_SFA.coverage.total_places,C.pleiades],
          ["Classified",GEO_SFA.coverage.classified_places,C.pass],
          ["Unclassified",GEO_SFA.coverage.unclassified_places,C.warn],
          ["Anchors",GEO_SFA.coverage.classification_anchors,C.wikidata],
          ["SubjectConcepts",GEO_SFA.coverage.subject_concepts,C.neo],
        ].map(([label,val,col])=>(
          <div key={label} style={{background:col+"10",border:`1px solid ${col}30`,borderRadius:4,
            padding:"6px 10px",textAlign:"center"}}>
            <div style={{fontSize:16,fontWeight:"bold",color:col}}>{val.toLocaleString()}</div>
            <div style={{fontSize:7.5,color:C.dim}}>{label}</div>
          </div>
        ))}
      </div>
      <SHead col="#9B59B6">SUBJECT CONCEPTS</SHead>
      <div style={{borderRadius:4,overflow:"hidden",border:`1px solid ${C.border}`}}>
        <div style={{display:"grid",gridTemplateColumns:"200px 80px 80px 1fr",
          background:C.border,padding:"4px 8px",fontSize:7.5,fontWeight:"bold",color:C.dim}}>
          <span>Subject ID</span><span>Members</span><span>Anchors</span><span>Label</span>
        </div>
        {NODE_TYPES.find(n=>n.name==="SubjectConcept")?.subjects?.map(s=>(
          <div key={s.id} style={{display:"grid",gridTemplateColumns:"200px 80px 80px 1fr",
            padding:"3px 8px",borderTop:`1px solid ${C.border}`,fontSize:8}}>
            <Mono col="#9B59B6" s={8}>{s.id}</Mono>
            <span style={{color:C.bright}}>{s.members.toLocaleString()}</span>
            <span style={{color:C.wikidata}}>{s.anchors}</span>
            <span style={{color:C.dim}}>{s.label}</span>
          </div>
        ))}
      </div>
      <div style={{marginTop:8,fontSize:7.5,color:C.warn,fontStyle:"italic"}}>
        {GEO_SFA.coverage.unclassified_reason}
      </div>
    </div>
  );
}

// ── BOOTSTRAP TAB ────────────────────────────────────────────────────────────
function BootstrapTab() {
  return (
    <div>
      <div style={{fontSize:9,color:C.dim,marginBottom:12,lineHeight:1.5}}>
        {AGENT_BOOTSTRAP.description}
      </div>
      {AGENT_BOOTSTRAP.queries.map(q=>(
        <div key={q.step} style={{marginBottom:10}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:4}}>
            <div style={{background:C.neo,color:"white",borderRadius:"50%",
              width:20,height:20,display:"flex",alignItems:"center",justifyContent:"center",
              fontSize:9,fontWeight:"bold",flexShrink:0}}>{q.step}</div>
            <span style={{fontWeight:"bold",color:C.bright,fontSize:9.5}}>{q.name}</span>
            <div style={{marginLeft:"auto"}}><CopyBtn text={q.query}/></div>
          </div>
          <pre style={{fontFamily:"'Courier New',monospace",fontSize:8,color:C.neo,
            background:C.neo+"08",borderRadius:4,padding:8,margin:0,
            whiteSpace:"pre-wrap",lineHeight:1.5}}>{q.query}</pre>
        </div>
      ))}
      <div style={{marginTop:12}}>
        <SHead col={C.cypher}>SYS_ REGISTRATION CYPHER</SHead>
        <div style={{fontSize:8,color:C.dim,marginBottom:6}}>
          Run once after migration to register geographic node types, relationships, and federation sources in Neo4j.
          This makes the graph self-describing — agents discover the schema by querying SYS_ nodes.
        </div>
        <div style={{display:"flex",justifyContent:"flex-end",marginBottom:4}}>
          <CopyBtn text={SYS_CYPHER}/>
        </div>
        <pre style={{fontFamily:"'Courier New',monospace",fontSize:7.5,color:C.cypher,
          background:C.cypher+"08",borderRadius:4,padding:10,margin:0,
          overflow:"auto",maxHeight:400,whiteSpace:"pre-wrap",lineHeight:1.5}}>{SYS_CYPHER}</pre>
      </div>
    </div>
  );
}

// ── ROOT ─────────────────────────────────────────────────────────────────────
export default function App() {
  const [view,setView]=useState("principles");
  const VIEWS=[
    ["principles",  "Principles"],
    ["nodes",       `Node Types (${NODE_TYPES.length})`],
    ["rels",        `Relationships (${REL_TYPES.length})`],
    ["rules",       `Rules (${GEO_RULES.length})`],
    ["queries",     `Queries (${GEO_QUERIES.length})`],
    ["fed",         `Federation (${GEO_FED.length})`],
    ["sfa",         "SFA Agent"],
    ["map",         `Map Layers (${MAP_LAYERS.length})`],
    ["migration",   "Migration"],
    ["bootstrap",   "Agent Bootstrap"],
  ];
  return (
    <div style={{background:C.bg,minHeight:"100vh",padding:16,
      fontFamily:"'Courier New',monospace",color:C.bright}}>
      <div style={{borderBottom:`1px solid ${C.border}`,paddingBottom:12,marginBottom:14}}>
        <div style={{display:"flex",alignItems:"center",gap:8,flexWrap:"wrap",marginBottom:4}}>
          <span style={{fontSize:8,color:C.dim,letterSpacing:"0.15em"}}>CHRYSTALLUM - AGENT CONSTITUTION</span>
          {[["Pleiades",C.pleiades],["GeoNames",C.geonames],["Wikidata",C.wikidata],["Neo4j",C.neo]].map(([l,c])=>(
            <span key={l} style={{background:c,color:"white",borderRadius:4,
              padding:"1px 8px",fontSize:8,fontWeight:"bold"}}>{l}</span>
          ))}
        </div>
        <div style={{fontSize:18,fontWeight:"bold",color:C.bright,marginBottom:2}}>
          Geographic Spatial-Temporal Constitution
        </div>
        <div style={{fontSize:9,color:C.dim,marginBottom:6}}>
          Temporal decomposition of Place with multi-fidelity spatial model.
          Places are identities with time-bounded names and geometries, not flat coordinate properties.
          44,193 Places | 201 ClassificationAnchors | 7 SubjectConcepts | 3,435 classified | D16 scored.
        </div>
        <div style={{display:"flex",gap:8,flexWrap:"wrap",fontSize:8,color:C.dim}}>
          <span>{NODE_TYPES.length} node types</span>
          <span>-</span><span>{REL_TYPES.length} relationships</span>
          <span>-</span><span>{GEO_RULES.length} rules</span>
          <span>-</span><span>{GEO_QUERIES.length} named queries</span>
          <span>-</span><span>{GEO_FED.length} federation sources</span>
          <span>-</span><span>{MAP_LAYERS.length} map layers</span>
          <span>-</span><span>1 SFA agent</span>
        </div>
        <div style={{marginTop:8,background:C.neo+"10",border:`1px solid ${C.neo}30`,
          borderRadius:4,padding:"5px 10px",fontSize:8,color:C.neo}}>
          AGENT INSTRUCTION: This is the geographic domain constitution.
          Geo backbone = Place WHERE place_scope='v1_core' (settlements, regions, villas, forts, colonies).
          Three source layers: Pleiades (identity), GeoNames (spatial hierarchy), Wikidata (bridge + enrichment).
          All node types and relationships are registered as SYS_ nodes in Neo4j.
          SFA agent: sfa_geographic (status=bootstrap). 7 SubjectConcepts with LCSH/FAST/LCC authority.
          D16 scoring (9 rules, max 100) applied to all Places. D5 temporal bypass for atemporal features.
          Query SYS_NodeType WHERE domain='geographic' to bootstrap.
        </div>
      </div>
      <div style={{display:"flex",gap:0,borderBottom:`1px solid ${C.border}`,marginBottom:14,flexWrap:"wrap"}}>
        {VIEWS.map(([k,l])=>(
          <button key={k} onClick={()=>setView(k)}
            style={{border:"none",background:"transparent",padding:"6px 12px",fontSize:8.5,
              cursor:"pointer",color:view===k?C.neo:C.dim,fontWeight:view===k?"bold":"normal",
              borderBottom:view===k?`2px solid ${C.neo}`:"2px solid transparent"}}>
            {l}
          </button>
        ))}
      </div>
      {view==="principles" && <PrinciplesTab/>}
      {view==="nodes"      && <NodeTypesTab/>}
      {view==="rels"       && <RelsTab/>}
      {view==="rules"      && <RulesTab/>}
      {view==="queries"    && <QueriesTab/>}
      {view==="fed"        && <FedTab/>}
      {view==="sfa"        && <SfaTab/>}
      {view==="map"        && <MapTab/>}
      {view==="migration"  && <MigrationTab/>}
      {view==="bootstrap"  && <BootstrapTab/>}
    </div>
  );
}
