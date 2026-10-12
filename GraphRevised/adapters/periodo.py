"""The PeriodO gazetteer of period definitions: who defined which period, when, and where.

PeriodO (https://perio.do) collects periodizations as published: each
definition keeps its source's own label and date wording ("Republic, 510-30
B.C", start "510 B.C.") beside normalized years, the region it applies to
(with Wikidata identifiers), and the authority (a book, catalogue, or
thesaurus) that defined it. The dataset is fetched once, cached outside
version control with its hash, version, and retrieval time, and refreshed
when older than the configured age. It is read-only here: a definition is
evidence of what one authority says, never an identity decision.

Years are astronomical, as in PeriodO and EDTF (31 BCE = -30).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

from .wikidata_identity import USER_AGENT

DATASET_URI = "https://data.perio.do/d.json"
PAYLOAD_NAME = "periodo-dataset.json"


@dataclass(frozen=True)
class PeriodSource:
    """The work that published a definition: book, catalogue, database, thesaurus."""

    authority_id: str
    title: str | None
    creators: tuple[str, ...]
    year: str | None
    citation: str | None
    url: str | None
    part_of: str | None  # the containing work's title, when the source is a chapter or entry
    locator: str | None


@dataclass(frozen=True)
class PeriodDefinition:
    id: str  # PeriodO identifier, such as p06c6g3p3g3
    uri: str  # resolvable ARK
    label: str  # the source's own label
    labels: tuple[str, ...]  # the label and its translations (localized labels in other languages)
    language: str | None
    start_label: str | None  # the source's wording of the start ("510 B.C.")
    stop_label: str | None
    start_years: tuple[int, int] | None  # astronomical (earliest, latest); equal for a single year
    stop_years: tuple[int, int] | None
    places: tuple[tuple[str, str], ...]  # (Wikidata QID or other id, label)
    place_description: str | None  # the source's wording of the region
    editorial_note: str | None  # PeriodO's note, never the source's text
    broader: tuple[str, ...]
    narrower: tuple[str, ...]
    source: PeriodSource
    page: str | None  # a definition-level locator in its source

    @property
    def span(self) -> tuple[int, int] | None:
        if self.start_years is None or self.stop_years is None:
            return None
        return self.start_years[0], self.stop_years[1]


@dataclass(frozen=True)
class PeriodDataset:
    definitions: tuple[PeriodDefinition, ...]
    version: str | None
    retrieved_at: str
    content_hash: str
    source_uri: str


def load_dataset(cache_directory: Path, *, source_uri: str = DATASET_URI, max_age_days: int = 90) -> PeriodDataset:
    """Load the cached dataset, fetching it when missing or older than `max_age_days`."""
    cache_directory.mkdir(parents=True, exist_ok=True)
    payload_path = cache_directory / PAYLOAD_NAME
    metadata_path = payload_path.with_suffix(".metadata.json")
    stale = True
    if payload_path.exists() and metadata_path.exists():
        retrieved = datetime.fromisoformat(json.loads(metadata_path.read_text(encoding="utf-8"))["retrievedAt"])
        stale = datetime.now(timezone.utc) - retrieved > timedelta(days=max_age_days)
    if stale:
        response = requests.get(source_uri, headers={"User-Agent": USER_AGENT}, timeout=120)
        response.raise_for_status()
        payload_path.write_bytes(response.content)
        metadata_path.write_bytes(json.dumps({
            "sourceUri": source_uri,
            "version": response.headers.get("ETag", "").strip('W/"') or None,
            "lastModified": response.headers.get("Last-Modified"),
            "retrievedAt": datetime.now(timezone.utc).isoformat(),
            "contentHash": hashlib.sha256(response.content).hexdigest(),
        }, indent=2).encode("utf-8"))
    payload = payload_path.read_bytes()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if hashlib.sha256(payload).hexdigest() != metadata["contentHash"]:
        raise ValueError(f"{payload_path} does not match its recorded hash")
    return PeriodDataset(
        definitions=tuple(parse_definitions(json.loads(payload))),
        version=metadata.get("version"), retrieved_at=metadata["retrievedAt"],
        content_hash=metadata["contentHash"], source_uri=metadata["sourceUri"],
    )


def _years(terminus: dict[str, Any]) -> tuple[int, int] | None:
    value = terminus.get("in") or {}
    try:
        if "year" in value:
            return int(value["year"]), int(value["year"])
        if "earliestYear" in value and "latestYear" in value:
            return int(value["earliestYear"]), int(value["latestYear"])
    except (TypeError, ValueError):
        return None
    return None


def _names(people: list[dict[str, Any]] | None) -> tuple[str, ...]:
    return tuple(person["name"].strip() for person in people or [] if person.get("name", "").strip())


def _source(authority_id: str, data: dict[str, Any]) -> PeriodSource:
    part_of = data.get("partOf") or {}
    return PeriodSource(
        authority_id=authority_id,
        title=(data.get("title") or part_of.get("title") or "").strip() or None,
        creators=_names(data.get("creators")) or _names(part_of.get("creators")),
        year=str(data.get("yearPublished") or part_of.get("yearPublished") or "") or None,
        citation=(data.get("citation") or "").strip() or None,
        url=data.get("url") or data.get("id") or part_of.get("id"),
        part_of=((part_of.get("title") or "").strip() or None) if data.get("title") else None,
        locator=data.get("locator"),
    )


def parse_definitions(data: dict[str, Any]) -> list[PeriodDefinition]:
    definitions = []
    for authority_id, authority in data["authorities"].items():
        source = _source(authority_id, authority.get("source") or {})
        for period_id, period in authority.get("periods", {}).items():
            # Same-language variants are left out: a gazetteer may list a combined
            # period's parts there ("Hellenistic Greek", "Roman Republic"), which
            # are not names of the definition itself.
            labels = [period.get("label", "")]
            for language, values in (period.get("localizedLabels") or {}).items():
                if language != period.get("languageTag"):
                    labels.extend(value.strip() for value in values)
            definitions.append(PeriodDefinition(
                id=period_id,
                uri=f"http://n2t.net/ark:/99152/{period_id}",
                label=period.get("label", ""),
                labels=tuple(dict.fromkeys(label for label in labels if label)),
                language=period.get("languageTag"),
                start_label=(period.get("start") or {}).get("label"),
                stop_label=(period.get("stop") or {}).get("label"),
                start_years=_years(period.get("start") or {}),
                stop_years=_years(period.get("stop") or {}),
                places=tuple((place.get("id", "").rsplit("/", 1)[-1], place.get("label", ""))
                             for place in period.get("spatialCoverage") or []),
                place_description=period.get("spatialCoverageDescription"),
                editorial_note=period.get("editorialNote"),
                broader=tuple([period["broader"]] if isinstance(period.get("broader"), str)
                              else period.get("broader") or ()),
                narrower=tuple(period.get("narrower") or ()),
                source=source,
                page=(period.get("source") or {}).get("locator"),
            ))
    return definitions
