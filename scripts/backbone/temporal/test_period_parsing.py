#!/usr/bin/env python3
"""Quick test to verify period parsing works."""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.backbone.temporal.enrich_periods_with_perplexity import parse_periods_from_cypher

def main():
    input_file = "Subjects/periods_import.cypher"
    
    print("Testing period parsing...")
    print(f"File: {input_file}")
    print()
    
    try:
        periods = parse_periods_from_cypher(input_file)
        print(f"✅ Successfully parsed {len(periods)} periods")
        print()
        print("Sample periods:")
        for i, p in enumerate(periods[:5], 1):
            print(f"  {i}. {p['label']}")
            print(f"     QID: {p['qid'][-15:]}")
            if p.get('start_year'):
                print(f"     Years: {p['start_year']}", end='')
                if p.get('end_year'):
                    print(f" - {p['end_year']}")
                else:
                    print()
            if p.get('current_facet'):
                print(f"     Current facet: {p['current_facet']}")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

