#!/usr/bin/env python3
"""
Federation Mapper Agent - With Progress Display

Maps SCA output to all federation sources with live progress:
- Wikidata (QID + Label)
- LCSH (ID + Label)
- FAST (ID + Label)
- LCC (Class + Label)
- PeriodO (ID + Label + dates)
- Pleiades (ID + Label + coords)
- Getty TGN (ID + Label)

Shows progress as it processes each entity
"""

import sys
from pathlib import Path
import json
import csv
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class FederationMapper:
    """Map entities to all federation sources"""
    
    def __init__(self, 
                 fast_path="Python/fast/key/FASTTopical_parsed.csv",
                 lcc_path="Subjects/lcc_flat.csv",
                 periodo_path="Temporal/periodo-dataset.csv",
                 pleiades_path="Geographic/pleiades_places.csv"):
        
        self.fast_path = Path(fast_path)
        self.lcc_path = Path(lcc_path)
        self.periodo_path = Path(periodo_path)
        self.pleiades_path = Path(pleiades_path)
        
        # Federation datasets
        self.fast_index = {}
        self.lcc_index = {}
        self.periodo_index = {}
        self.pleiades_index = {}
        
        # Results
        self.mapped_entities = []
        
    def load_federations(self):
        """Load all federation datasets"""
        
        print(f"\n{'='*80}")
        print(f"LOADING FEDERATION DATASETS")
        print(f"{'='*80}\n")
        
        # FAST
        if self.fast_path.exists():
            print(f"Loading FAST...")
            with open(self.fast_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fast_id = row.get('fast_id', '').strip()
                    label = row.get('preferred_label', '').strip()
                    if fast_id and label:
                        self.fast_index[label.lower()] = {
                            'id': fast_id,
                            'label': label
                        }
            print(f"  Loaded {len(self.fast_index)} FAST entries\n")
        
        # LCC
        if self.lcc_path.exists():
            print(f"Loading LCC...")
            with open(self.lcc_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get('code', '').strip()
                    label = row.get('label', '').strip()
                    if code and label:
                        self.lcc_index[label.lower()] = {
                            'id': code,
                            'label': label
                        }
            print(f"  Loaded {len(self.lcc_index)} LCC entries\n")
        
        # PeriodO
        if self.periodo_path.exists():
            print(f"Loading PeriodO...")
            with open(self.periodo_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    periodo_id = row.get('periodo_id', '').strip()
                    label = row.get('label', '').strip()
                    if periodo_id and label:
                        self.periodo_index[label.lower()] = {
                            'id': periodo_id,
                            'label': label,
                            'start': row.get('start', ''),
                            'end': row.get('stop', '')
                        }
            print(f"  Loaded {len(self.periodo_index)} PeriodO entries\n")
        
        # Pleiades
        if self.pleiades_path.exists():
            print(f"Loading Pleiades...")
            with open(self.pleiades_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pleiades_id = row.get('id', '').strip()
                    label = row.get('title', '').strip()
                    if pleiades_id and label:
                        self.pleiades_index[label.lower()] = {
                            'id': pleiades_id,
                            'label': label,
                            'lat': row.get('reprLat', ''),
                            'long': row.get('reprLong', '')
                        }
            print(f"  Loaded {len(self.pleiades_index)} Pleiades entries\n")
    
    def map_entity(self, entity_qid: str, entity_data: dict) -> dict:
        """Map single entity to all federations"""
        
        label = entity_data.get('label', entity_qid)
        label_lower = label.lower()
        claims = entity_data.get('claims', {})
        
        mapping = {
            'qid': entity_qid,
            'label': label,
            'federations': {}
        }
        
        # Wikidata (always present)
        mapping['federations']['wikidata'] = {
            'id': entity_qid,
            'label': label
        }
        
        # LCSH (from Wikidata P244 or local match)
        if 'P244' in claims:
            lcsh_id = claims['P244'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
            mapping['federations']['lcsh'] = {
                'id': lcsh_id,
                'label': f"LCSH:{lcsh_id}",  # Could query for full label
                'source': 'wikidata'
            }
        elif label_lower in self.fast_index:  # Try FAST as proxy
            mapping['federations']['fast_match'] = self.fast_index[label_lower]
        
        # FAST (from Wikidata P2163 or local match)
        if 'P2163' in claims:
            fast_id = claims['P2163'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
            mapping['federations']['fast'] = {
                'id': fast_id,
                'label': self.fast_index.get(label_lower, {}).get('label', fast_id),
                'source': 'wikidata'
            }
        elif label_lower in self.fast_index:
            mapping['federations']['fast'] = {
                **self.fast_index[label_lower],
                'source': 'local_match'
            }
        
        # LCC (from Wikidata P1149 or local match)
        if 'P1149' in claims:
            lcc_class = claims['P1149'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
            mapping['federations']['lcc'] = {
                'id': lcc_class,
                'label': lcc_class,
                'source': 'wikidata'
            }
        elif label_lower in self.lcc_index:
            mapping['federations']['lcc'] = {
                **self.lcc_index[label_lower],
                'source': 'local_match'
            }
        
        # PeriodO (local match only)
        if label_lower in self.periodo_index:
            mapping['federations']['periodo'] = {
                **self.periodo_index[label_lower],
                'source': 'local_match'
            }
        
        # Pleiades (from Wikidata P1584 or local match)
        if 'P1584' in claims:
            pleiades_id = claims['P1584'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
            mapping['federations']['pleiades'] = {
                'id': pleiades_id,
                'label': self.pleiades_index.get(label_lower, {}).get('label', pleiades_id),
                'source': 'wikidata'
            }
        elif label_lower in self.pleiades_index:
            mapping['federations']['pleiades'] = {
                **self.pleiades_index[label_lower],
                'source': 'local_match'
            }
        
        # Getty TGN (from Wikidata P1667)
        if 'P1667' in claims:
            tgn_id = claims['P1667'][0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
            mapping['federations']['tgn'] = {
                'id': tgn_id,
                'label': label,
                'source': 'wikidata'
            }
        
        return mapping
    
    def print_mapping_progress(self, mapping: dict, index: int, total: int):
        """Print mapping progress with all labels"""
        
        print(f"\n[{index}/{total}] Mapping {mapping['qid']} ({mapping['label']})")
        print(f"{'-'*80}")
        
        for fed_name, fed_data in mapping['federations'].items():
            fed_id = fed_data.get('id', '')
            fed_label = fed_data.get('label', '')
            source = fed_data.get('source', '')
            
            print(f"  {fed_name.upper():12} {fed_id:20} ({fed_label}) [{source}]")
        
        if not mapping['federations'] or len(mapping['federations']) == 1:  # Only wikidata
            print(f"  NO OTHER FEDERATIONS FOUND")
    
    def process_sca_output(self, sca_json_path: str):
        """Process SCA output and map to federations"""
        
        print(f"\n{'='*80}")
        print(f"FEDERATION MAPPER - PROCESSING SCA OUTPUT")
        print(f"{'='*80}\n")
        
        # Load SCA output
        print(f"Loading SCA output: {sca_json_path}")
        with open(sca_json_path, 'r', encoding='utf-8') as f:
            sca_data = json.load(f)
        
        entities = sca_data.get('entities', {})
        print(f"  Loaded {len(entities)} entities from SCA\n")
        
        # Load federations
        self.load_federations()
        
        # Process each entity
        print(f"\n{'='*80}")
        print(f"MAPPING ENTITIES TO FEDERATIONS")
        print(f"{'='*80}\n")
        
        for i, (qid, entity_data) in enumerate(entities.items(), 1):
            mapping = self.map_entity(qid, entity_data)
            self.mapped_entities.append(mapping)
            self.print_mapping_progress(mapping, i, len(entities))
        
        # Save results
        print(f"\n{'='*80}")
        print(f"SAVING RESULTS")
        print(f"{'='*80}\n")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"output/federation_mapping/mapping_{timestamp}.json"
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_entities': len(self.mapped_entities),
                'mappings': self.mapped_entities
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Saved: {output_file}\n")
        
        # Summary
        fed_counts = {}
        for mapping in self.mapped_entities:
            for fed_name in mapping['federations'].keys():
                fed_counts[fed_name] = fed_counts.get(fed_name, 0) + 1
        
        print(f"FEDERATION COVERAGE:")
        for fed_name, count in sorted(fed_counts.items()):
            pct = count / len(self.mapped_entities) * 100
            print(f"  {fed_name:12} {count:4}/{len(self.mapped_entities)} ({pct:.1f}%)")
        
        return output_file


if __name__ == "__main__":
    sca_file = sys.argv[1] if len(sys.argv) > 1 else "output/traversal/Q17167_traversal_latest.json"
    
    mapper = FederationMapper()
    mapper.process_sca_output(sca_file)
