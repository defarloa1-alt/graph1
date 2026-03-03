"""
wd_backlink_capture.py
======================
Layer 1 side-capture for Wikidata backlinks during the family tree harvest pass.

Designed to run alongside the main LLM context packet assembly — one SPARQL
query per person, deterministic, no LLM involvement. Results are stored as
properties on the Person node and as a raw JSON candidate list.

Captures:
  - Categorised backlink counts (prominence vector)
  - Raw person→person candidate list for later relationship enrichment

Does NOT:
  - Create WD_BacklinkCandidate nodes
  - Write relationship edges
  - Invoke the LLM
  - Block or slow the main harvest if Wikidata is unavailable

Usage (from harvest script):
    from wd_backlink_capture import capture_backlinks, build_update_cypher

    result = capture_backlinks(qid="Q125414", label="Cn. Pompeius Magnus")
    if result:
        cypher, params = build_update_cypher(entity_id="person_q125414", result=result)
        session.run(cypher, params)
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# ── Wikidata endpoint ─────────────────────────────────────────────────────────

WD_SPARQL = "https://query.wikidata.org/sparql"
WD_HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "Chrystallum/1.0 (knowledge graph harvest; contact via KDL)"
}

# ── P31 instance-of type buckets (10-bucket taxonomy, dev report 2026-03-03) ───
# Calibrated from Pompey backlinks. Numismatic was dominant and was missing.
# Unknown types fall to 'other'. Extend as corpus reveals new patterns.

PERSON_TYPES = {"Q5", "Q215627"}  # human, person

NUMISMATIC_TYPES = {
    "Q41207", "Q113813711", "Q45341", "Q42889", "Q751944", "Q855973"
}  # coin, coin type, aureus, denarius, token, commemorative

EVENT_TYPES = {
    "Q1190554", "Q198", "Q178561", "Q40231", "Q16510064", "Q1656682",
    "Q645883", "Q831663", "Q793"
}  # occurrence, war, battle, election, admin event, event, military op, campaign, siege

POLITICAL_ACT_TYPES = {
    "Q198", "Q178561", "Q645883", "Q831663", "Q793", "Q7184903", "Q131774",
    "Q4916", "Q1054718", "Q112965045"
}  # war, battle, military op, campaign, siege, civil war, alliance, contract, reorg, historical event

MILITARY_UNIT_TYPES = {"Q163323", "Q8473", "Q706"}  # Roman legion, military unit, org

PLACE_TYPES = {
    "Q618123", "Q2221906", "Q515", "Q6256", "Q3624078", "Q23442", "Q8502",
    "Q23397", "Q4022", "Q35145263", "Q8392", "Q41176", "Q23413", "Q17350442"
}  # geo, city, country, island, mountain, lake, river, settlement, arch site, building, theatre, domus

SCHOLARLY_RECEPTION_TYPES = {
    "Q13433827", "Q26267864", "Q591041", "Q5292", "Q4167410", "Q1343246"
}  # encyclopedia article, reference entry, reference work, encyclopedia, Wikipedia

MODERN_RECEPTION_TYPES = {
    "Q11424", "Q5398426", "Q24862", "Q28878302", "Q2431196"
}  # film, TV series, TV film, web series, audiovisual

VISUAL_ARTS_TYPES = {
    "Q3305213", "Q860861", "Q178659", "Q184296", "Q93184", "Q838948", "Q4502142"
}  # painting, sculpture, statue, bust, drawing, work of art, artistic theme

FICTIONAL_REPRESENTATION_TYPES = {
    "Q15632617", "Q95074", "Q1114461"
}  # fictional human, fictional character, comics character

FILTER_TYPES = {"Q4167836", "Q18616576"}  # Wikimedia category, Wikidata property — exclude


def _classify_type(instance_of_qids: list[str]) -> str:
    """
    Given P31 (instance of) QIDs for a backlink source item, return bucket name.
    10-bucket taxonomy per dev report 2026-03-03.
    """
    qid_set = set(instance_of_qids) - FILTER_TYPES
    if not qid_set:
        return "other"
    if qid_set & PERSON_TYPES:
        return "persons"
    if qid_set & NUMISMATIC_TYPES:
        return "numismatic"
    if qid_set & POLITICAL_ACT_TYPES:
        return "political_acts"
    if qid_set & EVENT_TYPES:
        return "events"
    if qid_set & MILITARY_UNIT_TYPES:
        return "military_units"
    if qid_set & PLACE_TYPES:
        return "physical_legacy"
    if qid_set & SCHOLARLY_RECEPTION_TYPES:
        return "scholarly_reception"
    if qid_set & MODERN_RECEPTION_TYPES:
        return "modern_reception"
    if qid_set & VISUAL_ARTS_TYPES:
        return "visual_arts"
    if qid_set & FICTIONAL_REPRESENTATION_TYPES:
        return "fictional_representations"
    return "other"


# ── SPARQL query ──────────────────────────────────────────────────────────────

BACKLINK_SPARQL = """
SELECT ?item ?itemLabel ?prop ?typeQid WHERE {{
  ?item ?prop wd:{qid} .
  OPTIONAL {{ ?item wdt:P31 ?typeQid . }}
  FILTER(?prop != schema:dateModified)
  FILTER(?prop != owl:sameAs)
  FILTER(STRSTARTS(STR(?prop), "http://www.wikidata.org/prop/direct/"))
  FILTER NOT EXISTS {{
    ?item wdt:P31 ?p31 .
    FILTER(?p31 IN (wd:Q4167836, wd:Q18616576))
  }}
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en,la" .
  }}
}}
LIMIT 500
"""


def _run_sparql(qid: str, timeout: int = 15) -> Optional[list[dict]]:
    """
    Execute the backlink SPARQL query. Returns raw bindings or None on failure.
    Non-blocking: any error returns None so the harvest pass continues.
    """
    query = BACKLINK_SPARQL.format(qid=qid)
    try:
        resp = requests.get(
            WD_SPARQL,
            params={"query": query, "format": "json"},
            headers=WD_HEADERS,
            timeout=timeout
        )
        if resp.status_code == 429:
            logger.warning("Wikidata rate limit on %s — skipping backlink capture", qid)
            return None
        if resp.status_code != 200:
            logger.warning("Wikidata HTTP %s for %s", resp.status_code, qid)
            return None
        return resp.json().get("results", {}).get("bindings", [])
    except requests.Timeout:
        logger.warning("Wikidata timeout for %s — skipping backlink capture", qid)
        return None
    except Exception as e:
        logger.warning("Wikidata error for %s: %s", qid, e)
        return None


# ── Core capture function ─────────────────────────────────────────────────────

def capture_backlinks(qid: str, label: str = "") -> Optional[dict]:
    """
    Query Wikidata for all items referencing this person (backlinks).
    Returns a structured result dict, or None if the query failed.

    Result structure:
    {
        "qid": "Q125414",
        "wd_bl_total": 47,
        "wd_bl_persons": 12,
        "wd_bl_events": 18,
        "wd_bl_places": 4,
        "wd_bl_works": 8,
        "wd_bl_reference_entries": 3,
        "wd_bl_other": 2,
        "wd_bl_harvested_at": "2026-03-03T...",
        "wd_bl_capped": False,   # True if result hit the 500-row LIMIT
        "wd_bl_candidate_persons": [
            {"qid": "Q336538", "label": "Cn. Pompeius Strabo", "property_id": "P22"},
            ...
        ]
    }
    """
    if not qid or not qid.startswith("Q"):
        logger.debug("Skipping backlink capture — no valid QID for %s", label)
        return None

    bindings = _run_sparql(qid)
    if bindings is None:
        return None

    # ── Aggregate ─────────────────────────────────────────────────────────────
    # Group by item QID first — each item may have multiple P31 values
    items: dict[str, dict] = {}
    for row in bindings:
        item_uri = row.get("item", {}).get("value", "")
        if not item_uri:
            continue

        item_qid = item_uri.rsplit("/", 1)[-1]  # extract Q-number
        prop_uri  = row.get("prop", {}).get("value", "")
        prop_id   = prop_uri.rsplit("/", 1)[-1]  # extract P-number
        type_uri  = row.get("typeQid", {}).get("value", "")
        type_qid  = type_uri.rsplit("/", 1)[-1] if type_uri else ""
        item_label = row.get("itemLabel", {}).get("value", item_qid)

        if item_qid not in items:
            items[item_qid] = {
                "qid": item_qid,
                "label": item_label,
                "properties": set(),
                "type_qids": set()
            }

        if prop_id:
            items[item_qid]["properties"].add(prop_id)
        if type_qid:
            items[item_qid]["type_qids"].add(type_qid)

    # ── Classify and count ────────────────────────────────────────────────────
    counts = {
        "persons": 0,
        "numismatic": 0,
        "events": 0,
        "political_acts": 0,
        "military_units": 0,
        "physical_legacy": 0,
        "scholarly_reception": 0,
        "modern_reception": 0,
        "visual_arts": 0,
        "fictional_representations": 0,
        "other": 0,
    }
    candidate_persons = []

    for item_qid, item in items.items():
        bucket = _classify_type(list(item["type_qids"]))
        counts[bucket] += 1

        # Capture person→person candidates — one entry per property per source
        if bucket == "persons":
            for prop_id in item["properties"]:
                candidate_persons.append({
                    "qid": item_qid,
                    "label": item["label"],
                    "property_id": prop_id
                })

    total = sum(counts.values())

    result = {
        "qid": qid,
        "wd_bl_total": total,
        "wd_bl_persons": counts["persons"],
        "wd_bl_numismatic": counts["numismatic"],
        "wd_bl_events": counts["events"],
        "wd_bl_political_acts": counts["political_acts"],
        "wd_bl_military_units": counts["military_units"],
        "wd_bl_physical_legacy": counts["physical_legacy"],
        "wd_bl_scholarly_reception": counts["scholarly_reception"],
        "wd_bl_modern_reception": counts["modern_reception"],
        "wd_bl_visual_arts": counts["visual_arts"],
        "wd_bl_fictional_representations": counts["fictional_representations"],
        "wd_bl_other": counts["other"],
        "wd_bl_harvested_at": datetime.now(timezone.utc).isoformat(),
        "wd_bl_capped": len(bindings) >= 500,  # hit LIMIT — counts are incomplete
        "wd_bl_candidate_persons": candidate_persons
    }

    logger.info(
        "Backlinks for %s (%s): total=%d  persons=%d  numismatic=%d  events=%d  "
        "political=%d  military=%d  physical=%d  scholarly=%d  modern=%d  "
        "visual=%d  fictional=%d  other=%d  candidates=%d%s",
        qid, label, total,
        counts["persons"], counts["numismatic"], counts["events"],
        counts["political_acts"], counts["military_units"], counts["physical_legacy"],
        counts["scholarly_reception"], counts["modern_reception"],
        counts["visual_arts"], counts["fictional_representations"], counts["other"],
        len(candidate_persons),
        "  [CAPPED]" if result["wd_bl_capped"] else ""
    )

    return result


# ── Neo4j write ───────────────────────────────────────────────────────────────

def build_update_cypher(entity_id: str, result: dict) -> tuple[str, dict]:
    """
    Build the Cypher SET statement and parameter dict to persist
    the backlink capture result onto the Person node.

    Returns (cypher_string, params_dict) ready for session.run().

    Candidate persons are stored as a JSON string — Neo4j has no native
    list-of-maps property type. Deserialise on read with json.loads().
    """
    cypher = """
MATCH (n:Entity {entity_id: $entity_id})
SET n.wd_bl_total                   = $wd_bl_total,
    n.wd_bl_persons                 = $wd_bl_persons,
    n.wd_bl_numismatic              = $wd_bl_numismatic,
    n.wd_bl_events                  = $wd_bl_events,
    n.wd_bl_political_acts          = $wd_bl_political_acts,
    n.wd_bl_military_units          = $wd_bl_military_units,
    n.wd_bl_physical_legacy         = $wd_bl_physical_legacy,
    n.wd_bl_scholarly_reception     = $wd_bl_scholarly_reception,
    n.wd_bl_modern_reception        = $wd_bl_modern_reception,
    n.wd_bl_visual_arts             = $wd_bl_visual_arts,
    n.wd_bl_fictional_representations = $wd_bl_fictional_representations,
    n.wd_bl_other                   = $wd_bl_other,
    n.wd_bl_harvested_at            = $wd_bl_harvested_at,
    n.wd_bl_capped                  = $wd_bl_capped,
    n.wd_bl_candidate_persons       = $wd_bl_candidate_persons
RETURN n.entity_id AS updated
"""
    params = {
        "entity_id": entity_id,
        "wd_bl_total": result["wd_bl_total"],
        "wd_bl_persons": result["wd_bl_persons"],
        "wd_bl_numismatic": result["wd_bl_numismatic"],
        "wd_bl_events": result["wd_bl_events"],
        "wd_bl_political_acts": result["wd_bl_political_acts"],
        "wd_bl_military_units": result["wd_bl_military_units"],
        "wd_bl_physical_legacy": result["wd_bl_physical_legacy"],
        "wd_bl_scholarly_reception": result["wd_bl_scholarly_reception"],
        "wd_bl_modern_reception": result["wd_bl_modern_reception"],
        "wd_bl_visual_arts": result["wd_bl_visual_arts"],
        "wd_bl_fictional_representations": result["wd_bl_fictional_representations"],
        "wd_bl_other": result["wd_bl_other"],
        "wd_bl_harvested_at": result["wd_bl_harvested_at"],
        "wd_bl_capped": result["wd_bl_capped"],
        "wd_bl_candidate_persons": json.dumps(
            result["wd_bl_candidate_persons"], ensure_ascii=False
        ),
    }
    return cypher.strip(), params


# ── Rate limit helper ─────────────────────────────────────────────────────────

class RateLimiter:
    """
    Simple token bucket for Wikidata SPARQL.
    Wikidata's published limit is 5 req/s for SPARQL — be conservative at 3/s
    to avoid 429s during a long batch.
    """
    def __init__(self, calls_per_second: float = 3.0):
        self.min_interval = 1.0 / calls_per_second
        self._last_call = 0.0

    def wait(self):
        elapsed = time.monotonic() - self._last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_call = time.monotonic()


# ── Batch helper ─────────────────────────────────────────────────────────────

def capture_batch(
    persons: list[dict],
    neo4j_session,
    rate_limiter: Optional[RateLimiter] = None
) -> dict:
    """
    Run backlink capture for a list of person dicts.
    Each dict must have keys: entity_id, qid, label (label is for logging only).

    persons = [
        {"entity_id": "person_q125414", "qid": "Q125414", "label": "Cn. Pompeius Magnus"},
        ...
    ]

    Skips persons with no QID or QID that looks like a hash (non-Wikidata).
    Returns summary stats dict.
    """
    if rate_limiter is None:
        rate_limiter = RateLimiter()

    stats = {"attempted": 0, "captured": 0, "skipped_no_qid": 0,
             "failed": 0, "capped": 0}

    for person in persons:
        qid = person.get("qid", "")
        entity_id = person.get("entity_id", "")
        label = person.get("label", qid)

        # Skip hash-style QIDs from non-Wikidata ingest
        if not qid or not qid.startswith("Q") or len(qid) > 12:
            stats["skipped_no_qid"] += 1
            continue

        stats["attempted"] += 1
        rate_limiter.wait()

        result = capture_backlinks(qid=qid, label=label)
        if result is None:
            stats["failed"] += 1
            continue

        if result["wd_bl_capped"]:
            stats["capped"] += 1
            logger.warning(
                "Backlink result capped at 500 for %s (%s) — "
                "consider a targeted follow-up query for high-prominence persons",
                qid, label
            )

        cypher, params = build_update_cypher(entity_id=entity_id, result=result)
        try:
            neo4j_session.run(cypher, params)
            stats["captured"] += 1
        except Exception as e:
            logger.error("Neo4j write failed for %s: %s", entity_id, e)
            stats["failed"] += 1

    logger.info(
        "Backlink capture batch complete: attempted=%d captured=%d "
        "skipped=%d failed=%d capped=%d",
        stats["attempted"], stats["captured"],
        stats["skipped_no_qid"], stats["failed"], stats["capped"]
    )
    return stats


# ── Integration point for harvest script ─────────────────────────────────────
#
# Drop into the per-person loop AFTER DPRR label parse, BEFORE LLM invocation.
# existing_edges comes from the context packet pre-fetch (family + office edges).
#
#   from wd_backlink_capture import (
#       capture_backlinks, filter_candidates, build_update_cypher, RateLimiter
#   )
#
#   rl = RateLimiter()   # one instance for the whole run
#
#   # Inside per-person loop:
#   if person["qid"] and person["qid"].startswith("Q"):
#       rl.wait()
#       bl = capture_backlinks(qid=person["qid"], label=person["label"])
#       if bl:
#           # Deduplicate against existing graph edges
#           existing_edges = context_packet.get("existing_family", [])
#           # existing_edges format: [{"qid": "Q336538", "rel_type": "FATHER_OF"}, ...]
#           filtered, counts = filter_candidates(bl["wd_bl_candidate_persons"], existing_edges)
#           bl["wd_bl_candidate_persons"]         = filtered
#           bl["wd_bl_candidate_novel_count"]     = counts["novel"]
#           bl["wd_bl_candidate_redundant_count"] = counts["redundant"]
#           bl["wd_bl_candidate_conflict_count"]  = counts["conflict"]
#
#           cypher, params = build_update_cypher(person["entity_id"], bl)
#           session.run(cypher, params)
#
#           # Pass profile into LLM context packet:
#           context_packet["backlink_profile"] = {
#               "total":      bl["wd_bl_total"],
#               "numismatic": bl["wd_bl_numismatic"],   # > 0 → Nomisma priority
#               "persons":    bl["wd_bl_persons"],
#               "events":     bl["wd_bl_political_acts"],
#               "novel":      counts["novel"],
#               "redundant":  counts["redundant"],       # high = good WD/DPRR alignment
#           }
#           # LLM emits backlink_significance_note in PersonHarvestPlan
#
# ── Reading candidates back out (future enrichment pass) ─────────────────────
#
#   MATCH (n:Entity {entity_type:'PERSON'})
#   WHERE n.wd_bl_candidate_persons IS NOT NULL
#     AND n.wd_bl_candidate_novel_count > 0
#   RETURN n.entity_id, n.label,
#          n.wd_bl_candidate_novel_count,
#          n.wd_bl_candidate_persons
#   ORDER BY n.wd_bl_candidate_novel_count DESC
#
#   import json
#   candidates = json.loads(node["wd_bl_candidate_persons"])
#   # [{qid, label, property_id, candidate_class, canonical_rel}, ...]
#   novel     = [c for c in candidates if c["candidate_class"] == "novel"]
#   conflicts = [c for c in candidates if c["candidate_class"] == "conflict"]
#
# ── Nomisma priority queue ────────────────────────────────────────────────────
#
#   MATCH (n:Entity {entity_type:'PERSON'})
#   WHERE n.wd_bl_numismatic > 0
#   RETURN n.entity_id, n.label, n.wd_bl_numismatic
#   ORDER BY n.wd_bl_numismatic DESC
#   # → feed directly into Nomisma harvest queue
