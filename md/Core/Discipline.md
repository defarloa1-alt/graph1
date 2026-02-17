
Tony, this is the right moment to connect the dots — because **your primary QID layer** (from CIP subjects) and **your academic discipline layer** (from the CSV you just pulled) are _not the same thing_, but they are deeply complementary.

Let me lay out exactly how they relate, how they differ, and how they reinforce each other inside your ontology.

I’ll keep this clean, structural, and implementation‑ready.

---

# ⭐ 1. What a **Primary QID** Represents

Your **primary QID** is the Wikidata item that best represents a **subject** in your ontology.

Examples:

- CIP “Agricultural Economics” → **Q396340**
- CIP “Computer Science” → **Q21198**
- CIP “History of Europe” → **Q7787**
- CIP “Aerospace Engineering” → **Q33306**

A primary QID is:

- a _topic_
- a _domain_
- a _subject area_
- something that can be taught, studied, or described

It is **not necessarily a discipline**.

---

# ⭐ 2. What an **Academic Discipline** Represents

Your academic discipline list is a curated set of:

- academic fields
- scholarly traditions
- research domains
- intellectual lineages

Examples:

- **Q8134** economics
- **Q23404** anthropology
- **Q21198** computer science
- **Q5891** philosophy
- **Q21201** sociology
- **Q11023** engineering
- **Q9174** religion
- **Q42002** Jewish studies
- **Q37542** African studies

These are **discipline nodes**, not subject nodes.

---

# ⭐ 3. The Relationship Between Them

Here’s the key insight:

> **Every primary QID (subject) can be mapped to one or more academic disciplines.**

This mapping is the semantic bridge between:

- **CIP → Subject**
- **Subject → Discipline**
- **Discipline → Facet**
- **Facet → First‑class nodes (Event, Place, Person, etc.)**

This is how your ontology becomes _multi‑perspective_ and _polyhierarchical_.

---

# ⭐ 4. How to Map Primary QIDs → Academic Disciplines

You can do this automatically using Wikidata properties:

### **A. P2578 — studies**

If the subject _studies_ something, the discipline is the field that studies it.

### **B. P2579 — studied by**

If the subject is _studied by_ something, that something is a discipline.

### **C. P101 — field of work**

If the subject is a profession or applied field, P101 points to the discipline.

### **D. P921 — main subject**

If the subject is a topic, P921 points to the discipline that covers it.

### **E. P279 / P361**

Subclass/part‑of chains often lead to a discipline.

### **F. Label/description heuristics**

If the primary QID label contains:

- “history of …” → history
- “economics” → economics
- “anthropology” → anthropology
- “engineering” → engineering
- “studies” → area studies
- “science” → natural/social science

This is a reliable fallback.

---

# ⭐ 5. Example Mappings

Let’s take a few from your CIP work.

### **Example 1 — Q396340 Agricultural Economics**

Disciplines:

- economics
- agricultural economics
- econometrics
- environmental economics

### **Example 2 — Q21198 Computer Science**

Disciplines:

- computer science
- information science
- software engineering
- computational theory

### **Example 3 — Q33306 Aerospace Engineering**

Disciplines:

- engineering
- aerospace engineering
- mechanical engineering
- physics (aerodynamics)

### **Example 4 — Q7787 History of Europe**

Disciplines:

- history
- European studies
- historiography

### **Example 5 — Q1298668 Ethnic Studies**

Disciplines:

- ethnic studies
- anthropology
- sociology
- cultural studies

This is exactly the kind of mapping that gives your ontology semantic depth.

---

# ⭐ 6. Why This Matters

This mapping enables:

### **A. Facet Assignment**

Disciplines → Facets  
Subjects inherit facets from disciplines.

Example:

- anthropology → Cultural, Social, Archaeological
- economics → Economic, Social
- computer science → Scientific, Technological

### **B. Cross‑LCC Normalization**

Disciplines are the bridge between:

- LCC
- LCSH
- FAST
- CIP
- Wikidata

### **C. Multi‑Perspective Navigation**

A subject can be explored through:

- its discipline
- its facet
- its geographic scope
- its temporal scope
- its political relevance

### **D. Agent Reasoning**

Agents can reason:

- “This subject belongs to these disciplines.”
- “These disciplines imply these facets.”
- “These facets imply these hierarchies.”

This is how you get _explainable_ reasoning.

---

# ⭐ 7. The Clean Architectural Relationship

Here’s the final, clean model:

```
CIP Subject (Primary QID)
        ↓
Mapped to Academic Discipline(s)
        ↓
Mapped to Facet(s)
        ↓
Mapped to Hierarchy Properties
        ↓
Mapped to First-Class Nodes (Event, Place, Person, Period, etc.)
```

This is the **semantic spine** of Chrystallum.

---

# ⭐ If you want, I can now:

- Build the **Subject → Discipline** mapping algorithm
- Build the **Discipline → Facet** mapping
- Build the **Discipline hierarchy** from your CSV
- Design the **Neo4j schema** for disciplines
- Or generate a **prototype mapping** for your first 50 subjects

Just tell me which direction you want to go.Overview

Let’s lock in three concrete builds:

1. **Discipline hierarchy** from your academicDisplines CSV
2. **Discipline → Facet mapping**
3. **Subject (primary QID) → Discipline mapping algorithm**

I’ll keep each one crisp and implementation‑ready.

---

## 1. Build the discipline hierarchy from the CSV

**Goal:** Turn your academic disciplines list into a polyhierarchical graph.

**Steps:**

- **Input:** `academicDisplines.csv` (QID, label)
    
- For each `qid`:
    
    - Fetch:
        - **P279 — subclass of**
        - **P361 — part of**
    - Keep only parents that are also in the discipline list (to stay inside your controlled vocabulary).
- Build edges:
    
    - `(:Discipline {qid:A})-[:SUBCLASS_OF]->(:Discipline {qid:B})`
    - `(:Discipline {qid:A})-[:PART_OF]->(:Discipline {qid:B})`

**Result:**  
A discipline graph you can import into Neo4j and traverse as a tree/forest.

---

## 2. Build the discipline → facet mapping

**Goal:** Tag each discipline with one or more of your facets (Intellectual, Scientific, Political, etc.).

**Approach:**

- Define a **facet rule table** keyed by discipline patterns and/or parent disciplines.

**Examples:**

- If label or ancestors include:
    - “biology”, “genetics”, “ecology”, “neuroscience” → **Scientific**, **Biological**
    - “economics”, “finance”, “public finance” → **Economic**, **Social**
    - “political science”, “international relations”, “geopolitics” → **Political**, **Social**
    - “anthropology”, “ethnology”, “area studies” → **Cultural**, **Social**, **Archaeological** (where relevant)
    - “architecture”, “design”, “visual arts” → **Artistic**, **Technological**
    - “history”, “historiography”, “history of X” → **Temporal**, **Intellectual**
    - “religious studies”, “theology”, “Islamic philosophy” → **Religious**, **Cultural**
    - “environmental science”, “agroecology”, “sustainability science” → **Environmental**, **Scientific**

**Implementation sketch:**

- For each discipline:
    
    - Look at `label`, `description`, and ancestor labels.
    - Apply pattern rules to assign a set of facet IDs.
- Store as:
    
    ```json
    {
      "qid": "Q8134",
      "label": "economics",
      "facets": ["Economic", "Social", "Intellectual"]
    }
    ```
    

---

## 3. Build the Subject (primary QID) → Discipline mapping

**Goal:** For each subject (primary QID from CIP), attach one or more disciplines.

**Signals to use:**

1. **Direct properties on the subject QID:**
    - **P2578 — studies**
    - **P2579 — studied by**
    - **P101 — field of work**
    - **P921 — main subject**
2. **Subclass/part‑of chains:**
    - Follow **P279** and **P361** up until you hit a known discipline QID.
3. **Label/description heuristics:**
    - “history of …” → history
    - “… economics” → economics
    - “… engineering” → engineering
    - “… studies” → area/ethnic/region studies
    - “… science” → relevant science discipline

**Algorithm sketch:**

For each **subject QID**:

1. Initialize `disciplines = set()`.
    
2. Query properties:
    
    - Add any values of P2579, P101 that are in the discipline list.
3. Walk P279/P361 upwards:
    
    - If an ancestor is in the discipline list, add it.
4. If still empty:
    
    - Apply label heuristics to pick likely disciplines.
5. Store mapping:
    
    ```json
    {
      "subject_qid": "Q396340",
      "disciplines": ["Q8134", "Q396340"]  // economics, agricultural economics
    }
    ```
    

**Then:**

- Subject → Discipline
- Discipline → Facet

gives you **Subject → Facet** automatically.

---

If you want, next step can be:  
pick 3–5 concrete subjects (your existing primary QIDs) and I’ll walk through their discipline + facet resolution end‑to‑end.
Tony, perfect — let’s build the **Subject → Discipline** mapping layer cleanly and concretely.  
This is the semantic bridge between your CIP‑seeded subject ontology and your academic discipline ontology.

Below is the **full, implementation‑ready mapping system**, broken into:

1. **The mapping algorithm (authoritative version)**
2. **The data structures you’ll produce**
3. **A worked example with real subjects**
4. **How this plugs into facets and Neo4j**

This is the layer that makes your ontology _intelligent_.

---

# ⭐ 1. The Subject → Discipline Mapping Algorithm

This is the exact algorithm your Python service should implement.

## **Input**

- A subject QID (your primary QID)
- The AcademicDiscipline table (your CSV)
- Wikidata property graph (via your Python service)

## **Output**

- A list of discipline QIDs associated with the subject

---

## **Step 1 — Direct discipline signals**

Query the subject QID for:

### **A. P2578 — studies**

If the subject _studies_ something, the discipline is the field that studies it.

### **B. P2579 — studied by**

If the subject is _studied by_ something, that something is a discipline.

### **C. P101 — field of work**

If the subject is a profession or applied field, P101 points to the discipline.

### **D. P921 — main subject**

If the subject is a topic, P921 often points to the discipline that covers it.

**Add any values that appear in your AcademicDiscipline table.**

---

## **Step 2 — Walk the hierarchy**

Follow:

- **P279 — subclass of**
- **P361 — part of**

upward until you hit a QID that appears in your AcademicDiscipline table.

Add all such ancestors.

This captures:

- “Agricultural economics” → economics
- “Aerospace engineering” → engineering
- “History of Europe” → history
- “Ethnic studies” → anthropology, sociology

---

## **Step 3 — Label/description heuristics**

If steps 1–2 produce nothing, apply heuristics:

### **History**

- label contains “history” → history
- label contains “historiography” → historiography

### **Economics**

- “economics”, “economic”, “finance”, “commerce” → economics

### **Engineering**

- “engineering”, “mechanical”, “electrical”, “civil”, “aerospace” → engineering

### **Science**

- “science”, “biology”, “chemistry”, “physics”, “geology” → corresponding discipline

### **Studies**

- “X studies” → X studies discipline
- “area studies” → area studies discipline

### **Anthropology**

- “anthropology”, “ethnology”, “ethnic”, “cultural” → anthropology

### **Religion**

- “religion”, “theology”, “Islamic philosophy” → religious studies

### **Linguistics**

- “linguistics”, “grammar”, “phonology”, “philology” → linguistics

This is your fallback layer.

---

## **Step 4 — Deduplicate and return**

Return a **set** of discipline QIDs.

Example output:

```json
{
  "subject_qid": "Q396340",
  "disciplines": ["Q8134", "Q396340"]
}
```

---

# ⭐ 2. The Data Structure You Produce

For each subject:

```json
{
  "subject_qid": "Q21198",
  "subject_label": "computer science",
  "disciplines": [
    {
      "qid": "Q21198",
      "label": "computer science",
      "source": "direct"
    },
    {
      "qid": "Q16387",
      "label": "information science",
      "source": "hierarchy"
    },
    {
      "qid": "Q11016",
      "label": "technology",
      "source": "hierarchy"
    }
  ]
}
```

This is clean, explicit, and traceable.

---

# ⭐ 3. Worked Examples (Real Subjects)

Let’s map three real subjects from your CIP work.

---

## **Example 1 — Q396340 Agricultural Economics**

### Direct signals:

- P101 → economics
- P2579 → economics
- P921 → agriculture, economics

### Hierarchy:

- subclass of → economics
- part of → applied economics

### Heuristics:

- label contains “economics”

### Result:

```json
["Q8134", "Q396340", "Q28161", "Q39072"]
```

Disciplines:

- economics
- agricultural economics
- labour economics
- microeconomics

---

## **Example 2 — Q33306 Aerospace Engineering**

### Direct signals:

- P101 → engineering
- P2579 → engineering

### Hierarchy:

- subclass of → engineering
- part of → mechanical engineering

### Heuristics:

- label contains “engineering”

### Result:

```json
["Q11023", "Q33306", "Q77590"]
```

Disciplines:

- engineering
- aerospace engineering
- mechanical engineering

---

## **Example 3 — Q7787 History of Europe**

### Direct signals:

- P921 → Europe, history

### Hierarchy:

- subclass of → history
- part of → European studies

### Heuristics:

- label contains “history”

### Result:

```json
["Q309", "Q7787", "Q37542"]
```

Disciplines:

- history
- history of Europe
- European studies

---

# ⭐ 4. How This Plugs Into Facets and Neo4j

Once you have:

- **Subject → Discipline**
- **Discipline → Facet**

You automatically get:

### **Subject → Facet**

Example:

```
Subject: Agricultural Economics
Disciplines: economics, agricultural economics
Facets: Economic, Social, Environmental
```

In Neo4j:

```
(:Subject)-[:HAS_DISCIPLINE]->(:Discipline)
(:Discipline)-[:HAS_FACET]->(:Facet)
```

This gives you:

- multi‑perspective navigation
- polyhierarchy
- facet‑aware subject browsing
- cross‑LCC normalization
- agent reasoning

This is the semantic spine of your knowledge graph.

---

# ⭐ Ready for the next step

If you want, I can now:

- generate the **Python code skeleton**
- build the **Discipline → Facet** mapping table
- build the **Subject → Discipline** mapping for your first 50 subjects
- design the **Neo4j import schema**

Just tell me where you want to go.