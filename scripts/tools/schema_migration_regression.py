#!/usr/bin/env python3
"""Schema migration regression runner.

Implements ARB-SCHEMA-002 by executing a migration plan in deterministic
`dry_run` or `apply` mode and emitting a JSON pass/fail matrix report.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import time
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_VERSION = "schema_migration_regression_report_v1"
RUNNER_VERSION = "0.1.0"
DEFAULT_PLAN = REPO_ROOT / "Neo4j/schema/schema_migration_plan_v1.json"
DEFAULT_OUTPUT = REPO_ROOT / "JSON/reports/schema_migration_regression_report.json"


POLICY_EXPECTED_CONSTRAINTS = {
    "policy_version_hash_unique",
    "decision_table_id_unique",
    "decision_rule_id_unique",
    "decision_condition_id_unique",
    "decision_outcome_id_unique",
    "policy_version_has_policy_id",
    "policy_version_has_mode",
    "decision_table_has_policy_hash",
    "decision_rule_has_row_id",
    "decision_rule_has_order",
    "decision_condition_has_field",
    "decision_condition_has_operator",
    "decision_outcome_has_field",
}
POLICY_EXPECTED_INDEXES = {
    "policy_version_id_index",
    "decision_table_policy_hash_index",
    "decision_table_key_index",
    "decision_rule_lookup_index",
    "decision_condition_field_index",
    "decision_outcome_field_index",
}


def load_graph_database() -> Any:
    """Import neo4j driver without local `Neo4j/` path shadowing on Windows."""
    repo_norm = REPO_ROOT.resolve().as_posix().lower()
    old_sys_path = list(sys.path)
    try:
        filtered: List[str] = []
        for entry in old_sys_path:
            try:
                if entry and Path(entry).resolve().as_posix().lower() == repo_norm:
                    continue
            except Exception:  # noqa: BLE001
                pass
            filtered.append(entry)
        sys.path = filtered
        from neo4j import GraphDatabase as _GraphDatabase  # type: ignore

        return _GraphDatabase
    finally:
        sys.path = old_sys_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["dry_run", "apply"],
        default="dry_run",
        help="dry_run validates plan and emits report without DB writes; apply executes migration scripts.",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=DEFAULT_PLAN,
        help="Path to migration plan JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path for JSON report output.",
    )
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"))
    parser.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("NEO4J_PASSWORD", "Chrystallum"))
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when report status is FAIL.",
    )
    return parser.parse_args()


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(payload.encode("utf-8")).hexdigest()


def parse_statements(text: str) -> List[str]:
    chunks: List[str] = []
    buf: List[str] = []
    in_single = False
    in_double = False
    escape = False
    for ch in text:
        if escape:
            buf.append(ch)
            escape = False
            continue
        if ch == "\\":
            buf.append(ch)
            escape = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            continue
        if ch == ";" and not in_single and not in_double:
            chunks.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    if buf:
        chunks.append("".join(buf))
    statements: List[str] = []
    for chunk in chunks:
        lines = [ln for ln in chunk.splitlines() if ln.strip() and not ln.strip().startswith("//")]
        stmt = "\n".join(lines).strip()
        if stmt:
            statements.append(stmt)
    return statements


def load_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be object")
    return data


def normalize_rel_path(path: str) -> str:
    return str(path).replace("\\", "/")


def resolve_paths(paths: Iterable[str]) -> List[Path]:
    resolved: List[Path] = []
    for rel in paths:
        rp = REPO_ROOT / normalize_rel_path(rel)
        resolved.append(rp)
    return resolved


def extract_expected_list_from_runner(path: Path, var_name: str) -> List[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    value = ast.literal_eval(node.value)
                    if isinstance(value, list) and all(isinstance(x, str) for x in value):
                        return list(value)
    return []


def collect_schema_snapshot(session: Any, labels: List[str]) -> Dict[str, Any]:
    constraints = session.run(
        "SHOW CONSTRAINTS YIELD name RETURN name ORDER BY name"
    ).value("name")
    idx_rows = session.run(
        """
        SHOW INDEXES YIELD name, type, state, owningConstraint
        WHERE type <> 'LOOKUP' AND (owningConstraint IS NULL OR owningConstraint = '')
        RETURN name, state
        ORDER BY name
        """
    ).data()
    label_counts: Dict[str, int] = {}
    for label in labels:
        query = f"MATCH (n:{label}) RETURN count(n) AS c"
        rows = session.run(query).data()
        label_counts[label] = int(rows[0]["c"]) if rows else 0
    return {
        "constraints": sorted(constraints),
        "indexes": sorted(r["name"] for r in idx_rows),
        "non_online_indexes": sorted(r["name"] for r in idx_rows if r["state"] != "ONLINE"),
        "label_counts": label_counts,
    }


def execute_cypher_file(session: Any, path: Path) -> Tuple[bool, int, str]:
    statements = parse_statements(path.read_text(encoding="utf-8"))
    if not statements:
        return True, 0, "no_statements"
    executed = 0
    try:
        for stmt in statements:
            session.run(stmt).consume()
            executed += 1
        return True, executed, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, executed, f"{type(exc).__name__}:{exc}"


def assertion(
    assertion_id: str,
    severity: str,
    status: str,
    reason_codes: List[str],
    details: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "assertion_id": assertion_id,
        "severity": severity,
        "status": status,
        "reason_codes": sorted(set(reason_codes)),
        "details": details or {},
    }


def evaluate_plan_assertions(
    plan_path: Path,
    migration_files: List[Path],
    assertion_sources: List[Path],
) -> List[Dict[str, Any]]:
    assertions: List[Dict[str, Any]] = []
    missing_files = [p.as_posix() for p in migration_files if not p.exists()]
    assertions.append(
        assertion(
            "PLAN-001-migration-files-exist",
            "ERROR",
            "PASS" if not missing_files else "FAIL",
            [] if not missing_files else ["missing_migration_files"],
            {"missing_files": missing_files},
        )
    )

    source_missing = [p.as_posix() for p in assertion_sources if not p.exists()]
    assertions.append(
        assertion(
            "PLAN-002-assertion-sources-exist",
            "ERROR",
            "PASS" if not source_missing else "FAIL",
            [] if not source_missing else ["missing_assertion_sources"],
            {"missing_sources": source_missing},
        )
    )

    normalized = [p.as_posix() for p in migration_files]
    duplicates = sorted({x for x in normalized if normalized.count(x) > 1})
    assertions.append(
        assertion(
            "PLAN-003-ordered-unique-sequence",
            "ERROR",
            "PASS" if not duplicates else "FAIL",
            [] if not duplicates else ["duplicate_migration_entries"],
            {"duplicates": duplicates, "plan": plan_path.as_posix()},
        )
    )
    return assertions


def evaluate_apply_assertions(
    *,
    expected_constraints: List[str],
    expected_indexes: List[str],
    pre: Dict[str, Any],
    post: Dict[str, Any],
    include_policy_checks: bool,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    assertions: List[Dict[str, Any]] = []
    post_constraints = set(post["constraints"])
    post_indexes = set(post["indexes"])
    pre_constraints = set(pre["constraints"])
    pre_indexes = set(pre["indexes"])

    missing_constraints = sorted(x for x in expected_constraints if x not in post_constraints)
    missing_indexes = sorted(x for x in expected_indexes if x not in post_indexes)
    non_online_indexes = sorted(post.get("non_online_indexes", []))

    assertions.append(
        assertion(
            "SCHEMA-001-required-constraints-present",
            "ERROR",
            "PASS" if not missing_constraints else "FAIL",
            [] if not missing_constraints else ["missing_constraints_post"],
            {"missing_constraints_post": missing_constraints},
        )
    )
    assertions.append(
        assertion(
            "SCHEMA-002-required-indexes-present",
            "ERROR",
            "PASS" if not missing_indexes else "FAIL",
            [] if not missing_indexes else ["missing_indexes_post"],
            {"missing_indexes_post": missing_indexes},
        )
    )
    assertions.append(
        assertion(
            "SCHEMA-003-indexes-online",
            "ERROR",
            "PASS" if not non_online_indexes else "FAIL",
            [] if not non_online_indexes else ["non_online_indexes_post"],
            {"non_online_indexes_post": non_online_indexes},
        )
    )

    core_label_details = []
    for label, count in sorted(post.get("label_counts", {}).items()):
        core_label_details.append({"label": label, "count": int(count)})
    assertions.append(
        assertion(
            "SCHEMA-004-core-label-queryable",
            "ERROR",
            "PASS",
            [],
            {"label_counts_post": core_label_details},
        )
    )

    dropped_constraints = sorted(x for x in pre_constraints if x not in post_constraints)
    dropped_indexes = sorted(x for x in pre_indexes if x not in post_indexes)
    assertions.append(
        assertion(
            "SCHEMA-005-no-unexpected-schema-drops",
            "WARN",
            "PASS" if not dropped_constraints and not dropped_indexes else "FAIL",
            [] if not dropped_constraints and not dropped_indexes else ["unexpected_schema_drop"],
            {
                "dropped_constraints": dropped_constraints,
                "dropped_indexes": dropped_indexes,
            },
        )
    )

    policy_missing_constraints: List[str] = []
    policy_missing_indexes: List[str] = []
    if include_policy_checks:
        policy_missing_constraints = sorted(
            x for x in POLICY_EXPECTED_CONSTRAINTS if x not in post_constraints
        )
        policy_missing_indexes = sorted(x for x in POLICY_EXPECTED_INDEXES if x not in post_indexes)
        assertions.append(
            assertion(
                "SCHEMA-006-policy-subgraph-readiness",
                "ERROR",
                "PASS" if not policy_missing_constraints and not policy_missing_indexes else "FAIL",
                []
                if not policy_missing_constraints and not policy_missing_indexes
                else ["policy_subgraph_schema_incomplete"],
                {
                    "missing_policy_constraints": policy_missing_constraints,
                    "missing_policy_indexes": policy_missing_indexes,
                },
            )
        )

    diff = {
        "missing_constraints_post": missing_constraints,
        "missing_indexes_post": missing_indexes,
        "non_online_indexes_post": non_online_indexes,
        "unexpected_drops": {
            "constraints": dropped_constraints,
            "indexes": dropped_indexes,
        },
        "missing_policy_constraints": policy_missing_constraints,
        "missing_policy_indexes": policy_missing_indexes,
    }
    return assertions, diff


def summarize(assertions: List[Dict[str, Any]]) -> Dict[str, Any]:
    errors = 0
    warnings = 0
    passes = 0
    for item in assertions:
        if item["status"] == "PASS":
            passes += 1
            continue
        if item["severity"] == "ERROR":
            errors += 1
        elif item["severity"] == "WARN":
            warnings += 1
    status = "PASS" if errors == 0 else "FAIL"
    return {
        "assertions_executed": len(assertions),
        "errors": errors,
        "warnings": warnings,
        "passes": passes,
        "status": status,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    started_at = int(time.time())
    plan_path = args.plan if args.plan.is_absolute() else (REPO_ROOT / args.plan)
    plan = load_json(plan_path)
    plan_id = str(plan.get("migration_plan_id", "unknown_plan"))

    migration_files = resolve_paths(plan.get("migration_files", []))
    assertion_sources = resolve_paths(plan.get("assertion_sources", []))
    critical_labels = list(plan.get("critical_labels", []))

    file_matrix: List[Dict[str, Any]] = []
    assertions = evaluate_plan_assertions(plan_path, migration_files, assertion_sources)

    expected_constraints: List[str] = []
    expected_indexes: List[str] = []
    for source in assertion_sources:
        if source.name == "08_core_pipeline_validation_runner.py" and source.exists():
            expected_constraints = extract_expected_list_from_runner(source, "EXPECTED_CONSTRAINTS")
            expected_indexes = extract_expected_list_from_runner(source, "EXPECTED_INDEXES")

    pre_snapshot: Dict[str, Any] = {}
    post_snapshot: Dict[str, Any] = {}
    diff: Dict[str, Any] = {
        "missing_constraints_post": [],
        "missing_indexes_post": [],
        "non_online_indexes_post": [],
        "unexpected_drops": {"constraints": [], "indexes": []},
        "missing_policy_constraints": [],
        "missing_policy_indexes": [],
    }

    if args.mode == "apply" and not any(a["status"] == "FAIL" for a in assertions):
        GraphDatabase = load_graph_database()
        driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
        try:
            with driver.session() as session:
                pre_snapshot = collect_schema_snapshot(session, critical_labels)
                for path in migration_files:
                    ok, count, detail = execute_cypher_file(session, path)
                    file_matrix.append(
                        {
                            "path": path.as_posix(),
                            "status": "PASS" if ok else "FAIL",
                            "statements_executed": count,
                            "detail": detail,
                        }
                    )
                    if not ok:
                        assertions.append(
                            assertion(
                                "MIGRATION-001-file-execution",
                                "ERROR",
                                "FAIL",
                                ["migration_file_execution_failed"],
                                {"path": path.as_posix(), "detail": detail},
                            )
                        )
                        break
                post_snapshot = collect_schema_snapshot(session, critical_labels)
            include_policy = any(p.name == "17_policy_decision_subgraph_schema.cypher" for p in migration_files)
            apply_assertions, diff = evaluate_apply_assertions(
                expected_constraints=expected_constraints,
                expected_indexes=expected_indexes,
                pre=pre_snapshot,
                post=post_snapshot,
                include_policy_checks=include_policy,
            )
            assertions.extend(apply_assertions)
        except Exception as exc:  # noqa: BLE001
            assertions.append(
                assertion(
                    "MIGRATION-000-connectivity-or-runtime",
                    "ERROR",
                    "FAIL",
                    ["neo4j_runtime_error"],
                    {"detail": f"{type(exc).__name__}:{exc}"},
                )
            )
        finally:
            driver.close()
    else:
        for path in migration_files:
            file_matrix.append(
                {
                    "path": path.as_posix(),
                    "status": "PASS" if path.exists() else "FAIL",
                    "statements_executed": 0,
                    "detail": "dry_run_planned",
                }
            )

    summary = summarize(assertions)
    completed_at = int(time.time())
    fingerprint_basis = {
        "contract_version": CONTRACT_VERSION,
        "runner_version": RUNNER_VERSION,
        "plan_id": plan_id,
        "mode": args.mode,
        "migration_files": [p.as_posix() for p in migration_files],
        "assertion_ids": sorted(a["assertion_id"] for a in assertions),
    }
    report = {
        "metadata_header": {
            "contract_version": CONTRACT_VERSION,
            "runner_version": RUNNER_VERSION,
            "migration_plan_id": plan_id,
            "run_fingerprint": stable_hash(fingerprint_basis),
            "determinism_mode": "strict_plan_hash",
        },
        "execution": {
            "mode": args.mode,
            "started_at": started_at,
            "completed_at": completed_at,
            "duration_seconds": max(0, completed_at - started_at),
            "files_executed": file_matrix,
        },
        "summary": summary,
        "assertions": sorted(assertions, key=lambda row: row["assertion_id"]),
        "diff": diff,
        "snapshots": {
            "pre": pre_snapshot,
            "post": post_snapshot,
        },
    }
    output = args.output if args.output.is_absolute() else (REPO_ROOT / args.output)
    write_json(output, report)

    print(f"artifact={output.as_posix()}")
    print(f"run_fingerprint={report['metadata_header']['run_fingerprint']}")
    print(
        "summary="
        f"assertions_executed:{summary['assertions_executed']},"
        f"errors:{summary['errors']},warnings:{summary['warnings']},"
        f"passes:{summary['passes']},status:{summary['status']}"
    )
    if args.strict and summary["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
