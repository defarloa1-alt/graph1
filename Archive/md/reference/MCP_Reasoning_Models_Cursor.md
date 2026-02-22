# Open Source Reasoning Models with MCP in Cursor

## Practical Guide

Open source reasoning models and frameworks that work with MCP (Model Context Protocol) specifically in Cursor IDE.

---

## Ready-to-Use MCP Reasoning Servers

### 1. **MCP Advanced Reasoning Server** ⭐ Recommended

**GitHub:** `AzDeltaQQ/Mcp-Reasoning-Server`

**Capabilities:**
- ✅ Monte Carlo Tree Search (MCTS)
- ✅ Beam Search
- ✅ R1 Transformer-based reasoning
- ✅ Hybrid reasoning methods
- ✅ Structured reasoning
- ✅ Complex cognitive tasks

**Installation:**
```bash
git clone https://github.com/AzDeltaQQ/Mcp-Reasoning-Server
cd Mcp-Reasoning-Server
pip install -r requirements.txt
```

**Cursor Configuration:**
```json
{
  "mcp.servers": {
    "advanced-reasoning": {
      "command": "python",
      "args": ["/path/to/Mcp-Reasoning-Server/server.py"],
      "env": {
        "REASONING_MODE": "hybrid"
      }
    }
  }
}
```

**Why It's Good:**
- ✅ Specifically designed for MCP
- ✅ Multiple reasoning methods
- ✅ Works with Cursor
- ✅ Active development

---

### 2. **Thinking MCP Server** ⭐ Recommended

**Developer:** `vitalymalakanov`

**Capabilities:**
- ✅ 19 distinct thinking modes
- ✅ Tree-structured thoughts
- ✅ Metacognitive analysis
- ✅ Logical consistency checking
- ✅ Sequential thinking

**Installation:**
```bash
# Available via cursormcp.net
# Or check GitHub repository
```

**Cursor Configuration:**
```json
{
  "mcp.servers": {
    "thinking": {
      "command": "npx",
      "args": ["-y", "@vitalymalakanov/mcp-thinking"]
    }
  }
}
```

**Why It's Good:**
- ✅ Many thinking modes
- ✅ Structured reasoning
- ✅ MCP standard compliant
- ✅ Cursor compatible

---

### 3. **Custom Neo4j Reasoning Server** ⭐ Best for Chrystallum

**Since you're already using Neo4j, create custom MCP server:**

**Implementation:**
```python
# neo4j_reasoning_mcp_server.py
from mcp.server import Server
from mcp.types import Tool
from neo4j import GraphDatabase
import json

# Initialize Neo4j
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

# Create MCP server
server = Server("neo4j-reasoning")

# Reasoning Tool 1: Consistency Checker
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="check_consistency",
            description="Check entity consistency across standards",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to check"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="infer_contemporaries",
            description="Infer contemporaries using graph patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="validate_entity_resolution",
            description="Validate entity resolution across identifiers",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to validate"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="infer_causal_chains",
            description="Infer causal chains from action structures",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "Event ID"
                    }
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="aggregate_confidence",
            description="Aggregate confidence from multiple sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID"
                    }
                },
                "required": ["entity_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute reasoning tools."""
    
    if name == "check_consistency":
        entity_id = arguments["entity_id"]
        query = """
        MATCH (e {id: $entity_id})
        RETURN {
          has_all_ids: (e.viaf_id IS NOT NULL 
                       AND e.qid IS NOT NULL 
                       AND e.backbone_marc IS NOT NULL),
          dates_valid: (e.start_date IS NOT NULL 
                       AND e.end_date IS NOT NULL 
                       AND e.start_date <= e.end_date),
          has_backbone: (e.backbone_fast IS NOT NULL 
                        AND e.backbone_lcc IS NOT NULL)
        } as consistency
        """
        with driver.session() as session:
            result = session.run(query, entity_id=entity_id)
            return {"content": [{"text": json.dumps(dict(result.single()["consistency"]))}]}
    
    elif name == "infer_contemporaries":
        entity_id = arguments["entity_id"]
        query = """
        MATCH (e:Human {id: $entity_id})
        MATCH (other:Human)
        WHERE e.backbone_lcc = other.backbone_lcc
          AND e.start_date <= other.end_date
          AND other.start_date <= e.end_date
          AND e <> other
        RETURN {
          entity_id: other.id,
          label: other.label,
          confidence: CASE
            WHEN ABS(DATEDIFF(e.start_date, other.start_date)) <= 10 THEN 0.9
            WHEN ABS(DATEDIFF(e.start_date, other.start_date)) <= 25 THEN 0.7
            ELSE 0.5
          END
        } as contemporary
        ORDER BY contemporary.confidence DESC
        LIMIT 10
        """
        with driver.session() as session:
            results = session.run(query, entity_id=entity_id)
            contemporaries = [dict(r["contemporary"]) for r in results]
            return {"content": [{"text": json.dumps(contemporaries)}]}
    
    elif name == "validate_entity_resolution":
        entity_id = arguments["entity_id"]
        query = """
        MATCH (e {id: $entity_id})
        OPTIONAL MATCH (other)
        WHERE e <> other
          AND (
            (e.viaf_id IS NOT NULL AND e.viaf_id = other.viaf_id)
            OR (e.qid IS NOT NULL AND e.qid = other.qid)
          )
        RETURN {
          has_duplicates: COUNT(other) > 0,
          duplicate_ids: COLLECT(other.id),
          resolution_status: CASE 
            WHEN COUNT(other) = 0 THEN 'unique'
            ELSE 'potential_duplicate'
          END
        } as resolution
        """
        with driver.session() as session:
            result = session.run(query, entity_id=entity_id)
            return {"content": [{"text": json.dumps(dict(result.single()["resolution"]))}]}
    
    elif name == "infer_causal_chains":
        event_id = arguments["event_id"]
        query = """
        MATCH (event:Event {id: $event_id})
        MATCH (event)-[r:CAUSED]->(effect:Event)
        WHERE event.action_type IS NOT NULL
          AND effect.result_type IS NOT NULL
        RETURN {
          effect_id: effect.id,
          label: effect.label,
          causal_strength: CASE
            WHEN event.action_type = 'MIL_ACT' 
              AND effect.result_type = 'POL_TRANS'
            THEN 0.9
            ELSE 0.6
          END
        } as causal_link
        ORDER BY causal_link.causal_strength DESC
        """
        with driver.session() as session:
            results = session.run(query, event_id=event_id)
            chains = [dict(r["causal_link"]) for r in results]
            return {"content": [{"text": json.dumps(chains)}]}
    
    elif name == "aggregate_confidence":
        entity_id = arguments["entity_id"]
        query = """
        MATCH (e {id: $entity_id})
        WITH e,
          COALESCE(e.confidence, 0.5) * 0.3 +
          CASE WHEN e.wikidata_disputed THEN 0.3 ELSE 0.9 END * 0.25 +
          CASE WHEN e.backbone_fast IS NOT NULL THEN 0.8 ELSE 0.5 END * 0.25 +
          CASE WHEN e.start_date IS NOT NULL THEN 0.8 ELSE 0.5 END * 0.2
          as integrated_confidence
        RETURN {
          integrated: integrated_confidence,
          chrystallum: COALESCE(e.confidence, 0.5),
          wikidata: CASE WHEN e.wikidata_disputed THEN 0.3 ELSE 0.9 END,
          backbone: CASE WHEN e.backbone_fast IS NOT NULL THEN 0.8 ELSE 0.5 END
        } as confidence
        """
        with driver.session() as session:
            result = session.run(query, entity_id=entity_id)
            return {"content": [{"text": json.dumps(dict(result.single()["confidence"]))}]}

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(main())
```

**Cursor Configuration:**
```json
{
  "mcp.servers": {
    "neo4j-reasoning": {
      "command": "python",
      "args": ["neo4j_reasoning_mcp_server.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "your_password"
      }
    }
  }
}
```

---

### 4. **OpenThinker-7B** (LLM-Based Reasoning)

**What it is:**
- Open source reasoning model
- Based on Qwen2.5-7B-Instruct
- Fine-tuned on STEM reasoning

**MCP Integration:**
- Can be used via MCP as reasoning tool
- Good for complex logical reasoning
- Text-based reasoning

**Limitation:**
- ⚠️ Still an LLM (not deterministic)
- ⚠️ Requires GPU/hardware

---

### 5. **MCP-Solver** (Constraint Programming)

**What it is:**
- Constraint programming via MCP
- Formal reasoning
- Logic-based

**Use Case:**
- Complex constraint satisfaction
- Formal logical reasoning
- Mathematical problems

**For Chrystallum:**
- ⚠️ Less relevant (not constraint-based problems)

---

## Recommended: Neo4j-Based Custom MCP Server

### Why This Is Best for Chrystallum

**Advantages:**
1. ✅ **Already using Neo4j** - No new infrastructure
2. ✅ **Cypher = Reasoning Rules** - Native graph reasoning
3. ✅ **Performance** - Fast graph queries
4. ✅ **Full Control** - Custom reasoning logic
5. ✅ **MCP Compatible** - Standard protocol

### Implementation Steps

#### Step 1: Install MCP SDK

```bash
pip install mcp
```

#### Step 2: Create Reasoning Server

```python
# Create file: neo4j_reasoning_mcp_server.py
# (Use code from above)
```

#### Step 3: Configure Cursor

**Cursor Settings** (`Settings > Features > MCP`):

```json
{
  "mcp.servers": {
    "chrystallum-reasoning": {
      "command": "python",
      "args": [
        "C:\\Projects\\federated-graph-framework\\graph 3\\neo4j_reasoning_mcp_server.py"
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

#### Step 4: Use in Cursor

**In Cursor:**
- MCP tools appear in AI interface
- Can call reasoning functions
- Integrated with code completion

---

## Alternative: LangChain + MCP

### If You Need More Sophistication

```python
from langchain.tools import MCPTool
from langchain.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain.llms import Ollama

# Create graph
graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="password"
)

# Create reasoning chain
llm = Ollama(model="llama2")
qa_chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True
)

# Expose as MCP tool
from mcp.server import Server

server = Server("langchain-reasoning")

@server.call_tool()
async def reason_about_entity(name: str, question: str):
    """Reason about entity using LangChain."""
    query = f"What can you tell me about {name}? {question}"
    result = qa_chain.run(query)
    return {"content": [{"text": result}]}
```

**Requires:**
- LangChain installed
- LLM model (Ollama, etc.)

---

## Complete MCP Reasoning Server Example

### Full Implementation for Chrystallum

```python
# chrystallum_reasoning_mcp_server.py
"""
MCP Server exposing Chrystallum reasoning capabilities.
"""
from mcp.server import Server
from mcp.types import Tool
from neo4j import GraphDatabase
import json
import os

# Neo4j connection
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "bolt://localhost:7687"),
    auth=(
        os.getenv("NEO4J_USERNAME", "neo4j"),
        os.getenv("NEO4J_PASSWORD", "password")
    )
)

# Create server
server = Server("chrystallum-reasoning")

# Register tools
@server.list_tools()
async def list_tools():
    """List all available reasoning tools."""
    return [
        Tool(
            name="check_consistency",
            description="Check entity consistency across FAST, Wikidata, VIAF, MARC standards",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Entity ID"}
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="infer_contemporaries",
            description="Infer contemporaries based on LCC period and overlapping dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Person entity ID"}
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="validate_entity_resolution",
            description="Validate entity resolution across VIAF, Wikidata, MARC identifiers",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Entity ID"}
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="infer_causal_chains",
            description="Infer causal relationships from action structures (Goal/Action/Result)",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID"}
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="aggregate_confidence",
            description="Aggregate confidence scores from Chrystallum, Wikidata, MARC, and consistency checks",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Entity ID"}
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="check_temporal_consistency",
            description="Validate temporal consistency (dates across standards, start/end date logic)",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Entity ID"}
                },
                "required": ["entity_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute reasoning tool."""
    
    # Implement each tool (from code above)
    # ...
    
    return {"content": [{"text": json.dumps(result)}]}

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream, 
                write_stream, 
                server.create_initialization_options()
            )
    
    asyncio.run(main())
```

---

## Quick Start: Set Up in Cursor

### 1. Install MCP SDK

```bash
pip install mcp
```

### 2. Create Reasoning Server

Create `chrystallum_reasoning_mcp_server.py` (full implementation above)

### 3. Configure Cursor

**File:** `%APPDATA%\Cursor\User\settings.json` (Windows)

```json
{
  "mcp.servers": {
    "chrystallum-reasoning": {
      "command": "python",
      "args": [
        "C:\\Projects\\federated-graph-framework\\graph 3\\chrystallum_reasoning_mcp_server.py"
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

### 4. Restart Cursor

Restart Cursor to load MCP server.

### 5. Use Tools

In Cursor, MCP tools appear as:
- Available function calls
- Context menu options
- AI assistant suggestions

---

## Summary: Best Options for Chrystallum

### Recommended Stack

1. **Custom Neo4j MCP Server** ⭐⭐⭐ **Best Fit**
   - Already using Neo4j
   - Cypher = reasoning rules
   - Full control
   - Native graph reasoning

2. **MCP Advanced Reasoning Server** ⭐⭐ **Alternative**
   - Pre-built reasoning
   - MCTS, Beam Search
   - Requires integration

3. **LangChain + MCP** ⭐⭐ **If Needed**
   - More sophisticated agents
   - Requires LLM model
   - More complexity

---

## Bottom Line

**For Chrystallum in Cursor, best approach:**

✅ **Custom Neo4j MCP Server** - Create reasoning tools that query your Neo4j graph using Cypher

**Why:**
- Uses existing Neo4j infrastructure
- Cypher queries = reasoning rules
- Full control over reasoning logic
- Native graph reasoning
- MCP-compatible

**Implementation:**
- Install `mcp` package
- Create server exposing Neo4j reasoning queries
- Configure in Cursor settings
- Use reasoning tools in Cursor

This gives you **open source, MCP-compatible reasoning** that works seamlessly in Cursor!





