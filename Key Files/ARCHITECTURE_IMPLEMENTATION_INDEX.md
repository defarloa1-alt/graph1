# Chrystallum Architecture Implementation Index

**Last Updated:** 2026-02-14  
**Status:** Consolidated-Only Crosswalk (canonical)

---

## Canonical Architecture Source

**Current (as of 2026-02-19):**
- `Key Files/ARCHITECTURE_CORE.md` - Sections 1-2 (Executive Summary & Overview)
- `Key Files/ARCHITECTURE_ONTOLOGY.md` - Sections 3-7 (Core Ontology Layers)
- `Key Files/ARCHITECTURE_IMPLEMENTATION.md` - Sections 8-9 (Technology & Workflows)
- `Key Files/ARCHITECTURE_GOVERNANCE.md` - Sections 10-12 (QA & Governance)
- `Key Files/Appendices/` - 26 appendices organized in 6 thematic clusters

**Archived (for reference only):**
- `Archive/2-12-26 Chrystallum Architecture - CONSOLIDATED.md` (15,910 lines)
  - Archived 2026-02-19 after decomposition into modular files
  - Git tag: `consolidated-pre-decomposition` for rollback if needed

**Why Decomposed:**
- Original file was 15,910 lines (~530 pages) - too large for efficient use
- Now organized into manageable files (<5,000 lines each)
- Better git diffs, faster loading, easier navigation
- See `md/Architecture/CONSOLIDATED_DOC_DECOMPOSITION_PLAN_2026-02-19.md` for rationale

---

## Section Crosswalk (Consolidated -> Implementation)

| Consolidated section | Implementation assets | Notes |
|---|---|---|
| **Section 3: Entity Layer** | `Neo4j/schema/01_schema_constraints.cypher`, `Neo4j/schema/02_schema_indexes.cypher`, `Neo4j/schema/03_schema_initialization.cypher`, `Neo4j/schema/05_temporal_hierarchy_levels.cypher` | First-class node and temporal backbone model |
| **Section 3.3: Facets** | `Facets/facet_registry_master.json`, `Facets/facet_registry_master.csv` | 18 facets: 16 core + Biographic (prosopography) + Communication (meta-facet) |
| **Section 3.4: Temporal Modeling** | `scripts/backbone/temporal/genYearsToNeo.py`, `scripts/backbone/temporal/migrate_temporal_hierarchy_levels.py`, `Neo4j/schema/05_temporal_hierarchy_levels.cypher` | Year->Decade->Century->Millennium hierarchy |
| **Section 4: Subject Layer** | `scripts/backbone/subject/create_subject_nodes.py`, `Python/fast/scripts/import_fast_subjects_to_neo4j.py` | SubjectConcept authority alignment |
| **Section 4.3: Temporal Authorities** | `Temporal/` assets, temporal scripts, PeriodO integration scripts (as available) | Authority alignment + uncertain date handling |
| **Section 4.4: Geographic Authorities** | `Geographic/` assets, place normalization scripts | TGN/Pleiades/GeoNames integration |
| **Section 4.5: Wikidata Integration** | `scripts/tools/wikidata_fetch_all_statements.py`, `scripts/tools/wikidata_statement_datatype_profile.py`, `scripts/tools/wikidata_backlink_harvest.py`, `scripts/tools/wikidata_backlink_profile.py` | Federation + backlink pipeline |
| **Section 5: Agent Architecture** | `md/Agents/` prompts/specs, orchestration docs in `md/Architecture/` | Domain routing + specialization |
| **Section 6: Claims Layer** | `Neo4j/schema/01_schema_constraints.cypher` (Claim constraints), claim proposal artifacts in `JSON/wikidata/proposals/` | claim_id + cipher + lifecycle |
| **Section 7: Relationship Layer** | `Relationships/relationship_types_registry_master.csv`, `CSV/project_p_values_canonical.csv` | canonical relation typing + P-value alignment |
| **Section 8: Technology/Orchestration** | `Neo4j/IMPLEMENTATION_ROADMAP.md`, orchestration docs in `md/Architecture/` | runtime architecture |
| **Section 8.6: Federation Dispatcher** | `scripts/tools/wikidata_backlink_harvest.py`, `Neo4j/FEDERATION_BACKLINK_STRATEGY.md` | route-by-datatype/value_type + gates |
| **Section 9: Workflows** | Workflow docs in `md/Architecture/`, scripts in `scripts/tools/` | extraction -> validation -> write |
| **Section 10: Quality Assurance** | `Neo4j/PHASE_1_CHECKLIST.md`, validation queries in `Neo4j/schema/04_temporal_bbox_queries.cypher` | quality gates + verification |

---

## Phase Mapping (Consolidated Numbering)

| Phase | Scope | Primary consolidated sections | Primary files |
|---|---|---|---|
| **Phase 1** | Schema + temporal backbone baseline | **3**, **3.4**, **10** | `Neo4j/schema/01_schema_constraints.cypher`, `Neo4j/schema/02_schema_indexes.cypher`, `Neo4j/schema/03_schema_initialization.cypher`, `Neo4j/schema/05_temporal_hierarchy_levels.cypher` |
| **Phase 2** | Federation + enrichment | **4.3**, **4.4**, **4.5**, **8.6**, **9** | `scripts/tools/wikidata_*`, `Neo4j/FEDERATION_BACKLINK_STRATEGY.md`, geographic/temporal federation scripts |
| **Phase 3** | Agent orchestration + claims lifecycle | **5**, **6**, **7**, **8**, **9**, **10** | agent specs/prompts, claim workflow scripts, relationship registries |

---

## Critical Alignment Rules

1. Section references in implementation docs must cite consolidated numbering.
2. `Subject`/`Concept` are legacy labels; use `SubjectConcept`.
3. `Person` is legacy wording; use `Human`.
4. `Communication` is a facet/domain axis, not a first-class node label.
5. Federation writes must pass dispatcher gates (Section 8.6) before persistence.

---

## Operational Entry Points

### Neo4j schema
- `Neo4j/schema/01_schema_constraints.cypher`
- `Neo4j/schema/02_schema_indexes.cypher`
- `Neo4j/schema/03_schema_initialization.cypher`
- `Neo4j/schema/05_temporal_hierarchy_levels.cypher`

### Federation tools
- `scripts/tools/wikidata_fetch_all_statements.py`
- `scripts/tools/wikidata_statement_datatype_profile.py`
- `scripts/tools/wikidata_backlink_harvest.py`
- `scripts/tools/wikidata_backlink_profile.py`
- `scripts/tools/wikidata_generate_claim_subgraph_proposal.py`

### Canonical registries
- `Relationships/relationship_types_registry_master.csv`
- `CSV/project_p_values_canonical.csv`
- `Facets/facet_registry_master.json`

---

## Verification Checklist

- [ ] No split-document references as source-of-truth.
- [ ] All phase mappings cite consolidated section numbers.
- [ ] All node label examples use canonical labels.
- [ ] Federation documentation references dispatcher controls.

---

## Change Control

When architecture changes, update in this order:
1. `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
2. Neo4j schema/scripts
3. This index file
4. `AI_CONTEXT.md` and `Change_log.py`
