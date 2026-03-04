# ADR-013: Migrate Hardcoded Temporal Bridge and Federation Scoring Rules to Decision Tables

Status: proposed
Date: 2026-03-04
Canonical architecture anchor: `sysml/DMN_DECISION_TABLES.md`

## Context

Two scripts central to person/family tree construction contain hardcoded business rules that should be governed as decision tables:

1. **`scripts/processing/temporal_bridge_discovery.py`** — Hardcodes 11 DIRECT relationship types, 24 BRIDGING relationship types, 5 gold bridge patterns, evidential marker keywords, and numeric gap thresholds (150 years for rejection, confidence 0.75 for undated, 0.1 for impossibility). These rules determine whether a family relationship claim (PARENT_OF, MARRIED_TO, etc.) is temporally plausible.

2. **`scripts/federation/federation_scorer.py`** — Hardcodes component weights (place_qid=30, period_qid=30, geo_context_qid=20, temporal_bounds=15, relationships=5) and state boundaries (FS0: 0-39, FS1: 40-59, FS2: 60-79, FS3: 80-100). D15–D18 exist in the graph for federation scoring but the code does not read them — it uses its own constants.

For person/family tree work driven from Wikidata QIDs, these are the two rule sets that matter. The claim ingestion pipeline's fallacy detection, confidence scoring, and FSA-layer concerns are downstream and out of scope for this ADR.

### Why this matters for family trees

The temporal bridge validator is the **sanity check** for Wikidata-sourced family relationships. If Wikidata says person A is PARENT_OF person B but there is a 300-year gap, the validator flags it. The relationship type sets and gap thresholds directly control which family claims are accepted or flagged — these should be tuneable without code changes.

The federation scorer determines how "complete" a person node is (does it have a QID, temporal bounds, place links?). The weights control which dimensions matter most. For ancient persons with sparse data, the relative weighting of available vs missing dimensions affects downstream triage.

## Decision

### D33 DETERMINE temporal bridge track

**Purpose:** Route relationship types to validation tracks (DIRECT_HISTORICAL / BRIDGING_DISCOVERY / UNKNOWN) and apply track-specific temporal gap thresholds. First matching row wins.

**Primary consumer:** `scripts/processing/temporal_bridge_discovery.py`

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| relationship_type | String | Claim relationship type (e.g. PARENT_OF, EXCAVATED_REMAINS_OF) |
| temporal_gap | Integer | Absolute year difference between source and target entities |
| has_temporal_data | Boolean | Whether both entities have date information |

**Output:** `track: String`, `valid: Boolean`, `confidence: Real`, `reason: String`

**Hit policy:** FIRST

**SYS_Threshold:** temporal_gap_direct_max (150), temporal_gap_high_priority (500), confidence_no_temporal_data (0.75), confidence_temporal_impossibility (0.10)

**Table A — Track assignment (relationship_type → track)**

| # | relationship_type | track |
|---|-------------------|-------|
| 1 | FOUGHT_ALONGSIDE | DIRECT_HISTORICAL |
| 2 | MARRIED_TO | DIRECT_HISTORICAL |
| 3 | PARENT_OF | DIRECT_HISTORICAL |
| 4 | TAUGHT | DIRECT_HISTORICAL |
| 5 | MET_WITH | DIRECT_HISTORICAL |
| 6 | DEFEATED_IN_BATTLE | DIRECT_HISTORICAL |
| 7 | NEGOTIATED_WITH | DIRECT_HISTORICAL |
| 8 | ALLIED_WITH | DIRECT_HISTORICAL |
| 9 | BETRAYED | DIRECT_HISTORICAL |
| 10 | COMPETED_WITH | DIRECT_HISTORICAL |
| 11 | ADVISED | DIRECT_HISTORICAL |
| 12 | DISCOVERED_EVIDENCE_FOR | BRIDGING_DISCOVERY |
| 13 | EXCAVATED_REMAINS_OF | BRIDGING_DISCOVERY |
| 14 | REINTERPRETED | BRIDGING_DISCOVERY |
| 15 | CHALLENGED_NARRATIVE_OF | BRIDGING_DISCOVERY |
| 16 | PROVIDED_NEW_EVIDENCE_FOR | BRIDGING_DISCOVERY |
| 17 | REFUTED_CLAIM_ABOUT | BRIDGING_DISCOVERY |
| 18 | CITED_HISTORICAL_PRECEDENT | BRIDGING_DISCOVERY |
| 19 | MODELED_ON | BRIDGING_DISCOVERY |
| 20 | DREW_INSPIRATION_FROM | BRIDGING_DISCOVERY |
| 21 | EXPLICITLY_REFERENCED | BRIDGING_DISCOVERY |
| 22 | DRAMATIZED | BRIDGING_DISCOVERY |
| 23 | DEPICTED | BRIDGING_DISCOVERY |
| 24 | ADAPTED | BRIDGING_DISCOVERY |
| 25 | COMMEMORATED | BRIDGING_DISCOVERY |
| 26 | PORTRAYED | BRIDGING_DISCOVERY |
| 27 | VALIDATED_CLAIM_ABOUT | BRIDGING_DISCOVERY |
| 28 | DISPROVED_CLAIM_ABOUT | BRIDGING_DISCOVERY |
| 29 | DATED_ARTIFACT_FROM | BRIDGING_DISCOVERY |
| 30 | ANALYZED_DNA_FROM | BRIDGING_DISCOVERY |
| 31 | ISOTOPE_ANALYSIS_SHOWED | BRIDGING_DISCOVERY |
| 32 | CARBON_DATED | BRIDGING_DISCOVERY |
| 33 | ANALYZED_ARTIFACT_FROM | BRIDGING_DISCOVERY |
| 34 | INSPIRED_BY | BRIDGING_DISCOVERY |
| 35 | COMPARED_TO_BY | BRIDGING_DISCOVERY |
| 36 | TRANSLATED_WORK_OF | BRIDGING_DISCOVERY |
| 37 | * (default) | UNKNOWN |

**Table B — Gap validation (track + temporal_gap → validity)**

| # | track | has_temporal_data | temporal_gap | valid | confidence | reason |
|---|-------|-------------------|-------------|-------|------------|--------|
| 1 | DIRECT_HISTORICAL | FALSE | — | TRUE | confidence_no_temporal_data | no_temporal_data_available |
| 2 | DIRECT_HISTORICAL | TRUE | > temporal_gap_direct_max | FALSE | confidence_temporal_impossibility | temporal_impossibility_direct_claim |
| 3 | DIRECT_HISTORICAL | TRUE | ≤ temporal_gap_direct_max | TRUE | (computed) | contemporaneous_plausible |
| 4 | BRIDGING_DISCOVERY | — | — | TRUE | (computed) | bridge_validated |
| 5 | UNKNOWN | — | — | FALSE | 0.0 | unknown_relationship_type |

**Family tree impact:** Rows 1–11 in Table A are the family-relevant relationship types. Row 2 in Table B is the 150-year sanity check that catches Wikidata data quality errors in PARENT_OF / MARRIED_TO claims.

---

### D34 DETERMINE person federation completeness

**Purpose:** Score how well-federated a person entity is based on the presence of external identifiers and temporal/spatial data. Complements D15–D18 (which exist in the graph but are not read by `federation_scorer.py`).

**Primary consumer:** `scripts/federation/federation_scorer.py`

**Inputs:**

| Input | Type | Source |
|-------|------|--------|
| component | String | Federation component name |
| component_present | Boolean | Whether the component has a non-null value |

**Output:** `weight: Integer` (contribution to federation score, max total = 100)

**Hit policy:** UNIQUE (one row per component)

**Table A — Place/Period subgraph weights**

| # | component | weight | rationale |
|---|-----------|--------|-----------|
| 1 | place_qid | 30 | Place federated to Wikidata (WHAT dimension) |
| 2 | period_qid | 30 | Period federated to Wikidata (WHEN dimension) |
| 3 | geo_context_qid | 20 | Geographic context federated (WHERE dimension) |
| 4 | temporal_bounds | 15 | Temporal signal (start/end dates) present |
| 5 | relationships | 5 | Vertex jump edges exist |

**Table B — Subject/authority weights (for SubjectConcept scoring)**

| # | component | weight | rationale |
|---|-----------|--------|-----------|
| 1 | lcsh_id | 30 | Library of Congress Subject Headings |
| 2 | fast_id | 30 | Faceted Application of Subject Terminology |
| 3 | lcc_class | 20 | Library of Congress Classification |
| 4 | qid | 20 | Wikidata QID |

**Table C — Score → federation state mapping**

| # | score_min | score_max | federation_state |
|---|-----------|-----------|-----------------|
| 1 | 0 | 39 | FS0_UNFEDERATED |
| 2 | 40 | 59 | FS1_BASE |
| 3 | 60 | 79 | FS2_FEDERATED |
| 4 | 80 | 100 | FS3_WELL_FEDERATED |

**Relationship to D15–D18:** D15 currently stores federation state routing logic in the graph. D16–D18 store place, period, and subject authority weights. D34 unifies the code-side view: `federation_scorer.py` should read D34 (or equivalently D15–D18) from the graph instead of using hardcoded `WEIGHTS` and `STATES` dicts. The table structures are intentionally compatible — D34 Tables A/B map to D16/D17/D18 rows, and D34 Table C maps to D15 state classification.

**Migration path:** Either (a) make `federation_scorer.py` read D15–D18 directly, or (b) create D34 as the unified code-facing table and deprecate the code-side constants. Option (a) is simpler if D15–D18 row structures are stable.

---

## Implementation

### Phase 1 — Register SYS_Threshold nodes

Create four new threshold nodes for temporal bridge validation:

```cypher
MERGE (t:SYS_Threshold {name: 'temporal_gap_direct_max'})
SET t.value = 150, t.unit = 'years',
    t.decision_table = 'D33_DETERMINE_temporal_bridge_track',
    t.rationale = 'Allow ~3 generations buffer for direct historical claims';

MERGE (t:SYS_Threshold {name: 'temporal_gap_high_priority'})
SET t.value = 500, t.unit = 'years',
    t.decision_table = 'D33_DETERMINE_temporal_bridge_track',
    t.rationale = 'Flag bridges spanning 500+ years as HIGH priority';

MERGE (t:SYS_Threshold {name: 'confidence_no_temporal_data'})
SET t.value = 0.75, t.unit = 'score',
    t.decision_table = 'D33_DETERMINE_temporal_bridge_track',
    t.rationale = 'Penalised confidence when no dates available';

MERGE (t:SYS_Threshold {name: 'confidence_temporal_impossibility'})
SET t.value = 0.10, t.unit = 'score',
    t.decision_table = 'D33_DETERMINE_temporal_bridge_track',
    t.rationale = 'Near-zero confidence for temporally impossible direct claims';
```

### Phase 2 — Create SYS_DecisionTable + SYS_DecisionRow nodes

```cypher
// D33 table node
MERGE (dt:SYS_DecisionTable {table_id: 'D33'})
SET dt.name = 'D33_DETERMINE_temporal_bridge_track',
    dt.hit_policy = 'FIRST',
    dt.purpose = 'Route relationship types to validation tracks and apply gap thresholds',
    dt.primary_consumer = 'temporal_bridge_discovery.py',
    dt.adr = 'ADR-013';

// D33 track assignment rows (family-relevant subset shown)
MERGE (r:SYS_DecisionRow {row_id: 'D33_R01'})
SET r.table_id = 'D33', r.relationship_type = 'PARENT_OF',
    r.track = 'DIRECT_HISTORICAL', r.priority = 1;
MERGE (dt)-[:HAS_ROW]->(r)
WITH dt

MERGE (r:SYS_DecisionRow {row_id: 'D33_R02'})
SET r.table_id = 'D33', r.relationship_type = 'MARRIED_TO',
    r.track = 'DIRECT_HISTORICAL', r.priority = 2;
MERGE (dt)-[:HAS_ROW]->(r)
WITH dt

MERGE (r:SYS_DecisionRow {row_id: 'D33_R03'})
SET r.table_id = 'D33', r.relationship_type = 'FOUGHT_ALONGSIDE',
    r.track = 'DIRECT_HISTORICAL', r.priority = 3;
MERGE (dt)-[:HAS_ROW]->(r);
// ... remaining rows follow same pattern for all 37 entries
```

### Phase 3 — Update code to read from graph

`temporal_bridge_discovery.py` changes:
1. Add a `_load_track_config()` method that queries `SYS_DecisionTable {table_id: 'D33'}` and its `HAS_ROW` children.
2. Build `DIRECT_CLAIM_TYPES` and `BRIDGING_CLAIM_TYPES` sets from rows instead of class constants.
3. Read `temporal_gap_direct_max` and `confidence_no_temporal_data` from `SYS_Threshold` instead of hardcoded `150` and `0.75`.
4. Retain current hardcoded values as fallbacks (same pattern as `claim_ingestion_pipeline.py:533-537`).

`federation_scorer.py` changes:
1. Add a `_load_weights()` method that queries D15–D18 (or D34) for component weights.
2. Add a `_load_states()` method that queries D15 (or D34 Table C) for score→state boundaries.
3. Retain `WEIGHTS` and `STATES` dicts as fallbacks.

## Boundaries

1. This ADR covers only the two rule sets identified. Fallacy scoring, KKO gating, role validation, and other hardcoded rules identified in the codebase audit are out of scope — they are FSA-layer concerns downstream of Wikidata-sourced person data.
2. D33 does not change relationship type semantics — it only externalises the existing classification.
3. D34 does not replace D15–D18 — it provides a unified code-facing view compatible with them.
4. Gold bridge patterns (GOLD_PATTERN_1–5 in `temporal_bridge_discovery.py`) and evidential marker keywords are deferred — they are stable reference data with lower churn than thresholds.

## Consequences

Positive:
1. Gap thresholds (150 years, 0.75 confidence) tuneable without code deploy.
2. New relationship types (e.g. ADOPTED, FOSTERED) can be added to the track table without code changes.
3. Federation weights adjustable for different entity domains (person vs place vs concept).
4. Audit trail — threshold changes tracked as graph mutations with timestamps.

Tradeoffs:
1. Graph query at initialisation adds latency (~1 query per table).
2. Fallback logic needed for offline/disconnected operation.
3. Two sources of truth during migration (graph + code fallbacks).

## Invariants

1. Every threshold read from graph must have a hardcoded fallback in the consuming script.
2. Track assignment is exhaustive — every relationship type resolves to a track (UNKNOWN as default).
3. Federation state boundaries must be contiguous and cover 0–100 with no gaps.

## Related Documents

1. `sysml/DMN_DECISION_TABLES.md` — D-table registry (D33/D34 to be added)
2. `md/Architecture/ADR-006-Claim-Confidence-Decision-Model.md` — Precedent for ordered single-hit tables
3. `md/Architecture/ADR-002-Policy-Gate-and-Update-Operator-Separation.md` — U/Pi/Commit separation
4. `Person/adr007_extracted.txt` — Person schema (§7 conflict resolution uses temporal gap logic)
5. `scripts/processing/temporal_bridge_discovery.py` — Source of D33 hardcoded rules
6. `scripts/federation/federation_scorer.py` — Source of D34 hardcoded rules
