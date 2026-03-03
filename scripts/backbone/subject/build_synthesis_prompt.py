#!/usr/bin/env python3
"""
Build synthesis prompt from adjacency matrix.

Reads matrix + survey files for labels. Produces LLM prompt asking for
SubjectConcept proposals grounded in federation evidence.

Output: output/synthesis/roman_republic_synthesis_prompt.txt

Usage:
  python scripts/backbone/subject/build_synthesis_prompt.py
  python scripts/backbone/subject/build_synthesis_prompt.py --matrix output/matrix/roman_republic_matrix.json --out output/synthesis/roman_republic_synthesis_prompt.txt
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from federation_node_schema import FederationSurvey

SURVEY_GLOB = "*_roman_republic.json"


def load_key_to_label(nodes_dir: Path) -> dict[str, dict]:
    """Load survey files, return {federation:id: {label, uri, federation}}."""
    key_to_meta = {}
    for p in nodes_dir.glob(SURVEY_GLOB):
        try:
            survey = FederationSurvey.load(p)
            for node in survey.nodes:
                key = f"{node.federation}:{node.id}"
                key_to_meta[key] = {
                    "label": node.label or node.id,
                    "uri": getattr(node, "uri", None),
                    "federation": node.federation,
                }
        except Exception as e:
            print(f"[WARN] Skip {p.name}: {e}", file=sys.stderr)
    return key_to_meta


def run(matrix_path: Path, nodes_dir: Path, out_path: Path) -> int:
    if not matrix_path.exists():
        print(f"ERROR: Matrix not found: {matrix_path}", file=sys.stderr)
        return 1

    print("[synthesis] Loading matrix...", file=sys.stderr)
    with open(matrix_path, encoding="utf-8") as f:
        m = json.load(f)

    node_keys = m["node_keys"]
    edges = m["edges"]
    counts = m["per_node_neighbour_counts"]

    print("[synthesis] Loading node labels from surveys...", file=sys.stderr)
    key_to_meta = load_key_to_label(nodes_dir)

    # Federation breakdown
    by_fed = Counter(k.split(":")[0] for k in node_keys)
    dim_totals = defaultdict(int)
    for c in counts.values():
        for dim, n in c.items():
            dim_totals[dim] += n

    # Cross-federation edges (sample)
    cross_edges = []
    cross_count = 0
    step = max(1, len(edges) // 50000)  # Sample ~50k edges
    for idx in range(0, len(edges), step):
        i, j, dims = edges[idx]
        a, b = node_keys[i].split(":")[0], node_keys[j].split(":")[0]
        if a != b:
            cross_count += 1
            if len(cross_edges) < 200:
                cross_edges.append((node_keys[i], node_keys[j], dims))

    # Top nodes by connectivity
    top_nodes = sorted(counts.items(), key=lambda x: sum(x[1].values()), reverse=True)[:30]

    # Build prompt
    lines = [
        "# Roman Republic Federation Synthesis — SubjectConcept Proposal",
        "",
        "## Context",
        "The Chrystallum project has federated nodes from multiple authorities (DPRR, Pleiades, LCSH, LCC, WorldCat).",
        "Nodes are connected when they share alignment dimensions: TEMPORAL (overlapping dates), GEOGRAPHIC (same place),",
        "INTELLECTUAL (same concept), SOCIAL (same person), BIBLIOGRAPHIC (same text), EVENT (same event).",
        "",
        "## Matrix Summary",
        f"- **Total nodes:** {len(node_keys)}",
        f"- **Total edges:** {len(edges)}",
        "",
        "### Nodes by federation",
    ]
    for fed, n in sorted(by_fed.items(), key=lambda x: -x[1]):
        lines.append(f"  - {fed}: {n}")
    lines.extend([
        "",
        "### Edge dimensions (neighbour-dim pairs)",
    ])
    for dim, t in sorted(dim_totals.items(), key=lambda x: -x[1]):
        lines.append(f"  - {dim}: {t}")
    lines.extend([
        "",
        "### Cross-federation edges",
        f"  - Found: {cross_count} in sample of {min(len(edges), 50000)} edges",
        f"  - Sample (first 200):",
        "",
    ])
    for a, b, dims in cross_edges[:50]:
        la = key_to_meta.get(a, {}).get("label", a)
        lb = key_to_meta.get(b, {}).get("label", b)
        lines.append(f"  - {a} ({la[:50]}...) ↔ {b} ({lb[:50]}...) via {dims}")
    if len(cross_edges) > 50:
        lines.append(f"  - ... and {len(cross_edges)-50} more")

    lines.extend([
        "",
        "### Top 30 nodes by neighbour count",
        "",
    ])
    for key, c in top_nodes:
        meta = key_to_meta.get(key, {})
        label = meta.get("label", key)
        total = sum(c.values())
        dims_str = ", ".join(f"{d}:{n}" for d, n in sorted(c.items(), key=lambda x: -x[1]))
        lines.append(f"- **{key}** — {label[:60]}")
        lines.append(f"  {total} neighbours ({dims_str})")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Your Task",
        "",
        "Propose **SubjectConcepts** for the Roman Republic domain (Q17167) based on this federation evidence.",
        "",
        "For each proposed SubjectConcept:",
        "1. **Name** — A short label (e.g. 'Offices and Magistracies', 'Rome and Italy')",
        "2. **Evidence** — Which federation nodes or clusters support it? Cite node keys (e.g. dprr:7373, pleiades:423025)",
        "3. **Dimensions** — Which alignment dimensions connect the evidence? (GEOGRAPHIC, TEMPORAL, etc.)",
        "4. **Primary facet** — POLITICAL, MILITARY, SOCIAL, ECONOMIC, RELIGIOUS, CULTURAL, GEOGRAPHIC, etc.",
        "",
        "Prioritise clusters that:",
        "- Span multiple federations (cross-federation edges)",
        "- Have strong GEOGRAPHIC or TEMPORAL coherence",
        "- Could serve as thematic anchors for entity organisation",
        "",
        "Output your proposals as a structured list. Each proposal must cite specific federation evidence from the matrix above.",
        "",
    ])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_text = "\n".join(lines)
    out_path.write_text(prompt_text, encoding="utf-8")

    print(f"[synthesis] Wrote {out_path} ({len(prompt_text)} chars)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build synthesis prompt from matrix")
    root = Path(__file__).resolve().parents[3]
    parser.add_argument("--matrix", type=Path, default=root / "output" / "matrix" / "roman_republic_matrix.json")
    parser.add_argument("--nodes-dir", type=Path, default=root / "output" / "nodes")
    parser.add_argument("--out", type=Path, default=root / "output" / "synthesis" / "roman_republic_synthesis_prompt.txt")
    args = parser.parse_args()
    return run(args.matrix, args.nodes_dir, args.out)


if __name__ == "__main__":
    sys.exit(main())
