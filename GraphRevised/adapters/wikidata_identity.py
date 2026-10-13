"""Bounded Wikidata identity discovery with preserved source payloads."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_ENTITY_URL = "https://www.wikidata.org/wiki/Special:EntityData/"
USER_AGENT = "Chrystallum/0.1 (authority identity discovery)"


def polite_get(url: str, *, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None,
               timeout: int = 30, attempts: int = 5) -> requests.Response:
    """GET with the project's User-Agent, retrying 429 and 5xx with backoff (Retry-After when the
    server gives it). Wikidata rate-limits bursts; the legacy harvest learned this the hard way."""
    import time

    delay = 2.0
    for attempt in range(attempts):
        response = requests.get(url, params=params, headers={"User-Agent": USER_AGENT, **(headers or {})},
                                timeout=timeout)
        if response.status_code != 429 and response.status_code < 500:
            response.raise_for_status()
            return response
        if attempt == attempts - 1:
            response.raise_for_status()
        wait = response.headers.get("Retry-After")
        time.sleep(float(wait) if wait and wait.isdigit() else delay)
        delay *= 2
    raise RuntimeError("unreachable")
QID_PATTERN = re.compile(r"^Q[1-9]\d*$")
MAX_RESULTS = 10


class WikidataAdapterError(RuntimeError):
    """Raised when Wikidata identity discovery cannot produce a result."""


@dataclass(frozen=True)
class IdentityCandidate:
    """A candidate returned by Wikidata; never an accepted local identity."""

    identifier: str
    label: str
    description: str | None
    match_type: str
    concept_uri: str


@dataclass(frozen=True)
class SourceObservationDraft:
    """Data suitable for the Phase 3 SourceObservation operation."""

    id: str
    label: str
    short_label: str
    source_system: str
    source_entity_id: str
    revision: str
    retrieved_at: str
    content_hash: str
    payload_uri: str
    status: str


@dataclass(frozen=True)
class IdentityDiscoveryResult:
    """The persisted source response and candidates discovered from it."""

    query: str
    language: str
    retrieved_at: str
    candidates: tuple[IdentityCandidate, ...]
    observation: SourceObservationDraft | None
    search_payload_uri: str
    search_payload_hash: str


class WikidataIdentityAdapter:
    """Discover Wikidata identity candidates without accepting local claims."""

    def __init__(
        self,
        payload_directory: Path,
        session: requests.Session | None = None,
        timeout_seconds: int = 20,
    ) -> None:
        self._payload_directory = payload_directory
        self._session = session or requests.Session()
        self._timeout_seconds = timeout_seconds

    def discover(
        self,
        query: str,
        *,
        language: str = "en",
        limit: int = 5,
    ) -> IdentityDiscoveryResult:
        """Return bounded candidates and a preserved top-candidate observation."""
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must not be empty")
        if not language.strip():
            raise ValueError("language must not be empty")
        if not 1 <= limit <= MAX_RESULTS:
            raise ValueError(f"limit must be between 1 and {MAX_RESULTS}")

        retrieved_at = _utc_now()
        search_payload = self._request(
            {
                "action": "wbsearchentities",
                "search": normalized_query,
                "language": language,
                "limit": limit,
                "format": "json",
                "formatversion": 2,
            }
        )
        search_path, search_hash = self._persist_payload(
            "search",
            _safe_filename(normalized_query),
            search_payload,
        )
        candidates = tuple(
            IdentityCandidate(
                identifier=item["id"],
                label=item.get("label", item["id"]),
                description=item.get("description"),
                match_type=item.get("match", {}).get("type", "unknown"),
                concept_uri=item.get(
                    "concepturi",
                    f"http://www.wikidata.org/entity/{item['id']}",
                ),
            )
            for item in search_payload.get("search", [])
            if QID_PATTERN.fullmatch(item.get("id", ""))
        )

        if not candidates:
            return IdentityDiscoveryResult(
                query=normalized_query,
                language=language,
                retrieved_at=retrieved_at,
                candidates=(),
                observation=None,
                search_payload_uri=search_path.as_uri(),
                search_payload_hash=search_hash,
            )

        entity_payload = self._request(
            {
                "action": "wbgetentities",
                "ids": candidates[0].identifier,
                "props": "info|labels|descriptions",
                "languages": language,
                "format": "json",
                "formatversion": 2,
            }
        )
        entity = _get_entity(entity_payload, candidates[0].identifier)
        revision = str(entity["lastrevid"])
        entity_path, content_hash = self._persist_payload(
            "entity",
            f"{candidates[0].identifier}-r{revision}",
            entity_payload,
        )
        observation = SourceObservationDraft(
            id=_observation_id(candidates[0].identifier, revision, content_hash),
            label=f"Wikidata observation: identity record for {candidates[0].label}",
            short_label=f"Wikidata: {candidates[0].label}",
            source_system="Wikidata",
            source_entity_id=candidates[0].identifier,
            revision=revision,
            retrieved_at=retrieved_at,
            content_hash=content_hash,
            payload_uri=entity_path.as_uri(),
            status="observed",
        )
        self._persist_metadata(
            entity_path,
            {
                "query": normalized_query,
                "candidate": asdict(candidates[0]),
                "observation": asdict(observation),
            },
        )
        return IdentityDiscoveryResult(
            query=normalized_query,
            language=language,
            retrieved_at=retrieved_at,
            candidates=candidates,
            observation=observation,
            search_payload_uri=search_path.as_uri(),
            search_payload_hash=search_hash,
        )

    def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._session.get(
                WIKIDATA_API_URL,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as error:
            raise WikidataAdapterError(
                f"Wikidata request failed for {params['action']}: {error}"
            ) from error
        except ValueError as error:
            raise WikidataAdapterError(
                f"Wikidata returned invalid JSON for {params['action']}"
            ) from error
        if "error" in payload:
            raise WikidataAdapterError(
                f"Wikidata API error for {params['action']}: {payload['error']}"
            )
        return payload

    def _persist_payload(
        self,
        category: str,
        identifier: str,
        payload: dict[str, Any],
    ) -> tuple[Path, str]:
        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
        content_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        path = self._payload_directory / f"wikidata-{category}-{identifier}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        # Write bytes so the file on disk is exactly what was hashed; text mode
        # would translate newlines on Windows.
        path.write_bytes(serialized.encode("utf-8"))
        return path.resolve(), content_hash

    def _persist_metadata(self, entity_path: Path, metadata: dict[str, Any]) -> None:
        metadata_path = entity_path.with_suffix(".metadata.json")
        serialized = json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        metadata_path.write_bytes(serialized.encode("utf-8"))


def _observation_id(identifier: str, revision: str, content_hash: str) -> str:
    digest = hashlib.sha256(
        f"Wikidata|{identifier}|{revision}|{content_hash}".encode("utf-8")
    ).hexdigest()[:20]
    return f"chr:observation:wikidata:{identifier}:r{revision}:{digest}"


def _get_entity(payload: dict[str, Any], identifier: str) -> dict[str, Any]:
    entities = payload.get("entities")
    if isinstance(entities, dict):
        entity = entities.get(identifier)
    elif isinstance(entities, list):
        entity = next(
            (item for item in entities if item.get("id") == identifier),
            None,
        )
    else:
        entity = None
    if not isinstance(entity, dict) or "lastrevid" not in entity:
        raise WikidataAdapterError(
            f"Wikidata entity response did not contain a revision for {identifier}"
        )
    return entity


def _safe_filename(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "query"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
