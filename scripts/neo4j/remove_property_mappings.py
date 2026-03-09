"""
remove_property_mappings.py

Remove all 500 SYS_PropertyMapping nodes and their facet edges.

These nodes were a bulk LLM-classified mapping of ALL Wikidata PIDs to facets.
They are redundant with the cipher mechanism (QID+PID+value = vertex address)
and mostly irrelevant to the Roman Republic domain (MusicBrainz, FilmAffinity, etc.).

The SYS_FacetRouter nodes (38) remain — those are the curated routing triggers.

What gets deleted:
  - 500 SYS_PropertyMapping nodes
  - ~500 HAS_PRIMARY_FACET edges (PropertyMapping → Facet)
  - ~195 HAS_SECONDARY_FACET edges (PropertyMapping → Facet)

Safe to re-run (MATCH-based deletion, no-op if already removed).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        # ── Pre-check ──────────────────────────────────────────────────
        count = session.run(
            "MATCH (pm:SYS_PropertyMapping) RETURN count(pm) AS c"
        ).single()["c"]
        edges = session.run(
            "MATCH (pm:SYS_PropertyMapping)-[r]->() RETURN count(r) AS c"
        ).single()["c"]
        print(f"Before: {count} SYS_PropertyMapping nodes, {edges} outbound edges")

        if count == 0:
            print("Nothing to remove.")
            driver.close()
            return

        # ── Delete ─────────────────────────────────────────────────────
        deleted = session.run(
            "MATCH (pm:SYS_PropertyMapping) DETACH DELETE pm "
            "RETURN count(pm) AS deleted"
        ).single()["deleted"]
        print(f"Deleted: {deleted} SYS_PropertyMapping nodes (with all edges)")

        # ── Verify ─────────────────────────────────────────────────────
        remaining = session.run(
            "MATCH (pm:SYS_PropertyMapping) RETURN count(pm) AS c"
        ).single()["c"]
        print(f"After: {remaining} SYS_PropertyMapping nodes remain")

        # ── Also clean up SYS_NodeType registry entry ──────────────────
        session.run(
            "MATCH (nt:SYS_NodeType {name: 'SYS_PropertyMapping'}) "
            "DETACH DELETE nt"
        )
        print("Removed SYS_NodeType registry entry for SYS_PropertyMapping")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
