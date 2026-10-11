"""The typed contract a proposer (script or agent) may submit."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DRAFT_SCHEMA_VERSION = "proposal-draft-v1"
LOCAL_ID_PATTERN = r"^chr:[a-z]+:[A-Za-z0-9._:-]+$"


class ProposalDraft(BaseModel):
    """A candidate assertion and the evidence offered for it.

    A draft names existing local nodes only. It cannot create entities,
    carry Cypher, or set a status; labels and IDs are derived deterministically
    when the draft is stored.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["proposal-draft-v1"] = DRAFT_SCHEMA_VERSION
    predicate: str = Field(min_length=1)
    subject_id: str = Field(pattern=LOCAL_ID_PATTERN)
    object_id: str = Field(pattern=LOCAL_ID_PATTERN)
    observation_ids: tuple[str, ...] = Field(min_length=1)
    rationale: str = Field(min_length=10, max_length=2000)
    proposed_by: str = Field(min_length=1)
    prompt_version: str | None = None
    model_id: str | None = None
    ambiguities: tuple[str, ...] = ()
