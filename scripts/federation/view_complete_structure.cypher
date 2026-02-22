// View Complete Chrystallum Federation Structure

// ============================================================================
// Option 1: Visual Graph (for Neo4j Browser visualization)
// ============================================================================

MATCH path1 = (c:Chrystallum)-[:HAS_FEDERATION_CLUSTER]->(fed_cat:Federation:Category)-[:IS_COMPOSED_OF]->(auth:Federation:AuthoritySystem)
OPTIONAL MATCH path2 = (c)-[:HAS_FACET_CLUSTER]->(facet_cat:Facets:Category)-[:IS_COMPOSED_OF]->(facet:CanonicalFacet)
RETURN path1, path2;

// ============================================================================
// Option 2: Table View (summary)
// ============================================================================

MATCH (c:Chrystallum)
OPTIONAL MATCH (c)-[:HAS_FEDERATION_CLUSTER]->(fed_cat)-[:IS_COMPOSED_OF]->(auth)
OPTIONAL MATCH (c)-[:HAS_FACET_CLUSTER]->(facet_cat)-[:IS_COMPOSED_OF]->(facet)
RETURN 
    c.label as Root,
    count(DISTINCT fed_cat) as FederationClusters,
    count(DISTINCT auth) as AuthoritySystems,
    count(DISTINCT facet_cat) as FacetClusters,
    count(DISTINCT facet) as CanonicalFacets;

// ============================================================================
// Option 3: Detailed Tree View
// ============================================================================

// Federations
MATCH (c:Chrystallum)-[:HAS_FEDERATION_CLUSTER]->(cat)-[:IS_COMPOSED_OF]->(fed:Federation:AuthoritySystem)
WITH 'FEDERATIONS' as cluster_type, collect({
    name: fed.label,
    role: fed.role,
    coverage: fed.coverage
}) as items
RETURN cluster_type, items

UNION

// Facets
MATCH (c:Chrystallum)-[:HAS_FACET_CLUSTER]->(cat)-[:IS_COMPOSED_OF]->(facet:CanonicalFacet)
WITH 'FACETS' as cluster_type, collect({
    key: facet.key,
    label: facet.label,
    description: facet.description
}) as items
RETURN cluster_type, items;

// ============================================================================
// Option 4: Count all subclusters
// ============================================================================

MATCH (c:Chrystallum)-[r]->(cluster)
RETURN 
    c.label as Root,
    type(r) as Relationship,
    cluster.label as Cluster,
    labels(cluster) as ClusterTypes;

