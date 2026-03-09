#!/usr/bin/env python3
"""
Domain Initiator (DI) -- Route.

SCA router: reads classify + harvest output, assembles per-facet packs,
dispatches each to the appropriate SFA.

Each SFA receives a facet pack containing:
  1. facet_delta  -- candidates (QID + label + role + score + signals), federation sources
  2. discipline_traversal -- academic disciplines with authority IDs
  3. corpus_endpoints -- 14 sources with query keys and live counts
  4. domain_context -- seed, LCSH tether, sub-subjects from backbone

Usage:
  python scripts/agents/domain_initiator/route.py \
    --classify output/di_classify/Q17167_di_classify.json \
    --harvest  output/di_harvest/Q17167_di_harvest.json

  # Dispatch only specific facets:
  python scripts/agents/domain_initiator/route.py \
    --classify output/di_classify/Q17167_di_classify.json \
    --harvest  output/di_harvest/Q17167_di_harvest.json \
    --facets military,political,economic

  # Write per-facet pack files (no SFA execution):
  python scripts/agents/domain_initiator/route.py \
    --classify output/di_classify/Q17167_di_classify.json \
    --harvest  output/di_harvest/Q17167_di_harvest.json \
    --write-packs --output output/di_route/
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Pack assembly
# ---------------------------------------------------------------------------

def load_inputs(classify_path: Path, harvest_path: Path) -> tuple[dict, dict]:
    """Load and validate classify + harvest JSON files."""
    with open(classify_path) as f:
        classify = json.load(f)
    with open(harvest_path) as f:
        harvest = json.load(f)

    # Sanity: same seed
    c_seed = classify["seed"]["qid"]
    h_seed = harvest["seed"]["qid"]
    if c_seed != h_seed:
        raise ValueError(f"Seed mismatch: classify={c_seed}, harvest={h_seed}")

    return classify, harvest


def build_domain_context(classify: dict, harvest: dict) -> dict:
    """Extract shared domain context from classify + harvest."""
    return {
        "seed": classify["seed"],
        "domain_tether": classify.get("subject_resolution", {}).get("domain_tether"),
        "sub_subjects": classify.get("subject_resolution", {}).get("sub_subjects", []),
        "backbone_summary": classify.get("subject_resolution", {}).get("backbone_summary", {}),
        "temporal_entities": classify.get("temporal_entities", []),
        "classification_summary": classify.get("classification_summary", {}),
    }


def build_facet_pack(
    facet_delta: dict,
    domain_context: dict,
    discipline_traversal: dict,
    corpus_endpoints: dict,
) -> dict:
    """Assemble a single facet pack for SFA consumption.

    Structure mirrors the SCA-SFA contract (docs/SCA_SFA_CONTRACT.md):
      - facet_delta:  candidates + federation sources + evidence summary
      - discipline_traversal: context_parents, disciplines, sub_disciplines
      - corpus_endpoints: authority_keys, subject_query, endpoints
      - domain_context: seed, tether, sub-subjects, backbone
    """
    return {
        "facet_key": facet_delta["facet_key"],
        "facet_label": facet_delta["facet_label"],
        "facet_definition": facet_delta.get("facet_definition", ""),
        "facet_delta": {
            "candidate_count": facet_delta["candidate_count"],
            "primary_count": facet_delta["primary_count"],
            "secondary_count": facet_delta["secondary_count"],
            "candidates": facet_delta["candidates"],
            "federation_sources": facet_delta.get("federation_sources", []),
            "evidence_summary": facet_delta.get("evidence_summary", ""),
            "recommended_action": facet_delta.get("recommended_action", "SFA_EVALUATE"),
        },
        "discipline_traversal": discipline_traversal,
        "corpus_endpoints": corpus_endpoints,
        "domain_context": domain_context,
    }


def build_all_packs(
    classify: dict,
    harvest: dict,
    facet_filter: Optional[List[str]] = None,
) -> List[dict]:
    """Build facet packs for all (or filtered) facet_deltas."""
    domain_context = build_domain_context(classify, harvest)
    discipline_traversal = harvest.get("discipline_traversal", {})
    corpus_endpoints = harvest.get("corpus_endpoints", {})

    packs = []
    for fd in classify.get("facet_deltas", []):
        key = fd["facet_key"]
        if facet_filter and key not in facet_filter:
            continue
        pack = build_facet_pack(fd, domain_context, discipline_traversal, corpus_endpoints)
        packs.append(pack)

    return packs


# ---------------------------------------------------------------------------
# SFA dispatch
# ---------------------------------------------------------------------------

def dispatch_pack(pack: dict, dry_run: bool = False) -> dict:
    """Dispatch a single facet pack to its SFA.

    Currently writes the pack to the SFA's accept_facet_pack() interface.
    If dry_run=True or the SFA is not available, returns a stub response.
    """
    facet_key = pack["facet_key"]
    upper_key = facet_key.upper()

    if dry_run:
        return _stub_response(pack, reason="dry_run")

    # Instantiate SFA with Claude agent + graph tools and dispatch
    try:
        from scripts.config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD or ""))
        try:
            from scripts.agents.subject_concept_facet_agents import SubjectConceptAgentFactory

            agent = SubjectConceptAgentFactory.create_agent(
                facet_key=upper_key,
                neo4j_driver=driver,
            )
            result = agent.accept_facet_pack(pack)
            return result
        finally:
            driver.close()
    except Exception as e:
        return _stub_response(pack, reason=f"sfa_error: {e}")


def _stub_response(pack: dict, reason: str = "stub") -> dict:
    """Return a stub SFA response when real dispatch is unavailable."""
    fd = pack["facet_delta"]
    return {
        "facet_key": pack["facet_key"],
        "facet_label": pack["facet_label"],
        "status": "pending_sfa",
        "reason": reason,
        "candidate_count": fd["candidate_count"],
        "primary_count": fd["primary_count"],
        "secondary_count": fd["secondary_count"],
        "federation_sources_count": len(fd.get("federation_sources", [])),
        "dispatched_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_packs(packs: List[dict], output_dir: Path, seed_qid: str) -> List[Path]:
    """Write individual facet pack files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for pack in packs:
        fname = f"{seed_qid}_{pack['facet_key']}_pack.json"
        out_path = output_dir / fname
        with open(out_path, "w") as f:
            json.dump(pack, f, indent=2, ensure_ascii=False)
        paths.append(out_path)
    return paths


def write_dispatch_report(
    packs: List[dict],
    responses: List[dict],
    output_dir: Path,
    seed_qid: str,
    classify_path: str,
    harvest_path: str,
) -> Path:
    """Write a combined dispatch report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "seed_qid": seed_qid,
        "dispatched_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "classify": str(classify_path),
            "harvest": str(harvest_path),
        },
        "facets_dispatched": len(packs),
        "facet_summary": [
            {
                "facet_key": p["facet_key"],
                "candidates": p["facet_delta"]["candidate_count"],
                "primary": p["facet_delta"]["primary_count"],
                "secondary": p["facet_delta"]["secondary_count"],
                "federation_sources": len(p["facet_delta"].get("federation_sources", [])),
                "sfa_status": r.get("status", "unknown"),
                "sfa_reason": r.get("reason", ""),
            }
            for p, r in zip(packs, responses)
        ],
    }
    out_path = output_dir / f"{seed_qid}_dispatch_report.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="DI SCA Router: classify + harvest -> per-facet SFA packs")
    parser.add_argument("--classify", required=True, help="Path to classify JSON")
    parser.add_argument("--harvest", required=True, help="Path to harvest JSON")
    parser.add_argument("--facets", default=None, help="Comma-separated facet keys to dispatch (default: all)")
    parser.add_argument("--write-packs", action="store_true", help="Write per-facet pack files")
    parser.add_argument("--dispatch", action="store_true", help="Dispatch packs to SFAs (requires Neo4j)")
    parser.add_argument("--output", default=None, help="Output directory (default: output/di_route/)")
    parser.add_argument("--dry-run", action="store_true", help="Dispatch in dry-run mode (stub responses)")
    args = parser.parse_args()

    classify_path = Path(args.classify)
    harvest_path = Path(args.harvest)

    if not classify_path.exists():
        print(f"ERROR: classify file not found: {classify_path}")
        sys.exit(1)
    if not harvest_path.exists():
        print(f"ERROR: harvest file not found: {harvest_path}")
        sys.exit(1)

    output_dir = Path(args.output) if args.output else ROOT / "output" / "di_route"

    # Parse facet filter
    facet_filter = None
    if args.facets:
        facet_filter = [f.strip().lower() for f in args.facets.split(",")]

    # Load
    print(f"Loading classify: {classify_path}")
    print(f"Loading harvest:  {harvest_path}")
    classify, harvest = load_inputs(classify_path, harvest_path)
    seed_qid = classify["seed"]["qid"]
    seed_label = classify["seed"]["label"]
    print(f"Seed: {seed_qid} ({seed_label})")
    print()

    # Build packs
    packs = build_all_packs(classify, harvest, facet_filter)
    print(f"Built {len(packs)} facet packs:")
    for p in packs:
        fd = p["facet_delta"]
        print(f"  {p['facet_key']:20s}  candidates={fd['candidate_count']:3d}  "
              f"primary={fd['primary_count']:2d}  secondary={fd['secondary_count']:2d}  "
              f"fed_sources={len(fd.get('federation_sources', []))}")
    print()

    # Write packs
    if args.write_packs:
        paths = write_packs(packs, output_dir, seed_qid)
        print(f"Wrote {len(paths)} pack files to {output_dir}/")
        for p in paths:
            print(f"  {p.name}")
        print()

    # Dispatch
    responses = []
    if args.dispatch or args.dry_run:
        dry = args.dry_run or not args.dispatch
        mode = "dry-run" if dry else "live"
        print(f"Dispatching {len(packs)} packs ({mode})...")
        for pack in packs:
            resp = dispatch_pack(pack, dry_run=dry)
            responses.append(resp)
            status = resp.get("status", "?")
            reason = resp.get("reason", "")
            print(f"  {pack['facet_key']:20s}  -> {status}  ({reason})")
        print()

        # Write dispatch report
        report_path = write_dispatch_report(
            packs, responses, output_dir, seed_qid,
            str(classify_path), str(harvest_path),
        )
        print(f"Dispatch report: {report_path}")
    elif not args.write_packs:
        # Default: just show summary, suggest next steps
        print("Use --write-packs to write per-facet pack files.")
        print("Use --dispatch to send packs to SFAs (requires Neo4j + accept_facet_pack).")
        print("Use --dry-run to generate stub responses without SFA execution.")


if __name__ == "__main__":
    main()
