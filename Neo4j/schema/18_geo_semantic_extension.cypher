// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: GEO SEMANTIC EXTENSION
// ============================================================================
// File: 18_geo_semantic_extension.cypher
// Purpose:
//   1) Add explicit geographic semantic distinction roots:
//        - MAN_MADE_STRUCTURE
//        - PHYSICAL_FEATURE
//        - SETTLEMENT_TYPE
//   2) Add reusable object/function/material taxonomy stubs for future curation.
// Notes:
//   - Safe to run repeatedly (MERGE / IF NOT EXISTS).
//   - Non-destructive: does not clear existing Place/Period/Claim data.
// ============================================================================

// ============================================================================
// CONSTRAINTS
// ============================================================================

CREATE CONSTRAINT geo_semantic_type_id_unique IF NOT EXISTS
FOR (gst:GeoSemanticType) REQUIRE gst.type_id IS UNIQUE;

CREATE CONSTRAINT object_type_id_unique IF NOT EXISTS
FOR (ot:ObjectType) REQUIRE ot.type_id IS UNIQUE;

CREATE CONSTRAINT function_type_id_unique IF NOT EXISTS
FOR (ft:FunctionType) REQUIRE ft.type_id IS UNIQUE;

// ============================================================================
// GEO SEMANTIC ROOTS
// ============================================================================

UNWIND [
  {type_id: 'MAN_MADE_STRUCTURE', label: 'Man-Made Structure', description: 'Human-built structures and infrastructure.'},
  {type_id: 'PHYSICAL_FEATURE', label: 'Physical Feature', description: 'Natural land, water, and terrain features.'},
  {type_id: 'SETTLEMENT_TYPE', label: 'Settlement Type', description: 'Population-place and administrative settlement units.'},
  {type_id: 'UNKNOWN_OR_NEEDS_REVIEW', label: 'Unknown or Needs Review', description: 'Fallback semantic type for unresolved mappings.'}
] AS row
MERGE (gst:GeoSemanticType {type_id: row.type_id})
ON CREATE SET gst.created = datetime()
SET gst.label = row.label,
    gst.description = row.description,
    gst.updated = datetime();

// ============================================================================
// OBJECT TYPE STUBS (ALIGNS PLACE/OBJECT VIEW)
// ============================================================================

UNWIND [
  {type_id: 'OBJECT_TYPE_ROOT', label: 'Object Type Root', geo_semantic_type_id: 'UNKNOWN_OR_NEEDS_REVIEW'},
  {type_id: 'BUILT_STRUCTURE', label: 'Built Structure', geo_semantic_type_id: 'MAN_MADE_STRUCTURE'},
  {type_id: 'DEFENSIVE_STRUCTURE', label: 'Defensive Structure', geo_semantic_type_id: 'MAN_MADE_STRUCTURE'},
  {type_id: 'SACRED_STRUCTURE', label: 'Sacred Structure', geo_semantic_type_id: 'MAN_MADE_STRUCTURE'},
  {type_id: 'TRANSPORT_INFRASTRUCTURE', label: 'Transport Infrastructure', geo_semantic_type_id: 'MAN_MADE_STRUCTURE'},
  {type_id: 'ARCHAEOLOGICAL_OBJECT_SITE', label: 'Archaeological Object/Site', geo_semantic_type_id: 'MAN_MADE_STRUCTURE'},
  {type_id: 'NATURAL_TERRAIN_FEATURE', label: 'Natural Terrain Feature', geo_semantic_type_id: 'PHYSICAL_FEATURE'},
  {type_id: 'HYDRO_FEATURE', label: 'Hydro Feature', geo_semantic_type_id: 'PHYSICAL_FEATURE'},
  {type_id: 'SETTLEMENT_UNIT', label: 'Settlement Unit', geo_semantic_type_id: 'SETTLEMENT_TYPE'},
  {type_id: 'ADMIN_SETTLEMENT_REGION', label: 'Administrative Settlement/Region', geo_semantic_type_id: 'SETTLEMENT_TYPE'}
] AS row
MERGE (ot:ObjectType {type_id: row.type_id})
ON CREATE SET ot.created = datetime()
SET ot.label = row.label,
    ot.updated = datetime()
WITH ot, row
MATCH (gst:GeoSemanticType {type_id: row.geo_semantic_type_id})
MERGE (ot)-[:BELONGS_TO_GEO_SEMANTIC_TYPE]->(gst);

UNWIND [
  {child: 'BUILT_STRUCTURE', parent: 'OBJECT_TYPE_ROOT'},
  {child: 'DEFENSIVE_STRUCTURE', parent: 'BUILT_STRUCTURE'},
  {child: 'SACRED_STRUCTURE', parent: 'BUILT_STRUCTURE'},
  {child: 'TRANSPORT_INFRASTRUCTURE', parent: 'BUILT_STRUCTURE'},
  {child: 'ARCHAEOLOGICAL_OBJECT_SITE', parent: 'BUILT_STRUCTURE'},
  {child: 'NATURAL_TERRAIN_FEATURE', parent: 'OBJECT_TYPE_ROOT'},
  {child: 'HYDRO_FEATURE', parent: 'OBJECT_TYPE_ROOT'},
  {child: 'SETTLEMENT_UNIT', parent: 'OBJECT_TYPE_ROOT'},
  {child: 'ADMIN_SETTLEMENT_REGION', parent: 'SETTLEMENT_UNIT'}
] AS edge
MATCH (child:ObjectType {type_id: edge.child})
MATCH (parent:ObjectType {type_id: edge.parent})
MERGE (child)-[:SUBCLASS_OF]->(parent);

// ============================================================================
// FUNCTION TYPE STUBS (FOR FUTURE :Object / :Place enrichment)
// ============================================================================

UNWIND [
  {type_id: 'FUNCTION_TYPE_ROOT', label: 'Function Type Root'},
  {type_id: 'HABITATION_FUNCTION', label: 'Habitation'},
  {type_id: 'DEFENSIVE_FUNCTION', label: 'Defensive'},
  {type_id: 'SACRAL_FUNCTION', label: 'Sacral'},
  {type_id: 'TRANSPORT_FUNCTION', label: 'Transport'},
  {type_id: 'ADMINISTRATIVE_FUNCTION', label: 'Administrative'},
  {type_id: 'PRODUCTION_FUNCTION', label: 'Production'}
] AS row
MERGE (ft:FunctionType {type_id: row.type_id})
ON CREATE SET ft.created = datetime()
SET ft.label = row.label,
    ft.updated = datetime();

UNWIND [
  {child: 'HABITATION_FUNCTION', parent: 'FUNCTION_TYPE_ROOT'},
  {child: 'DEFENSIVE_FUNCTION', parent: 'FUNCTION_TYPE_ROOT'},
  {child: 'SACRAL_FUNCTION', parent: 'FUNCTION_TYPE_ROOT'},
  {child: 'TRANSPORT_FUNCTION', parent: 'FUNCTION_TYPE_ROOT'},
  {child: 'ADMINISTRATIVE_FUNCTION', parent: 'FUNCTION_TYPE_ROOT'},
  {child: 'PRODUCTION_FUNCTION', parent: 'FUNCTION_TYPE_ROOT'}
] AS edge
MATCH (child:FunctionType {type_id: edge.child})
MATCH (parent:FunctionType {type_id: edge.parent})
MERGE (child)-[:SUBCLASS_OF]->(parent);

// ============================================================================
// OPTIONAL DERIVATION (SAFE): PLACE -> GEO SEMANTIC ROOT
// ============================================================================
// Requires PlaceType subgraph loaded by:
//   scripts/backbone/geographic/build_place_type_hierarchy.py --load-neo4j

MATCH (p:Place)-[:INSTANCE_OF_PLACE_TYPE]->(pt:PlaceType)-[:HAS_GEO_SEMANTIC_TYPE]->(gst:GeoSemanticType)
MERGE (p)-[r:HAS_GEO_SEMANTIC_TYPE {source: 'place_type_hierarchy_v1'}]->(gst)
SET r.updated = datetime();

// ============================================================================
// VERIFY
// ============================================================================

RETURN
  count { MATCH (:GeoSemanticType) } AS geo_semantic_types,
  count { MATCH (:ObjectType) } AS object_types,
  count { MATCH (:FunctionType) } AS function_types,
  count { MATCH (:Place)-[:HAS_GEO_SEMANTIC_TYPE]->(:GeoSemanticType) } AS place_geo_semantic_links;

