# Harvesting Process and Scripts — Guide

**Purpose:** Explain what the harvesting process does, which scripts run it, and how they fit into the pipeline.

---

## 1. Overview

**Harvesting** = discovering candidate entities from Wikidata that belong to the Roman Republic domain. We use **backlink traversal**: start from seed QIDs (SubjectConcept anchors like Q17167 Roman Republic, Q182547 Provinces), query Wikidata for entities that *point to* those seeds via semantic properties, then gate candidates by class (P31) and datatype quality.

**Pipeline position:** Harvester is **Layer 1** of four. It discovers entities only — it does not fetch full claims or build edges. Downstream layers do that.

### Full Pipeline Flow (Anchors → Graph)

```
subject_concept_anchors_qid_canonical.json
         │
         ├──────────────────────────────────┐
         │                                  │
         ▼                                  ▼
┌─────────────────────┐          ┌─────────────────────────────────┐
│ Subject             │          │ Harvester (Layer 1)             │
│ Characterization    │          │ Backlink traversal per anchor    │
│ Maps anchors →      │          │ → *_report.json                 │
│ facets, material_   │          │ → harvest_run_summary.json       │
│ type (18 facets)    │          └─────────────────────────────────┘
│ Guardrails:         │                          │
│ Wikidata, Wikipedia │                          ▼
│ extract only        │          ┌─────────────────────────────────┐
└─────────────────────┘          │ Entity Store (Layer 2)          │
         │                       │ Fetch full claims              │
         │                       └─────────────────────────────────┘
         │                                  │
         │                                  ▼
         │                       ┌─────────────────────────────────┐
         │                       │ Edge Building (Layer 3)        │
         │                       │ Map claims → typed edges       │
         │                       └─────────────────────────────────┘
         │                                  │
         ▼                                  ▼
┌─────────────────────┐          ┌─────────────────────────────────┐
│ Load SubjectConcepts│◄────────│ Cluster Assignment (Layer 4)    │
│ + MAPS_TO_FACET     │          │ harvest reports → MEMBER_OF     │
│ (from char. JSON)   │          └─────────────────────────────────┘
└─────────────────────┘
```

### Layer Summary

| Layer | Job | Scripts |
|-------|-----|---------|
| **Subject Characterization** | Map anchors → 18 facets, material_type (guardrails: Wikidata + Wikipedia only) | `subject_characterization_agent.py` |
| **Harvester** | Entity discovery via backlinks | `wikidata_backlink_harvest.py`, `harvest_all_anchors.py` |
| **Entity Store** | Fetch full claims for accepted entities | `wikidata_fetch_all_statements.py` |
| **Edge Building** | Map properties → typed edges | `wikidata_generate_claim_subgraph_proposal.py` |
| **Cluster Assignment** | Assign entities to SubjectConcepts (MEMBER_OF) | `cluster_assignment.py` |

---

## 2. Subject Characterization (Pre-Harvest)

**Path:** `scripts/backbone/subject/subject_characterization_agent.py`

**What it does:** Characterizes SubjectConcept anchors (QIDs) with 18 facets, weights, material_type, and summary. Uses **only** provided sources (guardrails): Wikidata description + P244/P1149/P2163/P1036, Wikipedia intro extract, and (when `--harvest-dir` passed) harvest report summary (entity counts, linking properties, federation IDs, P31 types). No web search; LLM reasons from context only.

**Input:** Anchor QIDs (single `--identifier` or batch from LCC CSV via `--input`)

**Output:** `output/subject_concepts/subject_characterization_results.json`

**When to run:** Before or in parallel with harvest. Same anchor input. Output feeds `load_subject_concepts` for MAPS_TO_FACET edges (when persistence is wired).

**Usage:**
```bash
# Single anchor (QID)
python scripts/backbone/subject/subject_characterization_agent.py --identifier Q17167 --provider perplexity

# With harvest context (entity types, properties, federation IDs from backlink reports)
python scripts/backbone/subject/subject_characterization_agent.py --identifier Q17167 --provider perplexity --harvest-dir output/backlinks

# Batch from anchors JSON (extract QIDs first) or LCC CSV
python scripts/backbone/subject/subject_characterization_agent.py --input output/nodes/lcc_roman_republic.csv --provider perplexity --limit 5

# Dry run (no LLM call)
python scripts/backbone/subject/subject_characterization_agent.py --identifier Q17167 --provider perplexity --dry-run
```

**Harvest integration:** When `--harvest-dir` is passed and a report exists for the anchor QID (e.g. `Q17167_report.json`), the agent adds: accepted entity count, scoping (temporal/domain/unscoped), top linking properties (P710, P17, etc.), federation IDs (Pleiades, LGPN, VIAF), and entity types (P31). This grounds facet weights in actual harvested graph data.

**Related:** `docs/SUBJECT_DOMAIN_CONCEPTUAL_MODEL.md`, `output/subject_concepts/subject_characterization_neo4j_preview.cypher`

### Scripts Quick Reference

| Script | Role |
|--------|------|
| `subject_characterization_agent.py` | Characterize anchors → facets, material_type (guardrails: Wikidata + Wikipedia only) |
| `wikidata_backlink_harvest.py` | Core harvester: SPARQL backlinks, quality gates, scoping, report output |
| `harvest_all_anchors.py` | Batch wrapper: runs harvester for all anchors, writes harvest_run_summary.json |
| `run_full_61_production_reharvest.py` | Full 61-anchor production re-harvest |
| `run_scoped_reharvest.py` | Re-harvest Q182547, Q337547 with anchor-specific allowlists |
| `wikidata_lgpn_forward_harvest.py` | Forward SPARQL for LGPN (P1047) persons |

---

## 3. Core Harvester: wikidata_backlink_harvest.py

**Path:** `scripts/tools/wikidata_backlink_harvest.py`

**What it does:**
1. Takes a **seed QID** (e.g. Q17167 Roman Republic)
2. Runs SPARQL: find entities `?source` where `?source ?prop ?seed` for allowed properties
3. Builds candidate set from backlink rows
4. **Quality gates:**
   - P31 denylist (e.g. Q4167836 Wikimedia category) → reject
   - Class allowlist (schema P31/P279) → accept only if P31 matches schema classes (production mode)
   - Unresolved class ratio > 20% → reject batch
   - Unsupported datatype ratio > 10% → reject batch
   - Literal-heavy threshold (80%) → not frontier-eligible
5. Applies **budget caps:** max_sources_per_seed, max_new_nodes_per_seed
6. Computes **scoping_status** (temporal_scoped, domain_scoped, unscoped) from federation IDs (P1584 Pleiades, P1047 LGPN, P1696 Trismegistos, P214 VIAF)
7. Writes a **report JSON** per seed

**Modes:**
- **discovery** — Broader property allowlist (DISCOVERY_PROPERTY_BOOTSTRAP), class gating disabled, higher budgets
- **production** — Narrower allowlist (P710, P1441, P138, P112, P737, P828), class gating from schema, tighter budgets

**Config:** Reads thresholds from SYS_Threshold when Neo4j available (D-032). Fallback: MODE_DEFAULTS.

**Usage:**
```bash
python scripts/tools/wikidata_backlink_harvest.py --seed-qid Q17167 --mode discovery
python scripts/tools/wikidata_backlink_harvest.py --seed-qid Q182547 --mode production --report-path output/backlinks/Q182547_report.json
```

---

## 4. Batch Wrappers

### harvest_all_anchors.py

**Path:** `scripts/backbone/subject/harvest_all_anchors.py`

**What it does:** Runs `wikidata_backlink_harvest.py` once per anchor QID from a JSON file. Deduplicates by QID (multiple SubjectConcepts can share an anchor). Tracks progress, supports `--resume`, writes `harvest_run_summary.json` for cluster assignment.

**Input:** Anchor JSON (e.g. `subject_concept_anchors_qid_canonical.json`)

**Output:** `output/backlinks/{QID}_report.json` per seed, `harvest_run_summary.json`, `harvest_progress.json`

**Usage:**
```bash
python scripts/backbone/subject/harvest_all_anchors.py \
  --anchors output/subject_concepts/subject_concept_anchors_qid_canonical.json \
  --harvester scripts/tools/wikidata_backlink_harvest.py \
  --output-dir output/backlinks \
  --mode discovery
```

### run_full_61_production_reharvest.py

**Path:** `scripts/backbone/subject/run_full_61_production_reharvest.py`

**What it does:** Convenience launcher for full 61-anchor production re-harvest. Uses schema class gating, `--use-schema-relationship-properties`, production mode.

**Usage:**
```bash
python scripts/backbone/subject/run_full_61_production_reharvest.py
python scripts/backbone/subject/run_full_61_production_reharvest.py --resume
```

### run_scoped_reharvest.py

**Path:** `scripts/backbone/subject/run_scoped_reharvest.py`

**What it does:** Re-harvests Q182547 and Q337547 with anchor-specific property allowlists (from `entity_scoping.anchor_to_property_allowlist` in schema). Q182547 Provinces → P31 only; Q337547 Public ritual → P140, P101, P361. Optionally runs cluster_assignment after.

**Usage:**
```bash
python scripts/backbone/subject/run_scoped_reharvest.py
python scripts/backbone/subject/run_scoped_reharvest.py --cluster-assignment --write
```

---

## 5. Forward Harvest: wikidata_lgpn_forward_harvest.py

**Path:** `scripts/tools/wikidata_lgpn_forward_harvest.py`

**What it does:** **Forward SPARQL** — finds persons with P1047 (LGPN ID). Backlink from Q899409 (gens) returns 0 LGPN entities because LGPN-attested persons are not backlinked to Q899409 in Wikidata. Forward harvest closes that gap.

**Usage:**
```bash
python scripts/tools/wikidata_lgpn_forward_harvest.py
python scripts/tools/wikidata_lgpn_forward_harvest.py --limit 500 --output output/lgpn/lgpn_persons.json
```

---

## 6. Downstream Scripts (Post-Harvest)

| Script | Purpose |
|--------|---------|
| `wikidata_fetch_all_statements.py` | Fetch full claims for a QID (Entity Store layer) |
| `wikidata_generate_claim_subgraph_proposal.py` | Map claims → edges (Edge Building layer) |
| `cluster_assignment.py` | Read harvest reports + summary → write MEMBER_OF edges to Neo4j |
| `load_subject_concepts_qid_canonical.py` | Load SubjectConcepts from anchors; optionally set `harvest_status` from backlink reports |
| `update_harvest_status_from_graph.py` | Set `harvest_status = 'confirmed'` on SubjectConcepts with MEMBER_OF edges |

---

## 7. Analysis and Diagnostics

| Script | Purpose |
|--------|---------|
| `analyze_harvest_reports.py` | Check Q182547 Pleiades dropped, Q337547 unscoped by property |
| `harvest_delta_extract.py` | Extract entities dropped by node budget cap |
| `harvest_penetration_analysis.py` | Analyze harvest coverage |
| `wikidata_backlink_profile.py` | Profile candidates without running harvest |

---

## 8. Output Structure

```
output/backlinks/
├── Q17167_report.json          # Per-seed harvest report
├── Q182547_report.json
├── ...
├── harvest_run_summary.json    # qid_to_subject_ids, completed, failed
└── harvest_progress.json       # completed QIDs for --resume
```

**Report JSON structure:**
- `accepted` — list of {qid, label, properties, p31, scoping_status, scoping_confidence, external_ids}
- `rejected` — list of {qid, reason, ...}
- `run_metadata` — mode, thresholds, limits

---

## 9. Property Allowlist

**Production:** P710 (participant), P1441 (present in work), P138 (named after), P112 (founded by), P737 (influenced by), P828 (has cause)

**Discovery:** Expands to schema relationship properties + DISCOVERY_PROPERTY_BOOTSTRAP (P31, P279, P361, P527, P131, P17, P39, P106, P921, P101, P2578, P2579, etc.)

**Property denylist:** P6104, P5008, P6216 (Wikidata administrative)

**Decision rule:** Add property X only if it discovers entities no current semantic property would find. Otherwise defer to Entity Store / Edge Building.

---

## 10. Scoping (HARVESTER_SCOPING_DESIGN.md)

| Scoping status | Signal |
|----------------|--------|
| temporal_scoped | P1584 (Pleiades), P1047 (LGPN), P1696 (Trismegistos) |
| domain_scoped | P214 (VIAF) + domain graph proximity |
| unscoped | No federation IDs → confidence 0.40, flagged for review |

---

## 11. Reference Scripts (Not in Main Pipeline)

| Script | Purpose |
|--------|---------|
| `scripts/reference/academic_property_harvester.py` | SPARQL harvest of P101, P2578, P921, P1269 for academic discipline properties |
| `scripts/reference/hierarchy_relationships_loader.py` | Load harvested academic properties into Neo4j |

---

## 12. Related Docs

| Document | Purpose |
|----------|---------|
| `docs/SUBJECT_DOMAIN_CONCEPTUAL_MODEL.md` | Subject characterization, facets, persistence model |
| `docs/HARVESTER_SCOPING_DESIGN.md` | Scoping rules (temporal vs conceptual) |
| `md/Architecture/PIPELINE_LAYERS_AND_PROPERTY_ALLOWLIST.md` | Four-layer architecture, allowlist decision framework |
| `docs/PIPELINE_READ_BACK_PRINCIPLE.md` | Read-back before write (harvester compares to existing entity set) |
| `sysml/BLOCK_CATALOG_RECONCILED.md` | Harvester block, SYS_Threshold values |

---

*Last updated: 2026-02-27*
