// Merge duplicate Place nodes by qid
// Run this BEFORE creating place_qid_unique constraint
// Requires: APOC (CALL apoc.refactor.mergeNodes)

MATCH (p:Place)
WHERE p.qid IS NOT NULL
WITH p.qid AS qid, collect(p) AS nodes
WHERE size(nodes) > 1
CALL apoc.refactor.mergeNodes(nodes) YIELD node
RETURN count(*) AS merged_groups;
