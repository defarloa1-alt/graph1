"""The typed contract a proposer (script or agent) may submit."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DRAFT_SCHEMA_VERSION = "proposal-draft-v6"
LOCAL_ID_PATTERN = r"^chr:[a-z]+:[A-Za-z0-9._:-]+$"
# An ISO 8601 duration from the context event: P4D (the fifth day), PT6H.
DURATION_PATTERN = r"^P(\d+Y)?(\d+M)?(\d+W)?(\d+D)?(T(\d+H)?(\d+M)?(\d+S)?)?$"


class Quotation(BaseModel):
    """The verbatim span of a passage observation that supports the draft."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    observation_id: str = Field(pattern=LOCAL_ID_PATTERN)
    text: str = Field(min_length=15, max_length=1500)


class QualifierQuotation(BaseModel):
    """The verbatim span that shows one qualifier: the role, the time, the
    context event, or the quantity. Shorter spans are allowed ("cos. 32")."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    observation_id: str = Field(pattern=LOCAL_ID_PATTERN)
    supports: Literal["role", "time", "context", "quantity"]
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
    # during: true throughout (or at) the value; within: at some point inside an uncertain window
    mode: Literal["during", "within"] = "during"

    @model_validator(mode="after")
    def _normalized_fields_go_together(self) -> "TimeQualifier":
        if (self.edtf is None) != (self.calendar is None) or (self.edtf is None) != (self.normalization_basis is None):
            raise ValueError("edtf, calendar, and normalization_basis are given together or not at all")
        if self.relative_offset is not None and self.relative_offset.rstrip("T") == "P":
            raise ValueError("relative_offset needs at least one duration component")
        if self.mode == "within" and self.edtf is None:
            raise ValueError("an uncertain window needs its normalized bounds")
        return self


class QuantityQualifier(BaseModel):
    """How many: of a component in its whole (thirty units in a larger unit) or
    of holders elected (two a year). An establishment or a count as a source
    gives it, never a headcount: `minimum` and `maximum` for a range,
    `typical` for a usual figure, `source_expression` the source's words."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_expression: str = Field(min_length=1, max_length=500)
    minimum: int | None = Field(default=None, ge=0)
    maximum: int | None = Field(default=None, ge=0)
    typical: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _a_consistent_figure(self) -> "QuantityQualifier":
        if self.minimum is None and self.maximum is None and self.typical is None:
            raise ValueError("a quantity gives at least one of minimum, maximum, and typical")
        low = self.minimum if self.minimum is not None else self.typical
        high = self.maximum if self.maximum is not None else self.typical
        if low is not None and high is not None and low > high:
            raise ValueError("a quantity's minimum cannot exceed its maximum (or its typical figure)")
        if self.typical is not None and not (
                (self.minimum is None or self.minimum <= self.typical)
                and (self.maximum is None or self.typical <= self.maximum)):
            raise ValueError("a quantity's typical figure lies between its minimum and maximum")
        return self

    def signature(self) -> dict[str, int]:
        """The figures that make a quantified claim a different claim; the wording does not."""
        return {key: value for key, value in (("minimum", self.minimum), ("maximum", self.maximum),
                                              ("typical", self.typical)) if value is not None}

    def display(self) -> str:
        if self.minimum is not None and self.maximum is not None:
            figure = str(self.minimum) if self.minimum == self.maximum else f"{self.minimum}–{self.maximum}"
        elif self.minimum is not None:
            figure = f"at least {self.minimum}"
        elif self.maximum is not None:
            figure = f"at most {self.maximum}"
        else:
            figure = ""
        if self.typical is not None:
            figure = f"{figure}, usually {self.typical}" if figure else str(self.typical)
        return figure


class ProposalDraft(BaseModel):
    """A candidate assertion and the evidence offered for it.

    A draft names existing local nodes only. It cannot create entities,
    carry Cypher, or set a status; labels and IDs are derived deterministically
    when the draft is stored. Every passage observation it cites needs a
    verbatim quotation from that passage. A unary predicate has no object.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["proposal-draft-v4", "proposal-draft-v5", "proposal-draft-v6"] = DRAFT_SCHEMA_VERSION
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
    quantity: QuantityQualifier | None = None
    qualifier_quotations: tuple[QualifierQuotation, ...] = ()

    @model_validator(mode="after")
    def _qualifier_fields_go_together(self) -> "ProposalDraft":
        if (self.mode == "attributed") != (self.attributed_to is not None):
            raise ValueError("an attributed claim names attributed_to; an asserted claim does not")
        if (self.context_id is None) != (self.context_basis is None):
            raise ValueError("context_id and context_basis are given together")
        return self
