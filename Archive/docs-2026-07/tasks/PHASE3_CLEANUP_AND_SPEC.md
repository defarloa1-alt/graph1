# Phase 3 — Cleanup + Spec (Post Pre-Work)

**Date:** 2026-02-26  
**Source:** Architect verification via MCP  
**Status:** Ready for dev

---

## Dev Cleanup Tasks (Run Before Phase 3 A1/A2)

### CLEANUP 1: SYS_FederationSource duplicates

**Script:** `scripts/neo4j/cleanup_federation_duplicates.cypher`

- 13 sources each duplicated (26 nodes total)
- Keeps lowest-id node per source, deletes higher-id duplicates
- **Dry run first:** Comment out FOREACH, use RETURN to preview

### CLEANUP 2: Ghost nodes

**Script:** `scripts/neo4j/cleanup_ghost_nodes.cypher`

- 10 unlabelled nodes with no properties
- **Dry run first:** `MATCH (n) WHERE size(labels(n)) = 0 RETURN count(n), collect(id(n))`

### CLEANUP 3: Out-of-domain VIAF IDs (DEFER)

- 423 entities with viaf_id that are noise (Crystal Palace, Willis Tower, etc.)
- Needs domain-relevant allowlist — architect to produce before running
- **Do not run yet**

---

## Phase 3 Task A1 — FAST IDs for 61 SubjectConcepts

**Priority:** Highest. Routing backbone for SCA.

**Target:** All 61 have label and qid. Zero have fast_id. Resolve via LC SRU or FAST API.

**Method:** Label-based FAST heading search → candidate review → write fast_id.

**Estimated:** 1–2 sessions.

---

## Phase 3 Task A2 — LCNAF for 35 DPRR persons

**Priority:** Medium.

**Target:** 35 persons with clean short-numeric VIAF IDs.

**Method:** VIAF cluster API → extract LC NID → write lcnaf_id.

**Estimated:** 1 session.

---

## BibliographySource stubs (micro-task)

- Broughton_MRR: add label="Magistrates of the Roman Republic", uri=...
- Zmeskal_Adfinitas: add label="Adfinitas", uri=...

---

## D-035 (parallel)

- D12/D13 wire read paths
- entity_count cleanup on SubjectConcept
