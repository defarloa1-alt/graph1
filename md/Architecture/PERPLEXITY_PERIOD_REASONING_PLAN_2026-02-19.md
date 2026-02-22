# Perplexity-Assisted Period & Subject Reasoning Plan

**Date:** 2026-02-19  
**Status:** In Progress  
**Purpose:** Use Perplexity API for reasoning over period/subject alignment challenges  
**Context:** Working on algorithm for periods with Wikidata and PeriodO

---

## Problem Statement

You're working on an algorithm to align and reason over periods from multiple sources:
- **Wikidata periods** (500+ QIDs in `more periods.md`)
- **PeriodO temporal authority**
- **Chrystallum canonical periods**

### Key Challenges

1. **Period Disambiguation:** Multiple Wikidata QIDs may refer to same historical period
2. **Temporal Alignment:** Different sources have different date ranges for same period
3. **Hierarchical Relationships:** How do periods nest/overlap (Byzantine Empire ⊃ Iconoclasm)
4. **Subject Classification:** Which SubjectConcept should anchor each period?
5. **Geographic Scope:** Period validity depends on location (Roman Republic != Global)

---

## Perplexity Integration Strategy

### What Perplexity Can Help With

✅ **Period Disambiguation:**
- Query: "Is Byzantine Iconoclasm (Q726252) a distinct period or part of Byzantine Empire (Q12544)?"
- Expected: Historical context + authoritative sources on relationship

✅ **Temporal Validation:**
- Query: "What is the scholarly consensus on start/end dates for Roman Republic?"
- Expected: Date ranges from multiple historians + uncertainty indicators

✅ **Subject/Facet Classification:**
- Query: "For period Q7318 (Nazi Germany), which facets are primary: political, military, social, cultural?"
- Expected: Ranking by historical salience + reasoning

✅ **Geographic Scope:**
- Query: "Was Tang Dynasty (Q9683) limited to China or did it extend to Central Asia?"
- Expected: Geographic boundaries + temporal evolution

---

## Current Data Assets

### Periods to Analyze

**File:** `Temporal/Data/more periods.md` (503 lines)
- 500+ Wikidata period QIDs
- Mixture of eras, dynasties, conflicts, movements
- **Examples:**
  - World War I (Q361)
  - Roman Republic (Q17167)
  - Byzantine Empire (Q12544)
  - Tang Dynasty (Q9683)
  - Nazi Germany (Q7318)

### Existing Temporal Data

From `AI_CONTEXT.md` backbone snapshot:
- **Loaded periods:** 1,077 Period nodes from PeriodO
- **Period candidates:** PeriodCandidate nodes
- **Geographic edges:** `(:Period)-[:HAS_GEO_COVERAGE]->(:GeoCoverageCandidate)` (2,961 relationships)
- **Hierarchy:** `PART_OF`, `BROADER_THAN`, `NARROWER_THAN` relationships

### Analysis Files (2026-02-18)

From recent work:
- `Temporal/wikidata_period_sca_categorization_2026-02-18.csv`
- `Temporal/wikidata_period_semantic_coverage_all_geo_2026-02-18.csv`
- `Temporal/wikidata_periodo_start_end_2026-02-18.csv`
- `Temporal/wikidata_period_geo_edges_all_geo_2026-02-18.csv`

---

## Perplexity Query Patterns

### Pattern 1: Period Relationship Discovery

**Purpose:** Determine hierarchical/temporal relationships between periods

**Query Template:**
```
For the historical periods [PERIOD_A_LABEL] (Wikidata Q[ID_A]) and [PERIOD_B_LABEL] (Wikidata Q[ID_B]), 
what is the scholarly consensus on their relationship? Specifically:
1. Do they overlap temporally or is one contained within the other?
2. Is there a hierarchical relationship (one a sub-period of the other)?
3. What are the authoritative start and end dates for each?

Cite academic historical sources.
```

**Example:**
```
For the historical periods "Byzantine Iconoclasm" (Wikidata Q726252) and "Byzantine Empire" (Wikidata Q12544),
what is the scholarly consensus on their relationship? [...]
```

**Expected Output:**
- Iconoclasm is a sub-period (726-843 CE) within Byzantine Empire (330-1453 CE)
- Hierarchical: Iconoclasm PART_OF Byzantine Empire
- Citations from Byzantine historians

---

### Pattern 2: Temporal Bounds Validation

**Purpose:** Get consensus scholarly dates for periods with uncertain bounds

**Query Template:**
```
What is the scholarly consensus on the start and end dates for [PERIOD_LABEL] (Wikidata Q[ID])?
Please provide:
1. Most widely accepted date range
2. Alternative date ranges from different scholarly traditions
3. Reasons for date uncertainty (if any)
4. Geographic scope that these dates apply to

Cite authoritative historical sources.
```

**Example:**
```
What is the scholarly consensus on the start and end dates for "Roman Republic" (Wikidata Q17167)? [...]
```

**Expected Output:**
- Consensus: 509 BCE - 27 BCE
- Alternative: Some scholars use 510 BCE start
- Uncertainty: Transition from Kingdom is gradual
- Scope: Italian Peninsula primarily, expanding to Mediterranean

---

### Pattern 3: Subject/Facet Classification

**Purpose:** Determine which facets are most relevant for a period

**Query Template:**
```
For the historical period [PERIOD_LABEL] (Wikidata Q[ID]), rank the following aspects by historical salience:
1. Political (governance, institutions, law)
2. Military (warfare, conflicts, strategy)
3. Economic (trade, currency, systems)
4. Religious (faith, institutions, clergy)
5. Social (class, kinship, family)
6. Cultural (identity, movements, symbols)
7. Artistic (art, architecture, aesthetics)
8. Intellectual (philosophy, ideas, schools)

Provide reasoning for top 3 most salient aspects.
```

**Example:**
```
For the historical period "Nazi Germany" (Wikidata Q7318), rank the following aspects [...] 
```

**Expected Output:**
1. Political (totalitarian state, NSDAP dominance)
2. Military (WWII, military expansion)
3. Social (racial policy, genocide)
Reasoning: Nazi regime defined by political ideology, militarism, racial hierarchy

---

### Pattern 4: Geographic Scope Determination

**Purpose:** Clarify geographic extent of periods

**Query Template:**
```
What was the geographic extent of [PERIOD_LABEL] (Wikidata Q[ID])?
Please specify:
1. Core territories/regions
2. Peripheral or contested areas
3. Changes in geographic scope over time
4. Modern countries that overlap with historical extent

Cite historical atlases and geographic authorities.
```

**Example:**
```
What was the geographic extent of "Tang Dynasty" (Wikidata Q9683)? [...]
```

**Expected Output:**
- Core: China proper (modern China)
- Peripheral: Central Asia, Korea (tributary states)
- Temporal changes: Expansion to 750 CE, contraction after An Lushan
- Modern overlap: China, parts of Mongolia, Xinjiang

---

## Implementation Workflow

### Phase 1: Sample Query Testing (Today)

**Tasks:**
1. ✅ Review period data in `more periods.md`
2. ⏳ Select 5 test cases representing different challenges:
   - Simple period (clear bounds): Roman Republic (Q17167)
   - Nested period: Byzantine Iconoclasm (Q726252) vs Byzantine Empire (Q12544)
   - Ambiguous dates: Middle Ages (Q12554)
   - Geographic complexity: Persian Empire (Q83311)
   - Recent/contested: Cold War (Q8683)

3. ⏳ Run Perplexity queries using each pattern
4. ⏳ Validate outputs against existing Wikidata/PeriodO data
5. ⏳ Document accuracy and usefulness

### Phase 2: Batch Processing (Tomorrow)

**Tasks:**
1. Load all 500+ periods from `more periods.md`
2. For each period:
   - Query Perplexity for temporal bounds
   - Query for subject/facet classification
   - Query for geographic scope
3. Store results in structured format: `Temporal/perplexity_period_enrichment_2026-02-19.csv`

**Output Schema:**
```csv
qid,label,start_date_consensus,end_date_consensus,date_uncertainty,geographic_core,geographic_peripheral,top_facet_1,top_facet_2,top_facet_3,perplexity_reasoning,sources_cited
Q17167,Roman Republic,-509,-27,low,"Italian Peninsula","Mediterranean Basin",political,military,social,"Republican governance structure...",Polybius;Livy;CAH
```

### Phase 3: Integration & Algorithm Development

**Tasks:**
1. Compare Perplexity outputs vs Wikidata claims
2. Compare Perplexity outputs vs PeriodO data
3. Identify discrepancies → flag for human review
4. Build reconciliation algorithm:
   - If all 3 sources agree → high confidence
   - If 2/3 agree → medium confidence
   - If all disagree → low confidence, require curator decision
5. Generate `Period` nodes with authority-backed properties

---

## Perplexity API Setup

### Configuration Needed

**Environment Variables:**
```bash
$env:PERPLEXITY_API_KEY = "pplx-your-api-key"
```

**Python Integration:**
```python
import os
import requests

def query_perplexity(prompt: str, model: str = "llama-3.1-sonar-large-128k-online") -> dict:
    """
    Query Perplexity API for period reasoning.
    
    Args:
        prompt: Natural language query
        model: Perplexity model (online models have web access)
    
    Returns:
        dict with 'answer' and 'sources'
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not set")
    
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a historical research assistant. Provide scholarly consensus with citations."},
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
```

### Cost Estimation

**Perplexity Pricing (2026):**
- Sonar Large (128k context): ~$5 per 1M tokens
- Online models (with web search): ~$5-10 per 1M tokens

**For 500 periods:**
- ~500 queries × 2,000 tokens avg = 1M tokens
- **Estimated cost:** $5-10 total

---

## Expected Outputs

### 1. Enriched Period Data

**File:** `Temporal/perplexity_period_enrichment_2026-02-19.csv`

Columns:
- `qid`: Wikidata QID
- `label`: Period name
- `start_date_consensus`: Scholarly consensus start
- `end_date_consensus`: Scholarly consensus end
- `date_uncertainty`: low/medium/high
- `geographic_core`: Primary territories
- `geographic_peripheral`: Secondary territories
- `top_facet_1`, `top_facet_2`, `top_facet_3`: Ranked facets
- `hierarchy_parent_qid`: Parent period (if nested)
- `perplexity_reasoning`: Summary reasoning
- `sources_cited`: Academic sources

### 2. Conflict Report

**File:** `Temporal/period_authority_conflicts_2026-02-19.md`

Format:
```markdown
## Conflicts Requiring Human Review

### Roman Republic (Q17167)
- **Wikidata:** -509 to -27
- **PeriodO:** -510 to -27
- **Perplexity:** -509 to -27 (consensus)
- **Recommendation:** Use Perplexity consensus, update Wikidata
- **Confidence:** High

### Middle Ages (Q12554)
- **Wikidata:** 476 to 1453
- **PeriodO:** 500 to 1500
- **Perplexity:** 476-1492 (European), 500-1500 (scholarly consensus)
- **Recommendation:** Flag for geographic disambiguation
- **Confidence:** Medium (depends on scope)
```

### 3. Algorithm Decision Logic

**Pseudo-code:**
```python
def reconcile_period_dates(qid: str) -> dict:
    """
    Reconcile period dates from multiple authorities.
    
    Returns dict with canonical dates + confidence.
    """
    wikidata_dates = fetch_wikidata_dates(qid)
    periodo_dates = fetch_periodo_dates(qid)
    perplexity_dates = query_perplexity_dates(qid)
    
    # 3-way agreement
    if all_agree([wikidata_dates, periodo_dates, perplexity_dates]):
        return {
            "start": wikidata_dates.start,
            "end": wikidata_dates.end,
            "confidence": 0.95,
            "authority": "consensus"
        }
    
    # 2-way agreement
    elif agrees(periodo_dates, perplexity_dates):
        return {
            "start": periodo_dates.start,
            "end": periodo_dates.end,
            "confidence": 0.85,
            "authority": "periodo+perplexity",
            "note": f"Wikidata disagrees: {wikidata_dates}"
        }
    
    # No agreement
    else:
        return {
            "start": None,
            "end": None,
            "confidence": 0.50,
            "authority": "conflict",
            "requires_curator": True,
            "options": [wikidata_dates, periodo_dates, perplexity_dates]
        }
```

---

## Next Steps

### Immediate (Today)

1. ✅ Quick fixes completed and committed
2. ⏳ Select 5 test periods from `more periods.md`
3. ⏳ Write Perplexity query script
4. ⏳ Test queries on sample periods
5. ⏳ Document results

### Short-term (This Week)

1. ⏳ Process all 500+ periods through Perplexity
2. ⏳ Generate enrichment CSV and conflict report
3. ⏳ Build reconciliation algorithm
4. ⏳ Test algorithm on Roman Republic (Q17167) as pilot
5. ⏳ Integrate with Neo4j period import pipeline

### Medium-term (Next Week)

1. Apply algorithm to full period corpus
2. Load enriched periods to Neo4j with authority metadata
3. Generate `(:Period)-[:HIERARCHICAL_PART_OF]->(:Period)` relationships
4. Link periods to SubjectConcepts via facet classification
5. Document methodology in architecture docs

---

## Questions for You

Before I proceed with Perplexity integration:

1. **API Access:** Do you have a Perplexity API key, or should I help you set one up?

2. **Test Cases:** Do these 5 test periods make sense, or would you prefer different ones?
   - Roman Republic (Q17167)
   - Byzantine Iconoclasm (Q726252)
   - Middle Ages (Q12554)
   - Persian Empire (Q83311)
   - Cold War (Q8683)

3. **Priority:** Which challenge is most urgent?
   - Date reconciliation (Wikidata vs PeriodO)
   - Hierarchical relationships (period nesting)
   - Subject/facet classification
   - Geographic scope determination

4. **Output Format:** CSV + Markdown report sufficient, or do you need JSON/other formats?

5. **Integration:** Should enriched period data go directly to Neo4j, or review first?

---

**Status:** Ready to execute Phase 1 pending your input  
**Estimated Time:** 2-3 hours for Phase 1, 6-8 hours for full batch processing  
**Cost:** $5-10 for complete Perplexity API usage

