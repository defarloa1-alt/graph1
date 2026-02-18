# Presentation Orchestration PLAO ESB v1

Status: draft v1 architecture spec

## 1. Purpose
Define a bounded orchestration layer for presentation requests:
1) classify user intent,
2) choose a presentation strategy,
3) route strategy tasks to adapters,
4) compose a single response envelope.

This document formalizes the PLAO and Agent ESB pattern as an implementation contract.

## 2. Scope
In scope:
1) request and response contracts,
2) routing and fallback rules,
3) adapter interface and lifecycle,
4) observability and failure handling.

Out of scope:
1) visual design language details,
2) domain ontology and claim semantics,
3) canonical graph mutation rules.

## 3. Architecture
Pipeline:
1) `IntentClassifier` -> derive normalized intent and confidence.
2) `StrategySelector` -> create execution plan from intent + context + policy.
3) `AdapterRegistry`/ESB -> execute plan tasks with adapter-specific routing.
4) `ResponseComposer` -> produce final presentation payload + trace.

## 4. Contracts
### 4.1 Presentation Request
Required fields:
1) `request_id`
2) `subject_key` (QID or local subject id)
3) `query_text`
4) `user_role`
5) `viewport` (`desktop|tablet|mobile|api`)
6) `analysis_run_id` (if available)

Optional fields:
1) `preferred_mode` (`graph|timeline|table|narrative|mixed`)
2) `constraints` (`latency_ms`, `max_adapters`, `budget_tokens`)
3) `session_context` (opaque map)

### 4.2 Strategy Plan
Required fields:
1) `plan_id`
2) `intent_key`
3) `confidence`
4) `tasks[]`

Task shape:
1) `task_id`
2) `adapter_id`
3) `input_payload`
4) `timeout_ms`
5) `critical` (bool)
6) `fallback_adapter_ids[]`

### 4.3 Adapter Response
Required fields:
1) `task_id`
2) `adapter_id`
3) `status` (`ok|degraded|error|timeout`)
4) `payload`
5) `latency_ms`
6) `error_code` (nullable)
7) `error_message` (nullable)

### 4.4 Final Envelope
Required fields:
1) `request_id`
2) `presentation_mode`
3) `content_blocks[]`
4) `trace` (`intent_key`, `plan_id`, `tasks_executed`, `degraded`)
5) `warnings[]`

## 5. Adapter Interface
All adapters must implement:
1) `adapter_id() -> str`
2) `capabilities() -> list[str]`
3) `health() -> AdapterHealth`
4) `execute(input_payload, timeout_ms) -> AdapterResponse`
5) `normalize(raw_payload) -> normalized_payload`

Adapter rules:
1) no direct canonical graph writes from adapter execution,
2) enforce per-adapter timeout and bounded retries,
3) produce deterministic `status` and `error_code`.

## 6. Routing and Fallback
Routing rules:
1) execute critical tasks first,
2) run independent non-critical tasks in parallel,
3) fail fast only if a critical task has no successful fallback.

Fallback rules:
1) if an adapter times out, try `fallback_adapter_ids` in order,
2) if all fail, mark task `degraded` unless task is `critical`,
3) degrade to a supported default mode (`table` or `narrative`) before returning hard error.

## 7. Reliability Controls
Required controls:
1) timeout budgets per task and per request,
2) circuit breaker per adapter (`open`, `half_open`, `closed`),
3) bounded retry policy (`max_retries <= 2`),
4) response cache for idempotent adapter calls.

## 8. Governance and Security
1) PLAO/ESB is read-oriented by default.
2) If a task requires mutation, it must emit a proposal event and use existing promotion/governance flows.
3) Log `request_id`, `plan_id`, `adapter_id`, and user role for auditability.
4) Redact secrets and personal data from adapter payload logs.

## 9. Observability
Required metrics:
1) `plao_requests_total`
2) `plao_latency_ms_p50_p95_p99`
3) `esb_task_success_rate`
4) `esb_task_timeout_rate`
5) `adapter_circuit_open_count`
6) `response_degraded_rate`

Required traces:
1) request-level trace spanning classification -> plan -> task execution -> composition.

## 10. Acceptance Criteria
1) Every request produces a typed final envelope.
2) Critical task failure behavior is deterministic and test-covered.
3) Adapter failures do not mutate canonical graph.
4) Degraded responses are explicit in output trace and warnings.
5) p95 request latency and degraded-rate are measurable via exported metrics.

## 11. Implementation Checklist
1) Implement `IntentClassifier`, `StrategySelector`, `AdapterRegistry`, `ResponseComposer`.
2) Define schema validators for request/plan/task/response/final envelope.
3) Add circuit-breaker + retry + timeout middleware in ESB execution path.
4) Add conformance tests for adapter contract and fallback behavior.
5) Add runbook entries for degraded mode and adapter outage response.

