# **8. Technology Stack & Orchestration**

## **8.0 Implementation Overview**

This section describes Chrystallum's technical implementation: the runtime environment, technology choices, orchestration patterns, and critical operational guidelines for safe system behavior.

**Key Components:**
- **Neo4j 4.x+**: Property graph database with APOC extensions
- **LangGraph**: Multi-agent orchestration framework (Python-based)
- **Python 3.11+**: Implementation language
- **LLM Integration**: OpenAI/Anthropic for extraction phase
- **Frontend**: React + Cytoscape.js for graph visualization

**Implementation Philosophy:**
- **Two-stage architecture**: LLM extraction â†’ deterministic validation (Section 1.2.1)
- **Evidence-aware**: Complete provenance chains for all knowledge
- **Safety-first**: Explicit identifier handling rules prevent data corruption

---

## **8.1 Core Technology Stack**

### **8.1.1 Neo4j Property Graph Database**

**Version:** Neo4j 4.x or later (5.x recommended)

**Required Extensions:**
- **APOC**: Utilities for graph algorithms, data integration, and schema operations
- **GDS (Graph Data Science)**: For network analysis and similarity computations (optional)

**Key Features Used:**
- Property graphs with typed relationships
- Cypher query language
- Multi-property indexes
- Full-text search
- Uniqueness constraints
- Temporal properties (ISO 8601 dates)

**Performance Considerations:**
- Index all frequently queried properties (qid, entity_id, fast_id, lcc_code)
- Use relationship direction intentionally (BROADER_THAN only, not NARROWER_THAN)
- Batch writes for bulk operations (use APOC batch functions)

**Connection Details:**
```python
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]
```

---

### **8.1.2 LangGraph Multi-Agent Orchestration**

**Purpose:** Coordinate multiple specialized agents for collaborative knowledge construction.

**Architecture Pattern:**
```
User Query â†’ CoordinatorAgent â†’ SubjectAgent â†’ EntityAgent â†’ Neo4j Write
                â†“                    â†“              â†“
           Route by LCC      Extract entities  Validate/Resolve
```

**Core LangGraph Concepts:**
- **Nodes**: Individual agents (SubjectAgent, EntityAgent, CoordinatorAgent)
- **Edges**: Communication channels between agents
- **State**: Shared context across agent invocations
- **Conditional Edges**: Routing logic based on state

**Example LangGraph Workflow:**
```python
from langgraph.graph import StateGraph, END

# Define workflow graph
workflow = StateGraph()

# Add agent nodes
workflow.add_node("coordinator", coordinator_agent)
workflow.add_node("subject_agent", subject_agent)
workflow.add_node("entity_agent", entity_agent)
workflow.add_node("neo4j_writer", neo4j_writer)

# Add edges
workflow.add_edge("coordinator", "subject_agent")
workflow.add_edge("subject_agent", "entity_agent")
workflow.add_edge("entity_agent", "neo4j_writer")
workflow.add_edge("neo4j_writer", END)

# Set entry point
workflow.set_entry_point("coordinator")

# Compile workflow
app = workflow.compile()
```

---

### **8.1.3 Python Implementation Environment**

**Version:** Python 3.11 or later

**Required Libraries:**
```python
# Core dependencies
neo4j>=5.0.0              # Neo4j driver
langgraph>=0.0.20         # Multi-agent orchestration
langchain>=0.1.0          # LLM integration
openai>=1.0.0             # OpenAI API (or anthropic for Claude)

# Data processing
pandas>=2.0.0             # CSV/data manipulation
pydantic>=2.0.0           # Data validation

# Utilities
python-dotenv>=1.0.0      # Environment variables
loguru>=0.7.0             # Logging

# Optional
requests>=2.31.0          # HTTP requests (Wikidata API)
spacy>=3.7.0              # NLP (if needed for extraction enhancement)
```

**Virtual Environment Setup:**
```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # Unix/macOS
.venv\\Scripts\\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## **8.2 LangGraph Workflow Architecture**

### **8.2.1 Agent Definitions**

**CoordinatorAgent:**
- **Purpose**: Routes queries to appropriate subject domain agents
- **Inputs**: User query, extracted entities/relationships
- **Outputs**: Routing decision (LCC code determination)
- **LLM Role**: Classify query into LCC domain

**SubjectAgent:**
- **Purpose**: Extract subject-specific knowledge from sources
- **Inputs**: Source text, domain context (LCC subdivision)
- **Outputs**: Structured entity/relationship proposals
- **LLM Role**: Extract entities, dates, relationships from unstructured text

**EntityAgent:**
- **Purpose**: Validate and resolve entities to canonical identifiers
- **Inputs**: Proposed entities from SubjectAgent
- **Outputs**: Validated entities with QIDs, authority IDs
- **LLM Role**: None (tool-based resolution only - Wikidata API, FAST lookup)

**ReasoningAgent** (optional):
- **Purpose**: Validate logical consistency of proposed claims
- **Inputs**: Claim structure, supporting evidence
- **Outputs**: Validation result, confidence score
- **LLM Role**: None (deterministic reasoning rules)

---

### **8.2.2 State Management**

**Shared State Structure:**
```python
from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    query: str                          # Original user query
    lcc_code: Optional[str]             # Classified LCC domain
    subject_concept_id: Optional[str]   # SubjectConcept node ID
    
    # Extracted entities (from SubjectAgent)
    proposed_entities: List[Dict]       # [{label, type, properties}, ...]
    proposed_relationships: List[Dict]  # [{from, to, type, properties}, ...]
    
    # Validated entities (from EntityAgent)
    validated_entities: List[Dict]      # [{label, qid, fast_id, ...}, ...]
    
    # Claims (from ReasoningAgent)
    claims: List[Dict]                  # [{claim_id, text, confidence}, ...]
    
    # Metadata
    agent_history: List[str]            # Agent execution trace
    errors: List[str]                   # Error messages
```

---

### **8.2.3 Agent Communication Pattern**

```python
def coordinator_agent(state: AgentState) -> AgentState:
    """Route query to appropriate subject domain."""
    query = state["query"]
    
    # LLM classifies query into LCC domain
    lcc_code = classify_query_to_lcc(query)
    
    # Update state
    state["lcc_code"] = lcc_code
    state["agent_history"].append("coordinator: classified to " + lcc_code)
    
    return state

def subject_agent(state: AgentState) -> AgentState:
    """Extract entities and relationships from source text."""
    lcc_code = state["lcc_code"]
    query = state["query"]
    
    # LLM extracts structured data
    extractions = extract_entities_and_relationships(query, lcc_code)
    
    # Update state
    state["proposed_entities"] = extractions["entities"]
    state["proposed_relationships"] = extractions["relationships"]
    state["agent_history"].append(f"subject_agent: extracted {len(extractions['entities'])} entities")
    
    return state

def entity_agent(state: AgentState) -> AgentState:
    """Validate and resolve entities to canonical identifiers."""
    proposed = state["proposed_entities"]
    validated = []
    
    for entity in proposed:
        # Tool-based resolution (NO LLM)
        qid = wikidata_lookup(entity["label"])
        fast_id = fast_lookup(entity["label"], entity["type"])
        
        validated.append({
            **entity,
            "qid": qid,
            "fast_id": fast_id,
            "validated": True
        })
    
    # Update state
    state["validated_entities"] = validated
    state["agent_history"].append(f"entity_agent: validated {len(validated)} entities")
    
    return state
```

---

## **8.3 Multi-Agent Coordination Patterns**

### **8.3.1 Sequential Processing**

**Pattern**: Execute agents in order (coordinator â†’ subject â†’ entity â†’ writer)

**Use Case**: Standard entity extraction and resolution

```python
workflow.add_edge("coordinator", "subject_agent")
workflow.add_edge("subject_agent", "entity_agent")
workflow.add_edge("entity_agent", "neo4j_writer")
```

---

### **8.3.2 Conditional Routing**

**Pattern**: Route to different agents based on state

**Use Case**: Route to specialist agents based on LCC classification

```python
def route_by_lcc(state: AgentState) -> str:
    """Route to specialist agent based on LCC code."""
    lcc = state["lcc_code"]
    
    if lcc.startswith("D"):  # History
        return "history_specialist"
    elif lcc.startswith("J"):  # Political science
        return "political_specialist"
    elif lcc.startswith("N"):  # Fine arts
        return "art_specialist"
    else:
        return "general_agent"

# Add conditional edge
workflow.add_conditional_edges(
    "coordinator",
    route_by_lcc,
    {
        "history_specialist": "history_agent",
        "political_specialist": "political_agent",
        "art_specialist": "art_agent",
        "general_agent": "subject_agent"
    }
)
```

---

### **8.3.3 Parallel Processing**

**Pattern**: Execute multiple agents simultaneously

**Use Case**: Validate entity and check for duplicates in parallel

```python
workflow.add_edge("subject_agent", ["entity_validator", "duplicate_checker"])
workflow.add_edge(["entity_validator", "duplicate_checker"], "merge_results")
```

---

### **8.3.4 Feedback Loops**

**Pattern**: Agent can route back to earlier stage

**Use Case**: Entity resolution fails â†’ request more context from subject agent

```python
def check_validation_status(state: AgentState) -> str:
    """Check if entities validated successfully."""
    if state.get("errors"):
        return "request_more_context"
    else:
        return "proceed_to_writer"

workflow.add_conditional_edges(
    "entity_agent",
    check_validation_status,
    {
        "request_more_context": "subject_agent",  # Loop back
        "proceed_to_writer": "neo4j_writer"       # Continue
    }
)
```

---

## **8.4 LLM Integration Patterns**

### **8.4.1 Extraction Phase (LLM-Powered)**

**Purpose**: Extract structured data from unstructured text

**LLM Role**: Natural language understanding, entity recognition, relationship extraction

**Example:**
```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def extract_entities_and_relationships(text: str, domain: str) -> Dict:
    """Extract structured data from text using LLM."""
    
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a historical research assistant. Extract entities and relationships from the provided text."),
        ("user", f"Domain: {domain}\\n\\nText: {text}\\n\\nExtract: 1) People (name, role), 2) Places (name, type), 3) Events (name, date), 4) Relationships (who did what to whom)")
    ])
    
    response = llm.invoke(prompt.format_messages())
    
    # Parse LLM response into structured format
    parsed = parse_llm_extraction(response.content)
    
    return parsed
```

**âš ï¸ CRITICAL**: Never pass system identifiers (QIDs, FAST IDs, LCC codes) to LLM. See Section 8.5.

---

### **8.4.2 Resolution Phase (Tool-Based, NO LLM)**

**Purpose**: Resolve entity labels to canonical identifiers

**LLM Role**: NONE - use deterministic API lookups

**Example:**
```python
def wikidata_lookup(entity_label: str) -> Optional[str]:
    """Resolve entity label to Wikidata QID using API (NO LLM)."""
    
    # Use Wikidata search API
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": entity_label,
        "language": "en",
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    results = response.json().get("search", [])
    
    if results:
        return results[0]["id"]  # Return QID as atomic string
    else:
        return None

def fast_lookup(subject_label: str, subject_type: str) -> Optional[str]:
    """Resolve subject to FAST ID using lookup table (NO LLM)."""
    
    # Use FAST subject headings lookup (from CSV or API)
    fast_mapping = load_fast_mapping()  # Pre-loaded CSV
    
    key = (subject_label.lower(), subject_type)
    fast_id = fast_mapping.get(key)
    
    return fast_id  # Return as atomic string
```

**âš ï¸ CRITICAL**: These functions return **atomic strings** (QIDs, FAST IDs). Never pass these to LLMs. See Section 8.5.

---

### **8.4.3 LLM Degradation Handling**

**Issue**: LLM responses can degrade over time due to model updates, prompt changes, or service issues.

**Mitigation Strategies:**
1. **Version locking**: Pin LLM model versions in production
2. **Response validation**: Schema validation (Pydantic) on all LLM outputs
3. **Fallback mechanisms**: If LLM fails, route to human review queue
4. **Monitoring**: Track extraction accuracy over time, alert on degradation

**Reference**: See `md/CIDOC/Reference/LLM_Degradation.md` for detailed analysis

---

## **8.5 Identifier Handling & LLM Safety** ðŸ”´ **CRITICAL**

### **8.5.1 The Tokenization Problem**

**CRITICAL ISSUE**: System identifiers (FAST IDs, LCC codes, MARC codes, Pleiades IDs, Wikidata QIDs) **fragment when tokenized by LLMs**, causing silent data corruption.

**Example of Fragmentation:**
```python
# âŒ DANGER - Passing FAST ID to LLM:
fast_id = "1145002"  # Technology (7-digit atomic identifier)
llm_response = llm.ask(f"What subject is FAST ID {fast_id}?")

# LLM tokenizes the input:
#   Input: "What subject is FAST ID 1145002?"
#   Tokens: ["What", "subject", "is", "FAST", "ID", "114", "500", "2", "?"]
#                                                      ^^^^^^^^^^^^^^^^^^^
#                                                      âŒ FRAGMENTED!

# LLM cannot recognize "1145002" as a single identifier
# Lookup fails, backbone alignment breaks silently

# âŒ Similar fragmentation for other identifiers:
lcc_code = "DG241-269"  # Roman history
# Tokens: ["DG", "241", "-", "269"]  âŒ FRAGMENTED!

marc_code = "sh85115058"  # Subject heading
# Tokens: ["sh", "851", "150", "58"]  âŒ FRAGMENTED!

pleiades_id = "423025"  # Rome
# Tokens: ["423", "025"]  âŒ FRAGMENTED!

qid = "Q17193"  # Roman Republic
# Tokens: ["Q", "17", "19", "3"]  âŒ FRAGMENTED!
```

**Consequence**: If agents accidentally pass these identifiers to LLMs:
- FAST backbone alignment fails â†’ subject classification breaks
- Pleiades lookups fail â†’ ancient geography breaks
- MARC integration fails â†’ bibliographic links break
- QID lookups fail â†’ entity resolution breaks
- **Silent failures** - no obvious errors, just bad data

---

### **8.5.2 The Two-Stage Processing Pattern** âœ…

**CORRECT PATTERN**: LLM extracts natural language labels â†’ Tools resolve to atomic identifiers

```python
# âœ… CORRECT - Two-stage processing:

# Stage 1: LLM extracts natural language labels
text = "During the Roman Republic, Rome was the capital"
extracted = llm.extract({
    "period": "Roman Republic",    # âœ… Natural language (LLM can process)
    "place": "Rome"                 # âœ… Natural language (LLM can process)
})

# Stage 2: Tools resolve labels to atomic identifiers (NO LLM)
resolved = {
    "period": {
        "label": "Roman Republic",                      # âœ… Human-readable
        "qid": wikidata_tool.lookup("Roman Republic"),  # "Q17193" (atomic)
        "fast_id": fast_tool.lookup("Roman Republic")   # "1411640" (atomic)
    },
    "place": {
        "label": "Rome",                           # âœ… Human-readable
        "qid": wikidata_tool.lookup("Rome"),       # "Q220" (atomic)
        "pleiades_id": pleiades_tool.lookup("Rome") # "423025" (atomic)
    }
}

# Stage 3: Store both formats in Neo4j
graph.create_node({
    "label": "Roman Republic",      # âœ… Natural (for display, search)
    "qid": "Q17193",                # âŒ Atomic (for lookups, NEVER pass to LLM)
    "fast_id": "1411640"            # âŒ Atomic (for backbone, NEVER pass to LLM)
})
```

---

### **8.5.3 Identifier Atomicity Rules**

**Golden Rule**: **NEVER pass atomic identifiers to LLMs for interpretation.**

| Identifier Type | Example | LLM Safe? | How to Handle | Tokenization Risk |
|-----------------|---------|-----------|---------------|-------------------|
| **Period name** | "Roman Republic" | âœ… YES | Extract with LLM | âœ… None (designed for it) |
| **Date text** | "49 BCE" | âœ… YES | Extract with LLM, convert with tool | âœ… None |
| **Place name** | "Rome" | âœ… YES | Extract with LLM | âœ… None |
| **Subject heading** | "Political science" | âœ… YES | Extract with LLM | âœ… None |
| | | | | |
| **Wikidata QID** | **"Q17193"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **FAST ID** | **"1145002"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **LCC code (range)** | **"DG241-269"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **LCC code (simple)** | **"T"** | **âŒ NO** | **Tool lookup only** | ðŸŸ¡ **MEDIUM** |
| **MARC code** | **"sh85115058"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **Pleiades ID** | **"423025"** | **âŒ NO** | **Tool lookup only** | ðŸ”´ **HIGH** |
| **GeoNames ID** | **"2643743"** | **âŒ NO** | **Tool lookup only** | ðŸŸ¡ **MEDIUM** |
| **ISO 8601 date** | **"-0753-01-01"** | **âŒ NO** | **Tool-formatted only** | ðŸ”´ **HIGH** |

---

### **8.5.4 Implementation Patterns**

#### **Pattern 1: Entity Extraction (Correct)**

```python
def extract_and_resolve_entities(source_text: str) -> List[Dict]:
    """Extract entities from text and resolve to canonical identifiers."""
    
    # Stage 1: LLM extracts natural language
    llm_prompt = f"""
    Extract historical entities from this text. For each entity, provide:
    - label: The entity's name (e.g., "Julius Caesar", "Rome")
    - type: Entity type (Person, Place, Event, etc.)
    
    Text: {source_text}
    
    Return JSON list of entities.
    """
    
    # âœ… GOOD: LLM processes natural language only
    raw_entities = llm.extract(llm_prompt)
    
    # Stage 2: Tools resolve to atomic identifiers (NO LLM)
    resolved_entities = []
    for entity in raw_entities:
        label = entity["label"]      # âœ… Natural language string
        entity_type = entity["type"]
        
        # âœ… GOOD: Tool-based resolution (NO LLM involved)
        qid = wikidata_api.search(label, entity_type)  # Returns atomic string
        fast_id = fast_api.lookup(label, entity_type)  # Returns atomic string
        
        resolved_entities.append({
            "label": label,           # âœ… Natural (human-readable)
            "qid": qid,               # âŒ Atomic (machine lookup key)
            "fast_id": fast_id,       # âŒ Atomic (machine lookup key)
            "entity_type": entity_type
        })
    
    return resolved_entities
```

#### **Pattern 2: Subject Classification (Correct)**

```python
def classify_query_to_lcc(query: str) -> str:
    """Classify user query into LCC domain using LLM."""
    
    # LLM classifies using NATURAL LANGUAGE descriptions
    llm_prompt = f"""
    Classify this query into a Library of Congress Classification domain.
    
    Query: {query}
    
    Choose from (PROVIDE DESCRIPTIONS, NOT CODES):
    - History: Events, people, civilizations, wars
    - Political Science: Governance, institutions, law
    - Fine Arts: Painting, sculpture, architecture
    - Philosophy: Ethics, logic, metaphysics
    - Literature: Poetry, novels, drama
    
    Return: The domain NAME (not the code).
    """
    
    # âœ… GOOD: LLM processes natural language domain names
    domain_name = llm.extract(llm_prompt)  # Returns "History", not "D"
    
    # Tool converts name to LCC code (NO LLM)
    lcc_code = lcc_mapping[domain_name]    # "History" â†’ "D"
    
    return lcc_code  # Returns atomic string "D" (NEVER pass back to LLM)
```

#### **Pattern 3: Backbone Alignment (Correct)**

```python
def align_entity_to_backbone(entity_label: str, entity_type: str) -> Dict:
    """Align entity to FAST/LCC/LCSH backbone standards."""
    
    # âœ… GOOD: All lookups use natural language labels, not codes
    fast_id = fast_api.lookup(entity_label, entity_type)
    lcc_code = lcc_api.classify(entity_label, entity_type)
    lcsh_heading = lcsh_api.lookup(entity_label)
    marc_code = marc_api.lookup(entity_label)
    
    # Return atomic identifiers (NEVER pass these to LLM)
    return {
        "fast_id": fast_id,        # "1145002" - atomic string
        "lcc_code": lcc_code,      # "DG241-269" - atomic string
        "lcsh_heading": lcsh_heading,  # "Rome--History--Republic" - natural language (OK)
        "marc_code": marc_code     # "sh85115058" - atomic string
    }
```

---

### **8.5.5 Validation Checklist**

**Before sending ANY text to an LLM, verify:**

- [ ] No QIDs (Q followed by digits)
- [ ] No FAST IDs (7-digit numbers)
- [ ] No LCC codes (letters + numbers with ranges like "DG241-269")
- [ ] No MARC codes (sh + 8 digits)
- [ ] No Pleiades IDs (6-digit numbers in geographic context)
- [ ] No GeoNames IDs (5-8 digit numbers in geographic context)
- [ ] No ISO dates (YYYY-MM-DD format, especially with negative years)
- [ ] No dates without delimiters (YYYYMMDD)

**If any detected â†’ Remove from prompt and use tool lookup instead!**

---

### **8.5.6 Validation Implementation**

```python
import re
from typing import List, Dict

class IdentifierValidator:
    """Validate prompts for atomic identifiers before LLM calls."""
    
    PATTERNS = {
        "qid": r"\\bQ\\d+\\b",                          # Q17193
        "fast_id": r"\\b\\d{7}\\b",                     # 1145002
        "lcc_range": r"\\b[A-Z]{1,2}\\d+[-]\\d+\\b",   # DG241-269
        "marc": r"\\bsh\\d{8}\\b",                      # sh85115058
        "pleiades": r"\\b\\d{6}\\b",                    # 423025
        "iso_date": r"-?\\d{4}-\\d{2}-\\d{2}",         # -0509-01-01
    }
    
    def check_prompt(self, prompt: str) -> Dict:
        """Check prompt for atomic identifiers."""
        issues = []
        
        for id_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, prompt)
            if matches:
                issues.append({
                    "type": id_type,
                    "matches": matches,
                    "risk": "HIGH",
                    "message": f"Found {id_type} in prompt: {matches}. Remove before LLM call."
                })
        
        return {
            "is_safe": len(issues) == 0,
            "issues": issues,
            "summary": f"Found {len(issues)} identifier safety issues" if issues else "Prompt is safe"
        }

# Usage example
validator = IdentifierValidator()

# Before LLM call:
prompt = "Tell me about Q17193"
result = validator.check_prompt(prompt)

if not result['is_safe']:
    raise ValueError(f"Prompt contains atomic identifiers: {result['summary']}")
    # Or: Clean prompt and use tool lookup instead
```

---

### **8.5.7 Storage Format Examples**

#### **Period Entity (With Both Formats)**

```json
{
  "label": "Roman Republic",           // âœ… Natural (LLM extracts)
  "qid": "Q17193",                     // âŒ Atomic (tool resolves)
  "fast_id": "1411640",                // âŒ Atomic (tool resolves)
  "lcc_code": "DG241-269",             // âŒ Atomic (tool resolves)
  "lcsh_heading": "Rome--History--Republic",  // âœ… Natural (human-readable)
  "marc_code": "sh85115058",           // âŒ Atomic (tool resolves)
  "start_date_text": "509 BCE",        // âœ… Natural (LLM extracts)
  "start_date_iso": "-0509-01-01",    // âŒ Atomic (tool formats)
  "start_year": -509                   // âœ… Numeric (calculations)
}
```

#### **Place Entity (With Both Formats)**

```json
{
  "label": "Rome",                     // âœ… Natural (LLM extracts)
  "qid": "Q220",                       // âŒ Atomic (tool resolves)
  "pleiades_id": "423025",             // âŒ Atomic (tool resolves)
  "geonames_id": "3169070",            // âŒ Atomic (tool resolves)
  "latitude": 41.9028,                 // âœ… Numeric (not string!)
  "longitude": 12.4964,                // âœ… Numeric (not string!)
  "description": "Capital of the Roman Empire"  // âœ… Natural (LLM extracts)
}
```

---

### **8.5.8 Common Anti-Patterns (AVOID)**

#### **âŒ Anti-Pattern 1: Passing QID to LLM**

```python
# âŒ WRONG - QID gets tokenized and fragmented
qid = "Q17193"
llm_response = llm.ask(f"What period is {qid}?")
# Tokens: ["What", "period", "is", "Q", "17", "19", "3", "?"]
# Result: LLM doesn't recognize QID, gives garbage response

# âœ… CORRECT - Use tool lookup
qid = "Q17193"
wikidata_data = wikidata_api.get_entity(qid)  # Tool-based, no LLM
period_label = wikidata_data["labels"]["en"]["value"]
```

#### **âŒ Anti-Pattern 2: Asking LLM to Generate FAST IDs**

```python
# âŒ WRONG - LLM cannot generate valid FAST IDs
subject_text = "political science"
llm_response = llm.ask(f"What is the FAST ID for {subject_text}?")
# LLM might hallucinate: "1145002" (could be wrong)

# âœ… CORRECT - Use FAST API or lookup table
fast_id = fast_api.lookup(subject_text)  # Authoritative source
```

#### **âŒ Anti-Pattern 3: Constructing LLM Prompts with Identifiers**

```python
# âŒ WRONG - Identifier in prompt gets tokenized
fast_id = "1145002"
lcc_code = "DG241-269"
llm_prompt = f"Classify this entity with FAST ID {fast_id} and LCC code {lcc_code}"
# Tokenization breaks both identifiers

# âœ… CORRECT - Use labels in prompts, identifiers for lookups
label = "Roman history"
llm_prompt = f"Classify this entity about {label}"
# After LLM response, use tools to get FAST/LCC
```

---

### **8.5.9 Emergency Decision Tree**

Is this data being processed?  
â”‚  
â”œâ”€ Natural language text? (period name, date text, place name)  
â”‚  â””â”€ âœ… LLM can extract it  
â”‚  
â”œâ”€ System identifier? (QID, FAST ID, LCC, MARC, Pleiades, GeoNames)  
â”‚  â””â”€ âŒ Tool resolves it, NEVER pass to LLM  
â”‚  
â”œâ”€ ISO 8601 date?  
â”‚  â””â”€ âŒ Tool formats it, NEVER pass to LLM  
â”‚  
â”œâ”€ Numeric value? (year, coordinate)  
â”‚  â””â”€ âœ… Store as number, use in calculations  
â”‚  
â””â”€ Unsure?  
   â””â”€ Default to âŒ Tool handling (safer to over-protect)

---

### **8.5.10 Summary: Identifier Safety Rules**

| âœ… LLM Can Process | âŒ LLM Cannot Process (Atomic) |
|-------------------|--------------------------------|
| Period names | Wikidata QIDs |
| Place names | FAST IDs |
| Date text (BCE/CE) | LCC codes |
| Subject headings (LCSH) | MARC codes |
| Descriptions | Pleiades IDs |
| Natural language | GeoNames IDs |
| | ISO 8601 dates |

**Remember:** When in doubt, use tools! It's always safer to over-protect identifiers than risk tokenization.

**For complete reference, see:** Appendix M (Identifier Safety Reference)

---

## **8.6 Federation Dispatcher and Backlink Control Plane**

All Wikidata statement ingestion MUST use a deterministic dispatcher keyed by:
- `mainsnak.datatype`
- `mainsnak.datavalue.type` (`value_type`)

This control plane separates topology, federation identity, and literal attributes.
No statement may bypass dispatcher routing.

### **8.6.1 Dispatcher Route Matrix (Normative)**

| Pair (`datatype + value_type`) | Route | Required Action |
|---|---|---|
| `wikibase-item + wikibase-entityid` | `edge_candidate` | Candidate graph edge write (subject to schema/class checks) |
| `external-id + string` | `federation_id` | Store namespaced external ID and run dedupe/merge check |
| `time + time` with precision >= threshold | `temporal_anchor` | Parse and anchor to temporal backbone |
| `time + time` with precision < threshold | `temporal_uncertain` | Route to uncertain bucket, do not treat as precise anchor |
| `string + string`, `monolingualtext + monolingualtext`, `url + string` | `node_property` | Store as literal/content attributes |
| `quantity + quantity` | `measured_attribute` | Store normalized numeric payload |
| `globe-coordinate + globecoordinate` | `geo_attribute` | Route to geographic handler |
| `commonsMedia + string` | `media_reference` | Store media reference metadata |
| missing `datavalue` | `quarantine_missing_datavalue` | Quarantine with reason |
| unsupported pair | `quarantine_unsupported_pair` | Quarantine with reason |

### **8.6.2 Temporal Precision Gate**

Use Wikidata precision codes:
- `9` year
- `10` month
- `11` day

Default policy:
- minimum precision for `temporal_anchor` is `9` (year)
- lower precision routes to `temporal_uncertain`

No temporal statement is silently dropped.

### **8.6.3 Class Controls and Backlink Admission**

For reverse-link expansion:
1. Start from reverse triples `?source ?property ?target`.
2. Resolve source classes via `P31`.
3. Expand class lineage via bounded `P279` walk.
4. Admit only schema-allowlisted classes.
5. Optionally reject explicit denylisted classes (`P31` denylist).

### **8.6.4 Frontier Eligibility Guard (Anti-Hairball Rule)**

Accepted nodes can still be excluded from traversal frontier.

Default exclusion rules:
- `edge_candidate_count == 0` -> exclude (`no_edge_candidates`)
- `literal_heavy_ratio > 0.80` -> exclude (`literal_heavy`)

These exclusions affect recursion and frontier growth, not node retention.

### **8.6.5 Provenance and Safety Requirements**

Every materialized backlink edge MUST include:
- `source_system`
- `source_mode`
- `source_property`
- `retrieved_at`

Every run report MUST emit:
- route counts
- quarantine reason counts
- unsupported pair rate
- unresolved class rate
- frontier eligible/excluded counts

Silent drops are prohibited.

### **8.6.6 Operational Reference**

Canonical tooling:
- `scripts/tools/wikidata_backlink_harvest.py`
- `scripts/tools/wikidata_backlink_profile.py`
- `JSON/wikidata/backlinks/README.md`

Operational contract details are defined in Appendix K.4 through K.6.

---

# **9. Workflows & Agent Coordination**

## **9.0 Workflow Overview**

This section describes the operational workflows that govern how agents collaborate to construct, validate, and promote knowledge in Chrystallum.

**Core Workflows:**
1. **Claim Generation**: Extract claims from source texts
2. **Claim Review**: Multi-agent validation of claims
3. **Consensus Building**: Resolve conflicting claims from multiple agents
4. **Claim Promotion**: Convert validated claims to canonical graph

**Workflow Properties:**
- **Asynchronous**: Agents operate concurrently on different tasks
- **Event-driven**: State changes trigger agent actions
- **Auditable**: Complete provenance trail for all operations
- **Idempotent**: Safe to re-run workflows without duplication

---

## **9.1 Claim Generation Workflow**

### **9.1.1 Workflow Steps**

```
Source Text â†’ SubjectAgent â†’ EntityAgent â†’ ClaimAgent â†’ Neo4j (Claim nodes)
                  â†“              â†“             â†“
            (Extract)      (Validate)    (Structure)
```

**Step 1: Extract Entities and Relationships (SubjectAgent)**
- **Input**: Source text (e.g., paragraph from Plutarch)
- **LLM Role**: Extract entities, dates, relationships from natural language
- **Output**: Proposed entities and relationships (labels only, no identifiers yet)

**Step 2: Validate and Resolve (EntityAgent)**
- **Input**: Proposed entities from Step 1
- **Tool Role**: Resolve labels to QIDs, FAST IDs, check for existing entities
- **Output**: Validated entities with canonical identifiers

**Step 3: Structure Claims (ClaimAgent)**
- **Input**: Validated entities and relationships
- **Tool Role**: Create Claim nodes with provenance properties
- **Output**: Structured claims with cipher (content-addressable hash)

**Step 4: Write to Neo4j**
- **Input**: Structured claims
- **Output**: Claim nodes, ProposedEdge nodes, ReasoningTrace nodes

---

### **9.1.2 Implementation Example**

```python
from typing import Dict, List

def claim_generation_workflow(source_text: str, source_work_qid: str, agent_id: str) -> Dict:
    """Generate claims from source text."""
    
    # Step 1: Extract entities and relationships (LLM)
    raw_extractions = subject_agent.extract(source_text)
    # Returns: {entities: [{label, type}, ...], relationships: [{from, to, type}, ...]}
    
    # Step 2: Validate and resolve (Tools, NO LLM)
    validated_entities = entity_agent.validate(raw_extractions["entities"])
    # Returns: [{label, qid, fast_id, entity_type}, ...]
    
    # Step 3: Structure claims
    claims = []
    for rel in raw_extractions["relationships"]:
        # Build claim structure
        claim = {
            "claim_text": f"{rel['from']} {rel['type']} {rel['to']}",
            "subject_entity_qid": find_qid(rel["from"], validated_entities),
            "object_entity_qid": find_qid(rel["to"], validated_entities),
            "relationship_type": rel["type"],
            "source_work_qid": source_work_qid,
            "source_agent_id": agent_id,
            "timestamp": datetime.now().isoformat(),
            "status": "proposed",  # Awaiting review
            "confidence": 0.7  # Initial confidence
        }
        
        # Generate content-addressable cipher
        claim["cipher"] = generate_cipher(claim)
        
        claims.append(claim)
    
    # Step 4: Write to Neo4j
    for claim in claims:
        neo4j_writer.create_claim(claim)
        
        # Create ProposedEdge for relationship
        neo4j_writer.create_proposed_edge(
            relationship_type=claim["relationship_type"],
            source_entity_id=claim["subject_entity_qid"],
            target_entity_id=claim["object_entity_qid"],
            claim_id=claim["claim_id"]
        )
        
        # Create ReasoningTrace for explainability
        neo4j_writer.create_reasoning_trace(
            agent_id=agent_id,
            claim_id=claim["cipher"],
            source_text=source_text,
            reasoning_steps=[
                "Extracted entities from source",
                "Resolved to Wikidata QIDs",
                "Structured as relationship claim"
            ]
        )
    
    return {
        "claims_generated": len(claims),
        "ciphers": [c["cipher"] for c in claims]
    }
```

---

## **9.2 Claim Review Workflow**

### **9.2.1 Workflow Steps**

```
Claim (proposed) â†’ ReviewerAgent â†’ Review Node â†’ Consensus Calculation â†’ Status Update
                       â†“               â†“                â†“
                  (Evaluate)      (Record)        (Aggregate)
```

**Step 1: Select Claims for Review**
- Query Neo4j for claims with `status="proposed"` and insufficient reviews (< 3)

**Step 2: Agent Review (ReviewerAgent)**
- **Input**: Claim structure, source text, existing evidence
- **LLM Role** (optional): Evaluate claim plausibility, check for fallacies
- **Tool Role**: Check against existing knowledge, verify sources
- **Output**: Review verdict (support/challenge/uncertain), confidence, reasoning

**Step 3: Record Review**
- Create Review node linked to Claim
- Record verdict, confidence, fallacies detected, reasoning summary

**Step 4: Calculate Consensus**
- Aggregate all reviews for this claim
- Calculate consensus score (weighted Bayesian average)
- Update claim status based on thresholds

**Step 5: Update Claim Status**
- `validated` (consensus â‰¥ 0.8 + 70% support)
- `disputed` (consensus â‰¥ 0.5 but mixed reviews)
- `rejected` (consensus < 0.5)

---

### **9.2.2 Implementation Example**

```python
def claim_review_workflow(claim_id: str, reviewer_agent_id: str) -> Dict:
    """Review existing claim and update consensus."""
    
    # Step 1: Retrieve claim from Neo4j
    claim = neo4j_reader.get_claim(claim_id)
    
    if not claim:
        return {"error": "Claim not found"}
    
    # Step 2: Agent evaluates claim
    review_result = reviewer_agent.evaluate_claim(
        claim_text=claim["text"],
        subject_qid=claim["subject_entity_qid"],
        object_qid=claim["object_entity_qid"],
        source_text=claim["passage_text"]
    )
    
    # Step 3: Record review in Neo4j
    review = {
        "review_id": generate_uuid(),
        "agent_id": reviewer_agent_id,
        "claim_id": claim_id,
        "timestamp": datetime.now().isoformat(),
        "verdict": review_result["verdict"],  # "support", "challenge", "uncertain"
        "confidence": review_result["confidence"],  # 0.0 - 1.0
        "reasoning_summary": review_result["reasoning"],
        "fallacies_detected": review_result.get("fallacies", [])
    }
    
    neo4j_writer.create_review(review)
    
    # Step 4: Calculate consensus
    all_reviews = neo4j_reader.get_reviews_for_claim(claim_id)
    consensus = calculate_consensus(all_reviews)
    
    # Step 5: Update claim status
    new_status = determine_status(consensus, all_reviews)
    
    neo4j_writer.update_claim(claim_id, {
        "consensus_score": consensus,
        "review_count": len(all_reviews),
        "status": new_status,
        "last_reviewed": datetime.now().isoformat()
    })
    
    return {
        "review_id": review["review_id"],
        "verdict": review["verdict"],
        "consensus_score": consensus,
        "new_status": new_status,
        "total_reviews": len(all_reviews)
    }

def calculate_consensus(reviews: List[Dict]) -> float:
    """Calculate weighted Bayesian consensus score."""
    if not reviews:
        return 0.5  # Neutral prior
    
    # Weight each review by agent confidence and expertise
    weighted_sum = 0
    weight_total = 0
    
    for review in reviews:
        weight = review.get("weight", 1.0)
        confidence = review["confidence"]
        
        # Convert verdict to numeric value
        if review["verdict"] == "support":
            value = 1.0
        elif review["verdict"] == "challenge":
            value = 0.0
        else:  # uncertain
            value = 0.5
        
        weighted_sum += value * confidence * weight
        weight_total += weight
    
    # Bayesian average with prior
    prior_weight = 1.0
    prior_value = 0.5
    
    consensus = (weighted_sum + prior_weight * prior_value) / (weight_total + prior_weight)
    
    return consensus

def determine_status(consensus: float, reviews: List[Dict]) -> str:
    """Determine claim status from consensus score and review distribution."""
    if len(reviews) < 3:
        return "proposed"  # Need minimum reviews
    
    # Count support vs challenge
    support_count = sum(1 for r in reviews if r["verdict"] == "support")
    total_count = len(reviews)
    support_ratio = support_count / total_count if total_count > 0 else 0
    
    # Apply thresholds
    if consensus >= 0.8 and support_ratio >= 0.7:
        return "validated"
    elif consensus >= 0.5:
        return "disputed"
    else:
        return "rejected"
```

---

## **9.3 Consensus Building Workflow**

### **9.3.1 Synthesis for Conflicting Claims**

When multiple agents propose conflicting claims about the same subject:

```
ClaimA (Agent1) â”€â”
ClaimB (Agent2) â”€â”¼â”€> SynthesisAgent â†’ Synthesis Node â†’ Resolved Claim
ClaimC (Agent3) â”€â”˜
```

**Example Conflict:**
- Agent1: "Caesar crossed Rubicon on January 10, 49 BCE"
- Agent2: "Caesar crossed Rubicon on January 11, 49 BCE"
- Agent3: "Caesar crossed Rubicon in early January 49 BCE"

**Resolution:**
- SynthesisAgent creates Synthesis node
- Records all conflicting claims
- Consensus method: Weighted average of dates + uncertainty annotation
- Result: "Caesar crossed Rubicon circa January 10-11, 49 BCE" (confidence 0.85)

---

### **9.3.2 Implementation Example**

```python
def synthesis_workflow(claim_ids: List[str], synthesis_agent_id: str) -> Dict:
    """Resolve conflicting claims through synthesis."""
    
    # Retrieve all conflicting claims
    claims = [neo4j_reader.get_claim(cid) for cid in claim_ids]
    
    # Analyze conflict type
    conflict_type = analyze_conflict(claims)
    # Returns: "temporal" (date conflict), "spatial" (location conflict), "factual" (contradiction)
    
    # Agent synthesizes resolution
    synthesis_result = synthesis_agent.resolve_conflict(
        claims=claims,
        conflict_type=conflict_type
    )
    
    # Create Synthesis node
    synthesis = {
        "synthesis_id": generate_uuid(),
        "agent_id": synthesis_agent_id,
        "timestamp": datetime.now().isoformat(),
        "consensus_method": "weighted_bayesian",
        "consensus_score": synthesis_result["confidence"],
        "resolution_strategy": synthesis_result["strategy"],
        "resolved_text": synthesis_result["resolution_text"]
    }
    
    neo4j_writer.create_synthesis(synthesis)
    
    # Link to all source claims
    for claim_id in claim_ids:
        neo4j_writer.create_edge(synthesis["synthesis_id"], "SYNTHESIZED_FROM", claim_id)
    
    # Create new resolved claim
    resolved_claim = {
        "claim_text": synthesis_result["resolution_text"],
        "cipher": generate_cipher(synthesis_result["resolution_text"]),
        "status": "validated",
        "confidence": synthesis_result["confidence"],
        "synthesis_id": synthesis["synthesis_id"],
        "source_claims": claim_ids
    }
    
    neo4j_writer.create_claim(resolved_claim)
    
    return {
        "synthesis_id": synthesis["synthesis_id"],
        "resolved_claim_cipher": resolved_claim["cipher"],
        "consensus_score": synthesis_result["confidence"]
    }
```

---

## **9.4 Claim Promotion Workflow**

### **9.4.1 Promotion Steps**

Convert validated claims from evidence layer to canonical graph:

```
Claim (validated) â†’ Promotion Process â†’ Canonical Entity/Relationship + Provenance Link
      â†“                    â†“                           â†“
(status=validated)   (4-step process)     (SUPPORTED_BY edge to claim)
```

**4-Step Promotion Process:**

1. **Remove Proposed Status**: Update entities/relationships to canonical
2. **Materialize from ASSERTS_EDGE**: Create actual relationship edge from validated ProposedEdge
3. **Update Metadata**: Set promotion date, promoted flag
4. **Link Provenance**: Create `SUPPORTED_BY` edge from canonical element to claim

---

### **9.4.2 Implementation Example**

```python
def claim_promotion_workflow(claim_id: str) -> Dict:
    """Promote validated claim to canonical graph."""
    
    # Step 1: Retrieve claim and verify status
    claim = neo4j_reader.get_claim(claim_id)
    
    if claim["status"] != "validated":
        return {"error": "Only validated claims can be promoted"}
    
    # Step 2: Promotion Process (4 steps)
    
    # Step 2a: Remove proposed status from nodes
    neo4j_writer.update_entity(claim["subject_entity_qid"], {
        "claim_status": None,  # Remove proposed flag
        "promoted": True,
        "promotion_date": datetime.now().isoformat()
    })
    
    neo4j_writer.update_entity(claim["object_entity_qid"], {
        "claim_status": None,
        "promoted": True,
        "promotion_date": datetime.now().isoformat()
    })
    
    # Step 2b: Convert ProposedEdge to actual relationship
    proposed_edges = neo4j_reader.get_proposed_edges_for_claim(claim_id)
    
    for pedge in proposed_edges:
        # Create actual relationship edge
        neo4j_writer.create_relationship(
            from_qid=pedge["source_entity_id"],
            to_qid=pedge["target_entity_id"],
            relationship_type=pedge["relationship_type"],
            properties={
                **pedge.get("edge_properties", {}),
                "promoted_from_claim_id": claim_id,
                "promotion_date": datetime.now().isoformat(),
                "confidence": claim["consensus_score"]
            }
        )
        
        # Keep ProposedEdge for audit; mark as promoted
        neo4j_writer.update_node(pedge["edge_id"], {
            "status": "validated",
            "promoted": True,
            "promotion_status": "canonical",
            "promotion_date": datetime.now().isoformat()
        })
    
    # Step 2c: Update claim metadata
    neo4j_writer.update_claim(claim_id, {
        "promoted": True,
        "promotion_date": datetime.now().isoformat()
    })
    
    # Step 2d: Link provenance (SUPPORTED_BY edge)
    canonical_entity = neo4j_reader.get_entity(claim["subject_entity_qid"])
    
    neo4j_writer.create_edge(
        from_id=canonical_entity["entity_id"],
        edge_type="SUPPORTED_BY",
        to_id=claim_id,
        properties={
            "confidence": claim["consensus_score"],
            "promotion_date": datetime.now().isoformat()
        }
    )
    
    return {
        "promoted": True,
        "claim_id": claim_id,
        "entities_promoted": [claim["subject_entity_qid"], claim["object_entity_qid"]],
        "relationships_created": len(proposed_edges),
        "consensus_score": claim["consensus_score"]
    }
```

---

### **9.4.3 Idempotency & Reversibility**

**Idempotent**: Safe to re-run promotion workflow
- Check if already promoted before processing
- Use MERGE instead of CREATE for edges
- Skip if `promoted=true` flag already set

**Reversible**: Can demote claim if evidence changes
- Keep original Claim nodes (don't delete)
- Mark canonical elements as `demoted=true`
- Preserve provenance trail for audit

```cypher
// Demotion query (if consensus drops below threshold)
MATCH (entity)-[r:SUPPORTED_BY]->(claim:Claim {claim_id: $claim_id})
WHERE claim.promoted = true AND claim.consensus_score < 0.8
SET entity.demoted = true,
    entity.demotion_date = datetime(),
    claim.promoted = false
// Keep claim and provenance for historical record
```

---

## **9.5 Error Handling & Recovery**

### **9.5.1 Workflow Failure Modes**

| Failure Type | Recovery Strategy |
|--------------|-------------------|
| **LLM Timeout** | Retry with exponential backoff (3 attempts) |
| **LLM Hallucination** | Validation layer catches (EntityAgent rejects invalid QIDs) |
| **Neo4j Connection Loss** | Queue writes, retry when connection restored |
| **Duplicate Claim** | Check cipher collision, merge reviews if duplicate found |
| **Agent Crash** | Workflow state persisted, resume from last checkpoint |

---

### **9.5.2 Workflow Monitoring**

```python
class WorkflowMonitor:
    """Monitor workflow execution and alert on failures."""
    
    def log_workflow_start(self, workflow_type: str, workflow_id: str):
        """Record workflow start."""
        log.info(f"Workflow {workflow_type} started: {workflow_id}")
        self.metrics["workflows_started"] += 1
    
    def log_workflow_completion(self, workflow_type: str, workflow_id: str, duration: float):
        """Record workflow completion."""
        log.info(f"Workflow {workflow_type} completed: {workflow_id} in {duration}s")
        self.metrics["workflows_completed"] += 1
        self.metrics["avg_duration"] = (self.metrics["avg_duration"] + duration) / 2
    
    def log_workflow_error(self, workflow_type: str, workflow_id: str, error: str):
        """Record workflow error and alert."""
        log.error(f"Workflow {workflow_type} failed: {workflow_id} - {error}")
        self.metrics["workflows_failed"] += 1
        
        # Alert if failure rate exceeds threshold
        failure_rate = self.metrics["workflows_failed"] / max(self.metrics["workflows_started"], 1)
        if failure_rate > 0.1:  # 10% failure rate
            self.send_alert(f"High workflow failure rate: {failure_rate:.1%}")
```

---

## **9.6 Facet Assessment Workflow** ðŸŸ¡ **STAR PATTERN - Multi-Dimensional Analysis**

### **9.6.1 Overview: Star Pattern for Claims**

**Core Concept:** A claim is evaluated **independently across all 18 analytical dimensions** simultaneously. Each facet (political, military, economic, biographic, etc.) receives its own assessment by a specialist agent.

**The Star Pattern:**
```
                â”Œâ”€â”€â†’ MilitaryFacet
                â”‚
   â”Œâ”€â”€â†’ Belief â”€â”¼â”€â”€â†’ DiplomaticFacet
   â”‚            â”‚
Claim â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â†’ PoliticalFacet
   â”‚          â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤â”€â”€â†’ EconomicFacet
               â””â”€â”€â†’ [12 other facet vectors]
```

**Key Property:** One AnalysisRun creates multiple independent FacetAssessments, each with its own confidence score, rationale, and source citations.

### **9.6.2 Facet Assessment Workflow (6 Steps)**

**Step 1: Receive Claim for Multi-Dimensional Analysis**
```python
def start_facet_assessment_workflow(claim_id: str) -> Dict:
    """Initiate multi-dimensional facet analysis."""
    claim = neo4j_reader.get_claim(claim_id)
    
    # Create AnalysisRun node (parent container)
    run_id = f"RUN_{claim_id}_{datetime.now().isoformat()}"
    run = neo4j_writer.create_node("AnalysisRun", {
        "run_id": run_id,
        "pipeline_version": "v2.0_faceted",
        "created_at": datetime.now().isoformat(),
        "status": "in_progress"
    })
    
    # Link claim to run
    neo4j_writer.create_edge(claim_id, "HAS_ANALYSIS_RUN", run_id)
    
    return {"run_id": run_id, "claim_id": claim_id, "status": "step_1_complete"}
```

**Step 2: Route Claim to Facet-Specialist Agents**
```python
def route_to_facet_agents(claim_id: str, run_id: str) -> List[Dict]:
    """Route claim to all 18 facet-specialist agents."""
    facet_agents = [
        ("AGENT_POLITICAL_V1", "PoliticalFacet"),
        ("AGENT_MILITARY_V1", "MilitaryFacet"),
        ("AGENT_ECONOMIC_V1", "EconomicFacet"),
        ("AGENT_CULTURAL_V1", "CulturalFacet"),
        ("AGENT_RELIGIOUS_V1", "ReligiousFacet"),
        ("AGENT_INTELLECTUAL_V1", "IntellectualFacet"),
        ("AGENT_SCIENTIFIC_V1", "ScientificFacet"),
        ("AGENT_ARTISTIC_V1", "ArtisticFacet"),
        ("AGENT_SOCIAL_V1", "SocialFacet"),
        ("AGENT_DEMOGRAPHIC_V1", "DemographicFacet"),
        ("AGENT_ENVIRONMENTAL_V1", "EnvironmentalFacet"),
        ("AGENT_TECHNOLOGICAL_V1", "TechnologicalFacet"),
        ("AGENT_LINGUISTIC_V1", "LinguisticFacet"),
        ("AGENT_ARCHAEOLOGICAL_V1", "ArchaeologicalFacet"),
        ("AGENT_DIPLOMATIC_V1", "DiplomaticFacet"),
        ("AGENT_GEOGRAPHIC_V1", "GeographicFacet"),
    ]
    
    routing_tasks = []
    for agent_id, facet_type in facet_agents:
        routing_tasks.append({
            "claim_id": claim_id,
            "run_id": run_id,
            "agent_id": agent_id,
            "facet_type": facet_type,
            "status": "queued"
        })
    
    return routing_tasks
```

**Step 3: Each Agent Creates Independent Facet Assessment**
```python
def evaluate_claim_for_facet(claim_id: str, run_id: str, agent_id: str, facet_type: str) -> Dict:
    """Evaluate claim from single facet perspective."""
    claim = neo4j_reader.get_claim(claim_id)
    
    # Agent evaluates claim through its facet lens
    # (e.g., political agent evaluates political implications)
    prompt = f"""
    Evaluate this historical claim from the {facet_type} perspective:
    
    "{claim['text']}"
    
    Provide:
    1. Confidence score (0.0-1.0)
    2. Status (supported/challenged/uncertain/mostly_supported)
    3. Rationale (2-3 sentences)
    4. Key supporting/contradicting evidence
    """
    
    assessment_result = llm_agent.evaluate(prompt)
    
    # Create FacetAssessment node
    assessment_id = f"FA_{claim_id}_{facet_type}_{run_id}"
    assessment = neo4j_writer.create_node("FacetAssessment", {
        "assessment_id": assessment_id,
        "score": assessment_result["confidence"],
        "status": assessment_result["status"],
        "rationale": assessment_result["rationale"],
        "evidence_count": len(assessment_result["sources"]),
        "created_at": datetime.now().isoformat()
    })
    
    # Link to AnalysisRun
    neo4j_writer.create_edge(run_id, "HAS_FACET_ASSESSMENT", assessment_id)
    
    # Link to Facet node
    facet_node = neo4j_reader.get_facet(facet_type)
    neo4j_writer.create_edge(assessment_id, "ASSESSES_FACET", facet_node["unique_id"])
    
    # Link to Agent
    neo4j_writer.create_edge(assessment_id, "EVALUATED_BY", agent_id)
    
    return {
        "assessment_id": assessment_id,
        "score": assessment_result["confidence"],
        "status": assessment_result["status"]
    }
```

**Step 4: Aggregate Facet Assessments (Star Pattern Complete)**
```python
def aggregate_facet_assessments(run_id: str) -> Dict:
    """Aggregate all 17 facet assessments into star pattern."""
    # Query: Get all assessments for this run
    query = """
    MATCH (run:AnalysisRun {run_id: $run_id})
      -[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
      -[:ASSESSES_FACET]->(f:Facet)
      -[:IN_FACET_CATEGORY]->(cat:FacetCategory)
    OPTIONAL MATCH (fa)-[:EVALUATED_BY]->(a:Agent)
    RETURN
      cat.key AS facet_category,
      f.label AS facet_label,
      fa.score AS assessment_score,
      fa.status AS assessment_status,
      fa.rationale AS assessment_rationale,
      a.label AS agent_label
    ORDER BY cat.key
    """
    
    assessments = neo4j_reader.query(query, run_id=run_id)
    
    # Group by facet category for UI tabs
    by_category = {}
    for assessment in assessments:
        cat = assessment["facet_category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(assessment)
    
    return {
        "run_id": run_id,
        "total_assessments": len(assessments),
        "facets_evaluated": len(by_category),
        "by_category": by_category,
        "status": "aggregated"
    }
```

**Step 5: Generate Multi-Dimensional Confidence Score**
```python
def calculate_multi_dimensional_confidence(run_id: str) -> Dict:
    """Calculate overall claim confidence from facet assessments."""
    query = """
    MATCH (run:AnalysisRun {run_id: $run_id})
      -[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
    RETURN
      fa.score AS score,
      fa.status AS status,
      count(*) AS count
    """
    
    results = neo4j_reader.query(query, run_id=run_id)
    
    # Calculate weighted average (supported=1.0, mostly_supported=0.8, uncertain=0.5, challenged=0.0)
    status_weights = {"supported": 1.0, "mostly_supported": 0.8, "uncertain": 0.5, "challenged": 0.0}
    
    total_score = 0
    total_weight = 0
    facet_scores = []
    
    for result in results:
        score = result["score"]
        status = result["status"]
        weight = status_weights.get(status, 0.5)
        
        total_score += score * weight
        total_weight += weight
        facet_scores.append({"status": status, "score": score})
    
    overall_confidence = total_score / total_weight if total_weight > 0 else 0.5
    
    return {
        "overall_confidence": overall_confidence,
        "facet_scores": facet_scores,
        "summary": f"{len(facet_scores)} dimensions analyzed, avg confidence {overall_confidence:.2f}"
    }
```

**Step 6: Mark Assessment Complete & Generate Reports**
```python
def complete_facet_assessment(run_id: str, overall_confidence: float) -> Dict:
    """Complete analysis run and generate reports."""
    # Update AnalysisRun status
    neo4j_writer.update_node(run_id, {
        "status": "completed",
        "updated_at": datetime.now().isoformat(),
        "overall_confidence": overall_confidence
    })
    
    # Query for report generation
    query = """
    MATCH (claim:Claim)-[:HAS_ANALYSIS_RUN]->(run:AnalysisRun {run_id: $run_id})
      -[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
      -[:ASSESSES_FACET]->(f:Facet)
      -[:IN_FACET_CATEGORY]->(cat:FacetCategory)
    OPTIONAL MATCH (fa)-[:EVALUATED_BY]->(a:Agent)
    RETURN
      claim.text AS claim_text,
      run.run_id AS run_id,
      run.pipeline_version AS pipeline_version,
      collect({
        category: cat.key,
        facet: f.label,
        score: fa.score,
        status: fa.status,
        rationale: fa.rationale,
        agent: a.label
      }) AS assessments
    """
    
    report = neo4j_reader.query(query, run_id=run_id)[0]
    
    return {
        "status": "complete",
        "run_id": run_id,
        "claim": report["claim_text"],
        "overall_confidence": overall_confidence,
        "facet_assessments": report["assessments"],
        "ui_ready": True
    }
```

### **9.6.3 UI Query Patterns (Facet Tab Interface)**

**Query 1: Get All Assessments Grouped by Facet Category**
```cypher
MATCH (c:Claim {claim_id: "CLAIM_CAESAR_RUBICON"})
  -[:HAS_ANALYSIS_RUN]->(run:AnalysisRun)
  -[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment)
  -[:ASSESSES_FACET]->(f:Facet)
  -[:IN_FACET_CATEGORY]->(cat:FacetCategory)
OPTIONAL MATCH (fa)-[:EVALUATED_BY]->(a:Agent)
RETURN
  cat.key AS facet_category,
  cat.label AS category_label,
  collect({
    facet_id: f.unique_id,
    facet_label: f.label,
    score: fa.score,
    status: fa.status,
    rationale: fa.rationale,
    agent: a.label
  }) AS assessments
ORDER BY facet_category;
```

**Result (JSON for UI tabs):**
```json
{
  "facet_category": "POLITICAL",
  "category_label": "Political",
  "assessments": [
    {
      "facet_id": "POLITICALFACET_Q3624078",
      "facet_label": "Caesar's political dominance",
      "score": 0.92,
      "status": "supported",
      "rationale": "Multiple primary sources corroborate political implications",
      "agent": "Political Historian Agent"
    }
  ]
}
```

**Query 2: Compare Two Analysis Runs (A/B Testing)**
```cypher
MATCH (claim:Claim)-[:HAS_ANALYSIS_RUN]->(run1:AnalysisRun {run_id: "RUN_001"})
MATCH (claim)-[:HAS_ANALYSIS_RUN]->(run2:AnalysisRun {run_id: "RUN_002"})
MATCH (run1)-[:HAS_FACET_ASSESSMENT]->(fa1:FacetAssessment)
MATCH (run2)-[:HAS_FACET_ASSESSMENT]->(fa2:FacetAssessment)
WHERE fa1.assessment_id STARTS WITH fa2.assessment_id SPLIT("_")[0]
RETURN
  fa1.score AS run1_score,
  fa2.score AS run2_score,
  fa1.score - fa2.score AS score_difference
ORDER BY abs(score_difference) DESC;
```

### **9.6.4 Benefits of Star Pattern**

1. **Multi-Dimensional Analysis:** Single event analyzed across all 17 analytical axes
2. **Agent Specialization:** Political expert evaluates political facet, military expert evaluates military facet
3. **Independent Confidence:** Each facet has its own confidence score (military_conf â‰  political_conf)
4. **Separate Sourcing:** Each facet cites relevant sources (military from military historians, political from political historians)
5. **UI Tabs:** Display "Political" | "Military" | "Economic" | etc. tabs for easy navigation
6. **Re-Runnable:** Compare analysis "v1" vs "v2" to track prompt/model improvements
7. **Extensible:** Add new facet dimensions without changing claim structure

---

