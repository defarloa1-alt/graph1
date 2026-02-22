// Fix CIDOC relationship
MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (cidoc:Federation:AuthoritySystem {id: 'FED_CIDOC_CRM'})
MERGE (cat)-[:IS_COMPOSED_OF {
    federation_type: 'ontology_standard',
    priority: 8
}]->(cidoc);

// Verify structure
MATCH (c:Chrystallum)-[:HAS_FEDERATION_CLUSTER]->(cat:Federation:Category)-[:IS_COMPOSED_OF]->(fed:Federation:AuthoritySystem)
RETURN 
    c.label as Root,
    cat.label as Category,
    fed.label as Federation,
    fed.role as Role
ORDER BY fed.id;

