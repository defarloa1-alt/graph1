// Neo4j Queries for Graph Overview
// Created: 2026-02-22
// Purpose: Best queries to visualize current graph state

// ═══════════════════════════════════════════════════════════════
// QUERY 1: Roman Republic + Direct Connections (RECOMMENDED START)
// ═══════════════════════════════════════════════════════════════

MATCH (rr:Entity {qid: 'Q17167'})-[r]-(connected)
RETURN rr, r, connected
LIMIT 100;

// Shows: Roman Republic at center with connections
// Good for: Visual exploration in Neo4j Browser


// ═══════════════════════════════════════════════════════════════
// QUERY 2: Sample Across Relationship Types
// ═══════════════════════════════════════════════════════════════

MATCH (a:Entity)-[r]->(b:Entity)
WITH type(r) as rel_type, collect({a:a, r:r, b:b}) as relationships
ORDER BY size(relationships) DESC
LIMIT 10
UNWIND relationships[0..5] as rel
RETURN rel.a, rel.r, rel.b;

// Shows: Top 10 relationship types with 5 examples each
// Good for: Understanding relationship diversity


// ═══════════════════════════════════════════════════════════════
// QUERY 3: Hierarchy Backbone (P31/P279/P361)
// ═══════════════════════════════════════════════════════════════

MATCH path = (e:Entity)-[:P31|P279|P361*1..3]->(class)
WHERE e.qid IN ['Q17167', 'Q1048', 'Q220', 'Q2277']
RETURN path;

// Shows: Classification and part-of chains for key entities
// Good for: Understanding hierarchical structure


// ═══════════════════════════════════════════════════════════════
// QUERY 4: Hub Entities (Most Connected) - FIXED
// ═══════════════════════════════════════════════════════════════

MATCH (hub:Entity)
OPTIONAL MATCH (hub)-[r]-()
WITH hub, count(r) as degree
WHERE degree > 0
ORDER BY degree DESC
LIMIT 20
MATCH (hub)-[rel]-(connected)
WITH hub, hub.qid as qid, hub.label as label, degree, 
     type(rel) as rel_type, collect(connected)[0..3] as samples
RETURN qid, label, degree, rel_type, samples
ORDER BY degree DESC;

// Shows: Top 20 most connected entities
// Good for: Finding hubs and central entities


// ═══════════════════════════════════════════════════════════════
// QUERY 5: Relationship Type Distribution (Table View)
// ═══════════════════════════════════════════════════════════════

MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC
LIMIT 30;

// Shows: What relationship types exist and their counts
// Good for: Understanding relationship composition


// ═══════════════════════════════════════════════════════════════
// QUERY 6: Connectivity Statistics
// ═══════════════════════════════════════════════════════════════

MATCH (e:Entity)
OPTIONAL MATCH (e)-[r]-()
WITH e, count(r) as degree
RETURN 
  count(e) as total_entities,
  min(degree) as min_connections,
  avg(degree) as avg_connections,
  max(degree) as max_connections,
  count(CASE WHEN degree = 0 THEN 1 END) as isolated,
  count(CASE WHEN degree > 0 THEN 1 END) as connected;

// Shows: Overall connectivity statistics
// Good for: Health check


// ═══════════════════════════════════════════════════════════════
// QUERY 7: Multi-Hop Discovery Test (Senator → Mollusk)
// ═══════════════════════════════════════════════════════════════

// Test if multi-hop paths exist
MATCH path = (start:Entity)-[*1..5]-(end:Entity)
WHERE start.label CONTAINS 'senator' 
  AND end.label CONTAINS 'mollusk'
RETURN path
LIMIT 1;

// Shows: Whether senator → mollusk path exists
// Good for: Validating multi-domain traversal


// ═══════════════════════════════════════════════════════════════
// RECOMMENDED STARTING POINT
// ═══════════════════════════════════════════════════════════════

// Start with Query 1 (Roman Republic visual)
// Then Query 5 (relationship types)
// Then Query 6 (connectivity stats)
// Then Query 4 (find hubs)
