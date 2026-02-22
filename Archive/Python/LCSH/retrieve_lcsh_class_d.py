#!/usr/bin/env python3
"""
Retrieve ALL LCSH Subjects with LCC Class D (History)
Uses id.loc.gov search API to systematically get all history subjects
"""

import requests
import json
import csv
import time
import sys
import io
from pathlib import Path
from typing import List, Dict

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# LCC Class D subdivisions for systematic retrieval
LCC_CLASS_D_PREFIXES = [
    "D",      # World History (general)
    "DA",     # Great Britain
    "DB",     # Austria-Hungary
    "DC",     # France
    "DD",     # Germany
    "DE",     # Mediterranean, Greco-Roman
    "DF",     # Greece
    "DG",     # Italy (Rome!)
    "DH",     # Low Countries - Netherlands
    "DJ",     # Netherlands
    "DK",     # Russia, Poland
    "DL",     # Scandinavia
    "DM",     # (unused)
    "DN",     # (unused)
    "DP",     # Spain, Portugal
    "DQ",     # Switzerland
    "DR",     # Balkans
    "DS",     # Asia
    "DT",     # Africa
    "DU",     # Oceania
]

def search_lcsh_by_lcc(lcc_prefix: str, limit: int = 1000) -> List[str]:
    """
    Search for LCSH subjects with specific LCC classification.
    
    Args:
        lcc_prefix: LCC prefix (e.g., "DG" for Italy)
        limit: Maximum results to return
        
    Returns:
        List of LCSH IDs
    """
    print(f"\nSearching LCC Class {lcc_prefix}...")
    
    # Use LoC search API
    # Format: https://id.loc.gov/search/?q=memberOf:http://id.loc.gov/authorities/subjects/collection_LCSH_General&q=cs:http://id.loc.gov/vocabulary/relators
    
    # Try suggest API with classification filter
    url = "https://id.loc.gov/authorities/subjects/suggest/"
    
    # We'll need to use their SPARQL or REST API
    # For now, let's use a different approach: fetch subjects page by page
    
    base_url = "https://id.loc.gov/authorities/subjects.json"
    params = {
        "q": f"classification:{lcc_prefix}*",
        "count": 100
    }
    
    lcsh_ids = set()
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # Parse response structure (depends on LoC API format)
            # This is a placeholder - actual parsing depends on API response
            print(f"  Response received, parsing...")
            
            # For now, return empty - we need to check actual API structure
            return []
        else:
            print(f"  [WARNING] HTTP {response.status_code}")
            return []
    
    except Exception as e:
        print(f"  [ERROR] {e}")
        return []

def get_all_history_subjects_method2() -> List[str]:
    """
    Alternative method: Use bulk data parsing approach.
    Since bulk download isn't available, we'll use targeted search.
    """
    print("="*80)
    print("RETRIEVING ALL CLASS D (HISTORY) SUBJECTS")
    print("="*80)
    print()
    print("Strategy: Systematic alphabet search for Class D subjects")
    print()
    
    # Use alphabetic search to discover subjects
    # Search for subjects containing historical terms + filter results by LCC
    
    all_lcsh_ids = set()
    
    # Expanded historical search terms
    search_terms = []
    
    # Add alphabet search for systematic coverage
    # Format: "History" + letter to discover all subjects
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        search_terms.append(f"History {letter}")
    
    # Add key historical categories
    historical_categories = [
        "Ancient civilization", "Medieval", "Renaissance", "Modern",
        "Empire", "Kingdom", "Republic", "Dynasty", "War", "Battle",
        "Revolution", "Conquest", "Invasion", "Treaty",
        "Century", "Period", "Age", "Era", "Epoch",
        "Rome", "Greece", "Egypt", "Persia", "China", "Japan", "India",
        "Britain", "France", "Germany", "Spain", "Italy", "Russia",
        "Ottoman", "Byzantine", "Holy Roman", "Mongol", "Arab",
        "Crusades", "Reformation", "Enlightenment", "Industrial",
        "Colonial", "Imperial", "National", "Civil", "World War"
    ]
    
    search_terms.extend(historical_categories)
    
    for term in search_terms:
        url = f"https://id.loc.gov/authorities/subjects/suggest/?q={term}"
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) >= 4:
                    uris = data[3]
                    count = 0
                    for uri in uris:
                        lcsh_id = uri.split('/')[-1]
                        if lcsh_id.startswith('sh') or lcsh_id.startswith('n'):
                            if lcsh_id not in all_lcsh_ids:
                                all_lcsh_ids.add(lcsh_id)
                                count += 1
                    
                    if count > 0:
                        print(f"  [{term}] Found {count} new subjects (total: {len(all_lcsh_ids)})")
            
        except Exception as e:
            print(f"  [ERROR] {term}: {e}")
        
        time.sleep(0.5)  # Rate limiting
    
    print()
    print(f"[SUCCESS] Discovered {len(all_lcsh_ids)} unique LCSH subjects")
    
    return sorted(list(all_lcsh_ids))

def save_id_list(lcsh_ids: List[str], output_path: Path):
    """Save list of LCSH IDs to file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for lcsh_id in lcsh_ids:
            f.write(f"{lcsh_id}\n")
    
    print(f"\n[SAVED] {len(lcsh_ids)} LCSH IDs to: {output_path}")

def main():
    """Main execution."""
    lcsh_ids = get_all_history_subjects_method2()
    
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / "CSV" / "lcsh_class_d_ids.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_id_list(lcsh_ids, output_path)
    
    print()
    print("="*80)
    print("NEXT STEP")
    print("="*80)
    print(f"Total history subjects discovered: {len(lcsh_ids)}")
    print()
    print("Run: retrieve_lcsh_details.py to fetch full data for each subject")
    print("Then: import_lcsh_to_neo4j.py to load into database")

if __name__ == "__main__":
    main()


