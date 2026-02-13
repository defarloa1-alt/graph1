#!/usr/bin/env python3
"""
Compare periods from more periods.md against query.tsv to find gaps.
"""
import sys
import io
import re
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Parse more periods.md (Wikidata list)
more_periods_file = Path("Temporal/more periods.md")
with open(more_periods_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract QIDs from format: "Label (QXXXXX)"
wikidata_periods = {}
for match in re.finditer(r'(.+?)\s+\(Q(\d+)\)', content):
    label = match.group(1).strip()
    qid = f"Q{match.group(2)}"
    wikidata_periods[qid] = label

print(f"Found {len(wikidata_periods)} periods in more periods.md")

# Parse query.tsv (our current data)
query_tsv = Path("Subjects/query.tsv")
with open(query_tsv, 'r', encoding='utf-8') as f:
    lines = f.readlines()

current_periods = {}
for line in lines[1:]:  # Skip header
    parts = line.strip().split('\t')
    if len(parts) >= 2:
        qid_full = parts[0]  # Format: <http://www.wikidata.org/entity/QXXXXX>
        label = parts[1]
        # Extract QID
        qid_match = re.search(r'Q(\d+)', qid_full)
        if qid_match:
            qid = f"Q{qid_match.group(1)}"
            current_periods[qid] = label

print(f"Found {len(current_periods)} periods in query.tsv")
print()

# Find gaps
missing_qids = set(wikidata_periods.keys()) - set(current_periods.keys())
missing_periods = {qid: wikidata_periods[qid] for qid in missing_qids}

print(f"GAPS: {len(missing_periods)} periods in Wikidata list but NOT in our database")
print()

# Categorize by type
categorized = {
    'Wars/Conflicts': [],
    'Empires/Dynasties': [],
    'Cultural/Artistic': [],
    'Modern Political': [],
    'Ancient': [],
    'Medieval': [],
    'Early Modern': [],
    'Modern': [],
    'Contemporary': [],
    'Other': []
}

for qid, label in sorted(missing_periods.items(), key=lambda x: x[1]):
    label_lower = label.lower()
    
    if any(k in label_lower for k in ['war', 'conflict', 'occupation', 'invasion']):
        categorized['Wars/Conflicts'].append((qid, label))
    elif any(k in label_lower for k in ['empire', 'dynasty', 'kingdom', 'republic']):
        categorized['Empires/Dynasties'].append((qid, label))
    elif any(k in label_lower for k in ['art', 'renaissance', 'golden age', 'culture', 'jazz', 'belle']):
        categorized['Cultural/Artistic'].append((qid, label))
    elif any(k in label_lower for k in ['century', 'contemporary', 'modern period', '20th', '21st']):
        categorized['Contemporary'].append((qid, label))
    elif any(k in label_lower for k in ['ancient', 'prehistoric', 'paleolithic', 'bronze age', 'iron age']):
        categorized['Ancient'].append((qid, label))
    elif any(k in label_lower for k in ['medieval', 'middle ages', 'viking', 'carolingian']):
        categorized['Medieval'].append((qid, label))
    elif any(k in label_lower for k in ['tudor', 'baroque', 'reformation', 'enlighten']):
        categorized['Early Modern'].append((qid, label))
    elif any(k in label_lower for k in ['19th', '1800', '1900', 'industrial', 'progressive']):
        categorized['Modern'].append((qid, label))
    else:
        categorized['Other'].append((qid, label))

# Report
print("="*80)
print("GAP ANALYSIS BY CATEGORY")
print("="*80)

for category, periods in categorized.items():
    if periods:
        print(f"\n{category}: {len(periods)} missing")
        for qid, label in periods[:10]:  # Show first 10
            print(f"  - {qid}: {label}")
        if len(periods) > 10:
            print(f"  ... and {len(periods) - 10} more")

# High priority additions
print("\n" + "="*80)
print("HIGH PRIORITY ADDITIONS (Major Periods)")
print("="*80)

high_priority = []
major_keywords = [
    'industrial revolution', 'renaissance', 'reformation', 'enlightenment',
    'roman empire', 'han dynasty', 'tang dynasty', 'ming dynasty', 'qing dynasty',
    'ottoman empire', 'byzantine empire', 'persian empire', 'achaemenid',
    'edo period', 'meiji', 'victorian', 'edwardian', 'atomic age', 'space age',
    'information age', 'great depression', 'nazi germany', 'weimar'
]

for qid, label in missing_periods.items():
    if any(keyword in label.lower() for keyword in major_keywords):
        high_priority.append((qid, label))

for qid, label in sorted(high_priority, key=lambda x: x[1]):
    print(f"  - {qid}: {label}")

print(f"\n✅ Gap analysis complete!")
print(f"   Total gaps: {len(missing_periods)}")
print(f"   High priority: {len(high_priority)}")

