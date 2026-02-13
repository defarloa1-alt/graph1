import re
import json
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any, Tuple


# ---------- Core parsing + hierarchy utilities ----------

def normalize_outline_lines(raw_text: str) -> List[str]:
    """
    Take raw OUTLINE text (possibly with broken lines) and:
    - Strip empty lines
    - Merge continuation lines into the previous code line

    Assumes each new class line starts with 1–2 letters + digit, e.g. 'KF500-599 ...'
    """
    lines = [l.rstrip() for l in raw_text.splitlines() if l.strip()]
    merged: List[str] = []
    code_re = re.compile(r'^[A-Z]{1,2}[0-9]')  # e.g. K, KF, PQ, RC, etc.

    for line in lines:
        if code_re.match(line):
            merged.append(line)
        else:
            if not merged:
                # Continuation before any code line; ignore.
                continue
            # Append continuation to previous line
            merged[-1] = merged[-1] + " " + line.strip()

    return merged


def parse_code_and_label(line: str) -> Tuple[str, str]:
    """
    Parse one normalized OUTLINE line into (code, label).

    Example:
        'KF500-599 Contracts. Obligations (General)'
        -> ('KF500-599', 'Contracts. Obligations (General)')
    """
    m = re.match(r'^([A-Z]{1,2}[0-9.]+(?:-[0-9.]+)?)\s+(.+)$', line)
    if not m:
        raise ValueError(f"Could not parse code/label from line: {line!r}")
    return m.group(1), m.group(2)


def parse_range(code: str) -> Tuple[str, float, float]:
    """
    Given an LCC code string like 'KF500-599' or 'RC954.6', return:
        prefix: 'KF', 'RC'
        start:  numeric start (float)
        end:    numeric end (float; = start if single)
    """
    c = code.replace(" ", "")
    m = re.match(r'^([A-Z]{1,2})([0-9.]+)(?:-([0-9.]+))?$', c)
    if not m:
        raise ValueError(f"Could not parse numeric range from code: {code!r}")
    prefix = m.group(1)
    start = float(m.group(2))
    end_raw = m.group(3)
    end = float(end_raw) if end_raw else start
    return prefix, start, end


def build_nodes(raw_text: str) -> List[Dict[str, Any]]:
    """
    End-to-end:
    - Normalize raw OUTLINE text
    - Extract (code, label) pairs
    - Build node dicts with numeric ranges and empty hierarchy links
    """
    lines = normalize_outline_lines(raw_text)

    entries = []
    for l in lines:
        try:
            code, label = parse_code_and_label(l)
        except ValueError:
            # Skip lines we can't parse cleanly
            continue
        entries.append({"code": code, "label": label})

    nodes: List[Dict[str, Any]] = []
    for e in entries:
        try:
            prefix, start, end = parse_range(e["code"])
        except ValueError:
            # Skip weird codes (e.g., pure letters with no number)
            continue

        nodes.append(
            {
                "id": e["code"],
                "code": e["code"],
                "prefix": prefix,
                "start": start,
                "end": end,
                "label": e["label"],
                "note": None,
                "primary_parent": None,
                "secondary_parents": [],
                "children": [],
            }
        )

    return nodes


def assign_hierarchy(nodes: List[Dict[str, Any]]) -> None:
    """
    Modifies nodes in-place to set:
        - primary_parent for each node
        - children lists on parents

    Rule:
        - Within each prefix (e.g., KF), a node's parent is the smallest
          interval that fully contains its [start, end].
        - Root nodes are those left with primary_parent = None.
    """
    # Index nodes by prefix to keep comparisons local
    nodes_by_prefix = {}
    for n in nodes:
        nodes_by_prefix.setdefault(n["prefix"], []).append(n)

    for prefix, group in nodes_by_prefix.items():
        # For each node, find candidate parents
        for i, n in enumerate(group):
            cands = []
            for j, p in enumerate(group):
                if i == j:
                    continue
                if p["start"] <= n["start"] and p["end"] >= n["end"]:
                    cands.append(p)
            if cands:
                # Choose the tightest parent (minimal interval length)
                parent = min(cands, key=lambda c: c["end"] - c["start"])
                n["primary_parent"] = parent["id"]
                parent["children"].append(n["id"])


def outline_to_json_file(raw_text: str, output_path: str) -> List[Dict[str, Any]]:
    """
    Convenience wrapper: parse an OUTLINE string, build hierarchy, and write JSON.

    Returns the in-memory nodes list as well.
    """
    nodes = build_nodes(raw_text)
    assign_hierarchy(nodes)

    path = Path(output_path)
    path.write_text(json.dumps(nodes, indent=2), encoding="utf-8")

    # Optional: basic stats to log
    print("Wrote", len(nodes), "nodes to", output_path)
    print("By prefix:", Counter(n["prefix"] for n in nodes))
    roots = [n for n in nodes if n["primary_parent"] is None]
    print("Roots:", len(roots))
    for r in roots:
        print(r["id"], "-", r["label"])

    return nodes


# ---------- Example usage ----------

if __name__ == "__main__":
    # Example: paste an OUTLINE chunk for T (Technology) here,
    # or read from a local TXT file extracted from PDF.

    example_text = """
    T1-995 Technology (General)
    T10.5-11.9 Communication of technical information
    T55-55.3 Industrial safety. Industrial accident prevention
    T57-57.97 Applied mathematics. Quantitative methods
    T57.6-57.97 Operations research. Systems analysis
    TA1-2040 Engineering (General). Civil engineering (General)
    TA164 Bioengineering
    TA168 Systems engineering
    """  # Put the full outline here or read from file

    # Convert and write to JSON
    outline_to_json_file(example_text, "lcc_T_example_hierarchy.json")
