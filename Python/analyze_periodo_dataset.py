#!/usr/bin/env python3
"""Analyze PeriodO dataset for import readiness"""

import csv

print("=" * 70)
print("PERIODO DATASET ANALYSIS")
print("=" * 70)

# Read the dataset
with open('Temporal/periodo-dataset.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"\nTotal rows: {len(rows)}")
print(f"Columns: {list(rows[0].keys())}")

# Filter: end date > -2000
print("\n[FILTER 1] End date > -2000 (after 2000 BCE)...")
after_2000bce = []
for r in rows:
    if r.get('stop') and r['stop'] and r['stop'] != '':
        try:
            if int(r['stop']) > -2000:
                after_2000bce.append(r)
        except:
            pass

print(f"  Rows passing filter: {len(after_2000bce)}/{len(rows)}")

# Filter: Has Wikidata QID
print("\n[FILTER 2] Has Wikidata QID...")
with_qid = [r for r in after_2000bce if r.get('qid') and r['qid'].strip()]
print(f"  With QID: {len(with_qid)}/{len(after_2000bce)}")

# Filter: Has spatial coverage
print("\n[FILTER 3] Has spatial coverage...")
with_spatial = [r for r in with_qid if r.get('spatial_coverage') and r['spatial_coverage'].strip()]
print(f"  With spatial coverage: {len(with_spatial)}/{len(with_qid)}")

# Filter: Has both start AND stop dates
print("\n[FILTER 4] Has both start AND stop dates...")
complete = [r for r in with_spatial if r.get('start') and r['start'].strip() and r.get('stop') and r['stop'].strip()]
print(f"  Complete periods: {len(complete)}/{len(with_spatial)}")

# Sample
print("\n=== Sample Complete Periods (Ready for Import) ===")
for i, row in enumerate(complete[:10], 1):
    spatial = row['spatial_coverage'][:60] + '...' if len(row['spatial_coverage']) > 60 else row['spatial_coverage']
    print(f"\n{i}. {row['label']}")
    print(f"   QID: {row['qid']}")
    print(f"   Dates: {row['start']} to {row['stop']}")
    print(f"   Location: {spatial}")
    print(f"   Authority: {row['source']}")

# Statistics
print("\n=== Statistics ===")
print(f"Total PeriodO periods: {len(rows)}")
print(f"After 2000 BCE: {len(after_2000bce)} ({len(after_2000bce)/len(rows)*100:.1f}%)")
print(f"With QID: {len(with_qid)} ({len(with_qid)/len(after_2000bce)*100:.1f}%)")
print(f"With spatial: {len(with_spatial)} ({len(with_spatial)/len(with_qid)*100:.1f}%)")
print(f"Complete (ready): {len(complete)} ({len(complete)/len(rows)*100:.1f}%)")

print(f"\n=== RECOMMENDATION ===")
print(f"Import {len(complete)} complete periods from PeriodO")
print(f"These have: dates, QID, spatial coverage, authority")

# Check for missing QIDs
no_qid = [r for r in after_2000bce if not r.get('qid') or not r['qid'].strip()]
if no_qid:
    print(f"\n{len(no_qid)} periods lack QIDs (would need Wikidata lookup)")
    for i, row in enumerate(no_qid[:5], 1):
        print(f"  {i}. {row['label']} ({row['start']} to {row['stop']})")

