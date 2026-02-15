# CHATGPT UPLOAD QUICK REFERENCE

## 🎯 THE SYSTEM PROMPT (Upload to "Instructions" field)

```
📄 FILE: md/Agents/QUERY_EXECUTOR_AGENT_PROMPT.md
📏 SIZE: 531 lines
✅ ACTION: Copy entire contents → paste into ChatGPT Instructions field
```

---

## 📁 FILES TO UPLOAD (Minimum 10)

### BATCH 1: CORE (5 files)
- [ ] QUICK_START.md
- [ ] COMPLETE_INTEGRATED_ARCHITECTURE.md
- [ ] IMPLEMENTATION_ROADMAP.md
- [ ] scripts/agents/QUERY_EXECUTOR_QUICKSTART.md
- [ ] COMPLETE_INTEGRATION_PACKAGE_SUMMARY.md

### BATCH 2: SCHEMA (5 files)
- [ ] Key Files/Main nodes.md
- [ ] Relationships/relationship_types_registry_master.csv
- [ ] Facets/facet_registry_master.json
- [ ] Neo4j/schema/01_schema_constraints.cypher
- [ ] Neo4j/schema/02_schema_indexes.cypher

### BATCH 3: SESSION 3 (3 files - LATEST)
- [ ] SESSION_3_EXECUTION_SUMMARY.md
- [ ] AI_CONTEXT.md
- [ ] Change_log.py

### BATCH 4: CODE REFERENCE (5 files - OPTIONAL)
- [ ] scripts/reference/hierarchy_query_engine.py
- [ ] scripts/reference/academic_property_harvester.py
- [ ] Cypher/wikidata_hierarchy_relationships.cypher
- [ ] scripts/agents/query_executor_agent_test.py
- [ ] scripts/tools/claim_ingestion_pipeline.py

---

## 🛠️ CHATGPT SETUP

**Agent Name:** Chrystallum Query Executor

**Description:**
```
Expert agent for executing live queries against the Chrystallum historical 
knowledge graph. Discovers Neo4j schema dynamically, generates Cypher queries 
from natural language, and submits claims. NOT a consultant - WILL execute 
queries and return live results from database.
```

**Conversation Starters:**
```
1. Show me entities related to the Roman Republic
2. What events happened in 49 BCE?
3. Who were military historians in Roman times?
4. Submit a claim about the Battle of Cannae
```

**Capabilities:**
- ✅ Web Browsing (for Wikidata lookups)
- ❌ Code Interpreter
- ❌ DALL-E

---

## ✔️ VERIFICATION TESTS

After uploading, run these 5 tests:

### Test 1: Schema Discovery
```
Query: "What node types are available?"
Expected: Agent lists SubjectConcept, Human, Event, Place, Period, etc.
Status: [ ] PASS
```

### Test 2: Canonical Labels
```
Query: "Find people in the Roman Republic"
Expected: Uses "Human" (NOT "Person"), "SubjectConcept" (NOT "Concept")
Status: [ ] PASS
```

### Test 3: Temporal Query
```
Query: "What events happened in 49 BCE?"
Expected: Uses Year nodes, ISO 8601 format ("-0049")
Status: [ ] PASS
```

### Test 4: Query Generation
```
Query: "Show me the top 10 events"
Expected: Valid Cypher with LIMIT 10
Status: [ ] PASS
```

### Test 5: Facet System
```
Query: "Show military concepts"
Expected: Recognizes "military" as valid facet
Status: [ ] PASS
```

---

## 📊 WHAT YOU'LL GET

✅ Live Neo4j query executor (NOT just a consultant)  
✅ Dynamic schema discovery  
✅ Natural language → Cypher generation  
✅ Result formatting + confidence scores  
✅ Claim submission with validation  
✅ Multi-layer authority grounding (5.5-layer)  
✅ Historical context built-in  
✅ 17-facet system understanding  

---

## 🚀 STATUS

✅ System prompt ready (531 lines)  
✅ 10+ files prepared for upload  
✅ Architecture complete (Layer 2.5 added)  
✅ Neo4j access configured  
✅ Display capabilities built  

**READY TO UPLOAD TO CHATGPT** 🎉
