# SCA Federation Positioning Step — Design Specification v2

**Date:** 2026-02-26  
**Status:** Draft — architect review required  
**Supersedes:** v1 (2026-02-26), Phase 3 A1 FAST ID manual mapping  
**Related:** sca_agent.py, SUBJECT_CONCEPT_AGENTS_GUIDE.md, SUBJECT_CONCEPT_CREATION_AND_AUTHORITY.md

---

## Motivation — The Two Librarians

**The traditional librarian** goes to a catalog, finds a FAST or LCSH heading, and says:

> "Roman Republic — that's DG254, third floor, east wing."

One shelf. One answer. You walk there and find what the library decided belongs together.

**The CCS librarian** — using the Chrystallum Classification System — says:

> "Roman Republic — let me show you its full coordinate space."

- **Political systems shelf** (Dewey 321.804) — next to republic, democracy, oligarchy, dictatorship. Drill up and you reach all systems of government. Drill down and you reach specific republican constitutions across history.

- **Roman history shelf** (DG231) — next to the Roman Kingdom before it and the Empire after. Drill up and you reach ancient Mediterranean civilisations. Drill down and you reach the Gracchi, the Punic Wars, the Social War.

- **Legal systems shelf** (KJA) — next to Roman law, Roman procedure, Roman citizenship. Drill up and you reach ancient legal systems. Drill down and you reach the Twelve Tables, praetorian law, senatorial procedure.

- **Religion shelf** (BL800s) — next to ancient Roman religion, augury, priesthoods. Drill up and you reach ancient Mediterranean religion. Drill down and you reach specific colleges and rituals.

- **CCS-native shelves** that do not physically exist in any library today: patronage networks as a political technology, aristocratic competition as a structural force, the mixed constitution as a historical experiment. These are coordinates grounded in the traditional shelves but synthesised into something more precise for this domain.

And the CCS librarian does not just hand you a list. If you say "I want to go deeper on the constitutional structure," they walk you up the political systems hierarchy to see the comparative context, or down into the specific magistracies and assemblies. Every hierarchy is **navigable in both directions**.

This is what the SubjectConcept container enables. And this is what no single federation system — Dewey, LCSH, FAST, or Wikidata alone — can give you. The CCS is the synthesis.

---

## The Golden Rule

**Every node in the system must be able to answer "What is this?"**

Not just "what are its properties" — but "what kind of thing is it, where does it sit in human knowledge organisation, and how does a researcher find materials about it."

This is not a special enrichment step. It is a **foundational obligation** of every harvesting operation the SCA performs.

---

## Core Architectural Statement

A SubjectConcept is not a thematic label with a QID attached.

It is a **federated resource container** — a pre-assembled bundle of everything an SFA needs to decompose its facet slice of the domain, grounded in the canonical knowledge organisation systems that define where this domain sits in the federated schema landscape.

The container holds:
- The domain root QID and its Wikidata properties
- All classification coordinates across Dewey, LCC, LCSH, FAST
- Typed edges to ClassificationAnchor nodes establishing ontological position
- The modern synthesis — an LLM-proposed, human-curated subject decomposition that is parameterised by the federation coordinates, not free-floating

The SFA receives this container. It does not need to re-orient itself against external systems. Everything it needs to reason about its facet slice is pre-assembled.

---

## Why the Current SubjectConcepts Are Incomplete

The 61 existing SubjectConcepts were proposed by an LLM reasoning from general knowledge about the Roman Republic — "what are the important themes in this domain?" — without any reference to where the domain sits in the federated schema landscape.

They were not generated with federation parameters. There was no curation against canonical classification systems. The result is a well-shaped but ungrounded hierarchy — thematically plausible, not federation-traceable.

Concretely:

- "Elite competition and network power" (Q2063299) — no library shelf. Coordinates scattered across Dewey 321, 305, 937. Boundaries drawn by LLM intuition, not by federation topology.
- "Factions, Patronage Power, and Civil Conflict" (Q20720797) — conflates three things federation systems treat separately.

What should have happened:
1. Run federation positioning on Q17167 first
2. Harvest full coordinate space across all reachable federation systems
3. Give that coordinate map to the LLM as explicit parameters
4. Ask: "given this domain occupies these coordinates, what is the principled decomposition?"

The federation positioning step is the missing foundation. Once it runs, SubjectConcept generation can be re-run or validated against the grounded coordinate space.

---

## The Federated Resource Container

```
SubjectConcept (container) {

  // ── Identity ────────────────────────────────────────────────────────────
  qid:          "Q17167"
  label:        "Roman Republic"
  subject_id:   "subj_roman_republic_q17167"
  primary_facet: POLITICAL

  // ── Wikidata properties (harvested — Layer 1) ────────────────────────────
  // All outbound Wikidata properties harvested from the QID
  // Stored as typed edges to Entity nodes or ClassificationAnchor nodes
  // Examples:
  //   INSTANCE_OF_CLASS → Q1307214 (form of government)
  //   INSTANCE_OF_CLASS → Q11514315 (historical period)
  //   INSTANCE_OF_CLASS → Q3024240 (historical country)
  //   TYPE_ANCHOR       → Q666680  (aristocratic republic)
  //   COMPOSITIONAL_PARENT → Q1747689 (Ancient Rome)
  //   FOLLOWED_BY       → Q2277 (Roman Empire)
  //   HAS_PARTS         → Q2839628, Q6106068, Q2815472 (period subdivisions)

  // ── Federation coordinates (positioned — Layer 1/2) ──────────────────────
  // Classification anchors reachable through the Wikidata P31/P279 chain
  // Each anchor tagged with its originating federation
  dewey:    ["321.804", "937", "340.5", "292"]    // via Q7270, Q11514315...
  lcc:      ["DG231", "JC", "KJA", "BL"]         // via P1149 on ancestor nodes
  lcsh_id:  "sh85115114"                          // direct P244 on Q17167
  fast_id:  (where present on QID or ancestors)

  // ── Classification chain (typed edges to anchors) ────────────────────────
  // Written as graph relationships, not flat properties
  // See Relationship Types section

  // ── Modern synthesis (LLM-proposed, human-curated — Layer 3) ────────────
  // Child SubjectConcepts proposed by LLM reasoning within federation parameters
  // Each proposal traceable to specific federation anchors
  // Human-curated before write
}
```

---

## The Federated Schema Landscape

The Roman Republic is not one thing. It is a coordinate in multiple canonical knowledge organisation systems simultaneously:

| System | Coordinate | Via |
|--------|-----------|-----|
| Dewey | 321.804 | Q17167 → Q666680 → Q7270 → P1036 |
| Dewey | 937 | Q17167 → Q11514315 → P1036 (Roman history) |
| LCC | DG231–269 | History of Rome — Republic |
| LCC | JC | Political theory/institutions |
| LCSH | sh85115114 | Direct P244 on Q17167 |
| FAST | (where present) | Flat subject heading, LCSH-derived |
| Wikidata | Q1307214, Q11514315, Q3024240 | P31 instance of |

Each system reveals different relationships:
- **Dewey** — disciplinary neighbours (what fields of study surround it)
- **LCC** — bibliographic neighbourhood (what is on the shelf next to it)
- **LCSH BT/NT** — conceptual hierarchy (broader and narrower terms)
- **Wikidata P31/P279** — ontological position (what class of thing it is)

No single federation gives the complete picture. The container holds all of them.

---

## Federation-Aware Positioning

The same node means different things depending on which federation's ontology you look through:

- **Wikidata:** instance of form of government, historical period, historical country
- **LCSH:** geographic/period subdivision under Rome
- **Dewey:** coordinate 321.804 within social sciences
- **CIDOC-CRM:** Period, Actor (political entity), Place (territorial entity)

The graph holds **multiple simultaneous ontological positions** — one per federation — without collapsing them into a single canonical answer.

```cypher
(Q17167) -[:POSITIONED_AS {federation: "wikidata", anchor_type: "HistoricalRegime"}]-> (anchor)
(Q17167) -[:POSITIONED_AS {federation: "lcsh",     anchor_type: "GeographicSubdivision"}]-> (anchor)
(Q17167) -[:POSITIONED_AS {federation: "dewey",    anchor_type: "ClassNumber"}]-> (anchor)
```

The SYS_FederationSource nodes are the natural home for federation vocabulary — each federation source knows its own ontological type system.

---

## The Flat List Problem and Three-Layer Resolution

When the SCA fetches backlinks for a classification node (e.g. Q1307214 form of government), it receives a flat list — democracy, monarchy, Roman Republic, triumvirate, unicameralism, protectorate... all collapsed into "links to Q1307214."

This list cannot be deterministically structured. It contains P279 subclass nodes, P31 instance nodes, P361 part-of nodes, associated concepts via other properties, and category meta-nodes — all mixed together.

Typing requires three layers:

| Layer | Method | Confidence | Write behaviour |
|-------|--------|-----------|-----------------|
| 1. Deterministic | Read Wikidata P31/P279/P361/P122 facts | HIGH | Write immediately |
| 2. Constrained rules | Apply SYS_Policy rules (e.g. "DDC 321.* → JC/JF") | MEDIUM | Write with policy citation |
| 3. LLM reasoning | Fill gaps neither Wikidata nor rules resolve | LOW–MEDIUM | Write with reasoning trace, flag for review |

This mirrors the existing confidence-layered claim model. Federation positioning uses the same pattern applied to classification rather than domain facts.

---

## ClassificationAnchor Node Type

Where a classification node does not already exist as an Entity in the graph, the SCA creates a lightweight ClassificationAnchor node. This is not a domain entity — it is a schema coordinate.

```
(:ClassificationAnchor {
  qid:          "Q1307214"
  label:        "form of government"
  dewey:        "321"               // P1036 from Wikidata, if present
  lcc:          "JC"                // P1149 from Wikidata, if present
  lcsh_id:      "sh..."             // P244 from Wikidata, if present
  fast_id:      "fst..."            // P2163 from Wikidata, if present
  anchor_type:  "FormOfGovernment"  // typed classification
  federation:   "wikidata"          // originating federation
})
```

**Rule:** If the target QID already exists as an Entity → use a typed relationship to that Entity. If not → create a ClassificationAnchor node.

ClassificationAnchor nodes are not domain entities. They exist only to carry classification coordinates and are queryable independently of the main entity graph.

---

## Relationship Types

| Relationship | Wikidata source | Semantic meaning |
|-------------|----------------|-----------------|
| `CLASSIFICATION_PARENT` | P279 subclass of | This is a type/subclass of the target |
| `INSTANCE_OF_CLASS` | P31 instance of | This is a specific instance of the target |
| `COMPOSITIONAL_PARENT` | P361 part of | This is part of the target |
| `COMPOSITIONAL_CHILD` | P527 has part | The target is part of this |
| `TYPE_ANCHOR` | P122 basic form of government | The target describes the type of this |
| `POSITIONED_AS` | federation-tagged | Position in a specific federation's ontology |
| `SAME_AS_CANDIDATE` | P460 said to be same as | Possible identity equivalence, requires review |
| `ASSOCIATIVE` | P1269 facet of, other | Related but not strictly hierarchical |

Each relationship carries:
- `via` — Wikidata property ID (P31, P279 etc.)
- `federation` — which system this position belongs to
- `hops` — integer distance from domain root
- `confidence` — HIGH / MEDIUM / LOW
- `reasoning_trace` — (Layer 3) LLM reasoning that produced this edge

---

## How the SFA Uses the Container

The SFA receives the pre-assembled container and reasons within it:

> "I am the POLITICAL SFA. From this container I can see:
> - Dewey 321.804 — my primary classification axis
> - LCSH sh85115114 subdivided by Politics and government
> - Wikidata INSTANCE_OF → form of government → peers: democracy, oligarchy, dictatorship
> - Child SubjectConcepts in my facet: Government and Constitutional Structure, Magistracies, Popular assemblies
> - Federation sources I can query: LC SRU for bibliography, Wikidata SPARQL for entity expansion
>
> I have everything I need to decompose my slice of this domain."

The SFA does not re-orient itself against external systems. It consumes the container.

**This fixes the curation gap.** Instead of asking the LLM "what are the themes in Roman Republic history," the SFA prompt becomes:

*"Given this SubjectConcept container — these Wikidata properties, these Dewey coordinates, these LCSH subdivisions, these classification peers — what is the principled decomposition of this domain from the POLITICAL facet perspective?"*

The LLM's reasoning is parameterised by the federated resource bundle. Its output is grounded. Its proposals are traceable to specific federation anchors. Human curation has a reference frame — not just "does this seem right" but "does this align with coordinate X in system Y."

---

## The Modern Synthesis

An LLM looking at the full coordinate space can propose a subject concept hierarchy that does not exist in any single federation — a post-shelf, post-federation decomposition that:

- Is grounded in canonical federation coordinates
- Synthesises across them into a domain-coherent structure
- Is more precise than any single federation for the purposes of this domain
- Is fully traceable — every proposed SubjectConcept points back to the federation anchors it was derived from

This is the **modern system** — the graph's own subject concept hierarchy, proposed by LLM reasoning within federation parameters, curated by humans, written as the SubjectConcept layer.

The 61 existing SubjectConcepts are a first approximation of this synthesis — proposed without federation parameters. Once the container is assembled, the LLM can validate, restructure, or extend them against the grounded coordinate space.

---

## Revised SCA Pipeline

```
1. Seed QID identified (Q17167)
        ↓
2. Wikidata harvest
   — collect all outbound properties (P31, P279, P361, P122, P244, P2163, P1149, P1036...)
   — collect backlinks (what links to this QID)
   — type each relationship (Layer 1 deterministic)
        ↓
3. Federation positioning
   — traverse P31/P279 chain upward to classification anchors
   — collect Dewey/LCC/LCSH/FAST coordinates at each node
   — write ClassificationAnchor nodes + typed edges
   — tag each position with originating federation
        ↓
4. Container assembly
   — bundle all harvested properties + federation coordinates
   — into SubjectConcept node + relationship structure
   — SubjectConcept is now a federated resource container
        ↓
5. SFA instantiation
   — each SFA receives the container
   — SFA prompt parameterised by federation coordinates
   — LLM decomposes its facet slice within the grounded parameter space
        ↓
6. Proposal generation
   — LLM proposes child SubjectConcepts
   — each proposal traceable to specific federation anchors
   — confidence rated by layer (HIGH/MEDIUM/LOW)
        ↓
7. Human curation
   — proposals reviewed against federation anchors
   — not just "does this seem right" but "does this align with coordinate X in system Y"
        ↓
8. Write
   — approved decomposition written to graph
   — SubjectConcept hierarchy is the modern synthesis
```

Steps 1–4 are the missing foundation. Steps 5–8 are what the current SCA already attempts but without the grounding that 1–4 provides.

---

## FAST IDs on Entity Nodes During Traversal

When the SCA traverses entity QIDs and finds P2163 (FAST ID), that entity has been recognised as something researchers study — FAST has a flat subject heading for it.

All FAST records are subjects. FAST has no hierarchy — it is flat. The hierarchy lives in LCSH (BT/NT), and Wikidata P31/P279 is the graph's proxy for that hierarchy.

When an entity has a FAST ID:
- Directly addressable in the library discovery layer
- No hierarchy walk needed — it already has a subject heading
- Enables bibliography pull from WorldCat and similar systems

When an entity does not have a FAST ID:
- Walk P31/P279 upward to find the nearest classified ancestor
- Record the ancestor's classification anchors with hop distance
- Gives approximate but useful discovery coordinates

---

## Scope for Implementation

**Phase 3 A1 (revised) — proof of concept on Q17167:**

1. Add `position_in_federated_schemas(seed_qid)` method to SCAAgent
2. Run on Q17167 only — prove the pattern before scaling
3. Layer 1 only (deterministic Wikidata traversal)
4. Create ClassificationAnchor nodes for hierarchy parents not in graph
5. Write typed CLASSIFICATION_PARENT / INSTANCE_OF_CLASS / TYPE_ANCHOR / POSITIONED_AS relationships
6. Collect Dewey/LCC/LCSH/FAST anchors at each node
7. Assemble container structure on Q17167 SubjectConcept node
8. Produce positioning report: which systems Q17167 is now addressable from, at what coordinates

**Not in scope for A1:**
- Layer 2 (SYS_Policy rules)
- Layer 3 (LLM gap-filling and modern synthesis)
- Running on all 61 SubjectConcepts
- Full backlink cloud typing
- Re-running SubjectConcept generation with federation parameters
- Multi-federation POSITIONED_AS (start with Wikidata as single proxy, extend later)

---

## Open Questions for Architect

**1. Federation-aware from the start vs Wikidata-first?**

The container model calls for federation-tagged positions from the start (POSITIONED_AS with federation property). But only Wikidata is currently programmatically reachable. LCSH, Dewey, CIDOC-CRM require separate clients.

Options:
- Build federation property into POSITIONED_AS now, populate Wikidata only, extend as clients are built
- Start with untagged positioning edges, add federation tag when second federation comes online

Recommendation: build the property in now. Retrofitting is harder than including from the start. The property can be `"wikidata"` for all A1 writes.

**2. Retype existing INSTANCE_OF edges or write parallel edges?**

The graph already has `(Q17167)-[:INSTANCE_OF]->(Q1307214)`. The new positioning step would write `INSTANCE_OF_CLASS` with enriched properties.

Options:
- Retype existing edges (cleaner, but destructive)
- Write parallel enriched edges, leave existing intact (safe, but duplicates)

Recommendation: parallel edges for now. Retype in a separate cleanup pass after the pattern is validated.

**3. Reasoning trace as relationship property or separate node?**

For Layer 3 writes, the reasoning trace could be a property on the relationship or a separate ReasoningTrace node.

Options:
- Relationship property (simpler, less queryable)
- Separate ReasoningTrace node (queryable, more schema)

Recommendation: relationship property for A1. Migrate to nodes if reasoning trace querying becomes a use case.

**4. What is this according to different federation ontologies?**

The same node means different things in different federation ontologies. The POSITIONED_AS relationship with a `federation` tag handles this — each federation gets its own answer. But the question of which federation ontological type vocabulary to use for `anchor_type` is open.

Options:
- Use Wikidata's own type vocabulary (Q11514315 = "historical period" etc.)
- Define a Chrystallum-internal type vocabulary (HistoricalRegime, FormOfGovernment etc.)
- Use the federation's native vocabulary per federation (CIDOC-CRM E4.Period, LCSH GeographicName etc.)

Recommendation: Chrystallum-internal vocabulary for `anchor_type` on ClassificationAnchor nodes, stored as a controlled list in SYS_Policy. Federation-native vocabulary stored as a separate property (`federation_type`) where known. This keeps the graph's own navigation clean while preserving federation-native semantics.

**5. SubjectConcept re-generation vs validation?**

The 61 existing SubjectConcepts were generated without federation parameters. Once the container is assembled, do we:
- Re-run SubjectConcept generation with federation parameters (principled, potentially disruptive)
- Validate existing 61 against federation coordinates and patch misalignments (conservative, preserves work done)

This is a post-A1 decision. A1 establishes the coordinate space. The re-generation/validation question is scoped to a future phase once the container model is proven.

---

## Refinements from Review (2026-02-26)

### Refinement 1 — Hops Semantics Defined in SYS_Policy

`hops` on POSITIONED_AS relationships must be explicitly defined so agents do not guess. The definition lives in a SYS_Policy node, referenced by all POSITIONED_AS writes.

**Policy node:** `SYS_Policy {name: "FederationPositioningHopsSemantics"}`

```
hops: 0 = self — the domain root QID (Q17167 itself)
hops: 1 = direct parent — immediate P31/P279/P361/P122 target
hops: 2 = grandparent — parent of a direct parent
hops: n = nth ancestor in the traversal chain
```

**Rules:**
- A node can have multiple POSITIONED_AS edges at the same hop distance (via different properties or different chains)
- Hop distance is the **shortest path** from the domain root to that anchor through the traversed properties
- Self-referential positions (e.g. Q17167's own P244 = sh85115114) are hops: 0
- Agents reading the container filter by hops to control how broadly they cast the net

**Cypher pattern for write:**
```cypher
MATCH (sc:SubjectConcept {qid: $domain_qid})
MATCH (anchor:ClassificationAnchor {qid: $anchor_qid})
MERGE (sc)-[r:POSITIONED_AS {
  federation:   $federation,
  anchor_type:  $anchor_type,
  hops:         $hops,
  via:          $wikidata_property,
  confidence:   $confidence
}]->(anchor)
SET r.policy_ref = "FederationPositioningHopsSemantics"
```

---

### Refinement 2 — FederationSource Wired into Positioning Layer

ClassificationAnchor nodes are linked to the SYS_FederationSource that provided them via a `PROVIDES_ANCHOR` relationship. This gives SFAs live handles to the external systems they can call per anchor — not just static coordinates.

**Relationship:**
```cypher
(:SYS_FederationSource) -[:PROVIDES_ANCHOR]-> (:ClassificationAnchor)
```

**Full pattern:**
```cypher
// The positioning edge
(Q17167:SubjectConcept)
  -[:POSITIONED_AS {federation:"wikidata", anchor_type:"HistoricalRegime", hops:0}]->
(anchor:ClassificationAnchor {qid:"Q17167", dewey:"321.804", lcsh_id:"sh85115114"})

// The federation handle
(:SYS_FederationSource {
  name:          "Wikidata",
  base_url:      "https://query.wikidata.org/sparql",
  access_method: "SPARQL",
  status:        "operational"
})
  -[:PROVIDES_ANCHOR]->
(anchor)
```

**What this enables for SFAs:**

When an SFA wants to expand beyond the container — "I need more entities related to this anchor" — it follows:

```cypher
MATCH (sc:SubjectConcept {qid: $qid})
      -[:POSITIONED_AS]->(anchor:ClassificationAnchor)
      <-[:PROVIDES_ANCHOR]-(fed:SYS_FederationSource)
WHERE fed.status = 'operational'
RETURN anchor.qid, anchor.dewey, anchor.lcsh_id,
       fed.name, fed.base_url, fed.access_method
```

The SFA gets both the coordinate and the live client handle in one query. It does not need to hardcode endpoint URLs — they come from the graph.

**For A1:** Only the Wikidata SYS_FederationSource is wired. LCSH, Dewey, FAST sources exist as nodes but PROVIDES_ANCHOR edges are written only when a ClassificationAnchor is actually resolved from that source. As new federation clients are built, they write their own PROVIDES_ANCHOR edges to the anchors they resolve.

---

## Updated Open Questions

The original four open questions plus question 5 (SubjectConcept re-generation vs validation) remain open for architect decision. The two refinements above are adopted as recommendations and reflected in A1 implementation scope.

**Revised A1 implementation checklist:**

- [ ] Add `position_in_federated_schemas(seed_qid)` to SCAAgent — Layer 1 only
- [ ] Create SYS_Policy node `FederationPositioningHopsSemantics` with hops definition
- [ ] Create ClassificationAnchor nodes for Q17167's P31/P279/P122 targets not in graph
- [ ] Write POSITIONED_AS edges with federation, anchor_type, hops, via, confidence, policy_ref
- [ ] Write PROVIDES_ANCHOR edges from Wikidata SYS_FederationSource to each new ClassificationAnchor
- [ ] Assemble container structure on Q17167 SubjectConcept node
- [ ] Produce positioning report: systems Q17167 is addressable from, coordinates, hop distances
- [ ] Update Kanban: phase3-a1-fast-id-resolution card → superseded; new card phase3-a1-federation-positioning
