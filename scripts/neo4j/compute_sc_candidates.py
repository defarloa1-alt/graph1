#!/usr/bin/env python3
"""
Compute sc_candidate flag and sc_candidate_facets on Person and Place nodes.

Principle: An entity with a bibliographic-type external identifier is recognized
by the bibliographic control universe and is therefore a SubjectConcept candidate.

Logic:
  1. Entity has ≥1 biblio authority ID (VIAF, GND, LoC, FAST, ISNI, BnF, etc.)
     → sc_candidate = true
  2. sc_candidate_facets = distinct facet keys from:
     - MEMBER_OF → SubjectConcept → HAS_PRIMARY_FACET → Facet  (if any)
     - Fallback: entity type default (Person→BIOGRAPHIC, Place→GEOGRAPHIC)
  3. sc_biblio_ids = count of distinct biblio authority IDs present
  4. Entities WITHOUT any biblio ID → sc_candidate = false

Usage:
  python scripts/neo4j/compute_sc_candidates.py --dry-run
  python scripts/neo4j/compute_sc_candidates.py --write
"""

from __future__ import annotations

import argparse
import io
import os
import sys
from collections import defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))

try:
    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
except ImportError:
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")

from neo4j import GraphDatabase

# ── Biblio authority properties per entity type ───────────────────────────────
# property_name → P-code (for traceability to SYS_PropertyMapping)

PERSON_BIBLIO_PROPS = {
    "viaf_id":          "P214",
    "gnd_id":           "P227",
    "loc_authority_id": "P244",
    "lcnaf_id":         None,     # derived from LoC, not a direct Wikidata PID
    "fast_id":          "P2163",
    "isni":             "P213",
    "bnf_id":           "P268",
    "idref_id":         "P269",
    "nli_id":           "P949",
}

PLACE_BIBLIO_PROPS = {
    "viaf_id":          "P214",
    "gnd_id":           "P227",
    "loc_authority_id": "P244",
    "fast_id":          "P2163",
    "geonames_id":      "P1566",
}

PERSON_DEFAULT_FACET = "BIOGRAPHIC"
PLACE_DEFAULT_FACET = "GEOGRAPHIC"


def build_biblio_count_expr(props: dict) -> str:
    """Build a Cypher CASE expression that counts how many biblio properties are non-null."""
    parts = []
    for prop in props:
        parts.append(f"CASE WHEN n.{prop} IS NOT NULL THEN 1 ELSE 0 END")
    return " + ".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Compute SC candidate flags on entities")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    write_mode = args.write and not args.dry_run
    print(f"SC Candidate Computation [{'WRITE' if write_mode else 'DRY RUN'}]")
    print("=" * 60)

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # ── Step 1: Preview Person biblio coverage ────────────────────────────────
    print("\nStep 1: Person biblio authority coverage...")
    person_expr = build_biblio_count_expr(PERSON_BIBLIO_PROPS)
    with driver.session() as session:
        result = session.run(f"""
            MATCH (n:Person)
            WITH n, ({person_expr}) AS biblio_count
            RETURN biblio_count, count(n) AS cnt
            ORDER BY biblio_count
        """)
        person_dist = []
        person_total = 0
        person_candidates = 0
        for r in result:
            bc = r["biblio_count"]
            cnt = r["cnt"]
            person_dist.append((bc, cnt))
            person_total += cnt
            if bc > 0:
                person_candidates += cnt
            print(f"  {bc} biblio IDs:  {cnt:>6} persons")
        print(f"\n  Candidates: {person_candidates} / {person_total} ({100*person_candidates/person_total:.1f}%)")

    # ── Step 2: Preview Place biblio coverage ─────────────────────────────────
    print("\nStep 2: Place biblio authority coverage...")
    place_expr = build_biblio_count_expr(PLACE_BIBLIO_PROPS)
    with driver.session() as session:
        result = session.run(f"""
            MATCH (n:Place)
            WITH n, ({place_expr}) AS biblio_count
            RETURN biblio_count, count(n) AS cnt
            ORDER BY biblio_count
        """)
        place_total = 0
        place_candidates = 0
        for r in result:
            bc = r["biblio_count"]
            cnt = r["cnt"]
            place_total += cnt
            if bc > 0:
                place_candidates += cnt
            print(f"  {bc} biblio IDs:  {cnt:>6} places")
        print(f"\n  Candidates: {place_candidates} / {place_total} ({100*place_candidates/place_total:.1f}%)")

    # ── Step 3: Preview facet routing from MEMBER_OF ──────────────────────────
    print("\nStep 3: Facet routing from MEMBER_OF → SC → Facet...")
    with driver.session() as session:
        # Persons with MEMBER_OF that routes to a Facet
        result = session.run("""
            MATCH (p:Person)-[:MEMBER_OF]->(sc:SubjectConcept)-[:HAS_PRIMARY_FACET]->(f:Facet)
            RETURN f.key AS facet, count(DISTINCT p) AS persons
            ORDER BY persons DESC
        """)
        print("  Person → Facet (via MEMBER_OF):")
        for r in result:
            print(f"    {r['facet']:20s}  {r['persons']:>6}")

        result = session.run("""
            MATCH (p:Place)-[:MEMBER_OF]->(sc:SubjectConcept)-[:HAS_PRIMARY_FACET]->(f:Facet)
            RETURN f.key AS facet, count(DISTINCT p) AS places
            ORDER BY places DESC
        """)
        print("  Place → Facet (via MEMBER_OF):")
        for r in result:
            print(f"    {r['facet']:20s}  {r['places']:>6}")

    if not write_mode:
        print(f"\n  [DRY RUN] Re-run with --write to apply.")
        print(f"\n  Would set:")
        print(f"    Person: {person_candidates} sc_candidate=true, {person_total - person_candidates} sc_candidate=false")
        print(f"    Place:  {place_candidates} sc_candidate=true, {place_total - place_candidates} sc_candidate=false")
        driver.close()
        return

    # ── Step 4: Write sc_candidate + sc_biblio_count on Person ────────────────
    print("\nStep 4: Writing Person sc_candidate flags...")
    with driver.session() as session:
        # Set sc_candidate = true where has biblio IDs
        result = session.run(f"""
            MATCH (n:Person)
            WITH n, ({person_expr}) AS biblio_count
            WHERE biblio_count > 0
            SET n.sc_candidate = true,
                n.sc_biblio_count = biblio_count,
                n.sc_candidate_updated = date('2026-03-08')
            RETURN count(n) AS cnt
        """)
        true_cnt = result.single()["cnt"]
        print(f"  {true_cnt} Person nodes → sc_candidate=true")

        # Set sc_candidate = false where no biblio IDs
        result = session.run(f"""
            MATCH (n:Person)
            WITH n, ({person_expr}) AS biblio_count
            WHERE biblio_count = 0
            SET n.sc_candidate = false,
                n.sc_biblio_count = 0,
                n.sc_candidate_updated = date('2026-03-08')
            RETURN count(n) AS cnt
        """)
        false_cnt = result.single()["cnt"]
        print(f"  {false_cnt} Person nodes → sc_candidate=false")

    # ── Step 5: Write sc_candidate + sc_biblio_count on Place ─────────────────
    print("\nStep 5: Writing Place sc_candidate flags...")
    with driver.session() as session:
        result = session.run(f"""
            MATCH (n:Place)
            WITH n, ({place_expr}) AS biblio_count
            WHERE biblio_count > 0
            SET n.sc_candidate = true,
                n.sc_biblio_count = biblio_count,
                n.sc_candidate_updated = date('2026-03-08')
            RETURN count(n) AS cnt
        """)
        true_cnt = result.single()["cnt"]
        print(f"  {true_cnt} Place nodes → sc_candidate=true")

        result = session.run(f"""
            MATCH (n:Place)
            WITH n, ({place_expr}) AS biblio_count
            WHERE biblio_count = 0
            SET n.sc_candidate = false,
                n.sc_biblio_count = 0,
                n.sc_candidate_updated = date('2026-03-08')
            RETURN count(n) AS cnt
        """)
        false_cnt = result.single()["cnt"]
        print(f"  {false_cnt} Place nodes → sc_candidate=false")

    # ── Step 6: Compute sc_candidate_facets from MEMBER_OF → SC → Facet ──────
    print("\nStep 6: Computing sc_candidate_facets...")
    with driver.session() as session:
        # Person: collect facet keys from MEMBER_OF path, default to BIOGRAPHIC
        result = session.run(f"""
            MATCH (p:Person)
            WHERE p.sc_candidate = true
            OPTIONAL MATCH (p)-[:MEMBER_OF]->(sc:SubjectConcept)-[:HAS_PRIMARY_FACET]->(f:Facet)
            WITH p, collect(DISTINCT f.key) AS facets
            WITH p, CASE WHEN size(facets) = 0 OR facets = [null]
                         THEN ['{PERSON_DEFAULT_FACET}']
                         ELSE [x IN facets WHERE x IS NOT NULL]
                    END AS candidate_facets
            SET p.sc_candidate_facets = candidate_facets
            RETURN count(p) AS cnt,
                   count(CASE WHEN size(candidate_facets) = 1 THEN 1 END) AS single_facet,
                   count(CASE WHEN size(candidate_facets) > 1 THEN 1 END) AS multi_facet
        """)
        r = result.single()
        print(f"  Person: {r['cnt']} with facets ({r['single_facet']} single, {r['multi_facet']} multi)")

        # Place: collect facet keys from MEMBER_OF path, default to GEOGRAPHIC
        result = session.run(f"""
            MATCH (p:Place)
            WHERE p.sc_candidate = true
            OPTIONAL MATCH (p)-[:MEMBER_OF]->(sc:SubjectConcept)-[:HAS_PRIMARY_FACET]->(f:Facet)
            WITH p, collect(DISTINCT f.key) AS facets
            WITH p, CASE WHEN size(facets) = 0 OR facets = [null]
                         THEN ['{PLACE_DEFAULT_FACET}']
                         ELSE [x IN facets WHERE x IS NOT NULL]
                    END AS candidate_facets
            SET p.sc_candidate_facets = candidate_facets
            RETURN count(p) AS cnt,
                   count(CASE WHEN size(candidate_facets) = 1 THEN 1 END) AS single_facet,
                   count(CASE WHEN size(candidate_facets) > 1 THEN 1 END) AS multi_facet
        """)
        r = result.single()
        print(f"  Place:  {r['cnt']} with facets ({r['single_facet']} single, {r['multi_facet']} multi)")

    # ── Verify ────────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("Verification:")
    with driver.session() as session:
        result = session.run("""
            MATCH (n)
            WHERE n:Person OR n:Place
            WITH labels(n)[0] AS entity_type,
                 n.sc_candidate AS cand,
                 n.sc_biblio_count AS bc
            RETURN entity_type,
                   cand,
                   count(*) AS cnt,
                   avg(bc) AS avg_biblio
            ORDER BY entity_type, cand
        """)
        print(f"  {'Type':8s}  {'Candidate':10s}  {'Count':>7}  {'Avg biblio IDs':>14}")
        for r in result:
            cand_str = str(r["cand"]) if r["cand"] is not None else "null"
            avg_b = f"{r['avg_biblio']:.1f}" if r["avg_biblio"] is not None else "-"
            print(f"  {r['entity_type']:8s}  {cand_str:10s}  {r['cnt']:>7}  {avg_b:>14}")

        # Facet breakdown for candidates
        result = session.run("""
            MATCH (n)
            WHERE (n:Person OR n:Place) AND n.sc_candidate = true
            UNWIND n.sc_candidate_facets AS facet
            RETURN facet, count(n) AS cnt
            ORDER BY cnt DESC
        """)
        print(f"\n  SC candidate facet distribution:")
        for r in result:
            print(f"    {r['facet']:20s}  {r['cnt']:>6}")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
