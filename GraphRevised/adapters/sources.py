"""One interface over passage sources, chosen by an inquiry's `source.type`.

    perseus-tei        {"edition": <preserved TEI path>, "chapters": "61-68"}
    lacuscurtius-html  {"pages": [<preserved page paths>], "chapters": "50.11-51.2", "translator": ...}

Paths are relative to the GraphRevised directory. `chapters` selects what a
run reads; `refs(None)` lists every section, for context windows.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import lacuscurtius_passages, perseus_passages


@dataclass(frozen=True)
class PassageSource:
    author: str
    title: str
    translator: str | None
    citation: str
    refs: Callable[[str | None], list[str]]
    observation: Callable[[str], dict[str, Any]]


def open_source(config: dict[str, Any], base: Path) -> PassageSource:
    kind = config.get("type", "perseus-tei")
    if kind == "perseus-tei":
        return _perseus(config, base)
    if kind == "lacuscurtius-html":
        return _lacuscurtius(config, base)
    raise ValueError(f"unknown source type {kind!r}")


def _perseus(config: dict[str, Any], base: Path) -> PassageSource:
    path = base / config["edition"]
    metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    edition = perseus_passages.load_edition(path, source_commit=path.stem.rsplit("-", 1)[1],
                                            rights=metadata.get("rights"))

    def refs(selection: str | None) -> list[str]:
        first, last = (int(n) for n in (selection or "1-999").split("-"))
        return perseus_passages.section_refs(edition, range(first, last + 1))

    return PassageSource(
        author=edition.author, title=edition.title, translator=edition.translator, citation=edition.citation,
        refs=refs,
        observation=lambda ref: perseus_passages.passage_observation(
            edition, ref, retrieved_at=metadata["retrievedAt"], source_uri=metadata["sourceUri"]),
    )


def _lacuscurtius(config: dict[str, Any], base: Path) -> PassageSource:
    edition = lacuscurtius_passages.load_edition([base / page for page in config["pages"]],
                                                 translator=config.get("translator"), language=config.get("language"))
    return PassageSource(
        author=edition.author, title=edition.title, translator=edition.translator, citation=edition.citation,
        refs=lambda selection: lacuscurtius_passages.section_refs(edition, selection) if selection else edition.all_refs(),
        observation=lambda ref: lacuscurtius_passages.passage_observation(edition, ref),
    )
