// ============================================================================
// SUBJECT CONCEPT OPERATIONS - Comprehensive Cypher Queries
// ============================================================================
// Purpose: Core queries for managing SubjectConcepts in Chrystallum
// Version: 1.0
// Date: 2026-02-20
// ============================================================================


// ============================================================================
// PART 1: SUBJECT CONCEPT CREATION & REGISTRATION
// ============================================================================

// Create a new SubjectConcept with full authority federation
// Required: subject_id, label, primary_facet
// Optional: qid, lcsh_id, fast_id, lcc_class, related_facets
CREATE (sc:SubjectConcept {
  subject_id: 'subj_roman_republic_q17167',
  label: 'Roman Republic',
  primary_facet: 'POLITICAL',
  related_facets: ['MILITARY', 'SOCIAL', 'ECONOMIC'],
  
  // Wikidata federation
  qid: 'Q17167',
  
  // Library authorities
  lcsh_id: 'sh85115087',
  fast_id: 'fst01204885',
  lcc_class: 'DG241-269',
  
  // Status & metadata
  status: 'approved',
  created_at: datetime(),
  created_by: 'sca_bootstrap',
  confidence: 0.95,
  
  // Descriptive
  description: 'Ancient Roman state and civilization (509-27 BCE)',
  temporal_scope: '-0509/-0027',
  geographic_scope: 'Mediterranean, Italy'
})
RETURN sc;


// Register SubjectConcept in SubjectConceptRegistry
MATCH (sys:Chrystallum)
MATCH (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)
MATCH (sc_root)-[:HAS_SUBJECT_REGISTRY]->(registry:SubjectConceptRegistry)
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (registry)-[:CONTAINS]->(sc)
RETURN registry, sc;


// Create facet-specific agent for SubjectConcept
// Pattern: SFA_{subject_id}_{facet_key}
MATCH (sys:Chrystallum)
MATCH (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)
MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg:AgentRegistry)
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
CREATE (agent:Agent {
  id: 'SFA_subj_roman_republic_q17167_MILITARY',
  agent_type: 'SubjectFacetAgent',
  facet: 'MILITARY',
  subject_concept_id: 'subj_roman_republic_q17167',
  status: 'active',
  created_at: datetime(),
  model: 'llama-3.1-sonar-large-128k-online',
  capabilities: ['analysis', 'discovery', 'classification']
})
MERGE (agent_reg)-[:HAS_AGENT]->(agent)
MERGE (agent)-[:ANALYZES]->(sc)
RETURN agent;


// ============================================================================
// PART 2: SUBJECT CONCEPT FEDERATION & ENRICHMENT
// ============================================================================

// Link SubjectConcept to LCSH authority
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (lcsh:LCSH_Subject {lcsh_id: 'sh85115087'})
ON CREATE SET 
  lcsh.heading = 'Rome--History--Republic, 265-30 B.C.',
  lcsh.created_at = datetime()
MERGE (sc)-[:HAS_LCSH_AUTHORITY]->(lcsh)
RETURN sc, lcsh;


// Link SubjectConcept to FAST authority
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (fast:FAST_Subject {fast_id: 'fst01204885'})
ON CREATE SET 
  fast.preferred_label = 'Rome--History--Republic, 265-30 B.C.',
  fast.created_at = datetime()
MERGE (sc)-[:HAS_FAST_AUTHORITY]->(fast)
RETURN sc, fast;


// Link SubjectConcept to LCC classification
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (lcc:LCC_Class {code: 'DG241-269'})
ON CREATE SET 
  lcc.label = 'Rome--History--Republic',
  lcc.created_at = datetime()
MERGE (sc)-[:CLASSIFIED_BY_LCC]->(lcc)
RETURN sc, lcc;


// Enrich SubjectConcept with Wikidata properties (external SPARQL query result)
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
SET 
  sc.wikidata_instance_of = 'Q15304597',  // ancient civilization
  sc.wikidata_part_of = 'Q1747689',        // Ancient Rome
  sc.wikidata_start_time = '-0509-01-01',
  sc.wikidata_end_time = '-0027-01-01',
  sc.wikidata_enriched_at = datetime()
RETURN sc;


// ============================================================================
// PART 3: SUBJECT CONCEPT HIERARCHIES
// ============================================================================

// Create parent-child relationship between SubjectConcepts
MATCH (parent:SubjectConcept {subject_id: 'subj_ancient_rome_q1747689'})
MATCH (child:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (child)-[:PART_OF]->(parent)
RETURN parent, child;


// Create broader-narrower relationships
MATCH (broader:SubjectConcept {subject_id: 'subj_classical_antiquity'})
MATCH (narrower:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (narrower)-[:BROADER_CONCEPT]->(broader)
RETURN broader, narrower;


// Get full hierarchy path for a SubjectConcept
MATCH path = (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})-[:PART_OF*]->(root:SubjectConcept)
WHERE NOT (root)-[:PART_OF]->()
RETURN path, 
       [node IN nodes(path) | node.label] AS hierarchy_labels,
       length(path) AS depth;


// ============================================================================
// PART 4: SUBJECT CONCEPT QUERIES & DISCOVERY
// ============================================================================

// Find all SubjectConcepts by primary facet
MATCH (sc:SubjectConcept {primary_facet: 'MILITARY'})
RETURN sc.subject_id, sc.label, sc.qid, sc.confidence
ORDER BY sc.confidence DESC;


// Find SubjectConcepts with multiple facets
MATCH (sc:SubjectConcept)
WHERE size(sc.related_facets) > 0
RETURN sc.subject_id, sc.label, sc.primary_facet, sc.related_facets
ORDER BY size(sc.related_facets) DESC;


// Find SubjectConcepts by LCC classification
MATCH (sc:SubjectConcept)-[:CLASSIFIED_BY_LCC]->(lcc:LCC_Class)
WHERE lcc.code STARTS WITH 'DG'
RETURN sc.subject_id, sc.label, lcc.code, lcc.label
ORDER BY lcc.code;


// Full-text search across SubjectConcepts
MATCH (sc:SubjectConcept)
WHERE toLower(sc.label) CONTAINS toLower('roman')
   OR toLower(sc.description) CONTAINS toLower('roman')
RETURN sc.subject_id, sc.label, sc.description, sc.primary_facet
ORDER BY sc.confidence DESC
LIMIT 50;


// Find SubjectConcepts pending approval
MATCH (sc:SubjectConcept {status: 'pending_approval'})
RETURN sc.subject_id, sc.label, sc.proposed_by, sc.proposed_at, sc.confidence
ORDER BY sc.confidence DESC, sc.proposed_at DESC;


// ============================================================================
// PART 5: AGENT OPERATIONS
// ============================================================================

// Get all agents for a SubjectConcept
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (agent:Agent)-[:ANALYZES]->(sc)
RETURN agent.id, agent.facet, agent.status, agent.created_at
ORDER BY agent.facet;


// Check which facets have active agents for a SubjectConcept
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
OPTIONAL MATCH (agent:Agent {status: 'active'})-[:ANALYZES]->(sc)
WITH sc, collect(agent.facet) AS active_facets
RETURN sc.subject_id, 
       sc.primary_facet, 
       sc.related_facets,
       active_facets,
       [facet IN sc.related_facets WHERE NOT facet IN active_facets] AS missing_agents;


// Get agent analysis history for a SubjectConcept
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (agent:Agent)-[:ANALYZES]->(sc)
OPTIONAL MATCH (agent)-[:CREATED_PROPOSAL]->(proposal)
RETURN agent.id, 
       agent.facet, 
       count(proposal) AS proposals_created,
       max(proposal.created_at) AS last_proposal
ORDER BY proposals_created DESC;


// ============================================================================
// PART 6: ENTITY RELATIONSHIPS
// ============================================================================

// Link entities to SubjectConcepts
MATCH (entity:Human {qid: 'Q1048'})  // Julius Caesar
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (entity)-[:CLASSIFIED_BY]->(sc)
RETURN entity, sc;


// Find all entities classified by a SubjectConcept
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (entity)-[:CLASSIFIED_BY]->(sc)
RETURN labels(entity)[0] AS entity_type, 
       count(entity) AS count,
       collect(entity.label)[0..5] AS sample_entities
ORDER BY count DESC;


// Find SubjectConcepts for an entity
MATCH (entity:Human {qid: 'Q1048'})  // Julius Caesar
MATCH (entity)-[:CLASSIFIED_BY]->(sc:SubjectConcept)
RETURN sc.subject_id, sc.label, sc.primary_facet, sc.confidence
ORDER BY sc.confidence DESC;


// Facet-based entity discovery
MATCH (sc:SubjectConcept {primary_facet: 'MILITARY'})
MATCH (entity)-[:CLASSIFIED_BY]->(sc)
WHERE entity:Human OR entity:Event
RETURN sc.label AS subject,
       labels(entity)[0] AS entity_type,
       entity.label AS entity,
       entity.qid
ORDER BY sc.label, entity_type, entity.label
LIMIT 100;


// ============================================================================
// PART 7: TEMPORAL TETHERING
// ============================================================================

// Link SubjectConcept to temporal backbone
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (start_year:Year {year: -509})
MATCH (end_year:Year {year: -27})
MERGE (sc)-[:STARTS_IN_YEAR]->(start_year)
MERGE (sc)-[:ENDS_IN_YEAR]->(end_year)
RETURN sc, start_year, end_year;


// Link SubjectConcept to Periods
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (period:Period)
WHERE period.qid = 'Q17167'  // Roman Republic period
MERGE (sc)-[:HAS_PERIOD]->(period)
RETURN sc, period;


// Find SubjectConcepts active in a year range
MATCH (sc:SubjectConcept)-[:STARTS_IN_YEAR]->(start:Year)
MATCH (sc)-[:ENDS_IN_YEAR]->(end:Year)
WHERE start.year >= -500 AND end.year <= -50
RETURN sc.subject_id, sc.label, start.year AS start, end.year AS end
ORDER BY start.year;


// ============================================================================
// PART 8: GEOGRAPHIC SCOPE
// ============================================================================

// Link SubjectConcept to geographic regions
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (place:Place {pleiades_id: '423025'})  // Roma (Rome)
MERGE (sc)-[:PRIMARY_LOCATION]->(place)
RETURN sc, place;


// Find SubjectConcepts by geographic scope
MATCH (sc:SubjectConcept)-[:PRIMARY_LOCATION]->(place:Place)
WHERE place.label CONTAINS 'Italy'
RETURN sc.subject_id, sc.label, place.label AS location
ORDER BY sc.label;


// ============================================================================
// PART 9: CLAIMS & EVIDENCE
// ============================================================================

// Link SubjectConcept to supporting claims
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (claim:Claim)
WHERE claim.subject_concept_id = sc.subject_id
MERGE (sc)-[:SUPPORTED_BY]->(claim)
RETURN sc, count(claim) AS supporting_claims;


// Get evidence strength for SubjectConcept
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
OPTIONAL MATCH (sc)-[:SUPPORTED_BY]->(claim:Claim)
WITH sc, 
     count(claim) AS total_claims,
     avg(claim.confidence) AS avg_confidence,
     collect(claim.source_agent)[0..5] AS sample_sources
RETURN sc.subject_id, 
       sc.label,
       total_claims,
       avg_confidence,
       sample_sources;


// ============================================================================
// PART 10: BULK OPERATIONS & MAINTENANCE
// ============================================================================

// Approve all pending SubjectConcepts above confidence threshold
MATCH (sc:SubjectConcept {status: 'pending_approval'})
WHERE sc.confidence >= 0.8
SET sc.status = 'approved',
    sc.approved_at = datetime(),
    sc.approved_by = 'bulk_approval'
RETURN count(sc) AS approved_count;


// Update confidence scores based on federation strength
MATCH (sc:SubjectConcept)
OPTIONAL MATCH (sc)-[:HAS_LCSH_AUTHORITY]->(lcsh)
OPTIONAL MATCH (sc)-[:HAS_FAST_AUTHORITY]->(fast)
OPTIONAL MATCH (sc)-[:CLASSIFIED_BY_LCC]->(lcc)
WITH sc, 
     CASE 
       WHEN lcsh IS NOT NULL THEN 1 ELSE 0 END +
       CASE WHEN fast IS NOT NULL THEN 1 ELSE 0 END +
       CASE WHEN lcc IS NOT NULL THEN 1 ELSE 0 END AS federation_score
SET sc.federation_score = federation_score,
    sc.confidence = sc.confidence * (0.7 + (federation_score * 0.1))
RETURN sc.subject_id, sc.label, sc.federation_score, sc.confidence
ORDER BY sc.confidence DESC;


// Delete SubjectConcepts below confidence threshold
MATCH (sc:SubjectConcept)
WHERE sc.confidence < 0.5 AND sc.status = 'pending_approval'
DETACH DELETE sc
RETURN count(sc) AS deleted_count;


// Reindex SubjectConcepts for facet distribution
MATCH (sc:SubjectConcept)
WITH sc.primary_facet AS facet, count(sc) AS count
RETURN facet, count
ORDER BY count DESC;


// ============================================================================
// PART 11: STATISTICS & REPORTING
// ============================================================================

// Overall SubjectConcept statistics
MATCH (sc:SubjectConcept)
RETURN 
  count(sc) AS total_subjects,
  count(CASE WHEN sc.status = 'approved' THEN 1 END) AS approved,
  count(CASE WHEN sc.status = 'pending_approval' THEN 1 END) AS pending,
  avg(sc.confidence) AS avg_confidence,
  count(CASE WHEN sc.qid IS NOT NULL THEN 1 END) AS wikidata_linked,
  count(CASE WHEN sc.lcsh_id IS NOT NULL THEN 1 END) AS lcsh_linked,
  count(CASE WHEN sc.fast_id IS NOT NULL THEN 1 END) AS fast_linked;


// Facet distribution
MATCH (sc:SubjectConcept)
RETURN sc.primary_facet AS facet, 
       count(sc) AS count,
       avg(sc.confidence) AS avg_confidence
ORDER BY count DESC;


// Agent activity statistics
MATCH (agent:Agent)
WHERE agent.agent_type = 'SubjectFacetAgent'
RETURN agent.facet AS facet,
       count(agent) AS agent_count,
       count(CASE WHEN agent.status = 'active' THEN 1 END) AS active_count
ORDER BY agent_count DESC;


// Federation coverage report
MATCH (sc:SubjectConcept)
RETURN 
  count(sc) AS total,
  count(CASE WHEN sc.qid IS NOT NULL THEN 1 END) AS has_wikidata,
  count(CASE WHEN sc.lcsh_id IS NOT NULL THEN 1 END) AS has_lcsh,
  count(CASE WHEN sc.fast_id IS NOT NULL THEN 1 END) AS has_fast,
  count(CASE WHEN sc.lcc_class IS NOT NULL THEN 1 END) AS has_lcc,
  count(CASE WHEN sc.qid IS NOT NULL AND sc.lcsh_id IS NOT NULL 
             AND sc.fast_id IS NOT NULL AND sc.lcc_class IS NOT NULL 
             THEN 1 END) AS fully_federated;


// ============================================================================
// PART 12: ADVANCED QUERIES
// ============================================================================

// Find related SubjectConcepts via shared entities
MATCH (sc1:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (entity)-[:CLASSIFIED_BY]->(sc1)
MATCH (entity)-[:CLASSIFIED_BY]->(sc2:SubjectConcept)
WHERE sc1 <> sc2
RETURN sc2.subject_id, sc2.label, sc2.primary_facet, count(entity) AS shared_entities
ORDER BY shared_entities DESC
LIMIT 20;


// Cross-facet analysis - find SubjectConcepts with complementary facets
MATCH (sc1:SubjectConcept {primary_facet: 'MILITARY'})
MATCH (sc2:SubjectConcept {primary_facet: 'POLITICAL'})
MATCH (entity)-[:CLASSIFIED_BY]->(sc1)
MATCH (entity)-[:CLASSIFIED_BY]->(sc2)
RETURN sc1.label AS military_subject,
       sc2.label AS political_subject,
       count(entity) AS shared_entities
ORDER BY shared_entities DESC
LIMIT 10;


// Temporal overlap analysis
MATCH (sc1:SubjectConcept)-[:STARTS_IN_YEAR]->(start1:Year)
MATCH (sc1)-[:ENDS_IN_YEAR]->(end1:Year)
MATCH (sc2:SubjectConcept)-[:STARTS_IN_YEAR]->(start2:Year)
MATCH (sc2)-[:ENDS_IN_YEAR]->(end2:Year)
WHERE sc1 <> sc2
  AND start1.year <= end2.year
  AND start2.year <= end1.year
WITH sc1, sc2,
     CASE 
       WHEN start1.year > start2.year THEN start1.year 
       ELSE start2.year 
     END AS overlap_start,
     CASE 
       WHEN end1.year < end2.year THEN end1.year 
       ELSE end2.year 
     END AS overlap_end
RETURN sc1.label, sc2.label, overlap_start, overlap_end, 
       (overlap_end - overlap_start) AS overlap_years
ORDER BY overlap_years DESC
LIMIT 20;


// ============================================================================
// END OF SUBJECT CONCEPT OPERATIONS
// ============================================================================
