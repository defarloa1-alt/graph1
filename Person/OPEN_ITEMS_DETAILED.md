# Chrystallum Person Schema — Open Items (Detailed)

**Last updated:** 2026-03-03  
**GEDCOM and OCD moved to backlog.**

---

## Immediate — Before Harvest Agent Runs

**Status: DONE (2026-03-03)**

### OPS-001: SYS_FederationSource DPRR status update ✓
**What it does:** The DPRR federation source node currently shows `status = "operational"`. The DPRR SPARQL endpoint is blocked by Anubis bot protection. If the harvest agent queries it, it will receive an Anubis challenge page instead of data.  
**Action:** Run `scripts/neo4j/ops001_dprr_snapshot_actions.cypher` to set `status = "blocked"`, `block_reason`, `block_type`, `blocked_since`, `last_successful_access`, `snapshot_date`, `snapshot_complete`, and snapshot counts. This routes the agent to graph-local `dprr_raw` instead of network calls.  
**Owner:** Write agent

### OPS-001: StatusType relabelling ✓
**What it does:** DPRR Status authority list uses numeric labels "1" and "2" in the graph. The ontology documents these as "eques" and "senator". HAS_STATUS edges point to StatusType nodes with label "1" (395 uses) or "2" (1,524 uses).  
**Action:** Apply Cypher from `Person/ops001_extracted.txt` to SET `label = "eques"` for "1" and `label = "senator"` for "2". Adds `label_latin`, `dprr_status_id`, `description`.  
**Owner:** Write agent

### wd_backlink_capture.py bucket taxonomy update ✓
**What it does:** The Wikidata backlink capture script classifies items that link *to* a person (e.g. coins, humans, films) into buckets. Initial classifier had six generic buckets; Pompey's real P31 data showed numismatic (coins, coin types) was dominant and missing.  
**Action:** Update `_classify_type()` with the revised 10-bucket taxonomy: numismatic, persons, events, political_acts, military_units, physical_legacy, scholarly_reception, modern_reception, visual_arts, fictional_representations, other. Add SPARQL filter to exclude Wikimedia category/property noise.  
**Owner:** Dev

### OI-007-09: CITIZEN_OF backfill ✓
**What it does:** Connect DPRR persons to Roman Republic (Q17167). All DPRR persons are Roman Republican citizens by definition.  
**Action:** Run `scripts/maintenance/backfill_citizen_of_roman_republic.py --execute`. Completed 2026-03-03: 4,862 CITIZEN_OF edges created.

### Polity amendment migration (Steps 1-5) ✓
**What it does:** Apply :Polity/:HistoricalPolity to historical nodes; re-target CITIZEN_OF from Q1747689 to Q17167; remove :Polity from contemporary states.  
**Action:** Run `scripts/maintenance/apply_polity_amendment_migration.py --execute`. Completed 2026-03-03: 9 nodes, 18 CITIZEN_OF re-targeted, 11 contemporary states reclassified.

### OI-007-10: HistoricalPolity inception/dissolution ✓
**What it does:** Populate inception_year and dissolution_year from Wikidata P571/P576 on :HistoricalPolity nodes.  
**Action:** Run `scripts/maintenance/enrich_historical_polity_temporal.py --execute`. Script created; run periodically to fill gaps from Wikidata.

---

## Phase 4 — P-code Promotion (remaining)

### P102 / P463 → MEMBER_OF_FACTION
**What it does:** Wikidata P102 (member of political party) and P463 (member of) point to political factions (e.g. optimates, populares, First Triumvirate). Promote these to canonical `MEMBER_OF_FACTION` edges. Targets become `:PoliticalFaction` nodes. Same pattern as P27→CITIZEN_OF, P140→HAS_RELIGION.  
**Deliverable:** `promote_p102_p463_to_member_of_faction.py`

### P3716 → IN_SOCIAL_ORDER
**What it does:** Wikidata P3716 (social status) points to entities like "nobilis", "eques", "plebeian". Promote to canonical `IN_SOCIAL_ORDER` edges. Targets become `:SocialOrder` nodes.  
**Deliverable:** `promote_p3716_to_in_social_order.py`

### P5025 → MEMBER_OF_GENS (cross-check)
**What it does:** Wikidata P5025 (member of gens) points to gens entities. DPRR already wires Person→Gens via `MEMBER_OF_GENS` from label parse. This item is cross-validation: compare Wikidata P5025 targets against DPRR gens_prefix. Log Type 1 (precision gap) or Type 4 (hard conflict) discrepancies.  
**Note:** Onomastic `MEMBER_OF_GENS` already wired from DPRR. P5025 promotion would add Wikidata-sourced gens links where DPRR lacks tribe/gens.

### P11491 → MEMBER_OF_TRIBE (cross-check)
**What it does:** Wikidata P11491 (member of tribe) points to Roman voting tribes. DPRR already wires Person→Tribe via `MEMBER_OF_TRIBE` from label parse. Cross-validate P11491 targets against DPRR tribe_abbrev. Log discrepancies.  
**Note:** Onomastic `MEMBER_OF_TRIBE` already wired from DPRR.

---

## Phase 4.3 — Family & Office Enrichment

### CHILD_OF materialisation
**What it does:** FATHER_OF and MOTHER_OF exist (person→parent). CHILD_OF is the inverse (parent→child). Many genealogy tools and GEDCOM expect bidirectional parent–child links. Materialising CHILD_OF from existing FATHER_OF/MOTHER_OF creates ~2,582 new edges so that (parent)-[:CHILD_OF]->(child) exists wherever (child)-[:FATHER_OF|MOTHER_OF]->(parent) exists.  
**Deliverable:** Script to MERGE (p)-[:CHILD_OF]->(c) for each (c)-[:FATHER_OF|MOTHER_OF]->(p).

### SPOUSE_OF enrichment
**What it does:** SPOUSE_OF edges exist but lack temporal and structural metadata. Enrich with: `start_year`, `end_year` (when marriage began/ended), `end_reason` (death, divorce, unknown), `series_ordinal` (for multiple marriages). Source: Wikidata qualifiers on P26 (spouse) or DPRR relationship assertions if available.  
**Deliverable:** Enrichment script or harvest executor step.

---

## Phase 5 — Context Packet & Agent Infrastructure

### VIAF, Nomisma, Trismegistos, LGPN in context packet
**What it does:** The context packet currently has `person_stub`, `dprr_raw`, `wikidata_raw`. The agent needs raw data from VIAF (authority records), Nomisma (numismatic), Trismegistos (papyri/epigraphy), LGPN (Greek personal names) to reconcile identity and attribute claims across all seven federation sources. Each source has its own API/SPARQL; add federation query runners that fetch and normalise into the packet.  
**Deliverable:** Query runners in `context_packet.py`; size caps per OI-008-02.

### Full 13-step execution sequence
**What it does:** The executor currently does Entity create/update + FATHER_OF/MOTHER_OF. ADR-008 §5.2 defines a 13-step dependency-ordered sequence (e.g. create Person → merge onomastic → write literals → write relationships → CHALLENGES_CLAIM → ConflictNote → D10 evaluation). Each step is idempotent and resumable. `execution_status` and `resume_from_step` support interrupted harvests.  
**Deliverable:** Execution engine with step runner; Cypher templates per operation type.

### SYS_HarvestPlan node writer
**What it does:** The agent produces a PersonHarvestPlan (JSON-serialisable). Store it as a graph node `(:SYS_HarvestPlan)` linked to the target Person. Enables audit trail, re-reasoning with a different model, and resumability. Idempotent: skip if `plan_id` already exists.  
**Deliverable:** Cypher template to MERGE SYS_HarvestPlan; register as system node type (OI-008-01).

### Person Harvest Gradio UI (pinned)
**What it does:** When person extract is ready, launch in Gradio with verbose streaming for every step. Each step (discovery, context packet, agent, executor) can take time; UI streams progress so user sees what is happening.  
**Plan:** `Person/PERSON_HARVEST_GRADIO_PLAN.md` — New tab, streaming output, step-by-step verbose.  
**Deliverable:** Person Harvest tab in `agent_gradio_app.py`; orchestrator yields progress for Gradio streaming.

---

## Phase 7 — Conflict Resolution

### CHALLENGES_CLAIM edge type
**What it does:** When two sources disagree on an attribute (e.g. birth year), one claim can challenge another. `CHALLENGES_CLAIM` links (challenger_claim)-[:CHALLENGES_CLAIM]->(challenged_claim) with properties: `challenger_source`, `challenge_type`, `created_at`. Supports the conflict resolution ladder.  
**Deliverable:** Schema definition; Cypher templates for writing challenges.

### ConflictNote node type
**What it does:** For Type 4 (hard irreconcilable) conflicts, the agent drafts a ConflictNote. Node properties: `conflict_type`, `attributes_in_dispute[]`, `sources_involved[]`, `tiebreaker_needed`, `resolution_status`, `ocd_applicable`. Human reviewers use these to resolve.  
**Deliverable:** Schema definition; agent prompt for ConflictNote drafting; Cypher template.

### Type 4 resolution ladder
**What it does:** When sources irreconcilably disagree (Type 4), apply: (1) authority tier weighting (primary > secondary_academic > secondary_populist > tertiary); (2) if tie, apply tiebreaker rule; (3) if still tie, write both as Proposed for human review. Also: `source_authority_tier` property on all claims.  
**Deliverable:** Resolution module; conflict classification (Type 1–4) logic.

---

## Phase 8 — Pompey PoC

### Pompey (POMP1976) end-to-end harvest
**What it does:** Full pipeline validation using Pompey as the worked example. Layer 1: parse DPRR label, normalise dates, map P-codes. Layer 2: agent reasons over DPRR + Wikidata + VIAF + LC + Nomisma + Trismegistos + LGPN. Layer 3: execute full 13-step sequence. Validates that the entire architecture works on a single high-profile person.  
**Blocked by:** Phase 5 (context packet), Phase 6 (full executor), Phase 7 (conflict structures if conflicts arise).

---

## ADR Open Items (OI-*)

### OI-007-02: OfficeHolding event node migration
**What it does:** POSITION_HELD edges currently store office-holding as (Person)-[:POSITION_HELD]->(Position). Full CIDOC-CRM compliance requires OfficeHolding as a first-class event node (E7_Activity). POSITION_HELD has been pre-populated with `start_year`, `end_year`. This item is the migration: create OfficeHolding event nodes, link Person and Position to them, move temporal data to the event. Deferred per OI-02.  
**ADR:** ADR-007

### OI-007-03: MythologicalPerson schema
**What it does:** Romulus, Remus, Europa are mythological. They carry `MythologicalPerson` and should have `mythological=true`, `DQ_UNRESOLVED_PERSONHOOD` flag. Ensure schema and remediation scripts handle these consistently (no false :Person label, no harvest expansion).  
**ADR:** ADR-007

### OI-007-05: EDH epigraphic enrichment
**What it does:** Epigraphic Database Heidelberg (EDH) holds Roman inscriptions. Harvest planning: define how EDH data would feed into Person profiles (e.g. office attestations, provenance). Requires EDH API/access design.  
**ADR:** ADR-007

### OI-007-07: LGPN integration
**What it does:** Lexicon of Greek Personal Names (LGPN) provides Greek name forms. Property `lgpn_id` is reserved on Person. Integration: fetch LGPN data for persons with Greek names, add to context packet, agent reconciles LGPN form with DPRR/Wikidata.  
**ADR:** ADR-007

### OI-007-08: Filiation as first-class relationship
**What it does:** Filiation (Cn. f. Sex. n. = son of Gnaeus, grandson of Sextus) is currently parsed into `filiation_chain[]` in the DPRR parse. This item considers whether filiation should be first-class edges (e.g. SON_OF, GRANDSON_OF) or remain as structured parse output. Post first-pass harvest review.  
**ADR:** ADR-007

### OI-008-01: SYS_HarvestPlan node definition
**What it does:** Register SYS_HarvestPlan as a system node type in the self-describing subgraph. Enables discovery, validation, and tooling to recognise harvest plans.  
**ADR:** ADR-008

### OI-008-03: Agent model selection and versioning policy
**What it does:** Define which LLM model(s) the harvest agent uses, how to version (e.g. gpt-4o-mini vs gpt-4o), and policy for re-reasoning existing plans with a newer model.  
**ADR:** ADR-008

### OI-008-04: Parallel harvest across gens subgraphs
**What it does:** Harvest can be parallelised by running independent gens (e.g. Cornelia, Pompeia) in parallel since they don't share nodes. Design: partition queue by gens, run workers, merge results.  
**ADR:** ADR-008

---

## Backlink Capture (post-integration)

### Integrate wd_backlink_capture into harvest script
**What it does:** Call backlink capture in Layer 1, per-person loop, after DPRR parse and before LLM context assembly. Rate limit ~3 req/s. Write `wd_bl_*` properties to Person node. Optionally pass `backlink_profile` into context packet so agent can prioritise Nomisma when `wd_bl_numismatic > 0`.  
**Deliverable:** Integration in `orchestrator.py`; `wd_backlink_capture.py` with updated taxonomy.

### Post-harvest: resolve wd_bl_candidate_persons
**What it does:** `wd_bl_candidate_persons` is a JSON list of {qid, label, property_id} for person→person backlinks not yet in graph. A dedicated pass: deserialise, resolve each QID against graph, agent classifies P-codes → candidate relationship types. High-confidence → claim edges. Low-confidence → WD_BacklinkCandidate ScaffoldNodes for human review.  
**Deliverable:** Enrichment script; agent classification prompt.

---

## BACKLOG

### OI-007-04: OCD federation integration
**What it does:** Oxford Classical Dictionary (OCD) is a scholarly reference. Integration would add OCD entries as a federation source for person profiles. Requires data access agreement with Oxford.  
**ADR:** ADR-007  
**Status:** Backlog

### OI-008-05: GEDCOM export agent
**What it does:** Export the Person/family subgraph to GEDCOM 7.0 format. Mapping defined in ADR-007 Appendix A: FAM derived from shared FATHER_OF/MOTHER_OF; tria nomina → NAME subtags; BCE offset applied at export. Post first-pass harvest.  
**ADR:** ADR-008  
**Status:** Backlog

---

## Summary

| Category | Count |
|----------|-------|
| Immediate | 3 |
| Phase 4 P-code | 4 |
| Phase 4.3 | 2 |
| Phase 5/6 | 3 |
| Phase 7 | 3 |
| Phase 8 | 1 |
| ADR OI-* (active) | 8 |
| Backlink | 2 |
| **Backlog** | **2** (GEDCOM, OCD) |
