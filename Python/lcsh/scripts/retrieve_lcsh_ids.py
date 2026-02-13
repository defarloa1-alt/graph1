#!/usr/bin/env python3
"""
Retrieve ALL LCSH Subject Headings from Library of Congress
Step 1: Get list of all LCSH identifiers
"""

import requests
import json
import time
import sys
import io
from pathlib import Path
from typing import List, Dict

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_lcsh_list() -> List[str]:
    """
    Get list of all LCSH subject identifiers.
    
    The LoC provides a suggest API that can help discover subjects,
    but for complete retrieval, we'll use their bulk data listing.
    
    Returns:
        List of LCSH IDs (e.g., ["sh85115114", "sh85085133", ...])
    """
    print("="*80)
    print("RETRIEVING LCSH IDENTIFIER LIST")
    print("="*80)
    print()
    print("Note: The Library of Congress has ~450,000 subject headings.")
    print("This script will retrieve a starter set for historical subjects.")
    print()
    
    # For now, we'll use a targeted approach:
    # Query the suggest API with common history-related terms
    # to build an initial list
    
    history_terms = [
        "Rome", "Greece", "Ancient", "History", "War", "Empire", 
        "Republic", "Kingdom", "Dynasty", "Period", "Age", "Era",
        "Medieval", "Renaissance", "Modern", "Century",
        "Egypt", "Mesopotamia", "China", "Europe", "Asia",
        "Battle", "Revolution", "Civilization"
    ]
    
    all_subjects = set()
    
    for term in history_terms:
        print(f"Querying suggestions for: {term}")
        
        url = f"https://id.loc.gov/authorities/subjects/suggest/?q={term}"
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                # Suggest API returns: [query, [labels], [ids], [uris]]
                if len(data) >= 4:
                    uris = data[3]
                    for uri in uris:
                        # Extract ID from URI
                        lcsh_id = uri.split('/')[-1]
                        if lcsh_id.startswith('sh'):
                            all_subjects.add(lcsh_id)
                    print(f"  Found {len(uris)} suggestions")
            else:
                print(f"  [WARNING] HTTP {response.status_code}")
        
        except Exception as e:
            print(f"  [ERROR] {e}")
        
        time.sleep(1)  # Rate limiting
    
    print()
    print(f"[SUCCESS] Found {len(all_subjects)} unique LCSH subjects")
    
    return sorted(list(all_subjects))

def save_id_list(lcsh_ids: List[str], output_path: Path):
    """Save list of LCSH IDs to file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for lcsh_id in lcsh_ids:
            f.write(f"{lcsh_id}\n")
    
    print(f"\n[SAVED] LCSH ID list to: {output_path}")

def main():
    """Main execution."""
    lcsh_ids = get_lcsh_list()
    
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / "output" / "lcsh_ids.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_id_list(lcsh_ids, output_path)
    
    print()
    print("="*80)
    print("NEXT STEP")
    print("="*80)
    print(f"Total subjects discovered: {len(lcsh_ids)}")
    print()
    print("This is a starter set. For complete LCSH coverage, you can:")
    print("1. Download bulk data from: https://id.loc.gov/download/")
    print("2. Run: retrieve_lcsh_details.py to fetch JSON for each subject")
    print()
    print(f"ID list saved to: {output_path}")

if __name__ == "__main__":
    main()


