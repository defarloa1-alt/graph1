# MCP Integration Analysis for Chrystallum

**Date:** December 12, 2025  
**Purpose:** Determine whether Neo4j and Wikidata MCP support should be integrated into Chrystallum architecture

---

## Executive Summary

**Recommendation: YES - MCP integration should be implemented**

**Key Benefits:**
- ✅ Real-time entity resolution during LLM extraction (prevents duplicates)
- ✅ Live validation against existing graph data
- ✅ Direct access to Wikidata for QID validation and enrichment
- ✅ Standardized tool interface for multi-agent coordination
- ✅ Alignment with existing architecture plans

**Priority:** High - Addresses core architectural needs identified in agent coordination design

---

## Project Overview

### Chrystallum Architecture

**Core Components:**
1. **Knowledge Graph (Neo4j)** - Primary storage for historical entities
2. **Backbone Structure** - Hierarchical taxonomies:
   - 23 Subjects (LCSH/FAST topics)
   - 86 Periods (temporal hierarchy)
   - 36 Places (geographic hierarchy)
3. **LLM Agents** - Subject Matter Experts (SMEs) that extract subgraphs
4. **Decision Agent** - Resolves conflicts (duplicate/additive/replacement)
5. **Multi-Agent Coordination** - Handles multi-perspective claims

**Current Data Flow:**
```
Text Input → LLM Extraction → JSON Subgraph → Decision Agent → Neo4j Import
```

**Problem:** LLM has no access to existing graph data during extraction

---

## Current Neo4j Usage

### Primary Operations

1. **Entity Storage**
   - Nodes: Person, Event, Organization, Period, Place, Subject
   - Relationships: OCCURRED_IN, SUBJECT_OF, CAUSED, PART_OF, etc.
   - Current: ~817 nodes (672 Years, 86 Periods, 36 Places, 23 Subjects)

2. **Backbone Management**
   - Temporal hierarchy (Year → Period → Period)
   - Geographic hierarchy (Place → Place)
   - Subject taxonomy (LCSH/FAST)

3. **Query Patterns**
   - Cypher queries for entity resolution
   - Temporal navigation (Year → Period)
   - Topical discovery (Event → Subject)
   - Relationship traversal

4. **Import Scripts**
   - Python scripts using `neo4j` driver
   - Batch imports from CSV
   - Cypher scripts for setup

### Current Limitations

**Without MCP:**
- ❌ LLM cannot check if entity exists before creating
- ❌ No real-time validation during extraction
- ❌ Duplicate detection happens AFTER import
- ❌ Manual entity resolution required
- ❌ No access to graph context during extraction

---

## Current Wikidata Integration

### Usage Patterns

1. **QID Storage**
   - Every entity has `qid` property (Wikidata identifier)
   - Used for entity alignment and deduplication
   - Example: `{qid: "Q1048"}` for Julius Caesar

2. **Alignment Strategy**
   - Map to Wikidata where possible
   - Create custom entities where more granularity needed
   - Document rationale for custom extensions

3. **Validation**
   - Scripts check QID validity
   - SPARQL queries for Wikidata data
   - Manual verification process

### Current Limitations

**Without MCP:**
- ❌ LLM cannot validate QIDs during extraction
- ❌ No real-time Wikidata lookup
- ❌ Manual QID verification required
- ❌ No access to Wikidata properties during extraction
- ❌ Cannot check Wikidata conflicts before import

---

## Why MCP Should Be Used

### 1. Addresses Core Architectural Needs

**From `MCP_Role_in_Chrystallum_Architecture.md`:**
> "LLM has no access to knowledge graph during extraction"
> "LLM can't query existing entities"
> "LLM can't validate against existing data"

**MCP Solution:**
- ✅ LLM can call `query_neo4j` tool during extraction
- ✅ LLM can call `resolve_entity` tool to check duplicates
- ✅ LLM can call `query_wikidata` tool for QID validation

### 2. Prevents Duplicate Entities

**Current Problem:**
```
LLM extracts "Caesar" → Creates new entity
But "Caesar" already exists in graph
Result: Duplicate entities
```

**With MCP:**
```
LLM extracts "Caesar"
→ Calls resolve_entity("Caesar", qid="Q1048")
→ Tool finds existing entity
→ LLM uses existing entity
Result: No duplicates
```

### 3. Enables Real-Time Validation

**Current Flow:**
```
Extract → Store → Later: Reasoning model finds conflicts
Problem: Conflicts already created
```

**With MCP:**
```
Extract → Validate (check_consistency) → Store
Benefit: Prevent conflicts at extraction time
```

### 4. Supports Multi-Agent Coordination

**From `building chrystallum a knowledge graph of history.md`:**
> "we have an agent that decides - is it a duplicate, additive or a replacement"

**MCP Enables:**
- Decision agent can query graph for existing claims
- Compare confidence scores in real-time
- Check for conflicts before graph update
- Access Wikidata for external validation

### 5. Standardizes Tool Interface

**Current State:**
- Custom Python scripts for each operation
- Different APIs for Neo4j, Wikidata, VIAF, FAST
- Manual integration code

**With MCP:**
- Standardized MCP protocol
- All tools use same interface
- Easier maintenance and extension

---

## Recommended MCP Tools

### Phase 1: Core Tools (High Priority)

#### 1. `query_neo4j`
**Purpose:** Query knowledge graph during extraction  
**Use Cases:**
- Check if entity exists
- Find similar entities
- Validate relationships
- Query temporal data

**Example:**
```python
@mcp_tool
def query_neo4j(query: str) -> dict:
    """Query Neo4j knowledge graph with Cypher."""
    result = neo4j_driver.execute_query(query)
    return {"results": result, "count": len(result)}
```

#### 2. `resolve_entity`
**Purpose:** Resolve entity identity (prevent duplicates)  
**Use Cases:**
- Check existing entities by QID
- Find entity by VIAF ID
- Fuzzy matching by label

**Example:**
```python
@mcp_tool
def resolve_entity(label: str, qid: str = None, viaf_id: str = None) -> dict:
    """Resolve entity identity in knowledge graph."""
    if qid:
        result = neo4j_driver.execute_query(
            "MATCH (e) WHERE e.qid = $qid RETURN e",
            qid=qid
        )
        if result:
            return {"found": True, "entity": result[0]}
    return {"found": False}
```

#### 3. `query_wikidata`
**Purpose:** Query Wikidata during extraction  
**Use Cases:**
- Validate QIDs
- Get entity properties
- Find relationships
- Check for conflicts

**Example:**
```python
@mcp_tool
def query_wikidata(entity_name: str, qid: str = None) -> dict:
    """Query Wikidata for entity information."""
    if qid:
        # SPARQL query for QID
        result = wikidata_client.get_entity(qid)
    else:
        # Search by name
        result = wikidata_client.search(entity_name)
    return {
        "qid": result.qid,
        "label": result.label,
        "properties": result.properties
    }
```

#### 4. `validate_date`
**Purpose:** Validate and normalize dates  
**Use Cases:**
- Convert dates to ISO 8601
- Validate temporal consistency
- Handle calendar conversions

**Example:**
```python
@mcp_tool
def validate_date(date_string: str, calendar: str = "gregorian") -> dict:
    """Validate and normalize date string."""
    validator = DateValidator()
    result = validator.normalize(date_string, calendar)
    return {
        "iso8601": result.iso8601,
        "precision": result.precision,
        "uncertainty": result.uncertainty
    }
```

### Phase 2: Enrichment Tools (Medium Priority)

#### 5. `lookup_viaf`
**Purpose:** VIAF authority lookup  
**Use Cases:**
- Get VIAF ID for entity
- Retrieve name variants
- Get authority record

#### 6. `lookup_fast`
**Purpose:** FAST subject heading lookup  
**Use Cases:**
- Find FAST ID for subject
- Get LCC classification
- Find LCSH terms

#### 7. `check_consistency`
**Purpose:** Consistency checking  
**Use Cases:**
- Validate entity resolution
- Check temporal consistency
- Detect conflicts

### Phase 3: Advanced Tools (Lower Priority)

#### 8. `infer_contemporaries`
**Purpose:** Graph-based reasoning  
**Use Cases:**
- Infer contemporaries using graph patterns
- Find related entities

#### 9. `aggregate_confidence`
**Purpose:** Confidence scoring  
**Use Cases:**
- Aggregate confidence from multiple sources
- Calculate integrated confidence scores

---

## Implementation Strategy

### Step 1: Create MCP Server

**File:** `scripts/mcp/chrystallum_mcp_server.py`

```python
from mcp.server import Server
from mcp.types import Tool
from neo4j import GraphDatabase
import os

# Initialize Neo4j
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(
        os.getenv("NEO4J_USERNAME", "neo4j"),
        os.getenv("NEO4J_PASSWORD", "password")
    )
)

# Create MCP server
server = Server("chrystallum-tools")

# Register tools (see examples above)
@server.list_tools()
async def list_tools():
    return [
        Tool(name="query_neo4j", ...),
        Tool(name="resolve_entity", ...),
        Tool(name="query_wikidata", ...),
        Tool(name="validate_date", ...),
        # ... more tools
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # Implement tool logic
    pass
```

### Step 2: Configure Cursor

**File:** `%APPDATA%\Cursor\User\settings.json` (Windows)

```json
{
  "mcp.servers": {
    "chrystallum-tools": {
      "command": "python",
      "args": [
        "C:\\Projects\\federated-graph-framework\\graph 3\\scripts\\mcp\\chrystallum_mcp_server.py"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "your_password"
      }
    }
  }
}
```

### Step 3: Update Agent Prompts

**File:** `Agents/prompts/system/extraction_agent.txt`

Add instructions for using MCP tools:
```
Before creating a new entity:
1. Call resolve_entity(label, qid) to check if exists
2. If found, use existing entity
3. If not found, validate QID with query_wikidata
4. Validate dates with validate_date
5. Check consistency with check_consistency
```

### Step 4: Integrate with Decision Agent

**File:** `scripts/agents/decision_agent.py`

```python
# Decision agent can use MCP tools
async def decide_claim(new_claim, existing_claims):
    # Query graph for existing claims
    existing = await mcp.call_tool("query_neo4j", 
        f"MATCH (e) WHERE e.qid = '{new_claim.qid}' RETURN e")
    
    if existing:
        # Check confidence scores
        if new_claim.confidence > existing.confidence + 0.15:
            return "REPLACE"
        elif abs(new_claim.confidence - existing.confidence) < 0.15:
            return "DEBATE"
        else:
            return "ADDITIVE"
    else:
        return "ADDITIVE"
```

---

## Benefits Summary

### For Extraction (LLM)

✅ **Real-time validation** - Check consistency during extraction  
✅ **External data access** - Look up VIAF, Wikidata, FAST  
✅ **Duplicate prevention** - Resolve entities before creating  
✅ **Enriched data** - Complete entities at extraction time  
✅ **Tool standardization** - Unified interface for all tools

### For Knowledge Graph

✅ **Better data quality** - Validated before storage  
✅ **Fewer duplicates** - Entity resolution at extraction  
✅ **Complete entities** - All identifiers from start  
✅ **Consistency** - Validated during extraction

### For Multi-Agent Coordination

✅ **Real-time conflict detection** - Check conflicts before graph update  
✅ **Confidence comparison** - Compare scores during decision  
✅ **Graph context** - Access existing claims during debate  
✅ **Standardized protocol** - All agents use same tools

---

## Risks and Mitigations

### Risk 1: Performance Overhead

**Concern:** MCP tool calls add latency to extraction

**Mitigation:**
- Cache frequently accessed entities
- Batch queries where possible
- Use async operations
- Only call tools when necessary

### Risk 2: Complexity

**Concern:** Additional infrastructure to maintain

**Mitigation:**
- Start with core tools only
- Use existing Neo4j and Wikidata libraries
- Follow MCP standard (not custom protocol)
- Document tool usage clearly

### Risk 3: Tool Reliability

**Concern:** External services (Wikidata) may be unavailable

**Mitigation:**
- Implement fallback behavior
- Cache Wikidata responses
- Graceful degradation
- Retry logic for transient failures

---

## Comparison: With vs. Without MCP

### Without MCP (Current)

```
Text Input
  ↓
LLM Extraction (no graph access)
  ↓
JSON Subgraph
  ↓
Decision Agent (queries graph separately)
  ↓
Neo4j Import
  ↓
Later: Reasoning model finds conflicts
```

**Problems:**
- Duplicates created before detection
- Incomplete data (missing QIDs, VIAF IDs)
- Conflicts need resolution after import
- Manual validation required

### With MCP (Proposed)

```
Text Input
  ↓
LLM Extraction
  ←→ MCP Tools:
     • query_neo4j (check existing)
     • resolve_entity (prevent duplicates)
     • query_wikidata (validate QIDs)
     • validate_date (normalize dates)
  ↓
Validated JSON Subgraph
  ↓
Decision Agent (uses MCP tools)
  ↓
Neo4j Import (clean data)
  ↓
Reasoning model (fewer conflicts)
```

**Benefits:**
- No duplicates (entity resolution)
- Complete data (external lookups)
- Validated data (consistency checks)
- Enriched immediately

---

## Conclusion

### Recommendation: **YES - Implement MCP Integration**

**Rationale:**
1. ✅ Addresses core architectural needs (entity resolution, validation)
2. ✅ Prevents duplicates and conflicts at extraction time
3. ✅ Enables real-time access to graph and external data
4. ✅ Supports multi-agent coordination design
5. ✅ Standardizes tool interface
6. ✅ Aligns with existing MCP documentation in project

**Priority:** High - Core functionality for agent-based extraction

**Implementation:** Start with Phase 1 tools (query_neo4j, resolve_entity, query_wikidata, validate_date)

**Timeline:** Can be implemented incrementally alongside existing agent development

---

## Next Steps

1. **Create MCP Server** (`scripts/mcp/chrystallum_mcp_server.py`)
2. **Implement Core Tools** (query_neo4j, resolve_entity, query_wikidata, validate_date)
3. **Configure Cursor** (MCP server settings)
4. **Update Agent Prompts** (instructions for using MCP tools)
5. **Test Integration** (extract test subgraph with MCP tools)
6. **Integrate with Decision Agent** (use MCP tools for conflict detection)
7. **Document Usage** (examples and patterns)

---

## References

- `Docs/MCP_Role_in_Chrystallum_Architecture.md` - MCP architecture design
- `Docs/MCP_Reasoning_Models_Cursor.md` - MCP reasoning integration
- `Docs/Open_Source_Reasoning_Models_with_MCP.md` - MCP implementation examples
- `Agents/README.md` - Agent architecture
- `building chrystallum a knowledge graph of history.md` - Project overview


