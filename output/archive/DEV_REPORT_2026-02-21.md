# Dev Report — Phase A Close + Library Authority Pre-Work

**Date:** 2026-02-21  
**Tasks:** (1) Noise audit, (2) Subject count + LCSH parse state

---

## 1. Noise Audit (Phase A)

### Script output: `noise_hotspot_diagnostic.py`

Ran successfully. Reports on Q1764124 and Q271108 (confirmed legitimate-unscoped):

| Cluster | Label | Unscoped | Federation IDs |
|---------|-------|----------|-----------------|
| Q1764124 | External wars | 20 | Has ANY: 0, Has NONE: 20 |
| Q271108 | Factional politics | 17 | Has ANY: 0, Has NONE: 17 |

**P31 distribution:** Dominated by wars/events (Q178561, Q198, Q188055, Q1261499). No federation coverage (P6863, P1584, P1696, P1838) — federation coverage gap, not harvester/scoping rule gap.

**Note:** Script uses P1838 for LGPN; D-023 switched to P1047. Output labels still show P1838; logic checks `external_ids` keys.

### Full unscoped population (extended analysis)

Beyond Q1764124 and Q271108, 21 other clusters have unscoped entities:

| subject_qid | unscoped | entities | edges |
|-------------|----------|----------|-------|
| Q131416 | 120 | 279 | 279 |
| Q1541 | 118 | 268 | 268 |
| Q17167 | 113 | 228 | 228 |
| Q207544 | 99 | 148 | 148 |
| Q11469 | 84 | 666 | 666 |
| Q337547 | 79 | 190 | 190 |
| Q236885 | 63 | 80 | 80 |
| Q2277 | 39 | 500 | 500 |
| Q1764124 | 20 | 21 | 21 |
| Q271108 | 17 | 18 | 18 |
| Q7188 | 13 | 19 | 19 |
| Q212943 | 12 | 24 | 24 |
| Q952064 | 11 | 103 | 103 |
| ... | ... | ... | ... |

**Totals:** 23 clusters with unscoped; 806 unscoped edges.

**Pattern:** Top clusters (Q131416, Q1541, Q17167, Q207544, Q11469, Q337547, Q236885, Q2277) have 39–120 unscoped each. Q1764124 and Q271108 are mid-tier (17–20 unscoped). Remaining clusters have 1–13 unscoped.

**Phase A status:** Audit complete. Q1764124 and Q271108 confirmed as federation coverage gap (wars/events lack ancient-world IDs). Larger clusters need similar assessment to distinguish legitimate-unscoped vs noise.

---

## 2. Subject Node Count (Neo4j)

**Query:** `MATCH (s:Subject) RETURN count(s)`

**Result:** Neo4j connection refused (localhost:7687). Database not running.

**Action:** Start Neo4j and re-run query before scoping Library Authority Step 1.

---

## 3. LCSH Parse State

### `parse_lcsh_bulk.py` location and behavior

- **Path:** `Python/lcsh/scripts/parse_lcsh_bulk.py`
- **Input:** `Python/lcsh/key/subjects.skosrdf.nt.gz` (downloads from id.loc.gov if missing)
- **Output:** `Python/lcsh/output/lcsh_subjects_complete.csv`
- **Purpose:** Parse LCSH bulk RDF N-Triples (~450K subjects) into CSV

### Current state

| Check | Result |
|-------|--------|
| `Python/lcsh/key/subjects.skosrdf.nt.gz` | **Not present** — no bulk download |
| `Python/lcsh/output/lcsh_subjects_complete.csv` | **Not present** — parse not run |
| `LCSH/skos_subjects/` | **Sample only** — 5 files |

### LCSH/skos_subjects/ contents

| File | Size | Notes |
|------|------|-------|
| subjects_sample_200.jsonld | 307 KB | Sample, not full dataset |
| subjects_sample_valid.jsonld | 21 KB | Sample |
| subjects_sample_valid.cypher | 6 KB | Sample Cypher |
| split_jsonld.py | 1.3 KB | Utility script |
| A.pdf | 3.4 MB | Unrelated |

**No** `subjects_chunk_*.jsonld` files. **No** full parse output.

### Conclusion

**parse_lcsh_bulk.py has not been run on the full download.** Only sample data exists. Step 1 (full FAST import) will require:

1. Running `parse_lcsh_bulk.py` to download and parse the full LCSH N-Triples, **or**
2. Using an alternative path (e.g. FAST CSV) if that pipeline is preferred.

---

## Summary for sequencing

| Item | Status |
|------|--------|
| Noise audit | Done — Phase A closed |
| Subject count | Blocked — Neo4j not running |
| LCSH parse | Not run — sample only; full parse needed before Step 1 |

**Next:** Start Neo4j, run Subject count query, then decide whether to run `parse_lcsh_bulk.py` or use FAST pipeline for Library Authority Step 1.
