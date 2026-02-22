#!/usr/bin/env python3
"""
Add Missing Facets to Periods via Pattern Matching
Adds Economic, Technological, Scientific, Religious, Environmental facets
that the LLM didn't detect.
"""
import sys
import io
import re
from neo4j import GraphDatabase

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Pattern-based facet detection
FACET_PATTERNS = {
    'TechnologicalFacet': [
        r'industrial|revolution|technological|technology|steam|digital|information age|iron age|bronze age',
        r'tool|production|machinery|automation'
    ],
    'EconomicFacet': [
        r'trade|commerce|economic|financial|merchant|commercial',
        r'market|capitalism|socialism|feudal.*economy'
    ],
    'ScientificFacet': [
        r'scientific|enlightenment|renaissance|reason|modernism',
        r'paradigm|intellectual|scholarly|academic'
    ],
    'ReligiousFacet': [
        r'reformation|counter-reformation|religious|crusade|jihad',
        r'christian|islamic|buddhist|hindu|temple|church|monastery'
    ],
    'EnvironmentalFacet': [
        r'ice age|climate|holocene|pleistocene|warming|drought',
        r'environmental|ecological|glacial'
    ],
    'MilitaryFacet': [
        r'military|warfare|conquest|occupation|invasion'
    ]
}

def detect_facets(label: str) -> list:
    """Detect all applicable facets for a period label."""
    label_lower = label.lower()
    detected_facets = []
    
    for facet_type, patterns in FACET_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, label_lower):
                detected_facets.append(facet_type)
                break  # Only add each facet once
    
    return detected_facets

def add_missing_facets(uri="bolt://localhost:7687", user="neo4j", password="Chrystallum"):
    """Add missing facet relationships to existing periods."""
    
    print("="*80)
    print("Adding Missing Facets to Periods")
    print("="*80)
    print(f"Neo4j: {uri}")
    print()
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Get all periods
        result = session.run("""
            MATCH (p:Period)
            OPTIONAL MATCH (p)-[]->(f:Facet)
            RETURN p.label as label, p.qid as qid, collect(DISTINCT labels(f)) as existing_facets
        """)
        
        periods = list(result)
        print(f"Found {len(periods)} periods to analyze")
        print()
        
        added_count = 0
        skipped_count = 0
        
        for period in periods:
            label = period['label']
            qid = period['qid']
            existing_facets = [f[0] if f and len(f) > 0 else None for f in period['existing_facets']]
            existing_facets = [f for f in existing_facets if f and f != 'Facet']
            
            # Detect potential new facets
            detected_facets = detect_facets(label)
            
            # Filter out facets that already exist
            new_facets = [f for f in detected_facets if f not in existing_facets]
            
            if not new_facets:
                skipped_count += 1
                continue
            
            print(f"Period: {label}")
            print(f"   Existing: {existing_facets}")
            print(f"   Adding: {new_facets}")
            
            # Add each new facet
            for facet_type in new_facets:
                facet_label = facet_type.replace('Facet', '').lower()
                facet_unique_id = f"{facet_type.upper()}_{facet_label.upper()}"
                relationship = f"HAS_{facet_type.upper().replace('FACET', '')}_FACET"
                
                session.run(f"""
                    MATCH (p:Period {{qid: $qid}})
                    MERGE (f:{facet_type}:Facet {{unique_id: $unique_id}})
                    SET f.label = $label
                    MERGE (p)-[:{relationship}]->(f)
                """, qid=qid, unique_id=facet_unique_id, label=facet_label)
                
                added_count += 1
            
            print()
        
        print("="*80)
        print("Summary")
        print("="*80)
        print(f"Periods analyzed: {len(periods)}")
        print(f"New facet relationships added: {added_count}")
        print(f"Periods unchanged: {skipped_count}")
        
        # Show new facet distribution
        print("\nFacet distribution after enhancement:")
        result = session.run("""
            MATCH ()-[r]->(f:Facet)
            RETURN [label IN labels(f) WHERE label <> 'Facet'][0] as facet_type, count(*) as count
            ORDER BY count DESC
        """)
        for record in result:
            print(f"  {record['facet_type']:25s}: {record['count']:>3}")
        
        print("\n✅ Facet enhancement complete!")
        print("="*80)
    
    driver.close()

if __name__ == "__main__":
    add_missing_facets()

