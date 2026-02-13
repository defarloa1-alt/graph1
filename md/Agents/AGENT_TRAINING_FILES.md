# ChatGPT Agent Training Files

**Purpose:** Files to upload to ChatGPT custom agent for Chrystallum Temporal Graph Framework  
**Date:** December 12, 2025  
**Total Recommended:** 25-30 core files

---

## ðŸ“‹ Priority 1: Core Documentation (MUST UPLOAD)

### Temporal System Documentation
1. âœ… `temporal/README.md` - Complete temporal system guide
2. âœ… `temporal/docs/Temporal_Comprehensive_Documentation.md` - Main reference (v2.0)
3. âœ… `temporal/docs/QUICK_START.md` - Fast import guide
4. âœ… `temporal/docs/Neo4j_Import_Guide.md` - Detailed import instructions
5. âœ… `temporal/docs/QUICK_REFERENCE.md` - Quick command reference

### Architecture Documentation
6. âœ… `Docs/Chrystallum_Architecture_Analysis.md` - ESB vs KG analysis
7. âœ… `Docs/Neo4j_Quick_Start.md` - Neo4j basics

### Relationship Types
8. âœ… `relations/README.md` - Relationship types guide
9. âœ… `Relationships/relationship_types_registry_master.csv` - 236 canonical relationships

### Scripts Guide
10. âœ… `Docs/guides/SCRIPTS_AND_FILES_GUIDE.md` - Complete scripts reference

---

## ðŸ“‹ Priority 2: Implementation Files (HIGHLY RECOMMENDED)

### Python Script Examples
11. âœ… `temporal/scripts/temporal_period_classifier.py` - Period classifier implementation
12. âœ… `temporal/scripts/query_wikidata_periods.py` - Wikidata integration

### Cypher Query Examples
13. âœ… `temporal/cypher/example_queries.cypher` - 50+ query examples (if restored)
14. âœ… `temporal/cypher/import_periods_to_neo4j.cypher` - Period import script (if restored)

### CSV Data Schemas
15. âœ… `Temporal/time_periods.csv` - Period definitions
16. âœ… `temporal/scripts/taxonomy_summary_report.csv` - Period summary (if exists)

### Batch File Examples
17. âœ… `temporal/scripts/README_BATCH_FILES.md` - Batch file guide (if exists)

---

## ðŸ“‹ Priority 3: Advanced Topics (RECOMMENDED)

### Geographic System (if completed)
18. âš ï¸ `temporal/Geo/README.md` - Geographic system guide
19. âš ï¸ `temporal/Geo/PERIOD_PLACE_MAPPING_ANALYSIS.md` - Period-place analysis

### Troubleshooting
20. âœ… `CLEAR_NEO4J_DATA_GUIDE.md` - How to clear/reset Neo4j data

### Additional Architecture
21. âœ… `Docs/Citation_and_Prose_Architecture.md` - Citation handling
22. âœ… `Docs/Property_Extensions_Implementation_Guide.md` - Property extensions

### Examples
23. âœ… `Docs/examples/Caesar_Rubicon_Example.md` - Complete worked example
24. âœ… `Docs/examples/India_Cotton_Trade_Extraction.md` - Extraction example

---

## ðŸ“‹ Priority 4: Reference Materials (OPTIONAL)

### Historical Context
25. âš ï¸ `Docs/Kingdom_to_Sulla_Scope.md` - Test data scope (753 BCE - 82 BCE)

### Archived Decisions
26. âš ï¸ `temporal/archive/decisions/Year_Backbone_vs_Alternatives_Analysis.md` - Design decisions
27. âš ï¸ `temporal/archive/QID_CORRECTIONS.md` - QID validation history
28. âš ï¸ `temporal/archive/QID_Tokenization_Issue.md` - Tokenization research

### CIDOC-CRM Integration
29. âš ï¸ `arch/Cidoc/CIDOC-CRM_vs_Chrystallum_Comparison.md` - CIDOC-CRM alignment

### Action Structure
30. âš ï¸ `relations/Action_Structure_With_Wikidata_Example.md` - Action structure implementation

---

## ðŸ“¦ How to Organize Upload

### Option A: Upload as Individual Files (Recommended)
- ChatGPT can index individual files better
- Easier to update specific files later
- Upload **Priority 1** (10 files) first
- Then add **Priority 2** (7 files)
- Add others as needed

### Option B: Create Knowledge Packages
If file limit is an issue, combine into packages:

**Package 1: Getting Started** (combine into one file)
- temporal/README.md
- temporal/docs/QUICK_START.md
- Docs/Neo4j_Quick_Start.md

**Package 2: Implementation Guide** (combine into one file)
- temporal/docs/Temporal_Comprehensive_Documentation.md
- Docs/guides/SCRIPTS_AND_FILES_GUIDE.md
- temporal/docs/Neo4j_Import_Guide.md

**Package 3: Reference Data** (combine into one CSV)
- Temporal/time_periods.csv
- Relationships/relationship_types_registry_master.csv

**Package 4: Query Examples** (combine into one file)
- temporal/cypher/example_queries.cypher
- Custom query examples you create

---

## ðŸŽ¯ Minimum Viable Agent

**If you can only upload 10 files, use these:**

1. `CHATGPT_AGENT_PROMPT.md` â† **The agent instructions (priority #1)**
2. `temporal/README.md`
3. `temporal/docs/Temporal_Comprehensive_Documentation.md`
4. `temporal/docs/QUICK_START.md`
5. `relations/README.md`
6. `Relationships/relationship_types_registry_master.csv`
7. `Docs/Chrystallum_Architecture_Analysis.md`
8. `Docs/guides/SCRIPTS_AND_FILES_GUIDE.md`
9. `Temporal/time_periods.csv`
10. `Docs/examples/Caesar_Rubicon_Example.md`

---

## âœ… Files Currently Available

Based on the recent context, these files definitely exist and are ready:

### Documentation
- âœ… `temporal/README.md` (391 lines)
- âœ… `temporal/docs/QUICK_START.md` (207 lines)
- âœ… `temporal/docs/IMPLEMENTATION_SUMMARY.md` (454 lines)
- âœ… `temporal/docs/Temporal_Data_Extraction_Guide.md` (693 lines)
- âœ… `Docs/Chrystallum_Architecture_Analysis.md` (442 lines)
- âœ… `Docs/Neo4j_Quick_Start.md` (113 lines)
- âœ… `Docs/guides/SCRIPTS_AND_FILES_GUIDE.md` (1338+ lines)
- âœ… `relations/README.md` (330+ lines)
- âœ… `CLEAR_NEO4J_DATA_GUIDE.md` (174 lines)

### Data Files
- âœ… `Temporal/time_periods.csv` (87 lines)
- âœ… `Relationships/relationship_types_registry_master.csv`
- âœ… `cypher_template_library.json` (86 lines)

### Scripts
- âœ… `temporal/scripts/temporal_period_classifier.py`
- âœ… `temporal/scripts/query_wikidata_periods.py`
- âœ… `temporal/scripts/generate_taxonomy_report.py` (239 lines)

---

## âš ï¸ Files That Were Deleted (Need Restoration)

These were recently deleted and may need to be restored if important:

### Temporal Scripts (if needed for examples)
- âŒ `temporal/scripts/import_year_nodes_to_neo4j.py` (deleted)
- âŒ `temporal/scripts/generate_csv_for_import.py` (deleted)
- âŒ `temporal/scripts/test_connection.py` (deleted)
- âŒ `temporal/scripts/import_periods.py` (deleted)

### Cypher Examples (if needed)
- âŒ `temporal/cypher/WORKING_VISUALIZATIONS.cypher` (deleted)
- âŒ `temporal/cypher/QUICK_GRAPH_VISUALIZATION.cypher` (deleted)

### Batch Files (if needed for examples)
- âŒ `temporal/scripts/classify_date.bat` (deleted)
- âŒ `temporal/scripts/test_connection.bat` (deleted)
- âŒ `temporal/scripts/import_periods.bat` (deleted)

**Note:** These can be recreated or pulled from your existing `scripts/backbone/temporal/` directory if needed.

---

## ðŸ“ Files to CREATE for Agent Training

### Custom Query Cheat Sheet
Create: **`temporal/QUERY_CHEAT_SHEET.md`**

```markdown
# Common Cypher Queries - Quick Reference

## Temporal Queries

### Navigate Time Forward
MATCH (y:Year {year: -753})-[:FOLLOWED_BY*1..10]->(next)
RETURN next;

### Find Years in Period
MATCH (y:Year)-[:PART_OF]->(p:Period {label: 'Roman Republic'})
RETURN y ORDER BY y.year;

## Geographic Queries
...
```

### Common Errors & Solutions
Create: **`temporal/TROUBLESHOOTING.md`**

Based on the issues you've encountered (connection errors, path errors, etc.)

---

## ðŸš€ Creating Your Agent

### Step 1: Upload Agent Instructions
1. Upload `CHATGPT_AGENT_PROMPT.md` as the **primary instructions**
2. This file tells the agent its role and capabilities

### Step 2: Upload Core Documentation (Priority 1)
Upload files 1-10 from Priority 1 list above

### Step 3: Upload Implementation Files (Priority 2)
Upload files 11-17 for practical examples

### Step 4: Test the Agent
Ask test questions:
- "How do I import temporal data to Neo4j?"
- "What's the difference between PART_OF and DURING?"
- "My Neo4j connection is failing, help me troubleshoot"

### Step 5: Iterative Improvement
- Add more files based on gaps you discover
- Update CHATGPT_AGENT_PROMPT.md with new patterns
- Add common Q&A to the prompt

---

## ðŸ’¡ Tips for Agent Configuration

### Agent Name
"Chrystallum Temporal Framework Expert" or "Temporal Graph SME"

### Agent Description
"Expert assistant for the Chrystallum Temporal Graph Framework. Helps with Neo4j imports, Cypher queries, temporal/geographic data modeling, and knowledge graph architecture."

### Conversation Starters
- "How do I import temporal data to Neo4j?"
- "Help me write a Cypher query for temporal data"
- "What's the difference between event-centric and period-centric models?"
- "My import is failing, help me troubleshoot"

### Capabilities to Enable
- âœ… Code Interpreter (for analyzing CSV structure, if needed)
- âœ… Web Browsing (for Wikidata lookups, if needed)
- âŒ DALL-E (not needed)

---

## ðŸ“Š Expected Agent Performance

**After training, the agent should be able to:**

1. âœ… Explain temporal backbone architecture
2. âœ… Provide correct import commands for Windows
3. âœ… Write accurate Cypher queries
4. âœ… Troubleshoot common errors
5. âœ… Reference correct relationship types
6. âœ… Explain design principles (event-centric model, two-stage extraction)
7. âœ… Guide users through workflows
8. âœ… Cite specific documentation sections

**The agent should NOT:**
- âŒ Invent relationship types not in canonical_relationship_types.csv
- âŒ Suggest using PART_OF for events (should use DURING)
- âŒ Recommend letting LLMs process QIDs directly
- âŒ Give incorrect file paths

---

## ðŸ”„ Maintenance

### When to Update Agent

Update the agent when you:
1. Add new historical periods to taxonomy
2. Add new relationship types
3. Change import workflows
4. Discover common error patterns
5. Add new features to the system

### What to Update
1. Upload new/modified documentation files
2. Update `CHATGPT_AGENT_PROMPT.md` with new patterns
3. Add new examples to demonstrate features

---

**Last Updated:** December 12, 2025  
**Purpose:** Training file list for Chrystallum ChatGPT Agent  
**Minimum Files:** 10 (Priority 1 + Agent Prompt)  
**Recommended Files:** 25-30 (Priority 1 + Priority 2 + Priority 3)


