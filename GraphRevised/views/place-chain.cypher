// A Place's chain in the gazetteer (27-GAZETTEER.md §3, "Visibility"): its ancient
// parents as Pleiades has them, and its modern chain up to the continent.
// Set the place with :param place => 'chr:entity:rome' in the Browser.
MATCH (place:Entity {id: $place})-[:AT_LOCATION]->(here:Location)
OPTIONAL MATCH ancient = (here)-[:WITHIN* {tree: 'ancient'}]->(:Location)
WITH place, here, collect(ancient) AS ancientPaths
// a Pleiades place reaches the modern tree through its bridge; a GeoNames one is already in it
OPTIONAL MATCH (here)-[bridge:MODERN_LOCATION]->(start:Location)
WITH place, here, ancientPaths, bridge, coalesce(start, CASE WHEN here.system = 'GeoNames' THEN here END) AS start
OPTIONAL MATCH modern = (start)-[:WITHIN* {tree: 'modern'}]->(top:Location)
WHERE NOT (top)-[:WITHIN {tree: 'modern'}]->()
RETURN place.label AS place,
       here.system + ' ' + here.identifier + ': ' + here.label AS location,
       [p IN ancientPaths | [n IN nodes(p) | n.label]] AS ancientChains,
       CASE WHEN bridge IS NULL THEN null
            ELSE bridge.how + coalesce(' via ' + bridge.viaLabel, '') + coalesce(', ' + toString(bridge.distanceKm) + ' km', '') END AS bridge,
       [n IN nodes(modern) | n.label] AS modernChain,
       here.location AS point
