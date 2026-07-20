#!/usr/bin/env python3
"""LEGACY / transitional — prefer Domain bootstrap pipeline.

New packs: `python chrystal_2/agents/domain/pipeline.py bootstrap ...`
(This script remains for RR re-runs and debugging; do not extend with new maps.)

Librarian — place SubjectDomain in biblio universe via lcsh_fast_lcc card.

Writes (registry-gated):
  (:SubjectDomain)-[:HAS_LCSH_AUTHORITY]->(:LCSH_Heading)
  (:SubjectDomain)-[:HAS_FAST_AUTHORITY]->(:FAST_Heading)   # soft facets OK
  (:SubjectDomain)-[:ALIGNED_WITH_LCC]->(:LCC_Class)        # soft correlation

Refuses unless NEO4J_URI hosts 7fe339d2.

Usage (repo root):
  python chrystal_2/agents/librarian/place_domain.py --domain-id roman_republic --dry-run
  python chrystal_2/agents/librarian/place_domain.py --domain-id roman_republic --write
  python chrystal_2/agents/librarian/place_domain.py --domain-id roman_republic --write --enrich-fast-lcc
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

from neo4j import GraphDatabase

from federation_tools import (  # type: ignore
    derive_fast_facets_from_lcsh_heading,
    lcc_lookup_class,
    loc_fetch_heading,
)
from scripts.config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME

FED_CARD_PATH = ROOT / "Chrystal_2" / "federations" / "lcsh_fast_lcc.json"
if not FED_CARD_PATH.exists():
    FED_CARD_PATH = ROOT / "chrystal_2" / "federations" / "lcsh_fast_lcc.json"

PACKS = ROOT / "JSON" / "wikidata" / "packs"
LCC_CSV = ROOT / "CSV" / "lcc_roman_republic.csv"
FEDERATION_ID = "lcsh_fast_lcc"
INSTANCE_MARKER = "7fe339d2"

REL_LCSH = "HAS_LCSH_AUTHORITY"
REL_FAST = "HAS_FAST_AUTHORITY"
REL_LCC = "ALIGNED_WITH_LCC"
NODE_LCSH = "LCSH_Heading"
NODE_FAST = "FAST_Heading"
NODE_LCC = "LCC_Class"

SH_RE = re.compile(r"^sh\d{6,}", re.I)
N_RE = re.compile(r"^n\d{6,}", re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_federation_card(source_id: str = FEDERATION_ID) -> dict[str, Any]:
    if source_id != FEDERATION_ID:
        raise SystemExit(f"Unsupported federation for this CLI: {source_id}")
    if not FED_CARD_PATH.exists():
        raise SystemExit(f"Missing FederationCard: {FED_CARD_PATH}")
    card = json.loads(FED_CARD_PATH.read_text(encoding="utf-8"))
    if card.get("source_id") != source_id:
        raise SystemExit(f"Card source_id mismatch: {card.get('source_id')}")
    return card


def assert_chrystal_2() -> None:
    if INSTANCE_MARKER not in (NEO4J_URI or ""):
        raise SystemExit(
            f"Refusing: NEO4J_URI is not chrystal_2 ({INSTANCE_MARKER}): {NEO4J_URI}"
        )


def load_registry_aboutness(session) -> tuple[set[str], set[str]]:
    nodes = {
        r["name"]
        for r in session.run("MATCH (n:SYS_NodeType) RETURN n.name AS name")
        if r["name"]
    }
    rels = {
        r["name"]
        for r in session.run("MATCH (r:SYS_RelationshipType) RETURN r.name AS name")
        if r["name"]
    }
    return nodes, rels


def get_subject_domain(session, domain_id: str) -> dict[str, Any] | None:
    row = session.run(
        """
        MATCH (sd:SubjectDomain {domain_id: $domain_id})
        OPTIONAL MATCH (sd)-[:HAS_LCSH_AUTHORITY]->(h:LCSH_Heading)
        OPTIONAL MATCH (sd)-[:HAS_FAST_AUTHORITY]->(f:FAST_Heading)
        OPTIONAL MATCH (sd)-[:ALIGNED_WITH_LCC]->(l:LCC_Class)
        RETURN sd.domain_id AS domain_id,
               sd.label AS label,
               sd.seed_qid AS seed_qid,
               sd.wd_p244 AS wd_p244,
               sd.biblio_lcsh_id AS biblio_lcsh_id,
               sd.biblio_heading AS biblio_heading,
               sd.identity_federations AS identity_federations,
               sd.status AS status,
               collect(DISTINCT {
                 lcsh_id: h.lcsh_id,
                 label: coalesce(h.label, h.heading),
                 uri: h.uri
               }) AS existing_lcsh,
               collect(DISTINCT {
                 fast_id: f.fast_id,
                 label: coalesce(f.label, f.heading)
               }) AS existing_fast,
               collect(DISTINCT {
                 class_number: coalesce(l.class_number, l.code),
                 label: l.label
               }) AS existing_lcc
        """,
        domain_id=domain_id,
    ).single()
    if not row:
        return None
    d = dict(row)

    def _clean(rows: list, key: str) -> list[dict]:
        out = []
        for x in rows or []:
            if x and x.get(key):
                out.append(x)
        return out

    d["existing_lcsh"] = _clean(d.get("existing_lcsh") or [], "lcsh_id")
    d["existing_fast"] = _clean(d.get("existing_fast") or [], "fast_id")
    d["existing_lcc"] = _clean(d.get("existing_lcc") or [], "class_number")
    return d


def pack_p244(seed_qid: str | None) -> str | None:
    if not seed_qid:
        return None
    path = PACKS / f"{seed_qid}_pack_library.json"
    if not path.exists():
        return None
    pack = json.loads(path.read_text(encoding="utf-8"))
    for row in pack.get("external_ids") or []:
        if row.get("pid") == "P244" and row.get("value"):
            return str(row["value"]).strip()
    claims = ((pack.get("statements") or {}).get("claims") or {}).get("P244") or []
    for stmt in claims:
        m = stmt.get("mainsnak") or {}
        val = m.get("value")
        if val:
            return str(val).strip()
    return None


def classify_loc_id(raw: str) -> dict[str, Any]:
    lid = (raw or "").strip()
    if SH_RE.match(lid):
        return {"kind": "lcsh", "lcsh_id": lid.lower(), "raw": lid}
    if N_RE.match(lid):
        return {
            "kind": "lcnaf",
            "raw": lid,
            "note": "LCNAF name authority — identity helix, not Librarian aboutness",
        }
    return {"kind": "unknown", "raw": lid, "note": "Unrecognized LoC authorities id shape"}


def build_plan(
    domain: dict[str, Any],
    card: dict[str, Any],
    node_types: set[str],
    rel_types: set[str],
    *,
    enrich_fast_lcc: bool,
) -> dict[str, Any]:
    plan: dict[str, Any] = {
        "domain_id": domain["domain_id"],
        "federation": card.get("source_id"),
        "actions": [],
        "skipped": [],
        "resolved_lcsh": None,
        "resolved_fast": [],
        "resolved_lcc": [],
    }

    def need_node(label: str) -> bool:
        if label not in node_types:
            plan["skipped"].append(
                {"reason": "node_label_not_in_registry", "node_label": label}
            )
            return False
        return True

    def need_rel(rel: str) -> bool:
        if rel not in rel_types:
            plan["skipped"].append(
                {"reason": "rel_type_not_in_registry", "relationship_type": rel}
            )
            return False
        return True

    # ── LCSH ──────────────────────────────────────────────────────────────
    heading_label: str | None = domain.get("biblio_heading")
    lcsh_id: str | None = None
    existing_lcsh_ids = {x["lcsh_id"] for x in domain.get("existing_lcsh") or []}

    if existing_lcsh_ids:
        lcsh_id = sorted(existing_lcsh_ids)[0]
        heading_label = heading_label or next(
            (x.get("label") for x in domain["existing_lcsh"] if x["lcsh_id"] == lcsh_id),
            None,
        )
        plan["skipped"].append(
            {
                "reason": "already_tethered_lcsh",
                "lcsh_id": lcsh_id,
                "existing": domain.get("existing_lcsh"),
            }
        )
    else:
        if not (need_node(NODE_LCSH) and need_rel(REL_LCSH)):
            return plan
        candidate = domain.get("wd_p244") or pack_p244(domain.get("seed_qid"))
        if not candidate:
            plan["skipped"].append({"reason": "no_p244_candidate"})
            return plan
        classified = classify_loc_id(str(candidate))
        if classified["kind"] != "lcsh":
            plan["skipped"].append({"reason": "not_lcsh_aboutness", **classified})
            return plan
        lcsh_id = classified["lcsh_id"]
        heading = loc_fetch_heading(lcsh_id)
        if not heading or not heading.get("label"):
            plan["skipped"].append({"reason": "loc_resolve_failed", "lcsh_id": lcsh_id})
            return plan
        plan["resolved_lcsh"] = heading
        heading_label = heading["label"]
        plan["actions"].append(
            {
                "action": "merge_lcsh_heading",
                "node_label": NODE_LCSH,
                "lcsh_id": heading["lcsh_id"],
                "label": heading["label"],
                "uri": heading.get("uri"),
                "source": FEDERATION_ID,
            }
        )
        plan["actions"].append(
            {
                "action": "tether_domain_lcsh",
                "domain_id": domain["domain_id"],
                "relationship_type": REL_LCSH,
                "lcsh_id": heading["lcsh_id"],
                "role": "pack_aboutness",
                "authority_source": FEDERATION_ID,
            }
        )
        plan["actions"].append(
            {
                "action": "stamp_biblio_meta",
                "domain_id": domain["domain_id"],
                "placed_at": _now(),
                "lcsh_id": heading["lcsh_id"],
                "heading": heading["label"],
            }
        )

    if not enrich_fast_lcc:
        return plan

    if not heading_label:
        # try resolve from biblio_lcsh_id / wd_p244
        lid = domain.get("biblio_lcsh_id") or lcsh_id or domain.get("wd_p244")
        if lid and classify_loc_id(str(lid))["kind"] == "lcsh":
            resolved = loc_fetch_heading(str(lid).lower())
            heading_label = (resolved or {}).get("label")
            plan["resolved_lcsh"] = resolved

    if not heading_label:
        plan["skipped"].append({"reason": "no_heading_for_enrichment"})
        return plan

    # ── FAST soft facets ──────────────────────────────────────────────────
    if need_node(NODE_FAST) and need_rel(REL_FAST):
        existing_fast = {x["fast_id"] for x in domain.get("existing_fast") or []}
        facets = derive_fast_facets_from_lcsh_heading(heading_label)
        plan["resolved_fast"] = facets
        if not facets:
            plan["skipped"].append(
                {
                    "reason": "fast_no_suggest_match",
                    "heading": heading_label,
                    "note": (
                        "Chronological LCSH often has no 1:1 FAST; "
                        "suggest returned no scored facet"
                    ),
                }
            )
        for facet in facets:
            fid = facet["fast_id"]
            if fid in existing_fast:
                plan["skipped"].append(
                    {"reason": "already_tethered_fast", "fast_id": fid}
                )
                continue
            plan["actions"].append(
                {
                    "action": "merge_fast_heading",
                    "node_label": NODE_FAST,
                    "fast_id": fid,
                    "label": facet["label"],
                    "uri": facet.get("uri"),
                    "source": FEDERATION_ID,
                    "soft": facet.get("soft", True),
                    "facet_role": facet.get("facet_role"),
                    "match_score": facet.get("match_score"),
                    "chrono_facet": facet.get("chrono_facet"),
                }
            )
            plan["actions"].append(
                {
                    "action": "tether_domain_fast",
                    "domain_id": domain["domain_id"],
                    "relationship_type": REL_FAST,
                    "fast_id": fid,
                    "label": facet.get("label"),
                    "role": f"soft_facet_{facet.get('facet_role')}",
                    "authority_source": FEDERATION_ID,
                    "soft": True,
                    "match_score": facet.get("match_score"),
                    "chrono_facet": facet.get("chrono_facet"),
                    "derived_from_lcsh": lcsh_id or domain.get("biblio_lcsh_id"),
                }
            )

    # ── LCC soft ─────────────────────────────────────────────────────────
    if need_node(NODE_LCC) and need_rel(REL_LCC):
        existing_lcc = {x["class_number"] for x in domain.get("existing_lcc") or []}
        classes = lcc_lookup_class(
            domain_id=domain["domain_id"],
            csv_path=LCC_CSV,
            heading=heading_label,
        )
        plan["resolved_lcc"] = classes
        if not classes:
            plan["skipped"].append(
                {
                    "reason": "lcc_no_soft_match",
                    "csv": str(LCC_CSV).replace("\\", "/"),
                }
            )
        for row in classes:
            code = row["class_number"]
            if code in existing_lcc:
                plan["skipped"].append(
                    {"reason": "already_aligned_lcc", "class_number": code}
                )
                continue
            plan["actions"].append(
                {
                    "action": "merge_lcc_class",
                    "node_label": NODE_LCC,
                    "class_number": code,
                    "label": row.get("label"),
                    "uri": row.get("uri"),
                    "source": FEDERATION_ID,
                    "soft": True,
                }
            )
            plan["actions"].append(
                {
                    "action": "align_domain_lcc",
                    "domain_id": domain["domain_id"],
                    "relationship_type": REL_LCC,
                    "class_number": code,
                    "role": row.get("role") or "soft_catalog_correlate",
                    "authority_source": FEDERATION_ID,
                    "soft": True,
                    "derived_from_lcsh": lcsh_id or domain.get("biblio_lcsh_id"),
                }
            )

    if any(
        a["action"].startswith(("merge_fast", "tether_domain_fast", "merge_lcc", "align_domain"))
        for a in plan["actions"]
    ):
        plan["actions"].append(
            {
                "action": "stamp_enrich_meta",
                "domain_id": domain["domain_id"],
                "enriched_at": _now(),
            }
        )

    return plan


def execute_plan(session, plan: dict[str, Any], write: bool) -> dict[str, Any]:
    if not write:
        return {
            "mode": "dry_run",
            "actions": plan["actions"],
            "skipped": plan["skipped"],
            "resolved_lcsh": plan.get("resolved_lcsh"),
            "resolved_fast": plan.get("resolved_fast"),
            "resolved_lcc": plan.get("resolved_lcc"),
        }

    applied = 0
    for step in plan["actions"]:
        action = step["action"]
        if action == "merge_lcsh_heading":
            session.run(
                """
                MERGE (h:LCSH_Heading {lcsh_id: $lcsh_id})
                SET h.label = $label,
                    h.heading = $label,
                    h.uri = $uri,
                    h.source = $source,
                    h.updated_at = datetime()
                """,
                lcsh_id=step["lcsh_id"],
                label=step["label"],
                uri=step.get("uri"),
                source=step.get("source"),
            )
            applied += 1
        elif action == "tether_domain_lcsh":
            session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                MATCH (h:LCSH_Heading {lcsh_id: $lcsh_id})
                MERGE (sd)-[r:HAS_LCSH_AUTHORITY]->(h)
                SET r.role = $role,
                    r.authority_source = $authority_source,
                    r.placed_by = 'librarian',
                    r.placed_at = datetime()
                """,
                domain_id=step["domain_id"],
                lcsh_id=step["lcsh_id"],
                role=step.get("role"),
                authority_source=step.get("authority_source"),
            )
            applied += 1
        elif action == "stamp_biblio_meta":
            session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                SET sd.biblio_lcsh_id = $lcsh_id,
                    sd.biblio_heading = $heading,
                    sd.biblio_placed_at = $placed_at,
                    sd.biblio_federation = $fed,
                    sd.biblio_status = 'placed'
                """,
                domain_id=step["domain_id"],
                lcsh_id=step["lcsh_id"],
                heading=step["heading"],
                placed_at=step["placed_at"],
                fed=FEDERATION_ID,
            )
            applied += 1
        elif action == "merge_fast_heading":
            session.run(
                """
                MERGE (f:FAST_Heading {fast_id: $fast_id})
                SET f.label = $label,
                    f.heading = $label,
                    f.uri = $uri,
                    f.source = $source,
                    f.soft = $soft,
                    f.updated_at = datetime()
                """,
                fast_id=step["fast_id"],
                label=step["label"],
                uri=step.get("uri"),
                source=step.get("source"),
                soft=bool(step.get("soft")),
            )
            applied += 1
        elif action == "tether_domain_fast":
            session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                MATCH (f:FAST_Heading {fast_id: $fast_id})
                MERGE (sd)-[r:HAS_FAST_AUTHORITY]->(f)
                SET r.role = $role,
                    r.authority_source = $authority_source,
                    r.soft = true,
                    r.match_score = $match_score,
                    r.chrono_facet = $chrono_facet,
                    r.derived_from_lcsh = $derived_from_lcsh,
                    r.placed_by = 'librarian',
                    r.placed_at = datetime()
                """,
                domain_id=step["domain_id"],
                fast_id=step["fast_id"],
                role=step.get("role"),
                authority_source=step.get("authority_source"),
                match_score=step.get("match_score"),
                chrono_facet=step.get("chrono_facet"),
                derived_from_lcsh=step.get("derived_from_lcsh"),
            )
            applied += 1
        elif action == "merge_lcc_class":
            session.run(
                """
                MERGE (l:LCC_Class {class_number: $class_number})
                SET l.code = $class_number,
                    l.label = $label,
                    l.uri = $uri,
                    l.source = $source,
                    l.soft = true,
                    l.updated_at = datetime()
                """,
                class_number=step["class_number"],
                label=step.get("label"),
                uri=step.get("uri"),
                source=step.get("source"),
            )
            applied += 1
        elif action == "align_domain_lcc":
            session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                MATCH (l:LCC_Class {class_number: $class_number})
                MERGE (sd)-[r:ALIGNED_WITH_LCC]->(l)
                SET r.role = $role,
                    r.authority_source = $authority_source,
                    r.soft = true,
                    r.derived_from_lcsh = $derived_from_lcsh,
                    r.placed_by = 'librarian',
                    r.placed_at = datetime()
                """,
                domain_id=step["domain_id"],
                class_number=step["class_number"],
                role=step.get("role"),
                authority_source=step.get("authority_source"),
                derived_from_lcsh=step.get("derived_from_lcsh"),
            )
            applied += 1
        elif action == "stamp_enrich_meta":
            session.run(
                """
                MATCH (sd:SubjectDomain {domain_id: $domain_id})
                SET sd.biblio_enriched_at = $enriched_at,
                    sd.biblio_status = 'placed_enriched'
                """,
                domain_id=step["domain_id"],
                enriched_at=step["enriched_at"],
            )
            applied += 1
        else:
            raise SystemExit(f"unknown action: {action}")

    return {
        "mode": "write",
        "applied": applied,
        "actions": plan["actions"],
        "skipped": plan["skipped"],
        "resolved_lcsh": plan.get("resolved_lcsh"),
        "resolved_fast": plan.get("resolved_fast"),
        "resolved_lcc": plan.get("resolved_lcc"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Librarian: place / enrich SubjectDomain via LCSH/FAST/LCC"
    )
    parser.add_argument("--domain-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--enrich-fast-lcc",
        action="store_true",
        help="Also soft-derive FAST facets + LCC CSV correlations",
    )
    parser.add_argument(
        "--review-only",
        action="store_true",
        help="LLM-review enrich plan; print drops; do not write",
    )
    parser.add_argument(
        "--review-write",
        action="store_true",
        help="LLM-review enrich plan then write kept actions",
    )
    args = parser.parse_args(argv)

    modes = sum(bool(x) for x in (args.dry_run, args.write, args.review_only, args.review_write))
    if modes > 1:
        print("Use only one of --dry-run / --write / --review-only / --review-write")
        return 2
    write = bool(args.write or args.review_write)
    do_review = bool(args.review_only or args.review_write)

    assert_chrystal_2()
    card = load_federation_card()

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    db = NEO4J_DATABASE or "neo4j"
    try:
        with driver.session(database=db) as session:
            node_types, rel_types = load_registry_aboutness(session)
            domain = get_subject_domain(session, args.domain_id.strip())
            if not domain:
                print(f"SubjectDomain not found: {args.domain_id}")
                return 2

            # Review targets enrich; ensure flag is on
            enrich = bool(args.enrich_fast_lcc or do_review)
            plan = build_plan(
                domain,
                card,
                node_types,
                rel_types,
                enrich_fast_lcc=enrich,
            )

            review = None
            if do_review:
                from review_enrich_plan import apply_review_drops, review_enrich_plan

                review = review_enrich_plan(
                    domain_id=domain["domain_id"],
                    heading=domain.get("biblio_heading"),
                    actions=plan["actions"],
                    skipped=plan["skipped"],
                )
                plan["actions"], plan["skipped"] = apply_review_drops(
                    plan["actions"],
                    plan["skipped"],
                    review.get("drop_indices") or [],
                )

            if args.review_only:
                result = {
                    "mode": "review_only",
                    "actions": plan["actions"],
                    "skipped": plan["skipped"],
                    "resolved_lcsh": plan.get("resolved_lcsh"),
                    "resolved_fast": plan.get("resolved_fast"),
                    "resolved_lcc": plan.get("resolved_lcc"),
                    "review": review,
                }
            else:
                result = execute_plan(session, plan, write=write)
                if review is not None:
                    result["review"] = review

            print(
                json.dumps(
                    {
                        "agent": "LIBRARIAN",
                        "card": card.get("source_id"),
                        "enrich_fast_lcc": enrich,
                        "domain": {
                            "domain_id": domain["domain_id"],
                            "label": domain.get("label"),
                            "wd_p244": domain.get("wd_p244"),
                            "biblio_heading": domain.get("biblio_heading"),
                            "existing_lcsh": domain.get("existing_lcsh"),
                            "existing_fast": domain.get("existing_fast"),
                            "existing_lcc": domain.get("existing_lcc"),
                        },
                        **result,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            if write and result.get("applied"):
                verify = get_subject_domain(session, args.domain_id.strip())
                print(
                    "\nVERIFY:",
                    json.dumps(
                        {
                            "lcsh": (verify or {}).get("existing_lcsh"),
                            "fast": (verify or {}).get("existing_fast"),
                            "lcc": (verify or {}).get("existing_lcc"),
                        },
                        indent=2,
                        ensure_ascii=False,
                    ),
                )
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
