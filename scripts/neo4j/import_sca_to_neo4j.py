#!/usr/bin/env python3
"""
Import SCA Output to Neo4j

Reads SCA traversal JSON and generates Neo4j Cypher:
1. Classify entities by type (SubjectConcept, Place, Event, etc.)
2. Create nodes with all properties
3. Map Wikidata relationships to canonical types
4. Generate executable Cypher files

Shows progress with QID (Label) format
"""

import sys
from pathlib import Path
import json
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


# Entity type mappings (Wikidata P31 → Chrystallum node type)
ENTITY_TYPE_MAP = {
    'SubjectConcept': ['Q11514315', 'Q6428674', 'Q186081'],  # historical period, era, time interval
    'Place': ['Q515', 'Q486972', 'Q2221906', 'Q1549591', 'Q3957', 'Q15661340'],  # city, place, big city, ancient city
    'Event': ['Q1190554', 'Q198', 'Q178561', 'Q180684', 'Q103495'],  # event, war, battle, conflict
    'Human': ['Q5'],  # human
    'Organization': ['Q43229', 'Q4830453', 'Q7210356'],  # organization, institution
    'Work': ['Q47461344', 'Q234460', 'Q571'],  # written work, text, book
    'Religion': ['Q9174', 'Q9058', 'Q108704490'],  # religion, belief system, polytheistic
    'Language': ['Q34770'],  # language
    'Concept': []  # Default for everything else
}

# Wikidata property → Canonical relationship mapping
RELATIONSHIP_MAP = {
    'P31': 'INSTANCE_OF',
    'P279': 'SUBCLASS_OF',
    'P361': 'PART_OF',
    'P527': 'HAS_PARTS',
    'P150': 'CONTAINS',
    'P155': 'FOLLOWS',
    'P156': 'FOLLOWED_BY',
    'P1365': 'REPLACES',
    'P1366': 'REPLACED_BY',
    'P36': 'HAS_CAPITAL',
    'P17': 'LOCATED_IN_COUNTRY',
    'P30': 'ON_CONTINENT',
    'P276': 'LOCATED_IN',
    'P47': 'SHARES_BORDER_WITH',
    'P706': 'LOCATED_IN_FEATURE',
    'P793': 'HAS_SIGNIFICANT_EVENT',
    'P1344': 'PARTICIPATED_IN',
    'P194': 'HAS_LEGISLATIVE_BODY',
    'P140': 'HAS_OFFICIAL_RELIGION',
    'P3075': 'HAS_OFFICIAL_RELIGION',
    'P38': 'HAS_CURRENCY',
    'P37': 'HAS_OFFICIAL_LANGUAGE',
    'P2936': 'USES_LANGUAGE',
    'P2348': 'WITHIN_TIME_PERIOD'
}


class Neo4jImporter:
    """Import SCA output to Neo4j"""
    
    def __init__(self, sca_json_path: str):
        self.json_path = Path(sca_json_path)
        self.entities = {}
        self.classified = {}
        self.cypher_statements = []
        
    def load_entities(self):
        """Load SCA output"""
        
        print(f"\n{'='*80}")
        print(f"LOADING SCA OUTPUT")
        print(f"{'='*80}\n")
        print(f"File: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.entities = data.get('entities', {})
        
        print(f"  Loaded {len(self.entities)} entities\n")
    
    def classify_entities(self):
        """Classify entities by type"""
        
        print(f"\n{'='*80}")
        print(f"CLASSIFYING ENTITIES")
        print(f"{'='*80}\n")
        
        for qid, entity in self.entities.items():
            label = entity.get('label', qid)
            
            # Get P31 values from entity (stored in original traversal)
            # For the clean output, we need to determine type from label or re-fetch
            # For now, classify as Concept by default
            node_type = 'Concept'
            
            # Store classification
            if node_type not in self.classified:
                self.classified[node_type] = []
            
            self.classified[node_type].append(qid)
        
        print(f"Classification complete:")
        for node_type, qids in self.classified.items():
            print(f"  {node_type}: {len(qids)}")
        print()
    
    def generate_cypher(self):
        """Generate Neo4j Cypher statements"""
        
        print(f"\n{'='*80}")
        print(f"GENERATING NEO4J CYPHER")
        print(f"{'='*80}\n")
        
        # Generate node creation — MERGE on qid for idempotency and multi-seed deduplication
        for i, (qid, entity) in enumerate(self.entities.items(), 1):
            label = entity.get('label', qid)
            props = entity.get('properties', 0)
            label_escaped = label.replace("\\", "\\\\").replace("'", "\\'")

            # MERGE on qid: creates if absent, matches if present (no duplicates across seeds)
            cypher = f"""
// Entity {i}: {qid} ({label})
MERGE (n{i}:Entity {{qid: '{qid}'}})
ON CREATE SET
  n{i}.label = '{label_escaped}',
  n{i}.properties_count = {props},
  n{i}.discovered_from = 'sca_traversal',
  n{i}.imported_at = datetime()
"""
            self.cypher_statements.append(cypher)
            
            if i % 100 == 0:
                print(f"  Generated Cypher for {i}/{len(self.entities)} entities...")
        
        print(f"\n  Total Cypher statements: {len(self.cypher_statements)}\n")
    
    def save_cypher(self):
        """Save Cypher to file"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"output/neo4j/import_{timestamp}.cypher"
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("// SCA Entity Import - Generated by import_sca_to_neo4j.py\n")
            f.write(f"// Generated: {datetime.now().isoformat()}\n")
            f.write(f"// Total entities: {len(self.entities)}\n\n")
            f.write('\n'.join(self.cypher_statements))
        
        print(f"Cypher saved: {output_file}\n")
        
        return output_file
    
    def run_import_generation(self):
        """Run complete import generation"""
        
        print(f"\n{'='*80}")
        print(f"NEO4J IMPORT GENERATOR")
        print(f"{'='*80}")
        
        # Load
        self.load_entities()
        
        # Classify
        self.classify_entities()
        
        # Generate Cypher
        self.generate_cypher()
        
        # Save
        cypher_file = self.save_cypher()
        
        print(f"\n{'='*80}")
        print(f"IMPORT READY")
        print(f"{'='*80}\n")
        print(f"Entities: {len(self.entities)}")
        print(f"Cypher file: {cypher_file}")
        print(f"\nExecute in Neo4j Browser to import!\n")
        
        return cypher_file


if __name__ == "__main__":
    sca_file = sys.argv[1] if len(sys.argv) > 1 else "output/traversal/Q17167_clean_20260220_230959.json"
    
    importer = Neo4jImporter(sca_file)
    importer.run_import_generation()
