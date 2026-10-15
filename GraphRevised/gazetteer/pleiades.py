"""Pleiades places, read from the preserved dump into plain records for the gazetteer.

Each place keeps what the gazetteer needs and nothing it would have to reinterpret:
its title, place types, representative point, ancient names with the periods they
are attested in (Pleiades' own period keys, resolved to years only at read time),
its parents (the `part_of_*` and `in_territory_of` connections, with their periods),
and the GeoNames, Wikidata, and TGN identifiers its references name.
"""

from __future__ import annotations

import gzip
import re
from pathlib import Path
from typing import Any, Iterator

import ijson

GEONAMES = re.compile(r"geonames\.org/(\d+)")
WIKIDATA = re.compile(r"wikidata\.org/(?:wiki|entity)/(Q\d+)")
TGN = re.compile(r"vocab\.getty\.edu/(?:page/)?tgn/(\d+)")
PLACE_URI = re.compile(r"pleiades\.stoa\.org/places/(\d+)/?$")


def iter_places(path: Path) -> Iterator[dict[str, Any]]:
    """Stream the places of a Pleiades JSON dump (gzipped), one plain record each."""
    with gzip.open(path, "rb") as handle:
        for record in ijson.items(handle, "@graph.item", use_float=True):
            yield parse_place(record)


def parse_place(record: dict[str, Any]) -> dict[str, Any]:
    point = record.get("reprPoint")
    references = [r.get("accessURI") or "" for r in record.get("references") or []]
    return {
        "id": str(record["id"]),
        "title": record.get("title") or str(record["id"]),
        "placeTypes": list(record.get("placeTypes") or []),
        "lon": float(point[0]) if point else None,
        "lat": float(point[1]) if point else None,
        "names": _names(record.get("names") or []),
        "connections": [_connection(c) for c in record.get("connections") or []],
        "geonames": _matches(GEONAMES, references),
        "wikidata": _matches(WIKIDATA, references),
        "tgn": _matches(TGN, references),
    }


def _names(names: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for name in names:
        label = (name.get("romanized") or name.get("attested") or "").strip()
        if label:
            periods = sorted({a["timePeriod"] for a in name.get("attestations") or [] if a.get("timePeriod")})
            out.append({"name": label, "periods": periods})
    return out


def _connection(connection: dict[str, Any]) -> dict[str, Any]:
    target = PLACE_URI.search(connection.get("connectsTo") or "")
    return {
        "type": connection.get("connectionType"),
        "target": target.group(1) if target else None,
        "periods": sorted({a["timePeriod"] for a in connection.get("attestations") or [] if a.get("timePeriod")}),
    }


def _matches(pattern: re.Pattern, uris: list[str]) -> list[str]:
    return sorted({m.group(1) for uri in uris for m in [pattern.search(uri)] if m})


def name_lines(names: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Names as two parallel lists for a node: the names, and each with its periods."""
    unique = list(dict.fromkeys(n["name"] for n in names))
    attested = [n["name"] + (f" ({', '.join(n['periods'])})" if n["periods"] else "") for n in names]
    return unique, list(dict.fromkeys(attested))
