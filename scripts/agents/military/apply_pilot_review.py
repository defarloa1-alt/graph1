"""
Apply human review decisions to Military training pilot claims.

Default (FACET_TRAINING_CONTRACT + date gate): HOLD all four FOUGHT_IN claims.
Do not validate while Event Q179591.start_date is a bio-harvest person-year
proxy (-0200 from Varro death) instead of Wikidata P585 (-0216-08-02).

Usage:
  python -m scripts.agents.military.apply_pilot_review --dry-run
  python -m scripts.agents.military.apply_pilot_review --apply
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

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

load_dotenv()

AGENT = "SFA_sc_q17167_military_wars_campaigns_MILITARY"

HOLD_NOTE = (
    "HOLD: Event Q179591.start_date=-0200 is not Wikidata P585. "
    "Wikidata Battle of Cannae (Q179591) has P585=-0216-08-02. "
    "Graph date came from biographic harvest _event_start_date "
    "(person death/birth year proxy; last writer C. Terentius Varro death=-200). "
    "Do not validate FOUGHT_IN until Event.start_date is corrected from Wikidata. "
    "NOTE: graph Event Q36456 labeled Cannae is contaminated — Wikidata Q36456 is Hannibal."
)

DECISIONS = {
    "claim_7b2f9eae6546": {
        "person": "C. Terentius Varro",
        "status": "held",
        "notes": HOLD_NOTE,
    },
    "claim_788f0bd18f86": {
        "person": "L. Aemilius Paullus",
        "status": "held",
        "notes": HOLD_NOTE,
    },
    "claim_964f1edc996c": {
        "person": "Cn. Servilius Geminus",
        "status": "held",
        "notes": HOLD_NOTE,
    },
    "claim_ff8790717eb9": {
        "person": "C. Calpurnius Piso",
        "status": "held",
        "notes": HOLD_NOTE,
    },
}


def apply(dry_run: bool) -> None:
    driver = GraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    ts = datetime.now(timezone.utc).isoformat()
    with driver.session(database=NEO4J_DATABASE) as session:
        for claim_id, decision in DECISIONS.items():
            if dry_run:
                print(
                    f"[dry-run] {claim_id} ({decision['person']}) -> {decision['status']}"
                )
                continue
            result = session.run(
                """
                MATCH (c:Claim {claim_id: $claim_id})
                WHERE c.source_agent = $agent
                SET c.status = $status,
                    c.review_notes = $notes,
                    c.reviewed_at = $ts,
                    c.reviewed_by = 'human_pilot_review_2026_07_16'
                RETURN c.claim_id AS id, c.status AS status
                """,
                claim_id=claim_id,
                agent=AGENT,
                status=decision["status"],
                notes=decision["notes"],
                ts=ts,
            )
            row = result.single()
            if row:
                print(f"OK {row['id']} -> {row['status']} ({decision['person']})")
            else:
                print(f"MISS {claim_id}")
    driver.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        parser.error("Specify --dry-run or --apply")
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
