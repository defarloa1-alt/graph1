# Military SFA Ontology Building Methodology

**Document Status:** Implementation Guide  
**Date:** February 15, 2026  
**Context:** Training Phase - Independent Domain Ontology Building  
**Related:** [SCA_SFA_ROLES_DISCUSSION.md](../SCA_SFA_ROLES_DISCUSSION.md) - Training Phase (lines 230-280)

---

## Overview

This document defines the **filtering methodology** for the Military Specialist Facet Agent (SFA) to extract a clean, disciplinary military ontology from Wikidata during the **Training Phase** (independent domain study).

**Goal:** Build a semantically coherent military ontology grounded in military science as an academic discipline, filtering out Wikidata platform noise, media artifacts, and cross-domain clutter.

**Scope:** Generic military ontology → Roman Republic specialization

---

## 1. Anchor: Military as Discipline

### Disciplinary Root

**Start Node:** `military science (Q192386)`  
**Rationale:** Treat military science as the scholarly discipline root, not "military" as a vague label. Anything not reachable via clear scholarly relations from this node is suspect for ontology design.

**Wikidata:** https://www.wikidata.org/wiki/Q192386  
**Wikipedia:** https://en.wikipedia.org/wiki/Military_science

### Key Properties from Discipline Root

| Property | Purpose | Example Targets |
|----------|---------|-----------------|
| **P279** (subclass of) | Navigate to subfields | strategy, logistics, military history, doctrine, intelligence |
| **P527** (has part) | Canonical components | organization, training, weapon systems, command-and-control |
| **P2670** (has parts of the class) | Class-level composition | institutional structures |
| **P425** (field of this occupation) | Professional roles | officers, military engineers, tacticians |

**Navigation Pattern:**
```
Q192386 (military science)
  ├─[P279]→ military strategy
  ├─[P279]→ military logistics
  ├─[P279]→ military history
  ├─[P527]→ military organization
  ├─[P527]→ weapon systems
  └─[P425]→ military officer (occupation)
```

---

## 2. Inclusion Criteria for Ontology Nodes

A Wikidata item should be **included** in the military ontology if it satisfies **most** of:

### A. Disciplinary Linkage

**Criteria:**
- Is `P279` (subclass of) or `P31` (instance of) a military domain class:
  * military unit
  * battle
  * campaign
  * military doctrine
  * weapon system
  * fortification
  * military rank
  * military formation
  * military strategy
- Has `P425` (field of this occupation) = `military science` or closely related fields:
  * military history
  * defense studies
  * military engineering

**Example:**
```cypher
// Good: Clear disciplinary linkage
(Q21081054:military_unit) -[:P279]-> (Q45382:military_organization)
                                   -[:P279]-> (Q192386:military_science)

// Bad: Weak or no disciplinary connection
(Q12345678:some_category) -[:P31]-> (Q4167836:Wikimedia_category)
```

### B. Role in Explanation (Not Just Metadata)

**Criteria:**
- The concept is **needed to explain** military processes, institutions, or behavior:
  * Strategy levels (tactical, operational, strategic)
  * Order of battle structures (army → corps → division → brigade → battalion)
  * Logistics chains (supply, transport, procurement)
  * Command hierarchy (chain of command, staff organization)
  * Recruitment systems (conscription, volunteers, military service)
  * Training institutions (military academies, training camps)

- Appears in **standard military-science treatments**:
  * Branches: military organization, military strategy, military intelligence, military history
  * Core concepts: combined arms, force concentration, lines of communication, military doctrine

**Test:** Can you cite this concept in a military science textbook or scholarly article? If yes → include. If only exists as metadata → exclude.

### C. Semantic Connectivity

**Criteria:**
- Has **meaningful relations** to other military items via core military properties:
  * `P361` (part of) / `P527` (has part) - compositional structure
  * `P607` (conflict) - participated in military conflict
  * `P241` (military branch) - belongs to branch of service
  * `P410` (military rank) - rank held
  * `P7779` (military unit) - associated unit
  * `P279` (subclass of) - taxonomic position
  * `P31` (instance of) - type classification

- Fits naturally as a **class in a hierarchy** rather than a one-off individual:
  * Good: "legion" (class of military unit)
  * Bad: "Legio X Equestris" (specific instance) - include only if modeling concrete history

**Example:**
```cypher
// Good: Rich semantic connectivity
(Q170944:legion)
  -[:P279]-> (Q45382:military_unit)
  -[:P527]-> (Q82955:cohort)
  -[:P241]-> (Q17167:Roman_Republic)
  -[:P607]-> (Q48314:Gallic_Wars)

// Bad: Orphaned, weak connectivity
(Q87654321:some_image)
  -[:P31]-> (Q4167836:Wikimedia_category)
  -[:P910]-> (Q192386:military_science)  // only via "main category" link
```

---

## 3. Exclusion Criteria to Strip Noise

Systematically **drop** large classes of items that clutter "what links here" around military terms:

### A. Platform / Project Infrastructure

**Exclude:**
- Items where `P31` (instance of) is any Wikimedia/project entity:
  * `Q4167836` - Wikimedia category
  * `Q11266439` - Wikimedia template
  * `Q17633526` - Wikinews article
  * `Q15184295` - Wikimedia module
  * `Q4663903` - Wikimedia portal
  * `Q13406463` - Wikimedia list article

**Rationale:** These are **curation artifacts**, not domain content. They exist to organize the platform, not to represent military concepts.

**Example:**
```cypher
// EXCLUDE: Platform infrastructure
(Q8463221) -[:P31]-> (Q4167836:Wikimedia_category)
           -[:P971]-> (Q192386:military_science)  // "category combines topics"
```

### B. Pure Media Containers

**Exclude:**
- Items where primary `P31` is:
  * Wikimedia Commons category
  * image
  * media file
- **Exception:** If explicitly modeling iconography or visual culture (outside scope of training phase)

**Example:**
```cypher
// EXCLUDE: Media container
(Q87654321:some_image) -[:P31]-> (Q125191:photograph)
                       -[:P180]-> (Q192386:military_science)  // "depicts"
```

### C. Over-Generic or Cross-Domain Properties

**Exclude:**
- Purely generic academic buzzwords:
  * "research" (unless military research institution)
  * "science" (unless military science specifically)
  * "study" (unless military studies)
- Items that only connect via weak edges:
  * `P1269` (facet of) - without other military relations
  * `P910` (main category) - only connection
  * `P1433` (published in) - bibliographic reference only

**Example:**
```cypher
// EXCLUDE: Over-generic connection
(Q12345678:research_methodology) -[:P1269]-> (Q192386:military_science)
                                  // No P279, P527, P607, P241, etc.
```

### D. Orphaned or Weakly Connected Items

**Exclude:**
- Nodes that **do not have any** of the core military properties:
  * `P241` (military branch)
  * `P410` (military rank)
  * `P607` (conflict)
  * `P7779` (military unit)
  * `P361`/`P527` (part of / has part) in a military context
- **AND** only relate through:
  * Category links
  * Commons links
  * Site links (Wikipedia, Wiktionary, etc.)

**Test:** If you strip all Wikimedia platform edges, is the node still connected to the military ontology? If no → exclude.

---

## 4. Structural Filters on Properties

### Property Whitelist (PREFER)

Use these properties to define the "ontology graph cut":

| Property | Code | Purpose | Priority |
|----------|------|---------|----------|
| **subclass of** | P279 | Taxonomic backbone | **HIGH** |
| **instance of** | P31 | Type classification (restricted to military classes) | **HIGH** |
| **part of** | P361 | Compositional structure (unit → formation → army) | **HIGH** |
| **has part** | P527 | Compositional structure (campaign → battles) | **HIGH** |
| **conflict** | P607 | Participated in military conflict | **HIGH** |
| **military branch** | P241 | Branch of service | **HIGH** |
| **military rank** | P410 | Rank held | **HIGH** |
| **military unit** | P7779 | Associated unit | **HIGH** |
| **field of occupation** | P425 | Disciplinary scope | MEDIUM |
| **has parts of the class** | P2670 | Class-level composition | MEDIUM |
| **applies to jurisdiction** | P1001 | Polity/period scope | MEDIUM |

### Property Blacklist (DE-EMPHASIZE or DROP)

Exclude or heavily filter these properties:

| Property | Code | Rationale |
|----------|------|-----------|
| **main Wikimedia portal** | P1151 | Platform navigation |
| **Commons category** | P373 | Media organization |
| **category's main topic** | P301 | Category metadata |
| **topic's main category** | P910 | Category metadata |
| **Commons gallery** | P935 | Media organization |
| **described by source** | P1343 | Bibliographic metadata (unless modeling sources) |
| **image** | P18 | Visual representation (unless modeling iconography) |
| **category combines topics** | P971 | Category logic, not domain logic |

**Implementation Pattern:**
```python
# Whitelist approach
MILITARY_PROPERTIES = {
    'P279',  # subclass of
    'P31',   # instance of
    'P361',  # part of
    'P527',  # has part
    'P607',  # conflict
    'P241',  # military branch
    'P410',  # military rank
    'P7779', # military unit
    'P425',  # field of occupation
    'P2670', # has parts of the class
    'P1001', # applies to jurisdiction
}

# Blacklist approach
WIKIMEDIA_CLASSES = {
    'Q4167836',   # Wikimedia category
    'Q11266439',  # Wikimedia template
    'Q17633526',  # Wikinews article
    'Q15184295',  # Wikimedia module
    'Q4663903',   # Wikimedia portal
    'Q13406463',  # Wikimedia list article
}

def should_include_edge(edge):
    """Filter edges during traversal."""
    if edge.property_id not in MILITARY_PROPERTIES:
        return False
    if edge.target_node.P31 in WIKIMEDIA_CLASSES:
        return False
    return True
```

---

## 5. Roman Republic–Specific Refinement

Once the **generic military ontology skeleton** is in place, **intersect** it with `Roman Republic (Q17167)` via historically meaningful properties.

### Inclusion Criteria (Roman Context)

**Include** items that:

1. **Jurisdictional Linkage:**
   - `P361` (part of) the Roman Republic
   - `P1001` (applies to jurisdiction) = `Q17167` (Roman Republic)

2. **Subclass Specialization:**
   - Are `P279` (subclass of) Roman-specific military formations, ranks, offices, doctrines, or campaigns:
     * Roman legion → legion → military unit
     * Roman centurion → military rank → military personnel
     * Gallic Wars → military campaign → military conflict
     * Roman military tactics → military tactics → military strategy

3. **Temporal Overlap:**
   - `P580` (start time) and `P582` (end time) overlap with Roman Republic period (509 BCE - 27 BCE)
   - Or: No temporal limit specified, but contextually tied to Republican Rome

**Example:**
```cypher
// Roman military ontology
(Q170944:legion)
  -[:P279]-> (Q45382:military_unit)
  -[:P1001]-> (Q17167:Roman_Republic)
  -[:P527]-> (Q82955:cohort)
  -[:P527]-> (Q1541817:manipulus)
  -[:P607]-> (Q48314:Gallic_Wars)

(Q2747456:centurion)
  -[:P279]-> (Q47509:military_rank)
  -[:P1001]-> (Q17167:Roman_Republic)
  -[:P7779]-> (Q170944:legion)
```

### Exclusion Criteria (Anachronisms)

**Exclude** items that:

1. **Temporal Mismatch:**
   - Belong to later Roman periods:
     * Roman Empire (post-27 BCE)
     * Late Antiquity
     * Byzantine Empire
   - **Exception:** If tracing institutional continuity, may include with explicit temporal tagging

2. **Anachronistic Branches:**
   - Modern military science concepts with no Republican-era equivalent:
     * Air force
     * Space force
     * Cyberwarfare
     * Modern operational-level concepts (corps, theater command)
   - **Exception:** If building a **comparative ontology** (ancient vs modern), may include with clear temporal partitioning

3. **Geographic Mismatch:**
   - Military structures of other polities unless modeling interactions:
     * Carthaginian military (include only if modeling Punic Wars)
     * Greek military (include only if modeling Greek influence on Roman tactics)
     * Gallic military (include only if modeling Gallic Wars)

**Example:**
```cypher
// EXCLUDE: Anachronistic
(Q8473:air_force) -[:P279]-> (Q45382:military_organization)
                  // No P1001 → Q17167, no temporal overlap

// EXCLUDE: Wrong polity (unless modeling interaction)
(Q848866:Carthaginian_military) -[:P1001]-> (Q6343:Carthage)
                                 // Only include if modeling Punic Wars
```

---

## 6. Implementation Strategy

### Phase 1: Generic Military Ontology

**Query Pattern:**
```sparql
SELECT ?item ?itemLabel ?property ?value ?valueLabel
WHERE {
  # Start from military science
  ?item (wdt:P279|wdt:P361)* wd:Q192386 .
  
  # Follow whitelisted properties
  ?item ?prop ?value .
  ?property wikibase:directClaim ?prop .
  FILTER(?prop IN (wdt:P279, wdt:P31, wdt:P361, wdt:P527, 
                    wdt:P607, wdt:P241, wdt:P410, wdt:P7779))
  
  # Exclude Wikimedia infrastructure
  FILTER NOT EXISTS { 
    ?item wdt:P31/wdt:P279* wd:Q4167836 .  # Wikimedia category
  }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
```

**Result:** Generic military ontology tree covering:
- Military organization (units, formations, ranks, branches)
- Military strategy (tactics, operations, doctrine, planning)
- Military logistics (supply, transport, procurement, maintenance)
- Military history (campaigns, battles, wars, military revolutions)
- Military technology (weapons, fortifications, military engineering)
- Military personnel (recruitment, training, career structures)

### Phase 2: Roman Republic Specialization

**Query Pattern:**
```sparql
SELECT ?item ?itemLabel ?property ?value ?valueLabel
WHERE {
  # Items from Phase 1 generic military ontology
  ?item (wdt:P279|wdt:P361)* wd:Q192386 .
  
  # Filter for Roman Republic context
  {
    # Direct jurisdiction link
    ?item wdt:P1001 wd:Q17167 .
  } UNION {
    # Part of Roman Republic
    ?item wdt:P361 wd:Q17167 .
  } UNION {
    # Temporal overlap with Republican period
    ?item wdt:P580 ?start .
    ?item wdt:P582 ?end .
    FILTER(YEAR(?start) >= -509 && YEAR(?end) <= -27)
  } UNION {
    # Subclass of Roman-specific military types
    ?item wdt:P279* ?romanClass .
    ?romanClass wdt:P1001 wd:Q17167 .
  }
  
  # Exclude Wikimedia infrastructure
  FILTER NOT EXISTS { 
    ?item wdt:P31/wdt:P279* wd:Q4167836 .
  }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
```

**Result:** Roman Republican military ontology covering:
- Legion structure (cohort, manipulus, centuria)
- Roman ranks (legatus, tribunus, centurion, optio)
- Republican magistracies with imperium (consul, praetor, dictator)
- Theaters and campaigns (Gallic Wars, Punic Wars, Social War, Civil Wars)
- Logistics and recruitment (ager publicus, dilectus, military colonies)
- Tactical innovations (manipular legion → cohort legion, siege techniques)

### Phase 3: Claim Creation (Training Mode)

For each ontology node, the Military SFA creates **Discovery Mode claims** about abstract military concepts:

**Example Claims (Independent, No Cross-Facet Review):**

```
Claim 1: "Legion was primary Roman military unit"
  - Type: Discovery Mode (abstract domain concept)
  - Source: Wikidata Q170944 + scholarly sources
  - Confidence: 0.95
  - Facet: Military
  - SCA Action: Accept as-is (NO QUEUE)

Claim 2: "Cohort composed of multiple maniples"
  - Type: Discovery Mode (abstract structural relationship)
  - Source: Wikidata Q82955, Q1541817
  - Confidence: 0.90
  - Facet: Military
  - SCA Action: Accept as-is (NO QUEUE)

Claim 3: "Centurion commanded century of soldiers"
  - Type: Discovery Mode (abstract organizational principle)
  - Source: Wikidata Q2747456
  - Confidence: 0.95
  - Facet: Military
  - SCA Action: Accept as-is (NO QUEUE)
```

**Rationale:** These are **disciplinary ontology claims**, not concrete historical events. They do not warrant cross-facet review by Political, Economic, or Cultural SFAs during training phase.

---

## 7. Validation Checklist

Before promoting a Wikidata item to the ontology, verify:

### Inclusion Checks (MUST PASS ≥3)

- [ ] Has `P279` or `P31` linking to military domain class
- [ ] Has `P425` = military science or related field
- [ ] Appears in military science scholarly treatments
- [ ] Has meaningful `P361`/`P527`/`P607`/`P241`/`P410` relations
- [ ] Fits naturally as a class in hierarchy
- [ ] Needed to explain military processes or institutions

### Exclusion Checks (MUST FAIL ALL)

- [ ] `P31` is Wikimedia infrastructure class
- [ ] Only connects via category/Commons/site links
- [ ] Orphaned (no core military properties)
- [ ] Over-generic buzzword without military specificity
- [ ] Pure media container (image, category)
- [ ] Anachronistic (for Roman Republic specialization)

### Quality Threshold

**Minimal Acceptable Node:**
- At least 1 taxonomic edge (`P279`)
- At least 1 compositional edge (`P361` or `P527`)
- NOT a Wikimedia infrastructure item
- Reachable from `Q192386` (military science) via whitelisted properties

**High-Quality Node:**
- Multiple taxonomic edges forming clear hierarchy
- Rich compositional structure
- Multiple semantic relations (`P607`, `P241`, `P410`)
- Documented in scholarly sources (`P1343`)
- Clear Roman Republic linkage (`P1001`, `P361`)

---

## 8. Expected Ontology Structure

### Top-Level Branches (from Q192386)

```
military science (Q192386)
├── military organization
│   ├── military unit
│   │   ├── legion (Roman Republican specialization)
│   │   │   ├── cohort
│   │   │   ├── manipulus
│   │   │   └── centuria
│   │   ├── army
│   │   └── military formation
│   ├── military rank
│   │   ├── centurion (Roman)
│   │   ├── tribune (Roman)
│   │   └── legatus (Roman)
│   └── military branch
│       ├── infantry
│       └── cavalry
├── military strategy
│   ├── military tactics
│   │   ├── battle tactics
│   │   └── siege warfare
│   ├── military doctrine
│   └── operational art
├── military logistics
│   ├── supply lines
│   ├── military procurement
│   └── military transport
├── military history
│   ├── military campaign
│   │   ├── Gallic Wars (Roman Republican)
│   │   ├── Punic Wars (Roman Republican)
│   │   └── Roman Civil Wars
│   └── battle
│       ├── Battle of Cannae
│       └── Battle of Alesia
├── military technology
│   ├── weapon
│   │   ├── gladius (Roman)
│   │   └── pilum (Roman)
│   └── fortification
│       ├── Roman military camp
│       └── Roman siege works
└── military intelligence
    ├── reconnaissance
    └── military intelligence gathering
```

### Ontology Statistics (Expected)

**Generic Military Ontology:**
- ~500-1,000 core concepts
- ~50-100 top-level classes
- ~2,000-5,000 edges (after filtering)

**Roman Republic Specialization:**
- ~100-200 Roman-specific concepts
- ~20-30 Republican-era institutions
- ~50-100 campaigns, battles, magistracies
- ~500-1,000 edges (after filtering)

---

## 9. Integration with SCA Workflow

### Training Phase (Current)

**SFA Actions:**
1. Execute filtered Wikidata queries (Phases 1-2 above)
2. Build generic military ontology skeleton
3. Specialize for Roman Republic
4. Create Discovery Mode claims about abstract concepts
5. Submit claims to SCA

**SCA Actions:**
1. Receive Military SFA claims
2. Validate: Are these abstract domain concepts? (YES)
3. Accept claims as-is (**NO QUEUE** to other SFAs)
4. Integrate into graph

**Rationale:** Political, Economic, Cultural SFAs do not need to review "legion composed of cohorts" during training phase. This is disciplinary ontology building, not concrete historical analysis.

### Operational Phase (Future)

When Military SFA encounters **concrete events** (e.g., "Caesar commanded legion at Alesia in 52 BCE"), SCA will evaluate for multi-facet review:

**SCA Evaluation:**
- Abstract vs Concrete: Concrete event (includes named individual, date, location)
- Multi-Domain Relevance:
  * Military: 1.0 (creator)
  * Political: 0.9 (Caesar = magistrate with imperium)
  * Economic: 0.7 (siege → resource allocation)
  * Cultural: 0.3 (minor impact)
- **Action:** Queue to Political SFA (0.9) and Economic SFA (0.7), skip Cultural SFA (0.3)

---

## 10. References

### Wikidata
- Military Science (Q192386): https://www.wikidata.org/wiki/Q192386
- Roman Republic (Q17167): https://www.wikidata.org/wiki/Q17167
- Legion (Q170944): https://www.wikidata.org/wiki/Q170944
- Property List: https://www.wikidata.org/wiki/Wikidata:List_of_properties/all_in_one_table

### Wikipedia
- Military Science: https://en.wikipedia.org/wiki/Military_science
- Category:Military Science: https://en.wikipedia.org/wiki/Category:Military_science
- Roman Republic: https://en.wikipedia.org/wiki/Roman_Republic

### Project Documentation
- [SCA_SFA_ROLES_DISCUSSION.md](../SCA_SFA_ROLES_DISCUSSION.md) - Two-phase SFA workflow
- [CLAIM_WORKFLOW_MODELS.md](../CLAIM_WORKFLOW_MODELS.md) - Training vs Operational modes
- [facet_registry_master.json](facet_registry_master.json) - Military facet configuration

---

## Next Steps

1. **Implement Wikidata Query Service Integration**
   - SPARQL endpoint connection
   - Property whitelist/blacklist enforcement
   - Wikimedia class filtering

2. **Build Ontology Extraction Pipeline**
   - Phase 1: Generic military ontology
   - Phase 2: Roman Republic specialization
   - Phase 3: Claim generation (Discovery Mode)

3. **Validate Ontology Quality**
   - Run validation checklist on sample nodes
   - Measure noise reduction (before vs after filtering)
   - Verify semantic coherence

4. **Test Training Phase Independence**
   - Military SFA builds ontology without other SFAs
   - SCA accepts all claims as-is (no queuing)
   - Measure efficiency vs previous automatic queuing

5. **Prepare for Operational Phase**
   - Define concrete event detection criteria
   - Implement multi-domain relevance scoring
   - Test selective queue with "Caesar at Alesia" example

---

**Status:** Ready for implementation - Military SFA's filtering methodology fully specified
