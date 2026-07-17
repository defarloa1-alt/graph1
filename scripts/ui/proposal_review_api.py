#!/usr/bin/env python3
"""
Lightweight API for human review of DI / SFA proposals.

Serves the enriched proposals JSON and persists approve / reject / hold decisions
back to disk (with backup). Used by the Chrystallum Viewer "Review Queue" tab.

Usage:
  python scripts/ui/proposal_review_api.py
  python scripts/ui/proposal_review_api.py --port 8765 --seed Q17167
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "agents" / "domain_initiator"))

from proposal_backbone import normalize_corpus_work  # noqa: E402
PROPOSALS_DIR = ROOT / "output" / "di_proposals"
BACKUP_DIR = PROPOSALS_DIR / ".review_backups"

from config_loader import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME  # noqa: E402

VALID_STATUSES = frozenset({"proposed", "approved", "rejected", "held"})
VALID_CLAIM_STATUSES = frozenset({"proposed", "validated", "rejected", "held"})

BIO_KEYWORDS = (
    "person",
    "prosopograph",
    "family",
    "gens",
    "biograph",
    "senator",
    "magistrate",
    "tribune",
    "consul",
    "praetor",
    "cursus",
    "honorum",
    "elite",
    "populist",
    "kinship",
    "marriage",
    "spouse",
    "genealog",
    "nomen",
    "cognomen",
    "patrician",
    "plebeian",
    "dprr",
    "career",
    "office holder",
    "office-holder",
    "prosop",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _doc_path(seed: str, *, enriched: bool = True) -> Path:
    suffix = "_proposals_enriched.json" if enriched else "_proposals.json"
    return PROPOSALS_DIR / f"{seed.upper()}{suffix}"


def _load_document(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_document(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup = BACKUP_DIR / f"{path.stem}_{stamp}.json"
        shutil.copy2(path, backup)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)


def _normalize_status(raw: str | None) -> str:
    if not raw:
        return "proposed"
    value = raw.strip().lower()
    if value == "hold":
        return "held"
    return value if value in VALID_STATUSES else "proposed"


def bio_conflict_hint(proposal: dict[str, Any]) -> str | None:
    """Flag non-biographic proposals that touch person/prosopography territory."""
    facet = (proposal.get("source_facet") or "").lower()
    if facet == "biographic":
        return None
    text = f"{proposal.get('label', '')} {proposal.get('description', '')}".lower()
    weights = proposal.get("facet_weights") or {}
    bio_weight = float(weights.get("biographic") or 0)
    keyword_hit = any(word in text for word in BIO_KEYWORDS)
    if bio_weight >= 0.4 or keyword_hit:
        return (
            "Person / prosopography signal — Biographic SFA is primary owner for "
            "Person nodes, kinship, and career identity. Other facets should attach "
            "secondary claims, not duplicate bio scaffolding."
        )
    return None


def _resolved_path(seed: str) -> Path:
    return PROPOSALS_DIR / f"{seed.upper()}_proposals_resolved.json"


def _merge_resolution_from_file(doc: dict[str, Any], seed: str) -> dict[str, Any]:
    rpath = _resolved_path(seed)
    if not rpath.exists():
        return doc
    with open(rpath, encoding="utf-8") as f:
        rdoc = json.load(f)
    by_id = {
        p["subject_id"]: p.get("resolution")
        for p in rdoc.get("proposals", [])
        if p.get("subject_id") and p.get("resolution")
    }
    merged = dict(doc)
    proposals = []
    for p in doc.get("proposals", []):
        row = dict(p)
        sid = row.get("subject_id")
        if sid and sid in by_id:
            row["resolution"] = by_id[sid]
        proposals.append(row)
    merged["proposals"] = proposals
    if rdoc.get("resolution_pass"):
        merged["resolution_pass"] = rdoc["resolution_pass"]
    return merged


def _enrich_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    row = dict(proposal)
    row["status"] = _normalize_status(row.get("status"))
    row["bio_conflict_hint"] = bio_conflict_hint(row)
    works = row.get("supporting_works") or []
    if works:
        normalized_works = []
        for work in works:
            normalized = normalize_corpus_work(
                work if isinstance(work, dict) else {"work_id": str(work)}
            )
            if normalized.get("work_id"):
                normalized_works.append(normalized)
        row["supporting_works"] = normalized_works
    resolution = row.get("resolution") or {}
    if resolution:
        row["resolution_action"] = resolution.get("action")
        row["resolution_tier"] = resolution.get("tier")
        row["resolution_rationale"] = resolution.get("rationale")
        row["resolution_merge_target"] = resolution.get("merge_target")
        row["bio_primary_note"] = resolution.get("bio_primary_note")
    return row


def _resolution_stats(proposals: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for p in proposals:
        action = p.get("resolution_action") or (p.get("resolution") or {}).get("action")
        if action:
            counts[action] = counts.get(action, 0) + 1
    return counts


def _stats(proposals: list[dict[str, Any]]) -> dict[str, int]:
    counts = {s: 0 for s in VALID_STATUSES}
    bio_flags = 0
    for p in proposals:
        status = _normalize_status(p.get("status"))
        counts[status] = counts.get(status, 0) + 1
        if bio_conflict_hint(p):
            bio_flags += 1
    return {
        **counts,
        "total": len(proposals),
        "bio_conflict_flags": bio_flags,
    }


class ReviewUpdate(BaseModel):
    status: str = Field(..., description="approved | rejected | held | proposed")
    review_notes: str = ""


class ClaimReviewUpdate(BaseModel):
    status: str = Field(..., description="validated | rejected | held | proposed")
    review_notes: str = ""


def _neo4j_driver():
    from neo4j import GraphDatabase

    if not NEO4J_PASSWORD:
        raise HTTPException(status_code=503, detail="NEO4J_PASSWORD not configured")
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def _claim_stats(session: Any, source_agent: str | None = "sfa_biographic") -> dict[str, Any]:
    if source_agent and source_agent != "all":
        rows = session.run(
            """
            MATCH (cl:Claim {source_agent: $source_agent})
            RETURN cl.status AS status,
                   cl.promoted AS promoted,
                   cl.reconciliation_status AS reconciliation_status,
                   cl.fischer_status AS fischer_status,
                   count(*) AS n
            """,
            source_agent=source_agent,
        ).data()
    else:
        rows = session.run(
            """
            MATCH (cl:Claim)
            RETURN cl.status AS status,
                   cl.promoted AS promoted,
                   cl.reconciliation_status AS reconciliation_status,
                   cl.fischer_status AS fischer_status,
                   count(*) AS n
            """
        ).data()
    stats: dict[str, Any] = {
        "total": 0,
        "proposed": 0,
        "validated": 0,
        "rejected": 0,
        "held": 0,
        "promoted": 0,
        "reconciliation": {},
        "fischer": {},
    }
    for row in rows:
        n = row["n"]
        stats["total"] += n
        status = (row["status"] or "proposed").lower()
        if status in stats:
            stats[status] += n
        if row["promoted"]:
            stats["promoted"] += n
        rkey = row["reconciliation_status"] or "unreconciled"
        stats["reconciliation"][rkey] = stats["reconciliation"].get(rkey, 0) + n
        fkey = row["fischer_status"] or "unknown"
        stats["fischer"][fkey] = stats["fischer"].get(fkey, 0) + n
    return stats


def _json_value(raw: Any) -> Any:
    if raw is None:
        return None
    if isinstance(raw, (str, int, float, bool)):
        return raw
    if isinstance(raw, dict):
        return {str(k): _json_value(v) for k, v in raw.items()}
    if isinstance(raw, (list, tuple)):
        return [_json_value(v) for v in raw]
    if hasattr(raw, "iso_format"):
        return raw.iso_format()
    if hasattr(raw, "isoformat"):
        return raw.isoformat()
    return str(raw)


def _parse_authority_ids(raw: Any) -> dict[str, str]:
    if not raw:
        return {}
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except json.JSONDecodeError:
            return {}
    return {}


def _format_year(year: Any) -> str | None:
    if year is None:
        return None
    try:
        y = int(year)
    except (TypeError, ValueError):
        return str(year)
    if y < 0:
        return f"{abs(y)} BCE"
    if y == 0:
        return "0 CE"
    return f"{y} CE"


def _format_lifespan(
    birth: Any,
    death: Any,
    floruit_start: Any = None,
    floruit_end: Any = None,
) -> str | None:
    b = _format_year(birth)
    d = _format_year(death)
    if b and d:
        return f"{b} – {d}"
    if b:
        return f"born {b}"
    if d:
        return f"died {d}"
    fs = _format_year(floruit_start)
    fe = _format_year(floruit_end)
    if fs and fe:
        return f"fl. {fs} – {fe}"
    if fs:
        return f"fl. {fs}"
    return None


def _parse_event_date(raw: Any) -> str | None:
    if raw is None:
        return None
    text = str(raw)
    if text.startswith("-") and len(text) >= 5:
        try:
            year = int(text[1:5])
            return f"{year} BCE"
        except ValueError:
            pass
    if len(text) >= 4 and text[:4].isdigit():
        return f"{text[:4]} CE"
    return text


def _build_approval_context(
    row: dict[str, Any],
    *,
    person_qid: str | None,
    candidate_qid: str | None,
    pred_pid: str | None,
) -> dict[str, Any]:
    person_lifespan = _format_lifespan(
        row.get("person_birth_year"),
        row.get("person_death_year"),
        row.get("person_floruit_start"),
        row.get("person_floruit_end"),
    )
    target_when = _parse_event_date(row.get("target_start_date"))
    if not target_when:
        target_when = _format_lifespan(row.get("target_birth_year"), row.get("target_death_year"))

    rel_start = _format_year(
        row.get("claim_start_year") if row.get("claim_start_year") is not None else row.get("relation_start_year")
    )
    rel_end = _format_year(
        row.get("claim_end_year") if row.get("claim_end_year") is not None else row.get("relation_end_year")
    )
    point_year = _format_year(row.get("claim_point_year"))
    relationship_when: str | None = None
    if rel_start and rel_end:
        relationship_when = f"{rel_start} – {rel_end}"
    elif rel_start:
        relationship_when = f"from {rel_start}"
    elif rel_end:
        relationship_when = f"until {rel_end}"
    elif point_year:
        relationship_when = point_year

    date_gaps: list[str] = []
    geo_gaps: list[str] = []
    other_gaps: list[str] = []
    rel_type = (row.get("relationship_type") or "").upper()
    enrichment_status = row.get("enrichment_status") or "pending"

    if not person_lifespan:
        other_gaps.append("Person anchor has no birth/death/floruit dates")
    if rel_type in {"PARTICIPATED_IN", "FOUGHT_IN", "ORGANIZED", "FOUNDED"} and not target_when:
        date_gaps.append("Event/target has no start date")
    # Place geodata gate: battle/event claims need Event -> Place with lat/long (normally WD P625).
    if rel_type in {"PARTICIPATED_IN", "FOUGHT_IN", "ORGANIZED", "FOUNDED", "LOCATION_OF_EVENT"}:
        place_qid = row.get("location_place_qid")
        place_lat = row.get("location_place_lat")
        place_long = row.get("location_place_long")
        if not place_qid:
            geo_gaps.append(
                "Event has no LOCATION_OF_EVENT Place — enrich from Wikidata P276/P625 "
                "(scripts/system/ensure_event_place_geo.py)"
            )
        elif place_lat is None or place_long is None:
            geo_gaps.append(
                f"Place {place_qid} missing lat/long — enrich from Wikidata P625"
            )
    if row.get("predicate_status") == "tbd":
        other_gaps.append(
            "Predicate status TBD — further research required before Validate"
        )
    # IGAR is optional interpretation for participation (FOUGHT_IN / P607).
    # Only warn when a claim_layer marks itself as interpretation and IGAR is missing.
    claim_layer = (row.get("claim_layer") or "atomic_participation").lower()
    if claim_layer in {"interpretation", "igar", "actor_decision"} and not row.get(
        "igar_complete"
    ):
        other_gaps.append(
            "Interpretation claim missing IGAR (Input → Goal → Action → Result)"
        )
    if rel_type in {
        "SPOUSE_OF",
        "POSITION_HELD",
        "HAD_ROLE",
        "RAISED_LEGION",
        "COMMISSIONED",
    } and not relationship_when:
        date_gaps.append("Relationship has no start/end dates (graph or Wikidata qualifiers)")
    if enrichment_status == "pending":
        other_gaps.append("Agent enrichment not run — run enrich_claims.py")
    elif enrichment_status == "partial":
        date_gaps.append("Wikidata statement found but no date qualifiers")
    elif enrichment_status == "missing":
        date_gaps.append("Wikidata statement not located for re-enrichment")

    reg_status = row.get("registry_status")
    if reg_status in (None, "unknown"):
        other_gaps.append("Relationship type not registry-validated — check SYS_RelationshipType / CSV")
    elif reg_status == "routing_only":
        other_gaps.append("Relationship type in BacklinkRouting but not implemented in CSV — Hold recommended")
    elif reg_status == "candidate":
        other_gaps.append("Relationship type is candidate in CSV — verify before promotion")
    elif reg_status == "unregistered":
        other_gaps.append("Relationship type not in relationship_types_registry_master.csv")

    rel_type = (row.get("relationship_type") or "").upper()
    if rel_type and not row.get("cidoc_crm_code"):
        try:
            from scripts.tools.cidoc_context import cidoc_for_relationship

            cidoc = cidoc_for_relationship(rel_type)
            if cidoc and cidoc.get("cidoc_crm_code"):
                row = {**row, "cidoc_crm_code": cidoc["cidoc_crm_code"]}
            elif rel_type:
                other_gaps.append(f"No CIDOC-CRM code mapped for relationship {rel_type}")
        except ImportError:
            pass

    recon = row.get("reconciliation_status")
    if recon in (None, "unreconciled"):
        other_gaps.append("Not yet reconciled against DPRR/canonical edges")

    scope_id = row.get("routed_subject_id") or row.get("scope_subject_id")
    if not scope_id:
        other_gaps.append("Not routed to SubjectConcept — run route_claims_to_sc.py")

    date_completeness = "not_applicable"
    if rel_type in {"PARTICIPATED_IN", "FOUGHT_IN", "ORGANIZED", "FOUNDED"}:
        date_completeness = "complete" if target_when else "missing"
    elif rel_type in {
        "SPOUSE_OF",
        "POSITION_HELD",
        "HAD_ROLE",
        "RAISED_LEGION",
        "COMMISSIONED",
    }:
        if relationship_when:
            date_completeness = "complete"
        elif enrichment_status == "not_applicable":
            date_completeness = "not_applicable"
        else:
            date_completeness = "missing"
    elif not date_gaps:
        date_completeness = "complete"

    warnings = date_gaps + geo_gaps + other_gaps

    location_when = None
    if row.get("location_place_qid") and row.get("location_place_lat") is not None:
        location_when = {
            "qid": row.get("location_place_qid"),
            "label": row.get("location_place_label"),
            "lat": row.get("location_place_lat"),
            "long": row.get("location_place_long"),
        }

    return {
        "person": {
            "qid": person_qid,
            "label": row.get("person_label"),
            "lifespan": person_lifespan,
        },
        "scope": {
            "subject_id": scope_id,
            "label": row.get("routed_subject_label") or row.get("scope_label"),
            "description": row.get("scope_description"),
            "routing_score": row.get("routing_score") or row.get("scope_routing_score"),
            "routing_method": row.get("routing_method") or row.get("scope_routing_method"),
        },
        "target": {
            "qid": candidate_qid,
            "label": row.get("target_label") or row.get("to_label") or row.get("from_label"),
            "entity_type": row.get("target_entity_type"),
            "event_type": row.get("target_event_type"),
            "when": target_when,
            "location": location_when,
        },
        "relationship": {
            "type": row.get("relationship_type"),
            "pred_pid": pred_pid,
            "when": relationship_when,
            "canonical_exists": bool(row.get("canonical_rel_type")),
            "canonical_rel_type": row.get("canonical_rel_type"),
            "canonical_source": row.get("canonical_source"),
        },
        "provenance": {
            "authority_source": row.get("authority_source"),
            "harvested_at": _json_value(row.get("harvested_at")),
            "direction_corrected": bool(row.get("direction_corrected")),
            "enrichment_status": enrichment_status,
            "enrichment_notes": row.get("enrichment_notes"),
            "enriched_at": _json_value(row.get("enriched_at")),
        },
        "igar": {
            "complete": bool(row.get("igar_complete")),
            "input": row.get("igar_input"),
            "goal": row.get("igar_goal"),
            "action": row.get("igar_action"),
            "result": row.get("igar_result"),
            "input_year": row.get("igar_input_year"),
            "action_year": row.get("igar_action_year"),
            "result_year": row.get("igar_result_year"),
        },
        "predicate_status": row.get("predicate_status") or "confirmed",
        "research_notes": row.get("research_notes") or "",
        "date_completeness": date_completeness,
        "date_gaps": date_gaps,
        "geo_gaps": geo_gaps,
        "other_gaps": other_gaps,
        "warnings": warnings,
    }


_CLAIM_RETURN_FIELDS = """
           cl.claim_id AS claim_id,
           cl.label AS label,
           cl.text AS text,
           cl.description AS description,
           cl.status AS status,
           cl.promoted AS promoted,
           cl.claim_type AS claim_type,
           cl.source_agent AS source_agent,
           cl.facet AS facet,
           cl.subject_qid AS subject_qid,
           cl.confidence AS confidence,
           cl.posterior_probability AS posterior_probability,
           cl.fischer_status AS fischer_status,
           cl.fallacies_detected AS fallacies_detected,
           cl.reconciliation_status AS reconciliation_status,
           cl.authority_source AS authority_source,
           cl.authority_ids AS authority_ids,
           cl.timestamp AS timestamp,
           cl.review_notes AS review_notes,
           cl.reviewed_at AS reviewed_at,
           cl.direction_corrected AS direction_corrected,
           cl.start_year AS claim_start_year,
           cl.end_year AS claim_end_year,
           null AS claim_point_year,
           cl.enrichment_status AS enrichment_status,
           cl.enrichment_notes AS enrichment_notes,
           cl.enriched_at AS enriched_at,
           cl.routed_subject_id AS routed_subject_id,
           cl.routed_subject_label AS routed_subject_label,
           cl.routing_score AS routing_score,
           cl.routing_method AS routing_method,
           cl.registry_status AS registry_status,
           cl.registry_message AS registry_message,
           cl.predicate_status AS predicate_status,
           cl.research_notes AS research_notes,
           cl.igar_complete AS igar_complete,
           cl.igar_input AS igar_input,
           cl.igar_goal AS igar_goal,
           cl.igar_action AS igar_action,
           cl.igar_result AS igar_result,
           cl.igar_input_year AS igar_input_year,
           cl.igar_action_year AS igar_action_year,
           cl.igar_result_year AS igar_result_year,
           cl.cidoc_crm_code AS cidoc_crm_code,
           cl.object_qid AS object_qid,
           cl.pred_pid AS claim_pred_pid,
           cl.wd_statement AS wd_statement,
           cl.claim_layer AS claim_layer,
           scope.subject_id AS scope_subject_id,
           scope.label AS scope_label,
           scope.description AS scope_description,
           scope_r.routing_score AS scope_routing_score,
           scope_r.routing_method AS scope_routing_method,
           pe.relationship_type AS relationship_type,
           src.qid AS from_qid,
           coalesce(src.label, src.qid) AS from_label,
           tgt.qid AS to_qid,
           coalesce(tgt.label, tgt.qid) AS to_label,
           ar.reasoning AS reasoning,
           bc.item_type_label AS item_type_label,
           bc.harvested_at AS harvested_at,
           bc.qualifier AS harvest_qualifier,
           bc.edge_type AS harvest_edge_type,
           anchor.label AS person_label,
           anchor.birth_year AS person_birth_year,
           anchor.death_year AS person_death_year,
           anchor.floruit_start AS person_floruit_start,
           anchor.floruit_end AS person_floruit_end,
           labels(endpoint)[0] AS target_entity_type,
           endpoint.label AS target_label,
           endpoint.start_date AS target_start_date,
           endpoint.event_type AS target_event_type,
           endpoint.birth_year AS target_birth_year,
           endpoint.death_year AS target_death_year,
           locPlace.qid AS location_place_qid,
           locPlace.label AS location_place_label,
           locPlace.lat AS location_place_lat,
           locPlace.long AS location_place_long,
           type(canon) AS canonical_rel_type,
           canon.start_year AS relation_start_year,
           canon.end_year AS relation_end_year,
           canon.source AS canonical_source
"""

_CLAIM_CONTEXT_MATCH = """
    OPTIONAL MATCH (cl)-[scope_r:IN_SCOPE]->(scope:SubjectConcept)
    OPTIONAL MATCH (anchor:Person {qid: cl.subject_qid})
    WITH cl, pe, src, tgt, ar, bc, anchor, scope, scope_r,
         CASE
           WHEN coalesce(src.qid, '') = cl.subject_qid THEN tgt
           WHEN coalesce(tgt.qid, '') = cl.subject_qid THEN src
           ELSE coalesce(tgt, src)
         END AS endpoint
    OPTIONAL MATCH (anchor)-[canon]-(endpoint)
    WHERE pe IS NULL
       OR type(canon) = pe.relationship_type
       OR (pe.relationship_type = 'CHILD_OF' AND type(canon) IN ['CHILD_OF', 'FATHER_OF', 'MOTHER_OF'])
       OR (pe.relationship_type IN ['PARENT_OF', 'FATHER_OF', 'MOTHER_OF']
           AND type(canon) IN ['CHILD_OF', 'FATHER_OF', 'MOTHER_OF', 'PARENT_OF'])
       OR (pe.relationship_type = 'SPOUSE_OF' AND type(canon) = 'SPOUSE_OF')
       OR (pe.relationship_type = 'PARTICIPATED_IN' AND type(canon) = 'PARTICIPATED_IN')
    WITH cl, pe, src, tgt, ar, bc, anchor, scope, scope_r, endpoint, head(collect(canon)) AS canon
    OPTIONAL MATCH (endpoint)-[:LOCATION_OF_EVENT]->(locCand:Place)
    WITH cl, pe, src, tgt, ar, bc, anchor, scope, scope_r, endpoint, canon,
         head([p IN collect(locCand) WHERE p.lat IS NOT NULL AND p.long IS NOT NULL | p]) AS locPlace
"""


def _serialize_claim(row: dict[str, Any]) -> dict[str, Any]:
    fallacies = row.get("fallacies_detected") or []
    if isinstance(fallacies, str):
        fallacies = [fallacies] if fallacies else []
    auth = _parse_authority_ids(row.get("authority_ids"))
    person_qid = auth.get("person_qid") or row.get("subject_qid")
    candidate_qid = auth.get("candidate_qid") or row.get("object_qid")
    if not candidate_qid:
        if row.get("from_qid") == person_qid:
            candidate_qid = row.get("to_qid")
        elif row.get("to_qid") == person_qid:
            candidate_qid = row.get("from_qid")
    pred_pid = row.get("claim_pred_pid") or auth.get("pred_pid")
    description = row.get("description") or row.get("reasoning") or ""
    approval_context = _build_approval_context(
        row,
        person_qid=person_qid,
        candidate_qid=candidate_qid,
        pred_pid=pred_pid,
    )
    return {
        "claim_id": row.get("claim_id"),
        "label": row.get("label") or row.get("text") or "",
        "text": row.get("text") or "",
        "description": description,
        "status": (row.get("status") or "proposed").lower(),
        "promoted": bool(row.get("promoted")),
        "claim_type": row.get("claim_type"),
        "source_agent": row.get("source_agent"),
        "facet": row.get("facet"),
        "subject_qid": row.get("subject_qid"),
        "person_qid": person_qid,
        "candidate_qid": candidate_qid,
        "pred_pid": pred_pid,
        "from_qid": row.get("from_qid"),
        "from_label": row.get("from_label"),
        "to_qid": row.get("to_qid"),
        "to_label": row.get("to_label"),
        "item_type_label": row.get("item_type_label"),
        "harvested_at": _json_value(row.get("harvested_at")),
        "harvest_qualifier": _json_value(row.get("harvest_qualifier")),
        "harvest_edge_type": row.get("harvest_edge_type"),
        "confidence": row.get("confidence"),
        "posterior_probability": row.get("posterior_probability"),
        "fischer_status": row.get("fischer_status"),
        "fallacies_detected": fallacies,
        "reconciliation_status": row.get("reconciliation_status"),
        "relationship_type": row.get("relationship_type"),
        "authority_source": row.get("authority_source"),
        "authority_ids": auth,
        "timestamp": row.get("timestamp"),
        "review_notes": row.get("review_notes") or "",
        "reviewed_at": row.get("reviewed_at"),
        "direction_corrected": bool(row.get("direction_corrected")),
        "person_label": row.get("person_label"),
        "person_birth_year": row.get("person_birth_year"),
        "person_death_year": row.get("person_death_year"),
        "person_lifespan": _format_lifespan(
            row.get("person_birth_year"),
            row.get("person_death_year"),
            row.get("person_floruit_start"),
            row.get("person_floruit_end"),
        ),
        "target_entity_type": row.get("target_entity_type"),
        "target_when": approval_context["target"]["when"],
        "target_event_type": row.get("target_event_type"),
        "relation_when": approval_context["relationship"]["when"],
        "canonical_rel_type": row.get("canonical_rel_type"),
        "canonical_source": row.get("canonical_source"),
        "enrichment_status": row.get("enrichment_status") or "pending",
        "enrichment_notes": row.get("enrichment_notes"),
        "enriched_at": _json_value(row.get("enriched_at")),
        "routed_subject_id": row.get("routed_subject_id") or row.get("scope_subject_id"),
        "routed_subject_label": row.get("routed_subject_label") or row.get("scope_label"),
        "routing_score": row.get("routing_score") or row.get("scope_routing_score"),
        "routing_method": row.get("routing_method") or row.get("scope_routing_method"),
        "registry_status": row.get("registry_status"),
        "registry_message": row.get("registry_message"),
        "predicate_status": row.get("predicate_status") or "confirmed",
        "research_notes": row.get("research_notes") or "",
        "igar": approval_context.get("igar"),
        "igar_complete": bool(row.get("igar_complete")),
        "cidoc_crm_code": row.get("cidoc_crm_code"),
        "object_qid": row.get("object_qid") or candidate_qid,
        "wd_statement": row.get("wd_statement"),
        "claim_layer": row.get("claim_layer") or "atomic_participation",
        "scope_description": row.get("scope_description"),
        "date_completeness": approval_context["date_completeness"],
        "approval_context": approval_context,
    }


def create_app(*, seed: str = "Q17167") -> FastAPI:
    app = FastAPI(title="Chrystallum Proposal Review API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/review/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "seed": seed.upper()}

    @app.get("/api/review/document")
    def get_document(seed_qid: str | None = None) -> dict[str, Any]:
        qid = (seed_qid or seed).upper()
        path = _doc_path(qid)
        doc = _merge_resolution_from_file(_load_document(path), qid)
        proposals = [_enrich_proposal(p) for p in doc.get("proposals", [])]
        return {
            "seed_qid": doc.get("seed_qid", qid),
            "seed_label": doc.get("seed_label", ""),
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "resolved_path": str(_resolved_path(qid).relative_to(ROOT)).replace("\\", "/")
            if _resolved_path(qid).exists()
            else None,
            "generated": doc.get("generated"),
            "enriched_at": doc.get("enriched_at"),
            "resolution_pass": doc.get("resolution_pass"),
            "facets_trained": doc.get("facets_trained", []),
            "facets_missing": doc.get("facets_missing", []),
            "stats": {**_stats(proposals), "resolution": _resolution_stats(proposals)},
            "proposals": proposals,
        }

    @app.patch("/api/review/proposals/{subject_id}")
    def update_proposal(subject_id: str, body: ReviewUpdate, seed_qid: str | None = None) -> dict[str, Any]:
        qid = (seed_qid or seed).upper()
        path = _doc_path(qid)
        doc = _load_document(path)
        status = _normalize_status(body.status)
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")

        updated: dict[str, Any] | None = None
        for proposal in doc.get("proposals", []):
            if proposal.get("subject_id") == subject_id:
                proposal["status"] = status
                proposal["review_notes"] = body.review_notes.strip()
                proposal["reviewed_at"] = _utc_now_iso()
                updated = _enrich_proposal(proposal)
                break

        if updated is None:
            raise HTTPException(status_code=404, detail=f"Proposal not found: {subject_id}")

        doc["last_review_save"] = _utc_now_iso()
        _save_document(path, doc)

        plain_path = _doc_path(qid, enriched=False)
        if plain_path.exists():
            plain_doc = _load_document(plain_path)
            for proposal in plain_doc.get("proposals", []):
                if proposal.get("subject_id") == subject_id:
                    proposal["status"] = status
                    proposal["review_notes"] = body.review_notes.strip()
                    proposal["reviewed_at"] = updated["reviewed_at"]
                    break
            plain_doc["last_review_save"] = doc["last_review_save"]
            _save_document(plain_path, plain_doc)

        return {"ok": True, "proposal": updated, "stats": _stats(doc.get("proposals", []))}

    @app.get("/api/review/claims")
    def list_claims(
        status: str | None = None,
        promoted: bool | None = None,
        reconciliation: str | None = None,
        source_agent: str | None = "sfa_biographic",
        limit: int = 500,
        offset: int = 0,
    ) -> dict[str, Any]:
        limit = max(1, min(limit, 2000))
        offset = max(0, offset)
        where: list[str] = []
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        agent = (source_agent or "sfa_biographic").strip()
        if agent and agent != "all":
            where.append("cl.source_agent = $source_agent")
            params["source_agent"] = agent
        if status:
            where.append("toLower(cl.status) = $status")
            params["status"] = status.strip().lower()
        if promoted is not None:
            where.append("cl.promoted = $promoted")
            params["promoted"] = promoted
        if reconciliation:
            if reconciliation == "unreconciled":
                where.append("cl.reconciliation_status IS NULL")
            else:
                where.append("cl.reconciliation_status = $reconciliation")
                params["reconciliation"] = reconciliation
        where_clause = " AND ".join(where) if where else "true"

        driver = _neo4j_driver()
        try:
            with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
                stats = _claim_stats(session, source_agent=agent)
                rows = session.run(
                    f"""
                    MATCH (cl:Claim)
                    WHERE {where_clause}
                    OPTIONAL MATCH (cl)-[:ASSERTS_EDGE]->(pe:ProposedEdge)
                    OPTIONAL MATCH (pe)-[:FROM]->(src)
                    OPTIONAL MATCH (pe)-[:TO]->(tgt)
                    OPTIONAL MATCH (cl)-[:HAS_ANALYSIS_RUN]->(ar:AnalysisRun)
                    OPTIONAL MATCH (cand)-[bc:BIO_CANDIDATE_REL {{claim_id: cl.claim_id}}]->(pers:Person)
                    {_CLAIM_CONTEXT_MATCH}
                    ORDER BY cl.timestamp DESC
                    SKIP $offset
                    LIMIT $limit
                    RETURN
                    {_CLAIM_RETURN_FIELDS}
                    """,
                    params,
                ).data()
                claims = [_serialize_claim(dict(r)) for r in rows]
                return {
                    "source": "neo4j",
                    "source_agent": agent,
                    "stats": stats,
                    "limit": limit,
                    "offset": offset,
                    "count": len(claims),
                    "claims": claims,
                }
        finally:
            driver.close()

    @app.patch("/api/review/claims/{claim_id}")
    def update_claim(claim_id: str, body: ClaimReviewUpdate) -> dict[str, Any]:
        status = body.status.strip().lower()
        if status == "hold":
            status = "held"
        if status not in VALID_CLAIM_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status: {body.status}")

        driver = _neo4j_driver()
        try:
            with driver.session(database=NEO4J_DATABASE or "neo4j") as session:
                row = session.run(
                    f"""
                    MATCH (cl:Claim {{claim_id: $claim_id}})
                    SET cl.status = $status,
                        cl.review_notes = $review_notes,
                        cl.reviewed_at = $reviewed_at
                    WITH cl
                    OPTIONAL MATCH (cl)-[:ASSERTS_EDGE]->(pe:ProposedEdge)
                    OPTIONAL MATCH (pe)-[:FROM]->(src)
                    OPTIONAL MATCH (pe)-[:TO]->(tgt)
                    OPTIONAL MATCH (cl)-[:HAS_ANALYSIS_RUN]->(ar:AnalysisRun)
                    OPTIONAL MATCH (cand)-[bc:BIO_CANDIDATE_REL {{claim_id: cl.claim_id}}]->(pers:Person)
                    {_CLAIM_CONTEXT_MATCH}
                    RETURN
                    {_CLAIM_RETURN_FIELDS}
                    """,
                    {
                        "claim_id": claim_id,
                        "status": status,
                        "review_notes": body.review_notes.strip(),
                        "reviewed_at": _utc_now_iso(),
                    },
                ).single()
                if not row:
                    raise HTTPException(status_code=404, detail=f"Claim not found: {claim_id}")
                claim = _serialize_claim(dict(row))
                return {"ok": True, "claim": claim, "stats": _claim_stats(session)}
        finally:
            driver.close()

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Proposal review API for Chrystallum Viewer")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--seed", default="Q17167")
    args = parser.parse_args()

    import uvicorn

    app = create_app(seed=args.seed)
    print(f"Proposal Review API — seed {args.seed.upper()}")
    print(f"  Document: {_doc_path(args.seed)}")
    print(f"  Listening: http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
