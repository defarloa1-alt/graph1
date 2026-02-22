# QID-Seeded SubjectConcept Promotion (Facet-Free) - Implementation Spec
Date: 2026-02-17
Status: Implementation-ready (v0-compatible)

## 1. Scope
This algorithm is generic for any seed QID and does not depend on facets.
It is compatible with v0 rules:
- Bootstrap writes scaffold artifacts only.
- Canonical `:SubjectConcept` writes happen only through explicit promotion.

## 2. Inputs
- `anchor_qid: string`
- `analysis_run_id: string`
- `max_depth_up: int` (default `4`)
- `max_depth_down: int` (default `2`)
- `per_parent_child_cap: int` (default `50`)
- `backlink_properties_allowlist: set[property_id]` (must map to canonical relationship set)
- `max_backlinks_total: int` (default `500`)
- `max_backlinks_per_property: int` (default `100`)
- `max_backlinks_per_top_class: int` (default `75`)
- `backlink_score_threshold_promote: int` (default `5`)
- `backlink_score_threshold_entity: int` (default `3`)
- `discipline_roots: set[qid]` from `WikidataClassMapping` (`is_discipline_root = true`)
- `meta_ceiling_qids: set[qid]` (class/metaclass/concept ceilings)
- `not_filter_qids` and label-pattern filters (disambiguation/category/article-about wrappers)
- `authority_check(qid)` returning:
  - `has_FAST`, `has_LCSH`, `has_ANZSRC`, `has_AAT`, `has_MeSH`

## 3. Deterministic Pipeline
1. Initialize `:AnalysisRun`.
2. Build local scaffold graph around `anchor_qid`:
   - Upward: `P31` lift once if anchor is instance-like, then `P279` chain up to `max_depth_up`.
   - Downward: inverse `P279` up to `max_depth_down` with cap and truncation markers.
3. Harvest backlink statements where `item -> property -> anchor_qid`:
   - Accept only properties in `backlink_properties_allowlist`.
   - Enforce caps per property, per top class, and total.
   - Persist statement-level provenance.
4. Score backlink items deterministically and classify:
   - `PROMOTE_SUBJECTCONCEPT` / `KEEP_AS_ENTITY` / `EVIDENCE_ONLY`.
5. Mark authority-backed candidates.
6. Compute leaf-likeness safely:
   - Local leaf only if no children in local subgraph and no truncation flag.
7. Promote path candidates:
   - From authority-backed leaves, walk upward via `P279` toward discipline roots.
   - Stop expansion at discipline root or meta ceiling.
8. Apply deterministic filter/score:
   - Keep all authority-backed leaves.
   - Keep all discipline roots.
   - Keep internal nodes with sufficient promoted support.
9. Persist promotion decisions as scaffold metadata (`promotion_candidate`, `promotion_reason`).
10. Run explicit promotion command to write canonical `:SubjectConcept`.

## 4. Data Model (Required)
### 4.1 Scaffold
- `(:AnalysisRun {run_id, seed_qid, params_json, created_at})`
- `(:ScaffoldNode {analysis_run_id, qid, wd_label, ceiling_hit, truncated_children, ...})`
- `(:ScaffoldEdge {edge_id, analysis_run_id, wd_property, up_level, down_depth, ...})`
- `(:BacklinkEvidence {analysis_run_id, statement_id, seed_qid, item_qid, property_id, rank, created_at})`
- `(e:ScaffoldEdge)-[:FROM]->(s:ScaffoldNode)`
- `(e:ScaffoldEdge)-[:TO]->(o:ScaffoldNode)`
- `(be:BacklinkEvidence)-[:SOURCE_ITEM]->(i:ScaffoldNode)`
- `(be)-[:TARGET_SEED]->(s:ScaffoldNode)`

Backlink triage fields on `:ScaffoldNode`:
- `backlink_score: int`
- `backlink_score_components_json: string`
- `backlink_candidate_class: string` (`PROMOTE_SUBJECTCONCEPT|KEEP_AS_ENTITY|EVIDENCE_ONLY`)
- `backlink_property_count: int`
- `backlink_statement_count: int`

### 4.2 Canonical
- `(:SubjectConcept {subject_id, qid, label, discipline, authority_ids_json, created_at, updated_at})`
- `(:PromotionEvent {event_id, analysis_run_id, created_at, params_json})`

## 5. Pseudo-Cypher
### 5.1 Constraints
```cypher
CREATE CONSTRAINT analysis_run_unique IF NOT EXISTS
FOR (r:AnalysisRun) REQUIRE r.run_id IS UNIQUE;

CREATE CONSTRAINT scaffold_node_unique IF NOT EXISTS
FOR (n:ScaffoldNode) REQUIRE (n.analysis_run_id, n.qid) IS UNIQUE;

CREATE CONSTRAINT scaffold_edge_unique IF NOT EXISTS
FOR (e:ScaffoldEdge) REQUIRE e.edge_id IS UNIQUE;

CREATE CONSTRAINT backlink_evidence_unique IF NOT EXISTS
FOR (b:BacklinkEvidence) REQUIRE (b.analysis_run_id, b.statement_id) IS UNIQUE;

CREATE CONSTRAINT subjectconcept_qid_unique IF NOT EXISTS
FOR (s:SubjectConcept) REQUIRE s.qid IS UNIQUE;
```

### 5.2 Initialize run
```cypher
MERGE (r:AnalysisRun {run_id: $analysis_run_id})
ON CREATE SET
  r.seed_qid = $anchor_qid,
  r.pipeline_version = $pipeline_version,
  r.params_json = $params_json,
  r.created_at = datetime(),
  r.updated_at = datetime()
ON MATCH SET
  r.updated_at = datetime();
```

### 5.3 Upsert scaffold node
```cypher
MERGE (n:ScaffoldNode {analysis_run_id: $run_id, qid: $qid})
ON CREATE SET
  n.wd_label = $wd_label,
  n.source = 'wikidata_entitydata',
  n.created_at = datetime()
SET
  n.has_FAST = $has_FAST,
  n.has_LCSH = $has_LCSH,
  n.has_ANZSRC = $has_ANZSRC,
  n.has_AAT = $has_AAT,
  n.has_MeSH = $has_MeSH,
  n.is_discipline_root = $is_discipline_root,
  n.ceiling_hit = coalesce($ceiling_hit, false),
  n.truncated_children = coalesce($truncated_children, false),
  n.not_filtered_reason = $not_filtered_reason;
```

### 5.4 Upsert scaffold edge (P279/P31 structural)
```cypher
MATCH (s:ScaffoldNode {analysis_run_id: $run_id, qid: $from_qid})
MATCH (o:ScaffoldNode {analysis_run_id: $run_id, qid: $to_qid})
MERGE (e:ScaffoldEdge {edge_id: $edge_id})
ON CREATE SET
  e.analysis_run_id = $run_id,
  e.wd_property = $wd_property,   // P279 | P31
  e.direction = $direction,       // forward | inverse
  e.up_level = $up_level,
  e.down_depth = $down_depth,
  e.sampled = coalesce($sampled, false),
  e.created_at = datetime()
MERGE (e)-[:FROM]->(s)
MERGE (e)-[:TO]->(o);
```

### 5.5 Ingest backlink evidence (allowlisted properties only)
```cypher
MATCH (seed:ScaffoldNode {analysis_run_id: $run_id, qid: $seed_qid})
MERGE (item:ScaffoldNode {analysis_run_id: $run_id, qid: $item_qid})
ON CREATE SET item.wd_label = $item_label, item.source = 'wikidata_entitydata', item.created_at = datetime()
MERGE (b:BacklinkEvidence {analysis_run_id: $run_id, statement_id: $statement_id})
ON CREATE SET
  b.seed_qid = $seed_qid,
  b.item_qid = $item_qid,
  b.property_id = $property_id,
  b.rank = $rank,
  b.created_at = datetime()
MERGE (b)-[:SOURCE_ITEM]->(item)
MERGE (b)-[:TARGET_SEED]->(seed);
```

Application gate before write:
- `property_id` must be in `backlink_properties_allowlist`.
- Statement rank must not be deprecated.
- `item_qid` must pass NOT filters.

### 5.6 Score and classify backlink candidates
Deterministic score formula:
- `score = 3*authority + 2*discipline_chain + 1*seed_specificity + 1*backlink_density - 2*noise_penalty`

Where:
- `authority = 1` if any of FAST/LCSH/ANZSRC/AAT/MeSH present, else `0`.
- `discipline_chain = 1` if class chain reaches `discipline_roots`, else `0`.
- `seed_specificity = 1` if backlink property is high-signal material/part-of mapping, else `0`.
- `backlink_density = 1` if item has multiple distinct statements to seed within run, else `0`.
- `noise_penalty = 1` if weak/meta wrapper signals present, else `0`.

Candidate class:
- `PROMOTE_SUBJECTCONCEPT` if `score >= backlink_score_threshold_promote` (default `5`)
- `KEEP_AS_ENTITY` if `score >= backlink_score_threshold_entity` and `< promote` (default `3..4`)
- `EVIDENCE_ONLY` otherwise

```cypher
MATCH (n:ScaffoldNode {analysis_run_id: $run_id})
SET n.backlink_score = $score,
    n.backlink_score_components_json = $score_components_json,
    n.backlink_candidate_class =
      CASE
        WHEN $score >= $score_threshold_promote THEN 'PROMOTE_SUBJECTCONCEPT'
        WHEN $score >= $score_threshold_entity THEN 'KEEP_AS_ENTITY'
        ELSE 'EVIDENCE_ONLY'
      END;
```

### 5.7 Mark deterministic promotion candidates in scaffold
```cypher
MATCH (n:ScaffoldNode {analysis_run_id: $run_id})
WITH n,
     (coalesce(n.has_FAST,false) OR coalesce(n.has_LCSH,false) OR
      coalesce(n.has_ANZSRC,false) OR coalesce(n.has_AAT,false) OR
      coalesce(n.has_MeSH,false)) AS authority_backed
SET n.authority_backed = authority_backed;

MATCH (n:ScaffoldNode {analysis_run_id: $run_id})
OPTIONAL MATCH (e:ScaffoldEdge {analysis_run_id: $run_id, wd_property: 'P279', direction: 'inverse'})-[:FROM]->(n)
OPTIONAL MATCH (e)-[:TO]->(c:ScaffoldNode {analysis_run_id: $run_id})
WITH n, count(c) AS local_child_count
WHERE n.authority_backed = true
  AND coalesce(n.truncated_children,false) = false
  AND local_child_count = 0
SET n.authority_leaf = true;
```

Note: production implementation should compute leafness in application logic to avoid query-shape errors and to incorporate full truncation metadata.

### 5.8 Promote to canonical only via explicit command
```cypher
MERGE (pe:PromotionEvent {event_id: $event_id})
ON CREATE SET pe.analysis_run_id = $run_id, pe.created_at = datetime(), pe.params_json = $params_json;

UNWIND $promoted_qids AS qid
MATCH (sn:ScaffoldNode {analysis_run_id: $run_id, qid: qid})
WHERE coalesce(sn.promotion_candidate,false) = true
  AND coalesce(sn.ceiling_hit,false) = false
  AND sn.not_filtered_reason IS NULL
MERGE (sc:SubjectConcept {qid: sn.qid})
ON CREATE SET
  sc.subject_id = randomUUID(),
  sc.created_at = datetime()
SET
  sc.label = sn.wd_label,
  sc.discipline = coalesce(sn.is_discipline_root,false),
  sc.authority_ids_json = $authority_map[sn.qid],
  sc.updated_at = datetime()
MERGE (pe)-[:PROMOTED]->(sc);
```

## 6. Promotion Decision Rules (Facet-Free)
- `promotion_candidate = true` iff:
  - Node is on at least one authority-backed path to a discipline root, and
  - Node is not excluded by NOT filters/meta ceiling, and
  - Node is not a truncation-artifact leaf, and
  - Node has `backlink_candidate_class = PROMOTE_SUBJECTCONCEPT` or qualifies through the core hierarchy rules as anchor/root/authority-leaf.
- Always keep:
  - Anchor node.
  - Authority-backed true leaves.
  - Discipline roots.

Backlink scoring defaults:
- `promote` threshold: `>=5`
- `entity` threshold: `3..4`
- `evidence_only`: `<3`

Promotion guardrails:
- Never promote a node excluded by NOT filters even if score is high.
- Never promote a node above meta ceiling.
- Backlink density is a tie-breaker, not a standalone promotion reason.

## 7. Idempotency Rules
- Re-running bootstrap with same `analysis_run_id` must not duplicate scaffold nodes/edges.
- Re-running bootstrap with new `analysis_run_id` creates a new scaffold run, no canonical mutation.
- Re-running promotion for same run + same selected QIDs must not duplicate `:SubjectConcept` due to `MERGE` on `qid`.

## 8. Acceptance Tests
1. Generic seed support:
- Given seed `Q897` and seed `Q17167` in separate runs,
- When bootstrap runs,
- Then both produce scaffold graphs without facet inputs.

2. Instance-to-class lift:
- Given an instance-like seed,
- When bootstrap runs,
- Then one `P31` lift is recorded before `P279` upward traversal.

3. Authority-backed leaf promotion:
- Given a node with FAST/LCSH authority and true leaf status,
- When candidate marking runs,
- Then `promotion_candidate=true`.

4. Truncation safety:
- Given child expansion cap reached for a node,
- When leaf detection runs,
- Then node is not treated as a true leaf solely due to local absence of children.

5. Discipline root stopping:
- Given upward path reaches discipline root,
- When path expansion runs,
- Then expansion stops at root and marks `discipline=true` on promotion.

6. Meta-ceiling exclusion:
- Given a node in `meta_ceiling_qids`,
- When promotion selection runs,
- Then node is excluded from canonical promotion.

7. Scaffold/canonical boundary:
- Given bootstrap completes,
- When no promotion command is executed,
- Then canonical `:SubjectConcept` count is unchanged.

8. Promotion idempotency:
- Given same run and same promoted QID set executed twice,
- When promotion runs twice,
- Then canonical nodes are unchanged after first run.

9. Facet independence:
- Given empty facet payload,
- When algorithm executes end-to-end,
- Then output is identical to run with any facet metadata present but ignored.

10. Backlink allowlist enforcement:
- Given backlink statement with property not in allowlist,
- When ingest phase runs,
- Then no `BacklinkEvidence` is written for that statement.

11. Backlink candidate classification:
- Given backlink item with authority + discipline-chain + high-signal property,
- When scoring runs,
- Then item is marked `backlink_candidate_class='PROMOTE_SUBJECTCONCEPT'`.

12. Backlink noise suppression:
- Given backlink item with weak/meta wrapper indicators,
- When scoring runs,
- Then noise penalty lowers class to `KEEP_AS_ENTITY` or `EVIDENCE_ONLY`.

13. Statement-level provenance:
- Given one backlink statement from item to seed,
- When ingest runs,
- Then `BacklinkEvidence` stores `statement_id`, `property_id`, `item_qid`, `seed_qid`, and `analysis_run_id`.

## 9. Operational Notes
- Keep LLM usage optional and advisory only for ambiguous authority mapping; final promotion decision remains deterministic.
- Log `promotion_reason` and `promotion_rule_version` on each promoted scaffold candidate for auditability.
- Keep diversity caps active (`max_backlinks_per_property`, `max_backlinks_per_top_class`) so one domain does not dominate candidate intake.
- Facet hints inferred from classes can be stored as optional metadata, but must not be required for candidate scoring or promotion.
