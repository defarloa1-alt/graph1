#!/usr/bin/env python3
"""
Link Entities to Subject Nodes (LCSH-based Topical Classification)

UPDATED (Dec 2025): Links entities to TOPICAL subjects only (not structural categories).
Uses LCSH as primary backbone identifier.

Examples:
- Event → Military history subject (topical)
- Person → Political science subject (topical)
- NOT: Period → Time subject (redundant!)
- NOT: Place → Geography subject (redundant!)
"""
import sys
import io
import argparse
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent.parent))

try:
    from neo4j import GraphDatabase
except ImportError:
    print("❌ ERROR: neo4j driver not installed")
    print("   Run: pip install neo4j")
    sys.exit(1)

try:
    from scripts.tools.wikidata_classification_lookup import get_all_classification_ids
except ImportError:
    print("⚠️  WARNING: wikidata_classification_lookup not found")
    print("   Entity enrichment will be disabled")
    get_all_classification_ids = None

def link_entities_to_subjects(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum", enrich_from_wikidata=True):
    """
    Link entities to TOPICAL Subject nodes (not structural categories).
    
    NEW ARCHITECTURE (Dec 2025):
    - Uses LCSH-based subjects
    - Links ONLY topical subjects (e.g., Military history, Political science)
    - Does NOT link structural categories (e.g., Time, Geography)
    - Can enrich entities with Wikidata classification data
    
    Args:
        uri: Neo4j connection URI
        user: Neo4j username
        password: Neo4j password
        enrich_from_wikidata: If True, fetch classification from Wikidata for entities with QIDs
    """
    
    print("="*80)
    print("Linking Entities to Topical Subject Backbone (LCSH)")
    print("="*80)
    print(f"URI: {uri}")
    print(f"Wikidata Enrichment: {'Enabled' if enrich_from_wikidata and get_all_classification_ids else 'Disabled'}")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Step 1: Link Events to topical subjects
        print("📊 Step 1: Linking Event nodes to topical subjects...")
        
        # Get events with QIDs
        result = session.run("""
            MATCH (e:Event)
            WHERE e.qid IS NOT NULL
            RETURN e.qid as qid, e.label as label
        """)
        
        events = list(result)
        print(f"   Found {len(events)} events with QIDs")
        
        if enrich_from_wikidata and get_all_classification_ids:
            linked_events = 0
            for event in events:
                class_data = get_all_classification_ids(event['qid'])
                
                if class_data and class_data.get('lcsh_id'):
                    # Find or create Subject node with LCSH ID
                    session.run("""
                        MERGE (s:Subject {lcsh_id: $lcsh_id})
                        ON CREATE SET
                            s.lcsh_heading = $lcsh_heading,
                            s.label = $label,
                            s.unique_id = $unique_id,
                            s.dewey_decimal = $dewey,
                            s.lcc_code = $lcc,
                            s.fast_id = $fast
                        WITH s
                        MATCH (e:Event {qid: $qid})
                        MERGE (e)-[r:SUBJECT_OF]->(s)
                        RETURN count(r) as linked
                    """, {
                        'lcsh_id': class_data['lcsh_id'],
                        'lcsh_heading': class_data.get('label', 'Unknown'),
                        'label': class_data.get('label', 'Unknown'),
                        'unique_id': f"SUBJECT_LCSH_{class_data['lcsh_id']}",
                        'dewey': class_data.get('dewey_decimal'),
                        'lcc': class_data.get('lcc_code'),
                        'fast': class_data.get('fast_id'),
                        'qid': event['qid']
                    })
                    linked_events += 1
                    if linked_events % 5 == 0:
                        print(f"   Linked {linked_events}/{len(events)} events...")
            
            print(f"✅ Linked {linked_events} Event nodes to topical subjects")
        else:
            print("   ⚠️  Wikidata enrichment disabled - skipping")
        print()
        
        # Step 2: Link Persons to topical subjects
        print("📊 Step 2: Linking Person nodes to topical subjects...")
        
        result = session.run("""
            MATCH (p:Person)
            WHERE p.qid IS NOT NULL
            RETURN p.qid as qid, p.label as label
        """)
        
        persons = list(result)
        print(f"   Found {len(persons)} persons with QIDs")
        
        if enrich_from_wikidata and get_all_classification_ids:
            linked_persons = 0
            for person in persons:
                class_data = get_all_classification_ids(person['qid'])
                
                if class_data and class_data.get('lcsh_id'):
                    session.run("""
                        MERGE (s:Subject {lcsh_id: $lcsh_id})
                        ON CREATE SET
                            s.lcsh_heading = $lcsh_heading,
                            s.label = $label,
                            s.unique_id = $unique_id,
                            s.dewey_decimal = $dewey,
                            s.lcc_code = $lcc,
                            s.fast_id = $fast
                        WITH s
                        MATCH (p:Person {qid: $qid})
                        MERGE (p)-[r:SUBJECT_OF]->(s)
                        RETURN count(r) as linked
                    """, {
                        'lcsh_id': class_data['lcsh_id'],
                        'lcsh_heading': class_data.get('label', 'Unknown'),
                        'label': class_data.get('label', 'Unknown'),
                        'unique_id': f"SUBJECT_LCSH_{class_data['lcsh_id']}",
                        'dewey': class_data.get('dewey_decimal'),
                        'lcc': class_data.get('lcc_code'),
                        'fast': class_data.get('fast_id'),
                        'qid': person['qid']
                    })
                    linked_persons += 1
                    if linked_persons % 10 == 0:
                        print(f"   Linked {linked_persons}/{len(persons)} persons...")
            
            print(f"✅ Linked {linked_persons} Person nodes to topical subjects")
        else:
            print("   ⚠️  Wikidata enrichment disabled - skipping")
        print()
        
        # Step 3: Verify
        result = session.run("""
            MATCH ()-[r:SUBJECT_OF]->(:Subject)
            RETURN count(r) as total
        """)
        record = result.single()
        total = record['total'] if record else 0
        
        # Count by entity type
        result = session.run("""
            MATCH (entity)-[:SUBJECT_OF]->(s:Subject)
            RETURN 
                CASE 
                    WHEN entity:Event THEN 'Event'
                    WHEN entity:Person THEN 'Person'
                    WHEN entity:Place THEN 'Place'
                    WHEN entity:Period THEN 'Period'
                    ELSE 'Other'
                END as type,
                count(entity) as count
            ORDER BY count DESC
        """)
        
        type_counts = {r['type']: r['count'] for r in result}
        
        print("="*80)
        print(f"✅ Entity-to-Subject linking complete!")
        print(f"   Total SUBJECT_OF relationships: {total}")
        print()
        print("   By entity type:")
        for entity_type, count in type_counts.items():
            print(f"     {entity_type:10s}: {count}")
        print("="*80)
        
        # Show sample
        print()
        print("📊 Sample linked entities:")
        result = session.run("""
            MATCH (entity)-[:SUBJECT_OF]->(s:Subject)
            WHERE s.lcsh_id IS NOT NULL
            RETURN 
                labels(entity)[0] as type,
                entity.label as name,
                s.label as subject,
                s.lcsh_id as lcsh_id,
                s.dewey_decimal as dewey
            LIMIT 15
        """)
        
        print(f"{'Type':<10} | {'Entity':<30} | {'Subject (LCSH)':<35} | {'Dewey'}")
        print("-" * 95)
        for record in result:
            dewey = record['dewey'] or 'N/A'
            print(f"{record['type']:<10} | {record['name'][:29]:<30} | {record['subject'][:34]:<35} | {dewey}")
    
    driver.close()
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Link entities to topical Subject nodes (LCSH-based)')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j URI')
    parser.add_argument('--user', default='neo4j', help='Neo4j username')
    parser.add_argument('--password', default='Chrystallum', help='Neo4j password')
    parser.add_argument('--no-wikidata', action='store_true', help='Disable Wikidata enrichment')
    
    args = parser.parse_args()
    
    success = link_entities_to_subjects(
        uri=args.uri,
        user=args.user,
        password=args.password,
        enrich_from_wikidata=not args.no_wikidata
    )
    sys.exit(0 if success else 1)
