// Create Federation Subcluster Structure
// Copy-paste this into Neo4j Browser

// Step 1: Create Chrystallum root node
MERGE (c:Chrystallum:Root {
    id: 'CHRYSTALLUM_ROOT'
})
SET c.label = 'Chrystallum',
    c.type = 'knowledge_graph_root',
    c.description = 'Root node of the Chrystallum knowledge graph';

// Step 2: Create Federation category node
MERGE (cat:Federation:Category {
    id: 'FEDERATION_CATEGORY'
})
SET cat.label = 'Federation',
    cat.type = 'organizational_category',
    cat.description = 'Category node for all federation entities';

// Step 3: Link Chrystallum to Federation category
MATCH (c:Chrystallum {id: 'CHRYSTALLUM_ROOT'})
MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MERGE (c)-[:HAS_SUBCLUSTER {
    cluster_type: 'federation',
    description: 'Federation organizational subcluster'
}]->(cat);

// Step 4: Create potential federation instances
MERGE (fed1:Federation:Organization {id: 'FED_EARTH'})
SET fed1.label = 'Earth Federation',
    fed1.type = 'planetary',
    fed1.description = 'Global planetary federation of Earth',
    fed1.federation_status = 'potential';

MERGE (fed2:Federation:Organization {id: 'FED_UNITED_NATIONS'})
SET fed2.label = 'United Nations',
    fed2.type = 'international',
    fed2.description = 'International organization for cooperation',
    fed2.federation_status = 'actual';

MERGE (fed3:Federation:Organization {id: 'FED_EUROPEAN_UNION'})
SET fed3.label = 'European Union',
    fed3.type = 'regional',
    fed3.description = 'Political and economic union of European states',
    fed3.federation_status = 'actual';

MERGE (fed4:Federation:Organization {id: 'FED_AFRICAN_UNION'})
SET fed4.label = 'African Union',
    fed4.type = 'regional',
    fed4.description = 'Continental union of African states',
    fed4.federation_status = 'actual';

MERGE (fed5:Federation:Organization {id: 'FED_ASEAN'})
SET fed5.label = 'ASEAN',
    fed5.type = 'regional',
    fed5.description = 'Association of Southeast Asian Nations',
    fed5.federation_status = 'actual';

// Step 5: Link Federation category to instances (IS_COMPOSED_OF)
MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (fed1:Federation:Organization {id: 'FED_EARTH'})
MERGE (cat)-[:IS_COMPOSED_OF {member_type: 'planetary'}]->(fed1);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (fed2:Federation:Organization {id: 'FED_UNITED_NATIONS'})
MERGE (cat)-[:IS_COMPOSED_OF {member_type: 'international'}]->(fed2);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (fed3:Federation:Organization {id: 'FED_EUROPEAN_UNION'})
MERGE (cat)-[:IS_COMPOSED_OF {member_type: 'regional'}]->(fed3);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (fed4:Federation:Organization {id: 'FED_AFRICAN_UNION'})
MERGE (cat)-[:IS_COMPOSED_OF {member_type: 'regional'}]->(fed4);

MATCH (cat:Federation:Category {id: 'FEDERATION_CATEGORY'})
MATCH (fed5:Federation:Organization {id: 'FED_ASEAN'})
MERGE (cat)-[:IS_COMPOSED_OF {member_type: 'regional'}]->(fed5);

// Verification
MATCH path = (c:Chrystallum)-[:HAS_SUBCLUSTER]->(cat:Federation:Category)-[:IS_COMPOSED_OF]->(fed:Federation:Organization)
RETURN path;

