#!/usr/bin/env python3
"""
Prepare Neo4j Import with Ciphers

Takes SCA checkpoint output and:
1. Adds Tier 1 and Tier 2 ciphers to each entity
2. Classifies entity types
3. Generates Neo4j Cypher with proper indexes
4. Creates first N entities for testing
"""

import sys
from pathlib import Path
import json
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.tools.entity_cipher import (
    generate_entity_cipher,
    generate_all_faceted_ciphers,
    classify_entity_type
)


def process_checkpoint_with_ciphers(checkpoint_file: str, limit: int = 300):
    """Process checkpoint and add ciphers"""
    
    print(f"\n{'='*80}")
    print(f"PREPARING NEO4J IMPORT WITH CIPHERS")
    print(f"{'='*80}\n")
    
    # Load checkpoint
    print(f"Loading checkpoint: {checkpoint_file}")
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entities = data.get('entities', {})
    total = len(entities)
    print(f"  Total entities in checkpoint: {total}")
    print(f"  Processing first {limit} entities\n")
    
    # Process each entity
    enriched = []
    seed_qid = data.get('seed', 'Q17167')
    
    for i, (qid, entity) in enumerate(list(entities.items())[:limit], 1):
        # Get entity type from types list
        types = entity.get('types', [])
        
        # Map to canonical entity type
        entity_type = 'CONCEPT'  # Default
        if 'historical period' in ' '.join(types).lower():
            entity_type = 'SUBJECTCONCEPT'
        elif 'city' in ' '.join(types).lower() or 'place' in ' '.join(types).lower():
            entity_type = 'PLACE'
        elif 'human' in ' '.join(types).lower() or 'person' in ' '.join(types).lower():
            entity_type = 'PERSON'
        elif 'war' in ' '.join(types).lower() or 'event' in ' '.join(types).lower():
            entity_type = 'EVENT'
        elif 'organization' in ' '.join(types).lower():
            entity_type = 'ORGANIZATION'
        
        # Generate Tier 1 cipher
        entity_cipher = generate_entity_cipher(qid, entity_type, "wd")
        
        # Generate Tier 2 ciphers (all 18 facets, anchored to seed)
        faceted_ciphers = generate_all_faceted_ciphers(entity_cipher, seed_qid)
        
        # Enrich entity
        enriched_entity = {
            **entity,
            'qid': qid,
            'entity_type': entity_type,
            'entity_cipher': entity_cipher,
            'namespace': 'wd',
            'faceted_ciphers': faceted_ciphers,
            'subjectconcept_anchor': seed_qid
        }
        
        enriched.append(enriched_entity)
        
        if i % 50 == 0:
            print(f"  Processed {i}/{limit} entities...")
    
    print(f"\n  Total processed: {len(enriched)}\n")
    
    # Generate Neo4j Cypher
    print(f"{'='*80}")
    print(f"GENERATING NEO4J CYPHER")
    print(f"{'='*80}\n")
    
    cypher_lines = []
    
    # Header
    cypher_lines.append("// Neo4j Import - SCA Entities with Ciphers")
    cypher_lines.append(f"// Generated: {datetime.now().isoformat()}")
    cypher_lines.append(f"// Total entities: {len(enriched)}")
    cypher_lines.append("")
    
    # Indexes
    cypher_lines.append("// ============ INDEXES ============")
    cypher_lines.append("")
    cypher_lines.append("// Tier 1: Entity cipher indexes")
    cypher_lines.append("CREATE INDEX entity_cipher_idx IF NOT EXISTS FOR (n:Entity) ON (n.entity_cipher);")
    cypher_lines.append("CREATE INDEX entity_qid_idx IF NOT EXISTS FOR (n:Entity) ON (n.qid);")
    cypher_lines.append("CREATE INDEX entity_type_idx IF NOT EXISTS FOR (n:Entity) ON (n.entity_type, n.entity_cipher);")
    cypher_lines.append("")
    cypher_lines.append("// Tier 2: Faceted cipher indexes")
    cypher_lines.append("CREATE INDEX faceted_cipher_idx IF NOT EXISTS FOR (n:FacetedEntity) ON (n.faceted_cipher);")
    cypher_lines.append("CREATE INDEX faceted_entity_facet_idx IF NOT EXISTS FOR (n:FacetedEntity) ON (n.entity_cipher, n.facet_id);")
    cypher_lines.append("")
    cypher_lines.append("// ============ ENTITIES ============")
    cypher_lines.append("")
    
    # Create entities
    for i, entity in enumerate(enriched, 1):
        qid = entity['qid']
        # Properly escape label for Cypher (backslashes first, then quotes)
        label = entity['label'].replace("\\", "\\\\").replace("'", "\\'")
        entity_cipher = entity['entity_cipher']
        entity_type = entity['entity_type']
        fed_score = entity.get('federation_score', 1)
        props_count = entity.get('properties_count', 0)
        
        # Generate entity_id (required by existing schema)
        entity_id = f"{entity_type.lower()}_{qid.lower()}"
        
        # Extract property summary (QID-valued properties only for now)
        property_summary = {}
        claims = entity.get('claims', {})
        
        for prop_id in list(claims.keys())[:50]:  # First 50 properties
            values = []
            for claim in claims.get(prop_id, [])[:5]:  # First 5 values per property
                datavalue = claim.get('mainsnak', {}).get('datavalue', {})
                if datavalue.get('type') == 'wikibase-entityid':
                    val_qid = datavalue.get('value', {}).get('id', '')
                    if val_qid:
                        values.append(val_qid)
            if values:
                property_summary[prop_id] = values
        
        # Convert to Cypher-safe string (escape quotes and backslashes)
        props_str = str(property_summary).replace("\\", "\\\\").replace("'", "\\'")
        
        # Escape label for Cypher (critical for special characters)
        label_escaped = label.replace("\\", "\\\\").replace("'", "\\'")
        
        # MERGE on qid for idempotency and multi-seed deduplication
        cypher = f"""
// Entity {i}: {qid} ({label})
MERGE (n:Entity {{qid: '{qid}'}})
ON CREATE SET
  n.entity_cipher = '{entity_cipher}',
  n.entity_id = '{entity_id}',
  n.label = '{label_escaped}',
  n.entity_type = '{entity_type}',
  n.namespace = 'wd',
  n.federation_score = {fed_score},
  n.properties_count = {props_count},
  n.property_summary = '{props_str}',
  n.status = 'candidate',
  n.proposed_by = 'sca_traversal',
  n.discovered_from = 'sca_traversal',
  n.imported_at = datetime()
"""
        cypher_lines.append(cypher)
    
    # Create FacetedEntity hub nodes for first 10 entities (sample)
    cypher_lines.append("\n// ============ FACETED ENTITIES (Sample - First 10) ============\n")
    
    for entity in enriched[:10]:
        entity_cipher = entity['entity_cipher']
        qid = entity['qid']
        
        for facet, faceted_cipher in entity['faceted_ciphers'].items():
            cypher = f"""
CREATE (:FacetedEntity {{
  faceted_cipher: '{faceted_cipher}',
  entity_cipher: '{entity_cipher}',
  qid: '{qid}',
  facet_id: '{facet}',
  subjectconcept_id: '{seed_qid}',
  created_at: datetime()
}})
"""
            cypher_lines.append(cypher)
    
    # Save Cypher
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"output/neo4j/import_with_ciphers_{timestamp}.cypher"
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cypher_lines))
    
    print(f"Cypher saved: {output_file}")
    print(f"  Entities: {len(enriched)}")
    print(f"  Lines: {len(cypher_lines)}")
    print(f"  Size: {Path(output_file).stat().st_size / 1024:.1f} KB\n")
    
    # Save enriched JSON
    enriched_json = f"output/enriched/entities_with_ciphers_{timestamp}.json"
    Path(enriched_json).parent.mkdir(parents=True, exist_ok=True)
    
    with open(enriched_json, 'w', encoding='utf-8') as f:
        json.dump({
            'seed': seed_qid,
            'total': len(enriched),
            'entities': enriched
        }, f, indent=2)
    
    print(f"Enriched JSON: {enriched_json}\n")
    
    print(f"{'='*80}")
    print(f"READY FOR NEO4J")
    print(f"{'='*80}\n")
    print(f"Execute in Neo4j Browser:")
    print(f"  {output_file}\n")
    
    return output_file


if __name__ == "__main__":
    checkpoint = sys.argv[1] if len(sys.argv) > 1 else "output/checkpoints/QQ17167_checkpoint_20260221_061318.json"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    process_checkpoint_with_ciphers(checkpoint, limit)
