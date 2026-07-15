# Deprecated: Chrystal 2.0 (Aura instance `0da8c4a3`)

**Status:** DEPRECATED as of 2026-07-14  
**Canonical instance:** `ac63a8e5` (`neo4j+s://ac63a8e5.databases.neo4j.io`)

---

## What Chrystal 2.0 was

A separate Neo4j Aura sandbox (created 2026-03-10) for an experimental schema:

- Facet curriculum graph (FacetRegistry → Facet → DisciplineSource → CourseSyllabus → Lecture)
- DI training outputs as `SubjectConcept` nodes with `status: proposed`
- Wiki concept map layer (`scripts/v2/write_concept_graph.py`)

It was **not** a migration of the production Chrystallum graph. It had ~920 nodes and no `Chrystallum` root, no `SYS_*` governance layer, and no federation entity data (Person, Place, DPRR, Pleiades).

---

## Why deprecated

- Split brain: root `.env` pointed at 0da8c4a3 while architecture docs and federation work assumed ac63a8e5.
- Production graph (153k nodes, rules-in-graph, MEMBER_OF wiring) lives on **ac63a8e5** only.
- v2 schema was never merged into the canonical ontology.

---

## Exported before shutdown

| File | Contents |
|------|----------|
| `output/deprecated_chrystal20/manifest.json` | Label counts, export metadata |
| `output/deprecated_chrystal20/proposed_subject_concepts.json` | 43 DI-proposed SubjectConcepts |
| `output/deprecated_chrystal20/sfa_artifacts.json` | SFA_Claim, SFA_SubScope, SFA_TrainingInsight nodes |

To promote proposals into the canonical graph: validate against ADR-020 (CCS), then MERGE via `propose.py` on **ac63a8e5**.

---

## Deprecated code paths

| Path | Notes |
|------|-------|
| `scripts/v2/*` | Chrystal 2.0–targeted scripts; do not run against production |
| `scripts/bootstrap/facet_curriculum.py` | Duplicate of v2 facet curriculum bootstrap |
| `Key Files/chrystallum_schema_backbone.jsx` | Viewer for v2 curriculum graph only |
| `Neo4j-0da8c4a3-Created-2026-03-10.txt` | Instance credentials (archive only) |

Wiki concept map **JSON** in `output/wiki_concept_maps/` remains useful; re-ingest via canonical pipeline if needed, not via `write_concept_graph.py` as-is.

---

## Manual steps (Aura + Railway)

1. **Confirm** root `.env` uses `ac63a8e5` (done in repo).
2. **Railway** (if deployed): set `NEO4J_URI` / `NEO4J_PASSWORD` to ac63a8e5 in the service env vars.
3. **Neo4j Aura console:** pause or delete instance `0da8c4a3` (Chrystal 2.0) when export is verified.
4. **Viewer:** `VITE_CYPHER_API_URL` → Railway MCP should now query ac63a8e5 after Railway env update.

---

## Canonical config

```env
NEO4J_URI=neo4j+s://ac63a8e5.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<ac63a8e5 password>
AURA_INSTANCEID=ac63a8e5
```

See `docs/ARCHITECTURE_CURRENT.md` for live graph inventory and active pipelines.
