#!/usr/bin/env python3
"""
Retrieve Full LCSH Details for Each Subject
Step 2: Fetch JSON data from id.loc.gov for each LCSH ID
"""

import requests
import json
import csv
import time
import sys
import io
from pathlib import Path
from typing import Dict, Optional

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def fetch_lcsh_json(lcsh_id: str, max_retries: int = 3) -> Optional[Dict]:
    """
    Fetch full JSON data for a single LCSH subject.
    
    Args:
        lcsh_id: LCSH identifier (e.g., "sh85115114")
        max_retries: Number of retry attempts
        
    Returns:
        Parsed JSON data or None if failed
    """
    url = f"https://id.loc.gov/authorities/subjects/{lcsh_id}.json"
    headers = {"Accept": "application/json"}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None  # Subject doesn't exist
            elif response.status_code == 429:
                wait = (attempt + 1) * 5
                print(f"    [RATE LIMIT] Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    [WARNING] HTTP {response.status_code}")
                time.sleep(2)
        
        except Exception as e:
            print(f"    [ERROR] {e}")
            time.sleep(2)
    
    return None

def extract_lcsh_data(json_data: Dict) -> Dict:
    """
    Extract our 8 columns from LCSH JSON.
    
    Returns:
        Dictionary with: lcsh_id, label, dewey_decimal, lcc_code, 
                        fast_id, broader_lcsh, scope_note, uri
    """
    # Get the main resource (first item in array)
    if isinstance(json_data, list) and len(json_data) > 0:
        resource = json_data[0]
    else:
        resource = json_data
    
    # Extract URI and ID
    uri = resource.get('@id', '')
    lcsh_id = uri.split('/')[-1] if uri else ''
    
    # Extract label
    label = ''
    if 'http://www.loc.gov/mads/rdf/v1#authoritativeLabel' in resource:
        labels = resource['http://www.loc.gov/mads/rdf/v1#authoritativeLabel']
        if isinstance(labels, list) and len(labels) > 0:
            label = labels[0].get('@value', '')
        elif isinstance(labels, dict):
            label = labels.get('@value', '')
    
    # Extract scope note
    scope_note = ''
    if 'http://www.w3.org/2004/02/skos/core#note' in resource:
        notes = resource['http://www.w3.org/2004/02/skos/core#note']
        if isinstance(notes, list) and len(notes) > 0:
            scope_note = notes[0].get('@value', '')
        elif isinstance(notes, dict):
            scope_note = notes.get('@value', '')
    
    # Extract broader subject
    broader_lcsh = ''
    if 'http://www.w3.org/2004/02/skos/core#broader' in resource:
        broader = resource['http://www.w3.org/2004/02/skos/core#broader']
        if isinstance(broader, list) and len(broader) > 0:
            broader_uri = broader[0].get('@id', '')
        elif isinstance(broader, dict):
            broader_uri = broader.get('@id', '')
        else:
            broader_uri = ''
        broader_lcsh = broader_uri.split('/')[-1] if broader_uri else ''
    
    # Extract external identifiers (Dewey, LCC, FAST)
    dewey_decimal = ''
    lcc_code = ''
    fast_id = ''
    
    if 'http://www.w3.org/2004/02/skos/core#closeMatch' in resource:
        matches = resource['http://www.w3.org/2004/02/skos/core#closeMatch']
        if not isinstance(matches, list):
            matches = [matches]
        
        for match in matches:
            match_uri = match.get('@id', '')
            
            if 'dewey.info' in match_uri:
                dewey_decimal = match_uri.split('/')[-1]
            elif 'id.worldcat.org/fast' in match_uri:
                fast_id = match_uri.split('/')[-1]
            elif 'id.loc.gov/authorities/classification' in match_uri:
                lcc_code = match_uri.split('/')[-1]
    
    return {
        'lcsh_id': lcsh_id,
        'label': label,
        'dewey_decimal': dewey_decimal,
        'lcc_code': lcc_code,
        'fast_id': fast_id,
        'broader_lcsh': broader_lcsh,
        'scope_note': scope_note,
        'uri': uri
    }

def retrieve_all_subjects(id_list_path: Path, output_path: Path):
    """Retrieve full data for all LCSH subjects."""
    print("="*80)
    print("RETRIEVING LCSH SUBJECT DETAILS")
    print("="*80)
    print()
    
    # Read ID list
    with open(id_list_path, 'r', encoding='utf-8') as f:
        lcsh_ids = [line.strip() for line in f if line.strip()]
    
    print(f"[INPUT] Reading {len(lcsh_ids)} LCSH IDs from: {id_list_path}")
    print(f"[OUTPUT] Will write to: {output_path}")
    print()
    print("This will take approximately {} minutes...".format(len(lcsh_ids) // 10))
    print()
    
    all_subjects = []
    failed = []
    
    for i, lcsh_id in enumerate(lcsh_ids, 1):
        print(f"[{i}/{len(lcsh_ids)}] Fetching {lcsh_id}...", end=' ')
        
        json_data = fetch_lcsh_json(lcsh_id)
        
        if json_data:
            try:
                subject_data = extract_lcsh_data(json_data)
                all_subjects.append(subject_data)
                print(f"[OK] {subject_data['label'][:50]}...")
            except Exception as e:
                print(f"[PARSE ERROR] {e}")
                failed.append(lcsh_id)
        else:
            print("[NOT FOUND]")
            failed.append(lcsh_id)
        
        # Rate limiting
        time.sleep(0.5)
        
        # Progress checkpoint every 100
        if i % 100 == 0:
            print()
            print(f"  Progress: {i}/{len(lcsh_ids)} ({i/len(lcsh_ids)*100:.1f}%)")
            print(f"  Success: {len(all_subjects)}, Failed: {len(failed)}")
            print()
    
    # Write to CSV
    fieldnames = ['lcsh_id', 'label', 'dewey_decimal', 'lcc_code', 'fast_id', 
                  'broader_lcsh', 'scope_note', 'uri']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_subjects)
    
    # Summary
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total requested: {len(lcsh_ids)}")
    print(f"Successfully retrieved: {len(all_subjects)}")
    print(f"Failed: {len(failed)}")
    print()
    
    # Statistics
    with_dewey = sum(1 for s in all_subjects if s['dewey_decimal'])
    with_lcc = sum(1 for s in all_subjects if s['lcc_code'])
    with_fast = sum(1 for s in all_subjects if s['fast_id'])
    with_broader = sum(1 for s in all_subjects if s['broader_lcsh'])
    
    print("[CLASSIFICATION COVERAGE]")
    print(f"  With Dewey:   {with_dewey:>5} ({with_dewey/len(all_subjects)*100:.1f}%)")
    print(f"  With LCC:     {with_lcc:>5} ({with_lcc/len(all_subjects)*100:.1f}%)")
    print(f"  With FAST:    {with_fast:>5} ({with_fast/len(all_subjects)*100:.1f}%)")
    print(f"  With broader: {with_broader:>5} ({with_broader/len(all_subjects)*100:.1f}%)")
    print()
    print(f"[OUTPUT] {output_path}")
    print()
    print("="*80)

def main():
    """Main execution."""
    script_dir = Path(__file__).parent.parent
    id_list_path = script_dir / "output" / "lcsh_ids.txt"
    output_path = script_dir / "output" / "lcsh_subjects_complete.csv"
    
    if not id_list_path.exists():
        print(f"[ERROR] ID list not found: {id_list_path}")
        print("Run retrieve_lcsh_ids.py first.")
        sys.exit(1)
    
    retrieve_all_subjects(id_list_path, output_path)
    
    print("[NEXT STEP] Run import_lcsh_to_neo4j.py to load into database")

if __name__ == "__main__":
    main()


