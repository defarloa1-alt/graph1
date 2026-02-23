# Chrystallum Logical Architecture Diagram

**Date:** February 22, 2026  
**Status:** Current System Model  
**Purpose:** Conceptual/logical model showing what the system is and how it works

---

## System Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    CHRYSTALLUM KNOWLEDGE GRAPH                  │
│          Scoped Knowledge Workers with Hierarchical            │
│                    Traversal Guardrails                         │
└────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Entity Model (Domain Data)

```
┌─────────────────────────────────────────────────────────────────┐
│ 8 CANONICAL ENTITY TYPES                                        │
│                                                                  │
│ ┌──────────┐  ┌───────┐  ┌───────┐  ┌──────────────┐          │
│ │ PERSON   │  │ EVENT │  │ PLACE │  │ ORGANIZATION │          │
│ └──────────┘  └───────┘  └───────┘  └──────────────┘          │
│                                                                  │
│ ┌────────┐  ┌──────────┐  ┌────────┐  ┌────────────────┐     │
│ │ PERIOD │  │ MATERIAL │  │ OBJECT │  │ SUBJECTCONCEPT │     │
│ └────────┘  └──────────┘  └────────┘  └────────────────┘     │
│                                                                  │
│ All stored as: :Entity {entity_type, entity_cipher, qid, ...}  │
│                                                                  │
│ NO separate :Human, :Organization labels (unified model)        │
│ NO :Work entity type (citations are properties, not entities)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 2: Relationship Model (Connections)

```
┌─────────────────────────────────────────────────────────────────┐
│ WIKIDATA PID RELATIONSHIPS (278 Types Imported)                 │
│                                                                  │
│ (:Entity)-[:P31 {wikidata_pid, canonical_type}]->(:Entity)     │
│           ↑                                                      │
│     Wikidata PID = Edge Type (preserved)                        │
│     Properties = Semantic layer (canonical_type, cidoc_crm)     │
│                                                                  │
│ THREE BUCKETS (Mechanical Classification):                      │
│                                                                  │
│ 1. ATTRIBUTES (60%)                                             │
│    datatype ≠ wikibase-entityid                                │
│    → Stored as node properties                                  │
│    Example: birth_date, coordinates, VIAF_id                   │
│                                                                  │
│ 2. SIMPLE EDGES (33%)                                           │
│    datatype = wikibase-entityid, no cipher qualifiers          │
│    → Relationships: :P31, :P279, :P361, :P47, etc.            │
│    Example: instance_of, part_of, shares_border                │
│                                                                  │
│ 3. NODE CANDIDATES (7%)                                         │
│    datatype = wikibase-entityid + cipher qualifiers            │
│    → FacetClaim nodes (complex, reified)                       │
│    Example: position_held with P580/P582/P1545 qualifiers     │
│                                                                  │
│ Current: 20,091 simple edges, 22,473 node candidates (defer)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 3: Facet Model (Analytical Lenses)

```
┌─────────────────────────────────────────────────────────────────┐
│ 18 CANONICAL FACETS (Dimensions of Analysis)                    │
│                                                                  │
│ ARCHAEOLOGICAL │ ARTISTIC    │ BIOGRAPHIC   │ COMMUNICATION    │
│ CULTURAL       │ DEMOGRAPHIC │ DIPLOMATIC   │ ECONOMIC         │
│ ENVIRONMENTAL  │ GEOGRAPHIC  │ INTELLECTUAL │ LINGUISTIC       │
│ MILITARY       │ POLITICAL   │ RELIGIOUS    │ SCIENTIFIC       │
│ SOCIAL         │ TECHNOLOGICAL                                  │
│                                                                  │
│ NOT partitions - same entity in multiple facets simultaneously  │
│                                                                  │
│ Each facet:                                                     │
│   - Scopes an Agent (POLITICAL_SFA, MILITARY_SFA, etc.)        │
│   - Defines analytical perspective                              │
│   - Determines which properties/relationships matter            │
│                                                                  │
│ Example: Julius Caesar                                          │
│   POLITICAL facet:  Consulships, alliances, power              │
│   MILITARY facet:   Campaigns, battles, command                │
│   BIOGRAPHIC facet: Birth, family, death                       │
│   ECONOMIC facet:   Debts, land grants, wealth                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 4: Claim Model (Assertions with Evidence)

```
┌─────────────────────────────────────────────────────────────────┐
│ FACETCLAIM (Pattern + Citation)                                 │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ COMPOUND CIPHER (Pattern + Attestation)                    │ │
│ │                                                             │ │
│ │ fclaim_pol_a1b2c3d4e5f6g7h8:Q[Heather]:c4e5               │ │
│ │ └─────── pattern ──────────┘└─ citation ┘                 │ │
│ │                                                             │ │
│ │ Pattern (immutable):                                        │ │
│ │   who × what × where × when × facet                        │ │
│ │                                                             │ │
│ │ Citation (provenance):                                      │ │
│ │   author, work_title, page                                 │ │
│ │   NOT separate Work entity                                  │ │
│ │   Just reference strings                                    │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ Properties:                                                      │
│   Pattern:    subject, predicate, object, temporal, location   │
│   Citation:   author, work_title, passage, year                │
│   Quality:    confidence, analysis_layer                        │
│   Meta:       created_by_agent, created_at                      │
│                                                                  │
│ NO source text stored (just structured extraction)              │
│ NO Work entities (just citation properties)                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 5: Meta-Model (Self-Describing Graph)

```
┌─────────────────────────────────────────────────────────────────┐
│ SYSTEM STRUCTURE (Graph Knows Itself)                           │
│                                                                  │
│ (:Chrystallum)                                                  │
│   ├─[HAS_FEDERATION_ROOT]→ 10 Federations                      │
│   │   • Wikidata (hub, taxonomic structure)                    │
│   │   • Pleiades (41,993 ancient places)                       │
│   │   • PeriodO (8,959 temporal periods)                       │
│   │   • LCSH, FAST, LCC (library epistemology)                 │
│   │   • GeoNames, BabelNet, VIAF, WorldCat                     │
│   │                                                              │
│   ├─[HAS_ENTITY_ROOT]→ 8 EntityTypes                           │
│   │   Registry of canonical entity types                        │
│   │                                                              │
│   ├─[HAS_FACET_ROOT]→ 18 Facets                                │
│   │   Registry of analytical dimensions                         │
│   │                                                              │
│   └─[HAS_SUBJECT_ROOT]→ 79 SubjectConcepts                     │
│       • Roman Republic (FS3_WELL_FEDERATED, score: 100)        │
│       • Tethered to: LCSH + FAST + LCC + Wikidata              │
│       • Has 3 active Agents (POLITICAL, MILITARY, SOCIAL)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Process Flow: Extract → Transform → Load → Analyze

```
┌─ EXTRACT (Wikidata) ──────────────────────────────────────────┐
│                                                                 │
│ Checkpoint: 5,000 entities, 342,945 claims                     │
│ Properties: 3,777 unique PIDs                                  │
│ Complete extraction (no filtering)                             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─ TRANSFORM (Mechanical Classification) ────────────────────────┐
│                                                                 │
│ For each claim, check:                                         │
│   1. datavalue.type (entityid vs other)                       │
│   2. qualifiers (cipher-eligible: P580/P582/P585/P276/P1545) │
│                                                                 │
│ Three buckets:                                                 │
│   Bucket 1: Attributes (206K)    → Node properties            │
│   Bucket 2: Simple Edges (114K)  → Relationships              │
│   Bucket 3: Node Candidates (22K) → FacetClaim nodes          │
│                                                                 │
│ NO hardcoded whitelist                                         │
│ NO AI classification                                           │
│ PURE Wikidata data model                                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─ LOAD (Neo4j) ─────────────────────────────────────────────────┐
│                                                                 │
│ Bucket 1 → SET properties on :Entity nodes                    │
│ Bucket 2 → CREATE :P31, :P361, :P39 edges (20,091 created)   │
│ Bucket 3 → CREATE :FacetClaim nodes (deferred)                │
│                                                                 │
│ Edge types = Wikidata PIDs (preserved)                         │
│ Edge properties = Semantic layer (canonical_type added later)  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─ ANALYZE (Backlink Profiles) ──────────────────────────────────┐
│                                                                 │
│ For each entity, compute:                                      │
│   X:  Entity type distribution (what points here)             │
│   X1: Property distribution (how they point)                  │
│   X2: Temporal distribution (when)                            │
│   X3: Facet affinity (which domain)                           │
│                                                                 │
│ Use for:                                                       │
│   - Validate entity types (anomaly detection)                 │
│   - Identify hubs vs leaves                                   │
│   - Predict SFA workload                                      │
│   - Filter temporal noise                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Model: Knowledge Workers

```
┌─────────────────────────────────────────────────────────────────┐
│ AGENTS (Domain-Agnostic Knowledge Workers)                      │
│                                                                  │
│ Agent learns scope:                                             │
│   1. Traverse UP (broader context)                             │
│      Economics → Economic History → Social Science             │
│                                                                  │
│   2. Traverse DOWN (subdivisions)                              │
│      Economics → Ancient Economics → Trade → Supply/Demand     │
│                                                                  │
│   3. Traverse ACROSS (related domains)                          │
│      Economics ↔ Social (status, class)                        │
│      Economics ↔ Political (fiscal policy)                     │
│                                                                  │
│ Agent produces:                                                 │
│   FacetClaims (evidence-based interpretations)                 │
│   Within scope (bounded by discipline guardrails)              │
│   With citations (author, work, passage)                       │
│                                                                  │
│ Example: ECONOMIC_SFA for Roman Republic                       │
│   - Learns: Ancient economics domain via P279/P361 traversal  │
│   - Discovers: Trade routes, taxation, currency               │
│   - Produces: Economic claims with evidence                    │
│   - Bounded: Doesn't reason about military strategy           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Raw Wikidata → Structured Knowledge

```
┌─ WIKIDATA (Training Ground) ───────────────────────────────────┐
│                                                                  │
│ Raw structure with 3,777 properties                            │
│ Hierarchies: P31/P279 (instance/subclass)                      │
│             P361/P527 (part/has_part)                          │
│                                                                  │
│ Claims (assertions): "Q17167 P31 Q11514315"                    │
│ Not truth - just what Wikidata says                            │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ↓ Extract & Transform
┌─ NEO4J GRAPH ───────────────────────────────────────────────────┐
│                                                                  │
│ NODES:                                                          │
│   - 2,600 :Entity (PERSON, PLACE, etc.)                        │
│   - 43K legacy :Period, :Place (need migration)                │
│   - 360 :FacetedEntity (Tier 2)                                │
│   - 0 :FacetClaim (Tier 3 - deferred)                          │
│                                                                  │
│ EDGES:                                                          │
│   - 20,091 :P31, :P279, :P361, etc. (Wikidata PIDs)           │
│   - 278 different PID types                                     │
│   - Properties: wikidata_pid, (canonical_type pending)         │
│                                                                  │
│ META-MODEL:                                                     │
│   - 1 :Chrystallum (system root)                               │
│   - 10 :Federation (authority sources)                         │
│   - 8 :EntityType (type registry)                              │
│   - 18 :Facet (analytical dimensions)                          │
│   - 79 :SubjectConcept (research themes)                       │
│   - 3 :Agent (deployed SFAs)                                   │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ↓ Agent Analysis
┌─ FACETED KNOWLEDGE ─────────────────────────────────────────────┐
│                                                                  │
│ Same entity analyzed through multiple facets:                  │
│                                                                  │
│ Julius Caesar (Q1048):                                         │
│   ├─ POLITICAL facet:  Consulships, alliances, power          │
│   ├─ MILITARY facet:   Gallic Wars, Civil War, strategy       │
│   ├─ BIOGRAPHIC facet: Family, birth, death                   │
│   └─ ECONOMIC facet:   Debts, land distribution               │
│                                                                  │
│ Each facet produces FacetClaims with evidence                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Compound Cipher Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: Entity Cipher (Cross-Subgraph Join)                    │
│                                                                  │
│ ent_{type}_{qid}                                               │
│ ent_per_Q1048 = Caesar across all contexts                    │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ TIER 2: Faceted Cipher (Subgraph Address)                      │
│                                                                  │
│ fent_{facet}_{qid}_{subject}                                   │
│ fent_pol_Q1048_Q17167 = Caesar in POLITICAL facet, RR context │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ TIER 3: Pattern Cipher (Assertion Identity)                    │
│                                                                  │
│ fclaim_{facet}_{pattern_hash}:{citation_id}                   │
│                                                                  │
│ Pattern (who × what × where × when):                           │
│   fclaim_pol_a1b2c3d4e5f6g7h8                                 │
│   ↑ Shared by all sources attesting same pattern              │
│                                                                  │
│ Citation (author + work + page):                               │
│   :Q[Heather]:c4e5                                            │
│   ↑ Specific to this attestation                              │
│                                                                  │
│ Multiple sources → Same pattern, different citations           │
│ Enables: Automatic cross-source corroboration                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Federation & Guardrails

```
┌─────────────────────────────────────────────────────────────────┐
│ FEDERATION TETHERING (Not Truth, But Structure)                │
│                                                                  │
│ Roman Republic (Q17167) tethered to:                           │
│   LCSH:     sh85115055 (Rome--History--Republic)              │
│   FAST:     fst01204885                                        │
│   LCC:      DG254                                              │
│   Wikidata: Q17167                                             │
│   Score:    100 (FS3_WELL_FEDERATED)                          │
│                                                                  │
│ Federations provide:                                           │
│   ┌────────────────────────────────────────┐                  │
│   │ Hierarchical Taxonomy (P279/P361)      │                  │
│   └────────────┬───────────────────────────┘                  │
│                │                                                 │
│                ↓                                                 │
│   ┌────────────────────────────────────────┐                  │
│   │ Discipline Guardrails                  │                  │
│   │ (Agents stay within scope)             │                  │
│   └────────────┬───────────────────────────┘                  │
│                │                                                 │
│                ↓                                                 │
│   ┌────────────────────────────────────────┐                  │
│   │ Traversal Paths (UP/DOWN/ACROSS)       │                  │
│   │ (Agents learn domain boundaries)       │                  │
│   └────────────────────────────────────────┘                  │
│                                                                  │
│ Enables: Multi-hop discovery (senator → mollusk)               │
│ Prevents: Hallucination outside discipline scope               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Example: Processing Historical Passage

```
┌─ INPUT: Heather, "Empires and Barbarians", p. 12 ──────────────┐
│                                                                  │
│ "IN THE SUMMER OF AD 882, close to the Hungarian Plain where   │
│  the River Danube flows between the Alps and the Carpathians,  │
│  Zwentibald, Duke of the Moravians..."                         │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ↓
┌─ MULTI-FACET EXTRACTION ────────────────────────────────────────┐
│                                                                  │
│ MILITARY_SFA extracts:                                         │
│   Event: Capture of Werinhar                                   │
│   Actors: Zwentibald → Werinhar                                │
│   Location: Hungarian Plain                                    │
│   Temporal: 882 AD                                             │
│                                                                  │
│ POLITICAL_SFA extracts:                                        │
│   Position: Zwentibald = Duke of Moravians                     │
│   Polity: Moravians                                            │
│   Political conflict context                                   │
│                                                                  │
│ BIOGRAPHIC_SFA extracts:                                       │
│   Person: Werinhar (son of Engelschalk)                        │
│   Family: Count Wezzilo (relative)                             │
│   Life event: Mutilation                                       │
│                                                                  │
│ GEOGRAPHIC_SFA extracts:                                       │
│   Location: Hungarian Plain, Danube                            │
│   Features: Alps, Carpathians                                  │
│   Spatial context                                              │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ↓
┌─ FACETCLAIM CREATION ───────────────────────────────────────────┐
│                                                                  │
│ Military FacetClaim:                                            │
│   pattern: Zwentibald × captured × Werinhar × 882 × Hung.Plain│
│   citation: Heather, "Empires", p. 12, 2009                   │
│   facet: MILITARY                                              │
│   analysis_layer: retrospective                                │
│                                                                  │
│ Political FacetClaim:                                           │
│   pattern: Zwentibald × holds_position × Duke × 882 × Moravia │
│   citation: Heather, "Empires", p. 12, 2009                   │
│   facet: POLITICAL                                             │
│                                                                  │
│ (+ 3-5 more facets extract relevant aspects)                   │
│                                                                  │
│ ONE passage → MULTIPLE FacetClaims (multi-dimensional)         │
│ NO source text stored (just structured extraction)             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Architectural Principles

1. **Entities NOT Books**
   - No WORK entity type for cataloging
   - Citations as properties (author, title, page)
   - Focus: Domain entities (people, places, events)

2. **Wikidata Preserved**
   - PIDs as edge types (:P31, :P361)
   - Semantic layer additive (canonical_type properties)
   - Raw structure intact (reversible)

3. **Mechanical Classification**
   - datavalue.type determines bucket
   - Qualifier presence determines reification
   - No AI, no guessing

4. **Multi-Dimensional**
   - Same entity in multiple facets
   - Same passage → multiple FacetClaims
   - Each facet sees different aspects

5. **Self-Describing**
   - Graph knows its own structure
   - Meta-model queryable
   - Dynamic schema evolution

6. **Grounded Reasoning**
   - Agents learn scope via traversal
   - Hierarchies provide guardrails
   - Evidence required (citations)

---

## Current State (Feb 22, 2026)

**Nodes:**
- 2,600 :Entity (clean)
- 43,070 legacy :Period/:Place (need migration)
- 360 :FacetedEntity (Tier 2 partial)

**Edges:**
- 20,091 simple edges (Bucket 2)
- 278 PID types
- Avg 16.02 per entity (99.9% connected)
- Thin properties (need canonicalization)

**Ready For:**
- Property canonicalization (stamp canonical_type)
- Legacy node migration (43K nodes)
- Node candidate import (22K FacetClaims)
- Agent training (graph now navigable)

---

**Document Status:** ✅ Logical Architecture Documented  
**Last Updated:** February 22, 2026  
**Purpose:** Complete conceptual model of system structure and operation
