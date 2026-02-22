# Bidirectional Federation Query Design (2026-02-18)

Status: `ARB-FED-001` design baseline.

## Objective
Define a bidirectional federation query pattern for priority authorities with explicit query path, caching policy, timeout controls, and fallback behavior.

## Priority Authorities (v1)
1. `Wikidata` (required baseline)
2. `Pleiades` (active geographic authority)
3. `VIAF` (person authority control)
4. `EDH` (epigraphic authority)
5. `Trismegistos` (ancient text/person/place authority)
6. `GeoNames` (supplemental geography)

## Query Directions
1. Forward federation (`internal -> authority`)
- Input: canonical node IDs + known authority keys (`qid`, `pleiades_id`, `viaf_id`, etc.).
- Action: fetch authoritative record/enrichment payload.
- Output: normalized federation proposal payloads (no direct canonical writes).

2. Reverse federation (`authority -> internal candidate`)
- Input: authority identifiers or backlink-style authority references.
- Action: resolve likely internal candidates and emit scored alignment proposals.
- Output: candidate links and reasons (`same_as_candidate`, `aligned_with_candidate`, `conflict_candidate`).

## Query Path (v1)
1. Resolve adapter contract from `facet_federation_matrix.json` and authority routing policy.
2. Build adapter request payload with:
- `lookup_key`
- `authority`
- `query_direction` (`forward` or `reverse`)
- `analysis_run_id`
3. Execute adapter with bounded timeout and retry policy.
4. Normalize response into federation proposal schema:
- `source_system`
- `external_id`
- `lookup_method`
- `retrieved_at`
- `analysis_run_id`
- `confidence`
- `match_type`
5. Route through policy gate for proposal persistence.
6. Emit telemetry and coverage metrics.

## Caching Policy (v1)
Cache key:
- `authority + query_direction + lookup_key + adapter_version`

Cache tiers:
1. In-process short cache (optional)
2. File artifact cache in repo outputs (authoritative for replay)

TTL policy:
- `Wikidata`: 24h
- `Pleiades`: 7d
- `VIAF`: 7d
- `EDH`: 7d
- `Trismegistos`: 7d
- `GeoNames`: 3d

Negative caching:
- Cache `not_found` for 12h to avoid repeated misses.

Stale handling:
- Serve stale cache when authority is degraded and mark result `cache_stale=true`.
- Queue async refresh in next scheduled federation run.

## Timeout, Retry, and Fallback
Timeouts (per request):
- `Wikidata`: 8s
- `Pleiades`: 8s
- `VIAF`: 10s
- `EDH`: 12s
- `Trismegistos`: 12s
- `GeoNames`: 8s

Retry policy:
- `max_retries=1`
- exponential backoff with jitter
- retry only on transient transport/status errors

Fallback order (v1 examples):
1. Person resolution: `VIAF -> Wikidata`
2. Ancient place resolution: `Pleiades -> Wikidata -> GeoNames`
3. Epigraphic/text authority: `EDH/Trismegistos -> Wikidata`

Degraded mode:
- If all configured authorities fail, continue with available cached data and record `adapter_degraded`.
- Do not block entire run unless policy marks authority as critical for that facet.

## Proposal and Governance Boundaries
- Federation adapters do not write canonical graph facts directly.
- All mutation candidates flow through `U -> Pi -> Commit`.
- Confidence from federation improves routing/review priority but is not an autonomous promotion trigger.

## Metrics and Observability
Per-run minimum metrics:
- `requests_total`
- `cache_hit_ratio`
- `timeout_count`
- `fallback_count`
- `degraded_adapter_count`
- `forward_hits`
- `reverse_hits`
- `normalized_proposals_emitted`

## Implementation Handoff
Planned implementation artifacts:
- `scripts/tools/federation_query_dispatcher.py` (planned)
- `scripts/tools/federation_cache_manager.py` (planned)
- optional adapter-specific clients under `scripts/tools/`

## Acceptance Criteria Mapping (`ARB-FED-001`)
- Query path defined: yes.
- Caching policy defined: yes.
- Timeout and fallback behavior defined: yes.
- Governance-safe (proposal-only writes): yes.
