# Domain-Specific Agent Initialization: Canonical Concept Learning

**Date**: 2026-02-15  
**Premise**: Each agent (Economic, Military, Political, etc.) learns domain-specific sub-concept patterns during initialization  
**Goal**: Agents propose sub-concepts grounded in canonical patterns within their facet

---

## 1. Architecture: Agent Initialization with Domain Ontology

### **Workflow**

```
Phase 2 Discovers: Roman Republic (SubjectConcept)
  ↓
Query: What facets have claims for Roman Republic?
  Economic: 0.87 confidence
  Military: 0.93 confidence
  Political: 0.91 confidence
  Diplomatic: 0.89 confidence
  ↓
For each facet threshold >= 0.80:
  Instantiate Agent:
    - EconomicAgent_RomanRepublic
    - MilitaryAgent_RomanRepublic
    - PoliticalAgent_RomanRepublic
    - DiplomaticAgent_RomanRepublic
  ↓
Each agent loads its DOMAIN ONTOLOGY:
  - EconomicAgent loads: "Roman Economic Canonical Concepts"
  - MilitaryAgent loads: "Roman Military Canonical Concepts"
  - etc.
  ↓
Agent analyzes Roman Republic through lens of its domain
  ↓
Agent checks: "Do my findings match canonical patterns?"
  ↓
If YES → Propose sub-concept grounded in domain pattern
```

---

## 2. Domain Ontologies: What Are They?

### **Definition**

A **Domain Ontology** is a curated JSON/Neo4j structure of canonical sub-concepts common in a specific historical or analytical domain.

**Example: Roman Economic Domain Ontology**

```json
{
  "domain": "Roman Economics",
  "civilization": "Ancient Rome",
  "parent_concept": "Q17167",  // Roman Republic
  "facet": "Economic",
  "typical_sub_concepts": [
    {
      "label": "Taxation and Tribute Systems",
      "description": "Imperial tax collection, grain taxes from Egypt, publicani contracts",
      "facet": "Economic",
      "evidence_patterns": [
        "tax collectors",
        "tax revenues",
        "tribute collection",
        "publicani",
        "tributum",
        "grain tax"
      ],
      "authority_hints": ["HJ6000-6899", "sh85134240"],  // LCC/LCSH
      "confidence_baseline": 0.85,
      "typical_claims": [
        "Taxation was primary revenue source",
        "Publicani contracted for tax collection",
        "Egypt grain tax funded state budget"
      ]
    },
    {
      "label": "Trade Networks and Commerce",
      "description": "Mediterranean trade routes, merchant networks, market mechanisms",
      "facet": "Economic",
      "evidence_patterns": [
        "trade route",
        "merchant",
        "commerce",
        "export",
        "import",
        "merchant fleet",
        "maritime trade"
      ],
      "authority_hints": ["HF3001-3005"],
      "confidence_baseline": 0.82,
      "typical_claims": [
        "Trade networks connected Mediterranean",
        "Roman merchants monopolized certain routes",
        "Price variations drove commerce"
      ]
    },
    {
      "label": "Coinage and Monetary Policy",
      "description": "Denarius standard, currency debasement, inflation mechanisms",
      "facet": "Economic",
      "evidence_patterns": [
        "denarius",
        "coin",
        "currency",
        "monetary",
        "inflation",
        "debasement",
        "exchange rate"
      ],
      "authority_hints": ["HG3001-3081"],
      "confidence_baseline": 0.88,
      "typical_claims": [
        "Denarius was standard currency",
        "Metal content debasement caused inflation",
        "Monetary policy reflected military spending"
      ]
    },
    {
      "label": "Labor Systems and Production",
      "description": "Slave labor in production, free labor specialization, agricultural latifundia",
      "facet": "Economic",
      "evidence_patterns": [
        "slave labor",
        "production",
        "latifundia",
        "artisan",
        "craftsman",
        "labor exploitation",
        "agricultural surplus"
      ],
      "authority_hints": ["HV8250-8280"],
      "confidence_baseline": 0.83,
      "typical_claims": [
        "Slave labor drove production efficiency",
        "Latifundia replaced small farms",
        "Labor specialization increased output"
      ]
    }
  ],
  "version": "1.0",
  "curated_by": "Chrystallum Historian",
  "last_updated": "2026-02-15"
}
```

---

## 3. How Agents Use Domain Ontologies

### **Agent Analysis Process**

```python
class FacetAgent:
    """Base class for facet-specific agents"""
    
    def __init__(self, subject_concept_id: str, facet: str):
        self.subject_concept_id = subject_concept_id
        self.facet = facet
        
        # Load domain ontology for this subject + facet
        self.domain_ontology = self.load_domain_ontology(
            subject_concept_id, facet
        )
        
        # Extract canonical concepts
        self.canonical_concepts = {
            c["label"]: c 
            for c in self.domain_ontology["typical_sub_concepts"]
        }
    
    def load_domain_ontology(self, subject_id: str, facet: str) -> Dict:
        """
        Load the domain-specific canonical concept library.
        
        Priority:
        1. Specific: "{civilization}_{facet}_ontology.json"
           (e.g., "Roman_Economic_ontology.json")
        2. General: "{facet}_ontology.json"
           (e.g., "Economic_ontology.json")
        """
        # Determine civilization from subject_concept
        subject = self.db.get_subject_concept(subject_id)
        civilization = subject.get("civilization", "Unknown")
        
        # Try specific first
        specific_path = f"ontologies/{civilization}_{facet}_ontology.json"
        if os.path.exists(specific_path):
            return json.load(open(specific_path))
        
        # Fall back to general
        general_path = f"ontologies/{facet}_ontology.json"
        if os.path.exists(general_path):
            return json.load(open(general_path))
        
        # If neither exists, return empty (no guidance available)
        return {"typical_sub_concepts": []}
    
    def analyze_and_propose_subconcepts(self, analysis_results: Dict) -> List[Dict]:
        """
        Given analysis results, check if they match canonical patterns.
        
        Returns: List of proposed sub-concepts grounded in domain ontology
        """
        
        proposed = []
        
        # For each canonical concept in domain ontology
        for canonical_label, canonical in self.canonical_concepts.items():
            
            # Extract evidence patterns (keywords to match)
            patterns = canonical["evidence_patterns"]
            
            # Check if agent's findings contain these patterns
            pattern_matches = self._match_patterns_in_evidence(
                analysis_results["findings"],
                patterns
            )
            
            # If sufficiently many patterns matched
            if len(pattern_matches) >= len(patterns) * 0.5:  # 50% threshold
                
                # Extract supporting claims
                matching_claims = [
                    claim for claim in analysis_results["claims"]
                    if self._claim_matches_canonical(claim, canonical)
                ]
                
                # Only propose if we have evidence
                if len(matching_claims) >= 3:
                    
                    # Compute confidence
                    confidence = min(
                        self._compute_confidence_from_claims(matching_claims),
                        canonical["confidence_baseline"]  # Cap at baseline
                    )
                    
                    # Propose concept
                    proposal = {
                        "label": canonical_label,
                        "parent_id": self.subject_concept_id,
                        "facet": self.facet,
                        "confidence": confidence,
                        "evidence": [c["text"] for c in matching_claims],
                        "canonical_pattern": canonical["description"],
                        "supporting_claims_count": len(matching_claims),
                        "wikidata_hint": canonical.get("wikidata_hint"),
                        "authority_hints": canonical.get("authority_hints")
                    }
                    
                    proposed.append(proposal)
                    
                    print(f"✓ Proposed: {canonical_label} ({confidence:.2f})")
        
        return proposed
    
    def _match_patterns_in_evidence(self, evidence: List[str], 
                                   patterns: List[str]) -> Dict:
        """
        Count how many patterns appear in evidence.
        Returns: {pattern: count, ...}
        """
        matches = {}
        evidence_text = " ".join(evidence).lower()
        
        for pattern in patterns:
            count = evidence_text.count(pattern.lower())
            if count > 0:
                matches[pattern] = count
        
        return matches
    
    def _claim_matches_canonical(self, claim: Dict, canonical: Dict) -> bool:
        """Check if a claim relates to this canonical concept"""
        claim_text = claim["text"].lower()
        patterns = canonical["evidence_patterns"]
        
        # Does claim text contain any of the canonical patterns?
        return any(p.lower() in claim_text for p in patterns)
    
    def _compute_confidence_from_claims(self, claims: List[Dict]) -> float:
        """Average confidence of matching claims"""
        if not claims:
            return 0.0
        return sum(c.get("confidence", 0.75) for c in claims) / len(claims)


class EconomicAgent(FacetAgent):
    """Economic facet agent"""
    
    def __init__(self, subject_concept_id: str):
        super().__init__(subject_concept_id, facet="Economic")
    
    # Override with economic-specific logic if needed


class MilitaryAgent(FacetAgent):
    """Military facet agent"""
    
    def __init__(self, subject_concept_id: str):
        super().__init__(subject_concept_id, facet="Military")
```

---

## 4. Concrete Example: EconomicAgent Analyzing Roman Republic

```
Input:
  SubjectConcept: Roman Republic
  Facet: Economic
  Findings from analysis: [
    "Grain taxation from Egypt funded state",
    "Publicani contractors collected taxes",
    "Tribute from allies supplemented revenue",
    "Denarius debasement caused inflation over time",
    "Slave labor in mines increased production",
    "Mediterranean merchants dominate trade routes"
  ]
  
  Claims generated:
    [
      {text: "Taxation was primary revenue source", confidence: 0.92},
      {text: "Publicani system monopolized tax collection", confidence: 0.88},
      {text: "Egypt grain reserves critical to budget", confidence: 0.85},
      {text: "Metal debasement triggered price changes", confidence: 0.87},
      {text: "Slave labor in mines exceeded free labor", confidence: 0.80},
      {text: "Merchants controlled Mediterranean shipping", confidence: 0.83}
    ]

Agent Process:
1. Load domain ontology: "Roman_Economic_ontology.json"
2. Extract canonical concepts:
   - Taxation and Tribute Systems
   - Trade Networks and Commerce
   - Coinage and Monetary Policy
   - Labor Systems and Production

3. For "Taxation and Tribute Systems" canonical:
   - Patterns: ["tax", "tribute", "publicani", "tributum"]
   - Evidence match: "taxation", "publicani", "tribute" found ✓✓✓
   - Pattern match score: 3/4 = 75% > 50% threshold
   - Matching claims: 3 (taxation, publicani, tribute)
   - Confidence: min(0.88 avg, 0.85 baseline) = 0.85
   
   → PROPOSE: "Roman Republic--Taxation and Tribute Systems"
     confidence: 0.85
     evidence: ["Grain taxation from Egypt...", "Publicani contractors...", "Tribute from allies..."]
     wikidata_hint: Q15811?
     authority_hints: ["HJ6000-6899"]

4. For "Coinage and Monetary Policy" canonical:
   - Patterns: ["denarius", "coin", "currency", "debasement", "inflation"]
   - Evidence match: "denarius", "debasement", "inflation" found ✓✓✓
   - Pattern match score: 3/5 = 60% > 50% threshold
   - Matching claims: 1 (metal debasement effect)
   - **But only 1 claim!** Needs >= 3 → REJECTED (insufficient evidence)

5. For "Labor Systems and Production" canonical:
   - Patterns: ["slave labor", "production", "latifundia", "artisan", "craftsman"]
   - Evidence match: "slave labor" found ✓
   - Pattern match score: 1/5 = 20% < 50% threshold → REJECTED

6. For "Trade Networks and Commerce" canonical:
   - Patterns: ["trade", "merchant", "commerce", "export", "import", "maritime"]
   - Evidence match: "merchants", "trade routes" found ✓✓
   - Pattern match score: 2/6 = 33% < 50% threshold → REJECTED

Results:
  ✓ Proposed: "Roman Republic--Taxation and Tribute Systems" (0.85)
  ✗ Insufficient evidence for Coinage/Monetary
  ✗ Pattern match too low for Labor Systems
  ✗ Pattern match too low for Trade Networks

Final Sub-Concept Proposals: 1 high-confidence proposal
```

---

## 5. Building Domain Ontologies: Curation Process

### **Where Do Domain Ontologies Come From?**

**Option A: Expert Curation** (Phase 1 - Setup)
- Subject matter experts manually create ontology JSON for key civilizations + facets
- Example: Historian creates "Roman_Economic_ontology.json"
- Includes: canonical concepts, typical evidence patterns, confidence baselines, authority hints

**Option B: Learned from Literature** (Phase 2-3 - Discovery)
- After Phase 2A+2B discovers 10,000+ Entities:
- Run clustering analysis on facet_claims to identify natural sub-concept groupings
- Convert clusters into formal ontology entries
- Validate against authorities (LCC, LCSH, FAST)

**Option C: Hybrid**
- Start with expert-curated ontologies for known civilizations (Roman, Greek, Medieval)
- Auto-generate ontologies for less-studied periods using Phase 2A+2B results

### **Ontology Structure**

```json
{
  "domain": "Roman Economics",
  "civilization": "Ancient Rome",
  "facet": "Economic",
  "parent_concepts": [
    "Q17167",     // Roman Republic
    "Q25419",     // Roman Empire
    "Q42395"      // Late Antiquity Rome
  ],
  "version": "1.0",
  "curated_by": "Dr. MacKillian, Economic Historian",
  "curated_date": "2026-02-01",
  "source": ["Smith et al. Roman Economic History (2020)", "Cambridge Ancient History Vol. VIII"],
  
  "typical_sub_concepts": [
    {
      "label": "Taxation and Tribute Systems",
      "description": "Imperial tax collection, grain taxes, publicani contracts",
      "facet": "Economic",
      "canonical_period": [-509, 476],  // BCE to CE
      "geographic_scope": ["Italia", "Provinces", "Egypt"],
      
      // Evidence matching
      "evidence_patterns": [
        "tax collector",
        "tax revenue",
        "tribute",
        "publicani",
        "grain tax",
        "tributum",
        "census"
      ],
      
      // Authority grounding
      "authority_hints": [
        {"authority": "LCC", "code": "HJ6000-6899"},
        {"authority": "LCSH", "id": "sh85134240"}
      ],
      
      // Quality signals
      "confidence_baseline": 0.85,
      "claims_typical_count": 2-5,  // Expect 2-5 claims for this sub-concept
      "importance_rating": "HIGH",   // How central to understanding domain?
      "temporal_coverage": {
        "Republic": 0.90,   // Confidence this appears in Republic era
        "Empire": 0.88,
        "Late": 0.72
      },
      
      // Examples of typical claims
      "typical_claims": [
        "Taxation was the primary source of imperial revenue",
        "Publicani competed in auction for tax collection contracts",
        "Egypt's grain tax was crucial to military funding",
        "Tax collection motivated provincial conquest"
      ]
    },
    // ... more canonical concepts
  ]
}
```

---

## 6. Advantages of Domain Ontology Approach vs Generic Density

### **Generic Density Analysis**
```
Pros:
  - Universal (works for any domain)
  - Objective (mathematical score)
  
Cons:
  - Doesn't understand domain context
  - May factor at wrong granularity
  - May miss subtle patterns
  - Agents propose generic splits (time-based) without domain insight
```

### **Domain Ontology Approach**
```
Pros:
  - Grounded in actual historical/scholarly patterns
  - Agents understand what "economics" really means for Romans
  - Proposes concepts historians would recognize
  - Confidence validated against expert baselines
  - Can be refined over time as domain knowledge improves
  
Cons:
  - Requires curation (but phased: experts first, then learned)
  - Specific to each civilization + facet (more effort)
  - Need to maintain ontologies as knowledge grows
```

---

## 7. Phase 2A+2B Integration

### **Workflow**

```
[Hour 1-2] Discover 2,100 entities → Create SubjectConcepts

[Hour 2-3] Generate 40,000+ facet claims
           → Organize by SubjectConcept + Facet
           
[Hour 3-4] FOR EACH SubjectConcept with facet_primaries >= 0.80:
             Instantiate facet agents
             Load domain ontologies
             ↓
             EconomicAgent_RomanRepublic.analyze_and_propose_subconcepts()
             MilitaryAgent_RomanRepublic.analyze_and_propose_subconcepts()
             PoliticalAgent_RomanRepublic.analyze_and_propose_subconcepts()
             ...
             
[Hour 4-5] Collect all proposals
           Filter to authority-grounded (Tier 1-3)
           Dedup (if multiple agents proposed same concept)
           ↓
[Hour 5-6] Load proposals to Neo4j
           Link existing claims to new sub-concepts

[Post] Curator review:
       - Verify proposals make sense
       - Approve/modify/reject
       - Refine domain ontologies based on feedback
```

---

## 8. Example Domain Ontologies to Create

### **Priority 1: Roman Civilization (3 ontologies)**
1. Roman_Military_ontology.json
   - Canonical: Legions, battles, commanders, tactics, forts
2. Roman_Political_ontology.json
   - Canonical: Government institutions, political factions, laws
3. Roman_Economic_ontology.json
   - Canonical: Taxation, trade, coinage, labor

### **Priority 2: Classical Greek (2 ontologies)**
1. Greek_Military_ontology.json
2. Greek_Political_ontology.json

### **Future Expansion**
- Medieval Europe, China, Islamic World, etc.

---

## 9. Summary: Domain Ontology vs Density Analysis

| Approach | When Agent Creates Sub-Concept |
|----------|--------------------------------|
| **Density** | "I have 45 claims total, 12 in Military, should I split?" |
| **Domain** | "I'm an EconomicAgent analyzing Romans, and I found evidence of Taxation Systems (canonical concept). Should I create this?" |

**Domain approach is superior** because:
- ✅ Leverages expert knowledge about what matters in each field
- ✅ Agents understand their domain deeply, not generic rules
- ✅ Naturally aligns with how scholars think about topics
- ✅ Enables iterative refinement (learn from Phase 2A+2B results)
- ✅ Produces concepts historians recognize

**Ready to create domain ontologies for Roman civilization?**

