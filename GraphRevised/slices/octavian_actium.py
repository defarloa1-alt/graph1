"""Persist the Octavian/Actium slice and submit its participation proposal.

    python -m GraphRevised.slices.octavian_actium

Idempotent: the Q1405 payload is fetched once and then reused from
phase-5-source/, and every graph write is a guarded Phase 3 operation. The
script stops at a submitted Proposal; acceptance is a curator step:

    python -m GraphRevised.proposals.review accept <proposal-id> --by <name> --basis "<reason>"
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from neo4j import GraphDatabase

from GraphRevised.adapters.wikidata_identity import USER_AGENT
from GraphRevised.adapters.wikidata_statements import REPOSITORY_ROOT, statement_observation
from GraphRevised.operations import load_operations, run_write
from GraphRevised.proposals.registry import load_registry
from GraphRevised.proposals.store import Neo4jReader, submit
from GraphRevised.proposals.wikidata_proposer import drafts_from_observation

GRAPH_REVISED = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = GRAPH_REVISED / "phase-5-source"
ACTIUM_PAYLOAD = GRAPH_REVISED / "phase-2-source" / "wikidata-Q160387-r2555342002.json"
OCTAVIAN_STATEMENT = "Q160387$d9469717-433b-c369-9fc7-3d7d5bf2b969"
QID = "Q1405"
ENTITY_ID = "chr:entity:augustus"
SOURCE_URI = f"https://www.wikidata.org/wiki/Special:EntityData/{QID}.json"


def preserved_identity_payload() -> tuple[Path, dict]:
    """Return the preserved Q1405 payload, fetching it only if none exists."""
    existing = sorted(SOURCE_DIRECTORY.glob(f"wikidata-{QID}-r*.json"))
    existing = [path for path in existing if not path.name.endswith(".metadata.json")]
    if existing:
        path = existing[-1]
        return path, json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))

    response = requests.get(SOURCE_URI, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    payload_bytes = response.content
    entity = json.loads(payload_bytes)["entities"][QID]
    metadata = {
        "sourceSystem": "Wikidata",
        "sourceUri": SOURCE_URI,
        "entityId": QID,
        "entityLabel": entity["labels"]["en"]["value"],
        "entityDescription": entity["descriptions"]["en"]["value"],
        "revision": entity["lastrevid"],
        "modified": entity["modified"],
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "contentHash": hashlib.sha256(payload_bytes).hexdigest(),
    }
    SOURCE_DIRECTORY.mkdir(exist_ok=True)
    path = SOURCE_DIRECTORY / f"wikidata-{QID}-r{entity['lastrevid']}.json"
    path.write_bytes(payload_bytes)
    path.with_suffix(".metadata.json").write_bytes(
        (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    return path, metadata


def persist(tx, payload_path: Path, metadata: dict):
    operations = load_operations()
    registry = load_registry()
    label = metadata["entityLabel"]

    run_write(tx, operations, "upsert_entity", {
        "id": ENTITY_ID,
        "kind": "Person",
        "label": label,
        "description": metadata["entityDescription"],
        "status": "provisional",
        "shortLabel": label,
    })
    run_write(tx, operations, "upsert_authority", {
        "entityId": ENTITY_ID,
        "id": f"chr:authority:wikidata:{QID}",
        "system": "Wikidata",
        "identifier": QID,
        "label": f"Wikidata record: {label} ({QID})",
        "shortLabel": f"Wikidata: {label}",
        "description": metadata["entityDescription"],
        "retrievedAt": metadata["retrievedAt"],
        "sourceUri": metadata["sourceUri"],
        "sourceRevision": metadata["revision"],
        "contentHash": metadata["contentHash"],
        "rawPayloadUri": payload_path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "role": "entity_identity",
        "relation": "closeMatch",
        "linkStatus": "accepted",
    })
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
    payload_path, metadata = preserved_identity_payload()
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
