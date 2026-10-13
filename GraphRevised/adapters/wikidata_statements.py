"""Statement-level SourceObservations from preserved Wikidata entity payloads."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from GraphRevised.proposals.temporal import display_edtf, wikidata_time

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class StatementNotFound(LookupError):
    """The preserved payload does not contain the requested statement."""


# Wikidata's time qualifiers (its data model, not any subject): how each one shapes a time value.
TIME_QUALIFIERS = {"P580": "start", "P582": "end", "P585": "point", "P1319": "earliest", "P1326": "latest"}


def assemble_time(values: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """One time value from Wikidata point, start/end, or earliest/latest values, by precision:
    {edtf, calendar, mode}, mode "during" for a point or span and "within" for an uncertain window.
    A point known only to its decade or century ("1st century BCE") is such a window: sometime
    within it, never throughout it."""
    def part(raw: dict[str, Any], side: str) -> tuple[str, str]:
        edtf, calendar = wikidata_time(raw)
        if "/" in edtf:  # a decade or century: its first year opens, its last year closes
            edtf = edtf.split("/")[0 if side == "start" else 1]
        return edtf, calendar

    if "point" in values:
        edtf, calendar = wikidata_time(values["point"])
        return {"edtf": edtf, "calendar": calendar, "mode": "within" if "/" in edtf else "during"}
    if "start" in values or "end" in values:
        start = part(values["start"], "start") if "start" in values else ("..", None)
        end = part(values["end"], "end") if "end" in values else ("..", None)
        return {"edtf": f"{start[0]}/{end[0]}", "calendar": start[1] or end[1], "mode": "during"}
    earliest = part(values["earliest"], "start") if "earliest" in values else ("..", None)
    latest = part(values["latest"], "end") if "latest" in values else ("..", None)
    return {"edtf": f"{earliest[0]}/{latest[0]}", "calendar": earliest[1] or latest[1], "mode": "within"}


def statement_time(statement: dict[str, Any]) -> dict[str, Any] | None:
    """The normalized time a statement states: its own value for a time statement, else its
    time qualifiers; None when it states none. Raises TimeValueError for a value it cannot read."""
    mainsnak = statement["mainsnak"]
    if mainsnak.get("datatype") == "time":
        value = mainsnak.get("datavalue", {}).get("value")
        return assemble_time({"point": value}) if isinstance(value, dict) else None
    values = {}
    for pid, role in TIME_QUALIFIERS.items():
        snaks = statement.get("qualifiers", {}).get(pid, [])
        value = snaks[0].get("datavalue", {}).get("value") if snaks else None
        if isinstance(value, dict):
            values[role] = value
    return assemble_time(values) if values else None


def carried_qualifiers(statement: dict[str, Any]) -> dict[str, list[Any]]:
    """Every qualifier other than time, as stated: colleague, jurisdiction, ordinal, end cause..."""
    carried = {}
    for pid, snaks in statement.get("qualifiers", {}).items():
        if pid in TIME_QUALIFIERS:
            continue
        values = []
        for snak in snaks:
            value = snak.get("datavalue", {}).get("value")
            values.append(value.get("id", value) if isinstance(value, dict) else value)
        carried[pid] = values
    return carried


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
    entity_id = statement_id.split("$", 1)[0].upper()  # some statement IDs start with a lowercase q
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
    is_time = statement["mainsnak"].get("datatype") == "time"
    if not isinstance(value, dict) or ("id" not in value and not is_time):
        raise StatementNotFound(f"{statement_id} has neither an entity nor a time value")
    time = statement_time(statement)

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
        "objectExternalId": None if is_time else value["id"],
        "externalStatementId": statement_id,
        "qualifierPropertyIds": sorted(statement.get("qualifiers", {})),
        "sourceRevision": revision,
        "retrievedAt": retrieved_at,
        "contentHash": hashlib.sha256(payload_bytes).hexdigest(),
        "rawPayloadUri": payload_path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "status": "observed",
        # recorded by the record_statement_time operation, fixed once set
        "statementTimeEdtf": time["edtf"] if time else None,
        "statementTimeCalendar": time["calendar"] if time else None,
        "statementTimeMode": time["mode"] if time else None,
        "statementTimeDisplay": display_edtf(time["edtf"]) if time else None,
        "statementQualifiers": json.dumps(carried_qualifiers(statement), ensure_ascii=False, sort_keys=True),
    }
