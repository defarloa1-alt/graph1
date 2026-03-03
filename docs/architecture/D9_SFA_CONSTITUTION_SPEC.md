# D9 — SFA Constitution Layer Spec

**Purpose:** Map each facet to its constitution layer — the graph structure that governs SFA interpretation for that facet.  
**Status:** D9 table exists with `status: 'placeholder'`. This spec defines what fills it.  
**Input:** SFA export (36 schema nodes, 859 bibliography, rationale) from `sfa_qid_explorer.py` → `sfa_export_llm.json`

---

## D9 Decision Table Structure

| Field | Value |
|-------|-------|
| **table_id** | `D9_DETERMINE_SFA_constitution_layer` |
| **inputs** | `['facet']` |
| **outputs** | `['constitution_doc_ids']` — or extended to `['constitution_schema_ref', 'scope_boundary_ref']` |
| **hit_policy** | UNIQUE (one row per facet) |
| **consumers** | SFA constitution loader, SFA agents, D5/D8 boundary evaluation |

### Row structure (per facet)

| Column | Type | Description |
|--------|------|--------------|
| row_id | String | D9_R01, D9_R02, … |
| conditions | JSON | `{"facet": "POLITICAL"}` |
| outputs | JSON | `{"constitution_doc_ids": ["..."], "scope_boundary": "..."}` |
| action_detail | String | Human-readable note |

---

## What the Constitution Layer Contains

1. **Schema node mapping** — 36 nodes → existing types:
   - 7 disciplines → `Discipline` (Q191600 "civil and political rights" already in DisciplineRegistry)
   - 7 LCC codes → `LCC_Class`
   - 10 LCSH headings → `LCSH_Heading`
   - 12 entities → `Organization` (Senate, assemblies, Republic, Carthage-as-polity), `Place` (Rome, Carthage, Athens, Byzantium), `Event` (Caesar's Civil War, Deposition), `Position` (Roman emperor)

2. **SubjectConcept wiring** — Disciplines and LCSH provide scholarly framing for 61 existing SubjectConcepts. Relationship: `FRAMES` or `INTERPRETS`. Example: "constitutional history" (discipline) → "Government & Constitutional Structure" (SubjectConcept Q7188).

3. **Relationship grammar** — 20 POLITICAL relationship types in SYS_RelationshipType (POSITION_HELD, CONTROLLED, LEGITIMATED, REFORMED, FOUNDED, etc.) + 25 Wikidata property mappings (P35, P194, P530, …). SFA maps which verb combinations are valid within the facet's scope boundary.

4. **Scope boundary** — The rationale's "unless" clause: *"Items primarily belonging to legal doctrine, social stratification, artistic production, or military operations are excluded UNLESS they served as direct mechanisms of political authority."* This is the boundary-case logic for D5 (scope match) and D8 (facet assignment).

---

## Data Flow

```
SFA export (sfa_export_llm.json)
    ├── meta (facet, seed_qid, sfa_rationale, counts)
    ├── schema_nodes (disciplines, LCC, LCSH, entities)
    ├── subject_concept_wiring (61 SubjectConcepts, wiring_guidance)
    ├── bibliography (859 entries)
    └── online_texts
    ↓
D9 population (manual or LLM-assisted)
    ├── facet → constitution_doc_ids (or schema_ref)
    ├── facet → scope_boundary (rationale excerpt)
    └── facet → subject_concept_mappings (discipline/LCSH → SubjectConcept qid)
    ↓
SFA constitution loader
    → Writes SYS_FacetConstitution or equivalent nodes
    → Wires schema nodes to graph
    → D5/D8 read scope_boundary for boundary-case evaluation
```

---

## Implementation Notes

- **D9 rows** currently placeholder: POLITICAL, MILITARY, SOCIAL with stub doc IDs. Replace with real constitution_doc_ids or schema_ref once mapping is designed.
- **SYS_FacetConstitution** (or similar) — Proposed node type to hold per-facet constitution structure. Properties: `facet`, `scope_boundary`, `schema_node_count`, `subject_concept_wiring_ref`.
- **LLM export** — `sfa_export_llm.json` now includes `subject_concept_wiring` section (61 SubjectConcepts, wiring_guidance) for independent LLM to propose schema consolidation and D9 population.
