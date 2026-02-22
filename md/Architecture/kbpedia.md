# KBpedia x IGAR x CRMinf Integration Note

Status: draft
Date: 2026-02-18
Purpose: define how KBpedia/KKO should be used in Chrystallum without creating a parallel ontology stack.
Canonical architecture anchor: `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`

## Pinned TODO
1. [x] Write `ADR-003-KBpedia-Role-and-Boundaries.md`.
2. [x] Build a canonical crosswalk table: `KKO class -> Chrystallum label -> CIDOC class -> CRMinf usage` (initial seed in `CSV/kko_chrystallum_crosswalk.csv`).
3. [x] Add a mapping confidence rubric (`exact`, `narrow`, `broad`, `related`) with reviewer gates (`md/Architecture/KBPEDIA_MAPPING_CONFIDENCE_RUBRIC.md`).
4. [x] Implement a non-mutating KKO loader that writes only scaffold/proposal artifacts (`scripts/tools/kko_mapping_proposal_loader.py`).
5. [ ] Add validation tests for event/action/situation disambiguation on 3-5 historical case studies.
6. [ ] Add query templates to inspect KKO-based typing decisions and confidence breakdowns.
7. [ ] Define promotion policy from KKO-scaffold typing to canonical labels.
8. [ ] Decide `Situation` modeling path: scaffold-only in v0/v1 vs canonical `Situation` node type in a later schema ADR.
9. [ ] Aggregate KKO crosswalk into a federation master crosswalk only after rows pass reviewer gates (no draft/blocked rows).

## Executive Position
KBpedia should be used as a semantic typing overlay and alignment source, not as canonical truth.

In Chrystallum terms:
1. KBpedia/KKO refines classification of event/action/situation/time.
2. CIDOC remains the formal interoperability backbone.
3. CRMinf remains the reasoning and belief/provenance layer.
4. Canonical mutation still follows `U -> Pi -> Commit` governance boundaries.

## Conceptual Fit
Core alignment:
1. `KKO Event` aligns to `Event` / `CIDOC E5`.
2. `KKO Activity/Action` aligns to `Activity` / `CIDOC E7`.
3. `KKO Situation/Context` aligns to world-state/context entities used by IGAR input/result.
4. `KKO Time` aligns to temporal entities (`Year`, `Period`, temporal extents).

IGAR interpretation:
1. Inputs: situations + time context.
2. Goals: actor intent.
3. Actions: activity/process nodes.
4. Results: event outcomes and derived situations.

CRMinf interpretation:
1. Beliefs attach to propositions about events/actions/situations.
2. Inference nodes track how evidence supports a classification or claim.
3. Belief revision records retyping when new evidence changes confidence.

## Technical Boundaries
Do:
1. Treat KKO classes and mappings as URI-based structured signals.
2. Store KKO mappings as provenance-bearing typing proposals.
3. Use KKO for disambiguation and routing confidence, not automatic canonical writes.

Do not:
1. Do not mint canonical entity identity from labels.
2. Do not import KKO text annotations as federation keys.
3. Do not bypass policy gate because a mapping exists.

## Data Model Guidance
Use an explicit mapping artifact, for example:
1. `source_system`: `kbpedia`
2. `source_uri`: KKO class URI
3. `target_label`: Chrystallum node label
4. `cidoc_class`: optional CIDOC class
5. `crminf_pattern`: optional inference pattern hint
6. `match_type`: `exact|narrow|broad|related`
7. `mapping_confidence`: `0.0..1.0`
8. `evidence`: URI list
9. `analysis_run_id`
10. `review_status`

Keep this in scaffold/proposal space until approved for promotion.

## Pipeline Recommendation
1. Ingest KBpedia/KKO graph to a staging representation.
2. Normalize mappings into a crosswalk table.
3. Run type disambiguation for candidate nodes.
4. Emit proposal artifacts with confidence and evidence.
5. Gate through policy checks (`Pi`).
6. Promote approved mappings to canonical typing relationships.

## Governance and QA
Required gates:
1. No canonical write from KKO mapping without reviewable proposal.
2. Every promoted typing decision must include source URI and run context.
3. Every rejection stores reason code.

QA scenarios (minimum):
1. Ambiguous node that can be event or situation.
2. Activity vs event confusion in military/political domains.
3. Time entity alignment between period labels and point dates.
4. Conflicting mappings (`exact` vs `broad`) from different sources.

## Near-Term Deliverables
1. ADR: KBpedia role/boundary decision.
2. `CSV/kko_chrystallum_crosswalk.csv` initial seed.
3. Loader prototype under `scripts/tools/` (proposal-only mode).
4. Validation report for first historical test pack.

## Related Architecture References
1. `Key Files/2-12-26 Chrystallum Architecture - CONSOLIDATED.md`
1. `md/Architecture/ADR-002-Policy-Gate-and-Update-Operator-Separation.md`
2. `md/Architecture/CRMinf_Implementation_Guide.md`
3. `md/Architecture/CIDOC-CRM_Wikidata_Alignment_Strategy.md`
4. `md/Architecture/2-17-26-CHRYSTALLUM_v0_AGENT_BOOTSTRAP_SPEC.md`
