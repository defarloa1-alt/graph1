# Chrystallum Conceptual Model (Foundation)

**Date:** February 22, 2026  
**Status:** Foundational Architecture  
**Purpose:** Articulate the conceptual model underlying all architectural decisions

---

## Core Concepts

### **SubjectConcept** (Research Theme / Domain Anchor)

**What it is:** A domain of inquiry (Roman Republic, Ancient Economics, Military Strategy)

**Purpose:** Anchor point for scoped investigation

**Tethers to:** 
- LCSH (subject heading)
- FAST (faceted topic)
- LCC (classification)
- Wikidata QID

**Contains:** Entities, events, claims within that domain

**Example:** "Roman Republic" as a research theme encompasses political actors, military events, economic systems, social structures — all analyzed within this scoped context.

---

### **Facet** (Analytical Lens)

**What it is:** A dimension of analysis (POLITICAL, ECONOMIC, SOCIAL, MILITARY, etc.)

**Purpose:** Perspective for interpreting the same entity/event

**18 Canonical Facets:** ARCHAEOLOGICAL, ARTISTIC, BIOGRAPHIC, COMMUNICATION, CULTURAL, DEMOGRAPHIC, DIPLOMATIC, ECONOMIC, ENVIRONMENTAL, GEOGRAPHIC, INTELLECTUAL, LINGUISTIC, MILITARY, POLITICAL, RELIGIOUS, SCIENTIFIC, SOCIAL, TECHNOLOGICAL

**Not:** Physical partition (same entity exists in multiple facets simultaneously)

**Enables:** Scoped reasoning (ECONOMIC_SFA reasons about economic dimension only)

**Example:** Julius Caesar analyzed through:
- POLITICAL facet: consulship, power dynamics, alliances
- MILITARY facet: campaigns, strategy, command
- ECONOMIC facet: debt, land redistribution, fiscal authority
- SOCIAL facet: patrician status, patron-client networks

---

### **Federation** (Authority Tether / Taxonomy Provider)

**What it is:** External classification/authority system (Wikidata, LCSH, FAST, LCC, PeriodO, Pleiades, etc.)

**Purpose:** Grounding in established epistemology

**Role:**
1. Provides hierarchical structure (P279, P361 chains)
2. Creates guardrails (discipline boundaries)
3. Scholarly consensus anchor (not validation)
4. Traversal paths for agent training

**Not:** Source of truth

**10 Federations:**
- **Wikidata** — Universal hub, taxonomic structure
- **LCSH/FAST/LCC/MARC** — Library science epistemology
- **PeriodO** — Temporal bounds
- **Pleiades/GeoNames** — Geographic authority
- **BabelNet** — Multilingual concepts
- **WorldCat/VIAF** — Bibliographic authority

**Example:** Roman Republic tethered to:
- LCSH: sh85115055 (Rome--History--Republic)
- FAST: fst01204885
- LCC: DG254
- Wikidata: Q17167
- Authority score: 100 (FS3_WELL_FEDERATED)

---

### **Claim** (Assertion with Evidence)

**What it is:** A statement about an entity/relationship with provenance

**Structure:** Pattern (who/what/where/when) + Attestation (source/confidence)

**Not:** Fact (it's an assertion to be evaluated)

**Two Types:**
- **InSituClaim:** Ancient source assertion (Plutarch, Polybius, Livy)
- **RetrospectiveClaim:** Modern scholarly interpretation (applies modern theory)

**Properties:**
- Pattern components: subject, predicate, object, temporal_scope, location, facet
- Attestation: source_qid, passage, confidence, analysis_layer
- Provenance: extracted_by, extracted_at

**Example:**
```
Pattern: "Caesar held consulship in Rome, 59 BCE" (POLITICAL facet)
Attestation 1: Plutarch (Lives.Caesar.11, confidence: 0.85, in_situ)
Attestation 2: Suetonius (Jul.20, confidence: 0.90, in_situ)
→ Aggregate confidence: 0.875 (corroboration)
```

---

### **Agent** (Knowledge Worker)

**What it is:** Scoped reasoner (ECONOMIC_SFA, POLITICAL_SFA, etc.)

**Not:** Domain-specific bot (agents are general knowledge workers)

**Capabilities:**
1. **Learn scope** — Traverse hierarchy to understand domain boundaries
2. **Train on structure** — Use federation taxonomy as training scaffold
3. **Learn discipline** — Economics, politics, law, intelligence, etc.
4. **Reason with evidence** — Produce interpretations with citations
5. **Stay within scope** — Bounded by discipline guardrails

**Process:**
- Query federation for discipline structure
- Traverse UP (broader context: Economics → Economic History)
- Traverse DOWN (subdivisions: Ancient Economics → Trade → Supply/Demand)
- Traverse ACROSS (connections: Economic → Social)
- Reason within discovered boundaries
- Produce claims with evidence

**Example:** ECONOMIC_SFA for Roman Republic
- Learns scope: Ancient Economics (via traversal to parent disciplines)
- Understands subdivisions: Trade, taxation, land distribution, currency
- Discovers cross-facet connections: Economic → Social (class status), Economic → Political (fiscal policy)
- Produces claims: "Caesar's debt obligations influenced political alliances" (with evidence from sources)

---

## Relationships Between Concepts (Conceptual Diagram)

```
┌─────────────────────────────────────────────────────────────┐
│ FEDERATION (External Taxonomies)                            │
│ • Wikidata (hierarchical structure via P279/P361)           │
│ • LCSH/FAST/LCC (library epistemology)                      │
│ • PeriodO/Pleiades (temporal/spatial authority)             │
│                                                              │
│ Provides:                                                    │
│   └─ Hierarchical Taxonomy (discipline structure)           │
│       └─ Guardrails (domain boundaries)                     │
│           └─ Traversal Paths (UP/DOWN/ACROSS)               │
└──────────────────────┬──────────────────────────────────────┘
                       │ tethers
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ SUBJECTCONCEPT (Research Theme Anchor)                      │
│ • Roman Republic, Ancient Greece, Medieval Europe           │
│                                                              │
│ Tethered to multiple federations:                           │
│   └─ LCSH + FAST + LCC + Wikidata → FS3_WELL_FEDERATED      │
│                                                              │
│ Contains:                                                    │
│   └─ Entities (people, places, events, objects)             │
│       └─ Connected via Wikidata Claims (raw structure)      │
└──────────────────────┬──────────────────────────────────────┘
                       │ analyzed through
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ FACET (Analytical Lens)                                     │
│ • 18 dimensions: POLITICAL, ECONOMIC, SOCIAL, MILITARY...   │
│                                                              │
│ Not partitions — same entity in multiple facets             │
│                                                              │
│ Each facet:                                                  │
│   └─ Scopes an Agent (ECONOMIC_SFA, POLITICAL_SFA)          │
└──────────────────────┬──────────────────────────────────────┘
                       │ scopes
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ AGENT (Knowledge Worker)                                    │
│ • ECONOMIC_SFA, POLITICAL_SFA, SOCIAL_SFA, etc.             │
│                                                              │
│ Process:                                                     │
│ 1. Learn Scope (traverse federation hierarchy)              │
│    └─ UP: Economics → Economic History                      │
│    └─ DOWN: Economics → Trade → Supply/Demand               │
│    └─ ACROSS: Economics ↔ Social connections                │
│                                                              │
│ 2. Reason Within Bounds (apply facet lens to raw structure) │
│    └─ Bounded by discipline guardrails                      │
│    └─ Grounded in federation taxonomy                       │
│                                                              │
│ 3. Produce Claims (evidence-based interpretations)          │
└──────────────────────┬──────────────────────────────────────┘
                       │ produces
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ CLAIM (Assertion with Evidence)                             │
│ • InSituClaim (ancient source) or RetrospectiveClaim        │
│                                                              │
│ Structure:                                                   │
│   └─ Pattern: who × what × where × when (immutable)         │
│   └─ Attestation: source + passage + confidence (mutable)   │
│                                                              │
│ Enables:                                                     │
│   └─ Corroboration (multiple sources, same pattern)         │
│   └─ Provenance (trace to source)                           │
│   └─ Confidence aggregation (consensus)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Process Flow (Modern Epistemology Construction)

```
┌─ STEP 1: Federation Provides Structure ─────────────────────┐
│                                                              │
│ Wikidata/LCSH/FAST → Hierarchical Taxonomy                  │
│                    → Discipline Boundaries                   │
│                    → Traversal Paths                         │
│                                                              │
│ Example: Wikidata P279 chains                               │
│   Economics → Economic History → Ancient Economics          │
│            → Microeconomics → Supply/Demand Theory          │
└──────────────────────────────────────────────────────────────┘
                       ↓
┌─ STEP 2: SubjectConcept Anchored ───────────────────────────┐
│                                                              │
│ Roman Republic → Tethered to Federations                    │
│               → Grounded in Scholarly Consensus             │
│               → Authority Score: 100 (FS3_WELL_FEDERATED)   │
└──────────────────────────────────────────────────────────────┘
                       ↓
┌─ STEP 3: Raw Structure Extracted ───────────────────────────┐
│                                                              │
│ Wikidata Claims (ALL properties, no whitelist filter)       │
│   → Complete graph structure                                │
│   → Training ground for agents (not truth!)                 │
│   → Enables multi-hop discovery (senator → mollusk)         │
└──────────────────────────────────────────────────────────────┘
                       ↓
┌─ STEP 4: Agent Learns Scope ────────────────────────────────┐
│                                                              │
│ ECONOMIC_SFA:                                                │
│   └─ Traverses UP: Economics → Economic History (context)   │
│   └─ Traverses DOWN: Economics → Ancient → Trade (detail)   │
│   └─ Traverses ACROSS: Economic ↔ Social (connections)      │
│   └─ Discovers boundaries (what's in/out of scope)          │
└──────────────────────────────────────────────────────────────┘
                       ↓
┌─ STEP 5: Agent Reasons Within Scope ────────────────────────┐
│                                                              │
│ Applies ECONOMIC facet lens → To raw Wikidata structure     │
│ Bounded by discipline guardrails                            │
│ Produces claims with evidence                               │
└──────────────────────────────────────────────────────────────┘
                       ↓
┌─ STEP 6: Claims Accumulate ─────────────────────────────────┐
│                                                              │
│ Multiple Agents → Multiple Facets → Multidimensional View   │
│ Multiple Sources → Same Pattern → Corroboration             │
│ Evidence chains preserved → Traceable reasoning             │
└──────────────────────────────────────────────────────────────┘
                       ↓
┌─ STEP 7: Modern Epistemology Emerges ───────────────────────┐
│                                                              │
│ Flexible (not shelf-based classification)                   │
│ BUT Traceable (tethered to federations)                     │
│ AND Grounded (agents bounded by discipline structure)       │
└──────────────────────────────────────────────────────────────┘
```

**Modern vs Traditional:**
- **Traditional:** Rigid shelf classification, single taxonomy, physical constraints
- **Chrystallum:** Flexible multi-faceted, multiple taxonomies, graph-based
- **Trace:** Modern system tethered to traditional epistemology (federations)

**Domain-Agnostic Application:**
- Historical research (current implementation)
- Legal discovery (case law, statutes, precedents)
- Intelligence analysis (sources, assessments, threats)
- Corporate strategy (competitors, markets, opportunities)

**Any domain requiring:** Scoped reasoning, evidence chains, hierarchical grounding, multi-source corroboration

---

**Document Status:** ✅ Conceptual Foundation Documented  
**Maintainers:** Chrystallum Graph Architect  
**Last Updated:** February 22, 2026  
**Purpose:** Foundation for all architectural specifications and decisions
