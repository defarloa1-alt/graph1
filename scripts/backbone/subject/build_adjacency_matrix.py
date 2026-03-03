#!/usr/bin/env python3
"""
Build adjacency matrix from aligned federation nodes.

Two modes:
  1. --nodes-dir: Load survey files, run alignment, build matrix (faster, no 4GB file)
  2. --input: Read pre-built aligned JSON (streams with ijson for large files)

Output: output/matrix/roman_republic_matrix.json
  - node_keys, edges, per_node_neighbour_counts

Usage:
  python scripts/backbone/subject/build_adjacency_matrix.py --nodes-dir output/nodes
  python scripts/backbone/subject/build_adjacency_matrix.py --input output/aligned/roman_republic_aligned.json
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

try:
    import ijson
except ImportError:
    ijson = None

from federation_node_schema import FederationSurvey, _norm_uri, _spatial_match

SURVEY_GLOB = "*_roman_republic.json"


def _node_key(node_or_dict) -> str:
    if isinstance(node_or_dict, dict):
        return f"{node_or_dict.get('federation', '')}:{node_or_dict.get('id', '')}"
    return f"{node_or_dict.federation}:{node_or_dict.id}"


def stream_aligned_nodes(aligned_path: Path):
    """Stream nodes from aligned JSON using ijson."""
    if ijson is None:
        raise ImportError("ijson required for streaming large JSON. pip install ijson")
    with open(aligned_path, "rb") as f:
        for node in ijson.items(f, "nodes.item"):
            yield node


def load_aligned_fallback(aligned_path: Path):
    """Fallback: load full JSON (may OOM on very large files)."""
    with open(aligned_path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("nodes", [])


def run_from_surveys(nodes_dir: Path, out_path: Path, limit: int | None = None) -> int:
    """Build matrix from survey files (avoids loading 4GB aligned file)."""
    from align_federations import load_all_surveys, build_indexes, find_neighbours, _node_key as _nk

    nodes = load_all_surveys(nodes_dir)
    if not nodes:
        print("ERROR: No nodes loaded from surveys", file=sys.stderr)
        return 1
    if limit:
        nodes = nodes[:limit]
    nodes_by_key = {_nk(n): n for n in nodes}
    indexes = build_indexes(nodes)

    node_keys = []
    key_to_index = {}
    edges = []
    edge_pairs = set()
    per_node_counts = defaultdict(lambda: defaultdict(int))

    for idx, node in enumerate(nodes):
        key = _nk(node)
        if key not in key_to_index:
            key_to_index[key] = len(node_keys)
            node_keys.append(key)
        i = key_to_index[key]
        confirmed, probable = find_neighbours(node, nodes_by_key, indexes)
        for nb_key, dims in confirmed + probable:
            if not dims:
                continue
            if nb_key not in key_to_index:
                key_to_index[nb_key] = len(node_keys)
                node_keys.append(nb_key)
            j = key_to_index[nb_key]
            pair = (min(i, j), max(i, j))
            if pair not in edge_pairs:
                edge_pairs.add(pair)
                edges.append([pair[0], pair[1], dims])
            for dim in dims:
                per_node_counts[key][dim] += 1
        if (idx + 1) % 1000 == 0:
            print(f"[matrix] Processed {idx + 1} nodes, {len(edges)} edges...", file=sys.stderr, flush=True)

    print(f"[matrix] Writing output (compact format)...", file=sys.stderr, flush=True)
    per_node_neighbour_counts = {k: dict(v) for k, v in per_node_counts.items()}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "domain": "roman_republic",
        "node_count": len(node_keys),
        "edge_count": len(edges),
        "node_keys": node_keys,
        "edges": edges,
        "per_node_neighbour_counts": per_node_neighbour_counts,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=None)  # Compact: ~3x smaller, much faster write
    print(f"[matrix] {len(node_keys)} nodes, {len(edges)} edges")
    print(f"[matrix] Wrote {out_path}")
    return 0


def run_from_aligned(aligned_path: Path, out_path: Path, use_streaming: bool = True, limit: int | None = None) -> int:
    if not aligned_path.exists():
        print(f"ERROR: Input not found: {aligned_path}", file=sys.stderr)
        return 1

    node_keys = []
    key_to_index = {}
    edges = []  # (i, j, dims) with i < j
    per_node_counts = defaultdict(lambda: defaultdict(int))

    if use_streaming and ijson:
        nodes_iter = stream_aligned_nodes(aligned_path)
        node_count_unknown = True
    else:
        nodes = load_aligned_fallback(aligned_path)
        nodes_iter = iter(nodes)
        node_count_unknown = False

    edge_pairs = set()  # (min_i, max_i) to dedupe

    for idx, node in enumerate(nodes_iter):
        key = _node_key(node)
        if key not in key_to_index:
            key_to_index[key] = len(node_keys)
            node_keys.append(key)

        i = key_to_index[key]
        aligned = node.get("aligned_ids") or {}
        neighbour_dims = aligned.get("neighbour_dims") or {}

        for nb_key, dims in neighbour_dims.items():
            if not dims:
                continue
            if nb_key not in key_to_index:
                key_to_index[nb_key] = len(node_keys)
                node_keys.append(nb_key)
            j = key_to_index[nb_key]
            pair = (min(i, j), max(i, j))
            if pair not in edge_pairs:
                edge_pairs.add(pair)
                edges.append([pair[0], pair[1], dims])

            for dim in dims:
                per_node_counts[key][dim] += 1

        if (idx + 1) % 5000 == 0:
            print(f"[matrix] Processed {idx + 1} nodes, {len(edges)} edges...", file=sys.stderr)

    # Convert per_node_counts to serializable dict
    per_node_neighbour_counts = {
        k: dict(v) for k, v in per_node_counts.items()
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "domain": "roman_republic",
        "node_count": len(node_keys),
        "edge_count": len(edges),
        "node_keys": node_keys,
        "edges": edges,
        "per_node_neighbour_counts": per_node_neighbour_counts,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[matrix] {len(node_keys)} nodes, {len(edges)} edges")
    print(f"[matrix] Wrote {out_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build adjacency matrix from aligned nodes or survey files")
    root = Path(__file__).resolve().parents[3]
    parser.add_argument("--nodes-dir", type=Path, default=None, help="Build from survey files (faster, no 4GB aligned file)")
    parser.add_argument("--input", type=Path, default=root / "output" / "aligned" / "roman_republic_aligned.json")
    parser.add_argument("--out", type=Path, default=root / "output" / "matrix" / "roman_republic_matrix.json")
    parser.add_argument("--no-streaming", action="store_true", help="Load full aligned JSON (may OOM on large files)")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N nodes (for testing)")
    args = parser.parse_args()

    if args.nodes_dir:
        return run_from_surveys(args.nodes_dir, args.out, limit=args.limit)
    return run_from_aligned(args.input, args.out, use_streaming=not args.no_streaming, limit=args.limit)


if __name__ == "__main__":
    sys.exit(main())
