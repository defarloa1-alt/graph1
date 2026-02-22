"""
Run a parameterized Neo4j claim pipeline for period/event/place QIDs.

Example:
  python Neo4j/schema/run_qid_pipeline.py ^
    --period-qid Q17167 --period-label "Roman Republic" --period-start -0510 --period-end -0027 ^
    --event-qid Q193304 --event-label "Battle of Actium" --event-date -0031-09-02 ^
    --place-qid Q41747 --place-label Actium --modern-country Greece --event-type battle
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from scripts.tools.claim_confidence_policy_engine import (  # noqa: E402
    policy_hash,
    clamp_confidence,
    evaluate_claim_confidence_policy,
    load_policy,
    map_claim_type_to_epistemic,
)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "unknown"


def qid_token(qid: str) -> str:
    t = re.sub(r"[^a-z0-9]+", "", qid.lower())
    if not t.startswith("q"):
        return f"q{t}"
    return t


def parse_year(value: str) -> int:
    return int(value)


def format_year(year: int) -> str:
    sign = "-" if year < 0 else ""
    return f"{sign}{abs(year):04d}"


def signed_year_token(value: str) -> str:
    year = parse_year(value)
    if year < 0:
        return f"neg{abs(year):04d}"
    return f"pos{year:04d}"


def date_token(date_str: str) -> str:
    m = re.match(r"^(-?\d{4})-(\d{2})-(\d{2})$", date_str)
    if not m:
        raise ValueError(f"Invalid --event-date: {date_str}; expected YYYY-MM-DD with optional leading '-'")
    year = m.group(1)
    month = m.group(2)
    day = m.group(3)
    return f"{signed_year_token(year)}_{month}_{day}"


def parse_event_year(date_str: str) -> int:
    m = re.match(r"^(-?\d{4})-\d{2}-\d{2}$", date_str)
    if not m:
        raise ValueError(f"Invalid --event-date: {date_str}; expected YYYY-MM-DD with optional leading '-'")
    return int(m.group(1))


def era_year_text(year: int) -> str:
    if year < 0:
        return f"{abs(year)} BCE"
    if year == 0:
        return "0"
    return f"{year} CE"


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_query(session: Any, name: str, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    print(f"Running: {name}")
    result = session.run(query, params)
    rows = result.data()
    if rows:
        print(f"Returned {len(rows)} row(s)")
        for row in rows:
            print(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"))
    parser.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("NEO4J_PASSWORD", "Chrystallum"))

    parser.add_argument("--period-qid", required=True)
    parser.add_argument("--period-label", required=True)
    parser.add_argument("--period-start", required=True, help="Example: -0510")
    parser.add_argument("--period-end", required=True, help="Example: -0027")

    parser.add_argument("--event-qid", required=True)
    parser.add_argument("--event-label", required=True)
    parser.add_argument("--event-date", required=True, help="Example: -0031-09-02")
    parser.add_argument("--event-type", default="event")

    parser.add_argument("--place-qid", required=True)
    parser.add_argument("--place-label", required=True)
    parser.add_argument("--place-type", default="place")
    parser.add_argument("--modern-country", default="")

    parser.add_argument("--facet", default="political")
    parser.add_argument("--source", default="wikidata")
    parser.add_argument("--pipeline-version", default="v1.0")
    parser.add_argument("--agent-version", default="v1.0")
    parser.add_argument("--policy-path", default="JSON/policy/claim_confidence_policy_v1.json")

    parser.add_argument("--factual-claim-type", default="factual")
    parser.add_argument("--factual-proposed-confidence", type=float, default=0.92)
    parser.add_argument("--factual-primary-count", type=int, default=1)
    parser.add_argument("--factual-secondary-count", type=int, default=1)
    parser.add_argument("--factual-tertiary-count", type=int, default=0)
    parser.add_argument("--factual-has-conflicts", action="store_true")
    parser.add_argument("--factual-federation-depth", type=int, choices=[1, 2, 3], default=2)

    parser.add_argument("--temporal-claim-type", default="temporal")
    parser.add_argument("--temporal-proposed-confidence", type=float, default=0.94)
    parser.add_argument("--temporal-primary-count", type=int, default=1)
    parser.add_argument("--temporal-secondary-count", type=int, default=1)
    parser.add_argument("--temporal-tertiary-count", type=int, default=0)
    parser.add_argument("--temporal-has-conflicts", action="store_true")
    parser.add_argument("--temporal-federation-depth", type=int, choices=[1, 2, 3], default=2)

    parser.add_argument("--reset-entities", action="store_true")
    parser.add_argument("--legacy-roman-clean", action="store_true")
    args = parser.parse_args()

    policy_path = (REPO_ROOT / args.policy_path).resolve()
    policy = load_policy(policy_path)
    policy_sha256 = policy_hash(policy)

    factual_epistemic_type = map_claim_type_to_epistemic(args.factual_claim_type)
    temporal_epistemic_type = map_claim_type_to_epistemic(args.temporal_claim_type)

    factual_policy = evaluate_claim_confidence_policy(
        policy,
        primary_count=args.factual_primary_count,
        secondary_count=args.factual_secondary_count,
        tertiary_count=args.factual_tertiary_count,
        has_conflicts=args.factual_has_conflicts,
        epistemic_type=factual_epistemic_type,
        federation_depth=args.factual_federation_depth,
    )
    temporal_policy = evaluate_claim_confidence_policy(
        policy,
        primary_count=args.temporal_primary_count,
        secondary_count=args.temporal_secondary_count,
        tertiary_count=args.temporal_tertiary_count,
        has_conflicts=args.temporal_has_conflicts,
        epistemic_type=temporal_epistemic_type,
        federation_depth=args.temporal_federation_depth,
    )

    factual_confidence = clamp_confidence(
        args.factual_proposed_confidence,
        factual_policy["min_confidence"],
        factual_policy["max_confidence"],
    )
    temporal_confidence = clamp_confidence(
        args.temporal_proposed_confidence,
        temporal_policy["min_confidence"],
        temporal_policy["max_confidence"],
    )

    factual_gate_status = (
        "review_required"
        if factual_policy["require_debate_bridge"] or factual_policy["require_expert_review"]
        else "auto_promote_eligible"
    )
    temporal_gate_status = (
        "review_required"
        if temporal_policy["require_debate_bridge"] or temporal_policy["require_expert_review"]
        else "auto_promote_eligible"
    )

    period_start_year = parse_year(args.period_start)
    period_end_year = parse_year(args.period_end)
    event_year = parse_event_year(args.event_date)

    period_start_iso = format_year(period_start_year)
    period_end_iso = format_year(period_end_year)

    period_t = qid_token(args.period_qid)
    event_t = qid_token(args.event_qid)
    place_t = qid_token(args.place_qid)

    period_slug = slugify(args.period_label)
    event_slug = slugify(args.event_label)
    place_slug = slugify(args.place_label)

    subject_id = f"subj_{period_t}_{period_slug}"
    agent_id = f"agent_{period_t}_{period_slug}_v1"

    period_entity_id = f"prd_{period_slug}_{period_t}"
    event_entity_id = f"evt_{event_slug}_{event_t}"
    place_entity_id = f"plc_{place_slug}_{place_t}"

    facet_key = slugify(args.facet)
    facet_label = args.facet.strip().title() if args.facet.strip() else "Political"
    factual_facet_id = f"facet_{facet_key}"

    factual_claim_id = f"claim_{period_t}_end_date_{signed_year_token(args.period_end)}"
    temporal_claim_id = f"claim_{event_t}_occurred_during_{period_t}_{date_token(args.event_date)}"

    factual_retrieval_id = f"retr_{period_t}_{args.source}_end_date_{signed_year_token(args.period_end)}"
    temporal_retrieval_id = f"retr_{event_t}_{args.source}_occurred_during_{period_t}"

    factual_run_id = f"run_{period_t}_end_date_{signed_year_token(args.period_end)}"
    temporal_run_id = f"run_{event_t}_occurred_during_{period_t}"

    temporal_facet_key = "military"
    temporal_facet_label = "Military"
    temporal_facet_id = f"facet_{temporal_facet_key}"

    factual_assessment_id = f"fa_{period_t}_{facet_key}_end_date_{signed_year_token(args.period_end)}"
    temporal_assessment_id = f"fa_{event_t}_{temporal_facet_key}_occurred_during_{period_t}"

    factual_label = f"{args.period_label} Ended in {era_year_text(period_end_year)}"
    factual_text = f"The {args.period_label} ended in {era_year_text(period_end_year)}."

    temporal_label = f"{args.event_label} Occurred During {args.period_label}"
    temporal_text = f"The {args.event_label} occurred during the {args.period_label} in {era_year_text(event_year)}."

    factual_claim_cipher = hash_text(f"{factual_claim_id}|{factual_text}|{args.source}")
    temporal_claim_cipher = hash_text(f"{temporal_claim_id}|{temporal_text}|{args.source}")

    base_params = {
        "subject_id": subject_id,
        "agent_id": agent_id,
        "period_qid": args.period_qid,
        "period_label": args.period_label,
        "period_entity_id": period_entity_id,
        "period_start": period_start_iso,
        "period_end": period_end_iso,
        "period_start_date_min": f"{period_start_iso}-01-01",
        "period_start_date_max": f"{period_start_iso}-12-31",
        "period_end_date_min": f"{period_end_iso}-01-01",
        "period_end_date_max": f"{period_end_iso}-12-31",
        "event_qid": args.event_qid,
        "event_label": args.event_label,
        "event_entity_id": event_entity_id,
        "event_type": args.event_type,
        "event_date": args.event_date,
        "place_qid": args.place_qid,
        "place_label": args.place_label,
        "place_entity_id": place_entity_id,
        "place_type": args.place_type,
        "modern_country": args.modern_country,
        "facet_key": facet_key,
        "facet_label": facet_label,
        "factual_facet_id": factual_facet_id,
        "source": args.source,
        "pipeline_version": args.pipeline_version,
        "agent_version": args.agent_version,
        "factual_claim_id": factual_claim_id,
        "factual_claim_label": factual_label,
        "factual_claim_text": factual_text,
        "factual_claim_cipher": factual_claim_cipher,
        "factual_claim_type": args.factual_claim_type,
        "factual_epistemic_type": factual_epistemic_type,
        "factual_confidence": factual_confidence,
        "factual_source_strength": factual_policy["source_strength"],
        "factual_conflict_code": factual_policy["conflict_code"],
        "factual_federation_depth": args.factual_federation_depth,
        "factual_source_row_id": factual_policy["row_ids"]["source_strength"],
        "factual_conflict_row_id": factual_policy["row_ids"]["conflict_code"],
        "factual_profile_row_id": factual_policy["row_ids"]["claim_confidence_profile"],
        "factual_min_confidence": factual_policy["min_confidence"],
        "factual_max_confidence": factual_policy["max_confidence"],
        "factual_require_debate_bridge": factual_policy["require_debate_bridge"],
        "factual_require_expert_review": factual_policy["require_expert_review"],
        "factual_gate_status": factual_gate_status,
        "temporal_claim_id": temporal_claim_id,
        "temporal_claim_label": temporal_label,
        "temporal_claim_text": temporal_text,
        "temporal_claim_cipher": temporal_claim_cipher,
        "temporal_claim_type": args.temporal_claim_type,
        "temporal_epistemic_type": temporal_epistemic_type,
        "temporal_confidence": temporal_confidence,
        "temporal_source_strength": temporal_policy["source_strength"],
        "temporal_conflict_code": temporal_policy["conflict_code"],
        "temporal_federation_depth": args.temporal_federation_depth,
        "temporal_source_row_id": temporal_policy["row_ids"]["source_strength"],
        "temporal_conflict_row_id": temporal_policy["row_ids"]["conflict_code"],
        "temporal_profile_row_id": temporal_policy["row_ids"]["claim_confidence_profile"],
        "temporal_min_confidence": temporal_policy["min_confidence"],
        "temporal_max_confidence": temporal_policy["max_confidence"],
        "temporal_require_debate_bridge": temporal_policy["require_debate_bridge"],
        "temporal_require_expert_review": temporal_policy["require_expert_review"],
        "temporal_gate_status": temporal_gate_status,
        "policy_id": policy.get("policy_id", "unknown_policy"),
        "policy_hash": policy_sha256,
        "factual_retrieval_id": factual_retrieval_id,
        "temporal_retrieval_id": temporal_retrieval_id,
        "factual_run_id": factual_run_id,
        "temporal_run_id": temporal_run_id,
        "factual_assessment_id": factual_assessment_id,
        "temporal_assessment_id": temporal_assessment_id,
        "temporal_facet_id": temporal_facet_id,
        "temporal_facet_label": temporal_facet_label,
        "period_start_year": period_start_year,
        "period_end_year": period_end_year,
        "event_year": event_year,
        "years": [period_start_year, period_end_year, event_year],
    }

    print(
        "Policy decisions:",
        {
            "policy_id": base_params["policy_id"],
            "policy_hash": base_params["policy_hash"],
            "factual": {
                "row": base_params["factual_profile_row_id"],
                "confidence": base_params["factual_confidence"],
                "range": [base_params["factual_min_confidence"], base_params["factual_max_confidence"]],
                "gate_status": base_params["factual_gate_status"],
            },
            "temporal": {
                "row": base_params["temporal_profile_row_id"],
                "confidence": base_params["temporal_confidence"],
                "range": [base_params["temporal_min_confidence"], base_params["temporal_max_confidence"]],
                "gate_status": base_params["temporal_gate_status"],
            },
        },
    )

    claim_ids = [factual_claim_id, temporal_claim_id]
    retrieval_ids = [factual_retrieval_id, temporal_retrieval_id]
    run_ids = [factual_run_id, temporal_run_id]
    assessment_ids = [factual_assessment_id, temporal_assessment_id]
    agent_ids = [agent_id]
    subject_ids = [subject_id]

    if args.legacy_roman_clean:
        claim_ids += [
            "claim_roman_republic_end_27bce_001",
            "claim_actium_in_republic_31bce_001",
            "claim_q17167_end_date_neg0027",
            "claim_q193304_occurred_during_q17167_neg0031_09_02",
        ]
        retrieval_ids += [
            "retr_roman_republic_q17167_001",
            "retr_actium_q193304_001",
            "retr_q17167_wikidata_end_date_neg0027",
            "retr_q193304_wikidata_occurred_during_q17167",
        ]
        run_ids += [
            "run_roman_republic_001",
            "run_actium_001",
            "run_q17167_end_date_neg0027",
            "run_q193304_occurred_during_q17167",
        ]
        assessment_ids += [
            "fa_roman_republic_pol_001",
            "fa_actium_mil_001",
            "fa_q17167_political_end_date_neg0027",
            "fa_q193304_military_occurred_during_q17167",
        ]
        agent_ids += ["agent_roman_republic_v1", "agent_q17167_roman_republic_v1"]
        subject_ids += ["subj_roman_republic_001", "subj_q17167_roman_republic"]

    reset_params = {
        "claim_ids": sorted(set(claim_ids)),
        "retrieval_ids": sorted(set(retrieval_ids)),
        "run_ids": sorted(set(run_ids)),
        "assessment_ids": sorted(set(assessment_ids)),
        "agent_ids": sorted(set(agent_ids)),
        "subject_ids": sorted(set(subject_ids)),
        "event_qid": args.event_qid,
        "place_qid": args.place_qid,
        "period_qid": args.period_qid,
    }

    q_reset_claims = """
    UNWIND $claim_ids AS claim_id
    MATCH (c:Claim {claim_id: claim_id})
    DETACH DELETE c
    """
    q_reset_retrieval = """
    UNWIND $retrieval_ids AS retrieval_id
    MATCH (rc:RetrievalContext {retrieval_id: retrieval_id})
    DETACH DELETE rc
    """
    q_reset_runs = """
    UNWIND $run_ids AS run_id
    MATCH (run:AnalysisRun {run_id: run_id})
    DETACH DELETE run
    """
    q_reset_assessments = """
    UNWIND $assessment_ids AS assessment_id
    MATCH (fa:FacetAssessment {assessment_id: assessment_id})
    DETACH DELETE fa
    """
    q_reset_agents = """
    UNWIND $agent_ids AS agent_id
    MATCH (a:Agent {agent_id: agent_id})
    DETACH DELETE a
    """
    q_reset_subjects = """
    UNWIND $subject_ids AS subject_id
    MATCH (sc:SubjectConcept {subject_id: subject_id})
    DETACH DELETE sc
    """
    q_reset_event = "MATCH (e:Event {qid: $event_qid}) DETACH DELETE e"
    q_reset_place = "MATCH (pl:Place {qid: $place_qid}) DETACH DELETE pl"
    q_reset_period = "MATCH (p:Period {qid: $period_qid}) DETACH DELETE p"

    q_seed_core = """
    MERGE (sc:SubjectConcept {subject_id: $subject_id})
    SET sc.label = $period_label,
        sc.qid = $period_qid,
        sc.facet = $facet_key,
        sc.entity_type = 'SubjectConcept',
        sc.status = 'active'
    MERGE (a:Agent {agent_id: $agent_id})
    SET a.label = $period_label + ' Specialist',
        a.agent_type = 'subject',
        a.description = 'QID pipeline subject agent for ' + $period_label,
        a.version = $agent_version,
        a.created_at = toString(datetime())
    MERGE (a)-[:OWNS_DOMAIN]->(sc)
    MERGE (c:Claim {claim_id: $factual_claim_id})
    SET c.cipher = $factual_claim_cipher,
        c.label = $factual_claim_label,
        c.text = $factual_claim_text,
        c.claim_type = $factual_claim_type,
        c.epistemic_type = $factual_epistemic_type,
        c.source_agent = $agent_id,
        c.timestamp = toString(datetime()),
        c.status = 'proposed',
        c.confidence = $factual_confidence,
        c.subject_entity_qid = $period_qid,
        c.property_name = 'end_date',
        c.property_value = $period_end,
        c.source_strength = $factual_source_strength,
        c.conflict_code = $factual_conflict_code,
        c.federation_depth = $factual_federation_depth,
        c.policy_id = $policy_id,
        c.policy_hash = $policy_hash,
        c.policy_source_row = $factual_source_row_id,
        c.policy_conflict_row = $factual_conflict_row_id,
        c.policy_profile_row = $factual_profile_row_id,
        c.policy_min_confidence = $factual_min_confidence,
        c.policy_max_confidence = $factual_max_confidence,
        c.require_debate_bridge = $factual_require_debate_bridge,
        c.require_expert_review = $factual_require_expert_review,
        c.policy_gate_status = $factual_gate_status
    MERGE (a)-[:MADE_CLAIM]->(c)
    MERGE (sc)-[:SUBJECT_OF]->(c)
    MERGE (rc:RetrievalContext {retrieval_id: $factual_retrieval_id})
    SET rc.agent_id = $agent_id,
        rc.timestamp = toString(datetime()),
        rc.source = $source,
        rc.seed_qid = $period_qid
    MERGE (c)-[:USED_CONTEXT]->(rc)
    MERGE (run:AnalysisRun {run_id: $factual_run_id})
    SET run.pipeline_version = $pipeline_version,
        run.status = 'completed',
        run.created_at = toString(datetime())
    MERGE (c)-[:HAS_ANALYSIS_RUN]->(run)
    MERGE (f:Facet {facet_id: $factual_facet_id})
    SET f.label = $facet_label
    MERGE (fa:FacetAssessment {assessment_id: $factual_assessment_id})
    SET fa.score = 0.95,
        fa.status = 'supported',
        fa.rationale = 'Direct alignment with canonical period boundary.',
        fa.created_at = toString(datetime()),
        fa.evidence_count = 1
    MERGE (run)-[:HAS_FACET_ASSESSMENT]->(fa)
    MERGE (fa)-[:ASSESSES_FACET]->(f)
    MERGE (fa)-[:EVALUATED_BY]->(a)
    """

    q_seed_years = """
    UNWIND $years AS year_value
    MERGE (y:Year {year: year_value})
    ON CREATE SET y.entity_id = 'year_' + toString(year_value),
                  y.entity_type = 'Year'
    """

    q_seed_entities = """
    MERGE (p:Period {qid: $period_qid})
    SET p.entity_id = $period_entity_id,
        p.label = $period_label,
        p.start = $period_start,
        p.end = $period_end,
        p.start_date_min = $period_start_date_min,
        p.start_date_max = $period_start_date_max,
        p.end_date_min = $period_end_date_min,
        p.end_date_max = $period_end_date_max,
        p.entity_type = 'Period',
        p.facet = $facet_key,
        p.status = 'active'
    WITH p
    MATCH (y_start:Year {year: $period_start_year})
    MATCH (y_end:Year {year: $period_end_year})
    MERGE (p)-[:STARTS_IN_YEAR]->(y_start)
    MERGE (p)-[:ENDS_IN_YEAR]->(y_end)
    WITH p
    MERGE (pl:Place {qid: $place_qid})
    SET pl.entity_id = $place_entity_id,
        pl.label = $place_label,
        pl.place_type = $place_type,
        pl.modern_country = $modern_country,
        pl.entity_type = 'Place',
        pl.status = 'active'
    WITH p, pl
    MERGE (e:Event {qid: $event_qid})
    SET e.entity_id = $event_entity_id,
        e.label = $event_label,
        e.entity_type = 'Event',
        e.event_type = $event_type,
        e.start_date = $event_date,
        e.end_date = $event_date,
        e.start_date_min = $event_date,
        e.start_date_max = $event_date,
        e.end_date_min = $event_date,
        e.end_date_max = $event_date,
        e.date_precision = 'day',
        e.status = 'active'
    WITH e, p, pl
    MATCH (y_event:Year {year: $event_year})
    MERGE (e)-[:OCCURRED_DURING]->(p)
    MERGE (e)-[:OCCURRED_AT]->(pl)
    MERGE (e)-[:STARTS_IN_YEAR]->(y_event)
    MERGE (e)-[:ENDS_IN_YEAR]->(y_event)
    """

    q_seed_temporal_claim = """
    MATCH (sc:SubjectConcept {subject_id: $subject_id})
    MATCH (a:Agent {agent_id: $agent_id})
    MATCH (e:Event {qid: $event_qid})
    MATCH (p:Period {qid: $period_qid})
    MERGE (p)-[:HAS_SUBJECT_CONCEPT]->(sc)
    MERGE (e)-[:HAS_SUBJECT_CONCEPT]->(sc)
    MERGE (c2:Claim {claim_id: $temporal_claim_id})
    SET c2.cipher = $temporal_claim_cipher,
        c2.label = $temporal_claim_label,
        c2.text = $temporal_claim_text,
        c2.claim_type = $temporal_claim_type,
        c2.epistemic_type = $temporal_epistemic_type,
        c2.source_agent = $agent_id,
        c2.timestamp = toString(datetime()),
        c2.status = 'proposed',
        c2.confidence = $temporal_confidence,
        c2.subject_entity_qid = $event_qid,
        c2.object_entity_qid = $period_qid,
        c2.relationship_type = 'OCCURRED_DURING',
        c2.temporal_data = $event_date,
        c2.source_strength = $temporal_source_strength,
        c2.conflict_code = $temporal_conflict_code,
        c2.federation_depth = $temporal_federation_depth,
        c2.policy_id = $policy_id,
        c2.policy_hash = $policy_hash,
        c2.policy_source_row = $temporal_source_row_id,
        c2.policy_conflict_row = $temporal_conflict_row_id,
        c2.policy_profile_row = $temporal_profile_row_id,
        c2.policy_min_confidence = $temporal_min_confidence,
        c2.policy_max_confidence = $temporal_max_confidence,
        c2.require_debate_bridge = $temporal_require_debate_bridge,
        c2.require_expert_review = $temporal_require_expert_review,
        c2.policy_gate_status = $temporal_gate_status
    MERGE (a)-[:MADE_CLAIM]->(c2)
    MERGE (sc)-[:SUBJECT_OF]->(c2)
    MERGE (e)-[:SUBJECT_OF]->(c2)
    MERGE (p)-[:SUBJECT_OF]->(c2)
    MERGE (rc2:RetrievalContext {retrieval_id: $temporal_retrieval_id})
    SET rc2.agent_id = $agent_id,
        rc2.timestamp = toString(datetime()),
        rc2.source = $source,
        rc2.seed_qid = $event_qid
    MERGE (c2)-[:USED_CONTEXT]->(rc2)
    MERGE (run2:AnalysisRun {run_id: $temporal_run_id})
    SET run2.pipeline_version = $pipeline_version,
        run2.status = 'completed',
        run2.created_at = toString(datetime())
    MERGE (c2)-[:HAS_ANALYSIS_RUN]->(run2)
    MERGE (f2:Facet {facet_id: $temporal_facet_id})
    SET f2.label = $temporal_facet_label
    MERGE (fa2:FacetAssessment {assessment_id: $temporal_assessment_id})
    SET fa2.score = 0.93,
        fa2.status = 'supported',
        fa2.rationale = 'Event date and period boundaries align and historical consensus is high.',
        fa2.created_at = toString(datetime()),
        fa2.evidence_count = 1
    MERGE (run2)-[:HAS_FACET_ASSESSMENT]->(fa2)
    MERGE (fa2)-[:ASSESSES_FACET]->(f2)
    MERGE (fa2)-[:EVALUATED_BY]->(a)
    """

    q_promote_claim = """
    MATCH (c:Claim {claim_id: $temporal_claim_id})
    OPTIONAL MATCH (c)-[:USED_CONTEXT]->(rc:RetrievalContext)
    WITH c, count(rc) AS rc_count
    OPTIONAL MATCH (c)-[:HAS_ANALYSIS_RUN]->(ar:AnalysisRun)
    WITH c, rc_count, count(ar) AS ar_count
    WHERE c.confidence >= c.policy_min_confidence
      AND c.confidence <= c.policy_max_confidence
      AND coalesce(c.require_debate_bridge, false) = false
      AND coalesce(c.require_expert_review, false) = false
      AND c.policy_gate_status = 'auto_promote_eligible'
      AND rc_count > 0
      AND ar_count > 0
    SET c.status = 'validated',
        c.promotion_date = toString(datetime()),
        c.promoted = true
    """

    q_promote_relationships = """
    MATCH (c:Claim {claim_id: $temporal_claim_id, status: 'validated'})
    MATCH (e:Event {qid: $event_qid})
    MATCH (p:Period {qid: $period_qid})
    MATCH (pl:Place {qid: $place_qid})
    MERGE (e)-[r:OCCURRED_DURING]->(p)
    SET r.promoted_from_claim_id = c.claim_id,
        r.promotion_date = toString(datetime()),
        r.promotion_status = 'canonical'
    MERGE (e)-[ra:OCCURRED_AT]->(pl)
    SET ra.promoted_from_claim_id = c.claim_id,
        ra.promotion_date = toString(datetime()),
        ra.promotion_status = 'canonical'
    MERGE (e)-[se:SUPPORTED_BY]->(c)
    SET se.claim_id = c.claim_id,
        se.promotion_date = toString(datetime())
    MERGE (p)-[sp:SUPPORTED_BY]->(c)
    SET sp.claim_id = c.claim_id,
        sp.promotion_date = toString(datetime())
    MERGE (pl)-[spl:SUPPORTED_BY]->(c)
    SET spl.claim_id = c.claim_id,
        spl.promotion_date = toString(datetime())
    """

    q_verify_core = """
    MATCH (sc:SubjectConcept {subject_id: $subject_id})
    OPTIONAL MATCH (a:Agent {agent_id: $agent_id})-[:OWNS_DOMAIN]->(sc)
    OPTIONAL MATCH (a)-[:MADE_CLAIM]->(c:Claim {claim_id: $factual_claim_id})
    OPTIONAL MATCH (sc)-[:SUBJECT_OF]->(c)
    OPTIONAL MATCH (c)-[:USED_CONTEXT]->(rc:RetrievalContext {retrieval_id: $factual_retrieval_id})
    OPTIONAL MATCH (c)-[:HAS_ANALYSIS_RUN]->(run:AnalysisRun {run_id: $factual_run_id})
    OPTIONAL MATCH (run)-[:HAS_FACET_ASSESSMENT]->(fa:FacetAssessment {assessment_id: $factual_assessment_id})
    OPTIONAL MATCH (fa)-[:ASSESSES_FACET]->(f:Facet {facet_id: $factual_facet_id})
    RETURN
      sc.subject_id AS subject_id,
      sc.label AS subject_label,
      a.agent_id AS agent_id,
      c.claim_id AS claim_id,
      c.label AS claim_label,
      c.status AS claim_status,
      c.policy_hash AS claim_policy_hash,
      c.policy_profile_row AS claim_policy_row,
      c.policy_gate_status AS claim_gate_status,
      rc.retrieval_id AS retrieval_id,
      run.run_id AS run_id,
      fa.assessment_id AS assessment_id,
      f.label AS assessed_facet
    """

    q_verify_event = """
    MATCH (e:Event {qid: $event_qid})
    MATCH (p:Period {qid: $period_qid})
    MATCH (pl:Place {qid: $place_qid})
    OPTIONAL MATCH (e)-[:OCCURRED_DURING]->(p)
    OPTIONAL MATCH (e)-[:OCCURRED_AT]->(pl)
    OPTIONAL MATCH (e)-[:STARTS_IN_YEAR]->(ys:Year)
    OPTIONAL MATCH (e)-[:ENDS_IN_YEAR]->(ye:Year)
    OPTIONAL MATCH (e)-[:SUBJECT_OF]->(c2:Claim {claim_id: $temporal_claim_id})
    OPTIONAL MATCH (p)-[:SUBJECT_OF]->(c2)
    OPTIONAL MATCH (c2)-[:USED_CONTEXT]->(rc2:RetrievalContext {retrieval_id: $temporal_retrieval_id})
    OPTIONAL MATCH (c2)-[:HAS_ANALYSIS_RUN]->(run2:AnalysisRun {run_id: $temporal_run_id})
    OPTIONAL MATCH (run2)-[:HAS_FACET_ASSESSMENT]->(fa2:FacetAssessment {assessment_id: $temporal_assessment_id})
    OPTIONAL MATCH (fa2)-[:ASSESSES_FACET]->(f2:Facet {facet_id: 'facet_military'})
    RETURN
      e.label AS event_label,
      e.qid AS event_qid,
      p.label AS period_label,
      p.qid AS period_qid,
      pl.label AS place_label,
      ys.year AS event_start_year,
      ye.year AS event_end_year,
      c2.claim_id AS claim_id,
      c2.label AS claim_label,
      c2.status AS claim_status,
      c2.policy_hash AS claim_policy_hash,
      c2.policy_profile_row AS claim_policy_row,
      c2.policy_gate_status AS claim_gate_status,
      rc2.retrieval_id AS retrieval_id,
      run2.run_id AS run_id,
      fa2.assessment_id AS assessment_id,
      f2.label AS assessed_facet
    """

    q_verify_promotion = """
    MATCH (c:Claim {claim_id: $temporal_claim_id})
    MATCH (e:Event {qid: $event_qid})
    MATCH (p:Period {qid: $period_qid})
    MATCH (pl:Place {qid: $place_qid})
    OPTIONAL MATCH (e)-[r:OCCURRED_DURING]->(p)
    OPTIONAL MATCH (e)-[ra:OCCURRED_AT]->(pl)
    OPTIONAL MATCH (e)-[se:SUPPORTED_BY]->(c)
    OPTIONAL MATCH (p)-[sp:SUPPORTED_BY]->(c)
    OPTIONAL MATCH (pl)-[spl:SUPPORTED_BY]->(c)
    WITH c, r, ra, pl,
         count(DISTINCT se) AS event_supported_by_count,
         count(DISTINCT sp) AS period_supported_by_count,
         count(DISTINCT spl) AS place_supported_by_count
    RETURN
      c.claim_id AS claim_id,
      c.label AS claim_label,
      c.status AS claim_status,
      c.policy_hash AS claim_policy_hash,
      c.policy_profile_row AS claim_policy_row,
      c.policy_gate_status AS claim_gate_status,
      c.promoted AS claim_promoted,
      c.promotion_date AS claim_promotion_date,
      type(r) AS canonical_rel_type,
      r.promoted_from_claim_id AS rel_promoted_from_claim_id,
      r.promotion_status AS rel_promotion_status,
      type(ra) AS canonical_place_rel_type,
      ra.promoted_from_claim_id AS place_rel_promoted_from_claim_id,
      ra.promotion_status AS place_rel_promotion_status,
      pl.entity_id AS place_entity_id,
      pl.qid AS place_qid,
      event_supported_by_count,
      period_supported_by_count,
      place_supported_by_count
    """

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    try:
        with driver.session() as session:
            run_query(session, "reset claims", q_reset_claims, reset_params)
            run_query(session, "reset retrieval context", q_reset_retrieval, reset_params)
            run_query(session, "reset analysis runs", q_reset_runs, reset_params)
            run_query(session, "reset facet assessments", q_reset_assessments, reset_params)
            run_query(session, "reset agents", q_reset_agents, reset_params)
            run_query(session, "reset subjects", q_reset_subjects, reset_params)
            if args.reset_entities:
                run_query(session, "reset event by qid", q_reset_event, reset_params)
                run_query(session, "reset place by qid", q_reset_place, reset_params)
                run_query(session, "reset period by qid", q_reset_period, reset_params)

            run_query(session, "seed core claim flow", q_seed_core, base_params)
            run_query(session, "seed required years", q_seed_years, base_params)
            run_query(session, "seed period/event/place entities", q_seed_entities, base_params)
            run_query(session, "seed temporal claim flow", q_seed_temporal_claim, base_params)
            run_query(session, "promote claim status", q_promote_claim, base_params)
            run_query(session, "promote canonical relationships", q_promote_relationships, base_params)

            run_query(session, "verify core flow", q_verify_core, base_params)
            run_query(session, "verify event flow", q_verify_event, base_params)
            run_query(session, "verify promotion", q_verify_promotion, base_params)
    finally:
        driver.close()

    print("QID pipeline complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
