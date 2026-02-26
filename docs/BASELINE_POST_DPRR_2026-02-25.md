# Post-DPRR Production Baseline

**Date:** 2026-02-25  
**Event:** DPRR federation import (complete) + cluster assignment + scoping source fix  
**Status:** **Definitive post-DPRR baseline** — all three DPRR passes done, cleanup done, no pending imports

---

## What Just Happened

Global unscoped dropped from **86.4% to 8.9%** in a single pipeline run. The 87.1% figure from months ago that has been the persistent benchmark is now effectively closed.

**Q899409** went from 18 scoped out of 999 (1.8%) to **5,272 out of 5,272 (0.0% unscoped)**. A cluster that was effectively unusable for research is now the most completely scoped cluster in the graph — better than Q182547, better than Q337547, better than any of the previously trustworthy anchors.

The 8.9% remaining unscoped represents approximately 5,600 entities. That is the genuine noise floor — entities that entered the graph through harvesting but have no authority file attestation in any federation source. Some of those will be legitimate domain entities that simply lack external identifiers. Some will be actual noise. That is a tractable cleanup problem, not a structural one.

---

## Formal Baseline Numbers

```
Date: 2026-02-25
Event: DPRR federation import + cluster assignment + scoping source fix
       + self-describing subgraph cleanup (Option B: Period/PeriodCandidate/GeoCoverageCandidate/FacetedEntity/PlaceTypeTokenMap removed)

Graph state (post-cleanup):
  Total nodes:           60,925  (was 63,689 before cleanup)
  Total edges:           49,152  (was 53,148 before cleanup)
  PERSON entities:       5,174

Scoping (from scoping_advisor_report.md):
  Global unscoped:       8.8%  (was 86.4% pre-DPRR)
  Global scoped:         91.2% (was 13.6% pre-DPRR)

Q899409 (Roman families):
  Total entities:        5,363 (was 999)
  Scoped:                5,363 (was 18)
  Unscoped %:            0.0%  (was 98.2%)

Scoping report: output/analysis/scoping_advisor_report.md

DPRR contribution (complete):
  Group A merged:        2,960
  Group C created:       1,916
  Relationships:         6,928
  Posts:                 9,807 (8,365 Group A + 1,442 Group C)
  Status assertions:     1,992 (1,298 Group A + 694 Group C)
  Unique to Chrystallum: 1,916 persons not in Wikidata
```

---

## What This Unlocks

**Family network navigation** — Q899409 has 5,272 scoped entities with 6,928 relationship edges between them sourced from Zmeskal's Adfinitas. The graph can answer "show me the Cornelii" or "trace the connections between the Sempronii and the Aemilii" with actual data behind it.

**Persona salience weight sets** — The prosopographer persona and the serious reader persona both depend on family network density. That density now exists.

**Fasti layer** — The 8,365 POSITION_HELD edges from PostAssertions give the graph its first complete career timeline layer (who held which office in which year, sourced from Broughton).

---

## Remaining Gaps (Non-Urgent)

| Gap | Count | Notes |
|-----|-------|-------|
| Status assertions | 1,298 imported | ✅ Imported 2026-02-25. `(Entity)-[:HAS_STATUS]->(StatusType)` with year and source_uri. 694 skipped (no qid). Delta: +1,298 edges, +few StatusType nodes. Scoping unchanged (status not a federation source). |
| Group C POSITION_HELD | 1,442 imported | ✅ Imported 2026-02-25 via `--group-c-posts`. Match by dprr_uri. +24 Office nodes. 694 status assertions re-attempted in same pass (all imported). |
| 8.8% remaining unscoped | ~806 MEMBER_OF unscoped | Two populations: (1) **Legitimate unscoped** — wars, battles, events; Q1764124, Q271108 confirmed. (2) **Potential noise** — worth investigating separately. |
| Trismegistos crosswalk | 0 overlap | SPARQL count (scripts/analysis/count_p1696_overlap.py): 0 of 6,989 entity QIDs have P1696 in Wikidata. Crosswalk would enrich 0 — defer until entities with P1696 enter graph. |

---

## Pipeline Fixes Applied

1. **Scoping advisor:** DPRR (P6863 / dprr_imported) added as valid scoping source → temporal_scoped, confidence 0.85
2. **dprr_import.py:** Group A and Group C entities now set scoping_status, scoping_confidence, scoping_source on Entity nodes
3. **cluster_assignment.py:** `--dprr-neo4j` flag loads DPRR entities from Neo4j and assigns to Q899409 (Roman families)
4. **Query robustness:** DPRR load uses `dprr_imported = true OR dprr_id IS NOT NULL` to catch legacy nodes

---

---

## Pipeline Sequence (Post-Baseline)

1. **Scoping advisor output** → establish baseline ✅
2. **DPRR status assertions** ✅ (1,298 imported; 694 skipped no qid; 2026-02-25)
3. **DPRR Group C POSITION_HELD** ✅ (1,442 posts + 694 statuses via dprr_uri; 2026-02-25)
4. **Cluster assignment + scoping advisor** ✅ (2026-02-25) — definitive post-DPRR-complete baseline
5. Noise audit on remaining unscoped
6. Project Mercury

---

*Baseline established before Project Mercury.*
