"""Shared reading rules and source briefs: how the reader's guidance is composed.

The guidance the reader sees for one source is, in order: the shared rules
(proposals/reading_rules.v1.json: general, event-inquiry, per-predicate, and
by the Work's form), the conventions of the source's brief (briefs/, written
by discovery/source_brief.py), and anything the inquiry itself adds. Briefs
keep their evidence for review; only the conventions reach the reader.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GRAPH_REVISED = Path(__file__).resolve().parents[1]
RULES_PATH = GRAPH_REVISED / "proposals" / "reading_rules.v1.json"
BRIEFS_DIRECTORY = GRAPH_REVISED / "briefs"

# Guidance never points at a passage or quotes the source (18 §20): the reader finds passages itself.
LOCATOR = re.compile(r"\b\d+\.\d+(?:\.\d+)?\b")
QUOTED = re.compile(r"[\"“]([^\"”]+)[\"”]|(?<![A-Za-z])['‘]([^'‘’]+)['’](?![A-Za-z])")


@dataclass(frozen=True)
class ReadingRules:
    version: int
    general: tuple[str, ...]
    event_inquiry: tuple[str, ...]
    predicates: dict[str, str]
    by_form: dict[str, tuple[str, ...]]
    scope: dict[str, Any]

    def guidance(self, *, form: str | None, event_inquiry: bool, predicates: list[str]) -> list[str]:
        lines = list(self.event_inquiry) if event_inquiry else []
        lines += [self.predicates[p] for p in predicates if p in self.predicates]
        lines += list(self.general)
        lines += list(self.by_form.get(form or "", ()))
        return lines


def load_reading_rules(path: Path = RULES_PATH) -> ReadingRules:
    data = json.loads(path.read_text(encoding="utf-8"))
    return ReadingRules(
        version=data["version"],
        general=tuple(data["general"]),
        event_inquiry=tuple(data["eventInquiry"]),
        predicates=dict(data["predicates"]),
        by_form={form: tuple(lines) for form, lines in data["byForm"].items()},
        scope=data["scope"],
    )


def brief_path(work_id: str, directory: Path = BRIEFS_DIRECTORY) -> Path:
    return directory / f"{work_id.rsplit(':', 1)[-1]}.json"


def load_brief(work_id: str, directory: Path = BRIEFS_DIRECTORY) -> dict[str, Any] | None:
    path = brief_path(work_id, directory)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def brief_guidance(brief: dict[str, Any] | None) -> list[str]:
    """The conventions of a brief that passed its checks, without their evidence."""
    return [c["rule"] for c in (brief or {}).get("conventions", [])]


def steering(line: str, source_text: str) -> str | None:
    """Why a guidance line would steer the reader to a passage, or None if it does not."""
    if LOCATOR.search(line):
        return "points at a passage"
    for double, single in QUOTED.findall(line):
        quoted = double or single
        if len(quoted.split()) >= 2 and normalize(quoted) in source_text:
            return "quotes the source"
    return None


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("’", "'")).strip().lower()
