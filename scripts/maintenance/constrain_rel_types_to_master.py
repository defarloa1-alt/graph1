#!/usr/bin/env python3
"""
Constrain SYS_RelationshipType nodes to the master CSV list.

Deletes any SYS_RelationshipType node whose rel_type is not in
Relationships/relationship_types_registry_master.csv.

Preserves infra/temporal types that are intentionally graph-only
(these are structural edges, not domain predicates).
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

CSV_PATH = ROOT / "Relationships" / "relationship_types_registry_master.csv"

# Infra/structural types intentionally kept even if absent from CSV.
# Includes: temporal wiring, taxonomy edges, federation edges, and
# graph-internal SYS_ machinery edges (status=system in master CSV).
INFRA_KEEP = {
    # Temporal
    "ACTIVE_IN_YEAR", "BORN_IN_YEAR", "DIED_IN_YEAR", "FOLLOWED_BY",
    "STARTS_IN_YEAR", "ENDS_IN_YEAR", "OCCURRED_IN_YEAR",
    "LIVED_DURING", "DURING_PERIOD",
    # Taxonomy / scoping
    "NARROWER_THAN", "BROADER_THAN", "RELATED_TO",
    "DISCIPLINE_SUBCLASS_OF", "DISCIPLINE_BROADER_THAN",
    "DISCIPLINE_PART_OF", "DISCIPLINE_HAS_PART",
    "IN_PERIOD", "MEMBER_OF", "SCOPED_TO", "HAS_FACET",
    # Federation / authority
    "ROUTES_TO", "FEDERATED_BY", "HAS_OA_SOURCE",
    "HAS_LCSH", "HAS_FAST", "HAS_GND", "HAS_BNF", "HAS_BNCF",
    "HAS_NDL", "HAS_UNESCO", "HAS_GETTY_AAT", "HAS_OPENALEX",
    "POSITION_HELD", "BORN_IN", "DIED_IN",
    # SYS_ graph-internal machinery (status=system in master CSV)
    "ALIGNED_WITH_GEO_BACKBONE", "ASSESSED_FOR_FACET", "ASSIGNED_TO_FACET",
    "BIO_CANDIDATE_REL", "CAN_TRANSITION_TO", "CONSTRAINED_BY", "COVERS_FACET",
    "FACET_OF", "GUARDS_TASKTYPE",
    "HAS_ADR", "HAS_AGENT", "HAS_AGENT_TYPE", "HAS_AUTHORITY_TIER",
    "HAS_BRIDGE_PATTERN", "HAS_CHILD_TYPE", "HAS_CLAIM_STATUS",
    "HAS_CLASSIFICATION_TIER", "HAS_CONFIDENCE_MODIFIER", "HAS_CONFIDENCE_TIER",
    "HAS_CURATION_DECISION", "HAS_DECISION_TABLE", "HAS_DISCIPLINE_REGISTRY",
    "HAS_DOMAIN", "HAS_EFFECT", "HAS_ENTITY_ROOT", "HAS_ENTITY_TYPE",
    "HAS_FACET_POLICY", "HAS_FACET_ROUTER", "HAS_FALLACY", "HAS_FEDERATION",
    "HAS_FRAMEWORK", "HAS_GEO_SEMANTIC_TYPE", "HAS_GOAL", "HAS_LIST",
    "HAS_ONBOARDING", "HAS_OUTPUT_CONTRACT", "HAS_PARADIGM_CLASS",
    "HAS_PATTERN", "HAS_POLICY", "HAS_PRIMARY_FACET", "HAS_PRINCIPLE",
    "HAS_QUERY_PATTERN", "HAS_REJECTION_REASON", "HAS_ROW", "HAS_SCHEMA",
    "HAS_SECONDARY_FACET", "HAS_STEP", "HAS_SUBJECT_CONCEPT_ROOT",
    "HAS_SUBJECT_REGISTRY", "HAS_TASKTYPE", "HAS_THRESHOLD", "HAS_TIER",
    "HAS_TRACE", "HAS_VALIDATION_RULE", "HAS_WORKFLOW",
    "IMPOSES_CONSTRAINT_ON", "INSTANCE_OF_TYPE", "IS_THE_STUDY_OF",
    "MAY_TAG", "NEXT_STEP", "POSITIONED_AS", "RELEVANT_TO_FACET",
    "SUBSCOPE_OF", "USES", "USES_MECHANISM", "USES_OUTPUT_CONTRACT",
    "USES_THRESHOLD", "USES_TYPE", "VALID_IN_PERIOD", "VALID_IN_PLACE",
}


def load_master_csv() -> set[str]:
    types = set()
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rt = row.get("relationship_type", "").strip()
            if rt:
                types.add(rt)
    return types


def main():
    master = load_master_csv()
    print(f"Master CSV: {len(master)} relationship types")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        # Get all graph nodes
        result = session.run(
            "MATCH (n:SYS_RelationshipType) RETURN n.rel_type AS rt, n.name AS nm, elementId(n) AS eid"
        )
        graph_nodes = [(r["rt"], r["nm"], r["eid"]) for r in result]
    print(f"Graph nodes: {len(graph_nodes)}")

    to_delete = []
    keep = []
    for rt, nm, eid in graph_nodes:
        canonical = rt or nm  # use rel_type, fall back to name
        if canonical in master or canonical in INFRA_KEEP:
            keep.append(canonical)
        else:
            to_delete.append((canonical, eid))

    print(f"\nKeep: {len(keep)}")
    print(f"Delete: {len(to_delete)}")

    if to_delete:
        print("\nSample deletions (first 20):")
        for rt, _ in to_delete[:20]:
            print(f"  - {rt}")
        if len(to_delete) > 20:
            print(f"  ... and {len(to_delete) - 20} more")

        # Only delete nodes with zero live edges in the graph
        print("\nChecking for live edges (safe-delete only)...")
        safe_to_delete = []
        with driver.session() as session:
            for canonical, eid in to_delete:
                if not canonical:
                    safe_to_delete.append((canonical, eid))
                    continue
                # Check if this rel_type has any actual edges in the graph
                r = session.run(
                    "MATCH ()-[r]->() WHERE type(r) = $rt RETURN count(r) AS cnt LIMIT 1",
                    rt=canonical
                )
                rec = r.single()
                if rec and rec["cnt"] > 0:
                    print(f"  LIVE {canonical} ({rec['cnt']} edges) — keeping")
                else:
                    safe_to_delete.append((canonical, eid))

        print(f"\nSafe to delete (no live edges): {len(safe_to_delete)}")
        print(f"Skipped (live edges exist): {len(to_delete) - len(safe_to_delete)}")

        with driver.session() as session:
            eids = [eid for _, eid in safe_to_delete]
            result = session.run(
                "MATCH (n:SYS_RelationshipType) WHERE elementId(n) IN $eids DETACH DELETE n RETURN count(n) AS deleted",
                eids=eids
            )
            rec = result.single()
            print(f"Deleted {rec['deleted']} nodes.")

    driver.close()
    print("Done.")


if __name__ == "__main__":
    main()
