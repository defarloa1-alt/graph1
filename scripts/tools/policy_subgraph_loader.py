#!/usr/bin/env python3
"""Project ordered decision-table policy JSON into Neo4j policy subgraph.

This loader is append-safe and hash-pinned:
1. `PolicyVersion` is keyed by canonical SHA-256 of policy payload.
2. Decision table artifacts are keyed by policy hash + table/rule identity.
3. Existing policy versions are not mutated.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from neo4j import GraphDatabase

from scripts.tools.claim_confidence_policy_engine import canonical_policy_hash


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_condition(expected: Any) -> Tuple[str, str]:
    if expected == "any":
        return "ANY", "any"
    if isinstance(expected, bool):
        return "EQ", str(expected).lower()
    if isinstance(expected, (int, float)):
        return "EQ", str(expected)
    if isinstance(expected, str):
        m = re.match(r"^\s*(>=|<=|>|<|=)\s*(.+)\s*$", expected)
        if m:
            op = m.group(1)
            rhs = m.group(2).strip()
            return op, rhs
        return "EQ", expected
    return "EQ", str(expected)


def normalize_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return "null"
    return str(value)


def load_policy(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["_policy_hash"] = canonical_policy_hash(payload)
    return payload


def table_rows(policy: Dict[str, Any]) -> Iterable[Tuple[str, List[Dict[str, Any]]]]:
    tables = policy.get("tables", {})
    if not isinstance(tables, dict):
        return []
    return tables.items()


def build_ids(policy_id: str, policy_hash: str, table_key: str, row_id: str) -> Tuple[str, str]:
    table_id = f"{policy_id}:{policy_hash[:12]}:{table_key}"
    rule_id = f"{table_id}:{row_id}"
    return table_id, rule_id


def upsert_policy_version(tx: Any, policy: Dict[str, Any], source_path: str) -> None:
    tx.run(
        """
        MERGE (pv:PolicyVersion {policy_hash: $policy_hash})
        ON CREATE SET
          pv.policy_id = $policy_id,
          pv.status = $status,
          pv.date = $date,
          pv.evaluation_mode = $evaluation_mode,
          pv.source_path = $source_path,
          pv.created_at = $created_at
        """,
        {
            "policy_hash": policy["_policy_hash"],
            "policy_id": policy.get("policy_id", "unknown_policy"),
            "status": policy.get("status", "unknown"),
            "date": policy.get("date", ""),
            "evaluation_mode": policy.get("evaluation_mode", ""),
            "source_path": source_path,
            "created_at": utc_now_iso(),
        },
    )


def upsert_table(tx: Any, policy: Dict[str, Any], table_key: str) -> str:
    policy_id = policy.get("policy_id", "unknown_policy")
    table_id, _ = build_ids(policy_id, policy["_policy_hash"], table_key, "__unused__")
    tx.run(
        """
        MATCH (pv:PolicyVersion {policy_hash: $policy_hash})
        MERGE (dt:DecisionTable {table_id: $table_id})
        ON CREATE SET
          dt.policy_id = $policy_id,
          dt.policy_hash = $policy_hash,
          dt.table_key = $table_key,
          dt.name = $table_key,
          dt.created_at = $created_at
        MERGE (pv)-[:HAS_TABLE]->(dt)
        """,
        {
            "policy_hash": policy["_policy_hash"],
            "policy_id": policy_id,
            "table_id": table_id,
            "table_key": table_key,
            "created_at": utc_now_iso(),
        },
    )
    return table_id


def upsert_rule(tx: Any, policy: Dict[str, Any], table_key: str, row: Dict[str, Any], order: int) -> str:
    policy_id = policy.get("policy_id", "unknown_policy")
    row_id = row.get("row_id", f"ROW_{order}")
    table_id, rule_id = build_ids(policy_id, policy["_policy_hash"], table_key, row_id)
    tx.run(
        """
        MATCH (dt:DecisionTable {table_id: $table_id})
        MERGE (dr:DecisionRule {rule_id: $rule_id})
        ON CREATE SET
          dr.policy_id = $policy_id,
          dr.policy_hash = $policy_hash,
          dr.table_key = $table_key,
          dr.row_id = $row_id,
          dr.rule_order = $rule_order,
          dr.is_default = $is_default,
          dr.created_at = $created_at
        MERGE (dt)-[:HAS_RULE]->(dr)
        """,
        {
            "table_id": table_id,
            "rule_id": rule_id,
            "policy_id": policy_id,
            "policy_hash": policy["_policy_hash"],
            "table_key": table_key,
            "row_id": row_id,
            "rule_order": order,
            "is_default": bool(row.get("default", False)),
            "created_at": utc_now_iso(),
        },
    )
    return rule_id


def upsert_conditions(tx: Any, rule_id: str, row: Dict[str, Any]) -> int:
    count = 0
    for field, expected in (row.get("conditions") or {}).items():
        op, value = parse_condition(expected)
        cond_id = f"{rule_id}:cond:{field}:{op}:{normalize_scalar(value)}"
        tx.run(
            """
            MATCH (dr:DecisionRule {rule_id: $rule_id})
            MERGE (dc:DecisionCondition {condition_id: $condition_id})
            ON CREATE SET
              dc.rule_id = $rule_id,
              dc.field = $field,
              dc.operator = $operator,
              dc.value = $value,
              dc.created_at = $created_at
            MERGE (dr)-[:HAS_CONDITION]->(dc)
            """,
            {
                "rule_id": rule_id,
                "condition_id": cond_id,
                "field": field,
                "operator": op,
                "value": normalize_scalar(value),
                "created_at": utc_now_iso(),
            },
        )
        count += 1
    return count


def upsert_outcomes(tx: Any, rule_id: str, row: Dict[str, Any]) -> int:
    count = 0
    for field, value in (row.get("output") or {}).items():
        out_id = f"{rule_id}:out:{field}:{normalize_scalar(value)}"
        tx.run(
            """
            MATCH (dr:DecisionRule {rule_id: $rule_id})
            MERGE (do:DecisionOutcome {outcome_id: $outcome_id})
            ON CREATE SET
              do.rule_id = $rule_id,
              do.field = $field,
              do.value = $value,
              do.created_at = $created_at
            MERGE (dr)-[:HAS_OUTCOME]->(do)
            """,
            {
                "rule_id": rule_id,
                "outcome_id": out_id,
                "field": field,
                "value": normalize_scalar(value),
                "created_at": utc_now_iso(),
            },
        )
        count += 1
    return count


def project_policy(uri: str, user: str, password: str, policy_path: Path) -> Dict[str, Any]:
    policy = load_policy(policy_path)
    source_path = str(policy_path.as_posix())
    counters = {"tables": 0, "rules": 0, "conditions": 0, "outcomes": 0}

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            write_fn = getattr(session, "execute_write", None) or getattr(session, "write_transaction")
            write_fn(upsert_policy_version, policy, source_path)
            for table_key, rows in table_rows(policy):
                write_fn(upsert_table, policy, table_key)
                counters["tables"] += 1
                for order, row in enumerate(rows, start=1):
                    rule_id = write_fn(upsert_rule, policy, table_key, row, order)
                    counters["rules"] += 1
                    counters["conditions"] += write_fn(upsert_conditions, rule_id, row)
                    counters["outcomes"] += write_fn(upsert_outcomes, rule_id, row)
    finally:
        driver.close()

    return {
        "policy_id": policy.get("policy_id", "unknown_policy"),
        "policy_hash": policy["_policy_hash"],
        "source_path": source_path,
        "counters": counters,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Load decision-table policy into Neo4j policy subgraph")
    parser.add_argument("--policy-path", default="JSON/policy/claim_confidence_policy_v1.json")
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"))
    parser.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("NEO4J_PASSWORD", "Chrystallum"))
    args = parser.parse_args()

    result = project_policy(
        uri=args.uri,
        user=args.user,
        password=args.password,
        policy_path=Path(args.policy_path),
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
