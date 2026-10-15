"""Named access to the Phase 3 direct Cypher operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

OPERATIONS_PATH = Path(__file__).resolve().parent / "13-PHASE-3-DIRECT-OPERATIONS.cypher"

# Statement order in the operations file.
OPERATION_NAMES = (
    "get_node",
    "get_subject",
    "get_neighborhood",
    "get_evidence",
    "get_temporal_context",
    "upsert_entity",
    "upsert_subject",
    "link_subject_focus",
    "link_year",
    "upsert_authority",
    "upsert_observation",
    "upsert_passage_observation",
    "upsert_assertion",
    "link_support",
    "upsert_proposal",
    "upsert_evidence_proposal",
    "link_pending_evidence",
    "decide_proposal",
    "apply_accepted_evidence",
    "reopen_assertion",
    "supersede_assertion",
    "retract_assertion",
    "upsert_qualified_assertion",
    "set_pending_qualifier_quotations",
    "link_assertion_years",
    "link_observation_work",
    "link_promoted_from",
    "upsert_transcription_observation",
    "upsert_annotation",
    "set_annotation_status",
    "delete_annotation",
    "decide_entity",
    "upsert_record_observation",
    "set_work_form",
    "upsert_subject_authority",
    "record_statement_time",
    "renormalize_statement_time",
    "unlink_assertion_years",
    "link_authority",
    "rename_authority_system",
    "merge_authority_into",
    "upsert_locations",
    "link_location_parents",
    "link_modern_locations",
    "link_place_locations",
)


class RefusedWrite(RuntimeError):
    """A guarded write returned zero rows: the operation refused the request."""


def load_operations(path: Path = OPERATIONS_PATH) -> dict[str, str]:
    """Return the operations file as {operation name: Cypher statement}."""
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("//")
    ]
    statements = [part.strip() for part in "\n".join(lines).split(";")]
    statements = [statement for statement in statements if statement]
    if len(statements) != len(OPERATION_NAMES):
        raise ValueError(
            f"{path.name} has {len(statements)} statements; expected {len(OPERATION_NAMES)}"
        )
    return dict(zip(OPERATION_NAMES, statements))


def run_write(tx: Any, operations: dict[str, str], name: str, params: dict[str, Any]) -> list[dict]:
    """Run a guarded write, raising RefusedWrite when it returns zero rows."""
    rows = tx.run(operations[name], params).data()
    if not rows:
        raise RefusedWrite(f"{name} refused: {params}")
    return rows
