#!/usr/bin/env python3
"""
Enrich Periods with MULTIPLE Facets (Preserves All InstanceOf Data)
- Groups duplicates by QID
- Keeps ALL facets for each period (not just primary)
- Maps instanceOf labels to typed facets
- Still validates: dates, location, date range, events
"""
import sys
import io
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Map original Wikidata instanceOf labels to typed facets
INSTANCE_OF_MAPPING = {
    'historical period': 'CulturalFacet',
    'historical country': 'PoliticalFacet',
    'dynasty': 'PoliticalFacet',
    'chinese dynasty': 'PoliticalFacet',
    'egyptian dynasty': 'PoliticalFacet',
    'empire': 'PoliticalFacet',
    'kingdom': 'PoliticalFacet',
    'republic': 'PoliticalFacet',
    'civilization': 'CulturalFacet',
    'ancient civilization': 'CulturalFacet',
    'culture': 'CulturalFacet',
    'archaeological period': 'ArchaeologicalFacet',
    'archaeological culture': 'ArchaeologicalFacet',
    'age': 'CulturalFacet',
    'era': 'CulturalFacet',
    'golden age': 'CulturalFacet',
    'style': 'ArtisticFacet',
    'art movement': 'ArtisticFacet',
    'architectural style': 'ArtisticFacet',
    'world war': 'MilitaryFacet',  # But mark as event
    'war': 'MilitaryFacet',  # But mark as event
    'conflict': 'MilitaryFacet',  # But mark as event
    'crisis': 'PoliticalFacet',
    'revolution': 'PoliticalFacet',  # Can be period or event
    'movement': 'CulturalFacet',
    'occupation': 'MilitaryFacet',
    'period': 'CulturalFacet',  # Generic fallback
}

# Event markers - if facet contains these AND dates are short (<10 years), it's likely an event
EVENT_MARKERS = ['world war', 'war', 'battle', 'siege', 'treaty', 'conference']

def parse_periods_multi_facet(file_path) -> Dict[str, Dict]:
    """Parse periods and group by QID, collecting ALL facets."""
    with open(str(file_path), 'r', encoding='utf-8') as f:
        content = f.read()
    
    period_groups = defaultdict(lambda: {
        'qid': None,
        'label': None,
        'start_year': None,
        'end_year': None,
        'location_qids': set(),
        'facet_labels': set(),
        'blocks': []
    })
    
    # Split into blocks
    blocks = re.split(r'(?=MERGE \(p:Period)', content)
    
    for block in blocks:
        if not block.strip() or 'MERGE (p:Period' not in block:
            continue
        
        # Extract QID
        qid_match = re.search(r"qid: '([^']+)'", block)
        if not qid_match:
            continue
        qid = qid_match.group(1)
        
        # Extract label
        label_match = re.search(r"SET p\.label = '((?:[^']|'')+)'", block)
        if label_match:
            label = label_match.group(1).replace("''", "'")
            if not period_groups[qid]['label']:
                period_groups[qid]['label'] = label
        
        # Extract start_year
        start_match = re.search(r"SET p\.start_year = (\d+)", block)
        if start_match and not period_groups[qid]['start_year']:
            period_groups[qid]['start_year'] = int(start_match.group(1))
        
        # Extract end_year
        end_match = re.search(r"SET p\.end_year = (\d+)", block)
        if end_match and not period_groups[qid]['end_year']:
            period_groups[qid]['end_year'] = int(end_match.group(1))
        
        # Extract location
        location_match = re.search(r"MERGE \(geo:Place \{qid: '([^']+)'\}\)", block)
        if location_match:
            period_groups[qid]['location_qids'].add(location_match.group(1))
        
        # Extract facet label
        facet_match = re.search(r"MERGE \(f:Facet \{label: '([^']+)'\}\)", block)
        if facet_match:
            period_groups[qid]['facet_labels'].add(facet_match.group(1))
        
        period_groups[qid]['qid'] = qid
        period_groups[qid]['blocks'].append(block[:200])
    
    return dict(period_groups)

def is_event(label: str, facets: set, start_year: int, end_year: int) -> bool:
    """Determine if this is an event rather than a period."""
    label_lower = label.lower()
    
    # Check for event markers in label
    if any(marker in label_lower for marker in EVENT_MARKERS):
        # If it's short duration (<10 years), likely an event
        if start_year and end_year and (end_year - start_year) < 10:
            return True
    
    # Check for war/battle/treaty in label
    event_keywords = ['battle', 'treaty', 'conference', 'assassination', 'siege']
    if any(keyword in label_lower for keyword in event_keywords):
        return True
    
    return False

def generate_multi_facet_cypher(period_groups: Dict, output_file):
    """Generate Cypher with multiple facets per period."""
    lines = []
    included_count = 0
    filtered_events = 0
    filtered_no_dates = 0
    filtered_no_location = 0
    filtered_too_old = 0
    
    print(f"\nGenerating Cypher for {len(period_groups)} unique periods...")
    
    for qid, data in period_groups.items():
        # Validation
        if not data.get('start_year') or not data.get('end_year'):
            filtered_no_dates += 1
            print(f"   ⚠️  FILTERED: No dates - {data.get('label', 'Unknown')}")
            continue
        
        if not data.get('location_qids'):
            filtered_no_location += 1
            print(f"   ⚠️  FILTERED: No location - {data.get('label', 'Unknown')}")
            continue
        
        if data.get('end_year') < -2000:
            filtered_too_old += 1
            print(f"   ⚠️  FILTERED: Too old (ends {data['end_year']}) - {data.get('label', 'Unknown')}")
            continue
        
        # Check if event
        if is_event(data['label'], data['facet_labels'], data['start_year'], data['end_year']):
            filtered_events += 1
            print(f"   ⚠️  FILTERED: Event - {data.get('label', 'Unknown')}")
            continue
        
        # Build Cypher block
        included_count += 1
        label = data['label'].replace("'", "''")
        
        block = [f"MERGE (p:Period {{qid: '{qid}'}})"]
        block.append(f"SET p.label = '{label}'")
        block.append(f"SET p.start_year = {data['start_year']}")
        block.append(f"SET p.end_year = {data['end_year']}")
        block.append(f"MERGE (start:Year {{value: {data['start_year']}}})")
        block.append("MERGE (p)-[:STARTS_IN]->(start)")
        block.append(f"MERGE (end:Year {{value: {data['end_year']}}})")
        block.append("MERGE (p)-[:ENDS_IN]->(end)")
        
        # Add ALL facets (multi-facet support!)
        facet_types = set()
        for facet_label in data['facet_labels']:
            facet_type = INSTANCE_OF_MAPPING.get(facet_label.lower(), 'CulturalFacet')
            facet_types.add(facet_type)
        
        # If no facets found, default to Cultural
        if not facet_types:
            facet_types.add('CulturalFacet')
        
        # Create relationships for ALL facets
        for i, facet_type in enumerate(sorted(facet_types)):
            facet_label = facet_type.replace('Facet', '').lower()
            facet_unique_id = f"{facet_type.upper()}_{facet_label.upper()}"
            var_name = f"f{i}" if i > 0 else "f"
            
            block.append(f"MERGE ({var_name}:{facet_type}:Facet {{unique_id: '{facet_unique_id}'}})")
            block.append(f"SET {var_name}.label = '{facet_label}'")
            relationship = f"HAS_{facet_type.upper().replace('FACET', '')}_FACET"
            block.append(f"MERGE (p)-[:{relationship}]->({var_name})")
        
        # Add ALL locations
        for i, location_qid in enumerate(sorted(data['location_qids'])):
            var_name = f"geo{i}" if i > 0 else "geo"
            block.append(f"MERGE ({var_name}:Place {{qid: '{location_qid}'}})")
            block.append(f"MERGE (p)-[:LOCATED_IN]->({var_name})")
        
        # Join with spaces (executed as one transaction)
        lines.append(' '.join(block) + ';')
        lines.append('')
        
        if included_count % 25 == 0:
            print(f"   ✅ Generated {included_count} periods...")
    
    # Write to file
    with open(str(output_file), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n✅ Generated {output_file}")
    print(f"   Included: {included_count}")
    print(f"   Filtered - Events: {filtered_events}")
    print(f"   Filtered - No dates: {filtered_no_dates}")
    print(f"   Filtered - No location: {filtered_no_location}")
    print(f"   Filtered - Too old: {filtered_too_old}")

def main():
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent
    
    input_file = project_root / "Subjects" / "periods_import.cypher"
    output_file = project_root / "Subjects" / "periods_import_multi_facet.cypher"
    
    print("="*80)
    print("Period Enrichment - MULTI-FACET (Preserves All InstanceOf Data)")
    print("="*80)
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print()
    
    if not input_file.exists():
        print(f"❌ ERROR: File not found: {input_file}")
        sys.exit(1)
    
    # Parse and group by QID
    print("📊 Step 1: Parsing and grouping by QID...")
    period_groups = parse_periods_multi_facet(input_file)
    print(f"   Found {len(period_groups)} unique periods")
    
    # Show sample multi-facet period
    print("\n📊 Sample multi-facet period:")
    for qid, data in list(period_groups.items())[:1]:
        print(f"   {data['label']}")
        print(f"   Facets: {data['facet_labels']}")
        print(f"   Locations: {len(data['location_qids'])}")
    
    # Generate Cypher
    print("\n📝 Step 2: Generating Cypher with multiple facets...")
    generate_multi_facet_cypher(period_groups, output_file)
    
    print("\n" + "="*80)
    print("✅ Multi-facet enrichment complete!")
    print("="*80)

if __name__ == "__main__":
    main()

