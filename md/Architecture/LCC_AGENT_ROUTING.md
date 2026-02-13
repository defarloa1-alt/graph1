# LCC-Based Agent Routing Architecture

**Date:** December 13, 2025  
**Status:** âœ… Implemented  
**Reason:** Dewey Decimal has only 12.3% coverage for history subjects in Wikidata

---

## The Problem

After importing LCC Class D (History) subjects from Wikidata:

```
Dewey Decimal:  16/130 subjects (12.3%) âŒ
LCC Codes:      130/130 subjects (100%) âœ…
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
D                    â† History (World history)
â”œâ”€ DA                â† Great Britain
â”œâ”€ DB                â† Austria, Liechtenstein, Hungary, Czechoslovakia
â”œâ”€ DC                â† France, Andorra, Monaco
â”œâ”€ DD                â† Germany
â”œâ”€ DE                â† Mediterranean Region, Greco-Roman World
â”œâ”€ DF                â† Greece
â”œâ”€ DG                â† Italy, Malta
â”‚  â”œâ”€ DG11-DG365     â† Italy: Description and travel
â”‚  â”œâ”€ DG51-DG365     â† Antiquities, Social life, Civilization
â”‚  â”œâ”€ DG201-DG365    â† History
â”‚  â”‚  â”œâ”€ DG235-DG254 â† Roman Republic (510-27 B.C.)
â”‚  â”‚  â”‚  â”œâ”€ DG247-DG249.4  â† Second Punic War
â”‚  â”‚  â”‚  â””â”€ DG247.97       â† Battle of Zama
â”‚  â”‚  â”œâ”€ DG260-DG285 â† Roman Empire (27 B.C.-476 A.D.)
â”‚  â”‚  â””â”€ DG311-DG365 â† Medieval and modern Italy (476-)
â”‚  â””â”€ DG401-DG583    â† Local history and description
â”œâ”€ DH                â† Low Countries (Belgium, Luxembourg, Netherlands)
â””â”€ ...
```

---

## Agent Assignment Strategy

### Seed Agents (Broad Classes)
```
Agent_D    â†’ World History (all periods, all regions)
Agent_DA   â†’ British History
Agent_DG   â†’ Italian & Roman History
Agent_DF   â†’ Greek History
```

### Specialist Agents (Spawned Dynamically)
```
Agent_D spawns:
  â†’ Agent_DG (Italian/Roman specialist)

Agent_DG spawns:
  â†’ Agent_DG235-254 (Roman Republic specialist)
  
Agent_DG235-254 spawns:
  â†’ Agent_DG247 (Punic Wars specialist)
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
  
  "lcc_code": "DG235-254",  // â† AGENT ROUTING KEY â­
  "dewey_decimal": "937.05", // â† Optional (12% coverage)
  "fast_id": "fst01210191"   // â† Optional (56% coverage)
}
```

---

## Coverage Statistics

### LCC Class D (History) - Currently Imported

```
Total Subjects:     130
With LCC codes:     130 (100%) âœ…
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
- âœ… 100% of history subjects have LCC codes (vs. 12% for Dewey)
- âœ… No missing classifications = no routing failures

### 2. Hierarchical Structure
- âœ… Clear parent-child relationships (D â†’ DG â†’ DG235)
- âœ… Enables systematic agent spawning
- âœ… Agents know their expertise boundaries

### 3. Geographic & Topical Organization
- âœ… Regional focus clear from code (DG = Italy, DF = Greece)
- âœ… Topical focus clear from numbers (DG235-254 = Republic)
- âœ… Natural expertise domains for agents

### 4. Library Standard
- âœ… Used by Library of Congress and major research libraries
- âœ… Stable, well-documented
- âœ… Comprehensive authority files available

---

## Implementation Files

### Scripts
- `graph3-1/python/lcsh/scripts/retrieve_lcsh_class_d_complete.py` - Fetch Class D subjects from Wikidata
- `graph3-1/python/lcsh/scripts/import_lcsh_class_d.py` - Import to Neo4j
- `graph3-1/Batch/rebuild_class_d_backbone.bat` - Full pipeline

### Schemas
- `md/Reference/NODE_SCHEMA_CANONICAL_SOURCES.md` - Subject node schema with LCC routing
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

1. **D** (History - World) âœ… DONE
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
1. Extract entities â†’ Julius Caesar (Q1048)
2. Query Wikidata â†’ P244 (Library of Congress authority ID): sh85070783, P1149 (LCC): DG260.C5
3. Find Subject node â†’ lcsh:sh85070783, lcc_code: DG260.C5
4. Route to most specific agent:
   - Check `Agent_DG260.C5` â†’ doesn't exist
   - Check `Agent_DG260-285` (Roman Empire) â†’ doesn't exist
   - Check `Agent_DG235-254` (Roman Republic) â†’ **EXISTS** âœ…
5. Spawn `Agent_DG260-285` as child of `Agent_DG235-254`
6. Assign query to `Agent_DG260-285`

### Example 2: Cross-Period Query

**Query:** "Compare Greek and Roman democracy"

**Routing:**
1. Identify multiple subjects:
   - Greek democracy â†’ LCC: DF78-DF78.8 (Ancient Greece)
   - Roman democracy â†’ LCC: DG235-254 (Roman Republic)
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
| Coverage (History) | 12.3% âŒ | 100% âœ… |
| Hierarchical | Yes âœ… | Yes âœ… |
| Geographic focus | Weak | Strong âœ… |
| In Wikidata | Sparse | Complete âœ… |
| Agent suitability | Poor (gaps) | Excellent âœ… |

**Winner:** LCC for agent routing âœ…

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
      "D" â†’ class="D", subclass=None, number=None
      "DG" â†’ class="D", subclass="G", number=None
      "DG541" â†’ class="D", subclass="G", number="541"
      "DG235-254" â†’ class="D", subclass="G", number="235-254"
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

âœ… **Architecture designed**  
âœ… **Class D subjects imported (130 subjects)**  
âœ… **Documentation complete**  
â³ **Agent spawning logic** (next step)  
â³ **Cross-domain queries** (future)  
â³ **Other LCC classes** (E, F, G, etc.)

---

**Conclusion:** LCC provides complete, hierarchical classification coverage for history subjects, making it the ideal foundation for agent routing in Chrystallum. Dewey Decimal, while valuable, has insufficient coverage in Wikidata to serve this purpose.


