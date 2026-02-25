# Advisor Report: Work Since Federation List

**Date:** February 21, 2026  
**Context:** Post–federation list delivery; review of deliverables and key file paths for advisor review.

---

## 1. Executive Summary

Since producing the complete federation list (13 federations), work has focused on:

1. **Relationship canonicalization** — Stamping semantic properties on Neo4j edges  
2. **Property chain trace** — Mapping which backlink properties bring in scoped entities  
3. **Federation Phase 1 scoping** — Domain proximity gate and conceptual-entity handling in the harvester  
4. **SubjectConcept model validation** — Facet-based queries and vertex jump verification on the graph  

---

## 2. Deliverables and Status

| Deliverable | Status | Output / Artifact |
|-------------|--------|-------------------|
| Federation list | Done | 13 federations documented |
| Relationship canonicalization | Done | 3,907 edges stamped; 16,491 unmapped |
| Property chain trace | Done | Q182547, Q337547, Q899409 analyzed |
| Domain proximity gate | Done | Harvester scoping for conceptual entities |
| LGPN expansion | Documented | Forward SPARQL needed; not backlink harvest |
| SubjectConcept validation | Done | 5 checks passed; 2 warnings |
| Unmapped relationship types | Done | 220 types listed |

---

## 3. Files Most Needed for Advisor Review

### 3.1 Federation and Scoping (Start Here)

| Path | Purpose |
|------|---------|
| `output/analysis/federations_complete_list.md` | Full list of 13 federations; scoping PIDs; Phase 2 targets |
| `docs/HARVESTER_SCOPING_DESIGN.md` | Temporal vs conceptual entity scoping; federation-aware gate logic |
| `scripts/tools/wikidata_backlink_harvest.py` | Harvester with `_compute_federation_scoping()`, `_load_category_to_scoping_class()` |
| `tests/test_federation_scoping.py` | 9 unit tests for federation scoping (temporal, domain, unscoped) |

### 3.2 Relationship Canonicalization

| Path | Purpose |
|------|---------|
| `canonicalize_edges.py` | Script that stamps `canonical_type`, `canonical_category`, `cidoc_crm_property` on PID edges |
| `Relationships/relationship_types_registry_master.csv` | Registry (95 PIDs mapped to Wikidata; use `utf-8-sig` encoding) |
| `output/analysis/registry_unmapped_to_wikidata.txt` | 220 relationship types not yet mapped to Wikidata |

### 3.3 Property Chain and Trace

| Path | Purpose |
|------|---------|
| `output/analysis/property_chain_trace.md` | Q182547 (Provinces), Q337547 (Public ritual) — which properties bring scoped entities |
| `scripts/analysis/trace_property_chains.py` | Script that produced the trace |

### 3.4 SubjectConcept Model and Validation

| Path | Purpose |
|------|---------|
| `scripts/validation/validate_subjectconcept_model.py` | Validation script (connectivity, entity types, vertex jump, canonical edges) |
| `output/analysis/subjectconcept_validation_20260221.json` | Validation results (JSON) |
| `scripts/tools/entity_cipher.py` | `vertex_jump()`, `generate_faceted_cipher()` — cipher computation |
| `ENTITY_CIPHER_FOR_VERTEX_JUMPS.md` | Design spec for faceted ciphers and vertex jumps |

### 3.5 Schema and Configuration

| Path | Purpose |
|------|---------|
| `JSON/chrystallum_schema.json` | v3.5 schema; `entity_scoping.category_to_scoping_class` (temporal vs conceptual) |
| `.env` | Neo4j credentials (`NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`) |
| `scripts/config_loader.py` | Loads `.env`; used by canonicalize_edges, validation, harvester |

---

## 4. Key Findings

### 4.1 Federation Scoping

- **Temporal scoped (0.95):** P1696 (Trismegistos), P1838 (LGPN), P1584 (Pleiades)  
- **Domain scoped (0.85):** P214 (VIAF) + domain proximity; conceptual entities + domain proximity  
- **Unscoped (0.40):** No federation IDs; no domain proximity  

### 4.2 Property Chain Trace

- **Q182547 (Provinces):** P31 brings 79 temporal-scoped entities; P1584 (Pleiades) present on 79  
- **Q337547 (Public ritual):** P140, P101 bring domain-scoped entities; P214 (VIAF) on 86  
- **Q899409:** 0 LGPN entities; LGPN expansion requires forward SPARQL, not backlink harvest  

### 4.3 SubjectConcept Validation (Current Graph)

- **Nodes:** 58,927 | **Edges:** 42,343  
- **Connectivity:** 26.2% (target 99.9%); 43,517 isolated nodes  
- **Entity cipher:** 9,049 of 58,927 have `entity_cipher`  
- **Passed:** SubjectConcept anchors (29), seed Q17167, canonical edges (3,907), vertex jump, faceted cipher format  

### 4.4 Relationship Registry

- **95 PIDs** mapped to canonical types (INSTANCE_OF, PART_OF, etc.)  
- **220 relationship types** unmapped to Wikidata (in `registry_unmapped_to_wikidata.txt`)  

---

## 5. Recommended Review Order

1. **Federation list** — `output/analysis/federations_complete_list.md`  
2. **Scoping design** — `docs/HARVESTER_SCOPING_DESIGN.md`  
3. **Harvester implementation** — `scripts/tools/wikidata_backlink_harvest.py` (lines 223–227, 542–570, 926–1070)  
4. **Tests** — `tests/test_federation_scoping.py`  
5. **Property trace** — `output/analysis/property_chain_trace.md`  
6. **Validation results** — `output/analysis/subjectconcept_validation_20260221.json`  
7. **Canonicalization** — `canonicalize_edges.py` and `Relationships/relationship_types_registry_master.csv`  

---

## 6. Commands for Quick Verification

```bash
# Run federation scoping tests
python -m pytest tests/test_federation_scoping.py -v

# Run SubjectConcept validation
python scripts/validation/validate_subjectconcept_model.py

# Dry-run canonicalization (no writes)
python canonicalize_edges.py --dry-run
```

---

*Report generated for advisor review. Paths are relative to project root `c:\Projects\Graph1`.*
