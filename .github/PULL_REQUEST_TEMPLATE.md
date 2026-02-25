## PR — Cloud Agent / Dev

**Task reference:** (e.g. `tasks/ROUND3_D10_D8_REFACTOR.md`)  
**DECISIONS.md entry:** (e.g. D-032)

---

### Pre-merge checklist

- [ ] **AGENTS.md compliance:** No files created outside task scope. No Docker, Node.js, or inferred dependencies.
- [ ] **Model-first:** If block catalog or DMN tables were updated, they were updated *before* code changes.
- [ ] **Threshold/Policy:** No hardcoded values. Scripts read from SYS_Threshold / SYS_Policy (or MCP).
- [ ] **Acceptance test:** `grep` confirms no hardcoded threshold/policy values in modified scripts.
- [ ] **Catalog match:** Implementation matches block catalog entries for any modified blocks.

---

### Changes in this PR

(Describe what was changed and why.)
