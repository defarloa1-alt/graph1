"""Reading context for an entity from its preserved Wikidata payload.

Context helps an agent identify names; it is never evidence. Values come from
the payload preserved for the entity's accepted Wikidata identity link, so no
request is made and the context is reproducible.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .wikidata_statements import REPOSITORY_ROOT

MAX_ALIASES = 8
DATE_PROPERTIES = {
    "P569": "born",
    "P570": "died",
    "P585": "date",
    "P580": "from",
    "P582": "until",
}


def entity_context(payload_uri: str | None, qid: str | None, language: str = "en") -> dict[str, Any]:
    """Aliases and dates for `qid` from its preserved payload; empty if unavailable."""
    if not payload_uri or not qid:
        return {}
    path = REPOSITORY_ROOT / payload_uri
    if not path.exists():
        return {}
    entity = json.loads(path.read_bytes()).get("entities", {}).get(qid)
    if entity is None:
        return {}
    aliases = [alias["value"] for alias in entity.get("aliases", {}).get(language, [])][:MAX_ALIASES]
    dates = {}
    for pid, name in DATE_PROPERTIES.items():
        for claim in entity.get("claims", {}).get(pid, [])[:1]:
            value = claim["mainsnak"].get("datavalue", {}).get("value")
            if isinstance(value, dict) and "time" in value:
                dates[name] = format_year(value["time"])
    return {"aliases": aliases, "dates": dates}


def format_year(wikidata_time: str) -> str:
    """'-0083-01-14T00:00:00Z' -> '83 BCE'; '+0014-08-19T00:00:00Z' -> '14 CE'."""
    year = int(wikidata_time[:wikidata_time.index("-", 1)])
    return f"{-year} BCE" if year < 0 else f"{year} CE"
