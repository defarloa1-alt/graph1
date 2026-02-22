// Verify and Fix Chrystallum → Federation Connection

// ============================================================================
// Check current state
// ============================================================================

// Check if Chrystallum exists
MATCH (c:Chrystallum)
RETURN c.label, c.id;

// Check if Federation category exists  
MATCH (f:Federation:Category)
RETURN f.label, f.id;

// Check if connection exists
MATCH (c:Chrystallum)-[r:HAS_FEDERATION_CLUSTER]->(f:Federation:Category)
RETURN c.label, type(r), f.label;

// ============================================================================
// Create/Fix the connection if needed
// ============================================================================

MATCH (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (fed_cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MERGE (c)-[:HAS_FEDERATION_CLUSTER {
    cluster_type: 'authority_systems',
    description: 'Federated authority systems and classification standards',
    federation_count: 9
}]->(fed_cat);

// ============================================================================
// Verify complete structure
// ============================================================================

// Should return 1 Chrystallum, 1 Federation category, 9 authority systems
MATCH (c:Chrystallum)
       -[:HAS_FEDERATION_CLUSTER]->
       (cat:Federation:Category)
       -[:IS_COMPOSED_OF]->
       (fed:Federation:AuthoritySystem)
RETURN 
    count(DISTINCT c) as chrystallum_nodes,
    count(DISTINCT cat) as federation_categories,
    count(DISTINCT fed) as authority_systems;

// View the tree structure
MATCH path = (c:Chrystallum)
             -[:HAS_FEDERATION_CLUSTER]->
             (cat:Federation:Category)
             -[:IS_COMPOSED_OF]->
             (fed:Federation:AuthoritySystem)
RETURN path;

// Table view of all federations
MATCH (c:Chrystallum)-[:HAS_FEDERATION_CLUSTER]->(cat)-[:IS_COMPOSED_OF]->(fed:Federation:AuthoritySystem)
RETURN 
    c.label as Root,
    cat.label as Category,
    fed.label as Federation,
    fed.role as Role,
    fed.type as Type
ORDER BY fed.id;

