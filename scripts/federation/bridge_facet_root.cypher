// ============================================================================
// BRIDGE: FacetRoot for bootstrap_subject_concept_agents compatibility
// ============================================================================
// create_facets_cluster.cypher creates HAS_FACET_CLUSTER → Facets:Category → CanonicalFacet.
// bootstrap_subject_concept_agents.cypher expects HAS_FACET_ROOT → FacetRoot → Facet.
// This bridge creates FacetRoot and links it to existing CanonicalFacet nodes
// (which have :Facet label), so bootstrap can find them.
//
// Run AFTER create_facets_cluster.cypher, BEFORE bootstrap_subject_concept_agents.cypher
// ============================================================================

MERGE (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MERGE (facet_root:FacetRoot {id: 'facet_root'})
ON CREATE SET facet_root.label = 'Canonical Facets', facet_root.created_at = datetime()
MERGE (c)-[:HAS_FACET_ROOT]->(facet_root);

MATCH (cat:Facets:Category {id: 'FACETS_CATEGORY'})-[:IS_COMPOSED_OF]->(f:CanonicalFacet)
MATCH (facet_root:FacetRoot {id: 'facet_root'})
MERGE (facet_root)-[:HAS_FACET]->(f);
