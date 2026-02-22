#!/usr/bin/env python3
"""
SCA Generic Traversal - Simple Runner with Progress

Just run this and watch the progress in the terminal!
Results save automatically.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from scripts.agents.sca_generic_traversal import GenericGraphTraversal


def main():
    """Run traversal with progress"""
    
    print("\n" + "="*80)
    print("SCA GENERIC GRAPH TRAVERSAL")
    print("="*80 + "\n")
    
    seed = input("Enter seed QID (default Q17167): ").strip() or "Q17167"
    
    max_entities_input = input("Max entities (default 5000): ").strip()
    max_entities = int(max_entities_input) if max_entities_input else 5000
    
    throttle_input = input("Throttle in seconds (default 1.0): ").strip()
    throttle = float(throttle_input) if throttle_input else 1.0
    
    print(f"\nStarting traversal...")
    print(f"  Seed: {seed}")
    print(f"  Max entities: {max_entities}")
    print(f"  Throttle: {throttle}s")
    print(f"  Estimated time: {max_entities * throttle / 3600:.1f} hours\n")
    
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Run traversal
    traversal = GenericGraphTraversal(seed, max_depth=3, max_entities=max_entities, throttle=throttle)
    output_path = traversal.traverse()
    
    print(f"\n✅ COMPLETE!")
    print(f"Results: {output_path}\n")


if __name__ == "__main__":
    main()
