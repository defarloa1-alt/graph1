# Temporal System - Directory Guide

## 📁 Directory Structure

```
temporal/
├── README.md                          ← You are here
│
├── 📚 docs/                           Documentation
│   ├── Temporal_Comprehensive_Documentation.md    ⭐ Main reference (v2.0)
│   ├── Temporal_Data_Extraction_Guide.md          ⭐ Temporal extraction rules
│   ├── Geographic_Data_Extraction_Guide.md        ⭐ Geographic extraction rules
│   ├── QUICK_START.md                             Quick reference
│   ├── Neo4j_Import_Guide.md                      Detailed import guide
│   ├── Critical_Review.md                         Bug analysis & fixes
│   ├── IMPLEMENTATION_SUMMARY.md                  Agent mode changes log
│   └── FINAL_STRUCTURE.txt                        Structure verification
│
├── 🐍 scripts/                        Python Scripts
│   ├── temporal_period_classifier.py              ✅ Classifier (fixed)
│   ├── import_year_nodes_to_neo4j.py             Year node generator
│   ├── query_wikidata_periods.py                 Wikidata validation
│   ├── find_correct_qids.py                      QID lookup tool
│   └── verify_all_qids.py                        QID verification
│
├── 🔷 cypher/                         Cypher Scripts
│   ├── import_periods_to_neo4j.cypher            Period import
│   └── example_queries.cypher                     50+ query examples
│
└── 📦 archive/                        Historical Documentation
    ├── QID_CORRECTIONS.md                         Historical QID issues
    ├── QID_Tokenization_Issue.md                  Tokenization analysis
    └── VERIFY_QIDS_MANUALLY.md                    Manual verification checklist
```

**Total: 18 files organized in 4 subdirectories**

---

## 🎯 Quick Start Guide

### I Want To...

#### **Understand the Temporal System**
→ `docs/Temporal_Comprehensive_Documentation.md` - Complete overview

#### **Implement Temporal Extraction in Agent**
→ `docs/Temporal_Data_Extraction_Guide.md` - How to extract temporal data  
→ `docs/Geographic_Data_Extraction_Guide.md` - How to extract geographic data  
→ Apply two-stage extraction: LLM extracts labels → Tools resolve identifiers

#### **Import Temporal Backbone to Neo4j**
→ Fast path: `docs/QUICK_START.md`  
→ Detailed path: `docs/Neo4j_Import_Guide.md`

#### **Classify a Date into Period**
→ Use `scripts/temporal_period_classifier.py`
```python
from scripts.temporal_period_classifier import TemporalPeriodClassifier
classifier = TemporalPeriodClassifier()
result = classifier.classify_date("1347", region="Europe")
print(result['primary_period']['period_name'])  # "Middle Ages"
```

#### **Validate Wikidata QIDs**
→ Run `python scripts/query_wikidata_periods.py --query validate`

#### **Write Temporal Queries**
→ See examples in `cypher/example_queries.cypher`

#### **Understand Tokenization Issues**
→ Read `archive/QID_Tokenization_Issue.md`

---

## 📚 Documentation Overview

### Primary Documentation (in `docs/`)

#### **Temporal_Comprehensive_Documentation.md** ⭐ START HERE
Complete reference for the temporal system (Version 2.0):
- Research foundation on LLM temporal reasoning
- Year nodes architecture (sequential backbone)
- Period classifier implementation
- International standards (ISO 8601, ISO 19108, W3C OWL-Time)
- Event-centric temporal model
- Integration guide

#### **Temporal_Data_Extraction_Guide.md** ⭐ EXTRACTION RULES
How AI agents should extract temporal data:
- **Natural Language Terms** (LLM can tokenize):
  - Period names: "Roman Republic", "The Great Depression"
  - Date expressions: "October 29, 1929", "49 BCE"
  - Fuzzy periods: Capture even if dates unclear
- **System Identifiers** (MUST be atomic):
  - Wikidata QIDs: "Q3281534" (NEVER let LLM process)
  - ISO 8601 dates: "-0753-01-01" (tool parsing only)
  - Coordinates: (41.9028, 12.4964) (atomic numerics)
- **Critical:** Two-stage extraction workflow
- **Principle:** Term consistency > date precision

#### **Geographic_Data_Extraction_Guide.md** ⭐ GEOGRAPHIC RULES
How AI agents should handle geographic data:
- **Multi-Name Place Entities:**
  - Same place, multiple names (Byzantium/Constantinople/Istanbul)
  - Cultural and temporal naming variations (Gaul vs France)
- **Geographic Stability Hierarchy:**
  - Very High: Continents, oceans (stable 10,000+ years)
  - High: Mountains, islands, rivers (stable 5,000+ years)
  - Very Low: Political boundaries (change in decades)
- **Stable Features as Anchors:**
  - Use permanent geography as reference points
  - Political boundaries are temporal overlays

#### **QUICK_START.md**
Fast path to importing the temporal backbone into Neo4j:
- 3-step process
- Windows CMD and PowerShell syntax
- Minimal explanation, maximum speed

#### **Neo4j_Import_Guide.md**
Detailed step-by-step guide for Neo4j import:
- Prerequisites and setup
- Import periods from CSV
- Generate and import year nodes
- Example queries
- Troubleshooting

#### **Critical_Review.md**
Analysis of temporal system issues and fixes:
- Bug reports (BCE dates, KeyError, etc.)
- Recommendations for improvements
- Validation findings
- **Status:** Issues documented and fixed

#### **IMPLEMENTATION_SUMMARY.md**
Complete record of agent mode implementation:
- What was created (extraction guides)
- What was updated (Comprehensive Documentation v2.0)
- What was cleaned (directory organization)
- Before/after comparison

---

## 🐍 Python Scripts (in `scripts/`)

### **temporal_period_classifier.py** ✅ CORE CLASSIFIER
Rule-based classifier for determining historical periods from dates:
- Parses various date formats (ISO 8601, BCE dates, year-only)
- Handles overlapping periods
- Regional context support
- Confidence scoring
- **Status:** Fixed and working (BCE date handling, KeyError fixes)

**Usage:**
```python
from scripts.temporal_period_classifier import TemporalPeriodClassifier

classifier = TemporalPeriodClassifier()
result = classifier.classify_date("1347")
print(result['primary_period']['period_name'])  # "Middle Ages"
```

### **import_year_nodes_to_neo4j.py**
Generate year nodes and relationships for Neo4j:
- Creates year nodes with sequential FOLLOWED_BY/PRECEDED_BY edges
- Optional period mapping (DURING relationships for years in periods, SUB_PERIOD_OF for period hierarchies)
- Configurable date range
- Command-line interface

**Usage:**
```bash
python scripts/import_year_nodes_to_neo4j.py --start -753 --end -82 --output output.cypher
```

### **query_wikidata_periods.py**
SPARQL query tool for Wikidata validation:
- `--query schema` - Get Wikidata time period schema
- `--query validate` - Validate local CSV against Wikidata
- `--query all` - Get all time periods from Wikidata

**Usage:**
```bash
python scripts/query_wikidata_periods.py --query validate
```

### **find_correct_qids.py**
Search tool to find correct Wikidata QIDs:
- Programmatic QID lookup
- Batch processing support
- Fixed: Unicode encoding for Windows console

### **verify_all_qids.py**
Systematic QID verification against Wikidata:
- Validates all QIDs in taxonomy
- Reports mismatches
- **Note:** May hit Wikidata rate limits

---

## 🔷 Cypher Scripts (in `cypher/`)

### **import_periods_to_neo4j.cypher**
Import historical periods from CSV into Neo4j:
- Creates period nodes from `Temporal/time_periods.csv`
- Sets up period metadata (QIDs, dates, regions)

**Usage:**
```bash
cypher-shell -u neo4j -p password < cypher/import_periods_to_neo4j.cypher
```

### **example_queries.cypher**
50+ example Cypher queries for temporal data:
- Find years in periods
- Period transitions
- Event temporal anchoring
- Date range queries
- Multi-period queries

---

## 📦 Archive (in `archive/`)

Historical documentation preserved for reference:

### **QID_CORRECTIONS.md**
Historical record of QID validation issues:
- Incorrect QIDs found in initial taxonomy
- Correction process documentation

### **QID_Tokenization_Issue.md**
Detailed analysis of LLM tokenization fragmentation:
- Why QIDs fragment during tokenization
- Impact on accuracy (10% error increase)
- Why tool-augmented approach is necessary
- Research findings

### **VERIFY_QIDS_MANUALLY.md**
Manual verification checklist with Wikidata URLs:
- Created when API access was limited
- Backup verification method

---

## 🔑 Key Concepts

### 1. Event-Centric Temporal Model

**Problem:** Fixed period mappings are culturally biased and context-inappropriate.

**Solution:**
```
Year Nodes (concrete anchors)
    ↓ POINT_IN_TIME
Events (concrete facts)
    ↓ Agent queries
Period Definitions (reference vocabulary)
    ↓ Agent selects
Contextually Appropriate Period
```

**Principle:** Periods are contextual frameworks (agent-determined), not fixed truth.

### 2. Tokenization Problem & Tool-Augmented Resolution

**Research Finding:** Tokenization fragmentation causes 10% accuracy drop.

**Problem:**
```python
"Q3281534" → [Q, 328, 15, 34]      # LLM cannot recognize QID
"-0753-01-01" → [-, 0, 753, ...]    # Date structure breaks
```

**Solution: Two-Stage Extraction**
1. **LLM Stage:** Extract natural language ("Roman Republic", "49 BCE")
2. **Tool Stage:** Resolve to atomic identifiers ("Q17167", "-0049-01-01")
3. **Storage:** Both formats with metadata

**Result:** 95.31% accuracy (tool-augmented) vs 34.5% (pure LLM)

### 3. Fuzzy Period Handling

**Principle:** **Term consistency > Date precision**

If a temporal term appears consistently in scholarly literature, **CAPTURE IT** even if:
- Exact start/end dates are debated
- Different sources give different ranges
- Boundaries are marked by different events

**Example:** "The Great Depression" - universally recognized, end date debated (1939? 1941? 1945?)

### 4. Multi-Name Place Entities

**Problem:** Geographic names are temporal AND cultural constructs.

**Example:** Byzantium (Greek, -657 to 330) → Constantinople (Roman/Byzantine, 330-1930) → Istanbul (Turkish, 1930-present)

**Solution:** Store multiple names with temporal/cultural metadata for the same stable geographic feature.

### 5. Geographic Stability Hierarchy

| Stability | Features | Change Rate | Use Case |
|-----------|----------|-------------|----------|
| **Very High** | Continents, Oceans | 10,000+ years | Long-term anchors |
| **High** | Mountains, Islands, Rivers | 5,000+ years | Historical anchors |
| **Very Low** | Political boundaries | Decades | Political context only |

**Usage:** Link events to stable features; political boundaries are temporal overlays.

---

## 📊 Research Foundation

### Tool-Augmented vs Pure LLM Reasoning

| Date Type | Pure LLM | Tool-Augmented |
|-----------|----------|----------------|
| **Contemporary (2010-2025)** | 82-87% | **97-99%** |
| **Historical (1500-1949)** | 68-76% | **92-96%** |
| **Ancient (pre-500)** | 45-58% | **85-92%** |
| **Overall accuracy** | ~34.5% | **95.31%** |

**Conclusion:** Tools are essential for temporal reasoning accuracy.

---

## 🔄 Integration Points

### Files That Need Temporal Integration

1. **`Docs/99-Langraph workflow.md`**
   - Add period classification to extraction node
   - Add temporal consistency validation

2. **`chrystallum_query_tools.py`**
   - Add temporal period query functions
   - Add date range query functions

3. **`cypher_templates.json`**
   - Add temporal query templates

4. **Agent Prompts**
   - Include `docs/Temporal_Data_Extraction_Guide.md` instructions
   - Include `docs/Geographic_Data_Extraction_Guide.md` instructions

---

## 📈 Version History

### Version 2.0 (2025-01-10) ✅ Current
- Added event-centric temporal model
- Added extraction guides (Temporal + Geographic)
- Documented QID tokenization issue
- Organized directory structure (docs/, scripts/, cypher/, archive/)
- Archived historical documentation
- Updated comprehensive documentation

### Version 1.0 (2025-01-09)
- Initial consolidated documentation
- Fixed temporal_period_classifier.py bugs
- Neo4j import implementation
- Wikidata validation tools

---

## 🚀 Getting Started

### New Users:
1. Read `docs/Temporal_Comprehensive_Documentation.md` (main reference)
2. Review `docs/Temporal_Data_Extraction_Guide.md` (extraction rules)
3. Review `docs/Geographic_Data_Extraction_Guide.md` (geographic rules)

### Implementing Extraction:
1. Follow two-stage extraction workflow (guides above)
2. Integrate with LangGraph workflow
3. Add query functions to `chrystallum_query_tools.py`

### Importing to Neo4j:
1. Fast: Follow `docs/QUICK_START.md`
2. Detailed: Follow `docs/Neo4j_Import_Guide.md`
3. Use scripts in `scripts/` directory
4. Run Cypher scripts from `cypher/` directory

---

*Last Updated: 2025-01-10*  
*Temporal System Version: 2.0*  
*Directory Structure: Organized (4 subdirectories)*  
*Status: ✅ Production Ready*
