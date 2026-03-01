# File Organization Plan - Incremental Cleanup

**Created:** 2026-02-22  
**PM:** AI PM Agent  
**Approach:** Incremental (Option C) - Move files as we touch them

---

## 🎯 **Strategy: Incremental, Not Disruptive**

**Principle:** Don't reorganize everything at once (too disruptive)

**Approach:**
- Move files incrementally as we edit/update them
- Keep AI_CONTEXT.md in root (coordination hub)
- Keep scripts/ folder unchanged (already organized)
- Keep REQUIREMENTS.md in root (visibility); Kanban in LachyFS extension (`.devtool/features/`)

---

## 📁 **Target Structure**

### **Root (Minimal - ~15 files)**
```
AI_CONTEXT.md              (coordination hub - STAYS)
Kanban                     (LachyFS extension, .devtool/features/ - no KANBAN.md)
REQUIREMENTS.md            (requirements - STAYS)
README.md                  (project overview)
requirements.txt           (Python deps)
.gitignore, .gitattributes
[2-3 launcher scripts]
```

### **docs/ (Organized Documentation)**
```
docs/
├── project-management/    (PM plans, QA reports, BA docs)
├── setup/                 (setup guides, MCP setup)
├── analysis/              (Roman Republic analysis, period charts)
├── sessions/              (session summaries)
├── reference/             (dictionaries, specifications)
└── ai-context/            (future: daily logs, not yet)
```

---

## 🔄 **Migration Rules**

### **When to Move a File:**
1. You're editing the file (already have it open)
2. File is creating new version (move old to archive)
3. File is duplicate (consolidate and move)

### **How to Move:**
```bash
# Create folder if needed
mkdir -p docs/project-management

# Move file (git mv preserves history)
git mv FILE.md docs/project-management/FILE.md

# Update any references
# (search for old path, update to new)

# Commit with clear message
git commit -m "Organize: Moved FILE.md to docs/project-management/"
```

### **Update References:**
- Check if file is referenced in other docs
- Update paths (use relative paths)
- Test links still work

---

## 📋 **File Move Queue (Prioritized)**

### **Batch 1: PM/QA Docs** (Next time you edit them)
```
PROJECT_PLAN_2026-02-20.md → docs/project-management/
PM_COMPREHENSIVE_PLAN_2026-02-20.md → docs/project-management/
QA_RESULTS_SUMMARY.md → docs/project-management/
BA_ACTION_ITEMS_FROM_ARCHITECTURE_REVIEW.md → docs/project-management/
```

### **Batch 2: Setup Docs** (Next time you edit them)
```
CURSOR_MCP_SETUP.md → docs/setup/
DEV_AGENT_SCHEMA_EXECUTION_GUIDE.md → docs/setup/
```

### **Batch 3: Analysis Docs** (As needed)
```
ROMAN_REPUBLIC_Q17167_COMPLETE_PROPERTIES.md → docs/analysis/
HISTORICAL_PERIOD_BACKLINKS_ANALYSIS.md → docs/analysis/
[~20 more analysis files] → docs/analysis/
```

### **Batch 4: Archive Duplicates** (Low priority)
```
Old PM plan revisions → Archive/
Old MCP setup versions → Archive/
Old analysis versions → Archive/
```

---

## ⚠️ **What NOT to Move**

**Keep in Root:**
- ✅ AI_CONTEXT.md (coordination hub)
- ✅ Kanban (extension; .devtool/features/)
- ✅ REQUIREMENTS.md (visibility)
- ✅ README.md (entry point)

**Keep Structure:**
- ✅ scripts/ (already well-organized)
- ✅ md/ (already well-organized)
- ✅ data folders (CSV/, Temporal/, Geographic/, etc.)

---

## 📝 **Tracking Progress**

**KANBAN Backlog Item:**
```
- [ ] Incremental File Organization #low
  - Approach: Move files as we edit them
  - Target: 90 → 15 files in root
  - Progress: Track in this card
  - No disruption to active work
```

**Metrics:**
- Current root files: ~90
- Target root files: ~15
- Progress: Track moves in git commits

---

## ✅ **Benefits**

**Short Term:**
- Cleaner root directory
- Easier to find files
- Better organization

**Long Term:**
- Scalable structure
- Clear patterns
- Easy maintenance

**No Disruption:**
- Incremental approach
- Move as we touch files
- Active work not blocked

---

**Saved to:** `docs/FILE_ORGANIZATION_PLAN.md`

**AI_CONTEXT updated with notice for other agents!** ✅
