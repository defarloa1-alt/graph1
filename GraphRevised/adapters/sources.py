"""One interface over passage sources, chosen by an inquiry's `source.type`.

    perseus-tei        {"edition": <preserved TEI path>, "chapters": "61-68"}
    lacuscurtius-html  {"pages": [<preserved page paths>], "chapters": "50.11-50.15,50.31-51.2", "translator": ...,
                        "author": ... (when the pages do not name one)}
    gutenberg-html     {"book": <preserved book path>, "edition": "<printed edition>"}  (refs: chapter.paragraph)
    wikipedia-html     {"article": <preserved parse response path>}  (refs: section.paragraph; 0 is the lead)

Paths are relative to the GraphRevised directory. `chapters` selects what a
run reads; `refs(None)` lists every section, for context windows.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import gutenberg_passages, lacuscurtius_passages, perseus_passages, wikipedia_passages


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
        source = _perseus(config, base)
    elif kind == "lacuscurtius-html":
        source = _lacuscurtius(config, base)
    elif kind == "gutenberg-html":
        source = _gutenberg(config, base)
    elif kind == "wikipedia-html":
        source = _wikipedia(config, base)
    else:
        raise ValueError(f"unknown source type {kind!r}")
    return _with_range_lists(source)


def _with_range_lists(source: PassageSource) -> PassageSource:
    """Let a selection list several ranges ("50.11-50.15,50.31-51.2"), in document order."""
    single = source.refs

    def refs(selection: str | None) -> list[str]:
        if not selection or "," not in selection:
            return single(selection)
        chosen = {ref for part in selection.split(",") for ref in single(part.strip())}
        return [ref for ref in single(None) if ref in chosen]

    return PassageSource(author=source.author, title=source.title, translator=source.translator,
                         citation=source.citation, refs=refs, observation=source.observation)


def _perseus(config: dict[str, Any], base: Path) -> PassageSource:
    path = base / config["edition"]
    metadata = json.loads(path.with_suffix(".metadata.json").read_text(encoding="utf-8"))
    edition = perseus_passages.load_edition(path, source_commit=path.stem.rsplit("-", 1)[1],
                                            rights=metadata.get("rights"), cts_urn=metadata.get("ctsUrn"))

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
                                                 translator=config.get("translator"), language=config.get("language"),
                                                 author=config.get("author"))
    return PassageSource(
        author=edition.author, title=edition.title, translator=edition.translator, citation=edition.citation,
        refs=lambda selection: lacuscurtius_passages.section_refs(edition, selection) if selection else edition.all_refs(),
        observation=lambda ref: lacuscurtius_passages.passage_observation(edition, ref),
    )


def _gutenberg(config: dict[str, Any], base: Path) -> PassageSource:
    edition = gutenberg_passages.load_edition(base / config["book"], edition=config.get("edition"))
    return PassageSource(
        author=edition.author, title=edition.title, translator=edition.translator, citation=edition.citation,
        refs=lambda selection: gutenberg_passages.section_refs(edition, selection) if selection else edition.all_refs(),
        observation=lambda ref: gutenberg_passages.passage_observation(edition, ref),
    )


def _wikipedia(config: dict[str, Any], base: Path) -> PassageSource:
    article = wikipedia_passages.load_article(base / config["article"])
    return PassageSource(
        author=article.author, title=article.title, translator=None, citation=article.citation,
        refs=lambda selection: wikipedia_passages.section_refs(article, selection) if selection else article.all_refs(),
        observation=lambda ref: wikipedia_passages.passage_observation(article, ref),
    )
