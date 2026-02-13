# MCP Role in Chrystallum Architecture

## What is MCP (Model Context Protocol)?

**MCP (Model Context Protocol)** is an open protocol developed by Anthropic for connecting AI models (LLMs) to external tools, data sources, and APIs.

**Key Features:**
- ✅ Standardized interface for tools
- ✅ Real-time data access
- ✅ Function calling
- ✅ Tool composition
- ✅ Secure, controlled access

---

## MCP's Role in Chrystallum Architecture

### Current Architecture (Without MCP)

```
Text Input
  ↓
LLM (Extraction)
  ↓
Knowledge Graph (Storage)
  ↓
Reasoning Model (Inference)
  ↓
Enriched Knowledge Graph
```

**Problem:**
- ❌ LLM has no access to knowledge graph during extraction
- ❌ LLM can't query existing entities
- ❌ LLM can't validate against existing data
- ❌ No real-time tool access

---

### Enhanced Architecture (With MCP)

```
Text Input
  ↓
LLM (Extraction)
  ←→ MCP Tools ←→
    - Neo4j Query Tool (Check existing entities)
    - VIAF Lookup Tool (Verify identifiers)
    - Wikidata Query Tool (Validate QIDs)
    - FAST Lookup Tool (Find subject headings)
    - Temporal Validator Tool (Check dates)
  ↓
Knowledge Graph (Storage)
  ↓
Reasoning Model (Inference)
  ↓
Enriched Knowledge Graph
```

**Benefits:**
- ✅ LLM can query graph during extraction
- ✅ LLM can validate against existing data
- ✅ LLM can access external sources
- ✅ Real-time tool integration

---

## MCP Tool Categories for Chrystallum

### 1. **Knowledge Graph Tools**

#### Neo4j Query Tool

**Purpose:** Allow LLM to query the knowledge graph during extraction

**Capabilities:**
- Check if entity already exists
- Find similar entities
- Validate relationships
- Query temporal data

**Example:**
```python
# MCP Tool: Query Neo4j
@mcp_tool
def query_neo4j(query: str) -> dict:
    """
    Query Neo4j knowledge graph.
    
    Args:
        query: Cypher query string
        
    Returns:
        Query results
    """
    result = neo4j_driver.execute_query(query)
    return result
```

**Use Case:**
```python
# LLM can call this during extraction
entities = llm.extract_entities(text)

# Before creating new entity, check if exists
existing = mcp.call_tool("query_neo4j", 
    "MATCH (e:Human {label: 'Julius Caesar'}) RETURN e")

if existing:
    # Use existing entity, don't create duplicate
    entity_id = existing[0]['e'].id
else:
    # Create new entity
    entity_id = create_entity(entities['Caesar'])
```

---

#### Entity Resolution Tool

**Purpose:** Help LLM resolve entity identity during extraction

**Capabilities:**
- Check existing entities by identifier
- Find entity by VIAF ID
- Find entity by Wikidata QID
- Fuzzy matching

**Example:**
```python
@mcp_tool
def resolve_entity(label: str, qid: str = None, viaf_id: str = None) -> dict:
    """
    Resolve entity identity in knowledge graph.
    
    Args:
        label: Entity label
        qid: Optional Wikidata QID
        viaf_id: Optional VIAF ID
        
    Returns:
        Existing entity or None
    """
    if qid:
        result = neo4j_driver.execute_query(
            "MATCH (e) WHERE e.qid = $qid RETURN e",
            qid=qid
        )
        if result:
            return result[0]
    
    # Fuzzy match by label
    result = neo4j_driver.execute_query(
        "MATCH (e) WHERE e.label CONTAINS $label RETURN e LIMIT 5",
        label=label
    )
    return result
```

**Use Case:**
```python
# LLM extracts "Caesar"
extracted = llm.extract("Caesar crossed Rubicon")

# LLM resolves entity identity
existing = mcp.call_tool("resolve_entity", 
    label="Caesar", 
    qid="Q1048")

if existing:
    # Use existing entity
    entity = existing
else:
    # Create new entity
    entity = create_new_entity(extracted['Caesar'])
```

---

### 2. **External Data Source Tools**

#### VIAF Lookup Tool

**Purpose:** Look up entity identifiers from VIAF during extraction

**Capabilities:**
- Search VIAF by name
- Get VIAF ID for entity
- Retrieve name variants
- Get authority record

**Example:**
```python
@mcp_tool
def lookup_viaf(name: str) -> dict:
    """
    Look up entity in VIAF database.
    
    Args:
        name: Entity name
        
    Returns:
        VIAF record with ID and variants
    """
    viaf_client = VIAFClient()
    result = viaf_client.search(name)
    return {
        'viaf_id': result.id,
        'variants': result.name_variants,
        'sources': result.sources
    }
```

**Use Case:**
```python
# LLM extracts "Julius Caesar"
extracted = llm.extract("Julius Caesar")

# LLM looks up VIAF ID
viaf_data = mcp.call_tool("lookup_viaf", "Julius Caesar")

# Add VIAF ID to entity
entity.viaf_id = viaf_data['viaf_id']
entity.name_variants = viaf_data['variants']
```

---

#### Wikidata Query Tool

**Purpose:** Query Wikidata during extraction

**Capabilities:**
- Get Wikidata QID
- Validate entity types
- Get entity properties
- Find relationships

**Example:**
```python
@mcp_tool
def query_wikidata(entity_name: str) -> dict:
    """
    Query Wikidata for entity information.
    
    Args:
        entity_name: Name of entity
        
    Returns:
        Wikidata data including QID
    """
    wikidata_client = WikidataClient()
    result = wikidata_client.search(entity_name)
    return {
        'qid': result.qid,
        'label': result.label,
        'type': result.instance_of,
        'properties': result.properties
    }
```

---

#### FAST/LCC Lookup Tool

**Purpose:** Find subject headings during extraction

**Capabilities:**
- Search FAST by subject
- Get LCC classification
- Find LCSH terms

**Example:**
```python
@mcp_tool
def lookup_fast(subject: str) -> dict:
    """
    Look up FAST subject heading.
    
    Args:
        subject: Subject term
        
    Returns:
        FAST ID and related terms
    """
    fast_client = FASTClient()
    result = fast_client.search(subject)
    return {
        'fast_id': result.id,
        'label': result.label,
        'lcc': result.lcc_code,
        'lcsh': result.lcsh_terms
    }
```

---

### 3. **Validation Tools**

#### Temporal Validator Tool

**Purpose:** Validate dates during extraction

**Capabilities:**
- Convert dates to ISO 8601
- Validate temporal consistency
- Check date ranges
- Handle calendar conversions

**Example:**
```python
@mcp_tool
def validate_date(date_string: str, calendar: str = "gregorian") -> dict:
    """
    Validate and normalize date string.
    
    Args:
        date_string: Date string (e.g., "49 BCE", "January 10, 49 BC")
        calendar: Calendar system
        
    Returns:
        Normalized ISO 8601 date and metadata
    """
    validator = DateValidator()
    result = validator.normalize(date_string, calendar)
    return {
        'iso8601': result.iso8601,
        'precision': result.precision,
        'uncertainty': result.uncertainty,
        'original': date_string
    }
```

**Use Case:**
```python
# LLM extracts date
extracted = llm.extract("Caesar crossed Rubicon in 49 BCE")

# LLM validates date
date_result = mcp.call_tool("validate_date", "49 BCE")

# Use normalized date
entity.start_date = date_result['iso8601']  # "-0049-01-01"
entity.date_precision = date_result['precision']  # "year"
```

---

#### Consistency Checker Tool

**Purpose:** Check consistency during extraction

**Capabilities:**
- Validate entity resolution
- Check temporal consistency
- Detect conflicts

**Example:**
```python
@mcp_tool
def check_consistency(entity_data: dict) -> dict:
    """
    Check consistency of extracted entity data.
    
    Args:
        entity_data: Entity properties from extraction
        
    Returns:
        Consistency check results
    """
    checker = ConsistencyChecker()
    result = checker.check(entity_data)
    return {
        'consistent': result.is_consistent,
        'conflicts': result.conflicts,
        'confidence': result.confidence
    }
```

---

## MCP Architecture in Chrystallum

### Complete MCP-Enhanced Pipeline

```
┌─────────────────────────────────────┐
│  Text Input                         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  LLM (Extraction Agent)             │
│                                     │
│  ←→ MCP Tools:                      │
│     • query_neo4j                   │
│     • resolve_entity                │
│     • lookup_viaf                   │
│     • query_wikidata                │
│     • lookup_fast                   │
│     • validate_date                 │
│     • check_consistency             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Knowledge Graph (Validated Data)   │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Reasoning Model (Inference)        │
└─────────────────────────────────────┘
```

---

## Benefits of MCP in Chrystallum

### 1. **Real-Time Validation During Extraction**

**Without MCP:**
- LLM extracts data
- Store in graph
- Later: Reasoning model finds conflicts
- **Problem:** Duplicates/conflicts already created

**With MCP:**
- LLM extracts data
- LLM calls `resolve_entity` tool → checks if exists
- LLM calls `check_consistency` tool → validates before storing
- **Benefit:** Prevent duplicates/conflicts at extraction time

---

### 2. **Enriched Extraction with External Data**

**Without MCP:**
- LLM extracts: "Caesar" → Creates entity with label only
- Later: Manual lookup of VIAF, Wikidata, FAST
- **Problem:** Incomplete data, manual work

**With MCP:**
- LLM extracts: "Caesar"
- LLM calls `lookup_viaf("Caesar")` → Gets VIAF ID
- LLM calls `query_wikidata("Caesar")` → Gets QID
- LLM calls `lookup_fast("Roman Republic")` → Gets FAST ID
- **Benefit:** Complete data at extraction time

---

### 3. **Intelligent Entity Resolution**

**Without MCP:**
- LLM extracts "Caesar" → Creates new entity
- But "Caesar" already exists in graph
- **Problem:** Duplicate entities

**With MCP:**
- LLM extracts "Caesar"
- LLM calls `resolve_entity("Caesar", qid="Q1048")`
- Tool finds existing entity
- LLM uses existing entity
- **Benefit:** No duplicates

---

### 4. **Standardized Tool Interface**

**Without MCP:**
- Each tool has different API
- Custom integration code
- **Problem:** Complexity, maintenance

**With MCP:**
- Standardized MCP protocol
- All tools use same interface
- **Benefit:** Simple, maintainable

---

## MCP Tools for Chrystallum

### Recommended MCP Tool Suite

#### 1. **Graph Tools**
- `query_neo4j` - Query knowledge graph
- `resolve_entity` - Find existing entities
- `find_relationships` - Find relationships
- `check_duplicate` - Check for duplicates

#### 2. **Authority Tools**
- `lookup_viaf` - VIAF authority lookup
- `lookup_wikidata` - Wikidata query
- `lookup_fast` - FAST subject heading lookup
- `lookup_marc` - MARC authority lookup

#### 3. **Validation Tools**
- `validate_date` - Date normalization/validation
- `check_consistency` - Consistency checking
- `validate_entity_type` - Entity type validation
- `check_temporal_logic` - Temporal consistency

#### 4. **Geographic Tools**
- `lookup_pleiades` - Pleiades geographic lookup
- `get_coordinates` - Geographic coordinates
- `validate_place` - Place validation

#### 5. **Reasoning Tools**
- `infer_relationships` - Relationship inference
- `calculate_confidence` - Confidence scoring
- `check_causal_chains` - Causal reasoning

---

## Implementation Example

### MCP Server for Chrystallum

```python
from mcp import Server, Tool

# Initialize MCP Server
server = Server("chrystallum-tools")

# Neo4j Query Tool
@server.tool()
def query_neo4j(query: str) -> dict:
    """Query Neo4j knowledge graph with Cypher."""
    result = neo4j_driver.execute_query(query)
    return {"results": result, "count": len(result)}

# Entity Resolution Tool
@server.tool()
def resolve_entity(
    label: str, 
    qid: str = None, 
    viaf_id: str = None
) -> dict:
    """Resolve entity identity in knowledge graph."""
    if qid:
        result = neo4j_driver.execute_query(
            "MATCH (e) WHERE e.qid = $qid RETURN e",
            qid=qid
        )
        if result:
            return {"found": True, "entity": result[0]}
    
    # Fuzzy match
    result = neo4j_driver.execute_query(
        "MATCH (e) WHERE e.label CONTAINS $label RETURN e LIMIT 5",
        label=label
    )
    return {"found": len(result) > 0, "matches": result}

# VIAF Lookup Tool
@server.tool()
def lookup_viaf(name: str) -> dict:
    """Look up entity in VIAF database."""
    viaf_client = VIAFClient()
    result = viaf_client.search(name)
    return {
        "viaf_id": result.id,
        "variants": result.name_variants,
        "sources": result.sources
    }

# Date Validation Tool
@server.tool()
def validate_date(date_string: str) -> dict:
    """Validate and normalize date to ISO 8601."""
    validator = DateValidator()
    result = validator.normalize(date_string)
    return {
        "iso8601": result.iso8601,
        "precision": result.precision,
        "uncertainty": result.uncertainty
    }

# Start server
if __name__ == "__main__":
    server.run()
```

---

## LLM Agent with MCP Tools

### Extraction with Tool Access

```python
from langchain.agents import AgentExecutor
from langchain.tools import MCPTool

# Create MCP tools
neo4j_tool = MCPTool(name="query_neo4j", mcp_server="chrystallum-tools")
viaf_tool = MCPTool(name="lookup_viaf", mcp_server="chrystallum-tools")
date_tool = MCPTool(name="validate_date", mcp_server="chrystallum-tools")

# LLM Agent with tools
agent = AgentExecutor(
    llm=llm,
    tools=[neo4j_tool, viaf_tool, date_tool],
    verbose=True
)

# Extraction with tool access
text = "Caesar crossed the Rubicon in 49 BCE"
result = agent.run(
    f"""
    Extract knowledge from this text: {text}
    
    Use tools to:
    1. Check if entities already exist (query_neo4j)
    2. Look up VIAF IDs (lookup_viaf)
    3. Validate dates (validate_date)
    4. Ensure no duplicates
    """
)
```

---

## MCP Benefits Summary

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

### For Reasoning Model

✅ **Cleaner data** - Less conflicts to resolve  
✅ **Higher confidence** - Complete, validated data  
✅ **Focus on inference** - Less time on validation  

---

## Architecture Comparison

### Without MCP

```
Text → LLM → [Extracted Data] → KG → [Conflicts/Duplicates] → Reasoning → Clean KG
```

**Problems:**
- Duplicates created
- Incomplete data
- Conflicts need resolution
- Manual lookup later

---

### With MCP

```
Text → LLM + MCP Tools → [Validated, Complete Data] → KG → Reasoning → Enriched KG
```

**Benefits:**
- No duplicates (entity resolution)
- Complete data (external lookups)
- Validated data (consistency checks)
- Enriched immediately

---

## Recommended MCP Tool Priority

### Phase 1: Core Tools (High Priority)

1. **`query_neo4j`** - Essential for entity resolution
2. **`resolve_entity`** - Prevent duplicates
3. **`validate_date`** - Critical for temporal data
4. **`lookup_viaf`** - Entity authority lookup

### Phase 2: Enrichment Tools (Medium Priority)

5. **`query_wikidata`** - Entity validation
6. **`lookup_fast`** - Subject classification
7. **`check_consistency`** - Validation

### Phase 3: Advanced Tools (Lower Priority)

8. **`lookup_pleiades`** - Geographic enrichment
9. **`infer_relationships`** - Reasoning integration
10. **`calculate_confidence`** - Confidence scoring

---

## Summary

### MCP's Role in Chrystallum

**MCP = Tool Integration Layer for LLM**

**Primary Functions:**
1. ✅ **Connect LLM to Knowledge Graph** - Query during extraction
2. ✅ **Connect LLM to External Sources** - VIAF, Wikidata, FAST
3. ✅ **Enable Real-Time Validation** - Check consistency during extraction
4. ✅ **Standardize Tool Interface** - Unified API for all tools

**Architecture Position:**
```
LLM ←→ MCP Tools ←→ Knowledge Graph
      ←→ MCP Tools ←→ External Sources (VIAF, Wikidata, FAST)
      ←→ MCP Tools ←→ Validation Services
```

**Benefits:**
- ✅ Better data quality at extraction
- ✅ Fewer duplicates and conflicts
- ✅ Enriched entities from start
- ✅ Real-time validation
- ✅ Standardized tool interface

**Bottom Line:** MCP acts as the **"tool layer"** that connects the LLM (extraction) to the knowledge graph and external data sources, enabling **intelligent, validated extraction** rather than naive extraction followed by cleanup.





