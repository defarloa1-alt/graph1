#!/usr/bin/env python3
"""
Deduplicate and analyze Q107649491 backlinks
"""

import csv
from pathlib import Path
from collections import Counter

# Input/Output
INPUT_FILE = Path("CSV/backlinks/Q107649491_property_types_20260222_135228.csv")
OUTPUT_FILE = Path("CSV/backlinks/Q107649491_property_types_CLEAN.csv")

print("Deduplicating and analyzing backlinks...")
print()

# Read and deduplicate
seen_qids = set()
unique_rows = []

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    total_rows = 0
    
    for row in reader:
        total_rows += 1
        qid = row['qid']
        
        if qid not in seen_qids:
            seen_qids.add(qid)
            # Clean label (remove QID suffix if present)
            label = row['label']
            if f"({qid})" in label:
                label = label.replace(f"({qid})", "").strip()
            row['label'] = label
            unique_rows.append(row)

print(f"Original rows: {total_rows:,}")
print(f"Unique QIDs: {len(unique_rows):,}")
print(f"Duplicates removed: {total_rows - len(unique_rows):,}")
print()

# Write deduplicated CSV
with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['qid', 'label', 'description'])
    writer.writeheader()
    writer.writerows(unique_rows)

print(f"Clean CSV written: {OUTPUT_FILE}")
print()

# Analysis: Categorize by Chrystallum relevance
categories = {
    'Historical Periods': [],
    'Authority Control': [],
    'Geographic': [],
    'Military': [],
    'Political': [],
    'Events': [],
    'People': [],
    'Works/Creative': [],
    'Religious': [],
    'Other': []
}

for row in unique_rows:
    label_lower = row['label'].lower()
    
    if 'ancient world' in label_lower or 'middle ages' in label_lower or 'renaissance' in label_lower or 'early modern' in label_lower:
        categories['Historical Periods'].append(row)
    elif 'authority control' in label_lower:
        categories['Authority Control'].append(row)
    elif 'location' in label_lower or 'place' in label_lower or 'geographic' in label_lower:
        categories['Geographic'].append(row)
    elif 'military' in label_lower or 'weapon' in label_lower:
        categories['Military'].append(row)
    elif 'politic' in label_lower or 'government' in label_lower:
        categories['Political'].append(row)
    elif 'event' in label_lower:
        categories['Events'].append(row)
    elif 'people' in label_lower or 'person' in label_lower:
        categories['People'].append(row)
    elif 'work' in label_lower or 'creative' in label_lower or 'film' in label_lower or 'book' in label_lower:
        categories['Works/Creative'].append(row)
    elif 'religion' in label_lower or 'church' in label_lower or 'islam' in label_lower or 'judaism' in label_lower:
        categories['Religious'].append(row)
    else:
        categories['Other'].append(row)

# Print categorized results
print("="*80)
print("CHRYSTALLUM RELEVANCE ANALYSIS")
print("="*80)
print()

for category, items in categories.items():
    if items and category != 'Other':
        print(f"{category}: {len(items)} property types")
        for item in items[:5]:
            print(f"  - {item['qid']:12} {item['label'][:65]}")
        if len(items) > 5:
            print(f"  ... and {len(items)-5} more")
        print()

print(f"Other: {len(categories['Other'])} property types")
print()

print("="*80)
print("COMPLETE!")
print("="*80)
