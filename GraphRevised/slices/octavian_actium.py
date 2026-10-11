"""Persist the Octavian/Actium slice and submit its participation proposal.

    python -m GraphRevised.slices.octavian_actium

Idempotent: the Q1405 payload is fetched once and then reused from
phase-5-source/, and every graph write is a guarded Phase 3 operation. The
script stops at a submitted Proposal; acceptance is a curator step:

    python -m GraphRevised.proposals.review accept <proposal-id> --by <name> --basis "<reason>"
"""

from __future__ import annotations

import os
from pathlib import Path

from neo4j import GraphDatabase

from GraphRevised.adapters.wikidata_statements import statement_observation
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.store import Neo4jReader, submit
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation
from GraphRevised.slices.add_entity import persist_identity, preserved_identity_payload

GRAPH_REVISED = Path(__file__).resolve().parents[1]
ACTIUM_PAYLOAD = GRAPH_REVISED / "phase-2-source" / "wikidata-Q160387-r2555342002.json"
OCTAVIAN_STATEMENT = "Q160387$d9469717-433b-c369-9fc7-3d7d5bf2b969"
QID = "Q1405"
ENTITY_ID = "chr:entity:augustus"


def persist(tx, payload_path: Path, metadata: dict):
    operations = load_operations()
    registry = load_registry()
    label = metadata["entityLabel"]
    persist_identity(tx, operations, entity_id=ENTITY_ID, kind="Person", payload_path=payload_path, metadata=metadata)
    observation = statement_observation(
        ACTIUM_PAYLOAD,
        OCTAVIAN_STATEMENT,
        label=f"Wikidata observation: {label} participated in Battle of Actium",
        short_label=f"Wikidata: {label} -> Actium",
    )
    run_write(tx, operations, "upsert_observation", observation)

    reader = Neo4jReader(tx)
    proposed = drafts_from_observation(reader.observation(observation["id"]), reader, registry)
    if proposed.unresolved or len(proposed.drafts) != 1:
        raise RuntimeError(f"unexpected proposer result: {proposed}")
    return submit(tx, proposed.drafts[0], registry, operations)


def main() -> int:
    payload_path, metadata = preserved_identity_payload(QID)
    print(f"identity payload: {payload_path.name} ({metadata['contentHash'][:16]})")
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            result = session.execute_write(persist, payload_path, metadata)
    finally:
        driver.close()
    validation = result.validation
    print(f"outcome: {validation.outcome.value}; stored: {result.stored}")
    print(f"proposal: {validation.proposal_id}")
    for reason in validation.reasons:
        print(f"  {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
