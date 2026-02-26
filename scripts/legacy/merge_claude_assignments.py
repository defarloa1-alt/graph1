#!/usr/bin/env python3
"""
Merge Claude's facet assignments with base mapping

Combines:
1. Base mapping (248 properties) - from Wikidata property types
2. Claude assignments (252 properties) - semantic analysis

Output: Complete 500-property mapping
"""

import csv
from pathlib import Path

BASE_FILE = Path("CSV/property_mappings/property_facet_mapping_20260222_143544.csv")
CLAUDE_BATCH_FILES = [
    Path("CSV/property_mappings/claude_facet_assignments_batch1.csv"),
    Path("CSV/property_mappings/claude_facet_assignments_batch2.csv"),
    Path("CSV/property_mappings/claude_facet_assignments_batch3.csv"),
    Path("CSV/property_mappings/claude_facet_assignments_batch4.csv"),
    Path("CSV/property_mappings/claude_facet_assignments_batch5_final.csv"),
]
OUTPUT_FILE = Path("CSV/property_mappings/property_facet_mapping_HYBRID.csv")

print("Merging facet assignments...")

# Load base mapping
with open(BASE_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    base_props = {row['property_id']: row for row in reader}

print(f"Base mapping: {len(base_props)} properties")

# Load Claude assignments from all batch files
claude_props = {}
total_claude = 0

for batch_file in CLAUDE_BATCH_FILES:
    if batch_file.exists():
        with open(batch_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                claude_props[row['property_id']] = row
                total_claude += 1
        print(f"  Loaded {batch_file.name}: {total_claude} assignments so far")

print(f"Total Claude assignments: {len(claude_props)} properties")

# Merge
for prop_id, claude_data in claude_props.items():
    if prop_id in base_props:
        base_props[prop_id]['primary_facet'] = claude_data['primary_facet']
        base_props[prop_id]['secondary_facets'] = claude_data['secondary_facets']
        base_props[prop_id]['all_facets'] = ','.join([
            claude_data['primary_facet']] + 
            (claude_data['secondary_facets'].split(',') if claude_data['secondary_facets'] else [])
        )
        base_props[prop_id]['confidence'] = claude_data['confidence']
        base_props[prop_id]['resolved_by'] = 'claude'
        base_props[prop_id]['claude_reasoning'] = claude_data['reasoning']

# Add resolved_by for base
for prop_id, prop in base_props.items():
    if 'resolved_by' not in prop or not prop.get('resolved_by'):
        prop['resolved_by'] = 'base_mapping'
        prop['claude_reasoning'] = ''

# Write merged
fieldnames = list(base_props[list(base_props.keys())[0]].keys())

with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(base_props.values())

print(f"\nOutput: {OUTPUT_FILE}")
print(f"Total properties: {len(base_props)}")

# Stats
claude_count = len([p for p in base_props.values() if p.get('resolved_by') == 'claude'])
base_count = len([p for p in base_props.values() if p.get('resolved_by') == 'base_mapping'])
unknown_count = len([p for p in base_props.values() if p['primary_facet'] == 'UNKNOWN'])

print(f"\nResolved by base mapping: {base_count}")
print(f"Resolved by Claude: {claude_count}")
print(f"Still UNKNOWN: {unknown_count}")
print(f"Coverage: {((500-unknown_count)/500)*100:.1f}%")
