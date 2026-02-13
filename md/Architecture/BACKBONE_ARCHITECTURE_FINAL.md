# Chrystallum Backbone Architecture (Final)

**Date:** December 13, 2025  
**Status:** Production Architecture  
**Version:** 2.0

## Executive Summary

After extensive analysis of FAST, LCSH, LCC, and Dewey Decimal Classification systems, we've determined the optimal backbone architecture for Chrystallum's **event-driven knowledge graph**:

**LCSH (Library of Congress Subject Headings) as Primary Backbone**
- Best coverage for events (86%)
- Primary source (FAST is derived from LCSH)
- Most specific subject headings

**Dewey Decimal for Agent Organization**
- Hierarchical agent spawning (937 → 937.05 → 937.052)
- Clear expertise boundaries
- Excellent period coverage

**FAST and LCC as Supplementary Properties**
- Store when available
- Use for cross-referencing
- Not required

---

## The Problem We Solved

### Initial Assumption: FAST as Primary Backbone
We initially chose FAST (Faceted Application of Subject Terminology) as our backbone because:
- It's well-structured
- It's derived from LCSH (authoritative)
- It's designed for linked data

### The Discovery: FAST Fails for Events
Testing revealed **critical coverage gaps**:

```python
# Coverage Test Results for Roman Events:
Battle of Pharsalus: LCSH ✅ | FAST ❌
Battle of Alesia: LCSH ✅ | FAST ❌
Crossing of Rubicon: LCSH ✅ | FAST ❌
Siege of Masada: LCSH ✅ | FAST ❌
Assassination of Caesar: LCSH ✅ | FAST ❌
Battle of Actium: LCSH ✅ | FAST ✅
Siege of Jerusalem: LCSH ✅ | FAST ❌

LCSH Coverage: 86% ✅
FAST Coverage: 14% ❌
```

**Why FAST Fails:**
- FAST is optimized for **entity identification** (people, places)
- Events are too specific for FAST's faceted approach
- LCSH has granular event headings (e.g., "Pharsalus, Battle of, 48 B.C.")
- FAST lacks this granularity

**The Insight:**
*"For an event-driven graph, use the system with the best event coverage as your backbone."*

---

## The Solution: Multi-System Architecture

### 1. **LCSH as Primary Backbone** ⭐

**Purpose:** Subject identification and unique key

**Properties:**
```cypher
(:Subject {
  lcsh_id: "sh85115055",              // ← PRIMARY KEY
  lcsh_heading: "Rome--History--Republic, 510-30 B.C.",
  unique_id: "SUBJECT_LCSH_sh85115055"  // ← Based on LCSH
})
```

**Why LCSH:**
- ✅ **86% event coverage** (best of all systems)
- ✅ **Primary source** (FAST is derived from this)
- ✅ **Specific headings** ("Pharsalus, Battle of, 48 B.C." vs generic "Battles")
- ✅ **Library standard** (universally recognized)
- ✅ **One-step Wikidata lookup** (P244)

**Wikidata Property:** P244 (LCSH ID)

---

### 2. **Dewey Decimal for Agent Routing** ⭐

**Purpose:** Organize agents hierarchically, determine who handles what

**Properties:**
```cypher
(:Subject {
  dewey_decimal: "937.05"  // ← AGENT ASSIGNMENT
})
```

**Agent Organization:**
```
Agent_937 (Ancient Rome - Seed Agent)
├─ Agent_937.01 (Early Italy)
├─ Agent_937.05 (Roman Republic) ← Handles Roman Republic queries
│  ├─ Agent_937.051 (Early Republic)
│  ├─ Agent_937.052 (Late Republic) ← Handles Pharsalus
│  └─ Agent_937.053 (Civil Wars)
└─ Agent_937.06 (Roman Empire)
```

**Agent Spawning Logic:**
```python
query = "Tell me about the Battle of Pharsalus"

# System resolves to Dewey 937.052
agent = find_agent_by_dewey("937.052")
# → Agent_937 (seed) spawns Agent_937.05 (Republic)
# → Agent_937.05 spawns Agent_937.052 (Late Republic specialist)
# → Agent_937.052 generates subgraph
```

**Why Dewey:**
- ✅ **Hierarchical structure** (perfect for agent trees)
- ✅ **Clear boundaries** (each agent owns a Dewey range)
- ✅ **Good period coverage** (Q11772 = 938, Q17167 = 937.05)
- ✅ **Librarian-friendly** (humans understand this)
- ✅ **Natural expertise** (3-digit = broad, 6-digit = hyperspecialized)

**Wikidata Property:** P1036 (Dewey Decimal Classification)

---

### 3. **LCC for Hierarchical Classification**

**Purpose:** Provide hierarchical taxonomy, library shelving codes

**Properties:**
```cypher
(:Subject {
  lcc_code: "DG235-254"  // ← Hierarchical code
})
```

**Hierarchy Example:**
```
D (World History)
└─ DG (Italy)
   └─ DG200-365 (Ancient Rome)
      └─ DG235-254 (Roman Republic)
         └─ DG254 (Late Republic, Civil Wars)
```

**Why LCC:**
- ✅ **Strict hierarchy** (clear parent-child relationships)
- ✅ **Complements LCSH** (same system, different purpose)
- ✅ **Physical shelving** (maps to library organization)
- ✅ **Range notation** (DG235-254 indicates span)

**Wikidata Property:** P1149 (LCC)

---

### 4. **FAST as Supplementary Property**

**Purpose:** Cross-referencing, interoperability

**Properties:**
```cypher
(:Subject {
  fast_id: "fst01210191"  // ← OPTIONAL PROPERTY
})
```

**Why NOT Primary:**
- ❌ **14% event coverage** (too low)
- ❌ **Derivative** (created from LCSH)
- ❌ **Too generic** for events

**Why Keep It:**
- ✅ **When available**, useful for cross-referencing
- ✅ **Some systems use FAST** (interoperability)
- ✅ **Good for people/places** (better entity coverage)

**Wikidata Property:** P2163 (FAST ID)

---

## Subject Node Schema

### Complete Properties:
```cypher
CREATE (:Subject {
  // PRIMARY BACKBONE (required)
  lcsh_id: "sh85115055",              // ← UNIQUE KEY
  lcsh_heading: "Rome--History--Republic, 510-30 B.C.",
  label: "Roman Republic",
  unique_id: "SUBJECT_LCSH_sh85115055",
  
  // AGENT ROUTING (recommended)
  dewey_decimal: "937.05",            // ← Which agent handles this
  
  // HIERARCHICAL CLASSIFICATION (optional)
  lcc_code: "DG235-254",              // ← Library hierarchy
  
  // SUPPLEMENTARY (optional)
  fast_id: "fst01210191",             // ← Property only
  
  // METADATA
  description: "Ancient Roman republican period",
  domain: "history"
})
```

### Validation Rules:
```cypher
// ✅ MUST have LCSH ID
MATCH (s:Subject)
WHERE s.lcsh_id IS NULL
RETURN s.label as invalid_subject;

// ✅ SHOULD have Dewey (for agent routing)
MATCH (s:Subject)
WHERE s.dewey_decimal IS NULL
RETURN s.label as missing_agent_assignment;

// ✅ unique_id MUST be based on LCSH
MATCH (s:Subject)
WHERE NOT s.unique_id STARTS WITH 'SUBJECT_LCSH_'
RETURN s.label as invalid_unique_id;
```

---

## Wikidata Integration Workflow

### Single Query for All Classification Data:
```python
from scripts.tools.wikidata_fast_lookup import get_all_classification_ids

# One function, all IDs
data = get_all_classification_ids("Q17167")

print(data['lcsh_id'])        # PRIMARY: "sh85115055"
print(data['dewey_decimal'])  # AGENT: "937.05"
print(data['lcc_code'])       # HIERARCHY: "DG235-254"
print(data['fast_id'])        # PROPERTY: "fst01210191"
```

### SPARQL Query:
```sparql
SELECT ?itemLabel ?dewey ?lcsh ?lcc ?fast WHERE {
  BIND(wd:Q17167 AS ?item)
  
  OPTIONAL { ?item wdt:P1036 ?dewey . }  # Dewey
  OPTIONAL { ?item wdt:P244 ?lcsh . }    # LCSH (PRIMARY)
  OPTIONAL { ?item wdt:P1149 ?lcc . }    # LCC
  OPTIONAL { ?item wdt:P2163 ?fast . }   # FAST
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

---

## Agent Architecture

### Agent Assignment by Dewey:

```python
class AgentRegistry:
    """Maps Dewey codes to agents"""
    
    agents = {
        "937": Agent_Ancient_Rome,      # Seed agent
        "937.05": Agent_Roman_Republic, # Republic specialist
        "937.052": Agent_Late_Republic, # Civil Wars specialist
        "938": Agent_Ancient_Greece,
        "951": Agent_China,
        "940": Agent_Modern_Europe
    }
    
    def route_query(self, query):
        # Resolve query to Dewey code
        dewey = self.resolve_query_to_dewey(query)
        
        # Find appropriate agent
        agent = self.find_agent(dewey)
        
        # Agent decides if it needs to spawn specialist
        return agent.handle(query, dewey)
```

### Agent Spawning Logic:

```python
class DeweyAgent:
    def __init__(self, dewey_code):
        self.dewey_code = dewey_code
        self.expertise_range = get_dewey_range(dewey_code)
    
    def handle(self, query, query_dewey):
        # Am I specialized enough?
        if self.is_my_expertise(query_dewey):
            return self.generate_subgraph(query)
        else:
            # Spawn more specialized agent
            child_dewey = self.get_child_code(query_dewey)
            child_agent = self.spawn_child(child_dewey)
            return child_agent.handle(query, query_dewey)
```

### Example: Battle of Pharsalus Query

```
User: "Tell me about the Battle of Pharsalus"

Step 1: Resolve to Dewey
  → Battle of Pharsalus (Q48314)
  → Wikidata P1036: Not found directly
  → Infer from period: Roman Republic (Q17167)
  → Wikidata P1036: "937.05"
  → Specific event: "937.052" (Late Republic)

Step 2: Route to Agent
  → Agent_937 (Ancient Rome) receives query
  → Checks dewey_code "937.052"
  → Not my specialty, spawning child...
  → Agent_937.05 (Roman Republic) spawned

Step 3: Specialized Agent
  → Agent_937.05 checks "937.052"
  → Still too specific, spawning child...
  → Agent_937.052 (Late Republic) spawned

Step 4: Expert Handles
  → Agent_937.052: "This is my core expertise!"
  → Generates subgraph:
      * Event: Battle of Pharsalus (Q48314)
      * Person: Julius Caesar (Q1048)
      * Person: Pompey (Q151438)
      * Subject: Rome--History--Republic (sh85115055)
      * Period: Roman Republic (Q17167)
      * Place: Pharsalus (Q207891)
```

---

## Timeline Visualization

### What Drives Timeline Display:

**Period Nodes (Structural Backbone):**
```cypher
MATCH (p:Period)
RETURN 
  p.label as name,
  p.start_date as start,
  p.end_date as end
ORDER BY p.start_date;
```

**Subject Classification (Topical Backbone):**
```cypher
MATCH (p:Period)-[:SUBJECT_OF]->(s:Subject)
RETURN 
  p.label as name,
  p.start_date as start,
  p.end_date as end,
  s.dewey_decimal as classification
ORDER BY p.start_date;
```

**Filtered Timeline (by Dewey):**
```cypher
// Show only Ancient Mediterranean (Dewey 93x)
MATCH (p:Period)-[:SUBJECT_OF]->(s:Subject)
WHERE s.dewey_decimal STARTS WITH '93'
RETURN p, s
ORDER BY p.start_date;
```

### Visual Example:
```
Timeline (Filtered by Dewey 937.x - Roman History):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-750  -500  -250    0    250   500
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Roman Kingdom (937.01)   ██████
Roman Republic (937.05)      ████████████████
Roman Empire (937.06)                    ██████████████
```

---

## Comparison Table

| System | Purpose | Coverage (Events) | Hierarchy | Agent Use | Status |
|--------|---------|-------------------|-----------|-----------|--------|
| **LCSH** | Subject ID | **86%** ✅ | ❌ No | Identification | **PRIMARY** |
| **Dewey** | Classification | Good (Periods) | ✅ Yes | **Routing** | **REQUIRED** |
| **LCC** | Classification | Moderate | ✅ Yes | Hierarchy | Optional |
| **FAST** | Cross-reference | 14% ❌ | ❌ No | None | Property |

---

## Migration Impact

### Scripts to Update:

1. ✅ **`wikidata_fast_lookup.py`** - Now fetches all IDs in one query
2. ⏳ **`create_subject_nodes.py`** - Use LCSH as primary key
3. ⏳ **`import_periods.py`** - Link periods to LCSH subjects
4. ⏳ **`generate_period_taxonomy.py`** - NEW: Dewey-driven generation
5. ⏳ **All subgraph generation scripts** - Update Subject linking

### Neo4j Data Migration:

```cypher
// Add LCSH IDs to existing Subject nodes
MATCH (s:Subject)
WHERE s.lcsh_id IS NULL AND s.fast_id IS NOT NULL
SET s.lcsh_id = resolve_fast_to_lcsh(s.fast_id);

// Update unique_id to be LCSH-based
MATCH (s:Subject)
WHERE s.unique_id STARTS WITH 'SUBJECT_FAST_'
SET s.unique_id = 'SUBJECT_LCSH_' + s.lcsh_id;

// Add Dewey codes for agent routing
MATCH (s:Subject)
WHERE s.dewey_decimal IS NULL
// Query Wikidata or infer from domain
SET s.dewey_decimal = get_dewey_for_subject(s.lcsh_id);
```

### Agent Prompt Updates:

```markdown
## Backbone Integration (Updated Dec 2025)

When generating subgraphs, link entities to Subject nodes using LCSH:

1. Provide entity QID (e.g., Q48314 for Battle of Pharsalus)
2. System automatically queries Wikidata for:
   - P244 (LCSH ID) - PRIMARY for subject identification
   - P1036 (Dewey) - for agent routing
   - P1149 (LCC) - for hierarchical classification
   - P2163 (FAST) - supplementary property only
3. System creates Subject node with LCSH as unique key
4. Your subgraph links to this Subject via SUBJECT_OF relationship

You do NOT need to manually look up classification codes.
You MUST provide accurate QIDs.
```

---

## Decision Rationale

### Why This Architecture Works:

1. **Event-Driven Focus**
   - LCSH has the best event coverage (86%)
   - Chrystallum is event-driven → use best event system

2. **Agent Organization**
   - Dewey provides clear hierarchical structure
   - Natural expertise boundaries (3-digit → 6-digit)
   - Librarian-friendly (humans understand this)

3. **Backbone Stability**
   - LCSH is primary source (FAST is derivative)
   - Library of Congress is authoritative
   - Long-term stability

4. **Flexibility**
   - FAST/LCC as properties (use when available)
   - Can query by any classification system
   - Interoperable with library systems

5. **Performance**
   - Single Wikidata query gets all IDs
   - No multi-step resolution (LCSH → FAST)
   - Direct P244 lookup

---

## Summary

**Primary Backbone:** LCSH (best event coverage, unique key)  
**Agent Organization:** Dewey (hierarchical routing, spawning logic)  
**Supplementary:** FAST & LCC (properties for cross-referencing)

**The Rule:**
> "Every entity MUST link to a Subject node identified by LCSH ID"

**The Benefit:**
> "Dewey routes queries to the right agent, LCSH provides specific subject identification, FAST & LCC enable interoperability"

---

**Status:** Ready for implementation  
**Next Steps:** Refactor existing scripts, migrate Neo4j data, update agent prompts


