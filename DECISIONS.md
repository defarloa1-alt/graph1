# Chrystallum — Decision Log

**Format:** Chronological append-only. Topical index at top updated at milestones.
**Purpose:** Preserve *why* decisions were made. KANBAN tracks *what*. Architecture docs track *how*.
**Owners:** Architect (Claude) + Dev. Both append. Neither edits past entries.

---

## Topical Index

| Topic | Entries |
|-------|---------|
| Schema / node model | D-003, D-004, D-007, D-008, D-022, D-028 |
| Federation | D-006, D-014, D-022, D-023 |
| Pipeline / harvester | D-009, D-010, D-011 |
| Agent architecture (SCA/SFA) | D-012, D-013 |
| Temporal model | D-005, D-015 |
| Self-describing subgraph | D-016, D-017, D-018, D-026, D-029 |
| Graph cleanup | D-001, D-002, D-015, D-027 |
| Process / governance | D-019, D-020 |
| Mercury / sequencing | D-021 |
| Modeling (SysML/DMN/BPMN) | D-024, D-030 |
| Library authority / bibliography | D-025, D-026, D-028 |
| MCP / tooling | D-031, D-034 |
| D6/D7 threshold refactor | D-032 |
| D10/D8 claim promotion + SFA confidence | D-033 |

---

## Entries

---

### D-034 — MCP Phase 2: Read-Only Graph Query + HTTP Transport
**Date:** 2026-02-25  
**Status:** Decided — spec ready for build  
**Context:** Architect pre-work cycle (write queries → dev runs → dev reports) is slow and loses fidelity. Claude.ai needs direct graph access for Library Authority pre-work and future workstreams.  
**Decision:** Extend MCP server with (1) `get_federation_sources()` and `get_subject_concepts()`, (2) `run_cypher_readonly` with strict allowlist (MATCH only; block CREATE/SET/DELETE/MERGE/CALL/LOAD; 500 char limit; 500 row cap), (3) HTTP transport for Claude.ai connector. Deploy to Railway (or similar) with Neo4j credentials as env secrets.  
**Rationale:** Architect queries graph directly → interprets → specs Phase 3 from live state. Serves every future workstream, not just Library Authority.  
**Consequences:** docs/D034_MCP_PHASE2_SPEC.md; chrystallum_mcp_server.py extended; HTTP layer added; block catalog updated.

**Gaps (2026-02-25):** SYS_FederationSource pid/scoping_weight/property_name null — stub nodes only. Populate before federation subsystem goes live.

---

### D-033 — D10 Claim Promotion + D8 SFA Confidence (Round 3)
**Date:** 2026-02-25  
**Status:** Decided — build complete  
**Context:** claim_ingestion_pipeline.py hardcoded 0.90/0.90 for promotion; subject_concept_facet_agents.py and sca_agent.py hardcoded 0.8 for proposal confidence. D10 and D8 tables specify SYS_Threshold/SYS_Policy.  
**Decision:** claim_ingestion_pipeline reads claim_promotion_confidence, claim_promotion_posterior from SYS_Threshold; checks ApprovalRequired from SYS_Policy (or Policy). If ApprovalRequired active, never auto-promote. subject_concept_facet_agents and sca_agent read sfa_proposal_confidence_default from SYS_Threshold for proposal confidence defaults.  
**Rationale:** Governance layer thresholds live in graph. ApprovalRequired policy is now live configuration.  
**Consequences:** claim_ingestion_pipeline.py, subject_concept_facet_agents.py, sca_agent.py refactored. Fallback 0.90/0.90/False and 0.75 when graph unavailable.

---

### D-032 — D6 Threshold Refactor (Harvester + ClusterAssignment)
**Date:** 2026-02-25  
**Status:** Decided — build complete  
**Context:** Harvester (wikidata_backlink_harvest.py) and ClusterAssignment (cluster_assignment.py) hardcode D6/D5/D7 threshold values. Block catalog updated first (model before build).  
**Decision:** Harvester reads 11 thresholds from SYS_Threshold at startup via direct Neo4j; CLI args become overrides. ClusterAssignment reads scoping_confidence_temporal_med for DPRR entities. ExternalFederationGateway scoping confidence (0.95, 0.85, 0.40) from SYS_Threshold in harvester's _compute_federation_scoping.  
**Rationale:** Single source of truth. Model-first: catalog updated before script refactor.  
**Consequences:** wikidata_backlink_harvest.py, cluster_assignment.py refactored. MODE_DEFAULTS remains as fallback for credential-less runs. Process doc committed with Round 2.

---

### D-030 — DMN Tables D1–D14 Complete
**Date:** 2026-02-25  
**Status:** Decided — tables documented  
**Context:** D-024 established SysML + DMN modeling approach. Five priority DMN decisions were identified; block catalog and extraction audit surfaced the full set of decision tables.  
**Decision:** Commit the complete D1–D14 decision table set as the canonical DMN layer. Tables: D1 (FederationRouting), D2 (ScopingAdvisor), D3 (ClusterAssignment), D4 (AgentRouter), D5 (HarvestAllowlist), D6 (HarvesterThresholds), D7 (HarvestAllowlistRefactor), D8 (SFAProposalConfidence), D9 (ClaimLifecycle), D10 (ClaimPromotion), D11 (SplitTrigger), D12 (ReadPathEntity), D13 (ReadPathSubjectConcept), D14 (EntityResolutionThresholds). Logic in tables; values in SYS_Threshold/SYS_Policy/SYS_PropertyMapping nodes.  
**Rationale:** Single source of truth for decision logic. Code reads from graph; domain expert updates nodes, not code. Completes the DMN layer started in D-024.  
**Consequences:** sysml/DMN_DECISION_TABLES.md; extraction audit; D6/D10/D8 refactors (D-032, D-033) implement table reads.

---

### D-031 — MCP Read-Only Server (Local-First)
**Date:** 2026-02-25  
**Status:** Decided — build complete  
**Context:** FORBIDDEN_FACETS was hardcoded identically in sca_agent.py and subject_concept_facet_agents.py — known fragmentation point from DMN extraction audit. SYS_Policy nodes already exist with correct values.  
**Decision:** Build a minimal MCP server (Python, stdio transport) exposing `get_policy(name)` and `get_threshold(name)` reading from SYS_Policy and SYS_Threshold. Refactor both scripts to read forbidden facets from graph via direct Neo4j driver (SCA already has connection; MCP tool is for Cursor agents and external callers). Cursor integration only in v1 — no HTTP, no Claude web.  
**Rationale:** Single source of truth for policy/threshold values. Any change in graph propagates everywhere. FORBIDDEN_FACETS refactor is acceptance test.  
**Consequences:** scripts/mcp/chrystallum_mcp_server.py, .cursor/mcp.json, SYS_Policy facet_key property, sca_agent and subject_concept_facet_agents refactored. Phase 2: get_federation_sources, get_subject_concepts, HTTP transport for Claude web.

---

### D-027 — Delete Staging Node Labels (Graph Cleanup)
**Date:** 2026-02-21  
**Status:** Decided  
**Context:** Node label audit identified four labels as remnants of earlier pipeline passes: FacetedEntity (360), PeriodCandidate (1,077), PlaceTypeTokenMap (212), GeoCoverageCandidate (357). PeriodCandidate is consistent with D-012 — period model was deleted. The others are pre-cleanup staging artifacts.  
**Decision:** Delete all five labels. FacetedEntity: orphaned Tier 2 cipher hubs, 0 edges. PeriodCandidate: staging for period canonicalization, all canonicalized. PlaceTypeTokenMap: pipeline lookup table. GeoCoverageCandidate: staging join linking PeriodCandidate↔Period. StatusType: orphaned enumeration stubs (2 nodes, label "1"/"2"), no architectural value.  
**Rationale:** No architectural question — these are staging artifacts with no downstream dependencies. Cleanup before further schema work.  
**Consequences:** Run delete Cypher; confirm counts. Add StatusType (2 nodes) to delete — orphaned enumeration stubs. Add Schema 3 (Period, D-012 stale artifact) and Schema 9 (empty stub) to delete. Add Schema 5 or 6 (one of two duplicate Wikidata-only stubs) — investigation confirmed duplicates. Do not delete PropertyMapping, KnowledgeDomain, Policy, or Threshold — those require reclassification (D-029).

---

### D-029 — Reclassify PropertyMapping, Policy, Threshold, KnowledgeDomain into Metanode
**Date:** 2026-02-21  
**Status:** Decided  
**Context:** Investigation found PropertyMapping (706), Policy (5), Threshold (3), KnowledgeDomain (1) are not staging artifacts. They are the embryo of an externalised rule system — partially built, disconnected. PropertyMapping encodes PID→facet mappings (EdgeBuilder/HarvestAllowlistService data substrate). Policy and Threshold encode governance rules (federation priority, forbidden facets, claim promotion, split triggers) that are currently hardcoded in code and prompts. KnowledgeDomain is a single root anchor for the 61 SubjectConcepts, not a domain classification system.  
**Decision:** Reclassify, do not delete. (1) **PropertyMapping** → migrate to Metanode as SYS_PropertyMapping. System configuration data; data substrate for DMN decision tables. Add `system: true`. (2) **Policy + Threshold** → migrate to Metanode as SYS_Policy and SYS_Threshold. Externalised rule values; DMN tables will read them. Add `system: true`. (3) **KnowledgeDomain** (1 node, "Roman Republic" Q17167) → absorb into SYS_SchemaRegistry design as SubjectConcept root anchor. Remove KnowledgeDomain label, add SYS_SubjectConceptRoot, `system: true`. Do not rename nodes yet — confirm migration approach first. Do not modify values yet.  
**Rationale:** The graph already contains the right intent. The DMN work completes what was started. Tables hold logic; nodes hold values. Domain expert adds PropertyMapping node for new PID, not code change.  
**Consequences:** Run dependency check before migration. load_federation_metadata.py creates Policy/Threshold; import_property_mappings_direct.py creates PropertyMapping; load_subject_concepts_qid_canonical.cypher creates KnowledgeDomain. No operational script currently reads Policy or Threshold for decision logic. PropertyMapping read only by verification scripts, not pipeline.

---

### D-028 — Subject vs SubjectConcept: Distinct Layers, Do Not Conflate
**Date:** 2026-02-21  
**Status:** Decided  
**Context:** Node label audit raised the question of Subject (LCSH/FAST, 0 nodes) vs SubjectConcept (61 nodes). Library Authority Step 1 will create Subject nodes. Risk of conflation would break SCA/SFA architecture.  
**Decision:** Subject and SubjectConcept are distinct layers. **Subject** = library classification infrastructure (LCSH/FAST, controlled vocabulary, lcsh_id/fast_id, BROADER_THAN hierarchy). Maintained by LibraryAuthoritySubsystem. **SubjectConcept** = interpretive anchor (thematic domain for SCA/SFA, narrative paths, facet assignments). Maintained by agent layer. Relationship: Subject CLASSIFIES SubjectConcept (proposed edge type). One informs the other; neither replaces the other.  
**Rationale:** Subject is classification infrastructure. SubjectConcept is scholarly judgment about what entities cohere around. Conflating them would break agent routing and MEMBER_OF semantics.  
**Consequences:** Library Authority Step 1 can proceed with clear Subject node design. Do not merge, do not conflate. FAST import creates Subject nodes; SubjectConcept remains separate.

---

### D-026 — BibliographyRegistry: Living Discovery Layer, Not Static List
**Date:** 2026-02-25  
**Status:** Decided  
**Context:** BibliographyRegistry was conceived as a manually curated list of books to include. D-025 (Library Authority Integration) reframes it: the VIAF→LC SRU→MARC pipeline auto-constructs BibliographySource nodes from entities with viaf_id.  
**Decision:** BibliographyRegistry is a **living discovery layer** — it grows as the entity graph grows. Every cluster assignment run that writes viaf_id onto new entities extends the bibliography chain automatically. The pipeline runs alongside the entity graph as infrastructure, not a one-time build. The node model must reflect this: dynamic extension, not manual population.  
**Rationale:** "Populate BibliographyRegistry then maintain it manually" is the wrong mental model. The right model: bibliography discovery is infrastructure that extends whenever new entities with VIAF IDs enter the graph.  
**Consequences:** Metanode design (SELF_DESCRIBING_SUBGRAPH_DESIGN, BLOCK_CATALOG) updated before SchemaRegistry build. BibliographyRegistry node model documents dynamic extension semantics.

---

### D-023 — LGPN Is P1047, Not P1838 (lgpn_id Mapping Fix)
**Date:** 2026-02-25  
**Status:** Decided  
**Context:** Backfill reported `lgpn_id = 'FR-75056-20'` on Montparnasse Tower (Q323767). LGPN IDs are ancient Greek person identifiers; FR-75056-20 is a French administrative/building code. Investigation: Wikidata Property:P1838 is **PSS-archi ID** (identifier for buildings in pss-archi.eu), not Lexicon of Greek Personal Names (LGPN). Project docs incorrectly assumed P1838 = LGPN.  
**Decision:** LGPN Wikidata property is **P1047**. Add P1047 → `lgpn_id` to cluster_assignment. Remove P1838 from lgpn_id mapping. Clear existing bogus values (2 entities) via `scripts/neo4j/clear_bogus_lgpn_id.cypher`. Update all references: SYS_FederationSource, scoping advisor, harvester, wikidata_lgpn_forward_harvest.py, FEDERATION_REGISTRY_REBUILD_SPEC, HARVESTER_SCOPING_DESIGN.  
**Alternatives considered:** Add format validation (reject FR-* pattern) — still wrong property; add `pss_archi_id` for P1838 — out of scope for Roman Republic federation set.  
**Rationale:** PID collision: P1838 = PSS-archi (buildings), P1047 = LGPN (ancient Greek persons). Writing PSS-archi IDs to `lgpn_id` corrupts the prosopographic layer.  
**Consequences:** cluster_assignment maps P1047 to lgpn_id. All federation docs and scripts use P1047 for LGPN. Re-run FederationRegistry rebuild to update SYS_FederationSource. Run P1047 overlap SPARQL for real LGPN count.

---

### D-025 — Library Authority Integration: Comprehensive Workstream
**Date:** 2026-02-25  
**Status:** Decided  
**Context:** VIAF (P214) was scoped as a standalone Phase A task — write viaf_id onto 947 Entity nodes. On examination, VIAF is the entry point to a full library authority ecosystem: FAST (faceted subject headings), LCSH (subject hierarchy), LC SRU (free MARC API), and WorldCat (holdings). We already have FASTTopical_parsed.csv (325MB downloaded, never fully imported to Neo4j), LCSH bulk download (sample only), and a partially built import pipeline. The VIAF→LC SRU→MARC path is free with no API key required.  
**Decision:** Treat library authority integration as a single coherent workstream, not scattered Phase tasks. Five steps in sequence: (1) Full FAST import to Neo4j. (2) LCSH→FAST hierarchy wiring via SKOS crosswalks. (3) VIAF→LC SRU MARC authority record pull for 947 VIAF-matched entities. (4) subjectOf bibliography construction — VIAF subjectOf links → MARC bibliographic records → BibliographySource nodes auto-constructed. (5) FAST headings on bibliography nodes → facet routing. WorldCat backlogged — no OCLC API procurement at this stage (no academic affiliation).  
**Alternatives considered:** VIAF as standalone Phase A task; WorldCat API procurement.  
**Rationale:** The key insight is that VIAF→WorldCat→MARC is a pipeline that auto-constructs BibliographyRegistry nodes. Instead of manually entering bibliography, SFAs discover it via the authority chain. FAST headings on MARC records provide automatic facet routing. The library backbone (FAST/LCSH/LCC) already in the graph was being used passively — this workstream makes it active. LC SRU covers the scholarly canon for Roman Republic studies without WorldCat.  
**Consequences:** VIAF standalone task removed from KANBAN. Replaced by Library Authority Integration workstream (5 steps). BibliographyRegistry build priority moves ahead of SchemaRegistry — bibliographic discovery is the most significant unbuilt agent capability. WorldCat added to backlog for future procurement if academic affiliation becomes available.

---

### D-024 — Modeling Approach: SysML + DMN, No BPMN
**Date:** 2026-02-25  
**Status:** Decided. Pinned — third thread, revisit after operational + metanode threads stabilise.  
**Context:** Question of whether to use BPMN for process modeling alongside SysML. Underlying architectural principle: all systems decompose into Data, Rules, and Process as orthogonal concerns. Rules belong outside code following Von Halle / Feldman / Ross Decision Model principles (DMN). Process modeling notation should only be used where rigor adds value over prose.  
**Decision:** Three-notation stack: (1) SysML v1.6 in VP 17.3 for structural model — block decomposition, port contracts, state machines. (2) DMN for decision layer — rules externalised from code into Decision Requirements Diagrams and Decision Tables. (3) Prose + SysML sequence diagrams for process flows — pipeline is simple enough that BPMN adds ceremony without clarity.  
**Alternatives considered:** Full BPMN for all process flows.  
**Rationale:** Chrystallum's processes are linear or simple loops — a BPMN diagram of the harvest pipeline is a straight line with five boxes. Not worth the notation overhead. The decision layer is where complexity lives — routing, scoping, promotion eligibility, federation class gates — and DMN is the right tool for that. BPMN earns its keep when processes have complex branching, parallel lanes, compensation flows, or message choreography between independent systems. Chrystallum has none of these currently.  
**Consequences:** Orchestrator block removed from SysML block catalog. AgentRouter routing logic moves to DMN Decision Requirements Diagram. FederationDispatcher becomes a Decision Service in DMN. GovernancePolicyService and ClaimLifecycleService become DMN decision tables. Five priority DMN decisions identified: federation routing, scoping, claim promotion, agent routing, harvest allowlist. Block catalog to be updated before XMI generation.

---

### D-022 — External IDs Persistence: Named Properties per Federation
**Date:** 2026-02-25  
**Status:** Decided  
**Context:** `external_ids` was removed from cluster_assignment WRITE_QUERY due to Neo4j 5/Aura Map param rejection. Result: federation IDs (P1584, P1696, P1838 etc.) are used for scoping but not persisted on Entity nodes. Every enrichment script must re-query Wikidata instead of reading from the graph. Problem compounds with each new federation added.  
**Decision:** Option B — separate named properties per federation PID on Entity nodes. Properties: `pleiades_id` (P1584), `trismegistos_id` (P1696), `lgpn_id` (P1838), `dprr_uri` (already exists), `viaf_id` (P214), `getty_aat_id` (P1014), `edh_id` (P2192), `ocd_id` (P9106). Use federation names not PIDs — `pleiades_id` not `P1584`.  
**Alternatives considered:** (A) JSON string property — requires APOC, loses index support; (C) Generated Cypher file — two write paths; (D) Re-test Map param — one attempt worth making but not the plan; (E) Separate enrichment pass — moves not solves the problem.  
**Rationale:** Eight named properties is not schema bloat. Each property is directly queryable with native Cypher and index-supported. Federation names are legible without lookup. Each federation's enrichment script queries its own property cleanly.  
**Consequences:** Update WRITE_QUERY in cluster_assignment. Update schema constraints to document as optional Entity properties. Re-run cluster assignment to backfill existing entities. All future enrichment scripts read named properties, not external_ids map.

---

### D-021 — Project Mercury Deprioritised
**Date:** 2026-02-25  
**Status:** Decided  
**Context:** Project Mercury (CHRR + CRRO numismatic federations) was the planned next major operational milestone after DPRR. CHRR provides coin hoard findspots; CRRO provides Republican coinage with issuing magistrate IDs linking to DPRR persons via Nomisma.  
**Decision:** Deprioritise Mercury. Run foundation federations first in sequence: Trismegistos crosswalk, VIAF, Pleiades Phase 2, LGPN, Getty AAT, Trismegistos Phase 2, EDH, OCD. Mercury moves to Phase D (specialised evidence, SFA-specific).  
**Alternatives considered:** Run Mercury next as originally planned.  
**Rationale:** Mercury's evidence chain (coin → findspot → place) requires Pleiades Phase 2 to close. 41,884 Place nodes currently have 0 edges. Running Mercury before Pleiades Phase 2 builds the middle of a bridge — material evidence nodes that cannot complete their geographic chain. Coins are important to specific SFAs (numismatic, economic historian) but are not foundational infrastructure. Foundation before specialisation.  
**Consequences:** Mercury sequenced after Pleiades Phase 2. Revised sequence in KANBAN Phases A–D. No work lost — Mercury spec remains valid, just repositioned.

---

### D-001 — SubjectConcept ID Refactor (Priority 0)
**Date:** 2026-02-23  
**Status:** Decided, not yet executed  
**Context:** Two hand-authored slugs (`subj_rr_soc_family_gentes` and `subj_rr_family_gentes`) resolved to the same Wikidata QID (Q899409, "gens"). The `rr` magic string encoded domain scope as a literal instead of a QID. SubjectConcept identity was hand-authored in `load_roman_republic_ontology.py`, not derived from the knowledge graph.  
**Decision:** Invert the flow. LLM reasons over Wikidata to determine which scholarly concepts exist under Q17167. `subject_id` is derived: `subj_{root_qid}_{anchor_qid}`. Example: `subj_Q17167_Q899409`.  
**Alternatives considered:** Keep slug system, add deduplication layer.  
**Rationale:** Building SFAs on the legacy slug system compounds migration debt badly. Vocabulary loading, harvest, cluster assignment, and SFA prompts all key off `subject_id`. One refactor now prevents a painful migration later.  
**Consequences:** Must complete before SFA build or vocabulary loading begins. `SUBJECT_CONCEPT_AGENTS_GUIDE.md` (dated 2026-02-20) still uses legacy slug format — guide is pre-decision and needs updating before SFA implementation sprint.  

---

### D-002 — Pipeline Contract: QID as Merge Key
**Date:** 2026-02-22  
**Status:** Implemented  
**Context:** Multi-seed harvests (Roman Republic + Ancient Greek History) were creating duplicate Entity nodes because merge keys were inconsistent.  
**Decision:** `MERGE (n:Entity {qid: $qid})` — QID is the identity key for all Wikidata-derived Entity nodes. Schema constraint `entity_qid_unique` enforces this.  
**Alternatives considered:** Label + name composite key.  
**Rationale:** QID is globally unique and stable. Composite keys on labels are fragile across language variants and name changes.  
**Consequences:** QID-less SubjectConcepts (hand-authored) must carry `authority_federation_state: "FS0_SYNTHETIC"` and `source: "synthetic"` to distinguish them.  

---

### D-003 — Separate Entity Classification from Property→Facet Mapping
**Date:** 2026-02-21  
**Status:** Implemented  
**Context:** Property labels sometimes returned as PID (e.g. "P8596") when Wikidata had no English label. These were sent to the LLM using the entity classification prompt ("Is this Period, Event, or SubjectConcept?"). The LLM produced SubjectConcepts from property descriptions. Those had no QIDs and were imported as islands with no MEMBER_OF edges — phantom SubjectConcepts.  
**Decision:** Never conflate the two operations. Entity→SubjectConcept classification uses `_classify_with_perplexity` (entities only). Property→facet mapping uses CSV lookup or `llm_resolve_unknown_properties.resolve_property_with_llm`. Two separate prompts, two separate pipelines, never mixed.  
**Alternatives considered:** Single unified classification prompt.  
**Rationale:** The failure mode (phantom SubjectConcepts with no graph connections) is silent and hard to detect. Separation makes the error impossible structurally.  
**Consequences:** Any future pipeline change that routes property descriptions to the entity classification prompt is a regression. QA should test for phantom SubjectConcepts (nodes with label SubjectConcept, zero MEMBER_OF edges, no QID) after any harvester change.  

---

### D-004 — Traversal-First Flow (Entities Before SubjectConcepts)
**Date:** 2026-02-22  
**Status:** Implemented  
**Context:** Early versions attempted to discover SubjectConcepts and entities simultaneously, causing circular dependencies in classification.  
**Decision:** Three-stage flow with no conflation. (1) Traversal discovers entities via MERGE on QID. (2) SubjectConcepts are predefined — hand-authored or LCSH-derived. (3) Cluster assignment runs separately: entities → MEMBER_OF → SubjectConcepts.  
**Alternatives considered:** Simultaneous discovery and classification.  
**Rationale:** Deterministic ordering eliminates circular classification problems and makes each stage independently testable.  
**Consequences:** Cluster assignment must be re-run after any significant entity import. It is not automatic — it is a deliberate pipeline step.  

---

### D-005 — Four-Layer Pipeline Architecture
**Date:** 2026-02-24  
**Status:** Implemented  
**Context:** Question arose about whether to add property X to the harvester allowlist.  
**Decision:** Four distinct layers with a decision framework for each. (1) Harvester: discovery only, narrow allowlist — add property only if it discovers entities no current semantic property would find. (2) Entity Store: full claims, broad. (3) Edge Building: all properties. (4) SFA: reasons over full graph. "If the entity would get in anyway and you just want the edge, that's the Entity Store and Edge Building layer's job."  
**Alternatives considered:** Single broad harvester with post-filtering.  
**Rationale:** Narrow harvester keeps discovery fast and focused. Broad entity store preserves all evidence for SFA reasoning. Separation makes each layer's purpose unambiguous.  
**Consequences:** See `md/Architecture/PIPELINE_LAYERS_AND_PROPERTY_ALLOWLIST.md` for full allowlist and decision framework.  

---

### D-006 — Federation Scoping Sources (Four PIDs)
**Date:** 2026-02-24  
**Status:** Implemented  
**Context:** Scoping advisor needed a definition of what counts as "scoped."  
**Decision:** Four PIDs define federation scoping: P6863 (DPRR), P1584 (Pleiades), P1696 (Trismegistos), P1838 (LGPN). An entity is scoped if it has at least one of these external IDs present in Wikidata.  
**Alternatives considered:** Broader PID set including VIAF, GND, etc.  
**Rationale:** These four cover the domain authorities for persons, places, and inscriptions in the ancient world. Broader PIDs would inflate the scoped count with entities that have library catalog coverage but no ancient world authority confirmation.  
**Consequences:** Wars, battles, and events will always show as unscoped under this definition — they have no applicable authority file. This is expected and acceptable (see D-015). Scoping percentage should be interpreted with this in mind.  

---

### D-007 — No Methods Agent; SFA Constitution Documents Instead
**Date:** 2026-02-24  
**Status:** Decided, not yet executed  
**Context:** Agent bootcamp thread proposed a standalone Methods Agent that would produce a Lens vocabulary for SFAs to query.  
**Decision:** Retire the Methods Agent framing. Each SFA has methodological self-awareness built in as constitution documents. The lens is constitutive of the SFA, not a service it calls. F001–F005 schema nodes are the graph representation of each SFA's methodological stance — not outputs of a Methods Agent.  
**Alternatives considered:** Shared Methods Agent as a service layer.  
**Rationale:** A shared Methods Agent creates an unnecessary dependency and centralizes something that should be distributed. Each SFA's methodological stance is domain-specific; a prosopographer SFA reasons prosopographically by design, not by consulting a service.  
**Consequences:** SFA implementation sprint must include constitution document preparation per SFA. See `docs/SFA_CONSTITUTION_NOTES_2026-02-25.md` for per-SFA document lists. KANBAN task: "SFA Constitution Documents" — parallel background work alongside Project Mercury.  

---

### D-008 — SCA/SFA Division of Labor
**Date:** 2026-02-24  
**Status:** Decided, implementation pending  
**Context:** Confusion about what SCA does vs what SFA does.  
**Decision:** SCA is the empirical foundation layer — grounded harvest evidence, confidence scores, entry doors, pre-computed narrative paths, entity counts. SFA is the interpretive judgment layer — within-facet concept additions, cross-facet relationship proposals, framework overlays. SCA routes and grounds. SFA reasons and interprets. SFA proposals enter the graph as claims: `source: "sfa_inference"`, `confidence: 0.75`, contestable by other SFAs. The loop closes when SFA proposals flow back and SCA re-scores.  
**Alternatives considered:** Single unified agent layer.  
**Rationale:** Separation preserves the distinction between what the data supports (SCA) and what scholarship tells us matters (SFA). SFA claims being contestable by other SFAs models genuine scholarly disagreement.  
**Consequences:** See `docs/SCA_SFA_CONTRACT.md` for the full contract. Neither agent can do the other's job — the loop requires both.  

---

### D-009 — Narrative Path Weighting (Conservative Cap)
**Date:** 2026-02-24  
**Status:** Implemented  
**Context:** Seven curated narrative paths defined in SCA. Question of how heavily to weight path membership in salience scoring.  
**Decision:** +0.05 per path, capped at +0.15. Narrative paths are a tiebreaker and mild boost, not the primary signal.  
**Alternatives considered:** Higher weighting that makes paths dominant.  
**Rationale:** A confirmed, entity-rich node with no curated path should not be buried under a thin node that happens to start a path. Entity count and federation confirmation are the primary signals.  
**Consequences:** Religion is currently absent from the seven paths — the religious-political entanglement (auspices, priesthoods, legitimacy) is a known gap. Flag for when the entity layer behind religious SubjectConcepts is richer. Re-evaluate path weighting calibration after cluster assignment populates real entity counts.  

---

### D-010 — DPRR Import: Three-Pass Strategy
**Date:** 2026-02-25  
**Status:** Complete  
**Context:** DPRR import initially covered Group A persons (Wikidata-aligned) and posts. Two gaps remained: status assertions (1,992 records) and Group C POSITION_HELD (1,442 records for persons without Wikidata QIDs).  
**Decision:** Three separate passes. Pass 1: full import (Group A merge + Group C create + posts + relationships). Pass 2: `--status-assertions` flag, QID match for Group A. Pass 3: `--group-c-posts` flag, dprr_uri match for Group C.  
**Alternatives considered:** Single pass with all data.  
**Rationale:** Separate passes allow incremental verification. Status assertions and Group C posts have different match strategies (QID vs dprr_uri) — cleaner as separate operations.  
**Consequences:** DPRR import is now complete. All 1,992 status assertions imported (1,298 via QID + 694 via dprr_uri). All 1,442 Group C POSITION_HELD records imported. 24 new Office nodes created. Global unscoped dropped from 86.4% to 8.9%.  

---

### D-011 — Legitimate-Unscoped Event Clusters
**Date:** 2026-02-25  
**Status:** Decided  
**Context:** Noise hotspot diagnostic showed Q1764124 (External wars) and Q271108 (Factional politics) at 100% unscoped. All 200+ entities in these clusters had P646, P2671, P244, P268 etc. but none had P6863, P1584, P1696, or P1838.  
**Decision:** These clusters are legitimate-unscoped, not noise. Wars, battles, and events are not covered by the four domain authority files (DPRR = persons, Pleiades = places, Trismegistos/LGPN = persons/inscriptions). Harvester is behaving correctly. No action needed on these clusters.  
**Alternatives considered:** Add event-focused federation source; use temporal qualifiers as scoping signal; use graph proximity as fallback.  
**Rationale:** Not everything needs federation coverage now. The 8.9% unscoped rate contains at least two distinct populations: legitimate-unscoped events (expected) and potential noise (to investigate separately). Conflating them produces a misleading metric.  
**Consequences:** Q1764124 and Q271108 marked as legitimate-unscoped in scoping advisor output. The `noise_hotspot_diagnostic.py` script is the right tool for distinguishing the two populations. Run against other high-unscoped clusters before Project Mercury.  

---

### D-012 — Period Nodes: Option B (temporal_anchor model)
**Date:** 2026-02-25  
**Status:** Implemented  
**Context:** 1,077 Period nodes from PeriodO import covered -1.4M to -2001 BCE (prehistoric range). Year backbone covers -2000 to 2025. No overlap — zero STARTS_IN_YEAR or ENDS_IN_YEAR edges could be created. Roman Republic (509–27 BCE) explicitly filtered out by the end_year < -2000 import filter. Two architectural options: (A) keep as standalone taxonomy with no Year links, (B) delete and use temporal_anchor model.  
**Decision:** Option B. Delete all 1,077 Period nodes. Use temporal_anchor on entities (e.g. Q17167 as ORGANIZATION with dates) and temporal_scope on claims. PeriodO retained as a federation for on-demand temporal definition lookup — not pre-imported.  
**Alternatives considered:** Option A — keep as disconnected taxonomy.  
**Rationale:** The nodes were structurally useless for Chrystallum's domain — no Year links, no connection to the Republican period, no edges to anything that matters. Dead weight. The temporal_anchor model (from `md/Architecture/perplexity-on-periods.md`) is architecturally cleaner — temporal scope belongs on entities and claims, not as a separate node type.  
**Consequences:** 1,077 nodes and ~3,107 edges removed in cleanup (2026-02-25). Q17167 + temporal_anchor covers the Roman Republic temporal range. PeriodO as on-demand lookup is sufficient for any temporal definition queries. See `docs/PERIOD_ENTITY_ARCHITECTURE_CLARIFICATION.md`.  

---

### D-013 — Graph Cleanup Scope (2026-02-25)
**Date:** 2026-02-25  
**Status:** Complete  
**Context:** Node audit identified several categories of staging artifacts, orphaned nodes, and stale pipeline objects in the graph.  
**Decision:** Delete in one script: Period (1,077), GeoCoverageCandidate (357), PeriodCandidate (1,077), PlaceTypeTokenMap (212), FacetedEntity (360). Total: 3,083 nodes, ~8,934 edges.  
**Alternatives considered:** Incremental deletion over multiple sessions.  
**Rationale:** All five categories were either confirmed staging artifacts (PeriodCandidate, GeoCoverageCandidate, PlaceTypeTokenMap), confirmed orphaned (FacetedEntity), or superseded by architecture decision (Period — see D-012). Single script with dry-run verification is safer than incremental deletion.  
**Consequences:** Graph baseline post-cleanup: 60,925 nodes, 49,152 edges. No unintended deletions confirmed. Entity, SubjectConcept, Facet, Federation, Office node counts all unchanged. Script at `scripts/neo4j/self_describing_subgraph_cleanup.py`.  

---

### D-014 — FederationRegistry: SYS_ Label Migration
**Date:** 2026-02-25  
**Status:** Decided, not yet executed  
**Context:** 13 Federation nodes in graph reflect pre-DPRR list — BabelNet, WorldCat, MARC present; DPRR, Trismegistos, LGPN missing. Self-describing subgraph design requires a proper FederationRegistry branch.  
**Decision:** Clear all existing Federation and FederationRoot nodes. Replace with 13 SYS_FederationSource nodes under a SYS_FederationRegistry root, wired to the Chrystallum system root. Label migration: `Federation` → `SYS_FederationSource`. All system nodes carry `{system: true}` property and `SYS_` prefix.  
**Alternatives considered:** Add new nodes alongside old ones.  
**Rationale:** The old list is wrong, not just incomplete. Clean replacement avoids hybrid state where some Federation nodes are old-format and some are new.  
**Consequences:** Any scripts querying `Federation` nodes directly must be updated to query `SYS_FederationSource`. Dev must grep for this dependency before executing. Spec at `docs/FEDERATION_REGISTRY_REBUILD_SPEC.md`. Estimated 30–45 minutes dev time.  

---

### D-015 — Self-Describing Subgraph: Same Neo4j Instance
**Date:** 2026-02-25  
**Status:** Decided, build not started  
**Context:** Design question of whether system metadata (schema, federations, bibliography, process state) should live in the same Neo4j instance as domain data or separately.  
**Decision:** Same instance. Label hygiene prevents contamination: all system nodes use `SYS_` prefix and `{system: true}` property. Domain queries exclude system nodes via `WHERE n.system IS NULL`. System queries are explicit via label.  
**Alternatives considered:** Separate Neo4j instance; separate database within same instance.  
**Rationale:** SFAs query the graph directly — a separate instance adds a network hop and an authentication context. Same instance with label discipline is simpler and sufficient.  
**Consequences:** Four-branch structure: `HAS_SCHEMA` → SchemaRegistry, `HAS_FEDERATION` → FederationRegistry, `HAS_BIBLIOGRAPHY` → BibliographyRegistry, `HAS_PROCESS` → ProcessRegistry. Build priority: FederationRegistry first (most immediate pipeline utility), SchemaRegistry second, Bibliography and Process after. See `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN.md`.  

---

### D-016 — AI_CONTEXT.md Deprecated
**Date:** 2026-02-25  
**Status:** Decided  
**Context:** AI_CONTEXT.md was a catch-all for session handoff — mixing decisions, QA results, pipeline notes, and process guidance. Became unwieldy and was partially lost when the main chat session crashed. Not a reliable persistence mechanism.  
**Decision:** Deprecate AI_CONTEXT.md. Redistribute live content to: DECISIONS.md (why), KANBAN.md (what), `docs/architecture/` (how), START_HERE.txt (orientation). Move AI_CONTEXT.md to Archive/ after redistribution is confirmed complete.  
**Alternatives considered:** Restructure AI_CONTEXT.md rather than deprecate.  
**Rationale:** A single file trying to serve multiple purposes serves none of them well. Separation by concern is more maintainable and more scannable for a new agent entering a session.  
**Consequences:** START_HERE.txt must be updated to point to DECISIONS.md, KANBAN.md, and the consolidated architecture doc instead of AI_CONTEXT.md. Any agent that starts a session by reading AI_CONTEXT.md will find it in Archive/ with a note pointing to the replacement files.  

---

### D-017 — Folder Organization: Root Discipline
**Date:** 2026-02-25  
**Status:** Decided, not yet executed  
**Context:** Root directory contains ~150 files — scripts, docs, analysis files, and config mixed with no structure. Makes orientation difficult for new agents and developers.  
**Decision:** Five files only at root: KANBAN.md, REQUIREMENTS.md, DECISIONS.md, README.md, START_HERE.txt (plus .env/config.py). Everything else has a home: active docs → `docs/` with subdirectories (architecture/, federations/, agents/, sessions/), scripts stay in `scripts/`, root-level Python scripts → `scripts/legacy/`, inactive markdown → `Archive/`.  
**Alternatives considered:** Incremental cleanup over time.  
**Rationale:** Clean root = fast orientation. Five files is scannable. Everything else is findable via folder structure.  
**Consequences:** Dev must grep active scripts for hardcoded relative paths before moving root-level Python files. Moving `scripts/` contents is safe (already in a folder). AGENT_REFERENCE_FILE_PATHS.md must be updated after any moves. Pending dev availability.  

---

### D-018 — OCD 1949: Role and Epistemic Stance
**Date:** 2026-02-24  
**Status:** Decided, extraction not started  
**Context:** Oxford Classical Dictionary 1949 edition is public domain on Archive.org. Question of how to integrate it.  
**Decision:** Four roles: (1) Reference source for SFA grounding — OCD entry changes confidence posture ("Wikidata asserts X, OCD 1949 asserts Y"). (2) Taxonomy enrichment — entry structure encodes scholarly consensus for SubjectConcept candidates. (3) Cross-reference graph — every (q.v.) is a directed edge, scholar-curated salience signal. (4) Browser extension anchor — authority chain for the extension use case. Epistemic stance: OCD 1949 is one lens, not privileged over domain authorities (DPRR, Pleiades, Trismegistos, LGPN) or later scholarship. Metadata: `authority_scope`, `superseded_by: Q69525831`, `date_limitations: "pre-1950"`.  
**Alternatives considered:** Use OCD 4th edition online (P9106) instead of 1949.  
**Rationale:** 1949 is public domain — full text extractable. P9106 (4th edition) is the Wikidata property but maps to the online edition, not the text we have. Use P9106 to confirm OCD coverage, match to 1949 headword by label normalization.  
**Consequences:** Three open actions: download full text from Archive.org, run P9106 SPARQL query, run P1343/Q430486 query. Extraction pipeline drafted in `docs/OCD_INTEGRATION_NOTES_2026-02-25.md`. Taxonomy gaps identified: legal concepts (provocatio, lex, imperium), religious institutions (flamines, Vestals), material culture (toga praetexta, fasces).  

---

### D-019 — Syme Index: Facts Extraction vs Text Reproduction
**Date:** 2026-02-24  
**Status:** Decided, extraction not started  
**Context:** Syme, Roman Revolution (1939) — index pages 535–568 (34 pages). Prose text in copyright (UK, life+70, until 2059).  
**Decision:** Extract index only, not prose. Index extraction = facts extraction (names, consular dates, page refs, short relationship phrases) — different copyright character than text reproduction. Document this distinction explicitly on the bibliography node.  
**Alternatives considered:** Wait for public domain; use summary only.  
**Rationale:** The index is the high-value component anyway. Disambiguation format (Nomen Cognomen, Praenomen, cos. YEAR B.C.) maps directly to DPRR PostAssertion format. Sub-entries are pre-parsed relationship candidates. Salience signal: entry density = Syme's editorial judgment about who matters.  
**Consequences:** Photography session needed (flat pages, even lighting, batches of 4–6). Upload here for JSON extraction. See `docs/SFA_CONSTITUTION_NOTES_2026-02-25.md` for full photography protocol and output format.  

---

### D-020 — Decision Log Replaces AI_CONTEXT for Why-Decisions
**Date:** 2026-02-25  
**Status:** Implemented (this file)  
**Context:** Main chat session crashed mid-session on 2026-02-25, requiring reconstruction from transcript. Significant time lost re-establishing context. AI_CONTEXT.md was not capturing decision rationale reliably.  
**Decision:** Chronological append-only DECISIONS.md at root. Topical index at top updated at milestones. Five fields per entry: Context, Decision, Alternatives considered, Rationale, Consequences. Both architect (Claude) and dev append. Neither edits past entries.  
**Alternatives considered:** Topical-only organization; embedding decisions in KANBAN.  
**Rationale:** Chronological append requires no filing judgment — reduces friction to zero. Topical index at top provides lookup without restructuring. Separation from KANBAN keeps each file focused: KANBAN = work state, DECISIONS = reasoning.  
**Consequences:** AI_CONTEXT.md deprecated (see D-016). START_HERE.txt updated to point here. New agents entering a session should read: START_HERE.txt → KANBAN.md → DECISIONS.md (recent entries) → relevant architecture doc.

---

### D-021 — Mercury Deprioritized; Foundation Federations First
**Date:** 2026-02-25  
**Status:** Decided  
**Context:** Mercury (CHRR + CRRO) was next on the pipeline. Architect reassessed: Mercury delivers person → office → coin → findspot evidence chain, but findspot data needs to link to Pleiades Place nodes. Pleiades Phase 2 has not run — 41,884 Place nodes have 0 edges, no coordinates, no LOCATED_IN. Running Mercury before Pleiades Phase 2 creates material evidence nodes that cannot complete their geographic chain.  
**Decision:** Deprioritize Mercury to Phase D. Revised sequence: Phase A (Trismegistos crosswalk, VIAF, noise audit) → Phase B (Pleiades Phase 2, LGPN forward, Getty AAT) → Phase C (Trismegistos Phase 2, EDH, OCD) → Phase D (Mercury, Syme index, epigraphic sources).  
**Alternatives considered:** Run Mercury now; add Pleiades Phase 2 in parallel.  
**Rationale:** Each phase makes the next more valuable. Pleiades Phase 2 activates 41,884 Place nodes — the biggest single activation in the graph. Mercury's evidence chain only closes when findspots link to places with coordinates. Coins are important for numismatic/economic SFAs later but are not foundational infrastructure. Building Mercury before the geographic and prosopographic layers are solid optimizes for a specific SFA before the general foundation is ready.  
**Consequences:** KANBAN updated with phased operational sequence. Mercury moves to Phase D. Trismegistos crosswalk, VIAF, Pleiades Phase 2, LGPN, Getty AAT prioritized before Mercury.  
