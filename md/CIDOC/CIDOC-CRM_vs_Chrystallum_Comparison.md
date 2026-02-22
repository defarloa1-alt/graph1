# CIDOC-CRM vs. Chrystallum: Do We Need Both?

## Critical Question

**Can CIDOC-CRM do what Chrystallum is trying to do? Should we build on CIDOC-CRM instead of creating a parallel system?**

---

## What CIDOC-CRM Does

### ✅ CIDOC-CRM Strengths

1. **Event-Centric Modeling**
   - Events as primary entities
   - Temporal, spatial, participant relationships
   - Causal chains and event hierarchies

2. **Temporal Modeling**
   - E52_Time-Span with uncertainty handling
   - P4_has_time-span links events to time periods
   - Supports date ranges and precision

3. **Spatial Modeling**
   - E53_Place for geographic locations
   - P7_took_place_at links events to places
   - Place hierarchies and coordinates

4. **Cultural Heritage Focus**
   - Museum/archival integration
   - Object/artifact modeling
   - Provenance tracking

5. **International Standard**
   - ISO 21127:2023
   - Widely adopted
   - Tool ecosystem

---

## What CIDOC-CRM Does NOT Do

### ❌ Key Gaps

1. **No Library Backbone Standards**
   - ❌ No FAST (Faceted Application of Subject Terminology)
   - ❌ No LCC (Library of Congress Classification)
   - ❌ No LCSH (Library of Congress Subject Headings)
   - ❌ No MARC (Machine-Readable Cataloging)

   **Impact:** Cannot directly integrate with library catalogs using standard subject headings

2. **No Systematic Historical Date Handling**
   - ⚠️ Supports temporal data but **not standardized**
   - ❌ No ISO 8601 negative years requirement
   - ❌ Date formats left to implementers
   - ❌ No systematic BCE date handling

   **Impact:** Temporal queries across systems are inconsistent

3. **No Action Structure (Goal/Trigger/Action/Result)**
   - ❌ Generic events without structured action semantics
   - ❌ No goal/trigger/result vocabularies
   - ❌ No narrative structure embedded in events

   **Impact:** Cannot query by action type, goal type, or result type systematically

4. **No Wikidata Alignment**
   - ⚠️ Can link to external vocabularies but not built-in
   - ❌ No systematic entity type → Wikidata QID mapping
   - ❌ No action type → Wikidata alignment

   **Impact:** Requires custom mapping for Wikidata integration

5. **No Proactive Backbone Alignment in Construction**
   - CIDOC-CRM is a **modeling standard**, not a construction methodology
   - Doesn't specify how to use standards during entity extraction

   **Impact:** No guidance on using library standards for disambiguation during KG construction

---

## Chrystallum's Unique Value Propositions

### 1. **Embedded Library Backbone Standards** ⭐ CRITICAL

**What Chrystallum Does:**
```cypher
(entity:Human {
  backbone_fast: 'fst01411640',
  backbone_lcc: 'DG261.C35',
  backbone_lcsh: ['Caesar, Julius'],
  backbone_marc: 'sh85018691'
})
```

**CIDOC-CRM Can't Do:**
- CIDOC-CRM has no FAST/LCC/LCSH/MARC properties
- Would need custom extensions
- No standard way to query by library subject headings

**Verdict:** ✅ **Chrystallum unique** - Critical for library integration

---

### 2. **Systematic ISO 8601 Historical Dates** ⭐ CRITICAL

**What Chrystallum Does:**
```cypher
(event:Event {
  start_date: '-0049-01-10',  // ISO 8601 negative year
  date_precision: 'day',
  temporal_uncertainty: false
})
```

**CIDOC-CRM Can Do (But Doesn't Require):**
```cypher
(event:E5_Event) -[:P4_has_time-span]-> 
(timeSpan:E52_Time-Span {
  // No standard format - left to implementer
  // Could be: "49 BCE", "-49", "-0049-01-10", etc.
})
```

**Verdict:** ⚠️ **CIDOC-CRM supports but doesn't standardize** - Chrystallum's systematic approach is unique

---

### 3. **Action Structure Vocabularies** ⭐ CRITICAL

**What Chrystallum Does:**
```cypher
(relationship:CAUSED {
  goal_type: 'POL',
  goal_type_qid: 'Q7163',
  trigger_type: 'OPPORT',
  action_type: 'MIL_ACT',
  result_type: 'POL_TRANS',
  narrative: '...'
})
```

**CIDOC-CRM Can't Do:**
- Generic events: E5_Event, E7_Activity
- No goal/trigger/action/result structure
- No action type vocabularies

**Verdict:** ✅ **Chrystallum unique** - Structured action semantics

---

### 4. **Wikidata Alignment Built-In** ⭐ IMPORTANT

**What Chrystallum Does:**
- Entity types have Wikidata QIDs
- Action types have Wikidata QIDs
- Systematic alignment

**CIDOC-CRM Can Do:**
- Can link to external vocabularies
- Not built-in or systematic

**Verdict:** ⚠️ **CIDOC-CRM supports but not systematic** - Chrystallum's systematic alignment is unique

---

### 5. **Historical Knowledge Graph Focus** ⭐ IMPORTANT

**What Chrystallum Does:**
- Ancient/medieval history focus
- Historical date handling (BCE)
- Historical period taxonomy

**CIDOC-CRM Can Do:**
- Works for any period
- Not optimized for historical dates

**Verdict:** ⚠️ **Both can do** - But Chrystallum optimized for historical focus

---

## The Real Question: Extend CIDOC-CRM or Build Parallel?

### Option 1: Build on CIDOC-CRM (Recommended) ✅

**Approach:** Use CIDOC-CRM as foundation, extend with Chrystallum's unique features

**Structure:**
```
CIDOC-CRM Core (Events, Temporal, Spatial)
  +
Chrystallum Extensions:
  - FAST/LCC/LCSH/MARC properties
  - Action structure vocabularies
  - Systematic ISO 8601 dates
  - Wikidata alignment
```

**Implementation:**
```cypher
// CIDOC-CRM base
(event:E5_Event) -[:P4_has_time-span]-> (timeSpan:E52_Time-Span)

// Chrystallum extensions
(event:E5_Event {
  // CIDOC-CRM standard
  cidoc_crm_class: 'E5_Event',
  
  // Chrystallum extensions
  backbone_fast: 'fst01411640',
  start_date: '-0049-01-10',  // ISO 8601 systematic
  action_type: 'MIL_ACT',
  goal_type: 'POL'
})
```

**Advantages:**
- ✅ Don't reinvent event-centric model
- ✅ Museum/archival compatibility
- ✅ International standard base
- ✅ Add our unique features as extensions
- ✅ Best of both worlds

**Disadvantages:**
- ⚠️ Must understand CIDOC-CRM
- ⚠️ More complex than pure Chrystallum

---

### Option 2: Pure Chrystallum (Current Approach)

**Approach:** Build independent system with CIDOC-CRM alignment layer

**Advantages:**
- ✅ Simpler initial implementation
- ✅ Focused on our specific needs
- ✅ No CIDOC-CRM learning curve

**Disadvantages:**
- ❌ Reinventing event-centric wheel
- ❌ Less museum/archival integration
- ❌ Not leveraging existing standard

---

## Recommendation: Hybrid Approach

### ✅ Use CIDOC-CRM as Foundation, Extend with Chrystallum Features

**Why:**
1. **CIDOC-CRM handles event modeling** (don't reinvent)
2. **CIDOC-CRM handles temporal/spatial** (solid foundation)
3. **Chrystallum adds library integration** (our unique value)
4. **Chrystallum adds action structure** (our unique value)
5. **Chrystallum adds systematic dates** (our unique value)

**What This Means:**
- Use CIDOC-CRM classes: E5_Event, E21_Person, E53_Place, E52_Time-Span
- Use CIDOC-CRM properties: P4_has_time-span, P7_took_place_at, P11_had_participant
- **Extend** with:
  - `backbone_fast`, `backbone_lcc`, `backbone_lcsh`, `backbone_marc` properties
  - `action_type`, `goal_type`, `trigger_type`, `result_type` properties
  - `start_date` (ISO 8601) alongside P4_has_time-span
  - Wikidata QID mappings

---

## Concrete Implementation

### Chrystallum = CIDOC-CRM + Extensions

```cypher
// CIDOC-CRM Foundation
(crossingEvent: E5_Event {
  label: 'Crossing of the Rubicon'
})

(timeSpan: E52_Time-Span {
  P82a_begin_of_the_begin: '-0049-01-10T00:00:00',
  P82b_end_of_the_end: '-0049-01-10T23:59:59'
})

(rubiconPlace: E53_Place {
  label: 'Rubicon River',
  pleiades_id: '393484'
})

(caesar: E21_Person {
  label: 'Julius Caesar'
})

// CIDOC-CRM relationships
(crossingEvent) -[:P4_has_time-span]-> (timeSpan)
(crossingEvent) -[:P7_took_place_at]-> (rubiconPlace)
(crossingEvent) -[:P11_had_participant]-> (caesar)

// Chrystallum Extensions
(crossingEvent: E5_Event {
  // Library backbone
  backbone_fast: 'fst01411640',
  backbone_lcc: 'DG241-269',
  
  // Systematic ISO 8601 (complements P4_has_time-span)
  start_date: '-0049-01-10',
  date_precision: 'day',
  
  // Action structure
  action_type: 'MIL_ACT',
  action_type_qid: 'Q178561',
  goal_type: 'POL',
  goal_type_qid: 'Q7163',
  result_type: 'POL_TRANS',
  result_type_qid: 'Q10931',
  
  // Wikidata
  qid: 'Q...',
  type_qid: 'Q1656682'  // Event
  
  // Chrystallum metadata
  confidence: 0.95,
  validation_status: 'verified'
})

// Relationship with action structure
(caesar) -[:CAUSED {
  // CIDOC-CRM property mapping
  cidoc_crm_property: 'P11_had_participant',
  
  // Chrystallum action structure
  goal_type: 'POL',
  trigger_type: 'OPPORT',
  action_type: 'MIL_ACT',
  result_type: 'POL_TRANS',
  narrative: '...'
}]-> (crossingEvent)
```

---

## What We Should Do

### ✅ Adopt CIDOC-CRM Core, Extend with Chrystallum Features

**Phase 1: CIDOC-CRM Foundation**
1. Use CIDOC-CRM classes (E5_Event, E21_Person, E53_Place, etc.)
2. Use CIDOC-CRM properties (P4_has_time-span, P7_took_place_at, etc.)
3. Implement CIDOC-CRM event-centric model

**Phase 2: Chrystallum Extensions**
1. Add `backbone_*` properties (FAST/LCC/LCSH/MARC)
2. Add action structure properties (`action_type`, `goal_type`, etc.)
3. Add systematic ISO 8601 dates (`start_date`, `end_date`)
4. Add Wikidata alignment (QIDs for types and entities)

**Phase 3: Best of Both Worlds**
- Query using CIDOC-CRM properties (museum integration)
- Query using library standards (`backbone_fast`, `backbone_lcc`)
- Query using action structure (`action_type`, `goal_type`)
- Query using systematic dates (ISO 8601)

---

## Conclusion

### Answer: Yes, CIDOC-CRM does much of what Chrystallum does, BUT...

**CIDOC-CRM handles:**
- ✅ Event-centric modeling
- ✅ Temporal/spatial relationships
- ✅ Museum/archival integration

**CIDOC-CRM does NOT handle:**
- ❌ Library backbone standards (FAST/LCC/LCSH/MARC)
- ❌ Systematic ISO 8601 historical dates
- ❌ Action structure vocabularies
- ❌ Built-in Wikidata alignment

**Recommendation:**
✅ **Use CIDOC-CRM as foundation, extend with Chrystallum's unique features**

**Result:**
- Don't reinvent the event-centric wheel
- Keep our unique library integration
- Keep our unique action structure
- Keep our systematic date handling
- Get museum/archival compatibility for free

**This is not reinventing the wheel - it's adding wheels to a solid foundation!**



