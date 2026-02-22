# Chrystallum Index Mining Phase 2.5: Launch Guide

**Status:** Ready to Begin  
**Date:** February 15, 2026  
**Target:** 50+ scholarly works with indexes extracted

---

## What is Index Mining?

**Core Hypothesis:** Book indexes are pre-curated knowledge graphs with curator-validated relationships.

**Why indexes are gold:**
- ✅ Controlled vocabulary (entries are expert-selected)
- ✅ Hierarchical structure (main entries + sub-entries map to facets)
- ✅ Relationship indicators ("See also" cross-references)
- ✅ Density signals (page counts indicate importance)
- ✅ Higher confidence than Wikipedia backlinks (human curator vs LLM inference)

**Scale:** Index from scholarly works → Claims at 0.90+ posterior probability

---

## Phase 2.5 Workflow

### Stage 1: Book Discovery & Scoring (Week 1)

**Agent Task:** Query library catalogs + score by 7-indicator algorithm

**7-Indicator Scoring:**
1. Publication date (recent = better indexes)
2. Book length (400+ pages = comprehensive)
3. Publisher prestige (academic press = reliable)
4. Index mention in metadata (explicit "includes index")
5. Subject heading relevance (history + genealogy focus)
6. Full-text availability (OCR quality checkable)
7. Citation count (widely referenced = canonical)

**Library Catalogs to Query:**
- Internet Archive (open source)
- HathiTrust (5M+ digitized works)
- Library of Congress API
- VIAF (Virtual International Authority File)
- WorldCat (450M+ library records)

**Expected Output:**
```
Top 5 Books Ranked by Index Quality Score:

1. Smith, J. (2015). "Roman Political Structure" - Score: 0.95
   ├─ Publisher: Oxford University Press
   ├─ Pages: 512 (comprehensive)
   ├─ Full text: Available
   ├─ Index entries: 2,347 (estimated)
   └─ Rationale: Recent, prestigious, extensive index

2. Jones, M. (2008). "Genealogy of Caesar's Circle" - Score: 0.87
   ├─ Publisher: Cambridge
   ├─ Pages: 384
   ├─ Index entries: 1,856
   └─ Rationale: Genealogy focus, academic press

3. Williams, K. (2019). "Mediterranean Trade Routes" - Score: 0.78
   ├─ Publisher: Routledge
   ├─ Pages: 296
   └─ Rationale: Good coverage, slightly shorter
```

### Stage 2: Index Extraction (Week 2-3)

**Process:**
1. Download PDF or full text from Internet Archive
2. Extract index section (OCR if necessary)
3. Parse structure: Main entry → Sub-entries → Page numbers
4. Entity resolution: Match entries to Wikidata QIDs
5. Generate claims with temporal + facet context

**OCR Quality Check:**
- Sample 100 index entries
- If recognition >95%: Proceed to full extraction
- If <95%: Manual review or skip book

**Expected Output:**
```
book_id: "smith_2015_romanhpsr"
extracted_index_entries: [
  {
    "main_entry": "Caesar, Julius",
    "qid": "Q1048",
    "sub_entries": [
      "Civil War role",
      "Political alliances",
      "Death and succession"
    ],
    "page_numbers": [45, 67, 89, 234, 456],
    "density": 0.18,  // 5 occurrences / 512 pages
    "confidence": 0.92
  }
]
```

### Stage 3: Claim Generation (Week 3-4)

**Methodology:**
1. Map index entries to SubjectConcept facets
2. Use page ranges as importance/confidence signals
3. Cross-reference with existing Neo4j claims (dedup + posterior merge)
4. Flag contradictions for historian review
5. Generate proposal files (JSON + Markdown)

**Claim Generation Example:**

**From Index:**
```
Caesar, Julius
  ├─ Birth and family background (18-20)
  ├─ Military campaigns (45, 67, 89)
  ├─ Political rise (123-156)
  ├─ Civil War leadership (234-267)
  └─ Death (456-458)
```

**Generated Claims:**
```
1. Caesar-MILITARY_CAMPAIGN-Gaul
   Facet: military
   Confidence: 0.93 (indexed across 45, 67, 89 = triple mention)
   Posterior: 0.94 (Wikidata + Index consensus)

2. Caesar-POLITICAL_RISE-Roman_Republic
   Facet: political
   Confidence: 0.89 (indexed pages 123-156)
   Posterior: 0.91

3. Caesar-CIVIL_WAR_LEADERSHIP-Roman_Civil_War
   Facet: military + political
   Confidence: 0.95 (pages 234-267 = 34 pages coverage)
   Posterior: 0.96
```

### Stage 4: Validation & Promotion (Week 4)

**Human Review Gate:**
- Review conflicts (index vs Wikidata disagreements)
- Verify OCR accuracy on sampled entries
- Approve/reject claims
- Mark facet confidence baselines

**Promotion Criteria:**
- Posterior ≥ 0.90 → Auto-promote to Neo4j
- 0.80-0.90 → Historian review required
- <0.80 → Flag for secondary sources

**Expected Outcome:**
- 50+ books → ~5,000-10,000 extracted index entries
- ~2,000-4,000 generated claims (after dedup)
- ~1,500-2,500 promoted claims (posterior ≥ 0.90)
- Enrichment gain: +150-250% over Wikipedia backlinks alone

---

## Immediate Actions (Today - Feb 15)

### Step 1: ChatGPT Agent Live
**Now:** Upload agent to ChatGPT
- System prompt: [md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md](md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md) (531 lines, 1.3k tokens)
- Upload files: Use [md/Agents/CHATGPT_QUICK_UPLOAD_CHECKLIST.md](md/Agents/CHATGPT_QUICK_UPLOAD_CHECKLIST.md)
- Test: Run sample query on Neo4j

**Expected:** Agent can query Year nodes, Facets, SubjectConcepts live

### Step 2: Begin Book Discovery
**Command to agent:**
```
Propose ingestion Q17167 depth=8 mode=discovery_phase_2_5
```

**Agent will:**
1. Query Internet Archive API for history books
2. Score by 7-indicator algorithm
3. Generate ranked list (top 50 candidates)
4. Output: `proposals/book_discovery_candidates_20260215.json`

### Step 3: Select Pilot Books
**Team selects top 5-7 books from agent's ranked list**

Criteria:
- Full text available (OCR testable)
- English language (easier OCR)
- 300-600 pages (comprehensive but manageable)
- Index explicitly mentioned in metadata
- Published 2000+ (modern indexing standards)

---

## Files Ready Today

**Agent System Prompt:**
- [md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md](md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md)

**ChatGPT Upload Guides:**
- [md/Agents/CHATGPT_QUICK_UPLOAD_CHECKLIST.md](md/Agents/CHATGPT_QUICK_UPLOAD_CHECKLIST.md)
- [md/Agents/CHATGPT_UPLOAD_PACKAGE.md](md/Agents/CHATGPT_UPLOAD_PACKAGE.md)

**Neo4j Setup:**
- [Neo4j/schema/01_schema_constraints_neo5_compatible.cypher](Neo4j/schema/01_schema_constraints_neo5_compatible.cypher)
- [Neo4j/schema/02_schema_indexes.cypher](Neo4j/schema/02_schema_indexes.cypher)
- [Neo4j/schema/03_schema_initialization_simple.cypher](Neo4j/schema/03_schema_initialization_simple.cypher)

**Ready Status:**
- ✅ Neo4j: 97 constraints, 150 indexes ONLINE
- ✅ Agent prompt: 8k token limit, proposal-based learning
- ✅ ChatGPT: Files prepared for upload
- ✅ Phase 2.5: Book discovery workflow designed

---

## Timeline

**Week of Feb 15:**
- Feb 15: ChatGPT agent live, book discovery begins ← **TODAY**
- Feb 16-17: Agent scores books, top 50 ranked
- Feb 18: Team selects pilot 5-7 books

**Week 1.5 (Feb 19-22):**
- Feb 19: Deploy Layer 2.5 hierarchy schema (if index mining parallel)
- Feb 20-22: Index extraction from pilot books (manual + OCR)

**Week 2.5 (Feb 24-Mar 3):**
- Manual index entry verification
- OCR quality assessment
- Claim generation from extracted indexes

**Week 3.5 (Mar 3-10):**
- Historian review of generated claims
- Posterior probability finalization
- Promotion to Neo4j

**Expected Outcome by Mar 15:**
- 5-7 books fully indexed
- 1,500-2,500 claims promoted
- +200% enrichment over Wikipedia backlinks
- Confidence baseline established for scaling

---

## Success Metrics

**Phase 2.5 Completion:**
- ✅ 5+ books selected with full-text available
- ✅ Index OCR quality >95% on sampled entries
- ✅ 500+ claims generated per book
- ✅ 80%+ promotion rate (posterior ≥ 0.90)
- ✅ Zero conflicts with existing Wikidata claims
- ✅ 3+ new facets enriched per book

**Decision Point (Mar 15):**
- If success → Scale to 50+ books (Apr-May)
- If challenges → Refine methodology, extend timeline

---

## Questions for Team

1. Which 5-7 books do you want to pilot with?
2. Manual index extraction (PDF + OCR) or AI-assisted?
3. Should we weight genealogical/military facts differently in scoring?
4. Acceptable OCR error rate before re-scanning?
5. Timeline flexibility: Can we extend 1-2 weeks if needed?

---

**Status:** Ready to launch index mining Phase 2.5 ✅
**Next action:** Deploy ChatGPT agent today
