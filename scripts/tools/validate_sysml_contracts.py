#!/usr/bin/env python3
"""
Validate SysML JSON contract artifacts under sysml/.

Checks:
1) JSON parse validity
2) Duplicate artifact names (e.g., filename copies like " (1)")
3) Duplicate content hashes
4) Duplicate or missing schema $id values
5) Strict object schemas (additionalProperties must be false)
6) Optional Draft-07 schema meta-validation if jsonschema package is available
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
SYSML_DIR = ROOT / "sysml"


@dataclass
class Issue:
    level: str  # ERROR | WARN | INFO
    file: str
    message: str


def _is_object_schema(node: Dict[str, Any]) -> bool:
    t = node.get("type")
    if t == "object":
        return True
    if isinstance(t, list) and "object" in t:
        return True
    return False


def _walk_for_non_strict_objects(node: Any, path: str = "$") -> List[str]:
    paths: List[str] = []
    if isinstance(node, dict):
        if _is_object_schema(node):
            if node.get("additionalProperties", None) is not False:
                paths.append(path)
        for key, value in node.items():
            child_path = f"{path}.{key}" if path != "$" else f"$.{key}"
            paths.extend(_walk_for_non_strict_objects(value, child_path))
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            paths.extend(_walk_for_non_strict_objects(value, f"{path}[{idx}]"))
    return paths


def _maybe_validate_with_jsonschema(
    docs: List[Tuple[Path, Dict[str, Any]]], issues: List[Issue]
) -> None:
    try:
        from jsonschema import Draft7Validator
        from jsonschema.exceptions import SchemaError
    except Exception:
        issues.append(
            Issue(
                "INFO",
                "-",
                "jsonschema package not installed; skipping Draft-07 meta-schema checks.",
            )
        )
        return

    for path, doc in docs:
        try:
            Draft7Validator.check_schema(doc)
        except SchemaError as exc:
            issues.append(Issue("ERROR", str(path), f"Draft-07 schema error: {exc.message}"))


def validate() -> int:
    issues: List[Issue] = []
    if not SYSML_DIR.exists():
        issues.append(Issue("ERROR", str(SYSML_DIR), "sysml directory not found"))
        _print_issues(issues)
        return 1

    schema_files = sorted(SYSML_DIR.glob("*.json"))
    if not schema_files:
        issues.append(Issue("ERROR", str(SYSML_DIR), "No JSON schema files found"))
        _print_issues(issues)
        return 1

    parsed_docs: List[Tuple[Path, Dict[str, Any]]] = []
    logical_name_seen: Dict[str, Path] = {}
    content_hash_seen: Dict[str, Path] = {}
    schema_id_seen: Dict[str, Path] = {}

    duplicate_copy_pattern = re.compile(r" \(\d+\)\.json$", re.IGNORECASE)

    for path in schema_files:
        if duplicate_copy_pattern.search(path.name):
            issues.append(
                Issue(
                    "ERROR",
                    str(path),
                    "Duplicate copy-style filename detected; remove/rename artifact.",
                )
            )

        logical_name = re.sub(r" \(\d+\)(?=\.json$)", "", path.name, flags=re.IGNORECASE)
        if logical_name in logical_name_seen:
            issues.append(
                Issue(
                    "ERROR",
                    str(path),
                    f"Duplicate logical filename '{logical_name}' also seen in {logical_name_seen[logical_name]}",
                )
            )
        else:
            logical_name_seen[logical_name] = path

        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest in content_hash_seen:
            issues.append(
                Issue(
                    "WARN",
                    str(path),
                    f"Content identical to {content_hash_seen[digest]} (possible redundant artifact).",
                )
            )
        else:
            content_hash_seen[digest] = path

        try:
            doc = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            issues.append(Issue("ERROR", str(path), f"Invalid JSON: {exc}"))
            continue

        if not isinstance(doc, dict):
            issues.append(Issue("ERROR", str(path), "Top-level JSON value must be an object"))
            continue

        if doc.get("type") != "object":
            issues.append(Issue("ERROR", str(path), "Top-level schema type must be 'object'"))

        schema_id = doc.get("$id")
        if not schema_id or not isinstance(schema_id, str):
            issues.append(Issue("ERROR", str(path), "Missing or invalid '$id'"))
        else:
            if schema_id in schema_id_seen:
                issues.append(
                    Issue(
                        "ERROR",
                        str(path),
                        f"Duplicate $id '{schema_id}' also seen in {schema_id_seen[schema_id]}",
                    )
                )
            else:
                schema_id_seen[schema_id] = path

        non_strict_paths = _walk_for_non_strict_objects(doc)
        for ns_path in non_strict_paths:
            issues.append(
                Issue(
                    "ERROR",
                    str(path),
                    f"Object schema at path {ns_path} must set additionalProperties to false",
                )
            )

        parsed_docs.append((path, doc))

    _maybe_validate_with_jsonschema(parsed_docs, issues)

    _print_issues(issues)
    has_error = any(i.level == "ERROR" for i in issues)
    return 1 if has_error else 0


def _print_issues(issues: List[Issue]) -> None:
    if not issues:
        print("PASS: SysML contract validation found no issues.")
        return

    counts = {"ERROR": 0, "WARN": 0, "INFO": 0}
    for issue in issues:
        counts[issue.level] = counts.get(issue.level, 0) + 1
        print(f"{issue.level}: {issue.file}: {issue.message}")

    print(
        f"\nSummary: errors={counts.get('ERROR', 0)}, warnings={counts.get('WARN', 0)}, infos={counts.get('INFO', 0)}"
    )


if __name__ == "__main__":
    sys.exit(validate())
