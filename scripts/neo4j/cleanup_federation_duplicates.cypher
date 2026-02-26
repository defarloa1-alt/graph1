// CLEANUP 1: SYS_FederationSource duplicates
// 13 sources each duplicated. Delete higher-ID duplicate per source.
// Run via Neo4j Browser or: python scripts/neo4j/run_cypher_file.py
//
// DRY RUN: Replace DETACH DELETE with RETURN to preview
// MATCH (reg:SYS_FederationRegistry)-[:CONTAINS]->(f:SYS_FederationSource)
// WITH f.name AS name, collect(f) AS dupes
// WHERE size(dupes) > 1
// UNWIND range(1, size(dupes)-1) AS i
// WITH dupes[i] AS toDelete
// RETURN id(toDelete), toDelete.name
//
// EXECUTE: Keep lowest-id node per source, delete higher-id duplicates
MATCH (reg:SYS_FederationRegistry)-[:CONTAINS]->(f:SYS_FederationSource)
WITH f.name AS name, collect(f) AS dupes
WHERE size(dupes) > 1
UNWIND dupes AS d
WITH name, d ORDER BY id(d)
WITH name, collect(d) AS sorted
FOREACH (x IN tail(sorted) | DETACH DELETE x)
