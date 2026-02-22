# Poly-Temporal Faceting Strategy for Chrystallum

**Date:** February 13, 2026  
**Context:** Part of Subject Layer Enhancement (Section 4.3)  
**Status:** Strategy documented, ready for Phase 2 implementation  

---

## Overview

**The Problem:** Time is the most contested dimension in historical knowledge graphs.

- A unified timeline is impossible
- Different domains slice time by different criteria
- The same event is valid in multiple temporal frames simultaneously
- User queries are fuzzy (\"ancient times\", \"recently\", \"Boomer era\")

**The Solution: Poly-Temporal Faceting**

Instead of forcing an event into one period, anchor it in **multiple OCCURRED_DURING edges**, each labeled with a facet showing which authority system defines that temporal relationship.

---

## Six Dimensions of Temporal Authority

### **1. Historiographical Slice (Human Narrative)**

**Definition:** Time divided by human agency, culture, and power. Often Eurocentric or dynastic.

**Subcategories:**

| Type | Examples | Characteristics |
|------|----------|------------------|
| **Dynastic/Regnal** | Victorian Era, Ming Dynasty, Augustan Age | Defined by ruler lifespan or reign |
| **Cultural/Intellectual** | Renaissance, Enlightenment, Modernism | Defined by shifts in thought, art, philosophy |
| **Political/Constitutional** | Roman Republic vs. Empire, Weimar Republic | Defined by systems of government |
| **Technological Ages** | Bronze Age, Iron Age, Information Age | Defined by dominant tool/material (Thomsen's Three-Age) |
| **Crisis/Conflict** | The Great Depression, Hundred Years' War | Defined by disruption or event |

**Example Entity (Julius Caesar):**
```cypher
(Event:CrossingRubicon)
  -[:OCCURRED_DURING {
    facet: "Dynastic",
    period_label: "Pompeian Era",
    start: "0066",
    end: "0048",
    authority: "Wikidata",
    confidence: 0.85
  }]->(:Period)
  
  -[:OCCURRED_DURING {
    facet: "Political",
    period_label: "Roman Republic",
    start: "-0509",
    end: "-0027",  // Ends with Augustus
    authority: "PeriodO",
    confidence: 0.90
  }]->(:Period)
```

**Query Pattern:**
```sparql
# Find all historiographical periods containing this date
SELECT ?period ?periodLabel ?facet WHERE {
  ?period crm:P4_has_time_span ?timespan .
  ?timespan crm:P82_at_some_time_within ?date .
  ?period rdfs:label ?periodLabel .
  ?period rdf:type ?facet .
  FILTER(?date >= "0049"^^xsd:gYear && ?date <= "0049"^^xsd:gYear)
  FILTER(?facet IN (wd:Q11148, crm:E5_Event, crm:E27_Site))
}
```

---

### **2. Scientific Slice (Physical Reality)**

**Definition:** Time divided by observable physical changes in Earth or universe. Quantitative and distinct from human history.

**Subcategories:**

| Type | Examples | Hierarchy | Authority |
|------|----------|-----------|-----------|
| **Geologic (GTS)** | Mesozoic Era, Jurassic Period, Anthropocene | Eon → Era → Period → Epoch → Age | IUGS standard, Wikidata P7511 |
| **Astronomical** | Stelliferous Era, Solar Cycle 25 | Varies by system | IAU (International Astronomical Union) |
| **Climatological** | Little Ice Age, Medieval Warm Period | Named events/phases | Climate records, Paleoclimatology |
| **Evolutionary/Biological** | Age of Reptiles, Cambrian Explosion | Flora/fauna dominance | Paleobiology, Evolutionary theory |

**Key Insight:** Geologic time overlaps but doesn't align with human history:
- Eruption of Vesuvius (79 AD): **Holocene Epoch** (not Bronze Age- that was 3,000 years earlier!)
- Ice Age humans: Would be **Pleistocene**, not \"Ice Age\" in the cultural sense

**Example Schema:**
```cypher
CREATE (period:Period {
  entity_id: "per_holocene_001",
  label: "Holocene Epoch",
  temporal_facet: "Scientific",
  scientific_subtype: "Geologic",
  
  start_date: "-0010000",        // 10,000 BCE in ISO 8601
  end_date: "present",
  
  gts_rank: "Epoch",              // Geologic rank
  gts_parent: "Quaternary Period",
  
  wikidata_qid: "Q200128",
  gts_authority: "IUGS",
  
  definition_source: "IUGS Chronostratigraphic Chart 2023",
  certainty: "definite"
})

CREATE (vesuvius:Event {event_id: "evt_vesuvius_001"})
  -[:OCCURRED_DURING {
    facet: "Scientific",
    scientific_type: "Geologic",
    authority_tier: "TIER_1",
    confidence: 0.99
  }]->(period)
```

**Query Pattern:**
```sparql
# Fetch GTS period containing this date
SELECT ?period ?periodLabel ?gtsRank ?startDate ?endDate WHERE {
  ?period wdt:P7511 ?gtsChronometer .         # GTS classification
  ?period wdt:P580 ?startDate .               # Start date
  ?period wdt:P582 ?endDate .                 # End date
  ?period rdfs:label ?periodLabel .
  FILTER(LANG(?periodLabel) = "en")
}
```

---

### **3. Religious/Calendrical Slice (Sacred Time)**

**Definition:** Time divided by revelation and ritual. Creates parallel chronologies requiring ISO-8601 mapping.

**Subcategories:**

| Type | Examples | Base Year | Offset from CE |
|------|----------|-----------|--------|
| **Soteriological (Salvation History)** | Anno Domini (AD/CE), Ante Christum (BC/BCE) | Jesus Christ birth | 0 |
| | Hijri (AH) / Islamic calendar | Hegira (Muhammad's journey) | +622 CE |
| | Kali Yuga (Hindu calendar) | Beginning of current age | -3102 CE |
| | Jewish calendar (AM) | Creation of world | -3760 CE |
| **Liturgical (Cyclic Ritual Time)** | Advent, Lent, Ramadan | Annual cycles | Repeats yearly |
| | Shmita Year (Jewish) | 7-year agricultural cycle | Every 7 years |
| | Church Fathers' era cycles | Ecclesiastical periods | Custom |

**Critical Implementation Issue:**
- Date \"49 AH\" must convert to \"670 CE\" (49 years after Hegira in 622)
- Conversion requires accuracy to decimal year (accounting for lunar vs. solar calendars)
- Confidence drops when converting between calendar systems (0.90 for CE → 0.70 for AH)

**Example Schema:**
```cypher
CREATE (hijra_event:Event {
  entity_id: "evt_hegira_001",
  iso_date: "0622-07-16",        // Julian calendar date
  label: "Hegira (Muhammad's departure from Mecca)"
})

CREATE (hijra_year_1:Year{
  entity_id: "yr_hijra_1_001",
  hijra_year: 1,
  gregorian_start: "0622-07-16",
  gregorian_end: "0623-07-15",
  calendar_system: "Islamic",
  
  authority_tier: "TIER_2",
  confidence: 0.85
})

// Example: Converting an Islamic date
CREATE (treaty_event:Event {
  iso_date: "0756",              // Treaty of Cordoba
  label: "Treaty of Cordoba"
})
  -[:OCCURRED_DURING {
    facet: "Religious",
    calendar_system: "Islamic",
    hijra_year: 138,
    gregorian_equivalent: "0756",
    conversion_confidence: 0.75
  }]->(period)
```

---

### **4. Economic/Legal Slice (Bureaucratic Time)**

**Definition:** Time divided by money and law. Arbitrary but rigorous.

**Subcategories:**

| Type | Examples | Duration | Authority |
|------|----------|----------|-----------|
| **Fiscal/Financial** | Q4 2025, Fiscal Year 2026, Tax Year | Variable by jurisdiction | Tax authorities (IRS, HMRC, etc.) |
| **Legal/Statutory** | Copyright Term (Life + 70), Statute of Limitations | Variable by jurisdiction/crime | Legal codes |
| **Legislative Periods** | Session of Parliament, Congressional term | Fixed (4, 5, 7 years) | Government |
| **Budget Cycles** | Federal Budget Year, Corporate fiscal year | Usually 12 months | Organizations |

**Use Case: Querying for \"events in Q4 2025\" or \"tax year 2026 revenues\"**

```cypher
CREATE (q4_2025:FiscalPeriod {
  entity_id: "fis_q4_2025",
  label: "Q4 2025",
  fiscal_quarter: 4,
  fiscal_year: 2025,
  
  start_date: "2025-10-01",
  end_date: "2025-12-31",
  
  authority: "International Accounting Standards",
  confidence: 0.95
})

CREATE (revenue_event:Event {event_id: "evt_corp_revenue_2025q4"})
  -[:OCCURRED_DURING {
    facet: "Economic",
    economic_type: "Fiscal",
    fiscal_context: "Q4",
    confidence: 0.98
  }]->(q4_2025)
```

---

### **5. PeriodO Meta-Slice (Academic Consensus)**

**Definition:** Custom periods defined by scholars, often spatio-temporally bounded. Authority: Wikidata P9350.

**Characteristics:**
- **Spatio-Temporal Bounding:** \"Late Bronze Age\" ≠ same dates in Greece vs. Scandinavia
- **Author-Defined:** \"The Long Nineteenth Century\" (Hobsbawm) = 1789–1914, not 1800–1899
- **Domain-Specific:** \"Georgian Era\" (architecture) differs from \"Georgian Period\" (history)

**Example: Late Bronze Age**

```cypher
CREATE (lba_greece:Period {
  entity_id: "per_lba_greece_001",
  label: "Late Bronze Age (Greece)",
  temporal_facet: "Historiographical",
  
  start_date: "-1200",
  end_date: "-0800",
  geographic_scope: ["Greece", "Aegean"],
  
  period_o_id: "p0h7k2",
  wikidata_qid: "Q209851",
  scholarly_source: "Archaeological Consensus",
  
  authority_tier: "TIER_2",
  confidence: 0.85
})

CREATE (lba_scandinavia:Period {
  entity_id: "per_lba_scandinavia_001",
  label: "Late Bronze Age (Scandinavia)",
  temporal_facet: "Historiographical",
  
  start_date: "-0500",           // Much later!
  end_date: "-0200",
  geographic_scope: ["Scandinavia", "Northern Europe"],
  
  period_o_id: "p0h7k3",         // Different PeriodO ID
  scholarly_source: "Archaeological Consensus (regional variation)",
  
  authority_tier: "TIER_2",
  confidence: 0.80
})

// Same event, different periods depending on geography
CREATE (artifact:Event {label: "Bronze tool discovered"})
  -[:OCCURRED_DURING {
    facet: "Historiographical",
    geographic_scope: "Greece",
    period_label: "Late Bronze Age (Greece)",
    confidence: 0.85
  }]->(lba_greece)

CREATE (artifact)
  -[:OCCURRED_DURING {
    facet: "Historiographical",
    geographic_scope: "Scandinavia",
    period_label: "Late Bronze Age (Scandinavia)",
    confidence: 0.80,
    note: "Different period boundaries in this region"
  }]->(lba_scandinavia)
```

**Query Pattern (PeriodO Lookup):**
```sparql
# Query PeriodO for period definitions with geographic scope
SELECT ?periodLabel ?startDate ?endDate ?spatialCoverage WHERE {
  SERVICE <http://perio.do/sparql> {
    ?period pe:name ?periodLabel ;
            pe:start_year ?startDate ;
            pe:stop_year ?endDate ;
            pe:spatialCovering ?spatialCovering .
    ?spatialCovering rdfs:label ?spatialCoverage .
  }
}
```

---

### **6. Fuzzy/Relative Slice (User & LLM Input)**

**Definition:** Non-standard time from user queries. Critical for conversational interfaces processing vague temporal expressions.

**Types:**

| Type | Examples | Mapping Strategy | Confidence |
|------|----------|------------------|------------|
| **Generational** | \"Boomers\" (1946–1964), \"Gen Z\" (1997–2012) | Map to demographic cohort periods | 0.70 |
| **Vague Terms** | \"In ancient times\", \"Recently\", \"Back in the day\" | Fuzzy matching to Historiographical periods | 0.40-0.60 |
| **Relative to Today** | \"10 years ago\", \"Next century\" | Calculate from current date | 0.95 |
| **Ordinal Time** | \"The 60s\", \"Victorian era\", \"Pre-Columbian\" | Fuzzy match against known periods | 0.65 |
| **Narrative Time** | \"When Caesar was alive\", \"During the Renaissance\" | Entity-linked temporal reference | 0.75 |

**Implementation Approach:**

```python
# Python pseudo-code for fuzzy temporal resolution
class FuzzyTemporalResolver:
    def resolve_fuzzy_temporal(self, user_input):
        \"\"\"
        Map user fuzzy temporal reference to Chrystallum periods
        Examples:
          \"ancient times\" → Historiographical periods (Classical Antiquity, etc.)
          \"Boomers\" → Generational period (1946-1964)
          \"recently\" → Last 50 years
          \"Victorian era\" → 1837-1901
        \"\"\"
        
        fuzzy_mappings = {
            # Vague temporal references
            \"ancient\": {\n                \"periods\": [\"Classical Antiquity\", \"Antiquity\"],
                \"confidence\": 0.50,
                \"facet\": \"Historiographical\",
                \"approximate_range\": (\"-0800\", \"0500\")
            },
            \"medieval\": {
                \"periods\": [\"Middle Ages\"],
                \"confidence\": 0.60,
                \"facet\": \"Historiographical\",
                \"approximate_range\": (\"0500\", \"1453\")
            },
            \"recently\": {
                \"periods\": [\"Modern\", \"Contemporary\"],
                \"confidence\": 0.40,
                \"facet\": \"Historiographical\",
                \"approximate_range\": (str(current_year - 50), str(current_year))
            },
            
            # Generational
            \"boomer\": {
                \"periods\": [\"Baby Boomer\"],
                \"confidence\": 0.85,
                \"facet\": \"Fuzzy/Generational\",
                \"range\": (\"1946\", \"1964\")
            },
            \"gen z\": {
                \"periods\": [\"Generation Z\"],
                \"confidence\": 0.80,
                \"facet\": \"Fuzzy/Generational\",
                \"range\": (\"1997\", \"2012\")
            },
            
            # Named periods
            \"victorian\": {
                \"periods\": [\"Victorian Era\"],
                \"confidence\": 0.90,
                \"facet\": \"Historiographical\",
                \"range\": (\"1837\", \"1901\")
            },
            \"renaissance\": {
                \"periods\": [\"Renaissance\"],
                \"confidence\": 0.75,
                \"facet\": \"Historiographical\",
                \"range\": (\"1300\", \"1700\")  # Contested!
            }
        }
        
        # Fuzzy matching
        matched_periods = fuzzy_match(user_input, fuzzy_mappings)
        
        # Create OCCURRED_DURING edges with lower confidence
        for period in matched_periods:
            cypher = f\"\"\"
            MATCH (event:Event {{event_id: '{event_id}'}})
            MATCH (p:Period {{label: '{period['label']}'}})
            CREATE (event)-[:OCCURRED_DURING {{
              facet: 'Fuzzy/User Input',
              user_query: '{user_input}',
              confidence: {period['confidence']},
              requires_validation: true,
              queued_for_agent_review: true
            }}]->(p)
            \"\"\"
            
        return matched_periods
```

**Example Ingestion:**

User Query: \"Caesar was active during ancient times\"

```cypher
# Temporal Agent parses fuzzy reference
CREATE (claim:Claim {
  claim_text: "Caesar was active during ancient times",
  temporal_anchor: "ancient times"  // Fuzzy!
})

// Resolve \"ancient times\" to Historiographical periods
MATCH (claim:Claim {temporal_anchor: "ancient times"})
WITH claim
// Fuzzy match: Try Classical Antiquity, Antiquity, etc.
MATCH (period:Period {label: "Classical Antiquity"})
CREATE (claim)-[:TEMPORAL_CONTEXT {
  facet: "Fuzzy/User Input",
  original_user_query: "ancient times",
  mapped_to_period: "Classical Antiquity",
  confidence: 0.50,
  requires_validation: true,
  queued_for_agent_review: true
}]->(period)
```

---

## Implementation Workflow

### Step 1: Event Ingestion

When an event enters the graph, query PeriodO for ALL applicable periods:

```python
def ingest_event_with_temporal_facets(event_data):
    \"\"\"
    Ingest event and automatically populate OCCURRED_DURING edges
    for all applicable temporal facets
    \"\"\"
    iso_date = normalize_to_iso8601(event_data['date'])
    
    # Query PeriodO for periods containing this date
    periodos_results = query_periodo_by_date(iso_date)
    
    cypher_statements = []
    
    for periodo in periodos_results:
        # Classify by facet type
        facet = classify_periodo_facet(periodo)
        
        # Determine confidence based on facet
        confidence = calculate_confidence(facet, periodo)
        
        # Create OCCURRED_DURING edge
        cypher = f\"\"\"
        MATCH (event:Event {{event_id: '{event_data['id']}'}})
        CREATE (event)-[:OCCURRED_DURING {{
          facet: '{facet}',
          period_label: '{periodo['label']}',
          period_o_id: '{periodo['id']}',
          start_date: '{periodo['start']}',
          end_date: '{periodo['end']}',
          geographic_scope: {periodo.get('geographic_scope', [])},
          authority_tier: 'TIER_2',
          confidence: {confidence},
          source: 'PeriodO',
          certainty: 'definite'
        }})->(period)
        \"\"\"
        cypher_statements.append(cypher)
    
    return cypher_statements
```

### Step 2: Facet Classification

Classify periods by their slicing dimension:

```python
def classify_periodo_facet(periodo_record):
    \"\"\"
    Classify a PeriodO period into one of six facet types
    \"\"\"
    
    # Check for geologic classification
    if periodo_record.get('gts_rank'):
        return \"Scientific\"
    
    # Check for religious calendar system
    if periodo_record.get('calendar_system') in ['Islamic', 'Hebrew', 'Hindu']:
        return \"Religious\"
    
    # Check for economic/fiscal
    if 'fiscal' in periodo_record.get('keywords', []).lower():
        return \"Economic\"
    
    # Check for dynastic
    if 'dynasty' in periodo_record.get('keywords', []).lower():
        return \"Dynastic\"
    
    # Default to Historiographical
    return \"Historiographical\"
```

### Step 3: Confidence Scoring

Confidence varies by facet:

```python
def calculate_confidence(facet, periodo):
    \"\"\"
    Confidence matrix based on facet type and data completeness
    \"\"\"
    confidence_matrix = {
        \"Scientific\": {
            \"Geologic\": 0.95,
            \"Astronomical\": 0.90,
            \"Climatological\": 0.80,
            \"Biological\": 0.75
        },
        \"Historiographical\": {
            \"Dynastic\": 0.85,
            \"Cultural\": 0.70,
            \"Political\": 0.80,
            \"Technological\": 0.65,
            \"Crisis\": 0.75
        },
        \"Religious\": 0.75,
        \"Economic\": 0.80,
        \"PeriodO\": 0.90,  # High confidence if from authoritative gazetteer
        \"Fuzzy\": 0.50
    }
    
    base_confidence = confidence_matrix.get(facet, {}).get(periodo.get('subtype'), 0.70)
    
    # Reduce confidence if end date is distant future or uncertain
    if periodo.get('certainty') == 'approximate':
        base_confidence *= 0.8
    
    # Boost if multiple sources agree
    if len(periodo.get('sources', [])) > 1:
        base_confidence = min(0.99, base_confidence * 1.1)
    
    return base_confidence
```

### Step 4: Query Patterns for Temporal Agents

**Query 1: \"What periods apply to this event?\"**

```cypher
MATCH (event:Event {event_id: "evt_vesuvius_001"})
-[:OCCURRED_DURING {facet: $facet}]->(period:Period)
RETURN period, event.OCCURRED_DURING
LIMIT 10
```

**Query 2: \"According to whom? (All facets for an event)\"**

```cypher
MATCH (event:Event {label: "Eruption of Vesuvius"})
-[rel:OCCURRED_DURING]->(period:Period)
RETURN period.label, rel.facet, rel.confidence
ORDER BY rel.confidence DESC
```

**Query 3: \"Find events in this Historiographical period\"**

```cypher
MATCH (period:Period {label: "Classical Antiquity", temporal_facet: "Historiographical"})
<-[:OCCURRED_DURING {facet: "Historiographical"}]-(event:Event)
RETURN event
```

**Query 4: \"Geographic time slicing (Late Bronze Age varies by region)\"**

```cypher
MATCH (event:Event {label: "Bronze tool discovered"})
-[rel:OCCURRED_DURING {geographic_scope: "Greece"}]->(period:Period)
RETURN period
// vs.
MATCH (event:Event {label: "Bronze tool discovered"})
-[rel:OCCURRED_DURING {geographic_scope: "Scandinavia"}]->(period:Period)
RETURN period
```

---

## Expected Impact

### Coverage
- **Events with 3-6 temporal facet anchors:** 80%+ of ingested events
- **PeriodO reference:** 70%+ of events
- **Fuzzy temporal queries:** 90% successful resolution with confidence ≥0.50

### Use Cases Unlocked
1. **Poly-Temporal Query:** \"Show me everything that happened in the 79 AD / Holocene / Flavian Dynasty / Classical Antiquity\"
2. **Geographic Time Variation:** \"When was the Late Bronze Age in Greece vs. Scandinavia?\"
3. **Academic Consensus:** \"According to PeriodO scholars, which authorities agree on this period?\"
4. **Fuzzy Input:** \"What happened in ancient times? (map to Classical Antiquity, Bronze Age, etc.)\"
5. **Diplomatic Periods:** \"Events during the Cold War / Q3 2008 / Ramadan 1435 AH\"

### Agent Intelligence
- Agents ask \"According to whom?\" not just \"When?\"
- Temporal conflicts automatically detected (if date outside all periods, flag for review)
- Fuzzy inputs queued for validation before materialization
- Confidence scores guide agent prioritization

---

## Files & Timeline

### Primary Implementation
- **File:** `Neo4j/TEMPORAL_FACET_STRATEGY.md` (this document)
- **Reference:** Main architecture Section 4.3 (updated)
- **Implementation Guide:** `Neo4j/IMPLEMENTATION_ROADMAP.md` (Phase 2, new subsection)

### Phase 2 Timeline
**Phase 2, Step 3: Temporal Facet Population**  
**Estimated Duration:** 1-2 days  
**Dependencies:** Phase 1 schema complete, PeriodO API accessible

| Task | Duration | Depends On |
|------|----------|-----------|
| Finalize facet classification logic | 2 hours | Phase 1 complete |
| Implement PeriodO query wrapper | 3 hours | PeriodO API access |
| Test on 100high-profile events | 2 hours | Query wrapper ready |
| Deploy batch temporal facet population | 3 hours | Testing validates approach |
| Fuzzy temporal resolver implementation | 4 hours | Basic facet population working |
| Agent review queue setup | 1 hour | All above complete |
| **Total** | **~15-16 hours (~2 days)** | |

---

## Integration with Main Architecture

**File:** Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md  
**Section:** 4.3 Temporal Authority Alignment & Poly-Temporal Faceting

**Cross-references:**
- Section 3.4 (Temporal Modeling in Entity Layer) → Updated with facet edge pattern
- Section 4.3 (This section) → Core poly-temporal framework
- Section 5 (Agent Architecture) → Temporal Agent uses facet queries
- Section 10 (QA) → Temporal validation rules based on facets

---

## Success Metrics

- ✅ 80%+ of events have 3+ temporal facet anchors
- ✅ 70%+ of events linked to PeriodO
- ✅ Geographic time variation correctly modeled (Late Bronze Age Greece ≠ Scandinavia)
- ✅ Fuzzy temporal queries resolve with confidence ≥0.50
- ✅ Temporal conflicts detected & queued for agent review
- ✅ Provenance complete (source, facet, confidence, certainty on all edges)

---

## References

- **Architecture:** Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md (Section 4.3)
- **Wikidata Temporal Properties:**
  - P580: Start time
  - P582: End time
  - P9350: PeriodO period ID (PeriodO reference)
  - P7511: Geologic Time (GTS classification)
- **PeriodO:** https://perio.do/ (Academic period gazetteer)
- **IUGS Chronostratigraphic Chart:** https://stratigraphy.org/
- **Wikidata Query Service:** https://query.wikidata.org/

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-13  
**Status:** Ready for Phase 2 Implementation
