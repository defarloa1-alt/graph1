#!/usr/bin/env python3
"""
Filter Wikidata Periods to Useful Historical Periods
Removes geological epochs, undated entries, and invalid data
"""

import csv
import sys
import io
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Valid classes for HISTORICAL periods (not geological)
VALID_CLASSES = {
    'Q11514315': 'historical period',
    'Q186081': 'time interval',
    'Q3186692': 'time period',
    'Q36507': 'calendar era'
}

def parse_year_from_iso(iso_date: str) -> int:
    """Extract year from ISO date string."""
    if not iso_date:
        return None
    
    try:
        if iso_date.startswith('-'):
            # BCE: -0509-01-01T00:00:00Z
            parts = iso_date.split('T')[0].split('-')
            return -int(parts[1])
        else:
            # CE: 1945-08-15T00:00:00Z
            parts = iso_date.split('T')[0].split('-')
            return int(parts[0])
    except (ValueError, IndexError):
        return None

def is_valid_historical_period(row: dict) -> tuple:
    """
    Determine if a period is a valid historical period.
    
    Returns:
        (is_valid: bool, reason: str)
    """
    # Must be a valid class
    if row['class_qid'] not in VALID_CLASSES:
        return (False, f"Invalid class: {row['class_label']}")
    
    # Must have SOME temporal data
    has_temporal = any([
        row['start_date'],
        row['end_date'],
        row['point_in_time']
    ])
    
    if not has_temporal:
        return (False, "No temporal data")
    
    # Check for geological time (pre-human history)
    start_year = parse_year_from_iso(row['start_date'])
    if start_year and start_year < -10000:
        return (False, f"Geological time: {start_year}")
    
    # Check for far future dates (likely data errors)
    end_year = parse_year_from_iso(row['end_date'])
    if end_year and end_year > 2100:
        return (False, f"Far future: {end_year}")
    
    # Valid!
    return (True, "Valid historical period")

def filter_periods(input_path: Path, output_path: Path):
    """Filter raw periods to useful historical periods."""
    print("="*80)
    print("FILTERING WIKIDATA PERIODS")
    print("="*80)
    print(f"\nInput:  {input_path}")
    print(f"Output: {output_path}\n")
    
    valid_periods = []
    rejection_reasons = defaultdict(int)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        total = 0
        
        for row in reader:
            total += 1
            is_valid, reason = is_valid_historical_period(row)
            
            if is_valid:
                valid_periods.append(row)
            else:
                rejection_reasons[reason] += 1
    
    # Write filtered periods
    if valid_periods:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=valid_periods[0].keys())
            writer.writeheader()
            writer.writerows(valid_periods)
    
    # Print summary
    print(f"[INPUT]  Total periods: {total:,}")
    print(f"[OUTPUT] Valid periods: {len(valid_periods):,}")
    print(f"[FILTER] Rejected:      {total - len(valid_periods):,} ({(total-len(valid_periods))/total*100:.1f}%)")
    print()
    
    print("[REJECTION REASONS]")
    for reason, count in sorted(rejection_reasons.items(), key=lambda x: -x[1]):
        print(f"  {reason:40s}: {count:>8,}")
    print()
    
    # Analyze valid periods
    print("="*80)
    print("FILTERED DATASET ANALYSIS")
    print("="*80)
    
    # By class
    print("\n[BY CLASS]")
    class_counts = defaultdict(int)
    for p in valid_periods:
        class_counts[p['class_label']] += 1
    
    for cls, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f"  {cls:30s}: {count:>6,}")
    
    # Temporal coverage
    print("\n[TEMPORAL COVERAGE]")
    with_start = sum(1 for p in valid_periods if p['start_date'])
    with_end = sum(1 for p in valid_periods if p['end_date'])
    with_both = sum(1 for p in valid_periods if p['start_date'] and p['end_date'])
    with_point = sum(1 for p in valid_periods if p['point_in_time'])
    
    print(f"  With start date:       {with_start:>6,} ({with_start/len(valid_periods)*100:.1f}%)")
    print(f"  With end date:         {with_end:>6,} ({with_end/len(valid_periods)*100:.1f}%)")
    print(f"  With both dates:       {with_both:>6,} ({with_both/len(valid_periods)*100:.1f}%)")
    print(f"  With point in time:    {with_point:>6,} ({with_point/len(valid_periods)*100:.1f}%)")
    
    # Classification coverage
    print("\n[CLASSIFICATION COVERAGE]")
    with_lcsh = sum(1 for p in valid_periods if p['lcsh_id'])
    with_dewey = sum(1 for p in valid_periods if p['dewey_decimal'])
    with_lcc = sum(1 for p in valid_periods if p['lcc_code'])
    with_fast = sum(1 for p in valid_periods if p['fast_id'])
    with_any_class = sum(1 for p in valid_periods if any([p['lcsh_id'], p['dewey_decimal'], p['lcc_code'], p['fast_id']]))
    
    print(f"  With LCSH (P244):      {with_lcsh:>6,} ({with_lcsh/len(valid_periods)*100:.1f}%)")
    print(f"  With Dewey (P1036):    {with_dewey:>6,} ({with_dewey/len(valid_periods)*100:.1f}%)")
    print(f"  With LCC (P1149):      {with_lcc:>6,} ({with_lcc/len(valid_periods)*100:.1f}%)")
    print(f"  With FAST (P2163):     {with_fast:>6,} ({with_fast/len(valid_periods)*100:.1f}%)")
    print(f"  With ANY classification: {with_any_class:>6,} ({with_any_class/len(valid_periods)*100:.1f}%)")
    
    # Hierarchy
    print("\n[HIERARCHY]")
    with_parent = sum(1 for p in valid_periods if p['part_of_qid'])
    with_follows = sum(1 for p in valid_periods if p['follows_qid'])
    with_followed_by = sum(1 for p in valid_periods if p['followed_by_qid'])
    
    print(f"  With parent (part of): {with_parent:>6,} ({with_parent/len(valid_periods)*100:.1f}%)")
    print(f"  With predecessor:      {with_follows:>6,} ({with_follows/len(valid_periods)*100:.1f}%)")
    print(f"  With successor:        {with_followed_by:>6,} ({with_followed_by/len(valid_periods)*100:.1f}%)")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    script_dir = Path(__file__).parent.parent
    input_path = script_dir / "CSV" / "wikidata_all_periods_raw.csv"
    output_path = script_dir / "CSV" / "wikidata_periods_filtered.csv"
    
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    
    filter_periods(input_path, output_path)
    
    print("[NEXT STEP] Open wikidata_periods_filtered.csv to see clean historical periods")


