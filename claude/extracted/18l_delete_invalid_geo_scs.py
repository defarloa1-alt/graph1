"""
18l_delete_invalid_geo_scs.py
Delete 3 invalid pre-CCS geo SubjectConcepts that are entity-type containers.

These have no LCC anchors, ccs_valid=null, and bucket Place nodes by
Pleiades feature type — not valid CCS subjects per ADR-020.

Labels deleted:
  - Settlements & Urban Places
  - Historical Places & Archaeological Sites
  - General Geographic Places

MEMBER_OF edges (~40k) are batched to avoid Aura transaction limits.
"""

import sys
from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

INVALID_SC_LABELS = [
    "Settlements & Urban Places",
    "Historical Places & Archaeological Sites",
    "General Geographic Places",
]

BATCH_SIZE = 5000


def run(driver):
    with driver.session() as session:
        # Step 1: batch-delete MEMBER_OF edges (largest rel type, ~40k)
        for label in INVALID_SC_LABELS:
            total = 0
            while True:
                result = session.run(
                    """
                    MATCH (n)-[r:MEMBER_OF]->(sc:SubjectConcept {label: $label})
                    WITH r LIMIT $batch
                    DELETE r
                    RETURN count(r) AS deleted
                    """,
                    label=label,
                    batch=BATCH_SIZE,
                )
                deleted = result.single()["deleted"]
                total += deleted
                print(f"  [{label}] MEMBER_OF deleted: {total}", end="\r")
                if deleted == 0:
                    break
            print(f"\n  [{label}] MEMBER_OF total removed: {total}")

        # Step 2: DETACH DELETE the SC nodes (remaining rels are small)
        result = session.run(
            """
            MATCH (sc:SubjectConcept)
            WHERE sc.label IN $labels
            DETACH DELETE sc
            RETURN count(sc) AS deleted
            """,
            labels=INVALID_SC_LABELS,
        )
        n = result.single()["deleted"]
        print(f"\nDeleted {n} SubjectConcept nodes (+ all remaining edges).")


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        print("Deleting invalid geo SubjectConcepts...")
        run(driver)
        print("Done.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
