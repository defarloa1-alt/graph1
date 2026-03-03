#!/usr/bin/env python3
"""
Person Harvest Discovery — Roman Republic persons from Wikidata and graph.

Discovers person QIDs to harvest:
  - Option A: Wikidata P31=Q5 (human) + P27=Q17167 (citizen of Roman Republic)
  - Option B: P6863 (DPRR ID) — persons already aligned
  - Option C: Graph entities with dprr_id or qid in Roman Republic scope

Also fetches P22 (father) and P25 (mother) for ancestry traversal.
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests

_scripts = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_scripts))

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "Chrystallum/1.0 (Person harvest discovery)"
ROMAN_REPUBLIC_QID = "Q17167"
HUMAN_QID = "Q5"


def discover_roman_republic_persons(
    limit: int = 500,
    use_p6863: bool = True,
    use_p27: bool = True,
    timeout: int = 60,
) -> list[dict]:
    """
    Discover Roman Republic persons from Wikidata.
    Returns list of {qid, label, dprr_id?, sources[]}.
    """
    # P31=human + P27=Roman Republic (citizen); optionally also P6863 (DPRR)
    if not use_p27 and not use_p6863:
        return []

    # Primary: P27=Q17167 (citizen of Roman Republic) or P6863 (DPRR-aligned)
    if use_p27 and use_p6863:
        scope = "?person wdt:P27 wd:" + ROMAN_REPUBLIC_QID + " . OPTIONAL { ?person wdt:P6863 ?dprr_id . }"
    elif use_p27:
        scope = "?person wdt:P27 wd:" + ROMAN_REPUBLIC_QID + " . OPTIONAL { ?person wdt:P6863 ?dprr_id . }"
    else:
        scope = "?person wdt:P6863 ?dprr_id ."

    query = f"""
    SELECT DISTINCT ?person ?personLabel ?dprr_id WHERE {{
      ?person wdt:P31 wd:{HUMAN_QID} .
      {scope}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {limit}
    """
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    r = requests.get(SPARQL_URL, params={"query": query}, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    bindings = data.get("results", {}).get("bindings", [])

    out = []
    for b in bindings:
        person_uri = b.get("person", {}).get("value", "")
        qid = person_uri.split("/")[-1] if person_uri else ""
        label = b.get("personLabel", {}).get("value", "")
        dprr_val = (b.get("dprr_id") or {}).get("value", "") if isinstance(b.get("dprr_id"), dict) else ""
        out.append({
            "qid": qid,
            "label": label,
            "dprr_id": dprr_val if dprr_val and dprr_val.isdigit() else None,
        })
    return out


def fetch_ancestry_qids(qid: str, timeout: int = 60) -> dict[str, str | None]:
    """
    Fetch P22 (father) and P25 (mother) for a person.
    Returns {father_qid, mother_qid} (None if absent).
    """
    query = f"""
    SELECT ?prop ?parent WHERE {{
      wd:{qid} ?prop ?parent .
      VALUES ?prop {{ wdt:P22 wdt:P25 }}
      FILTER(isIRI(?parent))
    }}
    """
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    r = requests.get(SPARQL_URL, params={"query": query}, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    bindings = data.get("results", {}).get("bindings", [])

    father_qid = mother_qid = None
    for b in bindings:
        prop_uri = b.get("prop", {}).get("value", "")
        parent_uri = b.get("parent", {}).get("value", "")
        pid = prop_uri.split("/")[-1] if prop_uri else ""
        parent_qid = parent_uri.split("/")[-1] if parent_uri else ""
        if pid == "P22":
            father_qid = parent_qid
        elif pid == "P25":
            mother_qid = parent_qid
    return {"father_qid": father_qid, "mother_qid": mother_qid}


def discover_from_graph(session, limit: int = 500) -> list[dict]:
    """
    Discover persons from Neo4j graph (entities with dprr_id or qid).
    Returns list of {qid, entity_id, label, dprr_id}.
    Excludes entities where qid is a 32-char hex hash (id_hash mistaken for qid).
    """
    result = session.run("""
        MATCH (e:Entity)
        WHERE (e.dprr_id IS NOT NULL OR (e.qid IS NOT NULL AND e.qid =~ 'Q[0-9]+'))
          AND (e.entity_type = 'PERSON' OR e.entity_type IS NULL)
        RETURN e.qid AS qid, e.entity_id AS entity_id, e.label AS label, e.dprr_id AS dprr_id
        LIMIT $limit
    """, limit=limit)
    return [dict(r) for r in result]
