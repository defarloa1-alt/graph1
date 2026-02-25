// D-027: Delete staging node labels
// Run each statement separately in Neo4j Browser or cypher-shell
// Confirm counts before/after with: MATCH (n:Label) RETURN count(n)

// 1. GeoCoverageCandidate (357) - delete first (may reference PeriodCandidate)
MATCH (n:GeoCoverageCandidate) DETACH DELETE n;

// 2. PeriodCandidate (1,077)
MATCH (n:PeriodCandidate) DETACH DELETE n;

// 3. PlaceTypeTokenMap (212)
MATCH (n:PlaceTypeTokenMap) DETACH DELETE n;

// 4. FacetedEntity (360) - orphaned Tier 2 cipher hubs, 0 edges
MATCH (n:FacetedEntity) DETACH DELETE n;

// 5. StatusType (2) - orphaned enumeration stubs, no architectural value
MATCH (n:StatusType) DETACH DELETE n;
