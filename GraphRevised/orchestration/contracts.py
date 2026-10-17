"""The typed contracts of one command (31-ONE-COMMAND.md §3): what the front door plans, what the
orchestrator records, and what the reconciler and the critic return.

Everything here is run state, kept in a file per run outside the graph (02 §1). A candidate entity
or a relationship need in an orientation brief is a planning artifact, never a graph node or a
ProposalDraft: only workers that go through proposals/ write to the graph, and only by proposal.

Models choose and interpret (which identity, which sources, which lenses, what a passage shows);
these contracts make their choices inspectable and resumable, and refuse what is malformed.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RUN_STATE_SCHEMA_VERSION = "inquiry-run-v1"
LOCAL_ID_PATTERN = r"^chr:[a-z]+:[A-Za-z0-9._:-]+$"
QID_PATTERN = r"^Q[1-9][0-9]*$"
ITEM_ID_PATTERN = r"^P[0-9]{2,3}$"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class _Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- The front door ------------------------------------------------------------------------------

class RunMode(str, Enum):
    """How much the curator decides before and during a run (31 §3.5)."""
    GUIDED = "guided"          # every plan item is approved, rejected, modified, or deferred first
    SUPERVISED = "supervised"  # the scope is approved; items run unless rejected or deferred
    AUTONOMOUS = "autonomous"  # the plan is shown and runs; everything stays proposed until promotion


SubjectKind = Literal["Person", "Event", "Place", "Polity", "Group", "Office", "Type", "Concept", "Period",
                      "Work", "Constellation"]


class ScopeDecision(_Contract):
    """08: is the request for historical graph construction?"""
    decision: Literal["IN_SCOPE", "OUT_OF_SCOPE", "REFRAME_REQUIRED"]
    primary_intent: str = Field(min_length=3)
    explanation: str = Field(min_length=10)
    reframings: list[str] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def _reframings_when_needed(self) -> "ScopeDecision":
        if self.decision != "IN_SCOPE" and not self.reframings:
            raise ValueError("a request out of scope or needing a reframe offers historical reframings")
        return self


class IdentityCandidate(_Contract):
    """One thing the command may name, with the authority's own label beside its code (rule 17)."""
    label: str = Field(min_length=1)
    description: str | None = None
    kind: SubjectKind
    qid: str | None = Field(default=None, pattern=QID_PATTERN)
    local_entity_id: str | None = Field(default=None, pattern=LOCAL_ID_PATTERN)
    why: str = Field(min_length=3)


class ResolvedFocus(_Contract):
    status: Literal["resolved", "ambiguous", "unresolved"]
    chosen: IdentityCandidate | None = None
    candidates: list[IdentityCandidate] = Field(default_factory=list)
    decided_by: str | None = None  # an agent id, or the curator once asked

    @model_validator(mode="after")
    def _consistent(self) -> "ResolvedFocus":
        if self.status == "resolved" and (self.chosen is None or not self.decided_by):
            raise ValueError("a resolved focus names its choice and who made it")
        if self.status == "ambiguous" and len(self.candidates) < 2:
            raise ValueError("an ambiguous focus lists at least two candidates")
        return self


class AuthorityMatch(_Contract):
    """A subject heading or identity record for the inquiry, checked at its authority."""
    system: str = Field(min_length=2)  # LCSH, FAST, Wikidata, Pleiades, ...
    identifier: str = Field(min_length=1)
    label: str = Field(min_length=1)  # read from the record, never typed
    match_type: Literal["exact", "close", "broader", "narrower", "related", "candidate"]
    checked_at: str | None = None

    @model_validator(mode="after")
    def _checked_unless_candidate(self) -> "AuthorityMatch":
        if self.match_type != "candidate" and not self.checked_at:
            raise ValueError("a match other than a candidate was checked at the authority: give checked_at")
        return self


class SubjectAnchor(_Contract):
    """The Subject the inquiry belongs to (28): an existing one, or a proposed one labelled as ours."""
    subject_id: str | None = Field(default=None, pattern=LOCAL_ID_PATTERN)
    proposed_label: str | None = None
    matches: list[AuthorityMatch] = Field(default_factory=list)
    provisional: bool

    @model_validator(mode="after")
    def _anchor(self) -> "SubjectAnchor":
        if (self.subject_id is None) == (self.proposed_label is None):
            raise ValueError("an anchor is either an existing Subject or a proposed label")
        if not self.provisional and not any(m.match_type == "exact" for m in self.matches):
            raise ValueError("a Subject without an exact heading is provisional (28 §6)")
        return self


class Gap(_Contract):
    kind: Literal["entity", "relationship", "source", "period", "place", "phase", "other"]
    description: str = Field(min_length=3)
    why: str = Field(min_length=3)


class CoverageMap(_Contract):
    """What the graph already holds for the focus, read before anything is planned."""
    read_at: str = Field(default_factory=_now)
    reused_entity_ids: list[str] = Field(default_factory=list)
    claims_by_status: dict[str, int] = Field(default_factory=dict)
    open_proposals: int = 0
    works_read: list[str] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)


class CandidateEntity(_Contract):
    """A thing the orientation expects the inquiry to meet. Run state only: not a graph node."""
    label: str = Field(min_length=1)
    kind: SubjectKind
    qid: str | None = Field(default=None, pattern=QID_PATTERN)
    why: str = Field(min_length=3)


class RelationshipNeed(_Contract):
    """A relationship the inquiry should establish or test. Run state only: not a claim."""
    subject: str
    predicate: str | None = None  # a registry predicate, or None when none fits yet
    object: str | None = None
    why: str = Field(min_length=3)


class OrientationStatement(_Contract):
    """What the orientation learned, with where it came from: reconnaissance, never evidence."""
    text: str = Field(min_length=3)
    source: str = Field(min_length=3)  # a URL, a QID with revision, or an observation id


class SourceCandidate(_Contract):
    author: str | None = None
    work: str = Field(min_length=1)
    kind: Literal["primary", "modern", "reference", "creative", "material", "dataset"]
    perspective: str | None = None
    why: str = Field(min_length=3)


class Choice(_Contract):
    """A federation or a lens chosen for the inquiry, with the reason."""
    name: str = Field(min_length=2)
    why: str = Field(min_length=3)


class OrientationBrief(_Contract):
    """The general orientation (a workflow stage, not a lens): enough of the subject to plan it."""
    focus: ResolvedFocus
    kind: SubjectKind
    earliest_year: int | None = None  # Chrystallum numbering: BCE negative, no year zero
    latest_year: int | None = None
    places: list[str] = Field(default_factory=list)
    candidates: list[CandidateEntity] = Field(default_factory=list)
    relationship_needs: list[RelationshipNeed] = Field(default_factory=list)
    federations: list[Choice] = Field(default_factory=list)
    sources: list[SourceCandidate] = Field(default_factory=list)
    lenses: list[Choice] = Field(default_factory=list)
    controversies: list[str] = Field(default_factory=list)
    identity_traps: list[str] = Field(default_factory=list)
    statements: list[OrientationStatement] = Field(default_factory=list)
    stopping_rule: str = Field(min_length=3)

    @model_validator(mode="after")
    def _bounds(self) -> "OrientationBrief":
        for year in (self.earliest_year, self.latest_year):
            if year == 0:
                raise ValueError("there is no year zero (03 §3)")
        if self.earliest_year is not None and self.latest_year is not None and self.earliest_year > self.latest_year:
            raise ValueError("the earliest year comes before the latest")
        return self


# --- The plan ------------------------------------------------------------------------------------

PlanAction = Literal[
    "FIRST_CONTACT", "HARVEST", "EXPAND", "WIKIPEDIA_CONTACT", "ENRICH", "SOURCE_PLAN", "BUILD_INQUIRY",
    "BRIEF", "FIND", "READ", "LENS", "PHASES", "RECONCILE", "CRITIQUE", "ACCOUNT", "SUB_INQUIRY",
]


class PlanDecision(_Contract):
    status: Literal["awaiting", "approved", "rejected", "modified", "deferred"] = "awaiting"
    by: str | None = None
    at: str | None = None
    note: str | None = None

    @model_validator(mode="after")
    def _decided_by_someone(self) -> "PlanDecision":
        if self.status != "awaiting" and not (self.by and self.at):
            raise ValueError("a decision records who made it and when")
        if self.status == "modified" and not self.note:
            raise ValueError("a modification says what changed")
        return self


class PlanItem(_Contract):
    item_id: str = Field(pattern=ITEM_ID_PATTERN)  # stable across plan versions
    action: PlanAction
    target: str = Field(min_length=1)  # what it acts on: an entity, a Work, a lens, a sub-inquiry
    rationale: str = Field(min_length=10)
    expected_outputs: list[str] = Field(min_length=1)
    budget_usd: float = Field(ge=0)
    depends_on: list[str] = Field(default_factory=list)
    lens: str | None = None
    decision: PlanDecision = Field(default_factory=PlanDecision)


class InquiryPlan(_Contract):
    """The front door's line-item plan. A decision or an edit makes a new version; the old stays."""
    plan_id: str = Field(min_length=1)
    version: int = Field(ge=1)
    previous_version: int | None = None
    command: str = Field(min_length=1)
    mode: RunMode
    scope: ScopeDecision
    focus: ResolvedFocus
    subject: SubjectAnchor | None = None
    coverage: CoverageMap
    recipe: SubjectKind
    lenses: list[Choice] = Field(default_factory=list)
    items: list[PlanItem]
    stopping_rules: list[str] = Field(min_length=1)
    unresolved_questions: list[str] = Field(default_factory=list)
    budget_usd: float = Field(gt=0)
    scope_approved: bool = False  # supervised mode runs once the curator approves the scope

    @model_validator(mode="after")
    def _well_formed(self) -> "InquiryPlan":
        ids = [item.item_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("plan item ids are unique")
        seen: set[str] = set()
        for item in self.items:
            unknown = [d for d in item.depends_on if d not in seen]
            if unknown:
                raise ValueError(f"{item.item_id} depends on {unknown}, which are not earlier items")
            seen.add(item.item_id)
        if sum(item.budget_usd for item in self.items) > self.budget_usd + 1e-9:
            raise ValueError("the items' budgets exceed the plan's")
        if self.scope.decision != "IN_SCOPE" and self.items:
            raise ValueError("a request not in scope has no plan items")
        if self.version > 1 and self.previous_version != self.version - 1:
            raise ValueError("a revised plan names the version it replaces")
        return self

    def item(self, item_id: str) -> PlanItem:
        return next(i for i in self.items if i.item_id == item_id)

    def decide(self, item_id: str, decision: PlanDecision) -> "InquiryPlan":
        """A new version with one item's decision; the plan itself is unchanged."""
        self.item(item_id)
        items = [i.model_copy(update={"decision": decision}) if i.item_id == item_id else i for i in self.items]
        return self.model_validate(self.model_dump() | {
            "items": [i.model_dump() for i in items], "version": self.version + 1, "previous_version": self.version})

    def approve_all(self, by: str, at: str | None = None) -> "InquiryPlan":
        """A new version with every item still awaiting a decision approved (32 decision 2); items
        already rejected, modified, or deferred keep their decision."""
        decision = PlanDecision(status="approved", by=by, at=at or _now(), note="approve all")
        items = [i.model_copy(update={"decision": decision}) if i.decision.status == "awaiting" else i
                 for i in self.items]
        return self.model_validate(self.model_dump() | {
            "items": [i.model_dump() for i in items], "version": self.version + 1, "previous_version": self.version})

    def runnable(self, item: PlanItem) -> bool:
        """Whether the mode lets this item run, by its decision alone (dependencies aside)."""
        status = item.decision.status
        if status in ("rejected", "deferred"):
            return False
        if self.mode is RunMode.GUIDED:
            return status in ("approved", "modified")
        if self.mode is RunMode.SUPERVISED:
            return self.scope_approved
        return True


# --- Running it ----------------------------------------------------------------------------------

class WorkerAssignment(_Contract):
    assignment_id: str = Field(min_length=1)
    item_id: str = Field(pattern=ITEM_ID_PATTERN)
    worker: str = Field(min_length=3)  # the module run, e.g. GraphRevised.discovery.event_phases
    arguments: list[str] = Field(default_factory=list)
    lens: str | None = None
    idempotency_key: str = Field(min_length=8)
    started_at: str = Field(default_factory=_now)


class CoverageContribution(_Contract):
    """What one worker added, measured in what is new and independent, not in volume (31 §3.8):
    the measure by which a run decides that more reading has stopped paying."""
    new_entities: int = Field(default=0, ge=0)
    new_claim_families: int = Field(default=0, ge=0)
    new_evidence: int = Field(default=0, ge=0)  # evidence added to claims already stored
    new_traditions: int = Field(default=0, ge=0)  # evidence from a tradition the claim did not have
    new_evidence_classes: list[str] = Field(default_factory=list)  # e.g. coin, inscription, papyrus
    gaps_closed: list[str] = Field(default_factory=list)


class WorkerResult(_Contract):
    assignment_id: str
    status: Literal["ok", "failed", "refused", "stopped"]
    outputs: list[str] = Field(default_factory=list)  # files written, plan files, proposal ids
    proposal_ids: list[str] = Field(default_factory=list)
    model: str | None = None
    prompt_version: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = Field(default=0, ge=0)
    coverage: CoverageContribution = Field(default_factory=CoverageContribution)
    error: str | None = None
    finished_at: str = Field(default_factory=_now)

    @model_validator(mode="after")
    def _failure_says_why(self) -> "WorkerResult":
        if self.status != "ok" and not self.error:
            raise ValueError("a result that is not ok says why")
        return self


class Reconciliation(str, Enum):
    EXACT_DUPLICATE = "EXACT_DUPLICATE"            # the same claim: nothing new
    EVIDENCE_ADDITION = "EVIDENCE_ADDITION"        # the same claim, new evidence
    QUALIFIER_ADDITION = "QUALIFIER_ADDITION"      # adds time, role, context, quantity, or place
    ALTERNATE_VOICE = "ALTERNATE_VOICE"            # the same matter in another source's voice
    CONFLICT = "CONFLICT"                          # incompatible with a stored claim: keep both
    NEW_CLAIM = "NEW_CLAIM"
    IDENTITY_UNRESOLVED = "IDENTITY_UNRESOLVED"    # held outside the graph until identity is decided
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class ReconciliationDecision(_Contract):
    """How one candidate claim relates to the graph. The reconciler classifies; it never merges."""
    candidate: str = Field(min_length=1)  # the draft's key in the worker's output
    classification: Reconciliation
    matched_assertion_ids: list[str] = Field(default_factory=list)
    explanation: str = Field(min_length=3)
    decided_by: str = Field(min_length=1)  # "deterministic" or a model id

    @model_validator(mode="after")
    def _matches_when_related(self) -> "ReconciliationDecision":
        related = {Reconciliation.EXACT_DUPLICATE, Reconciliation.EVIDENCE_ADDITION,
                   Reconciliation.QUALIFIER_ADDITION, Reconciliation.ALTERNATE_VOICE, Reconciliation.CONFLICT}
        if self.classification in related and not self.matched_assertion_ids:
            raise ValueError(f"{self.classification.value} names the stored claims it relates to")
        return self


class Verdict(str, Enum):
    SUPPORTED_AS_WRITTEN = "SUPPORTED_AS_WRITTEN"
    SUPPORTED_IF_MODIFIED = "SUPPORTED_IF_MODIFIED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    WRONG_PREDICATE = "WRONG_PREDICATE"
    IDENTITY_UNRESOLVED = "IDENTITY_UNRESOLVED"
    DUPLICATE = "DUPLICATE"
    CONFLICT_REQUIRES_PRESERVATION = "CONFLICT_REQUIRES_PRESERVATION"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    ESCALATE_TO_CURATOR = "ESCALATE_TO_CURATOR"


class CriticVerdict(_Contract):
    """An independent model's reading of one stored proposal. It advises; it decides nothing (21)."""
    proposal_id: str = Field(pattern=LOCAL_ID_PATTERN)
    verdict: Verdict
    modification: str | None = None
    explanation: str = Field(min_length=3)
    critic_model: str = Field(min_length=1)
    prompt_version: str = Field(min_length=3)
    saw_rationale: bool  # whether the proposer's rationale was in the evidence packet (blind first)

    @model_validator(mode="after")
    def _modification_when_needed(self) -> "CriticVerdict":
        if (self.verdict is Verdict.SUPPORTED_IF_MODIFIED) != bool(self.modification):
            raise ValueError("a supported-if-modified verdict, and only that verdict, says what to modify")
        return self


class Interrupt(_Contract):
    """A question for the curator that stops the run until answered."""
    interrupt_id: str = Field(min_length=1)
    reason: Literal["identity", "scope", "cost", "rights", "merge", "deviation", "plan"]
    question: str = Field(min_length=5)
    options: list[str] = Field(default_factory=list)
    item_id: str | None = None
    raised_at: str = Field(default_factory=_now)
    answer: str | None = None
    answered_by: str | None = None
    answered_at: str | None = None

    @property
    def open(self) -> bool:
        return self.answer is None


class RunStatus(str, Enum):
    PLANNING = "planning"
    AWAITING_USER = "awaiting_user"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    DONE = "done"
    FAILED = "failed"


class InquiryRunState(_Contract):
    """One command's run, resumable from its file. Workflow state, never graph data."""
    schema_version: Literal["inquiry-run-v1"] = RUN_STATE_SCHEMA_VERSION
    run_id: str = Field(min_length=1)
    command: str = Field(min_length=1)
    mode: RunMode
    owner: str = Field(min_length=1)  # whose workspace the run's candidates and notes belong to (32 §2.3)
    visibility: Literal["private", "shared", "public"] = "private"
    status: RunStatus = RunStatus.PLANNING
    created_at: str = Field(default_factory=_now)
    orientation: OrientationBrief | None = None
    plan: InquiryPlan | None = None
    plan_versions: list[int] = Field(default_factory=list)
    assignments: list[WorkerAssignment] = Field(default_factory=list)
    results: list[WorkerResult] = Field(default_factory=list)
    reconciliations: list[ReconciliationDecision] = Field(default_factory=list)
    verdicts: list[CriticVerdict] = Field(default_factory=list)
    interrupts: list[Interrupt] = Field(default_factory=list)
    spent_usd: float = Field(default=0, ge=0)
    stopping_explanation: str | None = None

    @model_validator(mode="after")
    def _consistent(self) -> "InquiryRunState":
        if self.status in (RunStatus.DONE, RunStatus.STOPPED, RunStatus.FAILED) and not self.stopping_explanation:
            raise ValueError("a finished run says why it stopped")
        if self.status is RunStatus.RUNNING and self.plan is None:
            raise ValueError("a running run has a plan")
        if self.status is RunStatus.RUNNING and self.open_interrupts():
            raise ValueError("a run with an open question is awaiting the user, not running")
        if self.plan is not None and self.plan.mode is not self.mode:
            raise ValueError("the plan's mode is the run's")
        assigned = {a.assignment_id for a in self.assignments}
        if any(r.assignment_id not in assigned for r in self.results):
            raise ValueError("every result answers an assignment")
        return self

    def open_interrupts(self) -> list[Interrupt]:
        return [i for i in self.interrupts if i.open]

    def done_items(self) -> set[str]:
        ok = {r.assignment_id for r in self.results if r.status == "ok"}
        return {a.item_id for a in self.assignments if a.assignment_id in ok}

    def next_item(self) -> PlanItem | None:
        """The first item, in plan order, that its decision lets run, whose dependencies are done,
        and that has not run; None when nothing can run now (finished, or waiting for the curator)."""
        if self.plan is None or self.open_interrupts():
            return None
        done = self.done_items()
        attempted = {a.item_id for a in self.assignments}
        for item in self.plan.items:
            if item.item_id in attempted or not self.plan.runnable(item):
                continue
            if all(d in done for d in item.depends_on):
                return item
        return None

    def remaining_budget(self) -> float:
        return (self.plan.budget_usd if self.plan else 0) - self.spent_usd

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((self.model_dump_json(indent=2) + "\n").encode("utf-8"))

    @classmethod
    def load(cls, path: Path) -> "InquiryRunState":
        return cls.model_validate(json.loads(path.read_text(encoding="utf-8")))
