"""
Biographic Subject Agent — core harvest logic

Harvests biographical context for Person nodes with QIDs:
  1. Forward properties (P569/570/19/20/509/119, external IDs, events)
  2. Backlinks (items referencing the person)
  3. Spouse qualifiers (P26 with P580/P582/P1545/P1534/P2842)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[3]  # project root (Graph1)
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import requests
from neo4j import GraphDatabase

from scripts.tools.entity_cipher import generate_entity_cipher


# ── Config ────────────────────────────────────────────────────────────────────

def _load_env() -> dict:
    env_path = _root / ".env"
    if not env_path.exists():
        raise FileNotFoundError(f".env not found at {env_path}")
    env = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env

_env = _load_env()
NEO4J_URI      = _env.get("NEO4J_URI",  "neo4j+s://ac63a8e5.databases.neo4j.io")
NEO4J_USER     = _env.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = _env["NEO4J_PASSWORD"]

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
HEADERS = {"User-Agent": "Chrystallum-BiographicAgent/1.0 (chrystallum@example.com)"}
SLEEP_SEC  = 1.0
BATCH_SIZE = 25

# ── Backlink predicate map (fallback when SYS_Policy BacklinkRouting not present) ─
BACKLINK_PREDICATE_MAP = {
    "P22":   ("CHILD_OF",        "inbound",   "father",   "bio"),
    "P25":   ("CHILD_OF",        "inbound",   "mother",   "bio"),
    "P26":   ("SPOUSE_OF",       "inbound",   None,       "bio"),
    "P3373": ("SIBLING_OF",      "inbound",   None,       "bio"),
    "P40":   ("PARENT_OF",       "outbound",  None,       "bio"),
    "P1038": ("RELATED_TO",      "inbound",   "kinship",  "bio"),
    "P3448": ("STEPPARENT_OF",   "inbound",   None,       "bio"),
    "P1066": ("TEACHER_OF",      "outbound",  None,       "bio"),
    "P802":  ("STUDENT_OF",      "inbound",   None,       "bio"),
    "P737":  ("INFLUENCED",      "outbound",  None,       "bio"),
    "P710":  ("PARTICIPATED_IN", "outbound",  None,       "military"),
    "P664":  ("ORGANIZED",       "outbound",  None,       "military"),
    "P748":  ("APPOINTED_BY",    "inbound",   None,       "military"),
    "P1308": ("HAD_ROLE",        "outbound",  "role",     "military"),
    "P488":  ("CHAIRED",         "outbound",  None,       "political"),
    "P6":    ("HEADED",          "outbound",  None,       "political"),
    "P112":  ("FOUNDED",         "outbound",  None,       "political"),
    "P138":  ("NAMESAKE_OF",     "outbound",  None,       "geographic"),
    "P176":  ("COMMISSIONED",    "outbound",  None,       "geographic"),
    "P1344": ("PARTICIPATED_IN", "outbound",  None,       "social"),
}

FORWARD_PROPS = {
    "P569": "birth_date", "P570": "death_date",
    "P19":  "birth_place_qid", "P20":  "death_place_qid",
    "P509": "cause_of_death_qid", "P119": "burial_place_qid",
    "P214": "viaf_id", "P227": "gnd_id", "P244": "lcnaf_id",
    "P1415": "ocd_id", "P3348": "nomisma_id", "P1667": "getty_tgn_id",
    "P607": "conflict_qid", "P793": "significant_event_qid",
    "P1344": "participated_in_qid", "P166": "award_qid",
    "P21": "sex_or_gender_qid", "P53": "noble_family_qid",
    "P172": "ethnic_group_qid", "P1317": "floruit",
}


def parse_year(date_str: str) -> int | None:
    if not date_str:
        return None
    m = re.match(r'^([+-]?)(\d{4})', date_str)
    if not m:
        return None
    sign, digits = m.groups()
    year = int(digits)
    if sign == '-':
        year = -year
    if year == 0:
        year = -1
    return year


def sparql(query: str) -> list[dict]:
    resp = requests.get(
        WIKIDATA_SPARQL,
        params={"query": query, "format": "json"},
        headers=HEADERS,
        timeout=45,
    )
    resp.raise_for_status()
    return resp.json()["results"]["bindings"]


def fetch_forward_props(qid: str) -> dict:
    EVENT_KEYS = ("conflict_qid", "significant_event_qid",
                  "participated_in_qid", "award_qid")
    EVENT_PIDS = {k: v for k, v in FORWARD_PROPS.items() if v in EVENT_KEYS}
    SCALAR_PIDS = {k: v for k, v in FORWARD_PROPS.items() if v not in EVENT_KEYS}

    result = {}
    prop_list = " ".join(f"wdt:{p}" for p in SCALAR_PIDS)
    rows = sparql(f"""
    SELECT ?prop ?value ?valueLabel WHERE {{
      VALUES ?prop {{ {prop_list} }}
      wd:{qid} ?prop ?value .
      OPTIONAL {{ ?value rdfs:label ?valueLabel . FILTER(LANG(?valueLabel)="en") }}
    }}
    """)
    for row in rows:
        pid = row["prop"]["value"].split("/")[-1]
        val = row["value"]["value"]
        key = SCALAR_PIDS.get(pid, pid)
        if key not in result:
            result[key] = val.split("/")[-1] if val.startswith("http") else val

    p_vals  = " ".join(f"p:{p}"  for p in EVENT_PIDS)
    ps_vals = " ".join(f"ps:{p}" for p in EVENT_PIDS)
    event_rows = sparql(f"""
    SELECT ?directClaim ?event ?eventLabel WHERE {{
      VALUES ?p  {{ {p_vals}  }}
      VALUES ?ps {{ {ps_vals} }}
      wd:{qid} ?p ?stmt .
      ?stmt ?ps ?event .
      ?propNode wikibase:statementProperty ?ps .
      ?propNode wikibase:directClaim ?directClaim .
      OPTIONAL {{ ?event rdfs:label ?eventLabel . FILTER(LANG(?eventLabel)="en") }}
    }}
    """)
    for row in event_rows:
        pid   = row["directClaim"]["value"].split("/")[-1]
        val   = row["event"]["value"]
        label = row.get("eventLabel", {}).get("value")
        key   = EVENT_PIDS.get(pid, pid)
        result.setdefault(key, [])
        entry = {"qid": val.split("/")[-1], "label": label}
        if entry not in result[key]:
            result[key].append(entry)

    return result


def fetch_spouse_qualifiers(qid: str) -> list[dict]:
    rows = sparql(f"""
    SELECT ?spouse ?spouseLabel ?spouseQid
           ?start ?end ?ordinal ?endCause ?endCauseLabel ?placeOfMarriage ?placeLabel
    WHERE {{
      wd:{qid} p:P26 ?stmt .
      ?stmt ps:P26 ?spouse .
      BIND(STRAFTER(STR(?spouse), "entity/") AS ?spouseQid)
      OPTIONAL {{ ?stmt pq:P580 ?start }}
      OPTIONAL {{ ?stmt pq:P582 ?end }}
      OPTIONAL {{ ?stmt pq:P1545 ?ordinal }}
      OPTIONAL {{ ?stmt pq:P1534 ?endCause . ?endCause rdfs:label ?endCauseLabel
                  FILTER(LANG(?endCauseLabel)="en") }}
      OPTIONAL {{ ?stmt pq:P2842 ?placeOfMarriage . ?placeOfMarriage rdfs:label ?placeLabel
                  FILTER(LANG(?placeLabel)="en") }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
    }}
    """)
    marriages = []
    for row in rows:
        marriages.append({
            "spouse_qid":       row.get("spouseQid", {}).get("value"),
            "spouse_label":     row.get("spouseLabel", {}).get("value"),
            "start_year":       parse_year(row.get("start", {}).get("value")),
            "end_year":         parse_year(row.get("end", {}).get("value")),
            "series_ordinal":   row.get("ordinal", {}).get("value"),
            "end_reason":       row.get("endCauseLabel", {}).get("value"),
            "place_qid":        row.get("placeOfMarriage", {}).get("value", "").split("/")[-1] or None,
            "place_label":      row.get("placeLabel", {}).get("value"),
        })
    return marriages


def fetch_backlinks(qid: str, predicate_map: dict | None = None) -> list[dict]:
    pmap = predicate_map or BACKLINK_PREDICATE_MAP
    pred_filter = " ".join(f"wdt:{p}" for p in pmap)
    rows = sparql(f"""
    SELECT DISTINCT ?item ?itemLabel ?itemType ?itemTypeLabel ?pred WHERE {{
      VALUES ?pred {{ {pred_filter} }}
      ?item ?pred wd:{qid} .
      OPTIONAL {{
        ?item wdt:P31 ?itemType .
        ?itemType rdfs:label ?itemTypeLabel .
        FILTER(LANG(?itemTypeLabel) = "en")
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
    }}
    """)
    results = []
    for row in rows:
        pid      = row["pred"]["value"].split("/")[-1]
        item_qid = row["item"]["value"].split("/")[-1]
        mapping  = pmap.get(pid, ("RELATED_TO", "inbound", None, "bio"))
        if isinstance(mapping, tuple):
            edge_type, direction, qualifier, sfa_queue = mapping
        else:
            edge_type  = mapping.get("edge_type", "RELATED_TO")
            direction  = mapping.get("direction", "inbound")
            qualifier  = mapping.get("qualifier")
            sfa_queue  = mapping.get("sfa_queue", "bio")
        results.append({
            "item_qid":        item_qid,
            "item_label":      row.get("itemLabel", {}).get("value"),
            "item_type_qid":   row.get("itemType",  {}).get("value", "").split("/")[-1] or None,
            "item_type_label": row.get("itemTypeLabel", {}).get("value"),
            "pred_pid":        pid,
            "edge_type":       edge_type,
            "direction":       direction,
            "qualifier":       qualifier,
            "sfa_queue":       sfa_queue,
        })
    return results


def resolve_place_pleiades(session, place_qid: str) -> str | None:
    if not place_qid:
        return None
    result = session.run(
        "MATCH (e:Entity {qid: $qid}) WHERE e.pleiades_id IS NOT NULL "
        "RETURN e.pleiades_id AS pleiades_id LIMIT 1",
        qid=place_qid
    ).single()
    if result:
        return result["pleiades_id"]
    try:
        rows = sparql(f"""
        SELECT ?pleiades WHERE {{
          wd:{place_qid} wdt:P1566 ?pleiades .
        }}
        """)
        if rows:
            return rows[0]["pleiades"]["value"]
    except Exception:
        pass
    return None


# ── Cypher templates ───────────────────────────────────────────────────────────

WRITE_BIO_ANCHORS = """
MATCH (p:Person {qid: $qid})
SET p.birth_year           = $birth_year,
    p.death_year           = $death_year,
    p.birth_place_qid      = $birth_place_qid,
    p.death_place_qid      = $death_place_qid,
    p.burial_place_qid     = $burial_place_qid,
    p.cause_of_death_qid   = $cause_of_death_qid,
    p.gnd_id               = $gnd_id,
    p.lcnaf_id             = $lcnaf_id,
    p.ocd_id               = $ocd_id,
    p.nomisma_id           = $nomisma_id,
    p.bio_harvested_at     = datetime()

WITH p
FOREACH (_ IN CASE WHEN $birth_year IS NOT NULL THEN [1] ELSE [] END |
  MERGE (y:Year {year: $birth_year})
  MERGE (p)-[:BORN_IN_YEAR {source: 'wikidata_p569'}]->(y)
)
FOREACH (_ IN CASE WHEN $death_year IS NOT NULL THEN [1] ELSE [] END |
  MERGE (y:Year {year: $death_year})
  MERGE (p)-[:DIED_IN_YEAR {source: 'wikidata_p570'}]->(y)
)
FOREACH (_ IN CASE WHEN $birth_place_qid IS NOT NULL THEN [1] ELSE [] END |
  MERGE (pl:Place {qid: $birth_place_qid})
  ON CREATE SET pl.label = coalesce($birth_place_label, $birth_place_qid),
                pl.entity_type = 'Place',
                pl.pleiades_id = $birth_pleiades,
                pl.resolved = ($birth_pleiades IS NOT NULL),
                pl.place_type = CASE WHEN $birth_pleiades IS NULL THEN 'region_stub' ELSE null END
  ON MATCH SET pl.pleiades_id = coalesce(pl.pleiades_id, $birth_pleiades)
  MERGE (p)-[:BORN_IN_PLACE {
    source: 'wikidata_p19',
    place_qid: $birth_place_qid,
    resolved: ($birth_pleiades IS NOT NULL)
  }]->(pl)
)
FOREACH (_ IN CASE WHEN $death_place_qid IS NOT NULL THEN [1] ELSE [] END |
  MERGE (pl:Place {qid: $death_place_qid})
  ON CREATE SET pl.label = coalesce($death_place_label, $death_place_qid),
                pl.entity_type = 'Place',
                pl.pleiades_id = $death_pleiades,
                pl.resolved = ($death_pleiades IS NOT NULL),
                pl.place_type = CASE WHEN $death_pleiades IS NULL THEN 'region_stub' ELSE null END
  ON MATCH SET pl.pleiades_id = coalesce(pl.pleiades_id, $death_pleiades)
  MERGE (p)-[:DIED_IN_PLACE {
    source: 'wikidata_p20',
    place_qid: $death_place_qid,
    resolved: ($death_pleiades IS NOT NULL)
  }]->(pl)
)
FOREACH (_ IN CASE WHEN $burial_place_qid IS NOT NULL THEN [1] ELSE [] END |
  MERGE (pl:Place {qid: $burial_place_qid})
  ON CREATE SET pl.label = coalesce($burial_place_label, $burial_place_qid),
                pl.entity_type = 'Place',
                pl.pleiades_id = $burial_pleiades,
                pl.resolved = ($burial_pleiades IS NOT NULL),
                pl.place_type = CASE WHEN $burial_pleiades IS NULL THEN 'region_stub' ELSE null END
  ON MATCH SET pl.pleiades_id = coalesce(pl.pleiades_id, $burial_pleiades)
  MERGE (p)-[:BURIED_AT {
    source: 'wikidata_p119',
    place_qid: $burial_place_qid,
    resolved: ($burial_pleiades IS NOT NULL)
  }]->(pl)
)
"""

WRITE_MARRIAGE_QUALIFIERS = """
MATCH (p:Person {qid: $person_qid})
MATCH (s:Person {qid: $spouse_qid})
MERGE (p)-[r:SPOUSE_OF]->(s)
SET r.start_year      = $start_year,
    r.end_year        = $end_year,
    r.series_ordinal  = $series_ordinal,
    r.end_reason      = $end_reason,
    r.place_qid       = $place_qid,
    r.place_label     = $place_label,
    r.source          = 'wikidata_p26_qualifiers',
    r.enriched_at     = datetime()
"""

WRITE_BACKLINK_CANDIDATE = """
MERGE (candidate:Entity {qid: $item_qid})
  ON CREATE SET candidate.label          = $item_label,
                candidate.qid            = $item_qid,
                candidate.entity_id      = 'entity_' + $item_qid,
                candidate.entity_type    = 'STUB',
                candidate.entity_cipher   = $entity_cipher,
                candidate.item_type_qid  = $item_type_qid,
                candidate.item_type_label= $item_type_label,
                candidate.stub           = true

WITH candidate
MATCH (p:Person {qid: $person_qid})
MERGE (candidate)-[r:BIO_CANDIDATE_REL {pred_pid: $pred_pid, person_qid: $person_qid}]->(p)
SET r.edge_type        = $edge_type,
    r.direction        = $direction,
    r.qualifier        = $qualifier,
    r.item_label       = $item_label,
    r.item_type_label  = $item_type_label,
    r.sfa_queue        = $sfa_queue,
    r.source           = 'wikidata_backlink',
    r.agent_reviewed   = false,
    r.harvested_at     = datetime()
"""

WRITE_EVENT_PARTICIPATION = """
MERGE (evt:Event {qid: $event_qid})
  ON CREATE SET evt.label     = $event_label,
                evt.event_type = $event_type,
                evt.qid        = $event_qid
MERGE (p:Person {qid: $person_qid})
MERGE (p)-[r:PARTICIPATED_IN]->(evt)
SET r.source = 'wikidata_' + $prop_id,
    r.harvested_at = datetime()
"""


# ── Core harvest ──────────────────────────────────────────────────────────────

def harvest_person(
    qid: str,
    dprr_id: str,
    session,
    dry_run: bool = False,
    decision_model=None,
):
    """
    Harvest biographical context for one person.
    If decision_model is provided and has BacklinkRouting, uses it for routing.
    """
    from collections import Counter

    print(f"\n{'='*60}")
    print(f"Harvesting: {dprr_id} / {qid}")
    print(f"{'='*60}")

    # 1. Forward properties
    print("  [1/3] Fetching forward properties...")
    props = fetch_forward_props(qid)
    birth_year = parse_year(props.get("birth_date", ""))
    death_year = parse_year(props.get("death_date", ""))

    birth_place_qid  = props.get("birth_place_qid")
    death_place_qid  = props.get("death_place_qid")
    burial_place_qid = props.get("burial_place_qid")

    birth_pleiades  = resolve_place_pleiades(session, birth_place_qid)
    death_pleiades  = resolve_place_pleiades(session, death_place_qid)
    burial_pleiades = resolve_place_pleiades(session, burial_place_qid)

    def place_label(qid_val):
        if not qid_val:
            return None
        try:
            rows = sparql(f"""
            SELECT ?label WHERE {{
              wd:{qid_val} rdfs:label ?label . FILTER(LANG(?label)="en")
            }} LIMIT 1""")
            return rows[0]["label"]["value"] if rows else qid_val
        except Exception:
            return qid_val

    birth_place_label  = None if birth_pleiades  else place_label(birth_place_qid)
    death_place_label  = None if death_pleiades  else place_label(death_place_qid)
    burial_place_label = None if burial_pleiades else place_label(burial_place_qid)

    born_str  = (birth_pleiades  or f"stub:{birth_place_label}")  if birth_place_qid  else "-"
    died_str  = (death_pleiades  or f"stub:{death_place_label}")  if death_place_qid  else "-"
    print(f"    birth: {birth_year}  death: {death_year}")
    print(f"    born_place: {born_str}  died_place: {died_str}")
    print(f"    OCD: {props.get('ocd_id','-')}  GND: {props.get('gnd_id','-')}  "
          f"LCNAF: {props.get('lcnaf_id','-')}")

    conflicts = props.get("conflict_qid", [])
    events    = props.get("significant_event_qid", []) + props.get("participated_in_qid", [])
    print(f"    conflicts: {len(conflicts)}  events: {len(events)}")
    for e in conflicts + events:
        print(f"      {e.get('label') or e['qid']}")

    # 2. Spouse qualifiers
    print("  [2/3] Fetching spouse qualifiers...")
    marriages = fetch_spouse_qualifiers(qid)
    print(f"    marriages with qualifiers: {len(marriages)}")
    for m in marriages:
        print(f"      {m['spouse_label']:<30} ord:{m['series_ordinal']}  "
              f"{m['start_year'] or '?'}->{m['end_year'] or '?'}  "
              f"end:{m['end_reason'] or '-'}")

    # 3. Backlinks — use decision model if available
    backlink_map = None
    if decision_model and decision_model._backlink:
        backlink_map = {}
        for pid in BACKLINK_PREDICATE_MAP:
            backlink_map[pid] = lambda p=pid, dm=decision_model: dm.route_backlink(p, None)
        # Build map from pid -> (edge_type, direction, qualifier, sfa_queue)
        def _route(pid, itl):
            r = decision_model.route_backlink(pid, itl)
            return (r["edge_type"], r["direction"], r.get("qualifier"), r["sfa_queue"])
        backlink_map = {pid: (lambda p=pid: lambda itl: _route(p, itl))() for pid in BACKLINK_PREDICATE_MAP}
        # Simpler: fetch_backlinks uses predicate_map for routing; we need to build
        # a map that returns (edge_type, direction, qualifier, sfa_queue) per (pid, item_type_label).
        # fetch_backlinks does the routing per row. So we need to either:
        # 1. Change fetch_backlinks to accept a decision_model and call route_backlink per row
        # 2. Or pre-build a mapping. The decision model routes by (pred_pid, item_type_class).
        # So we need to call route_backlink per backlink item. Let me change fetch_backlinks
        # to accept an optional decision_model and use it when present.
        pass  # Will use decision_model in the loop below

    print("  [3/3] Fetching backlinks...")
    backlinks = fetch_backlinks(qid)

    if decision_model and decision_model._backlink:
        for bl in backlinks:
            r = decision_model.route_backlink(bl["pred_pid"], bl["item_type_label"])
            bl["edge_type"] = r["edge_type"]
            bl["direction"] = r["direction"]
            bl["qualifier"] = r.get("qualifier")
            bl["sfa_queue"] = r["sfa_queue"]

    bl_by_queue = Counter(b["sfa_queue"] for b in backlinks)
    bl_by_type  = Counter(f"{b['edge_type']} ({b['sfa_queue']})" for b in backlinks)
    print(f"    total backlink items: {len(backlinks)}")
    print(f"    by SFA queue: " + "  ".join(f"{q}:{n}" for q, n in sorted(bl_by_queue.items())))
    for etype, cnt in sorted(bl_by_type.items(), key=lambda x: -x[1]):
        print(f"      {etype:<40} {cnt}")
    print()
    print("    sample items:")
    for b in backlinks[:15]:
        itype = b["item_type_label"] or "?"
        print(f"      [{b['sfa_queue']:<10}] {b['item_label'] or b['item_qid']:<35} "
              f"type:{itype:<20} via:{b['pred_pid']}")

    if dry_run:
        print("  [DRY RUN - no writes]")
        return

    # Writes
    session.run(WRITE_BIO_ANCHORS, {
        "qid":                qid,
        "birth_year":         birth_year,
        "death_year":         death_year,
        "cause_of_death_qid": props.get("cause_of_death_qid"),
        "gnd_id":             props.get("gnd_id"),
        "lcnaf_id":           props.get("lcnaf_id"),
        "ocd_id":             props.get("ocd_id"),
        "nomisma_id":         props.get("nomisma_id"),
        "birth_pleiades":     birth_pleiades,
        "birth_place_qid":    birth_place_qid,
        "birth_place_label":  birth_place_label,
        "death_pleiades":     death_pleiades,
        "death_place_qid":    death_place_qid,
        "death_place_label":  death_place_label,
        "burial_pleiades":    burial_pleiades,
        "burial_place_qid":   burial_place_qid,
        "burial_place_label": burial_place_label,
    })

    for m in marriages:
        if m.get("spouse_qid"):
            try:
                session.run(WRITE_MARRIAGE_QUALIFIERS, {
                    "person_qid":     qid,
                    "spouse_qid":     m["spouse_qid"],
                    "start_year":     m["start_year"],
                    "end_year":       m["end_year"],
                    "series_ordinal": m["series_ordinal"],
                    "end_reason":     m["end_reason"],
                    "place_qid":      m["place_qid"],
                    "place_label":    m["place_label"],
                })
            except Exception as e:
                print(f"    WARN marriage write failed for {m['spouse_qid']}: {e}")

    for evt in conflicts:
        session.run(WRITE_EVENT_PARTICIPATION, {
            "person_qid":  qid,
            "event_qid":   evt["qid"],
            "event_label": evt["label"],
            "event_type":  "conflict",
            "prop_id":     "p607",
        })
    for evt in events:
        session.run(WRITE_EVENT_PARTICIPATION, {
            "person_qid":  qid,
            "event_qid":   evt["qid"],
            "event_label": evt["label"],
            "event_type":  "significant_event",
            "prop_id":     "p793_p1344",
        })

    for bl in backlinks:
        try:
            session.run(WRITE_BACKLINK_CANDIDATE, {
                "person_qid":      qid,
                "item_qid":        bl["item_qid"],
                "item_label":      bl["item_label"],
                "entity_cipher":   generate_entity_cipher(bl["item_qid"], "STUB", "wd"),
                "item_type_qid":   bl["item_type_qid"],
                "item_type_label": bl["item_type_label"],
                "pred_pid":        bl["pred_pid"],
                "edge_type":       bl["edge_type"],
                "direction":       bl["direction"],
                "qualifier":       bl["qualifier"],
                "sfa_queue":       bl["sfa_queue"],
            })
        except Exception as e:
            print(f"    WARN backlink write failed for {bl['item_qid']}: {e}")

    print(f"  Written")


class BiographicAgent:
    """
    Biographic Subject Agent — harvests biographical context for Person nodes.
    """

    def __init__(self, session=None):
        self._session = session
        self._driver = None
        self._decision_model = None

    def connect(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
        self._session = self._session or self._driver.session()
        return self._session

    def load_decision_model(self):
        from .decision_loader import load_decision_model
        session = self.connect()
        self._decision_model = load_decision_model(session)
        return self._decision_model

    def harvest(self, qid: str, dprr_id: str = "?", dry_run: bool = False):
        session = self.connect()
        if self._decision_model is None:
            try:
                self.load_decision_model()
            except Exception:
                self._decision_model = False
        harvest_person(
            qid, dprr_id, session,
            dry_run=dry_run,
            decision_model=self._decision_model or None,
        )

    def close(self):
        if self._session:
            self._session.close()
            self._session = None
        if self._driver:
            self._driver.close()
            self._driver = None
