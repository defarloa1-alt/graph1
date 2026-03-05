# Chrystallum Session Handoff — 2026-03-05

## What Was Accomplished This Session

### 1. SubjectConcept Promotion — 29 nodes

Ran anchor-batch promotion of entities with both VIAF ID and Pleiades or DPRR ID. Total `:SubjectConcept` count went from 1 → 30.

**Cypher used:**
```cypher
MATCH (n:Entity)
WHERE n.subject_candidate = true
  AND n.viaf_id IS NOT NULL
  AND NOT n:Person
  AND (n.pleiades_id IS NOT NULL OR n.dprr_id IS NOT NULL)
SET n:SubjectConcept,
    n.subject_id = 'subj_' + toLower(n.qid),
    n.sca_confidence = 0.85,
    n.primary_facet = 'Political',
    n.promoted_by = 'ANCHOR_BATCH_V1',
    n.promoted_at = datetime()
```

The 29 nodes are all Roman provinces and settlements (Pannonia, Gallia Narbonensis, Lusitania, etc.) plus Temple of Augustus, Ostia, Stabiae, Tergeste. All have Pleiades spatial anchors. No DPRR-anchored concepts were in this batch.

**Constraint discovered:** `:SubjectConcept` requires `subject_id` property. Pattern confirmed: `subj_` + lowercase QID (e.g., `subj_q17167`).

---

### 2. subject_candidate Flagging — 540 nodes

```cypher
MATCH (n:Entity)
WHERE n.viaf_id IS NOT NULL
   OR n.fast_id IS NOT NULL
   OR n.lcsh_id IS NOT NULL
   OR n.lcc_id IS NOT NULL
   OR n.getty_aat_id IS NOT NULL
SET n.subject_candidate = true
```

**Important finding:** Authority ID alone is NOT a corpus fit signal. The 540 flagged nodes include Crystal Palace, Planet Hollywood, Holocaust memorials — modern entities that got harvested as Wikidata neighbors. Only 29 passed the dual-anchor filter (VIAF + Pleiades/DPRR). The remaining ~511 need a corpus fit score before promotion. Do NOT bulk-promote them.

---

### 3. subject_concept_enrich.py — Run Successfully

Script at: `C:\Projects\Graph1\scripts\subject_concept_enrich.py`

**What it does:**
1. Fetches all 30 `:SubjectConcept` nodes from Neo4j
2. Hits Wikidata SPARQL for P571 (inception) and P576 (dissolved)
3. Computes `temporal_bucket`: REPUBLICAN / IMPERIAL_EARLY / IMPERIAL_LATE / LATE_ANTIQUE / PRE_REPUBLICAN / UNKNOWN
4. Applies facet override map (Geographic for provinces, Archaeological for cities/temples)
5. Computes `capability_cipher` as SHA256(qid | temporal_bucket | sorted_authority_keys | sorted_fed_source_ids | sorted_facets)
6. Writes back to Neo4j

**Results — 30/30 nodes enriched:**

| Bucket | Count |
|--------|-------|
| UNKNOWN | 14 |
| IMPERIAL_EARLY | 9 |
| REPUBLICAN | 5 |
| IMPERIAL_LATE | 1 |
| PRE_REPUBLICAN | 1 |

14 UNKNOWN is expected — Wikidata lacks P571/P576 for many provinces reorganized multiple times.

Republican nodes: Roman Republic (Q17167), Africa (Q181238), Asia (Q210718), Gallia Narbonensis (Q26897), Bithynia et Pontus (Q913382).

---

### 4. Floruit Dates Derived from Office Years

```cypher
MATCH (p:Person)-[r:POSITION_HELD]->()
WHERE r.year IS NOT NULL OR r.start_year IS NOT NULL
WITH p,
     min(coalesce(r.year, r.start_year)) AS fl_start,
     max(coalesce(r.year, r.end_year, r.start_year)) AS fl_end
SET p.floruit_start = fl_start,
    p.floruit_end   = fl_end,
    p.floruit_derived = true
RETURN count(p) AS updated
```
Result: 3,448 persons now have `floruit_start` / `floruit_end`.

---

### 5. CHILD_OF Inverse Edges Created

```cypher
MATCH (parent:Person)-[:FATHER_OF]->(child:Person)
MERGE (child)-[:CHILD_OF {parent_type: 'father'}]->(parent)
```
```cypher
MATCH (parent:Person)-[:MOTHER_OF]->(child:Person)
MERGE (child)-[:CHILD_OF {parent_type: 'mother'}]->(parent)
```

Graph is now bidirectionally navigable for family tree traversal.

---

### 6. Family Tree Verified — Metelli

Query confirmed deep tree structure. Q. Caecilius Metellus Macedonicus (DPRR 1424) has 87 traceable descendants. 4 generations of output confirmed correct with branching into Claudii Pulchri (via Caecilia Metella → Claudius Pulcher marriage), Cornelii Scipiones, Servilii, Licinii Luculli, and others.

---

## Current Graph State

| Layer | Count | Status |
|-------|-------|--------|
| :Person nodes with DPRR ID | 4,863 | ✓ complete |
| POSITION_HELD edges (dated) | 7,342 | ✓ complete |
| FATHER_OF edges | 4,240 | ✓ complete |
| MOTHER_OF edges | 1,176 | ✓ complete |
| SIBLING_OF edges | 4,295 | ✓ complete |
| SPOUSE_OF edges | 1,202 | ✓ complete |
| CHILD_OF inverse edges | ~5,400 | ✓ created this session |
| Persons with floruit dates | 3,448 | ✓ derived this session |
| :SubjectConcept nodes | 30 | ✓ promoted this session |
| capability_cipher computed | 30 | ✓ computed this session |
| :Place nodes | 43,958 | ✓ pre-existing |
| :Pleiades_Place nodes | 32,572 | ✓ pre-existing |
| :Discipline nodes | 1,363 | ✓ pre-existing |
| :Periodo_Period nodes | 1,118 | ✓ pre-existing |

---

## DPRR Federation Source Status

- **Status:** `blocked` (should be changed to `partial`)
- **Block reason:** Anubis bot protection on live SPARQL endpoint since 2026-03-01
- **Snapshot:** COMPLETE as of 2026-02-25
  - 4,772 persons, 7,342 posts, 4,682 relationships imported
- **Action needed:** Run this in Neo4j Browser:

```cypher
MATCH (n:SYS_FederationSource {name: "DPRR"})
SET n.status = "partial",
    n.block_reason = "Anubis bot protection on live SPARQL endpoint — snapshot complete, live queries unavailable",
    n.live_queries_available = false,
    n.snapshot_available = true
```

---

## Key Architectural Decisions Made

### Temporal bucket added to capability cipher
Old cipher: `qid | p31_type_qids | authority_id_keys | fed_source_ids | facets`
New cipher: `qid | temporal_bucket | authority_id_keys | fed_source_ids | facets`

Rationale: Gallia Narbonensis (REPUBLICAN) and Pannonia (IMPERIAL_EARLY) had identical authority sources and facets — they would have produced identical ciphers. Adding `temporal_bucket` ensures agents can route by era without explicit date checks in every query.

### Non-Republican entities allowed in corpus
Provinces, settlements, and concepts outside 509–27 BCE are permitted as `:SubjectConcept` nodes provided they are:
1. Date-spanned (have or can derive `temporal_start`)
2. Not directly linked to Q17167 (Roman Republic node)
3. Connected via their own Pleiades/Periodo_Period anchors

---

## Immediate Next Steps (Priority Order)

### 1. Fix DPRR status (5 minutes)
Run the Cypher above to change `blocked` → `partial`.

### 2. Corpus fit scoring for remaining 511 subject_candidates
The 540 flagged - 29 promoted = 511 candidates still need scoring before promotion. Need a Python script that:
- Calls Wikidata for P31 (instance of) and P571 (inception) on each candidate
- Scores corpus fit: P31 ancestors that include Q17417 (province of Rome), Q28530 (Roman Republican office), Q12816 (Roman coin), etc. → high score
- Modern entities (post-500 CE P571, or P31 ancestor = Q3914 school, Q4438121 sports team, etc.) → score < 0.15 → reject
- Promotes candidates scoring ≥ 0.15 with appropriate `temporal_bucket` and facets

### 3. VIAF enrichment for top 116 family tree roots
116 root ancestors have no known parents and head trees averaging 39 persons each. Enriching the top 20 by tree size with VIAF data gives birth/death years and WorldCat bibliography links. Script needed: query VIAF API by name + DPRR ID cross-reference, write `birth_year`, `death_year`, `viaf_id` back to person nodes.

### 4. Family tree React visualizer
The graph data is ready. A React artifact using D3 tree layout (or dagre-d3 for DAG support — needed because of intermarriage) with:
- Root person selector (search by name or DPRR ID)
- FATHER_OF / MOTHER_OF / SPOUSE_OF edge rendering
- Floruit date timeline display
- Gens color coding
- Click-through to person detail (offices held, DPRR URI)

### 5. Wikidata P22/P25/P26 augmentation harvest
DPRR has 4,863 persons. Wikidata has Roman Republican persons not in DPRR (women, non-magistrates, mythological ancestors). Running P22 (father), P25 (mother), P26 (spouse), P40 (child) harvest on all persons with QIDs would fill gaps. Estimated 500–1,000 additional family edges. This is the enrichment sprint after VIAF.

---

## Files Produced This Session

| File | Location | Purpose |
|------|----------|---------|
| subject_concept_enrich.py | C:\Projects\Graph1\scripts\ | Temporal + cipher enrichment for SubjectConcepts |
| chrystallum_session_handoff_2026-03-05.md | outputs | This file |

---

## Graph Connection Details

- **URI:** neo4j+s://ac63a8e5.databases.neo4j.io
- **MCP server:** https://graph1-production.up.railway.app/mcp
- **Local project:** C:\Projects\Graph1

---

## Context for Next Session Agent

Tony's primary goal is **family tree construction and visualization** for Roman Republican persons. The genealogy data is already in the graph from the DPRR snapshot (complete Feb 25). Today's session added floruit dates and CHILD_OF inverse edges — the graph is now ready for tree rendering.

The Roman Republic card (constitution artifact) is the UI shell. The next major deliverable is the family tree visualizer tab within that card, backed by live MCP queries against the graph.

Tony is the creator of Chrystallum. He is familiar with Neo4j Cypher, Python scripting, and the full system architecture. Do not over-explain basics. Confirm graph state with MCP queries before making claims about what's in the graph.
