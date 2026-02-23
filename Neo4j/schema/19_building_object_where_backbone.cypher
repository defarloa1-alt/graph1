// ============================================================================
// CHRYSTALLUM NEO4J SCHEMA: BUILDING OBJECT "WHAT-WHERE-WHEN" BACKBONE
// ============================================================================
// File: 19_building_object_where_backbone.cypher
// Purpose:
//   - Instantiate :Building nodes from man-made :Place records.
//   - Link building -> location (:LOCATED_IN -> :Place).
//   - Link building -> temporal backbone (:STARTS_IN_YEAR / :ENDS_IN_YEAR).
//   - Emit deterministic ID-based cipher key for object subgraph testing.
// Preconditions:
//   - PlaceType + GeoSemanticType loaded (18 + place_type loader).
//   - Year backbone exists.
// ============================================================================

CREATE CONSTRAINT building_entity_id_unique IF NOT EXISTS
FOR (b:Building) REQUIRE b.entity_id IS UNIQUE;

MATCH (p:Place {authority: 'Pleiades'})-[:INSTANCE_OF_PLACE_TYPE]->(:PlaceType)-[:HAS_GEO_SEMANTIC_TYPE]->(gst:GeoSemanticType {type_id:'MAN_MADE_STRUCTURE'})
WITH DISTINCT p, gst,
     CASE
       WHEN p.pleiades_id IS NOT NULL AND trim(toString(p.pleiades_id)) <> '' THEN 'bldg_pleiades_' + toString(p.pleiades_id)
       WHEN p.qid IS NOT NULL AND trim(toString(p.qid)) <> '' THEN 'bldg_qid_' + toString(p.qid)
       ELSE 'bldg_place_' + toString(id(p))
     END AS building_id,
     CASE WHEN p.min_date =~ '^-?\\d+(\\.\\d+)?$' THEN toInteger(toFloat(p.min_date)) ELSE null END AS start_year,
     CASE WHEN p.max_date =~ '^-?\\d+(\\.\\d+)?$' THEN toInteger(toFloat(p.max_date)) ELSE null END AS end_year
MERGE (b:Building {entity_id: building_id})
ON CREATE SET b.created = datetime()
SET b.label = coalesce(p.label, b.label),
    b.node_type = 'building_object',
    b.source = 'Pleiades',
    b.source_place_id = p.pleiades_id,
    b.source_place_uri = p.uri,
    b.wikidata_qid = coalesce(p.wikidata_qid, p.qid, b.wikidata_qid),
    b.start_year_hint = start_year,
    b.end_year_hint = end_year,
    b.object_where_cipher_key =
        'what=Building'
        + '|where=' + coalesce(toString(p.pleiades_id), coalesce(toString(p.qid), coalesce(toString(p.entity_id), '')))
        + '|qid=' + coalesce(toString(coalesce(p.wikidata_qid, p.qid)), '')
        + '|start=' + coalesce(toString(start_year), '')
        + '|end=' + coalesce(toString(end_year), ''),
    b.is_fully_federated = CASE
        WHEN p.pleiades_id IS NOT NULL
          AND trim(toString(p.pleiades_id)) <> ''
          AND coalesce(toString(p.wikidata_qid), toString(p.qid), '') =~ '^Q\\d+$'
          AND (start_year IS NOT NULL OR end_year IS NOT NULL)
        THEN true ELSE false END,
    b.updated = datetime()
MERGE (b)-[:LOCATED_IN {source:'pleiades_place'}]->(p)
MERGE (b)-[:HAS_GEO_SEMANTIC_TYPE {source:'place_type_hierarchy_v1'}]->(gst);

MATCH (b:Building)
OPTIONAL MATCH (ot:ObjectType {type_id:'BUILT_STRUCTURE'})
WITH b, ot WHERE ot IS NOT NULL
MERGE (b)-[:INSTANCE_OF_OBJECT_TYPE {source:'geo_semantic_extension'}]->(ot);

MATCH (b:Building)
WITH b, b.start_year_hint AS sy, b.end_year_hint AS ey
OPTIONAL MATCH (ys:Year {year: sy})
OPTIONAL MATCH (ye:Year {year: ey})
FOREACH (_ IN CASE WHEN ys IS NULL THEN [] ELSE [1] END |
    MERGE (b)-[:STARTS_IN_YEAR {source:'pleiades'}]->(ys))
FOREACH (_ IN CASE WHEN ye IS NULL THEN [] ELSE [1] END |
    MERGE (b)-[:ENDS_IN_YEAR {source:'pleiades'}]->(ye));

RETURN
  count { MATCH (:Building) } AS buildings,
  count { MATCH (:Building)-[:LOCATED_IN]->(:Place) } AS building_located_in_edges,
  count { MATCH (:Building)-[:STARTS_IN_YEAR]->(:Year) } AS building_start_year_edges,
  count { MATCH (:Building)-[:ENDS_IN_YEAR]->(:Year) } AS building_end_year_edges,
  count { MATCH (:Building {is_fully_federated:true}) } AS fully_federated_buildings;

