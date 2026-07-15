# Handoff to Hub Dev — 2026-03-03

**Context:** Local dev has access to Neo4j and full repo. Hub dev has limited access. This captures what was done locally and what the hub dev should know.

---

## Done locally (you can pull/merge)

### 1. `scripts/tools/graph_census.py`
- Created locally (you may have created a version on another branch).
- Queries SYS_*, domain labels, relationship counts, federation sources, decision tables, etc.
- Outputs markdown or JSON. Run: `python -m scripts.tools.graph_census -o output/census.md`
- If you have a different version, merge and reconcile.

### 2. `scripts/tools/export_jsx_data.py`
- Created locally (item 5 from practical alignment).
- Dumps JSON for JSX: federation sources, SYS/domain counts, metrics.
- Run: `python -m scripts.tools.export_jsx_data -o output/jsx_architecture_data.json`
- JSX layout stays hand-crafted; this provides graph-backed data for when it’s wired up.

### 3. `docs/PRACTICAL_ALIGNMENT_2026-03-03.md`
- Updated to reflect both scripts as done.
- SYS_ gaps: migration run (item 3 done). Block catalog deprecation: done (item 4).

---

## D-table collision — one more case

You renumbered person domain D15→D30, D16→D31, D17→D32. There is another D15:

- **`Key Files/3-1-26-17_co_occurrence_layer.cypher`** — D15 = predicate refinement (co-occurrence pipeline, D8→D15→D10).
- This is separate from federation D15 and person D30.
- May need its own ID (e.g. D40+) if we want a single global namespace. Or leave as-is if co-occurrence is a different subsystem.

---

## Remaining work (priority order)

1. ~~**SYS_ gaps**~~ — Done (migration run 2026-03-03).
2. ~~**Block catalog deprecation**~~ — Done. Block catalog references `graph_census`; manual counts deprecated.
3. **JSX import** — When build supports it, have JSX import `output/jsx_architecture_data.json` (or equivalent path).

---

## Files to pull

- `scripts/tools/graph_census.py`
- `scripts/tools/export_jsx_data.py`
- `scripts/neo4j/sys_gaps_migration.cypher`
- `sysml/BLOCK_CATALOG_RECONCILED.md`
- `docs/PRACTICAL_ALIGNMENT_2026-03-03.md`
- `docs/HANDOFF_TO_HUB_DEV_2026-03-03.md` (this file)
