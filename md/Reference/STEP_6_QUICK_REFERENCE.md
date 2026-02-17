# Step 6: Wikipedia Training - Quick Reference

**Date:** February 15, 2026  
**Status:** 🎯 DESIGN COMPLETE - Ready for Implementation  

---

## What is Step 6?

**Step 6** adds **Wikipedia-based training** where agents systematically extract claims from Wikipedia articles and populate the knowledge graph.

### The Flow

```
Step 5 Phase 1: Un-Faceted Exploration
   - Nodes and edges discovered (NO facet lens)
   - Shell nodes from breadth exploration (e.g., Tyrian purple, murex)
   - Cross-domain links from backlinks
   - Proposed ontology output
         ↓
   ⚠️ APPROVAL POINT ⚠️
   (Human reviews proposed ontology)
         ↓
Step 5 Phase 2: Facet-by-Facet Analysis
   - SCA adopts facet roles sequentially
   - Military perspective → Political → Cultural → etc.
         ↓
Step 6: LLM discovers best Wikipedia articles
   - Articles for BOTH core concepts AND shell nodes
   - Cross-domain articles (purple → mollusk connections)
         ↓
Extract claims sentence-by-sentence
         ↓
Validate against registries
         ↓
Create new Claims OR augment existing Claims
         ↓
Track quality metrics
```

---

## Five Phases

### Phase 1: Article Discovery
**LLM selects 5-10 Wikipedia articles** based on proposed ontology

Input: Ontology classes (e.g., "Military Leadership", "Military Operations")
Output: List of articles (e.g., "Julius_Caesar", "Battle_of_Pharsalus")

### Phase 2: Line-by-Line Extraction
**Parse each article sentence by sentence**

For each sentence:
- Extract entities (names, places, dates)
- Identify relationships (DEFEATED, PARTICIPATED_IN)
- Extract temporal information (dates, years)
- Generate claim proposals

### Phase 3: Registry Validation
**Check against canonical registries**

Validate:
- ✓ Facet is one of canonical 17
- ✓ Relationship type exists in registry
- ✓ Entity types valid
- ✓ Dates in ISO 8601 format
- ✓ Confidence in range [0.0, 1.0]

### Phase 4: Claim Creation/Augmentation
**Create new or augment existing claims**

Decision logic:
- If claim does NOT exist → **CREATE** new Claim node
- If claim exists → **AUGMENT** with Wikipedia evidence
  - Add article to authority_ids.wikipedia
  - Increase posterior_probability (multi-source agreement)

### Phase 5: Quality Tracking
**Track metrics for validation**

Metrics:
- Claims extracted, created, augmented
- Validation pass rate
- Average confidence/posterior
- Performance (claims/minute, cost)

---

## Key Concepts

### Claim Creation vs. Augmentation

**Scenario 1: New Claim**
```
Wikidata: (no claim exists)
Wikipedia: "Caesar defeated Pompey at Pharsalus in 48 BCE"

Action: CREATE new Claim node
Result: 
  - claim_id: claim_caesar_defeated_pompey_48bce
  - authority_source: 'wikipedia'
  - confidence: 0.95
  - posterior: 0.95
```

**Scenario 2: Augment Existing**
```
Wikidata: Claim exists (confidence: 0.95, posterior: 0.95)
Wikipedia: Same claim found in article

Action: AUGMENT existing Claim
Result:
  - authority_ids: {wikidata: [...], wikipedia: ['Julius_Caesar']}
  - posterior: 0.98 (increased due to multi-source agreement)
  - confidence: 0.95 (unchanged - reflects source reliability)
```

### Registry Validation

**Canonical Registries:**
1. **Facet Registry:** 17 canonical facets (military, political, etc.)
2. **Relationship Registry:** Valid relationship types (DEFEATED, PARTICIPATED_IN)
3. **Entity Type Taxonomy:** Valid entity types (Person, Event, Place)
4. **Action Structure Vocabularies:** Valid verbs and actions

**Validation Example:**
```
Extracted: relationship_type = "BEAT"
Registry Check: "BEAT" not in registry
Correction: Suggest "DEFEATED" (closest match)
Result: Auto-correct with warning log
```

---

## Implementation Roadmap

### Method Signature

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
    Extract claims from Wikipedia articles using proposed ontology
    
    Returns:
        {
            'status': 'TRAINING_COMPLETE',
            'articles_processed': 5,
            'claims_created': 156,
            'claims_augmented': 47,
            'avg_confidence': 0.87,
            'avg_posterior': 0.89,
            'duration_seconds': 342.5,
            'log_file': str
        }
    """
```

### Gradio UI Tab

New accordion in "⚙️ Agent Operations" tab:

```
📚 Wikipedia Training
├─ Facet selector
├─ Max articles (1-10, default 5)
├─ Max sentences per article (50-500, default 100)
├─ Min confidence (0.5-1.0, default 0.80)
├─ "📚 Start Wikipedia Training" button
└─ Status output + Log output
```

---

## Discussion Points (From Design Doc)

### 1. How many articles per session?
**Recommendation:** 5-10 articles (focused, manageable quality)

### 2. Sentence vs. paragraph extraction?
**Recommendation:** Sentence-level with 1-2 sentence context

### 3. Registry violations: auto-correct or reject?
**Recommendation:** Auto-correct with warning log

### 4. Claim augmentation strategy?
**Recommendation:** Keep claim confidence same, increase posterior probability

### 5. Breadth vs. depth?
**Recommendation:** Depth first (5 articles, all sentences)

---

## Expected Output

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
- Augmented: 47 existing claims
- Rejected: 0 claims

Quality:
- Avg confidence: 0.87
- Avg posterior: 0.89
- Validation pass rate: 100%

Registry Checks:
- Facet mismatches: 2 (corrected)
- Relationship corrections: 5 (warnings)
- Entity warnings: 8 (flagged)

Performance:
- Duration: 5m 42s
- Claims/minute: 35.6
- Cost: $2.34
```

---

## Why Step 6 Matters

**Steps 1-5** built the **framework:**
- Steps 1-4: Agent capabilities (introspection, federation, validation, ontology)
- Step 5: Operational workflows (Initialize → Proposal → Training)

**Step 6** adds **content:**
- Populates knowledge graph with actual claims
- Moves from structure to data
- Provides evidence-backed claims (Wikipedia + Wikidata)
- Enables multi-source validation (higher posterior for agreement)

**The Complete Pipeline:**
```
Initialize → Propose Ontology → Train on Wikidata → Train on Wikipedia → Query
  (Step 5)      (Step 5)         (Step 5)           (Step 6)          (Step 5)
```

---

## Files

**Design Document:** [STEP_6_DESIGN_WIKIPEDIA_TRAINING.md](../Reports/STEP_6_DESIGN_WIKIPEDIA_TRAINING.md)

**Related:**
- [STEP_5_DESIGN_OPERATIONAL_MODES.md](../Reports/STEP_5_DESIGN_OPERATIONAL_MODES.md) - Operational modes framework
- [ARCHITECTURE_IMPLEMENTATION_INDEX.md](../Architecture/ARCHITECTURE_IMPLEMENTATION_INDEX.md) - Progress tracking
- [QUICK_START.md](../Guides/QUICK_START.md) - Claim structure and authority tracking

---

## Next Actions

1. **Review Design:** Read [STEP_6_DESIGN_WIKIPEDIA_TRAINING.md](../Reports/STEP_6_DESIGN_WIKIPEDIA_TRAINING.md)
2. **Discuss:** Review the 5 discussion points (article count, sentence vs. paragraph, etc.)
3. **Implement:** Add `execute_wikipedia_training()` method to FacetAgent
4. **Test:** Run with 5 military articles, validate output quality
5. **Iterate:** Adjust based on validation pass rate and quality metrics

