# 📦 **MIGRATION READY: graph3-1 → c:\projects\graph**

## ✅ **STATUS: READY TO MIGRATE**

All essential files are now consolidated in the **`graph3-1/`** folder.

---

## 📋 **MIGRATION CHECKLIST**

### 1️⃣ **What's in graph3-1/ (Ready to Move)**

```
graph3-1/
├── NODE_TYPE_SCHEMAS.md ⭐ (just moved here)
├── CHANGELOG.md
│
├── Batch/ (4 .bat files)
│   ├── activate.bat
│   ├── clean_to_backbones.bat
│   ├── deactivate.bat
│   └── rebuild_class_d_backbone.bat
│
├── CSV/ (5 data files)
│   ├── action_structure_vocabularies.csv
│   ├── action_structure_wikidata_mapping.csv
│   ├── canonical_relationship_types.csv
│   ├── stable_geographic_features.csv
│   └── year_nodes.csv
│
├── JSON/ (2 schema files)
│   ├── canonical_relationship_types_summary.json
│   └── chrystallum_schema.json
│
├── md/ (126 markdown docs)
│   ├── Core/ (1)
│   ├── Architecture/ (39)
│   ├── Agents/ (12)
│   ├── Reference/ (44)
│   ├── Examples/ (10)
│   ├── Guides/ (15)
│   └── CIDOC/ (5)
│
├── Prompts/ (2 agent prompts)
│   ├── extraction_agent.txt
│   └── person_research_agent.txt
│
└── Python/ (27 scripts)
    ├── import_lcsh_class_d.py
    ├── retrieve_lcsh_class_d_complete.py
    ├── clean_to_backbones.py
    ├── show_all_lcc_codes.py
    ├── import_roman_republic_subgraph.py
    ├── fix_missing_subject_links.py
    ├── link_composite_events_to_years.py
    ├── show_event_backbones.py
    ├── show_complete_event_view.py
    ├── test_neo4j_connection.py
    └── Library/ (helper modules)
```

### 2️⃣ **What's Still in "graph 3" Root (Need to Copy Separately)**

```
c:\Projects\federated-graph-framework\graph 3\
│
├── requirements.txt ⭐ (copy this)
│
├── data\
│   └── backbone\
│       └── subject\
│           └── lcsh_class_d_complete.csv ⭐ (copy this)
│
├── scripts\ ⭐ (copy this entire folder)
│   ├── backbone\
│   │   ├── subject\ (2 scripts)
│   │   └── temporal\ (1 script)
│   ├── setup\ (2 scripts)
│   └── tools\ (1 script)
│
├── cypher\ ⭐ (copy this entire folder)
│   ├── maintenance\
│   ├── queries\
│   └── setup\
│
├── Environment\
│   ├── Neo4j-e504e285-Created-2025-12-01.txt ⭐ (connection info)
│   └── Readme.txt
│
└── config\
    └── .gitignore (if exists)
```

### 3️⃣ **NOT Migrating (Leave Behind)**
- ❌ `venv/` and `venv312/` (recreate fresh)
- ❌ `Archive/` (historical)
- ❌ `Chats/` (historical)
- ❌ `Docs/` (only has 1 PDF, keep separately if needed)

---

## 🚀 **MIGRATION STEPS**

### ✅ **EVERYTHING IS NOW SELF-CONTAINED IN graph3-1/**

All essential files have been moved into the `graph3-1/` folder!

### Step 1: Cut/Paste (That's It!)
```
1. Cut the entire "graph3-1" folder from:
   c:\Projects\federated-graph-framework\graph 3\graph3-1
   
2. Paste to: c:\projects\
   
3. Rename "graph3-1" → "graph"
```

**Result:** `c:\projects\graph\` (fully self-contained, ready to use!)

No additional copying needed! Everything is included:
- ✅ requirements.txt
- ✅ data/backbone/subject/lcsh_class_d_complete.csv
- ✅ scripts/ (6 backend scripts)
- ✅ cypher/ (queries folder)
- ✅ Environment/ (Neo4j connection info)

### Step 2: Create New Files in c:\projects\graph\

**README.md:**
```markdown
# Chrystallum Knowledge Graph

LCC-based dual backbone architecture (Year + LCSH/LCC subjects) for historical knowledge graph.

## Quick Start
1. Install: `pip install -r requirements.txt`
2. Activate venv: `Batch\activate.bat`
3. Start Neo4j (see Environment\Neo4j-*.txt)
4. Run: `Batch\rebuild_class_d_backbone.bat`

## Documentation
See `md/` folder for all documentation, organized by category.
```

**.env:**
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=[your password]
```

**.gitignore:**
```
venv/
__pycache__/
*.pyc
.env
*.log
```

### Step 3: Final Structure Check
```
c:\projects\graph\
├── README.md (new)
├── .env (new)
├── .gitignore (new)
├── NODE_TYPE_SCHEMAS.md ✅
├── CHANGELOG.md ✅
├── requirements.txt ✅
├── Batch\ ✅
├── CSV\ ✅
├── JSON\ ✅
├── md\ ✅
├── Prompts\ ✅
├── Python\ ✅
├── data\backbone\subject\ ✅
├── scripts\ ✅
├── cypher\ ✅
└── Environment\ ✅
```

### Step 4: Create New Venv
```
cd c:\projects\graph
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 5: Test
```
python Python\test_neo4j_connection.py
python scripts\setup\check_database.py
```

---

## 📊 **SUMMARY**

**From graph3-1 (cut/paste):**
- ✅ 126 markdown docs
- ✅ 27 Python scripts
- ✅ 4 batch scripts
- ✅ 7 CSV/JSON data files
- ✅ 2 agent prompts
- ✅ NODE_TYPE_SCHEMAS.md
- ✅ CHANGELOG.md

**Additional copies needed:**
- ✅ requirements.txt
- ✅ data/backbone/subject/lcsh_class_d_complete.csv
- ✅ scripts/ (6 scripts)
- ✅ cypher/ (if any .cypher files)
- ✅ Environment/Neo4j-*.txt

**New files to create:**
- 📝 README.md
- 📝 .env
- 📝 .gitignore

**Total:** ~170 files + documentation

---

## ✅ **READY TO MIGRATE!**

Everything is organized and ready. Just follow the steps above and you'll have a clean `c:\projects\graph` installation!

