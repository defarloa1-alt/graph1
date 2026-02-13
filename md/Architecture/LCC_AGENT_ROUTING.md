# LCC-Based Agent Routing Architecture

**Date:** December 13, 2025  
**Status:** ✅ Implemented  
**Reason:** Dewey Decimal has only 12.3% coverage for history subjects in Wikidata

---

## The Problem

After importing LCC Class D (History) subjects from Wikidata:

```
Dewey Decimal:  16/130 subjects (12.3%) ❌
LCC Codes:      130/130 subjects (100%) ✅
FAST IDs:       73/130 subjects (56.2%)
```

**Dewey is too sparse for reliable agent routing!**

---

## The Solution: LCC-Based Routing

### LCC (Library of Congress Classification)

**Structure:**
- **Single letter** = Broad subject (D = History)
- **Two letters** = Regional/topical (DG = Italy and Roman history)
- **Numbers** = Specific topics (DG541 = Sack of Rome, 1527)
- **Ranges** = Related topics (DG235-254 = Roman Republic)

**Hierarchy Example:**
```
D                    ← History (World history)
├─ DA                ← Great Britain
├─ DB                ← Austria, Liechtenstein, Hungary, Czechoslovakia
├─ DC                ← France, Andorra, Monaco
├─ DD                ← Germany
├─ DE                ← Mediterranean Region, Greco-Roman World
├─ DF                ← Greece
├─ DG                ← Italy, Malta
│  ├─ DG11-DG365     ← Italy: Description and travel
│  ├─ DG51-DG365     ← Antiquities, Social life, Civilization
│  ├─ DG201-DG365    ← History
│  │  ├─ DG235-DG254 ← Roman Republic (510-27 B.C.)
│  │  │  ├─ DG247-DG249.4  ← Second Punic War
│  │  │  └─ DG247.97       ← Battle of Zama
│  │  ├─ DG260-DG285 ← Roman Empire (27 B.C.-476 A.D.)
│  │  └─ DG311-DG365 ← Medieval and modern Italy (476-)
│  └─ DG401-DG583    ← Local history and description
├─ DH                ← Low Countries (Belgium, Luxembourg, Netherlands)
└─ ...
```

---

## Agent Assignment Strategy

### Seed Agents (Broad Classes)
```
Agent_D    → World History (all periods, all regions)
Agent_DA   → British History
Agent_DG   → Italian & Roman History
Agent_DF   → Greek History
```

### Specialist Agents (Spawned Dynamically)
```
Agent_D spawns:
  → Agent_DG (Italian/Roman specialist)

Agent_DG spawns:
  → Agent_DG235-254 (Roman Republic specialist)
  
Agent_DG235-254 spawns:
  → Agent_DG247 (Punic Wars specialist)
```

### Query Routing Logic

```python
def route_query_to_agent(subject_lcc_code):
    """
    Route a query to the most specific available agent
    """
    # Example: "DG247.97" (Battle of Zama)
    
    # Try most specific first
    if agent_exists("Agent_DG247.97"):
        return "Agent_DG247.97"  # Hyperspecialist
    
    # Try range
    if agent_exists("Agent_DG247-DG249.4"):
        return "Agent_DG247-DG249.4"  # Punic Wars specialist
    
    # Try broader
    if agent_exists("Agent_DG235-254"):
        return "Agent_DG235-254"  # Roman Republic specialist
    
    # Try two-letter
    if agent_exists("Agent_DG"):
        return "Agent_DG"  # Italian/Roman history specialist
    
    # Fallback to single letter
    return "Agent_D"  # General history agent
```

---

## Subject Node Structure

```json
{
  "lcsh_id": "sh85115055",
  "label": "Rome--History--Republic, 510-30 B.C.",
  "unique_id": "lcsh:sh85115055",
  
  "lcc_code": "DG235-254",  // ← AGENT ROUTING KEY ⭐
  "dewey_decimal": "937.05", // ← Optional (12% coverage)
  "fast_id": "fst01210191"   // ← Optional (56% coverage)
}
```

---

## Coverage Statistics

### LCC Class D (History) - Currently Imported

```
Total Subjects:     130
With LCC codes:     130 (100%) ✅
With Dewey codes:   16 (12.3%)
With FAST codes:    73 (56.2%)
```

### Sample Subjects

| LCSH ID | Label | LCC Code | Dewey | FAST |
|---------|-------|----------|-------|------|
| sh95002163 | Sack of Rome, 1527 | DG541-DG541.8 | 945.632072 | - |
| n79032166 | Cicero | DG260.C5-59 | - | 32861 |
| sh85109112 | Second Punic War | DG247-DG249.4 | - | - |
| sh95002368 | Battle of Zama | DG247.97 | - | - |

---

## Benefits of LCC Routing

### 1. Complete Coverage
- ✅ 100% of history subjects have LCC codes (vs. 12% for Dewey)
- ✅ No missing classifications = no routing failures

### 2. Hierarchical Structure
- ✅ Clear parent-child relationships (D → DG → DG235)
- ✅ Enables systematic agent spawning
- ✅ Agents know their expertise boundaries

### 3. Geographic & Topical Organization
- ✅ Regional focus clear from code (DG = Italy, DF = Greece)
- ✅ Topical focus clear from numbers (DG235-254 = Republic)
- ✅ Natural expertise domains for agents

### 4. Library Standard
- ✅ Used by Library of Congress and major research libraries
- ✅ Stable, well-documented
- ✅ Comprehensive authority files available

---

## Implementation Files

### Scripts
- `graph3-1/python/lcsh/scripts/retrieve_lcsh_class_d_complete.py` - Fetch Class D subjects from Wikidata
- `graph3-1/python/lcsh/scripts/import_lcsh_class_d.py` - Import to Neo4j
- `graph3-1/Batch/rebuild_class_d_backbone.bat` - Full pipeline

### Schemas
- `NODE_TYPE_SCHEMAS.md` - Subject node schema with LCC routing
- `Agents/prompts/system/TEST_SUBJECT_AGENT_PROMPT.md` - Agent prompt with LCC explanation

### Documentation
- `CHANGELOG.md` - Complete change history
- `LCC_AGENT_ROUTING.md` - This file

---

## Future Expansion

### Other LCC Classes to Import

```
E: America (General)
F: United States, Canada, Latin America
G: Geography, Anthropology, Recreation
H: Social Sciences
J: Political Science
K: Law
M: Music
N: Fine Arts
P: Language and Literature
Q: Science
R: Medicine
S: Agriculture
T: Technology
U: Military Science
V: Naval Science
Z: Bibliography, Library Science
```

### Priority for Chrystallum (History-Focused)

1. **D** (History - World) ✅ DONE
2. **E** (American History - General)
3. **F** (United States, Canada, Latin America)
4. **G** (Geography, Anthropology)
5. **J** (Political Science - for political events)
6. **U** (Military Science - for military history)

---

## Query Examples

### Example 1: Roman Republic Query

**Query:** "Tell me about Julius Caesar's consulship"

**Routing:**
1. Extract entities → Julius Caesar (Q1048)
2. Query Wikidata → P244 (Library of Congress authority ID): sh85070783, P1149 (LCC): DG260.C5
3. Find Subject node → lcsh:sh85070783, lcc_code: DG260.C5
4. Route to most specific agent:
   - Check `Agent_DG260.C5` → doesn't exist
   - Check `Agent_DG260-285` (Roman Empire) → doesn't exist
   - Check `Agent_DG235-254` (Roman Republic) → **EXISTS** ✅
5. Spawn `Agent_DG260-285` as child of `Agent_DG235-254`
6. Assign query to `Agent_DG260-285`

### Example 2: Cross-Period Query

**Query:** "Compare Greek and Roman democracy"

**Routing:**
1. Identify multiple subjects:
   - Greek democracy → LCC: DF78-DF78.8 (Ancient Greece)
   - Roman democracy → LCC: DG235-254 (Roman Republic)
2. Detect cross-domain query
3. Spawn collaboration:
   - `Agent_DF78` (Greek specialist)
   - `Agent_DG235-254` (Roman Republic specialist)
   - `Agent_D` (coordinator - compares responses)
4. Return integrated response

---

## Comparison: Dewey vs. LCC

| Feature | Dewey Decimal | LCC |
|---------|---------------|-----|
| Coverage (History) | 12.3% ❌ | 100% ✅ |
| Hierarchical | Yes ✅ | Yes ✅ |
| Geographic focus | Weak | Strong ✅ |
| In Wikidata | Sparse | Complete ✅ |
| Agent suitability | Poor (gaps) | Excellent ✅ |

**Winner:** LCC for agent routing ✅

**Dewey Status:** Retained as optional property for cross-referencing

---

## Technical Notes

### LCC Code Parsing

```python
import re

def parse_lcc_code(lcc_code):
    """
    Parse LCC code into components
    
    Examples:
      "D" → class="D", subclass=None, number=None
      "DG" → class="D", subclass="G", number=None
      "DG541" → class="D", subclass="G", number="541"
      "DG235-254" → class="D", subclass="G", number="235-254"
    """
    match = re.match(r'^([A-Z])([A-Z])?(\d+[\d\.-]*)?$', lcc_code)
    if match:
        return {
            'class': match.group(1),
            'subclass': match.group(2),
            'number': match.group(3)
        }
    return None
```

### Agent Naming Convention

```
Agent_{LCC_CODE}

Examples:
  Agent_D            # Seed agent (History)
  Agent_DG           # Regional specialist (Italy/Rome)
  Agent_DG235-254    # Period specialist (Roman Republic)
  Agent_DG247.97     # Event specialist (Battle of Zama)
```

---

## Status

✅ **Architecture designed**  
✅ **Class D subjects imported (130 subjects)**  
✅ **Documentation complete**  
⏳ **Agent spawning logic** (next step)  
⏳ **Cross-domain queries** (future)  
⏳ **Other LCC classes** (E, F, G, etc.)

---

**Conclusion:** LCC provides complete, hierarchical classification coverage for history subjects, making it the ideal foundation for agent routing in Chrystallum. Dewey Decimal, while valuable, has insufficient coverage in Wikidata to serve this purpose.

