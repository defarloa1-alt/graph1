# SCA Federation Positioning Step — Design Specification v3

**Date:** 2026-02-26  
**Status:** Adopted — incorporates review feedback and proof-of-concept findings  
**Supersedes:** v2 (2026-02-26)  
**Related:** sca_agent.py, SUBJECT_CONCEPT_AGENTS_GUIDE.md, FEDERATION_POSITIONING_VERIFICATION_2026-02-26.md

---

## Formal Definitions

### SubjectConcept

A **SubjectConcept** is a **topic container**, not an entity. It represents a domain or theme that researchers study — "Roman Republic," "aristocratic competition," "magistracies." It holds federation coordinates and the modern synthesis. It is not a person, place, or thing in the world; it is a coordinate in knowledge organisation space.

**Identity rule:** SubjectConcept has `qid` (Wikidata QID of the topic) and `subject_id` (Chrystallum canonical). It does not represent the entity Q17167 as a historical polity — it represents the *topic* "Roman Republic" as a research domain.

### Entity

An **Entity** is a domain object — person, place, event, work. It has a QID and exists in the harvest graph. Entities can be targets of POSITIONED_AS when they serve as classification anchors (e.g. Q1307214 form of government). Provenance is implicit: if it has a QID, it came from Wikidata (or another federation). No PROVIDES_ANCHOR needed.

### ConceptAnchor vs NotationAnchor

**ConceptAnchor** — a classification coordinate that has identity (QID). May be an Entity node already in the graph, or a ClassificationAnchor node created when the QID is not yet harvested. Provenance is self-evident from the QID.

**NotationAnchor** — a classification coordinate that is notation-only (Dewey 321.804, LCC DG231, LCSH sh85115114). No QID. Exists only as a schema coordinate. Provenance is *not* self-evident — requires PROVIDES_ANCHOR to wire back to the federation that provided it.

**Split rule:** ConceptAnchors that are Entity nodes do not get PROVIDES_ANCHOR. NotationAnchors (and ConceptAnchors that are ClassificationAnchor nodes) always get PROVIDES_ANCHOR. This is the finding from the Q17167 proof of concept: all 6 targets were Entity nodes, so no PROVIDES_ANCHOR was written. The container is still addressable; the handle is implicit.

### POSITIONED_AS

**Discovery only, not hierarchy.** POSITIONED_AS establishes where a SubjectConcept sits in a federation's ontology for discovery and orientation. It does not assert hierarchy (broader/narrower) — that is a separate concern. POSITIONED_AS says "this topic is addressable at this coordinate." It does not say "this topic is a subclass of that."

---

## Provenance

Two streams, never mixed:

| Stream | Property | Meaning |
|--------|----------|---------|
| **wikidata_asserted** | `source_claim` | Direct assertion from Wikidata (P31, P279, P244, etc.). The federation made the claim. |
| **federation_retrieved** | `source_claim` | Retrieved via federation client (SPARQL, SRU, API). We fetched it; the federation did not assert it to us. |

Every coordinate in the container carries a `source_claim` that distinguishes these. When a federation retrieves its own coordinate directly (Stream 2), that carries more authority than Wikidata's crosswalk assertion (Stream 1). See Conflict handling.

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
- Typed edges to Entity nodes or ClassificationAnchor nodes (ConceptAnchor or NotationAnchor)
- The modern synthesis — an LLM-proposed, human-curated subject decomposition that is parameterised by the federation coordinates, not free-floating

The SFA receives this container. It does not need to re-orient itself against external systems. Everything it needs to reason about its facet slice is pre-assembled.

---

## Required SubjectConcept Fields

| Field | Purpose |
|-------|---------|
| `qid` | Wikidata QID of the topic |
| `label` | Human-readable label |
| `subject_id` | Chrystallum canonical ID |
| `kind` | Topic type (domain, theme, subdivision) |
| `scope_note` | What this topic covers; boundaries |
| `retrieval_intent` | What an SFA should retrieve when reasoning about this topic |
| `primary_facet` | Primary facet for this topic (retained; facet-neutrality expressed in Definitions) |

**Resolved:** Retain `primary_facet`. Rename to `seed_facet` was considered for facet-neutrality signal, but that signal is better carried by the Definitions section (SFAs take slices; container doesn't belong to a facet). Rename cost outweighs conceptual gain.

---

## Proof of Concept Findings (2026-02-26)

**Live graph confirmed:** 6 POSITIONED_AS edges from Q17167 to Entity nodes. SYS_Policy `FederationPositioningHopsSemantics` exists. Addressability validated.

**PROVIDES_ANCHOR rule (adopted):** Only for ConceptAnchor and NotationAnchor nodes, *not* for Entity nodes. Entity nodes have implicit provenance (QID). When all targets are Entity nodes — as in the Q17167 run — no PROVIDES_ANCHOR edges are written. The container is still addressable; the federation handle is implicit.

**NotationAnchor nodes:** Live SPARQL dry run (2026-02-26) surfaced LCSH (sh85115114 self, n79039816 on Q1747689) and FAST (1754964 on Q1747689). Dewey/LCC: none found on Q17167 or parents in Wikidata. Create NotationAnchor when notation present on self or ancestor; no rule inference in Layer 1.

**hops=0 for LCSH sh85115114:** **Resolved.** Live SPARQL dry run (2026-02-26) confirms the script writes hops=0 [SELF] with LCSH=sh85115114. Yes.

**61 existing SubjectConcepts disposition:** See "61 SubjectConcepts Validation Workflow" below.

---

## The Federated Resource Container

```
SubjectConcept (container) {

  // ── Identity ────────────────────────────────────────────────────────────
  qid:            "Q17167"
  label:          "Roman Republic"
  subject_id:     "subj_roman_republic_q17167"
  kind:           "domain"
  scope_note:     "Ancient Roman state 509 BCE – 27 BCE"
  retrieval_intent: "entities, events, and relationships within this period"
  primary_facet:  POLITICAL

  // ── POSITIONED_AS (discovery only) ─────────────────────────────────────
  // To Entity (ConceptAnchor) or ClassificationAnchor (ConceptAnchor/NotationAnchor)
  // Examples from Q17167 proof of concept:
  //   INSTANCE_OF_CLASS → Q1307214 (Entity)
  //   INSTANCE_OF_CLASS → Q11514315 (Entity)
  //   TYPE_ANCHOR       → Q666680 (Entity)
  //   COMPOSITIONAL_PARENT → Q1747689 (Entity)

  // ── Federation coordinates ──────────────────────────────────────────────
  dewey:    ["321.804", "937", "340.5", "292"]
  lcc:      ["DG231", "JC", "KJA", "BL"]
  lcsh_id:  "sh85115114"
  fast_id:  (where present)

  // ── Modern synthesis (Layer 3) ───────────────────────────────────────────
  // supporting_anchors, claim_type, reasoning_trace — see data contract below
}
```

---

## Modern Synthesis Data Contract

| Field | Type | Purpose |
|-------|------|---------|
| `supporting_anchors` | list of anchor refs | Federation anchors this proposal is derived from |
| `claim_type` | controlled vocabulary | `wikidata_asserted` \| `federation_retrieved` \| `rule_inferred` \| `llm_reasoned` \| `human_curated` |
| `reasoning_trace` | text | LLM reasoning that produced this proposal (Layer 3) |

**Conflict handling:** Store all coordinates; never force canonical. SFAs choose per facet. When conflicts must be resolved, precedence is:

```
human_curated > federation_retrieved > rule_inferred > wikidata_asserted > llm_reasoned
```

Rationale: When a federation retrieves its own coordinate directly (Stream 2), that carries more authority than Wikidata's crosswalk assertion (Stream 1). Document conflict in `reasoning_trace` or `scope_note`.

---

## PROVIDES_ANCHOR Rule (v3)

```
(:SYS_FederationSource) -[:PROVIDES_ANCHOR]-> (:ConceptAnchor | :NotationAnchor)
```

**Not** to Entity nodes. Entity nodes have QID; provenance is implicit. PROVIDES_ANCHOR is for anchors whose provenance is not self-evident — NotationAnchors (Dewey, LCC, LCSH notation) and ConceptAnchors that are ClassificationAnchor nodes (created when target QID not yet in graph).

---

## ClassificationAnchor and NotationAnchor

**ConceptAnchor** — has QID. May be Entity or ClassificationAnchor node. No PROVIDES_ANCHOR when Entity.

**NotationAnchor** — notation only (dewey, lcc, lcsh_id, fast_id). No QID. Always ClassificationAnchor node. Always gets PROVIDES_ANCHOR from the federation that provided the notation.

NotationAnchor nodes are created when live Wikidata SPARQL returns P1036/P1149/P244/P2163 on ancestor nodes. The stubbed write did not create them — all targets were Entity nodes. Full run will.

---

## Relationship Types

| Relationship | Wikidata source | Semantic meaning |
|-------------|----------------|-----------------|
| `CLASSIFICATION_PARENT` | P279 | This is a type/subclass of the target |
| `INSTANCE_OF_CLASS` | P31 | This is a specific instance of the target |
| `COMPOSITIONAL_PARENT` | P361 | This is part of the target |
| `COMPOSITIONAL_CHILD` | P527 | The target is part of this |
| `TYPE_ANCHOR` | P122 | The target describes the type of this |
| `POSITIONED_AS` | federation-tagged | Position for discovery; not hierarchy |
| `SAME_AS_CANDIDATE` | P460 | Possible identity equivalence |
| `ASSOCIATIVE` | P1269 | Related but not strictly hierarchical |

Each carries: `via`, `federation`, `hops`, `confidence`, `policy_ref`, `reasoning_trace` (Layer 3).

---

## Revised SCA Pipeline

```
1. Seed QID identified
2. Wikidata harvest (Layer 1)
3. Federation positioning — traverse P31/P279, write POSITIONED_AS to Entity or ClassificationAnchor
4. Container assembly — bundle into SubjectConcept
5. SFA instantiation — container parameterises prompt
6. Proposal generation — LLM proposes child SubjectConcepts
7. Human curation — against federation anchors
8. Write — approved decomposition
```

---

## 61 SubjectConcepts Validation Workflow

**Validation-first, re-generation as escalation path.** After federation positioning runs on all 61, each SubjectConcept is scored against its coordinate space automatically. Three outcomes:

| Outcome | Meaning | Action |
|---------|---------|--------|
| **Confirmed** | Coordinates align with existing SubjectConcept boundaries | No change needed |
| **Restructure candidate** | Coordinates suggest boundary adjustment (merge, split, re-parent) | Flag for human review with specific coordinate evidence |
| **Re-generate candidate** | Coordinates suggest SubjectConcept conflates two distinct federation regions | LLM proposes replacement with federation parameters; human adjudicates |

Full re-generation of all 61 is triggered only if validation produces an unacceptable number of re-generate candidates — architect sets that threshold. Preserves work, uses coordinate frame as referee, keeps human curation in the loop at the right granularity.

---

## Scope for Next Run

- Run `sca_federation_positioning.py` (live SPARQL) on all 61 SubjectConcepts
- Create NotationAnchor nodes where Dewey/LCC/LCSH/FAST present on ancestors
- Write PROVIDES_ANCHOR to NotationAnchors and new ConceptAnchors (ClassificationAnchor nodes)
- Validate 61 existing SubjectConcepts against federation coordinates; patch misalignments

---

## Open Questions — All Resolved

1. ~~**hops=0 for LCSH sh85115114**~~ — **Resolved.** Script writes it. Confirmed in live dry run.

2. ~~**seed_facet vs primary_facet**~~ — **Resolved.** Retain `primary_facet`; facet-neutrality expressed in Definitions.

3. ~~**Conflict resolution precedence**~~ — **Resolved.** See Conflict handling in Modern Synthesis Data Contract.

4. ~~**NotationAnchor creation trigger**~~ — **Resolved.** Create when notation present on self or ancestor (from Wikidata). No rule inference in Layer 1.

5. ~~**61 SubjectConcepts — full re-generation or validation-only?**~~ — **Resolved.** Validation-first; re-generation as escalation path. See 61 SubjectConcepts Validation Workflow.
