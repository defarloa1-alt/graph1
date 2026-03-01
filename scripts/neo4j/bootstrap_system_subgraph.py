#!/usr/bin/env python3
"""
Bootstrap the complete Chrystallum system subgraph.

Creates the full schema structure under the Chrystallum root:
  - Facets (18 CanonicalFacet)
  - Federations (authority systems + SYS registry)
  - Subject concepts (SubjectConceptRoot, registries, agents)
  - Bibliography (if BibliographySource nodes exist)
  - FacetRoot bridge (for bootstrap compatibility)

Run order:
  1. create_authority_federations.cypher  — Chrystallum + HAS_FEDERATION_CLUSTER
  2. create_facets_cluster.cypher         — HAS_FACET_CLUSTER → 18 facets
  3. bridge_facet_root.cypher            — HAS_FACET_ROOT for bootstrap
  4. rebuild_federation_registry.py      — HAS_FEDERATION → SYS_FederationRegistry
  5. bootstrap_subject_concept_agents.cypher — HAS_SUBJECT_CONCEPT_ROOT, agents
  6. wire_bibliography.cypher (optional)  — HAS_BIBLIOGRAPHY if nodes exist

After bootstrap, visualize with:
  scripts/federation/view_full_system_subgraph.cypher (run in Neo4j Browser)

Usage:
    python scripts/neo4j/bootstrap_system_subgraph.py
    python scripts/neo4j/bootstrap_system_subgraph.py --dry-run
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
NEO4J_SCRIPTS = SCRIPTS / "neo4j"
FEDERATION_SCRIPTS = SCRIPTS / "federation"
CYPHER = ROOT / "Cypher"


def run_cypher(rel_path: str) -> bool:
    """Run a Cypher file via run_cypher_file.py."""
    path = ROOT / rel_path
    if not path.exists():
        print(f"  SKIP: {rel_path} (not found)")
        return True
    print(f"\n  Running: {rel_path}")
    r = subprocess.run(
        [sys.executable, str(NEO4J_SCRIPTS / "run_cypher_file.py"), str(path)],
        cwd=str(ROOT),
    )
    return r.returncode == 0


def run_python(rel_path: str, *args: str) -> bool:
    """Run a Python script."""
    path = ROOT / rel_path
    if not path.exists():
        print(f"  SKIP: {rel_path} (not found)")
        return True
    print(f"\n  Running: {rel_path}")
    r = subprocess.run(
        [sys.executable, str(path), *args],
        cwd=str(ROOT),
    )
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser(description="Bootstrap complete Chrystallum system subgraph")
    ap.add_argument("--dry-run", action="store_true", help="Print steps only, no execution")
    ap.add_argument("--skip-subject", action="store_true", help="Skip bootstrap_subject_concept_agents (long)")
    ap.add_argument("--skip-biblio", action="store_true", help="Skip bibliography wiring")
    args = ap.parse_args()

    steps = [
        ("1. Authority federations", "scripts/federation/create_authority_federations.cypher", run_cypher),
        ("2. Facets cluster", "scripts/federation/create_facets_cluster.cypher", run_cypher),
        ("3. FacetRoot bridge", "scripts/federation/bridge_facet_root.cypher", run_cypher),
        ("4. Federation registry", "scripts/neo4j/rebuild_federation_registry.py", run_python),
        ("5. Subject concept agents", "Cypher/bootstrap_subject_concept_agents.cypher", run_cypher),
        ("6. Wire bibliography", "scripts/federation/wire_bibliography.cypher", run_cypher),
    ]

    print("=" * 60)
    print("CHRYSTALLUM SYSTEM SUBGRAPH BOOTSTRAP")
    print("=" * 60)

    if args.dry_run:
        print("\nDry run — would execute:")
        for name, path, _ in steps:
            skip = ""
            if "Subject" in name and args.skip_subject:
                skip = " (skipped)"
            if "biblio" in name and args.skip_biblio:
                skip = " (skipped)"
            print(f"  {name}: {path}{skip}")
        print("\nVisualize after: scripts/federation/view_full_system_subgraph.cypher")
        return 0

    ok = True
    for name, path, fn in steps:
        if "Subject" in name and args.skip_subject:
            print(f"\n  SKIP: {name}")
            continue
        if "biblio" in name and args.skip_biblio:
            print(f"\n  SKIP: {name}")
            continue
        print(f"\n--- {name} ---")
        if not fn(path):
            print(f"  FAILED: {path}")
            ok = False
            break

    if ok:
        print("\n" + "=" * 60)
        print("BOOTSTRAP COMPLETE")
        print("=" * 60)
        print("\nVisualize the full system subgraph in Neo4j Browser:")
        print("  Open scripts/federation/view_full_system_subgraph.cypher")
        print("  Copy contents, paste into Neo4j Browser, run")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
