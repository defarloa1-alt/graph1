# Subject Agent: Pushing Survey Data to Neo4j

How to push FederationSurvey output (LCSH, Pleiades, PeriodO, DPRR, WorldCat, LCC) to Neo4j. Two paths: **MCP** (AI agent in Cursor) and **non-MCP** (Python scripts, cypher-shell).

---

## 1. MCP Method (AI Agent in Cursor Chat)

**When:** You are the AI agent in Cursor and the user asks you to push survey data to Neo4j.

**Prerequisites:**
- Neo4j MCP server configured in Cursor (see `docs/agents/CURSOR_MCP_QUICK_START.md`)
- Neo4j running (local or Aura)

**How it works:**
- You have access to the `run_cypher_mutation` tool from the Neo4j MCP server.
- You read the survey JSON (e.g. `output/nodes/lcsh_roman_republic.json`), build Cypher, and call the tool.

**Steps:**
1. Load the survey JSON: `FederationSurvey.load("output/nodes/lcsh_roman_republic.json")`
2. Map each node to your target schema (e.g. `:SubjectConcept`, `:Place`, `:FederationNode`).
3. Build Cypher for each node, e.g.:
   ```cypher
   MERGE (n:SubjectConcept {id: $id})
   SET n.label = $label, n.uri = $uri, n.concept_ref = $concept_ref,
       n.federation = $federation, n.domain = $domain
   ```
4. Call `run_cypher_mutation` with the query and params.

**Batch size:** For large surveys (e.g. 18k Pleiades nodes), run in batches (e.g. 100–500 per mutation) to avoid timeouts.

**Example prompt to the agent:**
> "Push output/nodes/lcsh_roman_republic.json to Neo4j as SubjectConcept nodes. Use MERGE on id."

---

## 2. Non-MCP Methods (Python Scripts)

**When:** You are writing a script that runs outside Cursor (CLI, cron, pipeline).

### 2a. Python + neo4j Driver

**Install:** `pip install neo4j`

**Config:** `scripts/config_loader.py` loads from `.env`:
- `NEO4J_URI` (e.g. `bolt://localhost:7687` or `neo4j+s://xxx.databases.neo4j.io`)
- `NEO4J_USERNAME` (default `neo4j`)
- `NEO4J_PASSWORD`

**Pattern:**
```python
from neo4j import GraphDatabase

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session() as session:
    session.run("""
        MERGE (n:SubjectConcept {id: $id})
        SET n.label = $label, n.uri = $uri, n.federation = $federation
    """, id=node.id, label=node.label, uri=node.uri, federation=node.federation)

driver.close()
```

**Load survey:**
```python
# Run from project root: python scripts/federation/import_lcsh.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/ on path

from federation_node_schema import FederationSurvey

survey = FederationSurvey.load("output/nodes/lcsh_roman_republic.json")
# survey.nodes → list of FederationNode
```

**Batch writes:**
```python
# Use UNWIND for batch
session.run("""
    UNWIND $batch AS row
    MERGE (n:SubjectConcept {id: row.id})
    SET n.label = row.label, n.uri = row.uri, n.federation = row.federation
""", batch=[{"id": n.id, "label": n.label, "uri": n.uri, "federation": n.federation} for n in survey.nodes])
```

**Reference scripts:**
- `scripts/federation/dprr_import.py` — full Neo4j import (persons, posts, relationships)
- `scripts/neo4j/run_cypher_file.py` — run a .cypher file
- `scripts/backbone/subject/load_lcc_nodes.py` — load LCC nodes

### 2b. Generate Cypher File + cypher-shell

**When:** You want to inspect or run Cypher outside Python.

1. Write a script that reads the survey JSON and emits a `.cypher` file.
2. Run: `cypher-shell -u neo4j -p <password> -f output/neo4j/import_lcsh.cypher`

**Example:**
```python
# In your script
with open("output/neo4j/import_lcsh.cypher", "w") as f:
    for n in survey.nodes:
        f.write(f"MERGE (n:SubjectConcept {{id: '{n.id}'}}) SET n.label = '{n.label.replace(chr(39), chr(39)+chr(39))}';\n")
```

**Safer:** Use parameterized Cypher via `run_cypher_file.py` — it supports `$param` placeholders.

---

## 3. Schema Mapping: FederationSurvey → Neo4j

| Survey   | Suggested label(s) | Key id field   | Notes |
|----------|--------------------|----------------|-------|
| LCSH     | SubjectConcept     | id (sh...)     | concept_ref = LCSH URI |
| Pleiades | Place              | id (Pleiades)  | spatial_anchor, lat/lon |
| PeriodO  | SubjectConcept     | id (p0...)     | temporal_range, spatial_coverage |
| DPRR     | Entity, Office     | person_id, post | POSITION_HELD edges |
| WorldCat | Work               | id (LCCN/OCLC) | text_ref, concept_ref |
| LCC      | SubjectConcept     | id (LCC code)  | LCC hierarchy |

**Existing patterns:**
- `scripts/federation/dprr_import.py` — Entity, Office, POSITION_HELD, HAS_STATUS
- `scripts/backbone/geographic/import_pleiades_to_neo4j.py` — Place nodes
- `scripts/backbone/subject/load_lcc_nodes.py` — LCC hierarchy

---

## 4. Quick Reference

| Goal                    | Use |
|-------------------------|-----|
| AI in Cursor pushes     | MCP `run_cypher_mutation` |
| Python script pushes    | `neo4j.GraphDatabase` + `session.run()` |
| Run pre-built Cypher    | `python scripts/neo4j/run_cypher_file.py -f output/neo4j/import.cypher` |
| Config from env         | `config_loader.NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` |

---

## 5. Federation Survey Output Paths

```
output/nodes/lcsh_roman_republic.json
output/nodes/pleiades_roman_republic.json
output/nodes/periodo_roman_republic.json
output/nodes/dprr_roman_republic.json
output/nodes/worldcat_roman_republic.json
output/nodes/lcc_roman_republic.json   (when implemented)
```

---

*Last updated: 2026-02-27*
