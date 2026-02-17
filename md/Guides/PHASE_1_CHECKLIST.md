# Phase 1 Implementation Checklist: Neo4j Schema Bootstrap

**Target Launch Date:** February 13-14, 2026  
**Estimated Duration:** 2-3 hours  
**Status:** Ready for execution  

---

## Pre-Flight Checklist (30 min)

### Environment Setup
- [ ] Neo4j 5.0+ installed and running
  - [ ] Connection test: `cypher-shell -u neo4j -p <password> "RETURN 1"`
  - [ ] Browser accessible: http://localhost:7474
  - [ ] No existing Chrystallum database (if re-running: DROP DATABASE chrystallum;)
- [ ] Python environment activated
  - [ ] `.venv` activated: `&.\.venv\Scripts\Activate.ps1` (Windows)
  - [ ] Required packages: `pip list | grep py2neo` (should show py2neo, requests)
  - [ ] Python version: `python --version` (should be 3.9+)
- [ ] Workspace structure verified
  - [ ] `Neo4j/schema/` directory exists with 3 scripts
  - [ ] `Python/fast/scripts/` directory exists with import pipeline
  - [ ] `Neo4j/IMPLEMENTATION_ROADMAP.md` accessible
  - [ ] `Neo4j/schema/SCHEMA_BOOTSTRAP_GUIDE.md` accessible

### File Verification
- [ ] `01_schema_constraints.cypher` (600+ lines, constraints present)
- [ ] `02_schema_indexes.cypher` (400+ lines, index definitions present)
- [ ] `03_schema_initialization.cypher` (500+ lines, CREATE statements present)
- [ ] `SCHEMA_BOOTSTRAP_GUIDE.md` (documentation complete)

### Connection Credentials
- [ ] Neo4j username available (default: neo4j)
- [ ] Neo4j password accessible
- [ ] No firewall/network blocks on Neo4j port (7687 for Bolt)

---

## Step 1: Schema Definition & Deployment (45 min)

### 1.1 Constraints Phase (15 min)
- [ ] Open terminal in `Neo4j/schema/` directory
- [ ] Execute: `cypher-shell -u neo4j -p <password> -f 01_schema_constraints.cypher`
- [ ] Verify output: "No errors" or similar success message
- [ ] Expected output markers:
  - [ ] `Created constraint: entity_id_unique`
  - [ ] `Created constraint: human_qid_unique`
  - [ ] `Created constraint: claim_overall_confidence_required`
  - [ ] (60+ constraint creation messages total)
- [ ] Check database: Connect via browser → System database → node count should increase
- [ ] **STOP:** If any errors, consult SCHEMA_BOOTSTRAP_GUIDE.md "Troubleshooting" section

### 1.2 Indexes Phase (20 min)
- [ ] Execute: `cypher-shell -u neo4j -p <password> -f 02_schema_indexes.cypher`
- [ ] Verify output: "No errors"
- [ ] Expected output markers:
  - [ ] `Created index: entity_id_index`
  - [ ] `Created index: year_number_index`
  - [ ] `Created index: subject_facet_index`
  - [ ] (50+ index creation messages total)
- [ ] Monitor system resources: Indexing may use CPU/memory heavily
- [ ] Expected time: 5-10 minutes (cold database) to 1-2 minutes (subsequent runs)
- [ ] **STOP:** If timeout or errors, increase `--max-pool-size` or run async

### 1.3 Initialization Phase (10 min)
- [ ] Execute: `cypher-shell -u neo4j -p <password> -f 03_schema_initialization.cypher`
- [ ] Verify output: "No errors"
- [ ] Expected output markers:
  - [ ] `Created 4026 Year nodes`
  - [ ] `Created 16 FacetCategory nodes`
  - [ ] `Created 3 Place nodes`
  - [ ] `Created 3 Period nodes`
  - [ ] `Created 1 Human node: Julius Caesar`
  - [ ] `Created relationships`
- [ ] Check database: Browse Neo4j browser → database should show node types
- [ ] Sample verification queries (run in browser console):
  - [ ] `MATCH (y:Year) RETURN count(*);` → Should return 4026
  - [ ] `MATCH (f:FacetCategory) RETURN count(*);` → Should return 16
  - [ ] `MATCH (h:Human {name: "Julius Caesar"}) RETURN h;` → Should return 1 node

---

## Step 2: Schema Validation & Testing (45 min)

### 2.1 Constraint Verification (15 min)
Run each query in Neo4j browser (http://localhost:7474):

- [ ] **Test uniqueness enforcement:**
  ```cypher
  CREATE (e:Entity {entity_id: "e-test-duplicate", unique_id: "e-test-duplicate", 
    entity_type: "PERSON", label: "Test"})
  RETURN e;
  ```
  - Expected: Success (first creation)
  - Then repeat same CREATE → Expected: CONSTRAINT_VIOLATION error ✅
  - Cleanup: `MATCH (e:Entity {entity_id: "e-test-duplicate"}) DELETE e;`

- [ ] **Test required property constraint:**
  ```cypher
  CREATE (c:Claim {claim_id: "claim-test"})
  RETURN c;
  ```
  - Expected: CONSTRAINT_VIOLATION error (missing overall_confidence) ✅

### 2.2 Index Performance Verification (15 min)
- [ ] **Index presence check:**
  ```cypher
  SHOW INDEXES;
  ```
  - Expected: 50+ indexes listed
  - [ ] Verify `entity_id_index` present
  - [ ] Verify `year_number_index` present
  - [ ] Verify `human_qid_lookup` present

- [ ] **Index efficiency test (with timing):**
  ```cypher
  PROFILE MATCH (y:Year {year_number: 1066}) RETURN y;
  ```
  - Expected: Index hit ("Using index: year_number_index")
  - Execute time: < 50ms ✅

### 2.3 Data Integrity Check (15 min)
- [ ] **Year backbone integrity:**
  ```cypher
  MATCH (y:Year) WITH count(y) as total
  MATCH (y1:Year {year_number: -2000})-[:FOLLOWED_BY*]->
        (y2:Year {year_number: 2025})
  RETURN total, "Backbone valid" as status;
  ```
  - Expected: 4026 total years, backbone valid ✅

- [ ] **Facet category count:**
  ```cypher
  MATCH (f:FacetCategory) RETURN count(*) as facet_count;
  ```
  - Expected: 16 ✅

- [ ] **Julius Caesar test entity:**
  ```cypher
  MATCH (h:Human {name: "Julius Caesar"}) 
  RETURN h.entity_id, h.qid, h.viaf_id;
  ```
  - Expected: 1 node with properties ✅

---

## Step 3: Data Import Readiness (30 min)

### 3.1 Subject Import Pipeline Test
- [ ] Navigate to: `Python/fast/scripts/`
- [ ] Verify test data exists: `subjects_sample_50.jsonld`
  - [ ] File size: ~50KB+ (sanity check)
  - [ ] Contains valid JSONLD structure
- [ ] Execute test import:
  ```powershell
  python import_fast_subjects_to_neo4j.py "subjects_sample_50.jsonld" "test_output.cypher"
  ```
  - [ ] Process completes without errors
  - [ ] Output file created: `test_output.cypher` (2KB+)
  - [ ] Sample Cypher line inspection (first CREATE statement should have Subject node with properties)

- [ ] **Dry-run import to Neo4j:**
  ```powershell
  cypher-shell -u neo4j -p <password> -f test_output.cypher
  ```
  - [ ] No errors
  - [ ] Successfully imported 50 subjects
  - [ ] Verify in browser: `MATCH (s:Subject) RETURN count(*);` → 50

- [ ] Check Subject properties:
  ```cypher
  MATCH (s:Subject) LIMIT 1 RETURN properties(s);
  ```
  - [ ] Contains required fields: lcsh_id, label, authority_tier
  - [ ] Contains optional fields: facet scores ✅

### 3.2 Full Dataset Readiness (10 min)
- [ ] Verify FAST dataset available: `FASTTopical_parsed.csv` or `FASTTopical.marcxml`
  - [ ] File size: 50MB+ (typical FAST is 80-100MB)
  - [ ] Location documented in IMPLEMENTATION_ROADMAP.md
- [ ] Plan for full import:
  - [ ] Estimated rows: 100K+ LCSH subjects
  - [ ] Estimated import time: 30-60 minutes (if GPU-accelerated import available)
  - [ ] Disk space check: Neo4j database should have 2GB+ free space
- [ ] Documentation ready: `Python/fast/IMPORT_GUIDE.md` accessible for reference

### 3.3 Quality Metrics Baseline (10 min)
- [ ] **Capture baseline database stats before full import:**
  ```cypher
  MATCH (n) RETURN labels(n) as label, count(n) as count ORDER BY count DESC;
  ```
  - [ ] Record current node counts (for Phase 1 → Phase 2 diff comparison)
  - [ ] Documentation: Save to `metrics_baseline_phase1.txt`

---

## Step 4: Go/No-Go Decision (15 min)

### Success Criteria ✅

**All of the following must be true:**

- [ ] **Neo4j connectivity:** Can connect via cypher-shell & browser
- [ ] **Schema deployed:** 01, 02, 03 scripts executed without FATAL errors
- [ ] **Constraints active:** 60+ constraints exist & enforced
- [ ] **Indexes active:** 50+ indexes visible in SHOW INDEXES output
- [ ] **Bootstrap data:** 4,026 Year backbone intact, 16 Facets present, Julius Caesar test entity present
- [ ] **Performance verified:** Index queries execute in <50ms
- [ ] **Data integrity:** Year backbone linked (FOLLOWED_BY chain valid), facet relationships correct
- [ ] **Subject pipeline tested:** 50-subject sample imports cleanly to Neo4j
- [ ] **Documentation complete:** All guides accessible & referenced

### Go/No-Go Decision
- [ ] **GO:** All success criteria met → Proceed to Phase 2
- [ ] **NO-GO:** Any criteria failed → Debug using SCHEMA_BOOTSTRAP_GUIDE.md troubleshooting section

---

## Post-Launch Checklist (Phase 2 Prep)

Once Phase 1 completes:

- [ ] Document any deviations from expected results
- [ ] Update IMPLEMENTATION_ROADMAP.md: "Phase 1 completed on [DATE]"
- [ ] Mark Phase 2 start: "Federation Supercharging" (Step 4)
- [ ] Backup Neo4j database: `Neo4j/backup/chrystallum_postPhase1_[date].backup`
- [ ] Archive baseline metrics: `metrics_baseline_phase1.txt`
- [ ] Communicate Phase 2 readiness to team

---

## Troubleshooting Quick Reference

| Issue | Solution | Guide |
|-------|----------|-------|
| **Neo4j won't connect** | Check port 7687 open, Neo4j service running | SCHEMA_BOOTSTRAP_GUIDE.md: Installation |
| **Constraint creation fails** | Check for naming conflicts, drop existing constraints first | SCHEMA_BOOTSTRAP_GUIDE.md: Schema Troubleshooting |
| **Index creation hangs** | Run with `--max-pool-size 4` or increase timeout | SCHEMA_BOOTSTRAP_GUIDE.md: Performance Tuning |
| **Initialization creates no nodes** | Check for syntax errors in script, run line-by-line | SCHEMA_BOOTSTRAP_GUIDE.md: Debugging |
| **Subject import fails** | Verify JSONLD format, check Python environment | Python/fast/IMPORT_GUIDE.md |
| **Query returns 0 rows** | Verify data actually ingested, check node labels (case-sensitive) | SCHEMA_BOOTSTRAP_GUIDE.md: Verification Queries |

---

## Execution Timeline

| Phase | Task | Est. Time | Cumulative |
|-------|------|-----------|-----------|
| **Pre-Flight** | Environment & file verification | 30 min | 30 min |
| **Step 1** | Deploy schema (constraints → indexes → init) | 45 min | 1 hr 15 min |
| **Step 2** | Validation & testing | 45 min | 2 hr |
| **Step 3** | Data import readiness & quality baseline | 30 min | 2 hr 30 min |
| **Step 4** | Go/No-Go decision | 15 min | 2 hr 45 min |
| **Total** | Phase 1 completion | ~2.75 hrs | |

**Contingency buffer:** +30 min (debugging any single failure)  
**Maximum time:** ~3.5 hours

---

## Key Contacts & Resources

**Documentation:**
- Architecture spec: `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
- Implementation roadmap: `Neo4j/IMPLEMENTATION_ROADMAP.md`
- Schema guide: `Neo4j/schema/SCHEMA_BOOTSTRAP_GUIDE.md`
- Import guide: `Python/fast/IMPORT_GUIDE.md`
- This checklist: (current file)

**Neo4j Resources:**
- Online browser: http://localhost:7474 (after Neo4j starts)
- cypher-shell: Command-line interface to Neo4j
- Logs: Check Neo4j installation logs if service fails

**Python/Data:**
- FAST import: `Python/fast/scripts/import_fast_subjects_to_neo4j.py`
- Test data: `Python/fast/key/subjects_sample_50.jsonld`

---

## Sign-Off

**Pre-Flight Completed:** _________________ (Date/Time)  
**Schema Deployment Completed:** _________________ (Date/Time)  
**Validation Completed:** _________________ (Date/Time)  
**Go/No-Go Decision:** GO / NO-GO (circle one)  
**Phase 2 Ready:** Yes / No (date ready)  

---

**Generated:** 2026-02-13  
**Purpose:** Phase 1 execution guide  
**Next:** Phase 2 Federation Supercharging (See IMPLEMENTATION_ROADMAP.md)
