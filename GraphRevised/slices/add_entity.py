"""Add a curator-approved Entity with its Wikidata identity link.

    python -m GraphRevised.slices.add_entity --qid Q51673 --id chr:entity:mark-antony --kind Person

Identity setup only: it creates no Assertions. The Wikidata entity payload is
fetched once, preserved byte-for-byte in phase-5-source/, and reused on later
runs. Every graph write is a guarded Phase 3 operation, so a rerun is a no-op.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from neo4j import GraphDatabase

from GraphRevised.adapters.wikidata_identity import USER_AGENT
from GraphRevised.adapters.wikidata_statements import REPOSITORY_ROOT
from GraphRevised.operations import load_operations, run_write

GRAPH_REVISED = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = GRAPH_REVISED / "phase-5-source"
from GraphRevised.proposals.registry import load_registry

ENTITY_KINDS = load_registry().entity_kinds


def preserved_identity_payload(qid: str) -> tuple[Path, dict[str, Any]]:
    """Return the preserved Wikidata payload for `qid`, fetching it only if none exists."""
    existing = [
        path for path in sorted(SOURCE_DIRECTORY.glob(f"wikidata-{qid}-r*.json"))
        if not path.name.endswith(".metadata.json")
    ]
    if existing:
        path = existing[-1]
        return path, json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))

    source_uri = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    response = requests.get(source_uri, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    payload_bytes = response.content
    entity = json.loads(payload_bytes)["entities"][qid]
    metadata = {
        "sourceSystem": "Wikidata",
        "sourceUri": source_uri,
        "entityId": qid,
        "entityLabel": entity["labels"]["en"]["value"],
        "entityDescription": entity.get("descriptions", {}).get("en", {}).get("value"),
        "revision": entity["lastrevid"],
        "modified": entity["modified"],
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "contentHash": hashlib.sha256(payload_bytes).hexdigest(),
    }
    SOURCE_DIRECTORY.mkdir(exist_ok=True)
    path = SOURCE_DIRECTORY / f"wikidata-{qid}-r{entity['lastrevid']}.json"
    path.write_bytes(payload_bytes)
    path.with_suffix(".metadata.json").write_bytes(
        (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    return path, metadata


def persist_identity(
    tx: Any,
    operations: dict[str, str],
    *,
    entity_id: str,
    kind: str,
    payload_path: Path,
    metadata: dict[str, Any],
    status: str = "provisional",
) -> None:
    qid, label = metadata["entityId"], metadata["entityLabel"]
    run_write(tx, operations, "upsert_entity", {
        "id": entity_id,
        "kind": kind,
        "label": label,
        "description": metadata["entityDescription"],
        "status": status,
        "shortLabel": label,
    })
    run_write(tx, operations, "upsert_authority", {
        "entityId": entity_id,
        "id": f"chr:authority:wikidata:{qid}",
        "system": "Wikidata",
        "identifier": qid,
        "label": f"Wikidata record: {label} ({qid})",
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


def persist_local_entity(
    tx: Any,
    operations: dict[str, str],
    *,
    entity_id: str,
    kind: str,
    label: str,
    description: str,
    status: str = "provisional",
) -> None:
    """A local analytical Entity with no external identity, such as a fleet's wing."""
    run_write(tx, operations, "upsert_entity", {
        "id": entity_id,
        "kind": kind,
        "label": label,
        "description": description,
        "status": status,
        "shortLabel": None,
    })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--qid", required=True)
    parser.add_argument("--id", required=True, dest="entity_id")
    parser.add_argument("--kind", required=True, choices=ENTITY_KINDS)
    args = parser.parse_args(argv)

    payload_path, metadata = preserved_identity_payload(args.qid)
    driver = GraphDatabase.driver(
        os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        auth=(os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ["NEO4J_PASSWORD"]),
    )
    try:
        with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
            session.execute_write(
                persist_identity, load_operations(),
                entity_id=args.entity_id, kind=args.kind, payload_path=payload_path, metadata=metadata,
            )
    finally:
        driver.close()
    print(f"{args.entity_id}: {metadata['entityLabel']} ({args.qid}, r{metadata['revision']}) — "
          f"{metadata['entityDescription']}")
    print(f"payload: {payload_path.name} ({metadata['contentHash'][:16]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
