# SCA Process - Precise Narrative

**What the scripts actually did, step by step**  
**This is the behavior SCA agents should follow**

---

## 📋 STEP-BY-STEP PROCESS

### **STEP 1: INITIAL QID FETCH** (wikidata_full_fetch_enhanced.py)

**Input:** Single QID (Q17167 - Roman Republic)

**Actions:**
1. Fetch entity data from Wikidata API
2. Extract all claims (properties and values)
3. Collect ALL referenced QIDs (from property values, qualifiers, references)
4. Batch fetch labels for ALL QIDs (50 at a time to avoid rate limits)
5. Resolve every QID to its label throughout the data structure

**Output:**
- Complete entity with 61 properties
- ALL property IDs have labels (P31 → "instance of")
- ALL value QIDs have labels (Q11514315 → "historical period")
- ALL qualifier QIDs have labels
- File: Enhanced JSON with 119 QIDs resolved

**Key Discovery:**
```
Q17167 (Roman Republic)
  P31: Q11514315 (historical period), Q1307214 (form of government), 
       Q48349 (empire), Q3024240 (historical country)
  P361: Q1747689 (Ancient Rome)
  P527: Q2839628 (Early), Q6106068 (Middle), Q2815472 (Late)
```

**Data:** Labels ALWAYS included with IDs

---

### **STEP 2: TAXONOMY EXTRACTION** (wikidata_taxonomy_builder.py)

**Input:** Enhanced entity data

**Actions:**
1. Parse entity's claims_with_labels
2. Extract specific relationship properties:
   - P31 (instance of) → parents/classification
   - P279 (subclass of) → parent classes
   - P361 (part of) → parent context
   - P527 (has parts) → children
   - P2579 (studied by) → academic
   - P155/P156 (succession) → timeline
3. Organize into taxonomy structure
4. Create tables showing relationships

**Output:**
```
PARENTS (what it IS):
  - P31 → historical period, form of government, empire, country
  - P361 → Ancient Rome

CHILDREN (what it HAS):
  - P527 → Early, Middle, Late Roman Republic

SUCCESSION:
  - P155 → Roman Kingdom (before)
  - P156 → Roman Empire (after)

ACADEMIC:
  - P2579 → NOT on Q17167 (found on parent Q1747689)
```

**Key Discovery:** Roman Republic has NO P279 (subclass of), NO P2579 (studied by)  
**Data:** All values with labels (QID + label)

---

### **STEP 3: RECURSIVE 5-HOP EXPLORATION** (wikidata_recursive_taxonomy.py)

**Input:** Root QID (Q17167)

**Actions:**
1. **Fetch root entity** (Q17167)
2. **Explore UPWARD** (5 hops):
   - For each P31, P279, P361 value found
   - Fetch that entity
   - Recursively get ITS P31, P279, P361 values
   - Continue for 5 hops
   - Cache to avoid duplicates
3. **Explore DOWNWARD** (5 hops):
   - For each P527, P150 value found
   - Fetch that entity
   - Recursively get ITS P527, P150 values
   - Continue for 5 hops
4. **Explore SUCCESSION**:
   - Fetch P155 (follows) targets
   - Fetch P156 (followed by) targets

**Process details:**
- Start: 1 entity (Q17167)
- Hop 1 Up: 5 parents found → fetch 5 entities
- Hop 2 Up: 18 grandparents found → fetch 18 entities
- Hop 3-5 Up: ~70+ great-grandparents → fetch ~70 entities
- Hop 1 Down: 3 children → fetch 3 entities
- Hop 2-5 Down: 0 (children are leaf nodes)
- Succession: 3 entities → fetch 3 entities
- **Caching:** Circular references prevented (e.g., form of government ↔ monarchy)

**Output:**
- 100 unique entities (total)
- 600 relationships mapped
- ~5,000 property values collected
- File: 3.3 MB JSON with complete data

**Key Discovery:**
- Upward explosion: 1 → 5 → 18 → 70+ (exponential)
- Downward termination: 1 → 3 → 0 (dead end)
- Result: 93 abstract concepts, 7 concrete historical entities

**Data:** Every entity has full labels for all properties and values

---

### **STEP 4: BACKLINKS DISCOVERY** (wikidata_backlinks_explorer.py)

**Input:** Target QID (Q11514315 - historical period)

**Actions:**
1. SPARQL query: Find ALL entities with P31 (instance of) → Q11514315
2. Limit: 100 results (Wikidata default)
3. For each result:
   - Get QID + label
   - Fetch key temporal properties (P580, P582, P571, P576, P585)
   - Classify as: period, event, concept, other
4. Triage into buckets

**Output:**
- 89 periods (have start+end dates)
- 5 concepts (abstract)
- 6 other (mixed)
- 0 events (all had temporal ranges)

**Key Discovery:**
- Q41493 (ancient history) is BOTH period AND field of study
- Q17167 (Roman Republic) in the list (validates our approach)
- Many periods: Chinese dynasties, Medieval periods, Modern conflicts

**Data:** All with QID + label

---

### **STEP 5: CLASSIFICATION ENRICHMENT** (enrich_periods_with_classifications.py)

**Input:** 89 historical periods from backlinks

**Actions:**
1. For each of 89 periods:
   - Fetch entity data from Wikidata
   - Extract P31 (instance of) values with labels
   - Extract P279 (subclass of) values with labels
   - Extract P361 (part of) values with labels
2. Add delays between requests (2 sec) to avoid rate limits
3. Track successes and failures

**Output:**
- 77 periods successfully enriched (86.5%)
- 12 periods failed (rate limit 429 errors)
- File: JSON with P31/P279/P361 for each

**Key Discovery:**
```
Patterns:
  - P361 (part of) reveals hierarchies:
    - High/Late Middle Ages → part of → Middle Ages
    - Edo/Nara periods → part of → history of Japan
    - Roman Kingdom → part of → ancient history
  
  - P279 (subclass of) reveals classifications:
    - Middle Ages → subclass of → ancient history
    - France early modern → subclass of → history of France
  
  - P31 (instance of) reveals multiple types:
    - Roman Republic: period + government + empire + country
    - Ancient Greece: period + civilization + culture + archaeological culture
```

**Data:** All P31/P279/P361 values with labels

---

### **STEP 6: GEOGRAPHIC ANALYSIS** (analyze_geographic_properties.py)

**Input:** 100 entities from 5-hop JSON

**Actions:**
1. For each entity in 5-hop data:
   - Check for geographic properties:
     - P30 (continent)
     - P36 (capital)
     - P625 (coordinates)
     - P276 (location)
     - P17 (country)
     - P706 (located in)
     - P47 (borders)
2. Categorize: with geo vs without geo
3. Extract all geo values with labels

**Output:**
- 7 entities WITH geography (7%)
- 93 entities WITHOUT geography (93%)

**Key Discovery:**
```
WITH Geography (concrete historical):
  - Q1747689 (Ancient Rome) - 5 geo properties
  - Q201038 (Roman Kingdom) - 4 geo properties
  - Q17167 (Roman Republic) - 3 geo properties
  - Q2839628/Q6106068/Q2815472 (subdivisions) - 1 each
  - Q2267705 (field of study) - 1 (universities)

WITHOUT Geography (abstract concepts):
  - Q48349 (empire) - abstract concept
  - Q7269 (monarchy) - abstract concept
  - Q11042 (culture) - abstract concept
  - ... 90 more abstract/ontological concepts
```

**Insight:** 5-hop explored UP into abstraction, lost geographic grounding

**Data:** Geographic values with labels where present

---

### **STEP 7: LATERAL EXPLORATION** (wikidata_lateral_exploration.py)

**Input:** Root QID (Q17167)

**Actions:**
1. Fetch root entity
2. Follow LATERAL properties (different from hierarchical):
   - P36 (capital) → PLACES
   - P793 (significant event) → EVENTS
   - P194 (legislative body) → ORGANIZATIONS
   - P38 (currency) → OBJECTS
   - P1792 (people category) → PEOPLE
3. For each lateral entity found:
   - Fetch basic data (QID, label, description)
   - Check for authority IDs:
     - P1584 (Pleiades ID)
     - P1667 (Getty TGN)
     - P244 (LCSH)
     - P2163 (FAST)
     - P1149 (LCC)
   - Extract P31 (instance of) for type classification

**Output:**
- 12 lateral entities
- 1 place: Q220 (Rome) with Pleiades 423025 ✅
- 7 events: 4 with LCSH IDs
- 2 organizations
- 1 object
- 1 people category

**Key Discovery:**
```
Q220 (Rome) - THE CONNECTOR!
  pleiades_id: 423025 ✅
  tgn_id: 7000874
  lcsh_id: n79018704
  fast_id: 1204500
  
  → Full authority federation!
  → Geographic grounding!
```

**Data:** Authority IDs checked and reported

---

## 🎯 **COMPLETE SCA PROCESS FLOW:**

```
STEP 1: Seed QID (Q17167)
  ↓
STEP 2: Fetch + Resolve Labels (119 QIDs)
  ↓
STEP 3: Extract Taxonomy (parents, children, succession)
  ↓
STEP 4: Recursive 5-Hop (100 entities, hierarchical)
  ↓
STEP 5: Backlinks Query (89 periods from Q11514315)
  ↓
STEP 6: Enrich Backlinks (77 with P31/P279/P361)
  ↓
STEP 7: Geographic Analysis (7 with geo properties)
  ↓
STEP 8: Lateral Exploration (12 entities: places, events, orgs)
  ↓
RESULT: 
  - 100 hierarchical entities (ontology)
  - 77 peer periods (domain context)
  - 12 lateral entities (domain content)
  - 1 place with Pleiades ID ✅
```

---

## 📊 **DATA CHARACTERISTICS AT EACH STEP:**

| Step | Output | Labels? | Authority IDs? | Relationships? |
|------|--------|---------|----------------|----------------|
| 1 | 1 entity, 61 props | ✅ ALL | ❓ Not checked | ❓ Not extracted |
| 2 | 1 entity, 119 QIDs labeled | ✅ ALL | ❓ Not checked | ❓ Not extracted |
| 3 | Taxonomy tables | ✅ ALL | ❓ Not checked | ✅ Classified |
| 4 | 100 entities, 600 rels | ✅ ALL | ❓ Not checked | ✅ Mapped |
| 5 | 89 periods | ✅ ALL | ❓ Not checked | ❓ Not extracted |
| 6 | 77 periods + P31/P279/P361 | ✅ ALL | ❓ Not checked | ✅ Extracted |
| 7 | 7 entities flagged | ✅ ALL | ❓ Not checked | ✅ Geographic |
| 8 | 12 entities | ✅ ALL | ✅ **CHECKED!** | ✅ Lateral |

**Authority IDs first checked in Step 8 (lateral exploration)**

---

## 🎯 **FILTERING DECISIONS:**

### **NOT Applied Yet:**

❌ Did NOT filter by library authority IDs  
❌ Did NOT filter by property density  
❌ Did NOT remove any entities  
❌ Did NOT filter by facet relevance

### **Only Applied:**

✅ Triage by entity type (period vs event vs concept)  
✅ Triage by temporal completeness (has start+end vs not)  
✅ Triage by geographic presence (has geo vs not)

**Everything is still in CANDIDATE BUCKETS, not removed!**

---

## 💡 **PRECISE SCA BEHAVIOR:**

### **Phase 1: Hierarchical Traversal**

```python
1. START with seed QID (Q17167)

2. FETCH complete entity data:
   - All properties
   - All values
   - All qualifiers
   - All references

3. RESOLVE all QID references to labels:
   - Property IDs → property labels
   - Value QIDs → value labels
   - Qualifier QIDs → qualifier labels
   - Batch in groups of 50

4. TRAVERSE UPWARD (5 hops):
   For each value in P31, P279, P361:
     IF value is a QID:
       FETCH that entity (Step 2-3)
       RECURSIVELY traverse its P31, P279, P361 (Step 4)
     CACHE to prevent duplicates
     CONTINUE until hop limit reached

5. TRAVERSE DOWNWARD (5 hops):
   For each value in P527, P150:
     IF value is a QID:
       FETCH that entity (Step 2-3)
       RECURSIVELY traverse its P527, P150 (Step 5)
     CACHE to prevent duplicates
     CONTINUE until hop limit reached OR no children found

6. TRAVERSE SUCCESSION:
   For each value in P155, P156:
     FETCH that entity (once, no recursion)

7. COLLECT all cached entities → taxonomy network
```

**Result:** 100 unique entities (hierarchical network)

---

### **Phase 2: Peer Discovery**

```python
8. IDENTIFY key parent concepts:
   From Step 4 results, find:
     - Q11514315 (historical period) - appeared as P31 value

9. QUERY BACKLINKS:
   SPARQL: Find all entities with P31 → Q11514315
   Limit: 100
   
10. TRIAGE backlinks:
    For each backlink entity:
      FETCH key properties (P580, P582, P571, P576)
      CHECK temporal completeness:
        IF has (P580 AND P582) OR (P571 AND P576):
          → BUCKET: period
        ELIF has only P585:
          → BUCKET: event
        ELSE:
          → BUCKET: concept

11. ENRICH periods:
    For each period in BUCKET:
      FETCH entity data
      EXTRACT P31, P279, P361 with labels
      ADD delay (2 sec) between requests
      HANDLE rate limits (429) → BUCKET: failed
```

**Result:** 77 enriched periods, 12 failed (rate limits)

---

### **Phase 3: Lateral Expansion**

```python
12. IDENTIFY lateral properties from root:
    Properties to follow:
      - P36 (capital) → places
      - P793 (significant event) → events
      - P194 (legislative body) → organizations
      - P38 (currency) → objects
      - P1792 (people category) → people

13. FETCH lateral entities:
    For each lateral property value:
      FETCH entity data
      CHECK for authority IDs:
        - P1584 (Pleiades ID)
        - P1667 (Getty TGN)
        - P244 (LCSH)
        - P2163 (FAST)
        - P1149 (LCC)
      EXTRACT basic classification (P31)
      STORE with relationship context

14. CATEGORIZE by type:
    → BUCKET: places (if P31 = place/city/location)
    → BUCKET: events (if P31 = event/war/conflict)
    → BUCKET: organizations (if P31 = organization/assembly)
    → BUCKET: objects (if P31 = currency/artifact)
```

**Result:** 12 lateral entities, 1 with Pleiades ID (Rome)

---

### **Phase 4: Analysis & Bucketing**

```python
15. ANALYZE geographic coverage:
    For all entities collected:
      CHECK for properties: P30, P36, P625, P276, P17, P706, P47
      IF any present:
        → BUCKET: with_geography
      ELSE:
        → BUCKET: without_geography

16. ANALYZE temporal coverage:
    For all entities collected:
      CHECK for P2348 (time period)
      IF present:
        → TAG: has_temporal_context

17. ANALYZE authority coverage:
    For all entities collected:
      CHECK for P244, P2163, P1149, P10832
      COUNT how many have each
      DO NOT REMOVE - just track

18. CREATE candidate buckets:
    - Bucket 1: Time periods + library IDs
    - Bucket 2: Time periods - library IDs
    - Bucket 3: Places (check for Pleiades)
    - Bucket 4: Events (check for LCSH)
    - Bucket 5: Organizations
    - Bucket 6: Objects
    - Bucket 7: Abstract concepts
    - Bucket 8: Failed/retry
```

**Result:** All entities organized by type and characteristics, NONE removed

---

## 📊 **CURRENT STATE:**

### **Data Collected:**

| Source | Entities | Type | Has Labels | Has Authorities Checked |
|--------|----------|------|------------|------------------------|
| 5-hop hierarchical | 100 | Mixed | ✅ YES | ❌ NO |
| Backlinks enriched | 77 | Periods | ✅ YES | ❌ NO |
| Backlinks failed | 12 | Periods | ✅ YES | ❌ NO |
| Lateral from Q17167 | 12 | Mixed | ✅ YES | ✅ **YES** |
| **TOTAL** | **189** | **Mixed** | ✅ **ALL** | **12 checked** |

**Unique entities:** ~180-190 (some overlap between sets)

---

## 🎯 **WHAT SCA HAS DONE:**

### ✅ **Completed:**

1. ✅ Fetched seed entity (Q17167) with all properties
2. ✅ Resolved ALL QIDs to labels throughout
3. ✅ Extracted taxonomy (parents, children, succession)
4. ✅ Explored 5 hops hierarchically (100 entities)
5. ✅ Discovered peer periods (89 entities)
6. ✅ Enriched peer periods with classifications (77 entities)
7. ✅ Analyzed geographic coverage (7 with, 93 without)
8. ✅ Explored lateral relationships (12 entities)
9. ✅ Found place with Pleiades ID (Rome: 423025)
10. ✅ Found events with LCSH IDs (4 of 7 wars)

### ❌ **NOT Done Yet:**

1. ❌ Check library authority IDs for all 100 hierarchical entities
2. ❌ Check library authority IDs for all 77 peer periods
3. ❌ Explore lateral from all 89 periods (not just Q17167)
4. ❌ Fetch people from events/organizations
5. ❌ Explore 2nd-level lateral (from lateral entities)
6. ❌ Filter/remove based on authority presence
7. ❌ Map all entities to 18 facets
8. ❌ Create SubjectConcept proposals
9. ❌ Create SFA assignments
10. ❌ Generate Neo4j Cypher

---

## 🎯 **PRECISE SCA AGENT BEHAVIOR:**

### **Input:**
- Seed QID

### **Process:**
1. Hierarchical traverse (P31, P279, P361, P527) → N hops
2. Backlinks query (find peers via common parent)
3. Lateral traverse (P36, P793, P194, P38, etc.) → 1 hop from each
4. Enrich all with classifications (P31, P279, P361)
5. Check all for authorities (P244, P2163, P1149, P1584, P1667)
6. Analyze coverage (geographic, temporal, academic)
7. Organize into buckets (NOT remove)
8. Map to facets based on properties
9. Propose SubjectConcepts for entities with library IDs
10. Generate SFAs for entities with facet mappings

### **Output:**
- Complete taxonomy network
- All entities with labels
- All authorities identified
- Candidate buckets organized
- Ready for domain building

### **Critical Rules:**
- ✅ ALWAYS resolve QIDs to labels
- ✅ ALWAYS cache to prevent duplicates
- ✅ ALWAYS handle rate limits (delays, retries)
- ✅ ALWAYS check both P580/P582 AND P571/P576 for temporal
- ✅ ALWAYS explore both hierarchical AND lateral
- ❌ NEVER filter by density early
- ❌ NEVER remove before checking network role
- ❌ NEVER assume inheritance

---

**This is the precise behavior SCA should follow!** 🎯
