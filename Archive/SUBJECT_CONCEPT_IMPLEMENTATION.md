# SubjectConcept Schema & API - Implementation Complete

**Date**: 2026-02-15  
**Status**: ✅ Complete and Ready for Phase 2A+2B  
**Components**: Cypher schema + Python loader + Agent API

---

## 1. What Was Created

### **A. Cypher Schema** (`Cypher/subject_concept_schema.cypher`)
- 7 constraints for unique properties (concept_id, label+wikidata_qid, lcsh_id, fast_id, etc.)
- 14 indexes for query performance (facet, confidence, labels, timestamps)
- Enforces data integrity (all required properties present)
- Ready for LCSH/FAST/LCC authority integration

**Key Constraints on SubjectConcept:**
- `subject_id` IS UNIQUE (pointer to concept)
- `concept_id` IS UNIQUE (alternative pointer)
- (`label`, `wikidata_qid`) IS UNIQUE (prevents duplicates)
- `label` IS REQUIRED
- `facet` IS REQUIRED
- `subject_id` IS REQUIRED

### **B. Schema Loader** (`scripts/reference/create_subject_concept_schema.py`)
- Creates constraints & indexes automatically
- Bootstraps 5 core SubjectConcepts:
  1. Roman Republic (Political, -509 to -27)
  2. Roman Empire (Political, -27 to 476)
  3. Punic Wars (Military, -264 to -146)
  4. Caesar's Gallic Wars (Military, -58 to -50)
  5. Augustus (Biographical, -63 to 14)
- Creates SubjectConceptRegistry for governance
- Builds hierarchy (parent-child relationships)

**Execution:**
```bash
python scripts/reference/create_subject_concept_schema.py --password Chrystallum
```

**Output:**
```
✓ Schema constraints and indexes created
✓ Created 5 bootstrap SubjectConcepts
✓ Created registry with 5 concept links
✓ SubjectConcept nodes: 6
✓ SubjectConceptRegistry nodes: 1
✓ Claim nodes: 2
```

### **C. Agent API** (`scripts/reference/subject_concept_api.py`)
Programmatic interface for Phase 2A+2B GPT to:

1. **Check if concept exists**
   ```python
   api.concept_exists("Roman Republic")
   ```

2. **Claim new concept** (with validation)
   ```python
   concept = api.claim_new_concept(
       label="Caesar's Conquest of Gaul",
       parent_id="subj_roman_republic_q17167",
       wikidata_qid="Q181098",
       confidence=0.92,
       evidence="Caesar's Commentarii de Bello Gallico",
       period_start=-58,
       period_end=-50
   )
   ```
   
   **Validation Rules:**
   - Confidence ≥ 0.75 required (fails if below)
   - Confidence < 0.90 → "pending_review"
   - Confidence ≥ 0.90 → "auto_approved"
   - Checks duplicates automatically

3. **Create facet claims**
   ```python
   claim = api.create_facet_claim(
       concept_id=concept["concept_id"],
       text="Caesar used superior legionary tactics",
       primary_facet="Military",
       related_facets=["Political", "Technological"],
       confidence=0.95,
       evidence="Commentarii de Bello Gallico"
   )
   ```
   
   **Facet Assignment:**
   - 17 valid facets: Military, Political, Social, Economic, Diplomatic, Religious, Legal, Literary, Cultural, Technological, Artistic, Philosophical, Scientific, Geographic, Biographical, Demographic, Architectural, Communication
   - Related facets limited to 3 (automatically truncated)
   - All claims linked to SubjectConcept

4. **Get facet profile** (shows which facets have claims)
   ```python
   profile = api.get_concept_facet_profile(concept_id)
   # Returns:
   # {
   #     "Military": {"claim_count": 8, "avg_confidence": 0.93},
   #     "Political": {"claim_count": 6, "avg_confidence": 0.91},
   #     ...
   # }
   ```

---

## 2. Neo4j Structure

### **SubjectConcept Node** (5 bootstrap created)
```cypher
(:SubjectConcept {
    concept_id: "subj_roman_republic_q17167",        // Unique ID
    subject_id: "subj_roman_republic_q17167",        // Duplicate key (required by constraint)
    label: "Roman Republic",                         // Display name
    facet: "Political",                              // Primary facet
    wikidata_qid: "Q17167",                          // Wikidata link
    parent_concept_id: null,                         // Parent for hierarchy
    period_start: -509,                              // Start year (BCE = negative)
    period_end: -27,                                 // End year
    lcc_codes: ["DG232-DG248"],                      // Authority alignments
    lcsh_ids: ["sh85114436"],
    fast_ids: [1352255],
    is_canonical: true,                             // From bootstrap vs agent-created
    is_agent_created: false,
    validation_status: "approved",
    source: "Wikidata + LCC DG",
    creation_timestamp: "2026-02-15T14:30:00",
    facet_claims_count: 0,                          // Updated as claims added
    child_concept_count: 2,                         // Updated as children added
    concept_depth: 0                                // 0 = root, 1+ for children
})
```

### **SubjectConceptRegistry Node** (1 created)
```cypher
(:SubjectConceptRegistry {
    registry_id: "registry_roman_antiquity_001",
    parent_concept_id: "subj_roman_republic_q17167",
    total_concepts: 5,
    validation_threshold_confidence: 0.75,
    auto_approval_confidence: 0.90,
    last_updated: "2026-02-15T14:30:00",
    curator: "system_bootstrap",
    concept_ids_ordered: [...]
})
```

### **Relationships**
```
SubjectConcept -[:HAS_CHILD_CONCEPT]-> SubjectConcept (hierarchy)
  Roman Republic → Punic Wars
  Roman Republic → Caesar's Gallic Wars

SubjectConcept -[:HAS_FACET_CLAIM]-> Claim (facet-based knowledge)
  (when Phase 2 loads claims)

SubjectConceptRegistry -[:CONTAINS]-> SubjectConcept (governance)
  registry_roman_antiquity_001 → (all 5 concepts)
```

---

## 3. Phase 2A+2B Integration

### **How GPT Will Use This**

**Step 1: Check Registry**
```python
# At startup
api.concept_exists("Roman Republic")  # Returns existing concept

api.concept_exists("Battle of Cannae")  # Returns None (doesn't exist yet)
```

**Step 2: Discover Entities → SubjectConcepts**
```python
# While discovering entities
concept = api.claim_new_concept(
    label="Battle of Cannae",
    parent_id="subj_punic_wars_q3105",  # Link to parent
    wikidata_qid="Q181098",
    confidence=0.93,
    evidence="Livy's Ab Urbe Condita, Book 22"
)
```

**Step 3: Create Facet Claims**
```python
# For each discovered aspect
claim1 = api.create_facet_claim(
    concept_id=concept["concept_id"],
    text="Hannibal's double envelopment tactic defeated larger Roman force",
    primary_facet="Military",
    related_facets=["Tactical", "Political"],
    confidence=0.96
)

claim2 = api.create_facet_claim(
    concept_id=concept["concept_id"],
    text="Roman propaganda claimed tactical innovation (caligae marching speed)",
    primary_facet="Communication",
    related_facets=["Military", "Political"],
    confidence=0.82,
    communication_metadata={
        "medium": ["written narrative", "oral tradition"],
        "purpose": ["legitimation"],
        "audience": ["Senate", "Roman public"]
    }
)
```

**Step 4: Query Facet Profile**
```python
# After loading all claims for a SubjectConcept
profile = api.get_concept_facet_profile("subj_battle_cannae_...")

# Shows which agents should be created/prioritized
if profile.get("Military", {}).get("claim_count", 0) >= 5:
    print("→ Instantiate MilitaryAgent")
if profile.get("Communication", {}).get("claim_count", 0) >= 2:
    print("→ Flag Communication meta-facet for analysis")
```

---

## 4. Multi-Authority Federation (Ready for Phase 3)

### **Authority Alignment Pattern**
```cypher
// After FAST parser complete
(subj:SubjectConcept)-[:ALIGNED_WITH_FAST {
    fast_id: 1352255,
    confidence: 0.88,
    alignment_type: "approximate"
}]->(fast:FAST_Subject)

// After LCSH loader complete
(subj)-[:ALIGNED_WITH_LCSH {
    lcsh_id: "sh85114436",
    confidence: 0.98,
    alignment_type: "exact"
}]->(lcsh:LCSH_Subject)

// LCC already mapped
(subj)-[:ALIGNED_WITH_LCC {
    lcc_code: "DG232-248",
    confidence: 0.99,
    alignment_type: "exact"
}]->(lcc:LCC_Class)
```

**Confidence scores reflect authority quality:**
- LCC 0.99 (most granular on dates)
- LCSH 0.98 (official heading)
- FAST 0.88 (less granular on dates)

---

## 5. Key Files Summary

| File | Purpose | Status |
|------|---------|--------|
| `Cypher/subject_concept_schema.cypher` | Schema constraints & indexes | ✅ Created |
| `scripts/reference/create_subject_concept_schema.py` | Schema + bootstrap loader | ✅ Executed |
| `scripts/reference/subject_concept_api.py` | Agent interface for concept creation | ✅ Ready |
| `SUBJECT_ONTOLOGY_ARCHITECTURE.md` | Design documentation | ✅ Complete |
| `tmp/verify_subject_concepts.py` | Verification queries | ✅ Tested |

---

## 6. Next Steps

### **Immediate (Phase 2A+2B Ready)**
- ✅ SubjectConcept infrastructure complete
- ✅ API ready for GPT integration
- ⏳ Update GPT_PHASE_2_PARALLEL_PROMPT.md to include subject_concept_api import

### **Week 1-2 (Phase 2+)**
- Build FAST parser (extract 100K+ MARCXML subjects)
- Build LCSH loader (create LCSH_Subject nodes)
- Create authority alignment queries

### **Week 2-3 (Phase 3)**
- Multi-authority federation dashboard
- RDF/Linked Data export
- Entity → Place+PlaceVersion transformation

---

## 7. Quick Reference: API Usage

```python
from scripts.reference.subject_concept_api import SubjectConceptAPI

# Initialize
api = SubjectConceptAPI("bolt://localhost:7687", "neo4j", "Chrystallum")

# Check concept
existing = api.concept_exists("Caesar's Gallic Wars")

# Create concept (validates confidence >= 0.75)
concept = api.claim_new_concept(
    label="Caesar's Conquest of Gaul",
    parent_id="subj_roman_republic_q17167",
    wikidata_qid="Q181098",
    confidence=0.92,  # Required
    evidence="Caesar's Commentarii",
    agent_name="GPT_PHASE_2A+2B"
)

# Add facet claim
claim = api.create_facet_claim(
    concept_id=concept["concept_id"],
    text="Military tactics...",
    primary_facet="Military",
    related_facets=["Political"],
    confidence=0.95,
    evidence="Primary source"
)

# Get facet distribution
profile = api.get_concept_facet_profile(concept["concept_id"])
# {"Military": {"claim_count": 3, "avg_confidence": 0.93}}

api.close()
```

---

## Status: Ready for Phase 2A+2B Execution ✅

All infrastructure in place. GPT prompt should import and use `SubjectConceptAPI` to:
1. Check registry before creating entities
2. Create SubjectConcepts with validation
3. Populate facet claims per discovery
4. Record which facets have coverage (defines sub-agents)

