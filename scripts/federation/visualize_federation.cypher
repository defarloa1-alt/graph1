// Visualize Federation Subcluster Structure

// View complete structure
MATCH path = (c:Chrystallum)-[:HAS_SUBCLUSTER]->(cat:Federation:Category)-[:IS_COMPOSED_OF]->(fed:Federation:Organization)
RETURN path;

// View as table
MATCH (c:Chrystallum)-[:HAS_SUBCLUSTER]->(cat:Category)-[:IS_COMPOSED_OF]->(fed:Organization)
RETURN 
    c.label as Root,
    cat.label as Category,
    fed.label as Federation,
    fed.type as Type,
    fed.description as Description
ORDER BY fed.type, fed.label;

// Count structure
MATCH (c:Chrystallum)-[:HAS_SUBCLUSTER]->(cat)-[:IS_COMPOSED_OF]->(fed)
RETURN 
    c.label as Root,
    cat.label as Cluster,
    count(fed) as FederationCount;

