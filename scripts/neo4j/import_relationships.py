#!/usr/bin/env python3
"""
Import Entity Relationships - REQ-FUNC-010

Maps Wikidata properties to Chrystallum relationships:
- P31 (instance of) → INSTANCE_OF
- P279 (subclass of) → SUBCLASS_OF
- P361 (part of) → PART_OF
- P527 (has parts) → HAS_PARTS
- P155/P156 (succession) → FOLLOWS/FOLLOWED_BY
- Temporal properties → STARTS_IN_YEAR/ENDS_IN_YEAR

Uses MERGE for idempotency per BR-REL-02
Validates both entities exist per BR-REL-01
"""

import sys
from pathlib import Path
import json
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


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
    'P793': 'HAS_SIGNIFICANT_EVENT',
    'P194': 'HAS_LEGISLATIVE_BODY',
    'P140': 'HAS_OFFICIAL_RELIGION',
    'P38': 'HAS_CURRENCY',
    'P37': 'HAS_OFFICIAL_LANGUAGE'
}


def generate_relationship_import(checkpoint_file: str, limit_entities: int = 300):
    """Generate relationship import Cypher from checkpoint"""
    
    print(f"\n{'='*80}")
    print(f"GENERATING RELATIONSHIP IMPORT - REQ-FUNC-010")
    print(f"{'='*80}\n")
    
    # Load checkpoint
    print(f"Loading: {checkpoint_file}")
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entities = data.get('entities', {})
    entity_list = list(entities.items())[:limit_entities]
    
    print(f"  Entities: {len(entity_list)}\n")
    
    # Collect all QIDs for validation
    all_qids = set([qid for qid, _ in entity_list])
    
    # Generate Cypher
    cypher_lines = []
    
    cypher_lines.append("// Entity Relationship Import - REQ-FUNC-010")
    cypher_lines.append(f"// Generated: {datetime.now().isoformat()}")
    cypher_lines.append(f"// Entities: {len(entity_list)}")
    cypher_lines.append("")
    
    relationship_count = 0
    
    for qid_from, entity in entity_list:
        claims = entity.get('claims', {})
        
        if not claims:
            continue
        
        for prop_id, prop_claims in claims.items():
            # Check if this property maps to a relationship
            if prop_id not in RELATIONSHIP_MAP:
                continue
            
            rel_type = RELATIONSHIP_MAP[prop_id]
            
            # Extract target QIDs
            for claim in prop_claims:
                datavalue = claim.get('mainsnak', {}).get('datavalue', {})
                
                if datavalue.get('type') == 'wikibase-entityid':
                    qid_to = datavalue.get('value', {}).get('id', '')
                    
                    # Only create relationship if target entity exists in our set
                    if qid_to and qid_to in all_qids:
                        
                        cypher = f"""
// {qid_from} --{rel_type}--> {qid_to}
MATCH (from:Entity {{qid: '{qid_from}'}})
MATCH (to:Entity {{qid: '{qid_to}'}})
MERGE (from)-[r:{rel_type}]->(to)
ON CREATE SET
  r.wikidata_pid = '{prop_id}',
  r.created_at = datetime(),
  r.source = 'wikidata';
"""
                        cypher_lines.append(cypher)
                        relationship_count += 1
    
    print(f"  Relationships generated: {relationship_count}\n")
    
    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"output/neo4j/relationships_{timestamp}.cypher"
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cypher_lines))
    
    print(f"Saved: {output_file}")
    print(f"  Statements: {relationship_count}")
    print(f"  Size: {Path(output_file).stat().st_size / 1024:.1f} KB\n")
    
    return output_file, relationship_count


if __name__ == "__main__":
    checkpoint = sys.argv[1] if len(sys.argv) > 1 else "output/checkpoints/QQ17167_checkpoint_20260221_061318.json"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    output_file, count = generate_relationship_import(checkpoint, limit)
    
    print(f"{'='*80}")
    print(f"READY TO IMPORT")
    print(f"{'='*80}\n")
    print(f"File: {output_file}")
    print(f"Relationships: {count}")
    print(f"\nUse auto_import.py to import to Neo4j\n")
