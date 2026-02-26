# SubjectConcept QID-Canonical Migration Runbook

**Purpose:** Complete the subj_rr_* → QID-canonical migration.  
**Feature:** subj-rr-refactor-2026-02-24 (critical)

---

## Quick check: Are SubjectConcepts already clean?

If SubjectConcepts in Neo4j have `subject_id` = QID (e.g. Q17167, Q105427) — they're already QID-canonical. **Skip Step 1.** Run `output/neo4j/verify_subject_concepts_clean.cypher` to confirm.

---

## Prerequisites

- [x] `subject_concept_anchors_qid_canonical.json` (61 SubjectConcepts)
- [x] `subject_concept_hierarchy.json` (BROADER_THAN edges)
- [x] `harvest_run_summary.json` with `qid_to_subject_ids` (QID keys)
- [x] Harvest reports in `output/backlinks/*_report.json` (61 files)
- [ ] Neo4j Aura connection (URI, user, password in `.env` or CLI)

---

## Step 1: Remove Legacy SubjectConcepts (Neo4j)

**⚠️ Destructive:** Deletes legacy `subj_rr_*` and `subj_roman_republic_q17167` nodes and their MEMBER_OF edges.

**Option A — Neo4j Browser:**
1. Open Neo4j Browser (Aura console or desktop)
2. **Run each block separately** — select one block (e.g. DIAGNOSTIC), then Run (Ctrl+Enter)
3. Run DIAGNOSTIC first — it always returns a row with `total`, `sample_subject_ids`, `action`
4. If `action` says "proceed to Step 2", skip 1a/1b and go to Step 2
5. If "Legacy subj_rr_* found", run block 1a, then block 1b

**Option B — cypher-shell:**
```powershell
# From project root, with NEO4J_PASSWORD set
Get-Content output/neo4j/migrate_subject_concepts_to_qid_canonical.cypher | cypher-shell -u neo4j -a $env:NEO4J_URI
```

---

## Step 2: Load QID-Canonical SubjectConcepts

**Option A — Direct to Neo4j (recommended):**
```powershell
cd c:\Projects\Graph1
python scripts/backbone/subject/load_subject_concepts_qid_canonical.py
# Prompts for password if NEO4J_PASSWORD not set
```

**Option B — Generate Cypher file (no Neo4j connection):**
```powershell
python scripts/backbone/subject/load_subject_concepts_qid_canonical.py --cypher
# Then run output/neo4j/load_subject_concepts_qid_canonical.cypher in Neo4j Browser
```

**Expected output:**
- 61 SubjectConcept nodes
- DOMAIN_OF edges to KnowledgeDomain Q17167
- BROADER_THAN hierarchy edges

---

## Step 3: Recreate Entity–SubjectConcept Edges (cluster_assignment)

**Option A — Direct to Neo4j:**
```powershell
python scripts/backbone/subject/cluster_assignment.py `
  --harvest-dir output/backlinks `
  --summary output/backlinks/harvest_run_summary.json `
  --output-dir output/cluster_assignment `
  --write
```

**Option B — Cypher file only (inspect before committing):**
```powershell
python scripts/backbone/subject/cluster_assignment.py `
  --harvest-dir output/backlinks `
  --summary output/backlinks/harvest_run_summary.json `
  --output-dir output/cluster_assignment `
  --cypher
# Then run the generated .cypher in Neo4j Browser
```

**Expected:** MEMBER_OF edges from Entity nodes to SubjectConcept nodes (by qid).

---

## Verification

```cypher
// SubjectConcept count (expect 61)
MATCH (sc:SubjectConcept) RETURN count(sc) AS n;

// BROADER_THAN edges (expect ~60)
MATCH ()-[r:BROADER_THAN]->() RETURN count(r) AS n;

// MEMBER_OF edges (expect thousands)
MATCH ()-[r:MEMBER_OF]->(:SubjectConcept) RETURN count(r) AS n;

// Sample: entities linked to Roman Senate (Q105427)
MATCH (e:Entity)-[:MEMBER_OF]->(sc:SubjectConcept {qid: 'Q105427'})
RETURN e.qid, e.label LIMIT 5;
```

---

## Rollback (if needed)

If you need to restore legacy SubjectConcepts:
1. Re-run `load_roman_republic_ontology.py` (creates subj_rr_* nodes)
2. Re-run cluster_assignment with legacy harvest_run_summary (if you have one with subject_id keys)

**Note:** No automatic rollback. Back up Neo4j before Step 1 if uncertain.

---

## One-Liner (all steps, after Step 1 in Neo4j Browser)

```powershell
# Step 2 + 3 (after manual Step 1 in Neo4j)
python scripts/backbone/subject/load_subject_concepts_qid_canonical.py
python scripts/backbone/subject/cluster_assignment.py -d output/backlinks -s output/backlinks/harvest_run_summary.json -o output/cluster_assignment --write
```
