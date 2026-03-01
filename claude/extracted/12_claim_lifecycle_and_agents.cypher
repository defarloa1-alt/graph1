// ============================================================================
// CHRYSTALLUM: CLAIM LIFECYCLE + AGENT CONTRACTS + GOLDEN TRACE
// ============================================================================
// File: 12_claim_lifecycle_and_agents.cypher
// Purpose:
//   1) Define the Claim status state machine as queryable graph
//   2) Enrich Agent nodes with capability contracts
//   3) Create one fully-worked golden exemplar trace
// Safe: All MERGE - idempotent
// ============================================================================


// ============================================================================
// SECTION 1: CLAIM LIFECYCLE STATE MACHINE
// ============================================================================
// Pattern: SYS_ClaimStatus -[:CAN_TRANSITION_TO {trigger, requires}]-> SYS_ClaimStatus
// An agent queries this to know: "What states can a Claim be in? What moves
// it from one state to another? What do I need to provide?"

UNWIND [
  {status: 'proposed',            label: 'Proposed',            phase: 'discovery', description: 'Agent has created a claim with cipher, text, confidence, and provenance. Awaiting evaluation.', terminal: false},
  {status: 'needs_provenance',    label: 'Needs Provenance',    phase: 'discovery', description: 'Claim meets confidence threshold but lacks RetrievalContext. Agent must attach evidence.', terminal: false},
  {status: 'under_review',        label: 'Under Review',        phase: 'evaluation', description: 'Claim is being evaluated by the decision table (D10) and/or human reviewer.', terminal: false},
  {status: 'reviewed_approved',   label: 'Reviewed (Approved)', phase: 'evaluation', description: 'Human reviewer has approved. Ready for promotion.', terminal: false},
  {status: 'reviewed_rejected',   label: 'Reviewed (Rejected)', phase: 'evaluation', description: 'Human reviewer rejected. Rejection reason attached.', terminal: false},
  {status: 'promoted',            label: 'Promoted',            phase: 'canon', description: 'Claim has been promoted to a first-class edge in the graph. ProposedEdge materialized.', terminal: true},
  {status: 'rejected_low_confidence', label: 'Rejected (Low Confidence)', phase: 'terminal', description: 'Confidence below threshold. Agent may retry with better evidence.', terminal: false},
  {status: 'rejected_human',      label: 'Rejected (Human)',    phase: 'terminal', description: 'Human reviewer explicitly rejected. Reviewer notes available for learning.', terminal: true},
  {status: 'superseded',          label: 'Superseded',          phase: 'terminal', description: 'A newer claim with higher confidence replaces this one.', terminal: true},
  {status: 'retracted',           label: 'Retracted',           phase: 'terminal', description: 'Agent or human retracted the claim (found to be incorrect).', terminal: true}
] AS s
MERGE (cs:SYS_ClaimStatus {status: s.status})
SET cs.label = s.label,
    cs.phase = s.phase,
    cs.description = s.description,
    cs.terminal = s.terminal,
    cs.updated = datetime();

// Define valid transitions
UNWIND [
  {from: 'proposed',                to: 'under_review',            trigger: 'auto',  requires: 'confidence >= threshold AND provenance exists'},
  {from: 'proposed',                to: 'needs_provenance',        trigger: 'auto',  requires: 'confidence >= threshold AND no RetrievalContext attached'},
  {from: 'proposed',                to: 'rejected_low_confidence', trigger: 'auto',  requires: 'confidence < threshold'},
  {from: 'needs_provenance',        to: 'proposed',                trigger: 'agent', requires: 'Agent attaches RetrievalContext and re-submits'},
  {from: 'under_review',            to: 'reviewed_approved',       trigger: 'human', requires: 'Human approves via review interface'},
  {from: 'under_review',            to: 'reviewed_rejected',       trigger: 'human', requires: 'Human rejects with reason'},
  {from: 'reviewed_approved',       to: 'promoted',                trigger: 'auto',  requires: 'ProposedEdge materialized as first-class edge'},
  {from: 'reviewed_rejected',       to: 'rejected_human',          trigger: 'auto',  requires: 'Rejection finalized'},
  {from: 'rejected_low_confidence', to: 'proposed',                trigger: 'agent', requires: 'Agent re-submits with improved evidence/confidence'},
  {from: 'promoted',                to: 'retracted',               trigger: 'human', requires: 'Post-promotion retraction (error discovered)'},
  {from: 'promoted',                to: 'superseded',              trigger: 'auto',  requires: 'New claim with higher confidence on same proposition'}
] AS t
MATCH (from_s:SYS_ClaimStatus {status: t.from})
MATCH (to_s:SYS_ClaimStatus {status: t.to})
MERGE (from_s)-[r:CAN_TRANSITION_TO]->(to_s)
SET r.trigger = t.trigger,
    r.requires = t.requires,
    r.updated = datetime();


// ============================================================================
// SECTION 2: AGENT CAPABILITY CONTRACTS
// ============================================================================
// Enrich the 3 existing Agent nodes with capability metadata.
// Also define the agent type taxonomy.

// Agent type definitions
UNWIND [
  {type_id: 'SFA', label: 'Subject-Facet Assignment Agent', description: 'Evaluates SubjectConcepts and assigns them to facets. Uses Wikidata anchors and keyword analysis. Produces FacetAssessments.', capabilities: ['read_subject_concepts', 'read_wikidata', 'create_facet_assessment', 'propose_claim_sfa']},
  {type_id: 'HARVEST', label: 'Harvest Agent', description: 'Fetches entities from federation sources (Wikidata, Pleiades, etc.) within harvest budget limits. Runs SPARQL queries.', capabilities: ['read_federation_sources', 'run_sparql', 'create_entities', 'check_scope']},
  {type_id: 'CLAIM', label: 'Claim Discovery Agent', description: 'Analyzes existing entities to discover new relationships. Proposes Claims with cipher-encoded propositions and evidence chains.', capabilities: ['read_entities', 'read_claims', 'create_claims', 'create_retrieval_context', 'create_proposed_edge']},
  {type_id: 'RESOLUTION', label: 'Entity Resolution Agent', description: 'Detects and merges duplicate entities using fuzzy matching and QID alignment. Governed by D14 decision table.', capabilities: ['read_entities', 'fuzzy_match', 'merge_entities', 'flag_ambiguous']},
  {type_id: 'VALIDATION', label: 'Validation Agent', description: 'Runs SYS_ValidationRule checks against the graph. Reports integrity issues.', capabilities: ['read_all', 'run_validation_rules', 'create_alert']}
] AS at
MERGE (atype:SYS_AgentType {type_id: at.type_id})
SET atype.label = at.label,
    atype.description = at.description,
    atype.capabilities = at.capabilities,
    atype.updated = datetime();

// Enrich existing agents
MATCH (a:Agent {name: 'SFA_POLITICAL_RR'})
SET a.agent_type = 'SFA',
    a.description = 'Subject-Facet Assignment specialist for the Political facet. Evaluates political entities (governments, political events, legislation) for facet routing.',
    a.confidence_ceiling = 0.75,
    a.max_claims_per_run = 50,
    a.federation_sources = ['Wikidata', 'LCSH/FAST/LCC'],
    a.governed_by_policies = ['NoTemporalFacet', 'NoClassificationFacet', 'SFAProposalAsClaim'],
    a.governed_by_tables = ['D8_DETERMINE_SFA_facet_assignment'],
    a.updated = datetime();

MATCH (a:Agent {name: 'SFA_MILITARY_RR'})
SET a.agent_type = 'SFA',
    a.description = 'Subject-Facet Assignment specialist for the Military facet. Evaluates military entities (battles, armies, fortifications, military technology) for facet routing.',
    a.confidence_ceiling = 0.75,
    a.max_claims_per_run = 50,
    a.federation_sources = ['Wikidata', 'LCSH/FAST/LCC', 'DPRR'],
    a.governed_by_policies = ['NoTemporalFacet', 'NoClassificationFacet', 'SFAProposalAsClaim'],
    a.governed_by_tables = ['D8_DETERMINE_SFA_facet_assignment'],
    a.updated = datetime();

MATCH (a:Agent {name: 'SFA_SOCIAL_RR'})
SET a.agent_type = 'SFA',
    a.description = 'Subject-Facet Assignment specialist for the Social facet. Evaluates social entities (family, class structure, customs, social movements) for facet routing.',
    a.confidence_ceiling = 0.75,
    a.max_claims_per_run = 50,
    a.federation_sources = ['Wikidata', 'LCSH/FAST/LCC'],
    a.governed_by_policies = ['NoTemporalFacet', 'NoClassificationFacet', 'SFAProposalAsClaim'],
    a.governed_by_tables = ['D8_DETERMINE_SFA_facet_assignment'],
    a.updated = datetime();

// Link agents to their type
MATCH (a:Agent)
WHERE a.agent_type IS NOT NULL
MATCH (at:SYS_AgentType {type_id: a.agent_type})
MERGE (a)-[:INSTANCE_OF_TYPE]->(at);


// ============================================================================
// SECTION 3: GOLDEN EXEMPLAR TRACE
// ============================================================================
// One fully-worked example showing the complete lifecycle:
// Agent discovers a relationship → creates Claim → attaches provenance →
// creates ProposedEdge → undergoes review → gets promoted.
//
// Scenario: SFA_MILITARY_RR discovers that the Battle of Cannae (Q13377)
// should be assigned to the Military facet.

// Step 1: RetrievalContext (what evidence was gathered)
MERGE (rc:RetrievalContext {retrieval_id: 'rc_exemplar_001'})
SET rc.agent_id = 'SFA_MILITARY_RR',
    rc.authority_source = 'Wikidata',
    rc.query_used = 'SELECT ?item WHERE { ?item wdt:P31 wd:Q178561 . ?item wdt:P361 wd:Q165437 }',
    rc.query_description = 'Find battles that are part of the Second Punic War',
    rc.results_count = 12,
    rc.result_qids = ['Q13377', 'Q214085', 'Q210543'],
    rc.timestamp = datetime('2026-02-20T10:00:00Z'),
    rc.is_exemplar = true,
    rc.updated = datetime();

// Step 2: Claim (the proposition)
MERGE (c:Claim {claim_id: 'clm_exemplar_001'})
SET c.cipher = 'ASSIGN(Q13377, FACET:MILITARY, CONF:0.95)',
    c.text = 'The Battle of Cannae (Q13377) is a military event and should be assigned to the Military facet.',
    c.label = 'Battle of Cannae → Military facet',
    c.confidence = 0.95,
    c.claim_type = 'sfa_proposal',
    c.source_agent = 'SFA_MILITARY_RR',
    c.authority_source = 'Wikidata',
    c.status = 'promoted',
    c.timestamp = datetime('2026-02-20T10:01:00Z'),
    c.promoted_at = datetime('2026-02-20T11:00:00Z'),
    c.review_status = 'approved',
    c.reviewer = 'human_historian',
    c.is_exemplar = true,
    c.updated = datetime();

// Step 3: Link claim to provenance
MATCH (c:Claim {claim_id: 'clm_exemplar_001'})
MATCH (rc:RetrievalContext {retrieval_id: 'rc_exemplar_001'})
MERGE (c)-[:HAS_TRACE]->(rc);

// Step 4: Link claim to agent
MATCH (c:Claim {claim_id: 'clm_exemplar_001'})
MATCH (a:Agent {name: 'SFA_MILITARY_RR'})
MERGE (c)-[:PROPOSED_BY]->(a);

// Step 5: ProposedEdge (what edge would be created)
MERGE (pe:ProposedEdge {edge_id: 'pe_exemplar_001'})
SET pe.claim_id = 'clm_exemplar_001',
    pe.relationship_type = 'ASSIGNED_TO_FACET',
    pe.source_entity = 'Q13377',
    pe.source_label = 'Battle of Cannae',
    pe.target_entity = 'MILITARY',
    pe.target_label = 'Military',
    pe.status = 'promoted',
    pe.is_exemplar = true,
    pe.updated = datetime();

// Step 6: Link ProposedEdge to Claim
MATCH (pe:ProposedEdge {edge_id: 'pe_exemplar_001'})
MATCH (c:Claim {claim_id: 'clm_exemplar_001'})
MERGE (pe)-[:EVIDENCED_BY]->(c);

// Step 7: AnalysisRun that produced this
MERGE (ar:AnalysisRun {run_id: 'run_exemplar_001'})
SET ar.pipeline_version = '1.0',
    ar.status = 'completed',
    ar.started_at = datetime('2026-02-20T10:00:00Z'),
    ar.completed_at = datetime('2026-02-20T10:05:00Z'),
    ar.claims_proposed = 12,
    ar.claims_promoted = 8,
    ar.claims_rejected = 4,
    ar.is_exemplar = true,
    ar.updated = datetime();

// Link run to agent
MATCH (ar:AnalysisRun {run_id: 'run_exemplar_001'})
MATCH (a:Agent {name: 'SFA_MILITARY_RR'})
MERGE (a)-[:PERFORMED]->(ar);

// Step 8: FacetAssessment produced by the run
MERGE (fa:FacetAssessment {assessment_id: 'fa_exemplar_001'})
SET fa.score = 0.95,
    fa.facet_key = 'MILITARY',
    fa.entity_qid = 'Q13377',
    fa.entity_label = 'Battle of Cannae',
    fa.status = 'accepted',
    fa.rationale = 'P31=battle(Q178561), P361=Second Punic War(Q165437). Strong military signal from instance-of and part-of chains.',
    fa.is_exemplar = true,
    fa.updated = datetime();

// Link assessment to run
MATCH (fa:FacetAssessment {assessment_id: 'fa_exemplar_001'})
MATCH (ar:AnalysisRun {run_id: 'run_exemplar_001'})
MERGE (ar)-[:PRODUCED]->(fa);

// Link assessment to facet
MATCH (fa:FacetAssessment {assessment_id: 'fa_exemplar_001'})
MATCH (f:Facet {key: 'MILITARY'})
MERGE (fa)-[:ASSESSED_FOR_FACET]->(f);


// ============================================================================
// MARK EXEMPLAR NODES FOR AGENT DISCOVERY
// ============================================================================
// Agents can find the golden trace with:
//   MATCH (n) WHERE n.is_exemplar = true RETURN n

// Create an index for exemplar lookups (Claude Code should run this)
// CREATE INDEX exemplar_index IF NOT EXISTS FOR (n:Claim) ON (n.is_exemplar);


// ============================================================================
// VERIFICATION
// ============================================================================

// State machine
MATCH (s:SYS_ClaimStatus)
OPTIONAL MATCH (s)-[t:CAN_TRANSITION_TO]->(next)
RETURN s.status AS status, s.phase AS phase, s.terminal AS terminal,
       collect(next.status) AS can_go_to
ORDER BY s.phase, s.status;

// Golden trace
MATCH path = (a:Agent)-[:PERFORMED]->(ar:AnalysisRun)-[:PRODUCED]->(fa:FacetAssessment)
WHERE ar.is_exemplar = true
RETURN a.name AS agent, ar.run_id AS run, fa.assessment_id AS assessment, fa.score AS score;

MATCH path = (pe:ProposedEdge)-[:EVIDENCED_BY]->(c:Claim)-[:HAS_TRACE]->(rc:RetrievalContext)
WHERE c.is_exemplar = true
RETURN pe.edge_id AS edge, c.claim_id AS claim, c.status AS status, rc.retrieval_id AS context;
