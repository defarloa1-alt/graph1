#!/usr/bin/env python3
"""
Align federation survey nodes across federations.

Reads all output/nodes/*.json survey files, computes adjacency between nodes
using shared alignment fields (temporal_range overlap, spatial_anchor match,
concept_ref match, wikidata_qid). Outputs aligned node list for build_adjacency_matrix.

Neighbours:
  - Confirmed: same wikidata_qid (when present)
  - Probable: temporal overlap, spatial match, or concept_ref match

Usage:
  python scripts/backbone/subject/align_federations.py
  python scripts/backbone/subject/align_federations.py --nodes-dir output/nodes --out output/aligned/roman_republic_aligned.json
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from federation_node_schema import (
    FederationSurvey,
    _norm_uri,
    _spatial_match,
)


SURVEY_GLOB = "*_roman_republic.json"
DOMAIN = "roman_republic"


def _node_key(node) -> str:
    return f"{node.federation}:{node.id}"


def load_all_surveys(nodes_dir: Path) -> list:
    """Load all federation survey JSON files, return flat list of FederationNode."""
    all_nodes = []
    seen = set()
    for p in nodes_dir.glob(SURVEY_GLOB):
            if p.name in seen:
                continue
            seen.add(p.name)
            try:
                survey = FederationSurvey.load(p)
                for node in survey.nodes:
                    all_nodes.append(node)
            except Exception as e:
                print(f"[WARN] Skip {p.name}: {e}", file=sys.stderr)
    return all_nodes


def build_indexes(nodes: list) -> dict:
    """Build indexes for efficient neighbour lookup."""
    by_spatial = defaultdict(list)
    by_concept = defaultdict(list)
    by_qid = defaultdict(list)
    by_person = defaultdict(list)
    by_text = defaultdict(list)
    by_event = defaultdict(list)

    for node in nodes:
        if node.spatial_anchor:
            norm = _norm_uri(node.spatial_anchor)
            by_spatial[norm].append(node)
        if node.concept_ref:
            norm = _norm_uri(node.concept_ref)
            by_concept[norm].append(node)
        if node.wikidata_qid:
            by_qid[node.wikidata_qid].append(node)
        if node.person_ref:
            norm = _norm_uri(node.person_ref)
            by_person[norm].append(node)
        if node.text_ref:
            norm = _norm_uri(node.text_ref)
            by_text[norm].append(node)
        if node.event_ref:
            by_event[node.event_ref].append(node)

    return {
        "by_spatial": by_spatial,
        "by_concept": by_concept,
        "by_qid": by_qid,
        "by_person": by_person,
        "by_text": by_text,
        "by_event": by_event,
    }


def find_neighbours(node, nodes_by_key: dict, indexes: dict) -> tuple[list, list]:
    """
    Find confirmed and probable neighbours for a node.
    Returns (confirmed_neighbours, probable_neighbours) as lists of (key, shared_dims).
    """
    key = _node_key(node)
    confirmed = []
    probable = []
    seen = {key}

    # Confirmed: same wikidata_qid
    if node.wikidata_qid:
        for other in indexes["by_qid"].get(node.wikidata_qid, []):
            ok = _node_key(other)
            if ok not in seen:
                seen.add(ok)
                shared = node.adjacency(other)
                if shared:
                    confirmed.append((ok, shared))

    # Probable: spatial, concept, person, text, event, temporal
    def add_probable(candidates, dims):
        for other in candidates:
            ok = _node_key(other)
            if ok not in seen:
                shared = node.adjacency(other)
                if shared:
                    seen.add(ok)
                    probable.append((ok, shared))

    if node.spatial_anchor:
        norm = _norm_uri(node.spatial_anchor)
        add_probable(indexes["by_spatial"].get(norm, []), ["GEOGRAPHIC"])

    if node.concept_ref:
        norm = _norm_uri(node.concept_ref)
        add_probable(indexes["by_concept"].get(norm, []), ["INTELLECTUAL"])

    if node.person_ref:
        norm = _norm_uri(node.person_ref)
        add_probable(indexes["by_person"].get(norm, []), ["SOCIAL"])

    if node.text_ref:
        norm = _norm_uri(node.text_ref)
        add_probable(indexes["by_text"].get(norm, []), ["BIBLIOGRAPHIC"])

    if node.event_ref:
        add_probable(indexes["by_event"].get(node.event_ref, []), ["EVENT"])

    # Temporal-only: deferred (O(n²) with 32k nodes). Temporal overlap is still
    # computed in adjacency() when nodes match on spatial/concept — so we get
    # TEMPORAL in shared_dims for those pairs. For temporal-only neighbours,
    # run build_adjacency_matrix which can use a coarser temporal index.
    return confirmed, probable


def run(nodes_dir: Path, out_path: Path) -> int:
    nodes = load_all_surveys(nodes_dir)
    if not nodes:
        print("ERROR: No nodes loaded", file=sys.stderr)
        return 1

    nodes_by_key = {_node_key(n): n for n in nodes}
    indexes = build_indexes(nodes)

    aligned_nodes = []
    total_confirmed = 0
    total_probable = 0

    for node in nodes:
        confirmed, probable = find_neighbours(node, nodes_by_key, indexes)
        total_confirmed += len(confirmed)
        total_probable += len(probable)

        d = node.to_dict()
        d["aligned_ids"] = d.get("aligned_ids") or {}
        d["aligned_ids"]["confirmed_neighbours"] = [k for k, _ in confirmed]
        d["aligned_ids"]["probable_neighbours"] = [k for k, _ in probable]
        d["aligned_ids"]["neighbour_dims"] = {k: dims for k, dims in (confirmed + probable)}
        d["status"] = "aligned" if (confirmed or probable) else "raw"
        aligned_nodes.append(d)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "domain": DOMAIN,
        "aligned_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "node_count": len(aligned_nodes),
        "total_confirmed_edges": total_confirmed // 2,  # each edge counted twice
        "total_probable_edges": total_probable // 2,
        "nodes": aligned_nodes,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    aligned_count = sum(1 for n in aligned_nodes if n["status"] == "aligned")
    print(f"[align] {len(aligned_nodes)} nodes, {aligned_count} aligned, "
          f"~{total_confirmed // 2} confirmed + ~{total_probable // 2} probable edges")
    print(f"[align] Wrote {out_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Align federation survey nodes")
    root = Path(__file__).resolve().parents[3]
    parser.add_argument("--nodes-dir", type=Path, default=root / "output" / "nodes")
    parser.add_argument("--out", type=Path, default=root / "output" / "aligned" / "roman_republic_aligned.json")
    args = parser.parse_args()

    if not args.nodes_dir.exists():
        print(f"ERROR: Nodes dir not found: {args.nodes_dir}", file=sys.stderr)
        return 1

    return run(args.nodes_dir, args.out)


if __name__ == "__main__":
    sys.exit(main())
