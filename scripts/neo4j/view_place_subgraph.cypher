// ============================================================================
// VIEW PLACE SUBGRAPH
// ============================================================================
// For Neo4j Browser: paste and run ONE block. Returns nodes/relationships for graph viz.
// ============================================================================

// 1. Place hierarchy chains (Place -[:LOCATED_IN]-> Place, up to 3 levels)
//    Best for graph viz: shows city -> region -> country
MATCH path = (child:Place)-[:LOCATED_IN*1..3]->(top:Place)
WHERE child.pleiades_id IS NOT NULL AND NOT (top)-[:LOCATED_IN]->()
RETURN path
LIMIT 15;

// ============================================================================
// 2. Single Place + neighborhood (Rome 423025)
// ============================================================================
/*
MATCH (p:Place {pleiades_id: '423025'})
OPTIONAL MATCH (p)-[r1]-(x)
WHERE type(r1) IN ['HAS_NAME', 'HAS_LOCATION', 'INSTANCE_OF_PLACE_TYPE', 'LOCATED_IN']
   OR (x:Pleiades_Place AND type(r1) = 'ALIGNED_WITH_GEO_BACKBONE')
RETURN p, r1, x;
*/

// ============================================================================
// 3. Pleiades_Place -> Place alignment (sample)
// ============================================================================
/*
MATCH (pp:Pleiades_Place)-[r:ALIGNED_WITH_GEO_BACKBONE]->(p:Place)
RETURN pp, r, p LIMIT 25;
*/

// ============================================================================
// 4. PlaceType taxonomy (if populated)
// ============================================================================
/*
MATCH (pt:PlaceType)
OPTIONAL MATCH (pt)-[r:SUBCLASS_OF]->(parent:PlaceType)
RETURN pt, r, parent;
*/
