#!/usr/bin/env python3
"""
Generate Historical Periods Taxonomy from Wikidata

Queries Wikidata by Dewey Decimal Classification ranges (930-999 History),
fetches ALL classification IDs (LCSH, Dewey, LCC, FAST) in single SPARQL query.
Generates comprehensive historical_periods_taxonomy.csv.

NEW ARCHITECTURE (Dec 2025):
- LCSH (P244) as primary backbone identifier
- Dewey Decimal (P1036) for agent routing
- LCC (P1149) for hierarchical classification
- FAST (P2163) as supplementary property

Usage:
    python generate_period_taxonomy.py [--output OUTPUT_FILE] [--dewey-min MIN] [--dewey-max MAX]
"""

import sys
import io
import csv
import time
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Optional

from temporal_bounds import build_temporal_bbox

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
DEFAULT_OUTPUT = "../../data/backbone/temporal/historical_periods_taxonomy.csv"

# Dewey ranges for History (930-999)
DEWEY_RANGES = [
    (930, 939),  # Ancient world
    (940, 949),  # Europe
    (950, 959),  # Asia
    (960, 969),  # Africa
    (970, 979),  # North America
    (980, 989),  # South America
    (990, 999),  # Other areas
]

def query_wikidata(sparql: str, max_retries: int = 3, delay: float = 1.0) -> Optional[Dict]:
    """
    Query Wikidata SPARQL endpoint with retry logic and rate limiting.
    
    Args:
        sparql: SPARQL query string
        max_retries: Maximum number of retry attempts
        delay: Delay between retries (seconds)
        
    Returns:
        JSON response data or None if all retries fail
    """
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "ChrystallumBot/1.0 (federated-graph-framework; research project)"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                WIKIDATA_ENDPOINT,
                params={"query": sparql, "format": "json"},
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limited
                wait_time = delay * (2 ** attempt)
                print(f"  ⚠️  Rate limited. Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
                continue
            else:
                print(f"  ❌ Error {response.status_code}: {response.reason}")
                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))
                    
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request error: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
    
    return None

def query_periods_by_dewey_range(dewey_min: int, dewey_max: int) -> List[Dict]:
    """
    Query Wikidata for historical periods in a Dewey Decimal range.
    
    Fetches ALL classification IDs (LCSH, Dewey, LCC, FAST) in one query.
    
    Args:
        dewey_min: Minimum Dewey code (e.g., 930)
        dewey_max: Maximum Dewey code (e.g., 939)
        
    Returns:
        List of period dictionaries with all classification metadata
    """
    sparql = f"""
    SELECT DISTINCT 
      ?item ?itemLabel ?itemDescription
      ?start ?end ?inception ?dissolved
      ?dewey ?lcsh ?lcc ?fast
      ?country ?countryLabel
      ?region ?regionLabel
    WHERE {{
      # Must be a historical period (instance of Q186081 or subclass)
      ?item wdt:P31/wdt:P279* wd:Q186081 .
      
      # Must have Dewey Decimal in range
      ?item wdt:P1036 ?dewey .
      FILTER(?dewey >= {dewey_min} && ?dewey < {dewey_max + 1})
      
      # Temporal properties
      OPTIONAL {{ ?item wdt:P580 ?start . }}
      OPTIONAL {{ ?item wdt:P582 ?end . }}
      OPTIONAL {{ ?item wdt:P571 ?inception . }}
      OPTIONAL {{ ?item wdt:P576 ?dissolved . }}
      
      # ALL classification IDs (single query)
      OPTIONAL {{ ?item wdt:P1036 ?dewey . }}
      OPTIONAL {{ ?item wdt:P244 ?lcsh . }}
      OPTIONAL {{ ?item wdt:P1149 ?lcc . }}
      OPTIONAL {{ ?item wdt:P2163 ?fast . }}
      
      # Geographic context
      OPTIONAL {{ ?item wdt:P17 ?country . }}
      OPTIONAL {{ ?item wdt:P131 ?region . }}
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    ORDER BY ?dewey ?itemLabel
    """
    
    print(f"  Querying Dewey {dewey_min}-{dewey_max}...")
    data = query_wikidata(sparql)
    
    if not data:
        print(f"  ❌ Failed to retrieve data for Dewey {dewey_min}-{dewey_max}")
        return []
    
    bindings = data.get("results", {}).get("bindings", [])
    print(f"  ✅ Found {len(bindings)} periods")
    
    periods = []
    for b in bindings:
        # Extract QID
        item_uri = b.get('item', {}).get('value', '')
        qid = item_uri.split('/')[-1] if item_uri else ''
        
        # Extract LCSH ID from URI
        lcsh_uri = b.get('lcsh', {}).get('value', '')
        lcsh_id = lcsh_uri.split('/')[-1] if lcsh_uri else ''
        
        # Temporal (use most specific available), then normalize to a 4-point envelope.
        start_date = (
            b.get('start', {}).get('value', '')
            or b.get('inception', {}).get('value', '')
        )
        end_date = (
            b.get('end', {}).get('value', '')
            or b.get('dissolved', {}).get('value', '')
        )
        temporal = build_temporal_bbox(start_date=start_date, end_date=end_date)
        
        # Extract region/country
        country_qid = ''
        country_label = ''
        region_qid = ''
        region_label = ''
        
        country_uri = b.get('country', {}).get('value', '')
        if country_uri:
            country_qid = country_uri.split('/')[-1]
            country_label = b.get('countryLabel', {}).get('value', '')
        
        region_uri = b.get('region', {}).get('value', '')
        if region_uri:
            region_qid = region_uri.split('/')[-1]
            region_label = b.get('regionLabel', {}).get('value', '')
        
        # Determine region string (country or region label)
        region = country_label or region_label or ''
        
        period = {
            'qid': qid,
            'label': b.get('itemLabel', {}).get('value', ''),
            'description': b.get('itemDescription', {}).get('value', ''),
            **temporal,
            'dewey_decimal': b.get('dewey', {}).get('value', ''),
            'lcsh_id': lcsh_id,
            'lcc_code': b.get('lcc', {}).get('value', ''),
            'fast_id': b.get('fast', {}).get('value', ''),
            'region': region,
            'country_qid': country_qid,
            'region_qid': region_qid,
        }
        
        periods.append(period)
        
        # Rate limiting
        time.sleep(0.1)
    
    return periods

def generate_taxonomy(dewey_min: int = 930, dewey_max: int = 999) -> List[Dict]:
    """
    Generate comprehensive historical periods taxonomy.
    
    Queries all Dewey ranges and aggregates results.
    
    Args:
        dewey_min: Minimum Dewey code (default: 930)
        dewey_max: Maximum Dewey code (default: 999)
        
    Returns:
        List of all period dictionaries
    """
    print("=" * 80)
    print("GENERATE HISTORICAL PERIODS TAXONOMY")
    print("=" * 80)
    print(f"\nQuerying Dewey Decimal ranges {dewey_min}-{dewey_max}")
    print("This will query multiple ranges and may take 5-10 minutes...\n")
    
    all_periods = []
    
    # Query each Dewey range
    for dewey_min_range, dewey_max_range in DEWEY_RANGES:
        if dewey_min_range < dewey_min or dewey_max_range > dewey_max:
            continue
            
        periods = query_periods_by_dewey_range(dewey_min_range, dewey_max_range)
        all_periods.extend(periods)
        
        # Delay between ranges to avoid rate limiting
        if dewey_max_range < dewey_max:
            time.sleep(2)
    
    # Deduplicate by QID (keep first occurrence)
    seen_qids = set()
    unique_periods = []
    for period in all_periods:
        if period['qid'] and period['qid'] not in seen_qids:
            seen_qids.add(period['qid'])
            unique_periods.append(period)
    
    print(f"\n✅ Total periods found: {len(all_periods)}")
    print(f"✅ Unique periods: {len(unique_periods)}")
    
    return unique_periods

def write_csv(periods: List[Dict], output_file: str):
    """
    Write periods taxonomy to CSV file.
    
    Args:
        periods: List of period dictionaries
        output_file: Output CSV file path
    """
    # Ensure output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = [
        'qid', 'label', 'description',
        'start_date', 'end_date',
        'start_date_min', 'start_date_max', 'end_date_min', 'end_date_max',
        'earliest_start', 'latest_start', 'earliest_end', 'latest_end',
        'dewey_decimal', 'lcsh_id', 'lcc_code', 'fast_id', 'region'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(periods)
    
    print(f"\n✅ Wrote {len(periods)} periods to: {output_file}")

def print_statistics(periods: List[Dict]):
    """Print coverage statistics for the taxonomy."""
    total = len(periods)
    if total == 0:
        return
    
    with_dewey = sum(1 for p in periods if p.get('dewey_decimal'))
    with_lcsh = sum(1 for p in periods if p.get('lcsh_id'))
    with_lcc = sum(1 for p in periods if p.get('lcc_code'))
    with_fast = sum(1 for p in periods if p.get('fast_id'))
    with_dates = sum(1 for p in periods if p.get('start_date') or p.get('end_date'))
    with_region = sum(1 for p in periods if p.get('region'))
    
    print("\n" + "=" * 80)
    print("COVERAGE STATISTICS")
    print("=" * 80)
    print(f"Total periods:        {total}")
    print(f"With Dewey Decimal:  {with_dewey} ({with_dewey/total*100:.1f}%)")
    print(f"With LCSH ID:        {with_lcsh} ({with_lcsh/total*100:.1f}%)")
    print(f"With LCC Code:       {with_lcc} ({with_lcc/total*100:.1f}%)")
    print(f"With FAST ID:        {with_fast} ({with_fast/total*100:.1f}%)")
    print(f"With dates:          {with_dates} ({with_dates/total*100:.1f}%)")
    print(f"With region:         {with_region} ({with_region/total*100:.1f}%)")
    
    # Sample periods
    print("\nSample periods:")
    for period in periods[:5]:
        print(f"\n  {period['label']} ({period['qid']})")
        print(f"    Dewey: {period.get('dewey_decimal', 'N/A')}")
        print(f"    LCSH:  {period.get('lcsh_id', 'N/A')}")
        print(f"    LCC:   {period.get('lcc_code', 'N/A')}")
        print(f"    Dates: {period.get('start_date', '?')} - {period.get('end_date', '?')}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate historical periods taxonomy from Wikidata"
    )
    parser.add_argument(
        '--output', '-o',
        default=DEFAULT_OUTPUT,
        help=f"Output CSV file (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        '--dewey-min',
        type=int,
        default=930,
        help="Minimum Dewey Decimal code (default: 930)"
    )
    parser.add_argument(
        '--dewey-max',
        type=int,
        default=999,
        help="Maximum Dewey Decimal code (default: 999)"
    )
    
    args = parser.parse_args()
    
    # Generate taxonomy
    periods = generate_taxonomy(args.dewey_min, args.dewey_max)
    
    if not periods:
        print("\n❌ No periods found. Check your Dewey range and Wikidata connectivity.")
        sys.exit(1)
    
    # Write CSV
    write_csv(periods, args.output)
    
    # Print statistics
    print_statistics(periods)
    
    print("\n" + "=" * 80)
    print("✅ TAXONOMY GENERATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

