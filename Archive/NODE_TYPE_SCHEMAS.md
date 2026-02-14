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

id:
label:
qid:
qid_label:
broader_than:
narrower_than:
cip_id:
cip_label:

### Node Labels
```cypher
:Subject
```

**Purpose:** Topical/thematic classification using **Library of Congress Subject Headings (LCSH)** as the backbone authority system, now enriched with Wikidata properties and broader/narrower relationships.

**Backbone Authority:** LCSH (Library of Congress Subject Headings) - the authoritative controlled vocabulary managed by the Library of Congress

**What Subjects Are:** Subjects represent **what entities are ABOUT** (themes, topics), not what they ARE (structure)

**New Enrichment:**
- All Wikidata property QIDs and labels (e.g., P31_qids, P31_labels, P279_qids, P279_labels, etc.) are now included as node properties, auto-populated from Wikidata.
- Broader/narrower relationships are included as both properties and edges.
- Crosswalks to FAST, Dewey, LCC, VIAF, GND, etc. are included when available.

#### Example Node (Enriched)
```json
{
  "cip_id": "01.0101",
  "cip_label": "Agricultural Business and Management, General.",
  "qid": "Q3606845",
  "qid_label": "agricultural science",
  "label": "agricultural science",
  "broader_than": "Q28797",
  "broader_than_label": "applied science",
  "narrower_than": "Q110350495",
  "narrower_than_label": "Māori agriculture and forestry",
  "P31_qids": "Q11862829",
  "P31_labels": "academic discipline",
  "P279_qids": "Q441",
  "P279_labels": "(label)",
  "P361_qids": "",
  "P361_labels": "",
  // ... all other property columns ...
  "node_type": "concept_subject",
  "subject_type": "discipline"
}
```

All property columns from your property list (e.g., P31_qids, P31_labels, P279_qids, P279_labels, etc.) are included and filled with values fetched from Wikidata. Broader/narrower relationships are both properties and edges.



**LCSH Hierarchy for Agent Routing:**
- ✅ **LCSH broader/narrower terms used for agent hierarchy**
- Example: "Rome--History" (broader) → "Rome--History--Republic, 510-30 B.C." (narrower)
- Agent spawning follows LCSH subject tree: sh85114934 → sh85115055 → specialists

**FAST as Supplementary Property:**
- Store FAST ID when available from Wikidata (P2163) (~54% coverage)
- Not required; used for cross-referencing only

### Required Properties

| Property         | Type     | Format              | Example                           | Notes                                                |
|------------------|----------|---------------------|-----------------------------------|------------------------------------------------------|
| `cip_id`         | string   | text                | "01.0101"                        | CIP code if available                                |
| `cip_label`      | string   | text                | "Agricultural Business..."        | CIP label if available                               |
| `qid`            | string   | Q[0-9]+             | "Q3606845"                       | Wikidata QID (for federation)                        |
| `qid_label`      | string   | text                | "agricultural science"           | Wikidata label                                       |
| `label`          | string   | text                | "agricultural science"           | Human-readable label                                 |
| `broader_than`   | string   | Q[0-9]+             | "Q28797"                         | QID of broader subject                               |
| `broader_than_label` | string | text               | "applied science"                | Label of broader subject                             |
| `narrower_than`  | string   | Q[0-9]+             | "Q110350495"                     | QID of narrower subject                              |
| `narrower_than_label` | string | text              | "Māori agriculture and forestry" | Label of narrower subject                            |
| `P31_qids`       | string   | Q[0-9]+             | "Q11862829"                      | instance of (Wikidata property)                      |
| `P31_labels`     | string   | text                | "academic discipline"             | Label for P31_qids                                   |
| ...              | ...      | ...                 | ...                               | All other property columns from property list        |
| `node_type`      | string   | text                | "concept_subject"                 | Node type                                            |
| `subject_type`   | string   | text                | "discipline"                      | Subject type                                         |

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
| `birth_year` | integer | year | -100 | Birth year (for queries) |
| `death_date` | string | ISO 8601 | "-0044-03-15" | Death date (ISO 8601 format) |
| `death_year` | integer | year | -44 | Death year (for queries) |
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
  lcsh_id: "sh...",
  label: "Rome--History--Republic"
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
| `duration_days` | integer | days | 1 | Duration in days |
| `location_qid` | string | Q[0-9]+ | "Q14378" | Where it happened (Wikidata QID) |
| `location_label` | string | text | "Rubicon River" | Location name |
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
(:Subject {label: "Political transitions", fast_id: "..."})
  
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
```

---

## Place Node Schema

### Node Labels
```cypher
:Place
```

**Note:** No `:Concept` label - places are concrete geographic entities.

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q220" | Wikidata ID |
| `label` | string | text | "Rome" | Primary name |
| `unique_id` | string | pattern | "Q220_PLACE_ROME" | System ID |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `description` | string | text | "Capital of Roman Republic and Empire" | Short description |
| `aliases` | string[] | text | ["Roma", "Eternal City", "Urbs"] | Alternative names |
| `coordinates` | float[] | [lat, lon] | [41.9028, 12.4964] | Geographic coordinates (WGS84) |
| `latitude` | float | decimal | 41.9028 | Latitude |
| `longitude` | float | decimal | 12.4964 | Longitude |
| `elevation` | integer | meters | 21 | Elevation above sea level |
| `founded_date` | string | ISO 8601 | "-0753-04-21" | When founded |
| `founded_year` | integer | year | -753 | Founding year (for queries) |
| `dissolved_date` | string | ISO 8601 | "1453-05-29" | When dissolved |
| `dissolved_year` | integer | year | 1453 | Dissolution year (for queries) |
| `region` | string | text | "Lazio" | Administrative region |
| `country_qid` | string | Q[0-9]+ | "Q38" | Country QID |
| `country_label` | string | text | "Italy" | Country name |
| `population` | integer | count | 2873000 | Population (current or historical) |
| `area_km2` | float | square km | 1285.31 | Area in square kilometers |
| `stability` | string | enum | "high" | very_high/high/medium/low/very_low |
| `feature_type` | string | enum | "city" | natural/political/cultural/military |
| `place_category` | string[] | text | ["capital", "ancient city"] | Place categories |
| `geonames_id` | string | pattern | "3169070" | GeoNames identifier |
| `tgn_id` | string | pattern | "7000874" | Getty TGN identifier |
| `wikidata_url` | string | URL | "https://www.wikidata.org/wiki/Q220" | Full Wikidata URL |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `INSTANCE_OF` | Concept | 1 | Links to place type |

### Common Edges (Should Include)

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `LOCATED_IN` | Place | OUT | `(rome)-[:LOCATED_IN]->(italy)` |
| `BORDERS` | Place | BOTH | `(place1)-[:BORDERS]-(place2)` |
| `CAPITAL_OF` | Concept/Organization | OUT | `(rome)-[:CAPITAL_OF]->(republic)` |

### Template

```cypher
CREATE (place:Place:Concept {
  // REQUIRED
  qid: "Q220",
  label: "Rome",
  unique_id: "Q220_PLACE_ROME",
  
  // OPTIONAL (if known)
  coordinates: [41.9028, 12.4964],
  founded_date: "-0753-04-21",
  region: "Italy",
  stability: "high",
  feature_type: "city",
  description: "Capital of Roman Republic and Empire"
})

// REQUIRED EDGES
CREATE (place)-[:INSTANCE_OF]->(place_type:Concept {qid: "Q515"})

// COMMON EDGES
CREATE (place)-[:LOCATED_IN]->(region:Place)
CREATE (place)-[:CAPITAL_OF {start: -509, end: 330}]->(entity:Concept)
```

---

## Period Node Schema

### Node Labels
```cypher
:Period
```

**Note:** No `:Concept` label - periods are specific temporal entities in your ontology.

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q1747689" | Wikidata ID (AUTHORITY) |
| `label` | string | text | "Roman Empire" | Period name |
| `unique_id` | string | pattern | "Q1747689_PERIOD_ROMAN_EMPIRE" | System ID |
| `start_year` | integer | year | -27 | Start year (from Wikidata P580) |
| `end_year` | integer | year | 476 | End year (from Wikidata P582) |
| `period_type` | string | enum | "dynasty" | Source: Wikidata P31 value label |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `description` | string | text | "Roman state from 27 BCE to 476 CE" | From Wikidata description |
| `wikidata_uri` | string | URI | "http://www.wikidata.org/entity/Q1747689" | Full Wikidata entity URI |
| `start_date_raw` | string | ISO 8601 | "-0027-01-16T00:00:00Z" | Raw Wikidata P580 value |
| `end_date_raw` | string | ISO 8601 | "+0476-09-04T00:00:00Z" | Raw Wikidata P582 value |
| `duration_years` | integer | years | 503 | Calculated: end_year - start_year |
| `location_qid` | string | Q[0-9]+ | "Q38" | Geographic location (Wikidata P276) |
| `location_label` | string | text | "Italy" | Location name |
| `country_qid` | string | Q[0-9]+ | "Q38" | Country (Wikidata P17) |
| `country_label` | string | text | "Italy" | Country name |
| `follows_qid` | string | Q[0-9]+ | "Q17167" | Previous period QID (Wikidata P155) |
| `follows_label` | string | text | "Roman Republic" | Previous period name |
| `followed_by_qid` | string | Q[0-9]+ | "Q12544" | Next period QID (Wikidata P156) |
| `followed_by_label` | string | text | "Byzantine Empire" | Next period name |
| `lcsh_id` | string | sh[0-9]+ | "sh85115021" | LCSH authority ID (Wikidata P244) |
| `getty_aat_id` | string | [0-9]+ | "300020533" | Getty AAT ID (Wikidata P1014) |

### PeriodO Integration Properties (Recommended)

**Note:** PeriodO provides canonical period definitions with fuzzy intervals and authority tracking. See `md/Reference/PERIODO_ARCHITECTURE_IMPACT_ANALYSIS.md` for full details.

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `periodo_id` | string | URI | `"periodo:def456"` | PeriodO identifier (canonical) |
| `periodo_uri` | string | URI | `"https://n2t.net/ark:/99152/p0def456"` | Full PeriodO URI |
| `startMin` | integer | year | -520 | Earliest plausible start (PeriodO 4-part interval) |
| `startMax` | integer | year | -500 | Latest plausible start (PeriodO 4-part interval) |
| `endMin` | integer | year | -30 | Earliest plausible end (PeriodO 4-part interval) |
| `endMax` | integer | year | -20 | Latest plausible end (PeriodO 4-part interval) |
| `authority_uri` | string | URI | `"https://n2t.net/ark:/99152/p0authority1"` | Authority that defined this period |
| `authority_name` | string | text | "Classical Period Definitions" | Authority name |
| `spatial_qid` | string | Q[0-9]+ | "Q220" | Place QID for spatial coverage |
| `spatial_label` | string | text | "Rome" | Place label |
| `spatial_broader_qid` | string | Q[0-9]+ | "Q38" | Broader place (e.g., Italy) |

**PeriodO 4-Part Interval Model:**
- **Core Interval** [startMax, endMin]: Period is definitely active (confidence = 1.0)
- **Onset Interval** [startMin, startMax]: Transition zone (confidence 0.0 → 1.0)
- **Decline Interval** [endMin, endMax]: Transition zone (confidence 1.0 → 0.0)

**Authority Multivocality:**
- Multiple Period nodes can have the same label but different authorities
- Link to Authority nodes via `DEFINED_BY` relationship
- Enables handling of conflicting period definitions

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `INSTANCE_OF` | Concept | 1 | Links to period type |

### Common Edges (Should Include)

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `SUB_PERIOD_OF` | Period | OUT | `(period)-[:SUB_PERIOD_OF]->(parent_period)` |
| `PRECEDED_BY` | Period | IN | `(period1)-[:PRECEDED_BY]->(period2)` |
| `FOLLOWED_BY` | Period | OUT | `(period1)-[:FOLLOWED_BY]->(period2)` |
| `LOCATED_IN` | Place | OUT | `(period)-[:LOCATED_IN]->(region)` |

### PeriodO Integration Edges (Recommended)

| Relationship | Target | Direction | Example | Notes |
|--------------|--------|-----------|---------|-------|
| `DEFINED_BY` | Authority | OUT | `(period)-[:DEFINED_BY]->(authority)` | Authority that defined this period |
| `LINKED_TO` | AuthoritySystem | OUT | `(period)-[:LINKED_TO]->(periodo:AuthoritySystem {name: "PeriodO"})` | Link to PeriodO system |
| `HAS_AUTHORITY_RECORD` | AuthorityRecord | OUT | `(period)-[:HAS_AUTHORITY_RECORD]->(record)` | PeriodO definition record |
| `COVERS` | TimeIndex | OUT | `(period)-[:COVERS]->(timeIndex)` | Space-Time Tree indexing (optimization) |

### Template

```cypher
CREATE (period:Period:Concept {
  // REQUIRED
  qid: "Q17167",
  label: "Roman Republic",
  unique_id: "Q17167_PERIOD_ROMAN_REPUBLIC",
  start_year: -509,
  end_year: -27,
  
  // OPTIONAL
  region: "Italy",
  description: "Period of Roman history from overthrow of monarchy to establishment of empire",
  parent_period_qid: "Q11772"
})

// REQUIRED EDGES
CREATE (period)-[:INSTANCE_OF]->(period_type:Concept {qid: "Q186081"})

// COMMON EDGES
CREATE (period)-[:SUB_PERIOD_OF]->(parent:Period)
CREATE (period)-[:PRECEDED_BY]->(prev_period:Period)
CREATE (period)-[:FOLLOWED_BY]->(next_period:Period)
```

---

## Concept Node Schema

### Node Labels
```cypher
:Concept
```

**Note:** Concept nodes are abstract/categorical entities (positions, types, classifications)

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q20056508" | Wikidata ID |
| `label` | string | text | "Roman consul" | Concept name |
| `unique_id` | string | pattern | "Q20056508_CONCEPT_CONSUL" | System ID |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `description` | string | text | "Chief magistrate of Roman Republic" | Description |
| `category` | string | text | "political position" | Classification |

### Template

```cypher
CREATE (concept:Concept {
  // REQUIRED
  qid: "Q20056508",
  label: "Roman consul",
  unique_id: "Q20056508_CONCEPT_CONSUL",
  
  // OPTIONAL
  description: "Chief magistrate of Roman Republic",
  category: "political position"
})
```

---

## Dynasty Node Schema

### Node Labels
```cypher
:Dynasty:Period
```

**Purpose:** Dynasties are DUAL ENTITIES - both temporal periods (when they ruled) and social groups (ruling families). Multiple labels allow temporal queries via :Period and genealogical queries via :Dynasty.

**CIDOC-CRM Alignment:**
- `:Period` → E4_Period (temporal entity)
- `:Dynasty` → E74_Group (social collective)

### Design Rationale

Dynasties have unique characteristics that distinguish them from regular periods:

1. **Temporal Aspect** (inherited from :Period)
   - Start/end dates of rule
   - Temporal containment relationships
   - Links to Year nodes

2. **Genealogical Aspect** (unique to :Dynasty)
   - Founded by specific person
   - Succession relationships
   - Links to rulers/agents
   - Family lineage tracking

3. **Political Authority**
   - Ruled specific territories
   - Had capitals/power centers
   - Succession crises/transitions

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q7209" | Wikidata ID (dynasty entity) |
| `label` | string | text | "Han dynasty" | Dynasty name |
| `unique_id` | string | pattern | "Q7209_DYNASTY_HAN" | System ID |
| `start_year` | integer | year | -206 | Start of rule |
| `end_year` | integer | year | 220 | End of rule |
| `lcsh_id` | string | sh[0-9]+ | "sh85058182" | LCSH authority ID |
| `lcsh_heading` | string | text | "Han dynasty, 202 B.C.-220 A.D." | LCSH heading |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `description` | string | text | "Chinese imperial dynasty that ruled from 206 BCE to 220 CE" | Full description |
| `aliases` | string[] | text | ["Former Han", "Western Han", "Eastern Han"] | Alternative names |
| `founder_qid` | string | Q[0-9]+ | "Q7192" | Wikidata ID of founder (Emperor Gaozu) |
| `founder_label` | string | text | "Emperor Gaozu of Han" | Founder name |
| `capital_qid` | string | Q[0-9]+ | "Q5826" | Capital city QID (Chang'an) |
| `capital_label` | string | text | "Chang'an" | Capital city name |
| `region_qid` | string | Q[0-9]+ | "Q148" | Territory QID (China) |
| `region_label` | string | text | "China" | Territory name |
| `duration_years` | integer | years | 426 | Total reign duration |
| `successor_dynasty_qid` | string | Q[0-9]+ | "Q7172812" | Next dynasty QID (Three Kingdoms) |
| `predecessor_dynasty_qid` | string | Q[0-9]+ | "Q7209" | Previous dynasty QID (Qin) |
| `number_of_rulers` | integer | count | 29 | Total emperors/rulers |
| `wikidata_dynasty_id` | string | P4261 value | "Q7209" | Wikidata dynasty property value |
| `lcc_code` | string | LCC | "DS747.9-748.1" | Library of Congress Classification |
| `fast_id` | string | fst[0-9]+ | "fst00951106" | FAST authority ID (if available) |
| `aat_id` | string | [0-9]+ | "300018525" | Getty AAT ID (if available) |
| `wikidata_url` | string | URL | "https://www.wikidata.org/wiki/Q7209" | Full Wikidata URL |

### Required Edges

| Relationship | Target | Cardinality | Example |
|--------------|--------|-------------|---------|
| `SUBJECT_OF` | Subject | 1+ | `(:Dynasty {label: "Han dynasty"})-[:SUBJECT_OF]->(:Subject {lcsh_id: "sh85058182"})` |
| `FOUNDED_BY` | Person | 1 | `(:Dynasty {label: "Han dynasty"})-[:FOUNDED_BY]->(:Person {qid: "Q7192", label: "Emperor Gaozu"})` |
| `RULED_DURING` | Period | 0+ | `(:Dynasty {label: "Han dynasty"})-[:RULED_DURING]->(:Period {label: "Classical China"})` |

### Optional Edges

| Relationship | Target | Cardinality | Example |
|--------------|--------|-------------|---------|
| `TEMPORALLY_CONTAINS` | Year | 0+ | `(:Dynasty)-[:TEMPORALLY_CONTAINS]->(:Year {year: 100})` |
| `PRECEDED_BY` | Dynasty | 0-1 | `(:Dynasty {label: "Han"})-[:PRECEDED_BY]->(:Dynasty {label: "Qin"})` |
| `FOLLOWED_BY` | Dynasty | 0-1 | `(:Dynasty {label: "Han"})-[:FOLLOWED_BY]->(:Dynasty {label: "Three Kingdoms"})` |
| `HAD_RULER` | Person | 1+ | `(:Dynasty {label: "Han"})-[:HAD_RULER]->(:Person {label: "Emperor Wu"})` |
| `HAD_CAPITAL` | Place | 1+ | `(:Dynasty {label: "Han"})-[:HAD_CAPITAL]->(:Place {qid: "Q5826", label: "Chang'an"})` |
| `RULED_REGION` | Place | 1+ | `(:Dynasty {label: "Han"})-[:RULED_REGION]->(:Place {qid: "Q148", label: "China"})` |
| `CONTEMPORARY_WITH` | Dynasty/Period | 0+ | `(:Dynasty {label: "Han"})-[:CONTEMPORARY_WITH]->(:Dynasty {label: "Parthian"})` |
| `APPLIES_TO_REGION` | Subject | 0+ | `(:Dynasty)-[:APPLIES_TO_REGION]->(:Subject {facet: "Geographic", label: "China"})` |

### Wikidata Integration

**Dynasty Detection:** Query Wikidata for entities where:
- `P31` (instance of) = `Q164950` (dynasty)
- Has `P580` (start time) and `P582` (end time)
- Has `P1365` (replaces) and `P1366` (replaced by) for succession
- Has `P112` (founded by) for founder
- Has `P36` (capital) for seat of power

**Example SPARQL:**
```sparql
SELECT ?dynasty ?dynastyLabel ?startTime ?endTime ?founder ?founderLabel ?capital ?capitalLabel WHERE {
  ?dynasty wdt:P31 wd:Q164950 .  # Instance of: dynasty
  ?dynasty wdt:P580 ?startTime .
  ?dynasty wdt:P582 ?endTime .
  OPTIONAL { ?dynasty wdt:P112 ?founder . }
  OPTIONAL { ?dynasty wdt:P36 ?capital . }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

### Genealogical Relationships

Dynasties connect to Person nodes representing rulers:

```cypher
// Create dynasty with founder
MERGE (d:Dynasty:Period {
  qid: "Q7209",
  label: "Han dynasty",
  start_year: -206,
  end_year: 220
})
MERGE (p:Person {qid: "Q7192", label: "Emperor Gaozu of Han"})
MERGE (d)-[:FOUNDED_BY]->(p)

// Add succession of rulers
MERGE (d)-[:HAD_RULER]->(p)
MERGE (r2:Person {qid: "Q7183", label: "Emperor Wu of Han"})
MERGE (d)-[:HAD_RULER]->(r2)
MERGE (r2)-[:SUCCEEDED]->(p)  // On Person nodes
```

### Period vs Dynasty Queries

**Query as Period (temporal operations):**
```cypher
// Find all dynasties ruling in 100 CE
MATCH (d:Period)
WHERE d:Dynasty  // Filter to dynasties only
  AND d.start_year <= 100 <= d.end_year
RETURN d.label, d.start_year, d.end_year
```

**Query as Dynasty (genealogical operations):**
```cypher
// Find all rulers of Han dynasty in succession order
MATCH (d:Dynasty {label: "Han dynasty"})-[:HAD_RULER]->(ruler:Person)
OPTIONAL MATCH succession = (ruler)-[:SUCCEEDED*]->(predecessor:Person)
RETURN ruler, succession
ORDER BY length(succession) DESC
```

**Query both aspects:**
```cypher
// Find dynasties that ruled same region in same century
MATCH (d1:Dynasty)-[:RULED_REGION]->(region:Place)
MATCH (d2:Dynasty)-[:RULED_REGION]->(region)
WHERE d1 <> d2
  AND d1.start_year / 100 = d2.start_year / 100  // Same century
RETURN d1.label, d2.label, region.label
```

### Example: Han Dynasty Complete

```cypher
CREATE (han:Dynasty:Period {
  qid: "Q7209",
  label: "Han dynasty",
  unique_id: "Q7209_DYNASTY_HAN",
  description: "Chinese imperial dynasty (206 BCE - 220 CE)",
  aliases: ["Former Han", "Western Han", "Eastern Han", "Han Empire"],
  
  // Temporal properties (from :Period)
  start_year: -206,
  end_year: 220,
  duration_years: 426,
  
  // Dynasty-specific properties
  founder_qid: "Q7192",
  founder_label: "Emperor Gaozu of Han",
  capital_qid: "Q5826",
  capital_label: "Chang'an",
  region_qid: "Q148",
  region_label: "China",
  number_of_rulers: 29,
  
  // Authority IDs
  lcsh_id: "sh85058182",
  lcsh_heading: "Han dynasty, 202 B.C.-220 A.D.",
  lcc_code: "DS747.9-748.1",
  aat_id: "300018525",
  wikidata_url: "https://www.wikidata.org/wiki/Q7209",
  
  // Succession
  predecessor_dynasty_qid: "Q7201",
  successor_dynasty_qid: "Q7172812"
})
```

### LCSH Integration for Dynasties

Dynasties have rich LCSH subject headings with temporal and geographic subdivisions:

```
sh85058182 - Han dynasty, 202 B.C.-220 A.D.
  ├─ sh85058183 - Han dynasty, 202 B.C.-220 A.D.--History
  ├─ sh85058184 - Han dynasty, 202 B.C.-220 A.D.--Politics and government
  └─ sh2008105558 - Han dynasty, 202 B.C.-220 A.D.--History--Military
```

Link to all relevant LCSH subjects:
```cypher
MATCH (d:Dynasty {qid: "Q7209"})
MATCH (s:Subject)
WHERE s.lcsh_heading STARTS WITH "Han dynasty"
MERGE (d)-[:SUBJECT_OF]->(s)
```

---

## Event Node Schema

### Node Labels
```cypher
:Event
```

**Purpose:** Represents historical events with support for event granularity and temporal containment hierarchies.

### Event Granularity Types

Events exist at different levels of abstraction:

| Granularity | Duration | Example | Containment |
|-------------|----------|---------|-------------|
| **atomic** | Hours/days | Battle of Stalingrad | Contained by composite events |
| **composite** | Weeks/months | Soviet Counteroffensive | Contains atomic events, contained by period events |
| **period_event** | Months/years | Operation Barbarossa | Contains composite events, occurs in PeriodO periods |

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q48314" | Wikidata ID |
| `label` | string | text | "Battle of Pharsalus" | Event name |
| `unique_id` | string | pattern | "Q48314_EVENT_PHARSALUS" | System ID |
| `granularity` | string | enum | "atomic" | atomic/composite/period_event |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `start_date` | string | ISO 8601 | "-0048-08-09" | Event start |
| `end_date` | string | ISO 8601 | "-0048-08-09" | Event end |
| `start_year` | integer | year | -48 | Year start |
| `end_year` | integer | year | -48 | Year end |
| `location_qid` | string | Q[0-9]+ | "Q187471" | Where it happened |
| `description` | string | text | "Decisive battle in Caesar's civil war" | Description |
| `participants` | string[] | Q[0-9]+ | ["Q1048", "Q170417"] | People involved |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `SUBJECT_OF` | Subject | 1+ | **Topical classification** (what event is about) |

### Temporal Edges (Event Granularity)

| Relationship | Target | Direction | Purpose | Example |
|--------------|--------|-----------|---------|---------|
| `PART_OF` | Event | OUT | Event containment hierarchy | `(battle)-[:PART_OF]->(campaign)` |
| `HAS_PART` | Event | IN | Inverse of PART_OF | `(campaign)-[:HAS_PART]->(battle)` |
| `OCCURRED_IN` | Period | OUT | Anchor to PeriodO period | `(event)-[:OCCURRED_IN]->(period)` |
| `OCCURRED_ON` | Year | OUT | Anchor to temporal backbone | `(event)-[:OCCURRED_ON {month: 8, day: 9}]->(year)` |

**Note:** Use `PART_OF` for event→event nesting, `OCCURRED_IN` for event→period anchoring.

### Common Edges

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `LOCATED_AT` | Place | OUT | `(event)-[:LOCATED_AT]->(place)` |
| `PARTICIPATED_IN` | Person | IN | `(person)-[:PARTICIPATED_IN {role: "commander"}]->(event)` |
| `CAUSED` | Event | OUT | `(event1)-[:CAUSED]->(event2)` |
| `RESULTED_IN` | Various | OUT | `(event)-[:RESULTED_IN]->(outcome)` |

### Template

```cypher
CREATE (event:Event {
  // REQUIRED
  qid: "Q48314",
  label: "Battle of Pharsalus",
  unique_id: "Q48314_EVENT_PHARSALUS",
  granularity: "atomic",
  
  // OPTIONAL
  start_date: "-0048-08-09",
  end_date: "-0048-08-09",
  start_year: -48,
  end_year: -48,
  location_qid: "Q187471",
  description: "Decisive battle in Caesar's civil war"
})

// REQUIRED EDGES - Topical classification
CREATE (event)-[:SUBJECT_OF]->(military_subject:Subject {
  lcsh_id: "sh85109289",
  label: "Military history"
})

// TEMPORAL EDGES - Event granularity
CREATE (event)-[:PART_OF]->(civil_war:Event {
  label: "Caesar's Civil War",
  granularity: "composite"
})
CREATE (event)-[:OCCURRED_IN]->(roman_republic:Period {periodo_id: "p0..."})
CREATE (event)-[:OCCURRED_ON {
  month: 8,
  day: 9,
  precision: "day",
  confidence: 0.95,
  perspective: "Modern historian"
}]->(year_48_bce:Year)

// COMMON EDGES
CREATE (event)-[:LOCATED_AT]->(pharsalus:Place {qid: "Q187471"})
CREATE (caesar:Person)-[:PARTICIPATED_IN {role: "commander"}]->(event)
CREATE (pompey:Person)-[:PARTICIPATED_IN {role: "opposing commander"}]->(event)
```

### Example: Stacked Event Hierarchy

```cypher
// 4-layer temporal stack
(battle:Event {label: "Battle of Stalingrad", granularity: "atomic"})
  ↓ PART_OF
(counteroffensive:Event {label: "Soviet Counteroffensive", granularity: "composite"})
  ↓ PART_OF
(barbarossa:Event {label: "Operation Barbarossa", granularity: "period_event"})
  ↓ OCCURRED_IN
(wwii:Period {label: "World War II", periodo_id: "p0..."})
```

---

## Institution Node Schema ⭐ NEW

### Node Labels
```cypher
:Institution
```

**Purpose:** Represents ongoing social systems, legal frameworks, and institutional structures (patronage, slavery, protection systems) that persist over time with rules, obligations, and participants.

**Critical Distinction:** Use Institution nodes for relationships that are:
- **Temporal** (have duration, start/end)
- **Rule-based** (defined by obligations, rights, prohibitions)
- **Multi-participant** (involve defined roles)
- **Institutional** (part of social/legal fabric)

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q..." | Wikidata ID (if available) |
| `label` | string | text | "Roman Patronage System" | Institution name |
| `unique_id` | string | pattern | "INST_PATRONAGE_ROMAN" | System ID |
| `institution_type` | string | enum | "patronage" | patronage/slavery/protection/legal |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `description` | string | text | "System of mutual obligations between patron and client" | Description |
| `start_date` | string | ISO 8601 | "-0753" | When institution began |
| `end_date` | string | ISO 8601 | "0476" | When institution ended |
| `geographic_scope` | string | text | "Roman Republic" | Where it operated |
| `legal_basis` | string | text | "Roman customary law" | Legal foundation |
| `obligations` | string[] | text | ["protection", "legal representation", "financial support"] | What institution requires |
| `rights` | string[] | text | ["loyalty", "political support", "military service"] | What institution grants |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `SUBJECT_OF` | Subject | 1+ | Topical classification |

### Common Edges

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `MEMBER_OF` | Person/Class | IN | `(person)-[:MEMBER_OF {role: "patron"}]->(institution)` |
| `GOVERNED_BY` | LegalRestriction | OUT | `(institution)-[:GOVERNED_BY]->(restriction)` |
| `VALID_DURING` | Period | OUT | `(institution)-[:VALID_DURING]->(period)` |
| `OPERATED_IN` | Place | OUT | `(institution)-[:OPERATED_IN]->(place)` |

### Template

```cypher
CREATE (institution:Institution {
  // REQUIRED
  qid: "Q...",
  label: "Roman Patronage System",
  unique_id: "INST_PATRONAGE_ROMAN",
  institution_type: "patronage",
  
  // OPTIONAL
  description: "System of mutual obligations between patron and client in Roman society",
  start_date: "-0753",
  end_date: "0476",
  geographic_scope: "Roman Republic and Empire",
  legal_basis: "Roman customary law (mos maiorum)",
  obligations: ["protection", "legal representation", "financial support"],
  rights: ["loyalty", "political support", "military service"]
})

// REQUIRED EDGES - Topical classification
CREATE (institution)-[:SUBJECT_OF]->(social_subject:Subject {
  lcsh_id: "sh...",
  label: "Social structure"
})

// COMMON EDGES
CREATE (patron:Person)-[:MEMBER_OF {
  role: "patron",
  start_date: "-0100",
  obligations: ["protection", "legal representation"]
}]->(institution)

CREATE (client:SocialClass {label: "Clients"})-[:MEMBER_OF {
  role: "client",
  obligations: ["loyalty", "political support"]
}]->(institution)

CREATE (institution)-[:VALID_DURING]->(roman_republic:Period)
CREATE (institution)-[:OPERATED_IN]->(rome:Place)
```

### Example: Complete Institution Subgraph

```cypher
// Patronage System
(:Institution {label: "Roman Patronage System", institution_type: "patronage"})
  ↓ MEMBER_OF (role: "patron")
(:Person {label: "Marcus Crassus"})
  ↓ MEMBER_OF (role: "client")
(:Person {label: "Julius Caesar"})  // Early in career

// Slavery Institution
(:Institution {label: "Roman Slavery System", institution_type: "slavery"})
  ↓ GOVERNED_BY
(:LegalRestriction {label: "Slave property rights"})
  ↓ CHANGED_BY
(:Event {label: "Manumission", type: "ManumissionEvent"})
  ↓ RESULTED_IN
(:Person {status: "libertus"})
```

### When to Use Institution vs Simple Edge

❌ **Simple Edge:**
```cypher
(patron)-[:PATRON_OF]->(client)  // Too simple, loses context
```

✅ **Institution Node:**
```cypher
(patron)-[:MEMBER_OF {role: "patron"}]->(patronage_system:Institution)
(client)-[:MEMBER_OF {role: "client"}]->(patronage_system:Institution)
```

**Why:** Captures obligations, duration, legal context, and social structure.

---

## LegalRestriction Node Schema ⭐ NEW

### Node Labels
```cypher
:LegalRestriction
```

**Purpose:** Represents legal rules, rights exclusions, class-based restrictions, and institutional requirements with temporal validity and enforcement.

**Use Cases:**
- Civil rights exclusions (Plebeians excluded from certain offices)
- Class-based restrictions (Clients have no voting rights)
- Legal requirements (Foreign residents must have patron)
- Property rights
- Status restrictions

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q..." | Wikidata ID (if available) |
| `label` | string | text | "Plebeian office exclusion" | Restriction name |
| `unique_id` | string | pattern | "LEGAL_PLEBEIAN_EXCLUSION" | System ID |
| `restriction_type` | string | enum | "exclusion" | exclusion/requirement/prohibition/right |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `description` | string | text | "Plebeians forbidden from holding certain offices" | Description |
| `start_date` | string | ISO 8601 | "-0509" | When rule took effect |
| `end_date` | string | ISO 8601 | "-0367" | When rule was repealed |
| `legal_basis` | string | text | "Roman law" | Source of authority |
| `penalty` | string | text | "Nullification of acts" | Consequence of violation |
| `applies_to` | string[] | text | ["Plebeians"] | Who is restricted |
| `scope` | string | text | "Consulship, Dictatorship" | What is restricted |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `APPLIES_TO` | SocialClass/Person | 1+ | Who is affected by restriction |

### Common Edges

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `ENFORCED_BY` | Institution/Org | OUT | `(restriction)-[:ENFORCED_BY]->(senate)` |
| `VALID_DURING` | Period | OUT | `(restriction)-[:VALID_DURING]->(period)` |
| `REPEALED_BY` | Event | OUT | `(restriction)-[:REPEALED_BY]->(lex_licinia)` |
| `CREATED_BY` | Event | IN | `(event)-[:CREATED]->(restriction)` |

### Template

```cypher
CREATE (restriction:LegalRestriction {
  // REQUIRED
  qid: "Q...",
  label: "Plebeian office exclusion",
  unique_id: "LEGAL_PLEBEIAN_EXCLUSION",
  restriction_type: "exclusion",
  
  // OPTIONAL
  description: "Plebeians forbidden from holding consulship and other curule offices",
  start_date: "-0509",
  end_date: "-0367",
  legal_basis: "Roman patrician privilege",
  penalty: "Acts performed by plebeian magistrate considered void",
  applies_to: ["Plebeians"],
  scope: "Consulship, Dictatorship, Censorship"
})

// REQUIRED EDGES
CREATE (restriction)-[:APPLIES_TO]->(plebeians:SocialClass {label: "Plebeians"})

// COMMON EDGES
CREATE (restriction)-[:ENFORCED_BY]->(senate:Organization {label: "Roman Senate"})
CREATE (restriction)-[:VALID_DURING]->(early_republic:Period)
CREATE (restriction)-[:REPEALED_BY]->(lex_licinia:Event {
  label: "Lex Licinia Sextia",
  date: "-0367"
})
```

### Example: Complete Legal System

```cypher
// Patronage requirement for foreigners
(:LegalRestriction {
  label: "Foreign resident patron requirement",
  restriction_type: "requirement"
})
  ↓ APPLIES_TO
(:SocialClass {label: "Resident Foreigners"})
  ↓ REQUIRES
(:Institution {label: "Patronage System"})

// Slave property status
(:LegalRestriction {
  label: "Slave property rights",
  restriction_type: "prohibition"
})
  ↓ APPLIES_TO
(:SocialClass {label: "Slaves"})
  ↓ PROHIBITS
("Property ownership", "Legal testimony", "Marriage rights")
```

---

## Claim Node Schema ⭐ NEW

### Node Labels
```cypher
:Claim
```

**Purpose:** Represents uncertain historical assertions, hypotheses, and perspective-dependent interpretations with confidence scores and provenance tracking.

**Use Cases:**
- Ethnic origin hypotheses (Clients possibly originated from conquered towns)
- Disputed dates (Battle may have occurred in 216 or 217 BCE)
- Conflicting accounts (Different historians give different casualty figures)
- Archaeological interpretations
- Scholarly debates

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q..." | Wikidata ID (if applicable) |
| `label` | string | text | "Client ethnic origin hypothesis" | Claim name |
| `unique_id` | string | pattern | "CLAIM_CLIENT_ORIGIN_001" | System ID |
| `claim_type` | string | enum | "origin" | origin/date/causation/interpretation |
| `confidence` | float | 0.0-1.0 | 0.65 | Confidence score (posterior probability) |
| `prior_probability` | float | 0.0-1.0 | 0.50 | Prior belief before evidence |
| `posterior_probability` | float | 0.0-1.0 | 0.65 | Updated belief after evidence (same as confidence) |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `claim_text` | string | text | "Clients likely descended from conquered Latin populations" | The actual claim |
| `evidence` | string[] | text | ["Archaeological findings", "Onomastic patterns"] | Supporting evidence |
| `evidence_weight` | float | 0.0-1.0 | 0.75 | Strength of evidence (Bayesian likelihood ratio) |
| `source` | string | text | "Modern scholarship (Cornell 1995)" | Who made the claim |
| `perspective` | string | text | "Modern historian" | Scholarly perspective |
| `alternative_claims` | string[] | text | ["Indigenous Roman origin", "Foreign immigrant origin"] | Competing hypotheses |
| `date_proposed` | string | ISO 8601 | "1995" | When claim was made |
| `last_updated` | string | ISO 8601 | "2019-03-15" | When probability was last updated |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `CLAIMS` | Various | 1+ | What entity the claim is about |

### Common Edges

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `SOURCE` | Person/Work | OUT | `(claim)-[:SOURCE]->(historian)` |
| `CONTRADICTS` | Claim | OUT | `(claim1)-[:CONTRADICTS]->(claim2)` |
| `SUPPORTS` | Claim | OUT | `(claim1)-[:SUPPORTS]->(claim2)` |
| `BASED_ON` | Evidence | OUT | `(claim)-[:BASED_ON]->(archaeological_finding)` |

### Template

```cypher
CREATE (claim:Claim {
  // REQUIRED
  qid: "Q...",
  label: "Client ethnic origin hypothesis",
  unique_id: "CLAIM_CLIENT_ORIGIN_001",
  claim_type: "origin",
  confidence: 0.65,
  prior_probability: 0.50,
  posterior_probability: 0.65,
  
  // OPTIONAL
  claim_text: "Roman clients likely descended from conquered Latin populations incorporated into Roman society",
  evidence: [
    "Onomastic patterns showing Latin roots",
    "Archaeological evidence of Latin settlements",
    "Literary references to conquered towns"
  ],
  evidence_weight: 0.75,
  source: "Cornell, T.J. (1995). The Beginnings of Rome",
  perspective: "Modern historian - social history",
  alternative_claims: [
    "Clients were indigenous Romans of lower status",
    "Clients were foreign immigrants seeking protection"
  ],
  date_proposed: "1995",
  last_updated: "2019-03-15"
})

// REQUIRED EDGES
CREATE (claim)-[:CLAIMS]->(clients:SocialClass {label: "Clients"})

// COMMON EDGES
CREATE (claim)-[:SOURCE]->(cornell:Person {label: "T.J. Cornell"})
CREATE (claim)-[:BASED_ON]->(archaeology:Evidence {type: "archaeological"})

// Alternative claim
CREATE (alt_claim:Claim {
  label: "Client indigenous origin",
  confidence: 0.35,
  perspective: "Traditional view"
})
CREATE (claim)-[:CONTRADICTS]->(alt_claim)
```

### Example: Multi-Perspective Claims

```cypher
// Livy's account
(:Claim {
  label: "Battle casualties (Livy)",
  claim_text: "50,000 Romans killed at Cannae",
  confidence: 0.4,
  source: "Livy, Ab Urbe Condita",
  perspective: "Ancient Roman historian"
})

// Polybius's account
(:Claim {
  label: "Battle casualties (Polybius)",
  claim_text: "70,000 Romans killed at Cannae",
  confidence: 0.6,
  source: "Polybius, Histories",
  perspective: "Contemporary Greek historian"
})
  ↓ CONTRADICTS
(:Claim {label: "Battle casualties (Livy)"})

// Modern synthesis
(:Claim {
  label: "Battle casualties (modern estimate)",
  claim_text: "50,000-70,000 Romans killed at Cannae",
  confidence: 0.85,
  source: "Modern military historians",
  perspective: "Modern consensus"
})
```

---

## Organization Node Schema

### Node Labels
```cypher
:Organization
```

**Note:** No `:Concept` label - organizations are specific institutional entities.

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `qid` | string | Q[0-9]+ | "Q842606" | Wikidata ID |
| `label` | string | text | "Roman Senate" | Organization name |
| `unique_id` | string | pattern | "Q842606_ORG_ROMAN_SENATE" | System ID |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `description` | string | text | "Legislative body of Roman Republic" | Full description |
| `aliases` | string[] | text | ["Senate", "Roman Senate", "Senatus"] | Alternative names |
| `founded_date` | string | ISO 8601 | "-0509" | When established (ISO 8601) |
| `founded_year` | integer | year | -509 | Founding year (for queries) |
| `dissolved_date` | string | ISO 8601 | "0603" | When dissolved (ISO 8601) |
| `dissolved_year` | integer | year | 603 | Dissolution year (for queries) |
| `headquarters_qid` | string | Q[0-9]+ | "Q220" | Headquarters location QID |
| `headquarters_label` | string | text | "Rome" | Headquarters location name |
| `organization_type` | string | enum | "legislative" | legislative/executive/judicial/military/religious/commercial |
| `scope` | string | enum | "national" | local/regional/national/international |
| `parent_org_qid` | string | Q[0-9]+ | "Q1747689" | Parent organization QID |
| `member_count` | integer | count | 300 | Number of members (historical or current) |
| `wikidata_url` | string | URL | "https://www.wikidata.org/wiki/Q842606" | Full Wikidata URL |
| `viaf_id` | string | pattern | "144904638" | VIAF authority ID |

### Common Edges

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `HAS_MEMBER` | Person | IN | `(person)-[:MEMBER_OF]->(org)` |
| `LOCATED_IN` | Place | OUT | `(org)-[:LOCATED_IN]->(place)` |

---

## Year Node Schema

### Node Labels
```cypher
:Year
```

**Note:** No `:Concept` label - years are temporal backbone nodes, not abstract concepts.

**Note:** Year nodes form the temporal backbone

### Required Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `year_value` | integer | year | -49 | Year number (negative = BCE) |
| `label` | string | text | "49 BCE" | Human-readable year |
| `unique_id` | string | pattern | "YEAR_-49" | System ID |
| `iso8601_start` | string | ISO 8601 | "-0049-01-01" | Year start date |
| `iso8601_end` | string | ISO 8601 | "-0049-12-31" | Year end date |
| `temporal_backbone` | boolean | true/false | true | Part of temporal backbone |

### Optional Properties

| Property | Type | Format | Example | Notes |
|----------|------|--------|---------|-------|
| `century` | integer | century | -1 | Century number (negative for BCE) |
| `decade` | integer | decade | -50 | Decade number |
| `millennium` | integer | millennium | -1 | Millennium number |
| `era` | string | enum | "BCE" | BCE/CE/BP (Before Present) |
| `year_type` | string | enum | "gregorian" | gregorian/julian/proleptic_gregorian |
| `leap_year` | boolean | true/false | false | Whether this is a leap year |
| `description` | string | text | "Year of Caesar's crossing of the Rubicon" | Notable events/description |

### Required Edges

| Relationship | Target | Cardinality | Notes |
|--------------|--------|-------------|-------|
| `FOLLOWED_BY` | Year | 1 | Next year in sequence |
| `PRECEDED_BY` | Year | 1 | Previous year in sequence |

### Common Edges

| Relationship | Target | Direction | Example |
|--------------|--------|-----------|---------|
| `PART_OF` | Period | OUT | `(year)-[:PART_OF]->(period)` |

### Template

```cypher
CREATE (year:Year:Concept {
  // REQUIRED
  year_value: -49,
  label: "49 BCE",
  unique_id: "YEAR_-49",
  iso8601_start: "-0049-01-01",
  iso8601_end: "-0049-12-31",
  temporal_backbone: true
})

// REQUIRED EDGES
CREATE (year)-[:FOLLOWED_BY]->(next_year:Year {year_value: -48})
CREATE (year)-[:PRECEDED_BY]->(prev_year:Year {year_value: -50})

// COMMON EDGES
CREATE (year)-[:PART_OF]->(period:Period)
```

---

## Validation Rules

### For Any Node

1. ✅ Must have `qid`, `label`, `unique_id`
2. ✅ QIDs must match format `Q[0-9]+`
3. ✅ Must have at least one edge (no orphan nodes)
4. ✅ Dates must be ISO 8601 format

### For Edges

1. ✅ Relationship type must be from canonical list
2. ✅ Must have source and target nodes
3. ✅ Should have temporal properties (date/start/end) if applicable
4. ✅ Should have role/type properties if applicable

---

## Usage in Agent Prompt

Add this section to test subject agent:

```markdown
## Node Type Requirements

When generating subgraphs, follow these schemas:

### Person Nodes
- MUST have: qid, label, unique_id
- SHOULD have: birth_date, death_date, birth_place_qid, death_place_qid
- MUST connect: INSTANCE_OF → Concept
- SHOULD connect: BORN_IN → Place, DIED_IN → Place, HELD_POSITION → Position

### Event Nodes
- MUST have: qid, label, unique_id, date_iso8601
- SHOULD have: location_qid, goal_type, trigger_type, action_type, result_type
- MUST connect: INSTANCE_OF → Concept, POINT_IN_TIME → Year
- SHOULD connect: LOCATED_IN → Place, DURING → Period, PARTICIPATED_IN ← Person

### Place Nodes
- MUST have: qid, label, unique_id
- SHOULD have: coordinates, stability, feature_type
- MUST connect: INSTANCE_OF → Concept
- SHOULD connect: LOCATED_IN → Place (larger region), BORDERS ← Place

[Include full schemas from NODE_TYPE_SCHEMAS.md]
```

---

## Next Steps

1. **Add to agent training** - Include NODE_TYPE_SCHEMAS.md in knowledge files
2. **Validate responses** - Check that generated nodes match schemas
3. **Create validators** - Build tools to verify schema compliance
4. **Extend schemas** - Add more node types as needed (MilitaryUnit, Document, etc.)

---

**Purpose:** Standardize node structure across all subgraph generation  
**Benefit:** Complete, consistent, importable subgraphs  
**Next:** Add schema validation to extraction pipeline

