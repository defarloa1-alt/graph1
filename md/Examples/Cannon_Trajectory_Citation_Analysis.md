# Cannon Trajectory Text: Citation Quality Analysis

## Key Corrections Applied

### ✅ `id` vs `unique_id` Structure

**Problem:** Initial examples had `id` and `unique_id` as identical values.

**Solution:**
- **`id`**: Simple, human-readable identifier (e.g., `'cite_001'`)
- **`unique_id`**: Composite identifier for system-level deduplication (e.g., `'CITE_CANNON_TRAJECTORY_INSIGHT_001_HASH_ABC123'`)

**Rationale:**
- Citations are extracted prose, not entities in Wikidata → no QID
- `type_qid: 'Q49848'` represents the entity TYPE (Document/Citation), not the citation's own QID
- `unique_id` includes hash/descriptor for deduplication checks

### ✅ Wikidata QIDs for Concepts

**Corrected QIDs used in relationships:**
- Differential Equations: `Q177932` ✅
- Trajectory: `Q208513` ✅
- Cannon Ball: `Q1723884` ✅
- Citation Entity Type: `Q49848` ✅ (Document)

### ✅ FAST Backbone Properties

**Added backbone classification for library interoperability:**
- `backbone_fast`: FAST subject heading ID (verify at id.loc.gov/fast)
- `backbone_lcc`: Library of Congress Classification code
- `backbone_lcsh`: Library of Congress Subject Headings array
- `backbone_marc`: MARC authority record ID

**Note:** FAST/LCC/LCSH/MARC IDs in examples should be verified against actual Library of Congress databases for production use.

---

## Source Text

> "Aiming a cannon on a 17th century vessel is not even an art, much less a science. Calculating the proper trajectories for a projectile hurtling through the air at hundreds of miles per hour is hard enough on land. In fact, few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile. Some of the first differential equations were developed to predict the flight of a cannon ball shot."

---

## Citation Quality Scoring by Segment

### Segment 1: Opening Comparison
**Text:** *"Aiming a cannon on a 17th century vessel is not even an art, much less a science."*

**Quality Analysis:**
- ✅ **Stylistic:** Strong rhetorical structure (parallelism: "not even... much less")
- ✅ **Memorable:** Quotable phrase structure
- ✅ **Insightful:** Establishes theme (difficulty/complexity)
- ⚠️ **Semantic:** Descriptive but not particularly deep
- ⚠️ **Historical:** Context-setting, not historical claim

**Scores:**
- Stylistic: 8/10 (excellent parallelism)
- Semantic: 6/10 (surface-level comparison)
- Emotional: 5/10 (mild humor/irony)
- Historical: 4/10 (context only)
- Quotability: 7/10 (memorable phrasing)

**Composite: 6.0/10** ⚠️ *Good, but not exceptional*

**Verdict:** **Include as context** - Good opening, establishes difficulty theme, but not the most insightful part.

---

### Segment 2: Technical Challenge
**Text:** *"Calculating the proper trajectories for a projectile hurtling through the air at hundreds of miles per hour is hard enough on land."*

**Quality Analysis:**
- ⚠️ **Stylistic:** Functional, descriptive
- ⚠️ **Memorable:** Not particularly quotable
- ⚠️ **Insightful:** States a fact, doesn't reveal much
- ⚠️ **Semantic:** Informational but not deep
- ⚠️ **Historical:** No historical significance

**Scores:**
- Stylistic: 5/10 (competent but plain)
- Semantic: 5/10 (factual statement)
- Emotional: 4/10 (no emotional resonance)
- Historical: 3/10 (general statement)
- Quotability: 4/10 (not memorable)

**Composite: 4.2/10** ❌ *Too generic*

**Verdict:** **Exclude from citation** - This is transitional/explanatory text, not great writing. Provides context but lacks insight or memorability.

---

### Segment 3: Historical Insight ⭐
**Text:** *"In fact, few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile."*

**Quality Analysis:**
- ✅ **Stylistic:** Strong declarative structure ("few... have a longer history")
- ✅ **Memorable:** Claim structure makes it quotable
- ✅ **Insightful:** **Reveals historical pattern** (practical needs → math development)
- ✅ **Semantic:** **High information density** - connects practical needs to mathematical innovation
- ✅ **Historical:** **Significant historical claim** - identifies long-term pattern

**Scores:**
- Stylistic: 7/10 (strong claim structure)
- Semantic: **9/10** (high insight - connects domains)
- Emotional: 6/10 (appreciation for historical connection)
- Historical: **9/10** (significant historical claim)
- Quotability: **8/10** (memorable claim)

**Composite: 7.8/10** ✅ **GREAT WRITING**

**Verdict:** **PRIMARY CITATION** - This is the core insight. It synthesizes historical pattern, connects practical needs to mathematical development, and makes a memorable claim.

---

### Segment 4: Specific Historical Example
**Text:** *"Some of the first differential equations were developed to predict the flight of a cannon ball shot."*

**Quality Analysis:**
- ✅ **Stylistic:** Clear, direct
- ✅ **Memorable:** Specific historical fact ("first differential equations")
- ✅ **Insightful:** **Concrete example** supporting the previous claim
- ✅ **Semantic:** **High information value** - specific historical development
- ✅ **Historical:** **Highly significant** - identifies "first" development

**Scores:**
- Stylistic: 6/10 (clear but functional)
- Semantic: **8/10** (specific historical fact with high value)
- Emotional: 5/10 (interesting but not emotionally resonant)
- Historical: **9/10** (significant historical claim)
- Quotability: 7/10 (memorable fact)

**Composite: 7.0/10** ✅ *Strong historical claim*

**Verdict:** **SECONDARY CITATION** - Important specific example that supports the main insight. Less quotable than Segment 3 but contains significant historical information.

---

## Recommended Citation Strategy

### Option 1: Single Comprehensive Citation (Full Quote)

**Citation:**
> "Aiming a cannon on a 17th century vessel is not even an art, much less a science. Calculating the proper trajectories for a projectile hurtling through the air at hundreds of miles per hour is hard enough on land. In fact, few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile. Some of the first differential equations were developed to predict the flight of a cannon ball shot."

**Rationale:**
- ✅ Complete narrative arc (difficulty → historical pattern → specific example)
- ✅ Context preserved
- ⚠️ Includes weaker transitional text (Segment 2)

**Quality Score: 6.5/10**

---

### Option 2: Two-Tier Citation (Recommended) ⭐

#### Primary Citation (Core Insight)
**Citation:**
> "In fact, few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile."

**Quality Score: 7.8/10**
- ✅ Highest insight value
- ✅ Memorable and quotable
- ✅ Reveals historical pattern
- ✅ Synthesizes practical needs → mathematical development

#### Secondary Citation (Supporting Detail)
**Citation:**
> "Some of the first differential equations were developed to predict the flight of a cannon ball shot."

**Quality Score: 7.0/10**
- ✅ Specific historical fact
- ✅ Supports primary claim
- ✅ High information value

**Rationale:**
- Separates **insight** (primary) from **evidence** (secondary)
- Allows querying by citation type
- Preserves both core message and supporting detail

---

### Option 3: Three-Part Citation (Most Granular)

#### Citation 1: Opening Context
**Text:** "Aiming a cannon on a 17th century vessel is not even an art, much less a science."

**Use:** Context for understanding difficulty
**Quality Score: 6.0/10**

#### Citation 2: Core Insight (Primary)
**Text:** "In fact, few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile."

**Use:** Main historical insight
**Quality Score: 7.8/10**

#### Citation 3: Specific Example
**Text:** "Some of the first differential equations were developed to predict the flight of a cannon ball shot."

**Use:** Historical evidence
**Quality Score: 7.0/10**

**Rationale:**
- Maximum granularity
- Allows independent querying of each element
- Preserves context separately from insight

---

## Graph Structure: Citation Entities

### Understanding `id` vs `unique_id`

**For entities WITH Wikidata QIDs:**
- `id`: The Wikidata QID (e.g., `'Q1048'` for Julius Caesar)
- `unique_id`: Structured composite `QID_TYPE_SHORTLABEL` (e.g., `'Q1048_HUM_JULIUS_CAESAR'`)

**For Citations (no Wikidata QID):**
- `id`: Simple unique citation identifier (human-readable, sequential or descriptive)
- `unique_id`: Composite identifier for deduplication, typically based on:
  - Citation source + page + prose hash, OR
  - Structured format: `CITE_SHORTLABEL_NUMBER`, OR
  - Content hash for exact deduplication

**Why they differ:**
- `id`: Human-readable identifier for reference
- `unique_id`: System-level identifier for deduplication and uniqueness checks
- Citations are extracted prose, not entities in Wikidata, so they don't have QIDs
- `type_qid: 'Q49848'` represents the entity TYPE (Document/Citation), not the citation's own QID

---

### Recommended: Option 2 (Two-Tier)

```cypher
// Primary Citation - Core Insight
(primaryCite:Citation {
  // Core properties
  id: 'cite_001',  // Simple sequential ID
  unique_id: 'CITE_CANNON_TRAJECTORY_INSIGHT_001_HASH_ABC123',  // Composite for deduplication
  label: 'Historical insight: Practical tasks inspiring mathematical ingenuity',
  type: 'Citation',
  type_qid: 'Q49848',  // Document (citation entity type)
  
  // Note: Citations don't have their own Wikidata QID since they're extracted prose,
  // not entities in Wikidata. The type_qid (Q49848) represents the "Document" entity type.
  
  // Citation metadata
  prose: 'In fact, few practical tasks have a longer history of inspiring mathematical ingenuity than figuring out the trajectory of a projectile.',
  
  citation: '[Source Citation]',
  page_reference: '[Page]',
  
  // Quality scoring
  quality_score: 7.8,
  is_great_writing: true,
  is_quotable: true,
  is_insightful: true,
  is_historically_significant: true,
  
  quality_reasoning: 'Reveals historical pattern connecting practical needs to mathematical development; memorable claim structure; high semantic density',
  
  insight_type: 'historical_pattern',
  rhetorical_devices: ['superlative_claim', 'comparative_structure'],
  
  // Classification
  citation_type: 'primary_insight',
  
  // Backbone alignment (FAST/LCC/LCSH/MARC)
  // These backbone properties classify the citation's subject matter for library interoperability
  // Note: These FAST/LCC/LCSH/MARC IDs should be verified against actual Library of Congress databases
  // - FAST: id.loc.gov/fast (Faceted Application of Subject Terminology)
  // - LCC: Library of Congress Classification (loc.gov/catdir/cpso/lcco)
  // - LCSH: Library of Congress Subject Headings (id.loc.gov/authorities/subjects)
  // - MARC: Machine-Readable Cataloging authority records
  backbone_fast: 'fst00819777',  // Mathematics -- History (verify: id.loc.gov/fast/8019777)
  backbone_lcc: 'QA21',  // History of mathematics (Library of Congress Classification)
  backbone_lcsh: ['Mathematics -- History', 'Ballistics -- Mathematics', 'Projectiles -- Trajectories'],
  backbone_marc: 'sh85082139',  // Mathematics -- History (MARC authority: id.loc.gov/authorities/sh85082139)
  
  test_case: 'cannon_trajectory'
})

// Secondary Citation - Supporting Example
(secondaryCite:Citation {
  // Core properties
  id: 'cite_002',  // Simple sequential ID
  unique_id: 'CITE_CANNON_TRAJECTORY_EXAMPLE_002_HASH_DEF456',  // Composite for deduplication
  label: 'Historical example: First differential equations for cannon ball prediction',
  type: 'Citation',
  type_qid: 'Q49848',  // Document (citation entity type)
  
  // Citation metadata
  prose: 'Some of the first differential equations were developed to predict the flight of a cannon ball shot.',
  
  citation: '[Source Citation]',
  page_reference: '[Page]',
  
  // Quality scoring
  quality_score: 7.0,
  is_great_writing: false,
  is_quotable: true,
  is_insightful: true,
  is_historically_significant: true,
  
  quality_reasoning: 'Specific historical fact with high information value; supports primary insight; identifies "first" development',
  
  insight_type: 'historical_fact',
  
  // Classification
  citation_type: 'supporting_evidence',
  
  // Backbone alignment (FAST/LCC/LCSH/MARC)
  // These backbone properties classify the citation's subject matter for library interoperability
  // Note: These FAST/LCC/LCSH/MARC IDs should be verified against actual Library of Congress databases
  backbone_fast: 'fst00892866',  // Differential equations (verify: id.loc.gov/fast/892866)
  backbone_lcc: 'QA372',  // Differential equations (Library of Congress Classification)
  backbone_lcsh: ['Differential equations', 'Ballistics -- Mathematics', 'Projectiles -- Trajectories'],
  backbone_marc: 'sh85037890',  // Differential equations (MARC authority: id.loc.gov/authorities/sh85037890)
  
  test_case: 'cannon_trajectory'
})

// Relationships to Concepts (with correct QIDs from schema)
(primaryCite)-[:SUPPORTS]->(secondaryCite)

// Primary citation describes these concepts
(primaryCite)-[:DESCRIBES]->(mathIngenuity:Concept {
  id: 'mathematical_ingenuity',
  unique_id: 'mathematical_ingenuity_CONCEPT_MATHEMATICAL_INGENUITY',
  label: 'Mathematical Ingenuity',
  type: 'Concept',
  type_qid: 'Q151885'  // Concept
})

(primaryCite)-[:DESCRIBES]->(practicalTask:Concept {
  id: 'practical_task',
  unique_id: 'practical_task_CONCEPT_PRACTICAL_TASK',
  label: 'Practical Task',
  type: 'Concept',
  type_qid: 'Q151885'  // Concept
})

(primaryCite)-[:ANALYZES]->(trajectoryCalc:Concept {
  id: 'Q208513',
  unique_id: 'Q208513_CONCEPT_TRAJECTORY',
  label: 'Trajectory Calculation',
  type: 'Concept',
  type_qid: 'Q151885',  // Concept
  qid: 'Q208513'  // Trajectory
})

// Secondary citation describes these concepts
(secondaryCite)-[:DESCRIBES]->(diffEquations:Concept {
  id: 'Q177932',
  unique_id: 'Q177932_CONCEPT_DIFFERENTIAL_EQUATIONS',
  label: 'Differential Equations',
  type: 'Concept',
  type_qid: 'Q151885',  // Concept
  qid: 'Q177932'  // Differential equation
})

(secondaryCite)-[:MENTIONS]->(cannonBall:Concept {
  id: 'Q1723884',
  unique_id: 'Q1723884_CONCEPT_CANNON_BALL',
  label: 'Cannon Ball',
  type: 'Concept',
  type_qid: 'Q151885',  // Concept
  qid: 'Q1723884'  // Cannonball
})

(secondaryCite)-[:DESCRIBES]->(flight:Concept {
  id: 'flight_process',
  unique_id: 'flight_process_CONCEPT_FLIGHT',
  label: 'Flight',
  type: 'Concept',
  type_qid: 'Q151885'  // Concept
})

// Note: Secondary citation provides evidence that supports primary insight
(secondaryCite)-[:SUMMARIZES]->(primaryCite)  // Evidence supports insight
```

---

## Query Patterns Enabled

### Find Core Insights About Mathematical Development

```cypher
MATCH (cite:Citation {citation_type: 'primary_insight'})
WHERE cite.prose CONTAINS 'mathematical ingenuity'
RETURN cite.prose, cite.quality_score
ORDER BY cite.quality_score DESC
```

**Returns:** Primary citation (7.8/10)

---

### Find Historical Firsts Related to Mathematics

```cypher
MATCH (cite:Citation)
WHERE cite.prose CONTAINS 'first' 
  AND cite.prose CONTAINS 'differential'
RETURN cite.prose, cite.quality_score, cite.citation_type
```

**Returns:** Secondary citation (7.0/10, supporting_evidence)

---

### Find All Citations About Trajectory Calculation

```cypher
MATCH (cite:Citation)-[:DESCRIBES|:ANALYZES]->(entity)
WHERE entity.label CONTAINS 'Trajectory'
RETURN cite.prose, cite.quality_score, cite.citation_type
ORDER BY cite.quality_score DESC
```

**Returns:** Both citations, ranked by quality

---

## Comparison: All Text vs. Selective Citations

### All Text as Single Citation

**Pros:**
- ✅ Complete narrative context
- ✅ Preserves flow
- ✅ No information loss

**Cons:**
- ⚠️ Includes weaker segments (Score 4.2/10)
- ⚠️ Dilutes overall quality score
- ⚠️ Harder to query specific insights

**Average Quality: 6.5/10**

---

### Selective Citations (Recommended)

**Pros:**
- ✅ Highest quality segments only (7.8 + 7.0)
- ✅ Clear separation of insight vs. evidence
- ✅ Better queryability
- ✅ Preserves most valuable content
- ✅ Enables citation-type filtering

**Cons:**
- ⚠️ Loses some context (opening comparison)
- ⚠️ Requires two entities instead of one

**Average Quality: 7.4/10** (when including only top segments)

---

## Final Recommendation

### Best Approach: **Two-Tier Citation (Option 2)**

**Primary Citation:** Segment 3 (Core Insight)
- Quality Score: **7.8/10**
- Type: Primary Insight
- Most quotable and insightful

**Secondary Citation:** Segment 4 (Supporting Example)
- Quality Score: **7.0/10**
- Type: Supporting Evidence
- Important historical fact

**Exclude:**
- Segment 1 (Context only, 6.0/10) - Include in narrative, not as separate citation
- Segment 2 (Transitional, 4.2/10) - Too weak for citation

### Alternative: Include Opening if Context Needed

If the opening comparison is important for understanding the difficulty theme:

**Three-Part Citation:**
1. Opening Context (6.0/10) - Only if context preservation is critical
2. Core Insight (7.8/10) - **Essential**
3. Supporting Example (7.0/10) - **Essential**

---

## Summary Table

| Segment | Text | Quality | Include? | Type |
|---------|------|---------|----------|------|
| 1 | "Aiming a cannon... not even an art, much less a science" | 6.0/10 | Optional | Context |
| 2 | "Calculating the proper trajectories... hard enough on land" | 4.2/10 | ❌ No | Transitional |
| 3 | "Few practical tasks have a longer history..." | **7.8/10** | ✅ **Yes** | **Primary Insight** |
| 4 | "Some of the first differential equations..." | **7.0/10** | ✅ **Yes** | **Supporting Evidence** |

**Recommendation:** Extract **Segments 3 and 4** as citations. Segment 1 can be included in the narrative property of relationships for context, but doesn't need its own citation entity.


