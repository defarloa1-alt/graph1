# Node Type Schemas - Knowledge Graph Templates

**Purpose:** Define required properties and edges for each node type  
**Date:** December 12, 2025  
**Use:** Guide agents in generating complete, valid subgraphs

---

## Design Principle: Ontology-Specific Labels

**Your graph should reflect YOUR ontology, not generic abstractions.**

❌ **Don't use generic labels:**
```cypher
(p:Period:Concept)  // "Concept" is meaningless overgeneralization
```

✅ **Use specific domain labels:**
```cypher
(p:Period)  // Clear, specific, reflects your ontology
```

### Backbone Alignment: Multi-Authority System

**Authority Sources by Domain:**
- **Periods** → **Wikidata** (P580/P582 temporal bounds, P155/P156 succession, P31 classification)
- **Subjects** → **LCSH** (Library of Congress Subject Headings for topical classification)
- **Objects/Materials/Activities/Agents** → **Getty AAT** (Art & Architecture Thesaurus)

**Wikidata as Period Authority:**
- Temporal data: P580 (start time), P582 (end time) in proleptic Gregorian calendar
- Geographic scope: P276 (location), P17 (country)
- Succession: P155 (follows), P156 (followed by)
- Classification: P31 (instance of) - dynasty, historical period, archaeological period, etc.
- External mappings: P244 (LCSH), P1014 (Getty AAT)

**LCSH as Subject Classification Backbone:**
- Topical classification for all entities
- 86% event coverage in Wikidata
- Hierarchical structure via broader/narrower terms
- Drives agent routing via subject hierarchy

**Implementation:**
1. **Properties** on Period nodes: `{qid: "Q1747689", start_year: -27, end_year: 476, lcsh_id: "sh85115055"}`
2. **Relationships** to Subject nodes: `(period:Period)-[:SUBJECT_OF]->(subject:Subject {lcsh_id: "sh85115055"})`

---

## Schema Format

Each node type has:
1. **Required Properties** - Must be present
2. **Optional Properties** - Should be included if known
3. **Required Edges** - Must connect to other nodes
4. **Optional Edges** - Should connect if relevant
5. **Examples** - Reference implementations

---

## Subject Node Schema ⭐ TOPICAL CLASSIFICATION (LCSH Authority System)

### Node Labels
```cypher
:Subject
```

**Purpose:** Topical/thematic classification using **Library of Congress Subject Headings (LCSH)** as the backbone authority system

**Backbone Authority:** LCSH (Library of Congress Subject Headings) - the authoritative controlled vocabulary managed by the Library of Congress

**What Subjects Are:** Subjects represent **what entities are ABOUT** (themes, topics), not what they ARE (structure)

**Critical Distinction:**
- ✅ **Topical subjects** - Politics, Military, Religion, Culture, Economics (use these!)
- ❌ **Structural categories** - Time, Geography (these are redundant - use entity types instead!)

**Navigation vs. Classification:**
- **Navigate** through hierarchies: Period → Parent Period, Place → Parent Place, Year → Next Year
- **Classify** by topic: Event → Military Subject, Person → Political Subject

### NEW ARCHITECTURE (Dec 2025): LCSH as Backbone Authority System

**LCSH = The Backbone:**
- ✅ **Authoritative controlled vocabulary** maintained by Library of Congress
- ✅ **86% event coverage** in Wikidata (vs. 14% for FAST)
- ✅ **Primary source** (FAST is derived from LCSH)
- ✅ **Better granularity** for historical events (e.g., "Pharsalus, Battle of, 48 B.C.")
- ✅ **Agent routing** via broader/narrower term hierarchies

**LCSH Hierarchy for Agent Routing:**
- ✅ **LCSH broader/narrower terms used for agent hierarchy**
- Example: "Rome--History" (broader) → "Rome--History--Republic, 510-30 B.C." (narrower)
- Agent spawning follows LCSH subject tree: sh85114934 → sh85115055 → specialists

**FAST as Supplementary Property:**
- Store FAST ID when available from Wikidata (P2163) (~54% coverage)
- Not required; used for cross-referencing only

### Required Properties

| Property       | Type   | Format     | Example                                | Notes                                                    |
| -------------- | ------ | ---------- | -------------------------------------- | -------------------------------------------------------- |
| `qid`          | string | Q[0-9]+    | "Q17167"                               | Wikidata QID (for federation)                            |
| `lcsh_id`      | string | sh[0-9]{8} | "sh85115055"                           | LCSH ID (PRIMARY BACKBONE) ⭐                             |
| `lcsh_heading` | string | text       | "Rome--History--Republic, 510-30 B.C." | Library of Congress Subject Heading (authoritative form) |
| `label`        | string | text       | "Roman Republic"                       | Human-readable label                                     |
| `unique_id`    | string | pattern    | "SUBJECT_LCSH_sh85115055"              | System ID (based on LCSH)                                |

### Optional Properties (Classification Metadata)

| Property         | Type     | Format | Example                                              | Notes                               |
| ---------------- | -------- | ------ | ---------------------------------------------------- | ----------------------------------- |
| `description`    | string   | text   | "Ancient Roman republican period"                    | Short description                   |
| `aliases`        | string[] | text   | ["Roman Republic", "Res Publica"]                    | Alternative names/labels            |
| `domain`         | string   | text   | "history"                                            | Subject domain                      |
| `scope_note`     | string   | text   | "Use for works on the Roman Republican period..."    | LCSH scope note (usage guidance)    |
| `broader_terms`  | string[] | text   | ["Rome--History"]                                    | Broader LCSH terms (for hierarchy)  |
| `narrower_terms` | string[] | text   | ["Rome--History--Servile Wars"]                      | Narrower LCSH terms (for hierarchy) |
| `related_terms`  | string[] | text   | ["Republican Rome"]                                  | Related LCSH terms                  |
| `wikidata_url`   | string   | URL    | "https://www.wikidata.org/wiki/Q17167"               | Full Wikidata URL                   |
| `lcsh_url`       | string   | URL    | "https://id.loc.gov/authorities/subjects/sh85115055" | LCSH authority record URL           |

### Optional Properties (Authority Crosswalk via Wikidata) ⭐ NEW

**Wikidata as Universal Crosswalk Hub:** Use QID to fetch IDs from multiple authority systems via Wikidata properties. Enables interoperability with different agent preferences and external systems.

| Property         | Type     | Format              | Example                           | Wikidata Property | Coverage | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ----------------- | -------- | ---------------------------------------------------- |
| `fast_id`        | string   | fst[0-9]{8}         | "fst01210191"                     | P2163             | ~54%     | FAST ID (OCLC Faceted Application of Subject Terminology) - derived from LCSH, post-coordinated |
| `dewey`          | string   | [0-9]{3}\.[0-9]+    | "937.05"                          | P1036             | ~12%     | Dewey Decimal Classification - numerical classification for agent routing |
| `lcc_code`       | string   | [A-Z]{1,3}[0-9]+    | "DG235-254"                       | P1149             | varies   | Library of Congress Classification - alphanumeric shelf classification |
| `viaf_id`        | string   | [0-9]+              | "123456789"                       | P214              | varies   | Virtual International Authority File - international aggregator linking multiple national libraries |
| `gnd_id`         | string   | [0-9]{4,}(-[0-9xX])? | "4043912-4"                      | P227              | varies   | Gemeinsame Normdatei (GND) - German National Library authority ID |

**Fetching Crosswalk IDs:**
```python
# Query Wikidata to get all authority IDs for a Subject
import requests

qid = "Q17167"  # Roman Republic
url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
response = requests.get(url, headers={'User-Agent': 'YourBot/1.0'})
data = response.json()
claims = data['entities'][qid]['claims']

# Extract authority IDs
lcsh_id = claims['P244'][0]['mainsnak']['datavalue']['value']  # sh85115055
fast_id = claims['P2163'][0]['mainsnak']['datavalue']['value'] # fst01210191
dewey = claims['P1036'][0]['mainsnak']['datavalue']['value']   # 937.05
lcc = claims['P1149'][0]['mainsnak']['datavalue']['value']     # DG235-254
viaf_id = claims['P214'][0]['mainsnak']['datavalue']['value']  # 123456789
```

**Use Cases:**
- **Agent routing**: Different agents prefer different authorities (FAST facets vs LCSH pre-coordinated)
- **External system integration**: Link to library catalogs, databases using their preferred authority
- **Multilingual support**: VIAF connects to French (BnF), German (DNB), Japanese (NDL) national libraries
- **Cross-referencing**: Validate subject mappings across multiple authority systems

### Required Edges

**None** - Subject nodes are leaf nodes in the taxonomy (entities link TO them)

### LCSH Hierarchy Edges (Between Subjects)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `BROADER_THAN` | Subject | OUT | `(:Subject {lcsh_id: "sh85061097", lcsh_heading: "Historic buildings"})-[:BROADER_THAN]->(:Subject {lcsh_id: "sh85077493", lcsh_heading: "Literary landmarks"})` |

**Purpose:** BROADER_THAN relationships create the LCSH subject hierarchy used for agent routing and topical navigation.

**Database Status:** ✅ 10,992 BROADER_THAN relationships exist in the graph

**Direction Design:** Single-direction relationships (no NARROWER_THAN inverse)
```cypher
// Query narrower terms (traverse forward →)
MATCH (broader:Subject)-[:BROADER_THAN]->(narrower:Subject)
WHERE broader.lcsh_id = "sh85114934"
RETURN narrower

// Query broader terms (traverse backward ←)
MATCH (narrower:Subject)<-[:BROADER_THAN]-(broader:Subject)
WHERE narrower.lcsh_id = "sh85115055"
RETURN broader

// Multi-hop traversal (all ancestors)
MATCH path = (s:Subject {lcsh_id: "sh85115055"})<-[:BROADER_THAN*]-(ancestor)
RETURN ancestor

// Multi-hop traversal (all descendants)
MATCH path = (s:Subject {lcsh_id: "sh85114934"})-[:BROADER_THAN*]->(descendant)
RETURN descendant
```

**Why No NARROWER_THAN?** Neo4j relationships are bidirectional - you can traverse `BROADER_THAN` in both directions using `->` and `<-` in Cypher. Creating inverse relationships would duplicate all 10,992 edges and waste storage.

**Denormalized Properties:** For query performance, broader/narrower terms are ALSO stored as properties:
- `broader_ids` / `broader_terms` - Arrays of parent subject IDs and labels
- `narrower_ids` / `narrower_terms` - Arrays of child subject IDs and labels

**When to Use Each:**
- Use `BROADER_THAN` relationships for:
  - Graph visualization (shows lines between nodes)
  - Multi-hop traversal (find all ancestors/descendants)
  - Cypher path queries (`-[:BROADER_THAN*]->`)
  
- Use `broader_ids`/`broader_terms` properties for:
  - Quick single-level lookups (no traversal needed)
  - Displaying breadcrumbs in UI
  - API responses with immediate parent/child info

### Common Edges (Incoming)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `SUBJECT_OF` | Event, Person, Org | IN | `(event:Event {label: "Punic Wars"})-[:SUBJECT_OF]->(subject:Subject {lcsh_id: "sh85109289"})` |
| `DEFINED_BY` | PropertyRegistry | IN | `(reg:PropertyRegistry)-[:DEFINED_BY]->(subject)` |

**Note:** Do NOT link structural entity types to their obvious subjects:
- ❌ `(period:Period)-[:SUBJECT_OF]->(:Subject {label: "Time"})` - redundant!
- ❌ `(place:Place)-[:SUBJECT_OF]->(:Subject {label: "Geography"})` - redundant!
- ✅ `(event:Event {label: "Battle of Zama"})-[:SUBJECT_OF]->(:Subject {lcsh_id: "sh85109289"})` - good!

### Template

```cypher
CREATE (subject:Subject {
  // REQUIRED
  qid: "Q17167",  // Wikidata QID
  lcsh_id: "sh85115055",
  lcsh_heading: "Rome--History--Republic, 510-30 B.C.",
  label: "Roman Republic",
  unique_id: "SUBJECT_LCSH_sh85115055",
  
  // OPTIONAL (rich metadata)
  description: "Period of Roman history from overthrow of monarchy (510 BCE) to establishment of empire (27 BCE)",
  aliases: ["Roman Republic", "Res Publica Romana", "Republican Rome"],
  domain: "history",
  scope_note: "Use for works on the Roman Republican period. For specific events, see narrower terms.",
  broader_terms: ["Rome--History"],
  narrower_terms: [
    "Rome--History--Servile Wars, 135-71 B.C.",
    "Rome--History--Republic, 265-30 B.C.",
    "Rome--History--Social War, 91-88 B.C."
  ],
  related_terms: ["Republican government", "Roman Senate"],
  lcc_code: "DG235-254",  // Library shelving metadata
  fast_id: "fst01210191",  // Supplementary cross-reference
  wikidata_url: "https://www.wikidata.org/wiki/Q17167",
  lcsh_url: "https://id.loc.gov/authorities/subjects/sh85115055"
})

// Example usage - entities link TO topical subjects
CREATE (event:Event {label: "Battle of Pharsalus", qid: "Q48314"})
CREATE (event)-[:SUBJECT_OF]->(subject)

// BROADER_THAN relationships for LCSH hierarchy (visualizes as graph edges)
CREATE (broader:Subject {lcsh_id: "sh85114934", lcsh_heading: "Rome--History"})
CREATE (narrower:Subject {lcsh_id: "sh85115055", lcsh_heading: "Rome--History--Republic, 510-30 B.C."})
CREATE (broader)-[:BROADER_THAN]->(narrower)

// Denormalized properties mirror the relationships for quick lookup
SET narrower.broader_ids = ["sh85114934"]
SET narrower.broader_terms = ["Rome--History"]
SET broader.narrower_ids = [..., "sh85115055", ...]
SET broader.narrower_terms = [..., "Rome--History--Republic, 510-30 B.C.", ...]
```

**Visualization:**
```
┌─────────────────────────────────┐
│ Rome--History                   │  
│ (sh85114934)                    │
│ broader_ids: []                 │
│ narrower_ids: [sh85115055, ...] │  ← Properties (quick lookup)
└─────────────────┬───────────────┘
                  │ BROADER_THAN       ← Relationship (graph edge/line)
                  ↓
┌─────────────────────────────────┐
│ Rome--History--Republic         │
│ (sh85115055)                    │
│ broader_ids: [sh85114934]       │  ← Properties (denormalized)
│ narrower_ids: [...]             │
└─────────────────────────────────┘
```

### Critical Notes

**LCSH IDs are PRIMARY BACKBONE:**
- ✅ Primary key: `lcsh_id` (not FAST)
- ✅ Unique identifier: `SUBJECT_LCSH_sh85115055`
- ✅ Best coverage for events (86%)

**Dewey Decimal for AGENT ROUTING:**
- ✅ Determines which agent handles a query
- ✅ Hierarchical agent spawning (937 → 937.05 → 937.052)
- ✅ Good coverage for historical periods

**FAST as SUPPLEMENTARY PROPERTY:**
- ✅ Store when available from Wikidata P2163
- ✅ Use for cross-referencing
- ❌ NOT required (poor event coverage)
- ❌ NOT primary key

**LCC as LIBRARY METADATA:**
- ✅ Library shelving code (optional)
- ✅ Stored for interoperability with library systems
- ❌ NOT used for agent routing (LCSH hierarchy handles this)

**Subject nodes enable:**
1. Topical discovery (find all entities about "Military history")
2. Cross-domain connections (link Politics to Military events)
3. Library of Congress alignment (LCSH/LCC interoperability)
4. Agent routing (Dewey code → agent assignment)
5. Thematic browsing (explore by topic, not just by time/place)

**Ontology Principle:**
- **Structure** = Entity types + Hierarchies (Period → Period, Place → Place)
- **Topics** = Subject classifications (Event → Military, Person → Politics)
- Don't confuse the two!

**Workflow for Subject Creation:**
1. **Get entity QID** from source or Wikidata search
2. **Query Wikidata** for subject properties:
   - P244 (LCSH ID) - PRIMARY (required)
   - P1149 (LCC) - optional library metadata
   - P2163 (FAST) - optional supplementary property
3. **Get broader/narrower terms** from LCSH vocabulary
4. **Create Subject node** with complete properties including qid, lcsh_id

---

## Facet Node Types ⭐ UNIVERSAL FACET CLASSIFICATION

### Overview
Facet nodes provide a universal, reusable classification system for all major node types (Period, Event, Place, etc.), supporting faceted search, filtering, and semantic enrichment. Each facet is a node with a specific type and properties, and is linked to entities via explicit relationships.

### Facet Class Table
| Facet Class         | Label         | Definition                                                        | Example Wikidata QIDs           |
|---------------------|--------------|-------------------------------------------------------------------|---------------------------------|
| PoliticalFacet      | Political    | Periods defined by states, regimes, dynasties, governance         | Q11514315, Q3624078, Q164950    |
| CulturalFacet       | Cultural     | Cultural eras, shared practices, identity, literature, arts       | Q185363, Q735, Q11042           |
| TechnologicalFacet  | Technological| Tool regimes, production technologies, industrial phases          | Q11016, Q255, Q33767            |
| ReligiousFacet      | Religious    | Religious movements, institutions, doctrinal eras                 | Q9174, Q432, Q5043              |
| EconomicFacet       | Economic     | Economic systems, trade regimes, financial structures             | Q8134, Q7406919, Q184754        |
| MilitaryFacet       | Military     | Warfare, conquests, military systems, strategic eras              | Q8473, Q198, Q40231             |
| EnvironmentalFacet  | Environmental| Climate regimes, ecological shifts, environmental phases          | Q756, Q2715388, Q629            |
| DemographicFacet    | Demographic  | Population structure, migration, urbanization waves               | Q37577, Q208188, Q7937          |
| IntellectualFacet   | Intellectual | Schools of thought, philosophical or scholarly movements          | Q5891, Q5893, Q333              |
| ScientificFacet     | Scientific   | Scientific paradigms, revolutions, epistemic frameworks           | Q336, Q309, Q170058             |
| ArtisticFacet       | Artistic     | Art movements, architectural styles, aesthetic regimes            | Q968159, Q32880, Q735           |
| SocialFacet         | Social       | Social norms, class structures, social movements                  | Q2695280, Q49773, Q8436         |
| LinguisticFacet     | Linguistic   | Language families, scripts, linguistic shifts                     | Q315, Q8192, Q8196              |
| ArchaeologicalFacet | Archaeological| Material-culture periods, stratigraphy, typologies               | Q1190554, Q23442, Q11767        |
| DiplomaticFacet     | Diplomatic   | International systems, alliances, treaty regimes                  | Q186509, Q1065, Q3624078        |

### Facet Node Labels
- :Facet (abstract, not instantiated)
- :PoliticalFacet, :CulturalFacet, :TechnologicalFacet, :ReligiousFacet, :EconomicFacet, :MilitaryFacet, :EnvironmentalFacet, :DemographicFacet, :IntellectualFacet, :ScientificFacet, :ArtisticFacet, :SocialFacet, :LinguisticFacet, :ArchaeologicalFacet, :DiplomaticFacet

### Example Properties (per facet type)
- `unique_id`: e.g., "POLITICALFACET_{qid}", "TEMPORALFACET_{start}_{end}_{label}"
- `label`: Human-readable label
- `definition`: Facet definition (optional)
- `source_qid`: Wikidata QID (if available)
- Additional properties as needed (e.g., `start_year`, `end_year`, `region_qid`, `lat`, `lon`)

### Example Cypher Templates
```cypher
CREATE (pf:PoliticalFacet:Facet {
  unique_id: "POLITICALFACET_Q3624078",
  label: "Sovereign State",
  definition: "Periods defined by states, regimes, dynasties, governance structures",
  source_qid: "Q3624078"
})

MATCH (p:Period {qid: "Q11761"}), (pf:PoliticalFacet {unique_id: "POLITICALFACET_Q3624078"})
MERGE (p)-[:HAS_POLITICAL_FACET]->(pf)
```

### Relationships
- `HAS_[FACET_TYPE]_FACET` (any node) → [Facet Subclass] (e.g., HAS_POLITICAL_FACET, HAS_TECHNOLOGICAL_FACET)
- Each entity can point to multiple facets of different types, supporting multi-dimensional classification.

### Integration Notes
- All major node types should link to at least one facet node of each relevant type.
- Facet nodes are reusable: multiple entities can point to the same facet.
- Facet nodes can be extended (e.g., :ChronologicalFacet, :CulturalFacet) as needed.
- This system supports universal filtering, faceted search, and semantic navigation across the graph.

---

## Schema Format

Each node type has:
1. **Required Properties** - Must be present
2. **Optional Properties** - Should be included if known
3. **Required Edges** - Must connect to other nodes
4. **Optional Edges** - Should connect if relevant
5. **Examples** - Reference implementations

---

## Subject Node Schema ⭐ TOPICAL CLASSIFICATION (LCSH Authority System)

### Node Labels
```cypher
:Subject
```

**Purpose:** Topical/thematic classification using **Library of Congress Subject Headings (LCSH)** as the backbone authority system

**Backbone Authority:** LCSH (Library of Congress Subject Headings) - the authoritative controlled vocabulary managed by the Library of Congress

**What Subjects Are:** Subjects represent **what entities are ABOUT** (themes, topics), not what they ARE (structure)

**Critical Distinction:**
- ✅ **Topical subjects** - Politics, Military, Religion, Culture, Economics (use these!)
- ❌ **Structural categories** - Time, Geography (these are redundant - use entity types instead!)

**Navigation vs. Classification:**
- **Navigate** through hierarchies: Period → Parent Period, Place → Parent Place, Year → Next Year
- **Classify** by topic: Event → Military Subject, Person → Political Subject

### NEW ARCHITECTURE (Dec 2025): LCSH as Backbone Authority System

**LCSH = The Backbone:**
- ✅ **Authoritative controlled vocabulary** maintained by Library of Congress
- ✅ **86% event coverage** in Wikidata (vs. 14% for FAST)
- ✅ **Primary source** (FAST is derived from LCSH)
- ✅ **Better granularity** for historical events (e.g., "Pharsalus, Battle of, 48 B.C.")
- ✅ **Agent routing** via broader/narrower term hierarchies

**LCSH Hierarchy for Agent Routing:**
- ✅ **LCSH broader/narrower terms used for agent hierarchy**
- Example: "Rome--History" (broader) → "Rome--History--Republic, 510-30 B.C." (narrower)
- Agent spawning follows LCSH subject tree: sh85114934 → sh85115055 → specialists

**FAST as Supplementary Property:**
- Store FAST ID when available from Wikidata (P2163) (~54% coverage)
- Not required; used for cross-referencing only

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q17167" | Wikidata QID (for federation) |
| `lcsh_id` | string | sh[0-9]{8} | "sh85115055" | LCSH ID (PRIMARY BACKBONE) ⭐ |
| `lcsh_heading` | string | text | "Rome--History--Republic, 510-30 B.C." | Library of Congress Subject Heading (authoritative form) |
| `label` | string | text | "Roman Republic" | Human-readable label |
| `unique_id` | string | pattern | "SUBJECT_LCSH_sh85115055" | System ID (based on LCSH) |

### Optional Properties (Classification Metadata)

| Property         | Type     | Format              | Example                           | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ---------------------------------------------------- |
| `description`    | string   | text                | "Ancient Roman republican period" | Short description                                    |
| `aliases`        | string[] | text                | ["Roman Republic", "Res Publica"] | Alternative names/labels                             |
| `domain`         | string   | text                | "history"                         | Subject domain                                       |
| `scope_note`     | string   | text                | "Use for works on the Roman Republican period..." | LCSH scope note (usage guidance) |
| `broader_terms`  | string[] | text                | ["Rome--History"]                 | Broader LCSH terms (for hierarchy)                   |
| `narrower_terms` | string[] | text                | ["Rome--History--Servile Wars"]   | Narrower LCSH terms (for hierarchy)                  |
| `related_terms`  | string[] | text                | ["Republican Rome"]               | Related LCSH terms                                   |
| `wikidata_url`   | string   | URL                 | "https://www.wikidata.org/wiki/Q17167" | Full Wikidata URL                          |
| `lcsh_url`       | string   | URL                 | "https://id.loc.gov/authorities/subjects/sh85115055" | LCSH authority record URL            |

### Optional Properties (Authority Crosswalk via Wikidata) ⭐ NEW

**Wikidata as Universal Crosswalk Hub:** Use QID to fetch IDs from multiple authority systems via Wikidata properties. Enables interoperability with different agent preferences and external systems.

| Property         | Type     | Format              | Example                           | Wikidata Property | Coverage | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ----------------- | -------- | ---------------------------------------------------- |
| `fast_id`        | string   | fst[0-9]{8}         | "fst01210191"                     | P2163             | ~54%     | FAST ID (OCLC Faceted Application of Subject Terminology) - derived from LCSH, post-coordinated |
| `dewey`          | string   | [0-9]{3}\.[0-9]+    | "937.05"                          | P1036             | ~12%     | Dewey Decimal Classification - numerical classification for agent routing |
| `lcc_code`       | string   | [A-Z]{1,3}[0-9]+    | "DG235-254"                       | P1149             | varies   | Library of Congress Classification - alphanumeric shelf classification |
| `viaf_id`        | string   | [0-9]+              | "123456789"                       | P214              | varies   | Virtual International Authority File - international aggregator linking multiple national libraries |
| `gnd_id`         | string   | [0-9]{4,}(-[0-9xX])? | "4043912-4"                      | P227              | varies   | Gemeinsame Normdatei (GND) - German National Library authority ID |

**Fetching Crosswalk IDs:**
```python
# Query Wikidata to get all authority IDs for a Subject
import requests

qid = "Q17167"  # Roman Republic
url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
response = requests.get(url, headers={'User-Agent': 'YourBot/1.0'})
data = response.json()
claims = data['entities'][qid]['claims']

# Extract authority IDs
lcsh_id = claims['P244'][0]['mainsnak']['datavalue']['value']  # sh85115055
fast_id = claims['P2163'][0]['mainsnak']['datavalue']['value'] # fst01210191
dewey = claims['P1036'][0]['mainsnak']['datavalue']['value']   # 937.05
lcc = claims['P1149'][0]['mainsnak']['datavalue']['value']     # DG235-254
viaf_id = claims['P214'][0]['mainsnak']['datavalue']['value']  # 123456789
```

**Use Cases:**
- **Agent routing**: Different agents prefer different authorities (FAST facets vs LCSH pre-coordinated)
- **External system integration**: Link to library catalogs, databases using their preferred authority
- **Multilingual support**: VIAF connects to French (BnF), German (DNB), Japanese (NDL) national libraries
- **Cross-referencing**: Validate subject mappings across multiple authority systems

### Required Edges

**None** - Subject nodes are leaf nodes in the taxonomy (entities link TO them)

### LCSH Hierarchy Edges (Between Subjects)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `BROADER_THAN` | Subject | OUT | `(:Subject {lcsh_id: "sh85061097", lcsh_heading: "Historic buildings"})-[:BROADER_THAN]->(:Subject {lcsh_id: "sh85077493", lcsh_heading: "Literary landmarks"})` |

**Purpose:** BROADER_THAN relationships create the LCSH subject hierarchy used for agent routing and topical navigation.

**Database Status:** ✅ 10,992 BROADER_THAN relationships exist in the graph

**Direction Design:** Single-direction relationships (no NARROWER_THAN inverse)
```cypher
// Query narrower terms (traverse forward →)
MATCH (broader:Subject)-[:BROADER_THAN]->(narrower:Subject)
WHERE broader.lcsh_id = "sh85114934"
RETURN narrower

// Query broader terms (traverse backward ←)
MATCH (narrower:Subject)<-[:BROADER_THAN]-(broader:Subject)
WHERE narrower.lcsh_id = "sh85115055"
RETURN broader

// Multi-hop traversal (all ancestors)
MATCH path = (s:Subject {lcsh_id: "sh85115055"})<-[:BROADER_THAN*]-(ancestor)
RETURN ancestor

// Multi-hop traversal (all descendants)
MATCH path = (s:Subject {lcsh_id: "sh85114934"})-[:BROADER_THAN*]->(descendant)
RETURN descendant
```

**Why No NARROWER_THAN?** Neo4j relationships are bidirectional - you can traverse `BROADER_THAN` in both directions using `->` and `<-` in Cypher. Creating inverse relationships would duplicate all 10,992 edges and waste storage.

**Denormalized Properties:** For query performance, broader/narrower terms are ALSO stored as properties:
- `broader_ids` / `broader_terms` - Arrays of parent subject IDs and labels
- `narrower_ids` / `narrower_terms` - Arrays of child subject IDs and labels

**When to Use Each:**
- Use `BROADER_THAN` relationships for:
  - Graph visualization (shows lines between nodes)
  - Multi-hop traversal (find all ancestors/descendants)
  - Cypher path queries (`-[:BROADER_THAN*]->`)
  
- Use `broader_ids`/`broader_terms` properties for:
  - Quick single-level lookups (no traversal needed)
  - Displaying breadcrumbs in UI
  - API responses with immediate parent/child info

### Common Edges (Incoming)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `SUBJECT_OF` | Event, Person, Org | IN | `(event:Event {label: "Punic Wars"})-[:SUBJECT_OF]->(subject:Subject {lcsh_id: "sh85109289"})` |
| `DEFINED_BY` | PropertyRegistry | IN | `(reg:PropertyRegistry)-[:DEFINED_BY]->(subject)` |

**Note:** Do NOT link structural entity types to their obvious subjects:
- ❌ `(period:Period)-[:SUBJECT_OF]->(:Subject {label: "Time"})` - redundant!
- ❌ `(place:Place)-[:SUBJECT_OF]->(:Subject {label: "Geography"})` - redundant!
- ✅ `(event:Event {label: "Battle of Zama"})-[:SUBJECT_OF]->(:Subject {lcsh_id: "sh85109289"})` - good!

### Template

```cypher
CREATE (subject:Subject {
  // REQUIRED
  qid: "Q17167",  // Wikidata QID
  lcsh_id: "sh85115055",
  lcsh_heading: "Rome--History--Republic, 510-30 B.C.",
  label: "Roman Republic",
  unique_id: "SUBJECT_LCSH_sh85115055",
  
  // OPTIONAL (rich metadata)
  description: "Period of Roman history from overthrow of monarchy (510 BCE) to establishment of empire (27 BCE)",
  aliases: ["Roman Republic", "Res Publica Romana", "Republican Rome"],
  domain: "history",
  scope_note: "Use for works on the Roman Republican period. For specific events, see narrower terms.",
  broader_terms: ["Rome--History"],
  narrower_terms: [
    "Rome--History--Servile Wars, 135-71 B.C.",
    "Rome--History--Republic, 265-30 B.C.",
    "Rome--History--Social War, 91-88 B.C."
  ],
  related_terms: ["Republican government", "Roman Senate"],
  lcc_code: "DG235-254",  // Library shelving metadata
  fast_id: "fst01210191",  // Supplementary cross-reference
  wikidata_url: "https://www.wikidata.org/wiki/Q17167",
  lcsh_url: "https://id.loc.gov/authorities/subjects/sh85115055"
})

// Example usage - entities link TO topical subjects
CREATE (event:Event {label: "Battle of Pharsalus", qid: "Q48314"})
CREATE (event)-[:SUBJECT_OF]->(subject)

// BROADER_THAN relationships for LCSH hierarchy (visualizes as graph edges)
CREATE (broader:Subject {lcsh_id: "sh85114934", lcsh_heading: "Rome--History"})
CREATE (narrower:Subject {lcsh_id: "sh85115055", lcsh_heading: "Rome--History--Republic, 510-30 B.C."})
CREATE (broader)-[:BROADER_THAN]->(narrower)

// Denormalized properties mirror the relationships for quick lookup
SET narrower.broader_ids = ["sh85114934"]
SET narrower.broader_terms = ["Rome--History"]
SET broader.narrower_ids = [..., "sh85115055", ...]
SET broader.narrower_terms = [..., "Rome--History--Republic, 510-30 B.C.", ...]
```

**Visualization:**
```
┌─────────────────────────────────┐
│ Rome--History                   │  
│ (sh85114934)                    │
│ broader_ids: []                 │
│ narrower_ids: [sh85115055, ...] │  ← Properties (quick lookup)
└─────────────────┬───────────────┘
                  │ BROADER_THAN       ← Relationship (graph edge/line)
                  ↓
┌─────────────────────────────────┐
│ Rome--History--Republic         │
│ (sh85115055)                    │
│ broader_ids: [sh85114934]       │  ← Properties (denormalized)
│ narrower_ids: [...]             │
└─────────────────────────────────┘
```

### Critical Notes

**LCSH IDs are PRIMARY BACKBONE:**
- ✅ Primary key: `lcsh_id` (not FAST)
- ✅ Unique identifier: `SUBJECT_LCSH_sh85115055`
- ✅ Best coverage for events (86%)

**Dewey Decimal for AGENT ROUTING:**
- ✅ Determines which agent handles a query
- ✅ Hierarchical agent spawning (937 → 937.05 → 937.052)
- ✅ Good coverage for historical periods

**FAST as SUPPLEMENTARY PROPERTY:**
- ✅ Store when available from Wikidata P2163
- ✅ Use for cross-referencing
- ❌ NOT required (poor event coverage)
- ❌ NOT primary key

**LCC as LIBRARY METADATA:**
- ✅ Library shelving code (optional)
- ✅ Stored for interoperability with library systems
- ❌ NOT used for agent routing (LCSH hierarchy handles this)

**Subject nodes enable:**
1. Topical discovery (find all entities about "Military history")
2. Cross-domain connections (link Politics to Military events)
3. Library of Congress alignment (LCSH/LCC interoperability)
4. Agent routing (Dewey code → agent assignment)
5. Thematic browsing (explore by topic, not just by time/place)

**Ontology Principle:**
- **Structure** = Entity types + Hierarchies (Period → Period, Place → Place)
- **Topics** = Subject classifications (Event → Military, Person → Politics)
- Don't confuse the two!

**Workflow for Subject Creation:**
1. **Get entity QID** from source or Wikidata search
2. **Query Wikidata** for subject properties:
   - P244 (LCSH ID) - PRIMARY (required)
   - P1149 (LCC) - optional library metadata
   - P2163 (FAST) - optional supplementary property
3. **Get broader/narrower terms** from LCSH vocabulary
4. **Create Subject node** with complete properties including qid, lcsh_id

---

## Facet Node Types ⭐ UNIVERSAL FACET CLASSIFICATION

### Overview
Facet nodes provide a universal, reusable classification system for all major node types (Period, Event, Place, etc.), supporting faceted search, filtering, and semantic enrichment. Each facet is a node with a specific type and properties, and is linked to entities via explicit relationships.

### Facet Class Table
| Facet Class         | Label         | Definition                                                        | Example Wikidata QIDs           |
|---------------------|--------------|-------------------------------------------------------------------|---------------------------------|
| PoliticalFacet      | Political    | Periods defined by states, regimes, dynasties, governance         | Q11514315, Q3624078, Q164950    |
| CulturalFacet       | Cultural     | Cultural eras, shared practices, identity, literature, arts       | Q185363, Q735, Q11042           |
| TechnologicalFacet  | Technological| Tool regimes, production technologies, industrial phases          | Q11016, Q255, Q33767            |
| ReligiousFacet      | Religious    | Religious movements, institutions, doctrinal eras                 | Q9174, Q432, Q5043              |
| EconomicFacet       | Economic     | Economic systems, trade regimes, financial structures             | Q8134, Q7406919, Q184754        |
| MilitaryFacet       | Military     | Warfare, conquests, military systems, strategic eras              | Q8473, Q198, Q40231             |
| EnvironmentalFacet  | Environmental| Climate regimes, ecological shifts, environmental phases          | Q756, Q2715388, Q629            |
| DemographicFacet    | Demographic  | Population structure, migration, urbanization waves               | Q37577, Q208188, Q7937          |
| IntellectualFacet   | Intellectual | Schools of thought, philosophical or scholarly movements          | Q5891, Q5893, Q333              |
| ScientificFacet     | Scientific   | Scientific paradigms, revolutions, epistemic frameworks           | Q336, Q309, Q170058             |
| ArtisticFacet       | Artistic     | Art movements, architectural styles, aesthetic regimes            | Q968159, Q32880, Q735           |
| SocialFacet         | Social       | Social norms, class structures, social movements                  | Q2695280, Q49773, Q8436         |
| LinguisticFacet     | Linguistic   | Language families, scripts, linguistic shifts                     | Q315, Q8192, Q8196              |
| ArchaeologicalFacet | Archaeological| Material-culture periods, stratigraphy, typologies               | Q1190554, Q23442, Q11767        |
| DiplomaticFacet     | Diplomatic   | International systems, alliances, treaty regimes                  | Q186509, Q1065, Q3624078        |

### Facet Node Labels
- :Facet (abstract, not instantiated)
- :PoliticalFacet, :CulturalFacet, :TechnologicalFacet, :ReligiousFacet, :EconomicFacet, :MilitaryFacet, :EnvironmentalFacet, :DemographicFacet, :IntellectualFacet, :ScientificFacet, :ArtisticFacet, :SocialFacet, :LinguisticFacet, :ArchaeologicalFacet, :DiplomaticFacet

### Example Properties (per facet type)
- `unique_id`: e.g., "POLITICALFACET_{qid}", "TEMPORALFACET_{start}_{end}_{label}"
- `label`: Human-readable label
- `definition`: Facet definition (optional)
- `source_qid`: Wikidata QID (if available)
- Additional properties as needed (e.g., `start_year`, `end_year`, `region_qid`, `lat`, `lon`)

### Example Cypher Templates
```cypher
CREATE (pf:PoliticalFacet:Facet {
  unique_id: "POLITICALFACET_Q3624078",
  label: "Sovereign State",
  definition: "Periods defined by states, regimes, dynasties, governance structures",
  source_qid: "Q3624078"
})

MATCH (p:Period {qid: "Q11761"}), (pf:PoliticalFacet {unique_id: "POLITICALFACET_Q3624078"})
MERGE (p)-[:HAS_POLITICAL_FACET]->(pf)
```

### Relationships
- `HAS_[FACET_TYPE]_FACET` (any node) → [Facet Subclass] (e.g., HAS_POLITICAL_FACET, HAS_TECHNOLOGICAL_FACET)
- Each entity can point to multiple facets of different types, supporting multi-dimensional classification.

### Integration Notes
- All major node types should link to at least one facet node of each relevant type.
- Facet nodes are reusable: multiple entities can point to the same facet.
- Facet nodes can be extended (e.g., :ChronologicalFacet, :CulturalFacet) as needed.
- This system supports universal filtering, faceted search, and semantic navigation across the graph.

---

## Schema Format

Each node type has:
1. **Required Properties** - Must be present
2. **Optional Properties** - Should be included if known
3. **Required Edges** - Must connect to other nodes
4. **Optional Edges** - Should connect if relevant
5. **Examples** - Reference implementations

---

## Subject Node Schema ⭐ TOPICAL CLASSIFICATION (LCSH Authority System)

### Node Labels
```cypher
:Subject
```

**Purpose:** Topical/thematic classification using **Library of Congress Subject Headings (LCSH)** as the backbone authority system

**Backbone Authority:** LCSH (Library of Congress Subject Headings) - the authoritative controlled vocabulary managed by the Library of Congress

**What Subjects Are:** Subjects represent **what entities are ABOUT** (themes, topics), not what they ARE (structure)

**Critical Distinction:**
- ✅ **Topical subjects** - Politics, Military, Religion, Culture, Economics (use these!)
- ❌ **Structural categories** - Time, Geography (these are redundant - use entity types instead!)

**Navigation vs. Classification:**
- **Navigate** through hierarchies: Period → Parent Period, Place → Parent Place, Year → Next Year
- **Classify** by topic: Event → Military Subject, Person → Political Subject

### NEW ARCHITECTURE (Dec 2025): LCSH as Backbone Authority System

**LCSH = The Backbone:**
- ✅ **Authoritative controlled vocabulary** maintained by Library of Congress
- ✅ **86% event coverage** in Wikidata (vs. 14% for FAST)
- ✅ **Primary source** (FAST is derived from LCSH)
- ✅ **Better granularity** for historical events (e.g., "Pharsalus, Battle of, 48 B.C.")
- ✅ **Agent routing** via broader/narrower term hierarchies

**LCSH Hierarchy for Agent Routing:**
- ✅ **LCSH broader/narrower terms used for agent hierarchy**
- Example: "Rome--History" (broader) → "Rome--History--Republic, 510-30 B.C." (narrower)
- Agent spawning follows LCSH subject tree: sh85114934 → sh85115055 → specialists

**FAST as Supplementary Property:**
- Store FAST ID when available from Wikidata (P2163) (~54% coverage)
- Not required; used for cross-referencing only

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q17167" | Wikidata QID (for federation) |
| `lcsh_id` | string | sh[0-9]{8} | "sh85115055" | LCSH ID (PRIMARY BACKBONE) ⭐ |
| `lcsh_heading` | string | text | "Rome--History--Republic, 510-30 B.C." | Library of Congress Subject Heading (authoritative form) |
| `label` | string | text | "Roman Republic" | Human-readable label |
| `unique_id` | string | pattern | "SUBJECT_LCSH_sh85115055" | System ID (based on LCSH) |

### Optional Properties (Classification Metadata)

| Property         | Type     | Format              | Example                           | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ---------------------------------------------------- |
| `description`    | string   | text                | "Ancient Roman republican period" | Short description                                    |
| `aliases`        | string[] | text                | ["Roman Republic", "Res Publica"] | Alternative names/labels                             |
| `domain`         | string   | text                | "history"                         | Subject domain                                       |
| `scope_note`     | string   | text                | "Use for works on the Roman Republican period..." | LCSH scope note (usage guidance) |
| `broader_terms`  | string[] | text                | ["Rome--History"]                 | Broader LCSH terms (for hierarchy)                   |
| `narrower_terms` | string[] | text                | ["Rome--History--Servile Wars"]   | Narrower LCSH terms (for hierarchy)                  |
| `related_terms`  | string[] | text                | ["Republican Rome"]               | Related LCSH terms                                   |
| `wikidata_url`   | string   | URL                 | "https://www.wikidata.org/wiki/Q17167" | Full Wikidata URL                          |
| `lcsh_url`       | string   | URL                 | "https://id.loc.gov/authorities/subjects/sh85115055" | LCSH authority record URL            |

### Optional Properties (Authority Crosswalk via Wikidata) ⭐ NEW

**Wikidata as Universal Crosswalk Hub:** Use QID to fetch IDs from multiple authority systems via Wikidata properties. Enables interoperability with different agent preferences and external systems.

| Property         | Type     | Format              | Example                           | Wikidata Property | Coverage | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ----------------- | -------- | ---------------------------------------------------- |
| `fast_id`        | string   | fst[0-9]{8}         | "fst01210191"                     | P2163             | ~54%     | FAST ID (OCLC Faceted Application of Subject Terminology) - derived from LCSH, post-coordinated |
| `dewey`          | string   | [0-9]{3}\.[0-9]+    | "937.05"                          | P1036             | ~12%     | Dewey Decimal Classification - numerical classification for agent routing |
| `lcc_code`       | string   | [A-Z]{1,3}[0-9]+    | "DG235-254"                       | P1149             | varies   | Library of Congress Classification - alphanumeric shelf classification |
| `viaf_id`        | string   | [0-9]+              | "123456789"                       | P214              | varies   | Virtual International Authority File - international aggregator linking multiple national libraries |
| `gnd_id`         | string   | [0-9]{4,}(-[0-9xX])? | "4043912-4"                      | P227              | varies   | Gemeinsame Normdatei (GND) - German National Library authority ID |

**Fetching Crosswalk IDs:**
```python
# Query Wikidata to get all authority IDs for a Subject
import requests

qid = "Q17167"  # Roman Republic
url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
response = requests.get(url, headers={'User-Agent': 'YourBot/1.0'})
data = response.json()
claims = data['entities'][qid]['claims']

# Extract authority IDs
lcsh_id = claims['P244'][0]['mainsnak']['datavalue']['value']  # sh85115055
fast_id = claims['P2163'][0]['mainsnak']['datavalue']['value'] # fst01210191
dewey = claims['P1036'][0]['mainsnak']['datavalue']['value']   # 937.05
lcc = claims['P1149'][0]['mainsnak']['datavalue']['value']     # DG235-254
viaf_id = claims['P214'][0]['mainsnak']['datavalue']['value']  # 123456789
```

**Use Cases:**
- **Agent routing**: Different agents prefer different authorities (FAST facets vs LCSH pre-coordinated)
- **External system integration**: Link to library catalogs, databases using their preferred authority
- **Multilingual support**: VIAF connects to French (BnF), German (DNB), Japanese (NDL) national libraries
- **Cross-referencing**: Validate subject mappings across multiple authority systems

### Required Edges

**None** - Subject nodes are leaf nodes in the taxonomy (entities link TO them)

### LCSH Hierarchy Edges (Between Subjects)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `BROADER_THAN` | Subject | OUT | `(:Subject {lcsh_id: "sh85061097", lcsh_heading: "Historic buildings"})-[:BROADER_THAN]->(:Subject {lcsh_id: "sh85077493", lcsh_heading: "Literary landmarks"})` |

**Purpose:** BROADER_THAN relationships create the LCSH subject hierarchy used for agent routing and topical navigation.

**Database Status:** ✅ 10,992 BROADER_THAN relationships exist in the graph

**Direction Design:** Single-direction relationships (no NARROWER_THAN inverse)
```cypher
// Query narrower terms (traverse forward →)
MATCH (broader:Subject)-[:BROADER_THAN]->(narrower:Subject)
WHERE broader.lcsh_id = "sh85114934"
RETURN narrower

// Query broader terms (traverse backward ←)
MATCH (narrower:Subject)<-[:BROADER_THAN]-(broader:Subject)
WHERE narrower.lcsh_id = "sh85115055"
RETURN broader

// Multi-hop traversal (all ancestors)
MATCH path = (s:Subject {lcsh_id: "sh85115055"})<-[:BROADER_THAN*]-(ancestor)
RETURN ancestor

// Multi-hop traversal (all descendants)
MATCH path = (s:Subject {lcsh_id: "sh85114934"})-[:BROADER_THAN*]->(descendant)
RETURN descendant
```

**Why No NARROWER_THAN?** Neo4j relationships are bidirectional - you can traverse `BROADER_THAN` in both directions using `->` and `<-` in Cypher. Creating inverse relationships would duplicate all 10,992 edges and waste storage.

**Denormalized Properties:** For query performance, broader/narrower terms are ALSO stored as properties:
- `broader_ids` / `broader_terms` - Arrays of parent subject IDs and labels
- `narrower_ids` / `narrower_terms` - Arrays of child subject IDs and labels

**When to Use Each:**
- Use `BROADER_THAN` relationships for:
  - Graph visualization (shows lines between nodes)
  - Multi-hop traversal (find all ancestors/descendants)
  - Cypher path queries (`-[:BROADER_THAN*]->`)
  
- Use `broader_ids`/`broader_terms` properties for:
  - Quick single-level lookups (no traversal needed)
  - Displaying breadcrumbs in UI
  - API responses with immediate parent/child info

### Common Edges (Incoming)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `SUBJECT_OF` | Event, Person, Org | IN | `(event:Event {label: "Punic Wars"})-[:SUBJECT_OF]->(subject:Subject {lcsh_id: "sh85109289"})` |
| `DEFINED_BY` | PropertyRegistry | IN | `(reg:PropertyRegistry)-[:DEFINED_BY]->(subject)` |

**Note:** Do NOT link structural entity types to their obvious subjects:
- ❌ `(period:Period)-[:SUBJECT_OF]->(:Subject {label: "Time"})` - redundant!
- ❌ `(place:Place)-[:SUBJECT_OF]->(:Subject {label: "Geography"})` - redundant!
- ✅ `(event:Event {label: "Battle of Zama"})-[:SUBJECT_OF]->(:Subject {lcsh_id: "sh85109289"})` - good!

### Template

```cypher
CREATE (subject:Subject {
  // REQUIRED
  qid: "Q17167",  // Wikidata QID
  lcsh_id: "sh85115055",
  lcsh_heading: "Rome--History--Republic, 510-30 B.C.",
  label: "Roman Republic",
  unique_id: "SUBJECT_LCSH_sh85115055",
  
  // OPTIONAL (rich metadata)
  description: "Period of Roman history from overthrow of monarchy (510 BCE) to establishment of empire (27 BCE)",
  aliases: ["Roman Republic", "Res Publica Romana", "Republican Rome"],
  domain: "history",
  scope_note: "Use for works on the Roman Republican period. For specific events, see narrower terms.",
  broader_terms: ["Rome--History"],
  narrower_terms: [
    "Rome--History--Servile Wars, 135-71 B.C.",
    "Rome--History--Republic, 265-30 B.C.",
    "Rome--History--Social War, 91-88 B.C."
  ],
  related_terms: ["Republican government", "Roman Senate"],
  lcc_code: "DG235-254",  // Library shelving metadata
  fast_id: "fst01210191",  // Supplementary cross-reference
  wikidata_url: "https://www.wikidata.org/wiki/Q17167",
  lcsh_url: "https://id.loc.gov/authorities/subjects/sh85115055"
})

// Example usage - entities link TO topical subjects
CREATE (event:Event {label: "Battle of Pharsalus", qid: "Q48314"})
CREATE (event)-[:SUBJECT_OF]->(subject)

// BROADER_THAN relationships for LCSH hierarchy (visualizes as graph edges)
CREATE (broader:Subject {lcsh_id: "sh85114934", lcsh_heading: "Rome--History"})
CREATE (narrower:Subject {lcsh_id: "sh85115055", lcsh_heading: "Rome--History--Republic, 510-30 B.C."})
CREATE (broader)-[:BROADER_THAN]->(narrower)

// Denormalized properties mirror the relationships for quick lookup
SET narrower.broader_ids = ["sh85114934"]
SET narrower.broader_terms = ["Rome--History"]
SET broader.narrower_ids = [..., "sh85115055", ...]
SET broader.narrower_terms = [..., "Rome--History--Republic, 510-30 B.C.", ...]
```

**Visualization:**
```
┌─────────────────────────────────┐
│ Rome--History                   │  
│ (sh85114934)                    │
│ broader_ids: []                 │
│ narrower_ids: [sh85115055, ...] │  ← Properties (quick lookup)
└─────────────────┬───────────────┘
                  │ BROADER_THAN       ← Relationship (graph edge/line)
                  ↓
┌─────────────────────────────────┐
│ Rome--History--Republic         │
│ (sh85115055)                    │
│ broader_ids: [sh85114934]       │  ← Properties (denormalized)
│ narrower_ids: [...]             │
└─────────────────────────────────┘
```

### Critical Notes

**LCSH IDs are PRIMARY BACKBONE:**
- ✅ Primary key: `lcsh_id` (not FAST)
- ✅ Unique identifier: `SUBJECT_LCSH_sh85115055`
- ✅ Best coverage for events (86%)

**Dewey Decimal for AGENT ROUTING:**
- ✅ Determines which agent handles a query
- ✅ Hierarchical agent spawning (937 → 937.05 → 937.052)
- ✅ Good coverage for historical periods

**FAST as SUPPLEMENTARY PROPERTY:**
- ✅ Store when available from Wikidata P2163
- ✅ Use for cross-referencing
- ❌ NOT required (poor event coverage)
- ❌ NOT primary key

**LCC as LIBRARY METADATA:**
- ✅ Library shelving code (optional)
- ✅ Stored for interoperability with library systems
- ❌ NOT used for agent routing (LCSH hierarchy handles this)

**Subject nodes enable:**
1. Topical discovery (find all entities about "Military history")
2. Cross-domain connections (link Politics to Military events)
3. Library of Congress alignment (LCSH/LCC interoperability)
4. Agent routing (Dewey code → agent assignment)
5. Thematic browsing (explore by topic, not just by time/place)

**Ontology Principle:**
- **Structure** = Entity types + Hierarchies (Period → Period, Place → Place)
- **Topics** = Subject classifications (Event → Military, Person → Politics)
- Don't confuse the two!

**Workflow for Subject Creation:**
1. **Get entity QID** from source or Wikidata search
2. **Query Wikidata** for subject properties:
   - P244 (LCSH ID) - PRIMARY (required)
   - P1149 (LCC) - optional library metadata
   - P2163 (FAST) - optional supplementary property
3. **Get broader/narrower terms** from LCSH vocabulary
4. **Create Subject node** with complete properties including qid, lcsh_id

---

## Facet Node Types ⭐ UNIVERSAL FACET CLASSIFICATION

### Overview
Facet nodes provide a universal, reusable classification system for all major node types (Period, Event, Place, etc.), supporting faceted search, filtering, and semantic enrichment. Each facet is a node with a specific type and properties, and is linked to entities via explicit relationships.

### Facet Class Table
| Facet Class         | Label         | Definition                                                        | Example Wikidata QIDs           |
|---------------------|--------------|-------------------------------------------------------------------|---------------------------------|
| PoliticalFacet      | Political    | Periods defined by states, regimes, dynasties, governance         | Q11514315, Q3624078, Q164950    |
| CulturalFacet       | Cultural     | Cultural eras, shared practices, identity, literature, arts       | Q185363, Q735, Q11042           |
| TechnologicalFacet  | Technological| Tool regimes, production technologies, industrial phases          | Q11016, Q255, Q33767            |
| ReligiousFacet      | Religious    | Religious movements, institutions, doctrinal eras                 | Q9174, Q432, Q5043              |
| EconomicFacet       | Economic     | Economic systems, trade regimes, financial structures             | Q8134, Q7406919, Q184754        |
| MilitaryFacet       | Military     | Warfare, conquests, military systems, strategic eras              | Q8473, Q198, Q40231             |
| EnvironmentalFacet  | Environmental| Climate regimes, ecological shifts, environmental phases          | Q756, Q2715388, Q629            |
| DemographicFacet    | Demographic  | Population structure, migration, urbanization waves               | Q37577, Q208188, Q7937          |
| IntellectualFacet   | Intellectual | Schools of thought, philosophical or scholarly movements          | Q5891, Q5893, Q333              |
| ScientificFacet     | Scientific   | Scientific paradigms, revolutions, epistemic frameworks           | Q336, Q309, Q170058             |
| ArtisticFacet       | Artistic     | Art movements, architectural styles, aesthetic regimes            | Q968159, Q32880, Q735           |
| SocialFacet         | Social       | Social norms, class structures, social movements                  | Q2695280, Q49773, Q8436         |
| LinguisticFacet     | Linguistic   | Language families, scripts, linguistic shifts                     | Q315, Q8192, Q8196              |
| ArchaeologicalFacet | Archaeological| Material-culture periods, stratigraphy, typologies               | Q1190554, Q23442, Q11767        |
| DiplomaticFacet     | Diplomatic   | International systems, alliances, treaty regimes                  | Q186509, Q1065, Q3624078        |

### Facet Node Labels
- :Facet (abstract, not instantiated)
- :PoliticalFacet, :CulturalFacet, :TechnologicalFacet, :ReligiousFacet, :EconomicFacet, :MilitaryFacet, :EnvironmentalFacet, :DemographicFacet, :IntellectualFacet, :ScientificFacet, :ArtisticFacet, :SocialFacet, :LinguisticFacet, :ArchaeologicalFacet, :DiplomaticFacet

### Example Properties (per facet type)
- `unique_id`: e.g., "POLITICALFACET_{qid}", "TEMPORALFACET_{start}_{end}_{label}"
- `label`: Human-readable label
- `definition`: Facet definition (optional)
- `source_qid`: Wikidata QID (if available)
- Additional properties as needed (e.g., `start_year`, `end_year`, `region_qid`, `lat`, `lon`)

### Example Cypher Templates
```cypher
CREATE (pf:PoliticalFacet:Facet {
  unique_id: "POLITICALFACET_Q3624078",
  label: "Sovereign State",
  definition: "Periods defined by states, regimes, dynasties, governance structures",
  source_qid: "Q3624078"
})

MATCH (p:Period {qid: "Q11761"}), (pf:PoliticalFacet {unique_id: "POLITICALFACET_Q3624078"})
MERGE (p)-[:HAS_POLITICAL_FACET]->(pf)
```

### Relationships
- `HAS_[FACET_TYPE]_FACET` (any node) → [Facet Subclass] (e.g., HAS_POLITICAL_FACET, HAS_TECHNOLOGICAL_FACET)
- Each entity can point to multiple facets of different types, supporting multi-dimensional classification.

### Integration Notes
- All major node types should link to at least one facet node of each relevant type.
- Facet nodes are reusable: multiple entities can point to the same facet.
- Facet nodes can be extended (e.g., :ChronologicalFacet, :CulturalFacet) as needed.
- This system supports universal filtering, faceted search, and semantic navigation across the graph.

---

## Schema Format

Each node type has:
1. **Required Properties** - Must be present
2. **Optional Properties** - Should be included if known
3. **Required Edges** - Must connect to other nodes
4. **Optional Edges** - Should connect if relevant
5. **Examples** - Reference implementations

---

## Subject Node Schema ⭐ TOPICAL CLASSIFICATION (LCSH Authority System)

### Node Labels
```cypher
:Subject
```

**Purpose:** Topical/thematic classification using **Library of Congress Subject Headings (LCSH)** as the backbone authority system

**Backbone Authority:** LCSH (Library of Congress Subject Headings) - the authoritative controlled vocabulary managed by the Library of Congress

**What Subjects Are:** Subjects represent **what entities are ABOUT** (themes, topics), not what they ARE (structure)

**Critical Distinction:**
- ✅ **Topical subjects** - Politics, Military, Religion, Culture, Economics (use these!)
- ❌ **Structural categories** - Time, Geography (these are redundant - use entity types instead!)

**Navigation vs. Classification:**
- **Navigate** through hierarchies: Period → Parent Period, Place → Parent Place, Year → Next Year
- **Classify** by topic: Event → Military Subject, Person → Political Subject

### NEW ARCHITECTURE (Dec 2025): LCSH as Backbone Authority System

**LCSH = The Backbone:**
- ✅ **Authoritative controlled vocabulary** maintained by Library of Congress
- ✅ **86% event coverage** in Wikidata (vs. 14% for FAST)
- ✅ **Primary source** (FAST is derived from LCSH)
- ✅ **Better granularity** for historical events (e.g., "Pharsalus, Battle of, 48 B.C.")
- ✅ **Agent routing** via broader/narrower term hierarchies

**LCSH Hierarchy for Agent Routing:**
- ✅ **LCSH broader/narrower terms used for agent hierarchy**
- Example: "Rome--History" (broader) → "Rome--History--Republic, 510-30 B.C." (narrower)
- Agent spawning follows LCSH subject tree: sh85114934 → sh85115055 → specialists

**FAST as Supplementary Property:**
- Store FAST ID when available from Wikidata (P2163) (~54% coverage)
- Not required; used for cross-referencing only

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q17167" | Wikidata QID (for federation) |
| `lcsh_id` | string | sh[0-9]{8} | "sh85115055" | LCSH ID (PRIMARY BACKBONE) ⭐ |
| `lcsh_heading` | string | text | "Rome--History--Republic, 510-30 B.C." | Library of Congress Subject Heading (authoritative form) |
| `label` | string | text | "Roman Republic" | Human-readable label |
| `unique_id` | string | pattern | "SUBJECT_LCSH_sh85115055" | System ID (based on LCSH) |

### Optional Properties (Classification Metadata)

| Property         | Type     | Format              | Example                           | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ---------------------------------------------------- |
| `description`    | string   | text                | "Ancient Roman republican period" | Short description                                    |
| `aliases`        | string[] | text                | ["Roman Republic", "Res Publica"] | Alternative names/labels                             |
| `domain`         | string   | text                | "history"                         | Subject domain                                       |
| `scope_note`     | string   | text                | "Use for works on the Roman Republican period..." | LCSH scope note (usage guidance) |
| `broader_terms`  | string[] | text                | ["Rome--History"]                 | Broader LCSH terms (for hierarchy)                   |
| `narrower_terms` | string[] | text                | ["Rome--History--Servile Wars"]   | Narrower LCSH terms (for hierarchy)                  |
| `related_terms`  | string[] | text                | ["Republican Rome"]               | Related LCSH terms                                   |
| `wikidata_url`   | string   | URL                 | "https://www.wikidata.org/wiki/Q17167" | Full Wikidata URL                          |
| `lcsh_url`       | string   | URL                 | "https://id.loc.gov/authorities/subjects/sh85115055" | LCSH authority record URL            |

### Optional Properties (Authority Crosswalk via Wikidata) ⭐ NEW

**Wikidata as Universal Crosswalk Hub:** Use QID to fetch IDs from multiple authority systems via Wikidata properties. Enables interoperability with different agent preferences and external systems.

| Property         | Type     | Format              | Example                           | Wikidata Property | Coverage | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ----------------- | -------- | ---------------------------------------------------- |
| `fast_id`        | string   | fst[0-9]{8}         | "fst01210191"                     | P2163             | ~54%     | FAST ID (OCLC Faceted Application of Subject Terminology) - derived from LCSH, post-coordinated |
| `dewey`          | string   | [0-9]{3}\.[0-9]+    | "937.05"                          | P1036             | ~12%     | Dewey Decimal Classification - numerical classification for agent routing |
| `lcc_code`       | string   | [A-Z]{1,3}[0-9]+    | "DG235-254"                       | P1149             | varies   | Library of Congress Classification - alphanumeric shelf classification |
| `viaf_id`        | string   | [0-9]+              | "123456789"                       | P214              | varies   | Virtual International Authority File - international aggregator linking multiple national libraries |
| `gnd_id`         | string   | [0-9]{4,}(-[0-9xX])? | "4043912-4"                      | P227              | varies   | Gemeinsame Normdatei (GND) - German National Library authority ID |

**Fetching Crosswalk IDs:**
```python
# Query Wikidata to get all authority IDs for a Subject
import requests

qid = "Q17167"  # Roman Republic
url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
response = requests.get(url, headers={'User-Agent': 'YourBot/1.0'})
data = response.json()
claims = data['entities'][qid]['claims']

# Extract authority IDs
lcsh_id = claims['P244'][0]['mainsnak']['datavalue']['value']  # sh85115055
fast_id = claims['P2163'][0]['mainsnak']['datavalue']['value'] # fst01210191
dewey = claims['P1036'][0]['mainsnak']['datavalue']['value']   # 937.05
lcc = claims['P1149'][0]['mainsnak']['datavalue']['value']     # DG235-254
viaf_id = claims['P214'][0]['mainsnak']['datavalue']['value']  # 123456789
```

**Use Cases:**
- **Agent routing**: Different agents prefer different authorities (FAST facets vs LCSH pre-coordinated)
- **External system integration**: Link to library catalogs, databases using their preferred authority
- **Multilingual support**: VIAF connects to French (BnF), German (DNB), Japanese (NDL) national libraries
- **Cross-referencing**: Validate subject mappings across multiple authority systems

### Required Edges

**None** - Subject nodes are leaf nodes in the taxonomy (entities link TO them)

### LCSH Hierarchy Edges (Between Subjects)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `BROADER_THAN` | Subject | OUT | `(:Subject {lcsh_id: "sh85061097", lcsh_heading: "Historic buildings"})-[:BROADER_THAN]->(:Subject {lcsh_id: "sh85077493", lcsh_heading: "Literary landmarks"})` |

**Purpose:** BROADER_THAN relationships create the LCSH subject hierarchy used for agent routing and topical navigation.

**Database Status:** ✅ 10,992 BROADER_THAN relationships exist in the graph

**Direction Design:** Single-direction relationships (no NARROWER_THAN inverse)
```cypher
// Query narrower terms (traverse forward →)
MATCH (broader:Subject)-[:BROADER_THAN]->(narrower:Subject)
WHERE broader.lcsh_id = "sh85114934"
RETURN narrower

// Query broader terms (traverse backward ←)
MATCH (narrower:Subject)<-[:BROADER_THAN]-(broader:Subject)
WHERE narrower.lcsh_id = "sh85115055"
RETURN broader

// Multi-hop traversal (all ancestors)
MATCH path = (s:Subject {lcsh_id: "sh85115055"})<-[:BROADER_THAN*]-(ancestor)
RETURN ancestor

// Multi-hop traversal (all descendants)
MATCH path = (s:Subject {lcsh_id: "sh85114934"})-[:BROADER_THAN*]->(descendant)
RETURN descendant
```

**Why No NARROWER_THAN?** Neo4j relationships are bidirectional - you can traverse `BROADER_THAN` in both directions using `->` and `<-` in Cypher. Creating inverse relationships would duplicate all 10,992 edges and waste storage.

**Denormalized Properties:** For query performance, broader/narrower terms are ALSO stored as properties:
- `broader_ids` / `broader_terms` - Arrays of parent subject IDs and labels
- `narrower_ids` / `narrower_terms` - Arrays of child subject IDs and labels

**When to Use Each:**
- Use `BROADER_THAN` relationships for:
  - Graph visualization (shows lines between nodes)
  - Multi-hop traversal (find all ancestors/descendants)
  - Cypher path queries (`-[:BROADER_THAN*]->`)
  
- Use `broader_ids`/`broader_terms` properties for:
  - Quick single-level lookups (no traversal needed)
  - Displaying breadcrumbs in UI
  - API responses with immediate parent/child info

### Common Edges (Incoming)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `SUBJECT_OF` | Event, Person, Org | IN | `(event:Event {label: "Punic Wars"})-[:SUBJECT_OF]->(subject:Subject {lcsh_id: "sh85109289"})` |
| `DEFINED_BY` | PropertyRegistry | IN | `(reg:PropertyRegistry)-[:DEFINED_BY]->(subject)` |

**Note:** Do NOT link structural entity types to their obvious subjects:
- ❌ `(period:Period)-[:SUBJECT_OF]->(:Subject {label: "Time"})` - redundant!
- ❌ `(place:Place)-[:SUBJECT_OF]->(:Subject {label: "Geography"})` - redundant!
- ✅ `(event:Event {label: "Battle of Zama"})-[:SUBJECT_OF]->(:Subject {lcsh_id: "sh85109289"})` - good!

### Template

```cypher
CREATE (subject:Subject {
  // REQUIRED
  qid: "Q17167",  // Wikidata QID
  lcsh_id: "sh85115055",
  lcsh_heading: "Rome--History--Republic, 510-30 B.C.",
  label: "Roman Republic",
  unique_id: "SUBJECT_LCSH_sh85115055",
  
  // OPTIONAL (rich metadata)
  description: "Period of Roman history from overthrow of monarchy (510 BCE) to establishment of empire (27 BCE)",
  aliases: ["Roman Republic", "Res Publica Romana", "Republican Rome"],
  domain: "history",
  scope_note: "Use for works on the Roman Republican period. For specific events, see narrower terms.",
  broader_terms: ["Rome--History"],
  narrower_terms: [
    "Rome--History--Servile Wars, 135-71 B.C.",
    "Rome--History--Republic, 265-30 B.C.",
    "Rome--History--Social War, 91-88 B.C."
  ],
  related_terms: ["Republican government", "Roman Senate"],
  lcc_code: "DG235-254",  // Library shelving metadata
  fast_id: "fst01210191",  // Supplementary cross-reference
  wikidata_url: "https://www.wikidata.org/wiki/Q17167",
  lcsh_url: "https://id.loc.gov/authorities/subjects/sh85115055"
})

// Example usage - entities link TO topical subjects
CREATE (event:Event {label: "Battle of Pharsalus", qid: "Q48314"})
CREATE (event)-[:SUBJECT_OF]->(subject)

// BROADER_THAN relationships for LCSH hierarchy (visualizes as graph edges)
CREATE (broader:Subject {lcsh_id: "sh85114934", lcsh_heading: "Rome--History"})
CREATE (narrower:Subject {lcsh_id: "sh85115055", lcsh_heading: "Rome--History--Republic, 510-30 B.C."})
CREATE (broader)-[:BROADER_THAN]->(narrower)

// Denormalized properties mirror the relationships for quick lookup
SET narrower.broader_ids = ["sh85114934"]
SET narrower.broader_terms = ["Rome--History"]
SET broader.narrower_ids = [..., "sh85115055", ...]
SET broader.narrower_terms = [..., "Rome--History--Republic, 510-30 B.C.", ...]
```

**Visualization:**
```
┌─────────────────────────────────┐
│ Rome--History                   │  
│ (sh85114934)                    │
│ broader_ids: []                 │
│ narrower_ids: [sh85115055, ...] │  ← Properties (quick lookup)
└─────────────────┬───────────────┘
                  │ BROADER_THAN       ← Relationship (graph edge/line)
                  ↓
┌─────────────────────────────────┐
│ Rome--History--Republic         │
│ (sh85115055)                    │
│ broader_ids: [sh85114934]       │  ← Properties (denormalized)
│ narrower_ids: [...]             │
└─────────────────────────────────┘
```

### Critical Notes

**LCSH IDs are PRIMARY BACKBONE:**
- ✅ Primary key: `lcsh_id` (not FAST)
- ✅ Unique identifier: `SUBJECT_LCSH_sh85115055`
- ✅ Best coverage for events (86%)

**Dewey Decimal for AGENT ROUTING:**
- ✅ Determines which agent handles a query
- ✅ Hierarchical agent spawning (937 → 937.05 → 937.052)
- ✅ Good coverage for historical periods

**FAST as SUPPLEMENTARY PROPERTY:**
- ✅ Store when available from Wikidata P2163
- ✅ Use for cross-referencing
- ❌ NOT required (poor event coverage)
- ❌ NOT primary key

**LCC as LIBRARY METADATA:**
- ✅ Library shelving code (optional)
- ✅ Stored for interoperability with library systems
- ❌ NOT used for agent routing (LCSH hierarchy handles this)

**Subject nodes enable:**
1. Topical discovery (find all entities about "Military history")
2. Cross-domain connections (link Politics to Military events)
3. Library of Congress alignment (LCSH/LCC interoperability)
4. Agent routing (Dewey code → agent assignment)
5. Thematic browsing (explore by topic, not just by time/place)

**Ontology Principle:**
- **Structure** = Entity types + Hierarchies (Period → Period, Place → Place)
- **Topics** = Subject classifications (Event → Military, Person → Politics)
- Don't confuse the two!

**Workflow for Subject Creation:**
1. **Get entity QID** from source or Wikidata search
2. **Query Wikidata** for subject properties:
   - P244 (LCSH ID) - PRIMARY (required)
   - P1149 (LCC) - optional library metadata
   - P2163 (FAST) - optional supplementary property
3. **Get broader/narrower terms** from LCSH vocabulary
4. **Create Subject node** with complete properties including qid, lcsh_id

---

## Facet Node Types ⭐ UNIVERSAL FACET CLASSIFICATION

### Overview
Facet nodes provide a universal, reusable classification system for all major node types (Period, Event, Place, etc.), supporting faceted search, filtering, and semantic enrichment. Each facet is a node with a specific type and properties, and is linked to entities via explicit relationships.

### Facet Class Table
| Facet Class         | Label         | Definition                                                        | Example Wikidata QIDs           |
|---------------------|--------------|-------------------------------------------------------------------|---------------------------------|
| PoliticalFacet      | Political    | Periods defined by states, regimes, dynasties, governance         | Q11514315, Q3624078, Q164950    |
| CulturalFacet       | Cultural     | Cultural eras, shared practices, identity, literature, arts       | Q185363, Q735, Q11042           |
| TechnologicalFacet  | Technological| Tool regimes, production technologies, industrial phases          | Q11016, Q255, Q33767            |
| ReligiousFacet      | Religious    | Religious movements, institutions, doctrinal eras                 | Q9174, Q432, Q5043              |
| EconomicFacet       | Economic     | Economic systems, trade regimes, financial structures             | Q8134, Q7406919, Q184754        |
| MilitaryFacet       | Military     | Warfare, conquests, military systems, strategic eras              | Q8473, Q198, Q40231             |
| EnvironmentalFacet  | Environmental| Climate regimes, ecological shifts, environmental phases          | Q756, Q2715388, Q629            |
| DemographicFacet    | Demographic  | Population structure, migration, urbanization waves               | Q37577, Q208188, Q7937          |
| IntellectualFacet   | Intellectual | Schools of thought, philosophical or scholarly movements          | Q5891, Q5893, Q333              |
| ScientificFacet     | Scientific   | Scientific paradigms, revolutions, epistemic frameworks           | Q336, Q309, Q170058             |
| ArtisticFacet       | Artistic     | Art movements, architectural styles, aesthetic regimes            | Q968159, Q32880, Q735           |
| SocialFacet         | Social       | Social norms, class structures, social movements                  | Q2695280, Q49773, Q8436         |
| LinguisticFacet     | Linguistic   | Language families, scripts, linguistic shifts                     | Q315, Q8192, Q8196              |
| ArchaeologicalFacet | Archaeological| Material-culture periods, stratigraphy, typologies               | Q1190554, Q23442, Q11767        |
| DiplomaticFacet     | Diplomatic   | International systems, alliances, treaty regimes                  | Q186509, Q1065, Q3624078        |

### Facet Node Labels
- :Facet (abstract, not instantiated)
- :PoliticalFacet, :CulturalFacet, :TechnologicalFacet, :ReligiousFacet, :EconomicFacet, :MilitaryFacet, :EnvironmentalFacet, :DemographicFacet, :IntellectualFacet, :ScientificFacet, :ArtisticFacet, :SocialFacet, :LinguisticFacet, :ArchaeologicalFacet, :DiplomaticFacet

### Example Properties (per facet type)
- `unique_id`: e.g., "POLITICALFACET_{qid}", "TEMPORALFACET_{start}_{end}_{label}"
- `label`: Human-readable label
- `definition`: Facet definition (optional)
- `source_qid`: Wikidata QID (if available)
- Additional properties as needed (e.g., `start_year`, `end_year`, `region_qid`, `lat`, `lon`)

### Example Cypher Templates
```cypher
CREATE (pf:PoliticalFacet:Facet {
  unique_id: "POLITICALFACET_Q3624078",
  label: "Sovereign State",
  definition: "Periods defined by states, regimes, dynasties, governance structures",
  source_qid: "Q3624078"
})

MATCH (p:Period {qid: "Q11761"}), (pf:PoliticalFacet {unique_id: "POLITICALFACET_Q3624078"})
MERGE (p)-[:HAS_POLITICAL_FACET]->(pf)
```

### Relationships
- `HAS_[FACET_TYPE]_FACET` (any node) → [Facet Subclass] (e.g., HAS_POLITICAL_FACET, HAS_TECHNOLOGICAL_FACET)
- Each entity can point to multiple facets of different types, supporting multi-dimensional classification.

### Integration Notes
- All major node types should link to at least one facet node of each relevant type.
- Facet nodes are reusable: multiple entities can point to the same facet.
- Facet nodes can be extended (e.g., :ChronologicalFacet, :CulturalFacet) as needed.
- This system supports universal filtering, faceted search, and semantic navigation across the graph.

---

## Schema Format

Each node type has:
1. **Required Properties** - Must be present
2. **Optional Properties** - Should be included if known
3. **Required Edges** - Must connect to other nodes
4. **Optional Edges** - Should connect if relevant
5. **Examples** - Reference implementations

---

## Subject Node Schema ⭐ TOPICAL CLASSIFICATION (LCSH Authority System)

### Node Labels
```cypher
:Subject
```

**Purpose:** Topical/thematic classification using **Library of Congress Subject Headings (LCSH)** as the backbone authority system

**Backbone Authority:** LCSH (Library of Congress Subject Headings) - the authoritative controlled vocabulary managed by the Library of Congress

**What Subjects Are:** Subjects represent **what entities are ABOUT** (themes, topics), not what they ARE (structure)

**Critical Distinction:**
- ✅ **Topical subjects** - Politics, Military, Religion, Culture, Economics (use these!)
- ❌ **Structural categories** - Time, Geography (these are redundant - use entity types instead!)

**Navigation vs. Classification:**
- **Navigate** through hierarchies: Period → Parent Period, Place → Parent Place, Year → Next Year
- **Classify** by topic: Event → Military Subject, Person → Political Subject

### NEW ARCHITECTURE (Dec 2025): LCSH as Backbone Authority System

**LCSH = The Backbone:**
- ✅ **Authoritative controlled vocabulary** maintained by Library of Congress
- ✅ **86% event coverage** in Wikidata (vs. 14% for FAST)
- ✅ **Primary source** (FAST is derived from LCSH)
- ✅ **Better granularity** for historical events (e.g., "Pharsalus, Battle of, 48 B.C.")
- ✅ **Agent routing** via broader/narrower term hierarchies

**LCSH Hierarchy for Agent Routing:**
- ✅ **LCSH broader/narrower terms used for agent hierarchy**
- Example: "Rome--History" (broader) → "Rome--History--Republic, 510-30 B.C." (narrower)
- Agent spawning follows LCSH subject tree: sh85114934 → sh85115055 → specialists

**FAST as Supplementary Property:**
- Store FAST ID when available from Wikidata (P2163) (~54% coverage)
- Not required; used for cross-referencing only

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q17167" | Wikidata QID (for federation) |
| `lcsh_id` | string | sh[0-9]{8} | "sh85115055" | LCSH ID (PRIMARY BACKBONE) ⭐ |
| `lcsh_heading` | string | text | "Rome--History--Republic, 510-30 B.C." | Library of Congress Subject Heading (authoritative form) |
| `label` | string | text | "Roman Republic" | Human-readable label |
| `unique_id` | string | pattern | "SUBJECT_LCSH_sh85115055" | System ID (based on LCSH) |

### Optional Properties (Classification Metadata)

| Property         | Type     | Format              | Example                           | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ---------------------------------------------------- |
| `description`    | string   | text                | "Ancient Roman republican period" | Short description                                    |
| `aliases`        | string[] | text                | ["Roman Republic", "Res Publica"] | Alternative names/labels                             |
| `domain`         | string   | text                | "history"                         | Subject domain                                       |
| `scope_note`     | string   | text                | "Use for works on the Roman Republican period..." | LCSH scope note (usage guidance) |
| `broader_terms`  | string[] | text                | ["Rome--History"]                 | Broader LCSH terms (for hierarchy)                   |
| `narrower_terms` | string[] | text                | ["Rome--History--Servile Wars"]   | Narrower LCSH terms (for hierarchy)                  |
| `related_terms`  | string[] | text                | ["Republican Rome"]               | Related LCSH terms                                   |
| `wikidata_url`   | string   | URL                 | "https://www.wikidata.org/wiki/Q17167" | Full Wikidata URL                          |
| `lcsh_url`       | string   | URL                 | "https://id.loc.gov/authorities/subjects/sh85115055" | LCSH authority record URL            |

### Optional Properties (Authority Crosswalk via Wikidata) ⭐ NEW

**Wikidata as Universal Crosswalk Hub:** Use QID to fetch IDs from multiple authority systems via Wikidata properties. Enables interoperability with different agent preferences and external systems.

| Property         | Type     | Format              | Example                           | Wikidata Property | Coverage | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ----------------- | -------- | ---------------------------------------------------- |
| `fast_id`        | string   | fst[0-9]{8}         | "fst01210191"                     | P2163             | ~54%     | FAST ID (OCLC Faceted Application of Subject Terminology) - derived from LCSH, post-coordinated |
| `dewey`          | string   | [0-9]{3}\.[0-9]+    | "937.05"                          | P1036             | ~12%     | Dewey Decimal Classification - numerical classification for agent routing |
| `lcc_code`       | string   | [A-Z]{1,3}[0-9]+    | "DG235-254"                       | P1149             | varies   | Library of Congress Classification - alphanumeric shelf classification |
| `viaf_id`        | string   | [0-9]+              | "123456789"                       | P214              | varies   | Virtual International Authority File - international aggregator linking multiple national libraries |
| `gnd_id`         | string   | [0-9]{4,}(-[0-9xX])? | "4043912-4"                      | P227              | varies   | Gemeinsame Normdatei (GND) - German National Library authority ID |

**Fetching Crosswalk IDs:**
```python
# Query Wikidata to get all authority IDs for a Subject
import requests

qid = "Q17167"  # Roman Republic
url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
response = requests.get(url, headers={'User-Agent': 'YourBot/1.0'})
data = response.json()
claims = data['entities'][qid]['claims']

# Extract authority IDs
lcsh_id = claims['P244'][0]['mainsnak']['datavalue']['value']  # sh85115055
fast_id = claims['P2163'][0]['mainsnak']['datavalue']['value'] # fst01210191
dewey = claims['P1036'][0]['mainsnak']['datavalue']['value']   # 937.05
lcc = claims['P1149'][0]['mainsnak']['datavalue']['value']     # DG235-254
viaf_id = claims['P214'][0]['mainsnak']['datavalue']['value']  # 123456789
```

**Use Cases:**
- **Agent routing**: Different agents prefer different authorities (FAST facets vs LCSH pre-coordinated)
- **External system integration**: Link to library catalogs, databases using their preferred authority
- **Multilingual support**: VIAF connects to French (BnF), German (DNB), Japanese (NDL) national libraries
- **Cross-referencing**: Validate subject mappings across multiple authority systems

### Required Edges

**None** - Subject nodes are leaf nodes in the taxonomy (entities link TO them)

### LCSH Hierarchy Edges (Between Subjects)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `BROADER_THAN` | Subject | OUT | `(:Subject {lcsh_id: "sh85061097", lcsh_heading: "Historic buildings"})-[:BROADER_THAN]->(:Subject {lcsh_id: "sh85077493", lcsh_heading: "Literary landmarks"})` |

**Purpose:** BROADER_THAN relationships create the LCSH subject hierarchy used for agent routing and topical navigation.

**Database Status:** ✅ 10,992 BROADER_THAN relationships exist in the graph

**Direction Design:** Single-direction relationships (no NARROWER_THAN inverse)
```cypher
// Query narrower terms (traverse forward →)
MATCH (broader:Subject)-[:BROADER_THAN]->(narrower:Subject)
WHERE broader.lcsh_id = "sh85114934"
RETURN narrower

// Query broader terms (traverse backward ←)
MATCH (narrower:Subject)<-[:BROADER_THAN]-(broader:Subject)
WHERE narrower.lcsh_id = "sh85115055"
RETURN broader

// Multi-hop traversal (all ancestors)
MATCH path = (s:Subject {lcsh_id: "sh85115055"})<-[:BROADER_THAN*]-(ancestor)
RETURN ancestor

// Multi-hop traversal (all descendants)
MATCH path = (s:Subject {lcsh_id: "sh85114934"})-[:BROADER_THAN*]->(descendant)
RETURN descendant
```

**Why No NARROWER_THAN?** Neo4j relationships are bidirectional - you can traverse `BROADER_THAN` in both directions using `->` and `<-` in Cypher. Creating inverse relationships would duplicate all 10,992 edges and waste storage.

**Denormalized Properties:** For query performance, broader/narrower terms are ALSO stored as properties:
- `broader_ids` / `broader_terms` - Arrays of parent subject IDs and labels
- `narrower_ids` / `narrower_terms` - Arrays of child subject IDs and labels

**When to Use Each:**
- Use `BROADER_THAN` relationships for:
  - Graph visualization (shows lines between nodes)
  - Multi-hop traversal (find all ancestors/descendants)
  - Cypher path queries (`-[:BROADER_THAN*]->`)
  
- Use `broader_ids`/`broader_terms` properties for:
  - Quick single-level lookups (no traversal needed)
  - Displaying breadcrumbs in UI
  - API responses with immediate parent/child info

### Common Edges (Incoming)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `SUBJECT_OF` | Event, Person, Org | IN | `(event:Event {label: "Punic Wars"})-[:SUBJECT_OF]->(subject:Subject {lcsh_id: "sh85109289"})` |
| `DEFINED_BY` | PropertyRegistry | IN | `(reg:PropertyRegistry)-[:DEFINED_BY]->(subject)` |

**Note:** Do NOT link structural entity types to their obvious subjects:
- ❌ `(period:Period)-[:SUBJECT_OF]->(:Subject {label: "Time"})` - redundant!
- ❌ `(place:Place)-[:SUBJECT_OF]->(:Subject {label: "Geography"})` - redundant!
- ✅ `(event:Event {label: "Battle of Zama"})-[:SUBJECT_OF]->(:Subject {lcsh_id: "sh85109289"})` - good!

### Template

```cypher
CREATE (subject:Subject {
  // REQUIRED
  qid: "Q17167",  // Wikidata QID
  lcsh_id: "sh85115055",
  lcsh_heading: "Rome--History--Republic, 510-30 B.C.",
  label: "Roman Republic",
  unique_id: "SUBJECT_LCSH_sh85115055",
  
  // OPTIONAL (rich metadata)
  description: "Period of Roman history from overthrow of monarchy (510 BCE) to establishment of empire (27 BCE)",
  aliases: ["Roman Republic", "Res Publica Romana", "Republican Rome"],
  domain: "history",
  scope_note: "Use for works on the Roman Republican period. For specific events, see narrower terms.",
  broader_terms: ["Rome--History"],
  narrower_terms: [
    "Rome--History--Servile Wars, 135-71 B.C.",
    "Rome--History--Republic, 265-30 B.C.",
    "Rome--History--Social War, 91-88 B.C."
  ],
  related_terms: ["Republican government", "Roman Senate"],
  lcc_code: "DG235-254",  // Library shelving metadata
  fast_id: "fst01210191",  // Supplementary cross-reference
  wikidata_url: "https://www.wikidata.org/wiki/Q17167",
  lcsh_url: "https://id.loc.gov/authorities/subjects/sh85115055"
})

// Example usage - entities link TO topical subjects
CREATE (event:Event {label: "Battle of Pharsalus", qid: "Q48314"})
CREATE (event)-[:SUBJECT_OF]->(subject)

// BROADER_THAN relationships for LCSH hierarchy (visualizes as graph edges)
CREATE (broader:Subject {lcsh_id: "sh85114934", lcsh_heading: "Rome--History"})
CREATE (narrower:Subject {lcsh_id: "sh85115055", lcsh_heading: "Rome--History--Republic, 510-30 B.C."})
CREATE (broader)-[:BROADER_THAN]->(narrower)

// Denormalized properties mirror the relationships for quick lookup
SET narrower.broader_ids = ["sh85114934"]
SET narrower.broader_terms = ["Rome--History"]
SET broader.narrower_ids = [..., "sh85115055", ...]
SET broader.narrower_terms = [..., "Rome--History--Republic, 510-30 B.C.", ...]
```

**Visualization:**
```
┌─────────────────────────────────┐
│ Rome--History                   │  
│ (sh85114934)                    │
│ broader_ids: []                 │
│ narrower_ids: [sh85115055, ...] │  ← Properties (quick lookup)
└─────────────────┬───────────────┘
                  │ BROADER_THAN       ← Relationship (graph edge/line)
                  ↓
┌─────────────────────────────────┐
│ Rome--History--Republic         │
│ (sh85115055)                    │
│ broader_ids: [sh85114934]       │  ← Properties (denormalized)
│ narrower_ids: [...]             │
└─────────────────────────────────┘
```

### Critical Notes

**LCSH IDs are PRIMARY BACKBONE:**
- ✅ Primary key: `lcsh_id` (not FAST)
- ✅ Unique identifier: `SUBJECT_LCSH_sh85115055`
- ✅ Best coverage for events (86%)

**Dewey Decimal for AGENT ROUTING:**
- ✅ Determines which agent handles a query
- ✅ Hierarchical agent spawning (937 → 937.05 → 937.052)
- ✅ Good coverage for historical periods

**FAST as SUPPLEMENTARY PROPERTY:**
- ✅ Store when available from Wikidata P2163
- ✅ Use for cross-referencing
- ❌ NOT required (poor event coverage)
- ❌ NOT primary key

**LCC as LIBRARY METADATA:**
- ✅ Library shelving code (optional)
- ✅ Stored for interoperability with library systems
- ❌ NOT used for agent routing (LCSH hierarchy handles this)

**Subject nodes enable:**
1. Topical discovery (find all entities about "Military history")
2. Cross-domain connections (link Politics to Military events)
3. Library of Congress alignment (LCSH/LCC interoperability)
4. Agent routing (Dewey code → agent assignment)
5. Thematic browsing (explore by topic, not just by time/place)

**Ontology Principle:**
- **Structure** = Entity types + Hierarchies (Period → Period, Place → Place)
- **Topics** = Subject classifications (Event → Military, Person → Politics)
- Don't confuse the two!

**Workflow for Subject Creation:**
1. **Get entity QID** from source or Wikidata search
2. **Query Wikidata** for subject properties:
   - P244 (LCSH ID) - PRIMARY (required)
   - P1149 (LCC) - optional library metadata
   - P2163 (FAST) - optional supplementary property
3. **Get broader/narrower terms** from LCSH vocabulary
4. **Create Subject node** with complete properties including qid, lcsh_id

---

## Facet Node Types ⭐ UNIVERSAL FACET CLASSIFICATION

### Overview
Facet nodes provide a universal, reusable classification system for all major node types (Period, Event, Place, etc.), supporting faceted search, filtering, and semantic enrichment. Each facet is a node with a specific type and properties, and is linked to entities via explicit relationships.

### Facet Class Table
| Facet Class         | Label         | Definition                                                        | Example Wikidata QIDs           |
|---------------------|--------------|-------------------------------------------------------------------|---------------------------------|
| PoliticalFacet      | Political    | Periods defined by states, regimes, dynasties, governance         | Q11514315, Q3624078, Q164950    |
| CulturalFacet       | Cultural     | Cultural eras, shared practices, identity, literature, arts       | Q185363, Q735, Q11042           |
| TechnologicalFacet  | Technological| Tool regimes, production technologies, industrial phases          | Q11016, Q255, Q33767            |
| ReligiousFacet      | Religious    | Religious movements, institutions, doctrinal eras                 | Q9174, Q432, Q5043              |
| EconomicFacet       | Economic     | Economic systems, trade regimes, financial structures             | Q8134, Q7406919, Q184754        |
| MilitaryFacet       | Military     | Warfare, conquests, military systems, strategic eras              | Q8473, Q198, Q40231             |
| EnvironmentalFacet  | Environmental| Climate regimes, ecological shifts, environmental phases          | Q756, Q2715388, Q629            |
| DemographicFacet    | Demographic  | Population structure, migration, urbanization waves               | Q37577, Q208188, Q7937          |
| IntellectualFacet   | Intellectual | Schools of thought, philosophical or scholarly movements          | Q5891, Q5893, Q333              |
| ScientificFacet     | Scientific   | Scientific paradigms, revolutions, epistemic frameworks           | Q336, Q309, Q170058             |
| ArtisticFacet       | Artistic     | Art movements, architectural styles, aesthetic regimes            | Q968159, Q32880, Q735           |
| SocialFacet         | Social       | Social norms, class structures, social movements                  | Q2695280, Q49773, Q8436         |
| LinguisticFacet     | Linguistic   | Language families, scripts, linguistic shifts                     | Q315, Q8192, Q8196              |
| ArchaeologicalFacet | Archaeological| Material-culture periods, stratigraphy, typologies               | Q1190554, Q23442, Q11767        |
| DiplomaticFacet     | Diplomatic   | International systems, alliances, treaty regimes                  | Q186509, Q1065, Q3624078        |

### Facet Node Labels
- :Facet (abstract, not instantiated)
- :PoliticalFacet, :CulturalFacet, :TechnologicalFacet, :ReligiousFacet, :EconomicFacet, :MilitaryFacet, :EnvironmentalFacet, :DemographicFacet, :IntellectualFacet, :ScientificFacet, :ArtisticFacet, :SocialFacet, :LinguisticFacet, :ArchaeologicalFacet, :DiplomaticFacet

### Example Properties (per facet type)
- `unique_id`: e.g., "POLITICALFACET_{qid}", "TEMPORALFACET_{start}_{end}_{label}"
- `label`: Human-readable label
- `definition`: Facet definition (optional)
- `source_qid`: Wikidata QID (if available)
- Additional properties as needed (e.g., `start_year`, `end_year`, `region_qid`, `lat`, `lon`)

### Example Cypher Templates
```cypher
CREATE (pf:PoliticalFacet:Facet {
  unique_id: "POLITICALFACET_Q3624078",
  label: "Sovereign State",
  definition: "Periods defined by states, regimes, dynasties, governance structures",
  source_qid: "Q3624078"
})

MATCH (p:Period {qid: "Q11761"}), (pf:PoliticalFacet {unique_id: "POLITICALFACET_Q3624078"})
MERGE (p)-[:HAS_POLITICAL_FACET]->(pf)
```

### Relationships
- `HAS_[FACET_TYPE]_FACET` (any node) → [Facet Subclass] (e.g., HAS_POLITICAL_FACET, HAS_TECHNOLOGICAL_FACET)
- Each entity can point to multiple facets of different types, supporting multi-dimensional classification.

### Integration Notes
- All major node types should link to at least one facet node of each relevant type.
- Facet nodes are reusable: multiple entities can point to the same facet.
- Facet nodes can be extended (e.g., :ChronologicalFacet, :CulturalFacet) as needed.
- This system supports universal filtering, faceted search, and semantic navigation across the graph.

---

## Schema Format

Each node type has:
1. **Required Properties** - Must be present
2. **Optional Properties** - Should be included if known
3. **Required Edges** - Must connect to other nodes
4. **Optional Edges** - Should connect if relevant
5. **Examples** - Reference implementations

---

## Subject Node Schema ⭐ TOPICAL CLASSIFICATION (LCSH Authority System)

### Node Labels
```cypher
:Subject
```

**Purpose:** Topical/thematic classification using **Library of Congress Subject Headings (LCSH)** as the backbone authority system

**Backbone Authority:** LCSH (Library of Congress Subject Headings) - the authoritative controlled vocabulary managed by the Library of Congress

**What Subjects Are:** Subjects represent **what entities are ABOUT** (themes, topics), not what they ARE (structure)

**Critical Distinction:**
- ✅ **Topical subjects** - Politics, Military, Religion, Culture, Economics (use these!)
- ❌ **Structural categories** - Time, Geography (these are redundant - use entity types instead!)

**Navigation vs. Classification:**
- **Navigate** through hierarchies: Period → Parent Period, Place → Parent Place, Year → Next Year
- **Classify** by topic: Event → Military Subject, Person → Political Subject

### NEW ARCHITECTURE (Dec 2025): LCSH as Backbone Authority System

**LCSH = The Backbone:**
- ✅ **Authoritative controlled vocabulary** maintained by Library of Congress
- ✅ **86% event coverage** in Wikidata (vs. 14% for FAST)
- ✅ **Primary source** (FAST is derived from LCSH)
- ✅ **Better granularity** for historical events (e.g., "Pharsalus, Battle of, 48 B.C.")
- ✅ **Agent routing** via broader/narrower term hierarchies

**LCSH Hierarchy for Agent Routing:**
- ✅ **LCSH broader/narrower terms used for agent hierarchy**
- Example: "Rome--History" (broader) → "Rome--History--Republic, 510-30 B.C." (narrower)
- Agent spawning follows LCSH subject tree: sh85114934 → sh85115055 → specialists

**FAST as Supplementary Property:**
- Store FAST ID when available from Wikidata (P2163) (~54% coverage)
- Not required; used for cross-referencing only

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q17167" | Wikidata QID (for federation) |
| `lcsh_id` | string | sh[0-9]{8} | "sh85115055" | LCSH ID (PRIMARY BACKBONE) ⭐ |
| `lcsh_heading` | string | text | "Rome--History--Republic, 510-30 B.C." | Library of Congress Subject Heading (authoritative form) |
| `label` | string | text | "Roman Republic" | Human-readable label |
| `unique_id` | string | pattern | "SUBJECT_LCSH_sh85115055" | System ID (based on LCSH) |

### Optional Properties (Classification Metadata)

| Property         | Type     | Format              | Example                           | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ---------------------------------------------------- |
| `description`    | string   | text                | "Ancient Roman republican period" | Short description                                    |
| `aliases`        | string[] | text                | ["Roman Republic", "Res Publica"] | Alternative names/labels                             |
| `domain`         | string   | text                | "history"                         | Subject domain                                       |
| `scope_note`     | string   | text                | "Use for works on the Roman Republican period..." | LCSH scope note (usage guidance) |
| `broader_terms`  | string[] | text                | ["Rome--History"]                 | Broader LCSH terms (for hierarchy)                   |
| `narrower_terms` | string[] | text                | ["Rome--History--Servile Wars"]   | Narrower LCSH terms (for hierarchy)                  |
| `related_terms`  | string[] | text                | ["Republican Rome"]               | Related LCSH terms                                   |
| `wikidata_url`   | string   | URL                 | "https://www.wikidata.org/wiki/Q17167" | Full Wikidata URL                          |
| `lcsh_url`       | string   | URL                 | "https://id.loc.gov/authorities/subjects/sh85115055" | LCSH authority record URL            |

### Optional Properties (Authority Crosswalk via Wikidata) ⭐ NEW

**Wikidata as Universal Crosswalk Hub:** Use QID to fetch IDs from multiple authority systems via Wikidata properties. Enables interoperability with different agent preferences and external systems.

| Property         | Type     | Format              | Example                           | Wikidata Property | Coverage | Notes                                                |
| ---------------- | -------- | ------------------- | --------------------------------- | ----------------- | -------- | ---------------------------------------------------- |
| `fast_id`        | string   | fst[0-9]{8}         | "fst01210191"                     | P2163             | ~54%     | FAST ID (OCLC Faceted Application of Subject Terminology) - derived from LCSH, post-coordinated |
| `dewey`          | string   | [0-9]{3}\.[0-9]+    | "937.05"                          | P1036             | ~12%     | Dewey Decimal Classification - numerical classification for agent routing |
| `lcc_code`       | string   | [A-Z]{1,3}[0-9]+    | "DG235-254"                       | P1149             | varies   | Library of Congress Classification - alphanumeric shelf classification |
| `viaf_id`        | string   | [0-9]+              | "123456789"                       | P214              | varies   | Virtual International Authority File - international aggregator linking multiple national libraries |
| `gnd_id`         | string   | [0-9]{4,}(-[0-9xX])? | "4043912-4"                      | P227              | varies   | Gemeinsame Normdatei (GND) - German National Library authority ID |

**Fetching Crosswalk IDs:**
```python
# Query Wikidata to get all authority IDs for a Subject
import requests

qid = "Q17167"  # Roman Republic
url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
response = requests.get(url, headers={'User-Agent': 'YourBot/1.0'})
data = response.json()
claims = data['entities'][qid]['claims']

# Extract authority IDs
lcsh_id = claims['P244'][0]['mainsnak']['datavalue']['value']  # sh85115055
fast_id = claims['P2163'][0]['mainsnak']['datavalue']['value'] # fst01210191
dewey = claims['P1036'][0]['mainsnak']['datavalue']['value']   # 937.05
lcc = claims['P1149'][0]['mainsnak']['datavalue']['value']     # DG235-254
viaf_id = claims['P214'][0]['mainsnak']['datavalue']['value']  # 123456789
```

**Use Cases:**
- **Agent routing**: Different agents prefer different authorities (FAST facets vs LCSH pre-coordinated)
- **External system integration**: Link to library catalogs, databases using their preferred authority
- **Multilingual support**: VIAF connects to French (BnF), German (DNB), Japanese (NDL) national libraries
- **Cross-referencing**: Validate subject mappings across multiple authority systems

### Required Edges

**None** - Subject nodes are leaf nodes in the taxonomy (entities link TO them)

### LCSH Hierarchy Edges (Between Subjects)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `BROADER_THAN` | Subject | OUT | `(:Subject {lcsh_id: "sh85061097", lcsh_heading: "Historic buildings"})-[:BROADER_THAN]->(:Subject {lcsh_id: "sh85077493", lcsh_heading: "Literary landmarks"})` |

**Purpose:** BROADER_THAN relationships create the LCSH subject hierarchy used for agent routing and topical navigation.

**Database Status:** ✅ 10,992 BROADER_THAN relationships exist in the graph

**Direction Design:** Single-direction relationships (no NARROWER_THAN inverse)
```cypher
// Query narrower terms (traverse forward →)
MATCH (broader:Subject)-[:BROADER_THAN]->(narrower:Subject)
WHERE broader.lcsh_id = "sh85114934"
RETURN narrower

// Query broader terms (traverse backward ←)
MATCH (narrower:Subject)<-[:BROADER_THAN]-(broader:Subject)
WHERE narrower.lcsh_id = "sh85115055"
RETURN broader

// Multi-hop traversal (all ancestors)
MATCH path = (s:Subject {lcsh_id: "sh85115055"})<-[:BROADER_THAN*]-(ancestor)
RETURN ancestor

// Multi-hop traversal (all descendants)
MATCH path = (s:Subject {lcsh_id: "sh85114934"})-[:BROADER_THAN*]->(descendant)
RETURN descendant
```

**Why No NARROWER_THAN?** Neo4j relationships are bidirectional - you can traverse `BROADER_THAN` in both directions using `->` and `<-` in Cypher. Creating inverse relationships would duplicate all 10,992 edges and waste storage.

**Denormalized Properties:** For query performance, broader/narrower terms are ALSO stored as properties:
- `broader_ids` / `broader_terms` - Arrays of parent subject IDs and labels
- `narrower_ids` / `narrower_terms` - Arrays of child subject IDs and labels

**When to Use Each:**
- Use `BROADER_THAN` relationships for:
  - Graph visualization (shows lines between nodes)
  - Multi-hop traversal (find all ancestors/descendants)
  - Cypher path queries (`-[:BROADER_THAN*]->`)
  
- Use `broader_ids`/`broader_terms` properties for:
  - Quick single-level lookups (no traversal needed)
  - Displaying breadcrumbs in UI
  - API responses with immediate parent/child info

### Common Edges (Incoming)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `SUBJECT_OF` | Event, Person, Org | IN | `(event:Event {label: "Punic Wars"})-[:SUBJECT_OF]->(subject:Subject {lcsh_id: "sh85109289"})` |
| `DEFINED_BY` | PropertyRegistry | IN | `(reg:PropertyRegistry)-[:DEFINED_BY]->(subject)` |

**Note:** Do NOT link structural entity types to their obvious subjects:
- ❌ `(period:Period)-[:SUBJECT_OF]->(:Subject {label: "Time"})` - redundant!
- ❌ `(place:Place)-[:SUBJECT_OF]->(:Subject {label: "Geography"})` - redundant!
- ✅ `(event:Event {label: "Battle of Zama"})-[:SUBJECT_OF]->(:Subject {lcsh_id: "sh85109289"})` - good!

### Template

```cypher
CREATE (subject:Subject {
  // REQUIRED
  qid: "Q17167",  // Wikidata QID
  lcsh_id: "sh85115055",
  lcsh_heading: "Rome--History--Republic, 510-30 B.C.",
  label: "Roman Republic",
  unique_id: "SUBJECT_LCSH_sh85115055",
  
  // OPTIONAL (rich metadata)
  description: "Period of Roman history from overthrow of monarchy (510 BCE) to establishment of empire (27 BCE)",
  aliases: ["Roman Republic", "Res Publica Romana", "Republican Rome"],
  domain: "history",
  scope_note: "Use for works on the Roman Republican period. For specific events, see narrower terms.",
  broader_terms: ["Rome--History"],
  narrower_terms: [
    "Rome--History--Servile Wars, 135-71 B.C.",
    "Rome--History--Republic, 265-30 B.C.",
    "Rome--History--Social War, 91-88 B.C."
  ],
  related_terms: ["Republican government", "Roman Senate"],
  lcc_code: "DG235-254",  // Library shelving metadata
  fast_id: "fst01210191",  // Supplementary cross-reference
  wikidata_url: "https://www.wikidata.org/wiki/Q17167",
  lcsh_url: "https://id.loc.gov/authorities/subjects/sh85115055"
})

// Example usage - entities link TO topical subjects
CREATE (event:Event {label: "Battle of Pharsalus", qid: "Q48314"})
CREATE (event)-[:SUBJECT_OF]->(subject)

// BROADER_THAN relationships for LCSH hierarchy (visualizes as graph edges)
CREATE (broader:Subject {lcsh_id: "sh85114934", lcsh_heading: "Rome--History"})
CREATE (narrower:Subject {lcsh_id: "sh85115055", lcsh_heading: "Rome--History--Republic, 510-30 B.C."})
CREATE (broader)-[:BROADER_THAN]->(narrower)

// Denormalized properties mirror the relationships for quick lookup
SET narrower.broader_ids = ["sh85114934"]
SET narrower.broader_terms = ["Rome--History"]
SET broader.narrower_ids = [..., "sh85115055", ...]
SET broader.narrower_terms = [..., "Rome--History--Republic, 510-30 B.C.", ...]
```

**Visualization:**
```
┌─────────────────────────────────┐
│ Rome--History                   │  
│ (sh85114934)                    │
│ broader_ids: []                 │
│ narrower_ids: [sh85115055, ...] │  ← Properties (quick lookup)
└─────────────────┬───────────────┘
                  │ BROADER_THAN       ← Relationship (graph edge/line)
                  ↓
┌─────────────────────────────────┐
│ Rome--History--Republic         │
│ (sh85115055)                    │
│ broader_ids: [sh85114934]       │  ← Properties (denormalized)
│ narrower_ids: [...]             │
└─────────────────────────────────┘
```

### Critical Notes

**LCSH IDs are PRIMARY BACKBONE:**
- ✅ Primary key: `lcsh_id` (not FAST)
- ✅ Unique identifier: `SUBJECT_LCSH_sh85115055`
- ✅ Best coverage for events (86%)

**Dewey Decimal for AGENT ROUTING:**
- ✅ Determines which agent handles a query
- ✅ Hierarchical agent spawning (937 → 937.05 → 937.052)
- ✅ Good coverage for historical periods

**FAST as SUPPLEMENTARY PROPERTY:**
- ✅ Store when available from Wikidata P2163
- ✅ Use for cross-referencing
- ❌ NOT required (poor event coverage)
- ❌ NOT primary key

**LCC as LIBRARY METADATA:**
- ✅ Library shelving code (optional)
- ✅ Stored for interoperability with library systems
- ❌ NOT used for agent routing (LCSH hierarchy handles this)

**Subject nodes enable:**
1. Topical discovery (find all entities about "Military history")
2. Cross-domain connections (link Politics to Military events)
3. Library of Congress alignment (LCSH/LCC interoperability)
4. Agent routing (Dewey code → agent assignment)
5. Thematic browsing (explore by topic, not just by time/place)

**Ontology Principle:**
- **Structure** = Entity types + Hierarchies (Period → Period, Place → Place)
- **Topics** = Subject classifications (Event → Military, Person → Politics)
- Don't confuse the two!

**Workflow for Subject Creation:**
1. **Get entity QID** from source or Wikidata search
2. **Query Wikidata** for subject properties:
   - P244 (LCSH ID) - PRIMARY (required)
   - P1149 (LCC) - optional library metadata
   - P2163 (FAST) - optional supplementary property
3. **Get broader/narrower terms** from LCSH vocabulary
4. **Create Subject node** with complete properties including qid, lcsh_id

---

## Person Node Schema

### Node Labels
```cypher
:Person
```

**Note:** No `:Concept` label - your ontology uses specific entity types only.

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q1048" | Wikidata ID (unique identifier) |
| `label` | string | text | "Julius Caesar" | Primary name |
| `unique_id` | string | pattern | "Q1048_PERSON_JULIUS_CAESAR" | System ID |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `description` | string | text | "Roman military and political leader" | Short description |
| `aliases` | string[] | text | ["Gaius Julius Caesar", "Caesar"] | Alternative names |
| `birth_date` | string | ISO 8601 | "-0100-07-12" | Birth date (ISO 8601 format) |
| `death_date` | string | ISO 8601 | "-0044-03-15" | Death date (ISO 8601 format) |
| `birth_place_qid` | string | Q[0-9]+ | "Q220" | Birth place Wikidata QID |
| `birth_place_label` | string | text | "Rome" | Birth place name |
| `death_place_qid` | string | Q[0-9]+ | "Q220" | Death place Wikidata QID |
| `death_place_label` | string | text | "Rome" | Death place name |
| `gender_qid` | string | Q[0-9]+ | "Q6581097" | Q6581097 = male, Q6581072 = female |
| `occupation_qid` | string[] | Q[0-9]+ | ["Q82955", "Q37110"] | Occupation QIDs (general, statesman) |
| `occupation_labels` | string[] | text | ["Military commander", "Statesman"] | Human-readable occupations |
| `citizenship_qid` | string | Q[0-9]+ | "Q17167" | Citizenship/nationality |
| `wikidata_url` | string | URL | "https://www.wikidata.org/wiki/Q1048" | Full Wikidata URL |
| `viaf_id` | string | pattern | "286265178" | VIAF authority ID |
| `lcnaf_id` | string | pattern | "n79021400" | Library of Congress Name Authority File ID |

**Note:** For Roman history, consider using Roman naming entities (Praenomen, Gens, Cognomen) via relationships rather than storing as properties. See Roman Naming Edges section below.

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `SUBJECT_OF` | Subject | 1+ | **Topical classification** (what person is known for) |

### Common Edges (Should Include)

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `BORN_IN` | Place | OUT | `(caesar)-[:BORN_IN]->(rome:Place)` |
| `DIED_IN` | Place | OUT | `(caesar)-[:DIED_IN]->(rome:Place)` |
| `LIVED_DURING` | Period | OUT | `(caesar)-[:LIVED_DURING]->(roman_republic:Period)` |
| `HELD_POSITION` | Position | OUT | `(caesar)-[:HELD_POSITION {start_year: -59}]->(consul:Position)` |
| `PARTICIPATED_IN` | Event | OUT | `(caesar)-[:PARTICIPATED_IN {role: "military commander"}]->(gallic_wars:Event)` |
| `MEMBER_OF` | Organization | OUT | `(caesar)-[:MEMBER_OF]->(senate:Organization)` |

### Roman Naming Edges (Optional - for Roman history)

| Relationship | Target | Direction | Example | Notes |
|--------------|--------|-----------|---------|-------|
| `HAS_PRAENOMEN` | Praenomen | OUT | `(caesar)-[:HAS_PRAENOMEN]->(gaius:Praenomen)` | Roman given name |
| `MEMBER_OF_GENS` | Gens | OUT | `(caesar)-[:MEMBER_OF_GENS {validFrom: "-0100", primaryGens: true}]->(gens_julia:Gens)` | Clan membership |
| `HAS_COGNOMEN_PRIMARY` | Cognomen | OUT | `(caesar)-[:HAS_COGNOMEN_PRIMARY]->(caesar_cognomen:Cognomen)` | Primary family name |
| `HAS_COGNOMEN_OTHER` | Cognomen | OUT | `(caesar)-[:HAS_COGNOMEN_OTHER]->(divus_cognomen:Cognomen)` | Additional cognomina |

### Template

```cypher
CREATE (person:Person {
  // REQUIRED
  qid: "Q1048",
  label: "Julius Caesar",
  unique_id: "Q1048_PERSON_JULIUS_CAESAR",
  
  // OPTIONAL (if known)
  birth_date: "-0100-07-12",
  death_date: "-0044-03-15",
  birth_place_qid: "Q220",
  death_place_qid: "Q220",
  gender_qid: "Q6581097",
  occupation_qid: ["Q82955", "Q37110"],
  description: "Roman military and political leader"
})

// REQUIRED EDGES - Topical classification
CREATE (person)-[:SUBJECT_OF]->(political_subject:Subject {
  label: "Political science",
  fast_id: "1069263"
})
CREATE (person)-[:SUBJECT_OF]->(military_subject:Subject {
  label: "Military art and science",
  fast_id: "1020874"
})

// COMMON EDGES (include if relevant)
CREATE (person)-[:BORN_IN]->(rome:Place {qid: "Q220"})
CREATE (person)-[:DIED_IN]->(rome:Place {qid: "Q220"})
CREATE (person)-[:LIVED_DURING]->(roman_republic:Period {qid: "Q17167"})
CREATE (person)-[:HELD_POSITION {start_year: -59, end_year: -58}]->(consul:Position)
CREATE (person)-[:PARTICIPATED_IN {role: "military commander"}]->(gallic_wars:Event)

// ROMAN NAMING EDGES (for Roman history - optional)
CREATE (person)-[:HAS_PRAENOMEN]->(praenomen:Praenomen {qid: "Q...", label: "Gaius"})
CREATE (person)-[:MEMBER_OF_GENS {validFrom: "-0100", primaryGens: true}]->(gens:Gens {qid: "Q...", label: "Gens Julia"})
CREATE (person)-[:HAS_COGNOMEN_PRIMARY]->(cognomen:Cognomen {qid: "Q...", label: "Caesar"})
CREATE (person)-[:HAS_COGNOMEN_OTHER]->(divus_cognomen:Cognomen {qid: "Q...", label: "Divus"})
```

### Example: Complete Person Subgraph

```cypher
// Person node
(:Person {label: "Julius Caesar", qid: "Q1048"})
  ↓ SUBJECT_OF (topical - what he's known for)
(:Subject {label: "Political leaders", fast_id: "..."})
(:Subject {label: "Military commanders", fast_id: "..."})
  
  ↓ LIVED_DURING (temporal - when)
(:Period {label: "Roman Republic"})
  ↓ SUB_PERIOD_OF
(:Period {label: "Ancient Rome"})

  ↓ BORN_IN (geographic - where)
(:Place {label: "Rome"})
  ↓ LOCATED_IN
(:Place {label: "Italy"})

  ↓ PARTICIPATED_IN (events)
(:Event {label: "Gallic Wars"})
(:Event {label: "Crossing Rubicon"})
```

---

## Gens Node Schema (Roman Clan)

### Node Labels
```cypher
:Gens
```

**Purpose:** Represents a Roman gens (clan), an extended kin group sharing a claimed ancestor and political identity.

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q..." | Wikidata ID (if available) |
| `label` | string | text | "Gens Julia" | Human-readable label |
| `unique_id` | string | pattern | "GENS_JULIA_Q..." | System ID |
| `nomen_string` | string | text | "Julius" | Nomen (clan name) |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `canonical_form` | string | text | "Iulius" | Latin nominative form |
| `description` | string | text | "Patrician gens of ancient Rome" | Description |
| `active_from` | string | ISO 8601 | "-0753" | Approximate start century |
| `active_to` | string | ISO 8601 | "0476" | Approximate end century |
| `status` | string | text | "patrician" | Social status (patrician/plebeian) |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `SUBJECT_OF` | Subject | 1+ | Topical classification |

### Common Edges (Incoming)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `MEMBER_OF_GENS` | Person | IN | `(caesar:Person)-[:MEMBER_OF_GENS]->(gens_julia:Gens)` |

### Template

```cypher
CREATE (gens:Gens {
  // REQUIRED
  qid: "Q...",  // Wikidata ID if available
  label: "Gens Julia",
  unique_id: "GENS_JULIA_Q...",
  nomen_string: "Julius",
  
  // OPTIONAL
  canonical_form: "Iulius",
  description: "Patrician gens of ancient Rome",
  active_from: "-0753",
  active_to: "0476",
  status: "patrician"
})

// REQUIRED EDGES - Topical classification
CREATE (gens)-[:SUBJECT_OF]->(subject:Subject {
  label: "Rome--History--Republic",
  fast_id: "..."
})
```

---

## Praenomen Node Schema (Roman Given Name)

### Node Labels
```cypher
:Praenomen
```

**Purpose:** Represents a Roman praenomen (given name), used for disambiguation and name normalization.

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q..." | Wikidata ID (if available) |
| `label` | string | text | "Gaius" | Human-readable label |
| `unique_id` | string | pattern | "PRAENOMEN_GAIUS_Q..." | System ID |
| `label_latin` | string | text | "Gaius" | Latin form |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `abbreviation` | string | text | "C." | Common abbreviation |
| `typical_gender` | string | text | "male" | Gender typically associated |
| `use_from` | string | ISO 8601 | "-0753" | Approximate start century |
| `use_to` | string | ISO 8601 | "0476" | Approximate end century |
| `rarity` | string | text | "common" | Frequency (common/rare/uncommon) |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `SUBJECT_OF` | Subject | 1+ | Topical classification |

### Common Edges (Incoming)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `HAS_PRAENOMEN` | Person | IN | `(caesar:Person)-[:HAS_PRAENOMEN]->(gaius:Praenomen)` |

### Template

```cypher
CREATE (praenomen:Praenomen {
  // REQUIRED
  qid: "Q...",  // Wikidata ID if available
  label: "Gaius",
  unique_id: "PRAENOMEN_GAIUS_Q...",
  label_latin: "Gaius",
  
  // OPTIONAL
  abbreviation: "C.",
  typical_gender: "male",
  use_from: "-0753",
  use_to: "0476",
  rarity: "common"
})

// REQUIRED EDGES - Topical classification
CREATE (praenomen)-[:SUBJECT_OF]->(subject:Subject {
  lcsh_id: "sh...",
  label: "Rome--History"
})
```

---

## Cognomen Node Schema (Roman Family Name/Branch)

### Node Labels
```cypher
:Cognomen
```

**Purpose:** Represents a Roman cognomen (family name or branch identifier), distinguishing branches within a gens.

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q..." | Wikidata ID (if available) |
| `label` | string | text | "Caesar" | Human-readable label |
| `unique_id` | string | pattern | "COGNOMEN_CAESAR_Q..." | System ID |
| `label_latin` | string | text | "Caesar" | Latin form |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `meaning` | string | text | "hairy" | Etymology/meaning |
| `branch_of_gens_qid` | string | Q[0-9]+ | "Q..." | Gens this cognomen belongs to |
| `use_from` | string | ISO 8601 | "-0100" | Approximate start century |
| `use_to` | string | ISO 8601 | "0476" | Approximate end century |
| `origin` | string | text | "honorific" | Origin (honorific/adoptive/descriptive) |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `SUBJECT_OF` | Subject | 1+ | Topical classification |

### Common Edges (Incoming)

| Relationship | Source | Direction | Example |
|--------------|--------|-----------|---------|
| `HAS_COGNOMEN_PRIMARY` | Person | IN | `(caesar:Person)-[:HAS_COGNOMEN_PRIMARY]->(caesar_cognomen:Cognomen)` |
| `HAS_COGNOMEN_OTHER` | Person | IN | `(caesar:Person)-[:HAS_COGNOMEN_OTHER]->(divus_cognomen:Cognomen)` |

### Template

```cypher
CREATE (cognomen:Cognomen {
  // REQUIRED
  qid: "Q...",  // Wikidata ID if available
  label: "Caesar",
  unique_id: "COGNOMEN_CAESAR_Q...",
  label_latin: "Caesar",
  
  // OPTIONAL
  meaning: "hairy",
  branch_of_gens_qid: "Q...",  // Gens Julia
  use_from: "-0100",
  use_to: "0476",
  origin: "honorific"
})

// REQUIRED EDGES - Topical classification
CREATE (cognomen)-[:SUBJECT_OF]->(subject:Subject {
  lcsh_id: "sh...",
  label: "Rome--History"
})

// OPTIONAL - Link to Gens if branch identifier
CREATE (cognomen)-[:BRANCH_OF]->(gens:Gens {qid: "Q..."})
```

---

## Event Node Schema

### Node Labels
```cypher
:Event
```

**Note:** No `:Concept` label - events are events, not abstract concepts.

**Note:** Year nodes form the temporal backbone

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q161954" | Wikidata ID |
| `label` | string | text | "Crossing of the Rubicon" | Event name |
| `unique_id` | string | pattern | "Q161954_EVENT_CROSSING_RUBICON" | System ID |
| `date_iso8601` | string | ISO 8601 | "-0049-01-10" | When it happened |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `granularity` | string | enum | "atomic" | **REQUIRED** - atomic/composite/period_event (see below) |
| `description` | string | text | "Caesar crossed the Rubicon..." | Event description |
| `aliases` | string[] | text | ["Rubicon Crossing", "Crossing the Rubicon"] | Alternative names |
| `start_date` | string | ISO 8601 | "-0049-01-10" | Event start date |
| `end_date` | string | ISO 8601 | "-0049-01-15" | Event end date (for multi-day events) |
| `start_year` | integer | year | -49 | Start year (for queries) |
| `end_year` | integer | year | -49 | End year (for queries) |
| `duration_days` | integer | count | 1 | Duration in days |
| `location_qid` | string | Q[0-9]+ | "Q14378" | Where it happened (Wikidata QID) |
| `location_label` | string | text | "Zama" | Location name |
| `part_of_qid` | string | Q[0-9]+ | "Q46083" | Parent event QID (e.g., civil war) |
| `part_of_label` | string | text | "Caesar's Civil War" | Parent event name |
| `participants_qid` | string[] | Q[0-9]+ | ["Q1048", "Q2039"] | Participant QIDs |
| `participants_labels` | string[] | text | ["Julius Caesar", "XIII Legion"] | Participant names |
| `casualties` | integer | count | 0 | Casualties (if applicable) |
| `goal_type` | string | enum | "POL" | Political/Military/Economic/Social |
| `trigger_type` | string | enum | "OPPORT" | Opportunity/Threat/Crisis/Response |
| `action_type` | string | enum | "MIL_ACT" | Military_Action/Diplomatic/Legal/Cultural |
| `result_type` | string | enum | "POL_TRANS" | Political_Transformation/Military_Victory/etc |
| `significance` | string | enum | "major" | major/moderate/minor |
| `wikidata_url` | string | URL | "https://www.wikidata.org/wiki/Q161954" | Full Wikidata URL |

### Event Granularity Classification

**All Event nodes MUST include `granularity` property** to enable multi-perspective resolution and query optimization.

| Value | Definition | Typical Duration | Example | Use When |
|-------|------------|------------------|---------|----------|
| `atomic` | Single discrete moment, observable, short duration | Seconds to days (≤7 days) | "Assassination of Caesar" (44 BCE-03-15) | Specific date, short duration, named participants |
| `composite` | Collection of atomic events, explicit start/end | Weeks to years | "Gallic Wars" (58-50 BCE) | Multiple sub-events, campaign/reform program |
| `period_event` | Historiographical construct, interpretive, vague boundaries | Years to decades | "Fall of Roman Republic" (133-27 BCE) | Interpretive label, long duration, debated dates |
| `macro_event` | Abstract process, no sharp temporal boundaries | Decades to centuries | "Roman Expansion" | **Avoid** - use Period nodes instead |

**Multi-Perspective Resolution Rule:** When multiple agents describe overlapping events, **pick the most granular as anchor** (atomic > composite > period_event). Create perspective edges from anchor to other interpretations using `INTERPRETED_AS`, `PART_OF`, or `CAUSED_BY` relationships.

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `SUBJECT_OF` | Subject | 1+ | **Topical classification** (what the event is about) |
| `OCCURRED_IN` | Period | 1+ | Temporal context (which period) |

### Common Edges (Should Include)

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `OCCURRED_ON` | Year | OUT | `(event)-[:OCCURRED_ON]->(year:Year {year_value: -49})` |
| `LOCATED_AT` | Place | OUT | `(event)-[:LOCATED_AT]->(place:Place)` |
| `PARTICIPATED_IN` | Person | IN | `(person:Person)-[:PARTICIPATED_IN {role: "commander"}]->(event)` |
| `INVOLVED` | Organization | OUT | `(event)-[:INVOLVED]->(org:Organization)` |
| `CAUSED` | Event | OUT | `(event1)-[:CAUSED]->(event2:Event)` |
| `PRECEDED_BY` | Event | IN | `(event2)-[:PRECEDED_BY]->(event1:Event)` |
| `RESULTED_IN` | Multiple | OUT | `(event)-[:RESULTED_IN]->(outcome)` - can be Event, Organization, etc. |
| `FOLLOWED_BY` | Event | OUT | `(event1)-[:FOLLOWED_BY]->(event2)` |

### Template

```cypher
CREATE (event:Event {
  // REQUIRED
  qid: "Q161954",
  label: "Crossing of the Rubicon",
  unique_id: "Q161954_EVENT_CROSSING_RUBICON",
  date_iso8601: "-0049-01-10",
  
  // REQUIRED - Granularity classification
  granularity: "atomic",  // Single discrete moment, ≤7 days
  
  // OPTIONAL (if known)
  description: "Caesar crossed the Rubicon River with his legion",
  location_qid: "Q14378",
  goal_type: "POL",
  trigger_type: "OPPORT",
  action_type: "MIL_ACT",
  result_type: "POL_TRANS"
})

// REQUIRED EDGES - Topical classification
CREATE (event)-[:SUBJECT_OF]->(military_subject:Subject {
  label: "Military history",
  fast_id: "1020874"
})
CREATE (event)-[:SUBJECT_OF]->(political_subject:Subject {
  label: "Political science",
  fast_id: "1069263"
})

// REQUIRED EDGES - Temporal context
CREATE (event)-[:OCCURRED_IN]->(civil_war_period:Period {
  label: "Caesar's Civil War"
})

// COMMON EDGES
CREATE (event)-[:OCCURRED_ON]->(year:Year {year_value: -49})
CREATE (event)-[:LOCATED_AT]->(rubicon:Place {qid: "Q14378"})
CREATE (caesar:Person {qid: "Q1048"})-[:PARTICIPATED_IN {role: "military commander"}]->(event)
CREATE (event)-[:CAUSED]->(civil_war:Event {label: "Caesar's Civil War"})
CREATE (event)-[:RESULTED_IN]->(dictatorship:Event {label: "Caesar's Dictatorship"})
```

### Example: Complete Event Subgraph

```cypher
// Event node (central entity)
(:Event {label: "Crossing of the Rubicon", qid: "Q161954"})
  ↓ SUBJECT_OF (topical - what it's about)
(:Subject {label: "Military history", fast_id: "1020874"})
(:Subject {label: "Political transitions", fast_id: "1069263"})
  
  ↓ OCCURRED_IN (temporal - when)
(:Period {label: "Caesar's Civil War"})
  ↓ SUB_PERIOD_OF
(:Period {label: "Roman Republic"})
  ↓ SUB_PERIOD_OF
(:Period {label: "Ancient Rome"})

  ↓ LOCATED_AT (geographic - where)
(:Place {label: "Rubicon River"})
  ↓ LOCATED_IN
(:Place {label: "Italy"})

  ↓ PARTICIPATED_IN (who)
(:Person {label: "Julius Caesar"})
  ↓ SUBJECT_OF
(:Subject {label: "Political leaders"})

  ↓ CAUSED (consequences)
(:Event {label: "Caesar's Civil War"})
(:Event {label: "Caesar's Dictatorship"})
```

---

## CIDOC-CRM Mapping Table (Key Node Types)

| Node Type      | Proprietary Label | CIDOC-CRM Class | Notes |
|----------------|-------------------|-----------------|-------|
| Subject        | :Subject          | E55 Type        | Topical classification (LCSH/FAST) |
| Person         | :Person           | E21 Person      | Individual human being |
| Event          | :Event            | E5 Event        | Historical event, occurrence |
| Place          | :Place            | E53 Place       | Geographic location |
|

---

## Place Node Schema ⭐ GEOGRAPHIC BACKBONE (Getty TGN Authority Model)

### Node Labels
```cypher
:Place
```

**Purpose:** Canonical representation of geographic entities using the Getty Thesaurus of Geographic Names (TGN) as the backbone authority. Supports rich, multi-field authority records for places, enabling robust crosswalks to Wikidata, GeoNames, Pleiades, and other systems.

**Backbone Authority:** Getty TGN (Thesaurus of Geographic Names) - the authoritative, multi-field, hierarchical vocabulary for places.

**What Places Are:** Places represent real-world geographic entities (countries, cities, archaeological sites, natural features, etc.), not just coordinates or labels.

### Required Properties

| Property         | Type     | Format         | Example           | Notes |
|------------------|----------|---------------|-------------------|-------|
| `tgn_id`         | string   | [0-9]+        | "7011179"        | Getty TGN ID (primary key) ⭐ |
| `label`          | string   | text          | "Rome"           | Preferred name (English or local) |
| `unique_id`      | string   | pattern       | "PLACE_TGN_7011179" | System ID (based on TGN) |

### Optional Properties (Getty TGN Authority Fields)

| Property             | Type       | Format         | Example                | Notes |
|----------------------|------------|---------------|------------------------|-------|
| `tgn_type`           | string     | text          | "inhabited place"     | TGN type/category (e.g., city, region, water body) |
| `parent_id`          | string     | [0-9]+        | "1000080"             | TGN parent ID (hierarchical parent) |
| `parent_label`       | string     | text          | "Italy"               | Parent place label |
| `latitude`           | float      | decimal       | 41.8931                | Latitude (WGS84) |
| `longitude`          | float      | decimal       | 12.4828                | Longitude (WGS84) |
| `geojson`            | object     | GeoJSON       | {"type": "Point", ...} | GeoJSON geometry (point, polygon, etc.) |
| `country_code`       | string     | ISO 3166-1    | "IT"                  | Country code (if applicable) |
| `feature_code`       | string     | text          | "PPL"                  | Feature code (GeoNames-style, if mapped) |
| `wikidata_qid`       | string     | Q[0-9]+       | "Q220"                 | Wikidata QID (if mapped) |
| `geonames_id`        | string     | [0-9]+        | "3169070"              | GeoNames ID (if mapped) |
| `pleiades_id`        | string     | [0-9]+        | "423025"               | Pleiades ID (if mapped) |
| `dbpedia_uri`        | string     | URI           | "http://dbpedia.org/resource/Rome" | DBpedia URI (if mapped) |
| `tgn_scope_note`     | string     | text          | "Capital of Italy..."  | Getty TGN scope note/description |
| `variant_names`      | string[]   | text[]        | ["Roma", "Rome, Italy"] | All variant names/labels |
| `dates`              | string     | text          | "founded 753 BCE"      | Key historical dates (if known) |
| `place_types`        | string[]   | text[]        | ["capital", "ancient city"] | All applicable place types |
| `sources`            | string[]   | text[]        | ["Getty TGN", "Wikidata"] | Provenance of data fields |
| `external_links`     | string[]   | URL[]         | ["https://www.getty.edu/vow/TGNFullDisplay?find=7011179"] | External authority record URLs |

### Example Cypher Template

```cypher
CREATE (rome:Place {
  // REQUIRED
  tgn_id: "7011179",
  label: "Rome",
  unique_id: "PLACE_TGN_7011179",

  // OPTIONAL (Getty TGN fields)
  tgn_type: "inhabited place",
  parent_id: "1000080",
  parent_label: "Italy",
  latitude: 41.8931,
  longitude: 12.4828,
  geojson: {type: "Point", coordinates: [12.4828, 41.8931]},
  country_code: "IT",
  feature_code: "PPL",
  wikidata_qid: "Q220",
  geonames_id: "3169070",
  pleiades_id: "423025",
  dbpedia_uri: "http://dbpedia.org/resource/Rome",
  tgn_scope_note: "Capital of Italy, ancient city, seat of the Roman Empire.",
  variant_names: ["Roma", "Rome, Italy", "Roma, Italia"],
  dates: "founded 753 BCE",
  place_types: ["capital", "ancient city"],
  sources: ["Getty TGN", "Wikidata", "GeoNames"],
  external_links: [
    "https://www.getty.edu/vow/TGNFullDisplay?find=7011179",
    "https://www.wikidata.org/wiki/Q220",
    "https://www.geonames.org/3169070/rome.html"
  ]
})
```

### Required Edges

| Relationship     | Target         | Cardinality | Notes |
|------------------|---------------|-------------|-------|
| `LOCATED_IN`     | Place         | 0..1        | Hierarchical parent (TGN parent) |

### Common Edges (Should Include)

| Relationship         | Target         | Direction | Example |
|----------------------|----------------|-----------|---------|
| `LOCATED_IN`         | Place          | OUT       | `(rome)-[:LOCATED_IN]->(italy)` |
| `HAS_COORDINATES`    | Coordinates    | OUT       | `(rome)-[:HAS_COORDINATES]->(:Coordinates {lat: 41.8931, lon: 12.4828})` |
| `HAS_VARIANT_NAME`   | Name           | OUT       | `(rome)-[:HAS_VARIANT_NAME]->(:Name {label: "Roma"})` |
| `HAS_EXTERNAL_ID`    | ExternalID     | OUT       | `(rome)-[:HAS_EXTERNAL_ID]->(:ExternalID {type: "GeoNames", value: "3169070"})` |

**Note:** Place nodes should be as rich as possible, reflecting the full Getty TGN authority record structure. All crosswalks to Wikidata, GeoNames, Pleiades, and other systems should be included as properties or edges where possible.

---
|