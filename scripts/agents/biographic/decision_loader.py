"""
Biographic Agent — Decision model loader

Loads harvest decision rules from the graph at startup.
Replaces hardcoded BACKLINK_PREDICATE_MAP, EVENT_KEYS, and
snap_id priority logic when SYS_Policy nodes exist.

Usage:
    from scripts.agents.biographic.decision_loader import load_decision_model
    dm = load_decision_model(session)
    mapping = dm.route_backlink(pred_pid="P112", item_type_label="Roman legion")
"""

import json
import re


def classify_item_type(item_type_label: str | None) -> str:
    """Return a coarse item_type_class from a raw P31 label."""
    if not item_type_label:
        return "*"
    low = item_type_label.lower()
    for pattern, cls in _TYPE_CLASS_RULES:
        if re.search(pattern, low):
            return cls
    return "*"


_TYPE_CLASS_RULES = [
    (r"legion|military unit|regiment",        "legion"),
    (r"city|town|settlement|municipium|"
     r"colonia|civitas|oppidum|polis",         "settlement"),
    (r"battle|conflict|siege|campaign|war",   "conflict"),
    (r"ship|vessel|warship|frigate",          "vessel"),
    (r"painting|artwork|artistic theme|"
     r"sculpture|relief",                     "artwork"),
    (r"human|person",                         "person"),
]


class BioDecisionModel:
    """
    Holds decision tables loaded from SYS_Policy and
    SYS_WikidataProperty nodes. All routing logic is
    expressed as table lookups, not if-elif chains.
    """

    def __init__(self,
                 backlink_table: list[dict],
                 place_table: list[dict],
                 snap_table: list[dict],
                 wikidata_props: dict[str, dict]):
        self._backlink = backlink_table
        self._place    = place_table
        self._snap     = snap_table
        self._props    = wikidata_props

    def route_backlink(self, pred_pid: str,
                       item_type_label: str | None) -> dict:
        """Return routing decision for a backlink item."""
        item_cls = classify_item_type(item_type_label)
        for row in self._backlink:
            if row["pred_pid"] != pred_pid:
                continue
            tc = row["item_type_class"]
            if tc == "*" or tc == item_cls:
                return {
                    "edge_type":  row["edge_type"],
                    "direction":  row["direction"],
                    "qualifier":  row.get("qualifier"),
                    "sfa_queue":  row["sfa_queue"],
                }
        return {
            "edge_type": "RELATED_TO",
            "direction": "inbound",
            "qualifier": None,
            "sfa_queue": "Biographic",
        }

    def fetch_method(self, pid: str) -> str:
        return self._props.get(pid, {}).get("fetch_method", "truthy")

    def canonical_key(self, pid: str) -> str | None:
        return self._props.get(pid, {}).get("canonical_key")

    def sfa_primary(self, pid: str) -> str | None:
        return self._props.get(pid, {}).get("sfa_primary")

    def props_by_method(self, method: str) -> list[str]:
        return [pid for pid, rec in self._props.items()
                if rec.get("fetch_method") == method]

    def place_resolution_action(self, resolved: bool,
                                sfa_context: str) -> str:
        for row in self._place:
            if row["place_resolved"] != resolved:
                continue
            ctx = row["sfa_context"]
            if ctx == "*" or ctx == sfa_context:
                return row["action"]
        return "write_stub"

    def derive_snap_id(self, period: str,
                       dprr_id: str | None,
                       lgpn_id: str | None,
                       trismeg_id: str | None,
                       pir_id: str | None) -> str | None:
        presence = {
            "has_dprr":    bool(dprr_id),
            "has_lgpn":    bool(lgpn_id),
            "has_trismeg": bool(trismeg_id),
            "has_pir":     bool(pir_id),
        }
        values = {"dprr": dprr_id, "lgpn": lgpn_id,
                  "trismeg": trismeg_id, "pir": pir_id}
        for row in self._snap:
            if row["period"] != "*" and row["period"] != period:
                continue
            match = True
            for key in ("has_dprr", "has_lgpn", "has_trismeg", "has_pir"):
                if key in row and row[key] != presence[key]:
                    match = False
                    break
            if not match:
                continue
            prefix = row.get("snap_id_prefix")
            if prefix is None:
                return None
            val = values.get(prefix)
            return f"{prefix}:{val}" if val else None
        return None


def load_decision_model(session) -> BioDecisionModel:
    """
    Query the graph for all decision tables and property registry.
    Falls back to empty tables if nodes not yet migrated.
    """

    def load_policy(name: str) -> list[dict]:
        result = session.run(
            "MATCH (p:SYS_Policy {name: $name}) "
            "RETURN p.decision_table AS dt",
            name=name
        ).single()
        if not result or not result["dt"]:
            return []
        try:
            return sorted(json.loads(result["dt"]), key=lambda r: r.get("row", 99))
        except json.JSONDecodeError:
            return []

    def load_wikidata_props() -> dict[str, dict]:
        rows = session.run(
            "MATCH (p:SYS_WikidataProperty) "
            "RETURN p.pid AS pid, p.label AS label, "
            "       p.fetch_method AS fetch_method, "
            "       p.canonical_key AS canonical_key, "
            "       p.sfa_primary AS sfa_primary, "
            "       p.value_type AS value_type"
        )
        return {r["pid"]: dict(r) for r in rows}

    backlink = load_policy("BacklinkRouting")
    place    = load_policy("PlaceResolution")
    snap     = load_policy("SnapIdAuthority")
    props    = load_wikidata_props()
    return BioDecisionModel(backlink, place, snap, props)
