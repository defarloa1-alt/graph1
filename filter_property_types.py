#!/usr/bin/env python3
"""Filter property types: domain vs metadata"""

import csv

rows = list(csv.DictReader(open('CSV/backlinks/Q107649491_property_types_20260222_135228.csv', encoding='utf-8')))

# Filter domain-substantive (broader criteria)
domain = []
metadata = []

for r in rows:
    desc = r['description'].lower()
    label = r['label'].lower()
    
    # Metadata/infrastructure
    if any(x in label for x in ['wikidata property', 'wikimedia', 'obsolete', 'transitive', 'asymmetric', 'orderable']):
        if 'for items about' not in desc and 'related to' not in desc:
            metadata.append(r)
            continue
    
    # Domain-substantive
    domain.append(r)

print(f"Total property types: {len(rows)}")
print(f"Domain/Substantive: {len(domain)}")
print()

# Group by category
categories = {}
for r in domain:
    desc = r['description']
    
    if 'people' in desc:
        cat = 'PEOPLE'
    elif 'organizations' in desc or 'organization' in desc:
        cat = 'ORGANIZATIONS'
    elif 'places' in desc or 'location' in desc:
        cat = 'PLACES'
    elif 'works' in desc or 'creative' in desc:
        cat = 'WORKS'
    elif 'events' in desc or 'event' in desc:
        cat = 'EVENTS'
    elif 'economics' in desc or 'economic' in desc:
        cat = 'ECONOMICS'
    elif 'military' in desc:
        cat = 'MILITARY'
    elif 'medicine' in desc or 'health' in desc:
        cat = 'MEDICAL'
    elif 'sport' in desc:
        cat = 'SPORTS'
    elif 'chemistry' in desc or 'chemical' in desc:
        cat = 'CHEMISTRY'
    elif 'taxa' in desc or 'biological' in desc:
        cat = 'BIOLOGY'
    else:
        cat = 'OTHER'
    
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(r)

print("DOMAIN CATEGORIES:")
print("="*80)
for cat, items in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\n{cat} ({len(items)} property types):")
    for item in items[:5]:
        print(f"  {item['qid']}: {item['description']}")
    if len(items) > 5:
        print(f"  ... and {len(items) - 5} more")

# Do these match our entity types?
print()
print("="*80)
print("COMPARISON TO OUR ENTITY TYPES:")
print("="*80)
print()

our_types = ['PERSON', 'EVENT', 'PLACE', 'ORGANIZATION', 'WORK', 'PERIOD', 'MATERIAL', 'OBJECT']
found_match = ['PEOPLE', 'EVENTS', 'PLACES', 'ORGANIZATIONS', 'WORKS']
no_match = ['PERIOD', 'MATERIAL', 'OBJECT']

print("Property type categories that match our entity types:")
for match in found_match:
    if match in categories:
        print(f"  {match}: {len(categories[match])} property types")

print()
print("Our entity types with NO matching property category:")
for nm in no_match:
    print(f"  {nm}: (no direct property type category)")

print()
print("Property categories we DON'T have entity types for:")
other_cats = set(categories.keys()) - set(found_match) - {'OTHER'}
for cat in sorted(other_cats):
    print(f"  {cat}: {len(categories[cat])} property types")
