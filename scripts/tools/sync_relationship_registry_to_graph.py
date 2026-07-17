#!/usr/bin/env python3
"""
Sync relationship_types_registry_master.csv → Neo4j SYS_RelationshipType nodes.

Closes the gap where CSV has ~480 implemented types but graph SYS_RelationshipType
only mirrors ~378 keys (often without lifecycle_status / wikidata_property).

Usage:
  python -m scripts.tools.sync_relationship_registry_to_graph --dry
  python -m scripts.tools.sync_relationship_registry_to_graph --write
  python -m scripts.tools.sync_relationship_registry_to_graph --write --implemented-only
  python -m scripts.tools.sync_relationship_registry_to_graph --write --wire-schema

Idempotent (MERGE on rel_type). Safe to re-run after CSV edits.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402

from scripts.tools.sys_registry import DEFAULT_REGISTRY_CSV, normalize_relationship_type  # noqa: E402

MERGE_CYPHER = """
MERGE (rt:SYS_RelationshipType {rel_type: $rel_type})
SET rt.name = $rel_type,
    rt.category = $category,
    rt.description = $description,
    rt.wikidata_property = $wikidata_property,
    rt.directionality = $directionality,
    rt.lifecycle_status = $lifecycle_status,
    rt.status = $status,
    rt.parent_relationship = $parent_relationship,
    rt.cidoc_crm_code = $cidoc_crm_code,
    rt.cidoc_crm_kind = $cidoc_crm_kind,
    rt.reify_as = $reify_as,
    rt.lcsh_heading = $lcsh_heading,
    rt.lcc_code = $lcc_code,
    rt.mapping_source = $mapping_source,
    rt.registry_version = $registry_version,
    rt.registry_source = $registry_source,
    rt.synced_at = datetime($synced_at)
RETURN rt.rel_type AS rel_type
"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_csv_rows(*, implemented_only: bool) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    with open(DEFAULT_REGISTRY_CSV, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rel = normalize_relationship_type(row.get("relationship_type") or "")
            if not rel or rel in seen:
                continue
            lifecycle = (row.get("lifecycle_status") or "candidate").strip().lower()
            if implemented_only and lifecycle != "implemented":
                continue
            seen.add(rel)
            rows.append(row)
    return rows


def _row_props(row: dict[str, str], *, synced_at: str) -> dict[str, Any]:
    rel = normalize_relationship_type(row.get("relationship_type") or "")
    pid = (row.get("wikidata_property") or "").strip().upper() or None
    return {
        "rel_type": rel,
        "category": (row.get("category") or "").strip() or None,
        "description": ((row.get("description") or "").strip()[:2000]) or None,
        "wikidata_property": pid,
        "directionality": (row.get("directionality") or "").strip() or None,
        "lifecycle_status": (row.get("lifecycle_status") or "").strip().lower() or None,
        "status": (row.get("status") or "").strip() or None,
        "parent_relationship": (row.get("parent_relationship") or "").strip() or None,
        "cidoc_crm_code": (row.get("cidoc_crm_code") or "").strip() or None,
        "cidoc_crm_kind": (row.get("cidoc_crm_kind") or "").strip() or None,
        "reify_as": (row.get("reify_as") or "").strip() or None,
        "lcsh_heading": (row.get("lcsh_heading") or "").strip() or None,
        "lcc_code": (row.get("lcc_code") or "").strip() or None,
        "mapping_source": (row.get("mapping_source") or "").strip() or None,
        "registry_version": (row.get("version") or "1.0").strip(),
        "registry_source": str(DEFAULT_REGISTRY_CSV.relative_to(ROOT)).replace("\\", "/"),
        "synced_at": synced_at,
    }


def repair_null_rel_type_keys(session: Any, *, dry: bool) -> int:
    """Set rel_type = name where graph nodes only have name populated."""
    if dry:
        row = session.run(
            """
            MATCH (rt:SYS_RelationshipType)
            WHERE rt.rel_type IS NULL AND rt.name IS NOT NULL
            RETURN count(rt) AS c
            """
        ).single()
        return int(row["c"] or 0)
    row = session.run(
        """
        MATCH (rt:SYS_RelationshipType)
        WHERE rt.rel_type IS NULL AND rt.name IS NOT NULL
        SET rt.rel_type = rt.name
        RETURN count(rt) AS c
        """
    ).single()
    return int(row["c"] or 0)


def wire_schema_registry(session: Any, *, dry: bool) -> int:
    if dry:
        row = session.run(
            """
            MATCH (sr:SYS_SchemaRegistry), (rt:SYS_RelationshipType)
            WHERE NOT (sr)-[:HAS_RELATIONSHIP_TYPE]->(rt)
            RETURN count(rt) AS c
            """
        ).single()
        return int(row["c"] or 0)
    row = session.run(
        """
        MATCH (sr:SYS_SchemaRegistry), (rt:SYS_RelationshipType)
        MERGE (sr)-[:HAS_RELATIONSHIP_TYPE]->(rt)
        RETURN count(rt) AS c
        """
    ).single()
    return int(row["c"] or 0)


def sync_registry(
    session: Any,
    *,
    implemented_only: bool,
    dry: bool,
    wire_schema: bool,
    batch_size: int = 100,
) -> dict[str, int]:
    rows = _load_csv_rows(implemented_only=implemented_only)
    synced_at = _utc_now_iso()

    stats = {
        "csv_rows": len(rows),
        "repaired_null_keys": 0,
        "merged": 0,
        "wired_schema": 0,
        "graph_total_after": 0,
    }

    stats["repaired_null_keys"] = repair_null_rel_type_keys(session, dry=dry)

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        if dry:
            stats["merged"] += len(batch)
            continue
        for row in batch:
            props = _row_props(row, synced_at=synced_at)
            session.run(MERGE_CYPHER, props)
            stats["merged"] += 1

    if wire_schema:
        stats["wired_schema"] = wire_schema_registry(session, dry=dry)

    row = session.run("MATCH (rt:SYS_RelationshipType) RETURN count(rt) AS c").single()
    stats["graph_total_after"] = int(row["c"] or 0)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync CSV relationship registry to SYS_RelationshipType")
    ap.add_argument("--write", action="store_true", help="Persist to Neo4j")
    ap.add_argument("--dry", action="store_true", help="Preview counts only")
    ap.add_argument(
        "--implemented-only",
        action="store_true",
        help="Sync only lifecycle_status=implemented rows (default: all CSV rows)",
    )
    ap.add_argument(
        "--wire-schema",
        action="store_true",
        help="MERGE SYS_SchemaRegistry-[:HAS_RELATIONSHIP_TYPE]-> nodes",
    )
    ap.add_argument("--batch-size", type=int, default=100)
    args = ap.parse_args()
    dry = not args.write

    if not NEO4J_PASSWORD:
        print("NEO4J_PASSWORD not configured", file=sys.stderr)
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            stats = sync_registry(
                session,
                implemented_only=args.implemented_only,
                dry=dry,
                wire_schema=args.wire_schema,
                batch_size=max(1, args.batch_size),
            )
    finally:
        driver.close()

    mode = "DRY RUN" if dry else "WRITE"
    scope = "implemented" if args.implemented_only else "all CSV"
    print(f"=== Sync relationship registry to graph ({mode}, {scope}) ===")
    print(f"  CSV rows processed:     {stats['csv_rows']}")
    print(f"  Repaired null rel_type: {stats['repaired_null_keys']}")
    print(f"  MERGE operations:       {stats['merged']}")
    if args.wire_schema:
        print(f"  SchemaRegistry wired:   {stats['wired_schema']}")
    print(f"  SYS_RelationshipType after: {stats['graph_total_after']}")

    if dry:
        print("\nRe-run with --write to persist.")
    else:
        print("\nRun: python -m scripts.tools.validate_sys_registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
