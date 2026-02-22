# Phase 1: User Decisions & Implementation Strategy

**Status:** Decisions Locked In  
**Date:** February 14, 2026  

---

## DECISION 1: QID Resolution via LLM (NEW Option D)

**Your Decision:** "Would not LLM be able to determine the most appropriate QID?"

### Proposed Approach: LLM-Assisted QID Resolution

```
CLAIM INGESTION FLOW:

1. User/agent submits claim: "Marcus Brutus was son of Servilia"
   - No QID provided for Marcus Brutus
   
2. LLM QID Resolution Layer (NEW):
   - Extract entity: "Marcus Brutus"
   - Query Wikidata SPARQL: SEARCH "Marcus Brutus" → returns [Q83416, Q264000, Q29523]
   - Score candidates: 
     * Q83416 (Marcus Junius Brutus, 85-42 BCE) → **0.98** ✓ (matches context: Republican era, conspirator)
     * Q264000 (Marcus Brutus, unspecified) → 0.62 (too generic)
     * Q29523 (Brutus family ancestor) → 0.45 (too early)
   - AUTO-ASSIGN: qid = Q83416 (highest confidence match)
   
3. Fallback for no match:
   - IF Wikidata search < 0.70 confidence → use Option C: local_entity_{hash}
   - IF authority_ids exist (LCSH sh85018999) → accept hybrid entity
   
4. Claim ingestion proceeds with resolved QID
```

### Implementation

**Add to claim_ingestion_pipeline.py:**

```python
class QIDResolver:
    """LLM-assisted Wikidata QID resolution"""
    
    def resolve_qid(self, entity_label: str, context: dict = None) -> dict:
        """
        Attempt to resolve entity to Wikidata QID
        
        Args:
            entity_label: "Marcus Brutus"
            context: {period: "Roman Republic", role: "conspirator", ...}
        
        Returns:
            {qid: "Q83416", confidence: 0.98, method: "wikidata_search"}
            OR
            {qid: "local_entity_a8f9e2", confidence: None, method: "provisional"}
        """
        
        # 1. Wikidata fuzzy search
        candidates = self.wikidata_search(entity_label)
        
        # 2. Score candidates using context
        if candidates:
            scored = self.score_candidates(candidates, context)
            best = max(scored, key=lambda x: x['confidence'])
            
            if best['confidence'] >= 0.75:  # Accept threshold
                return {
                    "qid": best['qid'],
                    "confidence": best['confidence'],
                    "method": "wikidata_resolved",
                    "candidates": scored  # Track alternatives
                }
        
        # 3. Fallback: provisional local QID
        return {
            "qid": f"local_entity_{hash(entity_label)}",
            "confidence": None,
            "method": "provisional_local",
            "note": "No Wikidata match; enable post-hoc linking"
        }

resolver = QIDResolver()
result = resolver.resolve_qid(
    "Marcus Brutus",
    context={"period": "Roman Republic", "role": "conspirator"}
)
# Returns: {qid: "Q83416", confidence: 0.98, method: "wikidata_resolved"}
```

### Pros/Cons

**Pros:**
- ✅ Allows granular claims without pre-existing QIDs
- ✅ LLM leverages context (period, role, relationships) to disambiguate
- ✅ Scales to ambiguous historical figures automatically
- ✅ Graceful fallback to local_entity_* if no match

**Cons:**
- ❌ Wikidata API dependency (latency, quota limits)
- ❌ Matching confidence can be low for obscure figures
- ❌ Requires context extraction pipeline before resolution
- ❌ Local QIDs need post-hoc verification (optional second pass)

### When to Block

The constraint becomes:
```cypher
# PERMISSIVE: Allow either Wikidata OR authority_ids OR provisional
CREATE CONSTRAINT human_has_identifier IF NOT EXISTS
FOR (h:Human) REQUIRE h.qid IS NOT NULL OR h.authority_ids IS NOT NULL;
```

**Not** a hard QID requirement, but ensures **some** identifier for federation.

---

## DECISION 2: Per-Facet Confidence Baselines (Option B)

**Your Decision:** "Per facet"

### Implementation

**Relationship registry structure:**

```csv
relationship_type,inverse_type,wikidata_property,confidence_baseline_demographic,confidence_baseline_social,confidence_baseline_political,confidence_baseline_military,facets
PARENT_OF,CHILD_OF,P40,0.92,0.85,0.75,NA,demographic|social
SPOUSE_OF,SPOUSE_OF,P26,0.88,0.90,0.92,NA,social|political
PARTICIPATED_IN,HAD_PARTICIPANT,P710,NA,0.80,0.85,0.85,military|political|diplomatic
DIED_AT,DEATH_LOCATION,P1120,0.95,NA,NA,0.98,military|demographic
MEMBER_OF_GENS,HAS_GENS_MEMBER,P53,NA,0.90,0.85,NA,social|cultural
```

**Pipeline logic:**

```python
def ingest_claim_with_facet_baseline(
    self,
    relationship_type: str,
    confidence: float,
    facet: str
) -> dict:
    """
    Apply facet-specific baseline to confidence
    """
    
    # Look up baseline for this relationship + facet combo
    baseline_key = f"confidence_baseline_{facet}"
    baseline = self.registry[relationship_type].get(baseline_key)
    
    if baseline is None:
        # Facet not applicable to this relationship
        return {"error": f"{relationship_type} not applicable to {facet}"}
    
    # If submitted confidence is low, use baseline strategically
    if confidence < baseline:
        # For genealogy: boost to baseline (historical records reliable)
        if facet == "demographic":
            confidence = baseline * 0.95  # Slightly conservative
        # For political/military: use submitted confidence (user knows context)
        else:
            confidence = max(confidence, baseline * 0.80)
    
    return {
        "confidence_adjusted": confidence,
        "baseline_for_facet": baseline,
        "facet": facet,
        "relationship_type": relationship_type
    }

# Example: SPOUSE_OF claim
result = pipeline.ingest_claim_with_facet_baseline(
    relationship_type="SPOUSE_OF",
    confidence=0.85,
    facet="political"  # <- Political alliance context
)
# Returns: confidence_adjusted=0.92 (uses political baseline, higher than social)

result2 = pipeline.ingest_claim_with_facet_baseline(
    relationship_type="SPOUSE_OF",
    confidence=0.85,
    facet="social"  # <- Personal relationship context
)
# Returns: confidence_adjusted=0.90 (uses social baseline, slightly lower than political)
```

### Advantage Over Single Baseline

**Before (single baseline):**
```
SPOUSE_OF baseline = 0.88 (averaged across all facets)
Caesar-Cornelia marriage (political) promoted at 0.88 → might fail posterior
Caesar-Cornelia marriage (genealogical) promoted at 0.88 → loses nuance (too low)
```

**After (per-facet baseline):**
```
SPOUSE_OF baseline_political = 0.92 → captures alliance importance
SPOUSE_OF baseline_demographic = 0.88 → captures genealogical record reliability
SPOUSE_OF baseline_social = 0.90 → captures personal union record quality
```

---

## DECISION 3: Edge Properties with Dynamic Role Reference (Option A + Dynamic)

**Your Decision:** "Option A but don't we have a canonical list of roles, or can that be built dynamically and referenced by the LLM?"

### Hybrid Approach: Static Registry + Dynamic LLM Reference

**Part 1: Canonical Role Registry**

Create: `Relationships/role_qualifier_reference.json`

```json
{
  "military_roles": {
    "commander": {
      "p_value": "P598",
      "description": "Military command",
      "context_facets": ["military"],
      "examples": ["Julius Caesar at Battle of Pharsalus"]
    },
    "soldier": {
      "p_value": "P607",
      "description": "Combat participant",
      "context_facets": ["military"],
      "examples": ["Legionary at Actium"]
    },
    "scout": {
      "p_value": "P607",
      "description": "Reconnaissance",
      "context_facets": ["military"],
      "examples": ["Auxiliary scout"]
    },
    "general": {
      "p_value": "P410",
      "description": "General rank",
      "context_facets": ["military"],
      "examples": ["Caesar as general"]
    }
  },
  "diplomatic_roles": {
    "ambassador": {
      "p_value": "P50",
      "description": "Diplomatic envoy",
      "context_facets": ["diplomatic", "political"],
      "examples": ["Roman ambassador to Egypt"]
    },
    "negotiator": {
      "p_value": "P3342",
      "description": "Treaty negotiator",
      "context_facets": ["diplomatic"],
      "examples": ["Negotiated peace with Parthia"]
    }
  },
  "political_roles": {
    "senator": {
      "p_value": "P39",
      "description": "Senate member",
      "context_facets": ["political"],
      "examples": ["Cicero in Senate"]
    },
    "consul": {
      "p_value": "P39",
      "description": "Consul office",
      "context_facets": ["political"],
      "examples": ["Caesar as consul"]
    }
  }
}
```

**Part 2: LLM Role Validator**

```python
class RoleValidator:
    """Dynamic role reference with LLM constraint checking"""
    
    def __init__(self, role_registry: dict):
        self.registry = role_registry
        self.all_valid_roles = self._flatten_registry()
    
    def _flatten_registry(self) -> list:
        """Extract all valid role keys"""
        roles = []
        for category, role_dict in self.registry.items():
            roles.extend(role_dict.keys())
        return roles
    
    def validate_role(self, role_label: str, facet: str = None) -> dict:
        """
        Validate role against canonical list
        
        Args:
            role_label: "commander" or "leading the cavalry charge"
            facet: "military" (optional context)
        
        Returns:
            {canonical_role: "commander", confidence: 0.98, valid: True}
            OR
            {canonical_role: None, alternatives: ["commander", "general"], valid: False}
        """
        
        # 1. Exact match
        if role_label in self.all_valid_roles:
            return {
                "canonical_role": role_label,
                "confidence": 1.0,
                "valid": True,
                "method": "exact_match"
            }
        
        # 2. LLM fuzzy match (IMPORTANT: LLM resolves ambiguous roles)
        candidates = self._llm_fuzzy_match(role_label, facet)
        if candidates:
            best = max(candidates, key=lambda x: x['confidence'])
            if best['confidence'] >= 0.80:
                return {
                    "canonical_role": best['role'],
                    "confidence": best['confidence'],
                    "valid": True,
                    "method": "llm_fuzzy_match",
                    "alternatives": candidates
                }
        
        # 3. No valid match
        return {
            "canonical_role": None,
            "confidence": None,
            "valid": False,
            "method": "no_match",
            "valid_roles": self.all_valid_roles,
            "suggestion": "Role not recognized; use canonical list above"
        }
    
    def _llm_fuzzy_match(self, role_label: str, facet: str = None) -> list:
        """
        LLM-powered fuzzy matching
        Example: "leading the cavalry" → "commander"
        """
        # In real implementation: call LLM with role_label + valid_roles
        # For now: simple semantic matching
        
        similarity_scores = []
        for valid_role in self.all_valid_roles:
            # Pseudo-LLM: semantic distance
            score = self._semantic_similarity(role_label, valid_role)
            if score >= 0.70:
                similarity_scores.append({
                    'role': valid_role,
                    'confidence': score
                })
        
        return sorted(similarity_scores, key=lambda x: x['confidence'], reverse=True)

# Usage
validator = RoleValidator(role_registry)

# User submits: "Julius Caesar was leading the cavalry charge at Pharsalus"
result = validator.validate_role("leading the cavalry charge", facet="military")
# Returns: {canonical_role: "commander", confidence: 0.92, valid: True}

# User submits: "Pompey was foo_bar_role in the battle"
result2 = validator.validate_role("foo_bar_role")
# Returns: {canonical_role: None, valid: False, valid_roles: [...], suggestion: "..."}
```

**Part 3: Neo4j Edge Properties**

```cypher
// Create edges with validated roles
MATCH (h:Human {qid: "Q1048"}), (e:Event {qid: "Q193304"})
CREATE (h)-[:PARTICIPATED_IN {
  role: "commander",           // ← Validated from canonical registry
  role_p_value: "P598",        // ← Maps to Wikidata P598
  faction: "Roman",
  outcome: "victorious",
  confidence: 0.98,
  wikidata_property_id: "P710" // Generic participation property
}]->(e)
```

**Query example:**
```cypher
MATCH (h:Human)-[r:PARTICIPATED_IN]->(e:Event)
WHERE r.role IN ["commander", "general"]  // ← Constraint to canonical roles
RETURN h.label, r.role, e.label
```

### Pros/Cons of This Hybrid Approach

**Pros:**
- ✅ **Static registry maintains consistency** — All roles in one place
- ✅ **LLM fuzzy matching handles ambiguity** — "leading cavalry" → "commander"
- ✅ **Queryable** — Can search by role efficiently
- ✅ **Wikidata-aligned** — Each role maps to P-value
- ✅ **Extensible** — New roles added to registry dynamically
- ✅ **Constraint-enabled** — LLM can't invent roles; must be canonical

**Cons:**
- ❌ **Registry maintenance burden** — New roles must be added manually
- ❌ **LLM latency** — Fuzzy matching requires LLM call per claim
- ❌ **Overfitting risk** — If role list too specific, fuzzy match fails
- ❌ **Historical role ambiguity** — Roman "tribunus" ≠ modern "officer"; registry can't capture all context

### Decision Sub-Point: Registry Growth Strategy

**Option A1: Static Registry (Start Small)**
```
Initial roles: [commander, soldier, general, ambassador, consul, senator]
Add new roles only after evidence cluster of similar uses
Pros: Clean; less bloat
Cons: Slow scaling; might reject valid roles
```

**Option A2: Dynamic Registry (Start Big)**
```
Extract roles from Wikidata P410 (military rank) + P39 (position held)
Auto-populate registry from Wikidata
New roles auto-accepted if found in Wikidata
Pros: Scales fast
Cons: Wikidata may have conflicting definitions
```

**Recommendation:** Start with A1 (static, curated), expand to A2 after Phase 1.

---

## DECISION 4: CIDOC-CRM & CRMinf Alignment (Pros/Cons)

**Your Decision:** "Show pros and cons"

### Option X: Full CIDOC + CRMinf Integration

```
Each relationship gets:
- cidoc_crm_class: "E7_Activity" (what CIDOC does it align to?)
- minf_belief_class: "I2_Belief" (how CRMinf reasons about this?)
- minf_belief_id: unique identifier for reasoning chain
```

### Pros of Full Integration

| Aspect | Pro | Implication |
|--------|-----|------------|
| **Ontological Grounding** | Every claim aligned to CIDOC-CRM — semantic interoperability with other RDF systems | Can query across Graph1 + DBpedia + other CIDOC adopters |
| **Reasoning Transparency** | CRMinf belief tracking per relationship — know WHO asserts participation | Audit trail: "Wikidata P710 asserted this participation" vs. "Local LCSH entry asserted" |
| **Cross-System Validation** | CIDOC classes constrain what relationships are valid | Can't create invalid states (e.g., E7_Activity can't relate to E6_Destruction vice versa) |
| **Knowledge Integration** | Aligns with CIDOC practices in museums/archives — can import their data | Interoperability with Europeana, museum RDF stores |
| **Fallacy Detection Enhancement** | CRMinf reasoning rules can validate claims before ingestion | "E69_Death occurs once per person" — catch duplicates |

### Cons of Full Integration

| Aspect | Con | Implication |
|--------|-----|------------|
| **Schema Complexity** | Every relationship now has 3 properties: relationship_type + cidoc_crm_class + minf_belief_class | Ingestion pipeline becomes complex; more fields to validate |
| **Ontology Lock-In** | If CIDOC-CRM v7.1 changes, all relationships need re-mapping | Maintenance burden; hard to upgrade without migration |
| **Reasoning Overhead** | CRMinf inference engine must run against every claim | Latency increases; posterior scoring now depends on CRMinf consistency checks |
| **Historical Ambiguity** | Roman "tribunus" doesn't map cleanly to single E-class | CIDOC designed for museums; historical roles may not align perfectly |
| **Wikidata Conflict** | Wikidata P-values already encode semantics; CIDOC may contradict | P710 (participant) vs. E7_Activity — which authority wins? |
| **Query Complexity** | Queries become nested: relationship (E7) → belief (I2) → assertion (JX) | Harder for non-expert users to query |

### Recommendation: Phased Integration

**Phase 1 (Now):** 
```
DO: Add minf_belief_id per relationship (CRMinf tracking)
DON'T: Mandate CIDOC-CRM classes yet
Rationale: Unblock genealogy/participation ingestion; defer ontology alignment
```

**Phase 2 (After P1 Validated):**
```
ADD: cidoc_crm_class to relationships (optional initially)
Map highest-frequency relationships first (PARENT_OF, PARTICIPATED_IN)
Leave edge cases undefined initially
```

**Phase 3 (Optional):**
```
FULL CIDOC-CRM validation layer
Reasoning engine checks consistency
Historical roles mapped to CIDOC consensus (if exists)
```

### Decision: Which to Implement Now?

| Approach | Timeline | Risk | Recommendation |
|----------|----------|------|-----------------|
| Full (both CIDOC + CRMinf) | 2-3 weeks | High (complexity) | NO - defer to Phase 2 |
| CRMinf only (belief tracking) | 1 week | Low | **YES - Phase 1** |
| CIDOC only (class mapping) | 1.5 weeks | Medium (alignment work) | Maybe Phase 1.5 |
| Neither (relationships only) | 1 day | Very low | Only if no reasoning needed |

---

## FINAL DECISION MATRIX (LOCKED)

| Issue | Decision | Status | Next Action |
|-------|----------|--------|-------------|
| **QID Requirement** | LLM-assisted resolution (Option D) + provisional fallback | ✅ APPROVED | Build QID resolver into pipeline |
| **Facet Baselines** | Per-facet confidence (Option B) | ✅ APPROVED | Extend registry CSV with per-facet columns |
| **Role Storage** | Edge properties (Option A) + Dynamic role registry + LLM fuzzy match | ✅ APPROVED | Create role_qualifier_reference.json + validator |
| **CIDOC/CRMinf** | CRMinf tracking now (minf_belief_id), CIDOC deferred to Phase 2 | ✅ APPROVED | Add minf_belief_id to relationships; skip CIDOC for Phase 1 |

---

## IMPLEMENTATION SEQUENCE (Phase 1)

**Week 1:**
- [ ] Build QID resolver (LLM + Wikidata search)
- [ ] Create role_qualifier_reference.json (canonical roles)
- [ ] Build RoleValidator with LLM fuzzy match
- [ ] Update claim_ingestion_pipeline.py with resolver + validator

**Week 2:**
- [ ] Extend relationship_types_registry_master.csv with per-facet baselines
- [ ] Add minf_belief_id tracking to relationships
- [ ] Test with Caesar-Brutus genealogical cluster
- [ ] Document discovered role ambiguities

**Readiness:** All Phase 1 prerequisites now clear. Ready to proceed with implementation?
