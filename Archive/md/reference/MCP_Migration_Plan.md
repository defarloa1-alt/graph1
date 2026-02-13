# MCP Migration Plan: Minimal Disruption Approach

**Question:** How disruptive would moving to MCP be? Seems like a lot of refactoring.

**Answer:** **Can be done incrementally with minimal disruption** - Here's how.

---

## Current State Analysis

### Current Dependencies

**Agent Code Imports:**
```python
# scripts/agents/enrich_and_link_ancient_rome.py
from scripts.agents.fast_lookup_tool import FASTLookupTool
from scripts.utils.wikidata_sparql_queries import query_wikidata_sparql

# scripts/agents/agent_router.py
from scripts.agents.fast_lookup_tool import FASTLookupTool

# scripts/agents/example_usage.py
from scripts.agents.agent_router import route_to_agent
from scripts.agents.fast_lookup_tool import FASTLookupTool
```

**Direct Function Calls:**
- `FASTLookupTool().lookup()`
- `query_wikidata_entity(qid)`
- `check_entity_exists(qid)`

**Key Insight:** Agents are **standalone scripts** - they can run independently. This makes incremental migration easier.

---

## Migration Strategy: Incremental & Non-Breaking

### Phase 1: Add MCP Server (No Changes to Existing Code)

**Goal:** Create MCP server that wraps existing functions

**Approach:** **Adapter Pattern** - MCP tools call existing Python functions

**File:** `scripts/mcp/chrystallum_mcp_server.py`

```python
# MCP Server wraps existing code - NO refactoring needed
from scripts.agents.fast_lookup_tool import FASTLookupTool
from scripts.utils.wikidata_sparql_queries import query_wikidata_sparql
from scripts.utils.chrystallum_query_tools import check_entity_exists

@mcp_tool
def lookup_fast(subject: str) -> dict:
    """MCP wrapper around existing FASTLookupTool."""
    tool = FASTLookupTool()  # Use existing code
    return tool.lookup(subject)  # No changes to FASTLookupTool

@mcp_tool
def query_wikidata(qid: str) -> dict:
    """MCP wrapper around existing function."""
    return query_wikidata_entity(qid)  # Use existing code

@mcp_tool
def resolve_entity(qid: str) -> dict:
    """MCP wrapper around existing function."""
    entity = check_entity_exists(qid=qid)  # Use existing code
    return {"found": entity is not None, "entity": entity}
```

**Impact:** ✅ **Zero disruption** - Existing code unchanged, MCP just wraps it

**Time:** 2-4 hours (create MCP server, wrap existing functions)

---

### Phase 2: Optional MCP Usage (Agents Can Choose)

**Goal:** Allow agents to use MCP, but keep old code working

**Approach:** **Feature Flag** - Agents can use MCP or direct imports

**File:** `scripts/agents/enrich_and_link_ancient_rome.py`

```python
# Option 1: Use MCP (new)
USE_MCP = os.getenv("USE_MCP", "false").lower() == "true"

if USE_MCP:
    from scripts.mcp.mcp_client import MCPClient
    mcp = MCPClient()
    fast_result = await mcp.call_tool("lookup_fast", subject="Roman Republic")
else:
    # Option 2: Use existing code (old, still works)
    from scripts.agents.fast_lookup_tool import FASTLookupTool
    tool = FASTLookupTool()
    fast_result = tool.lookup("Roman Republic")
```

**Impact:** ✅ **Zero disruption** - Old code still works, new code optional

**Time:** 1-2 hours per agent (add feature flag, test both paths)

---

### Phase 3: Migrate One Agent at a Time

**Goal:** Gradually migrate agents to MCP

**Approach:** Migrate one agent, test, then move to next

**Migration Order (Low Risk First):**

1. **Test Agent** (`import_ancient_rome_test.py`)
   - Low risk (test script)
   - Simple (few dependencies)
   - **Time:** 1 hour

2. **Simple Agents** (`lookup_ancient_rome_fast.py`)
   - Only uses FAST lookup
   - **Time:** 1 hour

3. **Complex Agents** (`enrich_and_link_ancient_rome.py`)
   - Multiple dependencies
   - **Time:** 2-3 hours

4. **Core Router** (`agent_router.py`)
   - Used by other agents
   - **Time:** 2-3 hours

**Impact:** ✅ **Low disruption** - One agent at a time, can rollback if issues

**Total Time:** 6-9 hours (spread over days/weeks)

---

### Phase 4: Remove Old Code (Optional, Later)

**Goal:** Clean up old direct imports (only after all agents migrated)

**Approach:** Remove direct imports, keep MCP only

**When:** After Phase 3 complete, all agents tested

**Impact:** ⚠️ **Medium disruption** - But only after everything works

**Time:** 2-3 hours (remove old code, update tests)

---

## Minimal Disruption Approach

### Strategy: **Parallel Implementation**

**Keep Both Systems Running:**

```
┌─────────────────────────────────────┐
│  Existing Code (Still Works)       │
│  - fast_lookup_tool.py             │
│  - wikidata_sparql_queries.py      │
│  - chrystallum_query_tools.py      │
└─────────────────────────────────────┘
              ↓ (wraps)
┌─────────────────────────────────────┐
│  MCP Server (New)                   │
│  - Wraps existing functions         │
│  - No changes to existing code      │
└─────────────────────────────────────┘
              ↓ (optional)
┌─────────────────────────────────────┐
│  Agents (Gradually Migrate)         │
│  - Can use MCP or direct imports    │
│  - Feature flag controls behavior   │
└─────────────────────────────────────┘
```

**Key:** Existing code **never changes** - MCP just wraps it

---

## Refactoring Effort Breakdown

### What Needs Refactoring?

| Component | Refactoring Needed | Effort | Risk |
|-----------|-------------------|--------|------|
| **MCP Server** | Create new file, wrap existing functions | 2-4 hours | Low |
| **Agent Code** | Add feature flag, optional MCP usage | 1-2 hours/agent | Low |
| **Existing Tools** | **None** - Keep as-is | 0 hours | None |
| **Batch Scripts** | **None** - Not affected | 0 hours | None |
| **Tests** | Update to test both paths | 2-3 hours | Low |

### Total Effort

**Minimum (Just MCP Server):** 2-4 hours
- Create MCP server
- Wrap existing functions
- Test MCP tools work

**Incremental (One Agent):** +1-2 hours
- Add feature flag to one agent
- Test both paths work

**Full Migration (All Agents):** 6-9 hours
- Migrate all agents
- Test everything
- Remove old code (optional)

---

## Risk Assessment

### Low Risk Approach

**✅ Can Test Without Breaking Anything:**

1. **Create MCP Server** (doesn't affect existing code)
2. **Test MCP Tools** (standalone testing)
3. **Add Feature Flag** (old code still works)
4. **Test One Agent** (can rollback easily)
5. **Gradually Migrate** (one at a time)

**Rollback Plan:**
- If MCP has issues, just set `USE_MCP=false`
- Old code still works
- No data loss
- No breaking changes

### High Risk Approach (Avoid This)

**❌ Don't Do This:**
- Refactor all agents at once
- Remove old code before testing
- Change existing function signatures
- Break existing imports

---

## Practical Migration Steps

### Step 1: Create MCP Server (2-4 hours)

**File:** `scripts/mcp/chrystallum_mcp_server.py`

```python
"""
MCP Server - Wraps existing Chrystallum tools
No changes to existing code - just wraps it
"""

from mcp.server import Server
from scripts.agents.fast_lookup_tool import FASTLookupTool
from scripts.utils.wikidata_sparql_queries import query_wikidata_sparql
from scripts.utils.chrystallum_query_tools import check_entity_exists

server = Server("chrystallum-tools")

@server.tool()
def lookup_fast(subject: str) -> dict:
    """Wrap existing FASTLookupTool."""
    tool = FASTLookupTool()
    return tool.lookup(subject)

@server.tool()
def query_wikidata(qid: str) -> dict:
    """Wrap existing Wikidata function."""
    return query_wikidata_entity(qid)

@server.tool()
def resolve_entity(qid: str) -> dict:
    """Wrap existing entity check."""
    entity = check_entity_exists(qid=qid)
    return {"found": entity is not None, "entity": entity}
```

**Test:** Run MCP server, test tools work

**Impact:** ✅ Zero - doesn't affect existing code

---

### Step 2: Add MCP Client Helper (1 hour)

**File:** `scripts/mcp/mcp_client.py`

```python
"""
MCP Client Helper - Makes it easy for agents to use MCP
"""

import os
from typing import Optional

class MCPClient:
    """Helper to call MCP tools."""
    
    def __init__(self):
        self.use_mcp = os.getenv("USE_MCP", "false").lower() == "true"
        if self.use_mcp:
            # Initialize MCP connection
            pass
    
    async def call_tool(self, tool_name: str, **kwargs) -> dict:
        """Call MCP tool."""
        if not self.use_mcp:
            raise ValueError("MCP not enabled")
        # Call MCP tool
        pass
```

**Impact:** ✅ Zero - new file, doesn't affect existing code

---

### Step 3: Update One Test Agent (1-2 hours)

**File:** `scripts/agents/import_ancient_rome_test.py`

```python
# Add at top
import os
USE_MCP = os.getenv("USE_MCP", "false").lower() == "true"

if USE_MCP:
    from scripts.mcp.mcp_client import MCPClient
    mcp = MCPClient()
else:
    from scripts.agents.fast_lookup_tool import FASTLookupTool

# In function
if USE_MCP:
    fast_result = await mcp.call_tool("lookup_fast", subject="Roman Republic")
else:
    tool = FASTLookupTool()
    fast_result = tool.lookup("Roman Republic")
```

**Test:** 
- Run with `USE_MCP=false` (old code)
- Run with `USE_MCP=true` (new code)
- Both should work

**Impact:** ✅ Low - can rollback with env var

---

### Step 4: Gradually Migrate Other Agents (1-2 hours each)

**Repeat Step 3 for each agent:**
- `lookup_ancient_rome_fast.py`
- `enrich_and_link_ancient_rome.py`
- `agent_router.py`

**Impact:** ✅ Low - one at a time, can test each

---

## Time Investment

### Minimum Viable (Just MCP Server)

**Time:** 2-4 hours
- Create MCP server
- Wrap 3-4 core tools
- Test MCP works

**Benefit:** MCP available, can use in new agents

**Risk:** None - doesn't affect existing code

---

### Incremental (One Agent)

**Time:** +1-2 hours
- Add feature flag to one agent
- Test both paths

**Benefit:** One agent uses MCP, others unchanged

**Risk:** Low - can rollback with env var

---

### Full Migration (All Agents)

**Time:** 6-9 hours total
- MCP server: 2-4 hours
- Migrate 4-5 agents: 4-5 hours

**Benefit:** All agents use MCP, cleaner code

**Risk:** Low - incremental, can rollback

---

## Comparison: Big Bang vs. Incremental

### ❌ Big Bang Approach (High Disruption)

**What:** Refactor everything at once

**Time:** 2-3 days
- Refactor all agents
- Remove old code
- Update all tests
- Fix all issues

**Risk:** High
- Everything breaks at once
- Hard to rollback
- Long downtime

**Not Recommended**

---

### ✅ Incremental Approach (Low Disruption)

**What:** Add MCP, migrate gradually

**Time:** 6-9 hours (spread over days)

**Risk:** Low
- One component at a time
- Easy rollback
- No downtime

**Recommended**

---

## Recommendation

### Start Small, Grow Gradually

**Week 1:**
1. Create MCP server (2-4 hours)
2. Wrap 3-4 core tools
3. Test MCP works

**Week 2:**
4. Add feature flag to one test agent (1-2 hours)
5. Test both paths work
6. Use in new agents going forward

**Week 3-4:**
7. Migrate one agent per week (1-2 hours each)
8. Test each migration
9. Keep old code until all migrated

**Later (Optional):**
10. Remove old direct imports (2-3 hours)
11. Clean up feature flags

**Total:** 6-9 hours over 3-4 weeks

**Risk:** Very low - incremental, testable, rollback-able

---

## Alternative: Don't Migrate Existing Code

### Option: MCP for New Code Only

**Strategy:** 
- Keep existing agents as-is
- Use MCP for new agents only
- No refactoring needed

**Time:** 2-4 hours (just create MCP server)

**Benefit:** 
- No disruption to existing code
- New agents get MCP benefits
- Can migrate later if desired

**Trade-off:** 
- Some code duplication
- But minimal disruption

---

## Conclusion

### Is MCP Disruptive?

**Short Answer:** **No, if done incrementally**

**Key Points:**
1. ✅ **MCP wraps existing code** - No refactoring needed
2. ✅ **Feature flags** - Old code still works
3. ✅ **Incremental migration** - One agent at a time
4. ✅ **Easy rollback** - Can disable MCP anytime
5. ✅ **Low risk** - Test each step

**Minimum Effort:** 2-4 hours (just create MCP server)

**Full Migration:** 6-9 hours (spread over weeks)

**Risk Level:** Low (if done incrementally)

**Recommendation:** Start with MCP server, migrate gradually, or use MCP for new code only.


