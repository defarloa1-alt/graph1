# Practical Alignment — 2026-03-03

**Purpose:** Align dev work across sessions. Non-graphical, actionable steps.

---

## Completed (other dev)

### 1. D-table collision fix ✓
- **Problem:** Graph D15–D21 (federation scoring) and DMN doc D15–D17 (person domain) meant different things.
- **Solution:** Renumbered person tables D15→D30, D16→D31, D17→D32.
- **Files updated:** DMN index, detailed sections, implementation notes, block catalog, sysml README, JSX alignment patch.
- **ID scheme:** D1–D14 core, D15–D21 federation scoring, D30–D39 person domain.

### 2. graph_census.py ✓
- **Path:** `scripts/tools/graph_census.py`
- **What it does:** Queries SYS_* types, domain labels, relationship counts, federation sources, decision tables, thresholds, policies, ADRs, onboarding steps, authority/confidence tiers, node types. Outputs markdown or JSON.
- **Usage:** `python -m scripts.tools.graph_census` or `python -m scripts.tools.graph_census -o census.md`
- **Replaces:** Hand-maintained BLOCK_CATALOG_RECONCILED.md for counts.

---

## Remaining (priority order)

### 3. Fill 4 SYS_ gaps in the graph
- Add ADR-007 and ADR-008 to SYS_ADR (currently only 001–006)
- Set `layer` property on SYS_AgentType nodes (currently all null)
- Register missing node types in SYS_NodeType (only 10 of ~25+ actual labels)
- Add SYS_HarvestPlan type registration

### 4. Deprecate block catalog as hand-maintained ✓
- Replaced with census script output. Block catalog now references `graph_census` for all counts.
- DMN_DECISION_TABLES.md retained as design layer.

### 5. JSX data as build artifact ✓
- **Path:** `scripts/tools/export_jsx_data.py`
- Dumps JSON to `output/jsx_architecture_data.json` (federation sources, SYS/domain counts, metrics)
- Run: `python -m scripts.tools.export_jsx_data -o output/jsx_architecture_data.json`
- JSX can import this JSON; layout stays hand-crafted

---

## Quick reference

| Item | Status | Notes |
|------|--------|-------|
| D-table collision | Done | Person domain D30–D32 |
| graph_census.py | Done | Run instead of hand-maintaining counts |
| export_jsx_data.py | Done | JSON for JSX; run before build |
| SYS_ gaps in graph | Pending | 4 items |
| Block catalog deprecation | Done | Census output; block catalog references graph_census |
| export_jsx_data.py | Pending | JSX imports from graph |
