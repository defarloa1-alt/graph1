#!/usr/bin/env python3
"""Validate checkpoint has complete data (not just page 1)"""

import json

print("="*80)
print("CHECKPOINT COMPLETENESS VALIDATION")
print("="*80)
print()

# Load checkpoint
with open('output/checkpoints/QQ17167_checkpoint_20260221_061318.json', encoding='utf-8') as f:
    data = json.load(f)

entities = data.get('entities', {})

print(f"Total entities: {len(entities):,}")
print()

# Sample entity analysis
sample_qid = 'Q17167'  # Roman Republic
if sample_qid in entities:
    sample = entities[sample_qid]
    
    print(f"Sample entity: {sample_qid} ({sample.get('label', 'N/A')})")
    print(f"  Claims: {len(sample.get('claims', {}))} properties")
    print(f"  Sitelinks: {len(sample.get('sitelinks', {}))} Wikipedia editions")
    print()
    
    # Check a high-claim-count property
    claims = sample.get('claims', {})
    print("Property claim counts:")
    for pid, claim_list in sorted(claims.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"  {pid}: {len(claim_list)} claim(s)")
    print()

# Distribution analysis
print("ENTITY CLAIM COUNT DISTRIBUTION:")
print("-"*80)

claim_counts = [len(e.get('claims', {})) for e in entities.values()]
claim_counts.sort(reverse=True)

print(f"  Min claims per entity: {min(claim_counts)}")
print(f"  Avg claims per entity: {sum(claim_counts)/len(claim_counts):.1f}")
print(f"  Max claims per entity: {max(claim_counts)}")
print(f"  Median: {claim_counts[len(claim_counts)//2]}")
print()

print("Top 10 entities by claim count:")
entities_by_claims = [(qid, len(e.get('claims', {}))) for qid, e in entities.items()]
entities_by_claims.sort(key=lambda x: x[1], reverse=True)

for qid, count in entities_by_claims[:10]:
    label = entities[qid].get('label', 'N/A')
    print(f"  {qid} ({label[:40]}): {count} properties")
print()

# Check for suspicious patterns (would indicate pagination issues)
print("CHECKING FOR PAGINATION ISSUES:")
print("-"*80)

# If many entities have exactly same claim count, might be page limit
from collections import Counter
count_distribution = Counter(claim_counts)
suspicious = [(count, freq) for count, freq in count_distribution.items() if freq > 50 and count > 50]

if suspicious:
    print("⚠️  Suspicious patterns (possible pagination cutoff):")
    for count, freq in suspicious:
        print(f"  {freq} entities with exactly {count} properties")
else:
    print("✓ No suspicious patterns detected")
    print("  (Varied claim counts suggest complete extraction)")

print()
print("="*80)
print("Checkpoint appears complete" if not suspicious else "⚠️  May need re-extraction")
print("="*80)
