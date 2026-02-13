# Chrystallum Core Model v3.1  
## Backbone‑Driven, Agent‑Based Knowledge Graphs with Hybrid IDs and Wikidata Integration

**Version:** 3.1 (Core Model)
**Status:** Architecture Complete (Design Phase)
**Changelog (3.2):**
added dual backbone pattern, property and edge registry, universal required properties and edges

---

# Chrystallum Core Model v3.0

## Backbone‑Driven, Agent‑Based Knowledge Graphs with Hybrid IDs and Wikidata Integration

**Version:** 3.0 (Core Model)
**Date:** November 20, 2025
**Status:** Architecture Complete (Design Phase)
**Last Updated:** November 20, 2025

> This document specifies the *core conceptual and technical model* of Chrystallum.
> It describes the mathematical framework, backbone architecture, hybrid identity system,
> agent model, and data integration patterns. Implementation details, business models,
> and platform‑specific adaptations are handled in separate documents.

---

## Quick Navigation by Role

| Role                      | Start Here                     | Then Read                | Goal                                                   |
| ------------------------- | ------------------------------ | ------------------------ | ------------------------------------------------------ |
| **Researcher / Theorist** | §2 Core Mathematical Framework | Appendix A               | Understand subgraph dynamics & convergence assumptions |
| **System Architect**      | §3 Backbone Architecture       | §5 Agent Architecture    | Design backbone‑aligned, agent‑based KG systems        |
| **AI/ML Engineer**        | §6 Wikidata Patterns           | §7 Text Ingestion        | Implement data integration & extraction                |
| **Knowledge Engineer**    | Appendix B (YAML Schemas)      | §4 Hybrid ID System      | Map domains into the backbone model                    |
| **New to System**         | §1 Executive Summary           | §3 Backbone Architecture | Get oriented on backbone + agents + shell nodes        |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Core Mathematical Framework](#2-core-mathematical-framework)
3. [Backbone Architecture: LCC/LCSH/FAST/MARC](#3-backbone-architecture-lcclcshfastmarc)
4. [Hybrid Node ID System](#4-hybrid-node-id-system)
5. [Agent Architecture & Persistence Model](#5-agent-architecture--persistence-model)
6. [Wikidata Integration Patterns](#6-wikidata-integration-patterns)
7. [Text & Document Ingestion Pipeline](#7-text--document-ingestion-pipeline)
8. [Wikidata Feeder: Trusted Contribution](#8-wikidata-feeder-trusted-contribution)
9. [Project Status & Implementation Phases](#9-project-status--implementation-phases)

**Appendices**

* [Appendix A: Mathematical Notation & Formal Definitions](#appendix-a-mathematical-notation--formal-definitions)
* [Appendix B: Base Ontology & Backbone‑Aligned Schemas](#appendix-b-base-ontology--backbone-aligned-schemas)
* [Appendix C: LCC/LCSH/FAST/Wikidata Crosswalk](#appendix-c-lcclcshfastwikidata-crosswalk)
* [Appendix D: Implementation Code Snippets](#appendix-d-implementation-code-snippets)
* [Appendix E: LLM Prompt Templates](#appendix-e-llm-prompt-templates)
* [Appendix F: Glossary](#appendix-f-glossary)

---

# 1. Executive Summary

## 1.1 What is Chrystallum Core?

**Chrystallum Core** is a mathematically grounded, **backbone‑driven, agent‑based framework** for building self‑organizing knowledge graphs in which:

* **Each node is managed by an autonomous LLM agent** aligned to Library of Congress standards (LCC/LCSH/FAST/MARC).
* **Relationships are first‑class entities** with confidence scores, provenance, and version history.
* **Semantic state evolves via pressure fields** (Civic, Epistemic, Structural, Temporal) over local subgraphs.
* **Multi‑agent debate** resolves contradictions using evidence‑based consensus.
* **Dormancy** makes the system economically viable: agents sleep when local graphs are stable.
* **Shell nodes** provide a semantic scaffold without up‑front LLM cost (lazy expansion).
* A **hybrid identity system** (Wikidata QIDs, Chrystallum IDs, composite IDs) supports both public and private knowledge.
* **Deterministic content hashes** provide consistent deduplication and versioning.
* An **automatic Wikidata contribution** pipeline enables trusted, provenance‑rich additions to the open knowledge commons.
* The system is **multilingual by design**, leveraging QIDs and FAST/LCC crosswalks across many languages.

## 1.2 The Problem

Knowledge workers face:

* **Information chaos** – time lost to organizing sources and re‑searching.
* **Knowledge silos** – critical institutional knowledge trapped in departments or individuals.
* **Contradictions discovered late** – conflicting sources only appear after deep investment.
* **Manual synthesis overhead** – hours spent reconciling disparate sources and formats.
* **Interdisciplinary gaps** – difficulty linking related concepts across domains.
* **LLM cost pressure** – naive systems pay for every inference on every node.

## 1.3 The Core Idea

Chrystallum Core combines:

* **Backbone alignment (LCC/LCSH/FAST/MARC)** for semantic coherence and institutional legitimacy.
* **Backbone‑aligned subgraphs managed by agents**, each optimizing a local loss function.
* **Shell nodes + lazy expansion** to create a rich semantic horizon at low cost.
* **Local convergence (not global fixed points)** for scalable, distributed knowledge evolution.
* **Hybrid identity** so public, private, and composite entities coexist cleanly.
* **Wikidata federation** to both ingest from and contribute to the global open data ecosystem.

---

# 2. Core Mathematical Framework

## 2.1 Overview: Local Convergence Under Backbone Constraints

Chrystallum is built around **local subgraphs** managed by agents, each aligned to a specific backbone classification (e.g. “Earth’s Atmosphere” as Q6312 with corresponding FAST and LCC codes). Each agent seeks a local equilibrium for its subgraph while respecting constraints imposed by library standards.

Global behavior emerges from:

* Multiple agents updating their subgraphs.
* A shared backbone structure (LCC/LCSH/FAST).
* Compositional semantics via consistent identity and provenance.

## 2.2 Subgraph as Fundamental Unit

A subgraph managed by agent (A_i) is:

[
S_i = (V_i, E_i, P_i, A_i, B_i, \mathcal{M}_i)
]

Where:

* (V_i): nodes (entities, events, concepts) with QIDs or local IDs.
* (E_i): edges (typed relationships with confidence).
* (P_i): properties (5W1H: who, what, when, where, why, how).
* (A_i): the agent responsible for (S_i).
* (B_i): backbone alignment (LCC code, LCSH heading, FAST facet).
* (\mathcal{M}_i): metadata (version history, timestamps, provenance).

## 2.3 Content Hash for Node Versions

To support deterministic deduplication and versioning, Chrystallum defines a **content hash**:

[
\text{content_hash} = H(\text{QID or base ID} \mid\mid \text{canon}(P))
]

Where:

* (H) is SHA‑256.
* (\text{canon}(P)) is a canonical JSON serialization of properties.

**Intended use:**

* Distinguish different *states* of a concept that share the same underlying entity.
* Enable idempotent imports and updates (same semantic content → same content hash).
* Support version chains via `SUPERSEDED_BY` edges.

In the core model, **graph identity** (the primary `id`) and **content hash** are separated:

* `id` – stable node identity (QID, Chrystallum ID, or composite ID).
* `content_hash` – derived, version‑sensitive summary of properties.

## 2.4 Priority Metrics and Multi‑Objective Loss

The multi‑objective loss in §2.4 is intended as a design template, not a fixed formula. In practice, Chrystallum uses a small set of *priority metrics* to decide where agents spend effort and where prefetch should occur.

We distinguish two core signals at the node or subgraph level:

- **Demand score** – “how much do users or upstream processes care about this region?”
- **Gap score** – “how incomplete or unstable is our understanding of this region?”

### 2.4.1 Demand score (Civic / usage signal)

For a node \(v\), demand is a heuristic function of usage:

- View counts (graph views, inspections)
- Query hits (how often v appears in answers / results)
- Explicit user interest (bookmarks, pinning, inclusion in active projects)

Conceptually:

\[
\text{demand\_score}(v) \approx
w_1 \log(1 + \text{view\_count}(v)) +
w_2 \log(1 + \text{query\_hits}(v)) +
w_3 \cdot \text{bookmark\_flag}(v)
\]

This corresponds to what earlier drafts called **civic pressure**. High demand means users are frequently touching this part of the graph.

### 2.4.2 Gap score (Epistemic / structural / temporal signal)

For a node \(v\), the gap score measures how “fragile” the local knowledge is. It may combine:

- **Epistemic factors**: number of conflicting claims vs total claims  
- **Structural factors**: proportion of shell neighbors vs expanded neighbors  
- **Temporal factors**: staleness (time since last update in a domain where facts change)

A simple composite heuristic:

\[
\text{gap\_score}(v) \approx
a_1 \cdot \text{shell\_neighbor\_ratio}(v) +
a_2 \cdot \frac{\text{conflict\_count}(v)}{1 + \text{claim\_count}(v)} +
a_3 \cdot \text{staleness}(v)
\]

where each term is normalized to [0, 1] and the coefficients \(a_i\) are tuned empirically.

This corresponds to earlier **epistemic / structural / temporal pressure**: high gaps mean the region is under‑specified, contradictory, or outdated.

### 2.4.3 Maintenance vs prefetch priorities

Using these two signals, the system defines two composite priorities:

- **Maintenance priority** (for agent work):

\[
\text{priority\_maintenance}(v) =
\text{demand\_score}(v) \times \text{gap\_score}(v)
\]

Nodes that are both frequently used *and* under‑specified rise to the top of the repair queue; agents are scheduled there first.

- **Prefetch priority** (for shell expansion):

\[
\text{priority\_prefetch}(v) = \text{demand\_score}(v)
\]

Prefetch focuses on shells in regions users are actively exploring. Gap score still matters for agent maintenance, but prefetch is primarily about **perceived latency** rather than epistemic quality.

These metrics provide a concrete interpretation of the earlier abstract “pressure fields” without requiring precise physical analogies. They are cheap to recompute from graph metadata and usage logs, and they can be tuned per deployment.

### 2.4.4 Loss function as a design pattern

The earlier multi‑objective loss:

\[
\mathcal{L}(S_i, \Delta_i) =
\alpha_1 V_{\text{pressure}}(S_i, \Delta_i)
- \alpha_2 R_{\text{unleaf}}(S_i, \Delta_i)
+ \alpha_3 C_{\text{complexity}}(S_i, \Delta_i)
+ \alpha_4 B_{\text{constraint}}(S_i, \Delta_i)
\]

can now be interpreted as follows:

- \(V_{\text{pressure}}\) aggregates demand and gap signals within the subgraph.  
- \(R_{\text{unleaf}}\) rewards converting shell nodes into well‑connected expanded nodes (“unleafing”).  
- \(C_{\text{complexity}}\) penalizes unnecessary graph bloat.  
- \(B_{\text{constraint}}\) penalizes violations of backbone alignment.

Chrystallum does not require a single closed‑form expression for \(\mathcal{L}\); it requires a *family* of reasonable heuristics that can be evaluated from stored graph features. Implementations are free to choose specific formulas, provided they respect backbone constraints and avoid unbounded growth.

## 2.5 Convergence Principle (Local, with Backbone)

Instead of a fully formal theorem, Chrystallum Core adopts the following **design principle**:

> **Convergence Principle (Local):**  
> For a fixed subgraph \(S_i\) aligned to a backbone class \(B_i\) and a bounded evidence stream, we *expect* that repeatedly applying the update operator \(\Phi_i\) and using the priority metrics from §2.4 will drive that subgraph toward a stable configuration (low loss) in a finite number of steps.

Operationally:

- **Convergence time:** expected to be small for bounded subgraphs and stable evidence streams.  
- **Backbone compliance:** enforced by the \(B_{\text{constraint}}\) term and by prohibiting updates that would move nodes outside their allowed backbone range without an explicit governance action.  
- **Multiple equilibria:** are acceptable and expected in contested domains; Chrystallum records competing claims with provenance rather than forcing an artificial single “truth”.  
- **Dormancy:** when maintenance priority for all nodes in \(S_i\) is below a small threshold, the agent becomes dormant. It can be re‑activated when new evidence arrives or demand increases.

Formal proofs and empirical validation are left to implementation and experimentation; the core spec defines the **structure** of these dynamics and the **assumptions** they rely on.


# 3. Backbone Architecture: LCC/LCSH/FAST/MARC

## 3.1 Why Use Library Standards as a Backbone?

Chrystallum is grounded in **Library of Congress** standards:

* **LCC** (classification)
* **LCSH** (subject headings)
* **FAST** (faceted application of subject terminology)
* **MARC** (bibliographic records)

These provide:

* **Global institutional legitimacy** – 150+ years of curated knowledge.
* **Semantic coherence** – nodes align to vetted subject headings, avoiding ad‑hoc taxonomies.
* **Interoperability** – direct mapping to Wikidata properties, OCLC, and other knowledge systems.
* **Hierarchical structure** – clear parent/child categories for navigation and visualization.
* **Faceted search** – FAST supports machine‑optimized faceted browsing.
* **Multilingual support** – cross‑language mappings for subject headings.
* **Authority control** – deduplication of names, variants, and “see also” links.

## 3.2 Four‑Layer Backbone Model

| Layer   | Standard | Purpose                        | Example                                 |
| ------- | -------- | ------------------------------ | --------------------------------------- |
| Class   | LCC      | Broad hierarchical category    | K4349 (Telecommunications Law)          |
| Subject | LCSH     | Controlled subject heading     | “Telecommunication—Law and legislation” |
| Facet   | FAST     | Machine‑optimized facet        | 1177770 (Telecommunications industry)   |
| Record  | MARC     | Bibliographic record structure | Field 650 (Subject Added Entry)         |

## 3.3 Backbone‑Aligned Agents

Each **agent** is initialized with:

1. **Backbone class & subject** – e.g. an “AtmosphereAgent” aligned to LCC QC851‑859, LCSH “Atmosphere”, FAST 1010202.
2. **Allowed properties** – determined by the class (e.g. for physics: formula, unit, dimension, etc.).
3. **Allowed relationships** – constrained by the ontology (e.g. protects_from, interacts_with).
4. **Governance rules** – agents cannot extend beyond their backbone branch without explicit protocol (proposal/approval).

Example (simplified):

```yaml
Agent: AtmosphereAgent
BackboneClass: Q6312         # Earth's atmosphere
LCSH: "Atmosphere"
FAST: 1010202
LCC: QC851-859
AllowedProperties:
  - composition
  - thickness
  - pressure
  - temperature
  - functions
  - dynamics
AllowedRelationships:
  - protects_from
  - contains
  - interacts_with
  - affects
```

## 3.4 Interdisciplinary Linking via Backbone

The backbone enables safe cross‑disciplinary edges. For example, a single claim about the atmosphere may connect:

* Physics (heat transfer)
* Astrophysics (cosmic rays)
* Engineering (equivalent shielding thickness)
* Climatology (surface temperature)
* Bibliography (authors, books)

By aligning each concept to an appropriate backbone branch, Chrystallum allows navigation across disciplines without losing semantic integrity.

## 3.5 Shell Nodes and Backbone Alignment

When an agent identifies a related concept, it can create a **shell node**:
Shell nodes are created by agents when identifying related concepts during extraction or exploration. The agent:

1. **Generates a Chrystallum ID** (format: `C_<12-char-hash>` derived from label and context)
2. **Assigns backbone alignment** (LCC code, FAST ID, optional QID if entity exists in Wikidata)
3. **Sets status to "shell"** (indicates placeholder, not yet expanded)
4. **Persists minimal metadata** (label, type/backbone class, backbone codes)
5. **Leaves properties empty** (deferred until explicit expansion request)

* **Cost:** Negligible (graph write only, no LLM call).
* **Expansion:** Deferred until an agent or user explicitly requests it.


## 3.6 Dual Backbone Pattern for Domain Decomposition
Chrystallum uses a dual-backbone architecture to support both universal classification and effective domain-specific decomposition:

Universal Backbone (LCC/LCSH/FAST):

Every agent or content node is anchored to a universal backbone code (e.g., LCC, LCSH, or FAST).

This ensures semantic coherence, supports O(1) lookup, and enables interoperability with global knowledge standards (such as Wikidata).

Example: “Roman Republic” may be anchored to LCC DG231-261; “Civil War” to E468.

Domain-Specific Ontology Backbone:

When initial focus is too broad (e.g., “American history” or “Roman history”), a domain-specific ontology is introduced to offer granular decomposition: e.g., time periods, dynasties, thematic sub-domains, or chronologies.

Seed agents consult both backbones: the universal for category, the domain ontology for internal structure.

The domain ontology can be loaded from hand-curated YAML/JSON, imported from trusted external sources (e.g., Wikidata, Library of Congress timelines), or generated/supervised using LLMs.

Decomposition Logic:

The seed agent recursively breaks down the domain using domain ontologies aligned to the backbone codes, until the smallest operational “trainable unit” is reached.

Only then is an LLM-backed content agent activated for knowledge synthesis or further graph operations.

Higher-level seed agents are ephemeral, serving exclusively to guide the decomposition process and are not persistent.

This dual-backbone pattern guarantees:

Consistent institutional classification (universal backbone)

Practical, domain-relevant internal structure (domain-specific ontology)

Scalable agent deployment, with no bloated “mega-agents”

Traceable semantic lineage for every operational node/agent

# 4. Hybrid Node ID System

## 4.1 Motivation

Not all entities have Wikidata QIDs, and different contexts may require:

* Public, canonical identifiers (QIDs).
* Private, proprietary identifiers.
* Composite identifiers representing multi‑entity events.

The hybrid ID system supports all three while preserving O(1) lookups and clear semantics.

## 4.2 Tier 1 – Wikidata QID (Public, Canonical)

Use when the entity is already represented in Wikidata.

* **Format:** `Q1048` (Julius Caesar)
* **Properties:** globally unique, multilingual, stable, indexable.

Example:

```cypher
CREATE (caesar:Person {
  id: "Q1048",
  id_type: "wikidata",
  label: "Julius Caesar",
  backbone: "Q5 (Human)",
  qid: "Q1048",
  qid_url: "https://www.wikidata.org/wiki/Q1048"
})
```

## 4.3 Tier 2 – Chrystallum ID (Private / Proprietary)

Use for private, proprietary, or emerging entities.

* **Format:** `C_<12‑char hash>`
* **Generation:**

```python
def generate_chrystallum_id(label, context, namespace="local"):
    content = f"{namespace}|{label.lower()}|{sorted(context.items())}"
    digest = hashlib.sha256(content.encode()).hexdigest()[:12]
    return f"C_{digest}"
```

Example:

```cypher
CREATE (note:ResearchNote {
  id: "C_a3f5b2c8d1e9",
  id_type: "chrystallum",
  namespace: "personal",
  label: "Caesar's financial motivations",
  creator: "researcher_john",
  visibility: "private"
})
```

## 4.4 Tier 3 – Composite ID (Multi‑Entity Events)

Use for events or entities inherently defined by multiple components.

* **Format:** `QID1+QID2+...+QIDn_<hash>`

Example: “Caesar crosses the Rubicon on Jan 10, 49 BCE”:

* Q1048 = Julius Caesar
* Q14366 = Rubicon River
* Q2250 = specific date entity

Composite ID:

```text
Q1048+Q14366+Q2250_a7f3c8d2
```

Generation:

```python
def generate_composite_id(qids, properties):
    sorted_qids = sorted(qids)
    qid_string = "+".join(sorted_qids)
    prop_hash = hashlib.sha256(
        json.dumps(properties, sort_keys=True).encode()
    ).hexdigest()[:8]
    return f"{qid_string}_{prop_hash}"
```

## 4.5 Unified ID + Content Hash

In the core model, each node has:

```json
{
  "id": "Q1048",                     // or C_* or composite
  "id_type": "wikidata|chrystallum|composite",
  "label": "Human-readable name",
  "confidence": 0.85,

  "qid": "Q1048",                    // when applicable
  "namespace": "enterprise_acme",    // for Chrystallum IDs
  "component_qids": ["Q1048", "Q14366", "Q2250"],

  "content_hash": "9f17a967891d...", // hash(QID/base id + canonical properties)
  "visibility": "public|private|internal"
}
```

* `id` is the **primary graph identity** used for indexing and relationships.
* `content_hash` is used for **deduplication, versioning, and integrity**, not as the primary key.

Database constraints can still enforce uniqueness on `id` for O(1) semantic jumps.

---

# 5. Agent Architecture & Persistence Model

## 5.1 Agents as Stateless Execution Shells

**Core principle:** agents do not hold hidden long‑term state. They:

1. Query the graph for context and backbone information.
2. Invoke LLMs or external APIs in a stateless way.
3. Persist results (claims, nodes, relationships) back into the graph with full provenance.
4. Return references into the graph rather than raw opaque outputs.

Execution flow:

```text
1. Query graph for context/backbone alignment
   ↓
2. Call LLM or external API (stateless)
   ↓
3. Persist result to graph with provenance
   ↓
4. Return result as graph references (nodes/edges)
```

## 5.2 Graph as Single Source of Truth

Stored in the graph:

* Agent configuration (backbone alignment, capabilities, model).
* Agent invocations (audit trail, timestamps, status).
* Claims and concepts (with backbone properties).
* Provenance chains (sources, citations, evidence).
* Versioning (via `SUPERSEDED_BY` chains between claims or nodes).

## 5.3 Core Persistence Structures

**Agent node:**

```cypher
CREATE (agent:Agent {
  id: "agent_heat_transfer",
  type: "physics_analyzer",
  capability: "thermal_dynamics_validation",
  backbone_lcc: "QC311.5",
  backbone_fast: "0854703",
  backbone_qid: "Q18619352",
  api_endpoint: "https://api.openai.com/v1/chat/completions",
  model: "gpt-4",
  created_at: datetime(),
  status: "active"
})
```

**Invocation node:**

```cypher
CREATE (invocation:Invocation {
  id: "inv_12345",
  agent_id: "agent_heat_transfer",
  task: "validate_heat_retention_claim",
  timestamp: datetime(),
  duration_ms: 1250,
  status: "success",
  backbone_context: "QC311.5"
})
CREATE (agent)-[:INVOKED {timestamp: datetime()}]->(invocation)
```

**Claim node with backbone:**

```cypher
CREATE (claim:Claim {
  id: "Q18619352",                 -- primary identity (QID)
  content_hash: "9f17a967891d",    -- hash of properties
  id_type: "wikidata",
  label: "Heat retention in atmosphere",
  confidence: 0.85,
  backbone_lcc: "QC311.5",
  backbone_fast: "0854703",
  backbone_qid: "Q18619352",
  agent_id: "agent_heat_transfer",
  created_at: datetime(),
  version: 1
})
CREATE (invocation)-[:PRODUCED]->(claim)
CREATE (agent)-[:CREATED]->(claim)
```

**Provenance:**

```cypher
MATCH (claim:Claim {id: "Q18619352"})
MATCH (source:Source {title: "Physics textbook"})
CREATE (source)-[:EVIDENCE_FOR {confidence: 0.9}]->(claim)
```

**Versioning:**

```cypher
MATCH (old:Claim {id: "Q18619352", version: 1})
CREATE (new:Claim {
  id: "Q18619352",
  content_hash: "newhash...",
  version: 2,
  confidence: 0.88
})
CREATE (old)-[:SUPERSEDED_BY]->(new)
```

## 5.4 Shell Nodes & Lazy Expansion

Shell nodes are minimal placeholders created without LLM calls:

```cypher
CREATE (shell:Concept {
  id: "C_abc123def456",
  id_type: "chrystallum",
  label: "Heat loss",
  type: "Physics concept",
  backbone_lcc: "QC311.5",
  status: "shell",
  properties: {}
})
```

Expansion occurs only on demand:

```python
if node.status == "shell" and user_navigates_to(node):
    expanded = llm_expand(
        label=node.label,
        backbone=node.backbone_lcc,
        context=nearby_nodes,
    )
    update_node(node.id, {
        "properties": expanded,
        "status": "expanded",
        "expanded_at": datetime.now()
    })
```

This enables:

* **Cost control** – pay only for traversed nodes.
* **Scalable scaffolding** – large graphs of shells that become detailed as needed.
* **Dormancy** – agents can sleep once shell surfaces are stable.

## 5.5 Prefetch & Scheduling Policy

Chrystallum separates **what** agents do (update subgraphs) from **when** they are invoked. Prefetch and scheduling are policies layered on top of shell nodes and the priority metrics in §2.4.

### 5.5.1 Goals

The scheduling policy aims to:

1. Keep interactive latency low (clicking a node should feel fast).  
2. Spend LLM tokens where they create the most value.  
3. Avoid unbounded background activity that silently burns budget.

### 5.5.2 Prefetch (interactive latency)

Prefetch is responsible for expanding shell nodes *before* the user explicitly asks, when it is safe and useful to do so.

Typical prefetch triggers:

- **Viewport prefetch:** when a user opens a graph view, expand a small number of high‑priority shells in that region.  
- **Hover prefetch:** when a user hovers over a shell node for long enough, queue expansion in the background.  
- **Search prefetch:** when a node appears near the top of search results, prefetch its shell neighbors.

All prefetch decisions are constrained by:

- A **global budget** (e.g. max expansions per minute/hour).  
- **Per‑user budgets** (to avoid one user consuming all tokens).  
- Node‑level filters:
  - Only shells (`status = "shell"`).  
  - Prefetch priority above a configurable threshold.

Internally, prefetch priority is derived directly from the demand score (§2.4.1), optionally filtered by backbone branch or domain.

### 5.5.3 Agent maintenance scheduling

Beyond prefetch, agents perform **maintenance work** on subgraphs: refining claims, resolving conflicts, and strengthening structure.

Maintenance scheduling uses the **maintenance priority** from §2.4.3:

- At each scheduling interval, the system selects nodes (or small subgraphs) with the highest maintenance priority.  
- The responsible backbone‑aligned agents are invoked on those regions.  
- Work items may include:
  - Merging duplicate nodes (based on content hashes).  
  - Resolving conflicting claims or starting a debate.  
  - Expanding under‑connected shells.  
  - Updating stale Claims with new evidence.

As with prefetch, maintenance scheduling is bounded by:

- Global and per‑agent resource budgets.  
- Domain‑specific policies (e.g. some branches update more slowly).

### 5.5.4 Relationship to “pressure fields”

Earlier drafts of the architecture described **Civic / Epistemic / Structural / Temporal pressure fields** over the graph. In this core model, those ideas are concretized as:

- **Civic pressure** → demand score (§2.4.1)  
- **Epistemic / Structural / Temporal pressure** → components of gap score (§2.4.2)  

These are not physical fields; they are **derived priority metrics** computed from stored graph features and usage logs. They are designed to be:

- Cheap to compute.  
- Transparent to inspect and tune.  
- Flexible enough to evolve as empirical experience accumulates.

Implementations are encouraged to start with simple formulas for demand/gap scores and iteratively refine them based on observed behavior.

5.y Property & Edge Registry:
Ensuring Cross-Domain Interoperability
Chrystallum includes an explicit Property & Edge Registry to guarantee that all relationships and properties extracted—whether automatically by agents or contributed by users—remain harmonized and interoperable across all domains.

Purpose
Unify Relationship Types: Ensures that facts like INFLUENCED_BY, BIRTH_PLACE, MEMBER_OF, etc., have canonical definitions and identifiers, used uniformly throughout the graph.

Support Auto-Extraction: When seed/content agents pull properties and edges from Wikipedia, Wikidata, or other sources, these are mapped to standard registry entries.

Enable Cross-Domain Queries: Users and systems can confidently ask for all instances of a given relationship type across the entire knowledge graph.

Promote Schema Extension: When a new property/edge type is discovered, the registry allows for the structured proposal and review of candidate additions.

Schema
Field	Description
property_id	Unique identifier (e.g. REL_INFLUENCED_BY, PROP_BIRTH_DATE)
label	Standardized label (human-readable)
aliases	Variant labels/terms from different domains
description	Brief explanation of intended semantic
external_mapping	Reference to Wikidata P#, schema.org, etc.
created_by	Origin (auto/LCC/Wikidata/LLM/user)
status	approved / candidate / deprecated
created_at	Timestamp
Neo4j Example
text
CREATE (property_registry:PropertyRegistry {
  property_id: "REL_INFLUENCED_BY",
  label: "influenced by",
  aliases: ["affected by", "mentored by"],
  description: "Indicates that the subject was intellectually or artistically influenced by the object.",
  external_mapping: "P737",  // Wikidata property
  status: "approved",
  created_by: "wikidata_auto",
  created_at: datetime()
})
Workflow Integration
Property/Edge Auto-Mapping:

When a seed/content agent extracts a property or edge from a source, it first queries the registry for a matching definition.

If found, it attaches only the canonical property_id as the edge/property type.

If not found, it creates a candidate entry, including context and proposed mapping, and awaits review or auto-approval processes.

Query Uniformity:

All cross-domain traversals use the property_id, ensuring results span all domains, regardless of source vocabulary.

Extensibility:

The registry is itself versioned and auditable—a living schema backbone for property and edge types.

Summary Table: Combined Agent & Property Registry Layer
Registry	Purpose	Ensures
Agent Registry	One agent per knowledge unit	No duplication/conflict
Property Registry	Unified edge/property schema	Query/traversal consistency
The Property & Edge Registry is the schema backbone for cross-domain semantic alignment.
Every agent writes to and reads from this registry to ensure that relationships and attributes are meaningful, navigable, and analytics-ready across the global knowledge graph.

5.z Universal Required Properties and Edges
In Chrystallum, key node types—such as Person, Organization, and Event—each come with a core set of universal properties and edges that are always expected to be present, regardless of the auto-extracted or contributed content. This ensures cross-domain interoperability, data completeness, and enables robust queries and analytics across all domains.

Purpose
Schema Consistency: Guarantees that all core entities have a baseline set of information, making the graph predictable and integration-friendly.

Cross-Domain Analytics: Supports federated queries, join operations, and visualization without brittle edge-case handling.

Resilience: Even if some information is missing from the source, explicit placeholders ensure schema contracts are respected.

Required Properties Table
Node Type	Required Properties/Edges
Person	birth_date, death_date, gender, occupation, parent, child, spouse, aliases
Organization	founding_date, dissolution_date, type, founder, parent_organization, location
Event	date, location, involved_person, cause, outcome, related_event
Agent and Extraction Protocol
Agents must always check the Property & Edge Registry for these required fields.

During extraction, if a required property/edge is not found in the source:

The agent attempts to infer from structured data or external reference nodes.

If still unavailable, the property must be explicitly set to "unknown" or similar placeholder.

Agents may prompt a user or supervisor only if truly necessary, aiming for full automation but with graceful fallback.

Examples in Practice
When seeding a Person node:

If birth date is missing in extracted data, set: "birth_date": "unknown"

When seeding an Organization node:

If no founder is found, set: "founder": "unknown"

Prompt Pattern for LLM Extractors
“Extract all data for [NodeType: Person]. You must always return: birth_date, death_date, gender, occupation, parents, children, spouse, aliases. If any are missing or ambiguous, set that property to ‘unknown’.”

Summary
The universal required properties and edges are defined in the Property & Edge Registry and serve as a common semantic contract for all agents and node types. This design guarantees a high degree of reliability and coherence in Chrystallum-powered knowledge graphs, making them ready for enterprise, research, and public integration from the start.

# 6. Wikidata Integration Patterns

## 6.1 SPARQL vs Entity JSON

**SPARQL (Wikidata Query Service)**

* Use for: discovery, label search, type‑constrained queries, relationship exploration.
* Returns selected fields; good for interactive querying; heavily rate‑limited.

**Entity JSON (`Special:EntityData`)**

* Use for: full entity dumps with all claims, references, sitelinks.
* Query by QID; returns complete object; suitable for caching.

## 6.2 SPARQL Label Resolution

Example pattern:

* Given a label + type constraint (e.g. “Atmosphere” + instance of “natural environment”), use SPARQL to fetch candidate QIDs.
* Then use Entity JSON to pull full properties for chosen QIDs.

## 6.3 Seeding Nodes from Wikidata

Steps:

1. Resolve label → QID (SPARQL).
2. Fetch entity JSON by QID.
3. Extract key properties (dates, coordinates, related entities).
4. Create graph node with `id = QID`, and a computed `content_hash` for the property set.

Pseudo‑code:

```python
def seed_node_from_wikidata(label, qid, props_to_extract):
    entity_json = fetch_entity_json(qid)
    entity = next(iter(entity_json["entities"].values()), {})
    props = extract_properties(entity_json, props_to_extract)
    content_hash = hash_properties(props)

    node = {
        "id": qid,
        "id_type": "wikidata",
        "qid": qid,
        "label": entity.get("labels", {}).get("en", {}).get("value", label),
        "description": entity.get("descriptions", {}).get("en", {}).get("value", ""),
        "properties": props,
        "content_hash": content_hash,
        "sitelinks": entity.get("sitelinks", {}),
        "source": "wikidata",
        "confidence": 1.0
    }
    return node
```

---

# 7. Text & Document Ingestion Pipeline

## 7.1 High‑Level Workflow

1. **Ingest document** – PDF, markdown, HTML, etc.
2. **Chunk text** – into passages suitable for LLM context.
3. **LLM extraction** – entities, claims, relationships with confidences.
4. **Backbone alignment** – map entities to LCC/LCSH/FAST and QIDs when possible.
5. **Graph seeding** – create Concept, Claim, Event nodes and edges with provenance.
6. **Shell creation** – for related but unexplored concepts.

## 7.2 LLM‑Driven Extraction

Prompt pattern:

* Extract:

  * Entities: `{label, type, confidence, qid_candidate}`
  * Claims: `{claim, entities, confidence, source_sentence}`
  * Relationships: `{source, target, predicate, confidence}`

Use conservative confidence scores and explicit uncertainty markers.

## 7.3 Tables → Nodes

For structured content (e.g. historical timelines, experiment tables):

* Generate a markdown table (e.g. Date, Event, Location, Persons, Significance, Candidate QID, Source).
* Convert each row into an Event node with associated Concept and Claim nodes, using Chrystallum IDs when QIDs are unknown.

---

# 8. Wikidata Feeder: Trusted Contribution

## 8.1 Export Criteria

A node/claim is eligible for Wikidata suggestion if it:

* Has no QID or only a pseudo‑QID.
* Has `confidence_score ≥ 0.80`.
* Has ≥1 supporting reference with metadata (DOI, ISBN, URL).
* Meets a 5W1H completeness threshold.
* (Optionally) has been endorsed by a trusted user.

## 8.2 Export Payload

High‑level structure:

* Labels & descriptions in multiple languages.
* `instance_of` and main subject QIDs.
* Statements (properties with values and qualifiers).
* References (sources, authors, publication data).
* Provenance (who proposed it, timestamp, confidence, pseudo‑QID).

## 8.3 Review and Feedback Loop

* Candidate pool built from eligible nodes.
* Human reviewers adjust, approve, or reject.
* Approved candidates exported to Wikidata (e.g., via QuickStatements).
* Newly assigned QIDs synchronized back into the local graph (pseudo‑QID → canonical QID, with `CANONICALIZED_TO` edges for audit).

---

# 9. Project Status & Implementation Phases

## 9.1 Architecture vs Implementation

**Architecture (this document):**

* ✅ Core mathematical framework (subgraphs, loss, convergence principle).
* ✅ Backbone architecture (LCC/LCSH/FAST/MARC alignment, shell node strategy).
* ✅ Hybrid ID system (QID, Chrystallum ID, composite ID; content hashes).
* ✅ Agent architecture & persistence model (graph as source of truth).
* ✅ Wikidata integration patterns and text ingestion workflows.
* ✅ Base YAML ontology, crosswalk references, and prompt patterns.

**Implementation (separate work):**

* ❌ Core Neo4j (or other) runtime: agent lifecycle, loss computation, debate orchestration.
* ❌ Test suite: unit, integration, convergence and performance testing.
* ❌ UI/frontend: graph visualization, admin tools, analytics.
* ❌ Production hardening: deployment, monitoring, compliance.

## 9.2 Phase Outline

* **Phase 1 – Core System:**
  Backbone‑aligned schema, agents, shell node creation, basic LLM integration, single‑domain example.

* **Phase 2 – Data Integration:**
  Document parsing, extraction pipeline, QID resolution, provenance handling, Wikidata feeder.

* **Phase 3 – Validation:**
  Real‑user tests in a chosen domain; performance and cost benchmarks.

* **Phase 4 – Documentation & Packaging:**
  API documentation, operator guides, developer docs, reference implementation.

---

## Appendix A: Mathematical Notation & Formal Definitions

(*Adapted from the original v3.0 appendices, with `content_hash` replacing `node_id` where appropriate.*)

* **Subgraph definition**, update operator, loss function, and content hash formula
* Symbols and roles for each quantity used in §2

*(You can literally reuse your existing Appendix A with a search‑and‑replace of `node_id` → `content_hash` in the uniqueness formula.)*

---

## Appendix B: Base Ontology & Backbone‑Aligned Schemas

* Base 5W1H ontology (Event, Claim, Concept, Source, etc.).
* Example edge types (HAS_CLAIM, EVIDENCE_FOR, PROTECTS_FROM, EQUIVALENT_THICKNESS, etc.).
* Domain extension example (e.g. historical research) aligned to appropriate LCC classes.

---

## Appendix C: LCC/LCSH/FAST/Wikidata Crosswalk

* Sample crosswalk rows (Atmosphere, Heat Transfer, Cosmic Rays, Concrete, Julius Caesar, Telecommunications, etc.).
* Illustrates how a concept is consistently mapped into LCC, LCSH, FAST, and QID.

---

## Appendix D: Implementation Code Snippets

* `wikidata_client.py` (SPARQL + EntityData helper).
* Shell node creation and expansion functions.
* Content hash generator (previously property‑hash).
* LCC/FAST crosswalk builder.

---

## Appendix E: LLM Prompt Templates

* Entity & claim extraction.
* Markdown table generation for historical/structured data.
* Shell node expansion prompts (taking backbone classification and QID as context).

---

## Appendix F: Glossary

Update a few entries to reflect the new ID posture, for example:

| Term               | Definition                                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| **Agent**          | Autonomous LLM‑driven process that manages a backbone‑aligned subgraph.                           |
| **Backbone**       | Institutional standards (LCC/LCSH/FAST/MARC) governing alignment and relationships.               |
| **Composite ID**   | Identifier built from multiple QIDs plus a hash of contextual properties.                         |
| **Content Hash**   | Deterministic hash of an entity’s identity and properties, used for deduplication and versioning. |
**Pressure (Civic / Epistemic / Structural / Temporal)**  
Heuristic priority signals derived from graph structure, confidence levels, staleness, and usage logs. In the core model these are operationalized as demand and gap scores used for scheduling and prefetch, rather than literal physical fields.
|
| **QID**            | Wikidata identifier (e.g. Q1048 for Julius Caesar).                                               |
| **Shell Node**     | Placeholder node aligned to the backbone but not yet expanded by LLM.                             |
| **Unleafing**      | Process of discovering and adding connections to otherwise isolated (leaf) nodes.                 |
| **Wikidata**       | Global, multilingual, community‑maintained knowledge base.                                        |

---

If you’d like, the next step can be a **companion doc skeleton** for “Roman Republic Domain Pack” or “Obsidian Implementation Guide”, but this core doc should give you a clean, platform‑agnostic center of gravity for the repo.
