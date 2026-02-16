# Chrystallum Agent Use Case Matrix

This document defines the agent types, their roles, responsibilities, and interaction patterns within the Chrystallum knowledge graph system.

---

## Agent Architecture Overview

```cypher
// Agent type hierarchy
(:AgentClass {name: "Concierge Agent"})
  -[:COORDINATES]->
(:AgentClass {name: "Subject Facet Agent (SFA)"})
  -[:DELEGATES_TO]->
(:AgentClass {name: "Validation Agent"})

(:AgentClass {name: "Federation Agent"})
  -[:PROVIDES_DATA_TO]->
(:AgentClass {name: "Subject Facet Agent (SFA)"})
```

---

## Agent Type Matrix

| Agent Type | Count | Primary Role | Input | Output | Scope |
|------------|-------|--------------|-------|--------|-------|
| **Concierge Agent** | 1 | Query routing & orchestration | User query (natural language) | Routed subqueries + synthesized response | Entire system |
| **Subject Facet Agent (SFA)** | 17 | Domain-specific claim extraction | Parsed query + source documents | Validated claims in facet domain | Single facet (MILITARY, POLITICAL, etc.) |
| **Validation Agent** | 1 | Schema enforcement & confidence scoring | Raw claim structures | Validated/rejected claims with confidence | Cross-facet |
| **Federation Agent** | 5+ | External authority integration | Entity identifiers (QID, LCSH, etc.) | Enriched metadata + confidence bumps | Per-authority source |
| **Consensus Agent** | 1 | Multi-facet claim reconciliation | Multiple FacetPerspective nodes | Consensus claims or CONFLICTS_WITH edges | Cross-facet |
| **Query Agent** | 1 | Cypher generation & pattern matching | Structured queries | Neo4j results + provenance chains | Graph database |

---

## Detailed Agent Specifications

### 1. Concierge Agent (CCA)

**Role:** Front-door orchestrator and primary user interface

**Responsibilities:**
1. Parse incoming natural language queries
2. Classify query intent (entity lookup, relationship discovery, pattern analysis, theory testing)
3. Decompose complex queries into facet-specific subqueries
4. Route subqueries to appropriate SFAs based on LCSH backbone mapping
5. Aggregate multi-facet responses
6. Synthesize final user-facing answer with citations

**Input Schema:**
```json
{
  "query": "What military actions did Caesar take that challenged Republican institutions?",
  "user_context": {
    "session_id": "uuid",
    "prior_entities": ["Q1048"],  // Julius Caesar
    "active_facets": ["MILITARY", "POLITICAL"]
  }
}
```

**Output Schema:**
```json
{
  "routed_queries": [
    {"facet": "MILITARY", "sfa_id": "sfa_military", "subquery": "Caesar's military commands 50-44 BCE"},
    {"facet": "POLITICAL", "sfa_id": "sfa_political", "subquery": "Caesar's constitutional challenges"}
  ],
  "synthesis_strategy": "temporal_merge",  // or "comparison", "aggregation"
  "expected_node_types": ["Person", "Event", "Institution"]
}
```

**Decision Logic:**
```python
def route_query(query: str) -> List[SFAAssignment]:
    # Step 1: Extract subject concepts
    concepts = extract_subject_concepts(query)  # Returns LCSH IDs
    
    # Step 2: Map concepts to facets
    facets = []
    for concept in concepts:
        lcc_code = get_lcc_code(concept.authority_id)
        facets.extend(lcc_to_facet_mapping[lcc_code])
    
    # Step 3: Route to SFAs
    assignments = []
    for facet in set(facets):  # Deduplicate
        sfa = get_sfa_for_facet(facet)
        subquery = decompose_for_facet(query, facet)
        assignments.append(SFAAssignment(sfa, subquery, facet))
    
    return assignments
```

**Interaction Pattern:**
```mermaid
User Query → Concierge Agent
  ├→ SFA (MILITARY) → Claims
  ├→ SFA (POLITICAL) → Claims  
  └→ SFA (SOCIAL) → Claims
       ↓
Concierge Agent (aggregates) → User Response
```

---

### 2. Subject Facet Agent (SFA)

**Role:** Domain-specialized claim extractors with discipline-specific knowledge

**Canonical Set (17 agents):**
1. **SFA-ARCHAEOLOGICAL**: Material culture, excavations, artifact analysis
2. **SFA-ARTISTIC**: Visual arts, architecture, aesthetics
3. **SFA-CULTURAL**: Customs, traditions, cultural practices
4. **SFA-DEMOGRAPHIC**: Population, migration, census data
5. **SFA-DIPLOMATIC**: Treaties, embassies, international relations
6. **SFA-ECONOMIC**: Trade, currency, fiscal policy, resources
7. **SFA-ENVIRONMENTAL**: Climate, geography, natural resources
8. **SFA-GEOGRAPHIC**: Places, spatial relationships, territorial control
9. **SFA-INTELLECTUAL**: Philosophy, literature, education
10. **SFA-LINGUISTIC**: Languages, scripts, translation
11. **SFA-MILITARY**: Battles, commands, strategy, fortifications
12. **SFA-POLITICAL**: Governance, institutions, law, authority
13. **SFA-RELIGIOUS**: Cult, ritual, priesthood, temples
14. **SFA-SCIENTIFIC**: Technology, medicine, mathematics
15. **SFA-SOCIAL**: Class, family, gender, social structure
16. **SFA-TECHNOLOGICAL**: Engineering, innovation, tools
17. **SFA-COMMUNICATION**: Media, rhetoric, information transmission

**Responsibilities:**
1. Extract claims from source documents within facet domain
2. Apply IGAR framework to actor-related claims
3. Generate FacetPerspective nodes with confidence scores
4. Identify relationships using canonical relationship types from registry
5. Flag claims requiring multi-facet validation
6. Maintain facet-specific ontology extensions

**Input Schema:**
```json
{
  "subquery": "Identify Caesar's military commands during Gallic Wars",
  "facet_id": "MILITARY",
  "source_documents": [
    {
      "work_qid": "Q199762",  // De Bello Gallico
      "passages": [{"book": 1, "chapter": 7, "text": "..."}]
    }
  ],
  "target_entities": ["Q1048"],  // Caesar
  "temporal_scope": {"start": "-58", "end": "-50"}
}
```

**Output Schema:**
```json
{
  "claims": [
    {
      "claim_cipher": "sha256_hash_of_content",
      "subject_qid": "Q1048",
      "relationship_type": "COMMANDED",
      "object_qid": "Q3576110",  // Legio X Equestris
      "facet_perspective": {
        "facet_id": "MILITARY",
        "confidence": 0.92,
        "extractor_agent": "sfa_military_v1.2",
        "timestamp": "2026-02-16T23:30:00Z",
        "source_work_qid": "Q199762",
        "passage_locator": "Book 1, Ch. 7"
      },
      "requires_igar": true,
      "multi_facet_candidate": false
    }
  ],
  "proposed_entities": [],  // New entities requiring validation
  "relationship_ambiguities": []  // Cases needing human review
}
```

**IGAR Implementation:**
```python
class IGARChain:
    def extract_from_passage(self, actor_qid: str, passage: str) -> IGARStructure:
        return IGARStructure(
            input_nodes=self._extract_inputs(passage),      # What actor knew
            goal_nodes=self._extract_goals(passage),        # What actor wanted
            action_nodes=self._extract_actions(passage),    # What actor did
            result_nodes=self._extract_results(passage)     # What happened
        )
    
    def validate_temporal_consistency(self, igar: IGARStructure) -> bool:
        # Inputs must precede Actions
        for input_node in igar.input_nodes:
            for action_node in igar.action_nodes:
                if input_node.date > action_node.date:
                    raise PresentismError(f"Input {input_node} postdates Action {action_node}")
        return True
```

**Facet-Specific Knowledge:**

Each SFA maintains:
- **Domain ontology extensions**: Specialized node types (e.g., `MilitaryUnit`, `Battle`, `Siege`)
- **Relationship type preferences**: MILITARY favors `COMMANDED`, `BESIEGED`, `DEFEATED`
- **Confidence calibration**: Different standards for different claim types
- **Source authority ranking**: Which sources are most reliable for this domain

**Example: SFA-MILITARY**
```yaml
SFA-MILITARY:
  preferred_relationships:
    - COMMANDED
    - FOUGHT_AT
    - BESIEGED
    - ALLIED_WITH
    - DEFEATED
    - STRATEGIC_POSITION
  
  confidence_rules:
    - type: command_structure
      primary_sources: 0.85
      secondary_sources: 0.70
      inference: 0.60
    
    - type: battle_outcome
      primary_sources: 0.90
      archaeological: 0.80
      inference: 0.50
  
  federation_authorities:
    - Pleiades (geographic coordinates)
    - Trismegistos (unit identifications)
    - VIAF (commander identifications)
```

---

### 3. Validation Agent (VA)

**Role:** Schema enforcement and cross-facet consistency checking

**Responsibilities:**
1. Validate all claims against Pydantic schema definitions
2. Enforce Neo4j constraints before graph writes
3. Compute claim ciphers (content-only, excludes provenance)
4. Check for duplicate claims across facets
5. Apply confidence scoring rules
6. Flag claims requiring human review (confidence < 0.70)
7. Generate validation failure reports for schema evolution

**Input Schema:**
```json
{
  "claim": {
    "subject_qid": "Q1048",
    "relationship_type": "COMMANDED",
    "object_qid": "Q3576110",
    "source_work_qid": "Q199762",
    "passage_locator": "Book 1, Ch. 7",
    "passage_text_hash": "sha256_hash",
    "facet_id": "MILITARY",
    "confidence": 0.92
  },
  "validation_mode": "strict"  // or "permissive" for testing
}
```

**Output Schema:**
```json
{
  "validation_result": "PASS",  // or "FAIL", "WARN"
  "claim_cipher": "stable_content_hash",
  "duplicate_of": null,  // or existing claim_cipher if duplicate
  "confidence_adjusted": 0.92,  // After federation bumps
  "schema_violations": [],
  "warnings": [
    {
      "type": "low_confidence",
      "message": "Confidence 0.65 below review threshold 0.70",
      "recommendation": "FLAG_FOR_HUMAN_REVIEW"
    }
  ]
}
```

**Validation Pipeline:**
```python
class ValidationAgent:
    def validate_claim(self, claim: ClaimCandidate) -> ValidationResult:
        # Step 1: Schema validation
        try:
            validated = ClaimModel(**claim.dict())
        except ValidationError as e:
            return ValidationResult(status="FAIL", errors=[str(e)])
        
        # Step 2: Compute content-only cipher
        cipher = self.compute_cipher(
            subject=claim.subject_qid,
            relationship=claim.relationship_type,
            object=claim.object_qid,
            source=claim.source_work_qid,
            passage_hash=claim.passage_text_hash,
            temporal_scope=claim.temporal_scope,
            facet=claim.facet_id
        )
        
        # Step 3: Check for duplicates
        existing = self.graph.query(
            "MATCH (c:Claim {cipher: $cipher}) RETURN c",
            cipher=cipher
        )
        if existing:
            return ValidationResult(
                status="DUPLICATE",
                duplicate_of=cipher,
                action="MERGE_PERSPECTIVE"
            )
        
        # Step 4: Apply federation confidence bumps
        adjusted_confidence = self.apply_federation_bumps(claim)
        
        # Step 5: Check thresholds
        if adjusted_confidence < 0.70:
            return ValidationResult(
                status="WARN",
                flag="LOW_CONFIDENCE",
                requires_human_review=True
            )
        
        return ValidationResult(
            status="PASS",
            cipher=cipher,
            confidence=adjusted_confidence
        )
```

---

### 4. Federation Agent (FA)

**Role:** External authority integration and entity enrichment

**Agent Instances:**
1. **FA-WIKIDATA**: Primary entity resolution and property mapping
2. **FA-LCSH**: Subject concept authority and classification
3. **FA-PLEIADES**: Ancient place identification and coordinates
4. **FA-TRISMEGISTOS**: Prosopography and onomastics
5. **FA-PERIODO**: Temporal period standardization
6. **FA-EDH**: Epigraphic evidence integration
7. **FA-VIAF**: Author and person identification

**Responsibilities:**
1. Query external authority APIs
2. Map external identifiers to internal QIDs
3. Apply confidence bumps based on authority tier
4. Detect and resolve entity conflicts
5. Enrich claims with federated metadata
6. Track authority precedence (Tier 1 > Tier 2 > Tier 3)

**Input Schema:**
```json
{
  "entity_qid": "Q1048",  // Internal identifier
  "entity_type": "Person",
  "requested_properties": ["birth_date", "death_date", "coordinates"],
  "authority_preference": ["LCSH", "FAST", "Wikidata"],
  "confidence_floor": 0.85
}
```

**Output Schema:**
```json
{
  "enriched_properties": {
    "birth_date": {"value": "-100", "source": "Wikidata", "confidence": 0.88},
    "death_date": {"value": "-44-03-15", "source": "LCSH", "confidence": 0.95}
  },
  "federated_identifiers": {
    "wikidata_qid": "Q1048",
    "lcsh_id": "sh85020490",
    "viaf_id": "100227925",
    "trismegistos_id": "TM_12345"
  },
  "confidence_bump": 0.15,  // Applied to claims involving this entity
  "authority_tier": 1  // LCSH match found
}
```

**Authority Precedence Logic:**
```python
class FederationAgent:
    TIER_1 = ["LCSH", "FAST", "LCC"]  # Confidence floor: 0.95
    TIER_2 = ["CIP", "National Libraries"]  # Confidence floor: 0.90
    TIER_3 = ["Wikidata", "Pleiades", "Trismegistos"]  # Confidence floor: 0.85
    
    def resolve_entity(self, entity_qid: str) -> FederatedEntity:
        # Always check Tier 1 first
        for authority in self.TIER_1:
            result = self.query_authority(authority, entity_qid)
            if result:
                return FederatedEntity(
                    authority=authority,
                    tier=1,
                    confidence_floor=0.95,
                    confidence_bump=0.15,
                    data=result
                )
        
        # Fallback to Tier 2
        for authority in self.TIER_2:
            result = self.query_authority(authority, entity_qid)
            if result:
                return FederatedEntity(
                    authority=authority,
                    tier=2,
                    confidence_floor=0.90,
                    confidence_bump=0.10,
                    data=result
                )
        
        # Fallback to Tier 3
        for authority in self.TIER_3:
            result = self.query_authority(authority, entity_qid)
            if result:
                return FederatedEntity(
                    authority=authority,
                    tier=3,
                    confidence_floor=0.85,
                    confidence_bump=0.05,
                    data=result
                )
        
        # No federation match
        return None
```

**Confidence Bump Schedule:**
| Authority | Tier | Confidence Bump | Use Case |
|-----------|------|-----------------|----------|
| LCSH | 1 | +0.15 | Subject concept validation |
| FAST | 1 | +0.15 | Topical facet alignment |
| LCC | 1 | +0.15 | Classification verification |
| VIAF | 2 | +0.10 | Person identification |
| Wikidata | 3 | +0.05 | General entity enrichment |
| Pleiades | 3 | +0.12 | Ancient place coordinates |
| Trismegistos | 3 | +0.15 | Prosopographic match |
| EDH | 3 | +0.20 | Epigraphic primary evidence |
| PeriodO | 3 | +0.08 | Temporal period standardization |

---

### 5. Consensus Agent (CA)

**Role:** Multi-facet claim reconciliation and conflict resolution

**Responsibilities:**
1. Identify claims with multiple FacetPerspective nodes (2+)
2. Calculate consensus confidence scores
3. Detect conflicting claims across facets
4. Generate CONFLICTS_WITH edges with rationale
5. Propose "bridge concepts" for cross-facet entities
6. Flag claims requiring expert adjudication

**Input Schema:**
```json
{
  "claim_cipher": "stable_content_hash",
  "perspectives": [
    {
      "facet_id": "MILITARY",
      "confidence": 0.92,
      "extractor_agent": "sfa_military_v1.2",
      "timestamp": "2026-02-16T23:00:00Z"
    },
    {
      "facet_id": "POLITICAL",
      "confidence": 0.85,
      "extractor_agent": "sfa_political_v1.1",
      "timestamp": "2026-02-16T23:05:00Z"
    }
  ]
}
```

**Output Schema:**
```json
{
  "consensus_status": "AGREEMENT",  // or "CONFLICT", "PARTIAL"
  "consensus_confidence": 0.89,  // Weighted average
  "agreement_score": 0.95,  // Similarity between perspectives
  "conflicts": [],
  "recommended_action": "PROMOTE_TO_CONSENSUS",
  "bridge_concepts": [
    {
      "concept": "Trial",
      "facets": ["INSTITUTIONAL", "SOCIAL", "POLITICAL"],
      "reason": "Multi-facet entity requiring composite perspective"
    }
  ]
}
```

**Consensus Algorithm:**
```python
class ConsensusAgent:
    def reconcile_perspectives(self, perspectives: List[FacetPerspective]) -> ConsensusResult:
        if len(perspectives) < 2:
            return ConsensusResult(status="SINGLE_PERSPECTIVE", confidence=perspectives[0].confidence)
        
        # Calculate weighted consensus confidence
        total_weight = sum(p.confidence for p in perspectives)
        consensus_confidence = total_weight / len(perspectives)
        
        # Check for conflicts
        conflicts = []
        for i, p1 in enumerate(perspectives):
            for p2 in perspectives[i+1:]:
                if self.are_conflicting(p1, p2):
                    conflicts.append(Conflict(
                        perspective_1=p1,
                        perspective_2=p2,
                        conflict_type=self.classify_conflict(p1, p2),
                        resolution_strategy=self.suggest_resolution(p1, p2)
                    ))
        
        if conflicts:
            return ConsensusResult(
                status="CONFLICT",
                conflicts=conflicts,
                requires_adjudication=True
            )
        
        # Agreement: promote to consensus claim
        return ConsensusResult(
            status="AGREEMENT",
            consensus_confidence=consensus_confidence,
            agreement_score=self.calculate_agreement(perspectives),
            action="PROMOTE_TO_CONSENSUS"
        )
```

---

### 6. Query Agent (QA)

**Role:** Cypher generation and graph pattern matching

**Responsibilities:**
1. Convert natural language queries to Cypher
2. Generate optimized graph traversal patterns
3. Execute complex multi-hop queries
4. Return results with full provenance chains
5. Support pattern templates (e.g., "authoritarians arise when...")
6. Generate diff queries for claim version comparison

**Input Schema:**
```json
{
  "query_type": "pattern_match",  // or "entity_lookup", "relationship_discovery", "provenance_trace"
  "pattern": "Find all Person nodes where (:Person)-[:COMMANDED]->(:MilitaryUnit)-[:FOUGHT_AT]->(:Battle {outcome: 'victory'})",
  "filters": {
    "temporal_range": {"-60", "-44"},
    "facet_ids": ["MILITARY", "POLITICAL"],
    "min_confidence": 0.80
  },
  "return_fields": ["person.name", "battle.date", "unit.designation", "claim.confidence"]
}
```

**Output Schema:**
```json
{
  "cypher_query": "MATCH (p:Person)-[c1:COMMANDED]->(u:MilitaryUnit)-[c2:FOUGHT_AT]->(b:Battle {outcome: 'victory'}) WHERE ...",
  "results": [
    {
      "person.name": "Julius Caesar",
      "battle.date": "-52-09",
      "unit.designation": "Legio X Equestris",
      "claim.confidence": 0.92,
      "provenance_chain": [
        {"source_work_qid": "Q199762", "passage_locator": "Book 7, Ch. 50"},
        {"source_work_qid": "Q1396889", "passage_locator": "Life of Caesar, 25"}
      ]
    }
  ],
  "result_count": 1,
  "execution_time_ms": 45
}
```

**Pattern Template Library:**
```python
class QueryAgent:
    PATTERN_TEMPLATES = {
        "igar_chain": """
            MATCH (actor:Person {qid: $actor_qid})
            MATCH (actor)-[:HAS_INPUT]->(i:Input)
            MATCH (actor)-[:HAS_GOAL]->(g:Goal)
            MATCH (actor)-[:TOOK_ACTION]->(a:Action)
            MATCH (a)-[:RESULTED_IN]->(r:Result)
            WHERE i.date < a.date  // Temporal consistency
            RETURN actor, i, g, a, r
        """,
        
        "authoritarian_pattern": """
            MATCH (group:SocialGroup {status: 'formerly_powerful'})
            MATCH (change:Event {type: 'economic|social|political|religious'})
            MATCH (leader:Person)-[:PROMISES]->(restoration:Goal {type: 'dominance_restoration'})
            MATCH (leader)-[:FRAMES_AS]->(narrative:Narrative {type: 'betrayal_by_enemies'})
            MATCH (leader)-[:MINIMIZES]->(conditions:Condition)
            RETURN group, change, leader, narrative
        """,
        
        "provenance_trace": """
            MATCH (claim:Claim {cipher: $cipher})
            MATCH (claim)-[:EXTRACTED_FROM]->(passage:Passage)
            MATCH (passage)-[:PART_OF]->(work:Work)
            MATCH (work)-[:AUTHORED_BY]->(author:Person)
            MATCH (claim)<-[:ASSERTS]-(perspective:FacetPerspective)
            RETURN claim, passage, work, author, perspective
        """
    }
```

---

## Agent Interaction Patterns

### Pattern 1: Simple Entity Lookup
```mermaid
User: "Who was Julius Caesar?"
  ↓
Concierge Agent
  ↓
Query Agent → Neo4j
  ↓
Federation Agent (LCSH, Wikidata, VIAF)
  ↓
Concierge Agent → User Response
```

### Pattern 2: Multi-Facet Claim Extraction
```mermaid
User: "Analyze Caesar's crossing of the Rubicon"
  ↓
Concierge Agent
  ├→ SFA-MILITARY (military command)
  ├→ SFA-POLITICAL (constitutional violation)
  ├→ SFA-GEOGRAPHIC (river crossing location)
  └→ SFA-SOCIAL (public reaction)
       ↓
Validation Agent (schema check)
       ↓
Consensus Agent (multi-facet reconciliation)
       ↓
Concierge Agent → User Response with citations
```

### Pattern 3: Theory Testing with IGAR
```mermaid
User: "Test authoritarian pattern on Caesar"
  ↓
Concierge Agent
  ↓
Query Agent (load pattern template)
  ↓
SFA-POLITICAL (extract IGAR for Caesar)
  ├→ Input: Senate opposition, Gallic wealth
  ├→ Goal: Maintain political power
  ├→ Action: Cross Rubicon with legion
  └→ Result: Civil war, dictatorship
       ↓
Consensus Agent (compare to pattern)
       ↓
Concierge Agent → Theory fit analysis
```

### Pattern 4: Conflict Resolution
```mermaid
SFA-MILITARY: "Caesar commanded 10 legions"
SFA-POLITICAL: "Caesar commanded 8 legions"
  ↓
Validation Agent (same cipher, different claims)
  ↓
Consensus Agent
  ├→ Check sources
  ├→ Check temporal context
  └→ Create CONFLICTS_WITH edge
       ↓
Flag for human adjudication
```

---

## Agent Communication Protocol

### Message Schema
```json
{
  "message_id": "uuid",
  "sender_agent": "sfa_military_v1.2",
  "receiver_agent": "validation_agent_v1.0",
  "message_type": "CLAIM_SUBMISSION",
  "timestamp": "2026-02-16T23:30:00Z",
  "payload": {
    "claim": {...},
    "context": {...}
  },
  "requires_response": true,
  "timeout_ms": 5000
}
```

### Message Types
| Message Type | Sender | Receiver | Purpose |
|--------------|--------|----------|----------|
| `QUERY_ROUTE` | Concierge | SFA | Route subquery to facet agent |
| `CLAIM_SUBMISSION` | SFA | Validation | Submit claim for validation |
| `VALIDATION_RESULT` | Validation | SFA | Return validation outcome |
| `FEDERATION_REQUEST` | Validation | Federation | Request entity enrichment |
| `CONSENSUS_REQUEST` | Validation | Consensus | Request multi-facet reconciliation |
| `CONFLICT_ALERT` | Consensus | Concierge | Flag conflicting claims |
| `QUERY_EXECUTION` | Concierge | Query | Execute Cypher query |
| `ADJUDICATION_REQUIRED` | Any | Human | Escalate for expert review |

---

## Agent Metrics & Monitoring

### Per-Agent Metrics
```python
class AgentMetrics:
    agent_id: str
    
    # Performance
    average_response_time_ms: float
    total_requests_processed: int
    error_rate: float
    
    # Quality (for SFAs)
    claims_submitted: int
    claims_validated: int
    claims_rejected: int
    average_confidence: float
    
    # Efficiency
    duplicate_submissions: int  # Should be low
    schema_violations: int  # Should be low
    human_adjudications: int  # Should be minimized
```

### System-Wide Metrics
```python
class SystemMetrics:
    # Throughput
    queries_per_hour: float
    claims_per_hour: float
    
    # Quality
    multi_facet_consensus_rate: float  # Target: 0.40
    conflict_rate: float  # Should be < 0.10
    average_claim_confidence: float  # Target: 0.85+
    
    # Coverage
    entities_with_federation: float  # Target: 0.90+
    claims_with_multiple_sources: float  # Target: 0.60+
    facets_per_entity: float  # Target: 2.5+
```

---

## Agent Evolution & Versioning

### Version Control
All agents are versioned using semantic versioning: `v{major}.{minor}.{patch}`

Example: `sfa_military_v1.2.3`
- Major: Breaking changes to input/output schema
- Minor: New capabilities or improved algorithms
- Patch: Bug fixes

### Upgrade Strategy
```python
class AgentUpgrade:
    def migrate_agent(self, old_version: str, new_version: str):
        # Step 1: Deploy new version alongside old
        deploy_parallel(new_version)
        
        # Step 2: Route 10% traffic to new version
        canary_test(new_version, traffic_percent=0.10)
        
        # Step 3: Compare metrics
        metrics = compare_performance(old_version, new_version)
        
        # Step 4: Full rollout if metrics improve
        if metrics.new_version_better():
            full_rollout(new_version)
            retire(old_version)
        else:
            rollback(new_version)
```

---

## Use Case Examples

### Use Case 1: Historical Research Query
**Query:** "What were Caesar's political motivations for crossing the Rubicon?"

**Agent Flow:**
1. **Concierge Agent**: Parses query, identifies facets: POLITICAL, MILITARY
2. **SFA-POLITICAL**: Extracts IGAR chain:
   - Input: Senate opposition, threat of prosecution
   - Goal: Preserve political power and dignitas
   - Action: Cross Rubicon with legion
   - Result: Initiate civil war
3. **SFA-MILITARY**: Extracts military context:
   - Commanded Legio XIII
   - Strategic advantage of swift action
4. **Validation Agent**: Validates claims, applies confidence scores
5. **Federation Agent**: Enriches with Wikidata, LCSH identifiers
6. **Consensus Agent**: Reconciles POLITICAL + MILITARY perspectives
7. **Concierge Agent**: Synthesizes response with citations

**Response:**
> "Caesar crossed the Rubicon primarily to preserve his political standing. According to Suetonius (Life of Caesar, 31), he faced prosecution if he returned to Rome without his military command. His Input (threat of prosecution) led to the Goal (preserve dignitas and avoid prosecution), resulting in the Action (illegal river crossing with Legio XIII) and the Result (civil war and eventual dictatorship). This interpretation is supported by both political analysis (confidence: 0.88) and military context (confidence: 0.92), with consensus confidence of 0.90."

### Use Case 2: Legal Case Law Analysis
**Query:** "Find precedents where prosecution timing affected trial outcomes"

**Agent Flow:**
1. **Concierge Agent**: Routes to INSTITUTIONAL facet (legal domain)
2. **SFA-INSTITUTIONAL**: Searches for (:Trial)-[:PRECEDED_BY]->(:Prosecution) patterns
3. **Query Agent**: Generates Cypher for temporal analysis
4. **Validation Agent**: Filters for confidence > 0.80
5. **Concierge Agent**: Returns ranked precedents with citations

### Use Case 3: Intelligence Pattern Recognition
**Query:** "Identify instances matching authoritarian rise pattern"

**Agent Flow:**
1. **Concierge Agent**: Loads pattern template
2. **Query Agent**: Executes pattern match across historical cases
3. **Multiple SFAs**: Extract IGAR for key actors in each case
4. **Consensus Agent**: Scores pattern fit for each case
5. **Concierge Agent**: Returns ranked cases with mechanism graphs

---

## Summary: Agent Responsibilities at a Glance

| Responsibility | Concierge | SFA | Validation | Federation | Consensus | Query |
|----------------|-----------|-----|------------|------------|-----------|-------|
| **Parse user queries** | ✓ | | | | | |
| **Route to facets** | ✓ | | | | | |
| **Extract claims** | | ✓ | | | | |
| **Apply IGAR** | | ✓ | | | | |
| **Validate schema** | | | ✓ | | | |
| **Compute ciphers** | | | ✓ | | | |
| **Enrich entities** | | | | ✓ | | |
| **Check duplicates** | | | ✓ | | | |
| **Reconcile perspectives** | | | | | ✓ | |
| **Generate Cypher** | | | | | | ✓ |
| **Execute queries** | | | | | | ✓ |
| **Synthesize responses** | ✓ | | | | | |
| **Handle conflicts** | | | | | ✓ | |

---

## Next Steps

1. **Implement Concierge Agent** with LangGraph routing logic
2. **Deploy first 3 SFAs** (MILITARY, POLITICAL, GEOGRAPHIC) as proof of concept
3. **Build Validation Agent** with Pydantic schema enforcement
4. **Integrate Federation Agents** for LCSH, Wikidata, Pleiades
5. **Test end-to-end flow** with Roman Republic test case (Q17167)
6. **Scale to remaining 14 SFAs** based on domain priority