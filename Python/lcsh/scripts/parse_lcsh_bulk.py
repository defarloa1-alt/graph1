#!/usr/bin/env python3
"""
Parse LCSH Bulk Data from RDF N-Triples
Downloads and parses subjects.skosrdf.nt.gz from id.loc.gov
Extracts our 8 columns into CSV
"""

import gzip
import csv
import sys
import io
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import requests

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Download URL
# Note: LoC uses different filenames. Try these in order:
LCSH_BULK_URLS = [
    "https://id.loc.gov/download/vocabularysubjects.skosrdf.nt.zip",
    "https://id.loc.gov/download/vocabularysubjects.nt.gz",
    "https://id.loc.gov/download/vocabularysubjects.skosrdf.nt.gz",
    "https://id.loc.gov/static/data/vocabularysubjects.skosrdf.nt.gz",
]
LCSH_BULK_URL = LCSH_BULK_URLS[0]  # Try first one

# RDF predicates we care about
PREDICATES = {
    'label': '<http://www.w3.org/2004/02/skos/core#prefLabel>',
    'altLabel': '<http://www.w3.org/2004/02/skos/core#altLabel>',
    'broader': '<http://www.w3.org/2004/02/skos/core#broader>',
    'note': '<http://www.w3.org/2004/02/skos/core#note>',
    'closeMatch': '<http://www.w3.org/2004/02/skos/core#closeMatch>',
    'exactMatch': '<http://www.w3.org/2004/02/skos/core#exactMatch>',
}

def download_bulk_data(output_path: Path) -> bool:
    """Download LCSH bulk data file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print("="*80)
    print("DOWNLOADING LCSH BULK DATA")
    print("="*80)
    print(f"URL: {LCSH_BULK_URL}")
    print(f"Output: {output_path}")
    print()
    print("This file is ~800 MB. Download will take 5-15 minutes...")
    print()
    
    try:
        response = requests.get(LCSH_BULK_URL, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Progress bar
                    if total_size > 0:
                        progress = downloaded / total_size * 100
                        print(f"\r  Downloaded: {downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB ({progress:.1f}%)", end='')
        
        print()
        print()
        print("[SUCCESS] Download complete!")
        return True
    
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        return False

def parse_ntriple_line(line: str) -> tuple:
    """
    Parse a single N-Triple line.
    
    Format: <subject> <predicate> <object> .
    
    Returns:
        (subject_uri, predicate_uri, object_value)
    """
    # Remove trailing dot and newline
    line = line.strip().rstrip(' .')
    
    # Split into subject, predicate, object
    parts = line.split(' ', 2)
    if len(parts) < 3:
        return (None, None, None)
    
    subject = parts[0].strip('<>')
    predicate = parts[1]
    obj = parts[2]
    
    # Extract object value
    if obj.startswith('<'):
        # URI object
        obj_value = obj.strip('<>')
    elif obj.startswith('"'):
        # Literal object - extract the string value
        match = re.match(r'"(.+?)"(@[a-z]+)?(\^\^<.+>)?', obj)
        if match:
            obj_value = match.group(1)
        else:
            obj_value = obj
    else:
        obj_value = obj
    
    return (subject, predicate, obj_value)

def parse_bulk_data(gz_path: Path) -> Dict[str, Dict]:
    """
    Parse N-Triples file and extract subject data.
    
    Returns:
        Dictionary mapping lcsh_id to subject data
    """
    print("="*80)
    print("PARSING LCSH BULK DATA")
    print("="*80)
    print(f"Input: {gz_path}")
    print()
    print("Parsing ~450,000 subjects... This may take 5-10 minutes...")
    print()
    
    subjects = defaultdict(lambda: {
        'lcsh_id': '',
        'label': '',
        'dewey_decimal': '',
        'lcc_code': '',
        'fast_id': '',
        'broader_lcsh': '',
        'scope_note': '',
        'uri': ''
    })
    
    line_count = 0
    subject_count = 0
    
    with gzip.open(gz_path, 'rt', encoding='utf-8') as f:
        for line in f:
            line_count += 1
            
            # Progress indicator
            if line_count % 1000000 == 0:
                print(f"  Processed {line_count / 1000000:.1f}M lines, found {len(subjects):,} subjects...")
            
            subject_uri, predicate, obj_value = parse_ntriple_line(line)
            
            if not subject_uri or not predicate:
                continue
            
            # Only process LCSH subjects (starting with sh)
            if '/subjects/sh' not in subject_uri:
                continue
            
            # Extract LCSH ID
            lcsh_id = subject_uri.split('/')[-1]
            
            # Store URI
            if not subjects[lcsh_id]['uri']:
                subjects[lcsh_id]['uri'] = subject_uri
                subjects[lcsh_id]['lcsh_id'] = lcsh_id
            
            # Extract data based on predicate
            if predicate == PREDICATES['label']:
                subjects[lcsh_id]['label'] = obj_value
            
            elif predicate == PREDICATES['broader']:
                broader_id = obj_value.split('/')[-1]
                if broader_id.startswith('sh'):
                    subjects[lcsh_id]['broader_lcsh'] = broader_id
            
            elif predicate == PREDICATES['note']:
                subjects[lcsh_id]['scope_note'] = obj_value
            
            elif predicate in [PREDICATES['closeMatch'], PREDICATES['exactMatch']]:
                # Check for Dewey, FAST, LCC
                if 'dewey.info' in obj_value:
                    subjects[lcsh_id]['dewey_decimal'] = obj_value.split('/')[-1]
                elif 'id.worldcat.org/fast' in obj_value:
                    subjects[lcsh_id]['fast_id'] = obj_value.split('/')[-1]
                elif 'id.loc.gov/authorities/classification' in obj_value:
                    subjects[lcsh_id]['lcc_code'] = obj_value.split('/')[-1]
    
    print()
    print(f"[SUCCESS] Parsed {line_count:,} lines")
    print(f"[SUCCESS] Found {len(subjects):,} LCSH subjects")
    print()
    
    return dict(subjects)

def write_subjects_csv(subjects: Dict[str, Dict], output_path: Path):
    """Write subjects to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print("="*80)
    print("WRITING CSV OUTPUT")
    print("="*80)
    print(f"Output: {output_path}")
    print()
    
    fieldnames = ['lcsh_id', 'label', 'dewey_decimal', 'lcc_code', 'fast_id', 
                  'broader_lcsh', 'scope_note', 'uri']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for subject in subjects.values():
            writer.writerow(subject)
    
    print(f"[SUCCESS] Wrote {len(subjects):,} subjects to CSV")
    print()
    
    # Statistics
    with_label = sum(1 for s in subjects.values() if s['label'])
    with_dewey = sum(1 for s in subjects.values() if s['dewey_decimal'])
    with_lcc = sum(1 for s in subjects.values() if s['lcc_code'])
    with_fast = sum(1 for s in subjects.values() if s['fast_id'])
    with_broader = sum(1 for s in subjects.values() if s['broader_lcsh'])
    
    total = len(subjects)
    
    print("[STATISTICS]")
    print(f"  Total subjects:   {total:>8,}")
    print(f"  With label:       {with_label:>8,} ({with_label/total*100:.1f}%)")
    print(f"  With Dewey:       {with_dewey:>8,} ({with_dewey/total*100:.1f}%)")
    print(f"  With LCC:         {with_lcc:>8,} ({with_lcc/total*100:.1f}%)")
    print(f"  With FAST:        {with_fast:>8,} ({with_fast/total*100:.1f}%)")
    print(f"  With broader:     {with_broader:>8,} ({with_broader/total*100:.1f}%)")
    print()
    print("="*80)

def main():
    """Main execution."""
    script_dir = Path(__file__).parent.parent

    # Paths
    gz_path = script_dir / "key" / "subjects.skosrdf.nt.gz"
    csv_path = script_dir / "output" / "lcsh_subjects_complete.csv"
    
    # Step 1: Download if not exists
    if not gz_path.exists():
        print(f"[INFO] Bulk data not found locally")
        if not download_bulk_data(gz_path):
            print("[ERROR] Download failed!")
            sys.exit(1)
    else:
        print(f"[INFO] Using existing bulk data: {gz_path}")
        print()
    
    # Step 2: Parse RDF data
    subjects = parse_bulk_data(gz_path)
    
    # Step 3: Write to CSV
    write_subjects_csv(subjects, csv_path)
    
    print("[NEXT STEP] Run import_lcsh_to_neo4j.py to load into database")

if __name__ == "__main__":
    main()

