# Subject Facet Agent — Visual Console & I/O Contract

**Status:** Draft 2026-03-02  
**Context:** Reviewer advice on using the Discipline Universe JSX as the agent's visual/operational console, plus identified gaps.

---

## 1. Agent Console Workflow (from review)

The Discipline Universe (`chrystallum_discipline_universe.jsx`, `chrystallum_discipline_universe_v2.jsx`) is the agent's **visual/operational console**:

1. **Establish scope** — Read `FACET_COLOR` and facet list as the facet registry.
2. **Run facet→discipline map** — CQ-02: input facet label → disciplines whose `facets` or `primary_for` contain it.
3. **Inspect three views** — discipline-facet (PRIMARY_FOR vs SUPPORTS), hierarchy (LCC), federation (TEACHES_VIA).
4. **Decide federation sources** — From REPOS templates, select and parameterize URLs.
5. **Use canned Cypher as API** — CQ-01 through CQ-05.
6. **Use D3 graph as planning surface** — Node color, `in_graph`, edge types encode status.

---

## 2. JSON I/O Contract — Subject Facet Agent

### Request schema

```json
{
  "request_id": "uuid",
  "facet_label": "Political",
  "mode": "harvest_plan",
  "constraints": {
    "discipline_qids": ["Q830852", "Q36442"],
    "max_disciplines": 10,
    "prioritize_primary_for": true,
    "exclude_repos": ["JSTOR_SEARCH"]
  },
  "context": {
    "seed_entity_qid": "Q17167",
    "campaign_id": "optional-batch-id"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `facet_label` | string | Must match `FACET_COLOR` keys (Political, Military, etc.) |
| `mode` | enum | `scope` \| `harvest_plan` \| `status_snapshot` |
| `constraints.discipline_qids` | string[] | Optional filter to specific disciplines |
| `constraints.max_disciplines` | int | Cap on disciplines to return |
| `constraints.prioritize_primary_for` | bool | Rank disciplines where facet is primary higher |
| `constraints.exclude_repos` | string[] | REPOS keys to skip |

### Response schema — `mode: "scope"`

```json
{
  "request_id": "uuid",
  "facet_label": "Political",
  "facet_color": "#1A3A5C",
  "discipline_universe": [
    {
      "qid": "Q830852",
      "label": "history of ancient Rome",
      "role": "primary",
      "in_graph": true,
      "needs_harvest": false,
      "facet_count": 13,
      "lcc": "DG200-DG365",
      "repos": ["OPENALEX_WORKS", "PERSEUS", "OPEN_LIBRARY", "JSTOR_SEARCH", "INTERNET_ARCHIVE", "HATHI_TRUST"]
    }
  ],
  "total_disciplines": 42
}
```

### Response schema — `mode: "harvest_plan"`

```json
{
  "request_id": "uuid",
  "facet_label": "Political",
  "harvest_jobs": [
    {
      "job_id": "uuid",
      "discipline_qid": "Q180536",
      "discipline_label": "economic history",
      "facet_role": "secondary",
      "priority_score": 0.72,
      "urls": [
        {
          "repo": "OPENALEX_WORKS",
          "url": "https://api.openalex.org/works?filter=concepts.id:C2776944186&sort=cited_by_count:desc&per_page=25",
          "params": { "oa_id": "C2776944186", "label": "economic history", "slug": "economic-history", "lcsh": "sh85040830" }
        }
      ],
      "status": "pending"
    }
  ],
  "facet_discipline_snapshot": { "discipline_count": 10, "primary_count": 3, "harvest_gap_count": 7 }
}
```

### Response schema — `mode: "status_snapshot"`

```json
{
  "request_id": "uuid",
  "facet_label": "Political",
  "coverage": {
    "disciplines_total": 42,
    "disciplines_in_graph": 28,
    "disciplines_needs_harvest": 14,
    "harvest_jobs_pending": 5,
    "harvest_jobs_completed": 12
  },
  "graph_ready_for_ui": true
}
```

`graph_ready_for_ui: true` means the agent has emitted an updated facet→discipline snapshot that the React/D3 layer can render (e.g. via a shared store or Neo4j write).

---

## 3. Harvest Job Schema (addresses gap #6)

```json
{
  "job_id": "uuid",
  "discipline_qid": "Q830852",
  "facet_label": "Political",
  "repo_key": "OPENALEX_WORKS",
  "url": "https://api.openalex.org/works?filter=concepts.id:C2779756987&...",
  "status": "pending",
  "created_at": "ISO8601",
  "completed_at": null,
  "campaign_id": "optional"
}
```

**Status values:** `pending` | `running` | `completed` | `failed` | `skipped`

This schema can live as:
- A `HarvestJob` node in Neo4j, or
- A JSON file in `output/facet_harvest_jobs/{facet_label}/`, or
- Both (Neo4j for coordination, file for pipeline consumption).

---

## 4. Gap Assessment

### Gaps identified by reviewer

| # | Gap | Severity | Mitigation |
|---|-----|----------|------------|
| 1 | No explicit agent I/O contract | High | JSON schemas above; add to STACK in JSX |
| 2 | `needs_harvest` is global, not per-facet | High | Add `(Discipline)-[:NEEDS_HARVEST_FOR {facet}]->(Facet)` or `discipline.needs_harvest_by_facet: {Political: true, Military: false}` |
| 3 | No multi-facet coordination | Medium | Harvest job `campaign_id` + lock/claim protocol; or coordinator agent that assigns disciplines to facets |
| 4 | Harvest logic source-centric, not facet-aware | Medium | Facet agent emits harvest_plan with facet-scoped URLs; harvester consumes job spec |
| 5 | No feedback loop corpus → discipline graph | Medium | Post-harvest: update `facet_evidence_density` or `last_harvest_at` per (discipline, facet) |
| 6 | No scheduling/batching primitives | High | Harvest job schema above; optional `HarvestCampaign` node |

### Additional gaps

| # | Gap | Notes |
|---|-----|------|
| 7 | **CQ-02 assumes `Facet` nodes exist** | JSX uses `MATCH (f:Facet {label:$facet_label})` but DISCIPLINES are in-memory; Neo4j may not have `:Facet` nodes. Need to verify schema or make CQ-02 work with facet label only. |
| 8 | **REPOS params not derived from discipline** | Agent must compute `slug`, `oa_id`, `lcsh` from discipline; these live in DISCIPLINES array in JSX, not necessarily in Neo4j. Need discipline→properties mapping in graph or config. |
| 9 | **No facet-level thresholds/strategy** | Reviewer: "facet-level priorities, thresholds, or strategies" should be externalized. Add `SYS_FacetPolicy` or extend FACETS with `harvest_priority`, `min_discipline_coverage`, etc. |
| 10 | **View modes not wired to agent** | `discipline-facet`, `hierarchy`, `federation` are UI modes; agent has no programmatic way to request "give me federation view for my facet." Expose as query params or sub-modes in the I/O contract. |

---

## 5. Recommended Next Steps

1. ~~**Add I/O schemas to STACK**~~ — Done. `chrystallum_discipline_universe_v2.jsx` has `agent_io` block.
2. ~~**Implement CQ-02 against live graph**~~ — Done. CQ-02b added; `scripts/agents/facet_console/discipline_registry.py` tries Neo4j, falls back to `config/discipline_registry_fallback.json`.
3. ~~**Introduce per-facet harvest state**~~ — CQ-05b added for `needs_harvest_by_facet`; schema documented.
4. ~~**Create HarvestJob representation**~~ — Done. File-based: `output/facet_harvest_jobs/{facet}/jobs.jsonl`. `scripts/agents/facet_console/harvest_job.py`.
5. ~~**Add SYS_FacetPolicy**~~ — Done. `scripts/migrations/migration_facet_console.cypher` seeds Political, Biographic, Military.

---

## 6. Concrete Loop (from review, with I/O)

```
1. Identify: read FACET_COLOR, store facet_label + color
2. Request scope: POST { facet_label, mode: "scope" } → discipline_universe
3. Overlay CQ-05: filter discipline_universe by needs_harvest
4. Request harvest_plan: POST { facet_label, mode: "harvest_plan", constraints } → harvest_jobs
5. Emit job spec: write HarvestJob nodes or files
6. Emit snapshot: write/update facet→discipline state for UI
7. Harvester (separate process) consumes jobs, fetches, writes TextPassage/MENTIONS
8. Feedback: update needs_harvest_by_facet, last_harvest_at
```
