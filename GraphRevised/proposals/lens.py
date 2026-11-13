"""A lens for the passage reader: one lens in one scope (39-LENS-SPECIALISTS.md, D-137).

The lens definition comes from curation/lenses.json (purpose, scope rule, questions,
predicates) and its grounding for the scope from curation/lens-grounding/<scope>.json
(native terms, core sources, rules). A lens is a way of reading, never a node (D-039):
it narrows what the reader drafts and names who drafted it, the specialist
`lens-specialist:<lens>/<scope>`.

The reader with a lens drafts claims only with the lens's own predicates. A lens without
predicates in the registry (economic, religious today) drafts passages of note and asks
for predicates instead; it never stretches another lens's.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from .registry import PredicateRegistry

GRAPH_REVISED = Path(__file__).resolve().parents[1]
LENSES_PATH = GRAPH_REVISED / "curation" / "lenses.json"
GROUNDING_DIRECTORY = GRAPH_REVISED / "curation" / "lens-grounding"
SPECIALIST_PREFIX = "lens-specialist:"


@dataclass(frozen=True)
class Lens:
    id: str
    label: str
    purpose: str
    relevance: str
    questions: tuple[str, ...]
    predicates: tuple[str, ...]
    scope: str  # the grounding's file name: a polity, a period, or a discipline
    scope_label: str
    native_terms: tuple[tuple[str, str], ...]
    rules: tuple[str, ...]
    core_sources: tuple[dict[str, Any], ...]
    lenses_version: int | None = None
    grounding_version: int | None = None
    requested: str = ""  # open predicate requests shown to the reading (proposals/predicate_needs.py)

    @property
    def specialist_id(self) -> str:
        """Who drafted what this lens proposes: its `assertedBy`, `createdBy`, and note author."""
        return f"{SPECIALIST_PREFIX}{self.id}/{self.scope}"


def load_lens(lens_id: str, scope: str, *, lenses_path: Path = LENSES_PATH,
              grounding_directory: Path = GROUNDING_DIRECTORY) -> Lens:
    """The lens and its grounding for the scope. Both must exist: a grounding is drafted
    by the agent and reviewed by the curator before a lens reads with it."""
    lenses = json.loads(lenses_path.read_text(encoding="utf-8"))
    definition = next((lens for lens in lenses["lenses"] if lens["id"] == lens_id), None)
    if definition is None:
        known = ", ".join(lens["id"] for lens in lenses["lenses"])
        raise ValueError(f"no lens {lens_id!r} in {lenses_path.name} (known: {known})")
    path = grounding_directory / f"{scope}.json"
    if not path.exists():
        raise ValueError(f"no grounding for scope {scope!r}: {path.name} is drafted and reviewed first")
    grounding = json.loads(path.read_text(encoding="utf-8"))
    grounded = grounding.get("lenses", {}).get(lens_id)
    if grounded is None:
        raise ValueError(f"the {scope} grounding has no {lens_id} lens yet: it is drafted and reviewed first")
    return Lens(
        id=lens_id,
        label=definition["label"],
        purpose=definition["purpose"],
        relevance=definition["relevance"],
        questions=tuple(definition.get("questions", [])),
        predicates=tuple(definition.get("predicates", [])),
        scope=scope,
        scope_label=grounding.get("polity") or grounding.get("scope") or scope,
        native_terms=tuple((term, meaning) for term, meaning in grounded.get("nativeTerms", [])),
        rules=tuple(grounded.get("rules", [])),
        core_sources=tuple(grounded.get("coreSources", [])),
        lenses_version=lenses.get("version"),
        grounding_version=grounding.get("version"),
    )


def lens_registry(registry: PredicateRegistry, lens: Lens) -> PredicateRegistry:
    """The registry narrowed to the lens's predicates, for the prompt. Validation still uses
    the whole registry. A lens predicate missing from the registry is an error in lenses.json."""
    missing = sorted(set(lens.predicates) - set(registry.predicates))
    if missing:
        raise ValueError(f"the {lens.id} lens names predicates the registry lacks: {missing}")
    return replace(registry, predicates={k: v for k, v in registry.predicates.items() if k in lens.predicates})


def lens_text(lens: Lens) -> str:
    """The lens block of the task packet: the same for every passage of a run, so cached."""
    lines = [
        f"Lens: {lens.label}, for {lens.scope_label} (you draft as {lens.specialist_id})",
        f"Purpose: {lens.purpose}",
        f"In scope: {lens.relevance}",
        "Questions this lens asks:",
        *(f"- {question}" for question in lens.questions),
    ]
    if lens.native_terms:
        lines += ["Native terms (to read the source's words; never evidence, never claims):",
                  *(f"- {term}: {meaning}" for term, meaning in lens.native_terms)]
    if lens.rules:
        lines += ["Lens rules:", *(f"- {rule}" for rule in lens.rules)]
    if not lens.predicates:
        lines.append("This lens has no predicates yet: draft no claims; add passages of note, and report "
                     "the relationships it needs under predicate_needs.")
    if lens.requested:
        lines.append(lens.requested)
    return "\n".join(lines)
