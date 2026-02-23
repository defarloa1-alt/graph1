#!/usr/bin/env python3
"""
Manual LLM Resolution - Extract UNKNOWN properties for Claude review

Creates a readable file for Claude/human review with property details
"""

import csv
from pathlib import Path

INPUT_FILE = Path("CSV/property_mappings/property_facet_mapping_20260222_143544.csv")
OUTPUT_FILE = Path("CSV/property_mappings/UNKNOWN_properties_for_review.txt")

print("Extracting UNKNOWN properties for manual review...")

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    unknown = [row for row in reader if row['primary_facet'] == 'UNKNOWN']

print(f"Found {len(unknown)} UNKNOWN properties")
print()

# Write for easy review
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("UNKNOWN PROPERTIES FOR FACET ASSIGNMENT\n")
    f.write("="*80 + "\n\n")
    f.write(f"Total: {len(unknown)} properties\n")
    f.write("Format: Property ID | Label | Description\n\n")
    f.write("="*80 + "\n\n")
    
    for i, prop in enumerate(unknown, 1):
        f.write(f"{i}. {prop['property_id']} - {prop['property_label']}\n")
        f.write(f"   Description: {prop['property_description']}\n")
        f.write(f"   Type QIDs: {prop['type_qids']}\n")
        f.write(f"   Suggested Facet: _______________\n")
        f.write("\n")

print(f"Written to: {OUTPUT_FILE}")
print()
print("Next steps:")
print("  1. Open the file in Cursor")
print("  2. Ask Claude to review and suggest facets")
print("  3. Claude can batch-process these semantically")
