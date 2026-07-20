#!/usr/bin/env python3
"""Domain apply — registry-gated Neo writes from schema proposal + pack library.

WD values are candidates (provisional). Does not invent NodeType / RelType names.
Refuses unless NEO4J_URI hosts 7fe339d2.

Usage (repo root):
  python chrystal_2/agents/domain/apply_schema.py --qid Q17167 --domain-id roman_republic --dry-run
  python chrystal_2/agents/domain/apply_schema.py --qid Q17167 --domain-id roman_republic --write
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from neo4j import GraphDatabase

from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

PACKS = ROOT / "JSON" / "wikidata" / "packs"
SAFE_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SAFE_REL = re.compile(r"^[A-Z][A-Z0-9_]*$")
FACET_KEYS = [
    "ARCHAEOLOGICAL",
    "ARTISTIC",
    "BIOGRAPHIC",
    "COMMUNICATION",
    "CULTURAL",
    "DEMOGRAPHIC",
    "DIPLOMATIC",
    "ECONOMIC",
    "ENVIRONMENTAL",
    "GEOGRAPHIC",
    "INTELLECTUAL",
    "LINGUISTIC",
    "MILITARY",
    "POLITICAL",
    "RELIGIOUS",
    "SCIENTIFIC",
    "SOCIAL",
    "TECHNOLOGICAL",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _wd_year(time_obj: Any) -> int | None:
    if not isinstance(time_obj, dict):
        return None
    raw = time_obj.get("time") or ""
    if not raw or raw[0] not in "+-":
        return None
    sign = -1 if raw[0] == "-" else 1
    try:
        return sign * int(raw[1:5])
    except ValueError:
        return None


def claim_values(claims: dict[str, list], pid: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for stmt in claims.get(pid) or []:
        m = stmt.get("mainsnak") or {}
        out.append(
            {
                "value": m.get("value"),
                "value_label": m.get("value_label"),
                "datatype": m.get("datatype"),
                "rank": stmt.get("rank"),
                "statement_id": stmt.get("statement_id"),
            }
        )
    return out


def to_neo_property(value: Any) -> Any:
    """Neo4j properties: primitives or arrays of primitives only."""
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        if not value:
            return []
        if all(isinstance(x, (bool, int, float, str)) for x in value):
            return value
        # list of maps / mixed → JSON string
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, dict):
        # Prefer compact qid/label pairs as parallel fields handled by caller;
        # default: JSON string
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def flatten_domain_property(prop: str, value: Any) -> dict[str, Any]:
    """Expand structured values into Neo-safe property dict."""
    if value is None:
        return {}
    # Single item {qid,label}
    if isinstance(value, dict) and set(value.keys()) <= {
        "qid",
        "label",
        "value",
        "time",
        "year",
        "amount",
        "unit",
        "latitude",
        "longitude",
        "precision",
        "globe",
    }:
        out: dict[str, Any] = {}
        if "qid" in value:
            # Lean: display label on prop + qid companion. No duplicate *_label.
            out[prop] = value.get("label") or value.get("qid")
            out[f"{prop}_qid"] = value.get("qid")
            return out
        if "year" in value and value["year"] is not None and prop in {
            "start_year",
            "end_year",
        }:
            return {prop: value["year"]}
        if "latitude" in value and "longitude" in value:
            return {
                f"{prop}_lat": value.get("latitude"),
                f"{prop}_lon": value.get("longitude"),
            }
        if "amount" in value:
            return {prop: to_neo_property(value)}
        if "value" in value and len(value) <= 2:
            return {prop: to_neo_property(value.get("value"))}
        return {prop: to_neo_property(value)}

    if isinstance(value, list) and value and all(
        isinstance(x, dict) and "qid" in x for x in value
    ):
        return {
            prop: [x.get("label") or x.get("qid") for x in value],
            f"{prop}_qids": [x.get("qid") for x in value],
        }

    return {prop: to_neo_property(value)}


def normalize_prop_value(values: list[dict[str, Any]], prop_name: str) -> Any:
    """Map WD snaks to a Neo-friendly property value."""
    if prop_name in {"start_year", "end_year"}:
        for v in values:
            y = _wd_year(v.get("value"))
            if y is not None:
                return y
        return None

    items: list[Any] = []
    for v in values:
        dt = v.get("datatype")
        val = v.get("value")
        lab = v.get("value_label")
        if dt == "wikibase-item" or (
            isinstance(val, str) and val.startswith("Q") and lab is not None
        ):
            items.append({"qid": val, "label": lab})
        elif dt == "time":
            items.append({"time": val, "year": _wd_year(val), "label": lab})
        elif dt == "quantity" and isinstance(val, dict):
            items.append(
                {
                    "amount": val.get("amount"),
                    "unit": val.get("unit"),
                    "label": lab,
                }
            )
        elif dt == "globecoordinate" and isinstance(val, dict):
            items.append(
                {
                    "latitude": val.get("latitude"),
                    "longitude": val.get("longitude"),
                    "precision": val.get("precision"),
                    "globe": val.get("globe"),
                }
            )
        elif dt == "monolingualtext" and isinstance(val, dict):
            items.append(val.get("text") or val)
        else:
            items.append(val if lab is None else {"value": val, "label": lab})

    if not items:
        return None
    if len(items) == 1:
        return items[0]
    return items


class ApplyPlan:
    def __init__(self) -> None:
        self.actions: list[dict[str, Any]] = []
        self.skipped: list[dict[str, Any]] = []

    def add(self, action: str, **kwargs: Any) -> None:
        self.actions.append({"action": action, **kwargs})

    def skip(self, reason: str, **kwargs: Any) -> None:
        self.skipped.append({"reason": reason, **kwargs})


def load_registry(session) -> tuple[set[str], set[str]]:
    nodes = {
        r["n"]
        for r in session.run("MATCH (n:SYS_NodeType) RETURN n.name AS n")
        if r["n"]
    }
    rels = {
        r["t"]
        for r in session.run(
            """
            MATCH (r:SYS_RelationshipType)
            RETURN coalesce(r.rel_type, r.name) AS t
            """
        )
        if r["t"]
    }
    return nodes, rels


def build_plan(
    proposal: dict[str, Any],
    pack: dict[str, Any],
    domain_id: str,
    node_types: set[str],
    rel_types: set[str],
) -> ApplyPlan:
    plan = ApplyPlan()
    claims = (pack.get("statements") or {}).get("claims") or {}
    plan.add(
        "ensure_subject_domain",
        domain_id=domain_id,
        seed=pack.get("seed"),
    )

    for row in proposal.get("proposals") or []:
        pid = row.get("pid")
        decision = row.get("decision")
        values = claim_values(claims, pid)

        if decision in {"ignore", "defer"}:
            plan.skip(decision, pid=pid, property_label=row.get("property_label"))
            continue

        if decision == "subject_domain_property":
            prop = row.get("property") or f"wd_{pid.lower()}"
            if not SAFE_IDENT.match(prop):
                plan.skip("unsafe_property_name", pid=pid, property=prop)
                continue
            val = normalize_prop_value(values, prop)
            plan.add(
                "set_domain_property",
                pid=pid,
                property=prop,
                value=val,
                property_label=row.get("property_label"),
            )
            continue

        if decision == "identity_tether":
            fed = row.get("federation")
            prop = row.get("property") or f"wd_{pid.lower()}"
            if not SAFE_IDENT.match(prop):
                prop = f"wd_{pid.lower()}"
            val = normalize_prop_value(values, prop)
            plan.add(
                "set_identity_tether",
                pid=pid,
                property=prop,
                value=val,
                federation=fed,
                property_label=row.get("property_label"),
            )
            continue

        if decision in {"first_class_node", "first_class_relationship"}:
            node_label = row.get("node_label")
            rel_type = row.get("relationship_type")
            # Prefer typed node+rel; allow rel-only DIFFERENT_FROM with generic target
            if rel_type and not SAFE_REL.match(str(rel_type)):
                plan.skip("unsafe_rel_type", pid=pid, relationship_type=rel_type)
                continue
            if rel_type and rel_type not in rel_types:
                plan.skip("rel_type_not_in_registry", pid=pid, relationship_type=rel_type)
                continue

            item_vals = [
                v
                for v in values
                if isinstance(v.get("value"), str) and str(v["value"]).startswith("Q")
            ]
            if not item_vals:
                plan.skip("no_item_values", pid=pid, decision=decision)
                continue

            if node_label:
                if not SAFE_IDENT.match(str(node_label)):
                    plan.skip("unsafe_node_label", pid=pid, node_label=node_label)
                    continue
                if node_label not in node_types:
                    plan.skip(
                        "node_label_not_in_registry",
                        pid=pid,
                        node_label=node_label,
                    )
                    continue
            elif decision == "first_class_relationship" and rel_type:
                # Rel without node label: mint provisional Entity using seed qid key
                # Prefer skip unless rel is DIFFERENT_FROM — use no label mint as :Entity? not in registry
                plan.skip(
                    "rel_without_node_label",
                    pid=pid,
                    relationship_type=rel_type,
                    note="Need node_label in registry to mint endpoint",
                )
                continue
            else:
                plan.skip("missing_node_label", pid=pid, decision=decision)
                continue

            for v in item_vals:
                plan.add(
                    "merge_node_and_rel",
                    pid=pid,
                    property_label=row.get("property_label"),
                    node_label=node_label,
                    relationship_type=rel_type,
                    qid=v.get("value"),
                    label=v.get("value_label") or v.get("value"),
                    rank=v.get("rank"),
                )
            continue

        plan.skip("unknown_decision", pid=pid, decision=decision)

    plan.add("ensure_sfa_slots", domain_id=domain_id, count=18)
    plan.add(
        "stamp_apply_meta",
        domain_id=domain_id,
        applied_at=_now(),
        proposal_path=None,
    )
    return plan


def execute_plan(
    session,
    plan: ApplyPlan,
    domain_id: str,
    seed: dict[str, Any],
    proposal_rel: str,
    pack_rel: str,
    write: bool,
) -> dict[str, Any]:
    applied = 0
    if not write:
        return {
            "mode": "dry_run",
            "actions": len(plan.actions),
            "skipped": len(plan.skipped),
            "plan": plan.actions,
            "skipped_detail": plan.skipped,
        }

    for step in plan.actions:
        action = step["action"]
        if action == "ensure_subject_domain":
            session.run(
                """
                MERGE (sd:SubjectDomain {domain_id: $domain_id})
                SET sd.seed_qid = $seed_qid,
                    sd.label = coalesce(sd.label, $label),
                    sd.description = coalesce(sd.description, $description),
                    sd.kind = coalesce(sd.kind, 'historical_pack'),
                    sd.instance = 'chrystal_2',
                    sd.reference_json = $pack_rel,
                    sd.schema_proposal_json = $proposal_rel,
                    sd.status = 'schema_applied_provisional'
                """,
                domain_id=domain_id,
                seed_qid=seed.get("qid"),
                label=seed.get("label"),
                description=seed.get("description"),
                pack_rel=pack_rel,
                proposal_rel=proposal_rel,
            )
            applied += 1

        elif action in {"set_domain_property", "set_identity_tether"}:
            prop = step["property"]
            fields = flatten_domain_property(prop, step.get("value"))
            if not fields:
                continue
            # Validate property keys
            for k in fields:
                if not SAFE_IDENT.match(k):
                    raise SystemExit(f"unsafe property key: {k}")
            session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                SET sd += $fields,
                    sd.wd_apply_provisional = true
                """,
                domain_id=domain_id,
                fields=fields,
            )
            if action == "set_identity_tether" and step.get("federation"):
                session.run(
                    """
                    MATCH (sd:SubjectDomain {domain_id: $domain_id})
                    SET sd.identity_federations =
                      CASE
                        WHEN sd.identity_federations IS NULL THEN [$fed]
                        WHEN $fed IN sd.identity_federations THEN sd.identity_federations
                        ELSE sd.identity_federations + $fed
                      END
                    """,
                    domain_id=domain_id,
                    fed=step["federation"],
                )
            applied += 1

        elif action == "merge_node_and_rel":
            node_label = step["node_label"]
            rel_type = step["relationship_type"]
            qid = step["qid"]
            label = step["label"]
            # MERGE node
            session.run(
                f"""
                MERGE (t:{node_label} {{qid: $qid}})
                SET t.label = coalesce(t.label, $label),
                    t.instance = 'chrystal_2',
                    t.seed_source = 'wikidata_pack_apply',
                    t.provisional = true,
                    t.authority_status = 'wd_candidate'
                """,
                qid=qid,
                label=label,
            )
            if rel_type:
                session.run(
                    f"""
                    MATCH (sd:SubjectDomain {{domain_id: $domain_id}})
                    MATCH (t:{node_label} {{qid: $qid}})
                    MERGE (sd)-[r:{rel_type}]->(t)
                    SET r.pid = $pid,
                        r.provisional = true,
                        r.authority_source = 'wikidata',
                        r.applied_at = $applied_at
                    """,
                    domain_id=domain_id,
                    qid=qid,
                    pid=step.get("pid"),
                    applied_at=_now(),
                )
            applied += 1

        elif action == "ensure_sfa_slots":
            for facet_key in FACET_KEYS:
                slot_id = f"sfa_{domain_id}_{facet_key.lower()}"
                session.run(
                    """
                    MATCH (sd:SubjectDomain {domain_id: $domain_id})
                    MATCH (f:Facet {key: $facet_key})
                    MERGE (slot:SFASlot {slot_id: $slot_id})
                    SET slot.domain_id = $domain_id,
                        slot.facet_key = $facet_key,
                        slot.label = $label,
                        slot.status = 'inert',
                        slot.agent_type = 'SFA',
                        slot.instance = 'chrystal_2'
                    MERGE (sd)-[:CONTAINS]->(slot)
                    MERGE (slot)-[:HAS_FACET]->(f)
                    """,
                    domain_id=domain_id,
                    facet_key=facet_key,
                    slot_id=slot_id,
                    label=f"SFA {facet_key} ({domain_id})",
                )
            applied += 1

        elif action == "stamp_apply_meta":
            session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                SET sd.schema_applied_at = $applied_at,
                    sd.schema_apply_agent = 'DOMAIN',
                    sd.schema_proposal_json = $proposal_rel,
                    sd.reference_json = $pack_rel,
                    sd.status = 'schema_applied_provisional'
                WITH sd
                OPTIONAL MATCH (ys:Year {year: sd.start_year})
                FOREACH (_ IN CASE WHEN ys IS NULL THEN [] ELSE [1] END |
                  MERGE (sd)-[:STARTS_IN_YEAR]->(ys)
                )
                WITH sd
                OPTIONAL MATCH (ye:Year {year: sd.end_year})
                FOREACH (_ IN CASE WHEN ye IS NULL THEN [] ELSE [1] END |
                  MERGE (sd)-[:ENDS_IN_YEAR]->(ye)
                )
                """,
                domain_id=domain_id,
                applied_at=_now(),
                proposal_rel=proposal_rel,
                pack_rel=pack_rel,
            )
            applied += 1

    return {
        "mode": "write",
        "applied_steps": applied,
        "skipped": len(plan.skipped),
        "skipped_detail": plan.skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Domain apply schema proposal")
    parser.add_argument("--qid", required=True)
    parser.add_argument("--domain-id", required=True)
    parser.add_argument("--proposal", type=Path, default=None)
    parser.add_argument("--pack", type=Path, default=None)
    parser.add_argument("--model", default="claude-sonnet-4-5")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true", help="Print code plan only")
    g.add_argument("--write", action="store_true", help="Write code plan (no LLM review)")
    g.add_argument(
        "--review-only",
        action="store_true",
        help="Code plan → Domain LLM review → print revised plan (no write)",
    )
    g.add_argument(
        "--review-write",
        action="store_true",
        help="Code plan → Domain LLM review → write revised plan",
    )
    args = parser.parse_args()

    if "7fe339d2" not in (NEO4J_URI or ""):
        print(f"Refusing: NEO4J_URI is not chrystal_2 (7fe339d2): {NEO4J_URI}")
        return 2

    qid = args.qid.strip().upper()
    domain_id = args.domain_id.strip()
    proposal_path = args.proposal or (PACKS / f"{qid}_schema_proposal.json")
    pack_path = args.pack or (PACKS / f"{qid}_pack_library.json")
    if not proposal_path.exists() or not pack_path.exists():
        print(f"Missing proposal or pack: {proposal_path} / {pack_path}")
        return 2

    proposal = _load_json(proposal_path)
    pack = _load_json(pack_path)
    proposal_rel = str(proposal_path.relative_to(ROOT)).replace("\\", "/")
    pack_rel = str(pack_path.relative_to(ROOT)).replace("\\", "/")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=db) as session:
            node_types, rel_types = load_registry(session)
            plan = build_plan(proposal, pack, domain_id, node_types, rel_types)
            for step in plan.actions:
                if step["action"] == "stamp_apply_meta":
                    step["proposal_path"] = proposal_rel

            review = None
            if args.review_only or args.review_write:
                # Same-directory import (Windows folder casing breaks package imports)
                import importlib.util

                review_path = Path(__file__).resolve().parent / "review_apply_plan.py"
                spec = importlib.util.spec_from_file_location(
                    "domain_review_apply_plan", review_path
                )
                if spec is None or spec.loader is None:
                    raise SystemExit(f"Cannot load {review_path}")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                review = mod.review_apply_plan(
                    domain_id=domain_id,
                    actions=plan.actions,
                    skipped=plan.skipped,
                    model=args.model,
                )
                plan.actions, plan.skipped = mod.apply_review_drops(
                    plan.actions, plan.skipped, review.get("drop_pids") or []
                )

            by_action: dict[str, int] = {}
            for a in plan.actions:
                by_action[a["action"]] = by_action.get(a["action"], 0) + 1
            skip_reasons: dict[str, int] = {}
            for s in plan.skipped:
                skip_reasons[s["reason"]] = skip_reasons.get(s["reason"], 0) + 1

            if args.dry_run or args.review_only:
                print(
                    json.dumps(
                        {
                            "mode": "review_only" if args.review_only else "dry_run",
                            "domain_id": domain_id,
                            "review": review,
                            "action_counts": by_action,
                            "skip_reason_counts": skip_reasons,
                            "actions": plan.actions,
                            "skipped": plan.skipped,
                        },
                        indent=2,
                        ensure_ascii=False,
                        default=str,
                    )
                )
                return 0

            # --write or --review-write
            result = execute_plan(
                session,
                plan,
                domain_id,
                pack.get("seed") or {},
                proposal_rel,
                pack_rel,
                write=True,
            )
            smoke = session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                OPTIONAL MATCH (sd)-[r]->(t)
                WHERE type(r) <> 'CONTAINS'
                OPTIONAL MATCH (sd)-[:CONTAINS]->(s:SFASlot)
                RETURN sd.status AS status,
                       sd.start_year AS start_year,
                       sd.end_year AS end_year,
                       count(DISTINCT r) AS outbound_rels,
                       count(DISTINCT s) AS slots
                """,
                domain_id=domain_id,
            ).single()
            print(
                json.dumps(
                    {
                        **result,
                        "review": review,
                        "action_counts": by_action,
                        "skip_reason_counts": skip_reasons,
                        "smoke": dict(smoke) if smoke else None,
                    },
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )
            )
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
