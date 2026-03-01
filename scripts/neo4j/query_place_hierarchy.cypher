// Place hierarchy sample - run with: python scripts/neo4j/run_cypher_file.py scripts/neo4j/query_place_hierarchy.cypher
// Or use Neo4j Browser / Bloom

// 1. LOCATED_IN examples: Pleiades Place -> parent (Wikidata qid)
MATCH (c:Place)-[:LOCATED_IN]->(p:Place)
WHERE c.pleiades_id IS NOT NULL
RETURN c.label AS child, c.pleiades_id, p.label AS parent, p.qid AS parent_qid
LIMIT 10;
