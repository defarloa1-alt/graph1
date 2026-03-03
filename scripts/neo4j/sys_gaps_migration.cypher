// ============================================================================
// SYS_ Gaps Migration — 2026-03-03
// ============================================================================
// PURPOSE: Fill identified SYS_ gaps in the live graph.
//   1. Register missing SYS_ADR nodes (ADR-003, ADR-007, ADR-008)
//   2. Set name + layer on SYS_AgentType nodes (all currently null)
//   3. Register missing SYS_NodeType entries
//   4. Create SYS_HarvestPlan stub
// IDEMPOTENT: All statements use MERGE
// ============================================================================


// ── 1. Missing ADRs ─────────────────────────────────────────────────────────

// ADR-003: KBpedia Role and Boundaries (exists as docs/md, missing from graph)
MERGE (a:SYS_ADR {adr_id: 'ADR-003'})
SET a.title = 'KBpedia Role and Boundaries',
    a.status = 'PROPOSED',
    a.date = '2026-02-18',
    a.summary = 'Adopt KBpedia/KKO as a semantic typing overlay and alignment signal source, not canonical truth. Prevents parallel ontology drift and direct canonical writes from external mappings.';

// ADR-007: Person Domain Schema (spec exists in Person/adr007_extracted.txt)
MERGE (a:SYS_ADR {adr_id: 'ADR-007'})
SET a.title = 'Person Domain Schema',
    a.status = 'DRAFT',
    a.date = '2026-03-01',
    a.summary = 'Defines canonical :Person label, onomastic node types (Gens, Praenomen, Cognomen, Tribe, Polity), all relationship types, conflict resolution behaviour, label application rules, and data quality classification for the Roman Republican prosopographical corpus. Population: ~5,225 persons across DPRR and Wikidata.';

// ADR-008: Predicate-Dropped Co-Occurrence Layer
// (defined in Key Files/3-1-26-17_co_occurrence_layer.cypher, not yet loaded)
MERGE (a:SYS_ADR {adr_id: 'ADR-008'})
SET a.title = 'Predicate-Dropped Co-Occurrence Layer',
    a.status = 'ACCEPTED',
    a.date = '2026-03-01',
    a.summary = 'Three extraction layers: Layer 0 (co-occurrence, S↔O only), Layer 1 (typed predicate, S→P→O), Layer 2 (qualified with provenance). CO_OCCURS_WITH is a meta-relationship type. Two-pass extraction: Pass 1 via NER, Pass 2 via D40 refinement rules.';


// ── 2. SYS_AgentType — populate name, layer, agent_type_id ──────────────────
// Currently all 5 nodes have name=null, layer=null, id=null.
// Match by description (the only populated field) and set identity fields.

// SFA — Subject Facet Assignment
MATCH (at:SYS_AgentType)
WHERE at.description STARTS WITH 'Evaluates SubjectConcepts'
SET at.name = 'SFA',
    at.agent_type_id = 'agent_sfa',
    at.layer = 'analysis';

// HARVEST — Federation Entity Fetcher
MATCH (at:SYS_AgentType)
WHERE at.description STARTS WITH 'Fetches entities from federation'
SET at.name = 'HARVEST',
    at.agent_type_id = 'agent_harvest',
    at.layer = 'ingestion';

// DISCOVERY — Relationship Discovery
MATCH (at:SYS_AgentType)
WHERE at.description STARTS WITH 'Analyzes existing entities'
SET at.name = 'DISCOVERY',
    at.agent_type_id = 'agent_discovery',
    at.layer = 'analysis';

// RESOLUTION — Entity Resolution
MATCH (at:SYS_AgentType)
WHERE at.description STARTS WITH 'Detects and merges duplicate'
SET at.name = 'RESOLUTION',
    at.agent_type_id = 'agent_resolution',
    at.layer = 'ingestion';

// VALIDATION — Graph Integrity Checks
MATCH (at:SYS_AgentType)
WHERE at.description STARTS WITH 'Runs SYS_ValidationRule'
SET at.name = 'VALIDATION',
    at.agent_type_id = 'agent_validation',
    at.layer = 'quality';


// ── 3. Missing SYS_NodeType registrations ───────────────────────────────────
// Currently 10 registered. 30 domain labels exist but aren't in SYS_NodeType.
// Registering the ones that represent stable domain concepts.

// Person domain (from ADR-007)
MERGE (:SYS_NodeType {name: 'Person'});
MERGE (:SYS_NodeType {name: 'MythologicalPerson'});
MERGE (:SYS_NodeType {name: 'Gens'});
MERGE (:SYS_NodeType {name: 'Praenomen'});
MERGE (:SYS_NodeType {name: 'Nomen'});
MERGE (:SYS_NodeType {name: 'Cognomen'});
MERGE (:SYS_NodeType {name: 'Tribe'});
MERGE (:SYS_NodeType {name: 'Polity'});
MERGE (:SYS_NodeType {name: 'Religion'});

// Classification / reference
MERGE (:SYS_NodeType {name: 'LCC_Class'});
MERGE (:SYS_NodeType {name: 'LCSH_Heading'});
MERGE (:SYS_NodeType {name: 'WorldCat_Work'});
MERGE (:SYS_NodeType {name: 'BibliographySource'});

// Geo-semantic
MERGE (:SYS_NodeType {name: 'PlaceType'});
MERGE (:SYS_NodeType {name: 'GeoSemanticType'});
MERGE (:SYS_NodeType {name: 'HistoricalPolity'});

// Provenance / process
MERGE (:SYS_NodeType {name: 'Agent'});
MERGE (:SYS_NodeType {name: 'AnalysisRun'});
MERGE (:SYS_NodeType {name: 'FacetAssessment'});
MERGE (:SYS_NodeType {name: 'ProposedEdge'});
MERGE (:SYS_NodeType {name: 'RetrievalContext'});
MERGE (:SYS_NodeType {name: 'StatusType'});
MERGE (:SYS_NodeType {name: 'EntityType'});

// Structural roots / registries (internal)
MERGE (:SYS_NodeType {name: 'EntityRoot'});
MERGE (:SYS_NodeType {name: 'FacetRoot'});
MERGE (:SYS_NodeType {name: 'DisciplineRegistry'});
MERGE (:SYS_NodeType {name: 'SubjectConceptRegistry'});
MERGE (:SYS_NodeType {name: 'Root'});
MERGE (:SYS_NodeType {name: 'Schema'});
MERGE (:SYS_NodeType {name: 'Chrystallum'});


// ── 4. SYS_HarvestPlan stub ─────────────────────────────────────────────────
// No SYS_HarvestPlan label exists in graph. Create the initial stub
// that the Harvest agent will use to track planned harvest operations.

MERGE (hp:SYS_HarvestPlan {plan_id: 'harvest_plan_person_v1'})
SET hp.label = 'Person Domain Harvest Plan',
    hp.description = 'Harvest plan for Person domain entities. Covers DPRR label enrichment, Wikidata P-code resolution, onomastic node creation, and cross-federation authority linking.',
    hp.status = 'planned',
    hp.target_domain = 'Person',
    hp.adr_ref = 'ADR-007',
    hp.federation_sources = ['DPRR', 'Wikidata', 'VIAF', 'FAST', 'Trismegistos', 'LGPN', 'Nomisma'],
    hp.estimated_entities = 5225,
    hp.created_date = '2026-03-03';


// ============================================================================
// VERIFICATION QUERIES
// ============================================================================
//
// -- ADRs now include 003, 007, 008
// MATCH (a:SYS_ADR) RETURN a.adr_id, a.title, a.status ORDER BY a.adr_id
// Expected: 8 rows (001, 002, 003, 004, 005, 006, 007, 008)
//
// -- All agent types have name and layer
// MATCH (at:SYS_AgentType) RETURN at.name, at.layer
// Expected: 5 rows, no nulls
//
// -- Node types registered
// MATCH (nt:SYS_NodeType) RETURN count(nt)
// Expected: ~39 (10 existing + 29 new)
//
// -- Harvest plan exists
// MATCH (hp:SYS_HarvestPlan) RETURN hp.plan_id, hp.status
// Expected: 1 row
//
// ============================================================================
