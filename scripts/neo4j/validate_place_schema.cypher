// Place Schema Validation
// Run: python scripts/neo4j/run_cypher_file.py scripts/neo4j/validate_place_schema.cypher
// Or paste into Neo4j Browser

// 1. Node counts
MATCH (p:Place) WITH count(p) AS total
MATCH (p:Place) WHERE p.pleiades_id IS NOT NULL WITH total, count(p) AS by_pleiades
MATCH (p:Place) WHERE p.qid IS NOT NULL WITH total, by_pleiades, count(p) AS by_qid
MATCH (p:Place) WHERE p.geonames_id IS NOT NULL WITH total, by_pleiades, by_qid, count(p) AS by_geonames
MATCH (n:PlaceName) WITH total, by_pleiades, by_qid, by_geonames, count(n) AS place_names
MATCH (l:Location) WITH total, by_pleiades, by_qid, by_geonames, place_names, count(l) AS locations
MATCH (pt:PlaceType) WITH total, by_pleiades, by_qid, by_geonames, place_names, locations, count(pt) AS place_types
MATCH (pp:Pleiades_Place) WITH total, by_pleiades, by_qid, by_geonames, place_names, locations, place_types, count(pp) AS pleiades_place
RETURN total AS place_total, by_pleiades AS place_pleiades_id, by_qid AS place_qid, by_geonames AS place_geonames_id,
       place_names, locations, place_types, pleiades_place;

// 2. Relationship counts
MATCH (p:Place)-[r:HAS_NAME]->() WITH count(r) AS has_name
MATCH (p:Place)-[r:HAS_LOCATION]->() WITH has_name, count(r) AS has_location
MATCH (p:Place)-[r:INSTANCE_OF_PLACE_TYPE]->() WITH has_name, has_location, count(r) AS instance_of_type
MATCH (p:Place)-[r:LOCATED_IN]->() WITH has_name, has_location, instance_of_type, count(r) AS located_in
MATCH (pp:Pleiades_Place)-[r:ALIGNED_WITH_GEO_BACKBONE]->() WITH has_name, has_location, instance_of_type, located_in, count(r) AS aligned_geo
RETURN has_name, has_location, instance_of_type, located_in, aligned_geo;

// 3. Place identification overlap (should have at least one of pleiades_id, qid, geonames_id)
MATCH (p:Place)
WHERE p.pleiades_id IS NULL AND p.qid IS NULL AND p.geonames_id IS NULL
RETURN count(p) AS place_without_id;

// 4. LOCATED_IN source breakdown
MATCH (c:Place)-[r:LOCATED_IN]->(p:Place)
WHERE c.pleiades_id IS NOT NULL
RETURN r.source AS loc_in_source, count(r) AS cnt
ORDER BY cnt DESC;

// 5. Sample Place with full chain (names, location, type, hierarchy)
MATCH (p:Place {pleiades_id: '423025'})
OPTIONAL MATCH (p)-[:HAS_NAME]->(n:PlaceName)
OPTIONAL MATCH (p)-[:HAS_LOCATION]->(l:Location)
OPTIONAL MATCH (p)-[:INSTANCE_OF_PLACE_TYPE]->(pt:PlaceType)
OPTIONAL MATCH (p)-[:LOCATED_IN*1..3]->(anc:Place)
RETURN p.pleiades_id, p.label, p.place_type, p.lat, p.long, p.min_date, p.max_date,
       collect(DISTINCT n.name_attested) AS names,
       count(DISTINCT l) AS location_count,
       collect(DISTINCT pt.type_id) AS place_types,
       [a IN collect(DISTINCT anc) | a.label + ' (' + coalesce(a.pleiades_id, a.qid, a.geonames_id, '') + ')'] AS hierarchy_chain;

// 6. Orphan check: PlaceName or Location without Place
MATCH (n:PlaceName) WHERE NOT (n)<-[:HAS_NAME]-(:Place) RETURN count(n) AS orphan_placenames;
MATCH (l:Location) WHERE NOT (l)<-[:HAS_LOCATION]-(:Place) RETURN count(l) AS orphan_locations;
