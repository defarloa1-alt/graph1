"""
relabel_places_from_subjectconcept.py

Fixes mislabeled SubjectConcept nodes that are actually places/provinces.
All have duplicate Place nodes (same pleiades_id).

Strategy: transfer relationships from SC node to Place node, then delete SC node.
Avoids APOC mergeNodes property-conflict issues with uniqueness constraints.

Also cleans up 2 nodes (Achaea, Africa) that were partially merged by a prior
APOC run — they got SubjectConcept+Entity labels leaked onto the Place node.

Skips "Roman Republic" (subj_q17167) — legitimate seed domain node.
Idempotent — safe to re-run.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

SEED_SID = "subj_q17167"

# ── Step 0: Clean up nodes already merged by prior APOC run ──────────────────
# These Place nodes absorbed SubjectConcept+Entity labels + subject_id property.
CLEANUP_APOC_LEFTOVERS = """
MATCH (p:Place:SubjectConcept)
WHERE p.source IS NULL AND (p.subject_id IS NULL OR p.subject_id <> $seed_sid)
REMOVE p:SubjectConcept
REMOVE p.subject_id
RETURN p.label AS label
"""

# ── Step 1: Find SC nodes with a Place duplicate ─────────────────────────────
FIND_DUPES = """
MATCH (sc:SubjectConcept), (p:Place)
WHERE sc.source IS NULL
  AND sc.subject_id <> $seed_sid
  AND sc.pleiades_id IS NOT NULL
  AND sc.pleiades_id = p.pleiades_id
  AND sc <> p
RETURN sc.subject_id AS sid, sc.label AS label, sc.pleiades_id AS pid,
       elementId(sc) AS sc_eid, elementId(p) AS p_eid
ORDER BY sc.label
"""

# ── Step 2: Transfer all rels from SC to Place, then delete SC ────────────────
# Outgoing rels
TRANSFER_OUT = """
MATCH (sc:SubjectConcept {subject_id: $sid})-[r]->(target)
MATCH (p:Place {pleiades_id: $pid})
WHERE sc <> p AND NOT target = p
WITH p, target, type(r) AS rtype, properties(r) AS props, r
CALL apoc.create.relationship(p, rtype, props, target) YIELD rel
DELETE r
RETURN count(rel) AS moved
"""

# Incoming rels
TRANSFER_IN = """
MATCH (source)-[r]->(sc:SubjectConcept {subject_id: $sid})
MATCH (p:Place {pleiades_id: $pid})
WHERE sc <> p AND NOT source = p
WITH p, source, type(r) AS rtype, properties(r) AS props, r
CALL apoc.create.relationship(source, rtype, props, p) YIELD rel
DELETE r
RETURN count(rel) AS moved
"""

# Delete the now-orphaned SC node
DELETE_SC = """
MATCH (sc:SubjectConcept {subject_id: $sid})
DETACH DELETE sc
"""


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # Step 0: Clean up APOC leftovers from prior partial run
    with driver.session() as session:
        cleaned = session.run(CLEANUP_APOC_LEFTOVERS, {"seed_sid": SEED_SID}).data()
        if cleaned:
            print(f"Cleaned {len(cleaned)} APOC leftover nodes:")
            for c in cleaned:
                print(f"  - {c['label']} (removed SubjectConcept label)")
            print()

    # Step 1: Find duplicates
    with driver.session() as session:
        dupes = session.run(FIND_DUPES, {"seed_sid": SEED_SID}).data()
        print(f"Found {len(dupes)} SubjectConcept nodes with Place duplicates\n")

        # Step 2: Transfer rels and delete
        for i, d in enumerate(dupes):
            params = {"sid": d["sid"], "pid": d["pid"]}

            out = session.run(TRANSFER_OUT, params).single()["moved"]
            inc = session.run(TRANSFER_IN, params).single()["moved"]
            session.run(DELETE_SC, params).consume()

            print(f"  {i+1:2}. {d['label']:<30} {out} out + {inc} in rels transferred, node deleted")

    # Verify
    with driver.session() as session:
        remaining = session.run(
            "MATCH (sc:SubjectConcept) WHERE sc.source IS NULL RETURN count(sc) AS c"
        ).single()["c"]
        total_sc = session.run(
            "MATCH (sc:SubjectConcept) RETURN count(sc) AS c"
        ).single()["c"]
        print(f"\nRemaining source=NULL SubjectConcepts: {remaining} (expect 1 = Roman Republic)")
        print(f"Total SubjectConcept nodes: {total_sc} (expect 21 = 1 seed + 20 DI-written)")

    driver.close()


if __name__ == "__main__":
    main()
