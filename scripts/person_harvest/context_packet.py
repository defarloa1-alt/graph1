#!/usr/bin/env python3
"""
Context Packet Builder — ADR-008 §6

Assembles person_stub, existing_family, existing_offices, gens_network,
dprr_raw (from graph when blocked), wikidata_raw, layer1_output.
"""

from __future__ import annotations

import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1]
_federation = _scripts / "federation"
sys.path.insert(0, str(_scripts))
sys.path.insert(0, str(_federation))

import requests

try:
    from config_loader import WIKIDATA_SPARQL_ENDPOINT
except ImportError:
    WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

USER_AGENT = "Chrystallum/1.0 (Person harvest)"


def build_context_packet(
    qid: str,
    dprr_id: str | None,
    session,
    dprr_blocked: bool = True,
) -> dict:
    """
    Build context packet for one person. OPS-001: when DPRR blocked, dprr_raw
    comes from graph, not SPARQL.
    """
    packet = {
        "person_stub": {},
        "existing_family": [],
        "existing_offices": [],
        "gens_network": [],
        "dprr_raw": None,
        "wikidata_raw": None,
        "layer1_output": {},
    }

    # 1. person_stub from graph (ADR-007 four-label schema)
    r = session.run("""
        MATCH (e:Entity)
        WHERE e.qid = $qid OR e.dprr_id = $dprr_id
        RETURN e.entity_id AS entity_id, e.qid AS qid, e.dprr_id AS dprr_id,
               e.label AS label, e.label_dprr AS label_dprr, e.label_latin AS label_latin, e.label_sort AS label_sort,
               e.entity_type AS entity_type
        LIMIT 1
    """, qid=qid, dprr_id=dprr_id or "")
    row = r.single()
    if row:
        packet["person_stub"] = dict(row)

    # 2. existing_family (FATHER_OF, MOTHER_OF, PARENT_OF, SIBLING_OF, SPOUSE_OF, STEPPARENT_OF)
    r = session.run("""
        MATCH (e:Entity)-[r:FATHER_OF|MOTHER_OF|PARENT_OF|SIBLING_OF|SPOUSE_OF|STEPPARENT_OF]-(other:Entity)
        WHERE e.qid = $qid OR e.dprr_id = $dprr_id
        RETURN type(r) AS rel, other.label AS target_label, other.qid AS target_qid, other.dprr_id AS target_dprr_id
    """, qid=qid, dprr_id=dprr_id or "")
    packet["existing_family"] = [dict(row) for row in r]

    # 3. existing_offices (POSITION_HELD)
    r = session.run("""
        MATCH (e:Entity)-[r:POSITION_HELD]->(p:Position)
        WHERE e.qid = $qid OR e.dprr_id = $dprr_id
        RETURN p.label AS position, p.label_name AS label_name, r.year_start AS year_start
    """, qid=qid, dprr_id=dprr_id or "")
    packet["existing_offices"] = [dict(row) for row in r]

    # 4. dprr_raw: from graph when blocked (OPS-001)
    if dprr_blocked and (dprr_id or (packet.get("person_stub") or {}).get("dprr_id")):
        did = str(dprr_id or (packet.get("person_stub") or {}).get("dprr_id", ""))
        if did:
            r = session.run("""
                MATCH (e:Entity {dprr_id: $dprr_id})
                RETURN e.label AS label, e.label_dprr AS label_dprr, e.label_latin AS label_latin, e.label_sort AS label_sort
            """, dprr_id=did)
            row = r.single()
            if row:
                posts = []
                statuses = []
                r2 = session.run("""
                    MATCH (e:Entity {dprr_id: $dprr_id})-[:POSITION_HELD]->(p:Position)
                    RETURN p.label AS pos, p.label_name AS name
                """, dprr_id=did)
                for x in r2:
                    posts.append({"pos": x["pos"], "name": x["name"]})
                r3 = session.run("""
                    MATCH (e:Entity {dprr_id: $dprr_id})-[:HAS_STATUS]->(st:StatusType)
                    RETURN st.label AS status
                """, dprr_id=did)
                for x in r3:
                    statuses.append({"status": x["status"]})
                packet["dprr_raw"] = {
                    "dprr_id": did, "label": row["label"],
                    "label_dprr": row.get("label_dprr"), "label_latin": row.get("label_latin"), "label_sort": row.get("label_sort"),
                    "posts": posts, "statuses": statuses,
                }

    # 5. wikidata_raw: fetch from Wikidata API/SPARQL
    packet["wikidata_raw"] = _fetch_wikidata_item(qid)

    return packet


def _fetch_wikidata_item(qid: str, timeout: int = 30) -> dict | None:
    """Fetch Wikidata item claims (simplified — main props only)."""
    query = f"""
    SELECT ?prop ?value ?valueLabel WHERE {{
      wd:{qid} ?prop ?value .
      VALUES ?prop {{ wdt:P22 wdt:P25 wdt:P26 wdt:P27 wdt:P31 wdt:P40 wdt:P3373 wdt:P3448 wdt:P21 wdt:P569 wdt:P570 wdt:P19 wdt:P20 wdt:P6863 }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    headers = {"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT}
    try:
        r = requests.get(
            WIKIDATA_SPARQL_ENDPOINT,
            params={"query": query},
            headers=headers,
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        bindings = data.get("results", {}).get("bindings", [])
        claims = {}
        for b in bindings:
            prop = (b.get("prop", {}).get("value") or "").split("/")[-1]
            val = b.get("value", {}).get("value", "")
            val_label = (b.get("valueLabel", {}).get("value", "") or "").strip()
            if prop not in claims:
                claims[prop] = []
            claims[prop].append({"value": val.split("/")[-1] if "/" in val else val, "label": val_label})
        return {"qid": qid, "claims": claims}
    except Exception:
        return None
