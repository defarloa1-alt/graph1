"""Chrystallum's account of an inquiry's focus, traced statement by statement (29 §4, §4a, §4b).

The account is one stored, versioned file outside the graph. It is a voice of its own, labelled as
ours, and never a witness: attestation does not count it. Every statement it makes is one of three
kinds, so that nothing in it is unaudited prose:

    source     restates what preserved passages say: each citation names the observation, its
               locator, and the verbatim words; it may name the claims it restates (a passage the
               reader turned into no claim may still be cited, 29 §4)
    synthesis  our own reading across the account: marked as ours, citing no passage itself, resting
               on earlier statements of the account, which carry the evidence
    signpost   where the evidence ends ("not yet read: ..."): no citation, and a target for the next
               source plan (31 §3.4)

Sections are the account's narrative order; each names the phases it covers, which are the
historical order (29 §10 item 2). Names in a statement link to Entities by their words.

The contract checks shape; `check` checks the account against the graph through a small reader, so
a quotation that is not in its passage, a claim that was rejected, or a phase or name that does not
exist is reported before the account is shown.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from GraphRevised.proposals.validator import normalize

ACCOUNT_SCHEMA_VERSION = "account-v1"
OUR_VOICE = "Chrystallum"
ACCOUNT_ID_PATTERN = r"^chr:account:[A-Za-z0-9._-]+$"
INQUIRY_ID_PATTERN = r"^chr:inquiry:[A-Za-z0-9._-]+$"
ENTITY_ID_PATTERN = r"^chr:entity:[A-Za-z0-9._:-]+$"
ASSERTION_ID_PATTERN = r"^chr:assertion:[A-Za-z0-9._:#-]+$"
OBSERVATION_ID_PATTERN = r"^chr:observation:[A-Za-z0-9._:-]+$"
LOCAL_ID_PATTERN = r"^[a-z0-9][a-z0-9.-]*$"  # section and statement ids within the account
DEAD_CLAIM_STATUSES = ("rejected", "superseded")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class _Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Citation(_Contract):
    """One preserved passage behind a source statement, with the words that show it."""
    observation_id: str = Field(pattern=OBSERVATION_ID_PATTERN)
    locator: str = Field(min_length=1)  # as shown to the reader, the Work's short name and its locator
    quotation: str = Field(min_length=10, max_length=1500)
    passage_hash: str | None = None  # the passage's hash when cited: a change means the account is stale


class NameLink(_Contract):
    """Words of a statement that name an Entity, linked like Wikipedia's links (29 §4a)."""
    text: str = Field(min_length=1)
    entity_id: str = Field(pattern=ENTITY_ID_PATTERN)


class Statement(_Contract):
    statement_id: str = Field(pattern=LOCAL_ID_PATTERN)
    kind: Literal["source", "synthesis", "signpost"]
    text: str = Field(min_length=3)
    citations: list[Citation] = Field(default_factory=list)
    claim_ids: list[str] = Field(default_factory=list)  # claims the statement restates, if any
    rests_on: list[str] = Field(default_factory=list)  # a synthesis: the earlier statements it draws on
    links: list[NameLink] = Field(default_factory=list)

    @model_validator(mode="after")
    def _kind_rules(self) -> "Statement":
        if self.kind == "source" and not self.citations:
            raise ValueError(f"{self.statement_id}: a source statement cites at least one preserved passage")
        if self.kind == "synthesis":
            if self.citations:
                raise ValueError(f"{self.statement_id}: a synthesis cites no passage; it rests on statements that do")
            if not self.rests_on:
                raise ValueError(f"{self.statement_id}: a synthesis names the statements it rests on")
        if self.kind == "signpost" and (self.citations or self.claim_ids or self.rests_on):
            raise ValueError(f"{self.statement_id}: a signpost marks where evidence ends and cites nothing")
        if self.kind != "synthesis" and self.rests_on:
            raise ValueError(f"{self.statement_id}: only a synthesis rests on other statements")
        bad = [c for c in self.claim_ids if not re.fullmatch(ASSERTION_ID_PATTERN, c)]
        if bad:
            raise ValueError(f"{self.statement_id}: not claim ids: {bad}")
        missing = [link.text for link in self.links if link.text not in self.text]
        if missing:
            raise ValueError(f"{self.statement_id}: linked words not in the statement: {missing}")
        return self


class AccountSection(_Contract):
    section_id: str = Field(pattern=LOCAL_ID_PATTERN)
    title: str = Field(min_length=1)
    phase_ids: list[str] = Field(default_factory=list)  # the phases it covers; none for a framing section
    statements: list[Statement] = Field(min_length=1)

    @model_validator(mode="after")
    def _phases(self) -> "AccountSection":
        bad = [p for p in self.phase_ids if not re.fullmatch(ENTITY_ID_PATTERN, p)]
        if bad:
            raise ValueError(f"{self.section_id}: a phase is an Entity id, not {bad}")
        return self


class Account(_Contract):
    """One stored account of an inquiry's focus. A new version for every change; the old is kept."""
    schema_version: Literal["account-v1"] = ACCOUNT_SCHEMA_VERSION
    account_id: str = Field(pattern=ACCOUNT_ID_PATTERN)
    version: int = Field(ge=1)
    previous_version: int | None = None
    voice: Literal["Chrystallum"] = OUR_VOICE  # shown as Chrystallum's account, never as fact
    inquiry_id: str = Field(pattern=INQUIRY_ID_PATTERN)
    focus_ids: list[str] = Field(min_length=1)
    title: str = Field(min_length=3)
    status: Literal["draft", "proposed", "approved", "superseded"] = "draft"
    written_by: str = Field(min_length=1)  # the model, or the curator
    prompt_version: str | None = None
    written_at: str = Field(default_factory=_now)
    sections: list[AccountSection] = Field(min_length=1)

    @model_validator(mode="after")
    def _consistent(self) -> "Account":
        if self.version > 1 and self.previous_version != self.version - 1:
            raise ValueError("a revised account names the version it replaces")
        if self.version == 1 and self.previous_version is not None:
            raise ValueError("a first account replaces nothing")
        bad = [f for f in self.focus_ids if not re.fullmatch(ENTITY_ID_PATTERN, f)]
        if bad:
            raise ValueError(f"a focus is an Entity id, not {bad}")
        section_ids = [s.section_id for s in self.sections]
        if len(section_ids) != len(set(section_ids)):
            raise ValueError("section ids are unique")
        seen: dict[str, str] = {}
        for statement in self.statements():
            if statement.statement_id in seen:
                raise ValueError(f"statement id {statement.statement_id} is used twice")
            unknown = [r for r in statement.rests_on if r not in seen]
            if unknown:
                raise ValueError(f"{statement.statement_id} rests on {unknown}, which are not earlier statements")
            if any(seen[r] == "signpost" for r in statement.rests_on):
                raise ValueError(f"{statement.statement_id} rests on a signpost, which holds no evidence")
            seen[statement.statement_id] = statement.kind
        return self

    def statements(self) -> list[Statement]:
        return [statement for section in self.sections for statement in section.statements]

    def evidence_of(self, statement_id: str) -> list[Citation]:
        """The passages a statement rests on: its own, or, for a synthesis, those of what it draws on."""
        by_id = {s.statement_id: s for s in self.statements()}
        out: list[Citation] = []
        stack, done = [statement_id], set()
        while stack:
            current = by_id[stack.pop()]
            if current.statement_id in done:
                continue
            done.add(current.statement_id)
            out += current.citations
            stack += current.rests_on
        return out

    def trace(self) -> list[dict[str, Any]]:
        """Section by section: each statement with its phases, kind, claims, and passages (1f2(d))."""
        return [{"section": section.section_id, "phases": section.phase_ids, "statement": s.statement_id,
                 "kind": s.kind, "claims": s.claim_ids,
                 "passages": sorted({c.observation_id for c in self.evidence_of(s.statement_id)})}
                for section in self.sections for s in section.statements]

    def revise(self, sections: list[AccountSection], written_by: str,
               prompt_version: str | None = None) -> "Account":
        return self.model_validate(self.model_dump() | {
            "version": self.version + 1, "previous_version": self.version, "status": "draft",
            "sections": [s.model_dump() for s in sections], "written_by": written_by,
            "prompt_version": prompt_version, "written_at": _now()})

    def save(self, directory: Path) -> Path:
        path = directory / f"{self.account_id.split(':', 2)[2]}.v{self.version}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((self.model_dump_json(indent=2) + "\n").encode("utf-8"))
        return path

    @classmethod
    def load(cls, path: Path) -> "Account":
        return cls.model_validate(json.loads(path.read_text(encoding="utf-8")))


# --- Checked against the graph ---------------------------------------------------------------------

class AccountReader(Protocol):
    def observations(self, ids: list[str]) -> dict[str, dict[str, Any]]: ...  # id -> passageText, editorialNotes, passageHash
    def claim_statuses(self, ids: list[str]) -> dict[str, str]: ...
    def entities(self, ids: list[str]) -> set[str]: ...


class Neo4jAccountReader:
    """The reader over an open transaction; read-only."""

    def __init__(self, tx: Any) -> None:
        self.tx = tx

    def observations(self, ids: list[str]) -> dict[str, dict[str, Any]]:
        rows = self.tx.run("MATCH (o:SourceObservation) WHERE o.id IN $ids "
                           "RETURN o.id AS id, o.passageText AS passageText, o.editorialNotes AS editorialNotes, "
                           "o.passageHash AS passageHash", ids=ids).data()
        return {r["id"]: r for r in rows}

    def claim_statuses(self, ids: list[str]) -> dict[str, str]:
        rows = self.tx.run("MATCH (a:Assertion) WHERE a.id IN $ids RETURN a.id AS id, a.status AS status",
                           ids=ids).data()
        return {r["id"]: r["status"] for r in rows}

    def entities(self, ids: list[str]) -> set[str]:
        rows = self.tx.run("MATCH (e:Entity) WHERE e.id IN $ids AND e.status <> 'deprecated' RETURN e.id AS id",
                           ids=ids).data()
        return {r["id"] for r in rows}


def check(account: Account, reader: AccountReader) -> list[str]:
    """Every problem that keeps the account from being shown: an empty list when it is sound."""
    statements = account.statements()
    citations = [(s.statement_id, c) for s in statements for c in s.citations]
    observations = reader.observations(sorted({c.observation_id for _, c in citations}))
    problems = []
    for statement_id, c in citations:
        o = observations.get(c.observation_id)
        if o is None:
            problems.append(f"{statement_id}: {c.observation_id} is not a preserved observation")
            continue
        quote = normalize(c.quotation)
        if quote not in normalize(o.get("passageText") or ""):
            if any(quote in normalize(n) for n in o.get("editorialNotes") or []):
                problems.append(f"{statement_id}: the words cited from {c.locator} are an editorial note")
            else:
                problems.append(f"{statement_id}: the words cited are not in {c.locator}")
        if c.passage_hash and o.get("passageHash") and c.passage_hash != o["passageHash"]:
            problems.append(f"{statement_id}: {c.locator} has changed since it was cited")
    claims = sorted({c for s in statements for c in s.claim_ids})
    statuses = reader.claim_statuses(claims)
    for s in statements:
        for claim in s.claim_ids:
            status = statuses.get(claim)
            if status is None:
                problems.append(f"{s.statement_id}: no claim {claim}")
            elif status in DEAD_CLAIM_STATUSES:
                problems.append(f"{s.statement_id}: claim {claim} is {status}")
    wanted = {p for section in account.sections for p in section.phase_ids}
    wanted |= {link.entity_id for s in statements for link in s.links} | set(account.focus_ids)
    present = reader.entities(sorted(wanted))
    for section in account.sections:
        problems += [f"{section.section_id}: no phase {p}" for p in section.phase_ids if p not in present]
    problems += [f"{s.statement_id}: '{link.text}' links to no Entity {link.entity_id}"
                 for s in statements for link in s.links if link.entity_id not in present]
    problems += [f"no focus {f}" for f in account.focus_ids if f not in present]
    return problems
