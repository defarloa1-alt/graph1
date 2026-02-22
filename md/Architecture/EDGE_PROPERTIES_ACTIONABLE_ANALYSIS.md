# Edge Properties: Actionable Analysis from Literature

**Date:** February 22, 2026  
**Status:** Architectural Analysis  
**Purpose:** Extract actionable insights from 10 edge property resources and apply to Chrystallum

---

## Executive Summary

**Reviewed:** 10 resources on property graphs, reification, edge metadata, and temporal context

**Key Finding:** Property graphs (Neo4j) support **edges with arbitrary key-value properties** natively — this is the fundamental advantage over RDF.

**Actionable Result:** Complete edge property schema for Chrystallum (5 tiers + reification strategy)

---

## Resource 1: Property Graph Formal Definition (Wikipedia)

**URL:** https://en.wikipedia.org/wiki/Property_graph

### **Key Insight: Formal 7-Tuple Definition**

```
Property Graph = (N, A, K, V, α, κ, π)

Where:
N = Nodes (vertices)
A = Arcs (directed edges)
K = Keys (property names)
V = Values (property values)
α = Function mapping arcs to (source, target) node pairs
κ = Binary relation associating keys with nodes/arcs
π = Partial function providing values for properties
```

**Translation for Chrystallum:**
- **N** = Entity, FacetedEntity, FacetClaim nodes
- **A** = INSTANCE_OF, PART_OF, POSITION_HELD, ATTESTED_BY edges
- **K** = {wikidata_pid, temporal_start_year, location_qid, confidence, ...}
- **V** = {-59, "Q220", 0.85, ...}
- **π** = Edge property assignment function

---

### **Actionable Decision:**

**Edges can have arbitrary properties** — no theoretical limit!

**For Chrystallum:**
```cypher
-[:POSITION_HELD {
  wikidata_pid: "P39",                 // K₁ → V₁
  temporal_start_year: -59,            // K₂ → V₂
  temporal_end_year: -58,              // K₃ → V₃
  location_qid: "Q220",                // K₄ → V₄
  confidence: 0.85,                    // K₅ → V₅
  source_qid: "Q193291",               // K₆ → V₆
  passage_locator: "Lives.Caesar.11",  // K₇ → V₇
  claim_cipher: "fclaim_pol_...",      // K₈ → V₈
  created_at: "2026-02-21"             // K₉ → V₉
}]->
```

**Validation:** π(arc, key) returns value if property defined, undefined otherwise.

**Baseline vocabulary:** **Edges can legally carry any key-value pairs** (formal justification).

---

## Resource 2: AWS Property Graph Reference

**URL:** https://aws-samples.github.io/aws-dbs-refarch-graph/src/data-models-and-query-languages/

### **Key Insights: Production Patterns**

**1. Edge properties are FIRST-CLASS in property graphs:**
> "Property graphs support edge properties, making it easy to associate edge attributes, such as the strength, weight or quality of a relationship or some edge metadata, with the edge definition."

**2. Use edge properties for:**
- Timestamps (when relationship held)
- Weights (strength of connection)
- Quality metrics (confidence, salience)
- Provenance (source, evidence)
- Metadata (created_by, created_at)

**3. Bidirectional relationships:**
> "While every edge must be directed, Gremlin allows you to ignore edge direction in queries (using `both()` and `bothE()` steps). If you need to model bi-directional relationships, consider using a property graph."

---

### **Actionable for Chrystallum:**

**1. Store bidirectional edges** (ADR-011 validated by AWS best practice)

**2. Edge properties are production-standard:**
```cypher
-[:POSITION_HELD {
  temporal_start: -59,      // Timestamp (when)
  temporal_end: -58,
  confidence: 0.85,         // Quality (strength)
  source_qid: "Q193291",    // Provenance
  created_by: "SFA_POLITICAL" // Metadata
}]->
```

**3. Use compound IDs on edges:**
```cypher
{
  edge_id: "fclaim_pol_a1b2...:Q193291:c4e5",  // Unique edge identity
  pattern_id: "fclaim_pol_a1b2...",             // Shared pattern prefix
  // AWS: "All edge IDs must be unique"
}
```

---

## Resource 3: Reification Patterns (Douroucouli Blog)

**URL:** https://douroucouli.wordpress.com/2020/09/11/edge-properties-part-1-reification/

### **Key Insight: When to Reify (Turn Edge into Node)**

**RDF Problem:** Can't add properties to edges directly

**Solution Patterns:**
1. **Standard reification** — Create node representing statement
2. **Singleton properties** — Unique predicate per statement
3. **N-ary relations** — Intermediate node
4. **RDF-star** — Quoted triples `<< :A :knows :B >> :since 2002`

**Property Graph Advantage:**
> "With an LPG, an edge can have properties associated with it... depicted as tag-values underneath the edge label."

---

### **Actionable for Chrystallum:**

**Decision:** Use **native Neo4j edge properties** (not reification!)

**Why:**
- ✅ Neo4j is property graph (not RDF)
- ✅ Edges natively support properties
- ✅ No reification overhead
- ✅ Simpler queries

**When to Reify (Create FacetClaim Node):**
```
Use Edge Properties:                 Use FacetClaim Node:
- Simple qualifiers                  - Multiple sources attest same pattern
- Temporal bounds                    - Need to make statements ABOUT the assertion
- Confidence (single source)         - Retrospective claims analyze InSitu claims
- Provenance (single source)         - Complex argumentation structure

Example:                             Example:
Caesar -[:POSITION_HELD {            (:FacetClaim {pattern})
  temporal: -59,                       <-[:ATTESTED_BY {source, confidence}]-
  confidence: 0.85                   (:Source)
}]-> Consul
```

**Rule:** Reify when you need to make **statements about statements** (CRMinf argumentation). Otherwise use edge properties.

---

## Resource 4: RDF Reification Overview

**URL:** https://graph.stereobooster.com/notes/RDF-reification

### **Key Insight: 6 Reification Patterns Compared**

**Patterns:**
1. Standard reification (4 triples)
2. Singleton properties (unique predicate per statement)
3. Companion properties (cpprop)
4. Universal property graph
5. N-ary relations (intermediate node)
6. Named graphs (quad stores)
7. RDF-star (quoted triples)

**Performance Comparison:**
- Named graphs: Best query performance
- RDF-star: Clean syntax, growing support
- Standard reification: Verbose (4x storage)

---

### **Actionable for Chrystallum:**

**Neo4j is already a "Named Graph" equivalent:**
- Each edge has unique ID (implicit)
- Properties attached directly to edge
- No reification needed

**Our Compound Cipher Mimics RDF-star Syntax:**
```
RDF-star:   << :Caesar :holds :Consulship >> :since -59
Chrystallum: fclaim_pol_a1b2...:Q193291:c4e5
             └─── quoted triple ──┘└─ provenance ┘
```

**Validation:** Our approach aligns with modern RDF-star thinking (quoted triples + metadata)

---

## Resource 5: LinkML Property Graph Schema

**URL:** https://linkml.io/linkml/howtos/model-property-graphs.html

### **Key Insight: Edge Classes (First-Class Schema)**

**Pattern:** Define edge types as **classes** with properties

```yaml
classes:
  Edge:
    attributes:
      subject: {range: Node}
      predicate: {range: uriorcurie}
      object: {range: Node}
  
  ActedIn:
    is_a: Edge
    attributes:
      role: {range: string}      # Edge property!
```

**Benefit:** "Fine-grained control over properties of edges"

---

### **Actionable for Chrystallum:**

**Apply LinkML pattern to relationship categories:**

```python
# Pydantic models (equivalent to LinkML classes)

class HierarchicalRelationship(BaseRelationship):
    """INSTANCE_OF, SUBCLASS_OF, PART_OF"""
    relationship_type: Literal["INSTANCE_OF", "SUBCLASS_OF", "PART_OF"]
    wikidata_pid: str  # REQUIRED
    # NO temporal, NO spatial (timeless ontological)

class TemporalRelationship(BaseRelationship):
    """BROADER_THAN, SUB_PERIOD_OF, DURING"""
    relationship_type: Literal["BROADER_THAN", "SUB_PERIOD_OF", "DURING"]
    temporal_start_year: int  # REQUIRED
    temporal_end_year: int    # REQUIRED
    # Temporal edges MUST have temporal properties

class ParticipatoryRelationship(BaseRelationship):
    """PARTICIPATED_IN, POSITION_HELD, FOUGHT_IN"""
    relationship_type: Literal["PARTICIPATED_IN", "POSITION_HELD", "FOUGHT_IN"]
    temporal_start_year: int   # REQUIRED
    temporal_end_year: int     # REQUIRED
    location_qid: Optional[str]  # RECOMMENDED
    source_qid: str            # REQUIRED (evidence-backed)
    confidence: float          # REQUIRED
    role_in_event: Optional[str]  # Qualifier
```

**Benefit:** Type-safe edge creation (Pydantic validates properties match relationship category)

---

## Synthesis: Edge Property Schema for Chrystallum

### **Decision Matrix: What Properties Go on Edges**

Based on literature review + Chrystallum requirements:

| Property | On Edge? | On FacetClaim? | Rationale (from literature) |
|----------|----------|----------------|----------------------------|
| **wikidata_pid** | ✅ Yes | ✅ Yes | AWS: "Edge metadata" + LinkML: "Type designator" |
| **cidoc_crm_property** | ✅ Yes | ✅ Yes | Semantic interoperability (AWS principle) |
| **temporal_start/end** | ✅ Yes | ✅ Yes | AWS: "Timestamps" + Wikipedia: "Weighted graph" (temporal weight) |
| **location_qid** | ✅ Yes | ✅ Yes | AWS: "Edge attributes" (where relationship occurred) |
| **ordinal** | ✅ Yes | ✅ Yes | Distinguishes 1st vs 2nd instance (identity qualifier) |
| **confidence** | ⚠️ On edge if single source | ✅ Yes | Douroucouli: "Quality of relationship" |
| **source_qid** | ⚠️ Depends | ✅ Yes | **Reify if multiple sources** (compound cipher pattern) |
| **claim_cipher** | ✅ Yes | N/A (is the claim) | Linkage back to claim (provenance) |
| **analysis_layer** | ❌ No | ✅ Yes | Claim property, not edge property |
| **created_by_agent** | ✅ Yes | ✅ Yes | AWS: "Metadata" |

---

### **Reification Decision Rule (From Douroucouli)**

**Use Edge Properties When:**
- Simple relationship (one source)
- No need to make statements ABOUT the relationship
- Standard property graph model sufficient

**Reify to Node When:**
- Multiple sources attest same relationship (corroboration)
- Need to make statements ABOUT the relationship (CRMinf argumentation)
- Complex provenance structure

**For Chrystallum:**
```
Simple edge (one source):
  Caesar -[:POSITION_HELD {
    temporal: -59,
    source_qid: "Q193291",
    confidence: 0.85
  }]-> Consul

Reified (multiple sources):
  (:FacetClaim {
    cipher: "fclaim_pol_a1b2...:Q193291:c4e5",  # Plutarch attestation
    pattern_cipher: "fclaim_pol_a1b2...",
    temporal: -59,
    source_qid: "Q193291",
    confidence: 0.85
  })
  
  (:FacetClaim {
    cipher: "fclaim_pol_a1b2...:Q1385:f7a2",   # Suetonius attestation
    pattern_cipher: "fclaim_pol_a1b2...",      # SAME pattern!
    temporal: -59,
    source_qid: "Q1385",
    confidence: 0.90
  })
```

---

## Actionable Recommendations

### **Recommendation 1: Complete Edge Property Schema (CRITICAL)**

**Based on:** AWS patterns + LinkML + Property graph formalism

**Add to CANONICAL_REFERENCE Section 3.10:**

```yaml
# Edge Property Schema (LinkML-style)

classes:
  BaseRelationship:
    description: Base schema for all Neo4j edges
    attributes:
      wikidata_pid:
        range: string
        pattern: "^P\\d+$"
        required: false
        description: Wikidata property mapping
      
      cidoc_crm_property:
        range: string
        required: false
        description: CIDOC-CRM alignment
      
      relationship_category:
        range: string
        required: false
        description: Registry category (Political, Military, etc.)
      
      temporal_start_year:
        range: integer
        minimum: -10000
        maximum: 3000
        required: false
      
      temporal_end_year:
        range: integer
        minimum: -10000
        maximum: 3000
        required: false
      
      temporal_scope:
        range: string
        pattern: "^-?\\d{4}/-?\\d{4}$"
        required: false
      
      location_qid:
        range: string
        pattern: "^Q\\d+$"
        required: false
      
      source_qid:
        range: string
        pattern: "^Q\\d+$"
        required: false
      
      confidence:
        range: float
        minimum: 0.0
        maximum: 1.0
        required: false
      
      claim_cipher:
        range: string
        pattern: "^fclaim_[a-z]{3}_[a-f0-9]{16}"
        required: false

  HierarchicalRelationship:
    is_a: BaseRelationship
    slot_usage:
      wikidata_pid:
        required: true  # MUST have PID
      temporal_start_year:
        required: false  # Timeless relationships
  
  TemporalRelationship:
    is_a: BaseRelationship
    slot_usage:
      temporal_start_year:
        required: true  # MUST have temporal bounds
      temporal_end_year:
        required: true
  
  ParticipatoryRelationship:
    is_a: BaseRelationship
    slot_usage:
      temporal_start_year:
        required: true
      source_qid:
        required: true  # Evidence-backed
      confidence:
        required: true
```

---

### **Recommendation 2: Dual-Mode Edge Strategy (From Reification Literature)**

**Based on:** Douroucouli + RDF reification patterns

**Pattern:**
- **Mode 1:** Simple edges with properties (single source, no argumentation)
- **Mode 2:** Reified FacetClaim nodes (multiple sources, argumentation)

**Decision Table:**

| Condition | Use | Example |
|-----------|-----|---------|
| **Single source, simple assertion** | Edge with properties | `-[:CHILD_OF {source: "Q193291"}]->` |
| **Multiple sources, same pattern** | FacetClaim nodes (compound cipher) | 3 nodes with shared `pattern_cipher` |
| **Argumentation needed** (Retrospective analyzes InSitu) | FacetClaim nodes | `(:Retro)-[:SUPPORTS]->(:InSitu)` |
| **Simple hierarchy** (INSTANCE_OF, SUBCLASS_OF) | Edge (no reification) | `-[:INSTANCE_OF {wikidata_pid: "P31"}]->` |

---

### **Recommendation 3: Temporal Properties on Edges (AWS + LinkML)**

**Based on:** AWS "timestamps" + LinkML temporal context

**Pattern:** Edges representing temporal relationships MUST have temporal properties

```cypher
// Temporal relationship (POSITION_HELD)
-[:POSITION_HELD {
  temporal_start_year: -59,
  temporal_end_year: -58,
  temporal_scope: "-0059/-0058",
  temporal_calendar: "julian",
  temporal_precision: "year"
}]->

// Timeless relationship (INSTANCE_OF)
-[:INSTANCE_OF {
  wikidata_pid: "P31"
  // NO temporal properties (ontological, not temporal)
}]->
```

**Validation Rule:** If relationship_category = "Temporal" OR "Participatory", temporal properties REQUIRED.

---

### **Recommendation 4: Provenance on Edges (AWS Metadata)**

**Based on:** AWS "edge metadata" pattern

**Pattern:** Evidence-backed edges carry provenance

```cypher
-[:POSITION_HELD {
  source_qid: "Q193291",            // Which source
  passage_locator: "Lives.Caesar.11", // Where in source
  confidence: 0.85,                  // How confident
  extracted_by_agent: "SFA_POLITICAL", // Which agent
  extracted_at: "2026-02-21",         // When extracted
  claim_cipher: "fclaim_pol_a1b2..."  // Link to claim node
}]->
```

**For Simple Edges (Wikidata import):**
```cypher
-[:INSTANCE_OF {
  wikidata_pid: "P31",
  imported_from: "wikidata",
  imported_at: "2026-02-20"
  // Simple provenance (no claim cipher)
}]->
```

---

### **Recommendation 5: Compound Cipher as "Edge ID" (Wikipedia)**

**Based on:** Wikipedia: "Every edge must have unique ID"

**Pattern:** Use compound cipher as edge identifier

```cypher
-[:POSITION_HELD {
  edge_id: "fclaim_pol_a1b2c3d4e5f6g7h8:Q193291:c4e5",  // Unique edge ID
  pattern_id: "fclaim_pol_a1b2c3d4e5f6g7h8",             // Shared pattern
  
  // Pattern components
  subject_cipher: "ent_per_Q1048",
  object_qid: "Q39686",
  temporal_scope: "-0059/-0058",
  
  // Attestation components
  source_qid: "Q193291",
  passage_locator: "Lives.Caesar.11",
  passage_hash: "c4e5",
  confidence: 0.85
}]->
```

**Query for corroboration:**
```cypher
// All edges sharing same pattern
MATCH ()-[r:POSITION_HELD]->()
WHERE r.pattern_id = "fclaim_pol_a1b2..."
RETURN r.source_qid, r.confidence
// O(1) index seek on pattern_id
```

---

## Synthesis: Complete Chrystallum Edge Architecture

### **Three-Mode Edge System**

**Mode 1: Infrastructure Edges** (No Reification)
```cypher
// Ontological, imported from Wikidata
-[:INSTANCE_OF {
  wikidata_pid: "P31",
  imported_from: "wikidata"
}]->

-[:SUBCLASS_OF {
  wikidata_pid: "P279",
  transitive: true
}]->
```

**Properties:** Identity only (PID, category), no temporal/provenance

---

**Mode 2: Simple Evidentiary Edges** (Edge Properties)
```cypher
// Single source, no corroboration needed
-[:CHILD_OF {
  wikidata_pid: "P40",
  biological: true,
  source_qid: "Q193291",
  passage: "Lives.Caesar.1",
  confidence: 0.90,
  created_by: "SFA_BIOGRAPHIC"
}]->
```

**Properties:** Full 5-tier schema (identity, temporal, spatial, provenance, qualifiers)

---

**Mode 3: Reified Claims** (FacetClaim Nodes + Compound Cipher)
```cypher
// Multiple sources OR argumentation needed
(:FacetClaim {
  cipher: "fclaim_pol_a1b2...:Q193291:c4e5",  // Full compound
  pattern_cipher: "fclaim_pol_a1b2...",        // Canonical pattern
  
  // Pattern (immutable)
  subject_entity_cipher: "ent_per_Q1048",
  property_pid: "P39",
  object_qid: "Q39686",
  temporal_scope: "-0059/-0058",
  
  // Attestation (mutable per source)
  source_qid: "Q193291",
  passage_locator: "Lives.Caesar.11",
  confidence: 0.85
})

// Separate node per source, shared pattern_cipher
(:FacetClaim {
  cipher: "fclaim_pol_a1b2...:Q1385:f7a2",
  pattern_cipher: "fclaim_pol_a1b2...",  // SAME!
  source_qid: "Q1385",  // Different source
  confidence: 0.90
})
```

**When to use:** Multiple sources corroborate OR retrospective claims analyze pattern

---

## Actionable Checklist for Architect

### **Immediate (Add to CANONICAL_REFERENCE):**

- [x] Section 3.10: Edge Property Schema (5-tier system) — **DONE**
- [ ] Section 3.11: Reification Decision Rules (when edge vs node)
- [ ] Section 3.12: Mode-Specific Property Requirements (infrastructure vs evidentiary vs reified)
- [ ] Edge property validation (Pydantic models by category)
- [ ] Neo4j indexes for edge properties (temporal, source, confidence)

### **Update Existing Docs:**

- [x] ADR-012: Compound cipher (pattern + attestation) — **DONE**
- [ ] Update TIER_3_CLAIM_CIPHER_ADDENDUM.md with Mode 3 (reified) specification
- [ ] Update PYDANTIC_MODELS_SPECIFICATION.md with edge relationship models

### **For Dev Agent:**

- [ ] Implement Mode 1 edges (INSTANCE_OF, SUBCLASS_OF) with minimal properties
- [ ] Implement Mode 2 edges (CHILD_OF, etc.) with full 5-tier properties
- [ ] Defer Mode 3 (reified FacetClaims) until SFA deployment

---

## References

1. **Property Graph** (Wikipedia) — Formal 7-tuple definition
2. **AWS Property Graph Reference** — Production patterns (timestamps, weights, metadata)
3. **Douroucouli Blog** — Reification decision rules (when to reify)
4. **RDF Reification** (Stereobooster) — 7 reification pattern comparison
5. **LinkML Property Graphs** — Edge classes as first-class schema elements

---

## Key Takeaways

**1. Neo4j edges support arbitrary properties** — no theoretical limit (formal justification)

**2. Edge properties are production-standard** — AWS uses timestamps, weights, quality, provenance

**3. Reify only when needed** — Multiple sources OR argumentation (don't over-reify)

**4. Compound cipher aligns with RDF-star** — Pattern + attestation mimics quoted triples

**5. Three-mode edge system** — Infrastructure (minimal) → Evidentiary (full properties) → Reified (FacetClaim nodes)

---

**Document Status:** ✅ Actionable Analysis Complete  
**Next Action:** Update CANONICAL_REFERENCE with complete edge property schema  
**Impact:** Closes "Issue #3 (CRITICAL)" from advisor feedback
