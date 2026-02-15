# When Agents SHOULD Propose New SubjectConcepts: Density Analysis

**Date**: 2026-02-15  
**Premise**: Dense subjects need granular sub-concepts to properly represent complexity  
**Goal**: Agent recognizes when a concept is "too dense" and proposes children to factor it

---

## 1. Density Metrics: How to Measure When Granularity Is Needed

### **Metric A: Claim Saturation** (Primary Signal)

```
After generating claims for a SubjectConcept, count by primary_facet:

Roman Republic:
  Military: 12 claims ← Dense
  Political: 10 claims ← Dense
  Diplomatic: 6 claims ← Moderate
  Social: 4 claims ← Sparse
  Communication: 3 claims ← Sparse
  
Density Score = (sum of claims > 5) / total_claims
             = (12 + 10 + 6) / 35 = 0.80 (HIGH DENSITY)

Threshold: If Density ≥ 0.70, CANDIDATE FOR FACTORING
```

**Why?** If a concept has >10 high-confidence claims in a single facet, those claims likely involve sub-events that should be their own concepts.

### **Metric B: Facet Diversity** (Structural Signal)

```
If SubjectConcept touches many facets equally:

Roman Republic:
  Touches Military (12), Political (10), Diplomatic (6), 
  Social (4), Religious (3), Economic (2), Communication (3)
  
Facet Diversity = 7 facets with claims
                = More than half of 17 possibilities

→ This entity is STRUCTURALLY COMPLEX
→ Different facets may need specialized sub-concepts
```

**Why?** A concept covering 7+ facets is doing too much. Each facet cluster might deserve its own child concept.

### **Metric C: Temporal Span vs Event Density** (Historical Signal)

```
Roman Republic temporal span: -509 to -27 = 482 years

Event density = # of major events / temporal span in centuries
              = 45 events / 4.82 centuries
              ≈ 9.3 events per century

Threshold: If > 5 events per century, CANDIDATE FOR CHRONOLOGICAL FACTORING
```

**Examples:**
- Roman Republic: 9.3/century → FACTOR (create period/epoch sub-concepts)
- Augustus reign: 3.1/century → DON'T FACTOR (manageable)
- Battle of Cannae: single event → CAN'T FACTOR (leaf node)

**Why?** Dense historical periods need temporal granularity to avoid conflating unrelated events.

### **Metric D: Authority Subsumption** (External Signal)

```
Check if authorities have narrow sub-classifications:

Parent: Roman Republic → LCC: DG232-248

Child authorities found:
  DG232-235: Republic origins
  DG236-240: Early Republic (Punic wars era)
  DG241-245: Late Republic (Caesar-Pompey civil war)
  DG246-248: Late Republic administrative
  
Number of sub-classifications: 4
→ LCC itself suggests factoring into 4 concepts!

Factoring Signal: (LCC sub-classes > 2) OR (LCSH subdivisions > 3)
```

**Why?** If authorities pre-factored the topic, don't ignore that signal. Create corresponding sub-concepts.

### **Metric E: Primacy Clustering** (Claim Quality Signal)

```
After generating facet claims, check emergent primacy scores:

Roman Republic claim analysis:
  primacy_military = avg(confidence of Military claims)
                  = 0.93
  primacy_political = 0.91
  primacy_diplomatic = 0.87
  primacy_social = 0.72
  primacy_communication = 0.68
  
Clustering: Are some facets confidence-coherent (all 0.90+)?

Clusters found:
  Cluster 1: Military + Political (both 0.91+) → Could be "Republican Wars"
  Cluster 2: Social + Communication (both 0.68-0.72) → Could be "Republican Society"
  
→ Natural sub-concept boundaries emerge from claim coherence
```

**Why?** When claims naturally cluster by facet & confidence, that's a signal for child concepts.

---

## 2. Density Decision Framework

### **Step 1: Measure All Metrics**

```python
class DensityAnalyzer:
    def analyze_concept_density(self, concept_id: str) -> Dict:
        """
        Returns composite density score and factoring recommendations
        """
        
        # Metric A: Claim Saturation
        claims_by_facet = self.count_claims_by_facet(concept_id)
        saturation_score = self._calculate_saturation(claims_by_facet)
        
        # Metric B: Facet Diversity
        facet_count = len([f for f, count in claims_by_facet.items() if count > 0])
        diversity_score = facet_count / 17  # Out of 17 facets
        
        # Metric C: Temporal Density
        concept = self.get_concept(concept_id)
        temporal_span = concept["period_end"] - concept["period_start"]
        event_density = len(claims_by_facet) / max(temporal_span / 100, 1)
        
        # Metric D: Authority Subsumption
        lcc_codes = concept.get("lcc_codes", [])
        authority_subsumption = self._check_lcc_subdivisions(lcc_codes)
        
        # Metric E: Primacy Clustering
        primacy_clusters = self._cluster_by_primacy(concept_id)
        
        # Composite Score
        composite = (
            saturation_score * 0.40 +      # Most important: actual claim saturation
            diversity_score * 0.25 +       # Important: structural complexity
            authority_subsumption * 0.20 + # External validation
            (event_density > 5) * 0.15     # Historical density flag
        )
        
        return {
            "composite_density": composite,
            "saturation": saturation_score,
            "facet_diversity": diversity_score,
            "event_density": event_density,
            "authority_subsumption": authority_subsumption,
            "factoring_recommended": composite >= 0.65,
            "reasoning": self._generate_reasoning({...})
        }
```

### **Step 2: Interpret Density Tiers**

```
Composite Density Score (0.0 to 1.0):

0.0-0.40:  SPARSE    → No factoring needed
           Example: "Augustus" (single figure, 3-5 major claims)
           Action: Treat as leaf concept

0.40-0.65: MODERATE  → Optional factoring
           Example: "Roman Empire" (large but not yet overwhelming)
           Action: Monitor, suggest to curator if > 0.60

0.65-0.80: DENSE     → Factoring RECOMMENDED
           Example: "Roman Republic" with 35+ claims
           Action: Agent proposes 2-4 child concepts

0.80-1.00: VERY DENSE → Factoring CRITICAL
           Example: "Roman Wars" with 50+ claims across 7 facets
           Action: Agent must propose concepts or flag for splitting
```

---

## 3. Factoring Strategies: How to Actually Create Sub-Concepts

### **Strategy A: Facet-Based Factoring** (Best for Structural Density)

Used when: Entity has 5+ facets with significant claims

```python
# Parent: Roman Republic (Military + Political + Diplomatic + Social)

# Observation: Claims cluster naturally
clusters = {
    "Military/Diplomatic": ["Punic Wars", "Macedonian Wars", "Conquest strategy"],
    "Political": ["Senate governance", "Tribunes", "Laws enacted"],
    "Social": ["Class structure", "Citizen rights", "Plebeian revolt"]
}

# Create sub-concepts:
children = [
    api.claim_new_concept(
        label="Roman Republic--Military Campaigns",
        parent_id="subj_f5621c9e329e",  # Roman Republic
        confidence=0.92,
        evidence="Livy, Polybius describe wars as distinct topic",
        facet="Military",
        period_start=-509,
        period_end=-27
    ),
    api.claim_new_concept(
        label="Roman Republic--Political Institutions",
        parent_id="subj_f5621c9e329e",
        confidence=0.91,
        evidence="Political reforms, governance structures",
        facet="Political"
    ),
    api.claim_new_concept(
        label="Roman Republic--Social Structure",
        parent_id="subj_f5621c9e329e",
        confidence=0.88,
        evidence="Class system, citizen rights documentation"
    )
]
```

**When to use:** Entity spans 5+ unrelated facets; claims don't have temporal thread

---

### **Strategy B: Chronological Factoring** (Best for Temporal Density)

Used when: Long-lived entity with >5 events per century

```python
# Parent: Roman Republic (-509 to -27 = 482 years)
# Event density: 9.3 events/century (HighDensity!)

# Authority signal: LCC DG232-248 breaks into:
# DG232-235: Rise/Early Republic (509-264, favorable)
# DG236-240: Punic Wars era (264-146) 
# DG241-245: Late Republic civil war (146-27, tumultuous)

# Create temporal children:
children = [
    api.claim_new_concept(
        label="Roman Republic--Early Period (509-264 BCE)",
        parent_id="subj_f5621c9e329e",
        confidence=0.90,
        period_start=-509,
        period_end=-264,
        evidence="LCC DG232-235, Livy Books 1-10"
    ),
    api.claim_new_concept(
        label="Roman Republic--Classical Period (264-146 BCE)",
        parent_id="subj_f5621c9e329e",
        confidence=0.92,
        period_start=-264,
        period_end=-146,
        evidence="LCC DG236-240, Punic Wars era"
    ),
    api.claim_new_concept(
        label="Roman Republic--Late Period (146-27 BCE)",
        parent_id="subj_f5621c9e329e",
        confidence=0.91,
        period_start=-146,
        period_end=-27,
        evidence="LCC DG241-245, Civil wars documentation"
    )
]
```

**When to use:** Entity covers multiple centuries; temporal sub-divisions exist in authorities; event distribution uneven

---

### **Strategy C: Event-Based Factoring** (Best for Claim Event Density)

Used when: Entity has 10+ claims in single facet but they're about distinct sub-events

```python
# Parent: "Punic Wars" (Roman Republic--Military Campaigns child)
# Military claims: 15 claims about tactics, battles, commanders
# But they cluster around specific battles:

event_clusters = {
    "First Punic War (264-241 BCE)": ["Battle of Drepana", "Siege tactics", "Naval innovation"],
    "Second Punic War (218-201 BCE)": ["Hannibal tactics", "Cannae", "Scipio strategy"],
    "Third Punic War (149-146 BCE)": ["Siege of Carthage", "Final conquest"]
}

# Create event children:
children = [
    api.claim_new_concept(
        label="First Punic War",
        parent_id="subj_f36bb758dbd1",  # Punic Wars
        wikidata_qid="Q186214",
        confidence=0.94,
        period_start=-264,
        period_end=-241
    ),
    api.claim_new_concept(
        label="Second Punic War",
        parent_id="subj_f36bb758dbd1",
        wikidata_qid="Q186216",
        confidence=0.95,
        period_start=-218,
        period_end=-201
    ),
    api.claim_new_concept(
        label="Third Punic War",
        parent_id="subj_f36bb758dbd1",
        confidence=0.92,
        period_start=-149,
        period_end=-146
    )
]
```

**When to use:** Entity has 10+ claims about sub-events that are themselves named entities in Wikidata/authorities

---

### **Strategy D: Geographic/Administrative Factoring** (Best for Spatial Density)

Used when: Entity encompasses multiple geographic regions with distinct histories

```python
# Parent: "Roman Empire"
# Claims touch: Italy, Gaul, Egypt, Spain, Britain, Balkans, etc.
# Each region has distinct governance/history

children = [
    api.claim_new_concept(
        label="Roman Empire--Italia Province",
        parent_id="subj_5c01cbe0b9bc",
        facet="Political",
        confidence=0.93
    ),
    api.claim_new_concept(
        label="Roman Empire--Gallia Province",
        parent_id="subj_5c01cbe0b9bc",
        facet="Political",
        confidence=0.91
    ),
    # ... more provinces
]
```

**When to use:** Entity spans multiple provinces/regions; LCSH uses geographic subdivisions; claims have geographic coherence

---

## 4. Agent Decision Tree: "Should I Create This Sub-Concept?"

```
Agent finishes analyzing parent concept
↓
Run DensityAnalyzer.analyze_concept_density(concept_id)
↓
Get composite_density score
│
├─ Score < 0.40 (SPARSE)
│  └─ No, parent is manageable. Do nothing.
│
├─ Score 0.40-0.65 (MODERATE)
│  └─ Maybe: Flag for curator review, don't auto-create
│
├─ Score 0.65-0.80 (DENSE)
│  ├─ YES: Parent needs factoring
│  ├─ Determine strategy:
│  │  ├─ facet_diversity > 0.50? → Use FACET-BASED strategy
│  │  ├─ event_density > 5? → Use CHRONOLOGICAL strategy
│  │  ├─ saturation > 0.80? → Use EVENT-BASED strategy
│  │  └─ Otherwise → Use AUTHORITY-LED strategy
│  │
│  ├─ For each identified sub-cluster:
│  │  ├─ Search for Wikidata Q-identifier
│  │  ├─ Search for LCC sub-classification
│  │  └─ Generate confidence score
│  │
│  └─ Call api.claim_new_concept() for each child
│
└─ Score > 0.80 (VERY DENSE)
   ├─ CRITICAL: Must factor or flag
   ├─ Determine top 3-5 child concepts (don't go overboard)
   ├─ Create children with evidence from claim clustering
   └─ Link all existing claims to appropriate child concepts
```

**Implementation:**

```python
async def propose_sub_concepts_if_dense(self, concept_id: str) -> List[Dict]:
    """
    Agent autonomously proposes sub-concepts based on density analysis.
    Returns list of proposed concepts (not yet created).
    """
    
    # Analyze density
    density = self.analyzer.analyze_concept_density(concept_id)
    
    if density["composite_density"] < 0.65:
        return []  # Not dense enough to factor
    
    # Determine factoring strategy
    strategy = self._determine_strategy(density)
    
    # Identify natural child concepts
    children = self._identify_children(concept_id, strategy)
    
    # For each child, validate against authorities
    proposals = []
    for child in children:
        # Search authorities
        child["authority_search"] = search_authorities(
            label=child["label"],
            period_start=child.get("period_start")
        )
        
        # Generate confidence from evidence clustering
        child["confidence"] = self._infer_confidence_from_claims(
            concept_id, 
            child["label"]
        )
        
        # Check: Is this grounded in authorities?
        if child["authority_search"]["tier"] >= 1:
            proposals.append(child)
            print(f"✓ Proposed: {child['label']} ({child['confidence']})")
        else:
            print(f"✗ Skipped: {child['label']} (not authority-grounded)")
    
    return proposals
```

---

## 5. Examples: Density Analysis & Factoring Decisions

### **Example 1: Roman Republic (VERY DENSE)**

```
Density Analysis:
  Claims: 45 total
  Claim Saturation: 0.75 (Military 12, Political 10, Diplomatic 6)
  Facet Diversity: 7/17 = 0.41
  Temporal: -509 to -27 (482 years), 9.3 events/century
  Authority: LCC has 4 sub-classifications (DG232-248)
  
  Score = 0.75 * 0.40 + 0.41 * 0.25 + 0.50 * 0.20 + 1.0 * 0.15
        = 0.30 + 0.10 + 0.10 + 0.15 = 0.65 → BORDERLINE

  Actually: With saturation 0.75 & authority subsumption, composite ≈ 0.72 (DENSE)

Decision: YES, factor it
→ Create 3 temporal children + 1 thematic child
  - "Roman Republic--Early Period (509-264)"
  - "Roman Republic--Classical Period (264-146)"
  - "Roman Republic--Late Period (146-27)"
  - Alternative: "Roman Republic--Military Campaigns" (facet-based)
```

### **Example 2: Augustus (SPARSE)**

```
Density Analysis:
  Claims: 5 total
  Saturation: 0.20 (Biographical 3, Military 1, Political 1)
  Facet Diversity: 3/17 = 0.18
  Temporal: -63 to 14 CE (77 years), 0.65 events/century
  Authority: LCC no subdivisions
  
  Score = 0.20 * 0.40 + 0.18 * 0.25 + 0.0 * 0.20 + 0.0 * 0.15
        = 0.08 + 0.045 + 0 + 0 = 0.125 (SPARSE)

Decision: NO, don't factor
→ Augustus stays as leaf concept
→ His individual claims (military victories, laws) don't justify sub-concepts
```

### **Example 3: Caesar's Gallic Wars (MODERATE-DENSE)**

```
Density Analysis:
  Claims: 18 total
  Saturation: 0.65 (Military 12, Political 4, Communication 2)
  Facet Diversity: 3/17 = 0.18
  Temporal: -58 to -50 (8 years), 22.5 events/century (!!)
  Authority: LCC DG261-268 may have subdivisions
  
  Score = 0.65 * 0.40 + 0.18 * 0.25 + 0.50 * 0.20 + 1.0 * 0.15
        = 0.26 + 0.045 + 0.10 + 0.15 = 0.555 (MODERATE)

Decision: BORDERLINE - Check event density
→ High events/century (22.5) suggests chronological factoring
→ Propose: "Caesar's Conquest of Gallia--Year 1 (58 BCE)"
           "Caesar's Conquest of Gallia--Year 2-7 (57-52)"
           etc.
→ But: Short timespan means might not need full factoring
→ FLAG FOR CURATOR REVIEW rather than auto-create
```

---

## 6. Integration with Phase 2A+2B

### **When Agent Runs Density Analysis**

```
Phase 2A+2B Execution Timeline:

[Hour 1-2] GPT discovers 2,100 entities
  └─ Creates SubjectConcepts (T1-T3 grounded)

[Hour 2-3] GPT generates 40,000+ facet claims
  └─ Organizes claims by SubjectConcept

[Hour 3-4] Agent runs DENSITY ANALYSIS
  └─ Analyzes density for each concept
  └─ Identifies which need factoring
  └─ Generates proposals for sub-concepts

[Hour 4-5] Agent validates proposals
  └─ Searches authorities for each proposed child
  └─ Filters to only authority-grounded proposals
  └─ Confidence score each proposal

[Hour 5-6] Load Phase 2 results to Neo4j
  └─ Includes original concepts
  └─ Includes proposed sub-concepts
  └─ Includes claim-to-concept mappings

[Post] Curator review
  └─ Approve/reject borderline proposals
  └─ Adjust confidence scores as needed
```

---

## 7. Summary: Positive Criteria for Concept Creation

### **Create Sub-Concept If:**

✅ **Density Score ≥ 0.65** AND
✅ **Child Concept Is Authority-Grounded** (Tier 1-3) AND
✅ **Evidence Clusters Support The Split** (claims naturally group) AND
✅ **Confidence ≥ 0.80** (high confidence in proposal)

### **Don't Create If:**

❌ **Density Score < 0.65** (parent not actually dense)
❌ **Child Not Grounded** (no Wikidata, LCC, LCSH)
❌ **Single Claim Type** (only 1-2 claims about this sub-concept)
❌ **Too Many Children** (> 5 proposed; parent is over-factored)

### **Defer to Curator If:**

⏳ **0.55 ≤ Density < 0.65** (borderline density)
⏳ **Child Confidence 0.75-0.80** (borderline confidence)
⏳ **Authority Ambiguous** (maps to 2+ different concepts)

This grounds agent creativity in **observable complexity** while preventing hallucination.

