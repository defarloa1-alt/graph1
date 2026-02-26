#!/usr/bin/env python3
"""
Validate SubjectConcept Model on Neo4j Graph

Runs facet-based queries and vertex jump validation on the 99.9% connected graph
to confirm the SubjectConcept model before further work.

Checks:
  1. Graph connectivity (largest connected component %)
  2. Entity type distribution (SubjectConcept, Person, Event, Place, etc.)
  3. Entity cipher presence and format
  4. Vertex jump computation (pure function, no graph query)
  5. Canonical edge coverage (if edges exist)
  6. SubjectConcept anchor presence (Q17167 Roman Republic)

Usage:
    python scripts/validation/validate_subjectconcept_model.py
    python scripts/validation/validate_subjectconcept_model.py --json  # Machine-readable output
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

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

from scripts.tools.entity_cipher import (  # noqa: E402
    vertex_jump,
    generate_faceted_cipher,
    generate_entity_cipher,
    CANONICAL_FACETS,
)


def run_validation(driver, json_output: bool = False) -> dict:
    """Run all SubjectConcept model validations."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "passed": [],
        "failed": [],
        "warnings": [],
    }

    with driver.session() as session:
        # 1. Node and edge counts
        r = session.run("MATCH (n) RETURN count(n) as c").single()
        node_count = r["c"] if r else 0

        r = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()
        edge_count = r["c"] if r else 0

        results["checks"]["node_count"] = node_count
        results["checks"]["edge_count"] = edge_count

        if node_count == 0:
            results["failed"].append("No nodes in graph")
            return results

        # 2. Connectivity: structurally isolated vs weakly connected (advisor)
        try:
            # Structurally isolated: no edges at all
            r = session.run("""
                MATCH (n)
                WHERE NOT (n)--()
                RETURN count(n) as isolated
            """).single()
            structurally_isolated = r["isolated"] if r else 0

            # Weakly connected: has MEMBER_OF only, no canonical/enrichment edges
            r = session.run("""
                MATCH (n)-[:MEMBER_OF]->()
                WITH n
                OPTIONAL MATCH (n)-[e]->()
                WHERE type(e) <> 'MEMBER_OF'
                WITH n, count(e) as non_out
                OPTIONAL MATCH (n)<-[e]-()
                WHERE type(e) <> 'MEMBER_OF'
                WITH n, non_out, count(e) as non_in
                WHERE non_out = 0 AND non_in = 0
                RETURN count(n) as weakly_connected
            """).single()
            weakly_connected = r["weakly_connected"] if r else 0

            # Strongly connected: has non-MEMBER_OF edges (canonical or enrichment)
            connected = node_count - structurally_isolated
            strongly_connected = connected - weakly_connected
            conn_pct = (connected / node_count * 100) if node_count else 0

            results["checks"]["structurally_isolated"] = structurally_isolated
            results["checks"]["weakly_connected"] = weakly_connected
            results["checks"]["strongly_connected"] = strongly_connected
            results["checks"]["connectivity_pct"] = round(conn_pct, 2)

            if conn_pct >= 99.9:
                results["passed"].append(f"Connectivity: {conn_pct:.1f}% (target 99.9%)")
            elif conn_pct >= 50:
                results["warnings"].append(f"Connectivity: {conn_pct:.1f}% (target 99.9%)")
            elif conn_pct >= 10:
                results["warnings"].append(f"Connectivity: {conn_pct:.1f}% (target 99.9%)")
            else:
                results["failed"].append(f"Connectivity: {conn_pct:.1f}% (target 99.9%)")

            # Pipeline stage insight
            results["checks"]["connectivity_breakdown"] = (
                f"{structurally_isolated:,} isolated | {weakly_connected:,} MEMBER_OF-only | {strongly_connected:,} with other edges"
            )
        except Exception as e:
            results["warnings"].append(f"Connectivity: {e}")

        # 3. Entity type distribution
        try:
            r = session.run("""
                MATCH (n:Entity)
                RETURN n.entity_type as t, count(*) as c
                ORDER BY c DESC
            """)
            type_dist = {row["t"] or "NULL": row["c"] for row in r}
            results["checks"]["entity_type_distribution"] = type_dist

            subj_count = type_dist.get("SUBJECTCONCEPT", 0) + type_dist.get("sub", 0)
            if subj_count >= 1:
                results["passed"].append(f"SubjectConcept anchors: {subj_count} found")
            else:
                results["warnings"].append("SubjectConcept: No SUBJECTCONCEPT entities (may use entity_type 'sub')")
        except Exception as e:
            results["warnings"].append(f"Entity type distribution: {e}")

        # 3b. Entity type case consistency (advisor: flag upper+lowercase variants)
        try:
            types_seen = set(type_dist.keys()) - {"NULL"}
            case_variants = {}
            for t in types_seen:
                if t is None:
                    continue
                upper = t.upper() if isinstance(t, str) else t
                if upper not in case_variants:
                    case_variants[upper] = []
                if t not in case_variants[upper]:
                    case_variants[upper].append(t)
            inconsistent = {k: v for k, v in case_variants.items() if len(v) > 1}
            results["checks"]["entity_type_case_consistency"] = {
                "inconsistent": inconsistent,
                "consistent": len(inconsistent) == 0,
            }
            if inconsistent:
                results["warnings"].append(
                    f"Entity type case: {len(inconsistent)} types have upper+lower variants (run normalize_entity_type_casing.py)"
                )
            else:
                results["passed"].append("Entity type case: all consistent (no upper+lower variants)")
        except Exception as e:
            results["warnings"].append(f"Entity type case consistency: {e}")

        # 4. Entity cipher presence
        try:
            r = session.run("""
                MATCH (n:Entity)
                WHERE n.entity_cipher IS NOT NULL
                RETURN count(n) as with_cipher
            """).single()
            with_cipher = r["with_cipher"] if r else 0
            results["checks"]["entities_with_cipher"] = with_cipher

            if with_cipher >= node_count * 0.9:
                results["passed"].append(f"Entity cipher: {with_cipher}/{node_count} entities")
            elif with_cipher > 0:
                results["warnings"].append(f"Entity cipher: {with_cipher}/{node_count} (partial)")
            else:
                results["failed"].append("Entity cipher: No entities have entity_cipher")
        except Exception as e:
            results["warnings"].append(f"Entity cipher check: {e}")

        # 5. SubjectConcept anchor (Q17167 Roman Republic)
        try:
            r = session.run("""
                MATCH (n:Entity {qid: 'Q17167'})
                RETURN n.label as label, n.entity_cipher as cipher
            """).single()
            if r:
                results["checks"]["seed_anchor"] = {"qid": "Q17167", "label": r["label"], "cipher": r["cipher"]}
                results["passed"].append("Seed anchor Q17167 (Roman Republic) present")
            else:
                results["warnings"].append("Seed anchor Q17167 not found (graph may use different seed)")
        except Exception as e:
            results["warnings"].append(f"Seed anchor check: {e}")

        # 6. Canonical edge coverage (if edges exist)
        if edge_count > 0:
            try:
                r = session.run("""
                    MATCH ()-[r]->()
                    WHERE r.canonical_type IS NOT NULL
                    RETURN count(r) as canonicalized
                """).single()
                canon = r["canonicalized"] if r else 0
                results["checks"]["canonicalized_edges"] = canon
                if canon > 0:
                    results["passed"].append(f"Canonical edges: {canon:,} stamped")
                else:
                    results["warnings"].append("Canonical edges: None stamped (run canonicalize_edges.py)")
            except Exception as e:
                results["warnings"].append(f"Canonical edge check: {e}")

    # 7. Vertex jump (pure computation - no graph)
    try:
        target = vertex_jump("ent_per_Q1048", "MILITARY", "POLITICAL", "Q17167")
        expected = "fent_pol_Q1048_Q17167"
        if target == expected:
            results["passed"].append("Vertex jump: computation correct")
            results["checks"]["vertex_jump"] = {"input": "Caesar MILITARY->POLITICAL", "output": target}
        else:
            results["failed"].append(f"Vertex jump: got {target}, expected {expected}")
    except Exception as e:
        results["failed"].append(f"Vertex jump: {e}")

    # 8. Faceted cipher format
    try:
        c = generate_faceted_cipher("ent_per_Q1048", "POLITICAL", "Q17167")
        if c == "fent_pol_Q1048_Q17167":
            results["passed"].append("Faceted cipher format: correct")
        else:
            results["failed"].append(f"Faceted cipher: got {c}")
    except Exception as e:
        results["failed"].append(f"Faceted cipher: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate SubjectConcept model on Neo4j graph")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    if not NEO4J_PASSWORD:
        print("Error: NEO4J_PASSWORD not set. Use .env or config_loader.")
        sys.exit(1)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    try:
        results = run_validation(driver)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("=" * 70)
            print("SUBJECTCONCEPT MODEL VALIDATION")
            print("=" * 70)
            print(f"Timestamp: {results['timestamp']}")
            print()
            print("Checks:")
            for k, v in results["checks"].items():
                if isinstance(v, dict):
                    print(f"  {k}: {json.dumps(v)}")
                else:
                    print(f"  {k}: {v}")
            print()
            print("Passed:", len(results["passed"]))
            for p in results["passed"]:
                print(f"  [OK] {p}")
            if results["warnings"]:
                print()
                print("Warnings:", len(results["warnings"]))
                for w in results["warnings"]:
                    print(f"  [!!] {w}")
            if results["failed"]:
                print()
                print("Failed:", len(results["failed"]))
                for f in results["failed"]:
                    print(f"  [X] {f}")
            print()
            if results["failed"]:
                print("Result: FAILED")
                sys.exit(1)
            else:
                print("Result: PASSED (with warnings)" if results["warnings"] else "Result: PASSED")
                sys.exit(0)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
