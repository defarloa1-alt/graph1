#!/usr/bin/env python3
"""
SCA Proposal Resolution — orchestrates dupe vs additive vs conflict before graph write.

Architecture:
  Tier 1 (deterministic): concept_cipher, subject_id, label+facet, authority match
  Tier 2 (SCA LLM):       ambiguous cross-facet / bio-primary / merge judgment
  Tier 3 (human):         Review Queue approves holds and conflicts

The SCA is the orchestrator — not individual SFAs (facet-biased) and not Layer 4
(dumb executor). SFAs propose; SCA resolves; humans gate; propose.py --write executes.

Usage:
  python scripts/agents/sca/proposal_resolution.py --seed Q17167
  python scripts/agents/sca/proposal_resolution.py --seed Q17167 --llm
  python scripts/agents/sca/proposal_resolution.py --seed Q17167 --deterministic-only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

try:
    import anthropic
except ImportError:
    anthropic = None

from scripts.agents.republic_graph_context import append_republic_graph_context

RESOLUTION_ACTIONS = frozenset({"novel", "merge", "additive", "conflict", "hold", "skip"})
RESOLUTION_TIERS = frozenset({"deterministic", "sca_llm", "human_required"})

BIO_KEYWORDS = (
    "person", "prosopograph", "family", "gens", "biograph", "senator", "magistrate",
    "tribune", "consul", "praetor", "cursus", "elite", "populist", "kinship",
    "genealog", "career", "office",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_label(label: str) -> str:
    text = (label or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _bio_overlap(proposal: dict[str, Any]) -> bool:
    facet = (proposal.get("source_facet") or "").lower()
    if facet == "biographic":
        return False
    text = f"{proposal.get('label', '')} {proposal.get('description', '')}".lower()
    weights = proposal.get("facet_weights") or {}
    return float(weights.get("biographic") or 0) >= 0.4 or any(k in text for k in BIO_KEYWORDS)


def fetch_graph_index(session: Any, seed_qid: str) -> dict[str, Any]:
    """Load existing SubjectConcepts for resolution checks."""
    rows = list(
        session.run(
            """
            MATCH (sc:SubjectConcept)
            WHERE sc.seed_qid = $seed_qid OR sc.subject_id STARTS WITH 'sc_q'
            RETURN sc.subject_id AS subject_id,
                   sc.label AS label,
                   sc.concept_cipher AS concept_cipher,
                   sc.source AS source,
                   sc.source_facet AS source_facet,
                   sc.scope_key AS scope_key,
                   sc.lcsh_id AS lcsh_id
            """,
            seed_qid=seed_qid,
        )
    )
    by_id: dict[str, dict[str, Any]] = {}
    by_cipher: dict[str, dict[str, Any]] = {}
    by_label_facet: dict[tuple[str, str], dict[str, Any]] = {}
    by_lcsh: dict[str, dict[str, Any]] = {}

    for row in rows:
        rec = dict(row)
        sid = rec.get("subject_id")
        if sid:
            by_id[sid] = rec
        cipher = rec.get("concept_cipher")
        if cipher:
            by_cipher[cipher] = rec
        key = (_normalize_label(rec.get("label") or ""), (rec.get("source_facet") or "").lower())
        if key[0]:
            by_label_facet[key] = rec
        lcsh = rec.get("lcsh_id")
        if lcsh:
            by_lcsh[lcsh] = rec

    return {
        "by_id": by_id,
        "by_cipher": by_cipher,
        "by_label_facet": by_label_facet,
        "by_lcsh": by_lcsh,
        "count": len(rows),
    }


def resolve_deterministic(
    proposal: dict[str, Any],
    graph_index: dict[str, Any],
    *,
    seed_qid: str,
) -> dict[str, Any] | None:
    """Return resolution dict if Tier 1 can decide, else None."""
    subject_id = proposal.get("subject_id") or ""
    cipher = proposal.get("concept_cipher") or ""
    label = proposal.get("label") or ""
    facet = (proposal.get("source_facet") or "").lower()
    status = (proposal.get("status") or "proposed").lower()
    lcsh_id = proposal.get("lcsh_id") or (proposal.get("authority") or {}).get("lcsh_id")

    if status in ("rejected", "held", "hold"):
        return {
            "action": "hold" if status in ("held", "hold") else "skip",
            "tier": "deterministic",
            "merge_target": None,
            "rationale": f"Human review status={status}",
            "bio_primary_note": None,
        }

    by_id = graph_index["by_id"]
    by_cipher = graph_index["by_cipher"]
    by_label_facet = graph_index["by_label_facet"]
    by_lcsh = graph_index["by_lcsh"]

    if cipher and cipher in by_cipher:
        existing = by_cipher[cipher]
        existing_id = existing["subject_id"]
        if existing_id == subject_id:
            return {
                "action": "additive",
                "tier": "deterministic",
                "merge_target": existing_id,
                "rationale": "Same concept_cipher and subject_id — refresh bibliography/overview only.",
                "bio_primary_note": None,
            }
        return {
            "action": "conflict",
            "tier": "human_required",
            "merge_target": existing_id,
            "rationale": (
                f"concept_cipher collision: proposal {subject_id} vs existing {existing_id}. "
                "Requires human merge or ID fix."
            ),
            "bio_primary_note": None,
        }

    if subject_id and subject_id in by_id:
        return {
            "action": "additive",
            "tier": "deterministic",
            "merge_target": subject_id,
            "rationale": "subject_id already in graph — update evidence, do not recreate node.",
            "bio_primary_note": None,
        }

    norm_label = _normalize_label(label)
    if norm_label and (norm_label, facet) in by_label_facet:
        existing = by_label_facet[(norm_label, facet)]
        return {
            "action": "merge",
            "tier": "deterministic",
            "merge_target": existing["subject_id"],
            "rationale": f"Exact label+facet match to existing {existing['subject_id']}.",
            "bio_primary_note": None,
        }

    if lcsh_id and lcsh_id in by_lcsh:
        existing = by_lcsh[lcsh_id]
        if existing.get("subject_id") != subject_id:
            return {
                "action": "merge",
                "tier": "deterministic",
                "merge_target": existing["subject_id"],
                "rationale": f"Shared LCSH tether {lcsh_id} with {existing['subject_id']}.",
                "bio_primary_note": None,
            }

    if _bio_overlap(proposal):
        return None  # escalate to SCA LLM

    return {
        "action": "novel",
        "tier": "deterministic",
        "merge_target": None,
        "rationale": "No graph collision detected.",
        "bio_primary_note": None,
    }


def _should_escalate_to_llm(
    proposal: dict[str, Any],
    det: dict[str, Any] | None,
    *,
    bio_overlap_only: bool = False,
) -> bool:
    if det is None:
        return True
    facet = (proposal.get("source_facet") or "").lower()
    if bio_overlap_only and not _bio_overlap(proposal):
        return False
    if (
        _bio_overlap(proposal)
        and facet != "biographic"
        and det.get("action") in ("additive", "novel", "merge")
    ):
        return True
    return False


SYSTEM_PROMPT = """You are the Subject Concept Agent (SCA) resolution orchestrator for Chrystallum.

Your job is NOT to propose new SubjectConcepts. SFAs already proposed. You adjudicate
what happens when a proposal meets the existing graph:

  - novel     → new scope node (no substantive collision)
  - merge     → same scholarly scope as an existing SC; attach to merge_target, do NOT duplicate
  - additive  → existing SC gets new bibliography/evidence; no new node
  - conflict  → incompatible scopes or identity collision; human must decide
  - hold      → insufficient evidence to decide

Rules:
  - Biographic SFA is PRIMARY for Person/prosopography/family/career identity.
    If a non-biographic facet proposes person-shaped scope, prefer merge/additive
    toward an existing biographic SC or hold — never duplicate bio scaffolding.
  - Do not merge scopes that are related but academically distinct (e.g. "Roman Army"
    vs "Military Command Structure" — hold or novel, explain why).
  - When merging, merge_target MUST be an existing subject_id from the graph index.
  - Output ONLY valid JSON array, one object per proposal, same order as input.

Output schema per item:
{
  "subject_id": "...",
  "action": "novel|merge|additive|conflict|hold",
  "merge_target": "sc_..." or null,
  "rationale": "1-3 sentences",
  "bio_primary_note": "string or null"
}
"""


def _build_llm_user_message(
    proposals: list[dict[str, Any]],
    graph_index: dict[str, Any],
    seed_qid: str,
) -> str:
    compact_graph = [
        {
            "subject_id": v["subject_id"],
            "label": v.get("label"),
            "source_facet": v.get("source_facet"),
            "source": v.get("source"),
            "concept_cipher": v.get("concept_cipher"),
        }
        for v in list(graph_index["by_id"].values())[:120]
    ]
    compact_props = [
        {
            "subject_id": p.get("subject_id"),
            "label": p.get("label"),
            "source_facet": p.get("source_facet"),
            "description": (p.get("description") or "")[:240],
            "concept_cipher": p.get("concept_cipher"),
            "bio_overlap": _bio_overlap(p),
            "deterministic_hint": (p.get("_deterministic_resolution") or {}).get("action"),
        }
        for p in proposals
    ]
    biographic_scopes = [
        {
            "subject_id": v["subject_id"],
            "label": v.get("label"),
            "source_facet": v.get("source_facet"),
        }
        for v in graph_index["by_id"].values()
        if (v.get("source_facet") or "").lower() == "biographic"
    ]
    return (
        f"Seed: {seed_qid}\n\n"
        f"Biographic SubjectConcepts (primary owner for person/prosopography):\n"
        f"{json.dumps(biographic_scopes, indent=2)}\n\n"
        f"Existing SubjectConcepts ({len(compact_graph)} shown):\n"
        f"{json.dumps(compact_graph, indent=2)}\n\n"
        f"Proposals needing SCA adjudication ({len(compact_props)}):\n"
        f"{json.dumps(compact_props, indent=2)}"
    )


def resolve_with_llm(
    proposals: list[dict[str, Any]],
    graph_index: dict[str, Any],
    *,
    seed_qid: str,
    model: str = "claude-sonnet-4-6",
) -> list[dict[str, Any]]:
    if not anthropic:
        raise ImportError("anthropic required for --llm. pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key and (ROOT / ".env").exists():
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    system = append_republic_graph_context(SYSTEM_PROMPT, seed_qid)
    user = _build_llm_user_message(proposals, graph_index, seed_qid)

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=8000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:])
        if text.rstrip().endswith("```"):
            text = text[: text.rfind("```")].rstrip()

    parsed = json.loads(text)
    if isinstance(parsed, dict) and "resolutions" in parsed:
        parsed = parsed["resolutions"]
    if not isinstance(parsed, list):
        raise ValueError("LLM response must be a JSON array")

    by_id = {item.get("subject_id"): item for item in parsed if item.get("subject_id")}
    out: list[dict[str, Any]] = []
    for p in proposals:
        sid = p.get("subject_id")
        item = by_id.get(sid)
        if not item:
            out.append(
                {
                    "action": "hold",
                    "tier": "sca_llm",
                    "merge_target": None,
                    "rationale": "SCA LLM omitted this proposal — defaulting to hold.",
                    "bio_primary_note": None,
                }
            )
            continue
        action = str(item.get("action", "hold")).lower()
        if action not in RESOLUTION_ACTIONS:
            action = "hold"
        out.append(
            {
                "action": action,
                "tier": "sca_llm",
                "merge_target": item.get("merge_target"),
                "rationale": item.get("rationale") or "",
                "bio_primary_note": item.get("bio_primary_note"),
                "resolved_at": _utc_now_iso(),
            }
        )
    return out


def resolve_proposals(
    proposals: list[dict[str, Any]],
    *,
    seed_qid: str,
    graph_index: dict[str, Any] | None = None,
    use_llm: bool = True,
    bio_overlap_only: bool = False,
    session: Any | None = None,
) -> list[dict[str, Any]]:
    """Attach resolution block to each proposal."""
    idx = graph_index
    if idx is None:
        if session is None:
            raise ValueError("graph_index or Neo4j session required")
        idx = fetch_graph_index(session, seed_qid)

    escalated: list[dict[str, Any]] = []
    escalated_indices: list[int] = []
    resolutions: list[dict[str, Any] | None] = []

    for i, proposal in enumerate(proposals):
        det = resolve_deterministic(proposal, idx, seed_qid=seed_qid)
        if _should_escalate_to_llm(proposal, det, bio_overlap_only=bio_overlap_only):
            esc = dict(proposal)
            if det:
                esc["_deterministic_resolution"] = det
            escalated.append(esc)
            escalated_indices.append(i)
            resolutions.append(None)
        else:
            resolutions.append(det)

    if escalated and use_llm:
        llm_results = resolve_with_llm(escalated, idx, seed_qid=seed_qid)
        for pos, result in zip(escalated_indices, llm_results):
            resolutions[pos] = result
    elif escalated:
        for pos in escalated_indices:
            resolutions[pos] = {
                "action": "hold",
                "tier": "human_required",
                "merge_target": None,
                "rationale": "Bio/cross-facet overlap — requires SCA LLM or human adjudication.",
                "bio_primary_note": "Non-biographic proposal with person/prosopography signals.",
            }

    out: list[dict[str, Any]] = []
    for proposal, resolution in zip(proposals, resolutions):
        merged = dict(proposal)
        merged.pop("_deterministic_resolution", None)
        merged["resolution"] = resolution or {
            "action": "hold",
            "tier": "human_required",
            "merge_target": None,
            "rationale": "Unresolved",
            "bio_primary_note": None,
        }
        merged["resolution"]["resolved_at"] = merged["resolution"].get("resolved_at") or _utc_now_iso()
        out.append(merged)
    return out


def summarize_resolutions(proposals: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for p in proposals:
        action = (p.get("resolution") or {}).get("action", "?")
        counts[action] = counts.get(action, 0) + 1
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="SCA proposal resolution orchestrator")
    ap.add_argument("--seed", default="Q17167")
    ap.add_argument(
        "--input",
        type=Path,
        default=ROOT / "output" / "di_proposals" / "Q17167_proposals_enriched.json",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Default: output/di_proposals/{seed}_proposals_resolved.json",
    )
    ap.add_argument("--llm", action="store_true", help="Run SCA LLM for ambiguous proposals")
    ap.add_argument(
        "--bio-overlap-only",
        action="store_true",
        help="LLM-adjudicate only bio-overlap proposals (recommended after backfill)",
    )
    ap.add_argument("--deterministic-only", action="store_true")
    ap.add_argument("--status", default="approved", help="Filter proposals by status")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Not found: {args.input}")
        return 1

    with open(args.input, encoding="utf-8") as f:
        doc = json.load(f)

    seed_qid = doc.get("seed_qid", args.seed).upper()
    targets = [
        p
        for p in doc.get("proposals", [])
        if p.get("proposal_type") == "decomposition"
        and (not args.status or p.get("status") == args.status)
    ]

    from config_loader import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            graph_index = fetch_graph_index(session, seed_qid)
            resolved = resolve_proposals(
                targets,
                seed_qid=seed_qid,
                graph_index=graph_index,
                use_llm=args.llm and not args.deterministic_only,
                bio_overlap_only=args.bio_overlap_only,
                session=session,
            )
    finally:
        driver.close()

    resolved_by_id = {p["subject_id"]: p for p in resolved if p.get("subject_id")}
    merged_proposals = []
    for p in doc.get("proposals", []):
        sid = p.get("subject_id")
        if sid and sid in resolved_by_id:
            merged_proposals.append(resolved_by_id[sid])
        else:
            merged_proposals.append(p)

    out_doc = dict(doc)
    out_doc["proposals"] = merged_proposals
    out_doc["resolution_pass"] = {
        "at": _utc_now_iso(),
        "orchestrator": "SCA",
        "tier1": "deterministic",
        "tier2": "sca_llm" if args.llm and not args.deterministic_only else None,
        "bio_overlap_only": args.bio_overlap_only,
        "graph_sc_count": graph_index["count"],
        "summary": summarize_resolutions(resolved),
        "llm_escalated": len(resolved_by_id),
    }

    out_path = args.output or (
        ROOT / "output" / "di_proposals" / f"{seed_qid}_proposals_resolved.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_doc, f, indent=2, ensure_ascii=False)

    summary = summarize_resolutions(resolved)
    print(f"Resolved {len(resolved)} proposals -> {out_path.name}")
    print(f"  Graph SCs indexed: {graph_index['count']}")
    print(f"  Summary: {summary}")
    if not args.llm and not args.deterministic_only:
        print("  Tip: re-run with --llm for bio/cross-facet ambiguous cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
