# Agent Architecture, Persistence, and Ontology Creation: Complete Technical Guide

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [5W1H Foundation Principle](#5w1h-foundation-principle)
3. [Minimal Protocol YAML Templates](#minimal-protocol-yaml-templates)
4. [Agent Architecture: Stateless Shells](#agent-architecture-stateless-shells)
5. [Persistence Model: Graph as Source of Truth](#persistence-model-graph-as-source-of-truth)
6. [Dynamic Ontology Evolution](#dynamic-ontology-evolution)
7. [Canonical Math Mapped to 5W1H](#canonical-math-mapped-to-5w1h)
8. [Storage Scaling and Compression](#storage-scaling-and-compression)
9. [Implementation Examples](#implementation-examples)

---

## Executive Summary

This document defines the complete architecture for **agent-based knowledge graph systems** using Chrystallum's mathematical framework. The key innovations are:

1. **5W1H as Universal Foundation** - All knowledge modeling reduces to Who, What, When, Where, Why, How
2. **Minimal Seeding Protocol** - Define only base types/relations, agents extend dynamically
3. **Stateless Agent Shells** - Agents are API wrappers that persist everything to graph
4. **Graph-Based Persistence** - Neo4j (or similar) is the single source of truth
5. **Dynamic Schema Evolution** - Ontology grows as agents discover new relationships
6. **Canonical Math Enforcement** - Pressure fields minimize 5W1H gaps
7. **Storage Optimization** - Strategies for enterprise-scale deployment

---

## 5W1H Foundation Principle

### Core Insight

Every piece of knowledge—whether historical fact, software requirement, or architectural decision—can be decomposed into six fundamental questions:

| Dimension | Meaning | Graph Representation |
|-----------|---------|---------------------|
| **Who** | Agent, source, actor, stakeholder | Node property: `agent_id`, `provenance`; Edge: `CREATED_BY`, `SUPPORTED_BY` |
| **What** | Claim, event, entity, action | Node type, `label`, `description` |
| **When** | Time, date, sequence, version | Property: `timestamp`, `event_date`, `version`; Edge: `BEFORE`, `AFTER` |
| **Where** | Location, context, scope, domain | Property: `location`, `qid`, `project_id`; Edge: `OCCURRED_AT`, `PART_OF` |
| **Why** | Purpose, rationale, evidence, motivation | Property: `rationale`; Edge: `EVIDENCE_FOR`, `JUSTIFIED_BY`, `MOTIVATED_BY` |
| **How** | Method, mechanism, implementation | Property: `method`, `tool`; Edge: `IMPLEMENTED_BY`, `USES_TECHNIQUE` |

### Universal Applicability

**Historical Research Example:**
- **What**: "Caesar crossed the Rubicon"
- **Who**: Julius Caesar (Q1048), Agent: `agent_caesar_bio`
- **When**: January 10, 49 BCE
- **Where**: Rubicon River (Q2253)
- **Why**: To prevent prosecution by Senate
- **How**: Led legion across river boundary

**SDLC Example:**
- **What**: "Implement password reset feature"
- **Who**: Dev Team A, Architect: Sarah
- **When**: Sprint 23, Q1 2025
- **Where**: Auth Service module
- **Why**: Reduce support tickets by 30%
- **How**: JWT tokens, email service, 24-hour expiry

### Why This Works

1. **Human-Intuitive** - Everyone understands these questions
2. **Machine-Parseable** - Clear structure for LLMs to extract/generate
3. **Universally Applicable** - Works across all domains (history, SDLC, medicine, law)
4. **Completeness Metric** - Missing 5W1H = higher pressure (math penalty)
5. **Extensible** - Can add sub-dimensions (e.g., "How confident?" under Why)

---

## Minimal Protocol YAML Templates

### Base Schema (Domain-Agnostic)

```yaml
# base-ontology.yaml
# Minimal protocol that ALL domains must implement

version: "1.0"
description: "5W1H-based minimal ontology for Chrystallum knowledge graphs"

core_node_types:
  Event:
    description: "Something that happened or will happen"
    required_properties:
      - what: {type: string, description: "Event label/title"}
      - when: {type: datetime, description: "Timestamp or date"}
      - who: {type: string, description: "Agent or actor responsible"}
    optional_properties:
      - where: {type: string, description: "Location or context"}
      - why: {type: string, description: "Purpose or rationale"}
      - how: {type: string, description: "Method or mechanism"}
      - qid: {type: string, description: "Wikidata QID for semantic linking"}
      - confidence: {type: float, min: 0.0, max: 1.0, default: 0.7}
      - version: {type: integer, default: 1}

  Claim:
    description: "An assertion about a fact or relationship"
    required_properties:
      - what: {type: string, description: "Claim statement"}
      - who: {type: string, description: "Agent making claim"}
      - when: {type: datetime, description: "When claim was made"}
    optional_properties:
      - where: {type: string, description: "Scope or context"}
      - why: {type: string, description: "Evidence or rationale"}
      - how: {type: string, description: "Method of derivation"}
      - confidence: {type: float, min: 0.0, max: 1.0}
      - provenance: {type: string, description: "Source or citation"}

  Source:
    description: "Evidence or reference material"
    required_properties:
      - what: {type: string, description: "Source title"}
      - who: {type: string, description: "Author or publisher"}
    optional_properties:
      - when: {type: string, description: "Publication date"}
      - where: {type: string, description: "Location or URL"}
      - how: {type: string, enum: [book, article, video, inscription, dataset]}

  Agent:
    description: "Human or AI agent acting in the system"
    required_properties:
      - what: {type: string, description: "Agent identifier"}
      - who: {type: string, description: "Owner or creator"}
      - when: {type: datetime, description: "Creation timestamp"}
    optional_properties:
      - where: {type: string, description: "Domain or scope"}
      - why: {type: string, description: "Purpose or specialization"}
      - how: {type: string, description: "Implementation (LLM, script, human)"}
      - status: {type: string, enum: [active, dormant, archived]}

core_edge_types:
  SUPPORTS:
    from: [Claim, Source]
    to: [Claim]
    description: "Provides evidence for a claim"
    properties:
      - confidence: {type: float, min: 0.0, max: 1.0}
      - who: {type: string, description: "Agent creating this relationship"}
      - when: {type: datetime}

  CONTRADICTS:
    from: [Claim]
    to: [Claim]
    description: "Conflicts with another claim"
    properties:
      - confidence: {type: float, min: 0.0, max: 1.0}
      - who: {type: string}
      - when: {type: datetime}
      - why: {type: string, description: "Explanation of contradiction"}

  EVIDENCE_FOR:
    from: [Source]
    to: [Claim, Event]
    description: "Source provides evidence"
    properties:
      - who: {type: string}
      - when: {type: datetime}
      - how: {type: string, description: "How evidence was extracted"}

  CREATED_BY:
    from: [Event, Claim, Source]
    to: [Agent]
    description: "Agent that created this node"
    properties:
      - when: {type: datetime}

  OCCURRED_AT:
    from: [Event]
    to: [Location, Context]
    description: "Where event took place"
    properties:
      - when: {type: datetime, description: "When this location was determined"}

constraints:
  - name: no_orphan_claims
    description: "Every Claim must link to at least one Event or Source"
    cypher: "MATCH (c:Claim) WHERE NOT (c)-[:EVIDENCE_FOR|:SUPPORTS]->() RETURN count(c) = 0"

  - name: all_nodes_have_creator
    description: "Every node (except Agent) must have CREATED_BY edge"
    cypher: "MATCH (n) WHERE NOT n:Agent AND NOT (n)-[:CREATED_BY]->(:Agent) RETURN count(n) = 0"

  - name: timestamps_required
    description: "All nodes must have 'when' property"
    cypher: "MATCH (n) WHERE n.when IS NULL RETURN count(n) = 0"

completeness_metrics:
  minimal: ["what", "who", "when"]  # Must have these
  good: ["what", "who", "when", "where"]  # Should have these
  excellent: ["what", "who", "when", "where", "why", "how"]  # Ideal
```

### Domain Extension: Historical Research

```yaml
# domain-history.yaml
# Extension of base ontology for historical research

extends: base-ontology.yaml

domain_node_types:
  HistoricalEvent:
    extends: Event
    additional_properties:
      - period: {type: string, description: "Historical period (e.g., 'Roman Republic')"}
      - calendar: {type: string, enum: [Julian, Gregorian, Islamic, Chinese]}
      - uncertainty: {type: string, enum: [certain, probable, possible, disputed]}

  DateClaim:
    extends: Claim
    additional_properties:
      - date_value: {type: string, description: "Precise date (ISO 8601 or BCE/CE)"}
      - calendar: {type: string, enum: [Julian, Gregorian]}
      - precision: {type: string, enum: [year, month, day, hour]}

  PrimarySources:
    extends: Source
    additional_properties:
      - language: {type: string, description: "Original language"}
      - translation: {type: string, description: "Translator if applicable"}
      - manuscript: {type: string, description: "Manuscript identifier"}

domain_edge_types:
  REFINES:
    from: [DateClaim]
    to: [DateClaim]
    description: "More precise date refines broader date"
    properties:
      - precision_gain: {type: string}

  CONTEMPORARY_WITH:
    from: [HistoricalEvent]
    to: [HistoricalEvent]
    description: "Events occurred in same time period"

  CAUSED:
    from: [HistoricalEvent]
    to: [HistoricalEvent]
    description: "Causal relationship between events"
    properties:
      - causality_type: {type: string, enum: [direct, indirect, contributing]}
```

### Domain Extension: SDLC/Software Engineering

```yaml
# domain-sdlc.yaml
# Extension for software development lifecycle

extends: base-ontology.yaml

domain_node_types:
  Requirement:
    extends: Claim
    additional_properties:
      - requirement_id: {type: string, description: "Unique ID (e.g., REQ-001)"}
      - priority: {type: string, enum: [critical, high, medium, low]}
      - status: {type: string, enum: [proposed, approved, implemented, verified, rejected]}
      - acceptance_criteria: {type: array, items: string}

  Architecture:
    extends: Event
    additional_properties:
      - architecture_type: {type: string, enum: [system, component, deployment]}
      - technology_stack: {type: array, items: string}
      - adr_id: {type: string, description: "Architecture Decision Record ID"}

  Code:
    extends: Event
    additional_properties:
      - file_path: {type: string}
      - language: {type: string}
      - lines_of_code: {type: integer}
      - test_coverage: {type: float, min: 0.0, max: 1.0}
      - git_commit: {type: string}

  TestCase:
    extends: Claim
    additional_properties:
      - test_id: {type: string}
      - test_type: {type: string, enum: [unit, integration, e2e, performance]}
      - status: {type: string, enum: [passed, failed, skipped, blocked]}

domain_edge_types:
  SATISFIES:
    from: [Architecture, Code]
    to: [Requirement]
    description: "Implementation satisfies requirement"

  IMPLEMENTS:
    from: [Code]
    to: [Architecture]
    description: "Code implements architectural design"

  VERIFIES:
    from: [TestCase]
    to: [Requirement, Code]
    description: "Test verifies implementation"

  DEPENDS_ON:
    from: [Requirement, Architecture, Code]
    to: [Requirement, Architecture, Code]
    description: "Dependency relationship"
    properties:
      - dependency_type: {type: string, enum: [required, optional, breaking]}
```

---

## Agent Architecture: Stateless Shells

### Core Principle

**Agents have no persistent internal state.** All state is externalized to the knowledge graph.

### Agent as API Wrapper

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import yaml

class AgentShell(ABC):
    """
    Base class for all Chrystallum agents.
    
    Agents are stateless shells that:
    1. Query graph for context
    2. Invoke external API or LLM
    3. Persist results back to graph
    4. Log provenance
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.graph_db = Neo4jConnection(config['neo4j_uri'])
        self.ontology = self._load_ontology(config['ontology_path'])
    
    def _load_ontology(self, path: str) -> Dict:
        """Load YAML ontology definition"""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task.
        
        Steps:
        1. Query graph for context (5W1H)
        2. Call external API/LLM
        3. Validate response against ontology
        4. Persist to graph
        5. Return result
        """
        pass
    
    def query_context(self, node_id: str) -> Dict[str, Any]:
        """
        Query graph for 5W1H context around a node.
        
        Returns dict with keys: who, what, when, where, why, how
        """
        query = """
        MATCH (n {id: $node_id})
        OPTIONAL MATCH (n)-[:CREATED_BY]->(agent:Agent)
        OPTIONAL MATCH (n)-[:OCCURRED_AT]->(location)
        OPTIONAL MATCH (n)-[:EVIDENCE_FOR]->(evidence)
        RETURN 
          n.what as what,
          agent.what as who,
          n.when as when,
          location.what as where,
          n.why as why,
          n.how as how,
          collect(evidence) as evidence
        """
        result = self.graph_db.query(query, node_id=node_id)
        return result[0] if result else {}
    
    def persist_result(self, node_type: str, properties: Dict, edges: List[Dict]):
        """
        Persist agent output to graph.
        
        Validates against ontology before persisting.
        """
        # Validate node type exists in ontology
        if node_type not in self.ontology['core_node_types']:
            if node_type not in self.ontology.get('domain_node_types', {}):
                raise ValueError(f"Unknown node type: {node_type}")
        
        # Validate required properties (5W1H enforcement)
        required = self.ontology['core_node_types'][node_type]['required_properties']
        for prop in required:
            prop_name = list(prop.keys())[0]
            if prop_name not in properties:
                raise ValueError(f"Missing required property '{prop_name}' for {node_type}")
        
        # Create node
        node_id = self.graph_db.create_node(node_type, properties)
        
        # Create edges
        for edge in edges:
            self.graph_db.create_edge(
                edge['type'],
                node_id,
                edge['target'],
                edge.get('properties', {})
            )
        
        # Add provenance (who created this)
        self.graph_db.create_edge(
            'CREATED_BY',
            node_id,
            self.agent_id,
            {'when': datetime.now()}
        )
        
        return node_id
```

### Example: Historical Research Agent

```python
class CaesarDatesAgent(AgentShell):
    """
    Agent specialized in dating Caesar-related events.
    
    Calls external LLM to analyze sources and propose date claims.
    """
    
    def __init__(self, agent_id: str, config: Dict):
        super().__init__(agent_id, config)
        self.llm = OpenAI(api_key=config['openai_key'])
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Analyze sources for date of Rubicon crossing
        
        Steps:
        1. Query graph for Rubicon event + sources
        2. Send to LLM for analysis
        3. Create DateClaim nodes
        4. Link to sources via EVIDENCE_FOR
        5. Detect contradictions
        """
        event_id = task['event_id']
        
        # 1. Query context
        context = self.query_context(event_id)
        sources = self._get_sources(event_id)
        
        # 2. Call LLM
        prompt = f"""
        Analyze these historical sources for the date of: {context['what']}
        
        Sources:
        {self._format_sources(sources)}
        
        Extract:
        - Most likely date (with confidence 0-1)
        - Calendar type (Julian/Gregorian)
        - Evidence from each source
        - Any contradictions
        
        Return JSON format:
        {{
          "date_claims": [
            {{"date": "49-01-10", "confidence": 0.8, "source_id": "...", "evidence": "..."}}
          ],
          "contradictions": [...]
        }}
        """
        
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # 3. Persist DateClaim nodes
        for claim in result['date_claims']:
            properties = {
                'what': f"Date of {context['what']}: {claim['date']}",
                'who': self.agent_id,
                'when': datetime.now(),
                'where': context.get('where', 'unknown'),
                'why': claim['evidence'],
                'how': 'LLM analysis of historical sources',
                'date_value': claim['date'],
                'confidence': claim['confidence'],
                'provenance': claim['source_id']
            }
            
            edges = [
                {'type': 'EVIDENCE_FOR', 'target': event_id},
                {'type': 'SUPPORTS', 'target': claim['source_id']}
            ]
            
            claim_id = self.persist_result('DateClaim', properties, edges)
        
        # 4. Detect contradictions
        for contradiction in result.get('contradictions', []):
            self._create_contradiction_edge(
                contradiction['claim_a'],
                contradiction['claim_b'],
                contradiction['reason']
            )
        
        return {'status': 'success', 'claims_created': len(result['date_claims'])}
    
    def _get_sources(self, event_id: str) -> List[Dict]:
        """Query all sources linked to event"""
        query = """
        MATCH (event {id: $event_id})<-[:EVIDENCE_FOR]-(source:Source)
        RETURN source
        """
        return self.graph_db.query(query, event_id=event_id)
```

### Example: SDLC Architecture Agent

```python
class ArchitectAgent(AgentShell):
    """
    Agent that designs system architecture to satisfy requirements.
    
    Uses LLM to generate architectural decisions and SysML diagrams.
    """
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Design architecture for requirement
        
        Steps:
        1. Query requirement + constraints
        2. LLM generates architecture proposal
        3. Create Architecture nodes
        4. Link via SATISFIES edge
        5. Store ADR (Architecture Decision Record)
        """
        requirement_id = task['requirement_id']
        
        # 1. Query requirement
        req = self.query_context(requirement_id)
        constraints = self._get_constraints(requirement_id)
        
        # 2. LLM architectural design
        prompt = f"""
        Design system architecture for:
        Requirement: {req['what']}
        Why: {req['why']}
        Constraints: {constraints}
        
        Provide:
        - System components (blocks)
        - Interfaces between components
        - Technology choices (with rationale)
        - ADR explaining decisions
        
        Return JSON with SysML-style structure.
        """
        
        response = self.llm.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        architecture = json.loads(response.choices[0].message.content)
        
        # 3. Persist Architecture node
        properties = {
            'what': f"Architecture for {req['what']}",
            'who': self.agent_id,
            'when': datetime.now(),
            'where': req.get('where', 'system_level'),
            'why': architecture['adr']['rationale'],
            'how': architecture['adr']['technology_stack'],
            'architecture_type': 'system',
            'adr_id': f"ADR-{datetime.now().strftime('%Y%m%d-%H%M')}"
        }
        
        edges = [
            {'type': 'SATISFIES', 'target': requirement_id}
        ]
        
        arch_id = self.persist_result('Architecture', properties, edges)
        
        # 4. Create component nodes
        for component in architecture['components']:
            self._create_component(arch_id, component)
        
        return {'status': 'success', 'architecture_id': arch_id}
```

---

## Persistence Model: Graph as Source of Truth

### All State in Graph

**What gets persisted:**

1. **Agent Configuration** (as Agent nodes)
2. **Agent Inputs** (task parameters, context queries)
3. **Agent Outputs** (claims, decisions, generated content)
4. **Provenance** (who created what, when, why, how)
5. **Version History** (all changes tracked via node versions or chains)
6. **Debate Records** (β-α-π phase outputs)

**What does NOT get persisted:**
- Ephemeral LLM session state
- Temporary variables in agent code
- In-memory caches (except as performance optimization, separate from source of truth)

### Version Control Pattern

**Every update creates a new node (or node version), linked to previous:**

```cypher
// Old claim
(claim_v1:DateClaim {date_value: "49-01-10", version: 1})

// Agent proposes update
(claim_v2:DateClaim {date_value: "49-01-11", version: 2})
-[:SUPERSEDES]->(claim_v1)
-[:CREATED_BY]->(agent_historian)

// Both claims remain in graph for audit trail
// Queries default to latest version unless historical view requested
```

### Query Patterns

**Get current state:**
```cypher
MATCH (n:DateClaim {event_id: $event_id})
WHERE NOT (n)<-[:SUPERSEDES]-()
RETURN n
```

**Get full history:**
```cypher
MATCH path = (latest:DateClaim {event_id: $event_id})-[:SUPERSEDES*]->(oldest)
WHERE NOT (latest)<-[:SUPERSEDES]-()
RETURN path
ORDER BY latest.version DESC
```

**Get context for agent (5W1H):**
```cypher
MATCH (event:Event {id: $event_id})
OPTIONAL MATCH (event)-[:CREATED_BY]->(creator:Agent)
OPTIONAL MATCH (event)-[:OCCURRED_AT]->(location)
OPTIONAL MATCH (source:Source)-[:EVIDENCE_FOR]->(event)
OPTIONAL MATCH (event)-[r:SUPPORTS|CONTRADICTS]-(related)
RETURN 
  event.what as what,
  creator.what as who,
  event.when as when,
  location.what as where,
  event.why as why,
  event.how as how,
  collect(DISTINCT source) as evidence,
  collect(DISTINCT {type: type(r), node: related}) as related_claims
```

---

## Dynamic Ontology Evolution

### How Agents Extend Schema

**Pattern 1: Agent proposes new node type**

```python
def propose_new_node_type(self, type_name: str, properties: Dict, justification: str):
    """
    Agent proposes extension to ontology.
    
    Goes through approval process (could be automatic or human-in-loop).
    """
    proposal = {
        'type_name': type_name,
        'extends': 'Event',  # Or other base type
        'properties': properties,
        'justification': justification,
        'proposed_by': self.agent_id,
        'proposed_at': datetime.now()
    }
    
    # Create proposal node in graph
    proposal_id = self.graph_db.create_node('OntologyProposal', proposal)
    
    # Trigger review (could be automated via governance agent or human approval)
    return proposal_id
```

**Example: Agent discovers need for "Uncertainty" node type:**

```yaml
# Agent proposes via API or YAML extension:
new_node_type:
  UncertaintyAnnotation:
    extends: Claim
    description: "Quantifies uncertainty about a historical claim"
    additional_properties:
      - uncertainty_type: {type: string, enum: [temporal, spatial, causal, attribution]}
      - confidence_interval: {type: array, items: float, minItems: 2, maxItems: 2}
      - sensitivity_analysis: {type: string}
    justification: |
      Historical claims often have inherent uncertainty (e.g., "Caesar crossed 
      the Rubicon on Jan 10 or 11"). Need structured way to represent this.
    proposed_by: agent_uncertainty_quantifier
```

**Pattern 2: Agent proposes new edge type**

```python
# Agent working on code traceability discovers need for INSPIRED_BY edge
new_edge = {
    'type': 'INSPIRED_BY',
    'from': ['Code', 'Architecture'],
    'to': ['Code', 'Architecture'],
    'description': 'Design pattern or code inspired by previous work',
    'properties': {
        'similarity_score': {'type': 'float', 'min': 0.0, 'max': 1.0},
        'who': {'type': 'string'},
        'when': {'type': 'datetime'}
    },
    'justification': 'Need to track design pattern reuse and code inspiration chains'
}

self.propose_new_edge_type(new_edge)
```

### Ontology Governance

**Three approval models:**

1. **Automatic (for non-breaking changes)**
   - Agent proposes, system validates against base ontology, auto-approves if compatible
   - Example: Adding optional property to existing node type

2. **Governance Agent (for structural changes)**
   - Proposal triggers governance agent that checks:
     - Compatibility with existing constraints
     - Overlap with existing types (avoid duplication)
     - Adherence to 5W1H principle
   - Auto-approves if passes checks, else escalates to human

3. **Human Approval (for major changes)**
   - Breaking changes, new base types, fundamental shifts
   - Human reviews proposal, justification, impact analysis
   - Approves or rejects with feedback

---

## Canonical Math Mapped to 5W1H

### Pressure Fields as Completeness Metrics

**The canonical math from Section 4 directly maps to 5W1H completeness:**

```python
def calculate_epistemic_pressure(node: Dict) -> float:
    """
    Epistemic pressure = penalty for missing or weak 5W1H
    
    Higher pressure = more gaps in knowledge
    """
    penalty = 0.0
    
    # Who: Missing creator/agent?
    if not node.get('who') or node['who'] == 'unknown':
        penalty += 1.0
    
    # What: Unlabeled or vague?
    if not node.get('what') or len(node['what']) < 5:
        penalty += 1.0
    
    # When: Missing timestamp?
    if not node.get('when'):
        penalty += 0.8
    
    # Where: No context/location?
    if not node.get('where'):
        penalty += 0.5
    
    # Why: No rationale or evidence?
    why_edges = count_edges(node, 'EVIDENCE_FOR') + count_edges(node, 'JUSTIFIED_BY')
    if not node.get('why') and why_edges == 0:
        penalty += 1.5  # Highest penalty: unsupported claims
    
    # How: No method or implementation?
    if not node.get('how'):
        penalty += 0.5
    
    # Confidence: Low confidence compounds penalty
    confidence = node.get('confidence', 0.5)
    penalty *= (2.0 - confidence)  # Low confidence doubles penalty
    
    return penalty

def calculate_civic_pressure(node: Dict, graph) -> float:
    """
    Civic pressure = disagreement among agents on same topic
    
    Higher pressure = more contradiction/lack of consensus
    """
    # Count supporting vs contradicting claims
    support_count = count_edges(node, 'SUPPORTS')
    contradict_count = count_edges(node, 'CONTRADICTS')
    
    # High contradiction, low support = high pressure
    if support_count == 0 and contradict_count > 0:
        return 2.0 * contradict_count
    
    # Calculate consensus ratio
    total = support_count + contradict_count
    if total == 0:
        return 0.5  # Neutral: no opinions yet
    
    consensus_ratio = support_count / total
    
    # Pressure inversely proportional to consensus
    return (1.0 - consensus_ratio) * 2.0

def calculate_temporal_pressure(node: Dict, graph) -> float:
    """
    Temporal pressure = inconsistency in timeline/causality
    
    Higher pressure = events out of order or causally impossible
    """
    penalty = 0.0
    
    # Missing timestamp entirely
    if not node.get('when'):
        return 1.0
    
    # Check causal consistency
    # (node A caused node B, but A happened after B = violation)
    caused_nodes = get_related(node, 'CAUSED')
    for caused in caused_nodes:
        if caused.get('when') and caused['when'] < node['when']:
            penalty += 2.0  # Major violation
    
    return penalty

def calculate_structural_pressure(node: Dict, graph) -> float:
    """
    Structural pressure = orphaned, overly complex, or disconnected
    
    Higher pressure = poor graph topology
    """
    penalty = 0.0
    
    # Orphan nodes (no incoming or outgoing edges)
    edge_count = count_all_edges(node)
    if edge_count == 0:
        penalty += 2.0
    elif edge_count == 1:
        penalty += 1.0  # Weakly connected
    
    # Overly dense (hub node with >50 edges = hard to reason about)
    if edge_count > 50:
        penalty += (edge_count - 50) * 0.05
    
    # Disconnected from main graph
    if not is_reachable_from_root(node, graph):
        penalty += 1.5
    
    return penalty

def calculate_unleafing_reward(old_graph, new_graph, node) -> float:
    """
    Reward for connecting previously disconnected knowledge
    
    Higher reward = more value added by new connections
    """
    reward = 0.0
    
    # Reward for linking leaf node (out-degree was 0, now >0)
    old_out_degree = count_outgoing_edges(node, old_graph)
    new_out_degree = count_outgoing_edges(node, new_graph)
    
    if old_out_degree == 0 and new_out_degree > 0:
        reward += 2.0 * new_out_degree
    
    # Reward for bridging disconnected clusters
    old_clusters = find_disconnected_clusters(old_graph)
    new_clusters = find_disconnected_clusters(new_graph)
    
    if len(new_clusters) < len(old_clusters):
        reward += 5.0 * (len(old_clusters) - len(new_clusters))
    
    return reward
```

### Complete Update Operator

```python
def agent_update_operator(agent, current_graph, proposed_update):
    """
    Φ_i(G) = argmin over G' of:
      λ_E * P_epistemic(G,G') +
      λ_C * P_civic(G,G') +
      λ_S * P_structural(G,G') +
      λ_T * P_temporal(G,G') -
      R_unleaf(G,G')
    
    All pressures/rewards computed from 5W1H completeness.
    """
    # Apply proposed update to get G'
    new_graph = apply_update(current_graph, proposed_update)
    
    # Calculate pressures for affected nodes
    total_pressure = 0.0
    for node in proposed_update.affected_nodes:
        total_pressure += (
            agent.lambda_epistemic * calculate_epistemic_pressure(node) +
            agent.lambda_civic * calculate_civic_pressure(node, new_graph) +
            agent.lambda_structural * calculate_structural_pressure(node, new_graph) +
            agent.lambda_temporal * calculate_temporal_pressure(node, new_graph)
        )
    
    # Calculate unleafing reward
    total_reward = calculate_unleafing_reward(current_graph, new_graph, proposed_update.nodes)
    
    # Objective: minimize pressure, maximize reward
    objective = total_pressure - total_reward
    
    # Accept update if objective improves
    return objective < agent.acceptance_threshold
```

---

## Storage Scaling and Compression

### The Challenge

**Node explosion in large orgs:**
- 1,000 employees
- Each creates 10 nodes/day (requirements, code commits, decisions)
- 365 days/year
- = 3.65 million nodes/year
- Over 5 years: 18.25 million nodes

**Plus edges:**
- Average 5 edges per node
- = 91.25 million edges over 5 years

**Storage requirements:**
- Neo4j: ~100 bytes per node, ~50 bytes per edge
- Nodes: 18.25M × 100 bytes = 1.825 GB
- Edges: 91.25M × 50 bytes = 4.56 GB
- **Total: ~6.4 GB over 5 years**

**Actually manageable for most orgs, but...**

- This assumes minimal properties
- Rich media (videos, 3D models) stored externally
- Text-heavy properties (long descriptions, code, ADRs) can bloat storage

### Compression Strategies

#### 1. **Archival/Dormancy Strategy**

**Concept:** Move dormant subgraphs to cold storage, keep active in hot database.

```python
class GraphArchivalManager:
    """
    Manages hot/warm/cold storage tiers for knowledge graph.
    """
    
    def __init__(self, hot_db, warm_db, cold_storage):
        self.hot_db = hot_db  # Neo4j (active queries)
        self.warm_db = warm_db  # Neo4j (read-only, occasional access)
        self.cold_storage = cold_storage  # S3/Parquet (archival)
    
    def archive_dormant_subgraphs(self, dormancy_threshold_days=180):
        """
        Move subgraphs with no updates in 180 days to warm/cold storage.
        
        Steps:
        1. Identify dormant subgraphs (no CREATED_BY or updates in N days)
        2. Export to warm DB (read-only Neo4j instance)
        3. Compress to Parquet, upload to S3
        4. Delete from hot DB, keep stub with pointer to archive
        """
        # Find dormant subgraphs
        query = """
        MATCH (root)-[:CONTAINS*]->(node)
        WHERE NOT exists {
          MATCH (node)<-[:CREATED_BY]-(agent)
          WHERE agent.last_active > datetime() - duration({days: $threshold})
        }
        WITH root, collect(node) as dormant_nodes
        WHERE size(dormant_nodes) > 100  // Only archive large subgraphs
        RETURN root, dormant_nodes
        """
        
        dormant_subgraphs = self.hot_db.query(query, threshold=dormancy_threshold_days)
        
        for subgraph in dormant_subgraphs:
            # Export to Parquet
            parquet_path = self._export_to_parquet(subgraph)
            
            # Upload to S3
            s3_url = self.cold_storage.upload(parquet_path)
            
            # Create stub in hot DB
            stub = {
                'id': subgraph['root']['id'],
                'type': 'ArchivedSubgraph',
                'archive_url': s3_url,
                'archived_at': datetime.now(),
                'node_count': len(subgraph['dormant_nodes'])
            }
            self.hot_db.create_node('ArchiveStub', stub)
            
            # Delete from hot DB
            self.hot_db.delete_subgraph(subgraph['dormant_nodes'])
    
    def restore_from_archive(self, stub_id: str):
        """
        Restore archived subgraph to hot DB on-demand.
        """
        stub = self.hot_db.get_node(stub_id)
        
        # Download from S3
        parquet_path = self.cold_storage.download(stub['archive_url'])
        
        # Import to hot DB
        self._import_from_parquet(parquet_path, self.hot_db)
        
        # Delete stub
        self.hot_db.delete_node(stub_id)
```

**Storage impact:**
- Hot DB: Only active 6-12 months of data (~10-20% of total)
- Warm DB: 1-5 years, read-only (can use cheaper hardware)
- Cold storage (S3): 5+ years, $0.023/GB/month (vs Neo4j server costs)

**Example savings:**
- 18.25M nodes over 5 years
- 80% dormant (14.6M nodes)
- Archived to S3: 5.2 GB × $0.023/month = $0.12/month
- vs keeping in Neo4j: ~$500/month in server costs

#### 2. **Property Externalization**

**Store large text/binary data externally, keep pointer in node.**

```python
class PropertyExternalizer:
    """
    Moves large properties to external storage (S3, blob storage).
    """
    
    def __init__(self, db, blob_storage):
        self.db = db
        self.blob_storage = blob_storage
        self.size_threshold = 1024  # Externalize properties >1KB
    
    def externalize_property(self, node_id: str, property_name: str):
        """
        Move large property to blob storage.
        
        Before:
          node.description = "<10KB of text>"
        
        After:
          node.description_external = "s3://bucket/node123_description.txt"
          node.description = "<first 100 chars...>"  # Summary
        """
        node = self.db.get_node(node_id)
        prop_value = node[property_name]
        
        if len(prop_value) < self.size_threshold:
            return  # Small enough, keep in DB
        
        # Upload to blob storage
        blob_url = self.blob_storage.upload(
            data=prop_value,
            key=f"{node_id}_{property_name}.txt"
        )
        
        # Update node
        self.db.update_node(node_id, {
            f"{property_name}_external": blob_url,
            property_name: prop_value[:100] + "..."  # Summary
        })
```

**Example:**
- Code files: Store in Git, keep only file path + commit hash in Neo4j
- Videos: Store in CDN, keep only URL in Neo4j
- Long ADRs: Store in S3, keep summary in Neo4j

#### 3. **Edge Compression via Hypergraphs**

**Problem:** Many-to-many relationships create edge explosion.

Example: 100 requirements all DEPEND_ON same 50 components
- Naïve: 100 × 50 = 5,000 edges
- Hypergraph: 1 hyperedge connecting 100 requirements to 50 components

```cypher
// Instead of 5,000 edges:
(req1)-[:DEPENDS_ON]->(comp1)
(req1)-[:DEPENDS_ON]->(comp2)
...
(req100)-[:DEPENDS_ON]->(comp50)

// Create 1 hyperedge node:
(hyperedge:DependencyGroup {
  requirement_ids: [req1, req2, ..., req100],
  component_ids: [comp1, comp2, ..., comp50],
  created_by: "architect_agent",
  when: "2025-01-15"
})

(req1)-[:PART_OF]->(hyperedge)
(req100)-[:PART_OF]->(hyperedge)
(hyperedge)-[:DEPENDS_ON]->(comp1)
(hyperedge)-[:DEPENDS_ON]->(comp50)
```

**Savings:**
- 5,000 edges → 150 edges (100 PART_OF + 50 DEPENDS_ON)
- 97% reduction

#### 4. **Neo4j Native Compression**

**Neo4j Enterprise features:**

```properties
# neo4j.conf

# Enable property compression (strings >1KB)
dbms.tx_state.memory_allocation=ON_HEAP
dbms.memory.pagecache.size=4G

# Enable record compression
dbms.record_format=high_limit  # Supports larger graphs

# Enable index compression
dbms.index.default_schema_provider=native-btree-1.0
```

**Compression ratios:**
- Strings: 60-80% reduction (gzip-like)
- Numbers: 40-60% reduction
- Overall: ~50% storage reduction

#### 5. **Temporal Aggregation**

**Concept:** Aggregate fine-grained temporal data into summaries.

**Example: Code commit history**

```python
# Instead of storing every commit as a node:
# 1,000 commits/day × 365 days = 365K nodes/year

# Aggregate to daily summaries:
# 1 node per day = 365 nodes/year (1000× reduction)

def aggregate_commits_daily(date: str):
    """
    Replace individual commit nodes with daily summary.
    """
    query = """
    MATCH (c:Commit)
    WHERE date(c.when) = date($date)
    WITH count(c) as commit_count,
         sum(c.lines_added) as total_lines_added,
         sum(c.lines_deleted) as total_lines_deleted,
         collect(c.file_path) as affected_files
    CREATE (summary:DailySummary {
      date: $date,
      commit_count: commit_count,
      lines_added: total_lines_added,
      lines_deleted: total_lines_deleted,
      affected_files: affected_files,
      detail_archive: "s3://commits/" + $date + ".parquet"
    })
    """
    
    # Store detailed commits in S3 Parquet
    # Keep only summary in Neo4j
```

**Savings:**
- 365K commit nodes → 365 summary nodes (1000× reduction)
- Detail still accessible via S3 if needed

#### 6. **Lazy Property Loading**

**Concept:** Don't load all properties by default, fetch on-demand.

```python
class LazyNode:
    """
    Node proxy that loads properties lazily.
    """
    
    def __init__(self, node_id: str, db):
        self.id = node_id
        self.db = db
        self._properties = None  # Not loaded yet
    
    @property
    def properties(self):
        """Load properties on first access"""
        if self._properties is None:
            self._properties = self.db.get_node_properties(self.id)
        return self._properties
    
    def __getattr__(self, name):
        """Lazy property access"""
        return self.properties.get(name)

# Usage:
node = LazyNode("node_123", db)
# No DB query yet

print(node.what)  # NOW query DB for properties
```

**Benefit:** Reduces memory usage for large graph traversals (only load properties when accessed).

---

### Storage Recommendations by Deployment Size

| Deployment Size | Strategy | Hot DB Size | Cold Storage | Annual Cost |
|----------------|----------|-------------|--------------|-------------|
| **Solo (1 user)** | Local only | 1-10 GB | None needed | $0 |
| **Small team (5-20)** | Local + backup | 10-100 GB | S3 for backups | $10-50/year |
| **Mid-size (50-200)** | Hot + warm | 100GB-1TB hot, 1-5TB warm | S3 archival | $500-2K/year |
| **Enterprise (1,000+)** | Hot + warm + cold | 1-5TB hot, 10-50TB warm | S3 cold storage | $5K-20K/year |

**Key insight:** With aggressive dormancy + archival, even large orgs stay within manageable storage bounds.

---

### Neo4j Compression Summary

**Built-in features:**
1. **Property compression** (automatic for strings >1KB)
2. **Record format optimization** (high_limit format for large graphs)
3. **Index compression** (native-btree with compression)

**Manual strategies:**
1. **Dormancy + archival** (move old data to S3)
2. **Property externalization** (store large blobs externally)
3. **Hypergraph compression** (many-to-many as hyperedges)
4. **Temporal aggregation** (fine-grained → summaries)
5. **Lazy loading** (don't load unused properties)

**Expected compression ratios:**
- Naive storage: 100%
- Neo4j native compression: 50% (2× improvement)
- + Dormancy archival: 20% (5× improvement)
- + Property externalization: 10% (10× improvement)
- + Hypergraph compression: 5% (20× improvement)

**Bottom line:** With these strategies, a 1,000-person org over 5 years needs only **~300-500GB hot storage** (vs 6.4GB naive × 20 for rich content = ~130GB, so very manageable).

---

## Implementation Examples

### Example 1: Complete Rubicon Event Graph

```yaml
# rubicon-example.yaml
# Complete 5W1H graph for "Crossing the Rubicon"

nodes:
  - id: event_rubicon
    type: HistoricalEvent
    properties:
      what: "Crossing the Rubicon"
      who: "agent_caesar_bio"
      when: "49-01-10T06:00:00"  # Morning of Jan 10, 49 BCE (Julian)
      where: "Rubicon River"
      why: "Avoid prosecution by Senate, start civil war"
      how: "Led XIII Legion across river boundary"
      qid: "Q2253"
      confidence: 0.85
      version: 3

  - id: claim_date_plutarch
    type: DateClaim
    properties:
      what: "Date: January 10, 49 BC"
      who: "agent_caesar_dates"
      when: "2025-11-19T09:00:00"
      where: "Rubicon crossing event"
      why: "Plutarch Life of Caesar, Ch. 32 states 'tenth day'"
      how: "LLM analysis of primary source"
      date_value: "49-01-10"
      calendar: "Julian"
      confidence: 0.8
      provenance: "source_plutarch"

  - id: claim_date_alternative
    type: DateClaim
    properties:
      what: "Date: January 11, 49 BC"
      who: "agent_alternative_dates"
      when: "2025-11-19T10:00:00"
      where: "Rubicon crossing event"
      why: "Appian Civil Wars suggests 'eleventh day'"
      how: "LLM analysis of secondary interpretation"
      date_value: "49-01-11"
      calendar: "Julian"
      confidence: 0.6
      provenance: "source_appian"

  - id: source_plutarch
    type: PrimarySources
    properties:
      what: "Plutarch's Life of Caesar"
      who: "Plutarch"
      when: "circa 100 CE"
      where: "Greece"
      how: "book"
      language: "Greek"
      translation: "Dryden translation"

edges:
  - type: CREATED_BY
    from: event_rubicon
    to: agent_caesar_bio
    properties:
      when: "2025-11-15T14:00:00"

  - type: EVIDENCE_FOR
    from: source_plutarch
    to: claim_date_plutarch
    properties:
      who: "agent_caesar_dates"
      when: "2025-11-19T09:00:00"
      how: "Extracted from chapter 32"

  - type: CONTRADICTS
    from: claim_date_alternative
    to: claim_date_plutarch
    properties:
      who: "agent_debate_resolver"
      when: "2025-11-19T11:00:00"
      why: "Different date values for same event"
      confidence: 0.9
```

### Example 2: SDLC Password Reset Implementation

```yaml
# password-reset-example.yaml
# Complete traceability: Requirement → Architecture → Code → Test

nodes:
  - id: req_password_reset
    type: Requirement
    properties:
      what: "User password reset via email"
      who: "ba_agent_auth"
      when: "2025-01-10T10:00:00"
      where: "Auth Service"
      why: "Reduce support tickets by 30%"
      how: "Email-based reset with JWT tokens"
      requirement_id: "REQ-001"
      priority: "high"
      status: "implemented"
      acceptance_criteria:
        - "User receives email within 30 seconds"
        - "Link expires after 24 hours"
        - "Token is single-use"

  - id: arch_password_reset
    type: Architecture
    properties:
      what: "Password Reset System Architecture"
      who: "architect_agent"
      when: "2025-01-12T14:00:00"
      where: "System level"
      why: "Stateless, secure, standard JWT approach"
      how: "JWT tokens + SendGrid email + PostgreSQL token store"
      architecture_type: "system"
      technology_stack: ["FastAPI", "JWT", "SendGrid", "PostgreSQL"]
      adr_id: "ADR-007"

  - id: code_password_reset
    type: Code
    properties:
      what: "Password reset implementation"
      who: "developer_agent"
      when: "2025-01-15T16:30:00"
      where: "auth/password_reset.py"
      why: "Implements REQ-001 per architecture"
      how: "FastAPI endpoint + JWT generation + email sending"
      file_path: "auth/password_reset.py"
      language: "Python"
      lines_of_code: 150
      test_coverage: 0.95
      git_commit: "abc123def456"

  - id: test_happy_path
    type: TestCase
    properties:
      what: "Test password reset happy path"
      who: "qa_analyst_agent"
      when: "2025-01-16T10:00:00"
      where: "tests/test_password_reset.py"
      why: "Verify AC1: Email received within 30 seconds"
      how: "Integration test with mock email service"
      test_id: "TC-001"
      test_type: "integration"
      status: "passed"

edges:
  - type: SATISFIES
    from: arch_password_reset
    to: req_password_reset
    properties:
      who: "architect_agent"
      when: "2025-01-12T14:30:00"

  - type: IMPLEMENTS
    from: code_password_reset
    to: arch_password_reset
    properties:
      who: "developer_agent"
      when: "2025-01-15T16:30:00"

  - type: VERIFIES
    from: test_happy_path
    to: req_password_reset
    properties:
      who: "qa_analyst_agent"
      when: "2025-01-16T10:30:00"
      acceptance_criterion: "AC1"

  - type: CREATED_BY
    from: req_password_reset
    to: ba_agent_auth

  - type: CREATED_BY
    from: arch_password_reset
    to: architect_agent

  - type: CREATED_BY
    from: code_password_reset
    to: developer_agent

  - type: CREATED_BY
    from: test_happy_path
    to: qa_analyst_agent
```

---

## Conclusion

### Key Takeaways

1. **5W1H is the universal foundation** - Every knowledge domain reduces to these six dimensions
2. **Minimal seeding protocol** - Define base types/relations, agents extend dynamically
3. **Agents are stateless shells** - All state externalized to graph, agents are API wrappers
4. **Graph is source of truth** - Neo4j persists everything: inputs, outputs, provenance, versions
5. **Schema evolves dynamically** - Agents propose new types/relations as domain needs emerge
6. **Canonical math enforces 5W1H** - Pressure fields penalize gaps, rewards completeness
7. **Storage scales with strategy** - Dormancy + archival + compression keeps costs manageable

### Implementation Roadmap

**Phase 1: Foundation (Weeks 1-2)**
- Define base ontology YAML (5W1H core types)
- Implement AgentShell base class
- Set up Neo4j with basic schema

**Phase 2: Domain Extension (Weeks 3-4)**
- Create domain-specific YAML (history or SDLC)
- Implement first specialized agent (e.g., CaesarDatesAgent)
- Validate 5W1H completeness metrics

**Phase 3: Math Integration (Weeks 5-6)**
- Implement pressure field calculations
- Add debate system (β-α-π pipeline)
- Test update operator with real data

**Phase 4: Scaling (Weeks 7-8)**
- Implement dormancy detection
- Add archival system (hot/warm/cold)
- Performance testing with 1M+ nodes

**Phase 5: Production (Weeks 9-12)**
- Multi-agent orchestration
- UI for graph exploration
- Monitoring and optimization

### Success Metrics

- **Completeness:** Average 5W1H coverage >80%
- **Traceability:** Any node can trace back to source in <5 hops
- **Performance:** Query response <500ms for 95th percentile
- **Storage:** <100GB hot storage per 1,000 active users
- **Adoption:** Agents create >10 nodes/day per active user

---

## Appendices

### A. Complete Base Ontology YAML

(See "Minimal Protocol YAML Templates" section above for full definition)

### B. Agent Implementation Templates

(See "Agent Architecture" section for AgentShell, CaesarDatesAgent, ArchitectAgent examples)

### C. Storage Optimization Code

(See "Storage Scaling and Compression" section for GraphArchivalManager, PropertyExternalizer examples)

### D. Cypher Query Patterns

**Get 5W1H context:**
```cypher
MATCH (n {id: $node_id})
OPTIONAL MATCH (n)-[:CREATED_BY]->(who:Agent)
OPTIONAL MATCH (n)-[:OCCURRED_AT]->(where)
OPTIONAL MATCH (why:Source)-[:EVIDENCE_FOR]->(n)
RETURN 
  n.what as what,
  who.what as who,
  n.when as when,
  where.what as where,
  collect(why) as why,
  n.how as how
```

**Find incomplete nodes (high pressure):**
```cypher
MATCH (n)
WHERE 
  n.what IS NULL OR
  n.who IS NULL OR
  n.when IS NULL
RETURN n, 
  CASE 
    WHEN n.what IS NULL THEN 1 ELSE 0 
  END +
  CASE 
    WHEN n.who IS NULL THEN 1 ELSE 0 
  END +
  CASE 
    WHEN n.when IS NULL THEN 1 ELSE 0 
  END as incompleteness_score
ORDER BY incompleteness_score DESC
LIMIT 100
```

**Find contradictions:**
```cypher
MATCH (c1:Claim)-[r:CONTRADICTS]->(c2:Claim)
WHERE r.confidence > 0.7
RETURN c1, c2, r
ORDER BY r.confidence DESC
```

**Trace requirement to code:**
```cypher
MATCH path = (req:Requirement {requirement_id: $req_id})
-[:SATISFIES*0..1]->(arch:Architecture)
-[:IMPLEMENTS*0..1]->(code:Code)
RETURN path
```

### E. References

1. Neo4j Graph Database Documentation: https://neo4j.com/docs/
2. SysML Specification: https://www.omgsysml.org/
3. Wikidata Query Service: https://query.wikidata.org/
4. Section 4: Chrystallum Mathematical Framework (see section-4-revised.md)
5. SDLC Multi-Role Architecture (see sdlc-sysml-multi-role.md)
6. Presentation Layer Agent ESB (see presentation-layer-agent-esb.md)

---

**Document Version:** 1.0  
**Last Updated:** November 19, 2025  
**Author:** Chrystallum Development Team  
**License:** MIT (or specify your license)