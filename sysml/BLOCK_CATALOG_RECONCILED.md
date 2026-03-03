# Chrystallum — SysML Block Catalog (Reconciled)

**Version:** 1.2
**Date:** 2026-03-03
**Target:** Visual Paradigm 17.3, SysML v1.6
**Status:** Current
**Supersedes:** v1.1 (2026-02-25)
**Source of truth:** `DECISIONS.md` (all changes traceable to a decision entry)
**ADR alignment:** ADR-007 (Person Node Schema), ADR-008 (Person Harvest Agent)

---

## Reconciliation Notes (Changes from Feb-13 Starter)

| Change | Decision | Reason |
|--------|----------|--------|
| `TemporalEnrichmentPipeline` removed | D-012 | Period nodes deleted; temporal_anchor model adopted |
| `SubjectConceptCoordinator` split into `SCAEngine` + `SFAEngine` | D-008 | Two distinct contracts, different responsibilities |
| `Orchestrator` removed as runtime block | D-024 | No central orchestrator needed; pipeline is linear, SCA/SFA loop is choreographed not orchestrated |
| `AgentRouter` routing logic moved to DMN | D-024 | Routing is a decision, not a process; belongs in Decision Requirements Diagram |
| `FederationDispatcher` reframed as Decision Service | D-024 | Dispatch logic is rules, not process |
| `GovernancePolicyService` reframed as Decision Service | D-024 | Promotion eligibility is a decision table |
| `MetanodeSubsystem` added (4 child blocks) | D-015 | Self-describing subgraph |
| `SYS_BibliographyRegistry` reframed as living layer | D-025, D-026 | Auto-constructed via VIAF→LC SRU→MARC chain; grows with entity graph, not static list |
| `LibraryAuthoritySubsystem` added | D-025 | FAST + LCSH + VIAF + LC SRU as coherent subsystem |
| PID corrected: P1838 → P1047 for LGPN | D-023 | P1838 is PSS-archi (French buildings) |
| Named federation ID properties on Entity nodes | D-022 | Replaces external_ids map |
| ToolingSubsystem + ChrystallumMCPServer added | D-031 | MCP read-only server for policy/threshold; FORBIDDEN_FACETS refactor |
| ChrystallumMCPServer Phase 2: run_cypher_readonly, HTTP | D-034 | get_federation_sources, get_subject_concepts, read-only Cypher; Claude.ai connector |
| Harvester value properties → SYS_Threshold refs | D-032 | D6/D7 thresholds; ExternalFederationGateway scoping; ClusterAssignment DPRR |
| `PersonSubsystem` added (5 child blocks) | ADR-007, ADR-008 | Person node schema, onomastic layer, 3-layer harvest agent architecture |
| `OnomasticStore` added (5 node types operational) | ADR-007 §5 | Gens(585), Praenomen(24), Nomen(917), Cognomen(993), Tribe(29) — all operational |
| `PersonHarvestAgent` added (3 layers) | ADR-008 | DPRRLabelParser + PersonReasoningAgent + PersonHarvestExecutor |
| `ConflictResolutionService` added | ADR-007 §7 | CHALLENGES_CLAIM edge, ConflictNote node, Types 1–4 taxonomy |
| `SYS_HarvestPlan` added to MetanodeSubsystem | ADR-008 §4.2 | Audit trail for person harvest agent reasoning |
| DMN D10 extended for domain-scoped threshold | ADR-007 §7.4 | claim_promotion_confidence_ancient_person = 0.75 for pre-CE persons |
| DMN D15–D17 added | ADR-007 §2, §7 | Person label gate, conflict classification, conflict resolution ladder |
| Root block counts updated | Graph census 2026-03-03 | node_count: 60,925→105,559; edge_count: 49,152→107,870 |
| `DPRRAdapter` counts and onomastic parsing updated | ADR-007 §5, graph census | Onomastic parsing operational; person counts updated |
| `SYS_FederationRegistry` source count updated | Graph census | 13→17 federation source nodes |
| `VisualizationSubsystem` added | Implementation | GraphML export + cytoscape.js web viewer |

---

## Modeling Layer Separation (D-024)

Three concerns, three notations:

| Concern | Notation | Examples in Chrystallum |
|---------|----------|------------------------|
| **Data** | SysML blocks (this catalog) | Neo4j store, SubjectConcept layer, MetanodeSubsystem |
| **Rules** | DMN Decision Requirements Diagrams | Federation routing, scoping, claim promotion, agent routing, harvest allowlist |
| **Process** | Prose + SysML sequence diagrams | Pipeline flow, SCA/SFA loop |

Blocks in this catalog are **structural** — they describe what the system is composed of, not what it decides or how it sequences. Decision logic that was previously embedded in `Orchestrator` and `AgentRouter` blocks moves to the DMN model (to be built separately in VP 17.3).

---

## Block Hierarchy

```
«block» Chrystallum
  «block» PipelineSubsystem
    «block» Harvester
    «block» EntityStore
    «block» EdgeBuilder
    «block» ClusterAssignment
  «block» FederationSubsystem
    «block» ExternalFederationGateway
    «block» WikidataAdapter
    «block» DPRRAdapter
    «block» PleiadesAdapter
    «block» TrismegistosAdapter
    «block» LGPNAdapter
    «block» VIAFAdapter
    «block» GettyAATAdapter
    «block» EDHAdapter
    «block» OCDAdapter
  «block» LibraryAuthoritySubsystem         ← new (D-025)
    «block» FASTImporter
    «block» LCSHWirer
    «block» VIAFResolver
    «block» LCSRUClient
    «block» BibliographyConstructor
  «block» AgentSubsystem
    «block» SCAEngine
    «block» SFAEngine (×18 instances, one per facet)
    «block» AgentRAGStore
  «block» GovernanceSubsystem
    «block» ClaimLifecycleService
    «block» GraphPersistenceService
  «block» MetanodeSubsystem
    «block» SYS_SchemaRegistry
    «block» SYS_FederationRegistry
    «block» SYS_BibliographyRegistry
    «block» SYS_ProcessRegistry
  «block» PersonSubsystem                    ← new (ADR-007, ADR-008)
    «block» DPRRLabelParser                  ← Layer 1: deterministic onomastic extraction
    «block» PersonReasoningAgent             ← Layer 2: cross-federation reconciliation
    «block» PersonHarvestExecutor            ← Layer 3: 13-step idempotent writes
    «block» OnomasticStore                   ← Gens, Praenomen, Nomen, Cognomen, Tribe
    «block» ConflictResolutionService        ← CHALLENGES_CLAIM, ConflictNote, Types 1–4
  «block» VisualizationSubsystem             ← new (implementation)
    «block» GraphMLExporter
    «block» CytoscapeWebViewer
  «block» ToolingSubsystem         ← new (D-031)
    «block» ChrystallumMCPServer

«decisionService» PersonLabelGateService     ← DMN D15, not SysML block
«decisionService» ConflictClassificationService ← DMN D16, not SysML block
«decisionService» ConflictResolutionLadder   ← DMN D17, not SysML block
«decisionService» FederationDispatcher      ← DMN, not SysML block
«decisionService» AgentRoutingService       ← DMN, not SysML block
«decisionService» ScopingService            ← DMN, not SysML block
«decisionService» ClaimPromotionService     ← DMN, not SysML block
«decisionService» HarvestAllowlistService   ← DMN, not SysML block
```

---

## Block Definitions

---

### «block» Chrystallum
**Responsibility:** System root. Owns all subsystems. Single Neo4j Aura instance.  
**Key value properties:**
- `version: String`
- `neo4j_uri: String`
- `baseline_date: String`
- `node_count: Integer = 105559`
- `edge_count: Integer = 107870`

---

### «block» PipelineSubsystem
**Responsibility:** Four-layer data acquisition and processing. Each layer has a distinct, non-overlapping job. No decision logic — decisions are delegated to DMN services.

**Four-layer rule (D-005):** Add a property to the Harvester allowlist only if it discovers entities no current semantic property would find. If the entity would get in anyway and you just want the edge, that is EntityStore and EdgeBuilder work.

#### «block» Harvester
**Responsibility:** Entity discovery only. Narrow allowlist. Wikidata backlink traversal.  
**Implementation:** `scripts/tools/wikidata_backlink_harvest.py`  
**Decision tables:** D6 (entity class validity), D7 (harvest allowlist eligibility)

**Value properties (read from SYS_Threshold — do not hardcode):**
- `max_hops: Integer [SYS_Threshold: max_hops_p279]`
- `unresolved_class_threshold: Real [SYS_Threshold: unresolved_class_threshold]`
- `unsupported_datatype_threshold: Real [SYS_Threshold: unsupported_datatype_threshold]`
- `literal_heavy_threshold: Real [SYS_Threshold: literal_heavy_threshold]`
- `min_temporal_precision: Integer [SYS_Threshold: min_temporal_precision]`
- `sparql_limit: Integer [SYS_Threshold: sparql_limit_discovery | sparql_limit_production]` — depends on mode
- `max_sources_per_seed: Integer [SYS_Threshold: max_sources_discovery | max_sources_production]`
- `max_new_nodes_per_seed: Integer [SYS_Threshold: max_new_nodes_discovery | max_new_nodes_production]`
- `mode: String` — production | discovery (selects which budget thresholds apply via D7)

**Constraints:**
- Reads all threshold values from SYS_Threshold at startup (direct Neo4j or MCP). No hardcoded numeric values permitted. Fallback dict allowed only for credential-less runs (dry run).

**Flow ports:**
- `seedQIDsIn: ~SeedQIDSet`
- `harvestReportOut: HarvestReport`

#### «block» EntityStore
**Responsibility:** Full claims retrieval for harvested entities. All 6 Wikidata value types. Preserves qualifiers and references. Output is intermediate.  
**Implementation:** `scripts/tools/wikidata_fetch_all_statements.py`  
**Value properties:**
- `value_types: String[] = [item, string, quantity, time, monolingualtext, globecoordinate]`

**Flow ports:**
- `harvestReportIn: ~HarvestReport`
- `entityClaimsOut: EntityClaimsSet`

#### «block» EdgeBuilder
**Responsibility:** Canonical relationship mapping. All properties → typed edges. Registry + P-value alignment.  
**Implementation:** `scripts/tools/wikidata_generate_claim_subgraph_proposal.py`  
**Value properties:**
- `confidence_base: Real = 0.58`
- `unmapped_pid_ceiling: Real = 0.19`

**Flow ports:**
- `entityClaimsIn: ~EntityClaimsSet`
- `edgeProposalsOut: EdgeProposalSet`

#### «block» ClusterAssignment
**Responsibility:** Assign entities to SubjectConcepts via MEMBER_OF. Write named federation ID properties. Must be re-run after any significant import — not automatic.  
**Implementation:** `scripts/backbone/subject/cluster_assignment.py`  
**Decision tables:** D5 (federation scope match — DPRR scoping)

**Value properties:**
- `dprr_scoping_confidence: Real [SYS_Threshold: scoping_confidence_temporal_med]` — same node as temporal_med (0.85)
- `federation_id_map: String` — P1584→pleiades_id, P1696→trismegistos_id, P1047→lgpn_id, P214→viaf_id, P1014→getty_aat_id, P2192→edh_id, P9106→ocd_id
- `member_of_edges_written: Integer = 9144`
- `entities_in_clusters: Integer = 6990`

**Flow ports:**
- `edgeProposalsIn: ~EdgeProposalSet`
- `dprr_neo4jIn: ~DPRREntitySet` — optional
- `memberOfEdgesOut: MemberOfEdgeSet`

---

### «block» FederationSubsystem
**Responsibility:** All external authority file integrations. Routing decisions delegated to FederationDispatcher DMN service. No bypass of the decision service.

**Constraint:** Every external assertion must carry `source` and `retrieved_at`. No silent drops — every dropped statement emits reason metrics via DMN decision output.

#### «block» ExternalFederationGateway
**Responsibility:** Bounded external API access. Normalisation envelope. Rate limiting and budget enforcement. Scoping confidence (D5) computed here when harvester calls _compute_federation_scoping.  
**Decision tables:** D5 (federation scope match)

**Value properties (read from SYS_Threshold — do not hardcode):**
- `scoping_confidence_temporal_high: Real [SYS_Threshold: scoping_confidence_temporal_high]`
- `scoping_confidence_temporal_med: Real [SYS_Threshold: scoping_confidence_temporal_med]`
- `scoping_confidence_domain: Real [SYS_Threshold: scoping_confidence_domain]`
- `scoping_confidence_unscoped: Real [SYS_Threshold: scoping_confidence_unscoped]`
- `budget_sparql_limit: Integer`
- `budget_max_sources: Integer`
- `budget_max_new_nodes: Integer`

**Flow ports:**
- `federationQueryIn: ~FederationQuery`
- `federationResultOut: FederationResult`

#### «block» WikidataAdapter
**Status:** Operational | **Wikidata PID:** — (hub)  
**Scoping role:** Discovery and identity hub. Not a scoping source itself.  
**Phase 1:** Complete | **Phase 2:** Complete

#### «block» DPRRAdapter
**Status:** Operational | **Wikidata PID:** P6863
**Scoping role:** Elite Roman persons
**Phase 1:** Complete | **Phase 2:** Complete | **Phase 3 (Onomastic):** Complete
**Value properties:**
- `group_a_merged: Integer = 2960`
- `group_c_created: Integer = 1916`
- `posts_imported: Integer = 9807`
- `status_assertions: Integer = 1992`
- `match_strategy_a: String = "qid"`
- `match_strategy_c: String = "dprr_uri"`
- `dprr_persons_with_label: Integer = 4772`
- `onomastic_parse_operational: Boolean = true`
- `gens_nodes_created: Integer = 585`
- `praenomen_nodes_created: Integer = 24`
- `nomen_nodes_created: Integer = 917`
- `cognomen_nodes_created: Integer = 993`
- `tribe_nodes_created: Integer = 29`

**ADR-007 onomastic parsing:** DPRR label strings are parsed via grammar-based extraction (ADR-008 Layer 1) into gens_prefix, praenomen, nomen, cognomen[], tribe, and filiation_chain[]. Parsed components feed OnomasticStore node creation.

#### «block» PleiadesAdapter
**Status:** Operational | **Wikidata PID:** P1584  
**Scoping role:** Ancient places  
**Phase 1:** Complete | **Phase 2:** Pending  
**Value properties:**
- `place_nodes_imported: Integer = 41884`
- `place_nodes_enriched: Integer = 0` — Phase 2 not run
- `entities_with_pleiades_id: Integer = 164`

#### «block» TrismegistosAdapter
**Status:** Operational | **Wikidata PID:** P1696  
**Scoping role:** Non-elite persons and inscriptions (documentary/epigraphic)  
**Phase 1:** Complete | **Phase 2:** Pending  
**Value properties:**
- `current_overlap: Integer = 0` — DPRR-anchored harvest; TM persons not yet in entity set
- `api_endpoint: String = "https://www.trismegistos.org/dataservices/per/index.php"`

#### «block» LGPNAdapter
**Status:** Operational | **Wikidata PID:** P1047  
**Note:** P1838 = PSS-archi (French buildings). NOT LGPN. See D-023.  
**Scoping role:** Greek personal names  
**Phase 1:** Complete | **Phase 2:** Pending  
**Value properties:**
- `entities_with_lgpn_id: Integer = 1`
- `forward_sparql_designed: Boolean = false`

#### «block» VIAFAdapter
**Status:** Partial | **Wikidata PID:** P214  
**Scoping role:** Person name authority; entry point to library authority ecosystem  
**Phase 1:** Pending | **Phase 2:** Pending  
**Value properties:**
- `entities_with_viaf_id: Integer = 947` — confirmed via SPARQL

#### «block» GettyAATAdapter
**Status:** Partial | **Wikidata PID:** P1014  
**Scoping role:** Concept hierarchies for SubjectConcept enrichment  
**Phase 1:** Pending

#### «block» EDHAdapter
**Status:** Planned | **Wikidata PID:** P2192  
**Scoping role:** Latin inscriptions, primary source evidence  
**API:** `https://edh.ub.uni-heidelberg.de/data/api`

#### «block» OCDAdapter
**Status:** Planned | **Wikidata PID:** P9106  
**Scoping role:** Taxonomy enrichment and SFA grounding corpus  
**Source:** Public domain plain text, Archive.org

---

### «block» LibraryAuthoritySubsystem
**Responsibility:** Five-step pipeline activating the library authority ecosystem as a living discovery layer. Auto-constructs BibliographySource nodes from MARC records. Provides automatic facet routing via FAST headings. See D-025.

**Key insight:** VIAF→LC SRU→MARC is a pipeline, not a lookup. BibliographyRegistry grows automatically as entity graph grows — every new entity with viaf_id extends the bibliography chain.

**Assets already available:**
- `FASTTopical_parsed.csv` — 325MB full FAST topical export, downloaded
- `LCSH/skos_subjects/` — LCSH bulk download in JSON-LD SKOS
- Import pipeline partially built — sample working, full scale not run

#### «block» FASTImporter
**Responsibility:** Import full FAST topical dataset to Neo4j. Activates subject classification backbone.  
**Implementation:** `Python/fast/scripts/import_fast_subjects_to_neo4j.py`  
**Value properties:**
- `source_file: String = "Python/fast/key/FASTTopical_parsed.csv"`
- `source_size_mb: Integer = 325`
- `subjects_imported: Integer` — unknown until run

**Flow ports:**
- `fastCSVIn: ~FASTDataset`
- `subjectNodesOut: SubjectNodeSet`

#### «block» LCSHWirer
**Responsibility:** Build BROADER_THAN hierarchy and LCSH→FAST equivalence edges from SKOS crosswalks.  
**Implementation:** `scripts/tools/extract_lcsh_relationships.py`  
**Flow ports:**
- `subjectNodesIn: ~SubjectNodeSet`
- `lcshGraphOut: LCSHGraph`

#### «block» VIAFResolver
**Responsibility:** For each of the 947 VIAF-matched entities: resolve viaf_id → VIAF cluster → LC control number. Entry point to the MARC chain.  
**Value properties:**
- `viaf_entity_count: Integer = 947`
- `viaf_api_base: String = "https://viaf.org/viaf/"`

**Flow ports:**
- `entitySetIn: ~EntitySet`
- `lcControlNumbersOut: LCControlNumberSet`

#### «block» LCSRUClient
**Responsibility:** Free LC SRU endpoint queries. MARC authority records for persons. MARC bibliographic records for subjectOf works. No API key required.  
**Value properties:**
- `sru_endpoint: String = "https://lx2.loc.gov/lcweb2/catalog"`
- `record_schema: String = "MARC21"`

**Flow ports:**
- `lcControlNumbersIn: ~LCControlNumberSet`
- `marcRecordsOut: MARCRecordSet`

#### «block» BibliographyConstructor
**Responsibility:** Parse MARC records → construct BibliographySource nodes. Map MARC 650 fields (LCSH) → FAST equivalents → facet routing tags on bibliography nodes. Write VIAF_SUBJECT_OF edges: Entity → BibliographySource.  
**Value properties:**
- `marc_fields_used: String[] = [100, 400, 500, 650, 082, 050, 787]`
- `edge_type: String = "VIAF_SUBJECT_OF"`

**Flow ports:**
- `marcRecordsIn: ~MARCRecordSet`
- `bibliographyNodesOut: BibliographyNodeSet`

---

### «block» AgentSubsystem
**Responsibility:** SCA empirical grounding + SFA historical interpretation. Two distinct layers with defined contract. Routing delegated to AgentRoutingService DMN. See `docs/SCA_SFA_CONTRACT.md`.

**The loop:** SCA outputs feed SFA. SFA proposals flow back to graph. SCA re-scores. Neither can do the other's job.

#### «block» SCAEngine
**Responsibility:** Empirical foundation layer. Grounded harvest evidence, confidence scores, entity counts, narrative paths. Answers "what does the data support?" Queries SYS_FederationRegistry live — no hardcoded config.  
**Implementation:** `scripts/agents/sca_agent.py`  
**Value properties:**
- `subject_concepts_active: Integer = 61`
- `narrative_paths_count: Integer = 7`
- `path_weight: Real = 0.05`
- `path_weight_cap: Real = 0.15`
- `bootstrap_source: String = "SYS_FederationRegistry"`

**Flow ports:**
- `harvestEvidenceIn: ~HarvestEvidence`
- `sfaProposalsIn: ~SFAProposalSet` — re-score loop
- `scaOutputOut: SCAOutput`

#### «block» SFAEngine
**Responsibility:** Historical interpretive judgment. Within-facet concept additions, cross-facet relationship proposals, framework overlays. One instance per facet (×18). Proposals are claims, not ground truth — contestable by other SFA instances.  
**Implementation:** `scripts/agents/subject_concept_facet_agents.py`  
**Status:** 17/18 prompts built — BIOGRAPHIC missing  
**Value properties:**
- `facet: String` — one of 18 canonical UPPERCASE facets
- `proposal_confidence: Real = 0.75`
- `proposal_source: String = "sfa_inference"`
- `constitution_layer3: String[]` — methodological docs per SFA type

**Forbidden facets:** TEMPORAL, CLASSIFICATION, PATRONAGE, GENEALOGICAL

**Flow ports:**
- `scaOutputIn: ~SCAOutput`
- `sfaProposalOut: SFAProposalSet`

**Constitution layers:**
- Layer 1: Domain data from graph
- Layer 2: Primary source access via Perseus
- Layer 3: SFA-specific methodological documents (see `docs/SFA_CONSTITUTION_NOTES_2026-02-25.md`)

#### «block» AgentRAGStore
**Responsibility:** Per-agent private retrieval context. Constitution documents. Bibliography nodes accessible via VIAF chain.  
**Value properties:**
- `agent_id: String`
- `constitution_document_refs: String[]`

---

### «block» GovernanceSubsystem
**Responsibility:** Claim lifecycle management and graph persistence. No agent writes directly to Neo4j. All writes through GraphPersistenceService after policy clearance from ClaimPromotionService DMN.

#### «block» ClaimLifecycleService
**Responsibility:** Claim creation, review intake, consensus scoring, state transitions. Promotion eligibility delegated to ClaimPromotionService DMN.  
**Implementation:** `scripts/tools/claim_ingestion_pipeline.py`  
**Value properties:**
- `lifecycle_states: String[] = [proposed, validated, disputed, rejected]`

**Constraint:** `status` is lifecycle state. API operation result (`created | promoted | error`) is a separate field. Never conflate.

**Required claim properties:** `claim_id`, `cipher`, `text`, `source_agent`, `confidence`, `status`  
**Cipher:** Content-addressable cluster key — not a sequential ID.

#### «block» GraphPersistenceService
**Responsibility:** Only entry point for Neo4j writes. Constraint-safe. Write discipline: U → Pi → Commit.  
**Implementation:** `Neo4j/schema/*.cypher`, `Neo4j/schema/run_cypher_file.py`  

---

### «block» MetanodeSubsystem
**Responsibility:** Self-describing subgraph. Same Neo4j instance as domain data. Label hygiene: SYS_ prefix + `{system: true}` property. Domain queries exclude via `WHERE n.system IS NULL`.  
**Design:** `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN.md`

#### «block» SYS_SchemaRegistry
**Responsibility:** Machine-readable data dictionary. SYS_NodeType, SYS_EdgeType, SYS_Facet, SYS_PropertyDefinition nodes.  
**Status:** Pending | **Build priority:** 3 (after BibliographyRegistry)

#### «block» SYS_FederationRegistry
**Responsibility:** 17 SYS_FederationSource nodes. Scoping advisor queries live.
**Status:** Complete ✅ 2026-02-25; updated 2026-03-03
**Value properties per source:** `name`, `status`, `confidence`, `scoping_role`, `wikidata_property`, `phase1_complete`, `phase2_complete`, `system: true`
**Current counts:** 17 sources total (operational + partial + planned)

#### «block» SYS_BibliographyRegistry
**Responsibility:** Living discovery layer. Auto-constructed from VIAF→LC SRU→MARC chain. Not a static curated list. JUSTIFIES_DESIGN_CHOICE edges from ADR nodes to literature. VIAF_SUBJECT_OF edges from Entity nodes to BibliographySource nodes.  
**Status:** Pending — 3 BibliographySource nodes exist, 0 edges  
**Build priority:** 2 (ahead of SchemaRegistry — bibliographic discovery is the most significant unbuilt agent capability)

#### «block» SYS_HarvestPlanRegistry
**Responsibility:** SYS_HarvestPlan nodes — one per person harvest cycle. Complete audit trail of agent reasoning (Layer 2 output). Links to target Person node. Stores plan_id, sources_queried, identity_resolution_decisions, attribute_claims, conflict_notes, onomastic_parse, person_class, domain_scope, threshold_override, execution_status, resume_from_step, agent_model, reasoning_tokens.
**Status:** Defined in ADR-008 §4.2 | **Build priority:** 2 (needed before person harvest begins)
**Value properties:**
- `plan_count: Integer = 0` — none written yet; populated when PersonHarvestExecutor runs

#### «block» SYS_ProcessRegistry
**Responsibility:** SYS_ADR nodes, SYS_PipelineStage nodes, SYS_Baseline nodes. KanbanItem snapshots only — canonical Kanban in LachyFS extension (`.devtool/features/`).
**Status:** Pending | **Build priority:** 4

---

### «block» PersonSubsystem
**Responsibility:** Person profile construction, onomastic node management, cross-federation harvest, and conflict resolution for the Roman Republican prosopographical corpus. Three-layer architecture per ADR-008: deterministic pre-processing → agent reasoning → deterministic execution. The agent never writes directly to the graph.

**ADR alignment:** ADR-007 (Person Node Schema), ADR-008 (Person Harvest Agent Architecture)

**Key insight:** The name reconciliation problem across 7 federation sources (DPRR, Wikidata, VIAF, LC, Nomisma, Trismegistos, LGPN) is the only operation requiring agent reasoning. Everything else — label parsing, P-code mapping, date normalisation, graph writes — is deterministic.

**Census (2026-03-03):**
- `:Person` nodes: 5,149 (label applied via gates A/B/C + veto per ADR-007 §2)
- `:MythologicalPerson` nodes: 3 (Romulus, Remus, Europa)
- DPRR persons: 4,772 (with dprr_id)
- Wikidata-confirmed persons: 377 (P31→human, no dprr_id)
- Onomastic nodes: Gens(585), Praenomen(24), Nomen(917), Cognomen(993), Tribe(29)
- Onomastic edges: MEMBER_OF_GENS(4,749), HAS_NOMEN(4,531), HAS_COGNOMEN(3,758), HAS_PRAENOMEN(3,581), MEMBER_OF_TRIBE(345)
- Family edges: FATHER_OF(2,155), SIBLING_OF(2,144), MOTHER_OF(634), SPOUSE_OF(600)
- Civic edges: CITIZEN_OF(5,049), POSITION_HELD(7,342), HAS_STATUS(1,919)
- Polity nodes: 20

**Decision tables:** D10 (claim promotion — domain-scoped override), D15 (person label gate), D16 (conflict classification), D17 (conflict resolution ladder)

#### «block» DPRRLabelParser
**Responsibility:** Layer 1 deterministic pre-processing. Grammar-based extraction of tria nomina from DPRR label strings. No agent involvement. Produces structured onomastic_parse for Layer 2 and OnomasticStore.
**ADR:** ADR-008 §3.1
**Implementation:** `scripts/federation/dprr_label_parser.py` (planned)

**Token extraction rules (fixed grammar):**

| Token position | Content | Output field |
|----------------|---------|--------------|
| Prefix (4 chars) | Uppercase gens abbreviation | gens_prefix |
| Numeric suffix | DPRR person ID | dprr_id |
| Token 2 | Praenomen abbreviation (ending ".") | praenomen_abbrev |
| Token 3 | Nomen (capitalised, no period) | nomen |
| Parenthesised integer | DPRR ordinal within gens | dprr_ordinal |
| f./n. chain | Filiation: Cn. f. = son of Gnaeus | filiation_chain[] |
| 3–4 char abbreviation | Tribal abbreviation | tribe_abbrev |
| Final token(s) | Cognomen(s) | cognomen[] |

**Flow ports:**
- `dprrLabelsIn: ~DPRRLabelSet`
- `onomasticParseOut: OnomasticParseResult`

#### «block» PersonReasoningAgent
**Responsibility:** Layer 2 agent reasoning. Receives structured output of Layer 1 + federation source raw data as a context packet. Produces a PersonHarvestPlan — a complete serialised record of every decision. No graph writes occur during Layer 2. No live graph access — agent receives a pre-fetched context packet only.
**ADR:** ADR-008 §4
**Implementation:** `scripts/agents/person_harvest_agent.py` (planned)

**Tasks requiring agent reasoning:**
- Cross-federation name reconciliation (7 sources, radically different name forms)
- Conflict type classification (Types 1–4 per ADR-007 §7.1)
- Authority tier weighting (attribute-level, not source-global)
- Filiation chain disambiguation (edge cases: unknown praenomina, identical names across generations)
- Federation scope mismatch vs. genuine absence
- Mythological / legendary classification
- ConflictNote drafting (human-readable context for prosopographer review)

**Agent constraints (ADR-008 §4.3):**
- PROHIBITED: Writing any node or relationship directly to the graph
- PROHIBITED: Evaluating numeric confidence thresholds (D10 is Layer 3)
- PROHIBITED: Generating freeform Cypher
- PROHIBITED: Making promotion decisions (ApprovalRequired policy; human gate)
- PROHIBITED: Querying live graph during reasoning — all state pre-fetched

**Flow ports:**
- `contextPacketIn: ~PersonContextPacket`
- `harvestPlanOut: PersonHarvestPlan`

#### «block» PersonHarvestExecutor
**Responsibility:** Layer 3 deterministic execution. Consumes PersonHarvestPlan and executes all graph writes via schema-validated templates. 13-step idempotent execution sequence. Resumable — a timed-out harvest resumes from step N without re-reasoning.
**ADR:** ADR-008 §5
**Implementation:** `scripts/agents/person_harvest_executor.py` (planned)

**Execution sequence (dependency ordered, each step idempotent):**

| Step | Operation | Depends on |
|------|-----------|------------|
| 1 | Write SYS_HarvestPlan node | Plan complete |
| 2 | Merge :Gens, :Tribe, :Polity nodes | Onomastic parse |
| 3 | Merge :Praenomen, :Nomen, :Cognomen nodes | Step 2 |
| 4 | Apply :Person or :MythologicalPerson label | person_class decision |
| 5 | Write literal properties (dates, gender, IDs) | Step 4 |
| 6 | Write onomastic relationships | Steps 3, 4 |
| 7 | Write civic/political relationships | Step 4 |
| 8 | Write family relationship enrichments | Step 4 |
| 9 | Write office/military relationships | Step 4 |
| 10 | Write authority record links | Step 4 |
| 11 | Write conflict structures | Steps 5–10 |
| 12 | Evaluate D10 for all new Proposed claims | Steps 5–10 |
| 13 | Update SYS_HarvestPlan execution_status=COMPLETE | Step 12 |

**Value properties:**
- `execution_status: Enum = PENDING | IN_PROGRESS | COMPLETE | FAILED | RESUMED`

**Flow ports:**
- `harvestPlanIn: ~PersonHarvestPlan`
- `writeResultOut: PersonWriteReport`

#### «block» OnomasticStore
**Responsibility:** Manages the 5 first-class onomastic node types shared across persons. These are the primary axes of Roman prosopographical analysis — gens networks, tribal distributions, name patterns. Modelled as nodes (not properties) because they are query-critical.
**ADR:** ADR-007 §5

**Node types managed:**

| Label | Count | Key properties | Source |
|-------|-------|---------------|--------|
| `:Gens` | 585 | gens_id, label_latin, gens_prefix | DPRR label parse / Wikidata P5025 |
| `:Praenomen` | 24 | praenomen_id, label_latin, abbreviation | DPRR label parse / Wikidata P2358 |
| `:Nomen` | 917 | nomen_id, label_latin, gens_link | DPRR label parse / Wikidata P2359 |
| `:Cognomen` | 993 | cognomen_id, label_latin | DPRR label parse / Wikidata P2365 |
| `:Tribe` | 29 | tribe_id, label_latin, abbreviation | DPRR label parse / Wikidata P11491 |

**Relationship types:**

| Relationship | From | To | Count | Cardinality |
|-------------|------|-----|-------|-------------|
| HAS_PRAENOMEN | :Person | :Praenomen | 3,581 | 0..1 per person |
| HAS_NOMEN | :Person | :Nomen | 4,531 | 1 per person |
| HAS_COGNOMEN | :Person | :Cognomen | 3,758 | 0..* (multiple permitted) |
| MEMBER_OF_GENS | :Person | :Gens | 4,749 | 1 per person |
| MEMBER_OF_TRIBE | :Person | :Tribe | 345 | 0..1 per person |

**Constraint:** All node creation uses MERGE semantics on label_latin — no duplicate onomastic nodes permitted.

#### «block» ConflictResolutionService
**Responsibility:** Manages disagreements between federation sources for the same person attribute. Classifies conflicts into 4 types and applies resolution per ADR-007 §7.
**ADR:** ADR-007 §7
**Implementation:** `scripts/federation/conflict_resolver.py` (planned)

**Conflict type taxonomy:**

| Type | Description | Agent action |
|------|-------------|-------------|
| 1 — Precision gap | Source B more precise than A | Accept higher-precision; both as provenance |
| 2 — Silence | Source B doesn't cover attribute | Write from A; silence is not contradiction |
| 3 — Soft conflict | Overlapping but non-identical values | Compute intersection; write as range |
| 4 — Hard conflict | Non-overlapping values from covering sources | Resolution ladder (D17) → escalate if unresolvable |

**Graph structures:**
- `CHALLENGES_CLAIM` edge: challenger_source, challenge_type, created_at — links two Claim nodes
- `ConflictNote` node: conflict_type, attributes_in_dispute[], sources_involved[], tiebreaker_needed, resolution_status, ocd_applicable
- `source_authority_tier` property on claims: primary / secondary_academic / secondary_populist / tertiary

**Domain-scoped confidence threshold (ADR-007 §7.4):**
- Global: `claim_promotion_confidence = 0.90`
- Ancient persons: `claim_promotion_confidence_ancient_person = 0.75` (when Person has IN_PERIOD → Periodo_Period with end_date before year 0)

**Flow ports:**
- `conflictInputIn: ~ConflictCandidate`
- `resolutionOut: ConflictResolution`

---

### «block» VisualizationSubsystem
**Responsibility:** Graph export and interactive visualization. Read-only — no graph writes.

#### «block» GraphMLExporter
**Responsibility:** Export Neo4j subgraphs to GraphML format for Cytoscape Desktop. Five filtered views: persons_network, persons_onomastic, persons_offices, geo_roman_republic, full.
**Implementation:** `scripts/visualization/export_graphml.py`

**Value properties:**
- `person_filter: String = ":Person label"` — uses label gates, not entity_id prefix
- `geo_cap: Integer = 5000` — Roman Republic-scoped geo export capped for Desktop performance
- `gens_prefix_exported: Boolean = true` — enables Compound Spring Embedder grouping

#### «block» CytoscapeWebViewer
**Responsibility:** FastAPI + cytoscape.js interactive graph viewer. Parameterised endpoints only — no raw Cypher from client. Neo4j credentials server-side only.
**Implementation:** `scripts/visualization/cytoscape_app/app.py`

**Value properties:**
- `node_cap: Integer = 2000` — max nodes per query response
- `family_depth_default: Integer = 3` — max generations in family tree view
- `transport: String = "http"` — FastAPI on configurable port

**Endpoints (all parameterised, read-only):**
- `GET /api/person/{entity_id}?hops=1..3` — ego subgraph
- `GET /api/gens/{prefix}` — gens members via MEMBER_OF_GENS
- `GET /api/family/{entity_id}?depth=1..5` — depth-limited family tree
- `GET /api/offices/{entity_id}` — POSITION_HELD with temporal edge properties
- `GET /api/search?q=...` — label search (parameterised CONTAINS)
- `GET /api/stats` — graph summary statistics

---

## DMN Decision Services (to be modeled in VP 17.3 DMN)

These were previously modeled as SysML blocks. Under D-024 they are decision services — rules externalised from code, modeled in DMN Decision Requirements Diagrams.

| Decision Service | Key inputs | Key outputs | Priority |
|-----------------|-----------|-------------|----------|
| FederationDispatcher | assertion datatype, value_type, class_gate result | route (edge_candidate / federation_id / temporal_anchor / node_property / quarantine), frontier_eligible | 1 |
| ScopingService | entity external IDs (pleiades_id, lgpn_id etc.) | is_scoped: Boolean, scoping_source: String | 1 |
| AgentRoutingService | SubjectConcept anchor, facet match, temporal scope, geographic scope | primary_agent_facet, secondary_reviewer_set, escalation_flag | 2 |
| ClaimPromotionService | review_count, consensus_score, source_agent, confidence, domain_scope | promote: Boolean, deny_reason: String | 2 |
| HarvestAllowlistService | PID, does_it_discover_new_entities: Boolean | include_in_allowlist: Boolean, rationale: String | 3 |
| PersonLabelGateService | dprr_id, P31 targets, entity_id prefix, entity_type | person_label: Boolean, mythological: Boolean, dq_flag: String | 1 |
| ConflictClassificationService | source_A_value, source_B_value, source_coverage_map | conflict_type: Enum(1–4), recommended_action: String | 2 |
| ConflictResolutionLadder | conflict_type=4, authority_tiers, tiebreaker_sources | resolution: String, claims_written: Integer, escalate: Boolean | 2 |

---

## Claim Lifecycle State Machine

```
[*] --> proposed : claim created

proposed --> validated : review_count >= 1 AND consensus_score >= threshold
proposed --> disputed : consensus_score < threshold
validated --> disputed : counter_evidence submitted
disputed --> validated : resolution in favour
disputed --> rejected : resolution against
rejected --> [*] : terminal
```

Promotion eligibility governed by ClaimPromotionService DMN. Not agent-authoritative.

---

### «block» ToolingSubsystem
**Responsibility:** Read-only tooling for architect and dev. No write operations. Model-first discipline: catalog before spec.

#### «block» ChrystallumMCPServer
**Decision:** D-031, D-034
**Status:** Operational — v1 stdio; v2 (Phase 2) adds HTTP + run_cypher_readonly
**Implementation:** `scripts/mcp/chrystallum_mcp_server.py`

**Value properties:**
- `transport: String = "stdio" | "http"` — D-034 adds HTTP for Claude.ai
- `version: String = "1.0"`
- `write_permitted: Boolean = false`

**Flow ports:**
- `policy_query_in (in, type: PolicyQueryRequest)`
- `threshold_query_in (in, type: ThresholdQueryRequest)`
- `list_request_in (in, type: ListRequest)`
- `cypher_query_in (in, type: CypherReadOnlyQuery)` — D-034: MATCH only, 500 char, 500 row cap
- `federation_sources_out (out, type: FederationSourceList)` — D-034
- `subject_concepts_out (out, type: SubjectConceptList)` — D-034
- `response_out (out, type: MCPToolResponse)`

**Constraint:** Read-only. No write operations. Neo4j credentials never exposed to clients.

**Operations (exposed as MCP tools):**
- `get_policy(name: String): SYS_Policy`
- `get_threshold(name: String): SYS_Threshold`
- `list_policies(): SYS_Policy[]`
- `list_thresholds(): SYS_Threshold[]`

**Constraints:**
- Read-only. No write operations permitted in any version.
- Neo4j credentials never passed to MCP clients — server holds credentials, clients call tools.
- v1: stdio transport only. Cursor starts as subprocess. No network exposure.
- v2: HTTP transport added for Claude web architect validation. API key required.

**Connections:**
- Reads from: SYS_Policy (MetanodeSubsystem)
- Reads from: SYS_Threshold (MetanodeSubsystem)
- Called by: Cursor agent context (external, v1)
- Called by: Claude web architect session (external, v2 — pending)
- NOT called by: SCAEngine, SFAEngine — agents read Neo4j directly via driver

---

## Port Flow Types

| Type | Description |
|------|-------------|
| SeedQIDSet | Set of Wikidata QIDs as harvest seeds |
| HarvestReport | Per-anchor entity list with backlink metadata |
| EntityClaimsSet | Full statement set per entity (all 6 Wikidata value types) |
| EdgeProposalSet | Canonically mapped relationship proposals |
| MemberOfEdgeSet | Entity→SubjectConcept assignments |
| FederationQuery | Bounded external query with budget |
| FederationResult | Normalised assertion envelope with provenance |
| SCAOutput | Structured harvest: entity counts, confidence scores, narrative paths |
| SFAProposalSet | Within-facet additions and cross-facet proposals as claims |
| MARCRecordSet | Parsed MARC authority and bibliographic records |
| BibliographyNodeSet | Auto-constructed BibliographySource nodes with facet tags |
| LCControlNumberSet | LC control numbers from VIAF cluster resolution |
| PolicyQueryRequest | name: String — MCP tool request for SYS_Policy |
| ThresholdQueryRequest | name: String — MCP tool request for SYS_Threshold |
| ListRequest | type: String (enum: policies \| thresholds) — MCP list request |
| MCPToolResponse | content: JSON, isError: Boolean — MCP tool response |
| DPRRLabelSet | Set of DPRR label strings for onomastic parsing |
| OnomasticParseResult | Structured parse: gens_prefix, praenomen, nomen, cognomen[], tribe, filiation_chain[] |
| PersonContextPacket | Pre-fetched graph state + federation raw data for agent reasoning (ADR-008 §6) |
| PersonHarvestPlan | Serialised decisions from Layer 2: identity resolution, attribute claims, conflict notes, person_class |
| PersonWriteReport | Execution result from Layer 3: steps completed, claims written, conflicts flagged |
| ConflictCandidate | Two claims on same attribute from different sources with disagreement metadata |
| ConflictResolution | Resolution outcome: winning claim, challenger edge, ConflictNote if unresolved |

---

## Implementation Crosswalk (2026-02-25)

| Block | Implementation |
|-------|---------------|
| Harvester | scripts/tools/wikidata_backlink_harvest.py |
| EntityStore | scripts/tools/wikidata_fetch_all_statements.py |
| EdgeBuilder | scripts/tools/wikidata_generate_claim_subgraph_proposal.py |
| ClusterAssignment | scripts/backbone/subject/cluster_assignment.py |
| ExternalFederationGateway | scripts/tools/wikidata_fetch_all_statements.py |
| DPRRAdapter | scripts/federation/dprr_import.py |
| PleiadesAdapter | scripts/backbone/geographic/import_pleiades_to_neo4j.py |
| TrismegistosAdapter | scripts/integration/prosopographic_crosswalk.py |
| FASTImporter | Python/fast/scripts/import_fast_subjects_to_neo4j.py |
| LCSHWirer | scripts/tools/extract_lcsh_relationships.py |
| SCAEngine | scripts/agents/sca_agent.py |
| SFAEngine | scripts/agents/subject_concept_facet_agents.py |
| ClaimLifecycleService | scripts/tools/claim_ingestion_pipeline.py |
| GraphPersistenceService | Neo4j/schema/*.cypher |
| SYS_FederationRegistry | scripts/neo4j/rebuild_federation_registry.py |
| ChrystallumMCPServer | scripts/mcp/chrystallum_mcp_server.py |
| DPRRLabelParser | scripts/federation/dprr_label_parser.py (planned) |
| PersonReasoningAgent | scripts/agents/person_harvest_agent.py (planned) |
| PersonHarvestExecutor | scripts/agents/person_harvest_executor.py (planned) |
| OnomasticStore | scripts/neo4j/adr007_create_onomastic_nodes.py (operational) |
| ConflictResolutionService | scripts/federation/conflict_resolver.py (planned) |
| GraphMLExporter | scripts/visualization/export_graphml.py |
| CytoscapeWebViewer | scripts/visualization/cytoscape_app/app.py |

---

## Build Sequence for VP 17.3

1. ✅ Block catalog reconciled (this document)
2. BDD — System level: Chrystallum + 6 subsystems
3. BDD — AgentSubsystem: SCAEngine + SFAEngine×18 + RAGStore + constitution layers
4. BDD — FederationSubsystem: Gateway + 9 adapters
5. BDD — LibraryAuthoritySubsystem: 5-step pipeline blocks
6. IBD — PipelineSubsystem: four-layer flow, ports, connectors
7. IBD — MetanodeSubsystem: four registry blocks, internal wiring
8. IBD — LibraryAuthoritySubsystem: VIAF→LC SRU→MARC chain
9. Sequence — Harvest cycle: seed → Harvester → EntityStore → ClusterAssignment → SCA
10. Sequence — SCA/SFA loop: SCA output → SFA → graph write → SCA re-score
11. Sequence — Library authority: Entity → VIAF → LC SRU → MARC → BibliographyRegistry
12. State machine — Claim lifecycle
13. DMN — FederationDispatcher decision table (VP DMN editor)
14. DMN — ScopingService decision table
15. DMN — AgentRoutingService DRD
16. XMI export for version control
17. BDD — PersonSubsystem: 5 child blocks, 3-layer architecture
18. IBD — PersonSubsystem: Layer 1 → Layer 2 → Layer 3 flow, context packet assembly
19. Sequence — Person harvest cycle: DPRRLabelParser → PersonReasoningAgent → PersonHarvestExecutor → OnomasticStore
20. Sequence — Conflict resolution: ConflictClassificationService → ConflictResolutionLadder → human escalation
21. DMN — PersonLabelGateService (D15): 3 gates + veto
22. DMN — ConflictClassificationService (D16): Types 1–4 taxonomy
23. DMN — ConflictResolutionLadder (D17): 4-step escalation
24. BDD — VisualizationSubsystem: GraphMLExporter + CytoscapeWebViewer
