#!/usr/bin/env python3
"""
Comprehensive Relationship Import - FIXED VERSION

Import ALL Wikidata properties (not just 19 hardcoded ones).
Uses 314-relationship registry for canonical mapping.
Falls back to generic naming for unmapped properties.

Fixes: Hardcoded whitelist limitation (only 19 of 3,777 properties imported)
"""

import sys
from pathlib import Path
import json
import csv
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def load_relationship_registry():
    """Load canonical relationship mappings from registry CSV"""
    registry = {}
    registry_file = project_root / "Relationships" / "relationship_types_registry_master.csv"
    
    if not registry_file.exists():
        print(f"⚠️  Registry not found: {registry_file}")
        print("   Using fallback mapping")
        return {}
    
    with open(registry_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            wikidata_pid = row.get('wikidata_property', '').strip()
            rel_type = row.get('relationship_type', '').strip()
            lifecycle = row.get('lifecycle_status', '')
            
            # Only use implemented relationships
            if wikidata_pid and rel_type and lifecycle == 'implemented':
                registry[wikidata_pid] = rel_type
    
    return registry


def normalize_property_to_relationship(prop_id: str, wikidata_label: str = None) -> str:
    """
    Convert Wikidata property to canonical relationship type.
    
    Falls back to normalized property label if not in registry.
    """
    # Try registry first
    if prop_id in RELATIONSHIP_MAP:
        return RELATIONSHIP_MAP[prop_id]
    
    # Fallback: Use PID + label
    if wikidata_label:
        # Normalize label to relationship type
        # "position held" → "POSITION_HELD"
        normalized = wikidata_label.upper().replace(" ", "_").replace("-", "_")
        return normalized
    
    # Last resort: Use PID
    return f"WIKIDATA_{prop_id}"


def generate_comprehensive_relationship_import(
    checkpoint_file: str,
    limit_entities: int = 300,
    import_all: bool = True,
    property_whitelist: set = None
):
    """
    Generate comprehensive relationship import.
    
    Args:
        checkpoint_file: Path to checkpoint JSON
        limit_entities: Max entities to process
        import_all: If True, import ALL properties (not just registry)
        property_whitelist: If provided, only import these PIDs
    
    Returns:
        (output_file, relationship_count, property_count)
    """
    
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE RELATIONSHIP IMPORT")
    print(f"{'='*80}\n")
    
    # Load registry
    global RELATIONSHIP_MAP
    RELATIONSHIP_MAP = load_relationship_registry()
    print(f"Registry mappings: {len(RELATIONSHIP_MAP)}")
    
    # Load checkpoint
    print(f"Loading: {checkpoint_file}")
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entities = data.get('entities', {})
    entity_list = list(entities.items())[:limit_entities]
    
    print(f"  Entities: {len(entity_list)}")
    
    # Collect all QIDs for validation
    all_qids = set([qid for qid, _ in entity_list])
    
    # Analyze available properties
    all_props = set()
    for qid, entity in entity_list:
        all_props.update(entity.get('claims', {}).keys())
    
    print(f"  Properties in data: {len(all_props)}")
    
    if property_whitelist:
        props_to_import = property_whitelist & all_props
        print(f"  Whitelist filter: {len(props_to_import)} properties")
    elif import_all:
        props_to_import = all_props
        print(f"  Mode: IMPORT ALL ({len(props_to_import)} properties)")
    else:
        props_to_import = set(RELATIONSHIP_MAP.keys()) & all_props
        print(f"  Mode: Registry only ({len(props_to_import)} properties)")
    
    print()
    
    # Generate Cypher
    cypher_lines = []
    cypher_lines.append("// Comprehensive Entity Relationship Import")
    cypher_lines.append(f"// Generated: {datetime.now().isoformat()}")
    cypher_lines.append(f"// Entities: {len(entity_list)}")
    cypher_lines.append(f"// Properties imported: {len(props_to_import)}")
    cypher_lines.append(f"// Mode: {'ALL' if import_all else 'Registry only'}")
    cypher_lines.append("")
    
    relationship_count = 0
    property_usage = {}
    
    for qid_from, entity in entity_list:
        claims = entity.get('claims', {})
        
        if not claims:
            continue
        
        for prop_id, prop_claims in claims.items():
            # Filter by whitelist/mode
            if prop_id not in props_to_import:
                continue
            
            # Determine relationship type
            if prop_id in RELATIONSHIP_MAP:
                rel_type = RELATIONSHIP_MAP[prop_id]
                in_registry = True
            else:
                # Fallback for unmapped properties
                rel_type = f"WIKIDATA_{prop_id}"
                in_registry = False
            
            # Track usage
            if prop_id not in property_usage:
                property_usage[prop_id] = {
                    'count': 0,
                    'rel_type': rel_type,
                    'in_registry': in_registry
                }
            
            # Extract target QIDs
            for claim in prop_claims:
                datavalue = claim.get('mainsnak', {}).get('datavalue', {})
                
                if datavalue.get('type') == 'wikibase-entityid':
                    qid_to = datavalue.get('value', {}).get('id', '')
                    
                    # Only create relationship if target entity exists
                    if qid_to and qid_to in all_qids:
                        
                        # Extract qualifiers (temporal, location, etc.)
                        qualifiers = claim.get('qualifiers', {})
                        
                        # Build property string (Cypher SET uses = not :)
                        props = [
                            f"r.wikidata_pid = '{prop_id}'",
                            f"r.in_registry = {str(in_registry).lower()}",
                            "r.created_at = datetime()",
                            "r.source = 'wikidata'"
                        ]
                        
                        # Add temporal qualifiers if present
                        if 'P580' in qualifiers:  # start time
                            props.append("r.has_temporal = true")
                        
                        # Add location qualifier if present
                        if 'P276' in qualifiers:  # location
                            props.append("r.has_location = true")
                        
                        prop_string = ", ".join(props)
                        
                        cypher = f"""MATCH (from:Entity {{qid: '{qid_from}'}})
MATCH (to:Entity {{qid: '{qid_to}'}})
MERGE (from)-[r:{rel_type}]->(to)
ON CREATE SET {prop_string};
"""
                        cypher_lines.append(cypher)
                        relationship_count += 1
                        property_usage[prop_id]['count'] += 1
    
    print(f"{'='*80}")
    print(f"GENERATION SUMMARY")
    print(f"{'='*80}")
    print(f"  Relationships generated: {relationship_count:,}")
    print(f"  Properties used: {len(property_usage)}")
    print(f"  In registry: {sum(1 for p in property_usage.values() if p['in_registry'])}")
    print(f"  Unmapped: {sum(1 for p in property_usage.values() if not p['in_registry'])}")
    print()
    
    # Top 20 properties by usage
    print("Top 20 properties by relationship count:")
    for prop_id, info in sorted(property_usage.items(), key=lambda x: x[1]['count'], reverse=True)[:20]:
        status = "[REG]" if info['in_registry'] else "[NEW]"
        print(f"  {status} {prop_id}: {info['count']:,} ({info['rel_type']})")
    print()
    
    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"output/neo4j/relationships_comprehensive_{timestamp}.cypher"
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cypher_lines))
    
    print(f"Saved: {output_file}")
    print(f"  Statements: {relationship_count:,}")
    print(f"  Size: {Path(output_file).stat().st_size / 1024:.1f} KB\n")
    
    # Save property usage report
    report_file = f"output/relationship_property_usage_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'total_relationships': relationship_count,
            'properties_used': len(property_usage),
            'in_registry': sum(1 for p in property_usage.values() if p['in_registry']),
            'unmapped': sum(1 for p in property_usage.values() if not p['in_registry']),
            'property_details': property_usage
        }, f, indent=2)
    
    print(f"Property usage report: {report_file}\n")
    
    return output_file, relationship_count, len(property_usage)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive relationship import")
    parser.add_argument('checkpoint', nargs='?', 
                       default="output/checkpoints/QQ17167_checkpoint_20260221_061318.json",
                       help="Checkpoint file path")
    parser.add_argument('--limit', type=int, default=300,
                       help="Max entities to process")
    parser.add_argument('--registry-only', action='store_true',
                       help="Only import properties in registry (not all)")
    
    args = parser.parse_args()
    
    output_file, rel_count, prop_count = generate_comprehensive_relationship_import(
        args.checkpoint,
        limit_entities=args.limit,
        import_all=not args.registry_only
    )
    
    print(f"{'='*80}")
    print(f"READY TO IMPORT")
    print(f"{'='*80}\n")
    print(f"File: {output_file}")
    print(f"Relationships: {rel_count:,}")
    print(f"Property types: {prop_count}")
    print(f"\nExpected: {rel_count:,} / {args.limit} entities = {rel_count/args.limit:.1f} edges per entity")
    print(f"Current: 784 / 2,600 = 0.30 edges per entity")
    print(f"\n⚠️  Run with --registry-only to limit to {len(load_relationship_registry())} registered properties")
    print(f"   Or run without flag to import ALL {prop_count} properties\n")
