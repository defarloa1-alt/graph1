// Cleanup: Entity nodes with qid = 32-char hex (id_hash mistaken for Wikidata QID)
// These have no dprr_id, empty label, and block person harvest discovery.
// Run via: python Neo4j/schema/run_cypher_file.py scripts/neo4j/cleanup_hash_qid_entities.cypher
//
// Step 1: Count (run first to verify)
MATCH (e:Entity)
WHERE e.qid =~ '[0-9a-f]{32}' AND e.qid IS NOT NULL
RETURN count(e) AS hash_qid_count;

// Step 2: Delete (uncomment to execute)
// MATCH (e:Entity)
// WHERE e.qid =~ '[0-9a-f]{32}' AND e.qid IS NOT NULL
// DETACH DELETE e;
