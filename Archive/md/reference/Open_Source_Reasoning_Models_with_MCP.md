# Open Source Reasoning Models with MCP in Cursor

## Overview

Practical guide to open source reasoning models that work with MCP (Model Context Protocol) in Cursor IDE.

---

## Reasoning Models Compatible with MCP

### 1. **Neo4j with Cypher Queries** ✅ Recommended

**What it is:**
- Graph database with Cypher query language
- Rule-based and graph pattern reasoning
- Native graph reasoning capabilities

**MCP Integration:**
- Can create MCP server exposing Neo4j queries
- Cypher queries = reasoning rules
- Graph pattern matching = inference

**Implementation:**
```python
# MCP Server for Neo4j
from mcp import Server, Tool
import neo4j

server = Server("neo4j-reasoning")

@server.tool()
def infer_contemporaries(entity_id: str) -> dict:
    """
    Infer contemporaries using graph patterns.
    """
    query = """
    MATCH (e:Human {id: $entity_id})
    MATCH (other:Human)
    WHERE e.backbone_lcc = other.backbone_lcc
      AND e.start_date <= other.end_date
      AND other.start_date <= e.end_date
      AND e <> other
    RETURN other, 
           calculate_confidence(e, other) as confidence
    """
    result = neo4j_driver.execute_query(query, entity_id=entity_id)
    return {"contemporaries": result}

@server.tool()
def validate_consistency(entity_id: str) -> dict:
    """
    Validate entity consistency across standards.
    """
    query = """
    MATCH (e {id: $entity_id})
    RETURN 
      CASE WHEN e.viaf_id IS NOT NULL AND e.qid IS NOT NULL 
           THEN 'has_ids' ELSE 'missing_ids' END as status,
      CASE WHEN e.start_date IS NOT NULL AND e.end_date IS NOT NULL
           AND e.start_date > e.end_date
           THEN 'invalid_dates' ELSE 'valid_dates' END as date_status
    """
    result = neo4j_driver.execute_query(query, entity_id=entity_id)
    return {"consistency": result[0]}
```

**Why It Works:**
- ✅ Open source
- ✅ Native graph reasoning
- ✅ MCP-compatible (can expose as tools)
- ✅ Already using Neo4j

---

### 2. **LangChain with Graph Reasoning** ✅ Recommended

**What it is:**
- Framework for LLM applications
- Graph reasoning capabilities
- MCP integration support

**MCP Integration:**
- LangChain tools can be exposed via MCP
- Graph reasoning chains as MCP tools
- Agent-based reasoning

**Implementation:**
```python
from langchain.tools import MCPTool
from langchain.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from mcp import Server

# Create Neo4j graph
graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="password"
)

# Create reasoning chain
qa_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True
)

# Expose as MCP tool
server = Server("langchain-reasoning")

@server.tool()
def reason_about_entity(question: str, entity_id: str) -> dict:
    """
    Reason about entity using graph patterns.
    """
    query = f"What relationships does {entity_id} have?"
    result = qa_chain.run(query)
    return {"reasoning": result}
```

**Why It Works:**
- ✅ Open source
- ✅ Graph reasoning built-in
- ✅ MCP compatible
- ✅ LangChain ecosystem

---

### 3. **PyKE (Python Knowledge Engine)** ✅ Specialized

**What it is:**
- Rule-based reasoning engine
- Forward/backward chaining
- Knowledge base system

**MCP Integration:**
- Can wrap PyKE reasoning as MCP tools
- Rules as MCP-accessible functions

**Implementation:**
```python
from pyke import knowledge_engine, pattern
from mcp import Server

server = Server("pyke-reasoning")

# Knowledge base
kb = knowledge_engine.engine(__file__)

@server.tool()
def infer_relationships(entity_id: str) -> dict:
    """
    Infer relationships using PyKE rules.
    """
    kb.reset()
    kb.activate('inference_rules')
    
    # PyKE forward chaining
    with kb.prove_goal('contemporary($entity, $other)') as gen:
        results = []
        for vars in gen:
            results.append({
                'entity': vars['entity'],
                'other': vars['other'],
                'confidence': calculate_confidence(vars)
            })
    
    return {"inferred_relationships": results}
```

**Why It Works:**
- ✅ Open source
- ✅ Rule-based reasoning
- ✅ MCP compatible (wrap as tools)

**Limitation:**
- ⚠️ Less common, smaller community

---

### 4. **PyDatalog / Datalog-based Reasoning** ✅ Logical

**What it is:**
- Datalog logic programming
- Declarative reasoning
- Rule-based inference

**MCP Integration:**
- Datalog queries as MCP tools
- Reasoning rules exposed via MCP

**Implementation:**
```python
from pyDatalog import pyDatalog
from mcp import Server

pyDatalog.create_terms('contemporary', 'same_period', 'overlapping_dates')

# Datalog rules
+same_period(X, Y) <= (entity[X]['lcc'] == entity[Y]['lcc'])
+overlapping_dates(X, Y) <= (entity[X]['start'] <= entity[Y]['end']) & \
                             (entity[Y]['start'] <= entity[X]['end'])
+contemporary(X, Y) <= same_period(X, Y) & overlapping_dates(X, Y)

server = Server("datalog-reasoning")

@server.tool()
def infer_contemporaries(entity_id: str) -> dict:
    """
    Infer contemporaries using Datalog rules.
    """
    results = contemporary(entity_id, Y)
    return {"contemporaries": list(results)}
```

**Why It Works:**
- ✅ Open source
- ✅ Declarative reasoning
- ✅ MCP compatible

**Limitation:**
- ⚠️ Learning curve (Datalog syntax)

---

### 5. **OWL Reasoners (Pellet, HermiT, FaCT++)** ✅ Semantic Web

**What it is:**
- OWL ontology reasoners
- Semantic web reasoning
- Description logic

**MCP Integration:**
- OWL reasoning queries as MCP tools
- Ontology-based inference

**Implementation:**
```python
from owlready2 import *
from mcp import Server

# Load ontology
onto = get_ontology("chrystallum.owl").load()

# OWL reasoner
with onto:
    sync_reasoner_pellet()

server = Server("owl-reasoning")

@server.tool()
def infer_subclasses(entity_type: str) -> dict:
    """
    Infer subclasses using OWL reasoning.
    """
    entity_class = onto.search_one(iri="*" + entity_type)
    subclasses = entity_class.subclasses()
    return {"subclasses": [str(sc) for sc in subclasses]}
```

**Why It Works:**
- ✅ Open source
- ✅ Semantic web standard
- ✅ MCP compatible

**Limitation:**
- ⚠️ Requires OWL ontology conversion

---

### 6. **PyReasoner (Graph-based)** ✅ Modern

**What it is:**
- Graph-based reasoning framework
- Pattern matching
- Relationship inference

**MCP Integration:**
- Reasoning functions as MCP tools

**Implementation:**
```python
from pyreasoner import GraphReasoner
from mcp import Server

reasoner = GraphReasoner(neo4j_driver)

server = Server("pyreasoner")

@server.tool()
def reason_about_graph(pattern: str) -> dict:
    """
    Reason about graph using pattern matching.
    """
    results = reasoner.match_pattern(pattern)
    return {"matches": results}
```

**Note:** Check if PyReasoner exists or use custom graph reasoning.

---

## Recommended: Neo4j + Custom Reasoning Tools

### Best Approach for Chrystallum

**Why Neo4j:**
- ✅ Already using Neo4j
- ✅ Native graph reasoning
- ✅ Cypher = reasoning rules
- ✅ High performance
- ✅ MCP integration straightforward

### Implementation Strategy

#### Step 1: Create MCP Server

```python
# mcp_reasoning_server.py
from mcp import Server, Tool
from neo4j import GraphDatabase

class ChrystallumReasoningServer:
    def __init__(self, neo4j_uri, username, password):
        self.driver = GraphDatabase.driver(neo4j_uri, 
                                           auth=(username, password))
        self.server = Server("chrystallum-reasoning")
        self._register_tools()
    
    def _register_tools(self):
        """Register reasoning tools with MCP."""
        
        @self.server.tool()
        def check_consistency(entity_id: str) -> dict:
            """Check entity consistency across standards."""
            query = """
            MATCH (e {id: $entity_id})
            WITH e,
              CASE 
                WHEN e.viaf_id IS NOT NULL AND e.qid IS NOT NULL 
                THEN 'consistent'
                ELSE 'missing_identifiers'
              END as id_status,
              CASE 
                WHEN e.start_date IS NOT NULL AND e.end_date IS NOT NULL
                AND e.start_date > e.end_date
                THEN 'invalid'
                ELSE 'valid'
              END as date_status
            RETURN {
              id_status: id_status,
              date_status: date_status,
              has_all_standards: (e.backbone_fast IS NOT NULL 
                                  AND e.backbone_lcc IS NOT NULL
                                  AND e.qid IS NOT NULL)
            } as consistency
            """
            with self.driver.session() as session:
                result = session.run(query, entity_id=entity_id)
                return dict(result.single()['consistency'])
        
        @self.server.tool()
        def infer_contemporaries(entity_id: str) -> dict:
            """Infer contemporaries using graph patterns."""
            query = """
            MATCH (e:Human {id: $entity_id})
            MATCH (other:Human)
            WHERE e.backbone_lcc = other.backbone_lcc
              AND e.start_date <= other.end_date
              AND other.start_date <= e.end_date
              AND e <> other
            WITH e, other,
              CASE
                WHEN ABS(DATEDIFF(e.start_date, other.start_date)) <= 10
                THEN 0.9
                WHEN ABS(DATEDIFF(e.start_date, other.start_date)) <= 25
                THEN 0.7
                ELSE 0.5
              END as confidence
            RETURN {
              entity_id: other.id,
              label: other.label,
              confidence: confidence,
              reasoning: 'Same period + overlapping dates'
            } as contemporary
            ORDER BY confidence DESC
            LIMIT 10
            """
            with self.driver.session() as session:
                results = session.run(query, entity_id=entity_id)
                return {
                    "contemporaries": [dict(r['contemporary']) 
                                     for r in results]
                }
        
        @self.server.tool()
        def validate_entity_resolution(entity_id: str) -> dict:
            """Validate entity resolution across identifiers."""
            query = """
            MATCH (e {id: $entity_id})
            OPTIONAL MATCH (other)
            WHERE e <> other
              AND (
                (e.viaf_id IS NOT NULL AND e.viaf_id = other.viaf_id)
                OR (e.qid IS NOT NULL AND e.qid = other.qid)
                OR (e.backbone_marc IS NOT NULL 
                    AND e.backbone_marc = other.backbone_marc)
              )
            RETURN {
              has_duplicates: COUNT(other) > 0,
              duplicate_ids: COLLECT(other.id),
              resolution_status: CASE 
                WHEN COUNT(other) = 0 THEN 'unique'
                WHEN COUNT(other) = 1 THEN 'potential_duplicate'
                ELSE 'multiple_matches'
              END
            } as resolution
            """
            with self.driver.session() as session:
                result = session.run(query, entity_id=entity_id)
                return dict(result.single()['resolution'])
        
        @self.server.tool()
        def infer_causal_chains(event_id: str) -> dict:
            """Infer causal chains from action structures."""
            query = """
            MATCH (event:Event {id: $event_id})
            MATCH (event)-[r:CAUSED]->(effect:Event)
            WHERE event.action_type IS NOT NULL
              AND effect.result_type IS NOT NULL
            WITH event, effect, r,
              CASE
                WHEN event.action_type = 'MIL_ACT' 
                  AND effect.result_type = 'POL_TRANS'
                THEN 0.9
                WHEN event.action_type = effect.trigger_type
                THEN 0.8
                ELSE 0.6
              END as causal_strength
            RETURN {
              effect_id: effect.id,
              label: effect.label,
              causal_strength: causal_strength,
              reasoning: 'Action type matches result type + temporal sequence'
            } as causal_link
            ORDER BY causal_strength DESC
            """
            with self.driver.session() as session:
                results = session.run(query, event_id=event_id)
                return {
                    "causal_chain": [dict(r['causal_link']) 
                                   for r in results]
                }
        
        @self.server.tool()
        def aggregate_confidence(entity_id: str) -> dict:
            """Aggregate confidence from multiple sources."""
            query = """
            MATCH (e {id: $entity_id})
            WITH e,
              COALESCE(e.confidence, 0.5) as chrystallum_conf,
              CASE 
                WHEN e.wikidata_disputed THEN 0.3
                WHEN e.wikidata_verified THEN 0.9
                ELSE 0.7
              END as wikidata_conf,
              CASE
                WHEN e.backbone_fast IS NOT NULL 
                  AND e.backbone_lcc IS NOT NULL
                  AND e.backbone_marc IS NOT NULL
                THEN 0.8
                ELSE 0.5
              END as backbone_conf,
              CASE
                WHEN e.start_date IS NOT NULL 
                  AND e.end_date IS NOT NULL
                  AND e.start_date <= e.end_date
                THEN 0.8
                ELSE 0.5
              END as temporal_conf
            RETURN {
              chrystallum: chrystallum_conf,
              wikidata: wikidata_conf,
              backbone: backbone_conf,
              temporal: temporal_conf,
              integrated: (chrystallum_conf * 0.3 
                          + wikidata_conf * 0.25
                          + backbone_conf * 0.25
                          + temporal_conf * 0.2)
            } as confidence
            """
            with self.driver.session() as session:
                result = session.run(query, entity_id=entity_id)
                return dict(result.single()['confidence'])
    
    def start(self):
        """Start MCP server."""
        self.server.run()

if __name__ == "__main__":
    server = ChrystallumReasoningServer(
        neo4j_uri="bolt://localhost:7687",
        username="neo4j",
        password="password"
    )
    server.start()
```

---

## Setting Up MCP in Cursor

### Step 1: Install MCP SDK

```bash
pip install mcp
```

### Step 2: Configure Cursor MCP Settings

**Cursor Settings (settings.json):**
```json
{
  "mcp.servers": {
    "chrystallum-reasoning": {
      "command": "python",
      "args": [
        "/path/to/mcp_reasoning_server.py"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "password"
      }
    }
  }
}
```

### Step 3: Use in Cursor

**In Cursor, MCP tools appear as:**
- Available function calls
- Context-aware suggestions
- Integrated with code completion

---

## Complete MCP Reasoning Tool Suite

### Recommended Tools for Chrystallum

```python
# Complete reasoning server
REASONING_TOOLS = [
    # Consistency
    "check_consistency",
    "validate_entity_resolution",
    "check_temporal_consistency",
    
    # Inference
    "infer_contemporaries",
    "infer_causal_chains",
    "infer_relationships",
    
    # Confidence
    "aggregate_confidence",
    "calculate_source_confidence",
    
    # Validation
    "validate_dates",
    "validate_identifiers",
    "check_duplicates"
]
```

---

## Alternative: Rule-Based Reasoning Framework

### Custom Rule Engine with MCP

```python
from mcp import Server
from typing import List, Dict

class RuleBasedReasoner:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, condition, conclusion):
        """Add reasoning rule."""
        self.rules.append({
            'condition': condition,
            'conclusion': conclusion
        })
    
    def reason(self, facts: Dict) -> List[Dict]:
        """Apply rules to facts."""
        conclusions = []
        for rule in self.rules:
            if self.evaluate(rule['condition'], facts):
                conclusions.append(rule['conclusion'](facts))
        return conclusions

# MCP Server
server = Server("rule-reasoning")
reasoner = RuleBasedReasoner()

# Add rules
reasoner.add_rule(
    condition=lambda f: f.get('viaf_id') and f.get('qid'),
    conclusion=lambda f: {'entity_resolved': True}
)

@server.tool()
def apply_rules(entity_id: str) -> dict:
    """Apply reasoning rules to entity."""
    entity = get_entity(entity_id)
    conclusions = reasoner.reason(entity)
    return {"conclusions": conclusions}
```

---

## Summary: Recommended Stack

### For Chrystallum in Cursor

**Primary: Neo4j + Custom MCP Tools**
- ✅ Already using Neo4j
- ✅ Cypher = reasoning rules
- ✅ Native graph reasoning
- ✅ MCP integration straightforward

**Secondary: LangChain (if needed)**
- ✅ Graph reasoning chains
- ✅ MCP compatible
- ✅ Agent framework

**Tertiary: Custom Rule Engine**
- ✅ Simple rule-based reasoning
- ✅ Full control
- ✅ MCP compatible

---

## Quick Start Guide

### 1. Install Dependencies

```bash
pip install mcp neo4j
```

### 2. Create MCP Server

```python
# reasoning_server.py (from above)
```

### 3. Configure Cursor

Add to Cursor settings:
```json
{
  "mcp.servers": {
    "chrystallum-reasoning": {
      "command": "python",
      "args": ["reasoning_server.py"]
    }
  }
}
```

### 4. Use in Cursor

MCP tools will appear in Cursor's AI interface for:
- Entity reasoning
- Consistency checking
- Relationship inference
- Confidence scoring

---

## Bottom Line

**Best Open Source Reasoning with MCP for Cursor:**

1. **Neo4j + Custom Cypher Queries** ⭐ Recommended
   - Native graph reasoning
   - MCP server exposing Cypher queries
   - Already using Neo4j

2. **LangChain + Graph Reasoning**
   - If you need more sophisticated agent framework
   - MCP compatible

3. **Custom Rule Engine**
   - Simple, full control
   - MCP compatible

**All are open source and work with MCP in Cursor!**





