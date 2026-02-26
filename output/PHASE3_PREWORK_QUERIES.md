# Phase 3 Pre-Work — Live Graph Findings

**Date:** 2026-02-26  
**Source:** Architect via Chrystallum MCP (run_cypher_readonly)  
**Status:** Complete — ready for dev cleanup + Phase 3 Task A1/A2

---

## D-033 Verification — Live Graph State

### Graph Health — PASS

**Node inventory:**
| Label | Count |
|-------|-------|
| Place | 41,884 |
| Entity | 13,980 (12,064 with qid, 1,916 without) |
| Year | 4,025 |
| SYS_PropertyMapping | 706 |
| Office | 171 |
| SubjectConcept | 61 |
| Facet | 36 |
| SYS_FederationSource | 26 (13 unique — **duplicates**) |
| SYS_Threshold | 24 |
| SYS_Policy | 12 |
| BibliographySource | 3 |
| Agent | 3 |
| Unlabelled (ghost) | 10 |

**Relationship inventory (top):** MEMBER_OF 10,434 | POSITION_HELD 7,342 | FOLLOWED_BY 4,042 | P1343 3,630 | SIBLING_OF 2,144 | FATHER_OF 2,109 | P31 2,036 | HAS_STATUS 1,919 | BROADER_THAN 120 | DOMAIN_OF 61

### SYS_ Governance Layer — PASS with gaps

- **Thresholds (24):** All present, linked to DMN tables.
- **Policies (12):** All active. NoTemporalFacet, NoGenealogicalFacet, NoPatronageFacet, NoClassificationFacet, SFAProposalAsClaim, ApprovalRequired confirmed.
- **FederationSources:** 13 unique, **each duplicated** (26 nodes). All have pid=null, scoping_weight=null, property_name=null.

---

## Phase 3 Pre-Work Findings

### Finding 1 — VIAF: 508 entities, quality mixed

- **35** DPRR persons — clean short numeric IDs (Pompeius, Cicero, Antonius, etc.)
- **~50** Roman geographic entities
- **~423** out-of-domain (Crystal Palace, Willis Tower, Van Gogh Museum, etc.) — **noise**

### Finding 2 — LCNAF: 0 entities

Expected. Phase 3 Step 1 extracts LCNAF from VIAF clusters.

### Finding 3 — SubjectConcept: 61 nodes, 0 FAST IDs, 0 LCSH IDs

All 61 have qid and label. None have fast_id or lcsh_id. **Primary Phase 3 target.**  
16 SubjectConcepts have zero members. Families/Gentes dominates: 5,363 members (51%).

### Finding 4 — Entity quality split

- **12,064** with qid (86%) — Wikidata-sourced
- **1,916** without qid (14%) — DPRR-only persons, entity_id pattern person_dprr_NNNN

### Finding 5 — BibliographySource: 3 nodes, 2 stubs

- DPRR: clean
- Broughton_MRR, Zmeskal_Adfinitas: id only, no label, no uri — stubs

### Finding 6 — 10 unlabelled ghost nodes

Safe to delete.

---

## Phase 3 Spec — Refined

### Problem A — FAST IDs on SubjectConcepts (highest priority)

61 SubjectConcepts, no FAST IDs. Routing backbone gap.  
**Target:** Resolve FAST IDs via LC SRU or FAST API.  
**Complexity:** LOW. **Blocking:** nothing.

### Problem B — LCNAF on 35 DPRR persons with VIAF (medium priority)

**Target:** Extract LCNAF from VIAF clusters for 35 persons.  
**Complexity:** LOW. **Blocking:** nothing.

### Problem C — VIAF hygiene (lower priority, defer)

Remove 423 out-of-domain VIAF IDs. Defer until after A and B.

---

## Dev Cleanup Tasks (Before Phase 3)

### CLEANUP 1: SYS_FederationSource duplicates

13 sources each duplicated. Delete higher-ID duplicate per source.

### CLEANUP 2: 10 unlabelled ghost nodes

Single Cypher DELETE.

### CLEANUP 3: 423 out-of-domain VIAF IDs

Needs domain-relevant allowlist — architect review before running.

---

## Recommended Action Sequence

**IMMEDIATE:**
- Task A1: FAST ID resolution for 61 SubjectConcepts (1–2 sessions)
- Task A2: LCNAF extraction for 35 DPRR persons (1 session)
- Task A3: Clean ghost nodes (5 min)

**D-035 (parallel):** D12/D13 wire read paths, entity_count cleanup

**POST-PROTOTYPE:** Problem C, BibliographySource stubs, FederationSource stubs, LGPN for 1,916 DPRR-only
