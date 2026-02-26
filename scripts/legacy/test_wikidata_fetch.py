#!/usr/bin/env python3
"""
Quick Test Script for Wikidata Full Fetch

Run this to test the Wikidata fetcher before using the Gradio UI
"""

from scripts.agents.wikidata_full_fetch import WikidataFullFetcher, test_fetch_qid
import sys


def main():
    print("=" * 80)
    print("WIKIDATA FULL FETCH - QUICK TEST")
    print("=" * 80)
    print()
    
    # Get QID from command line or use default
    if len(sys.argv) > 1:
        qid = sys.argv[1]
    else:
        qid = 'Q17167'  # Roman Republic
        print(f"No QID provided, using default: {qid} (Roman Republic)")
        print("Usage: python test_wikidata_fetch.py Q12345")
        print()
    
    # Run test
    data = test_fetch_qid(qid)
    
    if data:
        print("\n" + "=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Check the saved JSON file in: output/wikidata/")
        print("2. Try the Gradio UI: python scripts/ui/test_wikidata_fetch_ui.py")
        print()
        print("Try other QIDs:")
        print("  - Q1048 (Julius Caesar)")
        print("  - Q1747689 (Ancient Rome)")
        print("  - Q842606 (Second Punic War)")
    else:
        print("\n" + "=" * 80)
        print("FAILED")
        print("=" * 80)
        print()
        print("Check the error message above")
        sys.exit(1)


if __name__ == "__main__":
    main()
