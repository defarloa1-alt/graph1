# QID → SFA Learning: End-to-End Flow

**Purpose:** Document the complete sequence from user passing a domain QID through SFA learning, schema/subagent decisions, and the point where the SFA starts making Claims.

**Status:** Draft — consolidates architecture decisions from 2026-03-02 session.

---

## 1. Input

**User passes:** A domain seed QID (e.g. `Q17167` Roman Republic).

**Intent:** Instantiate 18 SFAs, one per facet, all anchored to this subject node. For this flow we focus on the **Political Roman Republic SFA**.

---

## 2. SCA Runs (or Has Run)

The SCA is the pipeline that builds the deterministic base. It does **not** create SubjectConcepts (those emerge later). It provides:

### 2.1 Subject Cipher (Requirement)

The **subject node** (e.g. Roman Republic Q17167) has a cipher created by the SCA:

- **Formula:** `QID|P31:val1,val2|P36:val|...` — readable canonical string (no hash)
- **Scope:** All Wikidata statements on the subject (P31, P279, P361, P244, P1149, etc.)
- **Purpose:** IDs the subgraph; SFA updates that subgraph. Deterministic; same content → same cipher.
- **Minted by:** SCA (first agent with full subject + property data)

Example: `entity_cipher = "Q17167|P31:Q11514315,Q1307214,Q3024240,Q48349|P36:Q220|P122:Q666680|..."`

*The SFA edges back to this subject node and updates the subgraph it identifies.*

| Phase | What SCA Does | Output in Graph |
|-------|---------------|-----------------|
| **Discipline subgraph** | Backlink recursion from discipline roots (e.g. Q36442 political science) | Discipline nodes, BROADER_THAN, PART_OF, authority IDs |
| **Entity harvest** | Backlink recursion from domain seed + anchors | Entity nodes, P31/P279/P17/etc. relationships |
| **Classification anchors** | Dewey/LCC/LCSH positioning for domain | ClassificationAnchor nodes, POSITIONED_AS edges |
| **Characterization** | Facet weights, authority mappings | Facet assignments, SYS_PropertyMapping |

**Deterministic-first:** SCA exhausts Wikidata/SPARQL/authority lookups before any LLM. See `deterministic-first` todo.

---

## 3. SFA Instantiation

**Agent:** `SFA_subj_roman_republic_q17167_POLITICAL` (or equivalent pattern).

**Parameters:**
- `subject_qid`: Q17167 (Roman Republic)
- `facet`: POLITICAL
- `discipline_root_qid`: Q36442 (political science) — for learning phase

**Graph state required:** Entities, Discipline taxonomy, Classification anchors, SYS_ rules. SubjectConcepts may not exist.

---

## 4. SFA Learning Phase (First Order of Business)

The SFA does **not** classify entities or make Claims first. It **learns** from the resources the SCA provided plus external authorities. No approval needed — the SFA owns the schema in its subgraph.

### 4.1 Derive Learning Anchors (SFA Reasons)

The SFA **reasons** to derive learning anchors from SCA data. It does not use a predefined list.

**Inputs from SCA:** Subject node, POSITIONED_AS chain (direct parents), Classification anchors, Discipline taxonomy, Entity harvest.

**Reasoning:** The SFA inspects the parents (form of government, historical period, historical country, aristocratic republic, Ancient Rome, etc.) and decides which are learning anchors — which are "tops" of hierarchies worth traversing, which to prioritize for its facet. Config (`sfa_hierarchical_learning.json`) is a fallback; SFA reasoning is primary.

### 4.2 Three Learning Approaches (Traversal Directions)

| Direction | PIDs | Learning approach |
|-----------|------|-------------------|
| **Up** | P31, P279, P361 | Climb abstraction: "What kind of thing is this?" |
| **Down** | P527, P150 | Decompose: "What does it contain?" (provinces, institutions, magistracies) |
| **Succession** | P155, P156 | Temporal ordering: "What precedes/follows?" |

The SFA reiterates step 1 for each anchor, using all three directions where applicable.

### 4.3 Query the Graph (SCA-Provided)

- **Discipline subgraph:** `MATCH (d:Discipline {qid: "Q36442"})-[:BROADER_THAN|PART_OF*1..3]->(child) RETURN ...`
- **Classification anchors:** Dewey, LCC, LCSH for Q17167
- **SYS_ rules:** D10, policies, thresholds, forbidden facets
- **Entities:** Sample of harvested entities in domain

### 4.4 Query External Resources

| Source | What It Provides |
|--------|------------------|
| **LCC / LCSH** | Subject backbones, hierarchy, subdivisions |
| **FAST / Dewey** | Additional classification structure |
| **OpenAlex** | Topic hierarchy, citation clusters, how research is clustered |
| **OpenSyllabus** | Syllabi, reading lists, what is taught |
| **Works & bibliography** | Cited works, citation chains, core literature |

### 4.5 LLM Synthesis (When Needed)

The LLM synthesizes methodologies, boundary concepts, interpretive rules. **Deterministic-first:** Use LLM only when graph + authority queries don't resolve.

---

## 5. Persist Learning to Subgraph

**No D10 approval for learning.** The SFA owns the schema. It persists directly to its subgraph.

**Scope of the subgraph:** The learning subgraph extends *beyond* the subject (e.g. Roman Republic) into higher-level disciplines and how they break down. By traversing Up (P31/P279/P361) from anchors, the SFA builds a large subgraph that includes political science, history, classics, and their decomposition into subdisciplines, methodologies, and boundary concepts. This broader structure is the schema the SFA uses when it later makes Claims.

**Mechanism:** SFA (or script) writes nodes and edges to the subgraph identified by the subject cipher. Node types and edge types are chosen by the SFA (see §6).

---

## 6. SFA Decides Schema and Subagents

Before making Claims, the SFA makes two decisions:

### 6.1 Best Schema for Its Subgraph

The SFA **decides** what schema best fits what it learned. Options: Discipline + SUBCLASS_OF, Methodology + METHODOLOGY_FOR, BoundaryConcept, custom types (Institution, Magistracy, Assembly). The schema is chosen to fit the domain.

### 6.2 Which Slices Need Subagents

The SFA **decides** which branches warrant specialist subagents. Reasoning: Is this dense enough? Is the boundary clear? Would a specialist improve quality?

**SubjectConcepts emerge here.** The slices the SFA identifies as needing specialists become SubjectConcepts (or equivalent anchors) for specialist SFAs. SubjectConcepts are discovered through learning, not predefined.

---

## 7. Next Instantiation

On the next run, the SFA **loads** its learned subgraph from the graph. No re-synthesis. The graph is the agent's persistent memory.

---

## 8. SFA Starts Making Claims

**Only after** learning, schema choice, and subagent decisions does the SFA start making Claims.

- Classify entities against the facet
- Extract subject–property–object triples
- Propose Claims (with cipher, facet, provenance)
- Submit for **D10 review** — Claims require promotion; learning subgraph does not

---

## Summary Diagram

```
User passes QID (Q17167)
        │
        ▼
┌───────────────────┐
│ SCA runs          │  Discipline subgraph, entity harvest,
│ (deterministic)   │  classification anchors, SYS_
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ SFA instantiation │  Political SFA for Roman Republic
│ (subject + facet) │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ SFA learning      │  Derive anchors, traverse up/down/succession
│ (first order)     │  Query graph + OpenAlex, LCC/LCSH, works
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Persist learning  │  Direct to subgraph (no D10)
│ (SFA owns schema) │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ SFA decides       │  Best schema for subgraph
│ schema & subagents│  Which slices need specialists → SubjectConcepts
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ SFA makes Claims  │  Classify entities, extract triples
│ (D10 review)      │  Propose Claims → promotion
└───────────────────┘
```

---

## SFA Hierarchical Learning Config

**File:** `config/sfa_hierarchical_learning.json`

Defines:
- **learning_anchors** — Top-level QIDs from subject's POSITIONED_AS chain (form of government, historical period, etc.). SFA reiterates step 1 for each.
- **traversal_properties** — PIDs for backlink harvest: P31, P279, P361 (up), P527, P150 (down), P155, P156 (succession), P122 (type anchor).
- **p31_denylist** — QIDs to exclude (e.g. Q4167836 Wikimedia category).
- **max_hops_per_anchor**, **max_nodes_per_anchor** — Budget limits.

*Future: migrate to SYS_ nodes for self-describing.*

---

## Related Docs

- `SCA_SFA_CONTRACT.md` — division of labor
- `SCA_FEDERATION_POSITIONING_SPEC_v2.md` — container structure
- `TAXONOMY_HARVESTER_AGENT_SPEC.md` — classification neighborhood
- `2-16-26-Day in the life of a facet.md` — SFA daily workflow (assumes learning done)
- `claude/You are an agent in the Chrystallum fede.md` — SYS_ self-describing test, backlink recursion insight
