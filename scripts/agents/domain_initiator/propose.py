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

  # Write approved proposals to graph (same run as generation):
  python scripts/agents/domain_initiator/propose.py --seed Q17167 --write

  # Write from reviewed JSON without regenerating proposals:
  python scripts/agents/domain_initiator/propose.py --write-from output/di_proposals/Q17167_proposals_enriched.json --dry-run
  python scripts/agents/domain_initiator/propose.py --write-from output/di_proposals/Q17167_proposals_enriched.json --write

  # Mark all proposals approved in the review file, then write:
  python scripts/agents/domain_initiator/propose.py --write-from output/di_proposals/Q17167_proposals_enriched.json --approve-all --save-approvals --write

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

from proposal_backbone import (
    enrich_proposals,
    load_harvest,
    load_proposals_document,
    load_route_packs,
    normalize_bootstrap_subject_id,
    normalize_proposal_for_write,
)
from facet_umbrella import (
    collect_facet_keys,
    facet_umbrella_subject_id,
    fetch_training_facet_keys,
    wire_facet_hierarchy,
)
from proposal_provenance import write_proposal_provenance


def _resolution_action(proposal: dict) -> str:
    resolution = proposal.get("resolution") or {}
    return str(resolution.get("action") or "novel").lower()


def _write_target_subject_id(proposal: dict) -> str:
    resolution = proposal.get("resolution") or {}
    merge_target = resolution.get("merge_target")
    if merge_target and _resolution_action(proposal) in ("merge", "additive"):
        return str(merge_target)
    return str(proposal.get("subject_id") or "")


def _should_write_subject_node(proposal: dict) -> bool:
    action = _resolution_action(proposal)
    return action in ("novel",)  # merge/additive skip SC MERGE


def _should_write_provenance(proposal: dict) -> bool:
    action = _resolution_action(proposal)
    return action in ("novel", "merge", "additive")

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
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if "error" not in data:
                    results[facet] = data
            except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
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
        # Decomposition — collect ALL facets with sub_scopes, not just those flagged
        # should_decompose controls child-agent spawning; sub_scopes always map SC structure
        decomp = training.get("decomposition_assessment", {})
        if decomp.get("sub_scopes"):
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

def _authority_code(value: Any) -> str:
    """Extract bare code from string or {code, label} dict."""
    if isinstance(value, dict):
        return str(value.get("code") or "")
    return str(value or "")


def _candidate_qids(proposal: dict) -> List[str]:
    qids: List[str] = []
    for item in proposal.get("candidate_qids") or []:
        if isinstance(item, dict):
            qid = item.get("qid")
        else:
            qid = item
        if qid:
            qids.append(str(qid))
    return qids


def write_proposals_to_graph(
    proposals: List[dict],
    seed_qid: str,
    *,
    dry_run: bool = False,
) -> dict:
    """Write approved SubjectConcept proposals to Neo4j.

    Also persists review artifacts on approve-write:
      - Agent provenance (proposed_by, PROPOSED_BY edge)
      - scholarly_overview on SubjectConcept
      - HAS_BIBLIO edges to CorpusWork from supporting_works
    """
    approved = [
        normalize_proposal_for_write(p)
        for p in proposals
        if p.get("status") == "approved"
    ]
    stats = {
        "approved": len(approved),
        "written": 0,
        "missing_subject_id": 0,
        "missing_parent": [],
        "missing_domain": False,
        "scoped_to": 0,
        "part_of": 0,
        "has_facet": 0,
        "anchors": 0,
        "member_of": 0,
        "proposed_by": 0,
        "has_biblio": 0,
        "resolution_skipped": 0,
        "resolution_additive": 0,
        "facet_hierarchy": {},
    }

    if not approved:
        print("\nNo proposals with status=approved.")
        return stats

    from config_loader import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            domain_row = session.run(
                """
                MATCH (sd:SubjectDomain {seed_qid: $seed_qid})
                RETURN sd.label AS label
                LIMIT 1
                """,
                seed_qid=seed_qid,
            ).single()
            if not domain_row:
                stats["missing_domain"] = True
                print(f"\nERROR: No SubjectDomain for seed_qid={seed_qid}.")
                return stats
            seed_label = domain_row["label"] or seed_qid

            training_facets = fetch_training_facet_keys(session, seed_qid)
            facet_keys = collect_facet_keys(approved, training_facets)

            if not dry_run:
                wire_facet_hierarchy(
                    session,
                    seed_qid,
                    seed_label,
                    facet_keys,
                    [],
                    dry_run=False,
                )

            def umbrella_exists(facet_key: str) -> bool:
                umbrella_id = facet_umbrella_subject_id(seed_qid, facet_key)
                row = session.run(
                    "MATCH (sc:SubjectConcept {subject_id: $id}) RETURN sc.subject_id AS id",
                    id=umbrella_id,
                ).single()
                return bool(row)

            for p in approved:
                subject_id = p.get("subject_id")
                action = _resolution_action(p)
                if action in ("skip", "hold", "conflict"):
                    stats["resolution_skipped"] += 1
                    print(f"  SKIP resolution={action}: {p.get('label')} ({subject_id})")
                    continue

                write_target = _write_target_subject_id(p)
                if not subject_id and not write_target:
                    stats["missing_subject_id"] += 1
                    print(f"  SKIP (no subject_id): {p.get('label')}")
                    continue

                if action in ("merge", "additive"):
                    stats["resolution_additive"] += 1
                    if dry_run:
                        stats["written"] += 1
                        stats["proposed_by"] += 1
                        stats["has_biblio"] += len(p.get("supporting_works") or [])
                        continue
                    prov = dict(p)
                    prov["subject_id"] = write_target
                    write_proposal_provenance(session, prov, seed_qid=seed_qid, stats=stats)
                    stats["written"] += 1
                    continue

                if not _should_write_subject_node(p):
                    continue

                parent_id = facet_umbrella_subject_id(
                    seed_qid, (p.get("source_facet") or "").lower()
                )
                if parent_id and not umbrella_exists(p.get("source_facet", "")):
                    stats["missing_parent"].append(
                        {"subject_id": subject_id, "parent_subject_id": parent_id}
                    )

                if dry_run:
                    stats["written"] += 1
                    if parent_id and umbrella_exists(p.get("source_facet", "")):
                        stats["part_of"] += 1
                    stats["has_facet"] += sum(
                        1 for w in (p.get("facet_weights") or {}).values() if float(w) > 0.1
                    )
                    stats["anchors"] += sum(
                        1 for code in (p.get("lcc_codes") or []) if _authority_code(code)
                    )
                    stats["member_of"] += len(_candidate_qids(p))
                    stats["proposed_by"] += 1
                    stats["has_biblio"] += len(p.get("supporting_works") or [])
                    continue

                cipher = p.get("concept_cipher", "")
                session.run("""
                    MERGE (sc:SubjectConcept {subject_id: $subject_id})
                    SET sc.concept_cipher = $cipher,
                        sc.label = $label,
                        sc.description = $description,
                        sc.seed_qid = $seed_qid,
                        sc.scope_key = $scope_key,
                        sc.source_facet = $source_facet,
                        sc.proposal_type = $proposal_type,
                        sc.confidence = $confidence,
                        sc.lcsh_id = $lcsh_id,
                        sc.lcsh_label = $lcsh_label,
                        sc.lcc_primary = $lcc_primary,
                        sc.source = $source,
                        sc.status = 'approved',
                        sc.approved_date = datetime(),
                        sc.updated = datetime()
                """, subject_id=subject_id, cipher=cipher, label=p["label"],
                   description=p.get("description", ""),
                   seed_qid=seed_qid, scope_key=p.get("scope_key", ""),
                   source_facet=p.get("source_facet", ""),
                   proposal_type=p.get("proposal_type", ""),
                   confidence=p.get("confidence", 0.5),
                   lcsh_id=p.get("lcsh_id"),
                   lcsh_label=p.get("lcsh_label"),
                   lcc_primary=_authority_code(p.get("lcc_primary")),
                   source=p.get("source", "di_proposal"))

                if parent_id and umbrella_exists(p.get("source_facet", "")):
                    session.run("""
                        MATCH (sc:SubjectConcept {subject_id: $subject_id})
                        MATCH (parent:SubjectConcept {subject_id: $parent_id})
                        MERGE (sc)-[:PART_OF]->(parent)
                    """, subject_id=subject_id, parent_id=parent_id)
                    stats["part_of"] += 1

                for code in p.get("lcc_codes", []):
                    lcc_code = _authority_code(code)
                    if not lcc_code:
                        continue
                    result = session.run("""
                        MATCH (sc:SubjectConcept {subject_id: $subject_id})
                        MATCH (lcc:LCC_Class {code: $code})
                        MERGE (sc)-[:ANCHORS]->(lcc)
                        RETURN lcc.code AS code
                    """, subject_id=subject_id, code=lcc_code)
                    if result.single():
                        stats["anchors"] += 1

                facet_weights = p.get("facet_weights", {})
                for facet_key, weight in facet_weights.items():
                    if weight > 0.1:
                        result = session.run("""
                            MATCH (sc:SubjectConcept {subject_id: $subject_id})
                            MATCH (f:Facet {key: toUpper($facet_key)})
                            MERGE (sc)-[r:HAS_FACET]->(f)
                            SET r.weight = $weight,
                                r.is_primary = ($facet_key = $primary_facet)
                            RETURN f.key AS facet
                        """, subject_id=subject_id,
                           facet_key=facet_key.lower(),
                           weight=weight,
                           primary_facet=p.get("source_facet", "").lower())
                        if result.single():
                            stats["has_facet"] += 1

                for qid in _candidate_qids(p):
                    result = session.run("""
                        MATCH (sc:SubjectConcept {subject_id: $subject_id})
                        MATCH (e) WHERE e.qid = $qid
                        MERGE (e)-[:MEMBER_OF]->(sc)
                        RETURN e.qid AS qid
                    """, subject_id=subject_id, qid=qid)
                    if result.single():
                        stats["member_of"] += 1

                write_proposal_provenance(session, p, seed_qid=seed_qid, stats=stats)

                stats["written"] += 1

            stats["facet_hierarchy"] = wire_facet_hierarchy(
                session,
                seed_qid,
                seed_label,
                facet_keys,
                approved,
                dry_run=dry_run,
            )

            if dry_run:
                print(f"\n[DRY RUN] Would write {stats['written']} approved SubjectConcept proposals")
            else:
                print(f"Wrote {stats['written']} approved proposals to graph")
    finally:
        driver.close()

    if stats["missing_parent"]:
        print(f"\nWARNING: {len(stats['missing_parent'])} proposals have missing facet umbrella parents:")
        for item in stats["missing_parent"][:10]:
            print(f"  {item['subject_id']} -> {item['parent_subject_id']}")
        if len(stats["missing_parent"]) > 10:
            print(f"  ... and {len(stats['missing_parent']) - 10} more")

    print(
        f"  SCOPED_TO={stats['scoped_to']}  PART_OF={stats['part_of']}  "
        f"HAS_FACET={stats['has_facet']}  ANCHORS={stats['anchors']}  "
        f"MEMBER_OF={stats['member_of']}  PROPOSED_BY={stats.get('proposed_by', 0)}  "
        f"HAS_BIBLIO={stats.get('has_biblio', 0)}  "
        f"RES_SKIP={stats.get('resolution_skipped', 0)}  "
        f"RES_ADDITIVE={stats.get('resolution_additive', 0)}"
    )
    return stats


def apply_review_updates(
    doc: dict,
    *,
    approve_all: bool = False,
    fix_parent_ids: bool = True,
) -> bool:
    """Apply in-memory review updates. Returns True if document changed."""
    changed = False
    for proposal in doc.get("proposals", []):
        if approve_all and proposal.get("status") != "approved":
            proposal["status"] = "approved"
            changed = True
        if fix_parent_ids:
            parent_id = proposal.get("parent_subject_id")
            normalized = normalize_bootstrap_subject_id(parent_id)
            if normalized and normalized != parent_id:
                proposal["parent_subject_id"] = normalized
                changed = True
    return changed


def save_proposals_document(path: Path, doc: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False, default=str)
    print(f"Saved review file: {path}")


def ensure_seed_index(seed_qid: str) -> Path | None:
    """Build seed knowledge index from cached Wikidata artifacts when missing."""
    derived = ROOT / "JSON" / "wikidata" / "derived" / f"{seed_qid.upper()}_seed_index.json"
    if derived.exists():
        return derived

    statements = ROOT / "JSON" / "wikidata" / "statements" / f"{seed_qid.upper()}_statements_full.json"
    backlink_report = (
        ROOT / "JSON" / "wikidata" / "backlinks" / f"{seed_qid.upper()}_backlink_harvest_report.json"
    )
    if not statements.exists():
        print(f"  Seed index: skipped (no {statements.relative_to(ROOT)})")
        return None

    from scripts.tools.wikidata_build_seed_index import build_seed_index

    print(f"  Building seed knowledge index for {seed_qid}...")
    index = build_seed_index(
        qid=seed_qid.upper(),
        statements_path=statements,
        backlink_report_path=backlink_report,
        fetch_labels=True,
    )
    derived.parent.mkdir(parents=True, exist_ok=True)
    derived.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    allowed = index.get("allowed_candidate_qids", {}).get("count", 0)
    print(f"  Seed index written: {derived.relative_to(ROOT)} ({allowed} allowed QIDs)")
    return derived


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
    parser.add_argument("--route-dir", type=Path,
                        default=ROOT / "output" / "di_route")
    parser.add_argument("--harvest-dir", type=Path,
                        default=ROOT / "output" / "di_harvest")
    parser.add_argument("--aggregate-only", action="store_true",
                        help="Deterministic aggregation only (no LLM)")
    parser.add_argument("--resolve-lcsh-online", action="store_true",
                        help="Query id.loc.gov for scopes without Wikidata tethers")
    parser.add_argument("--pilot-facet", type=str, default=None,
                        help="Write facet-only pilot JSON (e.g. military)")
    parser.add_argument("--write", action="store_true",
                        help="Write approved proposals to Neo4j")
    parser.add_argument("--write-from", type=Path, default=None,
                        help="Load proposals from review JSON (skip regeneration)")
    parser.add_argument("--dry-run", action="store_true",
                        help="With --write / --write-from: verify without writing")
    parser.add_argument("--approve-all", action="store_true",
                        help="With --write-from: mark every proposal status=approved")
    parser.add_argument("--save-approvals", action="store_true",
                        help="With --write-from: persist review updates to the source file")
    args = parser.parse_args()

    if args.write_from:
        doc = load_proposals_document(args.write_from)
        seed_qid = doc.get("seed_qid", args.seed)
        if apply_review_updates(doc, approve_all=args.approve_all, fix_parent_ids=True):
            if args.save_approvals:
                save_proposals_document(args.write_from, doc)
            elif args.approve_all:
                print("Review updates applied in memory only (use --save-approvals to persist).")
        proposals = doc["proposals"]
        approved_count = sum(1 for p in proposals if p.get("status") == "approved")
        print(f"Loaded {len(proposals)} proposals from {args.write_from}")
        print(f"Approved: {approved_count}/{len(proposals)}")
        if args.write or args.dry_run:
            write_proposals_to_graph(
                proposals,
                seed_qid,
                dry_run=args.dry_run or not args.write,
            )
        elif not args.save_approvals:
            print("No action taken. Add --dry-run, --write, or --save-approvals.")
        return

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
    raw_proposals = decomp_proposals + insight_proposals

    packs = load_route_packs(args.route_dir, args.seed)
    harvest = load_harvest(args.harvest_dir, args.seed)
    ensure_seed_index(args.seed)
    all_proposals = enrich_proposals(
        raw_proposals,
        seed_qid=args.seed,
        trainings=trainings,
        packs=packs,
        harvest=harvest,
        fetch_wikidata=True,
        resolve_lcsh_online=args.resolve_lcsh_online,
    )

    print(f"\n--- SubjectConcept Proposals ---")
    print(f"From decompositions: {len(decomp_proposals)}")
    print(f"From insights: {len(insight_proposals)}")
    print(f"Total (backbone-enriched): {len(all_proposals)}")

    ccs_pass = sum(1 for p in all_proposals if p.get("validation", {}).get("ccs_pass"))
    print(f"CCS pass (excl. CCS-3 warnings): {ccs_pass}/{len(all_proposals)}")

    for i, p in enumerate(all_proposals, 1):
        src = p.get("source_facet", "?")
        label = p.get("label", "?")
        conf = p.get("confidence", 0)
        cands = len(p.get("candidate_qids", []))
        lcsh = p.get("lcsh_id") or "—"
        parent = p.get("parent_subject_id") or "—"
        valid = "OK" if p.get("validation", {}).get("ccs_pass") else "FAIL"
        print(f"  {i:2d}. [{src:12s}] {label}")
        print(f"      subject_id={p.get('subject_id')}  lcsh={lcsh}  parent={parent}  "
              f"candidates={cands}  ccs={valid}")

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

    if args.pilot_facet:
        facet_key = args.pilot_facet.strip().lower()
        pilot_proposals = [p for p in all_proposals if p.get("source_facet") == facet_key]
        pilot_path = args.output / f"{args.seed}_{facet_key}_pilot.json"
        pilot_output = {
            "seed_qid": args.seed,
            "seed_label": seed_label,
            "pilot_facet": facet_key,
            "parent_bootstrap": pilot_proposals[0].get("parent_subject_id") if pilot_proposals else None,
            "generated": datetime.now(timezone.utc).isoformat(),
            "proposal_count": len(pilot_proposals),
            "proposals": pilot_proposals,
            "review_notes": (
                "Pilot batch with backbone fields. Set status=approved on each proposal "
                "then run: propose.py --write-from output/di_proposals/Q17167_proposals_enriched.json --write"
            ),
        }
        with open(pilot_path, "w", encoding="utf-8") as f:
            json.dump(pilot_output, f, indent=2, ensure_ascii=False, default=str)
        print(f"Wrote pilot: {pilot_path} ({len(pilot_proposals)} proposals)")

    if args.aggregate_only:
        print("\n--aggregate-only: skipping LLM synthesis and graph write.")
        return

    # Write to graph if requested
    if args.write:
        write_proposals_to_graph(all_proposals, args.seed, dry_run=False)
    elif args.dry_run:
        write_proposals_to_graph(all_proposals, args.seed, dry_run=True)


if __name__ == "__main__":
    main()
