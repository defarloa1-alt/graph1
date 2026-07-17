# ADR 022: Multi-Agent Canonical Entity Claims Architecture

**Status:** Proposed  
**Date:** 2026-07-16  
**Authors:** Chrystallum Architecture Team  
**Reviewers:** Perplexity AI Advisory  

## Context

### The Fragmentation Problem

When multiple Specialized Facet Agents (SFAs) independently process knowledge from their domain perspective, they frequently encounter the **same real-world entities**:

- Military SFA and Bio SFA both discover "Caesar crossing the Rubicon" (Event)
- Political SFA and Economic SFA both analyze "land reform" (Concept)
- Geographic SFA and Military SFA both reference "the Rubicon" (Place)
- Temporal SFA and Bio SFA both scope "Late Roman Republic" (Period)

**Current risk:** Without coordination, each SFA creates its own node, leading to entity duplication and fragmentation. The graph loses coherence.

**Core question:** Should we **deduplicate to a single canonical entity** or **preserve multiple SFA-owned versions as distinct nodes**?

## Decision

We adopt the **Canonical Entity + Facet-Scoped Claims** architecture pattern, based on:

1. **Blackboard Architecture** (1970s AI multi-agent pattern, validated in modern LLM systems)
2. **CIDOC-CRM Event Model** (museum/cultural heritage standard)
3. **PROV-O Provenance** (W3C RDF standard for claim attribution)
4. **Wikidata Multi-Source Claims** (production knowledge graph pattern)

### Core Principles

#### Principle 1: Entity Canonicalization

**One real-world entity = One canonical node in the graph.**

- `(:Event)` — Caesar crossing Rubicon (Q40979)
- `(:Concept)` — Land reform
- `(:Place)` — Rome (Q220)
- `(:Period)` — Late Roman Republic
- `(:Person)` — Julius Caesar (Q1048)
- `(:Work)` — De Bello Gallico (Q214304)

**Entity ownership:** The graph owns the canonical entity node. SFAs **do not own entities**; they own **claims about entities**.

#### Principle 2: Facet-Scoped Claims

**SFAs assert interpretations, not facts.**

Each SFA writes `:ASSERTS` edges from their agent node to the canonical entity, carrying facet-specific metadata:

```cypher
(military_sfa:Agent {facet: 'MILITARY'})-[:ASSERTS {
  facet: 'MILITARY',
  agent_id: 'military_sfa_001',
  predicate: 'military_escalation',
  confidence: 0.90,
  source_qid: 'Q123456',
  submitted_at: timestamp(),
  status: 'CONFIRMED'
}]->(rubicon:Event {qid: 'Q40979'})

(bio_sfa:Agent {facet: 'BIOGRAPHIC'})-[:ASSERTS {
  facet: 'BIOGRAPHIC',
  agent_id: 'bio_sfa_001',
  predicate: 'career_defining_act',
  confidence: 0.95,
  source_qid: 'Q789012',
  submitted_at: timestamp(),
  status: 'CONFIRMED'
}]->(rubicon:Event {qid: 'Q40979'})
```

Both claims are **valid and complementary**. The military interpretation and biographical interpretation are **different perspectives on the same entity**.

#### Principle 3: Blackboard Coordination

**The Neo4j graph is the shared "blackboard."** All SFAs:
- Read from the blackboard
- Write to the blackboard through a **Claim Registry** (control shell)
- **Never communicate directly with each other**

The Claim Registry:
1. Checks for existing canonical entities before allowing writes
2. Enforces entity deduplication via entity cipher lookups
3. Routes claims to canonical nodes
4. Manages claim lifecycle (TBD → CONFIRMED → CONTESTED)

#### Principle 4: Two-Phase SFA Processing

| Phase | Function | Description |
|-------|----------|-------------|
| **Phase 1: Knowledge Acquisition** | Submit claims | SFA processes source material, identifies entities, submits `:ASSERTS` claims with `status: 'TBD'` |
| **Phase 2: Peer Review** | Review peer claims | SFA reads claims from other facets on shared entities, writes `:REVIEWED` edges, updates claim status |

Phase 2 implements the **Blackboard Consensus Loop**: iterative peer review directly on the graph reduces hallucination and establishes cross-facet validation.

**Scope note (2026-07-16):** Atomic participation claims (`claim_layer=atomic_participation`, Q–P–Q) use the blackboard as **shared state** only (read entities; write Claims via registry/gates). They do **not** require Phase-2 peer `:REVIEWED` consensus. Interpretation claims (IGAR) do. Binding rules: `docs/FACET_TRAINING_CONTRACT.md`.

### Claim Lifecycle (Predicate Status)

Claims progress through a formal lifecycle:

| Status | Meaning | Transition Condition |
|--------|---------|---------------------|
| `TBD` | SFA submitted claim, predicate not yet validated | Initial state |
| `PROPOSED` | SFA has candidate predicate, awaiting cross-facet review | SFA confidence ≥ 0.70 |
| `CONFIRMED` | Multiple facets agree on predicate interpretation | N facets reviewed, threshold agreement met |
| `CONTESTED` | Facets disagree on predicate or interpretation | N facets reviewed, consensus failed |
| `DEPRECATED` | Claim superseded by better evidence | Manual or automated review |

**Key insight:** Disagreement is **not an error** — it is **data**. `CONTESTED` claims signal areas requiring human scholarly judgment or further investigation.

### Entity Resolution Pipeline

Before creating any entity node, the Claim Registry executes:

```cypher
// 1. Check for existing canonical entity
MATCH (e:Event)
WHERE e.qid = $wikidata_qid 
   OR e.entity_cipher = $computed_cipher
RETURN e

// If found: use existing node
// If not found: create canonical node with entity cipher
```

**Resolution priority:**
1. Wikidata QID (if available) — highest authority
2. Entity cipher (computed from content hash) — for entities without QIDs
3. Fuzzy matching on name + date + context (last resort, requires human review)

### Claim Metadata Schema

Every `:ASSERTS` relationship carries provenance:

```cypher
{
  facet: 'MILITARY' | 'BIOGRAPHIC' | ...,  // Which SFA made this claim
  agent_id: 'military_sfa_001',            // Specific agent instance
  predicate: 'military_escalation',        // Semantic interpretation
  confidence: 0.90,                        // Agent's confidence score [0.0-1.0]
  source_qid: 'Q123456',                   // Wikidata source for evidence
  source_uri: 'https://...',               // External source URI
  submitted_at: timestamp(),               // When claim was submitted
  reviewed_at: timestamp(),                // When last reviewed
  status: 'TBD' | 'PROPOSED' | 'CONFIRMED' | 'CONTESTED' | 'DEPRECATED',
  review_count: 3,                         // Number of peer reviews
  agreement_score: 0.87                    // Cross-facet consensus score
}
```

## Consequences

### Positive

1. **Eliminates Entity Fragmentation**: One canonical node per real-world entity
2. **Preserves Facet Perspectives**: Each SFA's interpretation is retained with full provenance
3. **Enables Cross-Facet Queries**: "Show me all claims about Caesar from all facets"
4. **Treats Disagreement as Signal**: Contested claims identify scholarly research opportunities
5. **Scales to 18 Facets**: Pattern works uniformly across all facets
6. **Maps to Existing Standards**: CIDOC-CRM, PROV-O, Wikidata patterns
7. **Supports Incremental Training**: Claims can be refined as SFAs improve

### Negative

1. **Increased Complexity**: Requires Claim Registry coordination layer
2. **Processing Latency**: Two-phase processing adds round-trip time
3. **Entity Resolution Overhead**: Pre-write checks add query cost
4. **Consensus Threshold Tuning**: Requires empirical calibration
5. **Human Review Required**: Contested claims need manual resolution
6. **Schema Migration**: Existing data must be retrofitted to claim pattern

### Neutral

1. **Storage Cost**: More edges (N_facets × N_entities claims), but metadata is lightweight
2. **Query Patterns Change**: Need to traverse through `:ASSERTS` edges to get facet-specific views

## Rejected Alternatives

### Alternative 1: SFA Entity Ownership

**Pattern:** Each SFA owns its entities. Military SFA owns military_rubicon_crossing, Bio SFA owns bio_rubicon_crossing.

**Rejected because:**
- Creates unresolvable duplication
- Cannot answer queries like "What do all facets say about the Rubicon?"
- Loses graph coherence
- Contradicts canonical entity principle

### Alternative 2: Single Unified Agent

**Pattern:** One omniscient agent processes all facets, writes single unified claims.

**Rejected because:**
- Loses facet-specific resolution and expertise
- Cannot track provenance per domain
- Contradicts multi-agent architecture goal
- Eliminates peer review benefits

### Alternative 3: Master-Slave Agent Hierarchy

**Pattern:** One master SFA coordinates, slave SFAs report findings, master decides truth.

**Rejected because:**
- Bottlenecks on master agent
- Loses distributed resilience
- Master becomes single point of failure
- Contradicts Blackboard peer architecture

## Implementation Roadmap

### Phase 0: Prerequisites (Current Sprint)

**Deliverables:**
1. ✅ **Extend Entity Cipher to Events** (see ADR 023)
2. ✅ **Define Claim Metadata Schema** (documented above)
3. **Update `entity_cipher.py`** to support Event cipher generation

**Acceptance Criteria:**
- Event cipher format: `ent_evt_<QID>` or `ent_evt_<content_hash>`
- Cipher generation works for events without QIDs
- Unit tests pass for event deduplication

### Phase 1: Foundation (Sprint +1)

**Deliverables:**
1. **Claim Registry Service** (`scripts/agents/claim_registry.py`)
   - Entity deduplication logic
   - Pre-write canonical entity checks
   - Claim metadata validation
2. **Cypher Schema Updates**
   - Add `:ASSERTS` relationship type
   - Add `:REVIEWED` relationship type
   - Add claim metadata properties
   - Create indexes on entity_cipher, qid, facet
3. **Claim Submission API**
   - SFAs call `claim_registry.submit_claim(entity, predicate, facet, confidence)`
   - Registry handles deduplication + routing

**Acceptance Criteria:**
- No duplicate entity nodes created when multiple SFAs submit same entity
- All claims carry full provenance metadata
- Claim status defaults to 'TBD'

### Phase 2: Coordination (Sprint +2)

**Deliverables:**
1. **Control Shell** (`scripts/agents/control_shell.py`)
   - SFA lifecycle management
   - Phase 1 → Phase 2 transition orchestration
   - Claim promotion rules engine
2. **Phase 2 Review Workflow**
   - SFAs query peer claims: `MATCH (e)<-[:ASSERTS {status: 'PROPOSED'}]-(other_sfa)`
   - SFAs write `:REVIEWED` edges with agreement/disagreement
3. **Promotion Rules Engine**
   - Configurable consensus thresholds
   - TBD → PROPOSED (confidence ≥ 0.70)
   - PROPOSED → CONFIRMED (agreement_score ≥ 0.80, review_count ≥ 3)
   - PROPOSED → CONTESTED (agreement_score < 0.50, review_count ≥ 3)

**Acceptance Criteria:**
- SFAs successfully review peer claims
- Claim status updates automatically based on rules
- Contested claims flagged for human review

### Phase 3: Scale (Sprint +3+)

**Deliverables:**
1. **Conflict Resolution UI**
   - Human review interface for contested claims
   - Side-by-side facet comparison
   - Manual promotion/deprecation controls
2. **Cross-Facet Analytics**
   - Query: "All claims about X from all facets"
   - Query: "Find entities with most contested claims"
   - Query: "Which facets agree most often?"
3. **Confidence Calibration**
   - Track SFA accuracy over time
   - Auto-adjust confidence scores based on historical agreement
   - Identify facets needing retraining

**Acceptance Criteria:**
- Human reviewers can resolve contested claims in <2 min
- Cross-facet query performance acceptable (<500ms)
- SFA confidence scores correlate with actual agreement rates

## Monitoring and Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Deduplication Rate** | >95% | % of entities correctly deduplicated on first encounter |
| **Claim Promotion Rate** | >70% TBD→CONFIRMED | % of claims that reach CONFIRMED status |
| **Contested Claim Rate** | <10% | % of claims flagged as CONTESTED |
| **Cross-Facet Agreement** | >80% | Average agreement_score across all claims |
| **Human Review Backlog** | <100 claims | Number of contested claims awaiting review |
| **Phase 2 Latency** | <30s | Time for claim to progress TBD → CONFIRMED |

## References

1. **Blackboard Architecture** - Rajat Pandit, "The Blackboard Architecture in Agentic AI" (2024)
2. **CIDOC-CRM E5 Event** - OntoME Ontology Registry
3. **PROV-O Provenance** - W3C RDF Provenance Standard
4. **Wikidata Claims Model** - Wikidata Data Model Documentation
5. **Google Blackboard Research** - "Blackboard Multi-Agent Systems for Information Discovery in Data Science" (Research Paper)
6. **Neo4j Multi-Agent Memory** - NODES AI 2026 Session (YouTube)

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-16 | 0.1 | Initial draft based on Perplexity advisory |

## Appendices

### Appendix A: Example Cypher Queries

**Submit a claim (Phase 1):**
```cypher
// SFA submits claim about Rubicon crossing
MERGE (e:Event {entity_cipher: 'ent_evt_Q40979', qid: 'Q40979'})
  ON CREATE SET 
    e.label = 'Caesar crossing the Rubicon',
    e.date = '-49-01-10',
    e.cidoc_class = 'E5_Event'

MERGE (sfa:Agent {agent_id: 'military_sfa_001', facet: 'MILITARY'})

CREATE (sfa)-[:ASSERTS {
  facet: 'MILITARY',
  predicate: 'military_escalation',
  confidence: 0.90,
  source_qid: 'Q123456',
  submitted_at: timestamp(),
  status: 'TBD'
}]->(e)
```

**Review peer claim (Phase 2):**
```cypher
// Military SFA reviews Bio SFA's claim on same event
MATCH (bio_sfa:Agent {facet: 'BIOGRAPHIC'})-[claim:ASSERTS]->(e:Event {qid: 'Q40979'})
MATCH (mil_sfa:Agent {agent_id: 'military_sfa_001'})

CREATE (mil_sfa)-[:REVIEWED {
  agrees: true,
  note: 'Confirms military significance',
  timestamp: timestamp()
}]->(claim)

// Update claim status if consensus threshold met
WITH claim
MATCH (e)<-[c:ASSERTS]-(a)
WITH c, count(DISTINCT a.facet) as facet_count
WHERE facet_count >= 3
SET c.status = 'CONFIRMED'
```

**Query all facet perspectives on an entity:**
```cypher
MATCH (e:Event {qid: 'Q40979'})<-[claim:ASSERTS]-(sfa:Agent)
RETURN 
  e.label as entity,
  sfa.facet as perspective,
  claim.predicate as interpretation,
  claim.confidence as confidence,
  claim.status as status
ORDER BY claim.confidence DESC
```

### Appendix B: Entity Cipher Extension

See **ADR 023: Event Entity Cipher Specification** for complete details on extending the 3-tier cipher system to support Events and other entity types.
