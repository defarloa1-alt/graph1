# SubjectConcept "Suspect" Scope — Clarification for Architect

**Date:** 2026-02-21  
**Context:** Before running `--write` on all 61, architect asked: what does "suspect" mean specifically?

---

## 1. LCSH Sample — FAST Crosswalk Check

**File:** `LCSH/skos_subjects/subjects_sample_200.jsonld`  
**Format:** JSONL (one JSON object per line; each has `@graph` with SKOS concepts)

**Result:** **No `skos:exactMatch` or `owl:sameAs` to FAST** in the sample. Records have:
- `@id`, `@type`, `skos:broader`, `skos:prefLabel`, `skos:altLabel`, `skos:inScheme`, `skos:changeNote`
- No `skos:exactMatch`, no `owl:sameAs`, no `http://id.worldcat.org/fast/...`

**Conclusion:** The LCSH SKOS sample does **not** carry the LC linked-data FAST crosswalk. A full SKOS rebuild would need to be from a different LoC export (e.g. id.loc.gov linked-data service) that includes exactMatch. The current sample is LoC authorities format without FAST links.

---

## 2. Suspect Scope — Documented Issues

### A. QID Errors (Known)

| QID | Label | Problem | Status |
|-----|-------|---------|--------|
| **Q3952** | Late Republic (periodization) | Q3952 = Plauen, Germany (city). Correct QID = Q2815472 (Late Roman Republic) | **Fixed** in subject_concept_anchors_qid_canonical.json |
| **Q1234567** | Finance, contracts, and publicani | Placeholder QID | **FLAGGED** — do not write until fixed |

**Scripts:** `enrich_subject_concept_authority_ids.py` skips `SUSPECT_QIDS = {"Q1234567", "Q3952"}`. `verify_anchor_qids.py` catches QID mismatches (e.g. Q3952 label "Late Republic" vs Wikidata "Plauen").

### B. LCSH/FAST Mapping Gaps (from authority_enrichment_review.md)

| Status | Count | Meaning |
|--------|-------|---------|
| **FULL** | 1 | LCSH + FAST + LCC all present |
| **PARTIAL** | 19 | Some of LCSH/FAST/LCC present |
| **MISSING** | 40 | No LCSH, FAST, or LCC from Wikidata |
| **FLAGGED** | 1 | Q1234567 placeholder |

**Note:** "Partial" and "Missing" are from **Wikidata SPARQL** (P244, P2163, P1149). Many SubjectConcepts don't have these properties on their QID in Wikidata. That's a data gap, not necessarily an error.

### C. Structural / Hierarchy Issues

- **Multi-parent:** Q1993655 (civil wars) has 3 parents — Q2815472, Q20720797, Q1392538. Documented as intentional (multi-membership model).
- **Cycles:** Resolved in prior session (Q17167 zero parents).
- **BROADER_THAN:** 65 edges in subject_concept_hierarchy.json.

### D. LLM-Generated Labels vs Federation Coordinates

- **FAST_RESOLUTION_REVIEW.md:** 18 "MEDIUM" items — labels like "Early Republic (periodization)" mapped to parent FAST fst01204885 (Rome--History--Republic) because "Early Republic not in FAST; using parent."
- **Scope:** Period subdivisions, broad concepts (Culture, Economy), and Roman-specific terms (Optimates/Populares) don't have exact FAST matches. Curated mappings use best-available parent or related heading.

---

## 3. Scope of "Suspect" — Summary

| Category | Scope | Blocks --write? |
|----------|-------|-----------------|
| **QID errors** | Q3952 fixed; Q1234567 flagged | Q1234567 only |
| **LCSH/FAST mapping** | 40 MISSING, 19 PARTIAL from Wikidata | No — enrichment is additive |
| **Hierarchy structure** | Multi-parent intentional; cycles fixed | No |
| **LLM label alignment** | 18 MEDIUM confidence FAST mappings | No — human review path exists |

**Recommendation:** Only **Q1234567** blocks a clean run. Resolve or exclude it before `--write` on all 61. The rest are validation/review items, not blockers.
