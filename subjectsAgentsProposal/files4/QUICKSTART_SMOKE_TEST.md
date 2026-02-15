# Roman Republic Agent Smoke Test - Quick Start Guide

**Purpose**: Test single ChatGPT agent generating 17 claims (one per facet) for Roman Republic

---

## **Step-by-Step Instructions**

### **Step 1: Generate Claims with ChatGPT**

1. Open ChatGPT (GPT-4 recommended)

2. Copy the entire contents of `chatgpt_prompt_roman_republic.txt`

3. Paste into ChatGPT and press Enter

4. ChatGPT will generate a JSON object with 17 claims

5. Copy the entire JSON output

6. Save as `roman_republic_smoke_test.json`

**Expected output format:**
```json
{
  "subject": { ... },
  "claims": [
    { "facet": "Military", ... },
    { "facet": "Political", ... },
    ... 15 more claims ...
  ],
  "metadata": { ... }
}
```

---

### **Step 2: Validate Claims**

Run the validation script:

```bash
python validate_claims.py roman_republic_smoke_test.json
```

**What it checks:**
- ✅ All 17 facets covered (no duplicates or missing)
- ✅ Required fields present (facet, claim_text, evidence, confidence, temporal)
- ✅ Confidence scores between 0.0-1.0
- ✅ Temporal dates within Roman Republic range (-509 to -27)
- ✅ No duplicate claim text
- ✅ Evidence structure complete

**Expected output:**
```
======================================================================
SMOKE TEST VALIDATION REPORT
======================================================================

📊 STATISTICS:
  Subject: Roman Republic
  Total claims: 17
  Expected: 17

📋 FACETS COVERED:
  ✅ Agricultural: 1 claim(s)
  ✅ Artistic: 1 claim(s)
  ✅ Biographical: 1 claim(s)
  ... (all 17 facets)

📈 CONFIDENCE SCORES:
  Average: 0.87
  Range: 0.75 - 0.95

📚 AUTHORITY CITATIONS:
  Claims with authorities: 14/17

🔍 VALIDATION ISSUES:
  ✅ No issues found! All validations passed.

======================================================================
🎉 RESULT: ✅ PASSED - Ready for ingestion!
======================================================================
```

---

### **Step 3: Ingest into Neo4j**

Run the ingestion script:

```bash
python ingest_claims.py roman_republic_smoke_test.json
```

**What you'll be prompted for:**
```
Neo4j password: [enter your Neo4j password]
```

**What it does:**
1. Creates/updates `SubjectConcept` node for Roman Republic
2. Creates 17 `Facet` nodes (Military, Political, etc.)
3. Creates 17 `Claim` nodes
4. Creates `Authority` nodes (for claims with authorities)
5. Links claims to facets with relationships
6. Creates inter-facet relationships

**Expected output:**
```
🔄 Connecting to Neo4j at bolt://localhost:7687...
🔄 Ingesting claims from roman_republic_smoke_test.json...
✅ Created SubjectConcept: chrystallum:roman_republic
✅ Created 17 Facet nodes
✅ Ingested 17 claims
✅ Created inter-facet relationships

======================================================================
NEO4J INGESTION SUMMARY
======================================================================

📊 DATABASE STATISTICS:
  Subject: Roman Republic
  Claims: 17
  Facets: 17
  Authorities: 14

======================================================================

✅ Ingestion complete!
```

---

### **Step 4: Query in Neo4j**

Open Neo4j Browser and run queries:

#### **View all claims:**
```cypher
MATCH (s:SubjectConcept {label: "Roman Republic"})-[:HAS_CLAIM]->(c:Claim)
RETURN s, c
LIMIT 50
```

#### **See claims by facet:**
```cypher
MATCH (c:Claim)-[:ABOUT_FACET]->(f:Facet)
RETURN f.name AS facet, COUNT(c) AS claim_count
ORDER BY f.name
```

#### **View Communication facet specifically:**
```cypher
MATCH (c:Claim)-[:ABOUT_FACET]->(f:Facet {name: "Communication"})
RETURN c.text, c.confidence, c.source_text
```

#### **See claims with authorities:**
```cypher
MATCH (c:Claim)-[:CITES_AUTHORITY]->(a:Authority)
RETURN c.text AS claim, a.type AS auth_type, a.label AS authority
LIMIT 20
```

#### **Find related facets:**
```cypher
MATCH (c:Claim)-[:ABOUT_FACET]->(f1:Facet)
MATCH (c)-[:RELATED_TO_FACET]->(f2:Facet)
RETURN f1.name AS primary_facet, 
       COLLECT(DISTINCT f2.name) AS related_facets
ORDER BY f1.name
```

#### **View the full graph:**
```cypher
MATCH (s:SubjectConcept)-[:HAS_CLAIM]->(c:Claim)-[:ABOUT_FACET]->(f:Facet)
OPTIONAL MATCH (c)-[:CITES_AUTHORITY]->(a:Authority)
RETURN s, c, f, a
LIMIT 100
```

---

## **Troubleshooting**

### **Issue: ChatGPT doesn't return valid JSON**

**Solution:**
- Ask ChatGPT: "Please return ONLY the JSON, no explanation"
- Copy from the first `{` to the last `}`
- Use a JSON validator (jsonlint.com) to check format

### **Issue: Validation fails**

**Common problems:**
- Missing facets → Ask ChatGPT to regenerate missing facets
- Invalid dates → Check that years are negative for BC (e.g., -264)
- Low confidence → Review claims, may need better evidence

**Fix:**
1. Edit the JSON file directly to fix issues
2. Re-run validation
3. Once passing, proceed to ingestion

### **Issue: Neo4j connection fails**

**Check:**
- Neo4j is running (`systemctl status neo4j` or check Desktop app)
- Correct URI (default: `bolt://localhost:7687`)
- Correct username/password
- Try connecting with Neo4j Browser first

### **Issue: Claims already exist**

**Note:** The ingestion script uses `MERGE` for SubjectConcept and Facets, but `CREATE` for Claims. Re-running will create duplicate claims.

**To reset:**
```cypher
// Delete all claims for Roman Republic
MATCH (s:SubjectConcept {subject_id: "chrystallum:roman_republic"})-[:HAS_CLAIM]->(c:Claim)
DETACH DELETE c
```

---

## **Success Criteria**

### **You know it worked when:**

✅ ChatGPT generates 17 distinct claims  
✅ Validation passes with no critical errors  
✅ Ingestion completes successfully  
✅ Neo4j shows 17 claims linked to 17 facets  
✅ Claims have evidence and authorities  
✅ Graph visualization shows SubjectConcept → Claims → Facets  

---

## **Next Steps After Successful Smoke Test**

1. **Review claim quality** - Are they historically accurate?
2. **Test with different subjects** - Try "Caesar's Gallic War"
3. **Implement subagent spawning** - Create separate agents per facet
4. **Add validation layer** - Cross-check claims against authorities
5. **Build UI** - Visualize claims and facets

---

## **Files Reference**

| File | Purpose |
|------|---------|
| `chatgpt_prompt_roman_republic.txt` | Prompt for ChatGPT |
| `roman_republic_smoke_test.json` | Generated claims (you create this) |
| `validate_claims.py` | Validation script |
| `ingest_claims.py` | Neo4j ingestion script |
| `SMOKE_TEST_ROMAN_REPUBLIC_AGENT.md` | Full specification |

---

## **Quick Commands Summary**

```bash
# 1. Generate (do this in ChatGPT, save output)

# 2. Validate
python validate_claims.py roman_republic_smoke_test.json

# 3. Ingest
python ingest_claims.py roman_republic_smoke_test.json

# 4. Query (in Neo4j Browser)
MATCH (s:SubjectConcept)-[:HAS_CLAIM]->(c:Claim)-[:ABOUT_FACET]->(f:Facet)
RETURN s, c, f
```

---

**Need help?** Check `SMOKE_TEST_ROMAN_REPUBLIC_AGENT.md` for full details.
