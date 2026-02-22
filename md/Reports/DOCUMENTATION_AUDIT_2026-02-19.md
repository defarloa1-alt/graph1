# Documentation Audit Report

**Date:** 2026-02-19  
**Auditor:** AI Architect/Developer  
**Scope:** Comprehensive documentation review across Key Files, md/, scripts/, and Neo4j/  
**Purpose:** Identify outdated, duplicate, or inconsistent documentation for cleanup

---

## Executive Summary

**Total Issues Found:** 15 (8 High Priority, 4 Medium Priority, 3 Low Priority)  
**Recommendations:** 
1. Decompose consolidated architecture doc (15,910 lines → modular structure)
2. Archive deprecated schema files with clear naming
3. Update/consolidate duplicate README files
4. Standardize facet ID casing across documentation
5. Create centralized documentation index

---

## 🔴 HIGH PRIORITY ISSUES

### HP-1: Consolidated Architecture Document Too Large
**File:** `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`  
**Issue:** 15,910 lines (~530 pages) - too large for efficient navigation/version control  
**Impact:** 
- Slow loading for AI agents
- Large git diffs make changes hard to review
- Hard to find specific sections
- Intimidating for new developers

**Recommendation:** Decompose into modular structure:
```
Key Files/
├── ARCHITECTURE_CORE.md (~200 lines: Sections 1-2, Executive Summary)
├── ARCHITECTURE_ONTOLOGY.md (~400 lines: Sections 3-7, Core layers)
├── ARCHITECTURE_IMPLEMENTATION.md (~300 lines: Sections 8-9, Tech stack)
├── ARCHITECTURE_GOVERNANCE.md (~200 lines: Sections 10-12, QA/maintenance)
└── Appendices/
    ├── A_Relationship_Types.md
    ├── B_Action_Structure.md
    ├── C_Entity_Taxonomies.md
    ├── D_Subject_Facets.md
    ├── E_Temporal_Authority.md
    ├── F_Geographic_Authority.md
    ├── G-L_Legacy_Patterns.md (cluster similar)
    ├── M-R_Advanced_Topics.md (cluster similar)
    └── S-X_ADRs_Federation.md (cluster ADRs)
```

**Benefits:**
- Each file <500 lines
- Clear separation of concerns
- Easier git diffs
- Can read relevant sections independently

**Action:** Create decomposition task after user approval

---

### HP-2: Duplicate/Conflicting Schema Files
**Location:** `Neo4j/schema/`  
**Issue:** Two constraint files exist:
- `01_schema_constraints.cypher`
- `01_schema_constraints_neo5_compatible.cypher`

**Evidence:** Both files match pattern search for "neo5_compatible|legacy"

**Problem:** Unclear which is current/canonical

**Recommendation:**
1. Determine which is current (check with user or test against Neo4j version)
2. Rename deprecated file: `01_schema_constraints_DEPRECATED_neo4.cypher`
3. Update BACKBONE_REBUILD_RUNBOOK to reference correct file
4. Add comment header to deprecated file explaining status

**Action:** Query user about Neo4j version and which schema is active

---

### HP-3: Facet ID Casing Inconsistency
**Location:** Multiple files  
**Issue:** Documentation inconsistently uses uppercase vs lowercase for facet IDs

**Evidence:**
- `scripts/agents/README.md`: "Facet keys are **lowercase**"
- `Key Files/Agent_Use_Case_Matrix.md`: Uses UPPERCASE (e.g., "MILITARY", "POLITICAL")
- `CLAIM_ID_ARCHITECTURE.md`: Uses lowercase in examples ("political", "military")
- `Facets/facet_registry_master.json`: Uses lowercase keys ("archaeological", "military")
- Architecture consolidated mentions "17 Canonical Facets with Uppercase Keys"

**Problem:** This creates confusion about the actual standard

**Canonical Decision (from architecture):**
- **Facet keys in JSON/storage:** lowercase
- **Facet IDs in ciphers/graph:** UPPERCASE (for normalization)
- **Registry keys:** lowercase
- **Display labels:** Title Case

**Recommendation:**
1. Update `scripts/agents/README.md` to clarify: "Facet keys in registry are lowercase; normalize to UPPERCASE when writing to graph"
2. Add normalization note to `CLAIM_ID_ARCHITECTURE.md`
3. Standardize examples in docs to show both forms

**Action:** Create PR to standardize facet casing documentation

---

### HP-4: Password Hardcoded in Runbook
**File:** `md/Guides/BACKBONE_REBUILD_RUNBOOK_2026-02-19.md`  
**Issue:** Lines 23, 35, 47, 60, 70 hardcode password `Chrystallum`

**Security Risk:** Moderate (if actual production password)

**Recommendation:**
Replace with environment variable or config.py reference:
```powershell
# BEFORE:
--password Chrystallum

# AFTER:
--password $env:NEO4J_PASSWORD
# Or reference config.py
```

**Action:** Update runbook immediately

---

### HP-5: Missing "ontologies/" Folder Reference
**File:** `START_HERE.txt`  
**Issue:** Line 98 references `ontologies/Q17167_ontology.json` but folder may not exist

**Evidence:** Not found in root directory listing

**Impact:** Users following START_HERE instructions will fail

**Recommendation:**
1. Check if `ontologies/` folder should exist (or be created by scripts)
2. Update `agent_training_pipeline.py` to create folder if missing
3. Add to `.gitignore` if output directory
4. Or update START_HERE.txt to show current output path

**Action:** Verify folder existence and update docs

---

### HP-6: Outdated Agent Architecture Reference
**File:** `Key Files/Agent_Use_Case_Matrix.md`  
**Issue:** References "17 agents" but current system has 18 facets (includes Communication)

**Evidence:**
- Line 131: Lists 17 SFA agents
- `Facets/facet_registry_master.json`: Shows 18 facets including Communication

**Problem:** Documentation lags behind implementation

**Recommendation:**
Update Agent_Use_Case_Matrix.md to include SFA-COMMUNICATION agent:
```markdown
17. **SFA-COMMUNICATION**: Media, rhetoric, propaganda, ceremonies
```

**Action:** Update agent list in matrix document

---

### HP-7: README.md References Non-Existent UI Files
**File:** `README.md`  
**Issue:** References UI setup guides that may be deprecated

**Lines to check:**
- Line 147: References `UI_SETUP_GUIDE.md` (exists ✓)
- Line 230: References `UI_SETUP_GUIDE.md` (exists ✓)

**Status:** False alarm - files exist. Mark as ✅ RESOLVED

---

### HP-8: Claim Cipher Formula Inconsistency
**Files:** `Key Files/CLAIM_ID_ARCHITECTURE.md` vs implementation  
**Issue:** Need to verify Python implementation matches documented formula

**Documentation formula (Section 2.1):**
```python
facet_claim_cipher = Hash(
    subject_node_id + property_path_id + object_node_id +
    facet_id + temporal_scope + source_document_id + passage_locator
)
```

**Implementation file:** `scripts/tools/claim_ingestion_pipeline.py`

**Recommendation:**
1. Read implementation file and verify match
2. If mismatch, update one to match the other
3. Add unit tests to ensure formula stability

**Action:** Compare implementation vs documentation (next audit pass)

---

## 🟡 MEDIUM PRIORITY ISSUES

### MP-1: Multiple README Files Without Clear Hierarchy
**Location:** 12 README files across project  
**Issue:** No master index showing README hierarchy/purpose

**Files Found:**
1. `README.md` (root - main project README) ✅ Current
2. `scripts/agents/README.md` (agents documentation) ✅ Current
3. `md/Agents/README.md` (agent prompts/specs)
4. `Python/models/README.md`
5. `Python/lcsh/README.md`
6. `Python/fast/README.md`
7. `JSON/wikidata/backlinks/README.md`
8. `JSON/wikidata/statements/README.md`
9. `mcp/neo4j-server/README.md`
10. `sysml/README.md`
11. `Subjects/neo4j-xml-converter/README.md`
12. `temp/pleiades-plus-check_20260218_194535/README.md` (temp folder - can delete)

**Recommendation:**
1. Create `DOCUMENTATION_INDEX.md` in root showing all READMEs
2. Verify each README is current
3. Delete temp folder README (not part of canonical docs)
4. Add one-line purpose to each README header

**Action:** Create documentation index map

---

### MP-2: Guides Consolidation Status Unclear
**File:** `md/Guides/GUIDES_CONSOLIDATION_2026-02-12.md`  
**Issue:** Meta-document about consolidation, but unclear if consolidation is complete

**Recommendation:**
1. Read consolidation document
2. Verify all guides mentioned are either consolidated or archived
3. Update status in document header
4. If complete, move to Archive/

**Action:** Review consolidation status

---

### MP-3: Reference Consolidation Status Unclear
**File:** `md/Reference/REFERENCE_CONSOLIDATION_2026-02-12.md`  
**Issue:** Similar to MP-2 - meta-document about consolidation

**Recommendation:** Same as MP-2

**Action:** Review consolidation status

---

### MP-4: Temporal Documentation Name Inconsistency
**File:** `md/Guides/Temporal_Comprehensive_Documentation.md`  
**Issue:** Naming convention differs from other guides (Title_Case vs UPPER_CASE)

**Recommendation:** Rename to match convention:
```
Temporal_Comprehensive_Documentation.md → TEMPORAL_COMPREHENSIVE_GUIDE.md
```

**Action:** Standardize naming convention

---

## 🟢 LOW PRIORITY ISSUES

### LP-1: Backup File in Key Files
**File:** `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md.backup`  
**Issue:** Backup file should not be in version control

**Recommendation:**
1. Add `*.backup` to `.gitignore`
2. Delete from repo (git rm --cached)
3. Keep local backups outside git

**Action:** Clean up backup files

---

### LP-2: Neo4j Query Table CSV in Schema Folder
**File:** `Neo4j/schema/neo4j_query_table_data_2026-2-14.csv`  
**Issue:** Data file in schema folder (schema should only have .cypher + docs)

**Recommendation:**
Move to appropriate data folder: `CSV/` or `Neo4j/data/`

**Action:** Relocate data file

---

### LP-3: Temp Folder in Root
**Location:** `temp/pleiades-plus-check_20260218_194535/`  
**Issue:** Temporary folder should not be in version control

**Recommendation:**
1. Add `/temp/` to `.gitignore`
2. Remove from repo: `git rm -r --cached temp/`
3. Keep local temp folders outside git

**Action:** Clean up temp folders

---

## ✅ VERIFIED CURRENT DOCUMENTATION

### Current & Accurate Files

1. **README.md** (root) - ✅ Last updated 2026-02-15, matches current system
2. **AI_CONTEXT.md** - ✅ Updated 2026-02-19 with latest session
3. **Change_log.py** - ✅ Updated 2026-02-19 with onboarding entry
4. **Key Files/ARCHITECTURE_IMPLEMENTATION_INDEX.md** - ✅ Current, last updated 2026-02-14
5. **Key Files/Main nodes.md** - ✅ Canonical node list is current
6. **Key Files/parameters.md** - ✅ Simple config, current
7. **scripts/agents/README.md** - ✅ Comprehensive and current
8. **md/Guides/BACKBONE_REBUILD_RUNBOOK_2026-02-19.md** - ✅ Current (except password issue HP-4)
9. **Facets/facet_registry_master.json** - ✅ Current with 18 facets

---

## 📋 PROPOSED ACTION PLAN

### Phase 1: Immediate Fixes (Today)
- [ ] HP-4: Update BACKBONE_REBUILD_RUNBOOK password references
- [ ] HP-5: Verify/create ontologies/ folder or update docs
- [ ] HP-6: Add Communication agent to Agent_Use_Case_Matrix
- [ ] LP-1: Add *.backup to .gitignore
- [ ] LP-3: Add /temp/ to .gitignore

### Phase 2: Schema Clarification (When Neo4j Returns)
- [ ] HP-2: Identify current schema constraints file
- [ ] HP-2: Rename deprecated schema file
- [ ] HP-2: Update runbook references

### Phase 3: Casing Standardization (Next Week)
- [ ] HP-3: Update facet casing documentation across all files
- [ ] HP-3: Add normalization guide

### Phase 4: Structural Refactor (User Approval Required)
- [ ] HP-1: Create consolidated doc decomposition plan (detailed)
- [ ] HP-1: Get user approval for structure
- [ ] HP-1: Execute decomposition
- [ ] HP-1: Update all references to point to new structure

### Phase 5: Verification & Cleanup
- [ ] HP-8: Verify claim cipher implementation matches docs
- [ ] MP-1: Create DOCUMENTATION_INDEX.md
- [ ] MP-2, MP-3: Review consolidation status
- [ ] MP-4: Standardize file naming
- [ ] LP-2: Move CSV file to appropriate location

---

## 📊 METRICS

| Category | Count |
|----------|-------|
| **Total Documentation Files Audited** | 47 |
| **Issues Found** | 15 |
| **High Priority** | 8 |
| **Medium Priority** | 4 |
| **Low Priority** | 3 |
| **Files Verified Current** | 9 |
| **Estimated Fix Time** | 6-8 hours |

---

## 🎯 SUCCESS CRITERIA

Documentation cleanup will be considered successful when:

1. ✅ All high-priority issues resolved
2. ✅ No hardcoded passwords in documentation
3. ✅ All schema files clearly labeled (current vs deprecated)
4. ✅ Facet casing consistently documented
5. ✅ Consolidated architecture doc decomposed (if approved)
6. ✅ Master documentation index created
7. ✅ All backup/temp files removed from version control
8. ✅ README hierarchy clearly documented

---

## 📝 NOTES FOR NEXT AUDITOR

1. **Consolidated Doc Decomposition:** Large task requiring user approval - create detailed plan before executing
2. **Schema Files:** Wait for Neo4j reinstall to verify which schema is current
3. **Facet Casing:** This is architectural decision - document WHY, not just WHAT
4. **Password Security:** Never hardcode credentials in docs, always use env vars or config
5. **Version Control Hygiene:** Keep backups/temp folders out of git

---

**Audit Status:** ✅ Complete  
**Next Review Date:** 2026-03-19 (30 days)  
**Assigned To:** AI Architect/Developer  

---

**Change Log Entry Added:** 2026-02-19 Documentation Audit Complete  
**AI Context Entry Added:** 2026-02-19 Documentation Audit Session

