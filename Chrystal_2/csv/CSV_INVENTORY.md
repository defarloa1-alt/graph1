# CSV inventory — useful for Chrystal 2 bootstrap

**Scope:** Prefer domain-agnostic registries. Republic-specific harvest dumps stay reference-only until Domain agent runs.

Legend: **SHIP** = load or keep as source of truth for empty Neo · **KEEP** = useful later / schema specialist · **DEFER** = domain pack later · **ARCHIVE** = noise / superseded.

---

## Tier A — SHIP / primary registries (not under `CSV/` only)

These are the real spine; treat as canonical even though paths vary.

| File | Use |
|------|-----|
| `Relationships/relationship_types_registry_master.csv` | **SHIP** — `SYS_RelationshipType` source; schema specialist must not invent types |
| `Facets/facet_registry_master.csv` | **SHIP** — seed 18 `:Facet` nodes (dedupe by `facet_key`) |
| `CSV/year_nodes.csv` | **KEEP pattern only** — tiny Rome-era sample; **do not** use as full backbone. Load Years via `scripts/backbone/temporal/genYearsToNeo.py` |
| `CSV/project_p_values_canonical.csv` | **KEEP** — project-known PIDs + datatypes; seed thin `SYS_WikidataProperty` / specialist hints |
| `CSV/wikiPvalues_enriched.csv` | **KEEP** — full WD property catalog (large); lookup when specialist sees unknown PID |
| `CSV/lcc_full.csv` | **DEFER** until Librarian / subject backbone — biblio universe, not pre-harvest required |
| `Disciplines/discipline_facet_assignments.csv` | **DEFER** — discipline backbone not shipping yet |

---

## Tier B — useful for schema specialist (post–Domain JSON)

| File | Use |
|------|-----|
| `CSV/property_mappings/property_facet_mapping_COMPLETE.csv` | Facet hints for PIDs (INTELLECTUAL, DEMOGRAPHIC, …). Optional; Domain may not need facet routing at bootstrap |
| `CSV/property_mappings/claude_facet_assignments_batch*.csv` | Superseded by COMPLETE — **ARCHIVE** |
| `CSV/action_structure_vocabularies.csv` | Goal/action vocab — **DEFER** (claim/action modeling later) |
| `CSV/action_structure_wikidata_mapping.csv` | Same — **DEFER** |
| `CSV/geographic/place_type_hierarchy_v1.csv` | **KEEP** when geo becomes domain-scoped — place-type taxonomy |
| `CSV/geographic/federation_facet_policy_v1.csv` | **KEEP as pattern** — shows per-facet federation prefs; rewrite per Domain (Meiji ≠ Pleiades-first) |
| `CSV/geographic/place_temporal_status_policy_v1.csv` | **KEEP** for geo policy later |
| `CSV/stable_geographic_features.csv` | Small — **KEEP** if still accurate |

---

## Tier C — Republic / Q17167 pack (Domain agent input later — not SYS ship)

| File | Use |
|------|-----|
| `CSV/lcsh_roman_republic.csv` (+ `_analysis`) | Librarian / aboutness for RR pack |
| `chrystal_2/federations/crosswalks/*` | **KEEP** — curated LCSH/FAST/LCC (+QID) co-locations; datastore-first for Librarian |
| `CSV/lcc_roman_republic.csv` | Same, LCC slice |
| `CSV/periodo_roman_republic*.csv` | Period federation candidates for RR |
| `CSV/pleiades_roman_republic.csv` | Large geo dump — RR only |
| `CSV/dprr_roman_republic*.csv` | Tiny / analysis — real DPRR is Neo federation on `ac63a8e5` |
| `CSV/Q17167_initial-qid-subject-analysis.csv` | Early DI analysis — reference |
| `JSON/wikidata/statements/Q17167_statements_full.json` | **Preferred seed** for RR Domain (labeled) — not CSV |

---

## Tier D — discipline / majors experiments

| File | Use |
|------|-----|
| `CSV/disciplines_academic*.csv`, `academic_majors*.csv`, `discipline_*` | **DEFER** — subject/discipline backbone later |
| `CSV/1-15-26-q1 subjects.csv` | Early experiment — **ARCHIVE** |

---

## Tier E — registry / meta / noise

| File | Use |
|------|-----|
| `CSV/registry/project_artifact_registry.csv` | Meta-index of project files — **KEEP** for humans, not Neo load |
| `CSV/kko_chrystallum_crosswalk.csv` | Tiny KBpedia crosswalk — **ARCHIVE** unless revived |
| `CSV/neo4j_query_table_data_2026-2-20.csv` | Query export snapshot — **ARCHIVE** |
| `CSV/wikiPvalues.csv`, `wikiPvalues_alias_index.csv`, samples | Prefer `wikiPvalues_enriched.csv`; raw/alias **ARCHIVE** or KEEP offline |
| `CSV/backlinks/*`, `CSV/experiments/*` | **ARCHIVE** |
| `CSV/geographic/pleiades_*`, `geonames_*` crosswalks | **DEFER** with geo domain work; don’t preload on empty Neo |

---

## What to load on empty `7fe339d2` (from CSV / CSV-adjacent)

1. **Years** — script, not `year_nodes.csv`  
2. **Facets** — from `Facets/facet_registry_master.csv` (unique `facet_key`)  
3. **Relationship types** — from `Relationships/relationship_types_registry_master.csv` → `SYS_RelationshipType`  
4. Optional thin PID seed — subset of `project_p_values_canonical.csv` (P31, P571, P576, P244, P2163, P39, …)  

Do **not** load Pleiades/DPRR/PeriodO CSVs or peer-SC dumps into Chrystal 2 at bootstrap.
