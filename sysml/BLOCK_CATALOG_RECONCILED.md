# Chrystallum — SysML Block Catalog (Reconciled)

**Version:** 1.1  
**Date:** 2026-02-25  
**Target:** Visual Paradigm 17.3, SysML v1.6  
**Status:** Current  
**Supersedes:** `Key Files/2-13-26 SysML v2 System Model - Blocks and Ports (Starter).md`  
**Source of truth:** `DECISIONS.md` (all changes traceable to a decision entry)

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
- `node_count: Integer = 60925`
- `edge_count: Integer = 49152`

---

### «block» PipelineSubsystem
**Responsibility:** Four-layer data acquisition and processing. Each layer has a distinct, non-overlapping job. No decision logic — decisions are delegated to DMN services.

**Four-layer rule (D-005):** Add a property to the Harvester allowlist only if it discovers entities no current semantic property would find. If the entity would get in anyway and you just want the edge, that is EntityStore and EdgeBuilder work.

#### «block» Harvester
**Responsibility:** Entity discovery only. Narrow allowlist. Wikidata backlink traversal.  
**Implementation:** `scripts/tools/wikidata_backlink_harvest.py`  
**Value properties:**
- `max_hops: Integer = 4`
- `unresolved_class_threshold: Real = 0.20`
- `unsupported_datatype_threshold: Real = 0.10`
- `mode: String` — production | discovery

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
**Value properties:**
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
**Responsibility:** Bounded external API access. Normalisation envelope. Rate limiting and budget enforcement.  
**Value properties:**
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
**Phase 1:** Complete | **Phase 2:** Complete  
**Value properties:**
- `group_a_merged: Integer = 2960`
- `group_c_created: Integer = 1916`
- `posts_imported: Integer = 9807`
- `status_assertions: Integer = 1992`
- `match_strategy_a: String = "qid"`
- `match_strategy_c: String = "dprr_uri"`

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
**Responsibility:** 13 SYS_FederationSource nodes. Scoping advisor queries live.  
**Status:** Complete ✅ 2026-02-25  
**Value properties per source:** `name`, `status`, `confidence`, `scoping_role`, `wikidata_property`, `phase1_complete`, `phase2_complete`, `system: true`  
**Current counts:** operational (7), partial (2), planned (4)

#### «block» SYS_BibliographyRegistry
**Responsibility:** Living discovery layer. Auto-constructed from VIAF→LC SRU→MARC chain. Not a static curated list. JUSTIFIES_DESIGN_CHOICE edges from ADR nodes to literature. VIAF_SUBJECT_OF edges from Entity nodes to BibliographySource nodes.  
**Status:** Pending — 3 BibliographySource nodes exist, 0 edges  
**Build priority:** 2 (ahead of SchemaRegistry — bibliographic discovery is the most significant unbuilt agent capability)

#### «block» SYS_ProcessRegistry
**Responsibility:** SYS_ADR nodes, SYS_PipelineStage nodes, SYS_Baseline nodes. KanbanItem snapshots only — canonical KANBAN stays in KANBAN.md.  
**Status:** Pending | **Build priority:** 4

---

## DMN Decision Services (to be modeled in VP 17.3 DMN)

These were previously modeled as SysML blocks. Under D-024 they are decision services — rules externalised from code, modeled in DMN Decision Requirements Diagrams.

| Decision Service | Key inputs | Key outputs | Priority |
|-----------------|-----------|-------------|----------|
| FederationDispatcher | assertion datatype, value_type, class_gate result | route (edge_candidate / federation_id / temporal_anchor / node_property / quarantine), frontier_eligible | 1 |
| ScopingService | entity external IDs (pleiades_id, lgpn_id etc.) | is_scoped: Boolean, scoping_source: String | 1 |
| AgentRoutingService | SubjectConcept anchor, facet match, temporal scope, geographic scope | primary_agent_facet, secondary_reviewer_set, escalation_flag | 2 |
| ClaimPromotionService | review_count, consensus_score, source_agent, confidence | promote: Boolean, deny_reason: String | 2 |
| HarvestAllowlistService | PID, does_it_discover_new_entities: Boolean | include_in_allowlist: Boolean, rationale: String | 3 |

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
