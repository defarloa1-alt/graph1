#!/usr/bin/env python3
"""
Classify the 261 provisional relationship types into:
  A) system  — graph-internal infrastructure edges (SYS_ machinery, facet routing, pipeline)
  B) noise   — additional Wikidata metadata noise (delete edges + catalog nodes)
  C) active  — valid domain predicates (promote to active)

Updates the master CSV in place.
Also deletes Bucket B edges from the graph.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from neo4j import GraphDatabase

CSV_PATH = ROOT / "Relationships" / "relationship_types_registry_master.csv"

# ── Bucket A: graph-internal SYS/INFRA edges ─────────────────────────────────
# These connect SYS_ nodes or are pipeline infrastructure — not domain predicates.
BUCKET_A_SYS = {
    "ALIGNED_WITH_GEO_BACKBONE",
    "ASSESSED_FOR_FACET", "ASSIGNED_TO_FACET", "COVERS_FACET", "FACET_OF",
    "HAS_FACET_POLICY", "HAS_FACET_ROUTER", "HAS_PRIMARY_FACET", "HAS_SECONDARY_FACET",
    "RELEVANT_TO_FACET", "MAY_TAG",
    "BIO_CANDIDATE_REL",
    "CAN_TRANSITION_TO", "HAS_CLAIM_STATUS",
    "CONSTRAINED_BY", "IMPOSES_CONSTRAINT_ON",
    "GUARDS_TASKTYPE", "HAS_TASKTYPE",
    "HAS_ADR", "HAS_AGENT", "HAS_AGENT_TYPE", "HAS_AUTHORITY_TIER",
    "HAS_BRIDGE_PATTERN", "HAS_CHILD_TYPE", "HAS_CLASSIFICATION_TIER",
    "HAS_CONFIDENCE_MODIFIER", "HAS_CONFIDENCE_TIER", "HAS_CURATION_DECISION",
    "HAS_DECISION_TABLE", "HAS_DISCIPLINE_REGISTRY",
    "HAS_DOMAIN", "HAS_ENTITY_ROOT", "HAS_ENTITY_TYPE",
    "HAS_FALLACY", "HAS_FEDERATION", "HAS_FRAMEWORK",
    "HAS_GEO_SEMANTIC_TYPE", "HAS_GOAL", "HAS_LIST",
    "HAS_ONBOARDING", "HAS_OUTPUT_CONTRACT", "HAS_PARADIGM_CLASS",
    "HAS_PATTERN", "HAS_POLICY", "HAS_PRINCIPLE", "HAS_QUERY_PATTERN",
    "HAS_REJECTION_REASON", "HAS_ROW", "HAS_SCHEMA",
    "HAS_STEP", "HAS_SUBJECT_CONCEPT_ROOT", "HAS_SUBJECT_REGISTRY",
    "HAS_THRESHOLD", "HAS_TIER", "HAS_TRACE", "HAS_VALIDATION_RULE", "HAS_WORKFLOW",
    "INSTANCE_OF_TYPE", "IS_THE_STUDY_OF",
    "NEXT_STEP", "POSITIONED_AS",
    "SUBSCOPE_OF",
    "USES", "USES_MECHANISM", "USES_OUTPUT_CONTRACT", "USES_THRESHOLD", "USES_TYPE",
    "VALID_IN_PERIOD", "VALID_IN_PLACE",
    "HAS_EFFECT",
}

# ── Bucket B: additional Wikidata noise — delete edges + catalog nodes ────────
# Modern state symbols, Wikidata meta-links, census/admin data irrelevant to
# Roman Republic domain.
BUCKET_B_NOISE = {
    "ANTHEM",             # modern state symbol
    "COAT_OF_ARMS",       # modern state symbol
    "FLAG",               # modern state symbol
    "DEMOGRAPHICS_OF_TOPIC",  # Wikidata meta-link
    "ECONOMY_OF_TOPIC",   # Wikidata meta-link
    "GEOGRAPHY_OF_TOPIC", # Wikidata meta-link
    "HISTORY_OF_TOPIC",   # Wikidata meta-link to "History of X" article
    "IS_A_LIST_OF",       # Wikidata list metadata
    "LANGUAGE_REGULATORY_BODY",  # modern institution
    "MEANS_OF_LOCOMOTION",       # irrelevant
    "MOST_POPULOUS_URBAN_AREA",  # modern census
    "SHAPE",              # geometric property, not scholarly
    "WORLD_HERITAGE_CRITERIA",   # modern UNESCO admin
}


def main():
    # ── Pass 1: delete Bucket B edges + catalog nodes ─────────────────────────
    print(f"Pass B: deleting {len(BUCKET_B_NOISE)} additional noise types...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    total_edges = 0
    total_nodes = 0
    with driver.session() as s:
        for rt in sorted(BUCKET_B_NOISE):
            r = s.run("MATCH ()-[r]->() WHERE type(r) = $rt RETURN count(r) AS cnt", rt=rt)
            cnt = r.single()["cnt"]
            if cnt:
                s.run("MATCH ()-[r]->() WHERE type(r) = $rt DELETE r", rt=rt)
                total_edges += cnt
                print(f"  Deleted {cnt:>6} {rt} edges")
            r2 = s.run(
                "MATCH (n:SYS_RelationshipType) WHERE n.rel_type = $rt OR n.name = $rt "
                "DETACH DELETE n RETURN count(n) AS cnt", rt=rt
            )
            total_nodes += (r2.single() or {}).get("cnt", 0)
    driver.close()
    print(f"Pass B complete: {total_edges} edges deleted, {total_nodes} catalog nodes removed\n")

    # ── Pass 2: update CSV statuses ───────────────────────────────────────────
    print("Pass CSV: updating statuses (provisional -> system / active / noise)...")
    rows = []
    fieldnames = None
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        for row in reader:
            # Drop any extra None keys from malformed rows
            clean = {k: v for k, v in row.items() if k is not None and k in fieldnames}
            rows.append(clean)

    counts = {"system": 0, "active": 0, "noise": 0, "unchanged": 0}
    for row in rows:
        if row.get("status") != "provisional":
            continue
        rt = row["relationship_type"]
        if rt in BUCKET_A_SYS:
            row["status"] = "system"
            row["lifecycle_status"] = "implemented"
            row["category"] = "System"
            row["note"] = "graph-internal infrastructure edge"
            counts["system"] += 1
        elif rt in BUCKET_B_NOISE:
            row["status"] = "noise"
            row["lifecycle_status"] = "deprecated"
            row["note"] = "Wikidata noise deleted 2026-03-10"
            counts["noise"] += 1
        else:
            # Bucket C — valid domain predicate
            row["status"] = "active"
            row["lifecycle_status"] = "implemented"
            counts["active"] += 1

    # Write to temp file first, then rename (safe write)
    tmp = CSV_PATH.with_suffix(".tmp")
    with open(tmp, encoding="utf-8", newline="", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(CSV_PATH)

    print(f"  system: {counts['system']}")
    print(f"  active: {counts['active']}")
    print(f"  noise:  {counts['noise']}")
    print("\nDone.")


if __name__ == "__main__":
    main()
