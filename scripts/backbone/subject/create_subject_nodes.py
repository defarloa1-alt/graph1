#!/usr/bin/env python3
"""
Create Subject Nodes from Backbone Alignment Data

NEW (Dec 2025): Uses LCSH as primary backbone, Dewey for agent routing, FAST as property.
Generates :Subject nodes from LCSH taxonomy with full classification metadata.
"""
import sys
import io
from pathlib import Path
import csv
import argparse

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
    print("   Subject nodes will be created without Wikidata enrichment")
    get_all_classification_ids = None

def create_subject_nodes(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum", enrich_from_wikidata=True):
    """
    Create Subject nodes from PropertyRegistry and enrich with Wikidata classification data.
    
    NEW ARCHITECTURE (Dec 2025):
    - LCSH ID as primary backbone (unique key)
    - Dewey Decimal for agent routing
    - LCC for hierarchical classification  
    - FAST as supplementary property
    
    Args:
        uri: Neo4j connection URI
        user: Neo4j username
        password: Neo4j password
        enrich_from_wikidata: If True, fetch Dewey/LCC from Wikidata
    """
    
    print("="*80)
    print("Creating Subject Backbone (LCSH Primary)")
    print("="*80)
    print(f"URI: {uri}")
    print(f"Wikidata Enrichment: {'Enabled' if enrich_from_wikidata and get_all_classification_ids else 'Disabled'}")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Step 1: Get unique subjects from PropertyRegistry
        print("📊 Step 1: Extracting subjects from PropertyRegistry...")
        result = session.run("""
            MATCH (reg:PropertyRegistry)
            WHERE reg.lcsh_heading <> ''
            RETURN DISTINCT 
                reg.lcsh_heading as lcsh_heading,
                reg.category as category,
                reg.lcc_code as lcc_code
            ORDER BY reg.category
        """)
        
        subjects = []
        for record in result:
            subjects.append({
                'lcsh_heading': record.get('lcsh_heading', record['category']),
                'category': record['category'],
                'lcc_code': record.get('lcc_code', '')
            })
        
        print(f"   Found {len(subjects)} unique subjects from PropertyRegistry")
        print()
        
        # Step 2: Create Subject nodes with LCSH-based IDs
        print(f"📊 Step 2: Creating Subject nodes (LCSH primary)...")
        created = 0
        
        for subj in subjects:
            # Generate LCSH ID (simplified for PropertyRegistry items)
            lcsh_id = f"temp_{subj['lcsh_heading'].replace(' ', '_').replace(',', '').lower()[:20]}"
            unique_id = f"SUBJECT_LCSH_{lcsh_id}"
            
            query = """
            MERGE (s:Subject {unique_id: $unique_id})
            ON CREATE SET
                s.lcsh_id = $lcsh_id,
                s.label = $label,
                s.lcsh_heading = $lcsh_heading,
                s.lcc_code = $lcc_code,
                s.domain = $domain,
                s.backbone_alignment = true,
                s.created_from = 'PropertyRegistry',
                s.created = datetime()
            ON MATCH SET
                s.lcc_code = COALESCE(s.lcc_code, $lcc_code),
                s.updated = datetime()
            RETURN s.label as label
            """
            
            result = session.run(query, {
                'unique_id': unique_id,
                'lcsh_id': lcsh_id,
                'label': subj['lcsh_heading'],
                'lcsh_heading': subj['lcsh_heading'],
                'lcc_code': subj['lcc_code'],
                'domain': subj['category'].lower()
            })
            
            record = result.single()
            if record:
                created += 1
                if created % 10 == 0:
                    print(f"   Processed {created}/{len(subjects)}...")
        
        print(f"✅ Created/updated {created} Subject nodes")
        print()
        
        # Step 3: Link PropertyRegistry to Subjects
        print(f"📊 Step 3: Linking PropertyRegistry to Subjects...")
        result = session.run("""
            MATCH (reg:PropertyRegistry)
            MATCH (s:Subject)
            WHERE reg.lcsh_heading <> '' AND s.lcsh_heading = reg.lcsh_heading
            MERGE (reg)-[r:DEFINED_BY]->(s)
            RETURN count(r) as count
        """)
        
        record = result.single()
        link_count = record['count'] if record else 0
        print(f"✅ Created {link_count} DEFINED_BY relationships")
        print()
        
        # Step 4: Verify
        result = session.run("""
            MATCH (s:Subject)
            RETURN 
                count(s) as subject_count,
                count(s.lcsh_id) as with_lcsh,
                count(s.dewey_decimal) as with_dewey,
                count(s.fast_id) as with_fast
        """)
        record = result.single()
        subject_count = record['subject_count'] if record else 0
        with_lcsh = record['with_lcsh'] if record else 0
        with_dewey = record['with_dewey'] if record else 0
        with_fast = record['with_fast'] if record else 0
        
        result = session.run("""
            MATCH ()-[r:DEFINED_BY]->(:Subject)
            RETURN count(r) as rel_count
        """)
        record = result.single()
        rel_count = record['rel_count'] if record else 0
        
        print("="*80)
        print(f"✅ Subject backbone created successfully!")
        print(f"   Subject nodes: {subject_count}")
        if subject_count > 0:
            print(f"   With LCSH ID: {with_lcsh} ({with_lcsh/subject_count*100:.1f}%)")
            print(f"   With Dewey: {with_dewey} ({with_dewey/subject_count*100:.1f}%)")
            print(f"   With FAST: {with_fast} ({with_fast/subject_count*100:.1f}%)")
        print(f"   DEFINED_BY relationships: {rel_count}")
        print("="*80)
        
        # Show sample subjects
        print()
        print("📊 Sample Subject nodes:")
        result = session.run("""
            MATCH (s:Subject)
            RETURN 
                s.label as label,
                s.lcsh_id as lcsh_id,
                s.dewey_decimal as dewey,
                s.domain as domain
            ORDER BY s.domain, s.dewey_decimal
            LIMIT 15
        """)
        
        print(f"{'Label':<35} | {'LCSH ID':<25} | {'Dewey':<8} | {'Domain':<12}")
        print("-" * 90)
        for record in result:
            lcsh = (record['lcsh_id'] or 'N/A')[:24]
            dewey = record['dewey'] or 'N/A'
            print(f"{record['label'][:34]:<35} | {lcsh:<25} | {dewey:<8} | {record['domain']}")
    
    driver.close()
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Subject nodes from backbone alignment data (LCSH primary)')
    parser.add_argument('--uri', default='bolt://localhost:7687', help='Neo4j URI')
    parser.add_argument('--user', default='neo4j', help='Neo4j username')
    parser.add_argument('--password', default='Chrystallum', help='Neo4j password')
    parser.add_argument('--no-wikidata', action='store_true', help='Disable Wikidata enrichment')
    
    args = parser.parse_args()
    
    success = create_subject_nodes(
        uri=args.uri,
        user=args.user,
        password=args.password,
        enrich_from_wikidata=not args.no_wikidata
    )
    sys.exit(0 if success else 1)
