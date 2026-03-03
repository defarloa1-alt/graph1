# Handoff to Hub Dev — 2026-03-03

**Context:** Local dev has access to Neo4j and full repo. Hub dev has limited
access. This captures what was done locally and what the hub dev should know.

---

## Done locally (you can pull/merge)

### 1. `scripts/tools/graph_census.py`
- Queries SYS_*, domain labels, relationship counts, federation sources,
  decision tables, etc.
- Outputs markdown or JSON.
- Run: `python -m scripts.tools.graph_census -o output/census.md`

### 2. `scripts/tools/export_jsx_data.py`
- Dumps JSON for JSX: federation sources, SYS/domain counts, metrics.
- Run: `python -m scripts.tools.export_jsx_data -o output/jsx_architecture_data.json`
- JSX layout stays hand-crafted; this provides graph-backed data for when
  it's wired up.

### 3. `scripts/neo4j/sys_gaps_migration.cypher`
- Idempotent Cypher migration to close SYS_ gaps.
- Adds ADR-003, ADR-007, ADR-008 to SYS_ADR.
- Sets name/layer on all 5 SYS_AgentType nodes.
- Registers 29 missing SYS_NodeType entries.
- Creates SYS_HarvestPlan stub for Person domain.
- Run against Neo4j when ready.

### 4. `docs/PRACTICAL_ALIGNMENT_2026-03-03.md`
- Updated tracker reflecting all items above.

---

## D-Table Collision — Resolved

Co-occurrence layer script (`Key Files/3-1-26-17_co_occurrence_layer.cypher`)
originally used **D15** for predicate refinement. Collides with live graph's
`D15_DETERMINE_federation_state`. Person domain D15/D16/D17 were already
renumbered to D30/D31/D32.

**Fix:** Co-occurrence D15 renumbered to **D40** in the cypher file.
- `D15` → `D40` (table_id)
- `D15_R01`–`D15_R05` → `D40_R01`–`D40_R05` (row IDs)
- Pipeline wiring: D8 → D40 → D10 (unchanged semantically)
- ADR-008 summary updated to reference D40.

---

## Remaining Work (priority order)

1. **Run SYS_ gaps migration** — Execute `sys_gaps_migration.cypher` against
   Neo4j. Verify with queries in the file footer.
2. **Block catalog deprecation** — Use census output instead of
   hand-maintaining counts.
3. **JSX import** — When build supports it, wire JSX to import
   `output/jsx_architecture_data.json`.

---

## Files in this delivery

| File | Status |
|------|--------|
| `scripts/tools/graph_census.py` | Existing — unchanged |
| `scripts/tools/export_jsx_data.py` | New |
| `scripts/neo4j/sys_gaps_migration.cypher` | New |
| `docs/PRACTICAL_ALIGNMENT_2026-03-03.md` | New |
| `docs/HANDOFF_TO_HUB_DEV_2026-03-03.md` | New (this file) |
| `Key Files/3-1-26-17_co_occurrence_layer.cypher` | Edited (D15→D40) |
