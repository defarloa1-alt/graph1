# Chrystallum — Current Architecture

**Last updated: 2026-07-14 | Supersedes all prior architecture docs**

**Root: `docs/EPISTEMIC_MODEL.md` → this file → agent constitutions**  
**Navigation hub: `Key Files/ARCHITECTURE.md`**



**Canonical Neo4j:** Aura instance `ac63a8e5` (`neo4j+s://ac63a8e5.databases.neo4j.io`).  

Chrystal 2.0 (`0da8c4a3`) is deprecated — see `docs/DEPRECATED_CHRYSTAL_2.0.md`.



---



## 1. What It Is



A federated historical knowledge graph (Neo4j Aura) for the Roman Republic domain.

Claims are signed by federation source, scored by confidence, routed to SubjectConcepts

via a rules-in-graph pipeline.



**The core design principle:** the graph is the source of truth for rules, thresholds,

routing logic, and domain definitions. Nothing domain-specific is hardcoded in Python.



---



## 2. Live Inspection (not static counts)



Do not trust node counts in markdown. Query the canonical graph at runtime.



| Channel | Use |

|---------|-----|

| **Viewer → System Map** | `cd viewer && npm run dev` — live Cypher tabs (routing, subjects, federation, metrics) |

| **MCP (local stdio)** | `scripts/mcp/chrystallum_mcp_server.py` — Cursor project MCP |

| **Python** | `scripts/config_loader.py` → Bolt to ac63a8e5 |



Useful starter queries (run live, do not cache results here):



```cypher

MATCH (sc:SubjectConcept) RETURN sc.subject_id, sc.label ORDER BY sc.subject_id

MATCH (r:SYS_RoutingRule) RETURN r.match_mode, r.target_sc_id, r.pattern LIMIT 20

MATCH (p:Place) WHERE NOT (p)-[:MEMBER_OF]->() RETURN count(p) AS unwired_places

```



Railway-hosted MCP (`graph1-production.up.railway.app`) is **optional** — trial expired;

local Neo4j + Vite proxy is sufficient for development.



---



## 3. Three Backbones



Every entity in the graph connects to three orthogonal identity anchors:



```

Person / Place

    │

    ├─ IN_PERIOD ──────────────► Period (Q17167, -509 to -27)     [TEMPORAL]

    ├─ MEMBER_OF ──────────────► SubjectConcept (thematic / geo)  [SUBJECT]

    └─ SCOPED_TO ──────────────► Discipline (prosopography…)     [DOMAIN]



Person only:

    └─ BORN_IN ────────────────► Place (QID-resolved, Pleiades-backed) [GEO]



Place only:

    └─ MEMBER_OF ──────────────► geo SubjectConcept (by place_type rules)

```



**Note:** Graph label is `:Person` today; ontology norm is `:Human` (migration pending).



**MEMBER_OF edge properties (wire-complete at creation):**

- `source`: position_held | place_type | place_type_default | dprr_default | career_bounds

- `rank`: primary | inferred

- `earliest_year`, `latest_year`: from POSITION_HELD year_start/end or Place min_date/max_date

- `position_count`: count of matching POSITION_HELD edges (person routes only)



---



## 4. SubjectConcept Backbone



Governed by **ADR-020** (CCS — Chrystallum Classification System).



**Validity rules (every promoted SC must pass):**

1. Authority tether: ≥1 external ID (LCSH, FAST, LCC, Nomisma, Pleiades…)

2. Multidimensional: ≥2 HAS_FACET edges with weight + is_primary

3. Populatable: ≥1 FederationSource can supply members

4. Topic-grounded: named scholarly topic, NOT an entity-type container



**Scaffold layer (hand-defined, awaiting DI replacement):**

- **Thematic (`ccs_bootstrap`):** sc_constitution, sc_early/middle/late_republic, sc_military,

  sc_diplomacy, sc_economy, sc_religion, sc_law, sc_topography, sc_society, sc_historiography,

  sc_material_culture, sc_literature, sc_science

- **Geo (`geo_bootstrap`):** GEO_SETTLEMENTS, GEO_HIST_PLACES, GEO_GENERAL, GEO_PHYS_FEATURES,

  GEO_HYDROGRAPHY, GEO_POLITICAL_ENTITIES, GEO_ADMIN_DIVISIONS



**Period SCs carry bounds on the node** (`period_start` / `period_end`):

sc_early_republic (-509 to -264), sc_middle_republic (-264 to -133), sc_late_republic (-133 to -27).



**Current state (structural, not inventory):**

- Scaffolds are placeholders — DI `propose.py` will produce evidence-derived replacements.

- Geo backbone is **incomplete**: three geo SCs (GEO_SETTLEMENTS, GEO_GENERAL, GEO_HIST_PLACES)

  are absent from the graph while routing rules may still reference them; most Places lack

  `MEMBER_OF`. See `docs/GEO_BACKBONE_MAPPING_STATUS.md`.



---



## 5. Rules-in-Graph (not in code)



All routing rules live in `SYS_RoutingRule` nodes. Python reads, never hardcodes.



| match_mode | Role | Example |

|---|---|---|

| `exact` | Position label match | consul → sc_constitution |

| `contains` | Place-type substring | settlement → GEO_SETTLEMENTS |

| `catch_all` | Unmatched place types | → GEO_GENERAL |

| `domain_default` | Fallback for DPRR persons | → sc_constitution (inferred) |



**Period routing** reads `sc.period_start` / `sc.period_end` from SubjectConcept nodes.

No date constants in scripts.



**QID resolution** (BORN_IN, DIED_IN) reads PIDs from `SYS_WikidataProperty` nodes:

- P1566 (Pleiades ID) — direct lookup

- P131 (located in) — walk to parent, then check P1566



**Still in code (migration pending):**

- Facet scope definitions → `di/classify.py` static fallback (target: D4–D8 decision tables)



---



## 6. Federation Sources



**Phase A (active):** DPRR, Pleiades, Wikidata, LCSH/FAST/LCC, PeriodO, VIAF, Trismegistos, DOAJ  

**Phase B:** Getty AAT, LGPN  

**Phase C:** EDH, OCD  

**Phase D (planned):** OpenAlex, Open Syllabus, Open Library, Perseus, CHRR, CRRO



Each source is a `SYS_FederationSource` node: `source_id`, `label`, `phase`, `scoping_weight`,

`pid` (Wikidata external-ID PID). Status (`operational`, `partial`, `planned`) lives on the node — query live.



**Wire-complete contract:** no BORN_IN/DIED_IN without a Pleiades-backed target.

Unresolved stubs get `needs_resolution=true` on the Place node.



See also: `docs/FEDERATION_ARCHITECTURE.md`



---



## 7. Package Structure



```

packages/

  domain/

    routing_rules.py       ← load_rules(session, domain); reads SYS_RoutingRule



scripts/

  mcp/

    chrystallum_mcp_server.py  ← MCP + optional HTTP /api/cypher

  backbone/subject/

    populate_member_of.py      ← MEMBER_OF wiring engine

  federation/

    qid_resolver.py            ← reads PIDs from SYS_WikidataProperty

  agents/domain_initiator/     ← DI pipeline (harvest → propose)

  config_loader.py             ← NEO4J_URI/USER/PASS from .env



viewer/                        ← React shell over Key Files/*.jsx constitutions



Key Files/

  chrystallum_*_constitution.jsx  ← agent operational docs (DI, SCA, SFA, …)

  chrystallum_system_map.jsx      ← live graph explorer

  Appendices/05_Architecture_Decisions/  ← ADRs (ADR-020 governs CCS)



claude/extracted/              ← Cypher migration history (18a–18k); not active arch

```



**Migration rule:** extract to `packages/` only when a second caller appears.



---



## 8. DI Pipeline (Discipline Intelligence)



Converts Wikidata seed QIDs into evidence-derived SubjectConcept proposals.



```

harvest.py   → Wikidata universe around seed QID

classify.py  → 18-facet classification

route.py     → per-facet packs (candidates + corpus endpoints)

train.py     → LLM decomposes facet into SC proposals

propose.py   → aggregate, validate (CCS), optional graph write

```



**State (Q17167 Roman Republic) — baseline 2026-07-15:** see [BASELINE_Q17167_FACET_HIERARCHY_2026-07-15.md](BASELINE_Q17167_FACET_HIERARCHY_2026-07-15.md)

- harvest, classify, route: **done**
- train: **15/18 facets** (missing diplomatic, environmental, technological)
- propose + human review: **done** — 63 approved proposals
- graph write: **done** — 63 `di_proposal` SubjectConcepts + 15 `FacetUmbrella` nodes
- facet hierarchy wire: **done** — SubjectDomain → FacetUmbrella → decomposition

```
SubjectDomain (Roman Republic · Subject Domain)
  └─ HAS_SUBJECT_CONCEPT → FacetUmbrella (Facet — Military, …)
        ← PART_OF ── di_proposal SC (63)
  └─ OCCURS_DURING → Period Q17167  [temporal anchor only — not subject tree]
```

Review artifact: `output/di_proposals/Q17167_proposals_enriched.json`  
Baseline snapshot: `output/baseline/Q17167_facet_hierarchy_baseline.json`  
Browser query: `scripts/neo4j/view_roman_republic_facet_tree.cypher`

**Not yet in graph:** factual Wikidata claims (`Q17167_validated_claims_v2.json`)



Outputs: `output/di_harvest/`, `output/di_classify/`, `output/di_route/`, `output/di_training/`, `output/di_proposals/`

**Activation checklist:** [SCA_ACTIVATION_CHECKLIST.md](SCA_ACTIVATION_CHECKLIST.md)



Chrystal 2.0 exported proposals (if needed): `output/deprecated_chrystal20/proposed_subject_concepts.json`



---



## 9. Decision Tables



`SYS_DecisionTable` nodes in the graph **are** the spec — agents read rows; no parallel implementation doc.



Key tables:

- **D12** — split/merge thresholds (child_overload, crosslink_thresh)

- **D15–D18** — FederationScorer states and weights

- **D19** — DPRR relationship map



Threshold values live in `SYS_Threshold` nodes — query via MCP `get_threshold` / `list_thresholds`.



---



## 10. What to Give an Agent



### Viewer (start here)



`cd viewer && npm run dev` — tabs include DI, SCA, SFA, System Map, Subject/Geo constitutions.



Each agent constitution has a **pre-flight protocol**: read graph state, then decide fresh / resume / cleanup.



### Minimum bootstrap packet



1. This file

2. Agent constitution: `Key Files/chrystallum_{di,sca,sfa}_constitution.jsx`

3. `Key Files/Appendices/05_Architecture_Decisions/ADR_020_Chrystallum_Classification_System.md`

4. MCP tools: `get_domain_structure`, `get_subject_concepts`, `list_thresholds`, `run_cypher_readonly`

5. For DI train: `output/di_route/<facet>_pack.json`



### Do NOT give



- `Key Files/ARCHITECTURE_{CORE,ONTOLOGY,IMPLEMENTATION,GOVERNANCE}.md` — archived stubs; use this file

- `Archive/Key Files/Architecture_Decomposed_2026-02/` — Feb 2026 decomposed spec

- `Archive/ARCHITECTURE_OPTIMIZATION_REVIEW.md` — Feb 2026 performance ideas, not current design

- `Archive/Key Files/CLAIM_ID_ARCHITECTURE.md` — use ADR-001 + EPISTEMIC_MODEL instead

- `Archive/Key Files/CHRYSTALLUM_HANDOFF.md` — unbuilt ITGAR/governance handoff

- `docs/architecture/*_2026-02-19.md` — pre-CCS schema

- `claude/extracted/18*.cypher` — migration history

- `docs/AGENT_HANDOFF_2026-03-07.md` — mid-build snapshot

- Bulk of `docs/` predating 2026-03-01

- `scripts/v2/*` — deprecated Chrystal 2.0 (see `docs/DEPRECATED_CHRYSTAL_2.0.md`)

- `Key Files/chrystallum_schema_backbone.jsx` — deprecated v2 viewer

- `Key Files/chrystallum_subject_constitution.jsx` — diagram only, not an agent guide



---



## 11. Key Architectural Decisions



| Decision | Rationale |

|---|---|

| Graph is rule registry | Rules queryable, versionable, domain-swappable without code changes |

| Live graph over doc inventory | Counts rot; System Map and MCP are authoritative for inventory |

| MEMBER_OF wire-complete | Edges carry all properties at creation; no post-pass enrichment |

| QID canonical resolution | No BORN_IN to stub; Pleiades backing required |

| Domain prefix stripped from SC ids | Domain membership = edge, not encoded in id |

| occupation routing rejected | Time-boxed and role-confused; POSITION_HELD only |

| period_start/end on SC nodes | Date ranges are scholarly data, not code constants |

| packages/ on second caller | No premature abstraction |

| Phase 1 = subjects/objects; predicates later | DI identifies nodes; typed edges come in Phase 2 |

