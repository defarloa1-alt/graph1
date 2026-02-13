#!/usr/bin/env python3
"""
Debug: Check broader_lcsh field in CSV
"""

import csv
from pathlib import Path

script_dir = Path(__file__).parent.parent
csv_path = script_dir / "CSV" / "lcsh_subjects_complete.csv"

print("="*80)
print("CHECKING CSV FOR BROADER_LCSH DATA")
print("="*80)
print()

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    with_broader = []
    total = 0
    
    for row in reader:
        total += 1
        if row['broader_lcsh']:
            with_broader.append({
                'child_id': row['lcsh_id'],
                'child_label': row['label'],
                'parent_id': row['broader_lcsh']
            })
    
    print(f"Total subjects in CSV: {total}")
    print(f"Subjects with broader_lcsh: {len(with_broader)}")
    print()
    
    if with_broader:
        print("[SAMPLE BROADER RELATIONSHIPS IN CSV]")
        for item in with_broader[:10]:
            print(f"Child:  {item['child_id']} | {item['child_label'][:50]}")
            print(f"Parent: {item['parent_id']}")
            print()
    else:
        print("[NO BROADER RELATIONSHIPS FOUND IN CSV]")
        print("This means LCSH API didn't return 'broader' property")

print("="*80)


