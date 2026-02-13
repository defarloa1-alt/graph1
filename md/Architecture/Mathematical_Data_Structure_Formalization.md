# Mathematical Formalization of Chrystallum Data Structure

## Overview

Canonical mathematical representation of the Chrystallum knowledge graph data structure, including entities, relationships, action structures, and unique identifiers.

---

## 1. Entity Structure

### Entity Definition

An entity (vertex) $v$ is a tuple:

$$v = (id, unique\_id, label, type, qid, P, metadata)$$

**Note**: In the graph $KG$, entities become vertices: $v \in V$.

Where:

- $id \in QID \cup C\_ID$: Base identifier (QID from Wikidata or Chrystallum ID)
- $unique\_id = f(id, type, label, P)$: Composite unique identifier
- $label \in \Sigma^*$: Human-readable label (string)
- $type \in T$: Entity type from schema (e.g., Human, Place, Organization)
- $qid \in QID \cup \{\emptyset\}$: Wikidata QID (optional)
- $P = \{p_1, p_2, \ldots, p_n\}$: Set of property-value pairs
- $metadata = \{test\_case, confidence, temporal, \ldots\}$: Additional metadata
- $extensions$: Extended properties (see Section 14)

### Unique ID Function

$$unique\_id = f(id, type, label, P) = H(id \parallel type \parallel label \parallel sorted(P))$$

Where:
- $H$: Hash function (e.g., MD5, SHA-256)
- $\parallel$: String concatenation
- $sorted(P)$: Properties sorted by key

**Alternative (readable format for testing):**
$$unique\_id = id \parallel "\_" \parallel type \parallel "\_" \parallel normalize(label)$$

---

## 2. Relationship Structure

### Basic Relationship

A relationship $R$ is a tuple:

$$R = (source, target, rel\_type, properties)$$

Where:
- $source \in E$: Source entity
- $target \in E$: Target entity  
- $rel\_type \in REL$: Relationship type from schema
- $properties = \{prop_1, prop_2, \ldots, prop_n\}$: Relationship properties

### Relationship with Action Structure

A relationship with action structure $R_a$ extends the basic relationship:

$$R_a = (source, target, rel\_type, properties, action\_structure)$$

Where $action\_structure$ is defined as:

---

## 3. Action Structure (Mathematical Definition)

### Action Structure Tuple

An action structure $A$ is a 5-tuple:

$$A = (G, T, Act, Res, N)$$

Where:

**Goal $G$:**
$$G = (goal\_text, goal\_type)$$
- $goal\_text \in \Sigma^*$: Natural language description of goal
- $goal\_type \in GT$: Goal type code (e.g., POL, PERS, MIL)
  - $GT = \{POL, PERS, MIL, ECON, CONST, MORAL, CULT, RELIG, DIPL, SURV\}$

**Trigger $T$:**
$$T = (trigger\_text, trigger\_type)$$
- $trigger\_text \in \Sigma^*$: Natural language description of trigger
- $trigger\_type \in TT$: Trigger type code (e.g., CIRCUM, MORAL_TRIGGER, EMOT)
  - $TT = \{CIRCUM, MORAL\_TRIGGER, EMOT, POL\_TRIGGER, PERS\_TRIGGER, EXT\_THREAT, INT\_PRESS, LEGAL, AMB, OPPORT\}$

**Action $Act$:**
$$Act = (action\_type, action\_description)$$
- $action\_type \in AT$: Action type code (e.g., REVOL, MIL_ACT, CRIME)
  - $AT = \{REVOL, MIL\_ACT, CRIME, DIPL\_ACT, CONST\_INNOV, ECON\_ACT, LEGAL\_ACT, SOC\_ACT, RELIG\_ACT, PERS\_ACT, ADMIN, CAUSAL, TYRANNY, DEFENSIVE, OFFENSIVE\}$
- $action\_description \in \Sigma^*$: Natural language description

**Result $Res$:**
$$Res = (result\_text, result\_type)$$
- $result\_text \in \Sigma^*$: Natural language description of result
- $result\_type \in RT$: Result type code (e.g., POL_TRANS, INST_CREATE, TRAGIC)
  - $RT = \{POL\_TRANS, INST\_CREATE, CONQUEST, DEFEAT, ALLIANCE, TRAGIC, SUCCESS, FAILURE, STABILITY, INSTABILITY, LEGAL\_OUTCOME, CULT\_CHANGE, PERS\_OUTCOME, ECON\_OUTCOME, SOC\_CHANGE, RELIG\_OUTCOME, MORAL\_VICT, MORAL\_FAIL, NEUTRAL\}$

**Narrative $N$:**
$$N = (narrative\_summary, source\_text, source, confidence, temporal, spatial)$$
- $narrative\_summary \in \Sigma^*$: Human-readable narrative (1-3 sentences)
- $source\_text \in \Sigma^*$: Exact excerpt from source
- $source \in URL \cup Citation$: Source attribution
- $confidence \in [0, 1]$: Confidence score
- $temporal \in TimePeriod \cup \{\emptyset\}$: Temporal context
- $spatial \in Place \cup \{\emptyset\}$: Spatial context

### Complete Action Structure

$$A = \{(goal\_text, goal\_type), (trigger\_text, trigger\_type), (action\_type, action\_description), (result\_text, result\_type), N\}$$

---

## 4. Relationship with Action Structure (Complete)

### Relationship Structure

A relationship $e$ (which becomes an edge in the graph) is defined as:

$$e = (v_s, v_t, rel\_type, A, P_{standard})$$

Where:
- $v_s \in V$: Source vertex (entity)
- $v_t \in V$: Target vertex (entity)
- $rel\_type \in REL$: Relationship type
- $A$: Action structure (as defined in Section 3)
- $P_{standard} = \{temporal, location, confidence, created\_by\_agent, \ldots\}$: Standard properties

**Note**: When this relationship is added to the graph, it becomes edge $e \in E$ in $KG = (V, E, L_V, L_E, P_V, P_E)$.

---

## 5. Knowledge Graph Structure

### Graph Definition

A Chrystallum knowledge graph $KG$ is a directed labeled multigraph:

$$KG = (V, E, L_V, L_E, P_V, P_E)$$

Where:
- **$V$**: Set of vertices (entities) where each vertex $v \in V$ is an entity structure:
  $$V = \{v_i : v_i = E_i = (id_i, unique\_id_i, label_i, type_i, qid_i, P_i, metadata_i)\}$$
  
- **$E$**: Set of edges (relationships) where each edge $e \in E$ is a relationship structure:
  $$E = \{e_j : e_j = (v_{s_j}, v_{t_j}, rel\_type_j, A_j, P_{standard_j})\}$$
  where $v_{s_j}, v_{t_j} \in V$ and $A_j$ is the action structure (Section 3)
  
- **$L_V: V \to T$**: Vertex labeling function (maps entities to types)
  - $L_V(v) = v.type$ for entity $v$
  
- **$L_E: E \to REL$**: Edge labeling function (maps relationships to types)
  - $L_E(e) = e.rel\_type$ for relationship $e$
  
- **$P_V: V \to Properties$**: Vertex property function
  - $P_V(v) = \{v.id, v.unique\_id, v.label, v.type, v.qid, v.P, v.metadata\}$
  
- **$P_E: E \to Properties$**: Edge property function (includes action structure)
  - $P_E(e) = \{e.rel\_type, e.A, e.P_{standard}\}$
  - Where $e.A = (G, T, Act, Res, N)$ is the action structure

### Relationship as Edge (Formal)

Each edge $e \in E$ is defined as:

$$e = (v_s, v_t, rel\_type, A, P_{standard})$$

Where:
- $v_s \in V$: Source vertex (entity from Section 1)
- $v_t \in V$: Target vertex (entity from Section 1)
- $rel\_type \in REL$: Relationship type
- $A = (G, T, Act, Res, N)$: Action structure (from Section 3)
- $P_{standard} = \{temporal, location, confidence, created\_by\_agent, \ldots\}$: Standard properties

**Edge Properties Include Action Structure:**
$$P_E(e) = \{rel\_type\} \cup A \cup P_{standard} = \{rel\_type, G, T, Act, Res, N, P_{standard}\}$$

**Key Property**: The action structure $A$ is **embedded in** the edge properties:
$$A \subseteq P_E(e) \text{ for all } e \in E$$

This ensures that $A$, $G$, $T$, $Act$, $Res$, and $N$ are all **part of the graph structure** $KG$ and properly counted.

---

## 6. Unique ID Generation (Formal)

### Composite Unique ID

$$unique\_id: V \to ID$$

$$unique\_id(v) = \begin{cases}
H(v.id \parallel v.type \parallel v.label \parallel sorted(v.P)) & \text{if deterministic} \\
v.id \parallel "\_" \parallel type\_code(v.type) \parallel "\_" \parallel normalize(v.label) & \text{if readable}
\end{cases}$$

Where:
- $H: \Sigma^* \to \{0,1\}^n$: Cryptographic hash function
- $type\_code$: Abbreviated type code (e.g., GOV, HUM, CITY)
- $normalize: \Sigma^* \to \Sigma^*$: Label normalization function

### Deduplication Property

For entities $v_1, v_2$:

$$unique\_id(v_1) = unique\_id(v_2) \iff id_1 = id_2 \land type_1 = type_2 \land label_1 = label_2 \land P_1 = P_2$$

---

## 7. Triple with Action Structure (4-Tuple)

### Standard Triple

$$T = (s, r, o)$$

Where $s, o \in V$ (entities/vertices) and $r \in REL$ (relationship type).

### Extended Triple with Action Structure

$$T_a = (s, r, o, A)$$

Where:
- $s$: Subject entity
- $r$: Relationship type
- $o$: Object entity
- $A$: Action structure (5-tuple as defined above)

### Triple with Narrative (4th Component)

$$T_n = (s, r, o, N)$$

Where $N$ is the narrative summary (as defined in action structure).

### Complete Triple (Subject → Relationship → Object → Narrative/Action)

$$T_{complete} = (v_s, rel\_type, v_t, A, P_{metadata})$$

Where:
- $v_s \in V$: Subject entity (vertex)
- $v_t \in V$: Object entity (vertex)
- $rel\_type \in REL$: Relationship type
- $A = (G, T, Act, Res, N)$: Action structure (the 4th component)
- $P_{metadata}$: Additional metadata

This is the **4-tuple format** we're using. When instantiated, this becomes edge $e \in E$ in the graph $KG$.

---

## 8. Vocabulary Sets (Formal)

### Goal Types

$$GT = \{POL, PERS, MIL, ECON, CONST, MORAL, CULT, RELIG, DIPL, SURV\}$$

### Trigger Types

$$TT = \{CIRCUM, MORAL\_TRIGGER, EMOT, POL\_TRIGGER, PERS\_TRIGGER, EXT\_THREAT, INT\_PRESS, LEGAL, AMB, OPPORT\}$$

### Action Types

$$AT = \{REVOL, MIL\_ACT, CRIME, DIPL\_ACT, CONST\_INNOV, ECON\_ACT, LEGAL\_ACT, SOC\_ACT, RELIG\_ACT, PERS\_ACT, ADMIN, CAUSAL, TYRANNY, DEFENSIVE, OFFENSIVE\}$$

### Result Types

$$RT = \{POL\_TRANS, INST\_CREATE, CONQUEST, DEFEAT, ALLIANCE, TRAGIC, SUCCESS, FAILURE, STABILITY, INSTABILITY, LEGAL\_OUTCOME, CULT\_CHANGE, PERS\_OUTCOME, ECON\_OUTCOME, SOC\_CHANGE, RELIG\_OUTCOME, MORAL\_VICT, MORAL\_FAIL, NEUTRAL\}$$

---

## 9. Relationship Type Schema

### Relationship Type Definition

A relationship type $RT$ is a tuple:

$$RT = (name, category, directionality, wikidata\_prop, parent, specificity)$$

Where:
- $name \in REL$: Relationship type name
- $category \in CAT$: Category (e.g., Political, Military, Diplomatic)
- $directionality \in \{forward, inverse, symmetric, unidirectional\}$
- $wikidata\_prop \in P\_ID \cup \{\emptyset\}$: Wikidata property ID
- $parent \in REL \cup \{\emptyset\}$: Parent relationship (for hierarchy)
- $specificity \in \{1, 2, 3\}$: Specificity level

---

## 10. Complete Data Structure (JSON Schema Equivalent)

### Entity Schema

$$\mathcal{E} = \{
  id: String,
  unique\_id: String,
  label: String,
  type: T,
  qid: String | null,
  properties: P,
  metadata: M
\}$$

### Relationship Schema (with Action Structure)

$$\mathcal{R} = \{
  source: \mathcal{E},
  target: \mathcal{E},
  rel\_type: REL,
  action\_structure: \{
    goal: \{text: String, type: GT\},
    trigger: \{text: String, type: TT\},
    action: \{type: AT, description: String\},
    result: \{text: String, type: RT\},
    narrative: \{
      summary: String,
      source\_text: String,
      source: String,
      confidence: [0,1],
      temporal: String | null,
      spatial: String | null
    \}
  \},
  properties: P_{standard}
\}$$

---

## 11. Example (Monarchy to Republic)

### Entity Example

$$E_{republic} = (
  id = "Q17193",
  unique\_id = "Q17193\_GOV\_ROMANREPUBLIC",
  label = "Roman Republic",
  type = "Government",
  qid = "Q17193",
  P = \{start\_date: "509 BC"\},
  metadata = \{test\_case: "monarchy\_to\_republic"\}
)$$

### Relationship with Action Structure Example

$$R = (
  source = E_{brutus},
  target = E_{rebellion},
  rel\_type = "PARTICIPATED\_IN",
  A = \{
    G = ("Overthrow monarchy", POL),
    T = ("Rape of Lucretia", MORAL\_TRIGGER),
    Act = (REVOL, "Brutus rallied the people"),
    Res = ("Republic established", POL\_TRANS),
    N = ("Full narrative...", source, 0.95, "509 BC", "Rome")
  \},
  P_{standard} = \{temporal: "509 BC", confidence: 0.95\}
)$$

---

## 12. Query Patterns (Mathematical)

### Basic Relationship Query

$$\sigma_{rel\_type=r}(E \bowtie R \bowtie E)$$

Where $\bowtie$ is join operation.

### Query with Action Structure Filter

$$\sigma_{rel\_type=r \land goal\_type=gt \land result\_type=rt}(E \bowtie R_a \bowtie E)$$

### Path Query (Causal Chain)

$$path = E_1 \xrightarrow{r_1} E_2 \xrightarrow{r_2} E_3 \xrightarrow{r_3} \ldots \xrightarrow{r_n} E_{n+1}$$

Where relationships form a causal sequence:
$$\forall i, result\_type(r_i) = trigger\_type(r_{i+1})$$

---

## 13. Complete Unified Definition

### How Entities, Relationships, and Action Structure are Counted in KG

**Key Clarification**: All components are properly incorporated into $KG$:

**Mapping Structure:**
- **Entities** (defined in Section 1 as $E$) → Become **Vertices $V$** in the graph
- **Relationships** (defined in Section 4) → Become **Edges $E$** in the graph  
- **Action Structure** (defined in Section 3 as $A$) → Embedded in **Edge Properties $P_E$**

**Complete Count:**

1. **Entities**: Every entity $E_i$ becomes vertex $v_i \in V$
   - Total entities = $|V| = n$

2. **Relationships**: Every relationship becomes edge $e_j \in E$
   - Total relationships = $|E| = m$

3. **Action Structures**: Every action structure $A_j$ is embedded in edge properties
   - Total action structures = $|E| = m$ (one per relationship/edge)
   - Action structure properties are in $P_E(e_j)$ for each $e_j \in E$

**Therefore in $KG = (V, E, L_V, L_E, P_V, P_E)$:**
- All entities are counted as vertices: $V$
- All relationships are counted as edges: $E$
- All action structures are counted as edge properties: $A_j \in P_E(e_j)$ for all $e_j \in E$

**Nothing is missing—all components are fully incorporated and counted in the graph structure.**

---

## 14. Entity Property Extensions

### Extended Entity Structure

Entities may have additional extension properties based on type:

$$v = (id, unique\_id, label, type, qid, P, metadata, extensions)$$

Where $extensions$ is a conditional set based on entity type:

### Place Extensions

For entities where $v.type \in \{Place, City, Country, Region, \ldots\}$:

$$extensions_{place} = \{geo\_coordinates, pleiades\_id, pleiades\_link, google\_earth\_link, geo\_json\}$$

Where:
- $geo\_coordinates = (latitude, longitude, altitude, precision)$
- $pleiades\_id \in Pleiades\_ID$: Pleiades gazetteer identifier
- $pleiades\_link \in URL$: Link to Pleiades entry
- $google\_earth\_link \in URL$: Google Earth link/coordinates

### Temporal Extensions

For entities with temporal aspects:

$$extensions_{temporal} = \{start\_date, end\_date, date\_precision, temporal\_uncertainty\}$$

Where:
- $start\_date \in Date \cup \{\emptyset\}$
- $end\_date \in Date \cup \{\emptyset\}$ (NEW)
- $date\_precision \in \{year, month, day, approximate\}$
- $temporal\_uncertainty \in \{true, false\}$

### Backbone Alignment Extensions

For all entities (recommended):

$$extensions_{backbone} = \{backbone\_fast, backbone\_lcc, backbone\_lcsh, backbone\_marc\}$$

Where:
- $backbone\_fast \in FAST\_ID$: FAST (Faceted Application of Subject Terminology) ID
- $backbone\_lcc \in LCC\_Code$: Library of Congress Classification code
- $backbone\_lcsh \in LCSH\_Terms^*$: Library of Congress Subject Headings (list)
- $backbone\_marc \in MARC\_ID$: MARC authority record ID

### Person Extensions

For entities where $v.type = Human$:

$$extensions_{person} = \{image, related\_works, online\_text\}$$

Where:

**Image:**
$$image = \{image\_url, image\_source, image\_license, wikimedia\_image\}$$

**Related Works:**
$$related\_works = \{related\_fiction, related\_art, related\_nonfiction\}$$

Where each is a list of work references:
$$work\_ref = (title, author, work\_type, qid, url)$$

**Online Text:**
$$online\_text = \{online\_text\_available, online\_text\_sources\}$$

Where:
- $online\_text\_available \in \{true, false\}$
- $online\_text\_sources = [source_1, source_2, \ldots]$ where each source is:
  $$source = (source\_name, url, format, language)$$

### Complete Extension Set

For entity $v$:

$$extensions(v) = \begin{cases}
extensions_{backbone} \cup extensions_{temporal} \cup extensions_{place} & \text{if } v.type \in Places \\
extensions_{backbone} \cup extensions_{temporal} \cup extensions_{person} & \text{if } v.type = Human \\
extensions_{backbone} \cup extensions_{temporal} & \text{if } v.type \in Temporal\_Entities \\
extensions_{backbone} & \text{otherwise}
\end{cases}$$

This ensures all entities have backbone alignment, and type-specific extensions are applied conditionally.

### Knowledge Graph (Unified)

A Chrystallum knowledge graph is defined as:

$$KG = (V, E, L_V, L_E, P_V, P_E)$$

Where:

**Vertices (Entities):**
$$V = \{v_i : v_i = (id_i, unique\_id_i, label_i, type_i, qid_i, P_i, metadata_i)\}$$

Each vertex $v \in V$ is an entity structure.

**Edges (Relationships with Action Structure):**
$$E = \{e_j : e_j = (v_{s_j}, v_{t_j}, rel\_type_j, A_j, P_{standard_j})\}$$

Where:
- $v_{s_j}, v_{t_j} \in V$ (source and target entities/vertices)
- $rel\_type_j \in REL$ (relationship type)
- $A_j = (G_j, T_j, Act_j, Res_j, N_j)$ (action structure embedded in edge)
- $P_{standard_j}$ (standard relationship properties)

**Labeling Functions:**
- $L_V: V \to T$ where $L_V(v) = v.type$
- $L_E: E \to REL$ where $L_E(e) = e.rel\_type$

**Property Functions:**
- $P_V: V \to Properties$ maps each vertex to its entity properties
- $P_E: E \to Properties$ maps each edge to its relationship properties, where:
  $$P_E(e) = \{rel\_type, A, P_{standard}\} = \{rel\_type, (G, T, Act, Res, N), P_{standard}\}$$

### Key Property: Action Structure is Embedded

For each edge $e \in E$:
$$A \in P_E(e)$$

This means:
- **Action structure $A$ is part of the edge properties**
- **Goal $G$, Trigger $T$, Action $Act$, Result $Res$, and Narrative $N$ are all in $P_E(e)$**
- **Everything is properly nested within the graph $KG$**

### Summary

The complete Chrystallum data structure is formally defined as:

1. **Entities (Vertices)**: $v \in V$ where $v = (id, unique\_id, label, type, qid, P, metadata)$
2. **Relationships (Edges)**: $e \in E$ where $e = (v_s, v_t, rel\_type, A, P_{standard})$ 
3. **Action Structure**: $A = (G, T, Act, Res, N)$ **embedded in** $P_E(e)$ for each $e \in E$
4. **Knowledge Graph**: $KG = (V, E, L_V, L_E, P_V, P_E)$ where:
   - $V$ contains all entities
   - $E$ contains all relationships (with embedded action structure)
   - $A \subseteq P_E(e)$ for all $e \in E$

**Key Point**: 
- **Entities** (Section 1): Each entity $E$ becomes a vertex $v \in V$ in the graph
- **Relationships** (Section 4): Each relationship $r$ becomes an edge $e \in E$ in the graph
- **Action Structure** (Section 3): Each action structure $A$ is embedded in the edge properties $P_E(e)$

**Mapping:**
- $E$ (entity) → $v \in V$ (vertex)
- $r$ (relationship) → $e \in E$ (edge)
- $A$ (action structure) → $A \in P_E(e)$ (edge property)

All components are **fully counted and incorporated** in $KG = (V, E, L_V, L_E, P_V, P_E)$.

