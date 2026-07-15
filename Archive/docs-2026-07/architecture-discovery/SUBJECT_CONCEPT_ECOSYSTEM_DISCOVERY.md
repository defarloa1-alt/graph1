# SubjectConcept Ecosystem — Discovery & Sense-Making

**Date:** 2026-02-21  
**Purpose:** Map how LCSH/SKOS, LCC, FAST, and Wikidata relate to SubjectConcept. Clarify what exists, what's missing, what's sample vs full.

---

## Executive Summary

| Authority | Declared Path | Exists? | Sample or Full? | Role in SubjectConcept |
|-----------|---------------|---------|-----------------|------------------------|
| **LCSH/SKOS** | `LCSH/skos_subjects/` | Partial | Sample only (chunks deleted) | Enrichment lookup — **broken** |
| **LCC** | `Subjects/lcc_flat.csv` | ✅ Yes | Full (~4,700 rows) | Classification backbone; federation mapping |
| **FAST** | `Python/fast/key/FASTTopical_parsed.csv` | ❌ No | — | In .gitignore; 325MB expected; **missing** |
| **Wikidata** | SPARQL API | ✅ Yes | Live | Primary discovery; SubjectConcept identity = QID |

**SubjectConcept creation flow:** Does NOT depend on LCSH/FAST/LCC as input. It uses **Wikidata QIDs** as the canonical identity. LCSH/FAST/LCC are **enrichment** — added after the fact.

---

## 1. SubjectConcept Creation Flow (Actual)

```
Input (canonical):
  subject_concept_anchors_qid_canonical.json   ← 61 QIDs + labels (from LLM + human curation)
  subject_concept_hierarchy.json               ← BROADER_THAN edges

Source of anchors:
  load_roman_republic_ontology.py  → ONTOLOGY dict (hardcoded)
  find_subject_concept_anchors.py  → resolves QID-less concepts via Wikidata/Perplexity
  migrate_anchors_to_qid_canonical.py → produces subject_concept_anchors_qid_canonical.json

Load:
  load_subject_concepts_qid_canonical.py → MERGE SubjectConcept nodes in Neo4j
```

**Key insight:** SubjectConcept identity is **QID** (Wikidata). No LCSH or FAST required at creation time.

---

## 2. Authority Sources (Declared vs Actual)

### LCSH (Library of Congress Subject Headings)

| Item | Value |
|------|-------|
| **Declared path** | `LCSH/skos_subjects/` |
| **Format** | SKOS JSON-LD (chunked) |
| **Status** | **Broken** — chunks deleted (3.24 GB). Only samples remain. |
| **What remains** | `subjects_sample_200.jsonld`, `subjects_sample_valid.jsonld`, `split_jsonld.py` |
| **Used by** | `subject_concept_workflow.py` (lcsh_path) — but workflow loads LCC index; LCSH not used in load path |
| **enrich_ontology_with_authorities.py** | Uses **hardcoded** AUTHORITY_MAPPINGS dict for Roman Republic — not LCSH lookup |

**Conclusion:** LCSH/SKOS is **not** in the critical path. Enrichment is manual (hardcoded) or would use LCSH if chunks existed. Chunks are gone.

---

### LCC (Library of Congress Classification)

| Item | Value |
|------|-------|
| **Declared path** | `Subjects/lcc_flat.csv` |
| **Format** | CSV: id, code, prefix, start, end, label |
| **Status** | ✅ **Exists** — ~4,700 rows |
| **Source** | `2-10-26-latten_lcc.py` flattens `Subjects/LCC/lcc_*_hierarchy.json` |
| **Used by** | `load_federation_metadata.py`, `federation_mapper.py`, `subject_concept_workflow.py` |
| **Role** | Classification backbone; LCC code → label lookup for federation mapping |

**Conclusion:** LCC is **canonical and working**. Full hierarchy from JSON files.

---

### FAST (Faceted Application of Subject Terminology)

| Item | Value |
|------|-------|
| **Declared path** | `Python/fast/key/FASTTopical_parsed.csv` |
| **Format** | CSV (fast_id, preferred_label, alt_labels) |
| **Status** | ❌ **Missing** — in .gitignore (325 MB) |
| **Source** | `Python/fast/scripts/parse_fast_marcxml.py` parses `FAST/*.marcxml` |
| **FAST/*.marcxml** | Also in .gitignore. We have `FAST/FASTChronological.marcxml` (24K lines) — one schedule |
| **Used by** | `subject_concept_workflow.py` (fast_path), `federation_mapper.py` |
| **enrich_ontology_with_authorities.py** | Hardcoded fast_id for Roman Republic concepts |

**Conclusion:** FAST is **declared but missing**. Workflow will warn "FAST data not found". Enrichment uses hardcoded IDs.

---

### Wikidata

| Item | Value |
|------|-------|
| **Source** | SPARQL API (live) |
| **Status** | ✅ **Works** |
| **Role** | SubjectConcept identity (QID); federation positioning (P31/P279/P244/P2163); discovery |

**Conclusion:** Wikidata is the **primary** authority. No local file needed.

---

## 3. Sample vs Full — Clarification

| Data | Sample | Full | Notes |
|------|--------|------|-------|
| **LCSH/SKOS** | `subjects_sample_200.jsonld`, `subjects_sample_valid.jsonld` | Chunks (deleted) | Full was ~450K headings |
| **LCC** | — | `lcc_flat.csv` (4,700) | Full hierarchy from all JSON files |
| **FAST** | `subjects_sample_50.jsonld` (Python/fast/key/) | `FASTTopical_parsed.csv` (missing) | Full ~325 MB |
| **SubjectConcept** | — | 61 in `subject_concept_anchors_qid_canonical.json` | Roman Republic domain |

---

## 4. How They Relate (Data Flow)

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    SubjectConcept                        │
                    │  Identity: QID (Wikidata)                               │
                    │  Hierarchy: BROADER_THAN (from subject_concept_hierarchy)│
                    └─────────────────────────────────────────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         ▼                               ▼                               ▼
┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
│   Discovery     │           │   Enrichment    │           │  Positioning    │
│   (Wikidata)    │           │   (LCSH/FAST/   │           │  (Federation    │
│   SPARQL        │           │   LCC)          │           │   Positioning)  │
│   QID = identity│           │   lcsh_id,      │           │   POSITIONED_AS │
│                 │           │   fast_id,      │           │   to Entity/    │
│   ✅ Works      │           │   lcc_class     │           │   Anchor        │
│                 │           │                 │           │   ✅ Works      │
│                 │           │   ❌ LCSH: gone │           │                 │
│                 │           │   ❌ FAST: gone │           │                 │
│                 │           │   ✅ LCC: works │           │                 │
│                 │           │   (manual maps  │           │                 │
│                 │           │   for RR)       │           │                 │
└─────────────────┘           └─────────────────┘           └─────────────────┘
```

---

## 5. Gaps and Recommendations

### Critical Gaps

1. **LCSH/SKOS** — Chunks deleted. No full SKOS. Options:
   - Re-download LCSH bulk from LoC; re-run split_jsonld.py
   - Or: rely on Wikidata P244 (LCSH ID) for enrichment — federation positioning already harvests this

2. **FAST** — FASTTopical_parsed.csv missing. Options:
   - Parse FAST/*.marcxml (we have FASTChronological; need FASTTopical?)
   - Or: use Wikidata P2163 (FAST ID) where available
   - Or: LCSH→FAST crosswalk (FAST is derived from LCSH)

3. **Enrichment is manual** — `enrich_ontology_with_authorities.py` uses hardcoded AUTHORITY_MAPPINGS. No automated LCSH/FAST lookup.

### Recommendations

1. **Document the actual state** — Update bootstrap_packet/federations.json and load_federation_metadata.py to reflect:
   - LCSH: "sample only" or "unavailable"
   - FAST: "unavailable" or "requires parse"

2. **Federation positioning as primary** — `sca_federation_positioning.py` harvests P244 (LCSH), P2163 (FAST), P1036 (Dewey), P1149 (LCC) from Wikidata. That becomes the **live** enrichment source. Local LCSH/FAST files are optional for bulk lookup.

3. **Clarify SubjectConcept dependency** — SubjectConcept creation does NOT require LCSH/FAST. It requires:
   - QID (canonical identity)
   - Hierarchy (BROADER_THAN)
   - Optional: federation positioning (POSITIONED_AS) for discovery

4. **LCC as sole local classification** — LCC is the only local authority file that exists and works. Keep it canonical.

---

## 6. Local File Inventory (What We Have in Repo)

### SubjectConcept Canonical (output/)

| Path | Purpose | Rows/Size |
|------|---------|-----------|
| `output/subject_concepts/subject_concept_anchors_qid_canonical.json` | 61 SubjectConcept anchors (QID, label, facet) | 61 |
| `output/subject_concepts/subject_concept_hierarchy.json` | BROADER_THAN edges | ~65 |
| `output/subject_concepts/subject_concept_fast_resolution.json` | QID → FAST ID mappings (curated) | ~40 |
| `output/subject_concepts/subject_concept_wikidata_anchors.json` | Wikidata anchor resolution | — |
| `output/subject_concepts/federation_positioning_report.json` | Live SPARQL positioning output | — |

### LCC (Local — Full)

| Path | Purpose | Rows/Size |
|------|---------|-----------|
| `Subjects/lcc_flat.csv` | Flattened LCC (id, code, prefix, start, end, label) | ~4,700 |
| `Subjects/LCC/lcc_*_hierarchy.json` | LCC hierarchy by class (DG, K, P, etc.) | ~35 files |

### LCSH/SKOS (Local — Sample Only)

| Path | Purpose | Status |
|------|---------|--------|
| `LCSH/skos_subjects/subjects_sample_200.jsonld` | 200 LCSH subjects (SKOS) | Sample |
| `LCSH/skos_subjects/subjects_sample_valid.jsonld` | Valid subset | Sample |
| `LCSH/skos_subjects/split_jsonld.py` | Chunker script | — |
| `LCSH/skos_subjects/chunks/` | Broken-out SKOS chunks | **Deleted** |

### FAST (Local — Partial)

| Path | Purpose | Status |
|------|---------|--------|
| `Python/fast/key/subjects_sample_50.jsonld` | 50 FAST subjects (SKOS) | Sample |
| `Python/fast/key/FASTTopical_parsed.csv` | Full FAST topical | **Missing** (gitignored) |
| `FAST/FASTChronological.marcxml` | FAST chronological schedule | 24K lines — one schedule |
| `FAST/*.marcxml` (other) | FAST topical, geographic, etc. | **Missing** (gitignored) |

### CIP (Academic Disciplines — LCC/LCSH Crosswalk)

| Path | Purpose | Status |
|------|---------|--------|
| `Subjects/CIP/cip_code,cip_title,lcc_classes,lcsh_term.csv` | CIP → LCC + LCSH mapping | ~30 rows |
| `Subjects/disciplines_registry.csv` | Full disciplines | 383KB |

### LCC/FAST → Facet Mappings (Local)

| Path | Purpose | Status |
|------|---------|--------|
| `Facets/lcc_fast_seed_mappings_legacy.json` | LCC prefix → FAST ID + facet | LCC-based |
| `subjectsAgentsProposal/files/lcc_to_chrystallum_facets_v1.1.json` | LCC range → Chrystallum facets | DG, etc. |

### One-Off / Stale (Local but Not Canonical)

| Path | Purpose |
|------|---------|
| `Subjects/query_lcsh_enriched.tsv` | LCSH-enriched query output |
| `Subjects/sample_token_qid_enriched.csv` | Periodo token enrichment |
| `Subjects/2-4-26-lcc_concepts_sample.json` | LCC concepts sample |
| `Subjects/rawindex.txt` | Raw index scrape |

---

## 7. Next Steps

1. **Architect decision:** Re-download LCSH bulk and FAST, or rely on Wikidata for P244/P2163?
2. **Update federation metadata** — Mark LCSH/FAST as unavailable or sample in federations.json
3. **Consolidate enrichment** — Either automate (LCSH/FAST API or Wikidata) or document manual process
4. **SubjectConcept triage** — Proceed with Subjects/ triage; keep LCC as canonical; archive or fix LCSH/FAST references
