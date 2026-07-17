// ============================================================================
// Property Mapping Test Queries - Clean Cypher (No Markdown)
// Created: 2026-02-22 by QA Agent
// Usage: Copy/paste individual queries into Neo4j Browser
// ============================================================================

// ----------------------------------------------------------------------------
// Query 1: Get facet for a specific property
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping {property_id: 'P39'})
RETURN pm.primary_facet, pm.confidence, pm.property_label;


// ----------------------------------------------------------------------------
// Query 2: Route to agent (Property -> Facet -> Agent)
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping {property_id: 'P39'})
MATCH (pm)-[:HAS_PRIMARY_FACET]->(f:Facet)
MATCH (agent:Agent)-[:ASSIGNED_TO_FACET]->(f)
WHERE agent.subject_id = 'Q17167'
RETURN agent.id, f.key;


// ----------------------------------------------------------------------------
// Query 3: List all MILITARY properties
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping {primary_facet: 'MILITARY'})
RETURN pm.property_id, pm.property_label, pm.confidence
ORDER BY pm.confidence DESC;


// ----------------------------------------------------------------------------
// Query 4: Check imports by resolution method
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping)
WHERE pm.resolved_by IN ['claude', 'base_mapping']
RETURN pm.resolved_by as method, count(pm) as count;


// ----------------------------------------------------------------------------
// Query 5: Facet distribution (top 10)
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping)
RETURN pm.primary_facet as facet, count(pm) as count
ORDER BY count DESC
LIMIT 10;


// ----------------------------------------------------------------------------
// Query 6: Multi-facet properties
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping)
WHERE pm.secondary_facets IS NOT NULL AND pm.secondary_facets <> ''
RETURN pm.property_id, pm.property_label, pm.primary_facet, pm.secondary_facets
LIMIT 20;


// ----------------------------------------------------------------------------
// Query 7: High confidence properties
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping)
WHERE pm.confidence >= 0.9
RETURN pm.property_id, pm.property_label, pm.primary_facet, pm.confidence
ORDER BY pm.confidence DESC
LIMIT 20;


// ----------------------------------------------------------------------------
// Query 8: Authority control properties
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping {is_authority_control: true})
RETURN pm.property_id, pm.property_label, pm.primary_facet
LIMIT 20;


// ----------------------------------------------------------------------------
// Query 9: Claude-resolved properties (high quality)
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping {resolved_by: 'claude'})
WHERE pm.confidence >= 0.9
RETURN pm.property_id, pm.property_label, pm.primary_facet, pm.confidence
ORDER BY pm.confidence DESC
LIMIT 20;


// ----------------------------------------------------------------------------
// Query 10: Total count verification
// ----------------------------------------------------------------------------
MATCH (pm:PropertyMapping)
RETURN count(pm) as total_properties;


// ============================================================================
// PARAMETERIZED VERSIONS (For Python/Driver Use)
// ============================================================================

// Example: Get facet for any property
// In Python:
// session.run("MATCH (pm:PropertyMapping {property_id: $prop}) RETURN pm.primary_facet", prop="P39")

// Example: Route to agent for any property and subject
// session.run("""
//   MATCH (pm:PropertyMapping {property_id: $prop})
//   MATCH (pm)-[:HAS_PRIMARY_FACET]->(f:Facet)
//   MATCH (agent:Agent)-[:ASSIGNED_TO_FACET]->(f)
//   WHERE agent.subject_id = $subject
//   RETURN agent.id, f.key
// """, prop="P39", subject="Q17167")
