"""
Military facet training pilot — Claims track, both sides, atomic Q-P-Q first.

Per docs/FACET_TRAINING_CONTRACT.md:
  - Registry predicates only (provisional OK with predicate_status=tbd + Hold)
  - SubjectConcept scope under roman_republic
  - Atomic statement: subjectQID-PID-objectQID (multilingual)
  - IGAR optional interpretation — not required for FOUGHT_IN / P607
  - Slow / methodical: both sides of the battle

Usage:
  python -m scripts.agents.military.training_pilot --dry-run
  python -m scripts.agents.military.training_pilot --write
  python -m scripts.agents.military.training_pilot --clear-igar
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.config_loader import (  # noqa: E402
    NEO4J_DATABASE,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
)
from scripts.tools.claim_ingestion_pipeline import ClaimIngestionPipeline  # noqa: E402
from scripts.agents.military.registry_predicates import (  # noqa: E402
    assert_military_predicate,
)
from scripts.agents.military.igar import (  # noqa: E402
    MILITARY_BATTLE_METHOD_PROMPT,
    clear_igar_props,
)
from scripts.tools.entity_cipher import generate_entity_cipher  # noqa: E402

load_dotenv()

CANNAE_QID = "Q179591"
CANNAE_ENTITY_ID = "evt_Q179591"
SCOPE_SUBJECT_ID = "sc_q17167_military_wars_campaigns"
SOURCE_AGENT = "SFA_sc_q17167_military_wars_campaigns_MILITARY"
DOMAIN_ID = "roman_republic"
FACET = "military"
PRED_PID = "P607"

# Atomic both-sides seed. IGAR omitted — attach only after source-backed research.
ROSTER: list[dict[str, Any]] = [
    {
        "qid": "Q315274",
        "label": "C. Terentius Varro",
        "side": "roman",
        "role": "commander",
        "relationship_type": "FOUGHT_IN",
        "predicate_status": "confirmed",
        "sources": ["Wikidata P607", "Polybius 3.107-117", "Livy 22.44-61"],
    },
    {
        "qid": "Q432244",
        "label": "L. Aemilius Paullus",
        "side": "roman",
        "role": "commander",
        "relationship_type": "FOUGHT_IN",
        "predicate_status": "confirmed",
        "sources": ["Wikidata P607", "Polybius 3.116", "Livy 22.49"],
    },
    {
        "qid": "Q554632",
        "label": "Cn. Servilius Geminus",
        "side": "roman",
        "role": "commander",
        "relationship_type": "FOUGHT_IN",
        "predicate_status": "confirmed",
        "sources": ["Wikidata P607", "Livy 22.49"],
    },
    {
        "qid": "Q857028",
        "label": "C. Calpurnius Piso",
        "side": "roman",
        "role": "participant",
        "relationship_type": "FOUGHT_IN",
        "predicate_status": "tbd",
        "research_notes": (
            "Livy 22.61 places a Calpurnius Piso among Cannae prisoners; "
            "confirm identity vs Q857028 and whether FOUGHT_IN vs a finer "
            "captive/prisoner predicate is needed before Validate."
        ),
        "sources": ["Livy 22.61", "Wikidata Q857028"],
    },
    {
        "qid": "Q36456",
        "label": "Hannibal",
        "side": "carthaginian",
        "role": "commander",
        "relationship_type": "FOUGHT_IN",
        "predicate_status": "confirmed",
        "sources": ["Wikidata P607", "Polybius 3.113-117", "Livy 22.44-50"],
    },
    {
        "qid": "Q463438",
        "label": "Maharbal",
        "side": "carthaginian",
        "role": "officer",
        "relationship_type": "FOUGHT_IN",
        "predicate_status": "tbd",
        "research_notes": (
            "Traditional cavalry commander under Hannibal at Cannae (WD Q463438). "
            "Confirm whether COMMANDED_BY / SERVED_UNDER is better than FOUGHT_IN. "
            "Do NOT use Q249163 (wrong item)."
        ),
        "sources": ["Livy 22.51", "Wikidata Q463438"],
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_cannae_event(session: Any) -> None:
    session.run(
        """
        MATCH (e:Event {qid: $qid})
        SET e.entity_id = coalesce(e.entity_id, $entity_id),
            e.date_source = coalesce(e.date_source, 'wikidata_p585'),
            e.date_untrusted = false
        """,
        qid=CANNAE_QID,
        entity_id=CANNAE_ENTITY_ID,
    )


def ensure_person(session: Any, qid: str, label: str) -> dict[str, Any]:
    entity_id = f"person_{qid.lower()}"
    entity_cipher = generate_entity_cipher("PERSON", qid=qid, namespace="wd")

    if qid == "Q36456":
        session.run(
            """
            MATCH (n {qid: $qid})
            WHERE n:Event OR n:Person OR n:Entity
            WITH n LIMIT 1
            REMOVE n:Event
            SET n:Person:Entity,
                n.label = $label,
                n.entity_type = 'Person',
                n.entity_id = coalesce(n.entity_id, $entity_id),
                n.entity_cipher = coalesce(n.entity_cipher, $entity_cipher),
                n.quarantined = null,
                n.quarantine_reason = null,
                n.date_untrusted = null,
                n.start_date = null,
                n.event_type = null,
                n.corrected_from = 'mislabeled_event_as_cannae',
                n.corrected_at = datetime()
            """,
            qid=qid,
            label=label,
            entity_id=entity_id,
            entity_cipher=entity_cipher,
        )

    row = session.run(
        """
        MERGE (p:Person {qid: $qid})
        ON CREATE SET
            p:Entity,
            p.label = $label,
            p.entity_type = 'Person',
            p.entity_id = $entity_id,
            p.entity_cipher = $entity_cipher,
            p.stub = true,
            p.created_by = 'military_training_pilot',
            p.created_at = datetime()
        ON MATCH SET
            p:Entity,
            p.label = coalesce(p.label, $label),
            p.entity_id = coalesce(p.entity_id, $entity_id),
            p.entity_cipher = coalesce(p.entity_cipher, $entity_cipher),
            p.entity_type = coalesce(p.entity_type, 'Person')
        RETURN p.qid AS qid, p.label AS label, p.entity_id AS entity_id,
               p.stub AS stub
        """,
        qid=qid,
        label=label,
        entity_id=entity_id,
        entity_cipher=entity_cipher,
    ).single()
    return dict(row) if row else {"qid": qid, "label": label, "entity_id": entity_id}


def route_claim_to_scope(session: Any, claim_id: str) -> None:
    session.run(
        """
        MATCH (c:Claim {claim_id: $claim_id})
        MATCH (sc:SubjectConcept {subject_id: $subject_id})
        MERGE (c)-[r:IN_SCOPE]->(sc)
        SET r.routed_at = datetime(),
            r.routing_method = 'military_training_pilot',
            r.domain_id = $domain_id,
            c.routed_subject_id = $subject_id,
            c.routed_subject_label = sc.label,
            c.domain_id = $domain_id
        """,
        claim_id=claim_id,
        subject_id=SCOPE_SUBJECT_ID,
        domain_id=DOMAIN_ID,
    )


def clear_pilot_igar(session: Any) -> int:
    """Strip provisional/hand-authored IGAR; keep atomic Q-P-Q fields."""
    props = clear_igar_props()
    row = session.run(
        """
        MATCH (c:Claim)
        WHERE c.source_agent = $agent
        SET c.igar_json = null,
            c.igar_input = null,
            c.igar_goal = null,
            c.igar_action = null,
            c.igar_result = null,
            c.igar_input_year = null,
            c.igar_action_year = null,
            c.igar_result_year = null,
            c.igar_complete = false,
            c.claim_layer = 'atomic_participation',
            c.review_notes = coalesce(
              c.review_notes,
              ''
            ) + CASE
              WHEN c.review_notes CONTAINS 'IGAR cleared'
              THEN ''
              ELSE ' | IGAR cleared 2026-07-16: atomic Q-P-Q only; IGAR optional later'
            END,
            c.status = 'held'
        RETURN count(c) AS n
        """,
        agent=SOURCE_AGENT,
        **{k: props[k] for k in props if k.startswith("igar_")},
    ).single()
    return int(row["n"]) if row else 0


def build_batch(session: Any) -> list[dict[str, Any]]:
    print(MILITARY_BATTLE_METHOD_PROMPT)
    print()
    ensure_cannae_event(session)
    batch: list[dict[str, Any]] = []
    for entry in ROSTER:
        person = ensure_person(session, entry["qid"], entry["label"])
        rel = assert_military_predicate(
            entry["relationship_type"], require_implemented=True
        )
        pred_status = entry.get("predicate_status", "confirmed")
        research_notes = entry.get("research_notes", "")
        wd_statement = ClaimIngestionPipeline.format_wd_statement(
            entry["qid"], PRED_PID, CANNAE_QID
        )
        # English display label; language-neutral key lives in wd_statement
        label = f"{entry['label']} fought in Battle of Cannae"
        description = (
            f"Atomic participation claim ({wd_statement}). "
            f"Side={entry['side']}; role={entry['role']}. "
            f"Sources: {', '.join(entry.get('sources') or [])}. "
            "IGAR not attached — optional interpretation layer only."
        )
        if pred_status == "tbd":
            description += " PREDICATE TBD — Hold pending further research."

        batch.append(
            {
                "entity_id": person["entity_id"],
                "target_id": CANNAE_ENTITY_ID,
                "relationship_type": rel,
                "confidence": 0.72 if pred_status == "tbd" else 0.88,
                "label": label,
                "description": description,
                "subject_qid": entry["qid"],
                "igar": None,
                "predicate_status": pred_status,
                "research_notes": research_notes,
                "initial_status": "held",
                "require_igar": False,
                "side": entry["side"],
                "role": entry["role"],
                "wd_statement": wd_statement,
                "claim_signature": {
                    "qid": entry["qid"],
                    "pvalues": [PRED_PID],
                    "values": {PRED_PID: CANNAE_QID},
                    "rel": rel,
                    # Keep stable so re-runs MERGE the same claim_id as prior pilots
                    "pilot": "military_training_igar_both_sides_2026_07_16",
                    "side": entry["side"],
                },
                "authority_ids": {
                    "person_qid": entry["qid"],
                    "candidate_qid": CANNAE_QID,
                    "pred_pid": PRED_PID,
                    "domain_id": DOMAIN_ID,
                    "side": entry["side"],
                    "role": entry["role"],
                    "claim_layer": "atomic_participation",
                },
            }
        )
    return batch


def run(*, write: bool) -> int:
    driver = GraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    database = NEO4J_DATABASE or "neo4j"
    pipeline = ClaimIngestionPipeline(driver, database=database)
    results: list[dict[str, Any]] = []

    try:
        with driver.session(database=database) as session:
            batch = build_batch(session)
            print(f"Pilot batch size: {len(batch)} (both sides, atomic Q-P-Q)")
            for item in batch:
                print(
                    f"  - [{item['side']}/{item.get('role')}] "
                    f"{item.get('wd_statement')} "
                    f"({item['predicate_status']})"
                )
                if not write:
                    results.append({"status": "dry_run", **item})
                    continue

                outcome = pipeline.ingest_claim(
                    entity_id=item["entity_id"],
                    relationship_type=item["relationship_type"],
                    target_id=item["target_id"],
                    confidence=item["confidence"],
                    label=item["label"],
                    description=item["description"],
                    subject_qid=item["subject_qid"],
                    retrieval_source="military_training_pilot",
                    reasoning_notes=item["description"],
                    facet=FACET,
                    claim_signature=item["claim_signature"],
                    claim_type="relational",
                    source_agent=SOURCE_AGENT,
                    authority_source="wikidata",
                    authority_ids=item["authority_ids"],
                    pred_pid=PRED_PID,
                    strict_registry=True,
                    igar=None,
                    predicate_status=item["predicate_status"],
                    research_notes=item.get("research_notes") or "",
                    initial_status=item["initial_status"],
                    require_igar=False,
                )
                claim_id = outcome.get("claim_id")
                if claim_id and outcome.get("status") != "error":
                    route_claim_to_scope(session, claim_id)
                    session.run(
                        """
                        MATCH (c:Claim {claim_id: $claim_id})
                        SET c.status = 'held',
                            c.claim_layer = 'atomic_participation',
                            c.wd_statement = coalesce(c.wd_statement, $wd),
                            c.review_notes = 'Held: atomic Q-P-Q participation; IGAR optional'
                        """,
                        claim_id=claim_id,
                        wd=item.get("wd_statement"),
                    )
                results.append(outcome)
                print(
                    f"    -> {outcome.get('status')} claim_id={claim_id} "
                    f"err={outcome.get('error')}"
                )

        out_path = ROOT / "output" / "military_training_pilot_atomic_qpq.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(
                {
                    "ran_at": _utc_now(),
                    "mode": "write" if write else "dry_run",
                    "method_prompt": MILITARY_BATTLE_METHOD_PROMPT,
                    "domain_id": DOMAIN_ID,
                    "scope_subject_id": SCOPE_SUBJECT_ID,
                    "source_agent": SOURCE_AGENT,
                    "results": results,
                },
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        print(f"\nWrote {out_path}")
        errors = [r for r in results if r.get("status") == "error"]
        if errors:
            print(f"[WARN] {len(errors)} errors")
            return 2
        print("[OK] pilot complete" if write else "[OK] dry-run complete")
        return 0
    finally:
        driver.close()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Military training pilot (atomic Q-P-Q, both sides)"
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument(
        "--clear-igar",
        action="store_true",
        help="Strip hand-authored IGAR from existing military pilot claims",
    )
    args = ap.parse_args()
    if args.clear_igar:
        driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
            n = clear_pilot_igar(session)
            print(f"[OK] cleared IGAR on {n} military pilot claims")
        driver.close()
        return 0
    if not args.dry_run and not args.write:
        ap.error("Specify --dry-run, --write, or --clear-igar")
    return run(write=args.write)


if __name__ == "__main__":
    raise SystemExit(main())
