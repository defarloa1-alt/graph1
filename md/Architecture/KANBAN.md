# Chrystallum KANBAN
_Last updated: 2026-03-01_

---

## 🔵 IN PROGRESS

### Phase 0c — Matrix
**Context:** Alignment complete. 34,044 nodes, 1,023 aligned, ~7,019 probable edges (spatial/concept/person/text/event). Next: build adjacency matrix.

---

## 📋 TODO

### Phase 0c — Matrix

- [ ] **Write `build_adjacency_matrix.py`** @dev #medium
  - Input: aligned node list
  - For each node pair: call `node_a.adjacency(node_b)` → list of shared dimensions
  - Build sparse matrix: rows = nodes, columns = nodes, values = shared dimension count
  - Also build: per-node neighbour counts by dimension
  - Output: `output/matrix/roman_republic_matrix.json`
  - Note: `apply_rules.py` (DEAD/STUB/ALIVE/SPAWN) → backlog (Game of Life)

---

### Phase 1 — Synthesis

- [ ] **Write synthesis prompt builder** @dev #medium
  - Input: adjacency matrix (or aligned node list if Game-of-Life rules remain backlog)
  - Builds LLM prompt: nodes + adjacency structure; optionally ALIVE/SPAWN from apply_rules when unblocked
  - Ask LLM: name the clusters, assign facets, propose navigation paths
  - Output: `output/synthesis/roman_republic_synthesis_prompt.txt`

- [ ] **Run synthesis against Claude/Perplexity** @dev #medium
  - Feed prompt to LLM
  - Review proposed SubjectConcepts — these replace the 61 discarded LLM guesses
  - Each proposal must cite its federation evidence
  - Human review before any graph writes

---

### Optional — Work / Discipline / SubjectDomain loaders
**Context:** `docs/NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md` now specs Work, Discipline (registry), SubjectDomain. Loaders may not exist yet.

- [ ] **Implement Work loader** @dev #low
  - `scripts/backbone/work/load_worldcat_works.py`, `load_open_syllabus_works.py`
  - OA enrichment: `scripts/enrichment/enrich_work_openaccess.py`

- [ ] **Implement Discipline registry loader** @dev #low
  - `scripts/backbone/discipline/load_disciplines_registry.py`
  - Input: `discipline_majors_consolidated_disciplines_filtered.csv`

- [ ] **Implement SubjectDomain bootstrap** @dev #low
  - `scripts/backbone/domain/bootstrap_subject_domains.py`

---

### Housekeeping

- [ ] **Retire old SubjectConcept pipeline** @dev #low
  - `enrich_subject_concept_authority_ids.py` → rename to `validate_wikidata_authority_properties.py`
  - Make read-only — no graph writes
  - Document known bad data: Dewey-in-P1149 (Q11019, Q11469, Q185816, Q337547, Q7188), LCNAF-in-P244 (8 QIDs), placeholder QID Q1234567, wrong-entity QID Q1541
  - `subject_concept_anchors_qid_canonical.json` → archive to `output/archive/`

- [ ] **Archive old survey spec** @dev #low
  - `scripts/backbone/subject/ENRICH_SUBJECT_CONCEPTS_FROM_AUTHORITIES_SPEC.md` → superseded by Phase 0 pipeline
  - Keep for reference — it correctly identified the label decomposition problem even if the approach was wrong

---

## ✅ DONE (this session)

- [x] **Place enrichment pipeline** (2026-03-01)
  - `enrich_places_from_crosswalk.py` — qid, geonames_id, tgn_id from crosswalk
  - `link_pleiades_place_to_geo_backbone.py` — toString(pleiades_id) fix for type mismatch
  - `run_place_enrichment_pipeline.bat` / `.sh` — one-shot pipeline
  - 2,779 Place nodes enriched; 32,480 Pleiades_Place→Place linked
  - `docs/GEO_BACKBONE_MAPPING_STATUS.md` updated

- [x] **Phase 0a — All six federation surveys complete**
  - LCSH, Pleiades, Periodo, DPRR, WorldCat, LCC — all run, output in `output/nodes/*.json`
  - All surveys enriched with `semantic_facet` via `enrich_survey_facets_llm.py` (--fallback-heuristic)

- [x] **Neo4j loaders created and run**
  - `load_lcsh_survey.py`, `load_federation_survey.py`, `load_lcc_nodes.py`
  - LCSH (15), DPRR (2), WorldCat (196), Periodo (1,118), LCC (141) loaded
  - Pleiades: `output/neo4j/pleiades_load.cypher` generated (32,572 nodes)

- [x] **Neo4j reference doc created**
  - `docs/NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md` — all node types, attributes, relationships
  - Updated per node-review: Work, Discipline (registry), SubjectDomain, Agent, Claim; Quick Map

- [x] **Phase 0b — Alignment pass**
  - `align_federations.py` — 34,044 nodes, 1,023 aligned, ~7,019 probable edges
  - Output: `output/aligned/roman_republic_aligned.json`
  - Neighbours from spatial_anchor, concept_ref, person_ref, text_ref, event_ref, wikidata_qid (temporal-only deferred to build_adjacency_matrix)

- [x] **Federation schema and surveys** (prior sessions)
  - `federation_node_schema.py` v2 — alignment-field-first, dimensions derived
  - `survey_lcsh_domain.py`, `survey_pleiades.py`, `survey_periodo.py`, `survey_dprr.py`, `survey_worldcat.py`, `survey_lcc.py`

---

## 📦 BACKLOG — Game of Life (deferred)

**Decision (2026-02-27):** Game-of-Life update dynamics moved to backlog. The `adjacency()` method and dimension derivation remain — they are useful structure. The following are deferred:

- [ ] **`apply_rules.py`** — DEAD/STUB/ALIVE/SPAWN status transitions
- [ ] **Update dynamics over generations** — cellular automaton step (birth/SPAWN, death)
- [ ] **`survives` as pipeline filter** — POLITICAL+GEOGRAPHIC floor, score ≥ 4 (currently computed but unused)

**Rationale:** Update rules were never implemented. `survives` excludes LCSH entirely and is not wired to any loader or synthesis. Keep schema; defer the experiment.

---

## 🔴 ON HOLD

- [ ] **FASTTopical.marcxml download** — needed for FAST survey; 2–4GB from OCLC
  - Unblock after Phase 0a surveys confirm whether FAST is needed independently
  - LCSH→FAST crosswalk via 751 $0 may be sufficient

- [ ] **subjects_simplified.csv rebuild** — LCSH live mode makes this less urgent
  - Still useful for offline/faster matching in later phases
  - Build: `cd Subjects && python -c "import gzip,shutil;..."` then `python simplify_skos_to_csv.py`

---

## 📌 NOTES

**Current focus:** Phase 0c — build_adjacency_matrix.py

**Pipeline sequence:**
```
survey_lcsh.py → survey_pleiades.py → survey_periodo.py →
survey_dprr.py → survey_worldcat.py → survey_lcc.py →
align_federations.py → build_adjacency_matrix.py →
[apply_rules.py — backlog] → synthesis
```

**Key constraint:** Every survey script must import `federation_node_schema` and emit `FederationSurvey` JSON. Nothing downstream works otherwise.

**Academic experiment note:** Game-of-Life update dynamics (apply_rules, SPAWN, survives filter) are in backlog. The adjacency matrix remains a useful output; preserve it when built.

**Schema location:** `scripts/backbone/subject/federation_node_schema.py`
