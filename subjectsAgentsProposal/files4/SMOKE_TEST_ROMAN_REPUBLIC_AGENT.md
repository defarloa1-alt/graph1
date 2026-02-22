# Smoke Test: Roman Republic Agent - Facet Claim Generation

**Date**: 2026-02-15  
**Purpose**: Test single ChatGPT agent generating claims across all 17 facets  
**Future State**: Subagents will be created dynamically per facet  

---

## **Test Objective**

Validate that a single LLM agent can:
1. Understand the 17 facet taxonomy
2. Generate valid claims for each facet
3. Provide proper evidence/authority links
4. Output structured data for Neo4j ingestion

---

## **The 17 Facets**

### **16 Domain Facets**
1. Military
2. Political
3. Social
4. Economic
5. Diplomatic
6. Religious
7. Legal
8. Literary
9. Cultural
10. Technological
11. Agricultural
12. Artistic
13. Philosophical
14. Scientific
15. Geographic
16. Biographical

### **1 Meta-Facet**
17. Communication (cross-cutting dimension)

---

## **ChatGPT System Prompt**

```
You are an expert on the Roman Republic (509-27 BC). You have deep knowledge across all aspects: military, political, social, economic, diplomatic, religious, legal, literary, cultural, technological, agricultural, artistic, philosophical, scientific, geographic, and biographical.

Your task is to generate ONE claim for each of the 17 facets listed below. Each claim must:

1. Be SPECIFIC to the Roman Republic
2. Be HISTORICALLY ACCURATE
3. Include EVIDENCE (source reference)
4. Cite an AUTHORITY (if applicable): LCSH ID, LCC code, Wikidata QID, or scholarly source
5. Assign a CONFIDENCE score (0.0-1.0)

For each facet, return a JSON object with this structure:

{
  "facet": "Military",
  "claim_text": "The Roman legion's maniple formation, adopted during the Samnite Wars, provided tactical flexibility superior to the earlier phalanx system.",
  "evidence": {
    "source_type": "scholarly_consensus",
    "source_text": "The transition from phalanx to manipular legion occurred circa 315 BC, as documented in Livy's Ab Urbe Condita and confirmed by archaeological evidence from Samnite War battlefields.",
    "authority": {
      "type": "LCSH",
      "id": "sh85080392",
      "label": "Maniple (Military science)"
    }
  },
  "confidence": 0.92,
  "temporal": {
    "start_year": -315,
    "end_year": -107,
    "period": "Middle Republic"
  },
  "related_facets": ["Political", "Technological"]
}

CRITICAL RULES:
- Each claim must be DISTINCT and focused on its facet
- Do NOT repeat information across facets
- Evidence must be REAL (verifiable sources)
- Authorities must be REAL (valid LCSH/LCC/Wikidata IDs when provided)
- Communication facet should analyze HOW information was transmitted, not just WHAT

Generate 17 claims, one for each facet.
```

---

## **Expected Output Format**

### **Structure**

```json
{
  "subject": {
    "subject_id": "chrystallum:roman_republic",
    "label": "Roman Republic",
    "temporal": {
      "start_year": -509,
      "end_year": -27,
      "period_label": "Roman Republic"
    }
  },
  "claims": [
    {
      "claim_id": "auto-generated-uuid",
      "facet": "Military",
      "claim_text": "...",
      "evidence": { ... },
      "confidence": 0.92,
      "temporal": { ... },
      "related_facets": ["Political", "Technological"]
    },
    // ... 16 more claims
  ],
  "metadata": {
    "generated_by": "ChatGPT-4",
    "timestamp": "2026-02-15T12:00:00Z",
    "agent_version": "smoke_test_v1"
  }
}
```

---

## **Sample Claims (What We Expect)**

### **1. Military**
```json
{
  "facet": "Military",
  "claim_text": "The Roman legion's maniple formation, adopted during the Samnite Wars, provided tactical flexibility superior to the earlier phalanx system.",
  "evidence": {
    "source_type": "scholarly_consensus",
    "source_text": "Transition from phalanx to manipular legion circa 315 BC (Livy, Ab Urbe Condita; archaeological evidence).",
    "authority": {
      "type": "LCSH",
      "id": "sh85080392",
      "label": "Maniple (Military science)"
    }
  },
  "confidence": 0.92,
  "temporal": {
    "start_year": -315,
    "end_year": -107,
    "period": "Middle Republic"
  },
  "related_facets": ["Political", "Technological"]
}
```

### **2. Political**
```json
{
  "facet": "Political",
  "claim_text": "The Conflict of the Orders (494-287 BC) resulted in the plebeians gaining legal equality through the Lex Hortensia, which made plebiscites binding on all citizens.",
  "evidence": {
    "source_type": "primary_source",
    "source_text": "Livy, Ab Urbe Condita, Book 10; Cicero, De Re Publica.",
    "authority": {
      "type": "Wikidata",
      "qid": "Q741494",
      "label": "Conflict of the Orders"
    }
  },
  "confidence": 0.95,
  "temporal": {
    "start_year": -494,
    "end_year": -287,
    "period": "Early to Middle Republic"
  },
  "related_facets": ["Social", "Legal"]
}
```

### **3. Social**
```json
{
  "facet": "Social",
  "claim_text": "Roman society was stratified into patricians, plebeians, and slaves, with citizenship rights expanding through conquest and manumission.",
  "evidence": {
    "source_type": "scholarly_consensus",
    "source_text": "Social hierarchy documented across multiple sources (Livy, Polybius, Cicero); manumission practices confirmed by legal texts and inscriptions.",
    "authority": {
      "type": "LCSH",
      "id": "sh85123167",
      "label": "Social classes--Rome"
    }
  },
  "confidence": 0.90,
  "temporal": {
    "start_year": -509,
    "end_year": -27,
    "period": "Entire Republic"
  },
  "related_facets": ["Political", "Legal"]
}
```

### **17. Communication (Meta-Facet)**
```json
{
  "facet": "Communication",
  "claim_text": "Roman political discourse employed rhetorical strategies (ethos, pathos, logos) to persuade Senate and popular assemblies, with oral speech being the primary medium before widespread literacy.",
  "evidence": {
    "source_type": "primary_source",
    "source_text": "Cicero's speeches (In Catilinam, Pro Milone) exemplify rhetorical techniques; Quintilian's Institutio Oratoria codifies oratorical theory.",
    "authority": {
      "type": "LCC",
      "code": "PA6087",
      "label": "Latin language--Rhetoric"
    }
  },
  "confidence": 0.88,
  "temporal": {
    "start_year": -150,
    "end_year": -43,
    "period": "Late Republic"
  },
  "related_facets": ["Political", "Literary"],
  "communication_dimensions": {
    "medium": ["oral", "written"],
    "purpose": ["persuasion", "legitimation"],
    "audience": ["Senate", "Roman people"],
    "strategy": ["ethos", "pathos", "logos"]
  }
}
```

---

## **Validation Criteria**

### **Each Claim Must Have:**

✅ **Facet-Specific Content**
- Military ≠ Political ≠ Religious claims
- No overlap or repetition

✅ **Historical Accuracy**
- Verifiable facts
- Correct dates/periods
- Real sources cited

✅ **Evidence**
- Source type: primary_source, scholarly_consensus, archaeological, epigraphic
- Source text: Actual citation
- Authority (when applicable): Real LCSH/LCC/Wikidata ID

✅ **Confidence Score**
- Well-attested facts: 0.90-0.98
- Scholarly consensus: 0.80-0.89
- Debated topics: 0.60-0.79
- Speculative: 0.40-0.59

✅ **Temporal Scope**
- Start/end years
- Period label

✅ **Related Facets**
- List facets that overlap with this claim

---

## **Post-Generation Validation**

### **Automated Checks**

```python
def validate_smoke_test(claims_json):
    """
    Validate the 17 claims from the smoke test
    """
    issues = []
    
    # 1. Check count
    if len(claims_json['claims']) != 17:
        issues.append(f"Expected 17 claims, got {len(claims_json['claims'])}")
    
    # 2. Check facet coverage
    expected_facets = [
        "Military", "Political", "Social", "Economic", "Diplomatic",
        "Religious", "Legal", "Literary", "Cultural", "Technological",
        "Agricultural", "Artistic", "Philosophical", "Scientific",
        "Geographic", "Biographical", "Communication"
    ]
    
    found_facets = [c['facet'] for c in claims_json['claims']]
    missing = set(expected_facets) - set(found_facets)
    if missing:
        issues.append(f"Missing facets: {missing}")
    
    # 3. Check each claim structure
    for i, claim in enumerate(claims_json['claims']):
        claim_num = i + 1
        
        # Required fields
        required = ['facet', 'claim_text', 'evidence', 'confidence', 'temporal']
        for field in required:
            if field not in claim:
                issues.append(f"Claim {claim_num} ({claim.get('facet', 'unknown')}): Missing '{field}'")
        
        # Confidence range
        if 'confidence' in claim:
            conf = claim['confidence']
            if not (0.0 <= conf <= 1.0):
                issues.append(f"Claim {claim_num}: Invalid confidence {conf}")
        
        # Evidence structure
        if 'evidence' in claim:
            ev = claim['evidence']
            if 'source_type' not in ev or 'source_text' not in ev:
                issues.append(f"Claim {claim_num}: Incomplete evidence")
        
        # Temporal structure
        if 'temporal' in claim:
            temp = claim['temporal']
            if 'start_year' not in temp or 'end_year' not in temp:
                issues.append(f"Claim {claim_num}: Incomplete temporal data")
    
    # 4. Check for duplicate claim text
    claim_texts = [c['claim_text'] for c in claims_json['claims']]
    if len(claim_texts) != len(set(claim_texts)):
        issues.append("Duplicate claim texts detected")
    
    return issues

# Run validation
issues = validate_smoke_test(claims_data)
if issues:
    print("⚠️ VALIDATION ISSUES:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ All validations passed!")
```

---

## **Neo4j Ingestion Script**

```python
from neo4j import GraphDatabase
import json
from datetime import datetime
import uuid

def ingest_smoke_test_claims(claims_json, neo4j_uri, username, password):
    """
    Ingest the 17 smoke test claims into Neo4j
    """
    driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
    
    with driver.session() as session:
        # 1. Create/update SubjectConcept node
        subject = claims_json['subject']
        session.run("""
            MERGE (s:SubjectConcept {subject_id: $subject_id})
            SET s.label = $label,
                s.start_year = $start_year,
                s.end_year = $end_year,
                s.period_label = $period_label,
                s.last_updated = datetime()
        """, 
            subject_id=subject['subject_id'],
            label=subject['label'],
            start_year=subject['temporal']['start_year'],
            end_year=subject['temporal']['end_year'],
            period_label=subject['temporal']['period_label']
        )
        
        # 2. Create Facet nodes (if not exist)
        for claim in claims_json['claims']:
            session.run("""
                MERGE (f:Facet {name: $facet_name})
            """, facet_name=claim['facet'])
        
        # 3. Create Claim nodes and relationships
        for claim in claims_json['claims']:
            claim_id = str(uuid.uuid4())
            
            # Create Claim node
            session.run("""
                MERGE (s:SubjectConcept {subject_id: $subject_id})
                MERGE (f:Facet {name: $facet_name})
                CREATE (c:Claim {
                    claim_id: $claim_id,
                    text: $claim_text,
                    confidence: $confidence,
                    start_year: $start_year,
                    end_year: $end_year,
                    period: $period,
                    source_type: $source_type,
                    source_text: $source_text,
                    generated_by: $generated_by,
                    timestamp: datetime()
                })
                CREATE (s)-[:HAS_CLAIM]->(c)
                CREATE (c)-[:ABOUT_FACET]->(f)
            """,
                subject_id=subject['subject_id'],
                facet_name=claim['facet'],
                claim_id=claim_id,
                claim_text=claim['claim_text'],
                confidence=claim['confidence'],
                start_year=claim['temporal']['start_year'],
                end_year=claim['temporal']['end_year'],
                period=claim['temporal'].get('period', ''),
                source_type=claim['evidence']['source_type'],
                source_text=claim['evidence']['source_text'],
                generated_by=claims_json['metadata']['generated_by']
            )
            
            # Create Authority node (if present)
            if 'authority' in claim['evidence']:
                auth = claim['evidence']['authority']
                session.run("""
                    MATCH (c:Claim {claim_id: $claim_id})
                    MERGE (a:Authority {
                        type: $auth_type,
                        id: $auth_id,
                        label: $auth_label
                    })
                    CREATE (c)-[:CITES_AUTHORITY]->(a)
                """,
                    claim_id=claim_id,
                    auth_type=auth['type'],
                    auth_id=auth.get('id') or auth.get('qid') or auth.get('code'),
                    auth_label=auth['label']
                )
            
            # Create related facet relationships
            if 'related_facets' in claim:
                for related_facet in claim['related_facets']:
                    session.run("""
                        MATCH (c:Claim {claim_id: $claim_id})
                        MATCH (f:Facet {name: $related_facet})
                        CREATE (c)-[:RELATED_TO_FACET]->(f)
                    """,
                        claim_id=claim_id,
                        related_facet=related_facet
                    )
    
    driver.close()
    print(f"✅ Ingested {len(claims_json['claims'])} claims into Neo4j")

# Usage
with open('roman_republic_smoke_test.json', 'r') as f:
    claims_data = json.load(f)

ingest_smoke_test_claims(
    claims_data,
    neo4j_uri="bolt://localhost:7687",
    username="neo4j",
    password="your_password"
)
```

---

## **Success Metrics**

### **Quantitative**
- ✅ 17 claims generated (one per facet)
- ✅ All claims have required fields
- ✅ Confidence scores between 0.0-1.0
- ✅ No duplicate claim text
- ✅ All temporal data within Roman Republic range (-509 to -27)

### **Qualitative**
- ✅ Claims are factually accurate
- ✅ Claims are facet-specific (no overlap)
- ✅ Evidence is real and verifiable
- ✅ Authorities are valid (if provided)
- ✅ Communication facet demonstrates meta-layer understanding

---

## **Next Steps After Smoke Test**

### **If Successful:**
1. **Expand to more subjects** (Greek City-States, Caesar's Gallic War)
2. **Implement subagent spawning** (one agent per facet)
3. **Add agent collaboration** (agents share context)
4. **Build claim validation layer** (cross-check against authorities)

### **If Issues Found:**
1. **Refine prompts** for better facet differentiation
2. **Add examples** to guide claim structure
3. **Implement fallback** for missing authorities
4. **Improve temporal parsing** if date ranges are inaccurate

---

## **Files to Create**

1. **`chatgpt_prompt.txt`** - The system prompt for ChatGPT
2. **`roman_republic_smoke_test.json`** - Output from ChatGPT
3. **`validate_claims.py`** - Validation script
4. **`ingest_claims.py`** - Neo4j ingestion script

---

## **Running the Smoke Test**

### **Step 1: Generate Claims**
1. Copy the ChatGPT system prompt
2. Paste into ChatGPT
3. Request: "Generate all 17 claims as a single JSON object"
4. Save output as `roman_republic_smoke_test.json`

### **Step 2: Validate**
```bash
python validate_claims.py roman_republic_smoke_test.json
```

### **Step 3: Ingest to Neo4j**
```bash
python ingest_claims.py roman_republic_smoke_test.json
```

### **Step 4: Query in Neo4j**
```cypher
// See all claims
MATCH (s:SubjectConcept {label: "Roman Republic"})-[:HAS_CLAIM]->(c:Claim)
RETURN s, c

// See claims by facet
MATCH (c:Claim)-[:ABOUT_FACET]->(f:Facet)
RETURN f.name, COUNT(c) AS claim_count
ORDER BY f.name

// See Communication facet specifically
MATCH (c:Claim)-[:ABOUT_FACET]->(f:Facet {name: "Communication"})
RETURN c.text, c.confidence, c.source_text
```

---

**END OF SMOKE TEST SPECIFICATION**
