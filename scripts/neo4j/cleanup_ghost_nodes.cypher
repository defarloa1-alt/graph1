// CLEANUP 2: 10 unlabelled ghost nodes
// Nodes with no labels and no properties — orphaned from previous merge/import
//
// DRY RUN: Preview first
// MATCH (n) WHERE size(labels(n)) = 0 RETURN count(n) AS ghost_count, collect(id(n)) AS ids
//
// EXECUTE:
MATCH (n) WHERE size(labels(n)) = 0
DETACH DELETE n
