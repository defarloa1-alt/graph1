"""Statement-level SourceObservations from preserved Wikidata entity payloads."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class StatementNotFound(LookupError):
    """The preserved payload does not contain the requested statement."""


def statement_observation(
    payload_path: Path,
    statement_id: str,
    *,
    label: str,
    short_label: str,
    retrieved_at: str | None = None,
) -> dict[str, Any]:
    """Return parameters for the Phase 3 `upsert_observation` operation.

    The payload file is hashed byte-for-byte, so the observation stays tied to
    exactly the preserved bytes. `retrieved_at` defaults to the payload's
    `.metadata.json` sidecar.
    """
    payload_bytes = payload_path.read_bytes()
    payload = json.loads(payload_bytes)
    entity_id = statement_id.split("$", 1)[0]
    entity = payload["entities"][entity_id]

    statement = next(
        (
            claim
            for claims in entity.get("claims", {}).values()
            for claim in claims
            if claim["id"] == statement_id
        ),
        None,
    )
    if statement is None:
        raise StatementNotFound(f"{statement_id} is not in {payload_path.name}")

    value = statement["mainsnak"].get("datavalue", {}).get("value")
    if not isinstance(value, dict) or "id" not in value:
        raise StatementNotFound(f"{statement_id} does not have an entity value")

    if retrieved_at is None:
        metadata = json.loads(payload_path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
        retrieved_at = metadata["retrievedAt"]

    property_id = statement["mainsnak"]["property"]
    revision = entity["lastrevid"]
    statement_prefix = statement_id.split("$", 1)[1][:8].lower()
    return {
        "id": f"chr:observation:wikidata:{entity_id}:{property_id}:{statement_prefix}:r{revision}",
        "label": label,
        "shortLabel": short_label,
        "sourceSystem": "Wikidata",
        "sourceEntityId": entity_id,
        "predicateExternalId": property_id,
        "objectExternalId": value["id"],
        "externalStatementId": statement_id,
        "qualifierPropertyIds": sorted(statement.get("qualifiers", {})),
        "sourceRevision": revision,
        "retrievedAt": retrieved_at,
        "contentHash": hashlib.sha256(payload_bytes).hexdigest(),
        "rawPayloadUri": payload_path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "status": "observed",
    }
