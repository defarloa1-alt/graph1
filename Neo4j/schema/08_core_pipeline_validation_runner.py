"""
Core pipeline schema validator (Phase 1).

Why this exists:
- Some Neo4j builds only allow SHOW as top-level commands, which prevents
  pure-Cypher PASS/FAIL checks using WITH/CALL composition.
- This script performs the same checks client-side via the Neo4j Python driver.
"""

from __future__ import annotations

import os
import sys
from typing import Iterable

from neo4j import GraphDatabase


EXPECTED_CONSTRAINTS = [
    "human_entity_id_unique",
    "human_qid_unique",
    "human_viaf_id_unique",
    "human_has_name",
    "human_has_qid",
    "human_has_entity_type",
    "place_entity_id_unique",
    "place_qid_unique",
    "place_pleiades_id_unique",
    "place_tgn_id_unique",
    "place_has_label",
    "place_has_qid",
    "place_has_entity_type",
    "event_entity_id_unique",
    "event_qid_unique",
    "event_has_label",
    "event_has_start_date",
    "event_has_qid",
    "event_has_entity_type",
    "period_entity_id_unique",
    "period_qid_unique",
    "period_has_label",
    "period_has_start",
    "period_has_end",
    "period_has_entity_type",
    "subject_concept_id_unique",
    "subject_concept_has_subject_id",
    "subject_concept_has_label",
    "subject_concept_has_facet",
    "claim_id_unique",
    "claim_cipher_unique",
    "claim_has_text",
    "claim_has_label",
    "claim_has_confidence",
    "claim_has_cipher",
    "claim_has_claim_type",
    "claim_has_source_agent",
    "claim_has_timestamp",
    "claim_has_status",
    "retrieval_context_id_unique",
    "retrieval_context_has_id",
    "agent_id_unique",
    "agent_has_id",
    "agent_has_label",
    "agent_has_agent_type",
    "analysis_run_id_unique",
    "analysis_run_has_id",
    "analysis_run_has_pipeline_version",
    "facet_assessment_id_unique",
    "facet_assessment_has_id",
    "facet_assessment_has_score",
    "facet_assessment_has_status",
]

EXPECTED_INDEXES = [
    "human_birth_date_index",
    "human_death_date_index",
    "place_label_index",
    "event_label_index",
    "event_type_index",
    "event_start_date_index",
    "event_end_date_index",
    "event_start_date_min_index",
    "event_start_date_max_index",
    "event_end_date_min_index",
    "event_end_date_max_index",
    "event_temporal_bbox_index",
    "period_label_index",
    "period_facet_index",
    "period_start_index",
    "period_end_index",
    "period_start_date_min_index",
    "period_start_date_max_index",
    "period_end_date_min_index",
    "period_end_date_max_index",
    "period_temporal_bbox_minmax_index",
    "subject_label_index",
    "subject_facet_index",
    "subject_tier_index",
    "claim_status_index",
    "claim_label_index",
    "claim_confidence_index",
    "claim_timestamp_index",
    "claim_source_agent_index",
    "retrieval_context_agent_index",
    "retrieval_context_timestamp_index",
    "agent_type_index",
    "analysis_run_version_index",
    "analysis_run_status_index",
    "facet_assessment_score_index",
    "facet_assessment_status_index",
]


def missing(expected: Iterable[str], actual: Iterable[str]) -> list[str]:
    actual_set = set(actual)
    return [x for x in expected if x not in actual_set]


def main() -> int:
    uri = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "Chrystallum")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            constraints = session.run(
                "SHOW CONSTRAINTS YIELD name RETURN name ORDER BY name"
            ).value("name")

            idx_rows = session.run(
                """
                SHOW INDEXES YIELD name, type, state, owningConstraint
                WHERE type <> 'LOOKUP' AND (owningConstraint IS NULL OR owningConstraint = '')
                RETURN name, state
                ORDER BY name
                """
            ).data()

        actual_indexes = [r["name"] for r in idx_rows]
        non_online = [r["name"] for r in idx_rows if r["state"] != "ONLINE"]

        missing_constraints = missing(EXPECTED_CONSTRAINTS, constraints)
        missing_indexes = missing(EXPECTED_INDEXES, actual_indexes)

        print("=== Core Pipeline Schema Validation ===")
        print(f"expected_constraints: {len(EXPECTED_CONSTRAINTS)}")
        print(f"actual_constraints:   {len(constraints)}")
        print(f"missing_constraints:  {len(missing_constraints)}")
        if missing_constraints:
            print("  " + ", ".join(missing_constraints))

        print(f"expected_indexes:     {len(EXPECTED_INDEXES)}")
        print(f"actual_indexes:       {len(actual_indexes)}")
        print(f"missing_indexes:      {len(missing_indexes)}")
        if missing_indexes:
            print("  " + ", ".join(missing_indexes))

        print(f"non_online_indexes:   {len(non_online)}")
        if non_online:
            print("  " + ", ".join(non_online))

        ok = not missing_constraints and not missing_indexes and not non_online
        print(f"status: {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    finally:
        driver.close()


if __name__ == "__main__":
    sys.exit(main())
