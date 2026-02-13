# LCC Outline Parser Script

Save this as `parse_lcc_outline.py`:

```python
#!/usr/bin/env python3
"""
LCC Outline Parser

Parses Library of Congress Classification (LCC) outlines into hierarchical JSON.
Handles range notation, builds parent-child relationships via containment logic.

Usage:
    python parse_lcc_outline.py input.txt -o output.json --validate --verbose

Author: Generated for LCC hierarchy processing
Date: February 4, 2026
"""

import re
import json
import argparse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class LCCNode:
    """Represents a single LCC classification node."""
    id: str
    code: str
    prefix: str
    start: float
    end: float
    label: str
    note: Optional[str]
    primary_parent: Optional[str]
    secondary_parents: List[str]
    children: List[str]
    depth: int
    child_count: int


def parse_lcc_range(code: str) -> Optional[Tuple[str, float, float]]:
    """
    Parse an LCC range into (prefix, start, end).
    
    Handles:
    - Simple ranges: DS1-937
    - Decimal ranges: DS5.95-10
    - Parenthesized: D(204)-(475)
    - Cutter notation: DT469.M21-.M38
    - Single codes: DS11
    
    Returns:
        (prefix, start_num, end_num) or None if unparseable
    """
    code = code.strip()
    
    # Remove parentheses: D(204)-(475) -> D204-475
    code = re.sub(r'\((\d+)\)', r'\1', code)
    
    # Pattern 1: Range with dash (DS1-937, DS5.95-10)
    match = re.match(r'^([A-Z]+)([\d.]+)-([\d.]+)$', code)
    if match:
        prefix, start_str, end_str = match.groups()
        return (prefix, float(start_str), float(end_str))
    
    # Pattern 2: Cutter notation (DT469.M21-.M38)
    match = re.match(r'^([A-Z]+)([\d.]+)\.([A-Z])(\d+)-\.([A-Z])(\d+)$', code)
    if match:
        prefix, base, letter1, num1, letter2, num2 = match.groups()
        # Convert Cutter to decimal: M21 -> .21, M38 -> .38
        start = float(base) + float(f"0.{num1}")
        end = float(base) + float(f"0.{num2}")
        return (prefix, start, end)
    
    # Pattern 3: Single code (DS11)
    match = re.match(r'^([A-Z]+)([\d.]+)$', code)
    if match:
        prefix, num_str = match.groups()
        num = float(num_str)
        return (prefix, num, num)
    
    return None


def build_hierarchy(entries: List[Dict]) -> List[LCCNode]:
    """
    Build parent-child relationships via range containment.
    
    Algorithm:
    1. Group by prefix
    2. Sort by start, then by end descending (larger ranges first)
    3. For each entry, find narrowest containing parent
    4. Build children arrays
    5. Calculate depth from roots
    """
    nodes = []
    
    # Create nodes with parsed ranges
    for entry in entries:
        parsed = parse_lcc_range(entry['code'])
        if not parsed:
            print(f"Warning: Could not parse code '{entry['code']}' - skipping")
            continue
        
        prefix, start, end = parsed
        node = LCCNode(
            id=entry['code'],
            code=entry['code'],
            prefix=prefix,
            start=start,
            end=end,
            label=entry['label'],
            note=entry.get('note'),
            primary_parent=None,
            secondary_parents=[],
            children=[],
            depth=0,
            child_count=0
        )
        nodes.append(node)
    
    # Group by prefix for efficient containment checks
    by_prefix = {}
    for node in nodes:
        by_prefix.setdefault(node.prefix, []).append(node)
    
    # Sort each prefix group: by start asc, then by end desc (larger ranges first)
    for prefix in by_prefix:
        by_prefix[prefix].sort(key=lambda n: (n.start, -n.end))
    
    # Assign parents via containment
    for prefix, prefix_nodes in by_prefix.items():
        for i, node in enumerate(prefix_nodes):
            # Find narrowest containing parent among earlier nodes
            best_parent = None
            best_width = float('inf')
            
            for j in range(i):
                candidate = prefix_nodes[j]
                # Check if candidate contains node
                if candidate.start <= node.start and node.end <= candidate.end:
                    # Avoid self-assignment
                    if candidate.code == node.code:
                        continue
                    # Choose narrowest
                    width = candidate.end - candidate.start
                    if width < best_width:
                        best_parent = candidate
                        best_width = width
            
            if best_parent:
                node.primary_parent = best_parent.id
    
    # Build children arrays
    parent_to_children = {}
    for node in nodes:
        if node.primary_parent:
            parent_to_children.setdefault(node.primary_parent, []).append(node.id)
    
    for node in nodes:
        node.children = parent_to_children.get(node.id, [])
        node.child_count = len(node.children)
    
    # Calculate depth from roots
    def set_depth(node_id: str, current_depth: int):
        node = next((n for n in nodes if n.id == node_id), None)
        if node:
            node.depth = current_depth
            for child_id in node.children:
                set_depth(child_id, current_depth + 1)
    
    # Start from roots (nodes with no parent)
    for node in nodes:
        if node.primary_parent is None:
            set_depth(node.id, 0)
    
    return nodes


def validate_hierarchy(nodes: List[LCCNode]) -> List[str]:
    """
    Validate hierarchy structure.
    
    Checks:
    - No orphaned parent references
    - No cycles
    - Children arrays consistent with parent relationships
    - Depth values consistent
    """
    errors = []
    node_ids = {n.id for n in nodes}
    
    # Check 1: No orphaned parents
    for node in nodes:
        if node.primary_parent and node.primary_parent not in node_ids:
            errors.append(f"Orphaned parent: {node.id} → {node.primary_parent}")
    
    # Check 2: Children arrays match parent relationships
    parent_children_map = {}
    for node in nodes:
        if node.primary_parent:
            parent_children_map.setdefault(node.primary_parent, []).append(node.id)
    
    for node in nodes:
        expected_children = set(parent_children_map.get(node.id, []))
        actual_children = set(node.children)
        if expected_children != actual_children:
            errors.append(f"Children mismatch for {node.id}: expected {expected_children}, got {actual_children}")
    
    # Check 3: Depth consistency
    for node in nodes:
        if node.primary_parent:
            parent = next((n for n in nodes if n.id == node.primary_parent), None)
            if parent and node.depth != parent.depth + 1:
                errors.append(f"Depth inconsistency: {node.id} (depth {node.depth}) → parent {parent.id} (depth {parent.depth})")
    
    # Check 4: No cycles (depth should be set for all nodes)
    for node in nodes:
        if node.depth < 0:
            errors.append(f"Node {node.id} has invalid depth {node.depth} (possible cycle)")
    
    return errors


def parse_outline_file(filepath: str) -> List[Dict]:
    """
    Parse LCC outline text file into list of entries.
    
    Expected format:
        DS1-937     History of Asia
        DS5.95-10     Description and travel
        DS11          Antiquities
    
    Returns list of dicts with 'code' and 'label' keys.
    """
    entries = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Split on whitespace, code is first token, rest is label
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            
            code, label = parts
            entries.append({'code': code, 'label': label})
    
    return entries


def main():
    parser = argparse.ArgumentParser(
        description='Parse LCC outline into hierarchical JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python parse_lcc_outline.py input.txt -o output.json
  python parse_lcc_outline.py input.txt -o output.json --validate --verbose
        '''
    )
    parser.add_argument('input', help='Input text file with LCC outline')
    parser.add_argument('-o', '--output', required=True, help='Output JSON file')
    parser.add_argument('--validate', action='store_true', help='Validate hierarchy structure')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print statistics')
    
    args = parser.parse_args()
    
    # Parse input
    print(f"Parsing {args.input}...")
    entries = parse_outline_file(args.input)
    print(f"Found {len(entries)} entries")
    
    # Build hierarchy
    print("Building hierarchy...")
    nodes = build_hierarchy(entries)
    print(f"Created {len(nodes)} nodes")
    
    # Validate
    if args.validate:
        print("Validating structure...")
        errors = validate_hierarchy(nodes)
        if errors:
            print(f"⚠️  Found {len(errors)} validation errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✅ Validation passed")
    
    # Statistics
    if args.verbose:
        roots = [n for n in nodes if n.primary_parent is None]
        max_depth = max(n.depth for n in nodes)
        prefixes = sorted(set(n.prefix for n in nodes))
        
        print(f"\nStatistics:")
        print(f"  Roots: {len(roots)}")
        for root in roots:
            print(f"    - {root.code}: {root.label} ({root.child_count} children)")
        print(f"  Max depth: {max_depth}")
        print(f"  Prefixes: {', '.join(prefixes)}")
        
        # Per-prefix breakdown
        print(f"\n  Nodes by prefix:")
        for prefix in prefixes:
            count = sum(1 for n in nodes if n.prefix == prefix)
            print(f"    {prefix}: {count}")
    
    # Write output
    print(f"\nWriting {args.output}...")
    output_data = [asdict(node) for node in nodes]
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Done! Wrote {len(nodes)} nodes to {args.output}")


if __name__ == '__main__':
    main()
```

Save this as a `.py` file and make it executable with `chmod +x parse_lcc_outline.py`
