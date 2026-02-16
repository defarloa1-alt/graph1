#!/usr/bin/env python3
"""
Wikidata Property Pattern Miner
Experimental: Mine empirical patterns of property usage by entity type

Purpose:
- Discover which properties are commonly used together for different entity types
- Generate type signatures (mandatory/common/rare properties per type)
- Inform validation constraints and agent hinting

Usage:
    python wikidata_property_pattern_miner.py --sample diverse  # Use diverse 30-QID sample
    python wikidata_property_pattern_miner.py --qids Q5,Q42,Q937  # Custom QIDs
    python wikidata_property_pattern_miner.py --type Q5 --limit 100  # Sample 100 humans

Output:
    - property_patterns_{timestamp}.json - Type signatures with coverage stats
    - property_patterns_{timestamp}.csv - Tabular view for analysis
"""

import requests
import json
import time
from collections import defaultdict, Counter
from typing import Dict, List, Set, Optional
import argparse
from datetime import datetime

# Diverse sample covering major types (from user's suggestion)
DIVERSE_SAMPLE_30 = [
    'Q5',      # human
    'Q42',     # Douglas Adams (human instance)
    'Q64',     # Berlin (city)
    'Q76',     # Barack Obama (human instance)
    'Q84',     # London (city)
    'Q100',    # Boston (city)
    'Q146',    # cat (taxon)
    'Q937',    # Albert Einstein (human instance)
    'Q11424',  # film
    'Q1860',   # English language
    'Q2013',   # Wikidata
    'Q2221906',# geographic location
    'Q43229',  # organization
    'Q4628',   # Faroe Islands
    'Q571',    # book
    'Q618123', # geographic feature
    'Q6256',   # country
    'Q801',    # Israel
    'Q11451',  # acid (chemical)
    'Q159',    # Russia
    'Q30',     # United States
    'Q16',     # Canada
    'Q183',    # Germany
    'Q90',     # Paris
    'Q34',     # Sweden
    'Q60',     # New York City
    'Q7186',   # chemical element
    'Q11410',  # game
    'Q11423',  # video game
    'Q523'     # star
]

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "Graph1PropertyPatternMiner/1.0 (Chrystallum Knowledge Graph)"

class PropertyPatternMiner:
    """Mine property usage patterns from Wikidata entities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
        # Storage
        self.entities = {}  # qid -> entity data
        self.type_to_items = defaultdict(list)  # type_qid -> [item_qids]
        self.type_to_properties = defaultdict(lambda: defaultdict(int))  # type_qid -> {prop_id: count}
        self.type_labels = {}  # qid -> label
        self.property_labels = {}  # property_id -> label
        
    def fetch_entity(self, qid: str) -> Optional[Dict]:
        """Fetch entity with all properties from Wikidata API"""
        params = {
            'action': 'wbgetentities',
            'ids': qid,
            'format': 'json',
            'props': 'labels|descriptions|claims'
        }
        
        try:
            response = self.session.get(WIKIDATA_API, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'entities' in data and qid in data['entities']:
                entity = data['entities'][qid]
                if 'missing' not in entity:
                    return entity
        except Exception as e:
            print(f"  ⚠ Error fetching {qid}: {e}")
        
        return None
    
    def extract_properties_and_types(self, qid: str, entity: Dict) -> Dict:
        """Extract property list and instance-of types from entity"""
        result = {
            'qid': qid,
            'label': entity.get('labels', {}).get('en', {}).get('value', qid),
            'description': entity.get('description', {}).get('en', {}).get('value', ''),
            'properties': [],  # property IDs used
            'types': []  # P31 instance-of values
        }
        
        claims = entity.get('claims', {})
        
        # Extract all property IDs
        result['properties'] = list(claims.keys())
        
        # Extract P31 (instance of) types
        if 'P31' in claims:
            for statement in claims['P31']:
                try:
                    mainsnak = statement.get('mainsnak', {})
                    if mainsnak.get('datatype') == 'wikibase-item':
                        datavalue = mainsnak.get('datavalue', {})
                        value = datavalue.get('value', {})
                        type_qid = value.get('id')
                        if type_qid:
                            result['types'].append(type_qid)
                except Exception:
                    continue
        
        return result
    
    def fetch_batch(self, qids: List[str], batch_size: int = 50) -> None:
        """Fetch multiple entities in batches using batch API calls"""
        print(f"\n📥 Fetching {len(qids)} entities from Wikidata...")
        
        for i in range(0, len(qids), batch_size):
            batch = qids[i:i+batch_size]
            batch_num = i//batch_size + 1
            total_batches = (len(qids) + batch_size - 1) // batch_size
            print(f"  Batch {batch_num}/{total_batches}: {len(batch)} QIDs... ", end='', flush=True)
            
            # Batch API call (up to 50 entities at once)
            params = {
                'action': 'wbgetentities',
                'ids': '|'.join(batch),
                'format': 'json',
                'props': 'labels|descriptions|claims'
            }
            
            try:
                response = self.session.get(WIKIDATA_API, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                entities = data.get('entities', {})
                fetched = 0
                
                for qid in batch:
                    if qid in entities and 'missing' not in entities[qid]:
                        entity = entities[qid]
                        parsed = self.extract_properties_and_types(qid, entity)
                        self.entities[qid] = parsed
                        self.type_labels[qid] = parsed['label']
                        fetched += 1
                
                print(f"✓ {fetched}/{len(batch)}")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                # Fallback to individual fetching for this batch
                for qid in batch:
                    entity = self.fetch_entity(qid)
                    if entity:
                        parsed = self.extract_properties_and_types(qid, entity)
                        self.entities[qid] = parsed
                        self.type_labels[qid] = parsed['label']
                    time.sleep(0.1)
            
            time.sleep(0.5)  # Rate limiting between batches
        
        print(f"✓ Fetched {len(self.entities)} entities successfully")
    
    def build_type_mappings(self) -> None:
        """Group entities by their types and count property usage"""
        print("\n🔍 Building type → property mappings...")
        
        for qid, entity_data in self.entities.items():
            types = entity_data.get('types', [])
            properties = entity_data.get('properties', [])
            
            # If no P31 types, classify as "Unknown"
            if not types:
                types = ['Unknown']
            
            # For each type this entity has
            for type_qid in types:
                self.type_to_items[type_qid].append(qid)
                
                # Count property usage for this type
                for prop_id in properties:
                    self.type_to_properties[type_qid][prop_id] += 1
        
        print(f"✓ Found {len(self.type_to_items)} distinct types")
        for type_qid, items in self.type_to_items.items():
            type_label = self.type_labels.get(type_qid, type_qid)
            print(f"  {type_label} ({type_qid}): {len(items)} items")
    
    def calculate_coverage(self, type_qid: str, property_id: str) -> float:
        """Calculate coverage: fraction of items of this type that have this property"""
        total_items = len(self.type_to_items[type_qid])
        items_with_property = self.type_to_properties[type_qid][property_id]
        return items_with_property / total_items if total_items > 0 else 0.0
    
    def generate_type_signatures(self, min_coverage_mandatory: float = 0.9,
                                  min_coverage_common: float = 0.5) -> Dict:
        """Generate property signatures for each type"""
        print(f"\n📊 Generating type signatures...")
        print(f"  Mandatory threshold: {min_coverage_mandatory:.0%}")
        print(f"  Common threshold: {min_coverage_common:.0%}")
        
        signatures = {}
        
        for type_qid, items in self.type_to_items.items():
            type_label = self.type_labels.get(type_qid, type_qid)
            properties = self.type_to_properties[type_qid]
            
            # Calculate coverage for each property
            property_coverage = {}
            for prop_id, count in properties.items():
                coverage = self.calculate_coverage(type_qid, prop_id)
                property_coverage[prop_id] = coverage
            
            # Sort by coverage descending
            sorted_props = sorted(property_coverage.items(), key=lambda x: x[1], reverse=True)
            
            # Classify properties
            mandatory = [p for p, c in sorted_props if c >= min_coverage_mandatory]
            common = [p for p, c in sorted_props if min_coverage_common <= c < min_coverage_mandatory]
            optional = [p for p, c in sorted_props if c < min_coverage_common]
            
            signatures[type_qid] = {
                'type_qid': type_qid,
                'type_label': type_label,
                'sample_size': len(items),
                'sample_items': items[:5],  # First 5 as examples
                'total_properties': len(properties),
                'mandatory': {
                    'count': len(mandatory),
                    'properties': mandatory[:10],  # Top 10
                    'coverage': {p: property_coverage[p] for p in mandatory[:10]}
                },
                'common': {
                    'count': len(common),
                    'properties': common[:20],  # Top 20
                    'coverage': {p: property_coverage[p] for p in common[:20]}
                },
                'optional': {
                    'count': len(optional),
                    'properties': optional[:10],  # Top 10 by coverage
                    'coverage': {p: property_coverage[p] for p in optional[:10]}
                }
            }
        
        return signatures
    
    def export_results(self, signatures: Dict, output_prefix: str = "property_patterns") -> None:
        """Export signatures to JSON and CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON export (detailed)
        json_file = f"{output_prefix}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'timestamp': timestamp,
                    'total_entities': len(self.entities),
                    'total_types': len(signatures),
                    'user_agent': USER_AGENT
                },
                'signatures': signatures
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Exported JSON: {json_file}")
        
        # CSV export (flat statistics)
        csv_file = f"{output_prefix}_{timestamp}.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("type_qid,type_label,sample_size,total_properties,mandatory_count,common_count,optional_count,top_mandatory,top_common\n")
            
            for type_qid, sig in signatures.items():
                top_mandatory = ';'.join(sig['mandatory']['properties'][:5])
                top_common = ';'.join(sig['common']['properties'][:5])
                
                f.write(f"{type_qid},{sig['type_label']},{sig['sample_size']},{sig['total_properties']},"
                        f"{sig['mandatory']['count']},{sig['common']['count']},{sig['optional']['count']},"
                        f"\"{top_mandatory}\",\"{top_common}\"\n")
        
        print(f"✅ Exported CSV: {csv_file}")
    
    def print_summary(self, signatures: Dict, top_n: int = 3) -> None:
        """Print human-readable summary of top types"""
        print(f"\n{'='*80}")
        print(f"PROPERTY PATTERN SUMMARY (Top {top_n} Types by Sample Size)")
        print(f"{'='*80}\n")
        
        # Sort by sample size
        sorted_types = sorted(signatures.items(), key=lambda x: x[1]['sample_size'], reverse=True)
        
        for i, (type_qid, sig) in enumerate(sorted_types[:top_n], 1):
            print(f"{i}. {sig['type_label']} ({type_qid})")
            print(f"   Sample: {sig['sample_size']} items, {sig['total_properties']} distinct properties")
            
            print(f"\n   📌 Mandatory (≥90% coverage):")
            for prop in sig['mandatory']['properties'][:5]:
                coverage = sig['mandatory']['coverage'].get(prop, 0)
                print(f"      {prop}: {coverage:.1%}")
            
            print(f"\n   ⭐ Common (50-90% coverage):")
            for prop in sig['common']['properties'][:5]:
                coverage = sig['common']['coverage'].get(prop, 0)
                print(f"      {prop}: {coverage:.1%}")
            
            print()


def main():
    parser = argparse.ArgumentParser(description="Mine property usage patterns from Wikidata")
    parser.add_argument('--sample', choices=['diverse'], default=None,
                        help="Use predefined sample (diverse = 30 mixed entity types)")
    parser.add_argument('--qids', type=str,
                        help="Comma-separated list of QIDs (e.g., Q5,Q42,Q937)")
    parser.add_argument('--file', type=str,
                        help="File containing QIDs (one per line)")
    parser.add_argument('--output', default='property_patterns',
                        help="Output file prefix (default: property_patterns)")
    parser.add_argument('--mandatory-threshold', type=float, default=0.9,
                        help="Coverage threshold for mandatory properties (default: 0.9)")
    parser.add_argument('--common-threshold', type=float, default=0.5,
                        help="Coverage threshold for common properties (default: 0.5)")
    
    args = parser.parse_args()
    
    # Determine QIDs to process
    if args.file:
        print(f"📂 Loading QIDs from {args.file}...")
        with open(args.file, 'r') as f:
            qids = [line.strip() for line in f if line.strip() and line.strip().startswith('Q')]
        print(f"✓ Loaded {len(qids)} QIDs")
    elif args.qids:
        qids = [q.strip() for q in args.qids.split(',')]
    elif args.sample == 'diverse':
        qids = DIVERSE_SAMPLE_30
    else:
        print("❌ No QIDs specified. Use --qids, --file, or --sample")
        return
    
    print(f"{'='*80}")
    print(f"Wikidata Property Pattern Miner")
    print(f"{'='*80}")
    print(f"Sample: {len(qids)} QIDs")
    print(f"Mandatory threshold: {args.mandatory_threshold:.0%}")
    print(f"Common threshold: {args.common_threshold:.0%}")
    
    # Run mining
    miner = PropertyPatternMiner()
    miner.fetch_batch(qids)
    miner.build_type_mappings()
    signatures = miner.generate_type_signatures(
        min_coverage_mandatory=args.mandatory_threshold,
        min_coverage_common=args.common_threshold
    )
    
    # Export and display
    miner.export_results(signatures, args.output)
    miner.print_summary(signatures, top_n=5)
    
    print(f"\n{'='*80}")
    print("✅ Property pattern mining complete")
    print(f"{'='*80}\n")
    
    print("💡 Next steps:")
    print("   1. Review JSON file for detailed property signatures")
    print("   2. Integrate patterns into facet_agent_framework.py validation")
    print("   3. Use as hints for federation discovery (Step 3)")
    print("   4. Generate Neo4j shape constraints from patterns")


if __name__ == '__main__':
    main()
