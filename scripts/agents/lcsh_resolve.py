#!/usr/bin/env python3
"""
LCSH Resolution — Fetch label, broader, narrower, alt_labels from id.loc.gov.

Usage:
  from scripts.agents.lcsh_resolve import resolve_lcsh
  data = resolve_lcsh("sh85031326")
  # -> {"label": "Constitutional history", "broader": [...], "narrower": [...], "alt_labels": [...]}
"""

import json
import re
import urllib.request
from typing import Optional

ID_LOC_BASE = "https://id.loc.gov/authorities/subjects"


def _extract_id(url_or_id: str) -> str:
    """Normalize sh85031326 or full URI -> sh85031326."""
    if not url_or_id or not isinstance(url_or_id, str):
        return ""
    s = url_or_id.strip()
    m = re.search(r"(sh\d{8,}(?:-\d+)?)", s, re.I)
    return m.group(1).lower() if m else s


def _find_main_record(data: list, lid: str) -> Optional[dict]:
    """Find the main LCSH record in the JSON-LD array (has @id ending with our subject id)."""
    expected = f"http://id.loc.gov/authorities/subjects/{lid}"
    for obj in data:
        if not isinstance(obj, dict):
            continue
        aid = obj.get("@id", "")
        if aid == expected or str(aid).endswith("/" + lid):
            return obj
    return None


def _get_label(record: dict) -> str:
    for key in ("http://www.loc.gov/mads/rdf/v1#authoritativeLabel", "http://www.w3.org/2004/02/skos/core#prefLabel"):
        vals = record.get(key, [])
        if isinstance(vals, list):
            for v in vals:
                if isinstance(v, dict) and "@value" in v:
                    return v["@value"] or ""
        elif isinstance(vals, dict) and "@value" in vals:
            return vals["@value"] or ""
    return ""


def _get_refs(record: dict, pred: str) -> list:
    refs = []
    seen_ids = set()
    keys = [pred]
    if "broader" in pred:
        keys.append("http://www.loc.gov/mads/rdf/v1#hasBroaderAuthority")
    elif "narrower" in pred:
        keys.append("http://www.loc.gov/mads/rdf/v1#hasNarrowerAuthority")
    for key in keys:
        vals = record.get(key, [])
        if not isinstance(vals, list):
            vals = [vals] if vals else []
        for v in vals:
            if isinstance(v, dict) and "@id" in v:
                uri = v["@id"]
                lid = uri.split("/")[-1] if "/" in uri else uri
                if lid not in seen_ids:
                    seen_ids.add(lid)
                    refs.append({"id": lid, "uri": uri})
    return refs


def _get_alt_labels(record: dict) -> list:
    out = []
    for key in ("http://www.w3.org/2004/02/skos/core#altLabel",):
        vals = record.get(key, [])
        if not isinstance(vals, list):
            vals = [vals] if vals else []
        for v in vals:
            if isinstance(v, dict) and "@value" in v:
                out.append(v["@value"])
    return list(dict.fromkeys(out))


def resolve_lcsh(lcsh_id: str, timeout: int = 15) -> Optional[dict]:
    """
    Resolve LCSH ID via id.loc.gov. Returns label, broader, narrower, alt_labels.
    """
    lid = _extract_id(lcsh_id)
    if not lid:
        return None
    url = f"{ID_LOC_BASE}/{lid}.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Chrystallum/1.0 (LCSH resolution)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return None

    if not isinstance(data, list):
        return None

    record = _find_main_record(data, lid)
    if not record:
        return None

    label = _get_label(record)
    broader = _get_refs(record, "http://www.w3.org/2004/02/skos/core#broader")
    narrower = _get_refs(record, "http://www.w3.org/2004/02/skos/core#narrower")
    alt_labels = _get_alt_labels(record)

    return {
        "lcsh_id": lid,
        "label": label,
        "broader": broader,
        "narrower": narrower,
        "alt_labels": alt_labels,
        "uri": f"{ID_LOC_BASE}/{lid}",
    }
