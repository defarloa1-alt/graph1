#!/usr/bin/env python3
"""
Analyze Wikidata Claims - Three-Bucket Classification

Classify all claims in checkpoint into:
1. Attributes (node properties)
2. Simple edges (entity-to-entity, no qualifiers)
3. Node candidates (entity-to-entity with cipher qualifiers)

Output: Analysis report showing distribution and top properties per bucket
"""

import json
from collections import Counter, defaultdict

# Cipher-eligible qualifiers (from architecture spec)
CIPHER_ELIGIBLE_QUALIFIERS = {"P580", "P582", "P585", "P276", "P1545"}

def classify_claim(claim: dict) -> str:
    """
    Mechanical classification based on datavalue.type and qualifiers.
    
    Returns: 'attribute' | 'edge' | 'node_candidate'
    """
    mainsnak = claim.get('mainsnak', {})
    datavalue = mainsnak.get('datavalue', {})
    datatype = datavalue.get('type', '')
    
    # Bucket 1: Not entity reference
    if datatype != 'wikibase-entityid':
        return 'attribute'
    
    # It's entity-to-entity. Check qualifiers.
    qualifiers = set(claim.get('qualifiers', {}).keys())
    
    # Bucket 3: Has cipher-eligible qualifiers
    if qualifiers & CIPHER_ELIGIBLE_QUALIFIERS:
        return 'node_candidate'
    
    # Bucket 2: Simple edge
    return 'edge'


print("="*80)
print("WIKIDATA CLAIM CLASSIFICATION ANALYSIS")
print("="*80)
print()

# Load checkpoint
checkpoint_file = 'output/checkpoints/QQ17167_checkpoint_20260221_061318.json'
print(f"Loading checkpoint: {checkpoint_file}")

with open(checkpoint_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

entities = data.get('entities', {})
print(f"Entities: {len(entities):,}")
print()

# Classification counters
bucket_counts = Counter()
property_by_bucket = defaultdict(lambda: defaultdict(int))
datatype_by_bucket = defaultdict(Counter)

total_claims = 0
total_entities_with_claims = 0

# Classify all claims
for qid, entity in entities.items():
    claims = entity.get('claims', {})
    
    if not claims:
        continue
    
    total_entities_with_claims += 1
    
    for prop_id, prop_claims in claims.items():
        for claim in prop_claims:
            total_claims += 1
            
            # Classify
            bucket = classify_claim(claim)
            bucket_counts[bucket] += 1
            property_by_bucket[bucket][prop_id] += 1
            
            # Track datatype
            datatype = claim.get('mainsnak', {}).get('datavalue', {}).get('type', 'unknown')
            datatype_by_bucket[bucket][datatype] += 1

# Report
print("="*80)
print("CLASSIFICATION RESULTS")
print("="*80)
print()

print(f"Total entities analyzed: {len(entities):,}")
print(f"Entities with claims: {total_entities_with_claims:,}")
print(f"Total claims: {total_claims:,}")
print()

print("BUCKET DISTRIBUTION:")
print("-"*80)
for bucket in ['attribute', 'edge', 'node_candidate']:
    count = bucket_counts[bucket]
    pct = count / total_claims * 100 if total_claims > 0 else 0
    print(f"{bucket:20s}: {count:8,} ({pct:5.1f}%)")
print()

print("DATATYPES BY BUCKET:")
print("-"*80)
for bucket in ['attribute', 'edge', 'node_candidate']:
    print(f"\n{bucket.upper()}:")
    for datatype, count in datatype_by_bucket[bucket].most_common(5):
        print(f"  {datatype:25s}: {count:,}")
print()

print("="*80)
print("TOP PROPERTIES BY BUCKET")
print("="*80)
print()

# Top 30 for each bucket
for bucket in ['attribute', 'edge', 'node_candidate']:
    print(f"\n{bucket.upper()} (Top 30):")
    print("-"*80)
    for prop_id, count in sorted(property_by_bucket[bucket].items(), 
                                 key=lambda x: x[1], reverse=True)[:30]:
        print(f"  {prop_id}: {count:,}")

# Save detailed results
output = {
    'summary': {
        'total_entities': len(entities),
        'total_claims': total_claims,
        'bucket_distribution': dict(bucket_counts)
    },
    'datatypes_by_bucket': {
        bucket: dict(datatypes)
        for bucket, datatypes in datatype_by_bucket.items()
    },
    'properties_by_bucket': {
        bucket: dict(props)
        for bucket, props in property_by_bucket.items()
    }
}

output_file = 'output/claim_classification_analysis.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print()
print("="*80)
print(f"Analysis saved: {output_file}")
print("="*80)
print()

# Summary stats
print("SUMMARY:")
print(f"  Attributes: {bucket_counts['attribute']:,} (will be node properties)")
print(f"  Simple edges: {bucket_counts['edge']:,} (will create {len(property_by_bucket['edge'])} edge types)")
print(f"  Node candidates: {bucket_counts['node_candidate']:,} (will be FacetClaim nodes)")
print()
print(f"Current database: 784 edges (from 19 hardcoded properties)")
print(f"After import: ~{bucket_counts['edge']:,} edges (from {len(property_by_bucket['edge'])} properties)")
print(f"Improvement: ~{bucket_counts['edge']/784:.1f}x")
print()
