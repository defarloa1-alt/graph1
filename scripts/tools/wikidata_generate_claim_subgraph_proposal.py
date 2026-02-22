#!/usr/bin/env python3
"""Generate a claim-rich subgraph proposal from Wikidata statements + backlinks.

Inputs:
- Direct statements export from `wikidata_fetch_all_statements.py`
- Backlink harvest report from `wikidata_backlink_harvest.py`
- Relationship registry (for canonical relationship type mapping)
- Wikidata property catalog (for property label/description)

Outputs:
- `<prefix>.json`: machine-readable proposal payload
- `<prefix>.md`: human-readable summary and sample claims
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import requests


WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1ClaimProposal/1.0 (local tooling)"
QID_RE = re.compile(r"Q\d+$", re.IGNORECASE)
PID_RE = re.compile(r"P\d+$", re.IGNORECASE)


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_qid(value: str) -> str:
    qid = (value or "").strip().upper()
    if not QID_RE.fullmatch(qid):
        raise ValueError(f"Invalid QID: {value}")
    return qid


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _safe_claim_id(prefix: str, source_id: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9_]+", "_", source_id or "")
    clean = re.sub(r"_+", "_", clean).strip("_")
    if not clean:
        clean = "claim"
    return f"{prefix}_{clean}"


def _load_registry_property_map(path: Path) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = defaultdict(list)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = (row.get("wikidata_property") or "").strip().upper()
            rel = (row.get("relationship_type") or "").strip()
            if PID_RE.fullmatch(pid) and rel:
                out[pid].append(rel)
    for pid in list(out.keys()):
        out[pid] = sorted(set(out[pid]))
    return dict(out)


def _load_property_catalog(path: Path) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    if not path.exists():
        return out

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            first = (row[0] or "").strip()
            pid = ""
            if PID_RE.fullmatch(first.upper()):
                pid = first.upper()
            elif "/entity/P" in first:
                tail = first.rsplit("/", 1)[-1].upper()
                if PID_RE.fullmatch(tail):
                    pid = tail
            if not pid:
                continue

            label = row[1].strip() if len(row) > 1 else ""
            description = row[2].strip() if len(row) > 2 else ""
            datatype = row[3].strip() if len(row) > 3 else ""
            out[pid] = {
                "label": label,
                "description": description,
                "datatype": datatype,
            }
    return out


def _fetch_qid_labels_descriptions(
    qids: List[str],
    timeout_s: int = 45,
    batch_size: int = 50,
) -> Dict[str, Dict[str, str]]:
    if not qids:
        return {}

    headers = {"User-Agent": USER_AGENT}
    out: Dict[str, Dict[str, str]] = {}
    unique_qids = sorted({q for q in qids if QID_RE.fullmatch(q)})
    for batch in _chunks(unique_qids, max(1, batch_size)):
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": "|".join(batch),
            "languages": "en",
            "props": "labels|descriptions",
        }
        resp = requests.get(WIKIDATA_API_URL, params=params, headers=headers, timeout=timeout_s)
        resp.raise_for_status()
        payload = resp.json()
        for qid, entity in (payload.get("entities") or {}).items():
            if not QID_RE.fullmatch(qid):
                continue
            label = ((entity.get("labels") or {}).get("en") or {}).get("value", "")
            description = ((entity.get("descriptions") or {}).get("en") or {}).get("value", "")
            out[qid] = {"label": label, "description": description}
    return out


def _collect_reference_properties(references: List[Dict[str, Any]]) -> List[str]:
    props: Set[str] = set()
    for ref in references or []:
        snaks = ref.get("snaks", {}) or {}
        for prop in snaks.keys():
            if PID_RE.fullmatch((prop or "").upper()):
                props.add(prop.upper())
    return sorted(props)


def _score_claim(
    *,
    source_mode: str,
    reference_count: int,
    qualifier_count: int,
    rank: str,
    backlink_hits: int = 0,
) -> float:
    base = 0.58 if source_mode == "direct" else 0.54
    score = base
    if reference_count > 0:
        score += 0.15
    if qualifier_count > 0:
        score += 0.10
    if rank == "preferred":
        score += 0.05
    elif rank == "deprecated":
        score -= 0.15
    if source_mode == "backlink" and backlink_hits >= 3:
        score += 0.05
    return max(0.05, min(0.99, round(score, 3)))


def _top_counter_items(counter: Counter[str], limit: int = 20) -> List[Dict[str, Any]]:
    return [{"key": k, "count": v} for k, v in counter.most_common(limit)]


def build_proposal(
    *,
    seed_qid: str,
    statements_payload: Dict[str, Any],
    backlink_report: Dict[str, Any],
    registry_map: Dict[str, List[str]],
    property_catalog: Dict[str, Dict[str, str]],
    fetch_labels: bool,
) -> Dict[str, Any]:
    seed_label = statements_payload.get("label", "") or seed_qid
    seed_description = statements_payload.get("description", "")
    claims = statements_payload.get("claims", {}) or {}
    accepted_backlinks = backlink_report.get("accepted", []) or []

    direct_rel_claims: List[Dict[str, Any]] = []
    direct_attr_claims: List[Dict[str, Any]] = []
    backlink_rel_claims: List[Dict[str, Any]] = []

    direct_pred_counter: Counter[str] = Counter()
    backlink_pred_counter: Counter[str] = Counter()
    canonical_rel_counter: Counter[str] = Counter()

    all_qids_for_labeling: Set[str] = {seed_qid}

    # Direct claims from seed statements.
    for pid, statement_list in claims.items():
        pid = (pid or "").strip().upper()
        if not PID_RE.fullmatch(pid):
            continue

        pred_meta = property_catalog.get(pid, {})
        pred_label = pred_meta.get("label") or pid
        canonical_rels = registry_map.get(pid, [])

        for stmt in statement_list or []:
            mainsnak = stmt.get("mainsnak", {}) or {}
            datatype = mainsnak.get("datatype", "")
            value_type = mainsnak.get("value_type", "")
            value = mainsnak.get("value")
            rank = (stmt.get("rank") or "").strip()
            qualifiers = stmt.get("qualifiers", {}) or {}
            qualifier_count = sum(len(v) for v in qualifiers.values())
            qualifier_properties = sorted((qualifiers or {}).keys())
            references = stmt.get("references", []) or []
            reference_count = len(references)
            reference_properties = _collect_reference_properties(references)
            statement_id = stmt.get("statement_id", "")

            if (
                value_type == "wikibase-entityid"
                and isinstance(value, str)
                and QID_RE.fullmatch(value)
            ):
                object_qid = value.upper()
                all_qids_for_labeling.add(object_qid)
                direct_pred_counter[pid] += 1
                for rel in canonical_rels:
                    canonical_rel_counter[rel] += 1

                direct_rel_claims.append(
                    {
                        "claim_id": _safe_claim_id(seed_qid, statement_id or f"{pid}_{object_qid}"),
                        "source_mode": "direct",
                        "source_system": "wikidata",
                        "subject_qid": seed_qid,
                        "subject_label": seed_label,
                        "predicate_pid": pid,
                        "predicate_label": pred_label,
                        "canonical_relationship_types": canonical_rels,
                        "object_qid": object_qid,
                        "object_label": "",
                        "rank": rank,
                        "statement_id": statement_id,
                        "qualifier_count": qualifier_count,
                        "qualifier_properties": qualifier_properties,
                        "reference_count": reference_count,
                        "reference_properties": reference_properties,
                        "confidence": _score_claim(
                            source_mode="direct",
                            reference_count=reference_count,
                            qualifier_count=qualifier_count,
                            rank=rank,
                        ),
                    }
                )
            else:
                direct_attr_claims.append(
                    {
                        "claim_id": _safe_claim_id(seed_qid, stmt.get("statement_id", pid)),
                        "source_mode": "direct",
                        "source_system": "wikidata",
                        "subject_qid": seed_qid,
                        "subject_label": seed_label,
                        "predicate_pid": pid,
                        "predicate_label": pred_label,
                        "datatype": datatype,
                        "value_type": value_type,
                        "value": value,
                        "rank": rank,
                        "statement_id": statement_id,
                        "qualifier_count": qualifier_count,
                        "qualifier_properties": qualifier_properties,
                        "reference_count": reference_count,
                        "reference_properties": reference_properties,
                        "confidence": _score_claim(
                            source_mode="direct",
                            reference_count=reference_count,
                            qualifier_count=qualifier_count,
                            rank=rank,
                        ),
                    }
                )

    # Backlink-derived relational claims.
    for src in accepted_backlinks:
        source_qid = (src.get("qid") or "").strip().upper()
        if not QID_RE.fullmatch(source_qid):
            continue
        source_label = src.get("label") or source_qid
        all_qids_for_labeling.add(source_qid)
        properties = [p for p in src.get("properties", []) if PID_RE.fullmatch((p or "").upper())]
        properties = sorted({p.upper() for p in properties})
        profile = src.get("statement_profile", {}) or {}
        reference_count = int(profile.get("with_references") or 0)
        qualifier_count = int(profile.get("with_qualifiers") or 0)
        backlink_hits = int(src.get("backlink_hits") or 0)
        p31_list = [q for q in src.get("p31", []) if QID_RE.fullmatch((q or "").upper())]

        for pid in properties:
            pred_meta = property_catalog.get(pid, {})
            pred_label = pred_meta.get("label") or pid
            canonical_rels = registry_map.get(pid, [])
            backlink_pred_counter[pid] += 1
            for rel in canonical_rels:
                canonical_rel_counter[rel] += 1

            backlink_rel_claims.append(
                {
                    "claim_id": _safe_claim_id(seed_qid, f"backlink_{source_qid}_{pid}"),
                    "source_mode": "backlink",
                    "source_system": "wikidata",
                    "subject_qid": source_qid,
                    "subject_label": source_label,
                    "predicate_pid": pid,
                    "predicate_label": pred_label,
                    "canonical_relationship_types": canonical_rels,
                    "object_qid": seed_qid,
                    "object_label": seed_label,
                    "rank": "derived",
                    "statement_id": "",
                    "qualifier_count": qualifier_count,
                    "qualifier_properties": [],
                    "reference_count": reference_count,
                    "reference_properties": [],
                    "backlink_hits": backlink_hits,
                    "source_p31": p31_list,
                    "confidence": _score_claim(
                        source_mode="backlink",
                        reference_count=reference_count,
                        qualifier_count=qualifier_count,
                        rank="normal",
                        backlink_hits=backlink_hits,
                    ),
                }
            )

    # Label enrichment pass for direct object targets and backlink source entities.
    qid_labels: Dict[str, Dict[str, str]] = {}
    if fetch_labels:
        qid_labels = _fetch_qid_labels_descriptions(sorted(all_qids_for_labeling))

    def _label_for(qid: str, fallback: str = "") -> str:
        if qid == seed_qid:
            return seed_label
        row = qid_labels.get(qid, {})
        return row.get("label") or fallback or qid

    def _desc_for(qid: str) -> str:
        return (qid_labels.get(qid, {}) or {}).get("description", "")

    for row in direct_rel_claims:
        row["object_label"] = _label_for(row["object_qid"], row.get("object_label", ""))
    for row in backlink_rel_claims:
        row["subject_label"] = _label_for(row["subject_qid"], row.get("subject_label", ""))

    # Node proposals (seed + all participating nodes).
    node_roles: Dict[str, Set[str]] = defaultdict(set)
    node_roles[seed_qid].add("seed")
    for row in direct_rel_claims:
        node_roles[row["subject_qid"]].add("direct_subject")
        node_roles[row["object_qid"]].add("direct_object")
    for row in backlink_rel_claims:
        node_roles[row["subject_qid"]].add("backlink_source")
        node_roles[row["object_qid"]].add("backlink_target")

    nodes: List[Dict[str, Any]] = []
    for qid, roles in sorted(node_roles.items()):
        nodes.append(
            {
                "qid": qid,
                "label": _label_for(qid, qid),
                "description": _desc_for(qid),
                "roles": sorted(roles),
            }
        )

    relationship_claims = direct_rel_claims + backlink_rel_claims
    relationship_claims_sorted = sorted(
        relationship_claims,
        key=lambda x: (-float(x.get("confidence", 0.0)), x.get("predicate_pid", ""), x.get("claim_id", "")),
    )
    attribute_claims_sorted = sorted(
        direct_attr_claims,
        key=lambda x: (-float(x.get("confidence", 0.0)), x.get("predicate_pid", ""), x.get("claim_id", "")),
    )

    backlink_counts = backlink_report.get("counts", {}) or {}
    backlink_gates = backlink_report.get("gates", {}) or {}

    proposal = {
        "generated_at": _now_utc(),
        "seed": {
            "qid": seed_qid,
            "label": seed_label,
            "description": seed_description,
        },
        "sources": {
            "direct_statement_count": int(statements_payload.get("statement_count") or 0),
            "direct_property_count": int(statements_payload.get("property_count") or 0),
            "backlink_counts": backlink_counts,
            "backlink_gates": backlink_gates,
        },
        "summary": {
            "node_count": len(nodes),
            "relationship_claim_count": len(relationship_claims_sorted),
            "direct_relationship_claim_count": len(direct_rel_claims),
            "backlink_relationship_claim_count": len(backlink_rel_claims),
            "attribute_claim_count": len(attribute_claims_sorted),
            "top_direct_predicates": _top_counter_items(direct_pred_counter, 20),
            "top_backlink_predicates": _top_counter_items(backlink_pred_counter, 20),
            "top_canonical_relationship_types": _top_counter_items(canonical_rel_counter, 25),
        },
        "nodes": nodes,
        "relationship_claim_proposals": relationship_claims_sorted,
        "attribute_claim_proposals": attribute_claims_sorted,
        "analysis_notes": [
            "Claims are proposals with confidence heuristics, not canonical facts.",
            "Backlink-derived claims preserve reverse-link context with source class metadata.",
            "Canonical relationship mapping is sourced from relationship_types_registry_master.csv.",
        ],
    }
    return proposal


def write_markdown(
    *,
    proposal: Dict[str, Any],
    output_path: Path,
    statements_path: Path,
    backlinks_path: Path,
) -> None:
    seed = proposal.get("seed", {})
    summary = proposal.get("summary", {})
    sources = proposal.get("sources", {})
    rel_claims = proposal.get("relationship_claim_proposals", []) or []
    attr_claims = proposal.get("attribute_claim_proposals", []) or []

    lines: List[str] = []
    lines.append(f"# Claim Subgraph Proposal: {seed.get('label', '')} ({seed.get('qid', '')})")
    lines.append("")
    lines.append("## Inputs")
    lines.append(f"- Statements: `{statements_path}`")
    lines.append(f"- Backlinks: `{backlinks_path}`")
    lines.append("")
    lines.append("## Proposal Summary")
    lines.append(f"- Nodes: **{summary.get('node_count', 0)}**")
    lines.append(f"- Relationship claims: **{summary.get('relationship_claim_count', 0)}**")
    lines.append(f"- Direct relationship claims: **{summary.get('direct_relationship_claim_count', 0)}**")
    lines.append(f"- Backlink relationship claims: **{summary.get('backlink_relationship_claim_count', 0)}**")
    lines.append(f"- Attribute claims: **{summary.get('attribute_claim_count', 0)}**")
    lines.append("")

    backlink_counts = (sources.get("backlink_counts") or {})
    backlink_gates = (sources.get("backlink_gates") or {})
    if backlink_counts or backlink_gates:
        lines.append("## Backlink Gate Snapshot")
        lines.append(
            f"- candidates considered: {backlink_counts.get('candidate_sources_considered', 0)}"
        )
        lines.append(f"- accepted: {backlink_counts.get('accepted', 0)}")
        lines.append(f"- rejected: {backlink_counts.get('rejected', 0)}")
        lines.append(f"- unresolved class rate: {backlink_gates.get('unresolved_class_rate', 0):.4f}")
        lines.append(f"- unsupported pair rate: {backlink_gates.get('unsupported_pair_rate', 0):.4f}")
        lines.append(f"- overall status: `{backlink_gates.get('overall_status', '')}`")
        lines.append("")

    lines.append("## Top Direct Predicates")
    for row in summary.get("top_direct_predicates", [])[:12]:
        lines.append(f"- `{row['key']}`: {row['count']}")
    lines.append("")

    lines.append("## Top Backlink Predicates")
    for row in summary.get("top_backlink_predicates", [])[:12]:
        lines.append(f"- `{row['key']}`: {row['count']}")
    lines.append("")

    lines.append("## Top Canonical Relationship Types")
    for row in summary.get("top_canonical_relationship_types", [])[:15]:
        lines.append(f"- `{row['key']}`: {row['count']}")
    lines.append("")

    lines.append("## Sample Relationship Claims")
    for row in rel_claims[:30]:
        lines.append(
            "- "
            f"`{row.get('subject_qid')}` ({row.get('subject_label')}) "
            f"-[`{row.get('predicate_pid')}` {row.get('predicate_label')}]→ "
            f"`{row.get('object_qid')}` ({row.get('object_label')}) "
            f"| mode={row.get('source_mode')} conf={row.get('confidence')}"
        )
    lines.append("")

    lines.append("## Sample Attribute Claims")
    for row in attr_claims[:20]:
        val = row.get("value")
        if isinstance(val, (dict, list)):
            val_text = json.dumps(val, ensure_ascii=False)[:120]
        else:
            val_text = str(val)[:120]
        lines.append(
            "- "
            f"`{row.get('subject_qid')}` ({row.get('subject_label')}) "
            f"-[`{row.get('predicate_pid')}` {row.get('predicate_label')}]→ "
            f"`{val_text}` | datatype={row.get('datatype')} conf={row.get('confidence')}"
        )
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-qid", required=True, help="Seed QID (example: Q17167).")
    parser.add_argument(
        "--statements-json",
        help="Path to statements JSON. Default: JSON/wikidata/statements/<QID>_statements_full.json",
    )
    parser.add_argument(
        "--backlink-report",
        help="Path to backlink harvest report JSON. Default: JSON/wikidata/backlinks/<QID>_backlink_harvest_report.json",
    )
    parser.add_argument(
        "--relationship-registry",
        default="Relationships/relationship_types_registry_master.csv",
        help="Relationship registry CSV path.",
    )
    parser.add_argument(
        "--property-catalog",
        default="CSV/wikiPvalues.csv",
        help="Wikidata property catalog CSV path.",
    )
    parser.add_argument(
        "--output-prefix",
        help="Output prefix path (without extension). Default: JSON/wikidata/proposals/<QID>_claim_subgraph_proposal",
    )
    parser.add_argument(
        "--no-fetch-labels",
        action="store_true",
        help="Disable label enrichment calls to Wikidata API.",
    )
    args = parser.parse_args()

    seed_qid = _normalize_qid(args.seed_qid)
    statements_path = (
        Path(args.statements_json)
        if args.statements_json
        else Path(f"JSON/wikidata/statements/{seed_qid}_statements_full.json")
    )
    backlink_path = (
        Path(args.backlink_report)
        if args.backlink_report
        else Path(f"JSON/wikidata/backlinks/{seed_qid}_backlink_harvest_report.json")
    )
    output_prefix = (
        Path(args.output_prefix)
        if args.output_prefix
        else Path(f"JSON/wikidata/proposals/{seed_qid}_claim_subgraph_proposal")
    )

    if not statements_path.exists():
        raise FileNotFoundError(statements_path)
    if not backlink_path.exists():
        raise FileNotFoundError(backlink_path)

    statements_payload = _load_json(statements_path)
    backlink_report = _load_json(backlink_path)
    registry_map = _load_registry_property_map(Path(args.relationship_registry))
    property_catalog = _load_property_catalog(Path(args.property_catalog))

    proposal = build_proposal(
        seed_qid=seed_qid,
        statements_payload=statements_payload,
        backlink_report=backlink_report,
        registry_map=registry_map,
        property_catalog=property_catalog,
        fetch_labels=not args.no_fetch_labels,
    )

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_out = Path(f"{output_prefix}.json")
    md_out = Path(f"{output_prefix}.md")

    json_out.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(
        proposal=proposal,
        output_path=md_out,
        statements_path=statements_path,
        backlinks_path=backlink_path,
    )

    summary = proposal.get("summary", {})
    print(f"seed={seed_qid}")
    print(f"nodes={summary.get('node_count', 0)}")
    print(f"relationship_claims={summary.get('relationship_claim_count', 0)}")
    print(f"attribute_claims={summary.get('attribute_claim_count', 0)}")
    print(f"json={json_out}")
    print(f"markdown={md_out}")


if __name__ == "__main__":
    main()
