// ============================================================================
// Script 17: Co-Occurrence Meta-Relationship Layer
// ============================================================================
// PURPOSE: Adds the predicate-dropped co-occurrence signal as a first-class
//          concept in Chrystallum. Implements the Subject↔Object link that
//          exists BEFORE predicate refinement, enabling two-pass extraction.
// DEPENDS: Scripts 10-16
// CREATES: ~20 nodes, ~30 edges
//   - 1 SYS_RelationshipType: CO_OCCURS_WITH (meta-relationship)
//   - 3 SYS_ExtractionLayer nodes (Layer 0, 1, 2)
//   - 1 SYS_ConfidenceModifier (co_occurrence_untyped)
//   - 1 SYS_DecisionTable (D40_predicate_refinement)
//   - 5 SYS_DecisionRow (refinement rules)
//   - 1 SYS_ADR (ADR-008)
//   - 1 SYS_OnboardingStep (step 16)
//   - Properties SET on existing SYS_RelationshipType nodes
//   - CIDOC mappings for new nodes
// IDEMPOTENT: All statements use MERGE
// ============================================================================


// ── SECTION 1: CO_OCCURS_WITH Meta-Relationship ────────────────────────────
// This is NOT a semantic relationship. It is the statistical signal that
// two entities appear together in a shared context (sentence, paragraph,
// index entry, bibliography). It is the raw ore from which typed predicates
// are refined.

MERGE (rt:SYS_RelationshipType {name: 'CO_OCCURS_WITH', rel_type: 'CO_OCCURS_WITH'})
SET rt.source = 'ADR-008',
    rt.domain = 'Entity',
    rt.range = 'Entity',
    rt.facet = null,
    rt.added_date = '2026-03-01',
    rt.description = 'Meta-relationship: two entities co-occur in the same extraction context (sentence, paragraph, index entry, bibliography) BEFORE predicate classification. Not a semantic claim — a statistical signal. Serves as the base layer from which typed predicates are refined.',
    rt.is_meta = true,
    rt.extraction_layer = 0,
    rt.confidence_ceiling = 0.40,
    rt.cidoc_crm_class = 'E13_Attribute_Assignment',
    rt.cidoc_note = 'At Layer 0, only P140 (subject) and P141 (object) are expressed. P177 (predicate type) is absent — this is precisely the Wikidata gap.',
    rt.wikidata_pid = null,
    rt.refinement_target = true;

// Mark all existing kernel relationship types as Layer 1+ (typed predicates)
MATCH (rt:SYS_RelationshipType)
WHERE rt.name <> 'CO_OCCURS_WITH' AND rt.is_meta IS NULL
SET rt.extraction_layer = 1,
    rt.is_meta = false;


// ── SECTION 2: Extraction Layer Definitions ────────────────────────────────
// Three layers of information density, from cheapest to richest

MERGE (l:SYS_ExtractionLayer {layer_id: 'layer_0'})
SET l.label = 'Co-Occurrence (Predicate Dropped)',
    l.layer_number = 0,
    l.description = 'Subject ↔ Object link only. Two entities appear together in shared context. No claim about HOW they are related. Cheapest signal, highest recall, lowest precision.',
    l.confidence_range = '0.30-0.40',
    l.extraction_method = 'Named Entity Recognition only — no relationship parsing required',
    l.cidoc_coverage = 'P140 + P141 only (subject + object). P177 absent.',
    l.wikidata_expressible = true,
    l.cost = 'very_low',
    l.yield_per_page = '100-200 entity pairs',
    l.crminf_class = 'I2_Belief';

MERGE (l:SYS_ExtractionLayer {layer_id: 'layer_1'})
SET l.label = 'Typed Predicate (S→P→O)',
    l.layer_number = 1,
    l.description = 'Subject → Predicate → Object. The nature of the link is classified into the 48-type relationship kernel. Requires parsing and classification.',
    l.confidence_range = '0.50-0.70',
    l.extraction_method = 'Relationship extraction: pattern matching, NLP classification, or index qualifier parsing',
    l.cidoc_coverage = 'P140 + P141 + P177 (subject + object + predicate type). Full E13.',
    l.wikidata_expressible = false,
    l.wikidata_gap = 'P177 (assigned property type) has no Wikidata equivalent',
    l.cost = 'medium',
    l.yield_per_page = '30-70 typed assertions',
    l.crminf_class = 'I5_Inference_Making';

MERGE (l:SYS_ExtractionLayer {layer_id: 'layer_2'})
SET l.label = 'Qualified Predicate (S→P→O + Provenance)',
    l.layer_number = 2,
    l.description = 'Full Claim: Subject → Predicate → Object with temporal bounds, source citation, passage reference, confidence score, facet assignment, and agent provenance.',
    l.confidence_range = '0.70-0.82',
    l.extraction_method = 'Full claim pipeline: extraction + qualification + confidence scoring + provenance chain',
    l.cidoc_coverage = 'Complete E13 + I2 + I5/I7 chain with J-properties',
    l.wikidata_expressible = false,
    l.wikidata_gap = 'P177, I6 Belief Value (continuous), inference chains',
    l.cost = 'high',
    l.yield_per_page = '20-70 fully qualified claims',
    l.crminf_class = 'I5_Inference_Making';

// Layer progression edges
MATCH (l0:SYS_ExtractionLayer {layer_id: 'layer_0'})
MATCH (l1:SYS_ExtractionLayer {layer_id: 'layer_1'})
MERGE (l0)-[:REFINES_TO {mechanism: 'Predicate classification: pattern matching or NLP assigns relationship_type from 48-type kernel'}]->(l1);

MATCH (l1:SYS_ExtractionLayer {layer_id: 'layer_1'})
MATCH (l2:SYS_ExtractionLayer {layer_id: 'layer_2'})
MERGE (l1)-[:REFINES_TO {mechanism: 'Qualification: temporal bounds, source citation, confidence scoring, facet assignment, provenance chain'}]->(l2);

// CIDOC mapping for layers
MATCH (l0:SYS_ExtractionLayer {layer_id: 'layer_0'}), (cc:SYS_CidocClass {class_id: 'I2_Belief'})
MERGE (l0)-[:MAPS_TO_CIDOC {note: 'Layer 0 is a weak belief — co-occurrence without predicate'}]->(cc);

MATCH (l1:SYS_ExtractionLayer {layer_id: 'layer_1'}), (cc:SYS_CidocClass {class_id: 'I5_Inference_Making'})
MERGE (l1)-[:MAPS_TO_CIDOC {note: 'Layer 1 requires inference to classify the predicate type'}]->(cc);

MATCH (l2:SYS_ExtractionLayer {layer_id: 'layer_2'}), (cc:SYS_CidocClass {class_id: 'I5_Inference_Making'})
MERGE (l2)-[:MAPS_TO_CIDOC {note: 'Layer 2 is full inference with provenance, possibly including I7 Belief Adoption'}]->(cc);


// ── SECTION 3: Confidence Modifier for Untyped Co-Occurrence ───────────────

MERGE (cm:SYS_ConfidenceModifier {modifier_id: 'co_occurrence_untyped'})
SET cm.label = 'Untyped Co-Occurrence',
    cm.modifier_value = -0.40,
    cm.description = 'Applied when a ScaffoldEdge has relationship_type = CO_OCCURS_WITH. Reflects absence of predicate classification. Combined with secondary_academic base (0.825), yields ~0.425 — below the claim_promotion threshold.',
    cm.applies_to = 'ScaffoldEdge with CO_OCCURS_WITH',
    cm.cidoc_crm_class = 'I6_Belief_Value';


// ── SECTION 4: D40 Predicate Refinement Decision Table ─────────────────────
// Governs the upgrade from Layer 0 → Layer 1 → Layer 2
// NOTE: Originally D15, renumbered to D40 to avoid collision with
//       D15_DETERMINE_federation_state in the live graph.

MERGE (dt:SYS_DecisionTable {table_id: 'D40'})
SET dt.label = 'Predicate Refinement',
    dt.description = 'Governs how CO_OCCURS_WITH edges get refined into typed predicates. Determines when and how to upgrade Layer 0 signals to Layer 1 classified relationships.',
    dt.version = '1.0',
    dt.status = 'active';

// Row 1: Index qualifier pattern match → direct classification
MERGE (r:SYS_DecisionRow {row_id: 'D40_R01'})
SET r.condition = 'extraction_context contains qualifier phrase matching relationship_phrase_pattern',
    r.action = 'Classify CO_OCCURS_WITH → matched kernel type. Set extraction_layer = 1. Apply confidence bump +0.20.',
    r.example = '"wife of X" → SPOUSE_OF, "in alliance with X" → ALLIED_WITH',
    r.priority = 1;
MATCH (dt:SYS_DecisionTable {table_id: 'D40'}), (r:SYS_DecisionRow {row_id: 'D40_R01'})
MERGE (dt)-[:HAS_ROW]->(r);

// Row 2: Office/date parenthetical → POSITION_HELD
MERGE (r:SYS_DecisionRow {row_id: 'D40_R02'})
SET r.condition = 'extraction_context contains office abbreviation + year pattern: (cos.|pr.|tr.pl.|etc. NN B.C.)',
    r.action = 'Create typed POSITION_HELD edge with temporal anchor. Set extraction_layer = 1. Confidence +0.25 (office+year is near-unique identifier).',
    r.example = '"(cos. 46 B.C.)" → POSITION_HELD {position: consul, year: -46}',
    r.priority = 2;
MATCH (dt:SYS_DecisionTable {table_id: 'D40'}), (r:SYS_DecisionRow {row_id: 'D40_R02'})
MERGE (dt)-[:HAS_ROW]->(r);

// Row 3: Same-headword co-occurrence → infer gens membership
MERGE (r:SYS_DecisionRow {row_id: 'D40_R03'})
SET r.condition = 'Two entities share index headword in gentilicial index AND headword is a gens name',
    r.action = 'Create MEMBER_OF_GENS edge for both entities to shared gens. Set extraction_layer = 1. Confidence +0.15.',
    r.example = 'Entries under "Aemilius" headword → both MEMBER_OF_GENS Aemilii',
    r.priority = 3;
MATCH (dt:SYS_DecisionTable {table_id: 'D40'}), (r:SYS_DecisionRow {row_id: 'D40_R03'})
MERGE (dt)-[:HAS_ROW]->(r);

// Row 4: Cross-reference page overlap → strengthen co-occurrence
MERGE (r:SYS_DecisionRow {row_id: 'D40_R04'})
SET r.condition = 'Two CO_OCCURS_WITH entities share 3+ page references in same work',
    r.action = 'Apply multi_source_agreement modifier (+0.05). Flag for priority predicate classification.',
    r.example = 'Lepidus and Antonius share pages 109, 167, 192, 276 → strong co-occurrence signal',
    r.priority = 4;
MATCH (dt:SYS_DecisionTable {table_id: 'D40'}), (r:SYS_DecisionRow {row_id: 'D40_R04'})
MERGE (dt)-[:HAS_ROW]->(r);

// Row 5: No pattern match — retain as Layer 0
MERGE (r:SYS_DecisionRow {row_id: 'D40_R05'})
SET r.condition = 'No qualifier phrase, no office pattern, no structural signal',
    r.action = 'Retain as CO_OCCURS_WITH at Layer 0. Confidence remains 0.30-0.40. Mark for body-text pass if available.',
    r.example = 'Entity A appears on same page as Entity B with no qualifying text',
    r.priority = 99;
MATCH (dt:SYS_DecisionTable {table_id: 'D40'}), (r:SYS_DecisionRow {row_id: 'D40_R05'})
MERGE (dt)-[:HAS_ROW]->(r);

// Wire D40 into pipeline: D8 (source quality) → D40 → D10 (claim promotion)
MATCH (d8:SYS_DecisionTable {table_id: 'D8'})
MATCH (d40:SYS_DecisionTable {table_id: 'D40'})
MERGE (d8)-[:FEEDS_INTO]->(d40);

MATCH (d40:SYS_DecisionTable {table_id: 'D40'})
MATCH (d10:SYS_DecisionTable {table_id: 'D10'})
MERGE (d40)-[:FEEDS_INTO]->(d10);

// CIDOC mapping
MATCH (dt:SYS_DecisionTable {table_id: 'D40'}), (cc:SYS_CidocClass {class_id: 'I3_Inference_Logic'})
MERGE (dt)-[:MAPS_TO_CIDOC {note: 'Predicate refinement rules ARE inference logic applied during extraction'}]->(cc);


// ── SECTION 5: Two-Pass Extraction Pattern ─────────────────────────────────
// Formalize the two-pass architecture as a queryable process definition

MERGE (p1:SYS_ExtractionPass {pass_id: 'pass_1_co_occurrence'})
SET p1.label = 'Pass 1: Co-Occurrence Extraction',
    p1.pass_number = 1,
    p1.description = 'Fast, cheap, high-recall pass. Extract every named entity via NER. Build untyped CO_OCCURS_WITH ScaffoldEdge for every entity pair sharing an extraction context (index entry, sentence, paragraph).',
    p1.input = 'OCR text with entity boundaries identified',
    p1.output = 'ScaffoldNode per entity + CO_OCCURS_WITH ScaffoldEdge per co-occurring pair',
    p1.extraction_layer = 0,
    p1.confidence = 0.35,
    p1.cost_per_page = 'low',
    p1.entities_per_page = '30-50',
    p1.edges_per_page = '100-200',
    p1.nlp_required = 'NER only (no relationship extraction)',
    p1.frontier_discovery = true,
    p1.frontier_note = 'Entities co-occurring with known graph entities but not yet in graph are frontier candidates';

MERGE (p2:SYS_ExtractionPass {pass_id: 'pass_2_predicate_classification'})
SET p2.label = 'Pass 2: Predicate Classification',
    p2.pass_number = 2,
    p2.description = 'Slower, more expensive, high-precision pass. Classify each CO_OCCURS_WITH edge into typed predicate from 48-type kernel. Apply D40 refinement rules.',
    p2.input = 'CO_OCCURS_WITH ScaffoldEdges with extraction_context',
    p2.output = 'Typed ScaffoldEdge (ALLIED_WITH, SPOUSE_OF, etc.) + Claim with confidence + provenance',
    p2.extraction_layer = 1,
    p2.confidence = '0.50-0.82',
    p2.cost_per_page = 'medium-high',
    p2.edges_refined_per_page = '30-70',
    p2.edges_retained_layer_0 = '30-130',
    p2.nlp_required = 'Relationship extraction: pattern matching + NLP classification',
    p2.decision_table = 'D40';

// Pass sequence
MATCH (p1:SYS_ExtractionPass {pass_id: 'pass_1_co_occurrence'})
MATCH (p2:SYS_ExtractionPass {pass_id: 'pass_2_predicate_classification'})
MERGE (p1)-[:FOLLOWED_BY]->(p2);


// ── SECTION 6: Frontier Discovery from Co-Occurrence ───────────────────────
// Formalize how Layer 0 links feed entity discovery

MERGE (fd:SYS_QueryPattern {pattern_id: 'frontier_from_cooccurrence'})
SET fd.label = 'Frontier Entity Discovery via Co-Occurrence',
    fd.description = 'Find entities that co-occur with known graph entities but are not yet resolved. These are frontier candidates for entity resolution and graph expansion.',
    fd.query_template = 'MATCH (known)-[:CO_OCCURS_WITH]->(unknown:ScaffoldNode) WHERE known.entity_id IS NOT NULL AND unknown.entity_resolution_status = "unresolved" RETURN unknown, count(known) AS connection_strength ORDER BY connection_strength DESC',
    fd.use_case = 'After Pass 1, identify the most-connected unknown entities for priority resolution',
    fd.agent_relevance = 'SFA_INDEX_READER, HARVEST, RESOLUTION';


// ── SECTION 7: ADR-008 — Predicate-Dropped Co-Occurrence Layer ─────────────

MERGE (adr:SYS_ADR {adr_id: 'ADR-008'})
SET adr.title = 'Predicate-Dropped Co-Occurrence Layer',
    adr.status = 'ACCEPTED',
    adr.date = '2026-03-01',
    adr.summary = 'Text assertions decompose into three extraction layers: Layer 0 (co-occurrence, predicate dropped, S↔O only), Layer 1 (typed predicate, S→P→O), Layer 2 (qualified with provenance). CO_OCCURS_WITH is a meta-relationship type in the kernel — not semantic but statistical. Two-pass extraction: Pass 1 extracts entity pairs cheaply via NER; Pass 2 classifies predicates via D40 refinement rules. Layer 0 links enable frontier discovery: unknown entities with many co-occurrence links to known entities are priority resolution candidates.',
    adr.rationale = 'Layer 0 maps to CIDOC P140+P141 without P177 — exactly what Wikidata can express. Layer 1+ adds P177 (predicate type) — exactly what Wikidata cannot express and what Chrystallum implements. This decomposition explains where Chrystallum adds value over Wikidata and formalizes the incremental graph-building process.',
    adr.impacts = 'SFA_INDEX_READER gains two-pass architecture. All SYS_RelationshipType nodes gain extraction_layer property. D40 decision table governs predicate refinement. Confidence gradient: 0.30-0.40 (Layer 0) → 0.50-0.70 (Layer 1) → 0.70-0.82 (Layer 2).';


// ── SECTION 8: Onboarding Step 16 ─────────────────────────────────────────

MERGE (step:SYS_OnboardingStep {step_id: 'onboard_s16'})
SET step.label = 'Co-Occurrence Layer and Two-Pass Extraction',
    step.description = 'Understand the three extraction layers (co-occurrence → typed predicate → qualified claim) and the two-pass extraction architecture. CO_OCCURS_WITH is Layer 0 — a statistical signal, not a semantic claim. Pass 1 (NER) → Pass 2 (predicate classification via D40). Layer 0 links enable frontier entity discovery.',
    step.query_hint = 'MATCH (l:SYS_ExtractionLayer) RETURN l.layer_id, l.label, l.confidence_range, l.cidoc_coverage ORDER BY l.layer_number',
    step.depends_on = 'onboard_s15';

MATCH (prev:SYS_OnboardingStep {step_id: 'onboard_s15'})
MATCH (next:SYS_OnboardingStep {step_id: 'onboard_s16'})
MERGE (prev)-[:NEXT_STEP]->(next);


// ── SECTION 9: Co-Occurrence Context Types ─────────────────────────────────
// Define the extraction contexts that produce co-occurrence signals

MERGE (ctx:SYS_ExtractionContext {context_id: 'index_entry'})
SET ctx.label = 'Index Entry',
    ctx.description = 'Two entities under the same index headword or within the same indented entry. Strongest co-occurrence signal from indexes.',
    ctx.signal_strength = 'high',
    ctx.typical_confidence = 0.40;

MERGE (ctx:SYS_ExtractionContext {context_id: 'same_sentence'})
SET ctx.label = 'Same Sentence',
    ctx.description = 'Two entities mentioned in the same sentence of body text.',
    ctx.signal_strength = 'high',
    ctx.typical_confidence = 0.40;

MERGE (ctx:SYS_ExtractionContext {context_id: 'same_paragraph'})
SET ctx.label = 'Same Paragraph',
    ctx.description = 'Two entities in the same paragraph but different sentences.',
    ctx.signal_strength = 'medium',
    ctx.typical_confidence = 0.35;

MERGE (ctx:SYS_ExtractionContext {context_id: 'same_page'})
SET ctx.label = 'Same Page',
    ctx.description = 'Two entities on the same page (e.g., shared page reference in index). Weakest proximity signal.',
    ctx.signal_strength = 'low',
    ctx.typical_confidence = 0.30;

MERGE (ctx:SYS_ExtractionContext {context_id: 'shared_bibliography'})
SET ctx.label = 'Shared Bibliography',
    ctx.description = 'Two entities both cited in the same bibliographic source. Indirect co-occurrence.',
    ctx.signal_strength = 'medium',
    ctx.typical_confidence = 0.35;

MERGE (ctx:SYS_ExtractionContext {context_id: 'co_assignment'})
SET ctx.label = 'Co-Assignment (Open Syllabus)',
    ctx.description = 'Two works frequently assigned together on syllabi. Domain-level co-occurrence from Open Syllabus co-assignment graph.',
    ctx.signal_strength = 'medium',
    ctx.typical_confidence = 0.35;


// ============================================================================
// VERIFICATION QUERIES
// ============================================================================
//
// -- CO_OCCURS_WITH exists as meta-relationship
// MATCH (rt:SYS_RelationshipType {name: 'CO_OCCURS_WITH'}) 
// RETURN rt.is_meta, rt.extraction_layer, rt.confidence_ceiling
// Expected: true, 0, 0.40
//
// -- All other relationship types marked as Layer 1
// MATCH (rt:SYS_RelationshipType) WHERE rt.extraction_layer = 1 
// RETURN count(rt)
// Expected: 93 (all existing types)
//
// -- Three extraction layers
// MATCH (l:SYS_ExtractionLayer) RETURN l.layer_id, l.layer_number ORDER BY l.layer_number
// Expected: layer_0, layer_1, layer_2
//
// -- Layer refinement chain
// MATCH path = (l0:SYS_ExtractionLayer {layer_id:'layer_0'})-[:REFINES_TO*]->(end)
// WHERE NOT (end)-[:REFINES_TO]->()
// RETURN length(path), end.layer_id
// Expected: 2, layer_2
//
// -- D40 decision table with rows
// MATCH (dt:SYS_DecisionTable {table_id:'D40'})-[:HAS_ROW]->(r) RETURN count(r)
// Expected: 5
//
// -- D40 wired into pipeline
// MATCH (d8:SYS_DecisionTable {table_id:'D8'})-[:FEEDS_INTO]->(d40:SYS_DecisionTable {table_id:'D40'})-[:FEEDS_INTO]->(d10:SYS_DecisionTable {table_id:'D10'})
// RETURN d8.label, d40.label, d10.label
// Expected: 3 labels
//
// -- Two extraction passes
// MATCH (p1:SYS_ExtractionPass)-[:FOLLOWED_BY]->(p2:SYS_ExtractionPass)
// RETURN p1.label, p2.label
// Expected: Pass 1 → Pass 2
//
// -- Onboarding chain reaches step 16
// MATCH path = (s1:SYS_OnboardingStep {step_id:'onboard_s01'})-[:NEXT_STEP*]->(end)
// WHERE NOT (end)-[:NEXT_STEP]->()
// RETURN length(path), end.step_id
// Expected: 15, onboard_s16
//
// -- ADR-008
// MATCH (a:SYS_ADR {adr_id: 'ADR-008'}) RETURN a.title
// Expected: 'Predicate-Dropped Co-Occurrence Layer'
//
// -- Context types
// MATCH (ctx:SYS_ExtractionContext) RETURN count(ctx)
// Expected: 6
// ============================================================================
