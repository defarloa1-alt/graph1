#!/usr/bin/env python3
"""
Two-pass relationship type cleanup:
  Pass 1 — Delete Wikimedia/technical noise edges + their SYS_RelationshipType catalog nodes.
  Pass 2 — Add all remaining live-but-unlisted types to master CSV as 'provisional'.

Run: python scripts/maintenance/clean_wikidata_noise_edges.py
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

CSV_PATH = ROOT / "Relationships" / "relationship_types_registry_master.csv"

# Wikimedia meta, technical country/language admin metadata — not domain data.
# These came in via Wikidata bulk harvest and carry no scholarly value for
# a Roman Republic knowledge graph.
NOISE = {
    # Wikimedia infrastructure
    "MAINTAINED_BY_WIKIPROJECT", "ON_FOCUS_LIST_OF_WIKIMEDIA_PROJECT",
    "TOPICS_MAIN_WIKIMEDIA_PORTAL", "WIKIMEDIA_PORTALS_MAIN_TOPIC",
    "WIKIMEDIA_OUTLINE", "TEMPLATE_HAS_TOPIC", "TOPIC_HAS_TEMPLATE",
    "TOPICS_MAIN_CATEGORY", "CATEGORYS_MAIN_TOPIC", "CATEGORY_COMBINES_TOPICS",
    "CATEGORY_CONTAINS", "CATEGORY_FOR_HONORARY_CITIZENS_OF_ENTITY",
    "CATEGORY_FOR_PEOPLE_BORN_HERE", "CATEGORY_FOR_PEOPLE_BURIED_HERE",
    "CATEGORY_FOR_PEOPLE_WHO_DIED_HERE",
    # Copyright / IP metadata
    "COPYRIGHT_STATUS", "COPYRIGHT_STATUS_AS_A_CREATOR", "PERMANENT_DUPLICATED_ITEM",
    # Modern technical country metadata irrelevant to ancient Rome
    "DRIVING_SIDE", "ELECTRICAL_PLUG_TYPE", "RAILWAY_TRAFFIC_SIDE",
    "EMERGENCY_PHONE_NUMBER", "KPPEN_CLIMATE_CLASSIFICATION",
    "TOPLEVEL_INTERNET_DOMAIN", "TWINNED_ADMINISTRATIVE_BODY",
    # Financial noise
    "CURRENCY_SYMBOL_DESCRIPTION", "CENTRAL_BANKISSUER",
    # Media / entertainment
    "BROADCAST_BY", "FILMING_LOCATION",
    # Biology noise
    "TAXON_KNOWN_BY_THIS_COMMON_NAME", "COMMON_ORGANISM",
    "NATURAL_PRODUCT_OF_TAXON", "PRODUCED_SOUND",
    # Wikidata logic/dedup
    "DISJOINT_UNION_OF", "IS_METACLASS_FOR", "MODEL_ITEM",
    "SAID_TO_BE_THE_SAME_AS", "OPEN_DATA_PORTAL",
    # Academic admin
    "ACADEMIC_MAJOR",
}

INFRA = {
    # Temporal
    "ACTIVE_IN_YEAR", "BORN_IN_YEAR", "DIED_IN_YEAR", "FOLLOWED_BY",
    "STARTS_IN_YEAR", "ENDS_IN_YEAR", "OCCURRED_IN_YEAR", "LIVED_DURING", "DURING_PERIOD",
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


def load_master() -> set[str]:
    types = set()
    with open(CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rt = row.get("relationship_type", "").strip()
            if rt:
                types.add(rt)
    return types


def main():
    master = load_master()
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    # ── Pass 1: delete noise edges + catalog nodes ───────────────────────────
    print(f"Pass 1: deleting {len(NOISE)} noise relationship types...")
    total_edges = 0
    total_nodes = 0
    with driver.session() as s:
        for rt in sorted(NOISE):
            # Count live edges
            r = s.run("MATCH ()-[r]->() WHERE type(r) = $rt RETURN count(r) AS cnt", rt=rt)
            cnt = r.single()["cnt"]
            if cnt:
                s.run("MATCH ()-[r]->() WHERE type(r) = $rt DELETE r", rt=rt)
                total_edges += cnt
                print(f"  Deleted {cnt:>6} {rt} edges")
            # Delete SYS_RelationshipType catalog node
            r2 = s.run(
                "MATCH (n:SYS_RelationshipType) WHERE n.rel_type = $rt OR n.name = $rt "
                "DETACH DELETE n RETURN count(n) AS cnt", rt=rt
            )
            total_nodes += (r2.single() or {}).get("cnt", 0)

    print(f"\nPass 1 complete: {total_edges} edges deleted, {total_nodes} catalog nodes removed")

    # ── Pass 2: add live-but-unlisted types to master CSV as provisional ─────
    with driver.session() as s:
        rows = list(s.run(
            "MATCH (n:SYS_RelationshipType) WHERE n.rel_type IS NOT NULL RETURN n.rel_type AS rt"
        ))
    graph_types = {r["rt"] for r in rows}
    unlisted = graph_types - master - INFRA - NOISE

    print(f"\nPass 2: {len(unlisted)} live types not in master CSV -> adding as provisional")

    fieldnames = None
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

    added = 0
    with open(CSV_PATH, encoding="utf-8", newline="", mode="a") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for rt in sorted(unlisted):
            row = {k: "" for k in fieldnames}
            row["relationship_type"] = rt
            row["status"] = "provisional"
            row["lifecycle_status"] = "under_review"
            row["note"] = "auto-added from live graph 2026-03-10"
            row["source"] = "graph_audit"
            row["version"] = "1.0"
            writer.writerow(row)
            added += 1

    print(f"Added {added} provisional entries to master CSV")
    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
