// ============================================================
// Self-Describing Subgraph — Diagnostic Queries
// Run each section in Neo4j Browser. See docs/SELF_DESCRIBING_SUBGRAPH_DESIGN.md
// ============================================================

// ---------------------------------------------------------------------------
// 1. Chrystallum-connected labels (what's in the system tree?)
// ---------------------------------------------------------------------------
MATCH (sys:Chrystallum)-[*..4]->(n)
RETURN labels(n) AS label, count(n) AS count
ORDER BY count DESC;


// ---------------------------------------------------------------------------
// 2. PropertyMapping — connected to system subgraph?
// ---------------------------------------------------------------------------
MATCH (n:PropertyMapping) 
OPTIONAL MATCH (sys:Chrystallum)-[*..10]->(n)
RETURN count(n) AS total_pm, count(sys) AS connected_to_system;


// ---------------------------------------------------------------------------
// 3. GeoCoverageCandidate — what does it point to? (CRITICAL for keep vs delete)
// ---------------------------------------------------------------------------
MATCH (gcc:GeoCoverageCandidate)-[r]->(n)
RETURN type(r) AS rel, labels(n) AS target, count(*) AS cnt
ORDER BY cnt DESC;


// ---------------------------------------------------------------------------
// 4. KnowledgeDomain — connections (merge into SubjectConceptRoot?)
// ---------------------------------------------------------------------------
MATCH (kd:KnowledgeDomain)
RETURN kd, [(kd)-[r]-(n) | {rel: type(r), label: labels(n), dir: "any"}] AS connections;


// ---------------------------------------------------------------------------
// 5. FacetedEntity — confirm orphaned (0 edges)
// ---------------------------------------------------------------------------
MATCH (n:FacetedEntity)
OPTIONAL MATCH (n)-[r]-()
RETURN count(n) AS total, count(r) AS with_edges;


// ---------------------------------------------------------------------------
// 6. PropertyMapping sample — runtime query or config?
// ---------------------------------------------------------------------------
MATCH (pm:PropertyMapping)-[:HAS_PRIMARY_FACET]->(f:Facet)
RETURN pm.property_id AS property, f.key AS primary_facet
LIMIT 10;


// ---------------------------------------------------------------------------
// 7. Policy and Threshold — read contents before delete
// ---------------------------------------------------------------------------
MATCH (n:Policy) RETURN n LIMIT 5;
MATCH (n:Threshold) RETURN n LIMIT 5;


// ---------------------------------------------------------------------------
// 8. Place nodes — any edges at all?
// ---------------------------------------------------------------------------
MATCH (p:Place)
OPTIONAL MATCH (p)-[r]-()
RETURN count(p) AS total_place, count(r) AS total_edges;
