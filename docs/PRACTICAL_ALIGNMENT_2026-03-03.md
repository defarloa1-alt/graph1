# Practical Alignment Tracker — 2026-03-03

**Goal:** Close the gap between architecture docs and the live graph.

---

## Item 1 — Graph Census Script
**Status:** DONE
**File:** `scripts/tools/graph_census.py`
**Run:** `python -m scripts.tools.graph_census -o output/census.md`
Queries all SYS_* types, domain labels, relationship counts, federation sources,
decision tables, thresholds, policies, ADRs, onboarding steps, authority/confidence
tiers, and registered node types. Outputs markdown or JSON.

---

## Item 2 — JSX Architecture Data Export
**Status:** DONE
**File:** `scripts/tools/export_jsx_data.py`
**Run:** `python -m scripts.tools.export_jsx_data -o output/jsx_architecture_data.json`
Dumps JSON payload for JSX dashboard: federation sources, SYS/domain counts,
decision tables, policies, thresholds, ADRs. JSX layout stays hand-crafted;
this provides graph-backed data for when the import is wired up.

---

## Item 3 — SYS_ Gaps
**Status:** MIGRATION SCRIPT READY
**File:** `scripts/neo4j/sys_gaps_migration.cypher`

Gaps identified and addressed:

| Gap | Detail | Migration action |
|-----|--------|-----------------|
| Missing ADRs | ADR-003, ADR-007, ADR-008 not in graph | MERGE into SYS_ADR |
| SYS_AgentType identity | All 5 have name=null, layer=null | SET name, agent_type_id, layer |
| SYS_NodeType coverage | 10 registered vs 40 domain labels | MERGE 29 missing types |
| SYS_HarvestPlan | Label does not exist | MERGE stub for Person domain |

Run the migration Cypher against Neo4j to close these gaps.

---

## Item 4 — Block Catalog Deprecation
**Status:** PENDING
**Depends on:** Item 1 (census script).
Once census output is validated against the live graph, replace hand-maintained
block catalog counts with census-generated numbers. The census markdown can serve
as the canonical count reference.

---

## Item 5 — D-Table Collision Fix
**Status:** DONE
**File:** `Key Files/3-1-26-17_co_occurrence_layer.cypher` (edited)

The co-occurrence layer script originally used `D15` for predicate refinement,
which collides with the live graph's `D15_DETERMINE_federation_state`.
Person domain tables were previously renumbered (D15→D30, D16→D31, D17→D32).
Co-occurrence D15 has been renumbered to **D40** (D40_predicate_refinement,
rows D40_R01–D40_R05) and the pipeline wiring updated (D8→D40→D10).

---

## Item 6 — JSX Import Wiring
**Status:** PENDING
When build supports it, have JSX import `output/jsx_architecture_data.json`
or equivalent. No code change until the build pipeline is in place.
