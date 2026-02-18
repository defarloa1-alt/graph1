# Scenario Generation QA Gates v1

Status: draft v1 QA specification

## 1. Purpose
Define deterministic QA gates for scenario generation runs using:
1) completeness threshold,
2) minimality threshold,
3) constraint satisfaction checks,
4) reproducible run reporting.

## 2. Scope
In scope:
1) run-time QA metrics and thresholds,
2) pass/fail gate logic by test class,
3) report schema for CI and manual review.

Out of scope:
1) domain-specific scenario semantics,
2) adapter or UI orchestration logic,
3) canonical graph promotion policy.

## 3. Definitions
1) `constraint_satisfaction_rate`: fraction of scenarios satisfying all hard constraints.
2) `coverage_rate`: fraction of required constraint space covered by generated scenarios.
3) `minimality_score`: degree of independence between selected scenarios (higher is more independent).
4) `generation_latency_ms`: end-to-end scenario generation duration.

## 4. Test Classes and Thresholds
### 4.1 Smoke
1) `constraint_satisfaction_rate >= 0.95`
2) `coverage_rate >= 0.40`
3) `minimality_score >= 0.10`
4) `generation_latency_ms <= 5000`

### 4.2 Standard
1) `constraint_satisfaction_rate >= 0.99`
2) `coverage_rate >= 0.60`
3) `minimality_score >= 0.15`
4) `generation_latency_ms <= 15000`

### 4.3 Critical
1) `constraint_satisfaction_rate = 1.00`
2) `coverage_rate >= 0.70`
3) `minimality_score >= 0.20`
4) `generation_latency_ms <= 30000`

## 5. Gate Logic
A run is `pass` only if all class thresholds are met.

Gate output:
1) `pass`
2) `soft_fail` (only latency failed, correctness metrics passed)
3) `fail` (any correctness metric failed)

## 6. Deterministic Run Requirements
1) persist random seed in report (`seed`),
2) persist generator version and config hash (`generator_version`, `config_hash`),
3) persist constraint set id (`constraint_set_id`),
4) persist exact thresholds evaluated (`thresholds`).

## 7. Report Schema
Required report fields:
1) `run_id`
2) `timestamp_utc`
3) `test_class`
4) `seed`
5) `generator_version`
6) `config_hash`
7) `constraint_set_id`
8) `scenarios_generated`
9) `constraint_satisfaction_rate`
10) `coverage_rate`
11) `minimality_score`
12) `generation_latency_ms`
13) `gate_status`
14) `gate_reasons[]`

## 8. Validation Query Template
For each run, emit a deterministic metrics snapshot and evaluate against thresholds:

```json
{
  "run_id": "scenario_run_2026_02_18_001",
  "test_class": "standard",
  "seed": 42,
  "metrics": {
    "constraint_satisfaction_rate": 1.0,
    "coverage_rate": 0.64,
    "minimality_score": 0.18,
    "generation_latency_ms": 9100
  },
  "thresholds": {
    "constraint_satisfaction_rate": 0.99,
    "coverage_rate": 0.60,
    "minimality_score": 0.15,
    "generation_latency_ms": 15000
  },
  "gate_status": "pass"
}
```

## 9. CI Integration
1) run `smoke` on every PR touching generation logic,
2) run `standard` on merge to main,
3) run `critical` on release candidates.

Required CI behavior:
1) `fail` blocks merge/release,
2) `soft_fail` allowed on PR but must open remediation ticket,
3) all reports stored as artifacts and linked to commit SHA.

## 10. Acceptance Criteria
1) same seed + config hash reproduces same gate decision,
2) each run outputs full report schema,
3) gate decision is machine-evaluable without manual interpretation,
4) CI policy enforces class-specific thresholds consistently.

## 11. Implementation Checklist
1) add metrics collector in generator runtime,
2) add report serializer and schema validation,
3) add threshold evaluator by class,
4) wire gate status to CI checks,
5) add remediation template for `soft_fail` and `fail`.

