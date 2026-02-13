# Wikidata Backlink Enrichment Strategy

**Date:** February 13, 2026  
**Context:** Part of Federation Supercharging (Phase 2, Step 4b)  
**Status:** Strategy documented, ready for implementation  

---

## Overview

**Traditional Federation Approach:** Start with QID → fetch all outbound properties → get facts about entity

**Backlink Approach (NEW):** Start with QID → fetch all entities pointing to it → discover functional context

**The Game-Changer:** Reverse relationships provide concept expansion via **"What links here?"** queries. This automatically surfaces:
- Participations (what events/battles)
- Influences (what ideas/ideologies)
- Depictions (what cultural works)
- Causations (what crises/reforms)
- Eponyms (what things named after)

**Strategic Value:** Solves the "Unknown Unknowns" problem—agents don't need to know to ask about the Julian Calendar; they just ask "What points to Caesar?" and it reveals itself.

---

## Core Concept: Reverse Property Parsing

### Traditional Query (Outbound)
```sparql
SELECT ?prop ?value ?valueLabel WHERE {
  BIND(wd:Q1048 AS ?subject)     # Caesar
  ?subject ?prop ?value .         # What properties does Caesar have?
  SERVICE wikibase:label { ... }
}
```

**Results:** Birth date, death date, occupation, education, etc. ✓ (Known facts)

---

### Backlink Query (Inbound)
```sparql
SELECT ?source ?sourceLabel ?prop ?propLabel ?p31 ?p31Label WHERE {
  BIND(wd:Q1048 AS ?target)       # Caesar
  ?source ?prop ?target .          # What points TO Caesar?
  ?source wdt:P31 ?p31 .           # What IS that source entity?
  
  VALUES ?prop { 
    wdt:P710    # participant in (events)
    wdt:P1441   # present in work (depictions)
    wdt:P138    # named after (eponyms)
    wdt:P112    # founded by (institutions)
    wdt:P737    # influenced by (ideologies)
    wdt:P828    # has cause (causations)
  }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 500
```

**Results:** Battle of Pharsalus, Julian Calendar, Caesarism, Shakespeare's Julius Caesar, etc. ✓ (Unknown facts discovered!)

---

## Enrichment Buckets

### Bucket A: The Participator (P710 - Participant In)

**Question:** What events/battles/expeditions included this entity?

**Wikidata Filter:**
```sparql
?event wdt:P710 wd:Q1048 .         # Julius Caesar participated in...
?event wdt:P31 ?eventType .        # What type of event?
VALUES ?eventType {
  wd:Q18143 # Battle
  wd:Q4269  # War
  wd:Q1191  # Expedition
  wd:Q40231 # Siege
}
```

**Results for Caesar:**
- Battle of Pharsalus (Q25378)
- Siege of Alesia (Q165850)
- Crossing of the Rubicon (Q658154)
- Gallic Wars (Q41301)

**Chrystallum Action:**
```cypher
MATCH (caesar:Human {qid: "Q1048"})
MATCH (battle:Event {qid: "Q25378"})
CREATE (caesar)-[:PARTICIPATED_IN {
  source: 'wikidata_backlink',
  property: 'P710',
  confidence: 0.95,
  retrieved_at: datetime()
}]->(battle)
```

**Edge Properties:**
- `confidence: 0.95` (High - Wikidata maintains military history well)
- `source: 'wikidata_backlink'` (Provenance tracking)
- `property: 'P710'` (Enables filtering, compliance documentation)

---

### Bucket B: The Influencer (P737 - Influenced By)

**Question:** What concepts/ideologies/movements were influenced by this entity?

**Wikidata Filter:**
```sparql
?concept wdt:P737 wd:Q1048 .       # Something influenced by Caesar
?concept wdt:P31 ?conceptType .    # What type?
VALUES ?conceptType {
  wd:Q7257 # Political ideology
  wd:Q1047574 # Concept
  wd:Q4695322 # Scientific theory
}
```

**Results for Caesar:**
- Caesarism (political ideology concept)
- Julicism (political movement)
- Autocracy enhancements (governance philosophy)

**Chrystallum Action:**
```cypher
MATCH (caesar:Human {qid: "Q1048"})
MATCH (concept:Concept {qid: "Q1234567"})  # Caesarism
CREATE (caesar)-[:INFLUENCED {
  source: 'wikidata_backlink',
  property: 'P737',
  confidence: 0.90,
  retrieved_at: datetime()
}]->(concept)
```

**Edge Properties:**
- `confidence: 0.90` (Medium-High - Ideological influence is documented but sometimes interpretive)
- Chain effect: Enables discovery of Machiavelli influenced by Caesarism influenced by Caesar

---

### Bucket C: The Namesake (P138 - Named After)

**Question:** What entities were named after this entity?

**Wikidata Filter:**
```sparql
?namedThing wdt:P138 wd:Q1048 .    # Named after Caesar
?namedThing wdt:P31 ?typeClass .   # What type?
VALUES ?typeClass {
  wd:Q133 # Month / Calendar Unit
  wd:Q1734 # City
  wd:Q1347494 # Building
  wd:Q11226 # Organization
}
```

**Results for Caesar:**
- Month of July (English: July = "Iulius" = Julius Caesar)
- Calendar system variants
- Multiple Caesar Avenue / Caesar Boulevard street names
- Caesar Cipher (cryptography named after Caesar)
- Caesar Salad (disputed, but cultural reference)

**Chrystallum Action:**
```cypher
MATCH (caesar:Human {qid: "Q1048"})
MATCH (july:Month {qid: "Q129"})
CREATE (caesar)-[:EPONYM_OF {
  source: 'wikidata_backlink',
  property: 'P138',
  confidence: 0.90,
  retrieved_at: datetime()
}]->(july)
```

**Edge Properties:**
- `confidence: 0.90` (High for calendar, lower for streets: varies per materialized edge)
- Enables "What's named after me?" queries

---

### Bucket D: Cultural Reception (P1441 - Present In Work)

**Question:** In what cultural works (books, films, plays) is this entity depicted?

**Wikidata Filter:**
```sparql
?work wdt:P1441 wd:Q1048 .         # Work contains Caesar
?work wdt:P31 ?workType .          # What type of work?
VALUES ?workType {
  wd:Q7725634 # Literary work
  wd:Q11424 # Film
  wd:Q3994 # Creative work
  wd:Q387276 # Opera
  wd:Q5398426 # Play
}
```

**Results for Caesar:**
- Shakespeare's Julius Caesar (play)
- HBO's Rome (TV series)
- Dante's Inferno (literary work)
- Paradise Lost (John Milton)
- I, Claudius (historical fiction)
- Asterix & Obelix (comics)

**Chrystallum Action:**
```cypher
MATCH (caesar:Human {qid: "Q1048"})
MATCH (work:Work {qid: "Q8194"})  # Shakespeare's Julius Caesar
CREATE (caesar)-[:DEPICTED_IN {
  source: 'wikidata_backlink',
  property: 'P1441',
  confidence: 0.80,
  retrieved_at: datetime(),
  cultural_context: 'Reception History'
}]->(work)
```

**Edge Properties:**
- `confidence: 0.80` (Medium - Cultural references sometimes incidental)
- Enables "Reception History" subgraph analysis
- Use case: "How has this entity been represented across media?"

---

### Bucket E: Causation (P828 - Has Cause)

**Question:** What events/crises/reforms were caused by this entity?

**Wikidata Filter:**
```sparql
?effect wdt:P828 wd:Q1048 .        # Something was caused by Caesar
?effect wdt:P31 ?effectType .      # What type of effect?
VALUES ?effectType {
  wd:Q40231 # Siege
  wd:Q18143 # Battle
  wd:Q179593 # Civil war
  wd:Q133 # Reformation/reform
}
```

**Results for Caesar:**
- Roman Civil War (58-50 BCE) - causation chain
- Crossing of the Rubicon (triggering event)
- Pompey's flight to Egypt
- Egyptian Civil War interventions

**Chrystallum Action:**
```cypher
MATCH (caesar:Human {qid: "Q1048"})
MATCH (war:Event {qid: "Q186089"})  # Roman Civil War
CREATE (caesar)-[:HAS_CAUSE {
  source: 'wikidata_backlink',
  property: 'P828',
  confidence: 0.85,
  retrieved_at: datetime()
}]->(war)
```

**Edge Properties:**
- `confidence: 0.85` (Medium-High - Historical causation is documented in scholarly consensus)
- Enables "What changed because of me?" temporal chains

---

### Bucket F: Legacy Institutions (P112 - Founded By)

**Question:** What institutions/organizations/works did this entity found?

**Wikidata Filter:**
```sparql
?institution wdt:P112 wd:Q1048 .   # Founded by Caesar
?institution wdt:P31 ?instType .   # What type?
VALUES ?instType {
  wd:Q133 # Organization
  wd:Q1347494 # Building
  wd:Q4406 # Dynasty
  wd:Q11899 # Law/Legislation
}
```

**Results for Caesar:**
- Julia gens (dynastic continuation)
- Colonies named after Caesar (Colonia Caesarea)
- Legal reforms attributed to Caesar's foundation

**Chrystallum Action:**
```cypher
MATCH (caesar:Human {qid: "Q1048"})
MATCH (dynasty:Dynasty {qid: "Q652"})  # Julia gens
CREATE (caesar)-[:FOUNDED {
  source: 'wikidata_backlink',
  property: 'P112',
  confidence: 0.90,
  retrieved_at: datetime()
}]->(dynasty)
```

---

## Key Corrections to Original Insight

**Correction 1: P15 is NOT "influenced by"**
- ❌ P15 = "is designed to have property"
- ✅ P737 = "influenced by" (correct property)
- ✅ P828 = "has cause" (valid, more constrained)

**Correction 2: MediaWiki "What links here" vs. Statement Backlinks**
- ❌ Don't use MediaWiki page-link API (surface-level page references)
- ✅ Use SPARQL reverse triples: `?source ?prop ?target` (semantic relationships)
- This ensures you get structured knowledge graph relationships, not just page citations

**Correction 3: CIDOC Mapping is Manual**
- ❌ Wikidata P31 classes ≠ CIDOC classes automatically
- ✅ Maintain explicit mapping table: Wikidata P31 → CIDOC C classes
- Example:
  ```
  wd:Q18143 (Battle) → E5_Event (CIDOC-CRM)
  wd:Q2996394 (Literary work) → F1_Work
  wd:Q486972 (Human) → E21_Person
  ```

---

## Implementation Workflow

### Step 1: Prepare Backlink Query

```python
def prepare_backlink_query(qid, property_whitelist=None):
    """Generate SPARQL query for entity backlinks"""
    
    if property_whitelist is None:
        property_whitelist = [
            "wdt:P710",   # participant in
            "wdt:P1441",  # present in work
            "wdt:P138",   # named after
            "wdt:P112",   # founded by
            "wdt:P737",   # influenced by
            "wdt:P828",   # has cause
        ]
    
    prop_values = " ".join(property_whitelist)
    
    sparql = f"""
    SELECT ?source ?sourceLabel ?prop ?propLabel ?p31 ?p31Label WHERE {{
      BIND(wd:{qid} AS ?target)
      
      VALUES ?prop {{ {prop_values} }}
      ?source ?prop ?target .
      ?source wdt:P31 ?p31 .
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 500
    """
    
    return sparql
```

### Step 2: Query Wikidata & Bucket Results

```python
def fetch_and_bucket_backlinks(qid):
    """Fetch backlinks, bucket by property + P31"""
    
    sparql = prepare_backlink_query(qid)
    results = query_wikidata(sparql)
    
    buckets = {
        "participations": [],
        "influences": [],
        "eponyms": [],
        "depictions": [],
        "causations": [],
        "legacy": [],
        "other": []
    }
    
    for result in results:
        source_qid = result['source']
        prop = result['prop']
        p31 = result['p31']  # instance_of class
        label = result['sourceLabel']
        
        # Classify by property + P31
        if prop == "wdt:P710" and is_event(p31):
            buckets["participations"].append({
                'qid': source_qid,
                'label': label,
                'p31': p31
            })
        elif prop == "wdt:P737" and is_concept(p31):
            buckets["influences"].append({...})
        elif prop == "wdt:P138" and is_named_thing(p31):
            buckets["eponyms"].append({...})
        elif prop == "wdt:P1441" and is_work(p31):
            buckets["depictions"].append({...})
        elif prop == "wdt:P828" and is_event(p31):
            buckets["causations"].append({...})
        elif prop == "wdt:P112" and is_institution(p31):
            buckets["legacy"].append({...})
        else:
            buckets["other"].append({...})
    
    return buckets
```

### Step 3: Determine Confidence Scores

```python
def calculate_confidence(prop, p31, source_authority="wikidata"):
    """
    Confidence varies by property + P31 combination
    Reflects reliability of Wikidata's coverage for this type
    """
    
    confidence_matrix = {
        ("P710", "Event"): 0.95,      # Battles well-documented
        ("P710", "War"): 0.95,
        ("P710", "Expedition"): 0.90,
        
        ("P737", "Concept"): 0.85,    # Ideological influence sometimes debated
        ("P737", "Ideology"): 0.80,
        
        ("P138", "Month"): 0.98,      # Named-after facts very reliable
        ("P138", "Calendar"): 0.98,
        ("P138", "City"): 0.70,       # City names often contested
        ("P138", "Building"): 0.65,
        
        ("P1441", "Work"): 0.80,      # Cultural references sometimes peripheral
        ("P1441", "Film"): 0.85,
        ("P1441", "Literary work"): 0.85,
        
        ("P828", "Event"): 0.75,      # Causation historically debated
        ("P828", "War"): 0.70,
        
        ("P112", "Institution"): 0.90, # Founding clearly documented
        ("P112", "Dynasty"): 0.95,
    }
    
    key = (prop.replace("wdt:", ""), p31)
    return confidence_matrix.get(key, 0.60)  # Default: conservative
```

### Step 4: Materialize High-Confidence Edges

```python
def materialize_backlinks(entity_id, buckets, confidence_threshold=0.75):
    """
    Generate Cypher CREATE statements for backlink edges
    Only create if confidence >= threshold
    """
    
    cypher_statements = []
    ambiguous_items = []
    
    # Process each bucket
    for item in buckets["participations"]:
        conf = calculate_confidence("P710", item['p31'])
        if conf >= confidence_threshold:
            cypher = f"""
            MATCH (entity:Entity {{entity_id: '{entity_id}'}})
            MATCH (event:Event {{qid: '{item['qid']}'}})
            CREATE (entity)-[:PARTICIPATED_IN {{
              source: 'wikidata_backlink',
              property: 'P710',
              confidence: {conf},
              retrieved_at: datetime()
            }}]->(event)
            """
            cypher_statements.append(cypher)
        else:
            ambiguous_items.append((item, conf, "PARTICIPATED_IN"))
    
    # Repeat for other buckets...
    
    return cypher_statements, ambiguous_items
```

### Step 5: Queue Ambiguous Items for Agent Review

```python
def queue_for_agent_review(ambiguous_items, entity_id):
    """
    Create PENDING_REVIEW links for low-confidence backlinks
    Agents can assess during Phase 3 evaluation
    """
    
    cypher_statements = []
    
    for item, confidence, edge_type in ambiguous_items:
        cypher = f"""
        MATCH (entity:Entity {{entity_id: '{entity_id}'}})
        CREATE (entity)-[:PENDING_REVIEW {{
          target_qid: '{item['qid']}',
          target_label: '{item['label']}',
          edge_type: '{edge_type}',
          source: 'wikidata_backlink',
          confidence: {confidence},
          requires_human_review: true,
          queued_at: datetime()
        }}]->(review_node)
        """
        cypher_statements.append(cypher)
    
    return cypher_statements
```

---

## Performance Considerations

### Query Timing
- **Per-entity backlink query:** 500-2000ms (Wikidata SPARQL endpoint)
- **Batch query 1000 entities:** 500-2000 seconds (8-33 minutes)
- **Recommendation:** Parallelize across Wikidata endpoint instances if available

### Network Optimization
```python
# Batch queries to reduce round-trips
def batch_backlink_queries(qid_list, batch_size=10):
    """
    Group backlink queries to reduce network overhead
    """
    results = {}
    
    for batch_qids in chunks(qid_list, batch_size):
        sparql = f"""
        SELECT ?qid ?source ?sourceLabel ?prop ?p31 ?p31Label WHERE {{
          VALUES ?qid {{ {" ".join(["wd:" + q for q in batch_qids])} }}
          
          ?source ?prop ?qid .
          ?source wdt:P31 ?p31 .
          
          BIND(strafter(str(?qid), "Q") AS ?qid_num)
          
          VALUES ?prop {{
            wdt:P710 wdt:P1441 wdt:P138 wdt:P112 wdt:P737 wdt:P828
          }}
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        batch_results = query_wikidata(sparql)
        results.update(batch_results)
    
    return results
```

### Storage Optimization

**Pre-materialization:** Cache backlink results in Neo4j for 90 days

```cypher
-- Store backlink cache
MATCH (e:Entity {qid: "Q1048"})
SET e.backlink_cache = {
  "participations": [{"qid": "Q25378", "confidence": 0.95}, ...],
  "influences": [...],
  ...
},
    e.backlink_cache_retrieved_at = datetime(),
    e.backlink_cache_ttl = 7776000  # 90 days in seconds
```

---

## Expected Impact

### Coverage
- **High-profile entities (1000+ backlinks):** 500-1000 new edges each
- **Medium entities (100-1000 backlinks):** 50-200 new edges
- **Low-profile entities (<100 backlinks):** 5-30 new edges
- **Expected materialization rate:** 60-80% of discovered backlinks (after confidence filtering)

### Use Cases Unlocked
1. **Reception History:** "Show me all cultural works depicting this person"
2. **Temporal Biography:** "What events did this person participate in? (auto-timeline)
3. **Ideological Influence:** "What concepts/movements trace back to this person?"
4. **Legacy Discovery:** "What institutions/things were founded/named after this?"
5. **Causation Chains:** "What crises/transformations did this trigger?"

### Agent Intelligence
- Agents no longer require explicit prompting to discover enrichment
- Backlink buckets automatically categorize enrichment (participations vs. depictions vs. influences)
- Confidence scores enable agents to prioritize high-value relationships
- Ambiguous items queued for human review (audit trail maintained)

---

## Integration with Main Architecture

**File:** Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md

**Cross-references:**
- Section 4.5 (Wikidata Integration): References this strategy for concept expansion
- Section 5 (Agent Architecture): Agents use backlink buckets to evaluate claims
- Section 10 (QA): Backlink provenance stored for audit trail

**Related Sections:**
- Section 3 (Entity Layer): Backlinks enrich entity properties
- Section 4 (Subject Layer): Backlinks connect subjects to participation/influence
- Section 6 (Claims Layer): Backlinks generate candidate facts for claim evaluation

---

## Timeline

**Phase 2, Step 4b:** Backlink Enrichment  
**Estimated Duration:** 1 day  
**Dependencies:** Phase 2 Step 4a (Authority links supernode prerequisite)

| Task | Time | Depends On |
|------|------|-----------|
| Prepare backlink query template | 1 hour | Phase 2 Step 4a complete |
| Test on 100 high-profile entities | 2 hours | Query template ready |
| Implement bucketing logic | 2 hours | Test results validated |
| Deploy batch query processor | 2 hours | Bucketing logic verified |
| Run full enrichment on 10K entities | 4-6 hours | Batch processor ready |
| Agent review queue setup | 1 hour | Enrichment complete |
| **Total** | **~13-15 hours (~1.5 days)** | |

---

## Success Metrics

- ✅ 60-80% of entities have ≥1 backlink edge materialized
- ✅ Average 50-200 new relationship edges per entity
- ✅ <2% of materialized edges flagged for correction (via agent review)
- ✅ Reception History subgraph discoverable (cultural works linked to entities)
- ✅ Causation chains traceable (events linked to catalysts)
- ✅ Provenance complete (source, property, confidence, timestamp on all edges)

---

## References

- **Architecture:** Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md (Section 4.5)
- **Implementation Roadmap:** Neo4j/IMPLEMENTATION_ROADMAP.md (Phase 2, Step 4b)
- **Schema Guide:** Neo4j/schema/SCHEMA_BOOTSTRAP_GUIDE.md (Federation Supercharging)
- **Wikidata SPARQL:** https://query.wikidata.org/
- **Wikidata Properties:** https://www.wikidata.org/wiki/Wikidata:Database_reports/Properties

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-13  
**Status:** Ready for Phase 2 Implementation
