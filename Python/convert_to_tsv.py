#!/usr/bin/env python3
"""
Convert CSV to TSV (tab-delimited) for Excel
"""

import csv
import sys
from pathlib import Path

script_dir = Path(__file__).parent.parent
input_path = script_dir / "CSV" / "wikidata_periods_filtered.csv"
output_path = script_dir / "CSV" / "wikidata_periods_filtered.tsv"

with open(input_path, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        
        for row in reader:
            writer.writerow(row)

print(f"[SUCCESS] Created tab-delimited file:")
print(f"  {output_path}")
print()
print("Open this .tsv file in Excel - columns will separate correctly!")


