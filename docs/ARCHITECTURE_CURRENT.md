# Chrystallum — Current Architecture
**As of 2026-03-09 | Supersedes all prior architecture docs**

---

## 1. What It Is

A federated historical knowledge graph (Neo4j Aura) for the Roman Republic domain.
~100k nodes. Claims are signed by federation source, scored by confidence, routed to
SubjectConcepts via a rules-in-graph pipeline.

**The core design principle:** the graph is the source of truth for rules, thresholds,
routing logic, and domain definitions. Nothing domain-specific is hardcoded in Python.

---

## 2. Node Inventory (live counts)

| Label | Count | Notes |
|---|---|---|
| Place | 44,193 | Pleiades + Wikidata stubs |
| Person | 5,248 | 4,863 DPRR in-domain |
| Discipline | 972 | Backbone tier, all have authority IDs |
| LCC_Class | 4,496 | Library of Congress classification |
| Periodo_Period | 1,118 | PeriodO temporal authority |
| SubjectConcept | 22 | 15 ccs_bootstrap + 7 geo_bootstrap |
| SubjectDomain | 1 | domain_roman_republic |
| Period | 1 | Q17167 Roman Republic (-509 to -27) |
| Position | 171 | Formerly Office; Wikidata P39 aligned |
| SYS_FederationSource | 19 | Phase A–D |
| SYS_DecisionTable | 19 | D1–D19 |
| SYS_RoutingRule | 81 | 38 exact + 41 contains + 1 catch_all + 1 domain_default |
| SYS_WikidataProperty | ~50 | PIDs with semantic_role |
| SYS_Threshold | — | D12: child_overload=12, crosslink=0.3 |
| Facet | 18 | Canonical 18-facet system |

---

## 3. Three Backbones

Every entity in the graph connects to three orthogonal identity anchors:

```
Person / Place
    │
    ├─ IN_PERIOD ──────────────► Period (Q17167, -509 to -27)          [TEMPORAL]
    ├─ MEMBER_OF ──────────────► SubjectConcept (22 thematic/geo SCs)  [SUBJECT]
    └─ SCOPED_TO ──────────────► Discipline (prosopography, etc.)      [DOMAIN]

Person only:
    └─ BORN_IN ────────────────► Place (QID-resolved, Pleiades-backed) [GEO]

Place only:
    └─ MEMBER_OF ──────────────► geo SC (GEO_SETTLEMENTS, etc.)        [SUBJECT/GEO]
```

**MEMBER_OF edge properties (wire-complete at creation):**
- `source`: position_held | place_type | place_type_default | dprr_default | career_bounds
- `rank`: primary | inferred
- `earliest_year`, `latest_year`: from POSITION_HELD year_start/end or Place min_date/max_date
- `position_count`: count of matching POSITION_HELD edges (person routes only)

---

## 4. SubjectConcept Backbone (22 SCs)

Governed by **ADR-020** (CCS — Chrystallum Classification System).

**Validity rules (all 22 pass):**
1. Authority tether: ≥1 external ID (LCSH, FAST, LCC, Nomisma, Pleiades…)
2. Multidimensional: ≥2 HAS_FACET edges with weight + is_primary
3. Populatable: ≥1 FederationSource can supply members
4. Topic-grounded: named scholarly topic, NOT an entity-type container

**15 ccs_bootstrap (thematic):** sc_constitution (4,863), sc_late_republic (1,906),
sc_military (1,322), sc_middle_republic (1,010), sc_early_republic (684),
sc_diplomacy (368), sc_economy (366), sc_religion (248), sc_law (0),
sc_topography (0), sc_society (0), sc_historiography (0),
sc_material_culture (0), sc_literature (0), sc_science (0)

**7 geo_bootstrap (spatial):** GEO_SETTLEMENTS (17,521), GEO_HIST_PLACES (11,390),
GEO_GENERAL (11,360), GEO_PHYS_FEATURES (2,216), GEO_HYDROGRAPHY (2,115),
GEO_POLITICAL_ENTITIES (1,596), GEO_ADMIN_DIVISIONS (1,126)

**Period SCs carry their own bounds** (period_start/period_end on the node):
- sc_early_republic: -509 to -264
- sc_middle_republic: -264 to -133
- sc_late_republic: -133 to -27

Status: scaffold. DI batch_train (14 facets remaining) will replace ccs_bootstrap
with evidence-derived SC proposals.

---

## 5. Rules-in-Graph (not in code)

All routing rules live in `SYS_RoutingRule` nodes. Python reads, never hardcodes.

| match_mode | Count | Example |
|---|---|---|
| `exact` | 38 | pos.label='consul' → sc_constitution |
| `contains` | 41 | place_type CONTAINS 'settlement' → GEO_SETTLEMENTS |
| `catch_all` | 1 | no place_type match → GEO_GENERAL |
| `domain_default` | 1 | all DPRR persons → sc_constitution (inferred) |

**Period routing** reads `sc.period_start`/`sc.period_end` from SubjectConcept nodes.
No date constants exist in any script.

**QID resolution** (BORN_IN, DIED_IN) reads PIDs from `SYS_WikidataProperty` nodes:
- P1566 (Pleiades ID) — strategy 2: direct lookup
- P131 (located in) — strategy 3: walk to parent, then check P1566

Other rules still in code (migration pending):
- Facet scope definitions → `di/classify.py` static fallback (→ D4–D8 decision tables)

---

## 6. Federation Sources

**Phase A (active):** DPRR, Pleiades, Wikidata, LCSH/FAST/LCC, PeriodO, VIAF, Trismegistos, DOAJ
**Phase B:** Getty AAT, LGPN
**Phase C:** EDH, OCD
**Phase D (planned):** OpenAlex, Open Syllabus, Open Library, Perseus, CHRR, CRRO

Each source is a `SYS_FederationSource` node with `source_id`, `label`, `phase`,
`scoping_weight`, `pid` (Wikidata external identifier PID for that source).

**Wire-complete contract:** no BORN_IN/DIED_IN edge is created without a
Pleiades-backed target. Unresolved stubs get `needs_resolution=true` on the Place node.

---

## 7. Package Structure

```
packages/
  domain/
    routing_rules.py    ← load_rules(session, domain) — reads SYS_RoutingRule
                           summarise() — one-line log summary

scripts/
  backbone/subject/
    populate_member_of.py   ← wiring engine; imports from packages.domain
  federation/
    qid_resolver.py         ← QIDResolver; reads PIDs from SYS_WikidataProperty
  maintenance/
    promote_p19_p20_to_canonical.py  ← uses QIDResolver before creating BORN_IN
  config_loader.py          ← NEO4J_URI/USER/PASS from .env

claude/
  extracted/              ← Cypher migration scripts (18a–18k); history, not arch
  run_scripts.py          ← runner for .cypher files

viewer/                   ← React viewer (Vite)
mcp/neo4j-server/         ← MCP server (read-only Cypher, domain structure)

Key Files/
  chrystallum_subject_constitution.jsx  ← live backbone diagram (SysML v2 style)
  Appendices/05_Architecture_Decisions/ ← ADRs (ADR-020 is governing for CCS)
```

**Migration rule:** extract to `packages/` only when a second caller appears.
`scripts/config_loader.py` is the one remaining candidate (used everywhere).

---

## 8. DI Pipeline (Discipline Intelligence)

Converts Wikidata QIDs into evidence-derived SubjectConcept proposals.

```
harvest.py   → fetch all Wikidata statements for a QID
classify.py  → assign facets (18-dim vector)
route.py     → build per-facet corpus packs (OpenAlex abstracts)
train.py     → LLM decomposes domain into SC proposals per facet
propose.py   → aggregate proposals, validate against CCS rules
```

State: 1/15 facets trained (MILITARY). 14 remaining (~238 Claude API calls).
Output: `output/di_route/<facet>_pack.json`, `output/di_propose/<facet>_proposals.json`

MILITARY yielded 5 SC proposals: Wars, Organization, Civil Wars, Battles, Command.

---

## 9. Decision Tables (D1–D19)

All 19 `SYS_DecisionTable` nodes are in the graph. They ARE the spec — agents read
rows, there is no separate implementation.

Key tables for routing:
- **D12**: child_overload=12, crosslink_thresh=0.3 (split/merge thresholds)
- **D15–D18**: FederationScorer states and weights
- **D19**: DPRR relationship map (37 entries)

---

## 10. What to Give an Agent for Analysis

Minimum viable bootstrap packet:

1. This file (`docs/ARCHITECTURE_CURRENT.md`)
2. `Key Files/chrystallum_subject_constitution.jsx` — backbone schema + SC gallery
3. `Key Files/Appendices/05_Architecture_Decisions/ADR_020_Chrystallum_Classification_System.md`
4. MCP tools: `get_domain_structure`, `get_subject_concepts`, `list_thresholds`

For training specifically, also provide:
5. `output/di_route/<facet>_pack.json` — corpus for the target facet
6. MCP: `run_cypher_readonly` to inspect SYS_RoutingRule, SYS_Threshold

Do NOT give:
- `docs/architecture/*_2026-02-19.md` — pre-CCS, wrong schema
- `claude/extracted/18*.cypher` — migration history
- The hundreds of `docs/` files predating 2026-03-01

---

## 11. Key Architectural Decisions

| Decision | Rationale |
|---|---|
| Graph is rule registry | Rules queryable, versionable, domain-swappable without code changes |
| MEMBER_OF wire-complete | No post-pass enrichment; edges carry all properties at creation |
| QID canonical resolution | No BORN_IN to stub; Pleiades backing required |
| Domain prefix stripped from SC ids | Domain membership = edge (HAS_SUBJECT_CONCEPT), not encoded in id |
| occupation routing rejected | Occupations are time-boxed and role-confused; POSITION_HELD only |
| period_start/end on SC nodes | Date ranges are scholarly data, not code constants |
| packages/ extracted on second caller | No premature abstraction; single-caller scripts stay in scripts/ |
