# Claims Audit Report - Phase 2 Schema Compatibility

**Date**: July 16, 2026  
**Audited by**: Phase 2 Integration Agent

---

## Executive Summary

Two distinct claim architectures coexist in the Neo4j graph:

1. **Legacy System** (5,667 Claim nodes) - `claim_ingestion_pipeline.py`
2. **Phase 2 System** (10 test claims) - `ClaimRegistry`

**Key Finding**: The systems use **different data models** - Claims as nodes vs. claims as relationship properties. They are **architecturally incompatible** and require careful migration strategy.

---

## Detailed Findings

### 1. Legacy System Architecture (5,667 claims)

**Pattern:**
```
(Claim node) -[:ASSERTS]-> (Entity node)
(Claim node) -[:IN_SCOPE]-> (SubjectConcept node)
(Claim node) -[:ASSERTS_EDGE]-> (ProposedEdge node)
```

**Claim Node Properties** (Rich metadata):
```python
{
    'claim_id': 'claim_330da6e5dc0f',
    'cipher': 'fclaim_bio_86c4b6d726636d02',
    'facet': 'biographic',
    'confidence': 0.82,
    'status': 'proposed',  # or 'validated'
    'source_agent': 'sfa_biographic',
    'timestamp': '2026-07-15T18:44:23',
    'routed_subject_id': 'sc_q17167_senatorial_elite_careers',
    'routed_subject_label': 'Senatorial Elite & Magistrates',
    'routing_method': 'edge',
    'routing_score': 0.75,
    'label': 'Descriptive text',
    'description': 'Longer description',
    'claim_type': 'documentary',
    'evidence_score': 0.4622,
    'bayesian_score': 0.8128,
    'prior_probability': 0.692,
    'likelihood': 0.659,
    'posterior_probability': 0.8128,
    'promoted': True/None,
    'promotion_date': '2026-07-15T19:51:37',
    'reconciliation_status': 'promoted_gap_fill',
    'fischer_status': 'skipped',
    # ... more properties
}
```

**Relationship Counts**:
- 11,332 `:ASSERTS` to Entity
- 5,666 `:IN_SCOPE` to SubjectConcept
- 5,666 `:ASSERTS_EDGE` to ProposedEdge
- 255 `:HAS_ANALYSIS_RUN` to AnalysisRun
- 255 `:HAS_FACET_ASSESSMENT` to FacetAssessment

**Status Distribution**:
- Most claims: status=NULL (legacy format without status)
- Some claims: status='proposed' or 'validated'

**Facet Distribution**:
- Most claims: facet=NULL (11,451)
- biographic facet: exists in Claim nodes

---

### 2. Phase 2 System Architecture (10 claims)

**Pattern:**
```
(Agent node) -[:ASSERTS {properties}]-> (Entity node)
```

**Relationship Properties** (Metadata on edge):
```python
{
    'facet': 'MILITARY',
    'predicate': 'commanded_legion',
    'confidence': 0.95,
    'status': 'TBD',  # or 'PROPOSED', 'CONFIRMED', 'CONTESTED'
    'submitted_at': '2026-07-16T08:30:00',
    'review_count': 0,
    'agreement_score': 0.0,
    'source_qid': 'Q1048',
    # ... optional properties
}
```

**Agent Nodes**: 24 total
- Examples: `military_sfa_001`, `political_sfa_001`, `SFA_POLITICAL_RR`, etc.
- Most have `facet=NULL`

**Status Distribution**:
- TBD: 6
- CONFIRMED: 3
- CONTESTED: 1

---

## Architectural Differences

| Aspect | Legacy System | Phase 2 System |
|--------|---------------|----------------|
| **Claim Storage** | Claim node | Relationship property |
| **Pattern** | (Claim)-[:ASSERTS]->(Entity) | (Agent)-[:ASSERTS {props}]->(Entity) |
| **Metadata Location** | On Claim node | On :ASSERTS relationship |
| **Facet Format** | lowercase ('biographic') | UPPERCASE ('MILITARY') |
| **Status Values** | 'proposed', 'validated' | 'TBD', 'PROPOSED', 'CONFIRMED', 'CONTESTED' |
| **Routing** | :IN_SCOPE to SubjectConcept | Not yet implemented |
| **Bayesian Scores** | Yes (evidence, likelihood, posterior) | No |
| **Routing Metadata** | Yes (routing_method, routing_score) | No |
| **Peer Review** | No | Yes (:REVIEWED relationships) |

---

## Entity Cipher Compatibility

**Good News**:
- 2,373 entities have `entity_cipher` property
- Entity cipher format appears compatible with Phase 2
- Both systems can reference the same entities

---

## Migration Considerations

### Option 1: Coexistence (Recommended)

**Keep both systems operational**:
- Legacy system continues for existing 5,667 claims
- Phase 2 system for new SFA-generated claims
- Gradual migration over time

**Pros**:
- No disruption to existing claims
- Preserves Bayesian scores, routing metadata
- Allows testing Phase 2 before full migration

**Cons**:
- Two query patterns needed
- Increased complexity

### Option 2: Full Migration

**Convert all legacy Claim nodes to Phase 2 format**:
1. For each Claim node:
   - Create/find Agent node
   - Create :ASSERTS relationship with properties
   - Copy metadata from node to relationship
   - Archive or delete Claim node

**Pros**:
- Single unified system
- Simpler queries

**Cons**:
- Lossy conversion (Bayesian scores, routing don't fit Phase 2)
- Risk of data loss
- Requires careful testing

### Option 3: Hybrid Reporting

**Keep separate, build unified query layer**:
- Create views/procedures that query both
- Aggregate results for reporting
- UI shows claims from both systems

**Pros**:
- No migration needed
- Best of both worlds

**Cons**:
- Complex query layer
- Maintenance burden

---

## Recommendations

### Immediate Actions

1. **Complete Phase 2 audit** ✅ (Done)

2. **Document both systems** 
   - Create `LEGACY_CLAIMS_SPEC.md`
   - Create `PHASE2_CLAIMS_SPEC.md`

3. **Alignment decisions**:
   - Decide on facet naming (lowercase vs UPPERCASE)
   - Decide on status vocabulary alignment
   - Decide on migration timeline

4. **Test Military SFA with entities**:
   - Use existing 2,373 entities with entity_cipher
   - Don't worry about legacy claims yet
   - Focus on new claim generation

### Medium-Term (Next 2-4 Weeks)

5. **Implement Priority SFAs** (POLITICAL, GEOGRAPHIC, RELIGIOUS, ECONOMIC)
   - All use Phase 2 architecture
   - Generate new claims in Phase 2 format

6. **Create unified query API**:
   - Query both legacy and Phase 2 claims
   - Normalize results for UI

7. **Evaluate migration need**:
   - After 4-5 SFAs operational, assess whether legacy migration is needed
   - If legacy claims are stable/archival, coexistence may be fine

### Long-Term (2-3 Months)

8. **Migration script (if needed)**:
   - Convert legacy → Phase 2 format
   - Preserve what's possible
   - Archive what doesn't fit

9. **Deprecate claim_ingestion_pipeline.py**:
   - All new claims via ClaimRegistry
   - Legacy pipeline read-only

---

## Test Impact

**Phase 2 tests are unaffected**:
- Our 10 test claims are isolated
- Legacy claims don't interfere
- Tests pass because they create their own data

**Military SFA can proceed**:
- Will use existing entities (2,373 with entity_cipher)
- Will create new Phase 2 format claims
- Won't conflict with legacy claims

---

## Questions for Resolution

1. **Facet naming convention**:
   - Convert legacy lowercase to UPPERCASE?
   - Or support both?

2. **Status vocabulary**:
   - Map 'proposed' → 'PROPOSED', 'validated' → 'CONFIRMED'?
   - Or maintain separate vocabularies?

3. **Routing integration**:
   - Should Phase 2 claims have :IN_SCOPE to SubjectConcept?
   - Or is that legacy-only?

4. **Bayesian scores**:
   - Do we need these in Phase 2?
   - Or is confidence score sufficient?

5. **Migration timeline**:
   - Urgent, medium-term, or optional?
   - Depends on whether legacy system is actively used

---

## Conclusion

**The audit reveals TWO working systems with different architectures.**

**Immediate action**: Proceed with Phase 2 SFA development without migration. The systems can coexist.

**Decision needed**: User should decide on migration strategy based on:
- Whether legacy claims are actively being created
- Whether legacy claims need peer review
- Whether unified reporting is essential

**Next step**: Test Military SFA with existing entities, generate new Phase 2 claims, then evaluate migration need.
