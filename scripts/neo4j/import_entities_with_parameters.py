#!/usr/bin/env python3
"""
Neo4j Entity Import with Parameterized Queries
Replaces string interpolation approach to handle special characters properly
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from neo4j import GraphDatabase

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.tools.entity_cipher import (
    generate_entity_cipher,
    generate_all_faceted_ciphers,
    classify_entity_type
)

# Neo4j Connection
NEO4J_URI = "neo4j+s://f7b612a3.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "K2sHUx9dFYhEOurYzNjlBuNb8AV9-Xlw-KJcQ85QBHM"


def import_entities_with_parameters(checkpoint_file: str, limit: int = 2600, batch_size: int = 100):
    """Import entities using parameterized queries (handles all special characters)"""
    
    print(f"\n{'='*80}")
    print(f"NEO4J ENTITY IMPORT - PARAMETERIZED APPROACH")
    print(f"{'='*80}\n")
    
    # Load checkpoint
    print(f"Loading checkpoint: {checkpoint_file}")
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entities = data.get('entities', {})
    seed_qid = data.get('seed', 'Q17167')
    
    total = len(entities)
    print(f"  Total entities in checkpoint: {total}")
    print(f"  Processing first {limit} entities")
    print(f"  Batch size: {batch_size}\n")
    
    # Process entities
    entities_to_import = []
    
    for qid, entity in list(entities.items())[:limit]:
        # Get entity type
        types = entity.get('types', [])
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
        
        # Generate ciphers
        entity_cipher = generate_entity_cipher(qid, entity_type, "wd")
        entity_id = f"{entity_type.lower()}_q{qid.lower()[1:]}"
        
        # Get properties
        label = entity.get('label', qid)
        props_count = len(entity.get('properties', {}))
        property_summary = {}
        
        for prop_id, values in entity.get('properties', {}).items():
            value_qids = []
            for val in values:
                if isinstance(val, dict):
                    val_qid = val.get('value', {}).get('id')
                    if val_qid:
                        value_qids.append(val_qid)
            if value_qids:
                property_summary[prop_id] = value_qids
        
        # Calculate federation score
        fed_score = 1
        if props_count > 50:
            fed_score = 2
        if props_count > 100:
            fed_score = 3
        
        entities_to_import.append({
            'entity_cipher': entity_cipher,
            'entity_id': entity_id,
            'qid': qid,
            'label': label,  # NO ESCAPING - parameters handle it!
            'entity_type': entity_type,
            'federation_score': fed_score,
            'properties_count': props_count,
            'property_summary': str(property_summary)  # Convert to string
        })
    
    print(f"  Processed {len(entities_to_import)} entities\n")
    
    # Connect to Neo4j and import
    print(f"{'='*80}")
    print(f"IMPORTING TO NEO4J (Parameterized)")
    print(f"{'='*80}\n")
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        with driver.session() as session:
            # Import in batches
            total_imported = 0
            
            for i in range(0, len(entities_to_import), batch_size):
                batch = entities_to_import[i:i+batch_size]
                
                print(f"Importing batch {i//batch_size + 1} ({len(batch)} entities)...")
                
                # Parameterized query
                cypher = """
                UNWIND $entities AS entity
                MERGE (n:Entity {entity_cipher: entity.entity_cipher})
                ON CREATE SET
                    n.entity_id = entity.entity_id,
                    n.qid = entity.qid,
                    n.label = entity.label,
                    n.entity_type = entity.entity_type,
                    n.namespace = 'wd',
                    n.federation_score = entity.federation_score,
                    n.properties_count = entity.properties_count,
                    n.property_summary = entity.property_summary,
                    n.status = 'candidate',
                    n.proposed_by = 'sca_traversal',
                    n.discovered_from = 'sca_traversal',
                    n.imported_at = datetime()
                RETURN count(n) as imported
                """
                
                result = session.run(cypher, entities=batch)
                batch_count = result.single()['imported']
                total_imported += batch_count
                
                if (i + batch_size) % 500 == 0:
                    print(f"  Progress: {total_imported}/{limit} entities imported...")
            
            print(f"\n✅ Import complete: {total_imported} entities")
            
            # Verify
            result = session.run("MATCH (n:Entity) RETURN count(n) as total")
            total_in_db = result.single()['total']
            
            print(f"\nVerification:")
            print(f"  Entities in database: {total_in_db}")
            print(f"  Expected: {total_imported} (or existing + new)")
            
    finally:
        driver.close()
    
    print(f"\n{'='*80}")
    print(f"IMPORT COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Parameterized import successful")
    print(f"✅ All special characters handled correctly")
    print(f"✅ No escaping issues")


if __name__ == "__main__":
    checkpoint_file = "output/checkpoints/QQ17167_checkpoint_20260221_061318.json"
    
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = 2600
    
    print(f"Importing {limit} entities from {checkpoint_file}")
    import_entities_with_parameters(checkpoint_file, limit)
