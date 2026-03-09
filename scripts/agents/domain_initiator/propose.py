#!/usr/bin/env python3
"""
Domain Initiator (DI) -- Propose SubjectConcepts.

Reads training outputs for all facets of a seed, synthesizes cross-facet
insights, and produces a set of SubjectConcept proposals grounded in:
  - Training insights (corpus-based, per-facet)
  - Decomposition assessments (from D12 threshold)
  - Discipline backbone (authority IDs = corpus query keys)
  - Classification anchors (federation coordinates)

Output: JSON proposals ready for human review + optional graph write.

Architecture:
  Layer 2: Deterministic aggregation of training outputs
  Layer 3: Claude synthesis (cross-facet reasoning, dedup, hierarchy)
  Layer 4: Graph write (SubjectConcept nodes + MEMBER_OF + HAS_FACET)

Usage:
  # Aggregate training outputs and produce proposals (no write):
  python scripts/agents/domain_initiator/propose.py --seed Q17167

  # Write approved proposals to graph:
  python scripts/agents/domain_initiator/propose.py --seed Q17167 --write

  # Aggregate only (no LLM, deterministic summary):
  python scripts/agents/domain_initiator/propose.py --seed Q17167 --aggregate-only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

try:
    import anthropic
except ImportError:
    anthropic = None

CANONICAL_FACETS = [
    "archaeological", "artistic", "biographic", "communication",
    "cultural", "demographic", "diplomatic", "economic",
    "environmental", "geographic", "intellectual", "linguistic",
    "military", "political", "religious", "scientific",
    "social", "technological",
]


# ===========================================================================
# Layer 2: Deterministic aggregation
# ===========================================================================

def load_training_outputs(training_dir: Path, seed: str) -> Dict[str, dict]:
    """Load all training outputs for a seed, keyed by facet."""
    results = {}
    for facet in CANONICAL_FACETS:
        path = training_dir / f"{seed}_{facet.upper()}_training.json"
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                if "error" not in data:
                    results[facet] = data
            except (json.JSONDecodeError, KeyError):
                pass
    return results


def load_classify(classify_dir: Path, seed: str) -> Optional[dict]:
    """Load classify output for cross-reference."""
    path = classify_dir / f"{seed}_di_classify.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def aggregate_training(trainings: Dict[str, dict]) -> dict:
    """Deterministic aggregation of training outputs across facets.

    Extracts:
      - All decomposition proposals (facets that want to split)
      - Cross-facet links (insights referencing other facets)
      - Candidate verdicts (confirm/reject/reroute consensus)
      - Corpus coverage summary
      - Discipline connections
    """
    decompositions = {}
    cross_facet_links = []
    candidate_verdicts: Dict[str, List[dict]] = {}  # qid -> [verdicts]
    all_insights = []
    corpus_stats = {}
    graph_deltas = []

    for facet, training in trainings.items():
        # Decomposition
        decomp = training.get("decomposition_assessment", {})
        if decomp.get("should_decompose"):
            decompositions[facet] = decomp

        # Insights
        for insight in training.get("insights", []):
            insight["source_facet"] = facet
            all_insights.append(insight)
            if insight.get("insight_type") == "cross_facet_link":
                cross_facet_links.append(insight)

        # Candidate assessments
        for ca in training.get("candidate_assessments", []):
            qid = ca.get("qid", "")
            if qid:
                ca["source_facet"] = facet
                candidate_verdicts.setdefault(qid, []).append(ca)

        # Corpus stats
        key_works = training.get("key_works", [])
        discovered = training.get("discovered_works", [])
        corpus_stats[facet] = {
            "key_works": len(key_works),
            "discovered_works": len(discovered),
            "confidence": training.get("facet_confidence", 0),
            "gaps": training.get("corpus_gaps", []),
        }

        # Graph deltas
        for delta in training.get("graph_deltas", []):
            delta["source_facet"] = facet
            graph_deltas.append(delta)

    # Consensus verdicts
    consensus = {}
    for qid, verdicts in candidate_verdicts.items():
        confirm = sum(1 for v in verdicts if v.get("verdict") == "confirm")
        reject = sum(1 for v in verdicts if v.get("verdict") == "reject")
        reroute = sum(1 for v in verdicts if v.get("verdict") == "reroute")
        label = verdicts[0].get("label", qid)
        consensus[qid] = {
            "qid": qid,
            "label": label,
            "confirm": confirm,
            "reject": reject,
            "reroute": reroute,
            "total_votes": len(verdicts),
            "consensus": "confirm" if confirm > reject + reroute else
                        "reject" if reject > confirm + reroute else "mixed",
            "verdicts": verdicts,
        }

    return {
        "facets_trained": list(trainings.keys()),
        "facets_missing": [f for f in CANONICAL_FACETS if f not in trainings],
        "decompositions": decompositions,
        "cross_facet_links": cross_facet_links,
        "candidate_consensus": consensus,
        "all_insights": all_insights,
        "corpus_stats": corpus_stats,
        "graph_deltas": graph_deltas,
    }


def build_sc_proposals_from_decompositions(
    aggregation: dict,
    seed_qid: str,
    seed_label: str,
) -> List[dict]:
    """Build SubjectConcept proposals from decomposition assessments.

    Each facet that requested decomposition proposes sub-scopes.
    Each sub-scope becomes a candidate SubjectConcept.
    """
    proposals = []
    for facet, decomp in aggregation["decompositions"].items():
        for scope in decomp.get("sub_scopes", []):
            # Build cipher: hash of seed + facet + scope_key
            cipher_input = f"{seed_qid}:{facet}:{scope.get('scope_key', '')}"
            cipher = hashlib.sha256(cipher_input.encode()).hexdigest()[:16]

            proposal = {
                "proposal_type": "decomposition",
                "source_facet": facet,
                "scope_key": scope.get("scope_key", ""),
                "label": scope.get("scope_label", ""),
                "description": scope.get("scope_description", ""),
                "seed_qid": seed_qid,
                "seed_label": seed_label,
                "candidate_qids": scope.get("candidate_qids", []),
                "estimated_concepts": scope.get("estimated_concepts", 0),
                "needs": scope.get("needs", ""),
                "concept_cipher": cipher,
                "facet_weights": {facet: 1.0},
                "confidence": decomp.get("facet_confidence",
                              aggregation["corpus_stats"].get(facet, {}).get("confidence", 0.5)),
                "threshold_used": decomp.get("threshold_used", ""),
            }
            proposals.append(proposal)

    return proposals


def build_sc_proposals_from_insights(
    aggregation: dict,
    seed_qid: str,
) -> List[dict]:
    """Build SubjectConcept proposals from split_proposal insights."""
    proposals = []
    for insight in aggregation["all_insights"]:
        if insight.get("insight_type") != "split_proposal":
            continue
        cipher_input = f"{seed_qid}:{insight.get('source_facet', '')}:{insight.get('label', '')}"
        cipher = hashlib.sha256(cipher_input.encode()).hexdigest()[:16]

        proposals.append({
            "proposal_type": "insight_split",
            "source_facet": insight.get("source_facet", ""),
            "label": insight.get("label", ""),
            "description": insight.get("reasoning", ""),
            "seed_qid": seed_qid,
            "candidate_qids": [insight["qid"]] if insight.get("qid") else [],
            "concept_cipher": cipher,
            "facet_weights": insight.get("facet_weights", {}),
            "confidence": insight.get("confidence", 0.5),
            "evidence": insight.get("evidence", ""),
        })

    return proposals


# ===========================================================================
# Layer 4: Graph write
# ===========================================================================

def write_proposals_to_graph(proposals: List[dict], seed_qid: str, dry_run: bool = False):
    """Write approved SubjectConcept proposals to Neo4j."""
    if dry_run:
        print(f"\n[DRY RUN] Would write {len(proposals)} SubjectConcept proposals")
        return

    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            for p in proposals:
                if p.get("status") != "approved":
                    continue

                # MERGE SubjectConcept
                session.run("""
                    MERGE (sc:SubjectConcept {concept_cipher: $cipher})
                    SET sc.label = $label,
                        sc.description = $description,
                        sc.seed_qid = $seed_qid,
                        sc.source_facet = $source_facet,
                        sc.proposal_type = $proposal_type,
                        sc.confidence = $confidence,
                        sc.status = 'proposed',
                        sc.proposed_date = datetime()
                    WITH sc
                    MATCH (seed) WHERE seed.qid = $seed_qid
                    MERGE (sc)-[:SCOPED_TO]->(seed)
                """, cipher=p["concept_cipher"], label=p["label"],
                   description=p.get("description", ""),
                   seed_qid=seed_qid, source_facet=p.get("source_facet", ""),
                   proposal_type=p.get("proposal_type", ""),
                   confidence=p.get("confidence", 0.5))

                # Wire HAS_FACET
                facet_weights = p.get("facet_weights", {})
                for facet_key, weight in facet_weights.items():
                    if weight > 0.1:
                        session.run("""
                            MATCH (sc:SubjectConcept {concept_cipher: $cipher})
                            MATCH (f:Facet {label: $facet_label})
                            MERGE (sc)-[r:HAS_FACET]->(f)
                            SET r.weight = $weight
                        """, cipher=p["concept_cipher"],
                           facet_label=facet_key.capitalize(),
                           weight=weight)

                # Wire candidate entities as MEMBER_OF
                for qid in p.get("candidate_qids", []):
                    session.run("""
                        MATCH (sc:SubjectConcept {concept_cipher: $cipher})
                        MATCH (e) WHERE e.qid = $qid
                        MERGE (e)-[:MEMBER_OF]->(sc)
                    """, cipher=p["concept_cipher"], qid=qid)

            print(f"Wrote {sum(1 for p in proposals if p.get('status') == 'approved')} proposals to graph")
    finally:
        driver.close()


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="Q17167", help="Seed QID")
    parser.add_argument("--seed-label", default="Roman Republic")
    parser.add_argument("--training-dir", type=Path,
                        default=ROOT / "output" / "di_training")
    parser.add_argument("--classify-dir", type=Path,
                        default=ROOT / "output" / "di_classify")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "output" / "di_proposals")
    parser.add_argument("--aggregate-only", action="store_true",
                        help="Deterministic aggregation only (no LLM)")
    parser.add_argument("--write", action="store_true",
                        help="Write approved proposals to Neo4j")
    args = parser.parse_args()

    # Load training outputs
    trainings = load_training_outputs(args.training_dir, args.seed)
    if not trainings:
        print(f"No training outputs found in {args.training_dir} for {args.seed}")
        print("Run: python scripts/agents/domain_initiator/batch_train.py")
        return

    print(f"Loaded training for {len(trainings)} facets: {', '.join(trainings.keys())}")

    # Load classify for context
    classify = load_classify(args.classify_dir, args.seed)
    if classify:
        seed_label = classify.get("seed", {}).get("label", args.seed_label)
    else:
        seed_label = args.seed_label

    # Layer 2: Aggregate
    agg = aggregate_training(trainings)
    print(f"\n--- Aggregation Summary ---")
    print(f"Facets trained: {len(agg['facets_trained'])}")
    print(f"Facets missing: {agg['facets_missing'] or 'none'}")
    print(f"Decomposition requests: {len(agg['decompositions'])} "
          f"({', '.join(agg['decompositions'].keys()) or 'none'})")
    print(f"Cross-facet links: {len(agg['cross_facet_links'])}")
    print(f"Candidate consensus: {len(agg['candidate_consensus'])} candidates")
    print(f"Total insights: {len(agg['all_insights'])}")
    print(f"Graph deltas: {len(agg['graph_deltas'])}")

    # Corpus coverage
    print(f"\n--- Corpus Coverage ---")
    for facet, stats in sorted(agg["corpus_stats"].items()):
        conf = stats["confidence"]
        kw = stats["key_works"]
        dw = stats["discovered_works"]
        gaps = len(stats["gaps"])
        print(f"  {facet:15s}  conf={conf:.2f}  key_works={kw:2d}  discovered={dw:2d}  gaps={gaps}")

    # Build proposals from decompositions
    decomp_proposals = build_sc_proposals_from_decompositions(agg, args.seed, seed_label)
    insight_proposals = build_sc_proposals_from_insights(agg, args.seed)
    all_proposals = decomp_proposals + insight_proposals

    print(f"\n--- SubjectConcept Proposals ---")
    print(f"From decompositions: {len(decomp_proposals)}")
    print(f"From insights: {len(insight_proposals)}")
    print(f"Total: {len(all_proposals)}")

    for i, p in enumerate(all_proposals, 1):
        src = p.get("source_facet", "?")
        label = p.get("label", "?")
        conf = p.get("confidence", 0)
        cands = len(p.get("candidate_qids", []))
        print(f"  {i:2d}. [{src:12s}] {label} (conf={conf:.2f}, candidates={cands})")

    # Consensus on existing candidates
    confirmed = [v for v in agg["candidate_consensus"].values() if v["consensus"] == "confirm"]
    rejected = [v for v in agg["candidate_consensus"].values() if v["consensus"] == "reject"]
    mixed = [v for v in agg["candidate_consensus"].values() if v["consensus"] == "mixed"]
    print(f"\n--- Candidate Consensus ---")
    print(f"Confirmed: {len(confirmed)}, Rejected: {len(rejected)}, Mixed: {len(mixed)}")

    # Write output
    args.output.mkdir(parents=True, exist_ok=True)

    # Save aggregation
    agg_path = args.output / f"{args.seed}_aggregation.json"
    with open(agg_path, "w", encoding="utf-8") as f:
        json.dump(agg, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nWrote aggregation: {agg_path}")

    # Save proposals
    proposals_path = args.output / f"{args.seed}_proposals.json"
    output = {
        "seed_qid": args.seed,
        "seed_label": seed_label,
        "generated": datetime.now(timezone.utc).isoformat(),
        "facets_trained": agg["facets_trained"],
        "facets_missing": agg["facets_missing"],
        "proposals": all_proposals,
        "candidate_consensus": agg["candidate_consensus"],
        "cross_facet_links": agg["cross_facet_links"],
    }
    with open(proposals_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"Wrote proposals: {proposals_path}")

    if args.aggregate_only:
        print("\n--aggregate-only: skipping LLM synthesis and graph write.")
        return

    # Write to graph if requested
    if args.write:
        write_proposals_to_graph(all_proposals, args.seed)


if __name__ == "__main__":
    main()
