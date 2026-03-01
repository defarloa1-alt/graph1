# Subjects Directory Triage Report

**Date:** 2026-02-21  
**Scope:** All files in `Subjects/` and subdirs  
**Actions:** DELETE | EXTRACT (move) | KEEP

---

## Summary

| Action | Count |
|--------|-------|
| KEEP | 45 |
| EXTRACT | 52 |
| DELETE | 23 |

---

## Root: Subjects/

### KEEP (active, referenced, or canonical)

| File | Reason |
|------|--------|
| `lcc_flat.csv` | **Canonical.** Referenced by load_federation_metadata.py, federation_mapper.py, subject_concept_workflow.py. LCC classification backbone. |
| `lcsh-implementation-guide.md` | Reference doc for LCSH subject backbone. 847 lines, authoritative. |
| `lcc_processing_progress.md` | Status tracker for LCC class processing. Active reference. |
| `AUTOMATION_GUIDE.md` | LCC automation workflow. Referenced by progress doc. |
| `parse_lcc_outline.md` | LCC outline parsing instructions. |
| `LCC/pull_subjects.py` | Generates lcc_flat.csv from LCC hierarchy JSONs. **Keep in LCC/.** |
| `2-10-26-latten_lcc.py` | Flattens LCC JSON → lcc_flat.csv. Used by LCC pipeline. |
| `simplify_skos_to_csv.py` | SKOS→CSV converter. Reusable if SKOS dump restored. |

### EXTRACT (move to Archive or scripts)

| File | Action | Destination |
|------|--------|-------------|
| `concepts in the model.md` | Extract | `Archive/Subjects/` — historical model doc |
| `federation.md` | Extract | `Archive/Subjects/` or `docs/architecture/` if still relevant |
| `gobal federation.md` | Extract | `Archive/Subjects/` (typo in name; historical) |
| `local_vs_global.md` | Extract | `Archive/Subjects/` |
| `modern layer.md` | Extract | `Archive/Subjects/` — 127KB, historical |
| `possible finall subject model.md` | Extract | `Archive/Subjects/` (typo; historical) |
| `research assist in architecture.md` | Extract | `Archive/Subjects/` |
| `subject decisions.md` | Extract | `Archive/Subjects/` — 77KB, historical decisions |
| `viaf.md` | Extract | `Archive/Subjects/` |
| `2-12-26-perplexity-Claims-Schema-Final.md` | Extract | `Archive/Subjects/` — claims schema, superseded |
| `import re.py` | Extract | `scripts/legacy/` — LCC outline parser; rename to `parse_lcc_outline.py` (conflicts with stdlib `import re`) |
| `index_scan.py` | Extract | `scripts/legacy/` — Wikidata index scanner |
| `rawindex_clean.py` | Extract | `scripts/legacy/` — cleans rawindex.txt |
| `create_wiki_subject_master.py` | Extract | `scripts/legacy/` — historical periods QID merger |
| `match_lcsh.py` | Extract | `scripts/legacy/` — **broken:** requires chunks dir (deleted) |
| `disciplines_registry.csv` | Extract | `config/` or `CSV/` — CIP disciplines; 383KB |
| `historical_periods_master.csv` | Extract | `Temporal/` or `config/` — QID list |
| `Historical_Periods.txt` | Extract | `Temporal/` or Archive |
| `periodo_unique_tokens.txt` | Extract | `Temporal/` — referenced by Python scripts |
| `query_periods_and_edges.cypher` | Extract | `Cypher/` or `scripts/neo4j/` |
| `quick_period_query.cypher` | Extract | `Cypher/` or `scripts/neo4j/` |
| `processing historical periods.md` | Extract | `Archive/Subjects/` |

### DELETE (obsolete, superseded, or broken)

| File | Reason |
|------|--------|
| `1-15-26-gap-compare-query.tsv` | One-off analysis output. 424KB. |
| `1-15-26-q1 subjects.csv` | One-off query output. |
| `2-4-26-lcc_concepts_sample.json` | Sample; superseded by full hierarchy. |
| `query.csv` | One-off; 117KB. |
| `query_lcsh_enriched.tsv` | One-off; 432KB. |
| `rawindex.txt` | Raw scrape; 55KB. Clean version is rawindex_clean output. |
| `sample_token_qid_enriched.csv` | One-off enrichment; 581KB. |
| `sample_token_qid_enriched_copy.csv` | Duplicate; 131KB. |
| `subject_candidates.csv` | Duplicate of disciplines_registry.csv (same size 383KB). |
| `q1 query.txt` | One-off query. |
| `romanRepublicIcon.webp` | UI asset; doesn't belong in Subjects. Move to `assets/` or delete. |
| `subjectOntology.png` | Diagram; 970KB. Move to docs or delete. |
| `Triple_Canon_Knowledge_Architecture__Conceptual_to_Logical_Model.png` | Diagram; 955KB. |
| `United_States_USA_Sample.tl` | 1.1MB; unknown format. Delete if not referenced. |
| `subjects.skosrdf.jsonld.gz` | **65MB.** SKOS dump. In .gitignore territory. Delete if chunks gone and not re-downloading. |

---

## Subjects/CIP/

### KEEP

| File | Reason |
|------|--------|
| `2-11-26-pull_subjects.py` | CIP pipeline entry point. |
| `disciplines_registry.sparql` | SPARQL for CIP. |
| `cip_code,cip_title,lcc_classes,lcsh_term.csv` | Crosswalk. |
| `scripts_data/cip_wikidata_enrich.py` | Enrichment script. |
| `scripts_data/2-11-26-cip_cleaner.py` | Pipeline script. |
| `scripts_data/2-11-26-cip_qid.py` | Pipeline script. |
| `scripts_data/2-11-26-cip_splitter.py` | Pipeline script. |
| `scripts_data/2-11-26-concept_splitter.py` | Pipeline script. |
| `scripts_data/2-11-26-enhanced_cleaner_subject.py` | Pipeline script. |

### EXTRACT (move CIP to scripts/authority or Archive)

| File | Action | Destination |
|------|--------|-------------|
| Entire `CIP/` dir | Extract | `scripts/authority/cip/` for scripts; `output/archive/cip/` for runlogs and intermediate CSVs. CIP is academic-discipline taxonomy; separate from LCC/LCSH. |

**CIP runlogs and large CSVs:** Move to `output/archive/cip/`:
- `runlog-*.txt` (all)
- `2-11-26-*.csv` (intermediate outputs)
- `scripts_data/*.csv` except small config (ciplist.csv, concepts.csv if needed)

### DELETE (CIP)

| File | Reason |
|------|--------|
| `__pycache__/` | Generated. |
| `scripts_data/__pycache__/` | Generated. |
| `scripts_data/runlog-cip_wikidata_enrich.txt` | 693KB runlog. |
| `scripts_data/runlog-2-11-26-cip_qid.txt` | 361KB runlog. |
| Duplicate CSVs in scripts_data (cip_wikidata_rich vs 2-11-26-cip_wikidata_rich) | Keep one canonical. |

---

## Subjects/LCC/

### KEEP

| File | Reason |
|------|--------|
| `pull_subjects.py` | Produces lcc_flat.csv. **Actively used.** |
| All `lcc_*_hierarchy.json` | Source data for lcc_flat.csv. ~35 files. |
| `lcc_flat.csv` | **Lives in Subjects/ root** (from 2-10-26-latten_lcc.py). LCC/ has JSONs only. |

### EXTRACT

| File | Action |
|------|--------|
| `lcc_PB_PH_languages_backbone (1).json` | Rename: remove " (1)" — duplicate naming. |
| `lcc_PN_literature_general_hierarchy (1).json` | Same. |
| `lcc_R_medicine_hierarchy_part1.json`, `part2.json` | Fragments; merge or delete if superseded by lcc_R_medicine_hierarchy.json. |

### DELETE

| File | Reason |
|------|--------|
| (none) | LCC hierarchy JSONs are all useful. |

---

## Subjects/neo4j-xml-converter/

### EXTRACT

| Item | Action | Destination |
|------|--------|-------------|
| Entire `neo4j-xml-converter/` | Extract | `scripts/tools/neo4j-xml-converter/` or standalone repo. TypeScript project for XML→Neo4j. Generic tool, not Subjects-specific. |

---

## Execution Order

1. **Create destinations:** `Archive/Subjects/`, `output/archive/cip/`, `scripts/authority/cip/`
2. **Delete** obsolete files (runlogs, one-off outputs, duplicates)
3. **Extract** docs → Archive, scripts → scripts/legacy or scripts/authority
4. **Rename** `import re.py` → `parse_lcc_outline_utils.py` (avoid stdlib clash)
5. **Update** any hardcoded paths in scripts that reference moved files

---

## Dependencies to Update After Move

- `Python/enrich_periodo_tokens_wikidata.py` → `Subjects/periodo_unique_tokens.txt` (extract to Temporal/)
- `Python/extract_periodo_place_tokens.py` → `Subjects/periodo_unique_tokens.txt`
- `Python/sample_token_qid_enrichment.py` → `Subjects/sample_token_qid_enriched.csv` (DELETE target)
- `scripts/backbone/temporal/compare_periods.py` → `Subjects/query.tsv` (not in list; check)
- `rawindex_clean.py` → `Subjects/rawindex.txt` (DELETE target)

---

## Recommended Minimal Keep Set (if aggressive)

**Root:** lcc_flat.csv, lcsh-implementation-guide.md, lcc_processing_progress.md, AUTOMATION_GUIDE.md, parse_lcc_outline.md, simplify_skos_to_csv.py, 2-10-26-latten_lcc.py

**LCC/:** pull_subjects.py, all lcc_*_hierarchy.json (except (1) duplicates)

**CIP/:** Extract whole dir to scripts/authority/cip/; keep scripts, archive data.

**neo4j-xml-converter/:** Extract to scripts/tools/.
