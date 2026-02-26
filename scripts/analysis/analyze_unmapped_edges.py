#!/usr/bin/env python3
"""
Canonicalization: Unmapped Edges Analysis

Distinguishes high-frequency Wikidata PIDs missing from registry (add them)
from 220 historian-level types (expected 19% ceiling until RelationshipType work).

Usage:
    python scripts/analysis/analyze_unmapped_edges.py
    python scripts/analysis/analyze_unmapped_edges.py --output output/analysis/unmapped_edges_analysis.md
"""
import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from neo4j import GraphDatabase

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    import os
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", os.environ.get("NEO4J_USER", "neo4j"))
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

REGISTRY_PATH = ROOT / "Relationships" / "relationship_types_registry_master.csv"
UNMAPPED_PATH = ROOT / "output" / "analysis" / "registry_unmapped_to_wikidata.txt"

# PIDs that are admin/category noise — do not add to registry.
ADMIN_NOISE_PIDS = frozenset(["P971", "P6104", "P5008", "P6216"])


def main():
    parser = argparse.ArgumentParser(description="Analyze unmapped edges: high-freq PIDs vs historian types")
    parser.add_argument("--output", "-o", default="output/analysis/unmapped_edges_analysis.md", help="Output markdown path")
    parser.add_argument("--top", type=int, default=20, help="Top N unmapped PIDs to report (default 20)")
    args = parser.parse_args()

    if not NEO4J_PASSWORD:
        print("Error: NEO4J_PASSWORD not set.")
        sys.exit(1)

    # Load registry: PIDs and canonical relationship types (e.g. PART_OF, INSTANCE_OF)
    # Edges typed as canonical names are already canonicalized; exclude from unmapped count.
    registry_pids = set()
    registry_canonical_types = set()
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                pid = (row.get("wikidata_property") or "").strip()
                rel_type = (row.get("relationship_type") or "").strip()
                if pid and pid.startswith("P"):
                    registry_pids.add(pid)
                if rel_type and pid:
                    registry_canonical_types.add(rel_type)

    def _is_mapped(edge_type: str) -> bool:
        """Mapped if PID in registry or already canonical (e.g. PART_OF, INSTANCE_OF)."""
        return edge_type in registry_pids or edge_type in registry_canonical_types

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # Edge count per relationship type
        result = session.run("""
            MATCH ()-[r]->()
            WITH type(r) as rel_type, count(r) as c
            RETURN rel_type, c
            ORDER BY c DESC
        """)
        all_counts = [(r["rel_type"], r["c"]) for r in result]

    driver.close()

    # Scope: PID-typed edges (P31, P361, PART_OF, etc.) — Wikidata alignment metric
    pid_scope = [(t, c) for t, c in all_counts if t.startswith("P")]
    total_edges = sum(c for _, c in pid_scope)
    in_registry = [(t, c) for t, c in pid_scope if _is_mapped(t)]
    unmapped = [(t, c) for t, c in pid_scope if not _is_mapped(t)]
    canonicalized = sum(c for _, c in in_registry)
    unmapped_edges = sum(c for _, c in unmapped)

    # Top unmapped by frequency
    top_unmapped = unmapped[: args.top]

    # Build output
    lines = [
        "# Unmapped Edges Analysis",
        "",
        f"**Total PID edges:** {total_edges:,}",
        f"**Canonicalized (in registry):** {canonicalized:,} ({100 * canonicalized / total_edges:.1f}%)" if total_edges else "",
        f"**Unmapped:** {unmapped_edges:,} ({100 * unmapped_edges / total_edges:.1f}%)" if total_edges else "",
        "",
        "## Top Unmapped PIDs by Edge Count",
        "",
        "| PID | Edge Count | Action |",
        "|-----|------------|--------|",
    ]

    for pid, count in top_unmapped:
        action = "Add to registry if Wikidata property" if count > 100 else "Likely historian-level; CRM cross-ref"
        lines.append(f"| {pid} | {count:,} | {action} |")

    lines.extend([
        "",
        "## Interpretation",
        "",
        "- **ADMIN_NOISE (P971, P6104, P5008, P6216):** Wikimedia category/curation metadata. Do not add to registry.",
        "- **High-frequency unmapped (e.g. >500 edges):** Likely Wikidata PIDs not yet in registry. Add to `relationship_types_registry_master.csv`.",
        "- **Low-frequency unmapped:** Likely Chrystallum-native historian predicates (220 in `registry_unmapped_to_wikidata.txt`). Need CRM/CRMinf cross-ref at type level; 19% canonicalization ceiling until RelationshipType work.",
        "",
        f"**Registry:** {len(registry_pids)} PIDs mapped. **Historian types:** 220 in unmapped list.",
    ])

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()
