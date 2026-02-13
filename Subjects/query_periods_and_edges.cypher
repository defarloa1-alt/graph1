// Cypher Queries to View Periods and Their Edges

// ============================================================================
// Query 1: Count all periods and their relationships
// ============================================================================
MATCH (p:Period)
OPTIONAL MATCH (p)-[r]->(target)
RETURN 
    count(DISTINCT p) as total_periods,
    count(r) as total_relationships,
    collect(DISTINCT type(r)) as relationship_types
;

// ============================================================================
// Query 2: View periods with all their edges (visual graph)
// ============================================================================
MATCH (p:Period)
OPTIONAL MATCH (p)-[r]->(target)
RETURN p, r, target
LIMIT 50
;

// ============================================================================
// Query 3: Show periods grouped by facet type
// ============================================================================
MATCH (p:Period)-[r]->(f:Facet)
RETURN 
    labels(f) as facet_type,
    count(p) as period_count,
    collect(p.label)[0..5] as sample_periods
ORDER BY period_count DESC
;

// ============================================================================
// Query 4: Sample periods with complete structure
// ============================================================================
MATCH (p:Period)
OPTIONAL MATCH (p)-[:STARTS_IN]->(start:Year)
OPTIONAL MATCH (p)-[:ENDS_IN]->(end:Year)
OPTIONAL MATCH (p)-[facet_rel]->(f:Facet)
OPTIONAL MATCH (p)-[:LOCATED_IN]->(place:Place)
RETURN 
    p.label as period,
    p.start_year as start,
    p.end_year as end,
    type(facet_rel) as facet_relationship,
    labels(f) as facet_type,
    place.qid as location
LIMIT 20
;

// ============================================================================
// Query 5: Periods by primary facet (detailed breakdown)
// ============================================================================
MATCH (p:Period)-[r]->(f)
WHERE f:Facet
WITH labels(f)[0] as facet_label, type(r) as rel_type, count(p) as count
RETURN facet_label, rel_type, count
ORDER BY count DESC
;

// ============================================================================
// Query 6: Full subgraph for one period (example)
// ============================================================================
MATCH (p:Period {label: 'Habsburg Netherlands'})
OPTIONAL MATCH path1 = (p)-[:STARTS_IN]->(start:Year)
OPTIONAL MATCH path2 = (p)-[:ENDS_IN]->(end:Year)
OPTIONAL MATCH path3 = (p)-[facet_rel]->(f:Facet)
OPTIONAL MATCH path4 = (p)-[:LOCATED_IN]->(place:Place)
OPTIONAL MATCH path5 = (p)-[:PRECEDED_BY]->(prev:Period)
OPTIONAL MATCH path6 = (p)-[:FOLLOWED_BY]->(next:Period)
RETURN p, path1, path2, path3, path4, path5, path6
;

// ============================================================================
// Query 7: All relationship types from Period nodes
// ============================================================================
MATCH (p:Period)-[r]->()
RETURN type(r) as relationship_type, count(*) as count
ORDER BY count DESC
;

// ============================================================================
// Query 8: Periods with their complete edge list
// ============================================================================
MATCH (p:Period)
OPTIONAL MATCH (p)-[r]->(target)
WITH p, collect({
    relationship: type(r),
    target_label: labels(target)[0],
    target_property: COALESCE(target.label, target.value, target.qid)
}) as edges
RETURN 
    p.label as period,
    p.start_year as start,
    p.end_year as end,
    edges
LIMIT 10
;

// ============================================================================
// Query 9: Visual graph of periods and facets
// ============================================================================
MATCH (p:Period)-[r]->(f:Facet)
RETURN p, r, f
LIMIT 100
;

// ============================================================================
// Query 10: Check period temporal chain
// ============================================================================
MATCH (p:Period)-[:PRECEDED_BY|FOLLOWED_BY]-(other:Period)
RETURN p.label, type(r) as relationship, other.label
LIMIT 20
;

