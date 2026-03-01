// ============================================================================
// CHRYSTALLUM: AGENT ONBOARDING PROTOCOL
// ============================================================================
// File: 13_onboarding_protocol.cypher
// Purpose: Define a queryable ordered sequence that bootstraps an agent's
//          world model before it begins any work. Each step carries a
//          Cypher query and a natural-language explanation.
// Usage:
//   MATCH (s:SYS_OnboardingStep) RETURN s ORDER BY s.step_order
//   -- Then execute each s.query in sequence, reading s.learns for context.
// Safe: All MERGE - idempotent
// ============================================================================


// ============================================================================
// ROOT NODE
// ============================================================================

MERGE (protocol:SYS_OnboardingProtocol {protocol_id: 'onboard_v1'})
SET protocol.label = 'Chrystallum Agent Onboarding Protocol v1',
    protocol.description = 'Ordered sequence of graph queries an agent must execute on first activation. Each step builds on the prior, constructing a complete world model before the agent begins work.',
    protocol.version = '1.0',
    protocol.total_steps = 10,
    protocol.updated = datetime();


// ============================================================================
// STEPS
// ============================================================================

// Step 1: Identify yourself
MERGE (s1:SYS_OnboardingStep {step_id: 'onboard_s01'})
SET s1.step_order = 1,
    s1.label = 'Self-Identification',
    s1.learns = 'Who am I? What is my name, type, facet assignment, and capabilities?',
    s1.query = 'MATCH (a:Agent {name: $agent_name}) OPTIONAL MATCH (a)-[:ASSIGNED_TO_FACET]->(f:Facet) OPTIONAL MATCH (a)-[:INSTANCE_OF_TYPE]->(at:SYS_AgentType) RETURN a.name AS name, a.agent_type AS type, a.description AS description, a.confidence_ceiling AS confidence_ceiling, a.max_claims_per_run AS max_claims, a.federation_sources AS sources, a.governed_by_policies AS policies, a.governed_by_tables AS tables, collect(f.key) AS facets, at.capabilities AS capabilities',
    s1.explanation = 'Every agent begins by loading its own identity and understanding its scope. The confidence_ceiling caps how confident your claims can be. federation_sources lists what you can query. governed_by_policies are the rules you must follow.',
    s1.updated = datetime();

// Step 2: Understand the authority stack
MERGE (s2:SYS_OnboardingStep {step_id: 'onboard_s02'})
SET s2.step_order = 2,
    s2.label = 'Authority Tier Stack',
    s2.learns = 'What are the layers of validation that govern all knowledge in this graph?',
    s2.query = 'MATCH (t:SYS_AuthorityTier) RETURN t.tier AS tier, t.layer_name AS layer, t.description AS description, t.confidence_floor AS min_confidence, t.gates AS gates ORDER BY t.tier',
    s2.explanation = 'The 5.5-layer authority stack is the philosophical backbone of Chrystallum. Knowledge flows from Library Science (highest confidence) down through Federation, Semantic, Facet, Subject, and finally Agent Discovery (lowest confidence). Your claims enter at tier 5 and must prove their way up.',
    s2.updated = datetime();

// Step 3: Learn what node types exist
MERGE (s3:SYS_OnboardingStep {step_id: 'onboard_s03'})
SET s3.step_order = 3,
    s3.label = 'Entity Type Catalog',
    s3.learns = 'What kinds of nodes exist in the graph? What properties do they require?',
    s3.query = 'MATCH (et:EntityType) RETURN et.name AS name, et.description AS description, et.tier AS tier, et.required_properties AS required, et.canonical_outbound AS relationships, et.temporal AS temporal, et.authority_sources AS sources ORDER BY et.tier, et.name',
    s3.explanation = 'Each entity type has required properties (you must set these when creating), canonical outbound relationships (valid edges), and authority sources (where to validate). The temporal flag tells you whether this entity type uses bounding-box date queries.',
    s3.updated = datetime();

// Step 4: Learn valid relationships
MERGE (s4:SYS_OnboardingStep {step_id: 'onboard_s04'})
SET s4.step_order = 4,
    s4.label = 'Relationship Catalog',
    s4.learns = 'What edges can I create? Between what node types? What do they mean?',
    s4.query = 'MATCH (rt:SYS_RelationshipType) RETURN rt.name AS name, rt.source_label AS from_type, rt.target_label AS to_type, rt.semantic AS semantic, rt.description AS description, rt.cardinality AS cardinality ORDER BY rt.source_label, rt.name',
    s4.explanation = 'Only create edges that appear in this catalog. The semantic field tells you the conceptual role (spatial, temporal, provenance, etc.). Cardinality tells you whether edges are one-to-one, one-to-many, or many-to-many.',
    s4.updated = datetime();

// Step 5: Read the policies that govern you
MERGE (s5:SYS_OnboardingStep {step_id: 'onboard_s05'})
SET s5.step_order = 5,
    s5.label = 'Active Policies',
    s5.learns = 'What rules constrain my behavior? What am I forbidden from doing?',
    s5.query = 'MATCH (p:SYS_Policy) WHERE p.active = true OPTIONAL MATCH (p)-[:GOVERNED_BY]->(dt:SYS_DecisionTable) RETURN p.name AS policy, p.description AS description, p.priority AS priority, dt.table_id AS decision_table, dt.description AS table_description ORDER BY p.priority',
    s5.explanation = 'Policies are non-negotiable rules. If a policy says NoTemporalFacet, you cannot assign concepts to a temporal facet regardless of confidence. Each policy references a decision table where the actual condition/action logic lives.',
    s5.updated = datetime();

// Step 6: Read the decision tables (the actual logic)
MERGE (s6:SYS_OnboardingStep {step_id: 'onboard_s06'})
SET s6.step_order = 6,
    s6.label = 'Decision Table Logic',
    s6.learns = 'What are the exact conditions and actions for each decision I need to make?',
    s6.query = 'MATCH (dt:SYS_DecisionTable)-[:HAS_ROW]->(r:SYS_DecisionRow) WHERE dt.table_id IN $my_tables RETURN dt.table_id AS table_id, dt.label AS table_label, r.row_id AS row, r.priority AS priority, r.conditions AS conditions, r.action AS action, r.action_detail AS detail ORDER BY dt.table_id, r.priority',
    s6.explanation = 'Decision table rows are evaluated in priority order. Match conditions from top to bottom; the first matching row determines the action. This is the Von Halle/Goldberg/Feldman methodology — the logic IS the specification.',
    s6.updated = datetime();

// Step 7: Read active thresholds
MERGE (s7:SYS_OnboardingStep {step_id: 'onboard_s07'})
SET s7.step_order = 7,
    s7.label = 'Threshold Values',
    s7.learns = 'What are the numeric cutoffs that determine pass/fail in my decisions?',
    s7.query = 'MATCH (dt:SYS_DecisionTable)-[:USES_THRESHOLD]->(t:SYS_Threshold) WHERE dt.table_id IN $my_tables RETURN t.name AS threshold, t.value AS value, t.unit AS unit, dt.table_id AS used_by ORDER BY dt.table_id, t.name',
    s7.explanation = 'Thresholds are the numeric values plugged into decision table conditions. They can be changed without modifying the decision logic. Always read current values — never hardcode them.',
    s7.updated = datetime();

// Step 8: Learn the claim lifecycle
MERGE (s8:SYS_OnboardingStep {step_id: 'onboard_s08'})
SET s8.step_order = 8,
    s8.label = 'Claim Lifecycle States',
    s8.learns = 'What states can a claim be in? How does it move between states?',
    s8.query = 'MATCH (s:SYS_ClaimStatus) OPTIONAL MATCH (s)-[t:CAN_TRANSITION_TO]->(next:SYS_ClaimStatus) RETURN s.status AS status, s.description AS description, s.phase AS phase, s.terminal AS terminal, collect({to: next.status, trigger: t.trigger, requires: t.requires}) AS transitions ORDER BY s.phase, s.status',
    s8.explanation = 'Your claims start as proposed and move through the state machine. Understand which transitions YOU trigger (trigger=agent) vs which happen automatically (trigger=auto) vs which require human action (trigger=human). Terminal states cannot be exited.',
    s8.updated = datetime();

// Step 9: Study the golden exemplar
MERGE (s9:SYS_OnboardingStep {step_id: 'onboard_s09'})
SET s9.step_order = 9,
    s9.label = 'Golden Exemplar Trace',
    s9.learns = 'What does a correctly-executed claim look like end to end?',
    s9.query = 'MATCH (a:Agent)-[:PERFORMED]->(ar:AnalysisRun)-[:PRODUCED]->(fa:FacetAssessment) WHERE ar.is_exemplar = true WITH a, ar, fa MATCH (pe:ProposedEdge)-[:EVIDENCED_BY]->(c:Claim)-[:HAS_TRACE]->(rc:RetrievalContext) WHERE c.is_exemplar = true MATCH (c)-[:PROPOSED_BY]->(a2:Agent) RETURN a.name AS agent, ar.run_id AS run, ar.claims_proposed AS proposed, ar.claims_promoted AS promoted, c.claim_id AS claim, c.cipher AS cipher, c.text AS text, c.confidence AS confidence, c.status AS status, rc.retrieval_id AS retrieval, rc.query_used AS source_query, pe.edge_id AS proposed_edge, pe.relationship_type AS edge_type, fa.score AS assessment_score, fa.rationale AS rationale',
    s9.explanation = 'This is the reference implementation. Your outputs should follow this exact pattern: RetrievalContext (what you searched) → Claim (what you assert, with cipher) → ProposedEdge (what edge would be created) → FacetAssessment (your scoring rationale). Study the cipher format, the provenance chain, and the rationale field.',
    s9.updated = datetime();

// Step 10: Check federation sources you can access
MERGE (s10:SYS_OnboardingStep {step_id: 'onboard_s10'})
SET s10.step_order = 10,
    s10.label = 'Available Federation Sources',
    s10.learns = 'Which external data sources are operational and available to me?',
    s10.query = 'MATCH (fs:SYS_FederationSource) WHERE fs.status IN ["operational", "partial"] RETURN DISTINCT fs.name AS source, fs.status AS status ORDER BY fs.name',
    s10.explanation = 'Only query sources that are operational or partial. Planned sources are not yet available. Your Agent node lists which sources you are authorized to use — cross-reference with this list.',
    s10.updated = datetime();


// ============================================================================
// LINK STEPS TO PROTOCOL
// ============================================================================

MATCH (protocol:SYS_OnboardingProtocol {protocol_id: 'onboard_v1'})
MATCH (s:SYS_OnboardingStep)
WHERE s.step_id STARTS WITH 'onboard_s'
MERGE (protocol)-[:HAS_STEP]->(s);

// Chain steps sequentially
UNWIND range(1, 9) AS i
MATCH (curr:SYS_OnboardingStep {step_order: i})
MATCH (next:SYS_OnboardingStep {step_order: i + 1})
MERGE (curr)-[:NEXT_STEP]->(next);


// ============================================================================
// VERIFICATION
// ============================================================================

MATCH (protocol:SYS_OnboardingProtocol)-[:HAS_STEP]->(s:SYS_OnboardingStep)
RETURN protocol.label AS protocol,
       s.step_order AS step,
       s.label AS label,
       s.learns AS learns
ORDER BY s.step_order;
