# Chrystallum: Intent & Motivation - Agent Guidance Subgraph

This document encodes the **core intents and motivations** behind Chrystallum as a knowledge subgraph pattern that agents can reference when making architectural decisions, prioritizing features, or explaining the system to users.

---

## Core Identity Node

```cypher
(:Project {
  id: "chrystallum_v1",
  label: "Chrystallum Knowledge Graph",
  type: "Epistemological Engine",
  tagline: "GitHub for Subgraphs",
  primary_domain: "Historical Research",
  domain_agnostic: true,
  created: "2025-2026",
  status: "active_development"
})
```

---

## Primary Motivations (HAS_MOTIVATION edges)

### Motivation 1: Eliminate Presentism
```cypher
(:Project {id: "chrystallum_v1"})
  -[:HAS_MOTIVATION {priority: 1, weight: 0.95}]->
(:Motivation {
  id: "elim_presentism",
  label: "Eliminate Presentism Through Actor-Centric Reasoning",
  description: "Force reasoning from what actors knew AT THE TIME, not what we know now",
  method: "IGAR Protocol",
  philosophical_basis: "Zhengming (Rectification of Names)"
})
  -[:IMPLEMENTS_VIA]->
(:Protocol {
  id: "igar_v1",
  label: "IGAR: Input → Goal → Action → Result",
  purpose: "Model historical participants from their perspective",
  prevents: "Anachronistic attribution of knowledge/motives"
})
```

**Agent Guidance:**
- When generating claims about historical actors, ALWAYS construct IGAR chains
- Validate that Inputs temporally precede Actions
- Flag any Results that rely on Inputs postdating the event (presentism check)
- Reject claims that attribute modern concepts to ancient actors without evidence

### Motivation 2: Discover Non-Obvious Connections
```cypher
(:Project {id: "chrystallum_v1"})
  -[:HAS_MOTIVATION {priority: 2, weight: 0.90}]->
(:Motivation {
  id: "discover_edges",
  label: "Uncover Non-Obvious Relationships",
  description: "Find connections modern events → ancient claims, or cross-domain bridges",
  example: "Modern legal precedent → Roman Republican institutional pattern",
  value_proposition: "Edge semantics ARE the knowledge, not entity attributes"
})
  -[:REQUIRES]->
(:Architecture {
  id: "rich_edges",
  label: "Rich Relationship Semantics",
  components: ["311 canonical relationship types", "CIDOC-CRM alignment", "Wikidata property mapping"],
  forbidden: "Free-form predicates without registry backing"
})
```

**Agent Guidance:**
- Prioritize relationship type precision over entity proliferation
- When encountering ambiguous predicates, consult relationship_types_registry_master.csv
- Generate "bridge concept" proposals when queries span multiple facets
- Use BROADER_THAN/NARROWER_THAN to discover conceptual pathways

### Motivation 3: Version Control for History
```cypher
(:Project {id: "chrystallum_v1"})
  -[:HAS_MOTIVATION {priority: 3, weight: 0.88}]->
(:Motivation {
  id: "github_for_subgraphs",
  label: "Enable Competing Historical Narratives",
  description: "Treat history like code: propose claims, review evidence, merge consensus",
  metaphor: "Pull requests for historical subgraphs",
  inspiration: "Palantir graph systems + Git version control"
})
  -[:IMPLEMENTS_VIA]->
(:Architecture {
  id: "claim_cipher_system",
  label: "Content-Addressable Claim Identity",
  components: ["Stable ciphers", "FacetPerspective nodes", "Multi-source consensus tracking"],
  benefit: "Same assertion by different agents/times → single claim node (automatic deduplication)"
})
```

**Agent Guidance:**
- Compute claim ciphers from CONTENT ONLY (not provenance)
- Store agent_id, timestamp, confidence as FacetPerspective metadata
- When claims conflict, create CONFLICTS_WITH edges with rationale
- Support "diff" operations: show what changed between claim versions

### Motivation 4: Evidence Transparency
```cypher
(:Project {id: "chrystallum_v1"})
  -[:HAS_MOTIVATION {priority: 4, weight: 0.92}]->
(:Motivation {
  id: "evidence_visibility",
  label: "Make Evidence Chains Explicit and Traceable",
  description: "Every claim traces to source documents with passage locators",
  requirement: "Users see which sources support patterns, where data is thin, and what alternatives exist",
  confidence_model: "Bayesian progression with federation bumps"
})
  -[:REQUIRES]->
(:Pattern {
  id: "source_provenance",
  label: "Source Document → Passage → Claim → Assertion",
  mandatory_fields: ["source_work_qid", "passage_locator", "passage_text_hash"],
  validation: "Cannot create claim without source citation"
})
```

**Agent Guidance:**
- NEVER accept claims without source_work_qid + passage_locator
- When confidence < 0.70, flag for human review
- Apply federation confidence bumps: Trismegistos +0.15, EDH +0.20, VIAF +0.10
- Generate "evidence quality reports" showing source diversity per entity

---

## Architectural Principles (GUIDED_BY edges)

### Principle 1: Authority Precedence
```cypher
(:Project {id: "chrystallum_v1"})
  -[:GUIDED_BY {enforcement: "strict"}]->
(:Principle {
  id: "authority_precedence",
  label: "Tier 1 → Tier 2 → Tier 3 Authority Cascade",
  tiers: [
    {tier: 1, sources: ["LCSH", "FAST", "LCC"], confidence_floor: 0.95},
    {tier: 2, sources: ["CIP", "National Libraries"], confidence_floor: 0.90},
    {tier: 3, sources: ["Wikidata", "Domain Registries"], confidence_floor: 0.85}
  ],
  rule: "Always check Tier 1 before falling back to Tier 2/3"
})
```

**Agent Guidance:**
- SubjectConcept creation: Query LCSH first, FAST second, Wikidata third
- If Tier 1 match exists, DO NOT create separate Tier 3 node
- Store all IDs on single node: authority_id, fast_id, wikidata_qid, lcc_code

### Principle 2: Facet Specialization
```cypher
(:Project {id: "chrystallum_v1"})
  -[:GUIDED_BY {enforcement: "strict"}]->
(:Principle {
  id: "facet_specialization",
  label: "17 Canonical Facets with Uppercase Keys",
  facets: ["ARCHAEOLOGICAL", "ARTISTIC", "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC", "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC", "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC", "SOCIAL", "TECHNOLOGICAL", "COMMUNICATION"],
  rationale: "Deterministic routing, union-safe deduplication, discipline-specific analysis",
  validation: "Pydantic + Neo4j constraints enforce uppercase"
})
```

**Agent Guidance:**
- All facet_id values MUST be UPPERCASE
- When LLM outputs lowercase, normalize before graph write
- Route claims to appropriate SFA based on facet classification
- Support multi-facet entities (e.g., "Trial" = INSTITUTIONAL + SOCIAL + POLITICAL)

### Principle 3: Semantic Precision Over Reduction
```cypher
(:Project {id: "chrystallum_v1"})
  -[:GUIDED_BY {enforcement: "advisory"}]->
(:Principle {
  id: "semantic_precision",
  label: "311 Relationship Types Enable Nuanced Queries",
  example: "FATHER_OF, MOTHER_OF, PARENT_OF all map to Wikidata P40, but enable patrilineal vs matrilineal queries",
  user_insight: "Edge semantics ARE the knowledge graph's value proposition",
  anti_pattern: "Reducing to 48-type kernel for 'simplicity' loses domain precision"
})
```

**Agent Guidance:**
- When tempted to merge relationship types, ask: "Does this lose query capability?"
- Multiple Chrystallum → single Wikidata mappings are PRECISION, not redundancy
- V1 kernel (30 types) is operational baseline, not architectural ceiling

---

## Domain Applications (APPLICABLE_TO edges)

### Application 1: Historical Research (Primary)
```cypher
(:Project {id: "chrystallum_v1"})
  -[:APPLICABLE_TO {maturity: "primary", implementation_status: "production"}]->
(:Domain {
  id: "historical_research",
  label: "Historical Research - Roman Republic",
  test_case: "Q17167 (Roman Republic) with 197 Wikidata claims, 166 validated (84% coverage)",
  value_proposition: "Mechanism graphs showing 'how authoritarians arise' across multiple cases",
  competitive_advantage: "Theory testing with explicit IGAR for actors, not just timeline assembly"
})
```

### Application 2: Legal Firms (Validated Use Case)
```cypher
(:Project {id: "chrystallum_v1"})
  -[:APPLICABLE_TO {maturity: "validated", implementation_status: "conceptual"}]->
(:Domain {
  id: "legal_research",
  label: "Legal Case Law & Evidence Chains",
  top_level_concepts: ["Law (sh85075119)", "Criminal law (sh85034045)", "Civil procedure (sh85026447)"],
  facet_mapping: "INSTITUTIONAL (primary), SOCIAL (jury), POLITICAL (legislation), ECONOMIC (fees)",
  existing_relationships: ["CHARGED_WITH", "CONVICTED_OF", "SENTENCED_TO", "LEGAL_ACTION"],
  advantage_over_astronomy: "Legal relationships already in registry; astronomy has ZERO domain relationships"
})
```

### Application 3: Intelligence Analysis
```cypher
(:Project {id: "chrystallum_v1"})
  -[:APPLICABLE_TO {maturity: "validated", implementation_status: "conceptual"}]->
(:Domain {
  id: "intelligence_analysis",
  label: "Multi-Source Threat Analysis Without Palantir",
  target_users: ["Provincial/national security agencies outside US/EU", "City-level fusion centers"],
  value_proposition: "Pattern templates (authoritarian drift, radicalization) with IGAR overlays",
  competitive_advantage: "Evidence-linked visualizations without huge integration teams or classified infrastructure"
})
```

---

## Operational Constraints (MUST_RESPECT edges)

### Constraint 1: Schema-First Discipline
```cypher
(:Project {id: "chrystallum_v1"})
  -[:MUST_RESPECT]->
(:Constraint {
  id: "schema_first",
  label: "No Free-Form Data Writes",
  rule: "All nodes/edges must validate against canonical schema before graph write",
  validation_layers: ["Pydantic (Python)", "Neo4j constraints (database)", "LLM output filters"],
  rationale: "Cannot have functioning 'pull request' system without strict validation rules"
})
```

**Agent Guidance:**
- Validate ALL claim properties against validation_models.py before write
- If Neo4j constraint fails, DO NOT retry with relaxed validation
- Log validation failures with rationale for schema evolution tracking

### Constraint 2: Content-Only Cipher
```cypher
(:Project {id: "chrystallum_v1"})
  -[:MUST_RESPECT]->
(:Constraint {
  id: "content_only_cipher",
  label: "Claim Identity Excludes Provenance",
  included_in_cipher: ["source_work_qid", "passage_text_hash", "subject_entity_qid", "object_entity_qid", "relationship_type", "action_structure", "temporal_scope", "facet_id"],
  excluded_from_cipher: ["confidence_score", "extractor_agent_id", "extraction_timestamp"],
  rationale: "Provenance changes shouldn't create new claim identity (breaks deduplication)"
})
```

**Agent Guidance:**
- Recompute ciphers during validation to detect tampering
- Store provenance in FacetPerspective nodes, NOT in claim cipher
- When confidence updates, cipher remains stable (citation stability)

---

## Success Metrics (MEASURED_BY edges)

```cypher
(:Project {id: "chrystallum_v1"})
  -[:MEASURED_BY]->
(:Metric {
  id: "claim_validation_rate",
  label: "Wikidata Claim Validation Coverage",
  current_value: 0.84,
  target: 0.90,
  test_case: "Q17167 Roman Republic: 166/197 claims validated"
})

(:Project {id: "chrystallum_v1"})
  -[:MEASURED_BY]->
(:Metric {
  id: "multi_facet_consensus",
  label: "Claims with 2+ Facet Perspectives",
  current_value: "unknown",
  target: 0.40,
  rationale: "Multi-facet agreement indicates high-confidence assertions"
})

(:Project {id: "chrystallum_v1"})
  -[:MEASURED_BY]->
(:Metric {
  id: "source_diversity",
  label: "Average Sources Per Entity",
  current_value: "unknown",
  target: 3.0,
  rationale: "Multiple sources reduce single-source bias"
})
```

---

## Agent Decision Framework

When making architectural decisions, agents should:

### Priority 1: Does this enable evidence traceability?
- If YES → Prioritize
- If NO → Defer unless critical for operations

### Priority 2: Does this preserve semantic precision?
- If YES → Accept
- If NO (lossy merge/abstraction) → Reject or require strong justification

### Priority 3: Does this support competing narratives?
- If YES (e.g., CONFLICTS_WITH edges) → Prioritize
- If NO (forces single truth) → Reject

### Priority 4: Is this domain-agnostic or domain-specific?
- If domain-agnostic (core architecture) → Merge to main branch
- If domain-specific (e.g., Roman prosopography) → Keep in domain package

### Priority 5: Does this violate schema-first discipline?
- If YES (free-form writes) → REJECT immediately
- If NO (validated writes only) → Proceed

---

## Philosophical Touchstones

### Zhengming (Rectification of Names)
**Principle:** "If names are not correct, language will not be in accordance with the truth of things."

**Application:** Canonical relationship types must accurately reflect reality. "INVADED" vs "CROSSED" vs "CHALLENGED_AUTHORITY_OF" are not synonyms—each has distinct semantic content.

### Nanopublication Standards
**Principle:** "Assertions, provenance, and publication info are separate named graphs."

**Application:** Claim ciphers identify assertions. FacetPerspective nodes track provenance. CIDOC-CRM provides publication context.

### Actor-Centric History
**Principle:** "History is what people knew, believed, and did—not what we now know they should have done."

**Application:** IGAR forces temporal constraints. No "Caesar should have known the Senate would resist" without evidence Caesar had that information.

---

## Anti-Patterns (DO NOT)

❌ **Do not merge nodes to "simplify" if it loses query capability**
Example: Merging FATHER_OF and MOTHER_OF into PARENT_OF prevents patrilineal queries

❌ **Do not accept claims without source citations**
Example: "Caesar was ambitious" with no source → REJECT

❌ **Do not include provenance in claim cipher**
Example: Adding timestamp to cipher → same assertion by different agents creates duplicates

❌ **Do not create free-form relationship types**
Example: "led_a_battle" without registry entry → REJECT (use COMMANDED or PARTICIPATED_IN)

❌ **Do not force single-facet classification for multi-facet concepts**
Example: "Trial" requires INSTITUTIONAL + SOCIAL + POLITICAL perspectives

---

## Summary Query for Agent Orientation

```cypher
// Load project motivations
MATCH (p:Project {id: "chrystallum_v1"})-[r:HAS_MOTIVATION]->(m:Motivation)
RETURN m.label, m.description, r.priority, r.weight
ORDER BY r.priority

// Load guiding principles
MATCH (p:Project {id: "chrystallum_v1"})-[r:GUIDED_BY]->(pr:Principle)
RETURN pr.label, pr.rule, r.enforcement

// Load applicable domains
MATCH (p:Project {id: "chrystallum_v1"})-[r:APPLICABLE_TO]->(d:Domain)
RETURN d.label, d.value_proposition, r.maturity, r.implementation_status
```

**When in doubt, ask:**
- "Does this preserve evidence traceability?"
- "Does this enable competing narratives?"
- "Does this respect semantic precision?"
- "Would this work for legal/intelligence domains, or only history?"

If the answer is YES to all four, proceed. Otherwise, escalate for architectural review.