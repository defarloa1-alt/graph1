# Multi-Agent Canonical Entity Claims - Implementation Roadmap

**Status:** Active  
**Start Date:** 2026-07-16  
**Owner:** Chrystallum Architecture Team  

## Overview

This roadmap implements the **Canonical Entity + Facet-Scoped Claims** architecture (ADR 022) to solve the multi-agent entity fragmentation problem identified in the Perplexity advisory.

## Architecture Documents

- **ADR 022** - Multi-Agent Canonical Entity Claims Architecture (`Key Files/Appendices/05_Architecture_Decisions/ADR_022_Multi_Agent_Canonical_Entity_Claims.md`)
- **ADR 023** - Event Entity Cipher Specification (`Key Files/Appendices/05_Architecture_Decisions/ADR_023_Event_Entity_Cipher_Specification.md`)
- **Perplexity Advisory** - Original proposal (`multiagent proposal`)

## Core Principle

> **"The event exists once. Perspectives on it multiply."**

One canonical entity node in Neo4j. Multiple facet-scoped `:ASSERTS` claims from different SFAs, each with full provenance.

## Phased Implementation

### Phase 0: Prerequisites ✅ COMPLETE

**Goal:** Extend entity cipher system to support all entity types.

**Tasks:**

1. **Update `scripts/tools/entity_cipher.py`**
   - [x] Add entity type prefixes: EVENT (`evt`), PERIOD (`prd`), WORK (`wrk`)
   - [x] Add canonical property definitions for each type
   - [x] Implement `generate_entity_cipher()` with QID priority
   - [x] Implement content-hash fallback for entities without QIDs
   - [x] Add date normalization utilities

2. **Write Unit Tests**
   - [x] Test Event cipher with QID: `ent_evt_Q40979`
   - [x] Test Event cipher with content hash
   - [x] Test cipher determinism (same input → same cipher)
   - [x] Test collision resistance (different input → different cipher)
   - [x] Test all entity types (PERSON, PLACE, EVENT, PERIOD, CONCEPT, WORK)

3. **Documentation**
   - [x] ADR 023 - Event Entity Cipher Specification
   - [x] Phase 0 completion summary

**Acceptance Criteria:**
- ✅ All unit tests pass (29/29)
- ✅ Entity ciphers generated for all 10 entity types
- ✅ Content-hash ciphers are deterministic

**Completed:** 2026-07-16

---

### Phase 1: Foundation ✅ COMPLETE

**Goal:** Implement Claim Registry and update Neo4j schema.

**Deliverables:**
- [x] `scripts/agents/claim_registry.py` (420 lines)
- [x] `Cypher/phase1_multi_agent_schema.cypher`
- [x] `scripts/agents/apply_phase1_schema.py`
- [x] `scripts/tests/test_claim_registry_phase1.py` (10 tests)
- [x] `scripts/demos/phase1_demo.py`

**Core Functions Implemented:**
- [x] `check_entity_exists()` - Deduplication via cipher lookup
- [x] `create_canonical_entity()` - Create canonical nodes
- [x] `submit_claim()` - Submit facet-scoped claims
- [x] `get_claims_for_entity()` - Retrieve claims by facet/status
- [x] `update_claim_status()` - Manage lifecycle

**Schema:**
- [x] Constraints: `agent_id_unique`, plus partial entity constraints
- [x] Indexes: `agent_facet_idx`, `claim_facet_idx`, `claim_status_idx`, `claim_confidence_idx`, `claim_predicate_idx`
- [x] Relationship types: `:ASSERTS` (Agent → Entity)

**Integration Tests:**
- [x] Test deduplication: 2 SFAs → 1 entity, 2 claims ✅
- [x] Test claim metadata: all required fields ✅
- [x] Test entity resolution: QID and content-hash ✅
- [x] Test claim retrieval: filtering by facet/status ✅
- [x] Test status management: TBD → CONFIRMED ✅
- [x] Test error handling: validation ✅

**Test Results:** 10/10 passing

**Acceptance Criteria:**
- ✅ No duplicate entity nodes created (verified)
- ✅ All claims carry full provenance metadata (verified)
- ✅ Claim status defaults to 'TBD' (verified)
- ✅ Integration tests pass (10/10)

**Demo:** Caesar Rubicon event - 3 SFAs, 1 entity, 3 facet claims ✅

**Completed:** 2026-07-16

---

### Phase 2: Peer Review & Coordination ✅ COMPLETE

**Goal:** Implement cross-facet peer review and consensus-based claim promotion.

**Completed:** 2026-07-16

**Deliverables:**
- [x] `scripts/agents/peer_reviewer.py` (470 lines)
- [x] `scripts/tests/test_peer_reviewer_phase2.py` (9 tests)
- [x] `scripts/demos/phase2_demo.py`
- [x] `PHASE_2_COMPLETION_SUMMARY.md`

**Core Functions Implemented:**
- [x] `review_entity_claims()` - Cross-facet claim validation
- [x] `get_agreement_score()` - Calculate consensus (-1.0 to +1.0)
- [x] `promote_high_agreement_claims()` - Auto-promote to CONFIRMED
- [x] `flag_contested_claims()` - Auto-flag as CONTESTED
- [x] `find_contested_claims()` - Detect claims needing review

**Claim Status Lifecycle:**
```
TBD → PROPOSED → CONFIRMED/CONTESTED
 ↓       ↓           ↓
70%    80%+        40%-
conf.  agree      disagree
```

**Review Storage:**
- [x] `:REVIEWED` relationship: Agent → Entity
- [x] Properties: `reviewed_facet`, `reviewed_predicate`, `agrees`, `confidence`, `note`
- [x] Agreement scoring: `(agrees - disagrees) / total_reviews`

**Integration Tests:**
- [x] Test peer review workflow: One facet reviews another's claims ✅
- [x] Test high-confidence agreement ✅
- [x] Test low-confidence disagreement ✅
- [x] Test agreement score calculation ✅
- [x] Test auto-promotion to CONFIRMED ✅
- [x] Test auto-flagging as CONTESTED ✅
- [x] Test contested claim detection ✅
- [x] Test cross-facet consensus building ✅

**Test Results:** 9/9 passing

**Acceptance Criteria:**
- ✅ SFAs can review peer claims
- ✅ Agreement scores calculated correctly
- ✅ Automatic status promotion works
- ✅ Contested claims detected and flagged
- ✅ All integration tests pass

**Demo:** Caesar claims - 3 SFAs, peer review, consensus ✅

**Tasks:**

1. **Peer Review Agent** ✅
   - [x] Cross-facet claim validation
   - [x] Agreement scoring
   - [x] Conflict detection

2. **Automatic Status Promotion** ✅
   - [x] TBD → PROPOSED (confidence-based)
   - [x] PROPOSED → CONFIRMED (consensus-based)
   - [x] PROPOSED → CONTESTED (disagreement-based)

3. **Testing** ✅
   - [ ] Test Phase 2: SFAs review peer claims
   - [ ] Test promotion: TBD → CONFIRMED after reviews
   - [ ] Test contested: conflicting reviews → CONTESTED
   - [ ] Test end-to-end: full lifecycle for one entity

**Acceptance Criteria:**
- ✅ SFAs successfully complete Phase 2 review
- ✅ Claim status updates automatically
- ✅ Contested claims flagged
- ✅ Full lifecycle works end-to-end

**Estimated Effort:** 7-10 days

---

### Phase 3: Scale (Week 6+)

**Goal:** Human review UI, analytics, monitoring.

**Tasks:**

1. **Conflict Resolution UI**
   - Web interface for reviewing contested claims
   - Side-by-side facet comparison
   - Manual promotion/deprecation controls
   - Integration with existing React Neo4j Explorer

2. **Cross-Facet Analytics**
   - Query: "All claims about entity X from all facets"
   - Query: "Entities with most contested claims"
   - Query: "Which facets agree most often?"
   - Visualization of facet agreement patterns

3. **Monitoring Dashboard**
   - Metrics: deduplication rate, claim promotion rate, contested rate
   - Alerts: review backlog threshold exceeded
   - SFA performance: confidence calibration

4. **Confidence Calibration**
   - Track SFA accuracy over time
   - Auto-adjust confidence scores based on historical agreement
   - Identify SFAs needing retraining

**Acceptance Criteria:**
- ✅ Human reviewers can resolve contested claims
- ✅ Cross-facet queries perform well (<500ms)
- ✅ Monitoring dashboard operational
- ✅ Confidence scores correlate with accuracy

**Estimated Effort:** 2-3 weeks

---

## Current Status

**Phase:** Phase 2 ✅ COMPLETE  
**Progress:** Phase 0 ✅ | Phase 1 ✅ | Phase 2 ✅ | Phase 3 → Next  
**Next Action:** Begin Phase 3 - Conflict Resolution UI and SFA Integration

**Summary:**
- Entity fragmentation PREVENTED ✅
- Claim Registry operational ✅
- Schema deployed ✅
- Peer Review & Consensus operational ✅
- Automatic status promotion working ✅
- 19/19 integration tests passing (Phase 1: 10, Phase 2: 9) ✅
- Demos successful ✅

---

## Dependencies

| Task | Depends On | Blocks |
|------|------------|--------|
| Entity Cipher Extension | None | All subsequent work |
| Claim Registry | Entity Cipher | Control Shell |
| Control Shell | Claim Registry | Phase 2 Review |
| Phase 2 Review | Control Shell | Promotion Rules |
| Promotion Rules | Phase 2 Review | Conflict Resolution UI |

---

## Success Metrics (Target: End of Phase 2)

| Metric | Target | Current |
|--------|--------|---------|
| **Deduplication Rate** | >95% | N/A |
| **Claim Promotion Rate** | >70% TBD→CONFIRMED | N/A |
| **Contested Claim Rate** | <10% | N/A |
| **Cross-Facet Agreement** | >80% | N/A |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Entity cipher collisions** | Low | High | Use full SHA256, monitor collision rate |
| **Consensus threshold too strict** | Medium | Medium | Make thresholds configurable, tune empirically |
| **Phase 2 latency unacceptable** | Medium | High | Implement async processing, batch reviews |
| **Human review backlog grows** | High | Medium | Prioritize high-confidence contested claims |
| **SFA disagreement patterns unclear** | Medium | Low | Build analytics early, surface patterns |

---

## Notes

- **Perplexity feedback loop:** Share implementation learnings back to advisory process
- **Incremental deployment:** Phase 1 can ship without Phase 2 (manual promotion interim)
- **Backward compatibility:** Existing entity nodes need migration script to add ciphers
- **Performance:** Index all claim metadata fields (facet, status, confidence)

---

## Questions for Resolution

1. **Consensus threshold N:** How many facets must review before promotion? Start with 3, tune.
2. **Contested resolution SLA:** How fast must contested claims be reviewed by humans? Target: <48 hours.
3. **Predicate vocabulary:** Is there a controlled vocabulary of predicates, or free-form? Suggest controlled, extensible.
4. **Review incentives:** How are SFAs incentivized to perform Phase 2 reviews? Suggest: blocked on own promotions until reviews done.

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-16 | 0.1 | Initial roadmap |
| 2026-07-16 | 1.0 | Phase 0 complete, Phase 1 complete |
