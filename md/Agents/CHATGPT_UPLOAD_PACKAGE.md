# 📥 CHATGPT CUSTOM AGENT UPLOAD PACKAGE

**Purpose:** Complete list of files + system prompt to upload to ChatGPT for Query Executor Agent  
**Date:** February 15, 2026  
**Agent Type:** Live Query Executor (NOT consultant - executes queries)  

---

## 🎯 THE SYSTEM PROMPT

**File to Upload as "Instructions":**
```
📄 md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md
```

**Size:** 531 lines  
**Format:** Copy entire file content into ChatGPT "Instructions" field  

**Key Sections:**
- Your Role (Query Executor, NOT Consultant)
- System Architecture (5.5-layer Chrystallum)
- Critical Rules (Canonical labels, schema discovery)
- 6 Cypher Query Patterns
- Facet System (17-facet model)
- Authority Alignment (QIDs + LCSH + CRMinf)
- 3 Example Conversations
- Error Handling
- Success Criteria

---

## 📚 FILES TO UPLOAD (Minimum 10 Files)

**Priority 1: MUST UPLOAD**

| # | File | Size | Purpose |
|---|------|------|---------|
| 1 | `md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md` | 531 lines | **System prompt - INSTRUCTIONS field** |
| 2 | `QUICK_START.md` | ~100 lines | Quick overview of project |
| 3 | `COMPLETE_INTEGRATED_ARCHITECTURE.md` | 662 lines | 5.5-layer architecture (Layer 2.5 NEW) |
| 4 | `IMPLEMENTATION_ROADMAP.md` | ~300 lines | Week 1.5 deployment timeline |
| 5 | `scripts/agents/QUERY_EXECUTOR_QUICKSTART.md` | 602 lines | Agent usage guide |
| 6 | `COMPLETE_INTEGRATION_PACKAGE_SUMMARY.md` | 1,200 lines | Deployment guide + integration |
| 7 | `Key Files/Main nodes.md` | ~150 lines | Node type specifications |
| 8 | `Relationships/relationship_types_registry_master.csv` | CSV | All canonical relationship types |
| 9 | `Facets/facet_registry_master.json` | JSON | 17-facet system definition |
| 10 | `Neo4j/schema/01_schema_constraints.cypher` | ~319 lines | Neo4j constraint definitions |

**Priority 2: HIGHLY RECOMMENDED (Add if possible)**

| # | File | Size | Purpose |
|---|------|------|---------|
| 11 | `SESSION_3_EXECUTION_SUMMARY.md` | ~450 lines | This week's accomplishments |
| 12 | `scripts/reference/hierarchy_query_engine.py` | 620 lines | Hierarchy query engine code |
| 13 | `scripts/reference/academic_property_harvester.py` | 380 lines | SPARQL harvester |
| 14 | `Cypher/wikidata_hierarchy_relationships.cypher` | 250+ lines | New Layer 2.5 schema |
| 15 | `AI_CONTEXT.md` | ~700 lines | Session 3 entry + all prior context |
| 16 | `Change_log.py` | ~1,300 lines | Session 3 changelog entry |

**Priority 3: REFERENCE (Optional)**

| # | File | Size | Purpose |
|---|------|------|---------|
| 17 | `scripts/agents/query_executor_agent_test.py` | 460 lines | Agent Python implementation |
| 18 | `scripts/tools/claim_ingestion_pipeline.py` | 460 lines | Claim submission pipeline |
| 19 | `Temporal/time_periods.csv` | CSV | Temporal backbone data |
| 20 | `Neo4j/schema/02_schema_indexes.cypher` | ~200 lines | Neo4j indexes |

---

## 🚀 UPLOAD INSTRUCTIONS

### Step 1: Create New Custom GPT
1. Go to [chat.openai.com/](https://chat.openai.com/)
2. Click profile → "My GPTs" → "+ Create"
3. Choose "Configure" tab

### Step 2: Fill in Metadata
```
Name: Chrystallum Query Executor

Description: 
Expert agent for executing live queries against the Chrystallum historical knowledge graph. 
Discovers Neo4j schema dynamically, generates Cypher queries from natural language, and 
submits claims with automatic validation and promotion. Specializes in Roman Republic and 
Mediterranean history. NOT a consultant - WILL execute queries and return live results.

Instructions: 
[PASTE ENTIRE CONTENTS OF: md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md]

Conversation Starters:
- Show me entities related to the Roman Republic
- What events happened in 49 BCE?
- Who were the experts in military history?
- Submit a claim: Caesar crossed the Rubicon

Capabilities:
✓ Web Browsing (for Wikidata lookups if needed)
✗ Code Interpreter (not needed)
✗ DALL-E (not needed)
```

### Step 3: Upload Knowledge Base Files
Click "Add files" and upload in this order:

**Upload Batch 1 (Core - Must have):**
- QUICK_START.md
- COMPLETE_INTEGRATED_ARCHITECTURE.md
- IMPLEMENTATION_ROADMAP.md
- scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
- COMPLETE_INTEGRATION_PACKAGE_SUMMARY.md

**Upload Batch 2 (Schema - Critical):**
- Key Files/Main nodes.md
- Relationships/relationship_types_registry_master.csv
- Facets/facet_registry_master.json
- Neo4j/schema/01_schema_constraints.cypher
- Neo4j/schema/02_schema_indexes.cypher

**Upload Batch 3 (Session 3 - Latest):**
- SESSION_3_EXECUTION_SUMMARY.md
- AI_CONTEXT.md (scroll to bottom for Session 3 entry)
- Change_log.py (scroll to top for latest entry)

**Upload Batch 4 (Implementation - Code reference):**
- scripts/reference/hierarchy_query_engine.py
- scripts/reference/academic_property_harvester.py
- Cypher/wikidata_hierarchy_relationships.cypher
- scripts/agents/query_executor_agent_test.py
- scripts/tools/claim_ingestion_pipeline.py

**Upload Batch 5 (Reference - Optional):**
- Temporal/time_periods.csv
- Database schema files
- Any other reference materials

### Step 4: Test the Agent

**Test Queries to Verify Setup:**

1. **Schema Discovery Test**
   ```
   Query: "What node types are available in this knowledge graph?"
   Expected: Agent lists: SubjectConcept, Human, Event, Place, Period, Claim, Year, etc.
   ```

2. **Canonical Labels Test**
   ```
   Query: "Find people in the Roman Republic"
   Expected: Agent uses "Human" NOT "Person"; "SubjectConcept" NOT "Concept"
   ```

3. **Temporal Query Test**
   ```
   Query: "What events happened in 49 BCE?"
   Expected: Agent uses Year nodes; ISO 8601 format ("-0049")
   ```

4. **Query Generation Test**
   ```
   Query: "Show me the top 10 events"
   Expected: Agent generates valid Cypher with LIMIT 10
   ```

5. **Facet System Test**
   ```
   Query: "Show me military history related concepts"
   Expected: Agent queries facet system; recognizes "military" as valid facet
   ```

**Success Criteria:**
- ✅ All 5 queries answered correctly
- ✅ Agent displays schema information
- ✅ Cypher queries use canonical labels
- ✅ Results are formatted clearly
- ✅ Agent handles errors gracefully

### Step 5: Save & Enable
1. Click "Save" button
2. Agent is now available in your GPTs list
3. Share URL with team members if needed

---

## 📋 CHATGPT AGENT CONFIGURATION CHECKLIST

```
Instructions Field:
[ ] Pasted QUERY_EXECUTOR_AGENT_PROMPT.md (entire 531 lines)
[ ] Text is readable and complete
[ ] All code examples included

Knowledge Files:
[ ] Batch 1 uploaded (5 files - core)
[ ] Batch 2 uploaded (5 files - schema)
[ ] Batch 3 uploaded (3 files - session 3)
[ ] Batch 4 uploaded (5 files - implementation)
[ ] Total: minimum 10 files (maximum comfortable limit: 20)

Metadata:
[ ] Name: "Chrystallum Query Executor"
[ ] Description: Complete (mentions live queries, Neo4j, NOT consultant)
[ ] 4 Conversation Starters added
[ ] Web Browsing enabled
[ ] Code Interpreter disabled
[ ] DALL-E disabled

Testing:
[ ] Test Query 1 (Schema Discovery) - PASS
[ ] Test Query 2 (Canonical Labels) - PASS
[ ] Test Query 3 (Temporal Queries) - PASS
[ ] Test Query 4 (Query Generation) - PASS
[ ] Test Query 5 (Facet System) - PASS

Deployment:
[ ] Agent saved and active
[ ] Share link generated (if needed)
[ ] First real user test completed
```

---

## 🎯 IF UPLOADING GETS LIMITED

**Upload Priority (if file count limited):**

**Absolute Minimum (5-6 files):**
1. md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md (INSTRUCTIONS)
2. COMPLETE_INTEGRATED_ARCHITECTURE.md
3. QUICK_START.md
4. scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
5. Key Files/Main nodes.md
6. Relationships/relationship_types_registry_master.csv

**Add if there's room:**
7. Facets/facet_registry_master.json
8. IMPLEMENTATION_ROADMAP.md
9. SESSION_3_EXECUTION_SUMMARY.md
10. Neo4j/schema/01_schema_constraints.cypher

---

## 🔍 WHAT THE AGENT WILL BE ABLE TO DO

**After Upload:**

✅ **Discover Schema Dynamically**
- Lists available node types (SubjectConcept, Human, Event, Place, etc.)
- Shows relationship types (CLASSIFIED_BY, PARTICIPATED_IN, etc.)
- Explains what data is available

✅ **Execute Live Queries**
- Natural language → Cypher translation
- Executes queries against Neo4j
- Returns readable results

✅ **Display What It's Doing**
- Shows schema discovery process
- Displays generated Cypher
- Reports results with confidence + authority

✅ **Handle Historical Context**
- Roman Republic timeline built-in
- Key QIDs (Julius Caesar, etc.)
- Knows canonical periods

✅ **Submit Claims**
- Create new claims via ingestion pipeline
- Automatic validation passing
- Promotion to "validated" if confidence ≥ 0.90

✅ **Multi-Layer Authority Grounding**
- Layer 1: Library Authority (LCSH)
- Layer 2: Federation Authority (Wikidata)
- Layer 2.5: Hierarchy Queries (NEW - P31/P279/P361/P101/P2578/P921/P1269)
- Layer 3: Facet Discovery
- Layer 4: Subject Concepts
- Layer 5: Validation

---

## 📝 EXAMPLE AGENT CONVERSATION

```
User: "Show me people who worked on military history in the Roman Republic"

Agent:
[Discovers schema]
I found 14 node types including Human, SubjectConcept, Event, Period, Place...

[Generates Cypher]
MATCH (subject:SubjectConcept {label: 'Military History'})
MATCH (human:Human)-[:FIELD_OF_WORK]->(subject)
RETURN human.label, human.qid, human.confidence
LIMIT 10

[Executes]
Connecting to Neo4j at bolt://localhost:7687...
✓ Connected

[Results]
Found 4 military historians:
1. Polybius (Q7345) - confidence: 0.95
2. Livy (Q6058) - confidence: 0.93
3. Caesar (Q1048) - confidence: 0.90
4. Vegetius (Q185018) - confidence: 0.88

All linked via P101 (field_of_work) from Wikidata.
```

---

## ✅ STATUS: READY TO UPLOAD

All files prepared. System prompt comprehensive (531 lines). Neo4j access configured in agent Python implementation. Display capabilities built.

**Next Step:** Upload these 10-20 files to ChatGPT Custom GPT following instructions above.
