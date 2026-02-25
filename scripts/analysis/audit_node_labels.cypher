// ============================================================
// Node Label Audit
// Count nodes per label and list relationship types for each.
// Run each section separately in Neo4j Browser or cypher-shell.
// ============================================================

// ---------------------------------------------------------------------------
// 1. Node count per label (sorted by count desc)
// ---------------------------------------------------------------------------
MATCH (n)
UNWIND labels(n) AS label
RETURN label, count(*) AS nodeCount
ORDER BY nodeCount DESC;


// ---------------------------------------------------------------------------
// 2. Relationship types per label (edges in/out for each label)
// ---------------------------------------------------------------------------
MATCH (n)-[r]->()
UNWIND labels(n) AS label
WITH label, type(r) AS relType, count(r) AS edgeCnt
RETURN label, relType, edgeCnt, "OUT" AS direction
UNION ALL
MATCH (n)<-[r]-()
UNWIND labels(n) AS label
WITH label, type(r) AS relType, count(r) AS edgeCnt
RETURN label, relType, edgeCnt, "IN" AS direction
ORDER BY label, relType;


// ---------------------------------------------------------------------------
// 3. Labels with zero relationships (orphan / isolated types)
// ---------------------------------------------------------------------------
MATCH (n)
UNWIND labels(n) AS lbl
WITH lbl, count(n) AS nodeCnt
WHERE NOT EXISTS {
  MATCH (x) WHERE lbl IN labels(x)
  MATCH (x)-[]-()
}
RETURN lbl AS label, nodeCnt
ORDER BY nodeCnt DESC;


// ---------------------------------------------------------------------------
// 4. Multi-label nodes (nodes with 2+ labels — may indicate overlap)
// ---------------------------------------------------------------------------
MATCH (n)
WITH labels(n) AS lbls
WHERE size(lbls) >= 2
RETURN lbls, count(*) AS cnt
ORDER BY cnt DESC
LIMIT 50;


// ---------------------------------------------------------------------------
// 5. Labels with node + edge counts (edgeCnt ~2x actual, edges counted from both ends)
// ---------------------------------------------------------------------------
MATCH (n)
UNWIND labels(n) AS lbl
WITH lbl, n
OPTIONAL MATCH (n)-[r]-()
WITH lbl, count(DISTINCT n) AS nodeCnt, count(r) AS edgeCnt
RETURN lbl AS label, nodeCnt, edgeCnt, (edgeCnt > 0) AS hasEdges
ORDER BY nodeCnt DESC;
