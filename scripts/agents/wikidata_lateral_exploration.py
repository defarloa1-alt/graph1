#!/usr/bin/env python3
"""
Wikidata Lateral Exploration - Find Related Entities

From a root QID (e.g., Q17167 Roman Republic), explore LATERAL relationships:

PLACES:
- P36 (capital)
- P276 (location)
- P706 (located in/on physical feature)
- P1001 (applies to jurisdiction)

PEOPLE:
- From P793 (events) → P710 (participant)
- From organizations → P488 (chairperson), P112 (founder)

EVENTS:
- P793 (significant event)
- P1344 (participant in)

ORGANIZATIONS:
- P194 (legislative body)
- P1308 (officeholder)

OBJECTS:
- P38 (currency)
- P186 (made from material)

For each found entity, fetch:
- QID + Label
- Check for Pleiades ID (P1584)
- Check for library IDs (P244, P2163)
- Basic properties
"""

import sys
from pathlib import Path
import json
import requests
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


LATERAL_PROPERTIES = {
    # Places
    'P36': 'capital',
    'P276': 'location',
    'P706': 'located in/on physical feature',
    'P47': 'shares border with',
    
    # Events
    'P793': 'significant event',
    'P1344': 'participant in',
    
    # Organizations
    'P194': 'legislative body',
    
    # Objects
    'P38': 'currency',
    
    # People (indirect - through events)
    'P1792': 'category of associated people'
}


class LateralExplorer:
    """Explore lateral relationships from root entity"""
    
    def __init__(self):
        self.entity_url = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.cache = {}
        
    def explore_lateral(self, root_qid: str) -> dict:
        """
        Explore all lateral relationships from root
        
        Returns:
            Dict with places, people, events, organizations, objects
        """
        
        print(f"\n{'='*80}")
        print(f"LATERAL EXPLORATION FROM: {root_qid}")
        print(f"{'='*80}\n")
        
        # Fetch root entity
        print(f"Fetching root entity...")
        root_data = self._fetch_entity(root_qid)
        
        if not root_data:
            raise ValueError(f"Failed to fetch {root_qid}")
        
        root_label = root_data.get('labels', {}).get('en', {}).get('value', root_qid)
        print(f"  Root: {root_label}\n")
        
        # Results
        results = {
            'root_qid': root_qid,
            'root_label': root_label,
            'timestamp': datetime.now().isoformat(),
            'places': [],
            'events': [],
            'organizations': [],
            'objects': [],
            'people_categories': [],
            'statistics': {}
        }
        
        claims = root_data.get('claims', {})
        
        # Explore each lateral property
        print(f"Exploring lateral properties...\n")
        
        # PLACES
        place_props = ['P36', 'P276', 'P706', 'P47']
        for prop in place_props:
            if prop in claims:
                prop_label = LATERAL_PROPERTIES.get(prop, prop)
                print(f"  {prop} ({prop_label})...")
                
                for claim in claims[prop]:
                    entity_id = self._extract_entity_id(claim)
                    if entity_id:
                        entity_data = self._fetch_basic_data(entity_id)
                        if entity_data:
                            entity_data['relationship'] = prop
                            entity_data['relationship_label'] = prop_label
                            results['places'].append(entity_data)
                            print(f"    -> {entity_id} ({entity_data['label']})")
        
        # EVENTS
        event_props = ['P793', 'P1344']
        for prop in event_props:
            if prop in claims:
                prop_label = LATERAL_PROPERTIES.get(prop, prop)
                print(f"  {prop} ({prop_label})...")
                
                for claim in claims[prop]:
                    entity_id = self._extract_entity_id(claim)
                    if entity_id:
                        entity_data = self._fetch_basic_data(entity_id)
                        if entity_data:
                            entity_data['relationship'] = prop
                            entity_data['relationship_label'] = prop_label
                            results['events'].append(entity_data)
                            print(f"    -> {entity_id} ({entity_data['label']})")
        
        # ORGANIZATIONS
        org_props = ['P194']
        for prop in org_props:
            if prop in claims:
                prop_label = LATERAL_PROPERTIES.get(prop, prop)
                print(f"  {prop} ({prop_label})...")
                
                for claim in claims[prop]:
                    entity_id = self._extract_entity_id(claim)
                    if entity_id:
                        entity_data = self._fetch_basic_data(entity_id)
                        if entity_data:
                            entity_data['relationship'] = prop
                            entity_data['relationship_label'] = prop_label
                            results['organizations'].append(entity_data)
                            print(f"    -> {entity_id} ({entity_data['label']})")
        
        # OBJECTS
        obj_props = ['P38']
        for prop in obj_props:
            if prop in claims:
                prop_label = LATERAL_PROPERTIES.get(prop, prop)
                print(f"  {prop} ({prop_label})...")
                
                for claim in claims[prop]:
                    entity_id = self._extract_entity_id(claim)
                    if entity_id:
                        entity_data = self._fetch_basic_data(entity_id)
                        if entity_data:
                            entity_data['relationship'] = prop
                            entity_data['relationship_label'] = prop_label
                            results['objects'].append(entity_data)
                            print(f"    -> {entity_id} ({entity_data['label']})")
        
        # PEOPLE CATEGORIES
        people_props = ['P1792']
        for prop in people_props:
            if prop in claims:
                prop_label = LATERAL_PROPERTIES.get(prop, prop)
                print(f"  {prop} ({prop_label})...")
                
                for claim in claims[prop]:
                    entity_id = self._extract_entity_id(claim)
                    if entity_id:
                        entity_data = self._fetch_basic_data(entity_id)
                        if entity_data:
                            entity_data['relationship'] = prop
                            entity_data['relationship_label'] = prop_label
                            results['people_categories'].append(entity_data)
                            print(f"    -> {entity_id} ({entity_data['label']})")
        
        # Calculate statistics
        results['statistics'] = {
            'total_lateral_entities': (
                len(results['places']) + 
                len(results['events']) + 
                len(results['organizations']) + 
                len(results['objects']) +
                len(results['people_categories'])
            ),
            'places': len(results['places']),
            'events': len(results['events']),
            'organizations': len(results['organizations']),
            'objects': len(results['objects']),
            'people_categories': len(results['people_categories'])
        }
        
        return results
    
    def _fetch_entity(self, qid: str) -> dict:
        """Fetch complete entity data"""
        
        url = self.entity_url.format(qid=qid)
        
        response = requests.get(url, headers={
            'User-Agent': 'Chrystallum/1.0 (research project)'
        })
        response.raise_for_status()
        
        data = response.json()
        return data.get('entities', {}).get(qid, {})
    
    def _fetch_basic_data(self, qid: str) -> dict:
        """Fetch basic data for an entity + check for authority IDs"""
        
        if qid in self.cache:
            return self.cache[qid]
        
        try:
            entity = self._fetch_entity(qid)
            
            labels = entity.get('labels', {})
            descriptions = entity.get('descriptions', {})
            claims = entity.get('claims', {})
            
            # Check for authority IDs
            authorities = {}
            
            # Pleiades
            if 'P1584' in claims:
                pleiades_val = claims['P1584'][0].get('mainsnak', {}).get('datavalue', {}).get('value')
                authorities['pleiades_id'] = pleiades_val
            
            # Getty TGN
            if 'P1667' in claims:
                tgn_val = claims['P1667'][0].get('mainsnak', {}).get('datavalue', {}).get('value')
                authorities['tgn_id'] = tgn_val
            
            # LCSH
            if 'P244' in claims:
                lcsh_val = claims['P244'][0].get('mainsnak', {}).get('datavalue', {}).get('value')
                authorities['lcsh_id'] = lcsh_val
            
            # FAST
            if 'P2163' in claims:
                fast_val = claims['P2163'][0].get('mainsnak', {}).get('datavalue', {}).get('value')
                authorities['fast_id'] = fast_val
            
            # LCC
            if 'P1149' in claims:
                lcc_val = claims['P1149'][0].get('mainsnak', {}).get('datavalue', {}).get('value')
                authorities['lcc'] = lcc_val
            
            # P31 (instance of) for classification
            instance_of = []
            if 'P31' in claims:
                for claim in claims['P31'][:3]:  # First 3
                    val = self._extract_entity_id(claim)
                    if val:
                        instance_of.append(val)
            
            basic_data = {
                'qid': qid,
                'label': labels.get('en', {}).get('value', qid),
                'description': descriptions.get('en', {}).get('value', ''),
                'instance_of': instance_of,
                'authorities': authorities,
                'has_authorities': len(authorities) > 0
            }
            
            self.cache[qid] = basic_data
            return basic_data
            
        except Exception as e:
            print(f"      Error fetching {qid}: {e}")
            return None
    
    def _extract_entity_id(self, claim: dict) -> str:
        """Extract entity ID from claim"""
        
        datavalue = claim.get('mainsnak', {}).get('datavalue', {})
        
        if datavalue.get('type') == 'wikibase-entityid':
            return datavalue.get('value', {}).get('id', '')
        
        return None
    
    def print_results(self, results: dict):
        """Print exploration results"""
        
        stats = results['statistics']
        
        print(f"\n{'='*80}")
        print(f"LATERAL EXPLORATION RESULTS")
        print(f"{'='*80}\n")
        
        print(f"Root: {results['root_qid']} ({results['root_label']})")
        print(f"Total lateral entities: {stats['total_lateral_entities']}\n")
        
        print(f"BREAKDOWN:")
        print(f"  Places: {stats['places']}")
        print(f"  Events: {stats['events']}")
        print(f"  Organizations: {stats['organizations']}")
        print(f"  Objects: {stats['objects']}")
        print(f"  People categories: {stats['people_categories']}")
        print()
        
        # Show each category
        if results['places']:
            print(f"{'='*80}")
            print(f"PLACES ({len(results['places'])})")
            print(f"{'='*80}\n")
            for place in results['places']:
                auth_str = ", ".join([f"{k}={v}" for k, v in place['authorities'].items()]) if place['authorities'] else "No authorities"
                print(f"{place['qid']} - {place['label']}")
                print(f"  Via: {place['relationship_label']}")
                print(f"  Authorities: {auth_str}")
                print()
        
        if results['events']:
            print(f"{'='*80}")
            print(f"EVENTS ({len(results['events'])})")
            print(f"{'='*80}\n")
            for event in results['events']:
                auth_str = ", ".join([f"{k}={v}" for k, v in event['authorities'].items()]) if event['authorities'] else "No authorities"
                print(f"{event['qid']} - {event['label']}")
                print(f"  Via: {event['relationship_label']}")
                print(f"  Authorities: {auth_str}")
                print()
        
        if results['organizations']:
            print(f"{'='*80}")
            print(f"ORGANIZATIONS ({len(results['organizations'])})")
            print(f"{'='*80}\n")
            for org in results['organizations']:
                print(f"{org['qid']} - {org['label']}")
                print(f"  Via: {org['relationship_label']}")
                print()
        
        if results['objects']:
            print(f"{'='*80}")
            print(f"OBJECTS ({len(results['objects'])})")
            print(f"{'='*80}\n")
            for obj in results['objects']:
                print(f"{obj['qid']} - {obj['label']}")
                print(f"  Via: {obj['relationship_label']}")
                print()
    
    def save_results(self, results: dict, output_filename: str = None):
        """Save results to JSON"""
        
        if not output_filename:
            qid = results['root_qid']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"output/lateral/{qid}_lateral_{timestamp}.json"
        
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved: {output_path}")
        
        return str(output_path)
    
    def run_exploration(self, root_qid: str):
        """Run complete lateral exploration"""
        
        print(f"\n{'='*80}")
        print(f"LATERAL RELATIONSHIP EXPLORER")
        print(f"{'='*80}")
        
        # Explore
        results = self.explore_lateral(root_qid)
        
        # Print
        self.print_results(results)
        
        # Save
        json_path = self.save_results(results)
        
        print(f"\n{'='*80}")
        print(f"EXPLORATION COMPLETE")
        print(f"{'='*80}\n")
        print(f"File: {json_path}")
        print(f"Total entities: {results['statistics']['total_lateral_entities']}")
        
        return results


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    
    root_qid = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    
    explorer = LateralExplorer()
    results = explorer.run_exploration(root_qid)
    
    # Summary
    stats = results['statistics']
    print(f"\nSUMMARY:")
    print(f"  Places: {stats['places']} (check for Pleiades IDs!)")
    print(f"  Events: {stats['events']}")
    print(f"  Organizations: {stats['organizations']}")
    print(f"  Objects: {stats['objects']}")


if __name__ == "__main__":
    main()
