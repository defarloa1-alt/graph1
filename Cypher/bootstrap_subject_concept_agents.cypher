// ============================================================================
// BOOTSTRAP SUBJECT CONCEPT AGENT INFRASTRUCTURE
// ============================================================================
// Purpose: Create complete SCA infrastructure in Chrystallum
// Version: 1.0
// Date: 2026-02-20
//
// This script creates:
// 1. SubjectConceptRoot and registries
// 2. 18 Canonical Facets
// 3. Sample SubjectConcepts
// 4. On-demand agent templates
// ============================================================================


// ============================================================================
// STEP 1: CREATE SUBJECT CONCEPT ROOT & REGISTRIES
// ============================================================================

// Link SubjectConceptRoot to Chrystallum
MATCH (sys:Chrystallum)
MERGE (sc_root:SubjectConceptRoot {id: 'subject_concept_root'})
ON CREATE SET 
  sc_root.created_at = datetime(),
  sc_root.version = '1.0'
MERGE (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)

// Create SubjectConceptRegistry
WITH sc_root
MERGE (registry:SubjectConceptRegistry {registry_id: 'main_registry'})
ON CREATE SET
  registry.created_at = datetime(),
  registry.total_concepts = 0,
  registry.approved_concepts = 0,
  registry.pending_concepts = 0
MERGE (sc_root)-[:HAS_SUBJECT_REGISTRY]->(registry)

// Create AgentRegistry
WITH sc_root
MERGE (agent_reg:AgentRegistry {registry_id: 'agent_registry'})
ON CREATE SET
  agent_reg.created_at = datetime(),
  agent_reg.total_agents = 0,
  agent_reg.active_agents = 0,
  agent_reg.max_possible_agents = 1422
MERGE (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg)

RETURN sc_root, registry, agent_reg;


// ============================================================================
// STEP 2: CREATE 18 CANONICAL FACETS
// ============================================================================

// Link to existing FacetRoot or create facet nodes directly
MATCH (sys:Chrystallum)-[:HAS_FACET_ROOT]->(facet_root:FacetRoot)

// Create all 18 facets
WITH facet_root
UNWIND [
  {key: 'ARCHAEOLOGICAL', label: 'Archaeological'},
  {key: 'ARTISTIC', label: 'Artistic'},
  {key: 'BIOGRAPHIC', label: 'Biographic'},
  {key: 'COMMUNICATION', label: 'Communication'},
  {key: 'CULTURAL', label: 'Cultural'},
  {key: 'DEMOGRAPHIC', label: 'Demographic'},
  {key: 'DIPLOMATIC', label: 'Diplomatic'},
  {key: 'ECONOMIC', label: 'Economic'},
  {key: 'ENVIRONMENTAL', label: 'Environmental'},
  {key: 'GEOGRAPHIC', label: 'Geographic'},
  {key: 'INTELLECTUAL', label: 'Intellectual'},
  {key: 'LINGUISTIC', label: 'Linguistic'},
  {key: 'MILITARY', label: 'Military'},
  {key: 'POLITICAL', label: 'Political'},
  {key: 'RELIGIOUS', label: 'Religious'},
  {key: 'SCIENTIFIC', label: 'Scientific'},
  {key: 'SOCIAL', label: 'Social'},
  {key: 'TECHNOLOGICAL', label: 'Technological'}
] AS facet_data

MERGE (facet:Facet {key: facet_data.key})
ON CREATE SET
  facet.label = facet_data.label,
  facet.created_at = datetime()
MERGE (facet_root)-[:HAS_FACET]->(facet)

WITH count(facet) AS facet_count
RETURN facet_count;


// ============================================================================
// STEP 3: CREATE SAMPLE SUBJECT CONCEPTS
// ============================================================================

// Sample 1: Roman Republic (Political/Military/Social)
MATCH (registry:SubjectConceptRegistry {registry_id: 'main_registry'})
MERGE (sc1:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
ON CREATE SET
  sc1.label = 'Roman Republic',
  sc1.qid = 'Q17167',
  sc1.primary_facet = 'POLITICAL',
  sc1.related_facets = ['MILITARY', 'SOCIAL', 'ECONOMIC'],
  sc1.description = 'Ancient Roman state and civilization (509-27 BCE)',
  sc1.temporal_scope = '-0509/-0027',
  sc1.geographic_scope = 'Mediterranean, Italy',
  sc1.status = 'approved',
  sc1.created_at = datetime(),
  sc1.created_by = 'sca_bootstrap',
  sc1.confidence = 0.95,
  sc1.lcsh_id = 'sh85115087',
  sc1.fast_id = 'fst01204885',
  sc1.lcc_class = 'DG241-269'
MERGE (registry)-[:CONTAINS]->(sc1)
RETURN sc1;


// Sample 2: Ancient Greek Philosophy (Intellectual/Cultural)
MATCH (registry:SubjectConceptRegistry {registry_id: 'main_registry'})
MERGE (sc2:SubjectConcept {subject_id: 'subj_greek_philosophy_q192125'})
ON CREATE SET
  sc2.label = 'Ancient Greek Philosophy',
  sc2.qid = 'Q192125',
  sc2.primary_facet = 'INTELLECTUAL',
  sc2.related_facets = ['CULTURAL', 'RELIGIOUS'],
  sc2.description = 'Philosophical tradition of ancient Greece',
  sc2.temporal_scope = '-0600/-0300',
  sc2.geographic_scope = 'Greece, Mediterranean',
  sc2.status = 'approved',
  sc2.created_at = datetime(),
  sc2.created_by = 'sca_bootstrap',
  sc2.confidence = 0.92,
  sc2.fast_id = 'fst01060860',
  sc2.lcc_class = 'B171-708'
MERGE (registry)-[:CONTAINS]->(sc2)
RETURN sc2;


// Sample 3: Roman Military (Military)
MATCH (registry:SubjectConceptRegistry {registry_id: 'main_registry'})
MERGE (sc3:SubjectConcept {subject_id: 'subj_roman_military_q124508'})
ON CREATE SET
  sc3.label = 'Roman Military',
  sc3.qid = 'Q124508',
  sc3.primary_facet = 'MILITARY',
  sc3.related_facets = ['POLITICAL', 'TECHNOLOGICAL'],
  sc3.description = 'Military forces of ancient Rome',
  sc3.temporal_scope = '-0753/0476',
  sc3.geographic_scope = 'Roman Empire',
  sc3.status = 'approved',
  sc3.created_at = datetime(),
  sc3.created_by = 'sca_bootstrap',
  sc3.confidence = 0.93,
  sc3.fast_id = 'fst01204901',
  sc3.lcc_class = 'U35'
MERGE (registry)-[:CONTAINS]->(sc3)
RETURN sc3;


// Sample 4: Mediterranean Trade (Economic/Geographic)
MATCH (registry:SubjectConceptRegistry {registry_id: 'main_registry'})
MERGE (sc4:SubjectConcept {subject_id: 'subj_mediterranean_trade'})
ON CREATE SET
  sc4.label = 'Mediterranean Trade',
  sc4.primary_facet = 'ECONOMIC',
  sc4.related_facets = ['GEOGRAPHIC', 'SOCIAL'],
  sc4.description = 'Commercial networks in the Mediterranean region',
  sc4.temporal_scope = '-1000/0500',
  sc4.geographic_scope = 'Mediterranean Sea',
  sc4.status = 'approved',
  sc4.created_at = datetime(),
  sc4.created_by = 'sca_bootstrap',
  sc4.confidence = 0.88,
  sc4.lcc_class = 'HF385'
MERGE (registry)-[:CONTAINS]->(sc4)
RETURN sc4;


// Sample 5: Roman Religion (Religious/Cultural)
MATCH (registry:SubjectConceptRegistry {registry_id: 'main_registry'})
MERGE (sc5:SubjectConcept {subject_id: 'subj_roman_religion_q102782'})
ON CREATE SET
  sc5.label = 'Roman Religion',
  sc5.qid = 'Q102782',
  sc5.primary_facet = 'RELIGIOUS',
  sc5.related_facets = ['CULTURAL', 'POLITICAL'],
  sc5.description = 'Religious practices and beliefs of ancient Rome',
  sc5.temporal_scope = '-0753/0476',
  sc5.geographic_scope = 'Roman Empire',
  sc5.status = 'approved',
  sc5.created_at = datetime(),
  sc5.created_by = 'sca_bootstrap',
  sc5.confidence = 0.90,
  sc5.fast_id = 'fst01204920',
  sc5.lcc_class = 'BL800-820'
MERGE (registry)-[:CONTAINS]->(sc5)
RETURN sc5;


// Sample 6: Hellenistic Art (Artistic/Cultural)
MATCH (registry:SubjectConceptRegistry {registry_id: 'main_registry'})
MERGE (sc6:SubjectConcept {subject_id: 'subj_hellenistic_art_q34636'})
ON CREATE SET
  sc6.label = 'Hellenistic Art',
  sc6.qid = 'Q34636',
  sc6.primary_facet = 'ARTISTIC',
  sc6.related_facets = ['CULTURAL', 'INTELLECTUAL'],
  sc6.description = 'Art of the Hellenistic period',
  sc6.temporal_scope = '-0323/-0031',
  sc6.geographic_scope = 'Eastern Mediterranean, Near East',
  sc6.status = 'approved',
  sc6.created_at = datetime(),
  sc6.created_by = 'sca_bootstrap',
  sc6.confidence = 0.89,
  sc6.lcc_class = 'N5630-5896'
MERGE (registry)-[:CONTAINS]->(sc6)
RETURN sc6;


// ============================================================================
// STEP 4: CREATE SUBJECT CONCEPT HIERARCHIES
// ============================================================================

// Create hierarchy: Ancient Rome -> Roman Republic
MATCH (parent:SubjectConcept {subject_id: 'subj_ancient_rome'})
MATCH (child:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (child)-[:PART_OF]->(parent)
RETURN parent.label, child.label;

// Alternative: Create parent if it doesn't exist
MERGE (parent:SubjectConcept {subject_id: 'subj_ancient_rome'})
ON CREATE SET
  parent.label = 'Ancient Rome',
  parent.qid = 'Q1747689',
  parent.primary_facet = 'POLITICAL',
  parent.status = 'approved',
  parent.created_at = datetime(),
  parent.confidence = 0.95
WITH parent
MATCH (child:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (child)-[:PART_OF]->(parent)
RETURN parent, child;


// ============================================================================
// STEP 5: CREATE ON-DEMAND AGENT INFRASTRUCTURE
// ============================================================================

// Create agent for Roman Republic + MILITARY facet
MATCH (sys:Chrystallum)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)
MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg:AgentRegistry)
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (agent:Agent {id: 'SFA_subj_roman_republic_q17167_MILITARY'})
ON CREATE SET
  agent.agent_type = 'SubjectFacetAgent',
  agent.facet = 'MILITARY',
  agent.subject_concept_id = 'subj_roman_republic_q17167',
  agent.status = 'active',
  agent.created_at = datetime(),
  agent.model = 'llama-3.1-sonar-large-128k-online',
  agent.capabilities = ['analysis', 'discovery', 'classification'],
  agent.query_count = 0,
  agent.proposal_count = 0
MERGE (agent_reg)-[:HAS_AGENT]->(agent)
MERGE (agent)-[:ANALYZES]->(sc)
RETURN agent;


// Create agent for Roman Republic + POLITICAL facet
MATCH (sc_root:SubjectConceptRoot)
MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg:AgentRegistry)
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (agent:Agent {id: 'SFA_subj_roman_republic_q17167_POLITICAL'})
ON CREATE SET
  agent.agent_type = 'SubjectFacetAgent',
  agent.facet = 'POLITICAL',
  agent.subject_concept_id = 'subj_roman_republic_q17167',
  agent.status = 'active',
  agent.created_at = datetime(),
  agent.model = 'llama-3.1-sonar-large-128k-online',
  agent.capabilities = ['analysis', 'discovery', 'classification'],
  agent.query_count = 0,
  agent.proposal_count = 0
MERGE (agent_reg)-[:HAS_AGENT]->(agent)
MERGE (agent)-[:ANALYZES]->(sc)
RETURN agent;


// Create agent for Roman Republic + SOCIAL facet
MATCH (sc_root:SubjectConceptRoot)
MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg:AgentRegistry)
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (agent:Agent {id: 'SFA_subj_roman_republic_q17167_SOCIAL'})
ON CREATE SET
  agent.agent_type = 'SubjectFacetAgent',
  agent.facet = 'SOCIAL',
  agent.subject_concept_id = 'subj_roman_republic_q17167',
  agent.status = 'active',
  agent.created_at = datetime(),
  agent.model = 'llama-3.1-sonar-large-128k-online',
  agent.capabilities = ['analysis', 'discovery', 'classification'],
  agent.query_count = 0,
  agent.proposal_count = 0
MERGE (agent_reg)-[:HAS_AGENT]->(agent)
MERGE (agent)-[:ANALYZES]->(sc)
RETURN agent;


// ============================================================================
// STEP 6: TEMPORAL TETHERING
// ============================================================================

// Link Roman Republic to temporal backbone
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MATCH (start_year:Year {year: -509})
MATCH (end_year:Year {year: -27})
MERGE (sc)-[:STARTS_IN_YEAR]->(start_year)
MERGE (sc)-[:ENDS_IN_YEAR]->(end_year)
RETURN sc, start_year, end_year;


// Link Greek Philosophy to temporal backbone
MATCH (sc:SubjectConcept {subject_id: 'subj_greek_philosophy_q192125'})
MATCH (start_year:Year {year: -600})
MATCH (end_year:Year {year: -300})
MERGE (sc)-[:STARTS_IN_YEAR]->(start_year)
MERGE (sc)-[:ENDS_IN_YEAR]->(end_year)
RETURN sc, start_year, end_year;


// ============================================================================
// STEP 7: AUTHORITY FEDERATION LINKS
// ============================================================================

// Create LCSH authority link for Roman Republic
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (lcsh:LCSH_Subject {lcsh_id: 'sh85115087'})
ON CREATE SET
  lcsh.heading = 'Rome--History--Republic, 265-30 B.C.',
  lcsh.created_at = datetime()
MERGE (sc)-[:HAS_LCSH_AUTHORITY]->(lcsh)
RETURN sc, lcsh;


// Create FAST authority link
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (fast:FAST_Subject {fast_id: 'fst01204885'})
ON CREATE SET
  fast.preferred_label = 'Rome--History--Republic, 265-30 B.C.',
  fast.created_at = datetime()
MERGE (sc)-[:HAS_FAST_AUTHORITY]->(fast)
RETURN sc, fast;


// Create LCC classification link
MATCH (sc:SubjectConcept {subject_id: 'subj_roman_republic_q17167'})
MERGE (lcc:LCC_Class {code: 'DG241-269'})
ON CREATE SET
  lcc.label = 'Rome--History--Republic',
  lcc.created_at = datetime()
MERGE (sc)-[:CLASSIFIED_BY_LCC]->(lcc)
RETURN sc, lcc;


// ============================================================================
// STEP 8: UPDATE REGISTRY COUNTS
// ============================================================================

// Update SubjectConceptRegistry counts
MATCH (registry:SubjectConceptRegistry {registry_id: 'main_registry'})
MATCH (registry)-[:CONTAINS]->(sc:SubjectConcept)
WITH registry, 
     count(sc) AS total,
     count(CASE WHEN sc.status = 'approved' THEN 1 END) AS approved,
     count(CASE WHEN sc.status = 'pending_approval' THEN 1 END) AS pending
SET registry.total_concepts = total,
    registry.approved_concepts = approved,
    registry.pending_concepts = pending,
    registry.last_updated = datetime()
RETURN registry;


// Update AgentRegistry counts
MATCH (agent_reg:AgentRegistry {registry_id: 'agent_registry'})
MATCH (agent_reg)-[:HAS_AGENT]->(agent:Agent)
WITH agent_reg,
     count(agent) AS total,
     count(CASE WHEN agent.status = 'active' THEN 1 END) AS active
SET agent_reg.total_agents = total,
    agent_reg.active_agents = active,
    agent_reg.last_updated = datetime()
RETURN agent_reg;


// ============================================================================
// STEP 9: VERIFICATION QUERIES
// ============================================================================

// Verify SubjectConcept infrastructure
MATCH (sys:Chrystallum)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)
MATCH (sc_root)-[:HAS_SUBJECT_REGISTRY]->(registry)
MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg)
MATCH (registry)-[:CONTAINS]->(sc:SubjectConcept)
MATCH (agent_reg)-[:HAS_AGENT]->(agent:Agent)
RETURN 
  count(DISTINCT sc) AS subject_concepts,
  count(DISTINCT agent) AS agents,
  registry.approved_concepts AS approved,
  registry.pending_concepts AS pending,
  agent_reg.active_agents AS active_agents;


// Verify facet coverage
MATCH (sc:SubjectConcept)
RETURN sc.primary_facet AS facet, 
       count(sc) AS count
ORDER BY count DESC;


// Verify temporal coverage
MATCH (sc:SubjectConcept)-[:STARTS_IN_YEAR]->(start:Year)
MATCH (sc)-[:ENDS_IN_YEAR]->(end:Year)
RETURN sc.label, start.year AS start, end.year AS end
ORDER BY start.year;


// Verify authority federation
MATCH (sc:SubjectConcept)
OPTIONAL MATCH (sc)-[:HAS_LCSH_AUTHORITY]->(lcsh)
OPTIONAL MATCH (sc)-[:HAS_FAST_AUTHORITY]->(fast)
OPTIONAL MATCH (sc)-[:CLASSIFIED_BY_LCC]->(lcc)
RETURN 
  count(sc) AS total,
  count(lcsh) AS has_lcsh,
  count(fast) AS has_fast,
  count(lcc) AS has_lcc,
  count(CASE WHEN lcsh IS NOT NULL AND fast IS NOT NULL AND lcc IS NOT NULL THEN 1 END) AS fully_federated;


// ============================================================================
// BOOTSTRAP COMPLETE
// ============================================================================

// Final summary
MATCH (sys:Chrystallum)
MATCH (sys)-[:HAS_SUBJECT_CONCEPT_ROOT]->(sc_root)
MATCH (sys)-[:HAS_FACET_ROOT]->(facet_root)
MATCH (facet_root)-[:HAS_FACET]->(facet)
MATCH (sc_root)-[:HAS_SUBJECT_REGISTRY]->(registry)
MATCH (sc_root)-[:HAS_AGENT_REGISTRY]->(agent_reg)
MATCH (registry)-[:CONTAINS]->(sc:SubjectConcept)
MATCH (agent_reg)-[:HAS_AGENT]->(agent:Agent)
RETURN 
  'BOOTSTRAP COMPLETE' AS status,
  count(DISTINCT facet) AS facets,
  count(DISTINCT sc) AS subject_concepts,
  count(DISTINCT agent) AS agents,
  registry.approved_concepts AS approved,
  agent_reg.active_agents AS active_agents,
  datetime() AS completed_at;
