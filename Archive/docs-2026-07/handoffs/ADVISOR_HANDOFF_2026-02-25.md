# Chrystallum — Advisor Handoff

**Date:** 2026-02-25  
**For:** New advisor ramping up  
**Status:** Post-DPRR baseline established. Project Mercury next (scope pending).

---

## Start Here

1. **Graph orientation** — Query the self-description node (Cypher below)
2. **This document** — Current state, pipeline, and priorities
3. **Baseline** — `docs/BASELINE_POST_DPRR_2026-02-25.md` (the numbers that matter)
4. **KANBAN** — LachyFS extension (Ctrl+Shift+P → "Open Kanban Board"); tasks in `.devtool/features/`, context in `.devtool/KANBAN_CONTEXT.md`

---

## Current Graph State (Post-DPRR)

| Metric | Value |
|--------|-------|
| Total nodes | 63,689 |
| Total edges | 53,148 |
| PERSON entities | 5,174 |
| MEMBER_OF edges | 9,053 |
| **Global scoped** | **91.1%** (was 13.6%) |
| **Global unscoped** | **8.9%** (was 86.4%) |

**Q899409 (Roman families)** — 5,272 entities, 100% scoped, 0% unscoped. Strongest cluster. DPRR federation made family network navigation viable.

**DPRR contribution:** 2,960 Group A merged, 1,916 Group C created; 6,928 relationship edges; 8,365 POSITION_HELD (Fasti layer). 1,916 persons unique to Chrystallum (not in Wikidata).

---

## Self-Description Query

```cypher
MATCH (c:Chrystallum)-[:HAS_SELF_DESCRIPTION]->(sd:SystemDescription)
RETURN sd.narrative, sd.federation_summary, sd.subject_summary,
       sd.federation_count, sd.subject_concept_count, sd.anchor_coverage_pct
```

---

## Data Pipeline (Current)

| Step | Script | Notes |
|------|--------|-------|
| Harvest | `scripts/tools/wikidata_backlink_harvest.py` | Backlink discovery; scoping via P1696, P1838, P1584, P6863 (DPRR) |
| Cluster assignment | `scripts/backbone/subject/cluster_assignment.py` | MEMBER_OF edges; use `--dprr-neo4j` to include DPRR entities |
| DPRR import | `scripts/federation/dprr_import.py` | Persons, posts, relationships; run bibliography sources first |
| Scoping advisor | `scripts/analysis/scoping_advisor_report.py` | Reads `member_of_edges.json`; reports per-cluster scoping |
| System description | `scripts/backbone/system/generate_system_description.py` | Regenerates self-description from graph |

**Key paths:**
- Harvest reports: `output/backlinks/*_report.json`
- Cluster assignment: `output/cluster_assignment/member_of_edges.json`
- Scoping report: `output/analysis/scoping_advisor_report.md`
- Harvest summary: `output/backlinks/harvest_run_summary.json`

---

## What This Unlocks (Now)

- **Family network navigation** — "Show me the Cornelii" or "trace Sempronii–Aemilii connections" with real data
- **Persona salience weights** — Prosopographer and serious reader personas can use family density
- **Fasti layer** — 8,365 POSITION_HELD edges (who held which office, when; Broughton-sourced)

---

## Remaining Gaps (Non-Urgent)

| Gap | Notes |
|-----|-------|
| Status assertions | 1,992 senatorial/equestrian class records not imported |
| Group C POSITION_HELD | 1,442 office records for Group C persons |
| 8.9% unscoped | ~5,600 entities; noise audit to separate legitimate from noise |
| Self-describing subgraph | `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN.md` — Structure vs Process, cleanup phases |

---

## Design Debt (Still Relevant)

**subject_id architecture** — Legacy `subj_rr_*` keys in `load_roman_republic_ontology.py` are hand-authored. Proposed: QID-derived `subj_Q17167_{anchor_qid}`. Do before building SFAs. See `Federation/CHRYSTALLUM_HANDOFF.md` (legacy) for full detail.

---

## Next Focus: Cleanup (Mercury on hold)

- Re-run cluster assignment to fix 7,137 MEMBER_OF edges that failed (external_ids fix applied)
- Node label audit — run `scripts/analysis/audit_node_labels.cypher`
- KANBAN lists OCD alignment, entity type refinement, SFA prompts as ready items

---

## Self-Describing Subgraph Cleanup (2026-02-25)

**Federation count resolved:** 13 distinct Federation nodes, no duplicates. The 69 in diagnostics came from path-based query scope (Chrystallum-connected labels), not duplicate nodes.

**Approved deletions:** Period (1,077), GeoCoverageCandidate (357), PeriodCandidate (1,077), PlaceTypeTokenMap (212), FacetedEntity (360) — ~3,083 nodes in one script. Option B: temporal_anchor model; PeriodO on-demand only.

**PropertyMapping:** Wire into SchemaRegistry branch; do not move to config. (706 nodes, HAS_PRIMARY_FACET to Facet; pipeline queries at runtime.)

**Dev message:** Good findings. Approved to run cleanup script. Federation investigation complete; no hold.

---

## Files to Read

| File | Purpose |
|------|---------|
| `docs/BASELINE_POST_DPRR_2026-02-25.md` | Formal baseline numbers |
| `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN.md` | Structure vs Process, SchemaRegistry, FederationRegistry, cleanup phases |
| Kanban (extension) | Current priorities and done list; `.devtool/features/` |
| `AI_CONTEXT.md` | Session handover log (long; skim for recent) |
| `docs/HARVESTER_SCOPING_DESIGN.md` | Scoping rules |
| `Federation/CHRYSTALLUM_HANDOFF.md` | Legacy handoff (ITGAR, Fischer, governance — specified but not built) |
| `docs/SELF_DESCRIBING_SUBGRAPH_DESIGN_2026-02-25.md` | Self-describing subgraph design — structure agreed, build not started; node audit and open GeoCoverageCandidate issue |
| `docs/OCD_INTEGRATION_NOTES_2026-02-25.md` | OCD 1949 integration — extraction pipeline, Wikidata mapping strategy, taxonomy gaps, all pending |
| `docs/SFA_CONSTITUTION_NOTES_2026-02-25.md` | SFA constitution architecture — three-layer model, per-SFA document list, Syme index extraction plan, reading list as Layer 3 library |

---

## Quick Commands

```powershell
# Scoping advisor (after cluster assignment)
python scripts/analysis/scoping_advisor_report.py

# Cluster assignment with DPRR (use --dprr-all for full baseline)
python scripts/backbone/subject/cluster_assignment.py `
  --harvest-dir output/backlinks `
  --summary output/backlinks/harvest_run_summary.json `
  --output-dir output/cluster_assignment `
  --dprr-neo4j --dprr-all --cypher --write

# Node label audit (run in Neo4j)
# scripts/analysis/audit_node_labels.cypher

# Self-describing subgraph diagnostics (run in Neo4j)
# scripts/analysis/self_describing_subgraph_diagnostics.cypher

# Self-describing subgraph cleanup (dry-run first)
python scripts/neo4j/self_describing_subgraph_cleanup.py --dry-run
python scripts/neo4j/self_describing_subgraph_cleanup.py
```

---

*Replaces Federation/CHRYSTALLUM_HANDOFF.md for advisor ramp-up. Legacy handoff retained for ITGAR/governance spec.*
