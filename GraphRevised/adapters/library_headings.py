"""Library subject headings (LCSH, FAST): fetched once, preserved byte for byte, labels read from the record.

A heading's label always comes from its authority record, never from the
caller, so a code is never stored or shown without the authority's own words
(the curator's rule: never display codes alone). Payloads are kept in
phase-5-source/ beside the Wikidata identity payloads, hashed as bytes, and
reused on later runs.

    LCSH  identifier sh85000736  record https://id.loc.gov/authorities/subjects/<id>.json
    FAST  identifier 796265      record https://id.worldcat.org/fast/<id>.rdf.xml
          (the fst00796265 form is deprecated by OCLC; FAST data is ODC-By, attribution required)
"""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ElementTree
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from GraphRevised.adapters.wikidata_identity import USER_AGENT

SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / "phase-5-source"
LCSH_URI = "http://id.loc.gov/authorities/subjects/{identifier}"
FAST_URI = "http://id.worldcat.org/fast/{identifier}"
SKOS = "{http://www.w3.org/2004/02/skos/core#}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"


class HeadingError(ValueError):
    """The identifier is malformed or the record does not carry a label."""


SYSTEMS: dict[str, dict[str, Any]] = {
    "LCSH": {
        "pattern": re.compile(r"^sh\d{8,10}$"),
        "fetch": "https://id.loc.gov/authorities/subjects/{identifier}.json",
        "suffix": "json",
        "license": None,
    },
    "FAST": {
        "pattern": re.compile(r"^\d{1,8}$"),
        "fetch": "https://id.worldcat.org/fast/{identifier}.rdf.xml",
        "suffix": "rdf.xml",
        "license": "ODC-By 1.0 (OCLC FAST); attribution required",
    },
}


def lcsh_label(payload: bytes, identifier: str) -> str:
    uri = LCSH_URI.format(identifier=identifier)
    for node in json.loads(payload):
        if node.get("@id") == uri:
            for value in node.get("http://www.loc.gov/mads/rdf/v1#authoritativeLabel", []):
                if value.get("@language", "en") == "en":
                    return value["@value"]
    raise HeadingError(f"LCSH {identifier}: no authoritative label in the record")


def fast_label(payload: bytes, identifier: str) -> str:
    root = ElementTree.fromstring(payload)
    for description in root.iter(f"{RDF}Description"):
        if description.get(f"{RDF}about") == identifier:
            label = description.find(f"{SKOS}prefLabel")
            if label is not None and label.text:
                return label.text.strip()
    raise HeadingError(f"FAST {identifier}: no preferred label in the record")


LABEL_READERS = {"LCSH": lcsh_label, "FAST": fast_label}


def display(system: str, identifier: str, label: str) -> str:
    """How a heading is shown: the authority's words first, the code beside them, never alone."""
    return f"{label} ({system} {identifier})"


def preserved_heading(system: str, identifier: str) -> tuple[Path, dict[str, Any]]:
    """Return the preserved record for a heading, fetching it only if none exists."""
    if system not in SYSTEMS:
        raise HeadingError(f"unknown subject heading system {system!r}")
    config = SYSTEMS[system]
    if not config["pattern"].match(identifier):
        raise HeadingError(f"{system} identifier {identifier!r} is malformed")
    path = SOURCE_DIRECTORY / f"{system.lower()}-{identifier}.{config['suffix']}"
    metadata_path = SOURCE_DIRECTORY / f"{system.lower()}-{identifier}.metadata.json"
    if path.exists() and metadata_path.exists():
        return path, json.loads(metadata_path.read_text(encoding="utf-8"))

    source_uri = config["fetch"].format(identifier=identifier)
    response = requests.get(source_uri, headers={"User-Agent": USER_AGENT, "Accept": "*/*"}, timeout=30)
    response.raise_for_status()
    payload = response.content
    metadata = {
        "sourceSystem": system,
        "sourceUri": source_uri,
        "identifier": identifier,
        "uri": (LCSH_URI if system == "LCSH" else FAST_URI).format(identifier=identifier),
        "label": LABEL_READERS[system](payload, identifier),
        "license": config["license"],
        "retrievedAt": datetime.now(timezone.utc).isoformat(),
        "contentHash": hashlib.sha256(payload).hexdigest(),
    }
    SOURCE_DIRECTORY.mkdir(exist_ok=True)
    path.write_bytes(payload)
    metadata_path.write_bytes((json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return path, metadata
