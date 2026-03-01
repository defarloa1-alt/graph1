# Enrich SubjectConcepts from Authorities — Specification

**Version:** 1.0  
**Date:** 2026-02-21  
**Status:** Spec complete; implementation blocked on `subjects_simplified.csv`  
**Replaces:** QID-first enrichment in `enrich_subject_concept_authority_ids.py`

---

## 1. Purpose

Invert the enrichment flow: **authority systems define what exists. SubjectConcepts are positioned within them — not used to query them.**

The current pipeline (QID → Wikidata P244/P2163/P1149) produces:
- Dewey-in-P1149 written as LCC ranges
- LCNAF identifiers written as LCSH headings
- 40+ QIDs with no properties → empty enrichment silently
- All tagged `source_claim: wikidata_harvested` with no verification

The correct pipeline starts from SubjectConcept labels and scope notes, searches authority files by string, confirms via hierarchy context, and writes `source_claim: federation_retrieved`. Wikidata becomes a **validator** in a final step, not the enrichment source.

---

## 2. Prerequisites

| Prerequisite | Required? | Path | Build |
|--------------|-----------|------|-------|
| **LCSH** | **Yes** | `Subjects/subjects_simplified.csv` | `gunzip -k Subjects/subjects.skosrdf.jsonld.gz` + `python Subjects/simplify_skos_to_csv.py` |
| **FAST** | No (graceful degradation) | `Python/fast/key/FASTTopical_parsed.csv` or LCSH→FAST index | Parse `FASTTopical.marcxml` |
| **LCC** | No (graceful degradation) | LC SRU API or local `Subjects/lcc_flat.csv` | — |
| **SubjectConcept labels** | Yes | `output/subject_concepts/subject_concept_anchors_qid_canonical.json` or Neo4j | Already available |

**Minimum viable run:** LCSH only. FAST and LCC are optional; script degrades gracefully when absent.

---

## 3. Flow

```
SubjectConcept.label (+ scope_note if present)
        ↓
subjects_simplified.csv  →  candidate sh… headings (string match)
        ↓
Score + confirm (prefLabel exact / altLabel / BT context)
        ↓
sh… → fast_index (if available) → fst…
        ↓  
sh… → LC SRU 050 field (if available) → lcc_range
        ↓
Write to graph: lcsh_id, fast_id, lcc_range, source_claim: federation_retrieved
        ↓
QID check: does Wikidata P244 agree? If not → flag for review
```

---

## 4. Five Label Types (Core Design Choice)

SubjectConcept labels are **historiographical concept descriptions**, not LCSH headings. Examples:

- `"Institutions: Senate, Assemblies, Magistracies"` — no single LCSH match
- `"Marriage alliances and political kinship"` — may map to multiple or none
- `"Roman Republic"` — maps to `sh85115055` (Rome--History--Republic, 510-30 B.C.)

The matching logic must **decompose** labels. Getting decomposition wrong produces:
- **False matches** (too broad) — e.g. "Senate" → generic LCSH
- **Empty results** (too strict) — exact string match fails

### 4.1 Label decomposition strategy

| Type | Example | Strategy |
|------|---------|----------|
| **1. Colon-separated** | "Institutions: Senate, Assemblies, Magistracies" | Split on `:`, match each segment; prefer narrower (rightmost) if multiple candidates |
| **2. Comma-separated** | "Trade routes and maritime networks" | Treat as phrase; also try sub-phrases ("maritime networks", "trade routes") |
| **3. Parenthetical** | "Early Republic (periodization)" | Strip parenthetical; use as hint for facet, not for matching |
| **4. Single concept** | "Roman Republic" | Direct match |
| **5. Compound phrase** | "Land reform, redistribution, agrarian policy" | Try full phrase first; fall back to key terms ("land reform", "agrarian policy") |

### 4.2 BT chain scope confirmation (safety net)

Any `sh…` candidate that does **not** trace back to a Roman-history ancestor gets **penalised**. Ancestors include:

- `sh85115055` (Rome--History--Republic, 510-30 B.C.)
- `sh85115025` (Rome--History--Kings, 753-510 B.C.)
- `sh85115026` (Rome--History--Republic, 265-30 B.C.)
- Broader: Rome--History, Italy--History, Classical antiquities, etc.

**Scoring:** Candidate with BT chain reaching Roman-history ancestor: +1.0. No path: 0.0 or reject.

---

## 5. Matching Logic

### 5.1 Input

- `subjects_simplified.csv` columns: `id`, `prefLabel`, `altLabel`, `broader`, `narrower`
- `id` format: `http://id.loc.gov/authorities/subjects/sh85115055` → extract `sh85115055`

### 5.2 Match steps

1. **Normalise** SubjectConcept label: lowercase, strip parentheticals, split on `:` and `,`
2. **Generate query terms** from decomposition (see 4.1)
3. **Search** `prefLabel` and `altLabel` (pipe-separated in CSV) for each term
4. **Score** each candidate:
   - Exact prefLabel match: 1.0
   - Exact altLabel match: 0.9
   - Partial prefLabel: 0.7
   - Partial altLabel: 0.6
   - BT scope penalty: 0.0 if no Roman-history ancestor
5. **Select** best candidate above threshold (e.g. 0.6); if tie, prefer narrower (more specific)
6. **Confirm** via BT chain lookup in same CSV (`broader` column)

### 5.3 Output per SubjectConcept

```python
{
    "qid": "Q105427",
    "label": "Institutions: Senate, Assemblies, Magistracies",
    "lcsh_id": "sh85115062",           # Rome--Politics and government--510-30 B.C.
    "lcsh_heading": "Rome--Politics and government--510-30 B.C.",
    "fast_id": "fst01204903",          # if FAST available
    "lcc_range": "DG254",              # if LC SRU available
    "match_score": 0.85,
    "match_type": "prefLabel_partial",
    "source_claim": "federation_retrieved",
    "bt_scope_confirmed": True
}
```

---

## 6. FAST (optional)

- **If available:** Build index `sh… → fst…` from `FASTTopical_parsed.csv` (column `LCSH_ID` or equivalent from parse script)
- **If missing:** Skip; `fast_id` remains null. Log: `FAST index not found; skipping fast_id lookup`

---

## 7. LCC (optional)

- **If available:** Query LC SRU with `sh…` (or LCC API), extract 050 field → `lcc_range`
- **Alternative:** Use `Subjects/lcc_flat.csv` for label→code lookup if SRU unavailable
- **If missing:** Skip; `lcc_range` remains null. Log: `LCC lookup not configured; skipping lcc_range`

---

## 8. Write to graph

```cypher
MATCH (sc:SubjectConcept {qid: $qid})
SET sc.lcsh_id = $lcsh_id,
    sc.lcsh_heading = $lcsh_heading,
    sc.fast_id = CASE WHEN $fast_id IS NOT NULL THEN $fast_id ELSE sc.fast_id END,
    sc.lcc_range = CASE WHEN $lcc_range IS NOT NULL THEN $lcc_range ELSE sc.lcc_range END,
    sc.source_claim = 'federation_retrieved',
    sc.authority_match_score = $match_score,
    sc.authority_match_type = $match_type
```

**Never null out** existing values for `fast_id` or `lcc_range` when optional steps are skipped.

---

## 9. Wikidata validator (step 6)

**Rename:** `enrich_subject_concept_authority_ids.py` → `validate_wikidata_authority_properties.py`

**Role:** Read-only. After authority-first enrichment runs:

1. Fetch P244, P2163, P1149, P1036 from Wikidata for each QID
2. Compare to graph values (`lcsh_id`, `fast_id`, `lcc_range`)
3. **Flag mismatches:**
   - P244 ≠ lcsh_id → `wikidata_lcsh_mismatch`
   - P1149 contains Dewey pattern (e.g. `937.05`) → `wikidata_p1149_dewey_error`
   - P244 looks like LCNAF (e.g. `n` prefix) → `wikidata_p244_lcnaf_error`
4. Write flags to `output/subject_concepts/wikidata_validation_report.md`
5. **Do not overwrite** graph values with Wikidata. Authority-first wins.

---

## 10. Script interface

```
enrich_subject_concepts_from_authorities.py
  --lcsh-csv PATH          Subjects/subjects_simplified.csv (required)
  --anchors PATH           output/subject_concepts/subject_concept_anchors_qid_canonical.json
  --fast-csv PATH          Python/fast/key/FASTTopical_parsed.csv (optional)
  --lcc-sru                Enable LC SRU lookup (optional)
  --dry-run                No Neo4j write; output JSON/CSV
  --write                  Write to Neo4j
  --neo4j-uri, --neo4j-password
```

---

## 11. Outputs

| Output | When | Content |
|--------|------|---------|
| `output/subject_concepts/authority_enrichment_YYYYMMDD.json` | Always | Full results per QID |
| `output/subject_concepts/authority_enrichment_review.md` | Always | Human-readable table: QID, label, lcsh_id, match_score, status |
| Neo4j | `--write` | Updated SubjectConcept nodes |

---

## 12. Status values

| Status | Meaning |
|--------|---------|
| `MATCHED` | lcsh_id assigned, BT scope confirmed |
| `MATCHED_UNCONFIRMED` | lcsh_id assigned, BT scope not confirmed (penalised) |
| `NO_MATCH` | No candidate above threshold |
| `AMBIGUOUS` | Multiple candidates, manual review needed |
| `SKIPPED` | Suspect QID (e.g. Q1234567, Q3952) |

---

## 13. Sequencing

1. **Now:** Build LCSH (`gunzip` + `simplify_skos_to_csv.py`) — unblocks first run
2. **Implement:** `enrich_subject_concepts_from_authorities.py` with LCSH-only path
3. **Test:** Run against 61 labels; tune decomposition and thresholds
4. **Later:** Add FAST when `FASTTopical_parsed.csv` exists; add LCC when SRU or fallback ready
5. **Rename:** `enrich_subject_concept_authority_ids.py` → `validate_wikidata_authority_properties.py`; repurpose as validator

---

## 14. References

- `Subjects/simplify_skos_to_csv.py` — produces subjects_simplified.csv
- `Subjects/subjects.skosrdf.jsonld.gz` — LCSH source (id.loc.gov)
- `output/subject_concepts/subject_concept_anchors_qid_canonical.json` — 61 labels
- `scripts/backbone/subject/enrich_subject_concept_authority_ids.py` — current (to become validator)
- `docs/architecture/SUBJECT_CONCEPT_ECOSYSTEM_DISCOVERY.md` — authority source status
