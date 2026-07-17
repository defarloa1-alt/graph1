# IGAR + Multi-Agent Claims - Integration Decisions

**Date:** 2026-07-16  
**Status:** Approved for Implementation  

## Integration Decisions

### 1. IGAR in Claim Cipher
**Decision:** IGAR chains are **metadata**, NOT part of claim cipher calculation.

**Rationale:**
- Enables cross-facet validation (multiple SFAs can agree on same event)
- Preserves facet-specific IGAR interpretations as array
- Different perspectives = valuable data, not duplicate claims

**Implementation:**
```python
claim_metadata = {
    'claim_cipher': 'claim_<content_hash>',  # Event + relationship + temporal_scope
    'igar_perspectives': [
        {'facet': 'BIOGRAPHIC', 'input': '...', 'goal': '...', 'action': '...', 'result': '...'},
        {'facet': 'MILITARY', 'input': '...', 'goal': '...', 'action': '...', 'result': '...'}
    ]
}
```

### 2. Canonical Facet Count
**Decision:** **18 facets** (including BIOGRAPHIC)

**Complete List:**
1. ARCHAEOLOGICAL
2. ARTISTIC
3. BIOGRAPHIC
4. COMMUNICATION
5. CULTURAL
6. DEMOGRAPHIC
7. DIPLOMATIC
8. ECONOMIC
9. ENVIRONMENTAL
10. GEOGRAPHIC
11. INTELLECTUAL
12. LINGUISTIC
13. MILITARY
14. POLITICAL
15. RELIGIOUS
16. SCIENTIFIC
17. SOCIAL
18. TECHNOLOGICAL

**Action:** Update IGAR document to reflect 18 facets.

### 3. IGAR Scope
**Decision:** IGAR chains **only for actor-centric events**

**Applies to:**
- Events where human actors make decisions (Caesar crossing Rubicon)
- Events with clear Input → Goal → Action → Result structure

**Does NOT apply to:**
- Concepts (land reform, optimates)
- Places (Rome, Rubicon)
- Periods (Roman Republic)
- Natural events (earthquakes, eclipses)
- Works (De Bello Gallico)

**Validation:** Claim Registry checks entity type = EVENT and has actor before requiring IGAR.

### 4. IGAR Temporal Granularity
**Decision:** **Year-level precision**

**Format:** ISO year with BCE as negative: `-49`, `476`, `~100` (circa)

**Validation:**
- Input year ≤ Action year
- Action year ≤ Result year (or concurrent)
- Goal is timeless (no date required)

**Example:**
```python
igar_chain = {
    'input': 'Senate refuses demands',
    'input_year': -49,
    'goal': 'Maintain dignitas',
    'action': 'Cross Rubicon',
    'action_year': -49,
    'result': 'Civil war triggered',
    'result_year': -49
}
```

### 5. Conflict Representation
**Decision:** `CONTESTED` status + `:REVIEWED` edges **sufficient**

**No need for explicit** `CONFLICTS_WITH` edges at this time.

**Rationale:**
- CONTESTED status already flags disagreement
- :REVIEWED edges carry `agrees: false` rationale
- Can add CONFLICTS_WITH later if needed for specific queries
- Simpler implementation path

**Query pattern for conflicts:**
```cypher
// Find contested claims with disagreement rationale
MATCH (e)<-[c:ASSERTS {status: 'CONTESTED'}]-(sfa1)
MATCH (sfa2)-[r:REVIEWED {agrees: false}]->(c)
RETURN e.label, sfa1.facet, sfa2.facet, r.note
```

---

## Implementation Path

**Phase 0 (Week 1):** Entity cipher extension (Events, Periods, Works)  
**Phase 1 (Week 2-3):** Claim Registry with IGAR validation  
**Phase 2 (Week 4-5):** Two-phase SFA workflow  
**Phase 3 (Week 6+):** Conflict resolution UI  

---

## Next: Phase 0
See `MULTI_AGENT_IMPLEMENTATION_ROADMAP.md` for tasks.

Start with: `scripts/tools/entity_cipher.py` updates.
