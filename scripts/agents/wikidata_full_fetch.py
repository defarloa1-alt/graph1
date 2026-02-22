#!/usr/bin/env python3
"""
Wikidata Full Entity Fetch - Get ALL data for a QID

Fetches complete entity data from Wikidata API including:
- Labels (all languages)
- Descriptions (all languages)
- Aliases (all languages)
- Claims/Statements (all properties and values)
- External identifiers (VIAF, LCNAF, GND, etc.)
- Sitelinks (Wikipedia articles in all languages)
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime


class WikidataFullFetcher:
    """Fetch complete entity data from Wikidata API"""
    
    def __init__(self):
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.entity_url = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        
    def fetch_entity_full(self, qid: str) -> Dict:
        """
        Fetch complete entity data for a QID
        
        Args:
            qid: Wikidata QID (e.g., 'Q17167')
        
        Returns:
            Complete entity data dict
        """
        # Clean QID
        qid = qid.strip().upper()
        if not qid.startswith('Q'):
            qid = f'Q{qid}'
        
        print(f"\n{'='*80}")
        print(f"FETCHING COMPLETE DATA FOR: {qid}")
        print(f"{'='*80}\n")
        
        # Method 1: Use EntityData endpoint (most complete)
        url = self.entity_url.format(qid=qid)
        
        print(f"Fetching from: {url}")
        
        response = requests.get(url, headers={
            'User-Agent': 'Chrystallum/1.0 (research project)'
        })
        response.raise_for_status()
        
        data = response.json()
        
        # Extract entity from response
        entity = data.get('entities', {}).get(qid, {})
        
        if not entity:
            raise ValueError(f"QID {qid} not found in Wikidata")
        
        # Parse and structure the data
        structured = self._structure_entity_data(qid, entity)
        
        return structured
    
    def _structure_entity_data(self, qid: str, entity: Dict) -> Dict:
        """Structure raw entity data into organized format"""
        
        structured = {
            'qid': qid,
            'fetch_timestamp': datetime.utcnow().isoformat(),
            'labels': {},
            'descriptions': {},
            'aliases': {},
            'claims': {},
            'external_identifiers': {},
            'sitelinks': {},
            'statistics': {}
        }
        
        # 1. LABELS (all languages)
        print("Extracting labels...")
        labels = entity.get('labels', {})
        for lang, label_obj in labels.items():
            structured['labels'][lang] = label_obj.get('value', '')
        
        print(f"  Found {len(structured['labels'])} labels")
        
        # 2. DESCRIPTIONS (all languages)
        print("Extracting descriptions...")
        descriptions = entity.get('descriptions', {})
        for lang, desc_obj in descriptions.items():
            structured['descriptions'][lang] = desc_obj.get('value', '')
        
        print(f"  Found {len(structured['descriptions'])} descriptions")
        
        # 3. ALIASES (all languages)
        print("Extracting aliases...")
        aliases = entity.get('aliases', {})
        for lang, alias_list in aliases.items():
            structured['aliases'][lang] = [a.get('value', '') for a in alias_list]
        
        total_aliases = sum(len(a) for a in structured['aliases'].values())
        print(f"  Found {total_aliases} aliases across {len(structured['aliases'])} languages")
        
        # 4. CLAIMS/STATEMENTS (all properties)
        print("Extracting claims/properties...")
        claims = entity.get('claims', {})
        
        for prop_id, claim_list in claims.items():
            structured['claims'][prop_id] = []
            
            for claim in claim_list:
                claim_data = self._parse_claim(claim)
                structured['claims'][prop_id].append(claim_data)
                
                # Track external identifiers separately
                if self._is_external_identifier(prop_id):
                    if prop_id not in structured['external_identifiers']:
                        structured['external_identifiers'][prop_id] = []
                    structured['external_identifiers'][prop_id].append(claim_data['value'])
        
        print(f"  Found {len(structured['claims'])} properties")
        print(f"  Found {len(structured['external_identifiers'])} external identifier types")
        
        # 5. SITELINKS (Wikipedia articles)
        print("Extracting sitelinks...")
        sitelinks = entity.get('sitelinks', {})
        for site, link_obj in sitelinks.items():
            structured['sitelinks'][site] = {
                'title': link_obj.get('title', ''),
                'url': link_obj.get('url', '')
            }
        
        print(f"  Found {len(structured['sitelinks'])} sitelinks")
        
        # 6. STATISTICS
        structured['statistics'] = {
            'total_labels': len(structured['labels']),
            'total_descriptions': len(structured['descriptions']),
            'total_aliases': total_aliases,
            'total_properties': len(structured['claims']),
            'total_external_ids': len(structured['external_identifiers']),
            'total_sitelinks': len(structured['sitelinks']),
            'total_statements': sum(len(v) for v in structured['claims'].values())
        }
        
        return structured
    
    def _parse_claim(self, claim: Dict) -> Dict:
        """Parse a single claim/statement"""
        
        mainsnak = claim.get('mainsnak', {})
        datatype = mainsnak.get('datatype', '')
        datavalue = mainsnak.get('datavalue', {})
        
        claim_data = {
            'type': datatype,
            'value': None,
            'value_type': datavalue.get('type', ''),
            'rank': claim.get('rank', 'normal'),
            'qualifiers': {},
            'references': []
        }
        
        # Parse value based on type
        if datavalue.get('type') == 'wikibase-entityid':
            entity_id = datavalue.get('value', {}).get('id', '')
            claim_data['value'] = entity_id
            
        elif datavalue.get('type') == 'string':
            claim_data['value'] = datavalue.get('value', '')
            
        elif datavalue.get('type') == 'time':
            time_value = datavalue.get('value', {})
            claim_data['value'] = time_value.get('time', '')
            claim_data['precision'] = time_value.get('precision', 0)
            
        elif datavalue.get('type') == 'quantity':
            quantity_value = datavalue.get('value', {})
            claim_data['value'] = quantity_value.get('amount', '')
            claim_data['unit'] = quantity_value.get('unit', '')
            
        elif datavalue.get('type') == 'monolingualtext':
            mono_value = datavalue.get('value', {})
            claim_data['value'] = mono_value.get('text', '')
            claim_data['language'] = mono_value.get('language', '')
            
        elif datavalue.get('type') == 'globecoordinate':
            coord_value = datavalue.get('value', {})
            claim_data['value'] = {
                'latitude': coord_value.get('latitude', 0),
                'longitude': coord_value.get('longitude', 0),
                'precision': coord_value.get('precision', 0)
            }
        else:
            # Raw value for other types
            claim_data['value'] = datavalue.get('value')
        
        # Parse qualifiers
        qualifiers = claim.get('qualifiers', {})
        for qual_prop, qual_list in qualifiers.items():
            claim_data['qualifiers'][qual_prop] = [
                self._parse_snak(q) for q in qual_list
            ]
        
        # Parse references
        references = claim.get('references', [])
        for ref in references:
            ref_data = {}
            for ref_prop, ref_snaks in ref.get('snaks', {}).items():
                ref_data[ref_prop] = [self._parse_snak(s) for s in ref_snaks]
            claim_data['references'].append(ref_data)
        
        return claim_data
    
    def _parse_snak(self, snak: Dict) -> any:
        """Parse a snak (used in qualifiers and references)"""
        datavalue = snak.get('datavalue', {})
        
        if datavalue.get('type') == 'wikibase-entityid':
            return datavalue.get('value', {}).get('id', '')
        elif datavalue.get('type') == 'string':
            return datavalue.get('value', '')
        elif datavalue.get('type') == 'time':
            return datavalue.get('value', {}).get('time', '')
        else:
            return datavalue.get('value')
    
    def _is_external_identifier(self, prop_id: str) -> bool:
        """Check if property is an external identifier"""
        # Common external identifier properties start with P and are in certain ranges
        # This is a heuristic - you can expand this list
        external_id_props = {
            'P214',  # VIAF ID
            'P227',  # GND ID
            'P244',  # LCNAF ID
            'P268',  # BnF ID
            'P269',  # SUDOC ID
            'P345',  # IMDb ID
            'P396',  # SBN ID
            'P409',  # NLA ID
            'P646',  # Freebase ID
            'P691',  # NKCR ID
            'P906',  # SELIBR ID
            'P950',  # BNE ID
            'P1015', # NORAF ID
            'P1017', # BAV ID
            'P1050', # Filmportal ID
            'P1233', # ISFDB ID
            'P1566', # GeoNames ID
            'P2163', # FAST ID
            'P2427', # grid ID
            'P3348', # NLG ID
            'P4342', # Store norske leksikon ID
            'P7859', # WorldCat ID
        }
        
        return prop_id in external_id_props
    
    def get_property_labels(self, prop_ids: List[str]) -> Dict[str, str]:
        """
        Fetch labels for property IDs
        
        Args:
            prop_ids: List of property IDs (e.g., ['P31', 'P279'])
        
        Returns:
            Dict mapping property IDs to English labels
        """
        if not prop_ids:
            return {}
        
        # Wikidata API to get property labels
        params = {
            'action': 'wbgetentities',
            'ids': '|'.join(prop_ids[:50]),  # Max 50 at a time
            'props': 'labels',
            'languages': 'en',
            'format': 'json'
        }
        
        response = requests.get(self.api_url, params=params, headers={
            'User-Agent': 'Chrystallum/1.0 (research project)'
        })
        response.raise_for_status()
        
        data = response.json()
        
        labels = {}
        for prop_id, entity in data.get('entities', {}).items():
            label = entity.get('labels', {}).get('en', {}).get('value', prop_id)
            labels[prop_id] = label
        
        return labels
    
    def print_summary(self, structured: Dict):
        """Print a summary of fetched data"""
        
        stats = structured['statistics']
        
        print(f"\n{'='*80}")
        print(f"FETCH SUMMARY FOR: {structured['qid']}")
        print(f"{'='*80}\n")
        
        print(f"STATISTICS:")
        print(f"  Labels:              {stats['total_labels']} languages")
        print(f"  Descriptions:        {stats['total_descriptions']} languages")
        print(f"  Aliases:             {stats['total_aliases']} total")
        print(f"  Properties:          {stats['total_properties']} unique")
        print(f"  Total Statements:    {stats['total_statements']}")
        print(f"  External IDs:        {stats['total_external_ids']} types")
        print(f"  Sitelinks:           {stats['total_sitelinks']} (Wikipedia articles)")
        
        print(f"\nMAIN LABEL (English):")
        print(f"  {structured['labels'].get('en', 'N/A')}")
        
        print(f"\nDESCRIPTION (English):")
        print(f"  {structured['descriptions'].get('en', 'N/A')}")
        
        if structured['aliases'].get('en'):
            print(f"\nALIASES (English, first 5):")
            for alias in structured['aliases']['en'][:5]:
                print(f"  - {alias}")
        
        if structured['external_identifiers']:
            print(f"\nEXTERNAL IDENTIFIERS:")
            for prop_id, values in list(structured['external_identifiers'].items())[:10]:
                print(f"  {prop_id}: {', '.join(str(v) for v in values[:3])}")
        
        if structured['sitelinks']:
            print(f"\nWIKIPEDIA ARTICLES (first 5):")
            for site, link_data in list(structured['sitelinks'].items())[:5]:
                try:
                    print(f"  {site}: {link_data['title']}")
                except UnicodeEncodeError:
                    print(f"  {site}: {link_data['title'].encode('ascii', 'replace').decode('ascii')}")
        
        print(f"\n{'='*80}\n")
    
    def save_to_json(self, structured: Dict, filename: Optional[str] = None):
        """Save structured data to JSON file"""
        
        if not filename:
            qid = structured['qid']
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"output/wikidata/{qid}_{timestamp}.json"
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(structured, f, indent=2, ensure_ascii=False)
        
        print(f"SAVED to: {filename}")
        
        return filename


# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_fetch_qid(qid: str):
    """Test fetching a QID"""
    
    fetcher = WikidataFullFetcher()
    
    try:
        # Fetch complete data
        data = fetcher.fetch_entity_full(qid)
        
        # Print summary
        fetcher.print_summary(data)
        
        # Save to JSON
        filename = fetcher.save_to_json(data)
        
        # Get property labels for first 20 properties
        prop_ids = list(data['claims'].keys())[:20]
        if prop_ids:
            print("\nPROPERTY LABELS (first 20):")
            labels = fetcher.get_property_labels(prop_ids)
            for prop_id in prop_ids:
                count = len(data['claims'][prop_id])
                print(f"  {prop_id} ({labels.get(prop_id, 'Unknown')}): {count} statement(s)")
        
        return data
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Test with Roman Republic (Q17167) by default
    qid = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    
    print(f"Testing Wikidata Full Fetch with QID: {qid}")
    
    test_fetch_qid(qid)
