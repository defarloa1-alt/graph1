# Step 6 Design: Wikipedia-Based Initial Training

**Date:** February 15, 2026  
**Status:** 🎯 DESIGN PHASE  
**Prerequisites:** Steps 1-5 complete (Initialize → Ontology → Training operational)

---

## Overview

**Step 6** implements **Wikipedia-based initial training** where the LLM systematically extracts claims from Wikipedia articles, validates them against registries, and creates or augments claims in the knowledge graph.

### Purpose

After Step 5 provides the operational framework (Initialize → Proposal → Training), Step 6 adds **content-driven learning** where agents:

1. **Discover best Wikipedia pages** (LLM selects relevant articles based on domain ontology)
2. **Extract claims line-by-line** (systematic passage through article text)
3. **Validate against registries** (check facets, relationships, entities against canonical registries)
4. **Create or augment claims** (add new claims or strengthen existing ones with Wikipedia evidence)

---

## Architecture: Wikipedia Training Pipeline

```
┌─────────────────────────────────────────────────┐
│  Step 5 Output: Proposed Ontology              │
│  - Expansive ontology (breadth exploration)     │
│  - Shell nodes for cross-domain concepts       │
│  - 18+ claim templates                          │
│  - Validation rules                             │
└────────────────┬────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────┐
│  STEP 6: Wikipedia Training Pipeline           │
│                                                 │
│  Phase 1: Article Discovery                    │
│  → LLM selects best Wikipedia pages            │
│                                                 │
│  Phase 2: Line-by-Line Extraction              │
│  → Parse article text systematically           │
│  → Extract entities, relationships, claims     │
│                                                 │
│  Phase 3: Registry Validation                  │
│  → Check against facet registry                │
│  → Check against relationship registry         │
│  → Check against entity type taxonomy          │
│                                                 │
│  Phase 4: Claim Creation/Augmentation          │
│  → Create new Claim nodes (if not exists)      │
│  → Augment existing claims (add evidence)      │
│  → Track authority_source: "wikipedia"         │
│                                                 │
│  Phase 5: Quality Tracking                     │
│  → Calculate confidence scores                 │
│  → Track posterior probabilities               │
│  → Log all decisions                           │
└─────────────────────────────────────────────────┘
```

---

## Phase 1: Article Discovery

### Goal
LLM analyzes the proposed ontology and selects the **most relevant Wikipedia pages** for extracting domain-specific claims.

### Input
- Proposed subject ontology (from Step 5)
  - Core ontology classes (e.g., "Military Leadership", "Military Operations")
  - **Shell nodes** discovered via breadth exploration (e.g., "Tyrian purple", "murex")
  - Examples per class (e.g., "Caesar", "Battle of Pharsalus")
  - Characteristics (e.g., "rank", "date", "outcome")
  - **Cross-domain links** from backlinks (purple → mollusk connections)

### Process

```python
def discover_wikipedia_articles(proposed_ontology: Dict) -> List[Dict]:
    """
    LLM selects best Wikipedia articles for training
    
    Prompt structure:
    - Given domain: military (Roman Republic)
    - Given ontology classes: Military Leadership, Operations, Organization
    - Given examples: Caesar, Pompey, Battle of Pharsalus
    
    Select 5-10 Wikipedia articles that:
    1. Cover breadth (all ontology classes represented)
    2. Have quality content (featured, good articles preferred)
    3. Provide rich claim opportunities (dates, relationships, events)
    4. Link to other relevant articles (backlink potential)
    
    Return: List of Wikipedia titles with rationale
    """
    
    prompt = f"""
You are training an agent for the {facet} domain with this ontology:

Classes:
{format_ontology_classes(proposed_ontology)}

Select 5-10 Wikipedia articles that:
- Cover all ontology classes
- Are high-quality (featured/good articles)
- Provide rich factual claims
- Have good cross-references

Return JSON:
{{
  "articles": [
    {{
      "title": "Julius_Caesar",
      "rationale": "Covers Military Leadership class, has extensive dates, roles, battles",
      "ontology_classes": ["Military Leadership"],
      "priority": "HIGH"
    }},
    ...
  ]
}}
"""
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    
    articles = json.loads(response.choices[0].message.content)
    return articles['articles']
```

### Example Output

For military domain (Roman Republic):

```json
{
  "articles": [
    {
      "title": "Julius_Caesar",
      "rationale": "Comprehensive coverage of military commander, political career, battles",
      "ontology_classes": ["Military Leadership"],
      "priority": "HIGH",
      "estimated_claims": 150
    },
    {
      "title": "Battle_of_Pharsalus",
      "rationale": "Detailed military operation with participants, outcome, tactics",
      "ontology_classes": ["Military Operations"],
      "priority": "HIGH",
      "estimated_claims": 80
    },
    {
      "title": "Roman_legion",
      "rationale": "Military organization structure, size, composition",
      "ontology_classes": ["Military Organization"],
      "priority": "MEDIUM",
      "estimated_claims": 60
    },
    {
      "title": "Pompey",
      "rationale": "Another major military leader, rival to Caesar",
      "ontology_classes": ["Military Leadership"],
      "priority": "HIGH",
      "estimated_claims": 120
    },
    {
      "title": "Punic_Wars",
      "rationale": "Major military operations spanning decades",
      "ontology_classes": ["Military Operations"],
      "priority": "MEDIUM",
      "estimated_claims": 200
    }
  ],
  "total_estimated_claims": 610,
  "coverage": {
    "Military Leadership": 2,
    "Military Operations": 2,
    "Military Organization": 1
  }
}
```

---

## Phase 2: Line-by-Line Extraction

### Goal
Systematically parse each Wikipedia article **sentence by sentence** to extract entities, relationships, dates, and claims.

### Process

```python
def extract_claims_from_article(
    wikipedia_title: str,
    ontology: Dict,
    facet: str
) -> List[Dict]:
    """
    Extract claims line-by-line from Wikipedia article
    
    Returns: List of claim proposals
    """
    
    # Fetch article text
    article = fetch_wikipedia_article(wikipedia_title)
    
    # Split into sentences
    sentences = split_into_sentences(article['text'])
    
    claims_extracted = []
    
    for i, sentence in enumerate(sentences):
        # LLM extraction prompt
        prompt = f"""
Analyze this sentence from Wikipedia article "{wikipedia_title}":

"{sentence}"

Extract:
1. Entities mentioned (names, places, dates, organizations)
2. Relationships between entities
3. Temporal information (dates, periods)
4. Potential claims for {facet} facet

Context: This is for ontology class {ontology['classes'][0]['class_name']}

Return JSON with:
- entities: [{{type, label, wikidata_qid}}]
- relationships: [{{subject, predicate, object, confidence}}]
- temporal: {{date, period, year}}
- claims: [{{label, facet, confidence, evidence}}]
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        extraction = json.loads(response.choices[0].message.content)
        
        # Add metadata
        extraction['source'] = {
            'article': wikipedia_title,
            'sentence_index': i,
            'sentence_text': sentence
        }
        
        claims_extracted.append(extraction)
    
    return claims_extracted
```

### Example Extraction

**Sentence:** "In 48 BCE, Caesar defeated Pompey at the Battle of Pharsalus, securing control of the Roman Republic."

**Extracted:**
```json
{
  "entities": [
    {
      "type": "Person",
      "label": "Caesar",
      "wikidata_qid": "Q1048",
      "role": "victor"
    },
    {
      "type": "Person",
      "label": "Pompey",
      "wikidata_qid": "Q1131",
      "role": "defeated"
    },
    {
      "type": "Event",
      "label": "Battle of Pharsalus",
      "wikidata_qid": "Q28048",
      "role": "battle"
    },
    {
      "type": "Political Entity",
      "label": "Roman Republic",
      "wikidata_qid": "Q17167",
      "role": "state"
    }
  ],
  "relationships": [
    {
      "subject": "Q1048",
      "predicate": "DEFEATED",
      "object": "Q1131",
      "confidence": 0.95,
      "temporal": "-48"
    },
    {
      "subject": "Q1048",
      "predicate": "PARTICIPATED_IN",
      "object": "Q28048",
      "confidence": 0.98,
      "temporal": "-48"
    },
    {
      "subject": "Q28048",
      "predicate": "OCCURRED_DURING",
      "object": "Q17167",
      "confidence": 0.98,
      "temporal": "-48"
    }
  ],
  "temporal": {
    "date": "-48",
    "year": "-48",
    "precision": "year"
  },
  "claims": [
    {
      "label": "Caesar defeated Pompey at Battle of Pharsalus in 48 BCE",
      "facet": "military",
      "confidence": 0.95,
      "evidence": "In 48 BCE, Caesar defeated Pompey at the Battle of Pharsalus",
      "relationship_type": "DEFEATED",
      "subject_qid": "Q1048",
      "object_qid": "Q1131"
    },
    {
      "label": "Battle of Pharsalus secured Caesar's control of Roman Republic",
      "facet": "political",
      "confidence": 0.90,
      "evidence": "securing control of the Roman Republic",
      "relationship_type": "GAINED_CONTROL_OF",
      "subject_qid": "Q1048",
      "object_qid": "Q17167"
    }
  ],
  "source": {
    "article": "Battle_of_Pharsalus",
    "sentence_index": 42,
    "sentence_text": "In 48 BCE, Caesar defeated Pompey at the Battle of Pharsalus..."
  }
}
```

---

## Phase 3: Registry Validation

### Goal
Validate extracted claims against **canonical registries** to ensure consistency and prevent invalid data.

### Registries to Check

1. **Facet Registry** (`Facets/facet_registry_master.json`)
   - Canonical 17 facets
   - Facet descriptions and patterns

2. **Relationship Registry** (Appendix A in Architecture)
   - Canonical relationship types (e.g., DEFEATED, PARTICIPATED_IN)
   - Argument constraints (e.g., subject must be Person, object must be Person)

3. **Entity Type Taxonomy** (Appendix C)
   - Valid entity types (Person, Event, Place, etc.)

4. **Action Structure Vocabularies** (`CSV/action_structure_vocabularies.csv`)
   - Valid verbs and action types

### Validation Process

```python
def validate_claim_against_registries(claim: Dict) -> Dict:
    """
    Validate claim against all registries
    
    Returns: validation_result with status and corrections
    """
    
    validation_result = {
        'status': 'VALID',
        'errors': [],
        'warnings': [],
        'corrections': []
    }
    
    # 1. Validate facet
    if claim['facet'] not in CANONICAL_FACETS:
        validation_result['errors'].append(
            f"Invalid facet: {claim['facet']}. Must be one of 17 canonical facets."
        )
        validation_result['status'] = 'INVALID'
    
    # 2. Validate relationship type
    relationship_type = claim.get('relationship_type')
    if relationship_type and relationship_type not in RELATIONSHIP_REGISTRY:
        # Check if it's a close match (LLM might have used synonym)
        closest_match = find_closest_relationship(relationship_type)
        
        if closest_match:
            validation_result['warnings'].append(
                f"Relationship '{relationship_type}' not in registry. Did you mean '{closest_match}'?"
            )
            validation_result['corrections'].append({
                'field': 'relationship_type',
                'original': relationship_type,
                'suggested': closest_match
            })
        else:
            validation_result['errors'].append(
                f"Unknown relationship type: {relationship_type}"
            )
            validation_result['status'] = 'INVALID'
    
    # 3. Validate entity types
    for entity in claim.get('entities', []):
        if entity['type'] not in ENTITY_TYPE_TAXONOMY:
            validation_result['warnings'].append(
                f"Entity type '{entity['type']}' not in taxonomy. Suggest manual review."
            )
    
    # 4. Validate temporal format
    temporal = claim.get('temporal')
    if temporal:
        if not validate_iso8601_format(temporal['date']):
            validation_result['errors'].append(
                f"Invalid date format: {temporal['date']}. Must be ISO 8601."
            )
            validation_result['status'] = 'INVALID'
    
    # 5. Validate confidence range
    if not (0.0 <= claim['confidence'] <= 1.0):
        validation_result['errors'].append(
            f"Confidence {claim['confidence']} out of range [0.0, 1.0]"
        )
        validation_result['status'] = 'INVALID'
    
    return validation_result
```

### Example Validation

**Input Claim:**
```json
{
  "label": "Caesar beat Pompey at Pharsalus",
  "facet": "military",
  "relationship_type": "BEAT",  // ❌ Not in registry
  "confidence": 0.95
}
```

**Validation Result:**
```json
{
  "status": "NEEDS_CORRECTION",
  "errors": [],
  "warnings": [
    "Relationship 'BEAT' not in registry. Did you mean 'DEFEATED'?"
  ],
  "corrections": [
    {
      "field": "relationship_type",
      "original": "BEAT",
      "suggested": "DEFEATED"
    }
  ]
}
```

---

## Phase 4: Claim Creation/Augmentation

### Goal
**Create new Claim nodes** or **augment existing claims** with Wikipedia evidence.

### Decision Logic

```python
def create_or_augment_claim(validated_claim: Dict, neo4j_driver) -> Dict:
    """
    Check if claim already exists.
    - If YES: Augment with new evidence
    - If NO: Create new Claim node
    
    Returns: action_taken ('CREATED' or 'AUGMENTED')
    """
    
    # Generate claim ID
    claim_id = generate_claim_id(validated_claim)
    
    # Check if claim exists
    existing_claim = check_claim_exists(neo4j_driver, claim_id)
    
    if existing_claim:
        # AUGMENT EXISTING CLAIM
        result = augment_existing_claim(
            neo4j_driver,
            claim_id,
            validated_claim
        )
        
        return {
            'action': 'AUGMENTED',
            'claim_id': claim_id,
            'details': result
        }
    
    else:
        # CREATE NEW CLAIM
        result = create_new_claim(
            neo4j_driver,
            validated_claim
        )
        
        return {
            'action': 'CREATED',
            'claim_id': claim_id,
            'details': result
        }


def augment_existing_claim(driver, claim_id: str, new_evidence: Dict) -> Dict:
    """
    Augment existing claim with new Wikipedia evidence
    
    Updates:
    - authority_ids.wikipedia: add article title
    - confidence_source: append "Wikipedia"
    - posterior_probability: recalculate
    """
    
    cypher = """
    MATCH (c:Claim {claim_id: $claim_id})
    SET c.authority_ids.wikipedia = coalesce(c.authority_ids.wikipedia, []) + $article_title,
        c.confidence_source = c.confidence_source + ' + Wikipedia',
        c.updated_at = datetime()
    WITH c
    // Recalculate posterior (Wikidata + Wikipedia agreement)
    SET c.posterior_probability = 
        CASE 
            WHEN size(c.authority_ids.wikipedia) > 0 AND c.authority_ids.wikidata IS NOT NULL
            THEN 0.98  // Both sources agree
            ELSE c.prior_probability
        END
    RETURN c
    """
    
    with driver.session() as session:
        result = session.run(cypher, {
            'claim_id': claim_id,
            'article_title': new_evidence['source']['article']
        })
        
        return {
            'claim_id': claim_id,
            'action': 'augmented',
            'authority_added': 'wikipedia'
        }


def create_new_claim(driver, validated_claim: Dict) -> Dict:
    """
    Create new Claim node with Wikipedia as authority source
    """
    
    cypher = """
    CREATE (c:Claim {
        claim_id: $claim_id,
        label: $label,
        facet: $facet,
        relationship_type: $relationship_type,
        confidence: $confidence,
        authority_source: 'wikipedia',
        authority_ids: {
            wikipedia: [$article_title]
        },
        confidence_source: 'Wikipedia article analysis',
        evidence_text: $evidence_text,
        prior_probability: $confidence,
        posterior_probability: $confidence,
        created_at: datetime(),
        updated_at: datetime()
    })
    RETURN c
    """
    
    with driver.session() as session:
        result = session.run(cypher, {
            'claim_id': generate_claim_id(validated_claim),
            'label': validated_claim['label'],
            'facet': validated_claim['facet'],
            'relationship_type': validated_claim.get('relationship_type'),
            'confidence': validated_claim['confidence'],
            'article_title': validated_claim['source']['article'],
            'evidence_text': validated_claim['evidence']
        })
        
        return {
            'claim_id': generate_claim_id(validated_claim),
            'action': 'created',
            'authority_source': 'wikipedia'
        }
```

### Example Workflow

**Scenario 1: New Claim**

```
Extract: "Caesar defeated Pompey at Pharsalus in 48 BCE"
Validate: ✓ Facet OK, ✓ Relationship OK, ✓ Date OK
Check DB: No existing claim found
Action: CREATE new Claim node
Result: {
  action: 'CREATED',
  claim_id: 'claim_caesar_defeated_pompey_48bce',
  authority_source: 'wikipedia'
}
```

**Scenario 2: Augment Existing Claim**

```
Extract: "Caesar defeated Pompey at Pharsalus in 48 BCE" (from different article)
Validate: ✓ All checks pass
Check DB: Claim already exists (from Wikidata)
Action: AUGMENT with Wikipedia evidence
Result: {
  action: 'AUGMENTED',
  claim_id: 'claim_caesar_defeated_pompey_48bce',
  authority_ids: {
    wikidata: ['Q1048', 'Q1131'],
    wikipedia: ['Julius_Caesar', 'Battle_of_Pharsalus']  // ← ADDED
  },
  posterior_probability: 0.98  // ← INCREASED (both sources agree)
}
```

---

## Phase 5: Quality Tracking

### Goal
Track metrics to ensure training quality and identify issues.

### Metrics Tracked

```python
training_metrics = {
    'articles_processed': 5,
    'sentences_analyzed': 487,
    'claims_extracted': 203,
    'claims_validated': 203,
    'claims_created': 156,
    'claims_augmented': 47,
    'claims_rejected': 0,
    
    # Quality metrics
    'avg_confidence': 0.87,
    'avg_posterior': 0.89,
    'validation_pass_rate': 1.0,
    
    # Registry checks
    'facet_mismatches': 2,
    'relationship_corrections': 5,
    'entity_type_warnings': 8,
    
    # Performance
    'duration_seconds': 342.5,
    'claims_per_minute': 35.6,
    'api_calls': 487,
    'cost_usd': 2.34
}
```

### Logging

```
[2026-02-15T15:30:00] [WIKIPEDIA_TRAINING] START
[2026-02-15T15:30:01] [DISCOVERY] Discovered 5 articles: Julius_Caesar, Battle_of_Pharsalus, ...
[2026-02-15T15:30:05] [EXTRACTION] Processing Julius_Caesar (3,245 chars, 87 sentences)
[2026-02-15T15:30:06] [EXTRACTION] Sentence 1/87: "Gaius Julius Caesar was a Roman general..."
[2026-02-15T15:30:08] [EXTRACTION] Extracted: 3 entities, 2 relationships, 1 claim
[2026-02-15T15:30:09] [VALIDATION] Claim validated: VALID (facet=military, confidence=0.92)
[2026-02-15T15:30:10] [DATABASE] Checked: Claim does not exist
[2026-02-15T15:30:11] [DATABASE] Created Claim: claim_caesar_roman_general
[2026-02-15T15:30:12] [EXTRACTION] Sentence 2/87: "He played a critical role in..."
...
[2026-02-15T15:35:25] [SUMMARY] Training complete: 156 created, 47 augmented, 0 rejected
```

---

## Integration with Steps 1-5

### Step 5 → Step 6 Data Flow

```
Step 5 Outputs:
├─ Session ID: military_20260215_143500
├─ Proposed Ontology:
│  ├─ Classes: [Military Leadership, Operations, Organization]
│  ├─ Templates: 18 claim templates
│  └─ Strength: 0.88
└─ Initialized Nodes: 23 SubjectConcept nodes

                    ↓

Step 6 Process:
├─ Phase 1: LLM selects 5 Wikipedia articles based on ontology classes
├─ Phase 2: Extract claims from 487 sentences across articles
├─ Phase 3: Validate 203 claims against registries
├─ Phase 4: Create 156 new + augment 47 existing claims
└─ Phase 5: Track metrics, log everything

                    ↓

Step 6 Outputs:
├─ Claims Created: 156 (authority_source: 'wikipedia')
├─ Claims Augmented: 47 (added Wikipedia to existing Wikidata claims)
├─ Authority Coverage: Wikidata + Wikipedia for 47 claims (posterior: 0.98)
└─ Training Metrics: 87% avg confidence, 100% validation pass rate
```

---

## Implementation Checklist

### Method to Implement

```python
def execute_wikipedia_training(
    self,
    session_id: str,
    max_articles: int = 5,
    max_sentences_per_article: int = 100,
    min_confidence: float = 0.80,
    ui_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
    """
    WIKIPEDIA TRAINING MODE: Extract claims from Wikipedia articles
    
    Workflow:
    1. Load proposed ontology from Session ID
    2. LLM discovers best Wikipedia articles
    3. Extract claims line-by-line from articles
    4. Validate claims against registries
    5. Create/augment Claim nodes
    6. Track quality metrics
    
    Returns:
        {
            'status': 'TRAINING_COMPLETE',
            'articles_processed': int,
            'claims_created': int,
            'claims_augmented': int,
            'avg_confidence': float,
            'duration_seconds': float,
            'log_file': str
        }
    """
    pass
```

### Gradio UI Tab

```python
with gr.Accordion("📚 Wikipedia Training", open=False):
    gr.Markdown("""
    Extract claims from Wikipedia articles using the proposed ontology.
    
    LLM selects the best articles, extracts claims sentence-by-sentence,
    validates against registries, and creates/augments Claim nodes.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            wiki_facet_selector = gr.Dropdown(
                choices=get_available_facets(),
                value="military",
                label="Select Facet"
            )
            
            wiki_max_articles = gr.Slider(
                minimum=1,
                maximum=10,
                value=5,
                label="Max Articles"
            )
            
            wiki_max_sentences = gr.Slider(
                minimum=50,
                maximum=500,
                value=100,
                label="Max Sentences per Article"
            )
            
            wiki_run_btn = gr.Button(
                "📚 Start Wikipedia Training",
                variant="primary"
            )
        
        with gr.Column(scale=2):
            wiki_status_output = gr.Textbox(
                label="Status",
                lines=25
            )
    
    wiki_log_output = gr.Textbox(
        label="Detailed Log",
        lines=15
    )
```

---

## Discussion Points

### 1. Scale: How many articles?

**Option A:** 5-10 articles per training session (manageable, focused)
**Option B:** 20-50 articles (comprehensive, slower)

**Recommendation:** Start with 5-10, measure quality, scale up if validation pass rate stays high.

---

### 2. Sentence vs. Paragraph Extraction?

**Sentence-level:**
- ✅ More precise attribution
- ✅ Easier to validate specific claims
- ❌ May miss context

**Paragraph-level:**
- ✅ More context for LLM
- ❌ Harder to attribute specific claims
- ❌ More expensive (longer prompts)

**Recommendation:** Sentence-level with 1-2 sentence context window.

---

### 3. Registry Violations: Auto-correct or Reject?

**Auto-correct:**
- ✅ Faster processing
- ❌ May introduce errors if correction is wrong

**Reject:**
- ✅ Higher quality
- ❌ Loses valid data

**Recommendation:** Auto-correct with warning log, manual review for ambiguous cases.

---

### 4. Claim Augmentation Strategy

**Scenario:** Wikidata says "Caesar defeated Pompey" (confidence: 0.95). Wikipedia says same thing.

**Option A:** Increase confidence to 0.98
**Option B:** Keep confidence same, increase posterior
**Option C:** Add as separate claim

**Recommendation:** Option B - Keep claim confidence (reflects source reliability), increase **posterior probability** (reflects multi-source agreement).

---

### 5. Priority: Breadth vs. Depth?

**Breadth:** Process many articles lightly (first 50 sentences each)
**Depth:** Process few articles thoroughly (all sentences)

**Recommendation:** Depth first (5 articles, all sentences) to maximize claim extraction per article.

---

### 6. ⚠️ **Real vs Simulated SubjectFacetAgents (SFAs)** ⭐ NEW DECISION POINT

**Context:** Step 6 Wikipedia Training operates in Phase 2 (facet-by-facet analysis), where SCA sequentially adopts different facet roles to analyze extracted claims.

**Current Implementation:** Simulated agents (hard-coded mock responses)
- Phase 2 uses `_simulate_facet_query()` with hard-coded data
- Returns mock nodes for specific queries only ("senator & mollusk")
- Validates orchestration logic, but NOT real agent behavior

**Problem:**
- **SFAs need to be TRAINED in their discipline to be useful**
- Simulated agents have NO domain knowledge
- Hard-coded responses don't test real facet analysis
- Smoke test passes but real agents never validated

**Options:**

**Option A: Keep Simulated Agents**
- ✅ Fast, deterministic, no LLM cost during development
- ✅ Validates orchestration and bridge claim generation
- ❌ NOT a real smoke test of agent capabilities
- ❌ Doesn't test facet-specific analysis

**Option B: Spawn Real FacetAgents** (~2 hours effort)
- ✅ Real LLM reasoning from facet perspective
- ✅ System prompts provide facet expertise
- ✅ Works for ANY query (not just hard-coded)
- ✅ TRUE smoke test validation
- ❌ ~2 hours implementation effort
- ❌ LLM costs during testing

**Real Agent Implementation:**
- FacetAgentFactory already exists
- Each FacetAgent has LLM integration (`self.chat()`)
- System prompts loaded from JSON (17 facets)
- Modify `spawn_agent()` to use factory (~30 lines)
- See: [REAL_VS_SIMULATED_SFA_ANALYSIS.md](REAL_VS_SIMULATED_SFA_ANALYSIS.md)

**For Step 6 Wikipedia Training:**
- Real agents would analyze extracted Wikipedia claims from facet perspectives
- Example: "Caesar crossed the Rubicon" analyzed by:
  * Military SFA: "Military campaign decision, strategic move"
  * Political SFA: "Political defiance, declaration of war on Senate"
  * Geographic SFA: "River crossing, territorial boundary"
  * Cultural SFA: "Idiom origin, cultural milestone"

**Recommendation:** 🤔 **DECISION NEEDED**
- If goal is smoke test orchestration only → Keep simulated
- If goal is validate real facet-trained analysis → Spawn real agents (~2 hours)
- **For production Step 6:** Real agents provide genuine facet expertise

---

## Expected Output Example

```
✅ Wikipedia Training Complete!

Session: military_20260215_143500

Articles Processed: 5
- Julius_Caesar (87 sentences, 34 claims)
- Battle_of_Pharsalus (62 sentences, 28 claims)
- Roman_legion (45 sentences, 19 claims)
- Pompey (73 sentences, 31 claims)
- Punic_Wars (120 sentences, 44 claims)

Claims:
- Created: 156 new claims
- Augmented: 47 existing claims (added Wikipedia evidence)
- Rejected: 0 claims

Quality Metrics:
- Avg confidence: 0.87
- Avg posterior: 0.89
- Validation pass rate: 100%

Registry Checks:
- Facet mismatches: 2 (auto-corrected)
- Relationship corrections: 5 (warnings logged)
- Entity type warnings: 8 (flagged for review)

Performance:
- Duration: 5 minutes 42 seconds
- Claims per minute: 35.6
- API calls: 487
- Cost: $2.34 USD

Authority Coverage:
- Wikidata only: 109 claims
- Wikipedia only: 156 claims
- Both sources: 47 claims (posterior: 0.98)

Log file: logs/military_agent_military_20260215_143500_wikipedia.log
```

---

## Summary

**Step 6: Wikipedia Training** implements content-driven learning where agents:

1. **Discover** best Wikipedia articles via LLM (based on ontology)
2. **Extract** claims sentence-by-sentence (systematic passage through text)
3. **Validate** against canonical registries (facets, relationships, entities)
4. **Create/Augment** Claim nodes (new claims or strengthen existing)
5. **Track** quality metrics (confidence, posterior, validation rate)

This provides the **content foundation** for the knowledge graph, moving from structural setup (Steps 1-5) to **data population** (Step 6).

