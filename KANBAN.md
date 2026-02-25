# Chrystallum Project Kanban Board

**Last Updated:** 2026-02-25  
**PM:** AI PM Agent  
**Current Focus:** Phase A — Close current gaps before foundation federations

**Discipline:** Update KANBAN.md + REQUIREMENTS.md in same commit

---

## Operational Sequence (Revised 2026-02-25)

**Principle:** Each phase makes the next more valuable. Build foundation before specialized evidence.

### Phase A — Close current gaps (no new federations)
1. Trismegistos crosswalk — run existing script, close enrichment gap
2. VIAF — name authority on DPRR persons via P214
3. Noise audit — remaining unscoped clusters beyond Q1764124/Q271108

### Phase B — Foundation federations (activate what's dormant)
4. Pleiades Phase 2 — coordinates, period names, LOCATED_IN on 41,884 Place nodes
5. LGPN forward SPARQL — prosopographic coverage for non-Roman persons
6. Getty AAT — SubjectConcept taxonomy enrichment, prerequisite for SFA quality

### Phase C — Enrichment federations (deepen what's connected)
7. Trismegistos Phase 2 — attestations, primary source claims, non-elite persons
8. EDH — Latin inscriptions as primary source evidence
9. OCD — taxonomy enrichment, SFA grounding corpus

### Phase D — Specialized evidence (SFA-specific)
10. Mercury (CHRR + CRRO) — numismatic evidence chain (geographic foundation exists)
11. Syme index extraction — prosopographic salience weights
12. Further epigraphic sources as needed

**Parallel track (no graph touches):** File restructure + DEV_GUIDE.md, SFA constitution documents, SysML model

---

## In Progress

- [x] **D-031 MCP server v1** ✅ (2026-02-25)
  - scripts/mcp/chrystallum_mcp_server.py, .cursor/mcp.json
  - FORBIDDEN_FACETS refactor: sca_agent, subject_concept_facet_agents read from SYS_Policy
  - Acceptance: MCP get_policy works; no hardcoded FORBIDDEN_FACETS in agents

- [x] **P1696 count check** ✅ (2026-02-25)
  - SPARQL: 0 of 6,989 entity QIDs have P1696 in Wikidata
  - Script: scripts/analysis/count_p1696_overlap.py
  - Crosswalk deferred — no overlap in current entity set

- [ ] **Node label audit** #medium @dev
  - Run scripts/analysis/audit_node_labels.cypher in Neo4j
  - Document findings; identify redundant/questionable labels

---

## Ready (Phase A)

- [ ] **Trismegistos crosswalk** #low @dev (deferred)
  - 0 overlap in current 6,989 entities — run when entities with P1696 enter graph
  - Script: scripts/integration/prosopographic_crosswalk.py

- [ ] **Library Authority Integration** #high @dev (5-step workstream, replaces standalone VIAF task)
  - **Step 1:** Full FAST import — FASTTopical_parsed.csv (325MB), pipeline exists, run at full scale
  - **Step 2:** LCSH→FAST wiring — SKOS crosswalks, extract_lcsh_relationships.py, builds BROADER_THAN hierarchy
  - **Step 3:** VIAF→LC SRU — 947 entities with P214, free MARC authority records, no API key
  - **Step 4:** subjectOf bibliography — VIAF subjectOf → MARC bibliographic records → BibliographySource nodes auto-constructed
  - **Step 5:** FAST headings on bibliography nodes → facet routing for SFA constitution discovery
  - WorldCat: backlogged, no OCLC procurement
  - See DECISIONS.md D-025
  - **Pre-work:** Dev to confirm current Subject node count in Neo4j and LCSH parse state before Step 1

- [ ] **Noise audit** #medium @dev
  - Beyond Q1764124, Q271108 (confirmed legitimate-unscoped)
  - Script: scripts/analysis/noise_hotspot_diagnostic.py
  - Assess remaining high-unscoped clusters

---


## Ready (Phase B+)

- [ ] **Pleiades Phase 2** #high @dev
  - Coordinates, period names, LOCATED_IN on 41,884 Place nodes
  - Prerequisite for Mercury geographic chain
  - **Pre-Phase B check:** Confirm Pleiades Phase 2 import writes `pleiades_id` onto Place nodes. Place nodes are primary Pleiades entities; same persistence requirement as Entity.external_ids (D-022). `import_pleiades_to_neo4j.py` uses pleiades_id as MERGE key — verify any Phase 2 enrichment script also sets it.

- [ ] **LGPN forward SPARQL** #medium @dev
  - Greek personal names; fills gap DPRR leaves for non-Roman persons
  - LGPN = P1047 (D-023); P1838 = PSS-archi

- [ ] **Getty AAT** #medium @dev
  - SubjectConcept taxonomy enrichment before SFA build

---

## On Hold

- [ ] **Mercury (CHRR + CRRO)** — Deprioritized per D-021
  - Numismatic evidence chain requires Pleiades Phase 2 for geographic closure
  - Moved to Phase D; runs after foundation federations

- [ ] **Entity Scaling Phase 2** (Paused)
  - Quality over quantity; resume after foundation federations

---

## Done

- [x] **external_ids persistence fix (D-022)** ✅ (2026-02-25)
  - Option B: separate properties per federation PID on Entity nodes
  - Backfill: 164 pleiades_id; lgpn_id was PSS-archi (D-023), now 0
  - Sample: scripts/analysis/sample_federation_ids.py

- [x] **lgpn_id mapping fix (D-023)** ✅ (2026-02-25)
  - LGPN = P1047; P1838 = PSS-archi (buildings)
  - All references updated; P1047 overlap: 1 of 6,989 entities

- [x] **FederationRegistry Rebuild** ✅ (2026-02-25)
- [x] **DPRR Complete** ✅ (2026-02-25) — Group A, status, Group C posts
- [x] **Cluster assignment + baseline** ✅ (2026-02-25) — 9,144 MEMBER_OF, 91.2% scoped
- [x] **Self-describing subgraph cleanup** ✅ (2026-02-25) — 3,083 nodes removed
- [x] **Legitimate-unscoped event clusters** ✅ (2026-02-25) — Q1764124, Q271108
- [x] **Period/PeriodO Option B** ✅ (2026-02-25)
- [x] **DPRR Federation** ✅ (2026-02-25) — 86.4% → 8.9% unscoped

- [x] **Federation Phase 1** ✅ | **Property→Facet Mapping** ✅ | **Graph Connectivity** ✅
- [x] **Category cleanup** ✅ | **WIKIDATA_ prefix** ✅ | **Entity type casing** ✅
- [x] **Production scoped re-harvest** ✅ | **category_to_property_allowlist** ✅
- [x] **Relationship Canonicalization** ✅ | **Backlink Extraction** ✅

---

## Metrics

**Post-DPRR Baseline (2026-02-25):**
- **MEMBER_OF:** 9,144 edges | **Unique entities:** 6,990
- **Scoped:** 91.2% | **Unscoped:** 8.8%
- **Q899409:** 5,363 entities, 0.0% unscoped
- **DPRR:** 2,960 Group A | 1,916 Group C | 9,807 posts | 1,992 status

---

## Notes

**Mercury deprioritization:** See DECISIONS.md D-021. Mercury's evidence chain (person → coin → findspot → place) requires Pleiades Phase 2. Running Mercury before Pleiades Phase 2 builds the middle of a bridge. Coins are important for numismatic/economic SFAs later — not foundational infrastructure.

**Update Discipline:** KANBAN.md + REQUIREMENTS.md in same commit ✅
