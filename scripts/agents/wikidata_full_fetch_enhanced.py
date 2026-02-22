#!/usr/bin/env python3
"""
Wikidata Full Entity Fetch - ENHANCED with Label Resolution

Fetches complete entity data AND resolves all QID references to labels:
- Property labels (P31 -> "instance of")
- Value labels (Q11514315 -> "historical country")
- Qualifier labels
- Reference labels
"""

import requests
import json
from typing import Dict, List, Optional, Set
from datetime import datetime
from collections import defaultdict


class WikidataEnhancedFetcher:
    """Fetch complete entity data with ALL labels resolved"""
    
    def __init__(self):
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.entity_url = "https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        
        # Cache for labels to avoid repeated API calls
        self.label_cache = {}
        
    def fetch_entity_with_labels(self, qid: str) -> Dict:
        """
        Fetch complete entity data with ALL labels resolved
        
        Args:
            qid: Wikidata QID (e.g., 'Q17167')
        
        Returns:
            Complete entity data dict with labels
        """
        # Clean QID
        qid = qid.strip().upper()
        if not qid.startswith('Q'):
            qid = f'Q{qid}'
        
        print(f"\n{'='*80}")
        print(f"FETCHING COMPLETE DATA WITH LABELS FOR: {qid}")
        print(f"{'='*80}\n")
        
        # Fetch entity data
        url = self.entity_url.format(qid=qid)
        
        print(f"Step 1: Fetching entity data...")
        
        response = requests.get(url, headers={
            'User-Agent': 'Chrystallum/1.0 (research project)'
        })
        response.raise_for_status()
        
        data = response.json()
        entity = data.get('entities', {}).get(qid, {})
        
        if not entity:
            raise ValueError(f"QID {qid} not found in Wikidata")
        
        # Structure the data
        print(f"Step 2: Structuring entity data...")
        structured = self._structure_entity_data(qid, entity)
        
        # Collect all QIDs that need labels
        print(f"Step 3: Collecting all referenced QIDs...")
        all_qids = self._collect_all_qids(structured)
        
        print(f"  Found {len(all_qids)} unique QIDs to resolve")
        
        # Fetch all labels in batches
        print(f"Step 4: Fetching labels for all QIDs...")
        self._fetch_labels_batch(all_qids)
        
        # Resolve all labels in the data
        print(f"Step 5: Resolving labels in data structure...")
        enhanced = self._resolve_all_labels(structured)
        
        print(f"\nDONE! Data fully enhanced with labels")
        
        return enhanced
    
    def _structure_entity_data(self, qid: str, entity: Dict) -> Dict:
        """Structure raw entity data (same as before)"""
        
        structured = {
            'qid': qid,
            'fetch_timestamp': datetime.utcnow().isoformat(),
            'labels': {},
            'descriptions': {},
            'aliases': {},
            'claims': {},
            'sitelinks': {},
            'statistics': {}
        }
        
        # Labels
        labels = entity.get('labels', {})
        for lang, label_obj in labels.items():
            structured['labels'][lang] = label_obj.get('value', '')
        
        # Descriptions
        descriptions = entity.get('descriptions', {})
        for lang, desc_obj in descriptions.items():
            structured['descriptions'][lang] = desc_obj.get('value', '')
        
        # Aliases
        aliases = entity.get('aliases', {})
        for lang, alias_list in aliases.items():
            structured['aliases'][lang] = [a.get('value', '') for a in alias_list]
        
        # Claims
        claims = entity.get('claims', {})
        for prop_id, claim_list in claims.items():
            structured['claims'][prop_id] = []
            
            for claim in claim_list:
                claim_data = self._parse_claim(claim)
                structured['claims'][prop_id].append(claim_data)
        
        # Sitelinks
        sitelinks = entity.get('sitelinks', {})
        for site, link_obj in sitelinks.items():
            structured['sitelinks'][site] = {
                'title': link_obj.get('title', ''),
                'url': link_obj.get('url', '')
            }
        
        # Statistics
        total_aliases = sum(len(a) for a in structured['aliases'].values())
        structured['statistics'] = {
            'total_labels': len(structured['labels']),
            'total_descriptions': len(structured['descriptions']),
            'total_aliases': total_aliases,
            'total_properties': len(structured['claims']),
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
    
    def _collect_all_qids(self, structured: Dict) -> Set[str]:
        """Collect all QIDs that need label resolution"""
        qids = set()
        
        # Collect from claims
        for prop_id, claim_list in structured['claims'].items():
            # Property ID itself (P31, P279, etc.)
            qids.add(prop_id)
            
            for claim in claim_list:
                # Main value if it's a QID
                if isinstance(claim['value'], str) and (
                    claim['value'].startswith('Q') or claim['value'].startswith('P')
                ):
                    qids.add(claim['value'])
                
                # Qualifiers
                for qual_prop, qual_values in claim['qualifiers'].items():
                    qids.add(qual_prop)
                    for val in qual_values:
                        if isinstance(val, str) and (val.startswith('Q') or val.startswith('P')):
                            qids.add(val)
                
                # References
                for ref in claim['references']:
                    for ref_prop, ref_values in ref.items():
                        qids.add(ref_prop)
                        for val in ref_values:
                            if isinstance(val, str) and (val.startswith('Q') or val.startswith('P')):
                                qids.add(val)
        
        return qids
    
    def _fetch_labels_batch(self, qids: Set[str], batch_size: int = 50):
        """Fetch labels for QIDs in batches"""
        
        qid_list = list(qids)
        total_batches = (len(qid_list) + batch_size - 1) // batch_size
        
        for i in range(0, len(qid_list), batch_size):
            batch = qid_list[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"  Batch {batch_num}/{total_batches}: Fetching {len(batch)} labels...")
            
            params = {
                'action': 'wbgetentities',
                'ids': '|'.join(batch),
                'props': 'labels',
                'languages': 'en',
                'format': 'json'
            }
            
            response = requests.get(self.api_url, params=params, headers={
                'User-Agent': 'Chrystallum/1.0 (research project)'
            })
            response.raise_for_status()
            
            data = response.json()
            
            for entity_id, entity in data.get('entities', {}).items():
                label = entity.get('labels', {}).get('en', {}).get('value', entity_id)
                self.label_cache[entity_id] = label
    
    def _resolve_all_labels(self, structured: Dict) -> Dict:
        """Resolve all QID references to labels in the structured data"""
        
        enhanced = structured.copy()
        enhanced['claims_with_labels'] = {}
        
        for prop_id, claim_list in structured['claims'].items():
            prop_label = self.label_cache.get(prop_id, prop_id)
            
            enhanced['claims_with_labels'][prop_id] = {
                'property_id': prop_id,
                'property_label': prop_label,
                'statements': []
            }
            
            for claim in claim_list:
                enhanced_claim = claim.copy()
                
                # Resolve main value label if it's a QID
                if isinstance(claim['value'], str) and claim['value'].startswith('Q'):
                    enhanced_claim['value_label'] = self.label_cache.get(claim['value'], claim['value'])
                
                # Resolve qualifier labels
                enhanced_claim['qualifiers_with_labels'] = {}
                for qual_prop, qual_values in claim['qualifiers'].items():
                    qual_prop_label = self.label_cache.get(qual_prop, qual_prop)
                    
                    enhanced_qual_values = []
                    for val in qual_values:
                        if isinstance(val, str) and val.startswith('Q'):
                            enhanced_qual_values.append({
                                'value': val,
                                'label': self.label_cache.get(val, val)
                            })
                        else:
                            enhanced_qual_values.append({'value': val})
                    
                    enhanced_claim['qualifiers_with_labels'][qual_prop] = {
                        'property_id': qual_prop,
                        'property_label': qual_prop_label,
                        'values': enhanced_qual_values
                    }
                
                # Resolve reference labels
                enhanced_claim['references_with_labels'] = []
                for ref in claim['references']:
                    enhanced_ref = {}
                    for ref_prop, ref_values in ref.items():
                        ref_prop_label = self.label_cache.get(ref_prop, ref_prop)
                        
                        enhanced_ref_values = []
                        for val in ref_values:
                            if isinstance(val, str) and val.startswith('Q'):
                                enhanced_ref_values.append({
                                    'value': val,
                                    'label': self.label_cache.get(val, val)
                                })
                            else:
                                enhanced_ref_values.append({'value': val})
                        
                        enhanced_ref[ref_prop] = {
                            'property_id': ref_prop,
                            'property_label': ref_prop_label,
                            'values': enhanced_ref_values
                        }
                    
                    enhanced_claim['references_with_labels'].append(enhanced_ref)
                
                enhanced['claims_with_labels'][prop_id]['statements'].append(enhanced_claim)
        
        return enhanced
    
    def print_enhanced_summary(self, enhanced: Dict):
        """Print summary with all labels resolved"""
        
        stats = enhanced['statistics']
        
        print(f"\n{'='*80}")
        print(f"ENHANCED SUMMARY FOR: {enhanced['qid']}")
        print(f"{'='*80}\n")
        
        print(f"LABEL: {enhanced['labels'].get('en', 'N/A')}")
        print(f"DESCRIPTION: {enhanced['descriptions'].get('en', 'N/A')}\n")
        
        print(f"STATISTICS:")
        print(f"  Total properties: {stats['total_properties']}")
        print(f"  Total statements: {stats['total_statements']}")
        print(f"  Labels resolved: {len(self.label_cache)}\n")
        
        # Show top 20 properties with labels
        print(f"TOP 20 PROPERTIES (WITH LABELS):\n")
        
        count = 0
        for prop_id, prop_data in list(enhanced['claims_with_labels'].items())[:20]:
            prop_label = prop_data['property_label']
            num_statements = len(prop_data['statements'])
            
            print(f"{prop_id} ({prop_label}): {num_statements} statement(s)")
            
            # Show first statement with value label
            if prop_data['statements']:
                stmt = prop_data['statements'][0]
                value = stmt['value']
                value_label = stmt.get('value_label', '')
                
                if value_label:
                    print(f"  -> {value} ({value_label})")
                else:
                    print(f"  -> {value}")
                
                # Show qualifiers if any
                if stmt.get('qualifiers_with_labels'):
                    for qual_prop, qual_data in list(stmt['qualifiers_with_labels'].items())[:2]:
                        qual_label = qual_data['property_label']
                        qual_vals = qual_data['values']
                        if qual_vals:
                            val_info = qual_vals[0]
                            if 'label' in val_info:
                                print(f"     + qualifier: {qual_prop} ({qual_label}) = {val_info['value']} ({val_info['label']})")
                            else:
                                print(f"     + qualifier: {qual_prop} ({qual_label}) = {val_info['value']}")
            
            print()
            count += 1
            
            if count >= 20:
                break
        
        print(f"{'='*80}\n")
    
    def save_to_json(self, enhanced: Dict, filename: Optional[str] = None):
        """Save enhanced data to JSON file"""
        
        if not filename:
            qid = enhanced['qid']
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"output/wikidata_enhanced/{qid}_enhanced_{timestamp}.json"
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(enhanced, f, indent=2, ensure_ascii=False)
        
        print(f"SAVED to: {filename}")
        
        return filename


# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_enhanced_fetch(qid: str):
    """Test enhanced fetching with label resolution"""
    
    fetcher = WikidataEnhancedFetcher()
    
    try:
        # Fetch with labels
        data = fetcher.fetch_entity_with_labels(qid)
        
        # Print summary
        fetcher.print_enhanced_summary(data)
        
        # Save to JSON
        filename = fetcher.save_to_json(data)
        
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
    
    qid = sys.argv[1] if len(sys.argv) > 1 else 'Q17167'
    
    print(f"Testing Enhanced Wikidata Fetch with QID: {qid}")
    
    test_enhanced_fetch(qid)
