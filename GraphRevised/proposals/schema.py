"""The typed contract a proposer (script or agent) may submit."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DRAFT_SCHEMA_VERSION = "proposal-draft-v4"
LOCAL_ID_PATTERN = r"^chr:[a-z]+:[A-Za-z0-9._:-]+$"
# An ISO 8601 duration from the context event: P4D (the fifth day), PT6H.
DURATION_PATTERN = r"^P(\d+Y)?(\d+M)?(\d+W)?(\d+D)?(T(\d+H)?(\d+M)?(\d+S)?)?$"


class Quotation(BaseModel):
    """The verbatim span of a passage observation that supports the draft."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    observation_id: str = Field(pattern=LOCAL_ID_PATTERN)
    text: str = Field(min_length=15, max_length=1500)


class QualifierQuotation(BaseModel):
    """The verbatim span that shows one qualifier: the role, the time, or the
    context event. Shorter spans are allowed ("cos. 32")."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    observation_id: str = Field(pattern=LOCAL_ID_PATTERN)
    supports: Literal["role", "time", "context"]
    text: str = Field(min_length=3, max_length=1500)


class TimeQualifier(BaseModel):
    """When the relationship holds. `source_expression` is the source's own
    wording, verbatim; `edtf` the normalized value, given only when the source
    states a date or a cited conversion supplies one."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_expression: str = Field(min_length=1, max_length=500)
    edtf: str | None = Field(default=None, max_length=100)
    calendar: Literal["julian", "gregorian"] | None = None
    normalization_basis: Literal["source", "scholarship", "curator"] | None = None
    relative_offset: str | None = Field(default=None, pattern=DURATION_PATTERN)

    @model_validator(mode="after")
    def _normalized_fields_go_together(self) -> "TimeQualifier":
        if (self.edtf is None) != (self.calendar is None) or (self.edtf is None) != (self.normalization_basis is None):
            raise ValueError("edtf, calendar, and normalization_basis are given together or not at all")
        if self.relative_offset is not None and self.relative_offset.rstrip("T") == "P":
            raise ValueError("relative_offset needs at least one duration component")
        return self


class ProposalDraft(BaseModel):
    """A candidate assertion and the evidence offered for it.

    A draft names existing local nodes only. It cannot create entities,
    carry Cypher, or set a status; labels and IDs are derived deterministically
    when the draft is stored. Every passage observation it cites needs a
    verbatim quotation from that passage. A unary predicate has no object.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["proposal-draft-v4"] = DRAFT_SCHEMA_VERSION
    predicate: str = Field(min_length=1)
    subject_id: str = Field(pattern=LOCAL_ID_PATTERN)
    object_id: str | None = Field(default=None, pattern=LOCAL_ID_PATTERN)
    observation_ids: tuple[str, ...] = Field(min_length=1)
    rationale: str = Field(min_length=10, max_length=2000)
    proposed_by: str = Field(min_length=1)
    prompt_version: str | None = None
    model_id: str | None = None
    ambiguities: tuple[str, ...] = ()
    quotations: tuple[Quotation, ...] = ()
    inquiry_id: str | None = None
    relevance: str | None = Field(default=None, max_length=1000)
    mode: Literal["asserted", "attributed"] = "asserted"
    attributed_to: str | None = Field(default=None, pattern=LOCAL_ID_PATTERN)
    context_id: str | None = Field(default=None, pattern=LOCAL_ID_PATTERN)
    context_basis: Literal["quotation", "inquiry"] | None = None
    role_id: str | None = Field(default=None, pattern=LOCAL_ID_PATTERN)
    time: TimeQualifier | None = None
    qualifier_quotations: tuple[QualifierQuotation, ...] = ()

    @model_validator(mode="after")
    def _qualifier_fields_go_together(self) -> "ProposalDraft":
        if (self.mode == "attributed") != (self.attributed_to is not None):
            raise ValueError("an attributed claim names attributed_to; an asserted claim does not")
        if (self.context_id is None) != (self.context_basis is None):
            raise ValueError("context_id and context_basis are given together")
        return self
