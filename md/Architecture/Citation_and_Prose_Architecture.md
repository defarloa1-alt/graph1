# Missing Architecture Component: Citations & Insightful Prose

## The Gap

**Missing Component:** Actual citations of insightful prose/quotes from authors, clustered by authors, linked to graph entities.

**Current State:**
- ✅ We have source attribution (source name, type, tier)
- ✅ We have narrative summaries
- ❌ **Missing**: Actual prose/quotes from sources
- ❌ **Missing**: Author clustering of insights
- ❌ **Missing**: Direct linkage of quotes to entities/events

---

## What's Missing

### Current: Source Attribution Only

```cypher
(relationship:CAUSED {
  sources: [
    {
      source: 'Suetonius - Life of Caesar',
      source_type: 'primary',
      tier: 1,
      citation: 'Suet. Caes. 31-32'
    }
  ]
})
```

**Problem:**
- ❌ No actual quote/text
- ❌ No link to author entity
- ❌ No clustering of insights by author
- ❌ Can't retrieve what the source actually said

---

### Needed: Citations with Actual Prose

```cypher
// Author entity
(suetonius:Human {
  label: 'Suetonius',
  qid: 'Q...',
  type: 'Human'
})

// Citation entity with actual prose
(citation1:Citation {
  id: 'cite_suet_caes_31',
  label: 'Suetonius on Caesar crossing Rubicon',
  prose: 'When news was brought that Gaius Caesar was approaching 
          with an army and was already on his way to Rome, Suetonius 
          writes that Caesar crossed the Rubicon, saying "The die is cast."',
  original_language: 'la',
  translation: 'English',
  citation: 'Suet. Caes. 31',
  page_reference: 'Book 1, Chapter 31',
  quote_start: 'When news was brought',
  quote_end: 'The die is cast.'
})

// Work entity
(suetonius_work:Work {
  label: 'The Twelve Caesars',
  type: 'Book',
  qid: 'Q...'
})

// Relationships
(suetonius) -[:AUTHOR_OF]-> (suetonius_work)
(citation1) -[:EXTRACTED_FROM]-> (suetonius_work)
(citation1) -[:ATTRIBUTED_TO]-> (suetonius)
(citation1) -[:DESCRIBES]-> (crossingEvent:Event)
(citation1) -[:MENTIONS]-> (caesar:Human)
(citation1) -[:MENTIONS]-> (rubicon:River)
```

---

## Proposed Architecture

### 1. Citation Entity Type

**New Entity Type:** `Citation`

**Properties:**
- `id`: Unique citation ID
- `label`: Human-readable label
- `prose`: **Actual quoted text**
- `original_language`: ISO 639 code (e.g., 'la' for Latin)
- `translation`: Translated text (if applicable)
- `citation`: Bibliographic citation
- `page_reference`: Page/chapter reference
- `quote_start`: Start of quote (if excerpt)
- `quote_end`: End of quote
- `quote_context`: Surrounding context
- `insight_type`: Type of insight (analysis, description, interpretation)
- `confidence`: Confidence in citation accuracy

---

### 2. Author Clustering

**Structure:**
```
Author Entity
  ↓ AUTHOR_OF
Work Entity
  ↓ EXTRACTED_FROM
Citation Entities (multiple quotes from same author)
  ↓ DESCRIBES / MENTIONS
Graph Entities (entities/events described)
```

**Benefits:**
- ✅ Cluster all insights by author
- ✅ Compare different author perspectives
- ✅ Track author expertise/views
- ✅ Find all author's insights about topic

---

### 3. Citation → Entity Relationships

**Relationship Types:**
- `DESCRIBES` - Citation describes entity/event
- `MENTIONS` - Citation mentions entity
- `ANALYZES` - Citation provides analysis of entity
- `INTERPRETS` - Citation interprets entity/event
- `QUOTES` - Citation is direct quote from source
- `SUMMARIZES` - Citation summarizes entity/event

**Example:**
```cypher
// Citation describes event
(citation1:Citation)-[:DESCRIBES {
  confidence: 0.95,
  insight_type: 'primary_description'
}]->(crossingEvent:Event)

// Citation mentions entities
(citation1)-[:MENTIONS {
  role: 'actor'
}]->(caesar:Human)

(citation1)-[:MENTIONS {
  role: 'location'
}]->(rubicon:River)

// Citation analyzes consequences
(citation1)-[:ANALYZES {
  insight_type: 'causal_analysis'
}]->(civilWar:Event)
```

---

## Complete Citation Architecture

### Citation Entity Structure

```cypher
(citation:Citation {
  // Core properties
  id: 'cite_suet_caes_31',
  unique_id: 'cite_suet_caes_31',
  label: 'Suetonius on Caesar crossing Rubicon',
  type: 'Citation',
  type_qid: 'Q49848',  // Document
  
  // Citation metadata
  citation: 'Suet. Caes. 31',
  citation_standard: 'APA',  // or Chicago, MLA, etc.
  page_reference: 'Book 1, Chapter 31',
  line_reference: 'Lines 14-28',
  
  // Actual prose
  prose: 'When news was brought that Gaius Caesar was approaching 
          with an army and was already on his way to Rome, Caesar 
          crossed the Rubicon, saying "The die is cast."',
  prose_original: 'Cum nuntiatum esset Gaium Caesarem cum exercitu 
                   appropinquare ac iam Romam tendere, Caesar 
                   Rubiconem transiit, dicens "Alea iacta est."',
  
  // Language
  original_language: 'la',
  original_language_qid: 'Q397',  // Latin
  translation_language: 'en',
  translation_language_qid: 'Q1860',  // English
  
  // Quote boundaries
  quote_start: 'When news was brought',
  quote_end: 'The die is cast.',
  quote_context: 'Preceding paragraph about Senate orders...',
  
  // Insight classification
  insight_type: 'primary_description',
  insight_category: 'historical_narrative',
  contains_analysis: true,
  contains_interpretation: false,
  
  // Temporal/spatial context
  describes_period: '49 BCE',
  describes_location: 'Rubicon River, Italy',
  
  // Validation
  confidence: 0.95,
  validation_status: 'verified',
  verified_by: ['expert_reviewer_1'],
  
  // Backbone alignment
  backbone_fast: 'fst01411640',
  backbone_lcc: 'DG261.C35',
  
  // Metadata
  test_case: 'caesar_rubicon',
  created_date: '2025-01-02',
  extracted_by: 'llm_extraction_v1.0'
})
```

---

### Author Clustering Structure

```cypher
// Author
(suetonius:Human {
  label: 'Suetonius',
  qid: 'Q205033',
  type: 'Human',
  occupation: 'Historian',
  period: 'c. 69-122 CE'
})

// Work by author
(suetonius_lives:Work {
  label: 'The Twelve Caesars',
  type: 'Book',
  qid: 'Q...',
  language: 'la',
  date_composed: 'c. 121 CE'
})

// Multiple citations from same work
(citation1:Citation {
  prose: 'Quote about crossing Rubicon...',
  citation: 'Suet. Caes. 31'
})

(citation2:Citation {
  prose: 'Quote about Caesar\'s character...',
  citation: 'Suet. Caes. 45'
})

(citation3:Citation {
  prose: 'Quote about assassination...',
  citation: 'Suet. Caes. 82'
})

// Relationships: Author clustering
(suetonius) -[:AUTHOR_OF {
  role: 'author',
  date_composed: 'c. 121 CE'
}]-> (suetonius_lives)

(citation1) -[:EXTRACTED_FROM {
  chapter: '31',
  page: '45'
}]-> (suetonius_lives)

(citation2) -[:EXTRACTED_FROM]-> (suetonius_lives)
(citation3) -[:EXTRACTED_FROM]-> (suetonius_lives)

// All citations attributed to author
(citation1) -[:ATTRIBUTED_TO]-> (suetonius)
(citation2) -[:ATTRIBUTED_TO]-> (suetonius)
(citation3) -[:ATTRIBUTED_TO]-> (suetonius)

// Citations describe different entities
(citation1) -[:DESCRIBES]-> (crossingEvent:Event)
(citation2) -[:DESCRIBES]-> (caesar:Human)
(citation3) -[:DESCRIBES]-> (assassination:Event)
```

---

### Query Patterns: Author Clustering

**Find all insights by author about topic:**
```cypher
// All Suetonius quotes about Caesar
MATCH (author:Human {label: 'Suetonius'})
MATCH (author)<-[:ATTRIBUTED_TO]-(citation:Citation)
MATCH (citation)-[:DESCRIBES]->(entity)
WHERE entity.label CONTAINS 'Caesar'
RETURN citation.prose, citation.citation, entity.label
ORDER BY citation.citation
```

**Compare author perspectives:**
```cypher
// Compare Suetonius vs. Plutarch on same event
MATCH (suet:Human {label: 'Suetonius'})
MATCH (plut:Human {label: 'Plutarch'})
MATCH (event:Event {label: 'Crossing of Rubicon'})
MATCH (suet)<-[:ATTRIBUTED_TO]-(suetCite:Citation)-[:DESCRIBES]->(event)
MATCH (plut)<-[:ATTRIBUTED_TO]-(plutCite:Citation)-[:DESCRIBES]->(event)
RETURN 
  suetCite.prose as suetonius_quote,
  plutCite.prose as plutarch_quote,
  event.label
```

**Cluster insights by author:**
```cypher
// All authors who wrote about Caesar
MATCH (author:Human)
MATCH (author)<-[:ATTRIBUTED_TO]-(citation:Citation)
MATCH (citation)-[:DESCRIBES|:MENTIONS]->(entity)
WHERE entity.label CONTAINS 'Caesar'
RETURN author.label, 
       COUNT(DISTINCT citation) as citation_count,
       COLLECT(DISTINCT citation.citation) as citations
ORDER BY citation_count DESC
```

---

## Integration with Existing Schema

### Extend Entity Types

**Add to Schema:**
```json
{
  "category": "Work",
  "type": "Citation",
  "description": "Quoted text/citation from source",
  "wikidata_qid": "Q49848"
}
```

---

### Extend Relationship Types

**Add to Schema:**
```json
{
  "category": "Attribution",
  "type": "DESCRIBES",
  "description": "Citation describes entity/event",
  "directionality": "forward"
},
{
  "category": "Attribution",
  "type": "MENTIONS",
  "description": "Citation mentions entity",
  "directionality": "forward"
},
{
  "category": "Attribution",
  "type": "ANALYZES",
  "description": "Citation provides analysis",
  "directionality": "forward"
},
{
  "category": "Attribution",
  "type": "EXTRACTED_FROM",
  "description": "Citation extracted from work",
  "directionality": "forward"
},
{
  "category": "Attribution",
  "type": "ATTRIBUTED_TO",
  "description": "Citation attributed to author",
  "directionality": "forward"
}
```

---

## Use Cases

### 1. **Author Perspective Analysis**

**Query:** "What did Suetonius say about Caesar's crossing of Rubicon?"

**Result:**
- All Suetonius citations about the event
- Actual prose/quotes
- Context and interpretation
- Comparison with other authors

---

### 2. **Insight Clustering**

**Query:** "What insights do primary sources provide about this event?"

**Result:**
- All citations from primary sources
- Clustered by author
- Actual prose, not just summaries
- Different perspectives

---

### 3. **Scholarly Discourse**

**Query:** "How have modern historians interpreted this event?"

**Result:**
- Citations from scholarly works
- Author clustering
- Evolution of interpretation
- Different analytical perspectives

---

### 4. **Source Verification**

**Query:** "Show me the exact quote that supports this claim"

**Result:**
- Direct citation with prose
- Source attribution
- Context
- Validation status

---

## Implementation Strategy

### Phase 1: Citation Entity Type

**Add to Schema:**
1. Add `Citation` to entity types
2. Define citation properties
3. Create citation → entity relationships

---

### Phase 2: Author Clustering

**Implementation:**
1. Link citations to authors
2. Link citations to works
3. Enable author-based queries

---

### Phase 3: Prose Extraction

**LLM Extraction:**
1. Extract quotes from sources
2. Identify quote boundaries
3. Link quotes to entities
4. Attribute to authors

---

## Complete Example

### "Caesar Crossed Rubicon" with Citations

```cypher
// Event
(crossingEvent:Event {
  label: 'Crossing of the Rubicon',
  start_date: '-0049-01-10'
})

// Authors
(suetonius:Human {label: 'Suetonius', qid: 'Q205033'})
(plutarch:Human {label: 'Plutarch', qid: 'Q41523'})
(appian:Human {label: 'Appian', qid: 'Q36212'})

// Works
(suetonius_lives:Work {
  label: 'The Twelve Caesars',
  type: 'Book'
})

(plutarch_lives:Work {
  label: 'Parallel Lives',
  type: 'Book'
})

// Citations with actual prose
(suetoniusCite:Citation {
  prose: 'When news was brought that Gaius Caesar was approaching 
          with an army and was already on his way to Rome, Caesar 
          crossed the Rubicon, saying "The die is cast." This act 
          marked the beginning of civil war.',
  citation: 'Suet. Caes. 31',
  original_language: 'la',
  translation: 'en',
  insight_type: 'primary_description'
})

(plutarchCite:Citation {
  prose: 'Caesar, seeing that war was now inevitable, crossed the 
          Rubicon with his army. It is said that he paused at the 
          river and deliberated, then crossed with the words 
          "Let the die be cast."',
  citation: 'Plut. Caes. 32',
  original_language: 'grc',
  translation: 'en',
  insight_type: 'primary_description'
})

// Author clustering
(suetonius) -[:AUTHOR_OF]-> (suetonius_lives)
(plutarch) -[:AUTHOR_OF]-> (plutarch_lives)

(suetoniusCite) -[:EXTRACTED_FROM]-> (suetonius_lives)
(suetoniusCite) -[:ATTRIBUTED_TO]-> (suetonius)

(plutarchCite) -[:EXTRACTED_FROM]-> (plutarch_lives)
(plutarchCite) -[:ATTRIBUTED_TO]-> (plutarch)

// Citations describe event
(suetoniusCite) -[:DESCRIBES {
  confidence: 0.95,
  insight_type: 'primary_description'
}]-> (crossingEvent)

(plutarchCite) -[:DESCRIBES {
  confidence: 0.95,
  insight_type: 'primary_description'
}]-> (crossingEvent)

// Citations mention entities
(suetoniusCite) -[:MENTIONS {role: 'actor'}]-> (caesar:Human)
(suetoniusCite) -[:MENTIONS {role: 'location'}]-> (rubicon:River)
(suetoniusCite) -[:ANALYZES]-> (civilWar:Event)
```

---

## Benefits

### 1. **Verifiable Claims**

**Current:**
- "Suetonius says X" - but what exactly?

**With Citations:**
- "Suetonius says: '[actual quote]'" - verifiable

---

### 2. **Author Perspective Analysis**

**Current:**
- Hard to compare author perspectives

**With Citations:**
- Query all quotes by author
- Compare different perspectives
- Cluster insights by author

---

### 3. **Scholarly Discourse Tracking**

**Current:**
- Can't track how interpretations evolved

**With Citations:**
- Citations from different periods
- Author clustering shows perspectives
- Evolution of interpretation

---

### 4. **Rich Context**

**Current:**
- Narrative summaries only

**With Citations:**
- Actual source prose
- Quote context
- Original language
- Translations

---

## Schema Updates Needed

### 1. Add Citation Entity Type

**Update:** `JSON/chrystallum_schema.json`

```csv
Work,Citation,Quoted text from source,Q49848
```

---

### 2. Add Citation Relationships

**Update:** `Relationships/relationship_types_registry_master.csv`

```csv
Attribution,DESCRIBES,Citation describes entity/event,forward
Attribution,MENTIONS,Citation mentions entity,forward
Attribution,ANALYZES,Citation provides analysis,forward
Attribution,EXTRACTED_FROM,Citation extracted from work,forward
Attribution,ATTRIBUTED_TO,Citation attributed to author,forward
```

---

### 3. Update Action Structure

**Include citation in narrative:**
```cypher
(relationship:CAUSED {
  narrative: 'Caesar crossed the Rubicon...',
  citations: [
    {
      citation_id: 'cite_suet_caes_31',
      quote: 'When news was brought...',
      author: 'Suetonius',
      relevance: 'primary_description'
    }
  ]
})
```

---

## Summary

### What's Missing

**Citations with Actual Prose:**
- ✅ Citation entity type
- ✅ Actual quoted text
- ✅ Author attribution
- ✅ Work linkage

**Author Clustering:**
- ✅ Author → Work → Citations
- ✅ Citation → Entities
- ✅ Query by author
- ✅ Compare perspectives

### Why It Matters

**Value:**
- ✅ **Verifiable claims** - actual quotes, not summaries
- ✅ **Author perspectives** - cluster insights by author
- ✅ **Scholarly discourse** - track interpretations
- ✅ **Rich context** - original prose, translations, context

### Implementation

**Add to Schema:**
1. Citation entity type
2. DESCRIBES, MENTIONS, ANALYZES relationships
3. EXTRACTED_FROM, ATTRIBUTED_TO relationships

**This is a critical missing piece** - citations with actual prose, clustered by authors, would add significant value to the knowledge graph!

---

## Schema Updates Required

### Files to Update

1. **`JSON/chrystallum_schema.json`** - Add Citation entity type
2. **`Relationships/relationship_types_registry_master.csv`** - Add citation relationships
3. **`JSON/chrystallum_schema.json`** - Regenerate with new entities/relationships

### CSV Format for Entities

Add to `JSON/chrystallum_schema.json`:

```csv
Work,Citation,Quoted text/prose from source with author attribution,Q49848
```

### CSV Format for Relationships

Add to `Relationships/relationship_types_registry_master.csv`:

```csv
Attribution,DESCRIBES,Citation describes entity/event,forward
Attribution,MENTIONS,Citation mentions entity,forward
Attribution,ANALYZES,Citation provides analysis of entity,forward
Attribution,EXTRACTED_FROM,Citation extracted from work,forward
Attribution,ATTRIBUTED_TO,Citation attributed to author,forward
Attribution,QUOTES,Citation is direct quote from source,forward
Attribution,INTERPRETS,Citation interprets entity/event,forward
Attribution,SUMMARIZES,Citation summarizes entity/event,forward
```

### After Updates

Run `consolidate_schema.py` to regenerate `JSON/chrystallum_schema.json` with the new citation architecture integrated.

