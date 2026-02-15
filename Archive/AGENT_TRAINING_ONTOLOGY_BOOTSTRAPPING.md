# AGENT TRAINING & ONTOLOGY BOOTSTRAPPING
## Self-Service Domain Ontology Discovery from Wikidata + Wikipedia

**Core Concept**: Agents don't use pre-curated ontologies. Instead, they **train themselves** by:
1. Receiving a Wikidata Q-identifier (QID)
2. Fetching all Wikidata properties + backlinks
3. Generating canonical subject_concept_id
4. Parsing Wikipedia article structure (TOC/sections)
5. Automatically discovering domain sub-concepts from Wikipedia index

**Result**: Self-bootstrapped, Wikipedia-grounded domain ontologies.

---

## Why This Approach?

### Problem with Pre-Curated Ontologies
- Manual curation is labor-intensive (3-4 hours per civilization+facet)
- Static: needs updates when new concepts emerge
- Curator bias: might miss relevant categories
- Not scalable to 50+ civilizations × 17 facets

### Wikipedia as Authority
- Wikipedia table of contents = curated domain knowledge
- Section structure reveals what historians consider important
- Automatically updated by Wikipedia editors
- Peer-reviewed, multi-language validated
- Free, openly available

### Wikidata as Identity
- Canonical properties: start date, end date, location, etc.
- Deterministic subject_concept_id from properties
- Backlinks show related entities
- Federation with LCSH/FAST/MARC built-in

---

## 5-Phase Training Pipeline

### Phase 1: Fetch Wikidata Properties

**Input**: Q-identifier (e.g., Q17167 = Roman Republic)

**Process**:
```
GET https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q17167
```

**Example Output**:
```json
{
  "Q17167": {
    "labels": {
      "en": {"value": "Roman Republic"}
    },
    "descriptions": {
      "en": {"value": "period of ancient Rome before the empire"}
    },
    "claims": {
      "P580": [{"mainsnak": {"datavalue": {"value": "-509-01-01T00:00:00Z"}}}],  // start time
      "P582": [{"mainsnak": {"datavalue": {"value": "-27-01-01T00:00:00Z"}}}],   // end time
      "P131": [{"mainsnak": {"datavalue": {"value": {"id": "Q38"}}}}],          // located in (Italy)
      "P625": [{"mainsnak": {"datavalue": {"value": {"latitude": 41.9, "longitude": 12.5}}}}], // coords
      "P910": [{"mainsnak": {"datavalue": {"value": {"id": "Q7032956"}}}}]     // main category
    }
  }
}
```

**Output**: Dictionary of properties ready for phase 3 (canonical ID generation)

---

### Phase 2: Fetch Wikidata Backlinks

**Purpose**: What entities are related to this QID?

**Example**: For Q17167 (Roman Republic), backlinks might include:
- Q186214 (First Punic War) → occurs in Q17167
- Q3105 (Punic Wars) → part of Q17167
- Q1048 (Julius Caesar) → historically related to Q17167
- Q12098 (Roman Empire) → successor to Q17167

**Process**:
- Query entities where property X = Q17167
- Collect related entities
- Use as hints for related sub-concepts

**Output**: List of related QIDs + relationship types

---

### Phase 3: Generate Canonical subject_concept_id

**Input**: Wikidata properties from Phase 1

**Process**:
```python
def generate_subject_concept_id(qid, p580, p582, p131):
    # Build canonical composite from properties
    canonical = f"{qid}|start:{p580}|end:{p582}|location:{p131}"
    
    # Hash for stability
    hash_hex = SHA256(canonical)[:12]
    
    return f"subj_{hash_hex}"
```

**Example**:
```
QID: Q17167
P580 (start): -509-01-01T00:00:00Z
P582 (end):   -27-01-01T00:00:00Z
P131 (location): Q38

Canonical: Q17167|start:-509-01-01T00:00:00Z|end:-27-01-01T00:00:00Z|location:Q38
Hash: SHA256(...)[0:12] = f5621c9e329e
Result: subj_f5621c9e329e
```

**Property**: Idempotent — same properties always produce same ID

---

### Phase 4: Fetch Wikipedia & Parse Index

**Input**: Wikipedia title (from Wikidata sitelinks)

**Process**:
```
GET https://en.wikipedia.org/w/api.php?
  action=query&
  titles=Roman_Republic&
  prop=extracts|sections&
  explaintext=true
```

**Wikipedia TOC Example** (Roman Republic):

```
Level 2: Early history and development
Level 2: Government
  Level 3: Magistrates and consuls
  Level 3: Senate
  Level 3: Assemblies
Level 2: Military
  Level 3: Legions
  Level 3: Naval warfare
Level 2: Economy
  Level 3: Trade routes
  Level 3: Coinage
Level 2: Society
  Level 3: Class structure
  Level 3: Slavery
Level 2: Wars and conflicts
  Level 3: Punic Wars
  Level 3: Macedonian Wars
```

**Key Insight**: Each **Level 2 section** = candidate for domain facet sub-concept!

---

### Phase 5: Build Domain Ontology

**Input**: Wikipedia sections + Wikidata properties

**Process**:

1. **Facet Inference**: Map section titles to our 17 facets
   ```
   "Government" → Political facet
   "Military" → Military facet
   "Economy" → Economic facet
   "Society" → Social facet
   "Wars and conflicts" → Military facet
   ```

2. **Canonical Concept Label**: `{MainConcept}--{SectionTitle}`
   ```
   "Roman Republic--Government"
   "Roman Republic--Military"
   "Roman Republic--Economy"
   ```

3. **Evidence Pattern Extraction**: Keywords from section title
   ```
   Section: "Government"
   Keywords: ["government", "governments", "politics", "political"]
   
   Section: "Military"
   Keywords: ["military", "army", "legion", "legions", "soldier", "soldiers"]
   ```

4. **Confidence Baseline**: High (0.82) because sourced from Wikipedia expert review

**Output**: Domain ontology JSON
```json
{
  "qid": "Q17167",
  "subject_concept_id": "subj_f5621c9e329e",
  "wikipedia_title": "Roman Republic",
  "generated_date": "2026-02-15T12:34:56.789Z",
  
  "facets": {
    "Political": {"concepts": 3},
    "Military": {"concepts": 4},
    "Economic": {"concepts": 2},
    "Social": {"concepts": 2}
  },
  
  "typical_sub_concepts": [
    {
      "id": 1,
      "label": "Roman Republic--Early history and development",
      "section_title": "Early history and development",
      "facet": "Political",
      "description": "Wikipedia section: Early history and development",
      "evidence_patterns": ["early", "history", "development", "foundations"],
      "confidence_baseline": 0.82,
      "authority_hints": [],
      "typical_claims_count": [2, 5],
      "wikipedia_source": true
    },
    {
      "id": 2,
      "label": "Roman Republic--Government",
      "section_title": "Government",
      "facet": "Political",
      "evidence_patterns": ["government", "governments", "senate", "magistrate", "consul"],
      "confidence_baseline": 0.82,
      "authority_hints": []
    },
    {
      "id": 3,
      "label": "Roman Republic--Military",
      "section_title": "Military",
      "facet": "Military",
      "evidence_patterns": ["military", "army", "legion", "legions", "soldier", "soldiers"],
      "confidence_baseline": 0.82,
      "authority_hints": []
    },
    ...
  ]
}
```

---

## Agent Initialization with Trained Ontology

### Before Training (Generic Agent)
```python
agent = EconomicAgent(
    civilization="Roman Republic",
    time_period="Period 2",
    facet="Economic"
)
# No domain knowledge
```

### After Training (Specialized Agent)
```python
training_pipeline = AgentTrainingPipeline(qid="Q17167")
ontology = training_pipeline.train()

agent = EconomicAgent(
    civilization="Roman Republic",
    time_period="Period 2",
    facet="Economic",
    domain_ontology=ontology  # ← Self-bootstrapped knowledge
)

# Agent knows:
# - Roman Republic economic sub-concepts: Trade, Coinage, Taxation, Labor
# - Evidence patterns for each
# - Confidence baselines from Wikipedia review
# - Wikidata backlinks to related concepts
```

### Agent Pattern Matching
```python
def propose_sub_concepts(self, findings):
    """
    Agent receives findings from entity discovery phase.
    Pattern-matches against trained domain ontology.
    """
    
    proposals = []
    
    for claim in findings.claims:
        # Loop through ontology sub-concepts
        for concept in self.domain_ontology["typical_sub_concepts"]:
            
            # Count evidence pattern matches
            pattern_matches = 0
            for pattern in concept["evidence_patterns"]:
                if pattern in claim.text.lower():
                    pattern_matches += 1
            
            # If 50%+ patterns matched, candidate for proposal
            if pattern_matches >= len(concept["evidence_patterns"]) * 0.5:
                
                # Confidence = min(claim confidence, concept baseline)
                confidence = min(claim.confidence, concept["confidence_baseline"])
                
                proposals.append({
                    "parent": self.main_concept,
                    "label": concept["label"],
                    "facet": concept["facet"],
                    "source_claim": claim.id,
                    "confidence": confidence,
                    "evidence_pattern_matches": pattern_matches,
                    "wikipedia_section": concept["section_title"]
                })
    
    return proposals
```

---

## Execution Workflow

### Step 1: Train Agents
```bash
# Train economic agent for Roman Republic
python scripts/reference/agent_training_pipeline.py Q17167

# Output: JSON files
## ontologies/Q17167_ontology.json
##   subject_concept_id: subj_f5621c9e329e
##   typical_sub_concepts: [Trade, Coinage, Taxation, Labor]
```

### Step 2: Store Ontologies in Neo4j
```cypher
CREATE (agent:FacetAgent {
  facet: "Economic",
  civilization: "Roman Republic",
  subject_concept_id: "subj_f5621c9e329e"
})
SET agent.domain_ontology = <JSON array of sub-concepts>
SET agent.trained_date = datetime.now()
```

### Step 3: Run Entity Discovery with Trained Agents
```python
# Phase 2A+2B GPT prompted with:
# - SubjectConceptAPI
# - Trained domain ontologies per agent
# - Pattern matching rules

# Result: 40,000+ claims + sub-concept proposals
```

### Step 4: Load Results to Neo4j
```cypher
CREATE (concept:SubjectConcept {
  subject_id: "subj_...",
  label: "Roman Republic--Government",
  qid: "Q17167",
  parent_concept_id: "subj_f5621c9e329e",
  confidence: 0.82,
  wikipedia_section: "Government",
  source: "Agent proposal + Wikipedia validation"
})
```

---

## Advantages of Self-Trained Ontologies

| Aspect | Pre-Curated | Self-Trained |
|--------|------------|--------------|
| **Curation Labor** | 3-4 hrs/ontology | Automated (20-30 min) |
| **Scalability** | Limited to key civilizations | 100+ civilizations possible |
| **Update Frequency** | Manual (static) | Automatic (follows Wikipedia) |
| **Authority Grounding** | Curator choice | Wikipedia peer review |
| **Expert Validation** | Curator expertise only | Wikipedia expert consensus |
| **Finding Bias** | May miss relevant categories | Comprehensive (Wikipedia articles comprehensive) |
| **Facet Coverage** | Manually mapped | Automatically inferred |
| **Geographic Adaptability** | Special case handling | Automatic (from Wikidata) |

---

## Example: Training Agents for Multiple Civilizations

### Initialize Training Batch
```python
civilizations = {
    "Q17167": "Roman Republic",      # Roman history
    "Q6519": "Ancient Egypt",         # Egyptian history
    "Q11017": "Ancient Greece",       # Greek history
    "Q170814": "Islamic Caliphate",   # Islamic history
}

for qid, label in civilizations.items():
    pipeline = AgentTrainingPipeline(qid=qid)
    ontology = pipeline.train()
    pipeline.save_ontology(f"ontologies/{qid}_{label}_ontology.json")
    
    # Register with SubjectConceptRegistry
    registry.register_trained_agent(
        subject_concept_id=ontology["subject_concept_id"],
        civilization=label,
        ontology=ontology
    )
```

### Result: Neo4j Knowledge Graph
```
SubjectConcept(Roman Republic)
  ├─ trained_ontology: [Govt, Military, Economy, Society]
  
SubjectConcept(Ancient Egypt)
  ├─ trained_ontology: [Pharaohs, Religion, Trade, Architecture]

SubjectConcept(Ancient Greece)
  ├─ trained_ontology: [City-States, Philosophy, Democracy, Military]
```

---

## Integration into Phase 2A+2B

### Updated GPT Prompt Structure

```markdown
## SECTION: Agent Domain Ontology Initialization

You are an [EconomicAgent | MilitaryAgent | ...] trained on Wikipedia-curated domain knowledge.

### Your Trained Domain Ontology

Main subject: {main_concept_label}
Subject Concept ID: {subject_concept_id}
Wikipedia Title: {wikipedia_title}

**Your recognized sub-concepts (trained from Wikipedia TOC):**

{for each sub-concept in ontology:
  - Label: {label}
    Evidence Patterns: {evidence_patterns}
    Confidence Baseline: {confidence_baseline}
    Wikipedia Source: {wikipedia_section}
}

### When You Propose Sub-Concepts

When analyzing your findings, check if the evidence contains patterns from your trained ontology.

If 50%+ of a sub-concept's patterns match your findings:
1. Propose the sub-concept
2. Use Wikipedia section title for facet grounding
3. Cite evidence patterns matched
4. Set confidence = MIN(finding_confidence, concept_baseline)

Example:
- Finding: "Evidence of tax collection systems and tribute mechanisms"
- Pattern match: ["tax", "tribute"] matched in concept "Roman Republic--Taxation"
- Pattern score: 2/3 = 66% match ✓
- Proposal: Create sub-concept "Roman Republic--Taxation and Tribute Systems"
- Confidence: MIN(0.88, 0.82) = 0.82

```

---

## FAQ

**Q: What if Wikipedia doesn't have an article for a QID?**
A: Fallback to Wikidata properties only. Build minimal ontology from:
   - P580/P582 (temporal bounds) → suggest "Chronological breakdown"
   - P131 (location) → suggest "Geographic sub-regions"
   - Backlinks → suggest "Related concepts"

**Q: How often should agents retrain?**
A: Training is lightweight (20-30 min per QID). Retrain when:
   - Wikipedia article updated significantly
   - Quarterly refresh cycle
   - Before new civilization/facet agent deployment

**Q: What about non-canonical Wikidata QIDs (low-quality data)?**
A: Pre-validate QIDs:
   - Require 5+ claims in Wikidata
   - Check for Wikipedia article
   - Verify linked labels/descriptions in multiple languages
   - Skip QIDs with <80% data completeness

**Q: Can we use other sources (Oxford Reference, Encyclopedia Britannica)?**
A: Yes! Extend pipeline to:
   - Fetch from external APIs (if available)
   - Parse table of contents from academic sources
   - Merge multiple sources' ontologies
   - Weight by authority (Wikipedia 0.82, Academic 0.90)

---

## Next Steps

1. **Implement Training Pipeline**
   - ✅ `agent_training_pipeline.py` created
   - Test with Q17167 (Roman Republic)
   - Collect Wikipedia TOC parsing results

2. **Register Trained Ontologies in Neo4j**
   - Create FacetAgent nodes with domain_ontology property
   - Link to SubjectConcepts
   - Store confidence baselines

3. **Update Phase 2A+2B GPT Prompt**
   - Integrate domain ontology guidance
   - Add sub-concept proposal criteria
   - Include pattern matching rules

4. **Execute Phase 2A+2B with Trained Agents**
   - Run entity discovery with self-bootstrapped knowledge
   - Collect sub-concept proposals
   - Validate against Wikipedia sources

5. **Scale to Multiple Civilizations**
   - Train 10+ civilization root concepts
   - Generate ontologies for each
   - Build comprehensive agent fleet
