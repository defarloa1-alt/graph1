# 2-17-26 Facet Federation Action Plan

Status: draft implementation plan derived from the facet-to-federation matrix.

## 1. Inputs
- Facet keys: `Facets/facet_registry_master.json`
- Federation matrix: `Facets/facet_federation_matrix.json`
- Bootstrap run context: `AnalysisRun.run_id`, seed QID, mapped scaffold outputs

## 2. Execution contract
For each active facet:
1) Load facet policy from `facet_federation_matrix.json`.
2) Execute all `primary` adapters first.
3) Mark coverage state:
- `facet_ready` when `min_primary_hits` is met.
- `facet_degraded` when primary misses occur.
4) Execute `secondary` adapters only after primary pass (or in parallel if adapters are independent).
5) Persist adapter results with provenance:
- `source_system`, `external_id`, `lookup_method`, `retrieved_at`, `run_id`.
6) Emit run metrics:
- `primary_hits`, `secondary_hits`, `coverage_ratio`, `errors_by_adapter`.

## 3. Minimum output schema
Each federated match must output:
- `facet_key` (lowercase registry key)
- `adapter_id`
- `entity_qid` or local subject key
- `external_id`
- `label`
- `match_type` (`exact`, `narrow`, `broad`, `related`)
- `confidence`
- `provenance_url`
- `analysis_run_id`

## 4. Routing and gating
- Promotion never depends on federation counts alone.
- Federation coverage can increase routing confidence and queue priority.
- If a facet is `facet_degraded`, keep processing with Wikidata-only coverage and log a remediation task.

## 5. v1 categorized-density trigger policy
Use categorized density for subagent proposals:
- `backlinks_by_type[type]` and `backlinks_by_facet[facet]`
- optional joint buckets such as `by_type_and_facet[EVENT][economic]`

Spawn proposal rule (v1 draft):
1) Category count passes an absolute floor.
2) Category density is above facet-local percentile threshold.
3) Cooldown and hysteresis checks pass.

Subagent scope must be category-specific (for example `economic/events` rather than generic `economic`).

## 6. Delivery checklist
1) Add matrix loader in federation dispatcher path.
2) Add adapter interface with `adapter_id`, `lookup`, `normalize`, `score`.
3) Implement primary-only pass for all facets with Wikidata (baseline).
4) Add per-facet secondary adapters incrementally.
5) Add telemetry dashboard for coverage and error rates.

## 7. Acceptance criteria
1) All 18 facet keys resolve to a policy row.
2) Missing facet keys fail fast at validation time.
3) Each run emits per-facet coverage metrics with adapter-level traceability.
4) Federation adapter failures do not mutate canonical graph directly.
5) v1 subagent proposals include categorized-density evidence payloads.

