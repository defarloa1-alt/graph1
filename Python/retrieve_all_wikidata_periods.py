#!/usr/bin/env python3
"""
Retrieve ALL Time Periods from Wikidata
Queries all 7 time period classes and exports to CSV for analysis/normalization
"""

import requests
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

# All time period classes to query
TIME_PERIOD_CLASSES = {
    "Q11514315": "historical period",
    "Q186081": "time interval",
    "Q573302": "era",
    "Q2164983": "historical era",
    "Q49848": "epoch",
    "Q3186692": "time period",
    "Q36507": "calendar era"
}


def _pick(*values: str) -> str:
    for v in values:
        if v and str(v).strip():
            return str(v).strip()
    return ""


def build_temporal_bbox(start_date: str = "", end_date: str = "") -> Dict[str, str]:
    """Normalize point or interval dates into a 4-point temporal envelope."""
    s_min = _pick(start_date)
    s_max = _pick(start_date)
    e_min = _pick(end_date)
    e_max = _pick(end_date)
    return {
        "start_date": _pick(start_date, s_min, s_max),
        "end_date": _pick(end_date, e_min, e_max),
        "start_date_min": s_min,
        "start_date_max": s_max,
        "end_date_min": e_min,
        "end_date_max": e_max,
        "earliest_start": s_min,
        "latest_start": s_max,
        "earliest_end": e_min,
        "latest_end": e_max,
    }

def query_wikidata(sparql: str, max_retries: int = 3) -> Dict:
    """Execute SPARQL query with retry logic."""
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "ChrystallumBot/1.0 (research project)"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                "https://query.wikidata.org/sparql",
                params={"query": sparql},
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                wait_time = (attempt + 1) * 10
                print(f"  [RATE LIMIT] Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  [ERROR] HTTP {response.status_code}: {response.reason}")
                time.sleep(5)
        
        except Exception as e:
            print(f"  [ERROR] {e}")
            time.sleep(5)
    
    return None

def retrieve_periods_for_class(class_qid: str, class_label: str) -> List[Dict]:
    """
    Retrieve all periods for a given Wikidata class.
    
    Returns:
        List of period dictionaries with all available properties
    """
    print(f"\n[{class_qid}] Querying: {class_label}")
    print("  This may take 30-60 seconds...")
    
    sparql = f"""
    SELECT DISTINCT 
      ?item ?itemLabel ?itemDescription
      ?start ?end ?inception ?dissolved ?pointInTime
      ?lcsh ?dewey ?lcc ?fast
      ?partOf ?partOfLabel
      ?follows ?followsLabel
      ?followedBy ?followedByLabel
      ?country ?countryLabel
      ?location ?locationLabel
    WHERE {{
      ?item wdt:P31 wd:{class_qid} .
      
      # Temporal properties
      OPTIONAL {{ ?item wdt:P580 ?start . }}
      OPTIONAL {{ ?item wdt:P582 ?end . }}
      OPTIONAL {{ ?item wdt:P571 ?inception . }}
      OPTIONAL {{ ?item wdt:P576 ?dissolved . }}
      OPTIONAL {{ ?item wdt:P585 ?pointInTime . }}
      
      # Classification IDs
      OPTIONAL {{ ?item wdt:P244 ?lcsh . }}
      OPTIONAL {{ ?item wdt:P1036 ?dewey . }}
      OPTIONAL {{ ?item wdt:P1149 ?lcc . }}
      OPTIONAL {{ ?item wdt:P2163 ?fast . }}
      
      # Relationships
      OPTIONAL {{ ?item wdt:P361 ?partOf . }}
      OPTIONAL {{ ?item wdt:P155 ?follows . }}
      OPTIONAL {{ ?item wdt:P156 ?followedBy . }}
      
      # Geographic
      OPTIONAL {{ ?item wdt:P17 ?country . }}
      OPTIONAL {{ ?item wdt:P276 ?location . }}
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    
    result = query_wikidata(sparql)
    if not result:
        print(f"  [FAILED] Could not retrieve data for {class_qid}")
        return []
    
    bindings = result.get("results", {}).get("bindings", [])
    print(f"  [SUCCESS] Found {len(bindings)} results")
    
    periods = []
    for b in bindings:
        # Extract QID
        qid = b.get('item', {}).get('value', '').split('/')[-1]
        
        # Extract LCSH ID from URI
        lcsh_uri = b.get('lcsh', {}).get('value', '')
        lcsh_id = lcsh_uri.split('/')[-1] if lcsh_uri else ''
        
        start_date = b.get('start', {}).get('value', '') or b.get('inception', {}).get('value', '')
        end_date = b.get('end', {}).get('value', '') or b.get('dissolved', {}).get('value', '')
        temporal = build_temporal_bbox(start_date=start_date, end_date=end_date)

        # Build period dictionary
        period = {
            'qid': qid,
            'class_qid': class_qid,
            'class_label': class_label,
            'label': b.get('itemLabel', {}).get('value', ''),
            'description': b.get('itemDescription', {}).get('value', ''),
            
            # Temporal envelope (4-point model + aliases)
            **temporal,
            'point_in_time': b.get('pointInTime', {}).get('value', ''),
            
            # Raw temporal fields (for analysis)
            'raw_start': b.get('start', {}).get('value', ''),
            'raw_end': b.get('end', {}).get('value', ''),
            'raw_inception': b.get('inception', {}).get('value', ''),
            'raw_dissolved': b.get('dissolved', {}).get('value', ''),
            
            # Classification
            'lcsh_id': lcsh_id,
            'dewey_decimal': b.get('dewey', {}).get('value', ''),
            'lcc_code': b.get('lcc', {}).get('value', ''),
            'fast_id': b.get('fast', {}).get('value', ''),
            
            # Relationships
            'part_of_qid': b.get('partOf', {}).get('value', '').split('/')[-1],
            'part_of_label': b.get('partOfLabel', {}).get('value', ''),
            'follows_qid': b.get('follows', {}).get('value', '').split('/')[-1],
            'follows_label': b.get('followsLabel', {}).get('value', ''),
            'followed_by_qid': b.get('followedBy', {}).get('value', '').split('/')[-1],
            'followed_by_label': b.get('followedByLabel', {}).get('value', ''),
            
            # Geographic
            'country_qid': b.get('country', {}).get('value', '').split('/')[-1],
            'country_label': b.get('countryLabel', {}).get('value', ''),
            'location_qid': b.get('location', {}).get('value', '').split('/')[-1],
            'location_label': b.get('locationLabel', {}).get('value', ''),
        }
        
        periods.append(period)
    
    return periods

def write_to_csv(all_periods: List[Dict], output_path: Path):
    """Write all periods to CSV file."""
    fieldnames = [
        'qid', 'class_qid', 'class_label', 'label', 'description',
        'start_date', 'end_date',
        'start_date_min', 'start_date_max', 'end_date_min', 'end_date_max',
        'earliest_start', 'latest_start', 'earliest_end', 'latest_end',
        'point_in_time',
        'raw_start', 'raw_end', 'raw_inception', 'raw_dissolved',
        'lcsh_id', 'dewey_decimal', 'lcc_code', 'fast_id',
        'part_of_qid', 'part_of_label',
        'follows_qid', 'follows_label',
        'followed_by_qid', 'followed_by_label',
        'country_qid', 'country_label',
        'location_qid', 'location_label'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_periods)
    
    print(f"\n[SUCCESS] Wrote {len(all_periods)} periods to:")
    print(f"  {output_path}")

def print_summary(all_periods: List[Dict]):
    """Print summary statistics."""
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    # By class
    print("\n[BY CLASS]")
    class_counts = {}
    for p in all_periods:
        cls = p['class_label']
        class_counts[cls] = class_counts.get(cls, 0) + 1
    
    for cls, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f"  {cls:30s}: {count:>6,}")
    
    # Temporal coverage
    print("\n[TEMPORAL COVERAGE]")
    with_start = sum(1 for p in all_periods if p['start_date'])
    with_end = sum(1 for p in all_periods if p['end_date'])
    with_point = sum(1 for p in all_periods if p['point_in_time'])
    total = len(all_periods)
    
    print(f"  With start date:    {with_start:>6,} ({with_start/total*100:.1f}%)")
    print(f"  With end date:      {with_end:>6,} ({with_end/total*100:.1f}%)")
    print(f"  With point in time: {with_point:>6,} ({with_point/total*100:.1f}%)")
    
    # Classification coverage
    print("\n[CLASSIFICATION COVERAGE]")
    with_lcsh = sum(1 for p in all_periods if p['lcsh_id'])
    with_dewey = sum(1 for p in all_periods if p['dewey_decimal'])
    with_lcc = sum(1 for p in all_periods if p['lcc_code'])
    with_fast = sum(1 for p in all_periods if p['fast_id'])
    
    print(f"  With LCSH (P244):   {with_lcsh:>6,} ({with_lcsh/total*100:.1f}%)")
    print(f"  With Dewey (P1036): {with_dewey:>6,} ({with_dewey/total*100:.1f}%)")
    print(f"  With LCC (P1149):   {with_lcc:>6,} ({with_lcc/total*100:.1f}%)")
    print(f"  With FAST (P2163):  {with_fast:>6,} ({with_fast/total*100:.1f}%)")
    
    # Hierarchy
    print("\n[HIERARCHY]")
    with_parent = sum(1 for p in all_periods if p['part_of_qid'])
    with_follows = sum(1 for p in all_periods if p['follows_qid'])
    with_followed_by = sum(1 for p in all_periods if p['followed_by_qid'])
    
    print(f"  With parent (part of): {with_parent:>6,} ({with_parent/total*100:.1f}%)")
    print(f"  With predecessor:      {with_follows:>6,} ({with_follows/total*100:.1f}%)")
    print(f"  With successor:        {with_followed_by:>6,} ({with_followed_by/total*100:.1f}%)")
    
    print("\n" + "="*80)

def main():
    """Main execution."""
    print("="*80)
    print("RETRIEVE ALL WIKIDATA TIME PERIODS")
    print("="*80)
    print(f"\nQuerying {len(TIME_PERIOD_CLASSES)} time period classes...")
    print("This will take 5-10 minutes total.\n")
    
    all_periods = []
    
    for class_qid, class_label in TIME_PERIOD_CLASSES.items():
        periods = retrieve_periods_for_class(class_qid, class_label)
        all_periods.extend(periods)
        
        # Rate limiting between classes
        print(f"  [WAITING] 5 seconds before next class...")
        time.sleep(5)
    
    # Remove duplicates by QID (some items may have multiple classes)
    seen_qids = set()
    unique_periods = []
    for period in all_periods:
        if period['qid'] not in seen_qids:
            seen_qids.add(period['qid'])
            unique_periods.append(period)
    
    print(f"\n[DEDUPLICATION] {len(all_periods)} results -> {len(unique_periods)} unique periods")
    
    # Write to CSV
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / "CSV" / "wikidata_all_periods_raw.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    write_to_csv(unique_periods, output_path)
    
    # Print summary
    print_summary(unique_periods)
    
    print("\n[NEXT STEP] Run normalize_periods.bat to clean and standardize this data")

if __name__ == "__main__":
    main()


