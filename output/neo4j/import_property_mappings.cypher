// ============================================================================
// PROPERTY FACET MAPPING - NEO4J IMPORT
// ============================================================================
// 
// Imports complete property→facet mapping system into Neo4j
// Source: CSV/property_mappings/property_facet_mapping_HYBRID.csv
// Coverage: 500 properties, 100% mapped to Chrystallum's 18 facets
// Resolution: Base mapping (248) + Claude semantic (252)
//
// Generated: 2026-02-22
// Status: Production Ready
// ============================================================================

// ============================================================================
// STEP 1: CREATE INDEXES
// ============================================================================

// Primary indexes for PropertyMapping nodes
CREATE INDEX property_mapping_pid_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.property_id);
CREATE INDEX property_mapping_facet_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.primary_facet);
CREATE INDEX property_mapping_confidence_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.confidence);

// Composite index for facet + confidence queries
CREATE INDEX property_mapping_facet_conf_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.primary_facet, pm.confidence);

// Authority control flag index
CREATE INDEX property_mapping_authority_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.is_authority_control);

// Historical flag index
CREATE INDEX property_mapping_historical_idx IF NOT EXISTS FOR (pm:PropertyMapping) ON (pm.is_historical);

// PropertyType indexes (for Q107649491 classifications)
CREATE INDEX property_type_qid_idx IF NOT EXISTS FOR (pt:PropertyType) ON (pt.qid);
CREATE INDEX property_type_label_idx IF NOT EXISTS FOR (pt:PropertyType) ON (pt.label);

// Facet node indexes (if not already exist)
CREATE INDEX facet_key_idx IF NOT EXISTS FOR (f:Facet) ON (f.key);

// ============================================================================
// STEP 2: IMPORT PROPERTY MAPPINGS
// ============================================================================

// Load property mappings from CSV
LOAD CSV WITH HEADERS FROM 'file:///property_facet_mapping_HYBRID.csv' AS row

// Create PropertyMapping node
CREATE (pm:PropertyMapping {
  property_id: row.property_id,
  property_label: row.property_label,
  property_description: row.property_description,
  
  // Facet assignments
  primary_facet: row.primary_facet,
  secondary_facets: row.secondary_facets,
  all_facets: row.all_facets,
  
  // Metadata
  confidence: toFloat(row.confidence),
  resolved_by: row.resolved_by,
  
  // Flags
  is_historical: row.is_historical = 'True',
  is_authority_control: row.is_authority_control = 'True',
  
  // Property type classifications
  type_qids: row.type_qids,
  type_labels: row.type_labels,
  type_count: toInteger(row.type_count),
  
  // Timestamps
  imported_at: datetime(),
  mapping_version: '1.0',
  source: 'wikidata_property_types_q107649491'
});

// ============================================================================
// STEP 3: LINK TO FACET NODES
// ============================================================================

// Link each PropertyMapping to its primary Facet node
MATCH (pm:PropertyMapping)
WHERE pm.primary_facet IS NOT NULL AND pm.primary_facet <> 'UNKNOWN'
MATCH (f:Facet {key: pm.primary_facet})
MERGE (pm)-[:HAS_PRIMARY_FACET]->(f);

// Link to secondary facets (if any)
MATCH (pm:PropertyMapping)
WHERE pm.secondary_facets IS NOT NULL AND pm.secondary_facets <> ''
UNWIND split(pm.secondary_facets, ',') AS facet_key
MATCH (f:Facet {key: facet_key})
MERGE (pm)-[:HAS_SECONDARY_FACET]->(f);

// ============================================================================
// STEP 4: CREATE PROPERTY TYPE REGISTRY (Optional Enhancement)
// ============================================================================

// Load Q107649491 property type classifications
LOAD CSV WITH HEADERS FROM 'file:///Q107649491_property_types_CLEAN.csv' AS row
MERGE (pt:PropertyType {qid: row.qid})
ON CREATE SET
  pt.label = row.label,
  pt.description = row.description,
  pt.meta_type = 'property_classification',
  pt.parent_qid = 'Q107649491',
  pt.imported_at = datetime();

// Link PropertyMappings to their PropertyTypes
MATCH (pm:PropertyMapping)
WHERE pm.type_qids IS NOT NULL AND pm.type_qids <> ''
UNWIND split(pm.type_qids, ',') AS type_qid
MATCH (pt:PropertyType {qid: type_qid})
MERGE (pm)-[:HAS_TYPE]->(pt);

// ============================================================================
// STEP 5: CREATE DOMAIN PROFILES (Optional Enhancement)
// ============================================================================

// Create DomainProfile nodes for different research domains
CREATE (dp:DomainProfile {
  domain_id: 'ancient_history',
  domain_name: 'Ancient & Medieval History',
  temporal_scope: '-3000 to 1800',
  priority_facets: 'MILITARY,POLITICAL,RELIGIOUS,BIOGRAPHIC,ARCHAEOLOGICAL',
  description: 'Ancient Mediterranean and Medieval European history',
  created_at: datetime()
});

CREATE (dp:DomainProfile {
  domain_id: 'technology',
  domain_name: 'Technology & Computing',
  temporal_scope: '1945 to present',
  priority_facets: 'TECHNOLOGICAL,SCIENTIFIC,ECONOMIC',
  description: 'Computing, software, and technology history',
  created_at: datetime()
});

CREATE (dp:DomainProfile {
  domain_id: 'biology',
  domain_name: 'Biological Sciences',
  temporal_scope: 'all_time',
  priority_facets: 'SCIENTIFIC,ENVIRONMENTAL',
  description: 'Biology, taxonomy, ecology, conservation',
  created_at: datetime()
});

// Link high-priority properties to appropriate domains
// Ancient History domain
MATCH (dp:DomainProfile {domain_id: 'ancient_history'})
MATCH (pm:PropertyMapping)
WHERE pm.property_id IN ['P19', 'P20', 'P39', 'P241', 'P410', 'P509', 'P569', 'P570', 'P580', 'P582', 'P607']
   OR pm.is_historical = true
   OR pm.primary_facet IN ['MILITARY', 'POLITICAL', 'RELIGIOUS', 'ARCHAEOLOGICAL', 'BIOGRAPHIC']
MERGE (dp)-[:PRIORITIZES {tier: 1, boost: 1.0}]->(pm);

// Technology domain
MATCH (dp:DomainProfile {domain_id: 'technology'})
MATCH (pm:PropertyMapping)
WHERE pm.property_id IN ['P348', 'P408', 'P487', 'P404']
   OR pm.primary_facet IN ['TECHNOLOGICAL']
MERGE (dp)-[:PRIORITIZES {tier: 1, boost: 1.0}]->(pm);

// Biology domain
MATCH (dp:DomainProfile {domain_id: 'biology'})
MATCH (pm:PropertyMapping)
WHERE pm.property_id IN ['P181', 'P183', 'P225', 'P405', 'P784', 'P787', 'P830']
   OR pm.property_label CONTAINS 'taxon'
   OR pm.property_label CONTAINS 'species'
MERGE (dp)-[:PRIORITIZES {tier: 1, boost: 1.0}]->(pm);

// ============================================================================
// STEP 6: CREATE HELPER VIEWS (Optional)
// ============================================================================

// Create a convenient lookup function (if Neo4j supports)
// Alternative: Use simple MATCH patterns in application code

// ============================================================================
// VERIFICATION QUERIES
// ============================================================================

// Count total property mappings
// MATCH (pm:PropertyMapping) RETURN count(pm) as total;
// Expected: 500

// Count by facet
// MATCH (pm:PropertyMapping)
// RETURN pm.primary_facet as facet, count(pm) as count
// ORDER BY count DESC;

// Get high-confidence properties
// MATCH (pm:PropertyMapping)
// WHERE pm.confidence >= 0.8
// RETURN pm.property_id, pm.property_label, pm.primary_facet, pm.confidence
// ORDER BY pm.confidence DESC
// LIMIT 20;

// Get authority control properties
// MATCH (pm:PropertyMapping {is_authority_control: true})
// RETURN pm.property_id, pm.property_label, pm.primary_facet;

// Get properties for a specific facet
// MATCH (pm:PropertyMapping {primary_facet: 'MILITARY'})
// RETURN pm.property_id, pm.property_label, pm.confidence
// ORDER BY pm.confidence DESC;

// Get historical properties
// MATCH (pm:PropertyMapping {is_historical: true})
// RETURN pm.property_id, pm.property_label, pm.primary_facet;

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

// Example 1: Route property to facet agent
// MATCH (pm:PropertyMapping {property_id: 'P241'})
// MATCH (f:Facet {key: pm.primary_facet})
// MATCH (agent:Agent)-[:ASSIGNED_TO_FACET]->(f)
// RETURN agent.id as facet_agent;

// Example 2: Get all properties for a facet
// MATCH (f:Facet {key: 'MILITARY'})<-[:HAS_PRIMARY_FACET]-(pm:PropertyMapping)
// RETURN pm.property_id, pm.property_label
// ORDER BY pm.confidence DESC;

// Example 3: Multi-facet property routing
// MATCH (pm:PropertyMapping {property_id: 'P189'})
// MATCH (pm)-[:HAS_PRIMARY_FACET]->(pf:Facet)
// MATCH (pm)-[:HAS_SECONDARY_FACET]->(sf:Facet)
// RETURN pf.key as primary, collect(sf.key) as secondary;

// Example 4: Domain-specific property filtering
// MATCH (dp:DomainProfile {domain_id: 'ancient_history'})-[:PRIORITIZES]->(pm:PropertyMapping)
// RETURN pm.property_id, pm.property_label, pm.primary_facet
// ORDER BY pm.confidence DESC;

// ============================================================================
// END OF IMPORT SCRIPT
// ============================================================================
//
// Total Nodes Created:
// - PropertyMapping: 500
// - PropertyType: 500 (optional)
// - DomainProfile: 3 (optional)
//
// Total Relationships Created:
// - HAS_PRIMARY_FACET: 500
// - HAS_SECONDARY_FACET: ~150 (varies)
// - HAS_TYPE: ~1500 (avg 3 types per property)
// - PRIORITIZES: ~150 (domain-specific)
//
// ============================================================================
