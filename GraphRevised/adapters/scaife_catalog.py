"""The Scaife (Perseus) library catalogue: which CTS works and editions exist.

The catalogue is fetched once, cached outside version control with its hash
and retrieval time, and used read-only to check whether a candidate source
has a digital edition and in which languages. It records availability, not
what a text says.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

from .wikidata_identity import USER_AGENT

CATALOG_URI = "https://scaife.perseus.org/library/json/"


@dataclass(frozen=True)
class CatalogSnapshot:
    works: dict[str, str]  # work URN -> label
    text_groups: dict[str, str]  # text-group URN -> author label
    editions: dict[str, list[str]]  # work URN -> edition URNs
    retrieved_at: str
    content_hash: str
    source_uri: str = CATALOG_URI

    def editions_of(self, work_urn: str) -> list[str]:
        return self.editions.get(work_urn, [])

    def languages_of(self, work_urn: str) -> list[str]:
        """Edition languages from their CTS version suffix (perseus-eng2 -> eng)."""
        found = set()
        for urn in self.editions_of(work_urn):
            match = re.search(r"-([a-z]{3})\d*$", urn)
            if match:
                found.add(match.group(1))
        return sorted(found)

    def author_matches(self, name: str) -> list[str]:
        """Text-group URNs whose author label contains every word of `name`."""
        words = [w.lower() for w in re.findall(r"\w+", name) if len(w) > 2]
        return [urn for urn, label in self.text_groups.items() if words and all(w in label.lower() for w in words)]


def load_catalog(cache_directory: Path) -> CatalogSnapshot:
    """Load the cached catalogue, fetching it once if no cache exists."""
    cache_directory.mkdir(parents=True, exist_ok=True)
    payload_path = cache_directory / "scaife-library.json"
    metadata_path = cache_directory / "scaife-library.metadata.json"
    if not payload_path.exists():
        response = requests.get(CATALOG_URI, headers={"User-Agent": USER_AGENT}, timeout=60)
        response.raise_for_status()
        payload_path.write_bytes(response.content)
        metadata_path.write_bytes(json.dumps({
            "sourceUri": CATALOG_URI,
            "retrievedAt": datetime.now(timezone.utc).isoformat(),
            "contentHash": hashlib.sha256(response.content).hexdigest(),
        }, indent=2).encode("utf-8"))
    payload = payload_path.read_bytes()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if hashlib.sha256(payload).hexdigest() != metadata["contentHash"]:
        raise ValueError(f"{payload_path} does not match its recorded hash")
    return parse_catalog(json.loads(payload), retrieved_at=metadata["retrievedAt"], content_hash=metadata["contentHash"])


def parse_catalog(data: dict, *, retrieved_at: str, content_hash: str) -> CatalogSnapshot:
    editions: dict[str, list[str]] = {}
    for text in data["texts"]:
        work_urn = text["urn"].rsplit(".", 1)[0]
        editions.setdefault(work_urn, []).append(text["urn"])
    return CatalogSnapshot(
        works={work["urn"]: work["label"] for work in data["works"]},
        text_groups={group["urn"]: group["label"] for group in data["text_groups"]},
        editions=editions,
        retrieved_at=retrieved_at,
        content_hash=content_hash,
    )
