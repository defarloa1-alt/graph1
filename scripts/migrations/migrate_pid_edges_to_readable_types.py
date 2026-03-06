#!/usr/bin/env python3
"""
Migrate PID-typed edges to human-readable relationship types.

Neo4j Bloom/Browser show the relationship type, not r.label. This script renames
P31 → INSTANCE_OF, P1050 → MEDICAL_CONDITION, etc. so the graph displays readable names.

- Registry-mapped PIDs: use canonical relationship_type (INSTANCE_OF, TYPE_OF, ...)
- Unmapped PIDs: derive from r.label ("medical condition" → MEDICAL_CONDITION)

Requires: APOC, .env with NEO4J_*

Usage:
  python scripts/migrations/migrate_pid_edges_to_readable_types.py --dry-run
  python scripts/migrations/migrate_pid_edges_to_readable_types.py
"""
import argparse
import csv
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI", "neo4j+s://default.databases.neo4j.io")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", os.environ.get("NEO4J_USER", "neo4j"))
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

from neo4j import GraphDatabase

REGISTRY_PATH = PROJECT_ROOT / "Relationships" / "relationship_types_registry_master.csv"
BATCH_SIZE = 5000


def sanitize_label_to_type(label: str) -> str:
    """'medical condition' → MEDICAL_CONDITION. Valid Cypher identifier."""
    if not label or not isinstance(label, str):
        return "UNKNOWN"
    s = re.sub(r"[^a-zA-Z0-9\s]", "", label)
    s = re.sub(r"\s+", "_", s.strip()).upper()
    return s or "UNKNOWN"


def load_registry() -> dict[str, str]:
    """pid → canonical relationship_type"""
    out = {}
    if not REGISTRY_PATH.exists():
        return out
    with open(REGISTRY_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            pid = (row.get("wikidata_property") or "").strip()
            if not pid:
                continue
            canonical = (row.get("relationship_type") or "").strip()
            if canonical and re.match(r"^[A-Z][A-Z0-9_]*$", canonical):
                out[pid] = canonical
    return out


def main():
    ap = argparse.ArgumentParser(description="Migrate PID edges to human-readable types")
    ap.add_argument("--dry-run", action="store_true", help="Report only, no writes")
    args = ap.parse_args()

    if not NEO4J_PASSWORD:
        print("NEO4J_PASSWORD not set. Use .env")
        sys.exit(1)

    registry = load_registry()
    print(f"Registry: {len(registry)} PID -> canonical mappings")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME or "neo4j", NEO4J_PASSWORD))

    # True PID types only: P31, P1050, WIKIDATA_P6379
    with driver.session() as session:
        r = session.run("""
            CALL db.relationshipTypes() YIELD relationshipType
            WHERE relationshipType =~ '^P[0-9]+$' OR relationshipType =~ '^WIKIDATA_P[0-9]+$'
            RETURN relationshipType AS rel_type
            ORDER BY rel_type
        """)
        rel_types = [row["rel_type"] for row in r]

    def to_pid(rt: str) -> str:
        return rt.replace("WIKIDATA_", "", 1) if rt.startswith("WIKIDATA_") else rt

    # Build mapping: rel_type → new_type
    mapping: dict[str, str] = {}
    seen_new_types: set[str] = set()

    for rel_type in rel_types:
        pid = to_pid(rel_type)
        if pid in registry:
            new_type = registry[pid]
        else:
            # Derive from r.label
            with driver.session() as session:
                r = session.run(f"""
                    MATCH ()-[r:`{rel_type}`]->()
                    WHERE r.label IS NOT NULL AND r.label <> ''
                    RETURN r.label AS lbl
                    LIMIT 1
                """)
                row = r.single()
            if row and row["lbl"]:
                base = sanitize_label_to_type(row["lbl"])
                new_type = f"{pid}_{base}" if base in seen_new_types else base
                seen_new_types.add(new_type)
            else:
                new_type = f"P{pid}" if not pid.startswith("P") else pid  # fallback: keep PID
        mapping[rel_type] = new_type

    print()
    print("Migration plan:")
    for rt, nt in sorted(mapping.items()):
        if rt != nt:
            print(f"  {rt} -> {nt}")
    print()

    if args.dry_run:
        print("[DRY RUN] No changes made.")
        driver.close()
        return 0

    total = 0
    for rel_type, new_type in sorted(mapping.items()):
        if rel_type == new_type:
            continue
        cypher_rel = f"`{rel_type}`" if " " in rel_type or "-" in rel_type else rel_type
        # Escape new_type for Cypher if needed
        new_type_esc = new_type.replace("'", "\\'") if "'" in new_type else new_type

        print(f"Migrating {rel_type} -> {new_type}...", end=" ", flush=True)
        type_total = 0
        while True:
            with driver.session() as session:
                result = session.run(f"""
                    MATCH (a)-[old:{cypher_rel}]->(b)
                    WITH a, old, b, properties(old) AS props
                    LIMIT {BATCH_SIZE}
                    CALL apoc.create.relationship(a, '{new_type_esc}', props, b)
                    YIELD rel
                    DELETE old
                    RETURN count(rel) AS n
                """)
                n = result.single()["n"]
            type_total += n
            if n == 0:
                break
        total += type_total
        print(f"{type_total:,} edges")

    driver.close()
    print()
    print(f"Total migrated: {total:,} edges")
    return 0


if __name__ == "__main__":
    sys.exit(main())
