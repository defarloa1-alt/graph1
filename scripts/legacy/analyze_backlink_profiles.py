#!/usr/bin/env python3
"""
Backlink Profile Analysis

Compute four-dimensional backlink profiles for all entities:
- X: Entity type distribution (what kinds of things point here)
- X1: Property distribution (how they point)
- X2: Temporal distribution (when they point - future)
- X3: Facet affinity (which research domain)

Output: Backlink profiles showing entity roles in knowledge graph
"""

import json
from neo4j import GraphDatabase
from collections import Counter, defaultdict

# Neo4j connection
driver = GraphDatabase.driver(
    'neo4j+s://f7b612a3.databases.neo4j.io',
    auth=('neo4j', 'K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM')
)

# Property to Facet mapping (simplified - will expand based on registry)
PID_TO_FACET = {
    'P39': 'POLITICAL',
    'P607': 'MILITARY',
    'P26': 'BIOGRAPHIC',
    'P40': 'BIOGRAPHIC',
    'P22': 'BIOGRAPHIC',
    'P25': 'BIOGRAPHIC',
    'P19': 'BIOGRAPHIC',
    'P20': 'BIOGRAPHIC',
    'P27': 'POLITICAL',
    'P106': 'SOCIAL',
    'P31': 'ONTOLOGICAL',
    'P279': 'ONTOLOGICAL',
    'P361': 'ONTOLOGICAL',
    'P527': 'ONTOLOGICAL',
    'P17': 'GEOGRAPHIC',
    'P131': 'GEOGRAPHIC',
    'P47': 'GEOGRAPHIC',
    'P150': 'GEOGRAPHIC',
    'P276': 'GEOGRAPHIC',
    'P50': 'LITERARY',
    'P921': 'LITERARY',
    'P793': 'HISTORICAL',
    'P1343': 'DOCUMENTARY'
}

print("="*80)
print("BACKLINK PROFILE ANALYSIS")
print("="*80)
print()

# Get all entities and their backlinks
print("Querying backlink profiles from Neo4j...")
print()

profiles = {}

with driver.session() as session:
    # Get backlinks for all entities
    result = session.run("""
        MATCH (target:Entity)
        OPTIONAL MATCH (source:Entity)-[r]->(target)
        WITH target, 
             collect({
                 source_qid: source.qid,
                 source_type: source.entity_type,
                 source_label: source.label,
                 property: type(r)
             }) as backlinks
        RETURN 
            target.qid as qid,
            target.label as label,
            target.entity_type as entity_type,
            backlinks,
            size(backlinks) as backlink_count
        ORDER BY backlink_count DESC
    """)
    
    print("Computing profiles...")
    
    for record in result:
        qid = record['qid']
        backlinks = record['backlinks']
        
        if not backlinks or backlinks == [None]:
            continue
        
        # Compute four-dimensional profile
        profile = {
            'qid': qid,
            'label': record['label'],
            'entity_type': record['entity_type'],
            'total_backlinks': record['backlink_count'],
            
            # X: Entity type distribution
            'source_type_dist': Counter(),
            
            # X1: Property distribution
            'property_dist': Counter(),
            
            # X3: Facet affinity
            'facet_dist': Counter(),
            
            # Derived metrics
            'dominant_source_type': None,
            'dominant_property': None,
            'dominant_facet': None,
            'hub_score': 0.0
        }
        
        for bl in backlinks:
            if not bl or bl['source_qid'] is None:
                continue
            
            # X: Source type
            source_type = bl['source_type'] or 'UNKNOWN'
            profile['source_type_dist'][source_type] += 1
            
            # X1: Property
            prop = bl['property']
            if prop:
                # Extract PID from relationship type
                if prop.startswith('WIKIDATA_'):
                    pid = prop.replace('WIKIDATA_', '')
                else:
                    pid = prop
                
                profile['property_dist'][pid] += 1
                
                # X3: Map to facet
                facet = PID_TO_FACET.get(pid, 'OTHER')
                profile['facet_dist'][facet] += 1
        
        # Compute dominant dimensions
        if profile['source_type_dist']:
            profile['dominant_source_type'] = profile['source_type_dist'].most_common(1)[0][0]
        
        if profile['property_dist']:
            profile['dominant_property'] = profile['property_dist'].most_common(1)[0][0]
        
        if profile['facet_dist']:
            profile['dominant_facet'] = profile['facet_dist'].most_common(1)[0][0]
        
        # Hub score: diversity × volume
        type_diversity = len(profile['source_type_dist'])
        volume = profile['total_backlinks']
        profile['hub_score'] = type_diversity * (volume ** 0.5)  # Sqrt to dampen outliers
        
        profiles[qid] = profile

driver.close()

print(f"Profiles computed: {len(profiles):,}")
print()

# Analysis
print("="*80)
print("BACKLINK PROFILE RESULTS")
print("="*80)
print()

# Top 20 hubs by backlink count
print("TOP 20 HUBS (by backlink count):")
print("-"*80)
sorted_by_backlinks = sorted(profiles.items(), key=lambda x: x[1]['total_backlinks'], reverse=True)
for qid, profile in sorted_by_backlinks[:20]:
    label = profile['label'] or 'N/A'
    types = profile['source_type_dist']
    top_type = profile['dominant_source_type']
    backlinks = profile['total_backlinks']
    
    print(f"{qid} ({label[:30]})")
    print(f"  Backlinks: {backlinks}")
    print(f"  Dominant type: {top_type}")
    print(f"  Distribution: {dict(types.most_common(3))}")
    print()

# Top hubs by diversity (cross-domain bridges)
print("TOP 20 CROSS-DOMAIN BRIDGES (by hub score):")
print("-"*80)
sorted_by_hub = sorted(profiles.items(), key=lambda x: x[1]['hub_score'], reverse=True)
for qid, profile in sorted_by_hub[:20]:
    label = profile['label'] or 'N/A'
    backlinks = profile['total_backlinks']
    diversity = len(profile['source_type_dist'])
    
    print(f"{qid} ({label[:30]})")
    print(f"  Hub score: {profile['hub_score']:.1f}")
    print(f"  Backlinks: {backlinks}, Type diversity: {diversity}")
    print(f"  Facet profile: {dict(profile['facet_dist'].most_common(3))}")
    print()

# Entities by dominant facet
print("ENTITIES BY DOMINANT FACET:")
print("-"*80)
by_facet = defaultdict(list)
for qid, profile in profiles.items():
    facet = profile['dominant_facet']
    if facet:
        by_facet[facet].append((qid, profile['total_backlinks']))

for facet in sorted(by_facet.keys()):
    entities = by_facet[facet]
    print(f"\n{facet} ({len(entities)} entities):")
    for qid, count in sorted(entities, key=lambda x: x[1], reverse=True)[:5]:
        label = profiles[qid]['label'] or 'N/A'
        print(f"  {qid} ({label[:30]}): {count} backlinks")

# Save
output = {
    'profiles': {
        qid: {
            'label': p['label'],
            'entity_type': p['entity_type'],
            'total_backlinks': p['total_backlinks'],
            'source_type_dist': dict(p['source_type_dist']),
            'property_dist': dict(p['property_dist']),
            'facet_dist': dict(p['facet_dist']),
            'dominant_source_type': p['dominant_source_type'],
            'dominant_property': p['dominant_property'],
            'dominant_facet': p['dominant_facet'],
            'hub_score': p['hub_score']
        }
        for qid, p in profiles.items()
    }
}

with open('output/backlink_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print()
print("="*80)
print("Saved: output/backlink_profiles.json")
print("="*80)
print()

# Summary stats
total_backlinks = sum(p['total_backlinks'] for p in profiles.values())
print("SUMMARY:")
print(f"  Entities analyzed: {len(profiles):,}")
print(f"  Total backlinks: {total_backlinks:,}")
print(f"  Avg backlinks per entity: {total_backlinks/len(profiles):.1f}")
print()
print("Distribution by dominant facet:")
for facet, entities in sorted(by_facet.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  {facet}: {len(entities)} entities")
print()
